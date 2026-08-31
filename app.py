from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import uuid
import re
import os

# ============================================================
# APP INITIALIZATION & SECURITY CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(BASE_DIR, 'templates')

app = Flask(__name__, template_folder=template_dir)
app.secret_key = os.environ.get("SECRET_KEY", "medoriva-mvp-secret-key-2026")
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

# ============================================================
# FLASK-LOGIN AUTHENTICATION
# ============================================================

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = "Please log in to access MedOriva AI."

@login_manager.unauthorized_handler
def unauthorized():
    if request.path.startswith('/api/'):
        return jsonify({"error": "Unauthorized", "message": "Please log in to proceed."}), 401
    return redirect(url_for('login', next=request.path))

DEMO_EMAIL = "demo@medoriva.com"
DEMO_PASSWORD = "medoriva2026"

class User(UserMixin):
    def __init__(self, email):
        self.id = email.strip().lower()
        self.email = email.strip().lower()

@login_manager.user_loader
def load_user(user_id):
    if user_id and user_id.strip().lower() == DEMO_EMAIL.lower():
        return User(user_id)
    return None

# ============================================================
# CACHE & NORMALIZATION UTILITIES
# ============================================================

translation_cache = {}

def normalize_text(text):
    """Strips punctuation, lowercases, and normalizes whitespaces."""
    if not text:
        return ""
    cleaned = re.sub(r'[^\w\s]', ' ', str(text).lower())
    return " ".join(cleaned.split())

def is_native_script(text):
    """Detects if string contains non-Latin scripts (Tamil, Arabic, Devanagari, etc.)."""
    if not text:
        return False
    return any(ord(char) > 0x0590 for char in text)

def get_cached_translation(text, target_lang):
    cache_key = f"{normalize_text(text)}_{target_lang}"
    return translation_cache.get(cache_key)

def set_cached_translation(text, target_lang, result):
    cache_key = f"{normalize_text(text)}_{target_lang}"
    translation_cache[cache_key] = result

def reset_translation_session():
    """Clears translation session variables while preserving user authentication."""
    keys_to_clear = ["session_id", "context", "lang", "lang_code", "active"]
    for key in keys_to_clear:
        session.pop(key, None)

LANG_MAP = {
    "ta": "ta", "hi": "hi", "ml": "ml", "bn": "bn",
    "ur": "ur", "ar": "ar", "pl": "pl", "so": "so", "ro": "ro",
}

def get_clean_lang_code(lang_code):
    if not lang_code:
        return "en"
    return LANG_MAP.get(lang_code.lower()[:2], lang_code.lower()[:2])

# ============================================================
# CLINICAL SIMPLIFICATION RULES
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
    (r"hypertension", "high blood pressure"),
    (r"hypotension", "low blood pressure"),
    (r"myocardial\s+infarction", "heart attack"),
    (r"cerebrovascular\s+accident", "stroke"),
    (r"dyspnea", "shortness of breath"),
    (r"fracture", "broken bone"),
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
# NEGATION PATTERNS & TRIAGE ENGINE
# ============================================================

NEGATION_PATTERNS = {
    "ta": [
        "illai", "illa", "varadhu", "varala", "ila", "kidayathu", "illamal", 
        "இல்லை", "இல்ல", "கிடையாது", "வராது", "இல்லாமல்", "குறைவு"
    ],
    "hi": [
        "nahi", "nahin", "nhi", "mat", "na", "bina", "kuch nahi", 
        "नहीं", "ना", "मत", "बिना", "कुछ नहीं", "नहीं है"
    ],
    "ml": [
        "illa", "alla", "illathe", "illaatha", "othiri illa", 
        "ഇല്ല", "അല്ല", "ഇല്ലാതെ", "ഇല്ലായ്മ"
    ],
    "pl": [
        "nie", "brak", "bez", "nie ma", "ani", "zadnych", "nie czuje", "nigdy"
    ],
    "ar": [
        "la", "laysa", "mish", "ma", "bidun", "kalla", 
        "لا", "ليس", "ما", "مش", "بدون", "كلا", "غير"
    ],
    "ur": [
        "nahi", "nahin", "na", "bina", "baghair", 
        "نہیں", "نہ", "بغیر", "کوئی نہیں"
    ],
    "bn": [
        "na", "ni", "nay", "chara", "nei", 
        "না", "নেই", "নয়", "ছাড়া", "নাই"
    ],
    "so": [
        "ma", "maya", "ma jiro", "ma qabo", "aan", "waxba", "ma hayo"
    ],
    "ro": [
        "nu", "nici", "fara", "n-am", "nu am", "deloc", "nimic"
    ],
    "en": [
        "no", "not", "dont", "don't", "doesnt", "doesn't", "denies", "denied", 
        "without", "never", "didnt", "didn't", "free of", "negative", "none", "no pain"
    ]
}

URGENT_SYMPTOMS_CONFIG = {
    "chest pain": [
        "chest pain", "heart pain", "heart attack", "crushing chest", "tight chest",
        "nenji vali", "nenju vali", "seene mein dard", "chhati mein dard", "nenjil vali", 
        "bol klatki", "bol w klatce", "ألم في الصدر", "وجع قلب", "سینے میں درد", "دل میں درد", 
        "বুকে ব্যথা", "xanuun laabta", "durere in piept", "நெஞ்சு வலி", "மார் வலி", "सीने में दर्द"
    ],
    "breathing difficulty": [
        "can't breathe", "cant breathe", "difficulty breathing", "trouble breathing", 
        "shortness of breath", "gasping", "suffocating", "breathless",
        "moochu varadhu", "moochu pidikuthu", "moochu thinaral", "saans nahi", 
        "saans lene mein takleef", "dam ghutna", "shwasam muttunnu", "trudnosci z oddychaniem", 
        "duszno", "صعوبة في التنفس", "ضيق تنفس", "سانس لینے میں دشواری", "دم گھٹنا", 
        "শ্বাস নিতে কষ্ট", "দম বন্ধ", "neefsasho dhib", "neefta igu dhegaysa", 
        "dificultate de respiratie", "lipsa de aer", "மூச்சு திணறல்", "மூச்சு விட முடியவில்லை", 
        "सांस फूलना", "सांस लेने में दिक्कत"
    ],
    "bleeding": [
        "bleeding", "severe blood", "loss of blood", "coughing blood", "vomiting blood",
        "iratham", "iratha pokku", "khoon", "khoon behna", "raktham", "krwawienie", "krwotok",
        "نزيف", "دم", "خون", "خون بہنا", "রক্তপাত", "রক্ত পড়ছে", "dhiig", "dhiig bax",
        "sângerare", "hemoragie", "இரத்தப்போக்கு", "இரத்தம் வருகிறது", "रक्तस्राव", "खून आ रहा है"
    ],
    "unconscious": [
        "unconscious", "passed out", "collapsed", "fainted", "seizure", "stroke", "blackout",
        "mayakkam", "surukku vizhunthan", "behosh", "chakkar aakar behosh", "bodhakshayam",
        "stracil przytomnosc", "omdlenie", "ataki padaczkowe", "إغماء", "فقدان الوعي", "جلطة",
        "بے ہوش", "دورہ", "অজ্ঞান", "খিঁচুনি", "miyir beel", "suuxdin", "leșin", "inconștient",
        "convulsii", "மயக்கம்", "வலிப்பு", "बेहोश", "दौरा"
    ],
}

def detect_negation(text, lang_code=None):
    norm = f" {normalize_text(text)} "
    tokens = norm.split()
    
    if lang_code and lang_code in NEGATION_PATTERNS:
        for word in NEGATION_PATTERNS[lang_code]:
            clean_word = normalize_text(word)
            if f" {clean_word} " in norm or clean_word in tokens:
                return True

    for word in NEGATION_PATTERNS["en"]:
        if f" {word} " in norm or word in tokens:
            return True

    return False

def evaluate_medical_triage(original_text, english_text, lang_code):
    combined_text = f"{normalize_text(original_text)} {normalize_text(english_text)}"
    
    is_neg = detect_negation(original_text, lang_code) or detect_negation(english_text, "en")
    
    detected_symptom = None
    is_urgent = False
    
    for symptom_name, phrase_list in URGENT_SYMPTOMS_CONFIG.items():
        for phrase in phrase_list:
            if normalize_text(phrase) in combined_text:
                detected_symptom = symptom_name
                is_urgent = True
                break
        if is_urgent:
            break
            
    medical_alert = bool(is_urgent and not is_neg)
    
    return {
        "symptom_detected": detected_symptom,
        "is_negative": is_neg,
        "medical_alert": medical_alert
    }

# ============================================================
# MASTER CLINICAL VOCABULARY & PHRASEBOOK
# Format: { lang_code: { normalized_key: (English, NativeScript, is_neg, symptom) } }
# ============================================================

CLINICAL_DICTIONARY = {
    "ta": {
        # --- Staff Guided Prompts ---
        "good morning how can i help you": ("Good morning. How can I help you?", "காலை வணக்கம். நான் உங்களுக்கு எப்படி உதவ முடியும்?", False, None),
        "do you have an appointment": ("Do you have an appointment?", "உங்களுக்கு முன்பதிவு உள்ளதா?", False, None),
        "can i take your name and date of birth": ("Can I take your name and date of birth?", "உங்கள் பெயரையும் பிறந்த தேதியையும் சொல்ல முடியுமா?", False, None),
        "please take a seat the doctor will see you shortly": ("Please take a seat. The doctor will see you shortly.", "தயவு செய்து உட்காருங்கள். மருத்துவர் விரைவில் உங்களை பார்ப்பார்.", False, None),
        "do you need any assistance": ("Do you need any assistance?", "உங்களுக்கு உதவி தேவையா?", False, None),
        "is this your first visit": ("Is this your first visit?", "இது உங்கள் முதல் வருகையா?", False, None),
        "do you have your nhs number": ("Do you have your NHS number?", "உங்களிடம் என்.எச்.எஸ் எண் உள்ளதா?", False, None),
        "would you like to speak to someone": ("Would you like to speak to someone?", "நீங்கள் யாரிடமாவது பேச விரும்புகிறீர்களா?", False, None),
        "please fill in this form": ("Please fill in this form.", "தயவு செய்து இந்த படிவத்தை நிரப்பவும்.", False, None),
        "have you been here before": ("Have you been here before?", "நீங்கள் இங்கு முன்பு வந்திருக்கிறீர்களா?", False, None),
        "please wait the doctor will call you": ("Please wait. The doctor will call you.", "தயவு செய்து காத்திருக்கவும். மருத்துவர் உங்களை அழைப்பார்.", False, None),
        "your appointment is confirmed": ("Your appointment is confirmed.", "உங்கள் முன்பதிவு உறுதி செய்யப்பட்டுள்ளது.", False, None),
        "the doctor will see you now": ("The doctor will see you now.", "மருத்துவர் இப்போது உங்களை பார்ப்பார்.", False, None),
        "do you have your appointment letter": ("Do you have your appointment letter?", "உங்களிடம் முன்பதிவு கடிதம் உள்ளதா?", False, None),
        "please bring your medication list": ("Please bring your medication list.", "உங்கள் மருந்து பட்டியலை கொண்டு வாருங்கள்.", False, None),
        "do you need an interpreter": ("Do you need an interpreter?", "உங்களுக்கு மொழிபெயர்ப்பாளர் தேவையா?", False, None),
        "is anyone with you today": ("Is anyone with you today?", "இன்று உங்களுடன் யாராவது வந்துள்ளார்களா?", False, None),
        "please wait in the waiting area": ("Please wait in the waiting area.", "தயவு செய்து காத்திருப்பு அறையில் காத்திருக்கவும்.", False, None),
        "the appointment will take about 15 minutes": ("The appointment will take about 15 minutes.", "இந்த சந்திப்பு சுமார் 15 நிமிடங்கள் எடுக்கும்.", False, None),
        "please follow me to the consultation room": ("Please follow me to the consultation room.", "தயவு செய்து என்னை மருத்துவ ஆலோசனை அறைக்கு பின்தொடரவும்.", False, None),
        "where is your pain": ("Where is your pain?", "உங்கள் வலி எங்கே இருக்கிறது?", False, None),
        "how long have you had this": ("How long have you had this?", "இது உங்களுக்கு எவ்வளவு காலமாக உள்ளது?", False, None),
        "do you have a fever": ("Do you have a fever?", "உங்களுக்கு காய்ச்சல் உள்ளதா?", False, None),
        "are you having difficulty breathing": ("Are you having difficulty breathing?", "உங்களுக்கு மூச்சு விடுவதில் சிரமம் உள்ளதா?", False, "breathing difficulty"),
        "do you feel dizzy or faint": ("Do you feel dizzy or faint?", "நீங்கள் தலை சுற்றல் அல்லது மயக்கத்தை உணர்கிறீர்களா?", False, "unconscious"),
        "do you have chest pain": ("Do you have chest pain?", "உங்களுக்கு நெஞ்சு வலி உள்ளதா?", False, "chest pain"),
        "on a scale of 1 to 10 how severe is your pain": ("On a scale of 1 to 10, how severe is your pain?", "1 முதல் 10 வரை, உங்கள் வலி எவ்வளவு தீவிரமாக உள்ளது?", False, None),
        "do you have any allergies": ("Do you have any allergies?", "உங்களுக்கு ஏதேனும் ஒவ்வாமை உள்ளதா?", False, None),
        "are you taking any medication": ("Are you taking any medication?", "நீங்கள் ஏதேனும் மருந்து உட்கொள்கிறீர்களா?", False, None),
        "have you had this before": ("Have you had this before?", "இது உங்களுக்கு முன்பு ஏற்பட்டதா?", False, None),
        "do you have any other symptoms": ("Do you have any other symptoms?", "உங்களுக்கு வேறு ஏதேனும் அறிகுறிகள் உள்ளனவா?", False, None),
        "does anything make it better or worse": ("Does anything make it better or worse?", "ஏதாவது அதை குணப்படுத்துகிறதா அல்லது மோசமாக்குகிறதா?", False, None),
        "is there any bleeding": ("Is there any bleeding?", "ஏதேனும் இரத்தப்போக்கு உள்ளதா?", False, "bleeding"),
        "when did the symptoms start": ("When did the symptoms start?", "அறிகுறிகள் எப்போது தொடங்கின?", False, None),

        # --- Patient Positive Symptoms (Tamil Script + Tanglish) ---
        "enaku nenji vali irukku": ("I have chest pain", "எனக்கு நெஞ்சு வலி இருக்கிறது", False, "chest pain"),
        "enaku nenju vali irukku": ("I have chest pain", "எனக்கு நெஞ்சு வலி இருக்கிறது", False, "chest pain"),
        "nenji vali irukku": ("I have chest pain", "நெஞ்சு வலி இருக்கிறது", False, "chest pain"),
        "nenju vali": ("Chest pain", "நெஞ்சு வலி", False, "chest pain"),
        "nenjil vali": ("Pain in the chest", "நெஞ்சில் வலி", False, "chest pain"),
        "எனக்கு நெஞ்சு வலி இருக்கிறது": ("I have chest pain", "எனக்கு நெஞ்சு வலி இருக்கிறது", False, "chest pain"),
        "நெஞ்சு வலி": ("Chest pain", "நெஞ்சு வலி", False, "chest pain"),
        "நெஞ்சில் வலி": ("Chest pain", "நெஞ்சில் வலி", False, "chest pain"),

        "enaku moochu varadhu": ("I cannot breathe properly", "எனக்கு மூச்சு திணறல் உள்ளது", False, "breathing difficulty"),
        "moochu varadhu": ("Cannot breathe properly", "மூச்சு திணறல் உள்ளது", False, "breathing difficulty"),
        "moochu pidikuthu": ("I am having difficulty breathing", "எனக்கு மூச்சு விடுவதில் சிரமம் உள்ளது", False, "breathing difficulty"),
        "moochu thinaral irukku": ("I have shortness of breath", "எனக்கு மூச்சுத் திணறல் இருக்கிறது", False, "breathing difficulty"),
        "enala moochu vida mudiyala": ("I cannot breathe", "என்னால் மூச்சு விட முடியவில்லை", False, "breathing difficulty"),
        "மூச்சு திணறல்": ("Shortness of breath", "மூச்சு திணறல்", False, "breathing difficulty"),
        "மூச்சு விட முடியவில்லை": ("Cannot breathe", "மூச்சு விட முடியவில்லை", False, "breathing difficulty"),

        "iratham varuthu": ("I am bleeding", "எனக்கு இரத்தப்போக்கு உள்ளது", False, "bleeding"),
        "ratham varuthu": ("Bleeding", "இரத்தம் வருகிறது", False, "bleeding"),
        "irathapokku irukku": ("I have bleeding", "எனக்கு இரத்தப்போக்கு இருக்கிறது", False, "bleeding"),
        "இரத்தப்போக்கு": ("Bleeding", "இரத்தப்போக்கு", False, "bleeding"),

        "thalai sutharuthu": ("I feel dizzy", "எனக்கு தலை சுற்றுகிறது", False, "unconscious"),
        "mayakkam varuthu": ("I feel like fainting", "எனக்கு மயக்கம் வருகிறது", False, "unconscious"),
        "mayakkamaga irukku": ("I feel dizzy and faint", "மயக்கமாக இருக்கிறது", False, "unconscious"),
        "மயக்கம்": ("Fainting / Dizziness", "மயக்கம்", False, "unconscious"),
        "தலை சுற்றல்": ("Dizziness", "தலை சுற்றல்", False, "unconscious"),

        "enaku thalai vali irukku": ("I have a headache", "எனக்கு தலைவலி இருக்கிறது", False, None),
        "thalai vali irukku": ("I have a headache", "தலைவலி இருக்கிறது", False, None),
        "thalai valikuthu": ("My head hurts", "தலை வலிக்கிறது", False, None),
        "தலைவலி": ("Headache", "தலைவலி", False, None),

        "enaku kaichal irukku": ("I have a fever", "எனக்கு காய்ச்சல் இருக்கிறது", False, None),
        "kaichal irukku": ("I have a fever", "காய்ச்சல் இருக்கிறது", False, None),
        "udambu suudaga irukku": ("My body feels hot / feverish", "உடம்பு சூடாக இருக்கிறது", False, None),
        "காய்ச்சல்": ("Fever", "காய்ச்சல்", False, None),

        "enaku vayiru vali irukku": ("I have stomach pain", "எனக்கு வயிற்று வலி இருக்கிறது", False, None),
        "vayiru valikuthu": ("My stomach hurts", "வயிறு வலிக்கிறது", False, None),
        "வயிற்று வலி": ("Stomach pain", "வயிற்று வலி", False, None),

        "vanthi varuthu": ("I feel like vomiting", "எனக்கு வாந்தி வருகிறது", False, None),
        "vanthi eduthen": ("I vomited", "நான் வாந்தி எடுத்தேன்", False, None),
        "வாந்தி": ("Vomiting", "வாந்தி", False, None),

        "irumal irukku": ("I have a cough", "எனக்கு இருமல் இருக்கிறது", False, None),
        "sali pidichirukku": ("I have a cold", "எனக்கு சளி பிடித்துள்ளது", False, None),
        "muthugu vali irukku": ("I have back pain", "எனக்கு முதுகு வலி இருக்கிறது", False, None),
        "kaal vali irukku": ("I have leg pain", "எனக்கு கால் வலி இருக்கிறது", False, None),
        "kai vali irukku": ("I have arm pain", "எனக்கு கை வலி இருக்கிறது", False, None),
        "romba vali irukku": ("I have severe pain", "எனக்கு அதிக வலி இருக்கிறது", False, None),

        # --- Patient Negative Symptoms (Tamil Script + Tanglish) ---
        "enaku nenji vali illai": ("I do not have chest pain", "எனக்கு நெஞ்சு வலி இல்லை", True, "chest pain"),
        "enaku nenju vali illai": ("I do not have chest pain", "எனக்கு நெஞ்சு வலி இல்லை", True, "chest pain"),
        "nenji vali illai": ("I do not have chest pain", "நெஞ்சு வலி இல்லை", True, "chest pain"),
        "nenju vali illa": ("No chest pain", "நெஞ்சு வலி இல்லை", True, "chest pain"),
        "nenjil vali illai": ("No chest pain", "நெஞ்சில் வலி இல்லை", True, "chest pain"),
        "எனக்கு நெஞ்சு வலி இல்லை": ("I do not have chest pain", "எனக்கு நெஞ்சு வலி இல்லை", True, "chest pain"),
        "நெஞ்சு வலி இல்லை": ("No chest pain", "நெஞ்சு வலி இல்லை", True, "chest pain"),

        "enaku moochu thinaral illai": ("I do not have breathing difficulty", "எனக்கு மூச்சுத் திணறல் இல்லை", True, "breathing difficulty"),
        "moochu viduvathil siramam illai": ("No difficulty in breathing", "மூச்சு விடுவதில் சிரமம் இல்லை", True, "breathing difficulty"),
        "மூச்சு திணறல் இல்லை": ("No difficulty breathing", "மூச்சு திணறல் இல்லை", True, "breathing difficulty"),

        "iratham varavillai": ("I am not bleeding", "இரத்தம் வரவில்லை", True, "bleeding"),
        "irathapokku illai": ("No bleeding", "இரத்தப்போக்கு இல்லை", True, "bleeding"),
        "இரத்தப்போக்கு இல்லை": ("No bleeding", "இரத்தப்போக்கு இல்லை", True, "bleeding"),

        "mayakkam illai": ("I do not feel dizzy or faint", "மயக்கம் இல்லை", True, "unconscious"),
        "மயக்கம் இல்லை": ("No fainting", "மயக்கம் இல்லை", True, "unconscious"),

        "enaku thalai vali illai": ("I do not have a headache", "எனக்கு தலைவலி இல்லை", True, None),
        "thalai vali illai": ("No headache", "தலைவலி இல்லை", True, None),
        "தலைவலி இல்லை": ("No headache", "தலைவலி இல்லை", True, None),

        "kaichal illai": ("I do not have a fever", "காய்ச்சல் இல்லை", True, None),
        "காய்ச்சல் இல்லை": ("No fever", "காய்ச்சல் இல்லை", True, None),

        "vayiru vali illai": ("I do not have stomach pain", "வயிற்று வலி இல்லை", True, None),
        "vali illai": ("I have no pain", "வலி இல்லை", True, None),
        "vali kidayathu": ("No pain", "வலி கிடையாது", True, None),
        "வலி இல்லை": ("No pain", "வலி இல்லை", True, None),

        "aama": ("Yes", "ஆம்", False, None),
        "aam": ("Yes", "ஆம்", False, None),
        "illai": ("No", "இல்லை", True, None),
        "seri": ("Okay", "சரி", False, None),
        "puriyuthu": ("I understand", "புரிகிறது", False, None),
        "puriyala": ("I do not understand", "புரியவில்லை", True, None),
        "help pannunga": ("Please help me", "தயவு செய்து எனக்கு உதவுங்கள்", False, None),
        "nalla irukken": ("I am fine", "நான் நலமாக இருக்கிறேன்", False, None),
    },

    "hi": {
        # --- Staff Guided Prompts ---
        "good morning how can i help you": ("Good morning. How can I help you?", "सुप्रभात। मैं आपकी कैसे मदद कर सकता हूँ?", False, None),
        "do you have an appointment": ("Do you have an appointment?", "क्या आपका कोई अपॉइंटमेंट है?", False, None),
        "can i take your name and date of birth": ("Can I take your name and date of birth?", "क्या मैं आपका नाम और जन्मतिथि ले सकता हूँ?", False, None),
        "please take a seat the doctor will see you shortly": ("Please take a seat. The doctor will see you shortly.", "कृपया बैठ जाइए। डॉक्टर जल्द ही आपसे मिलेंगे।", False, None),
        "do you need any assistance": ("Do you need any assistance?", "क्या आपको किसी सहायता की आवश्यकता है?", False, None),
        "is this your first visit": ("Is this your first visit?", "क्या यह आपकी पहली यात्रा है?", False, None),
        "do you have your nhs number": ("Do you have your NHS number?", "क्या आपके पास एनएचएस नंबर है?", False, None),
        "please fill in this form": ("Please fill in this form.", "कृपया यह फॉर्म भरें।", False, None),
        "please wait the doctor will call you": ("Please wait. The doctor will call you.", "कृपया प्रतीक्षा करें। डॉक्टर आपको बुलाएंगे।", False, None),
        "your appointment is confirmed": ("Your appointment is confirmed.", "आपका अपॉइंटमेंट पक्का हो गया है।", False, None),
        "the doctor will see you now": ("The doctor will see you now.", "डॉक्टर अब आपसे मिलेंगे।", False, None),
        "where is your pain": ("Where is your pain?", "आपको दर्द कहाँ हो रहा है?", False, None),
        "how long have you had this": ("How long have you had this?", "यह समस्या आपको कब से है?", False, None),
        "do you have a fever": ("Do you have a fever?", "क्या आपको बुखार है?", False, None),
        "are you having difficulty breathing": ("Are you having difficulty breathing?", "क्या आपको सांस लेने में कठिनाई हो रही है?", False, "breathing difficulty"),
        "do you feel dizzy or faint": ("Do you feel dizzy or faint?", "क्या आपको चक्कर या बेहोशी महसूस हो रही है?", False, "unconscious"),
        "do you have chest pain": ("Do you have chest pain?", "क्या आपको सीने में दर्द है?", False, "chest pain"),
        "do you have any allergies": ("Do you have any allergies?", "क्या आपको कोई एलर्जी है?", False, None),
        "are you taking any medication": ("Are you taking any medication?", "क्या आप कोई दवा ले रहे हैं?", False, None),

        # --- Patient Positive Symptoms (Devanagari + Hinglish) ---
        "mujhe chest mein dard hai": ("I have chest pain", "मुझे सीने में दर्द है", False, "chest pain"),
        "seene mein dard hai": ("I have chest pain", "सीने में दर्द है", False, "chest pain"),
        "seene mein dard": ("Chest pain", "सीने में दर्द", False, "chest pain"),
        "chhati mein dard hai": ("I have chest pain", "छाती में दर्द है", False, "chest pain"),
        "मुझे सीने में दर्द है": ("I have chest pain", "मुझे सीने में दर्द है", False, "chest pain"),
        "सीने में दर्द": ("Chest pain", "सीने में दर्द", False, "chest pain"),

        "saans lene mein takleef hai": ("I have difficulty breathing", "मुझे सांस लेने में तकलीफ है", False, "breathing difficulty"),
        "saans nahi aa rahi": ("I cannot breathe", "सांस नहीं आ रही है", False, "breathing difficulty"),
        "dam ghut raha hai": ("I am suffocating", "दम घुट रहा है", False, "breathing difficulty"),
        "सांस लेने में तकलीफ": ("Difficulty breathing", "सांस लेने में तकलीफ", False, "breathing difficulty"),
        "सांस नहीं आ रही": ("Cannot breathe", "सांस नहीं आ रही है", False, "breathing difficulty"),

        "khoon nikal raha hai": ("I am bleeding", "खून बह रहा है", False, "bleeding"),
        "khoon aa raha hai": ("Bleeding", "खून आ रहा है", False, "bleeding"),
        "खून बह रहा है": ("Bleeding", "खून बह रहा है", False, "bleeding"),

        "chakkar aa raha hai": ("I feel dizzy", "मुझे चक्कर आ रहा है", False, "unconscious"),
        "behosh ho gaya tha": ("I fainted", "मैं बेहोश हो गया था", False, "unconscious"),
        "चक्कर आ रहा है": ("Dizziness", "चक्कर आ रहा है", False, "unconscious"),
        "बेहोशी": ("Fainting", "बेहोशी", False, "unconscious"),

        "mujhe sar dard hai": ("I have a headache", "मुझे सिरदर्द है", False, None),
        "sar dard hai": ("I have a headache", "सिरदर्द है", False, None),
        "सिरदर्द": ("Headache", "सिरदर्द", False, None),

        "mujhe bukhar hai": ("I have a fever", "मुझे बुखार है", False, None),
        "bukhar hai": ("I have a fever", "बुखार है", False, None),
        "बुखार है": ("Fever", "बुखार है", False, None),

        "pet mein dard hai": ("I have stomach pain", "पेट में दर्द है", False, None),
        "ulti aa rahi hai": ("I feel like vomiting", "उल्टी आ रही है", False, None),
        "khansi hai": ("I have a cough", "खांसी है", False, None),
        "bahut dard hai": ("I have severe pain", "बहुत तेज दर्द है", False, None),

        # --- Patient Negative Symptoms ---
        "chest mein dard nahi hai": ("I do not have chest pain", "सीने में दर्द नहीं है", True, "chest pain"),
        "seene mein dard nahi hai": ("I do not have chest pain", "सीने में दर्द नहीं है", True, "chest pain"),
        "सीने में दर्द नहीं है": ("I do not have chest pain", "सीने में दर्द नहीं है", True, "chest pain"),

        "saans lene mein koi takleef nahi": ("No difficulty in breathing", "सांस लेने में कोई तकलीफ नहीं है", True, "breathing difficulty"),
        "सांस लेने में तकलीफ नहीं है": ("No difficulty breathing", "सांस लेने में तकलीफ नहीं है", True, "breathing difficulty"),

        "khoon nahi nikal raha": ("Not bleeding", "खून नहीं निकल रहा है", True, "bleeding"),
        "खून नहीं आ रहा": ("No bleeding", "खून नहीं आ रहा है", True, "bleeding"),

        "chakkar nahi aa rahe": ("Not feeling dizzy", "चक्कर नहीं आ रहे हैं", True, "unconscious"),
        "चक्कर नहीं आ रहे": ("No dizziness", "चक्कर नहीं आ रहे हैं", True, "unconscious"),

        "sar dard nahi hai": ("I do not have a headache", "सिरदर्द नहीं है", True, None),
        "सिरदर्द नहीं है": ("No headache", "सिरदर्द नहीं है", True, None),

        "bukhar nahi hai": ("I do not have a fever", "बुखार नहीं है", True, None),
        "बुखार नहीं है": ("No fever", "बुखार नहीं है", True, None),

        "dard nahi hai": ("I have no pain", "दर्द नहीं है", True, None),
        "कोई दर्द नहीं है": ("No pain", "कोई दर्द नहीं है", True, None),

        "haan": ("Yes", "हाँ", False, None),
        "nahi": ("No", "नहीं", True, None),
        "theek hoon": ("I am fine", "मैं ठीक हूँ", False, None),
        "theek hai": ("Okay", "ठीक है", False, None),
        "samajh aa gaya": ("I understand", "समझ आ गया", False, None),
        "samajh nahi aaya": ("I do not understand", "समझ नहीं आया", True, None),
        "madad karo": ("Please help me", "कृपया मेरी मदद करें", False, None),
    },

    "ml": {
        "good morning how can i help you": ("Good morning. How can I help you?", "സുപ്രഭാതം. എനിക്ക് നിങ്ങളെ എങ്ങനെ സഹായിക്കാനാകും?", False, None),
        "do you have an appointment": ("Do you have an appointment?", "നിങ്ങൾക്ക് ഒരു അപ്പോയിന്റ്മെന്റ് ഉണ്ടോ?", False, None),
        "do you have chest pain": ("Do you have chest pain?", "നിങ്ങൾക്ക് നെഞ്ചുവേദന ഉണ്ടോ?", False, "chest pain"),
        "nenjil vali undu": ("I have chest pain", "നെഞ്ചിൽ വേദനയുണ്ട്", False, "chest pain"),
        "നെഞ്ചിൽ വേദനയുണ്ട്": ("I have chest pain", "നെഞ്ചിൽ വേദനയുണ്ട്", False, "chest pain"),
        "shwasam muttunnu": ("I have difficulty breathing", "ശ്വാസം മുട്ടുന്നു", False, "breathing difficulty"),
        "ശ്വാസം മുട്ടൽ": ("Difficulty breathing", "ശ്വാസം മുട്ടൽ", False, "breathing difficulty"),
        "raktham varunnu": ("I am bleeding", "രക്തം വരുന്നു", False, "bleeding"),
        "thalavalikkunnu": ("I have a headache", "തലവേദനയുണ്ട്", False, None),
        "pani undu": ("I have a fever", "പനിയുണ്ട്", False, None),
        "vayaril vali undu": ("I have stomach pain", "വയറുവേദനയുണ്ട്", False, None),
        "chardi varunnu": ("I feel like vomiting", "ഛർദ്ദി വരുന്നു", False, None),
        
        "nenjil vali illa": ("I do not have chest pain", "നെഞ്ചിൽ വേദനയില്ല", True, "chest pain"),
        "നെഞ്ചിൽ വേദനയില്ല": ("I do not have chest pain", "നെഞ്ചിൽ വേദനയില്ല", True, "chest pain"),
        "shwasathadassam illa": ("No difficulty in breathing", "ശ്വാസതടസ്സമില്ല", True, "breathing difficulty"),
        "pani illa": ("I do not have a fever", "പനിയില്ല", True, None),
        "vali illa": ("I have no pain", "വേദനയില്ല", True, None),
        "athe": ("Yes", "അതെ", False, None),
        "alla": ("No", "അല്ല", True, None),
        "manasilayi": ("I understand", "മനസ്സിലായി", False, None),
    },

    "pl": {
        "good morning how can i help you": ("Good morning. How can I help you?", "Dzień dobry. W czym mogę pomóc?", False, None),
        "do you have an appointment": ("Do you have an appointment?", "Czy ma Pan/Pani umówioną wizytę?", False, None),
        "do you have chest pain": ("Do you have chest pain?", "Czy ma Pan/Pani ból w klatce piersiowej?", False, "chest pain"),
        "mam bol w klatce piersiowej": ("I have chest pain", "Mam ból w klatce piersiowej", False, "chest pain"),
        "bol w klatce piersiowej": ("Chest pain", "Ból w klatce piersiowej", False, "chest pain"),
        "trudno mi oddychac": ("I have difficulty breathing", "Trudno mi oddychać", False, "breathing difficulty"),
        "duszno mi": ("I feel breathless", "Duszno mi", False, "breathing difficulty"),
        "krwawie": ("I am bleeding", "Krwawię", False, "bleeding"),
        "kreci mi sie w glowie": ("I feel dizzy", "Kręci mi się w głowie", False, "unconscious"),
        "bol glowy": ("I have a headache", "Boli mnie głowa", False, None),
        "mam goraczke": ("I have a fever", "Mam gorączkę", False, None),
        "mam bol brzucha": ("I have stomach pain", "Mam ból brzucha", False, None),
        
        "nie mam bolu w klatce": ("I do not have chest pain", "Nie mam bólu w klatce piersiowej", True, "chest pain"),
        "nie mam problemow z oddychaniem": ("No breathing problems", "Nie mam problemów z oddychaniem", True, "breathing difficulty"),
        "nie krwawie": ("Not bleeding", "Nie krwawię", True, "bleeding"),
        "nie mam goraczki": ("I do not have a fever", "Nie mam gorączki", True, None),
        "nie boli mnie nic": ("I have no pain", "Nic mnie nie boli", True, None),
        "tak": ("Yes", "Tak", False, None),
        "nie": ("No", "Nie", True, None),
        "rozumiem": ("I understand", "Rozumiem", False, None),
    },

    "ar": {
        "good morning how can i help you": ("Good morning. How can I help you?", "صباح الخير. كيف يمكنني مساعدتك؟", False, None),
        "do you have an appointment": ("Do you have an appointment?", "هل لديك موعد؟", False, None),
        "do you have chest pain": ("Do you have chest pain?", "هل تعاني من ألم في الصدر؟", False, "chest pain"),
        "عندي ألم في الصدر": ("I have chest pain", "عندي ألم في الصدر", False, "chest pain"),
        "ألم في الصدر": ("Chest pain", "ألم في الصدر", False, "chest pain"),
        "لا استطيع التنفس": ("I cannot breathe", "لا أستطيع التنفس", False, "breathing difficulty"),
        "صعوبة في التنفس": ("Difficulty breathing", "صعوبة في التنفس", False, "breathing difficulty"),
        "عندي نزيف": ("I am bleeding", "عندي نزيف", False, "bleeding"),
        "أشعر بالدوار": ("I feel dizzy", "أشعر بالدوار", False, "unconscious"),
        "عندي صداع": ("I have a headache", "عندي صداع", False, None),
        "عندي حمى": ("I have a fever", "عندي حمى", False, None),
        "عندي ألم في المعدة": ("I have stomach pain", "عندي ألم في المعدة", False, None),
        
        "ليس لدي ألم في الصدر": ("I do not have chest pain", "ليس لدي ألم في الصدر", True, "chest pain"),
        "لا يوجد صعوبة في التنفس": ("No difficulty breathing", "لا يوجد صعوبة في التنفس", True, "breathing difficulty"),
        "لا يوجد نزيف": ("No bleeding", "لا يوجد نزيف", True, "bleeding"),
        "ليس لدي حمى": ("I do not have a fever", "ليس لدي حمى", True, None),
        "ليس لدي ألم": ("I have no pain", "ليس لدي أي ألم", True, None),
        "نعم": ("Yes", "نعم", False, None),
        "لا": ("No", "لا", True, None),
        "أفهم": ("I understand", "أفهم", False, None),
    },

    "ur": {
        "good morning how can i help you": ("Good morning. How can I help you?", "صبح بخیر۔ میں آپ کی کیسے مدد کر سکتا ہوں؟", False, None),
        "do you have an appointment": ("Do you have an appointment?", "کیا آپ کا کوئی اپوائنٹمنٹ ہے؟", False, None),
        "do you have chest pain": ("Do you have chest pain?", "کیا آپ کو سینے میں درد ہے؟", False, "chest pain"),
        "میرے سینے میں درد ہے": ("I have chest pain", "میرے سینے میں درد ہے", False, "chest pain"),
        "سینے میں درد": ("Chest pain", "سینے میں درد", False, "chest pain"),
        "سانس لینے میں دشواری": ("I have difficulty breathing", "سانس لینے میں دشواری ہے", False, "breathing difficulty"),
        "سانس نہیں آ رہی": ("Cannot breathe", "سانس نہیں آ رہی", False, "breathing difficulty"),
        "خون بہہ رہا ہے": ("I am bleeding", "خون بہہ رہا ہے", False, "bleeding"),
        "چکر آ رہے ہیں": ("I feel dizzy", "چکر آ رہے ہیں", False, "unconscious"),
        "میرا سر درد ہے": ("I have a headache", "میرا سر درد ہے", False, None),
        "مجھے بخار ہے": ("I have a fever", "مجھے بخار ہے", False, None),
        "پیٹ میں درد ہے": ("I have stomach pain", "پیٹ میں درد ہے", False, None),
        
        "میرے سینے میں درد نہیں": ("I do not have chest pain", "میرے سینے میں درد نہیں ہے", True, "chest pain"),
        "سانس کی کوئی تکلیف نہیں": ("No breathing difficulty", "سانس کی کوئی تکلیف نہیں ہے", True, "breathing difficulty"),
        "خون نہیں بہہ رہا": ("No bleeding", "خون نہیں بہہ رہا", True, "bleeding"),
        "مجھے بخار نہیں": ("I do not have a fever", "مجھے بخار نہیں ہے", True, None),
        "مجھے کوئی درد نہیں": ("I have no pain", "مجھے کوئی درد نہیں ہے", True, None),
        "ہاں": ("Yes", "ہاں", False, None),
        "نہیں": ("No", "نہیں", True, None),
        "سمجھ آ گیا": ("I understand", "سمجھ آ گیا", False, None),
    },

    "bn": {
        "good morning how can i help you": ("Good morning. How can I help you?", "সুপ্রভাত। আমি আপনাকে কীভাবে সাহায্য করতে পারি?", False, None),
        "do you have chest pain": ("Do you have chest pain?", "আপনার কি বুকে ব্যথা আছে?", False, "chest pain"),
        "আমার বুকে ব্যথা": ("I have chest pain", "আমার বুকে ব্যথা আছে", False, "chest pain"),
        "বুকে ব্যথা": ("Chest pain", "বুকে ব্যথা", False, "chest pain"),
        "শ্বাস নিতে কষ্ট": ("I have difficulty breathing", "আমার শ্বাস নিতে কষ্ট হচ্ছে", False, "breathing difficulty"),
        "রক্ত পড়ছে": ("I am bleeding", "রক্ত পড়ছে", False, "bleeding"),
        "মাথা ঘুরছে": ("I feel dizzy", "আমার মাথা ঘুরছে", False, "unconscious"),
        "আমার মাথা ব্যাথা": ("I have a headache", "আমার মাথা ব্যাথা করছে", False, None),
        "আমার জ্বর": ("I have a fever", "আমার জ্বর আছে", False, None),
        "পেটে ব্যথা": ("I have stomach pain", "পেটে ব্যথা করছে", False, None),
        
        "আমার বুকে ব্যথা নেই": ("I do not have chest pain", "আমার বুকে ব্যথা নেই", True, "chest pain"),
        "বুকে ব্যথা নেই": ("No chest pain", "বুকে ব্যথা নেই", True, "chest pain"),
        "শ্বাসকষ্ট নেই": ("No breathing difficulty", "শ্বাসকষ্ট নেই", True, "breathing difficulty"),
        "রক্তপাত নেই": ("No bleeding", "রক্তপাত নেই", True, "bleeding"),
        "আমার জ্বর নেই": ("I do not have a fever", "আমার জ্বর নেই", True, None),
        "কোনো ব্যথা নেই": ("I have no pain", "কোনো ব্যথা নেই", True, None),
        "হ্যাঁ": ("Yes", "হ্যাঁ", False, None),
        "না": ("No", "না", True, None),
    },

    "so": {
        "good morning how can i help you": ("Good morning. How can I help you?", "Subax wanaagsan. Sideen ku caawin karaa?", False, None),
        "do you have chest pain": ("Do you have chest pain?", "Ma qabtaa xanuun laabta?", False, "chest pain"),
        "xanuun laabta": ("I have chest pain", "Waxaan qabaa xanuun laabta ah", False, "chest pain"),
        "neefsasho dhib": ("I have difficulty breathing", "Waxaan qabaa dhibaatada neefsashada", False, "breathing difficulty"),
        "dhiig ayaa iga socda": ("I am bleeding", "Dhiig ayaa iga socda", False, "bleeding"),
        "madax xanuun": ("I have a headache", "Waxaan qabaa madax xanuun", False, None),
        "qandho": ("I have a fever", "Waxaan qabaa qandho", False, None),
        
        "ma laha xanuun laabta": ("I do not have chest pain", "Ma qabo xanuun laabta ah", True, "chest pain"),
        "neefsashadu ma adka": ("No breathing difficulty", "Neefsashadu ma adka", True, "breathing difficulty"),
        "dhiig ma jiro": ("No bleeding", "Dhiig ma jiro", True, "bleeding"),
        "ma qabo qandho": ("I do not have a fever", "Ma qabo qandho", True, None),
        "xanuun ma jiro": ("I have no pain", "Wax xanuun ah ma jiro", True, None),
        "haa": ("Yes", "Haa", False, None),
        "maya": ("No", "Maya", True, None),
    },

    "ro": {
        "good morning how can i help you": ("Good morning. How can I help you?", "Bună dimineața. Cu ce vă pot ajuta?", False, None),
        "do you have chest pain": ("Do you have chest pain?", "Aveți dureri în piept?", False, "chest pain"),
        "durere in piept": ("I have chest pain", "Am dureri în piept", False, "chest pain"),
        "am dureri in piept": ("I have chest pain", "Am dureri în piept", False, "chest pain"),
        "dificultate de respiratie": ("I have difficulty breathing", "Am dificultăți de respirație", False, "breathing difficulty"),
        "sangerez": ("I am bleeding", "Sângerez", False, "bleeding"),
        "ma simt ametit": ("I feel dizzy", "Mă simt amețit", False, "unconscious"),
        "durere de cap": ("I have a headache", "Am o durere de cap", False, None),
        "febra": ("I have a fever", "Am febră", False, None),
        "durere de stomac": ("I have stomach pain", "Am dureri de stomac", False, None),
        
        "nu am durere in piept": ("I do not have chest pain", "Nu am dureri în piept", True, "chest pain"),
        "nu am dificultati de respiratie": ("No breathing difficulty", "Nu am dificultăți de respirație", True, "breathing difficulty"),
        "nu sangerez": ("Not bleeding", "Nu sângerez", True, "bleeding"),
        "nu am febra": ("I do not have a fever", "Nu am febră", True, None),
        "nu ma doare nimic": ("I have no pain", "Nu mă doare nimic", True, None),
        "da": ("Yes", "Da", False, None),
        "nu": ("No", "Nu", True, None),
    }
}

def lookup_clinical_phrase(text, lang_code):
    if not lang_code or lang_code not in CLINICAL_DICTIONARY:
        return None
    
    lang_dict = CLINICAL_DICTIONARY[lang_code]
    norm_input = normalize_text(text)
    
    if norm_input in lang_dict:
        return lang_dict[norm_input]
    
    best_match = None
    best_len = 0
    for phrase_key, data in lang_dict.items():
        norm_key = normalize_text(phrase_key)
        if norm_key in norm_input or norm_input in norm_key:
            if len(norm_key) > best_len:
                best_match = data
                best_len = len(norm_key)
                
    return best_match

# ============================================================
# GUIDED PROMPT LISTINGS
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
# TRANSLATION ENGINES
# ============================================================

def execute_online_translation(text, src, target):
    if not text:
        return ""
    try:
        from deep_translator import GoogleTranslator
        res = GoogleTranslator(source=src, target=target).translate(text)
        if res:
            return res
    except Exception:
        pass

    try:
        from deep_translator import MyMemoryTranslator
        res = MyMemoryTranslator(source=src, target=target).translate(text)
        if res:
            return res
    except Exception:
        pass

    return text

def translate_staff_to_native(text, target_lang_code):
    if not text:
        return "", None

    lookup = lookup_clinical_phrase(text, target_lang_code)
    if lookup:
        return lookup[1], None

    cached = get_cached_translation(text, target_lang_code)
    if cached:
        return cached, None

    target = get_clean_lang_code(target_lang_code)
    translated = execute_online_translation(text, "en", target)
    
    if translated:
        set_cached_translation(text, target_lang_code, translated)
        return translated, None

    return text, "Translation unavailable"

def translate_patient_input(text, lang_code):
    if not text:
        return "", "", None

    lookup = lookup_clinical_phrase(text, lang_code)
    if lookup:
        return lookup[0], lookup[1], None

    if is_native_script(text):
        native_trans = text
        target_src = get_clean_lang_code(lang_code)
        english_trans = execute_online_translation(text, target_src, "en")
        return english_trans, native_trans, None

    # For Romanized input (e.g. Tanglish / Hinglish), translate to English then reconstruct pure native script
    english_trans = execute_online_translation(text, "auto", "en")
    target_clean = get_clean_lang_code(lang_code)
    native_trans = execute_online_translation(english_trans, "en", target_clean)
    
    return english_trans, native_trans, None

# ============================================================
# FLASK ROUTES
# ============================================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = (request.form.get('email') or request.form.get('username') or "").strip().lower()
        password = (request.form.get('password') or "").strip()
        
        if email == DEMO_EMAIL.lower() and password == DEMO_PASSWORD:
            user = User(email)
            login_user(user, remember=True)
            next_url = request.args.get('next')
            if next_url and next_url.startswith('/'):
                return redirect(next_url)
            return redirect(url_for('index'))
            
        flash('Invalid email or password', 'error')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    reset_translation_session()
    return redirect(url_for('login'))

@app.route("/")
@login_required
def index():
    return render_template("index.html")

@app.route("/api/ping", methods=["GET"])
@login_required
def ping():
    return jsonify({"status": "Flask is running", "session": dict(session)})

@app.route("/api/start_session", methods=["POST"])
@login_required
def start_session():
    try:
        data = request.get_json() or {}
        reset_translation_session()
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
        return jsonify({"status": "error", "error": f"Could not start session: {str(e)}"}), 500

@app.route("/api/end_session", methods=["POST"])
@login_required
def end_session():
    reset_translation_session()
    return jsonify({"status": "ok"})

@app.route("/api/translate_staff", methods=["POST"])
@login_required
def translate_staff():
    data = request.get_json() or {}
    raw_text = data.get("text", "").strip()
    if not raw_text:
        return jsonify({"error": "No text provided"}), 400

    lang_code = session.get("lang_code", "ta")
    lang_name = session.get("lang", "Tamil")

    simplified, was_simplified = simplify_text(raw_text)
    translated_native, error = translate_staff_to_native(simplified, lang_code)
    
    if not translated_native:
        translated_native = raw_text

    return jsonify({
        "original": raw_text,
        "simplified": simplified,
        "was_simplified": was_simplified,
        "translated": translated_native,
        "lang": lang_name,
        "urgent": False,
        "warning": error
    })

@app.route("/api/translate_patient", methods=["POST"])
@login_required
def translate_patient():
    data = request.get_json() or {}
    raw_text = data.get("text", "").strip()
    if not raw_text:
        return jsonify({"error": "No text provided"}), 400

    lang_code = session.get("lang_code", "ta")
    lang_name = session.get("lang", "Tamil")

    english_translation, native_script, error = translate_patient_input(raw_text, lang_code)
    triage = evaluate_medical_triage(raw_text, english_translation, lang_code)

    return jsonify({
        "original": raw_text,
        "native": native_script,
        "translated": english_translation,
        "lang": lang_name,
        "symptom_detected": triage["symptom_detected"],
        "is_negative": triage["is_negative"],
        "medical_alert": triage["medical_alert"],
        "warning": error
    })

@app.route("/api/simplify", methods=["POST"])
@login_required
def simplify_endpoint():
    data = request.get_json() or {}
    text = data.get("text", "")
    simplified, changed = simplify_text(text)
    return jsonify({"simplified": simplified, "changed": changed})

@app.route("/api/session_status")
@login_required
def session_status():
    return jsonify({
        "active": session.get("active", False),
        "context": session.get("context"),
        "lang": session.get("lang"),
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(debug=False, host="0.0.0.0", port=port)
