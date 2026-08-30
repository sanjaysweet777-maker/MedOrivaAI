from flask import Flask, render_template, request, jsonify, session
import uuid
import re

app = Flask(__name__)
app.secret_key = "medoriva-mvp-secret-key"

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

URGENT_PHRASES = [
    "chest pain", "chest hurt", "can't breathe", "cant breathe",
    "difficulty breathing", "heart pain", "bleeding heavily",
    "unconscious", "stroke", "seizure", "collapsed", "not breathing",
    "nenji vali", "moochu varadhu", "iratha", "padaippu",
    "seene mein dard", "saans nahi", "khoon", "behosh",
    "bol klatki", "trudnosci z oddychaniem", "krwawienie",
    "nenjil vali", "maarbu vali",
]

NEGATION_WORDS = [
    "illai", "illa", "kidaiyathu", "varadhu", "varala", "ila",
    "nahi", "nahin", "mat", "nhi",
    "nie", "brak",
    "la", "laysa", "mish",
    "no", "not", "don't", "dont", "do not", "never", "none",
    "cannot", "can't", "cant", "doesn't", "doesnt", "does not",
    "alla", "allatha", "ille",
]

def is_negative(text):
    lower = text.lower()
    for word in NEGATION_WORDS:
        pattern = r'\b' + re.escape(word) + r'\b'
        if re.search(pattern, lower):
            return True
    return False

URGENT_SYMPTOMS = [
    "chest pain", "chest hurt", "heart pain", "cant breathe", "can't breathe",
    "difficulty breathing", "not breathing", "bleeding heavily", "unconscious",
    "stroke", "seizure", "collapsed", "severe pain", "very bad pain",
    "nenji vali", "moochu varadhu", "moochu pidikuthu", "iratha",
    "seene mein dard", "saans nahi", "bahut dard", "behosh", "khoon",
    "bol klatki", "trudnosci z oddychaniem", "krwawienie", "bardzo boli",
    "nenjil vali", "maarbu vali", "ശ്വാസം", "നെഞ്ചുവേദന",
]

def needs_medical_consultation(text):
    lower = text.lower()
    has_urgent = any(phrase in lower for phrase in URGENT_SYMPTOMS)
    has_negation = is_negative(text)
    return has_urgent and not has_negation

TRANSLATION_DICT = {
    # Tamil / Thanglish — positive
    "enaku nenji vali irukku": "I have chest pain",
    "enaku nenji vali iruku": "I have chest pain",
    "ennaku nenji vali irukku": "I have chest pain",
    "nenji vali irukku": "I have chest pain",
    "nenji vali iruku": "I have chest pain",
    "nenji valikuthu": "I have chest pain",
    "en nenji valikuthu": "my chest is hurting",
    "nenji vali": "chest pain",
    "enaku moochu varadhu": "I cannot breathe properly",
    "moochu varadhu": "I cannot breathe properly",
    "moochu pidikuthu": "I am having difficulty breathing",
    "enaku thalai vali irukku": "I have a headache",
    "thalai vali irukku": "I have a headache",
    "thalai vali iruku": "I have a headache",
    "thalai valikuthu": "my head is hurting",
    "enaku thalai vali": "I have a headache",
    "enaku kaichal irukku": "I have a fever",
    "kaichal irukku": "I have a fever",
    "kaichal iruku": "I have a fever",
    "enaku kaichal": "I have a fever",
    "kaichal varuthu": "I have a fever",
    "enaku vayiru vali irukku": "I have stomach pain",
    "vayiru vali irukku": "I have stomach pain",
    "vayiru vali iruku": "I have stomach pain",
    "vayiru valikuthu": "my stomach is hurting",
    "kaal vali irukku": "I have leg pain",
    "kaal vali iruku": "I have leg pain",
    "kai vali irukku": "I have arm pain",
    "thalai sutharuthu": "I feel dizzy",
    "vanthi varuthu": "I feel like vomiting",
    "romba vali irukku": "I have severe pain",
    "vali irukku": "I have pain",
    "vali iruku": "I have pain",
    # Tamil / Thanglish — negative
    "enaku nenji vali illai": "I do not have chest pain",
    "nenji vali illai": "I do not have chest pain",
    "nenji vali illa": "I do not have chest pain",
    "moochu varadhu illai": "I have no breathing difficulty",
    "thalai vali illai": "I do not have a headache",
    "thalai vali illa": "I do not have a headache",
    "kaichal illai": "I do not have a fever",
    "kaichal illa": "I do not have a fever",
    "enaku kaichal illai": "I do not have a fever",
    "vayiru vali illai": "I do not have stomach pain",
    "vali illai": "I have no pain",
    "vali illa": "I have no pain",
    # Tamil general
    "aama": "yes",
    "illai": "no",
    "seri": "okay",
    "puriyuthu": "I understand",
    "puriyala": "I do not understand",
    "theriyala": "I do not know",
    "help pannunga": "please help me",
    "nalla irukken": "I am fine",
    "jolly ah irukken": "I am feeling well",
    # Hindi — positive
    "mujhe chest mein dard hai": "I have chest pain",
    "seene mein dard hai": "I have chest pain",
    "mujhe seene mein dard hai": "I have chest pain",
    "sar dard hai": "I have a headache",
    "mujhe sar dard hai": "I have a headache",
    "bukhar hai": "I have a fever",
    "mujhe bukhar hai": "I have a fever",
    "pet mein dard hai": "I have stomach pain",
    "saans lene mein takleef hai": "I have difficulty breathing",
    "chakkar aa raha hai": "I feel dizzy",
    "ulti aa rahi hai": "I feel like vomiting",
    "bahut dard hai": "I have severe pain",
    "dard hai": "I have pain",
    # Hindi — negative
    "chest mein dard nahi hai": "I do not have chest pain",
    "seene mein dard nahi": "I do not have chest pain",
    "sar dard nahi hai": "I do not have a headache",
    "bukhar nahi hai": "I do not have a fever",
    "pet mein dard nahi": "I do not have stomach pain",
    "dard nahi hai": "I have no pain",
    "theek hoon": "I am fine",
    "haan": "yes",
    "nahi": "no",
    "theek hai": "okay",
    "samajh nahi aaya": "I do not understand",
    # Polish — positive
    "mam bol w klatce piersiowej": "I have chest pain",
    "bol glowy": "I have a headache",
    "mam goraczke": "I have a fever",
    "mam bol brzucha": "I have stomach pain",
    "trudno mi oddychac": "I have difficulty breathing",
    "krecimi sie w glowie": "I feel dizzy",
    "bardzo boli": "it hurts a lot",
    "boli mnie": "I have pain",
    # Polish — negative
    "nie mam bolu w klatce": "I do not have chest pain",
    "nie mam bolu glowy": "I do not have a headache",
    "nie mam goraczki": "I do not have a fever",
    "nie boli": "it does not hurt",
    "czuje sie dobrze": "I feel fine",
    "tak": "yes",
    "nie": "no",
    "nie rozumiem": "I do not understand",
    # Malayalam — positive
    "എനിക്ക് നെഞ്ചുവേദന ഉണ്ട്": "I have chest pain",
    "nenjil vali undu": "I have chest pain",
    "nenjil vali und": "I have chest pain",
    "ente nenjil valikkunnu": "my chest is hurting",
    "eniku nenjil vali und": "I have chest pain",
    "eniku thalavalikkunnu": "I have a headache",
    "thalavalikkunnu": "I have a headache",
    "thala valikkunnu": "my head is hurting",
    "eniku pani undu": "I have a fever",
    "pani undu": "I have a fever",
    "eniku vayaril vali": "I have stomach pain",
    "vayaril vali undu": "I have stomach pain",
    "shwasam muttunnu": "I am having difficulty breathing",
    "thalayan thonum": "I feel dizzy",
    "otti varunnu": "I feel like vomiting",
    "valiya vali undu": "I have severe pain",
    "vali undu": "I have pain",
    # Malayalam — negative
    "eniku nenjil vali illa": "I do not have chest pain",
    "nenjil vali illa": "I do not have chest pain",
    "thalavalikkunilla": "I do not have a headache",
    "pani illa": "I do not have a fever",
    "eniku pani illa": "I do not have a fever",
    "vayaril vali illa": "I do not have stomach pain",
    "vali illa": "I have no pain",
    "saukaryamayi irikkunnu": "I am fine",
    "athe": "yes",
    "alla": "no",
    "manasilayilla": "I do not understand",
}

def lookup_translation(text):
    lower = text.lower().strip()
    if lower in TRANSLATION_DICT:
        return TRANSLATION_DICT[lower]
    best_match = None
    best_length = 0
    for phrase, translation in TRANSLATION_DICT.items():
        if phrase in lower and len(phrase) > best_length:
            best_match = translation
            best_length = len(phrase)
    return best_match

SYMPTOM_MAP = {
    "tamil": {
        "nenji vali iruku": "chest pain", "nenji vali irukku": "chest pain",
        "nenji vali": "chest pain", "moochu varadhu": "breathing difficulty",
        "thalai vali": "headache", "kaichal": "fever",
        "vayiru vali": "stomach pain", "kaal vali": "leg pain",
        "thalai sutharuthu": "dizziness",
    },
    "hindi": {
        "seene mein dard": "chest pain", "saans lene mein takleef": "breathing difficulty",
        "sar dard": "headache", "bukhar": "fever",
        "pet dard": "stomach pain", "chakkar": "dizziness",
    },
    "polish": {
        "bol klatki": "chest pain", "trudnosci z oddychaniem": "breathing difficulty",
        "bol glowy": "headache", "goraczka": "fever", "bol brzucha": "stomach pain",
    },
    "malayalam": {
        "nenjil vali": "chest pain", "nenjil vali undu": "chest pain",
        "shwasam muttunnu": "breathing difficulty",
        "thalavalikkunnu": "headache", "pani undu": "fever",
        "vayaril vali": "stomach pain", "thalayan thonum": "dizziness",
    },
}

def detect_symptom(text, lang_code):
    lang_map = {"ta": "tamil", "hi": "hindi", "pl": "polish", "ml": "malayalam"}
    lang_key = lang_map.get(lang_code, "")
    symptoms = SYMPTOM_MAP.get(lang_key, {})
    lower = text.lower().strip()
    for phrase, meaning in symptoms.items():
        if phrase.lower() in lower:
            return meaning
    return None

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
    ],
}

# ============================================================
# FIXED: Using MyMemoryTranslator instead of GoogleTranslator
# ============================================================

def translate_to_english(text, lang_code="auto"):
    builtin = lookup_translation(text)
    if builtin:
        return builtin, None
    try:
        from deep_translator import MyMemoryTranslator
        try:
            result = MyMemoryTranslator(source="auto", target="en").translate(text)
            if result and result.strip().lower() != text.strip().lower():
                return result, None
        except Exception:
            pass
        if lang_code and lang_code != "auto":
            try:
                result = MyMemoryTranslator(source=lang_code, target="en").translate(text)
                if result and result.strip().lower() != text.strip().lower():
                    return result, None
            except Exception:
                pass
        for src in ["ta", "hi", "pl", "ar", "ur", "bn", "so", "ro", "ml"]:
            try:
                result = MyMemoryTranslator(source=src, target="en").translate(text)
                if result and result.strip().lower() != text.strip().lower():
                    return result, None
            except Exception:
                continue
        return text, None
    except ImportError:
        return text, "deep-translator not installed"
    except Exception as e:
        return text, str(e)

def translate_to_language(text, target_lang_code):
    try:
        from deep_translator import MyMemoryTranslator
        result = MyMemoryTranslator(source="en", target=target_lang_code).translate(text)
        return result, None
    except Exception as e:
        return None, str(e)

def convert_to_native_script(text, lang_code):
    try:
        from deep_translator import MyMemoryTranslator
        english, _ = translate_to_english(text, lang_code)
        if not english or english.strip().lower() == text.strip().lower():
            return text
        native = MyMemoryTranslator(source="en", target=lang_code).translate(english)
        if native and native.strip() != text.strip():
            return native
        return text
    except Exception:
        return text

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
    return jsonify({
        "status": "ok",
        "session_id": session["session_id"],
        "prompts": prompts,
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

    # 1. Translate to English for staff
    english_text, error = translate_to_english(text, lang_code)
    if error:
        return jsonify({"error": error}), 500

    # 2. Convert patient input to proper native script
    native_text = text
    try:
        from deep_translator import MyMemoryTranslator
        if english_text and english_text.strip().lower() != text.strip().lower():
            converted = MyMemoryTranslator(source="en", target=lang_code).translate(english_text)
            if converted and converted.strip() != text.strip():
                native_text = converted
        if native_text == text:
            converted2 = MyMemoryTranslator(source="auto", target=lang_code).translate(text)
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
