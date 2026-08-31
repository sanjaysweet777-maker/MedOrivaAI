from flask import Flask, render_template, request, jsonify, session
import uuid
import re
import time
import os

# ============================================================
# APP INITIALIZATION
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(BASE_DIR, 'templates')

app = Flask(__name__, template_folder=template_dir)
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
# LANGUAGE CODE MAPPING
# ============================================================

LANG_MAP = {
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

def get_lang_code(lang_code):
    return LANG_MAP.get(lang_code, "en-GB")

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
# URGENT PHRASES & DETECTION - FIXED
# ============================================================

# ONLY these trigger a medical alert (life-threatening symptoms)
URGENT_SYMPTOMS = [
    # English
    "chest pain", "heart pain", "can't breathe", "cant breathe",
    "difficulty breathing", "not breathing", "bleeding",
    "unconscious", "stroke", "seizure", "collapsed", "heart attack",
    
    # Tamil / Thanglish (chest pain & breathing issues)
    "nenji vali", "moochu varadhu", "iratha", "moochu pidikuthu",
    
    # Hindi (chest pain & breathing issues)
    "seene mein dard", "saans nahi", "khoon", "saans lene mein takleef",
    
    # Polish
    "bol klatki", "trudnosci z oddychaniem",
    
    # Malayalam
    "nenjil vali", "shwasam muttunnu",
]

NEGATION_WORDS = [
    "illai", "illa", "varadhu", "varala", "ila",
    "nahi", "nahin", "nhi", "mat", "na",
    "nie", "brak", "bez",
    "la", "laysa", "mish", "ma",
    "no", "not", "don't", "dont", "never", "none",
]

def is_negative(text):
    lower = text.lower()
    for word in NEGATION_WORDS:
        if word in lower:
            return True
    return False

def needs_medical_consultation(text):
    lower = text.lower()
    # Check if ANY urgent symptom is mentioned
    has_urgent = any(phrase in lower for phrase in URGENT_SYMPTOMS)
    # Check if it's negated (e.g., "no chest pain")
    has_negation = is_negative(text)
    # Only return True if urgent AND not negated
    return has_urgent and not has_negation

# ============================================================
# COMPLETE TRANSLATION DICTIONARY (TAMIL + HINDI + MORE)
# ============================================================

TRANSLATION_DICT = {
    # ======== STAFF PROMPTS - TAMIL ========
    "good morning how can i help you": "காலை வணக்கம். நான் உங்களுக்கு எப்படி உதவ முடியும்?",
    "good morning. how can i help you": "காலை வணக்கம். நான் உங்களுக்கு எப்படி உதவ முடியும்?",
    "do you have an appointment": "உங்களுக்கு முன்பதிவு உள்ளதா?",
    "can i take your name and date of birth": "உங்கள் பெயரையும் பிறந்த தேதியையும் சொல்ல முடியுமா?",
    "please take a seat the doctor will see you shortly": "தயவு செய்து உட்காருங்கள். மருத்துவர் விரைவில் உங்களை பார்ப்பார்.",
    "do you need any assistance": "உங்களுக்கு உதவி தேவையா?",
    "is this your first visit": "இது உங்கள் முதல் வருகையா?",
    "do you have your nhs number": "உங்களிடம் என்.எச்.எஸ் எண் உள்ளதா?",
    "would you like to speak to someone": "நீங்கள் யாரிடமாவது பேச விரும்புகிறீர்களா?",
    "please fill in this form": "தயவு செய்து இந்த படிவத்தை நிரப்பவும்.",
    "have you been here before": "நீங்கள் இங்கு முன்பு வந்திருக்கிறீர்களா?",
    "please wait the doctor will call you": "தயவு செய்து காத்திருக்கவும். மருத்துவர் உங்களை அழைப்பார்.",
    "your appointment is confirmed": "உங்கள் முன்பதிவு உறுதி செய்யப்பட்டுள்ளது.",
    "the doctor will see you now": "மருத்துவர் இப்போது உங்களை பார்ப்பார்.",
    "do you have your appointment letter": "உங்களிடம் முன்பதிவு கடிதம் உள்ளதா?",
    "please bring your medication list": "தயவு செய்து உங்கள் மருந்து பட்டியலை கொண்டு வாருங்கள்.",
    "do you need an interpreter": "உங்களுக்கு மொழிபெயர்ப்பாளர் தேவையா?",
    "is anyone with you today": "இன்று உங்களுடன் யாராவது இருக்கிறார்களா?",
    "please wait in the waiting area": "தயவு செய்து காத்திருக்கும் பகுதியில் காத்திருக்கவும்.",
    "the appointment will take about 15 minutes": "இந்த முன்பதிவு சுமார் 15 நிமிடங்கள் ஆகும்.",
    "please follow me to the consultation room": "தயவு செய்து என்னை பின்பற்றி ஆலோசனை அறைக்கு வாருங்கள்.",
    "your appointment is at time": "உங்கள் முன்பதிவு [நேரம்] அன்று உள்ளது.",
    "please arrive 10 minutes early": "தயவு செய்து 10 நிமிடங்கள் முன்னதாக வந்து சேருங்கள்.",
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
    "do you have any other symptoms": "உங்களுக்கு வேறு ஏதேனும் அறிகுறிகள் உள்ளனவா?",
    "does anything make it better or worse": "ஏதாவது அதை சிறப்பாக அல்லது மோசமாக்குகிறதா?",
    "is there any bleeding": "ஏதேனும் இரத்தப்போக்கு உள்ளதா?",
    "when did the symptoms start": "அறிகுறிகள் எப்போது தொடங்கின?",

    # ======== STAFF PROMPTS - HINDI ========
    "good morning how can i help you": "सुप्रभात। मैं आपकी कैसे मदद कर सकता हूँ?",
    "good morning. how can i help you": "सुप्रभात। मैं आपकी कैसे मदद कर सकता हूँ?",
    "do you have an appointment": "क्या आपका कोई अपॉइंटमेंट है?",
    "can i take your name and date of birth": "क्या मैं आपका नाम और जन्मतिथि ले सकता हूँ?",
    "please take a seat the doctor will see you shortly": "कृपया बैठ जाइए। डॉक्टर जल्द ही आपसे मिलेंगे।",
    "do you need any assistance": "क्या आपको किसी सहायता की आवश्यकता है?",
    "is this your first visit": "क्या यह आपकी पहली यात्रा है?",
    "do you have your nhs number": "क्या आपके पास एनएचएस नंबर है?",
    "would you like to speak to someone": "क्या आप किसी से बात करना चाहेंगे?",
    "please fill in this form": "कृपया यह फॉर्म भरें।",
    "have you been here before": "क्या आप पहले यहाँ आ चुके हैं?",
    "please wait the doctor will call you": "कृपया प्रतीक्षा करें। डॉक्टर आपको बुलाएंगे।",
    "your appointment is confirmed": "आपका अपॉइंटमेंट पुष्टि हो गया है।",
    "the doctor will see you now": "डॉक्टर अब आपसे मिलेंगे।",
    "do you have your appointment letter": "क्या आपके पास अपॉइंटमेंट पत्र है?",
    "please bring your medication list": "कृपया अपनी दवाओं की सूची लाएँ।",
    "do you need an interpreter": "क्या आपको अनुवादक की आवश्यकता है?",
    "is anyone with you today": "क्या आज आपके साथ कोई है?",
    "please wait in the waiting area": "कृपया प्रतीक्षा क्षेत्र में प्रतीक्षा करें।",
    "the appointment will take about 15 minutes": "अपॉइंटमेंट में लगभग 15 मिनट लगेंगे।",
    "please follow me to the consultation room": "कृपया मेरे पीछे परामर्श कक्ष में चलें।",
    "your appointment is at time": "आपका अपॉइंटमेंट [समय] पर है।",
    "please arrive 10 minutes early": "कृपया 10 मिनट पहले आ जाएँ।",
    "where is your pain": "आपको दर्द कहाँ हो रहा है?",
    "how long have you had this": "यह आपको कितने दिनों से है?",
    "do you have a fever": "क्या आपको बुखार है?",
    "are you having difficulty breathing": "क्या आपको सांस लेने में कठिनाई हो रही है?",
    "do you feel dizzy or faint": "क्या आपको चक्कर या बेहोशी महसूस हो रही है?",
    "do you have chest pain": "क्या आपको सीने में दर्द है?",
    "on a scale of 1 to 10 how severe is your pain": "1 से 10 के पैमाने पर आपका दर्द कितना गंभीर है?",
    "do you have any allergies": "क्या आपको कोई एलर्जी है?",
    "are you taking any medication": "क्या आप कोई दवा ले रहे हैं?",
    "have you had this before": "क्या आपको यह पहले भी हुआ है?",
    "do you have any other symptoms": "क्या आपको कोई अन्य लक्षण हैं?",
    "does anything make it better or worse": "क्या किसी चीज़ से यह बेहतर या बदतर होता है?",
    "is there any bleeding": "क्या कोई रक्तस्राव है?",
    "when did the symptoms start": "लक्षण कब शुरू हुए?",

    # ======== TAMIL PATIENT RESPONSES ========
    "enaku nenji vali irukku": "I have chest pain",
    "enaku nenji vali iruku": "I have chest pain",
    "nenji vali irukku": "I have chest pain",
    "nenji vali iruku": "I have chest pain",
    "nenji vali": "chest pain",
    "enaku moochu varadhu": "I cannot breathe properly",
    "moochu varadhu": "I cannot breathe properly",
    "moochu pidikuthu": "I am having difficulty breathing",
    "enaku thalai vali irukku": "I have a headache",
    "enaku thalai valikuthu": "I have a headache",
    "thalai vali irukku": "I have a headache",
    "thalai valikuthu": "my head is hurting",
    "enaku kaichal irukku": "I have a fever",
    "kaichal irukku": "I have a fever",
    "enaku vayiru vali irukku": "I have stomach pain",
    "vayiru vali irukku": "I have stomach pain",
    "thalai sutharuthu": "I feel dizzy",
    "vanthi varuthu": "I feel like vomiting",
    "romba vali irukku": "I have severe pain",
    "enala moochu vida mudiyala": "I cannot breathe",
    "moochu varala": "I cannot breathe",

    # ======== TAMIL NEGATIVE ========
    "enaku nenji vali illai": "I do not have chest pain",
    "nenji vali illai": "I do not have chest pain",
    "enaku thalai vali illai": "I do not have a headache",
    "thalai vali illai": "I do not have a headache",
    "kaichal illai": "I do not have a fever",
    "vali illai": "I have no pain",
    "moochu varadhu illai": "I have no breathing difficulty",

    # ======== TAMIL GENERAL ========
    "aama": "yes",
    "illai": "no",
    "seri": "okay",
    "puriyuthu": "I understand",
    "puriyala": "I do not understand",
    "help pannunga": "please help me",
    "nalla irukken": "I am fine",

    # ======== HINDI PATIENT RESPONSES ========
    "mujhe chest mein dard hai": "I have chest pain",
    "seene mein dard hai": "I have chest pain",
    "mujhe seene mein dard hai": "I have chest pain",
    "sar dard hai": "I have a headache",
    "mujhe sar dard hai": "I have a headache",
    "bukhar hai": "I have a fever",
    "mujhe bukhar hai": "I have a fever",
    "pet mein dard hai": "I have stomach pain",
    "mujhe pet mein dard hai": "I have stomach pain",
    "saans lene mein takleef hai": "I have difficulty breathing",
    "saans nahi aa rahi": "I cannot breathe",
    "chakkar aa raha hai": "I feel dizzy",
    "bahut dard hai": "I have severe pain",
    "mere pair mein dard ho raha hai": "I have leg pain",
    "mere haath mein dard hai": "I have arm pain",
    "mere gale mein dard hai": "I have throat pain",
    "mujhe dard hai": "I have pain",

    # ======== HINDI NEGATIVE ========
    "chest mein dard nahi hai": "I do not have chest pain",
    "seene mein dard nahi hai": "I do not have chest pain",
    "sar dard nahi hai": "I do not have a headache",
    "bukhar nahi hai": "I do not have a fever",
    "pet mein dard nahi hai": "I do not have stomach pain",
    "dard nahi hai": "I have no pain",
    "mere pair mein dard nahi hai": "I do not have leg pain",

    # ======== HINDI GENERAL ========
    "theek hoon": "I am fine",
    "haan": "yes",
    "nahi": "no",
    "theek hai": "okay",
    "samajh nahi aaya": "I do not understand",
    "samajh aa gaya": "I understand",
    "meri madad karo": "please help me",

    # ======== POLISH ========
    "mam bol w klatce piersiowej": "I have chest pain",
    "bol glowy": "I have a headache",
    "mam goraczke": "I have a fever",
    "mam bol brzucha": "I have stomach pain",
    "trudno mi oddychac": "I have difficulty breathing",
    "nie moge oddychac": "I cannot breathe",
    "bardzo boli": "I have severe pain",
    "nie mam bolu w klatce": "I do not have chest pain",
    "nie mam goraczki": "I do not have a fever",
    "czuje sie dobrze": "I am fine",
    "tak": "yes",
    "nie": "no",

    # ======== MALAYALAM ========
    "nenjil vali undu": "I have chest pain",
    "thalavalikkunnu": "I have a headache",
    "pani undu": "I have a fever",
    "vayaril vali undu": "I have stomach pain",
    "shwasam muttunnu": "I am having difficulty breathing",
    "valiya vali undu": "I have severe pain",
    "nenjil vali illa": "I do not have chest pain",
    "pani illa": "I do not have a fever",
    "vali illa": "I have no pain",
    "athe": "yes",
    "alla": "no",
}

def lookup_translation(text):
    text_lower = text.lower().strip()
    # Exact match
    if text_lower in TRANSLATION_DICT:
        return TRANSLATION_DICT[text_lower]
    # Partial match
    best_match = None
    best_length = 0
    for phrase, translation in TRANSLATION_DICT.items():
        if phrase in text_lower and len(phrase) > best_length:
            best_match = translation
            best_length = len(phrase)
    return best_match

# ============================================================
# SYMPTOM DETECTION - WITH HINDI
# ============================================================

SYMPTOM_MAP = {
    "ta": {
        "nenji vali": "chest pain",
        "moochu varadhu": "breathing difficulty",
        "thalai vali": "headache",
        "kaichal": "fever",
        "vayiru vali": "stomach pain",
        "thalai sutharuthu": "dizziness",
        "vanthi": "vomiting",
    },
    "hi": {
        "seene mein dard": "chest pain",
        "saans lene mein takleef": "breathing difficulty",
        "saans nahi": "breathing difficulty",
        "sar dard": "headache",
        "bukhar": "fever",
        "pet dard": "stomach pain",
        "chakkar": "dizziness",
        "ulti": "vomiting",
        "pair mein dard": "leg pain",
        "haath mein dard": "arm pain",
    },
    "pl": {
        "bol klatki": "chest pain",
        "trudnosci z oddychaniem": "breathing difficulty",
        "bol glowy": "headache",
        "goraczka": "fever",
        "bol brzucha": "stomach pain",
    },
    "ml": {
        "nenjil vali": "chest pain",
        "shwasam muttunnu": "breathing difficulty",
        "thalavalikkunnu": "headache",
        "pani undu": "fever",
        "vayaril vali": "stomach pain",
    },
}

def detect_symptom(text, lang_code):
    symptoms = SYMPTOM_MAP.get(lang_code, {})
    lower = text.lower().strip()
    for phrase, meaning in symptoms.items():
        if phrase in lower:
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
        "Please wait. The doctor will call you.",
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
# TRANSLATION FUNCTIONS
# ============================================================

def translate_to_english(text, lang_code="auto"):
    builtin = lookup_translation(text)
    if builtin:
        return builtin, None

    try:
        from deep_translator import MyMemoryTranslator
        try:
            result = MyMemoryTranslator(source="auto", target="en-GB").translate(text)
            if result and result.strip().lower() != text.strip().lower():
                return result, None
        except:
            pass
        if lang_code and lang_code != "auto":
            try:
                target = get_lang_code(lang_code)
                result = MyMemoryTranslator(source=target, target="en-GB").translate(text)
                if result and result.strip().lower() != text.strip().lower():
                    return result, None
            except:
                pass
        for src in ["ta", "hi", "pl", "ml", "ar", "ur", "bn", "so", "ro"]:
            try:
                target = get_lang_code(src)
                result = MyMemoryTranslator(source=target, target="en-GB").translate(text)
                if result and result.strip().lower() != text.strip().lower():
                    return result, None
            except:
                continue
        return text, None
    except:
        return text, "Translation service unavailable"

def translate_to_language(text, target_lang_code):
    if not text:
        return text, None

    cached = get_cached_translation(text, target_lang_code)
    if cached:
        return cached, None

    builtin = lookup_translation(text)
    if builtin:
        set_cached_translation(text, target_lang_code, builtin)
        return builtin, None

    try:
        from deep_translator import MyMemoryTranslator
        target = get_lang_code(target_lang_code)
        for attempt in range(3):
            try:
                result = MyMemoryTranslator(source="en-GB", target=target).translate(text)
                if result:
                    set_cached_translation(text, target_lang_code, result)
                    return result, None
            except Exception as e:
                if "too many requests" in str(e).lower():
                    time.sleep((attempt + 1) * 2)
                    continue
                return None, str(e)
        return text, None
    except:
        return text, "Translation service unavailable"

# ============================================================
# ROUTES
# ============================================================

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/ping", methods=["GET"])
def ping():
    return jsonify({"status": "Flask is running", "session": dict(session)})

@app.route("/api/start_session", methods=["POST"])
def start_session():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        session.clear()
        session["session_id"] = str(uuid.uuid4())[:8]
        session["context"] = data.get("context", "Reception")
        session["lang"] = data.get("lang", "Tamil")
        session["lang_code"] = data.get("lang_code", "ta")
        session["active"] = True

        prompts = GUIDED_PROMPTS.get(session["context"], [])

        return jsonify({
            "status": "ok",
            "session_id": session["session_id"],
            "prompts": prompts,
            "context": session["context"],
            "lang": session["lang"],
        })

    except Exception as e:
        print(f"Error in start_session: {str(e)}")
        return jsonify({
            "status": "error",
            "error": f"Could not start session: {str(e)}"
        }), 500

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

    lang_code = session.get("lang_code", "ta")
    lang_name = session.get("lang", "Tamil")

    # Check dictionary first (exact match)
    for phrase, translation in TRANSLATION_DICT.items():
        if raw_text.lower() == phrase.lower():
            set_cached_translation(raw_text, lang_code, translation)
            return jsonify({
                "original": raw_text,
                "simplified": raw_text,
                "was_simplified": False,
                "translated": translation,
                "lang": lang_name,
                "urgent": False,
            })

    # Try partial match
    lookup = lookup_translation(raw_text)
    if lookup:
        set_cached_translation(raw_text, lang_code, lookup)
        return jsonify({
            "original": raw_text,
            "simplified": raw_text,
            "was_simplified": False,
            "translated": lookup,
            "lang": lang_name,
            "urgent": False,
        })

    # Fall back to API
    simplified, was_simplified = simplify_text(raw_text)
    translated, error = translate_to_language(simplified, lang_code)

    if error:
        return jsonify({"error": "Could not translate. Please try again."}), 500

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

    lang_code = session.get("lang_code", "ta")
    lang_name = session.get("lang", "Tamil")

    english_text, error = translate_to_english(text, lang_code)
    if error:
        return jsonify({"error": "Could not translate. Please try again."}), 500

    symptom = detect_symptom(text, lang_code)
    medical_alert = needs_medical_consultation(text) or needs_medical_consultation(english_text or "")

    return jsonify({
        "original": text,
        "native": text,
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
