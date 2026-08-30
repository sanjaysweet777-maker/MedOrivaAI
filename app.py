from flask import Flask, render_template, request, jsonify, session
import uuid
import re
import time
from functools import lru_cache

app = Flask(__name__)
app.secret_key = "medoriva-mvp-secret-key"

# ============================================================
# TRANSLATION CACHE
# ============================================================

translation_cache = {}

def get_cached_translation(text, target_lang):
    cache_key = f"{text}_{target_lang}"
    return translation_cache.get(cache_key)

def set_cached_translation(text, target_lang, result):
    cache_key = f"{text}_{target_lang}"
    translation_cache[cache_key] = result

# ============================================================
# MYMEMORY LANGUAGE CODE MAPPING
# ============================================================

MYMEMORY_LANG_MAP = {
    "ta": "ta-IN",
    "hi": "hi-IN",
    "ml": "ml-IN",
    "bn": "bn-IN",
    "ur": "ur-PK",
    "ar": "ar-SA",
    "pl": "pl-PL",
    "so": "so-SO",
    "ro": "ro-RO",
}

def get_mymemory_lang_code(lang_code):
    if not lang_code:
        return "en-GB"
    return MYMEMORY_LANG_MAP.get(lang_code, lang_code)

# ============================================================
# SIMPLIFICATION RULES
# ============================================================

SIMPLIFY_RULES = [
    (r"require\s+further\s+diagnostic\s+evaluation", "need more tests"),
    (r"administer\s+medication", "give medicine"),
    (r"experiencing\s+discomfort", "feeling pain"),
    (r"prior\s+to", "before"),
    (r"in\s+order\s+to", "to"),
    (r"approximately", "about"),
    (r"at\s+this\s+point\s+in\s+time", "now"),
    (r"due\s+to\s+the\s+fact\s+that", "because"),
    (r"facilitate", "help"),
    (r"commence", "start"),
    (r"terminate", "end"),
    (r"endeavour", "try"),
    (r"obtain", "get"),
    (r"sufficient", "enough"),
    (r"physician", "doctor"),
]

def simplify_text(text):
    simplified = text
    changed = False
    for pattern, replacement in SIMPLIFY_RULES:
        result = re.sub(pattern, replacement, simplified, flags=re.IGNORECASE)
        if result != simplified:
            changed = True
            simplified = result
    return simplified, changed

# ============================================================
# URGENT PHRASES (truncated for space — keep your full list)
# ============================================================

URGENT_PHRASES = [
    "chest pain", "chest hurt", "can't breathe", "cant breathe",
    "difficulty breathing", "heart pain", "bleeding heavily",
    "unconscious", "stroke", "seizure", "collapsed", "not breathing",
    "nenji vali", "moochu varadhu", "iratha", "padaippu",
]

NEGATION_WORDS = [
    "illai", "illa", "kidaiyathu", "varadhu", "varala", "ila",
    "nahi", "nahin", "mat", "nhi", "nie", "brak", "bez",
    "la", "laysa", "mish", "ma", "no", "not", "don't", "dont",
    "do not", "never", "none", "cannot", "can't", "cant",
    "alla", "allatha", "ille", "illa",
]

def is_negative(text):
    lower = text.lower()
    for word in NEGATION_WORDS:
        pattern = r'\b' + re.escape(word) + r'\b'
        if re.search(pattern, lower):
            return True
    return False

URGENT_SYMPTOMS = [
    "chest pain", "chest hurt", "heart pain", "cant breathe",
    "can't breathe", "difficulty breathing", "not breathing",
    "bleeding heavily", "unconscious", "stroke", "seizure",
    "collapsed", "severe pain", "very bad pain",
    "nenji vali", "moochu varadhu", "moochu pidikuthu", "iratha",
]

def needs_medical_consultation(text):
    lower = text.lower()
    has_urgent = any(phrase in lower for phrase in URGENT_SYMPTOMS)
    has_negation = is_negative(text)
    return has_urgent and not has_negation

# ============================================================
# TRANSLATION DICTIONARY (KEEP YOUR FULL LIST)
# ============================================================

TRANSLATION_DICT = {
    "enaku nenji vali irukku": "I have chest pain",
    "good morning how can i help you": "காலை வணக்கம். நான் உங்களுக்கு எப்படி உதவ முடியும்?",
    "do you have an appointment": "உங்களுக்கு முன்பதிவு உள்ளதா?",
    "please take a seat": "தயவு செய்து உட்காருங்கள்",
    "the doctor will see you shortly": "மருத்துவர் விரைவில் உங்களை பார்ப்பார்",
    "do you need any assistance": "உங்களுக்கு உதவி தேவையா?",
    "is this your first visit": "இது உங்கள் முதல் வருகையா?",
    "do you have your nhs number": "உங்களிடம் என்.எச்.எஸ் எண் உள்ளதா?",
    "would you like to speak to someone": "நீங்கள் யாரிடமாவது பேச விரும்புகிறீர்களா?",
    "your appointment is confirmed": "உங்கள் முன்பதிவு உறுதி செய்யப்பட்டுள்ளது",
    "the doctor will see you now": "மருத்துவர் இப்போது உங்களை பார்ப்பார்",
    "where is your pain": "உங்கள் வலி எங்கே?",
    "how long have you had this": "இது உங்களுக்கு எவ்வளவு காலமாக உள்ளது?",
    "do you have a fever": "உங்களுக்கு காய்ச்சல் உள்ளதா?",
    "are you having difficulty breathing": "உங்களுக்கு மூச்சு விடுவதில் சிரமம் உள்ளதா?",
    "do you feel dizzy or faint": "நீங்கள் தலை சுற்றல் அல்லது மயக்கத்தை உணர்கிறீர்களா?",
    "do you have chest pain": "உங்களுக்கு மார்பு வலி உள்ளதா?",
    "on a scale of 1 to 10 how severe is your pain": "1 முதல் 10 வரையிலான அளவில் உங்கள் வலி எவ்வளவு கடுமையானது?",
    "do you have any allergies": "உங்களுக்கு ஏதேனும் ஒவ்வாமை உள்ளதா?",
    "are you taking any medication": "நீங்கள் ஏதேனும் மருந்து எடுத்துக்கொள்கிறீர்களா?",
    "have you had this before": "இது உங்களுக்கு முன்பு ஏற்பட்டதா?",
    "please wait": "தயவு செய்து காத்திருக்கவும்",
    "thank you": "நன்றி",
    "yes": "ஆம்",
    "no": "இல்லை",
    "i understand": "எனக்கு புரிகிறது",
    "i do not understand": "எனக்கு புரியவில்லை",
}

def lookup_translation(text):
    lower = text.lower().strip()
    if lower in TRANSLATION_DICT:
        return TRANSLATION_DICT[lower]
    for phrase, translation in TRANSLATION_DICT.items():
        if phrase in lower and len(phrase) > 5:
            return translation
    return None

# ============================================================
# SYMPTOM DETECTION (KEEP YOUR FULL LIST)
# ============================================================

SYMPTOM_MAP = {
    "tamil": {
        "nenji vali": "chest pain",
        "moochu varadhu": "breathing difficulty",
        "thalai vali": "headache",
        "kaichal": "fever",
        "vayiru vali": "stomach pain",
        "kaal vali": "leg pain",
        "thalai sutharuthu": "dizziness",
    },
    "hindi": {
        "seene mein dard": "chest pain",
        "saans lene mein takleef": "breathing difficulty",
        "sar dard": "headache",
        "bukhar": "fever",
        "pet dard": "stomach pain",
        "chakkar": "dizziness",
    },
    "polish": {
        "bol klatki": "chest pain",
        "trudnosci z oddychaniem": "breathing difficulty",
        "bol glowy": "headache",
        "goraczka": "fever",
        "bol brzucha": "stomach pain",
    },
    "malayalam": {
        "nenjil vali": "chest pain",
        "shwasam muttunnu": "breathing difficulty",
        "thalavalikkunnu": "headache",
        "pani undu": "fever",
        "vayaril vali": "stomach pain",
    },
}

def detect_symptom(text, lang_code):
    lang_map = {
        "ta": "tamil", "hi": "hindi", "pl": "polish",
        "ml": "malayalam", "ar": "arabic", "ur": "urdu",
        "bn": "bengali", "so": "somali", "ro": "romanian"
    }
    lang_key = lang_map.get(lang_code, "")
    symptoms = SYMPTOM_MAP.get(lang_key, {})
    lower = text.lower().strip()
    for phrase, meaning in symptoms.items():
        if phrase.lower() in lower:
            return meaning
    return None

# ============================================================
# GUIDED PROMPTS
# ============================================================

GUIDED_PROMPTS = {
    "Reception": [
        "Good morning. How can I help you?",
        "Do you have an appointment?",
        "Can I take your name and date of birth?",
        "Please take a seat. The doctor will see you shortly.",
        "Do you need any assistance?",
        "Is this your first visit?",
        "Do you have your NHS number?",
        "Would you like to speak to someone?",
        "Please fill in this form.",
        "Have you been here before?",
        "Please wait, the doctor will call you.",
    ],
    "Appointment": [
        "Your appointment is confirmed.",
        "The doctor will see you now.",
        "Do you have your appointment letter?",
        "Please bring your medication list.",
        "Do you need an interpreter?",
        "Is anyone with you today?",
        "Please wait in the waiting area.",
        "The appointment will take about 15 minutes.",
        "Please follow me to the consultation room.",
        "Your appointment is at [time].",
        "Please arrive 10 minutes early.",
    ],
    "Basic Symptoms": [
        "Where is your pain?",
        "How long have you had this?",
        "Do you have a fever?",
        "Are you having difficulty breathing?",
        "Do you feel dizzy or faint?",
        "Do you have chest pain?",
        "On a scale of 1 to 10, how severe is your pain?",
        "Do you have any allergies?",
        "Are you taking any medication?",
        "Have you had this before?",
        "Do you have any other symptoms?",
        "Does anything make it better or worse?",
        "Is there any bleeding?",
        "When did the symptoms start?",
    ],
}

# ============================================================
# CORE TRANSLATION FUNCTIONS
# ============================================================

def translate_to_english(text, lang_code="auto"):
    builtin = lookup_translation(text)
    if builtin:
        return builtin, None
    try:
        from deep_translator import MyMemoryTranslator
        # Try auto detection
        try:
            result = MyMemoryTranslator(source="auto", target="en-GB").translate(text)
            if result and result.strip().lower() != text.strip().lower():
                return result, None
        except Exception:
            pass
        # Try with language code
        if lang_code and lang_code != "auto":
            mymemory_lang = get_mymemory_lang_code(lang_code)
            try:
                result = MyMemoryTranslator(source=mymemory_lang, target="en-GB").translate(text)
                if result and result.strip().lower() != text.strip().lower():
                    return result, None
            except Exception:
                pass
        # Try all supported languages
        for src in ["ta", "hi", "pl", "ml", "ar", "ur", "bn", "so", "ro"]:
            mymemory_src = get_mymemory_lang_code(src)
            try:
                result = MyMemoryTranslator(source=mymemory_src, target="en-GB").translate(text)
                if result and result.strip().lower() != text.strip().lower():
                    return result, None
            except Exception:
                continue
        return text, None
    except Exception as e:
        return text, str(e)

def translate_to_language(text, target_lang_code):
    if not text:
        return text, None
    
    # Check cache
    cached = get_cached_translation(text, target_lang_code)
    if cached:
        return cached, None
    
    # Check dictionary
    for phrase, translation in TRANSLATION_DICT.items():
        if text.lower() == phrase.lower() or text.lower() in phrase.lower():
            set_cached_translation(text, target_lang_code, translation)
            return translation, None
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            from deep_translator import MyMemoryTranslator
            mymemory_target = get_mymemory_lang_code(target_lang_code)
            translator = MyMemoryTranslator(source="en-GB", target=mymemory_target)
            result = translator.translate(text)
            if result:
                set_cached_translation(text, target_lang_code, result)
                time.sleep(0.3)
                return result, None
        except Exception as e:
            error_msg = str(e).lower()
            if "too many requests" in error_msg or "rate limit" in error_msg:
                wait_time = (attempt + 1) * 2
                time.sleep(wait_time)
                continue
            return None, str(e)
    
    return text, "Translation failed after retries"

# ============================================================
# ROUTES
# ============================================================

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/start_session", methods=["POST"])
def start_session():
    data = request.json
    session.clear()
    session["session_id"] = str(uuid.uuid4())[:8]
    session["context"] = data.get("context")
    session["lang"] = data.get("lang")
    session["lang_code"] = data.get("lang_code")
    session["active"] = True
    
    prompts = GUIDED_PROMPTS.get(session["context"], [])
    lang_code = session.get("lang_code", "ta")
    
    # Pre-translate all prompts in one batch
    translated_prompts = []
    for prompt in prompts:
        translated = None
        for phrase, translation in TRANSLATION_DICT.items():
            if prompt.lower() == phrase.lower():
                translated = translation
                break
        if translated:
            translated_prompts.append(translated)
        else:
            result, _ = translate_to_language(prompt, lang_code)
            translated_prompts.append(result if result else prompt)
    
    session["translated_prompts"] = translated_prompts
    
    return jsonify({
        "status": "ok",
        "session_id": session["session_id"],
        "prompts": prompts,
        "translated_prompts": translated_prompts,
        "context": session["context"],
        "lang": session["lang"],
    })

@app.route("/api/end_session", methods=["POST"])
def end_session():
    session.clear()
    return jsonify({"status": "ok"})

@app.route("/api/translate_staff", methods=["POST"])
def translate_staff():
    data = request.json
    raw_text = data.get("text", "").strip()
    if not raw_text:
        return jsonify({"error": "No text provided"}), 400
    
    # Check cache
    cached = get_cached_translation(raw_text, session.get("lang_code", "ta"))
    if cached:
        return jsonify({
            "original": raw_text,
            "simplified": raw_text,
            "was_simplified": False,
            "translated": cached,
            "lang": session.get("lang", "Tamil"),
            "urgent": False,
        })
    
    # Check dictionary
    for phrase, translation in TRANSLATION_DICT.items():
        if raw_text.lower() == phrase.lower():
            set_cached_translation(raw_text, session.get("lang_code", "ta"), translation)
            return jsonify({
                "original": raw_text,
                "simplified": raw_text,
                "was_simplified": False,
                "translated": translation,
                "lang": session.get("lang", "Tamil"),
                "urgent": False,
            })
    
    simplified, was_simplified = simplify_text(raw_text)
    lang_code = session.get("lang_code", "ta")
    lang_name = session.get("lang", "Tamil")
    
    translated, error = translate_to_language(simplified, lang_code)
    if error:
        return jsonify({"error": error}), 500
    
    return jsonify({
        "original": raw_text,
        "simplified": simplified,
        "was_simplified": was_simplified,
        "translated": translated,
        "lang": lang_name,
        "urgent": False,
    })

@app.route("/api/translate_patient", methods=["POST"])
def translate_patient():
    data = request.json
    text = data.get("text", "").strip()
    if not text:
        return jsonify({"error": "No text provided"}), 400

    lang_name = session.get("lang", "Tamil")
    lang_code = session.get("lang_code", "ta")

    english_text, error = translate_to_english(text, lang_code)
    if error:
        return jsonify({"error": error}), 500

    native_text = text
    try:
        from deep_translator import MyMemoryTranslator
        if english_text and english_text.strip().lower() != text.strip().lower():
            mymemory_target = get_mymemory_lang_code(lang_code)
            converted = MyMemoryTranslator(source="en-GB", target=mymemory_target).translate(english_text)
            if converted and converted.strip() != text.strip():
                native_text = converted
        if native_text == text:
            mymemory_target = get_mymemory_lang_code(lang_code)
            converted2 = MyMemoryTranslator(source="auto", target=mymemory_target).translate(text)
            if converted2 and converted2.strip() != text.strip():
                native_text = converted2
    except Exception:
        native_text = text

    symptom = detect_symptom(text, lang_code)
    medical_alert = needs_medical_consultation(text) or needs_medical_consultation(english_text or "")

    return jsonify({
        "original": text,
        "native": native_text,
        "translated": english_text,
        "lang": lang_name,
        "symptom_detected": symptom,
        "medical_alert": medical_alert,
    })

@app.route("/api/simplify", methods=["POST"])
def simplify_endpoint():
    data = request.json
    text = data.get("text", "")
    simplified, changed = simplify_text(text)
    return jsonify({"simplified": simplified, "changed": changed})

@app.route("/api/session_status")
def session_status():
    return jsonify({
        "active": session.get("active", False),
        "context": session.get("context"),
        "lang": session.get("lang"),
    })

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=10000)
