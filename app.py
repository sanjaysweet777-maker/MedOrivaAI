import json
import logging
import os
import re
import secrets
import unicodedata
import uuid
from urllib.parse import urlparse
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from flask_login import LoginManager, UserMixin, current_user, login_required, login_user, logout_user

from translation_engine import (
    LANGUAGES,
    Translation,
    configured_key,
    online,
    patient_translation,
    staff_translation,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(BASE_DIR, 'templates')

app = Flask(__name__, template_folder=template_dir)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("medoriva.app")

env_secret = os.environ.get("SECRET_KEY")
if not env_secret:
    logger.warning("SECRET_KEY unset in environment. Generating dynamic cryptographic secret.")
    app.secret_key = secrets.token_hex(32)
else:
    app.secret_key = env_secret

cookie_secure = os.environ.get("COOKIE_SECURE", "false").lower() in ("true", "1", "yes")
app.config["SESSION_COOKIE_SECURE"] = cookie_secure
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

# ============================================================
# CANONICAL LANGUAGE MAPPING (All 9 Approved MVP Languages)
# ============================================================
CANONICAL_LANGUAGES = {
    "ta": ("Tamil", "ta"), "tamil": ("Tamil", "ta"),
    "hi": ("Hindi", "hi"), "hindi": ("Hindi", "hi"),
    "ml": ("Malayalam", "ml"), "malayalam": ("Malayalam", "ml"),
    "pl": ("Polish", "pl"), "polish": ("Polish", "pl"),
    "ar": ("Arabic", "ar"), "arabic": ("Arabic", "ar"),
    "ur": ("Urdu", "ur"), "urdu": ("Urdu", "ur"),
    "bn": ("Bengali", "bn"), "bengali": ("Bengali", "bn"),
    "so": ("Somali", "so"), "somali": ("Somali", "so"),
    "ro": ("Romanian", "ro"), "romanian": ("Romanian", "ro"),
}

def get_canonical(raw_lang, raw_code=None):
    if raw_code and str(raw_code).strip().lower() in CANONICAL_LANGUAGES:
        return CANONICAL_LANGUAGES[str(raw_code).strip().lower()]
    if raw_lang:
        token = re.split(r'[\s\(\-_/]', str(raw_lang).strip())[0].lower()
        if token in CANONICAL_LANGUAGES:
            return CANONICAL_LANGUAGES[token]
        return (str(raw_lang).strip(), str(raw_code or raw_lang).strip())
    return ("Tamil", "ta")

def normalize_phrase(text):
    if not text:
        return ""
    chars = [c for c in unicodedata.normalize('NFC', str(text)) if not unicodedata.category(c).startswith('P')]
    return " ".join("".join(chars).lower().split())

# ============================================================
# 1. COMPLETE 21 GUIDED PROMPTS ACROSS ALL 3 CONTEXTS
# ============================================================
CONTEXT_PROMPTS = {
    "Reception": [
        "Good morning. How can I help you?",
        "Do you have an appointment?",
        "Can I take your name and date of birth?",
        "Please take a seat.",
        "Do you have your NHS number?",
        "Please fill in this form.",
        "Do you need an interpreter?"
    ],
    "Appointment": [
        "Your appointment is confirmed.",
        "The doctor will see you now.",
        "Do you have your appointment letter?",
        "Please bring your medication list.",
        "Is anyone with you today?",
        "Please wait in the waiting area.",
        "The appointment will take about 15 minutes."
    ],
    "Basic Symptoms": [
        "Where is your pain?",
        "How long have you had this?",
        "Do you have a fever?",
        "Are you having difficulty breathing?",
        "Do you feel dizzy or faint?",
        "Do you have chest pain?",
        "When did the symptoms start?"
    ]
}

# ============================================================
# 2. PREPARED STAFF TRANSLATIONS FOR EXTENDED PROMPTS (9 Languages)
# Ensures zero "Machine translation" fallbacks on prompt clicks
# ============================================================
RAW_EXTENDED_STAFF = {
    "Good morning. How can I help you?": {
        "ta": "காலை வணக்கம். நான் உங்களுக்கு எப்படி உதவ முடியும்?",
        "hi": "नमस्ते। मैं आपकी क्या मदद कर सकता हूँ?",
        "ml": "ശുഭോദയം. ഞാൻ നിങ്ങളെ എങ്ങനെ സഹായിക്കണം?",
        "pl": "Dzień dobry. W czym mogę Panu/Pani pomóc?",
        "ar": "صباح الخير. كيف يمكنني مساعدتك؟",
        "ur": "صبح بخیر۔ میں آپ کی کیا مدد کر سکتا ہوں؟",
        "bn": "সুপ্রভাত। আমি আপনাকে কীভাবে সাহায্য করতে পারি?",
        "so": "Subax wanaagsan. Sideen kuu caawin karaa?",
        "ro": "Bună dimineața. Cu ce vă pot ajuta?"
    },
    "Can I take your name and date of birth?": {
        "ta": "உங்கள் பெயர் மற்றும் பிறந்த தேதியை அறியலாமா?",
        "hi": "क्या मुझे आपका नाम और जन्म तिथि मिल सकती है?",
        "ml": "നിങ്ങളുടെ പേരും ജനനത്തീയതിയും പറയാമോ?",
        "pl": "Czy mogę prosić o Pana/Pani imię, nazwisko i datę urodzenia?",
        "ar": "هل يمكنني معرفة اسمك وتاريخ ميلادك؟",
        "ur": "کیا میں آپ کا نام اور تاریخ پیدائش جان سکتا ہوں؟",
        "bn": "আমি কি আপনার নাম এবং জন্ম তারিখ জানতে পারি?",
        "so": "Ma ii sheegi kartaa magacaaga iyo taariikhda dhalashadaada?",
        "ro": "Îmi puteți spune numele și data nașterii?"
    },
    "Please fill in this form.": {
        "ta": "தயவுசெய்து இந்தப் படிவத்தைப் பூர்த்தி செய்யவும்.",
        "hi": "कृपया यह फॉर्म भरें।",
        "ml": "ദയവായി ഈ ഫോം പൂരിപ്പിക്കുക.",
        "pl": "Proszę wypełnić ten formularz.",
        "ar": "يرجى ملء هذا النموذج.",
        "ur": "براہ کرم یہ فارم پر کریں۔",
        "bn": "দয়া করে এই ফর্মটি পূরণ করুন।",
        "so": "Fadlan buuxi foomkan.",
        "ro": "Vă rugăm să completați acest formular."
    },
    "Your appointment is confirmed.": {
        "ta": "உங்கள் அப்பாயிண்ட்மென்ட் உறுதி செய்யப்பட்டுள்ளது.",
        "hi": "आपका अपॉइंटमेंट पक्का हो गया है।",
        "ml": "നിങ്ങളുടെ അപ്പോയിന്റ്മെന്റ് സ്ഥിരീകരിച്ചിരിക്കുന്നു.",
        "pl": "Pana/Pani wizyta została potwierdzona.",
        "ar": "تم تأكيد موعدك.",
        "ur": "آپ کے اپائنٹمنٹ کی تصدیق ہو گئی ہے۔",
        "bn": "আপনার অ্যাপয়েন্টমেন্ট নিশ্চিত করা হয়েছে।",
        "so": "Ballantaada waa la xaqiijiyay.",
        "ro": "Programarea dumneavoastră este confirmată."
    },
    "The doctor will see you now.": {
        "ta": "மருத்துவர் இப்போது உங்களைப் பார்ப்பார்.",
        "hi": "डॉक्टर अब आपसे मिलेंगे।",
        "ml": "ഡോക്ടർ ഇപ്പോൾ നിങ്ങളെ കാണും.",
        "pl": "Lekarz przyjmie Pana/Panią teraz.",
        "ar": "الطبيب سيراك الآن.",
        "ur": "ڈاکٹر اب آپ کو دیکھیں گے۔",
        "bn": "ডাক্তার এখন আপনাকে দেখবেন।",
        "so": "Dhaqtarku hadda wuu ku arkayaa.",
        "ro": "Medicul vă poate primi acum."
    },
    "Please bring your medication list.": {
        "ta": "தயவுசெய்து உங்கள் மருந்துப் பட்டியலைக் கொண்டு வாருங்கள்.",
        "hi": "कृपया अपनी दवाइयों की सूची साथ लाएँ।",
        "ml": "ദയവായി നിങ്ങളുടെ മരുന്നുകളുടെ ലിസ്റ്റ് കൊണ്ടുവരിക.",
        "pl": "Proszę przynieść listę przyjmowanych leków.",
        "ar": "يرجى إحضار قائمة الأدوية الخاصة بك.",
        "ur": "براہ کرم اپنی ادویات کی فہرست ساتھ لائیں۔",
        "bn": "দয়া করে আপনার ওষুধের তালিকা সাথে নিয়ে আসুন।",
        "so": "Fadlan soo qaado liiska daawooyinkaaga.",
        "ro": "Vă rugăm să aduceți lista dumneavoastră de medicamente."
    },
    "Is anyone with you today?": {
        "ta": "இன்று உங்களுடன் யாராவது வந்துள்ளார்களா?",
        "hi": "क्या आज आपके साथ कोई आया है?",
        "ml": "ഇന്ന് നിങ്ങളുടെ കൂടെ ആരെങ്കിലും ഉണ്ടോ?",
        "pl": "Czy jest dzisiaj z Panem/Panią ktoś towarzyszący?",
        "ar": "هل يرافقك أحد اليوم؟",
        "ur": "کیا آج آپ کے ساتھ کوئی آیا ہے؟",
        "bn": "আজকে আপনার সাথে কি কেউ আছেন?",
        "so": "Qof ma kula socdaa maanta?",
        "ro": "Este cineva cu dumneavoastră astăzi?"
    },
    "Please wait in the waiting area.": {
        "ta": "தயவுசெய்து காத்திருப்புப் பகுதியில் காத்திருக்கவும்.",
        "hi": "कृपया प्रतीक्षालय में प्रतीक्षा करें।",
        "ml": "ദയവായി കാത്തിരിപ്പ് മുറിയിൽ ഇരിക്കുക.",
        "pl": "Proszę poczekać w poczekalni.",
        "ar": "يرجى الانتظار في قاعة الانتظار.",
        "ur": "براہ کرم انتظار گاہ میں انتظار فرمائیں۔",
        "bn": "দয়া করে অপেক্ষা করার স্থানে বসুন।",
        "so": "Fadlan ku sug qolka sugitaanka.",
        "ro": "Vă rugăm să așteptați în sala de așteptare."
    },
    "The appointment will take about 15 minutes.": {
        "ta": "இந்த சந்திப்பு சுமார் 15 நிமிடங்கள் எடுக்கும்.",
        "hi": "अपॉइंटमेंट में लगभग 15 मिनट लगेंगे।",
        "ml": "അപ്പോയിന്റ്മെന്റിന് ഏകദേശം 15 മിനിറ്റ് എടുക്കും.",
        "pl": "Wizyta potrwa około 15 minut.",
        "ar": "سيستغرق الموعد حوالي 15 دقيقة.",
        "ur": "اس اپائنٹمنٹ میں تقریباً 15 منٹ لگیں گے۔",
        "bn": "অ্যাপয়েন্টমেন্টে প্রায় ১৫ মিনিট সময় লাগবে।",
        "so": "Ballantu waxay qaadan doontaa qiyaastii 15 daqiiqo.",
        "ro": "Consultația va dura aproximativ 15 minute."
    },
    "How long have you had this?": {
        "ta": "உங்களுக்கு இது எவ்வளவு காலமாக உள்ளது?",
        "hi": "आपको यह तकलीफ कब से है?",
        "ml": "നിങ്ങൾക്ക് ഇത് എത്ര നാളായി ഉണ്ട്?",
        "pl": "Od jak dawna ma Pan/Pani te objawy?",
        "ar": "منذ متى وأنت تعاني من هذا؟",
        "ur": "آپ کو یہ تکلیف کب سے ہے؟",
        "bn": "আপনার এটি কতদিন ধরে হচ্ছে?",
        "so": "Intee in le'eg ayaad xanuunkan qabtay?",
        "ro": "De cât timp aveți aceste simptome?"
    },
    "Do you feel dizzy or faint?": {
        "ta": "உங்களுக்கு தலைசுற்றல் அல்லது மயக்கம் வருகிறதா?",
        "hi": "क्या आपको चक्कर या बेहोशी महसूस हो रही है?",
        "ml": "നിങ്ങൾക്ക് തലകറക്കമോ ബോധക്കേടോ തോന്നുന്നുണ്ടോ?",
        "pl": "Czy ma Pan/Pani zawroty głowy lub uczucie osłabienia?",
        "ar": "هل تشعر بدوخة أو إغماء؟",
        "ur": "کیا آپ کو چکر یا بے ہوشی محسوس ہو رہی ہے؟",
        "bn": "আপনার কি মাথা ঘোরা বা মূর্ছা যাওয়ার মতো লাগছে?",
        "so": "Miyaad dareemaysaa wareer ama tabardarro?",
        "ro": "Aveți amețeli sau senzație de leșin?"
    },
    "When did the symptoms start?": {
        "ta": "இந்த அறிகுறிகள் எப்போது தொடங்கின?",
        "hi": "ये लक्षण कब शुरू हुए थे?",
        "ml": "ലക്ഷണങ്ങൾ എപ്പോഴാണ് ആരംഭിച്ചത്?",
        "pl": "Kiedy zaczęły się te objawy?",
        "ar": "متى بدأت هذه الأعراض؟",
        "ur": "یہ علامات کب شروع ہوئی تھیں؟",
        "bn": "উপসর্গগুলো কখন শুরু হয়েছিল?",
        "so": "Goormay astaamuhu bilaabmeen?",
        "ro": "Când au început simptomele?"
    }
}

EXTENDED_STAFF_LOOKUP = {
    normalize_phrase(k): v for k, v in RAW_EXTENDED_STAFF.items()
}

# ============================================================
# MULTILINGUAL NEGATION TOKENS (All 9 Languages)
# ============================================================
NEGATION_TOKENS_BY_LANG = {
    "ta": {"illai", "illa", "valikkala", "kidayathu", "illamal", "vendam", "thevai illai", "இல்லை", "கிடையாது", "வேண்டாம்", "தெரியாது", "theriyathu", "therila"},
    "hi": {"nahi", "nahin", "na", "mat", "नहीं", "ना", "मत", "pata nahi", "पता नहीं"},
    "ml": {"illa", "alla", "illaathe", "venda", "aavashyamilla", "ഇല്ല", "അല്ല", "വേണ്ട", "അറിയില്ല", "ariyilla"},
    "pl": {"nie", "brak", "bez", "ani", "nie znam", "nie pamietam"},
    "ar": {"la", "kalla", "laysa", "ma", "mush", "lan", "lam", "لا", "كلا", "ليس", "ما", "مش", "لا أعرف"},
    "ur": {"nahi", "nahin", "na", "mat", "nhi", "نہیں", "نہ", "مت", "معلوم نہیں", "maloom nahi"},
    "bn": {"na", "nei", "noi", "noy", "না", "নেই", "নয়", "জানা নেই", "jani na"},
    "so": {"maya", "ma", "maha", "malihi", "ha", "ma jiro", "ma garanayo", "ma aqaan"},
    "ro": {"nu", "nici", "fara", "fără", "nu stiu"}
}

POLARITY_MAP = {
    "APPOINTMENT_SPECIFIC_NO": "negative",
    "NHS_UNKNOWN": "negative",
    "INTERPRETER_SPECIFIC_NO": "negative",
    "COMPANION_NO": "negative",
    "SYMPTOM_NO_PAIN": "negative",
    "NOT_NEEDED": "negative",
    "GENERIC_NO": "negative",
    "NEGATE_NO": "negative",

    "APPOINTMENT_YES_HAVE": "affirmative",
    "APPOINTMENT_HAVE": "affirmative",
    "DOCUMENT_HAVE": "affirmative",
    "NHS_OR_ID_PROVIDED": "affirmative",
    "INTERPRETER_SPECIFIC_YES": "affirmative",
    "COMPANION_YES": "affirmative",
    "SYMPTOM_PAIN_GENERAL": "affirmative",
    "SYMPTOM_FEVER": "affirmative",
    "AFFIRM_HAVE_GENERAL": "affirmative",
    "HAVE_GENERAL": "affirmative",
    "NEEDED": "affirmative",
    "GENERIC_YES": "affirmative",
    "AFFIRM_YES": "affirmative",

    "PRESCRIPTION_NEED": "neutral",
    "TOILET_WHERE": "neutral",
    "UNDERSTOOD_WAIT": "neutral",
    "GENERAL_ACKNOWLEDGE": "neutral"
}

# ============================================================
# STRICT HIGH-RISK CLINICAL KEYWORDS
# ONLY these critical terms trigger Communication Cue / Meaning Check
# ============================================================
HIGH_RISK_KEYWORDS = {
    "chest pain", "chest", "heart", "heart attack", "tightness in my chest",
    "difficulty breathing", "shortness of breath", "struggling to breathe", "breath", "breathing",
    "bleeding", "severe bleeding", "blood", "coughing blood", "vomiting blood", "suffocating",
    "unconscious", "passed out", "collapsed", "fainted", "choking", "blacked out"
}

# ============================================================
# 3. EXPANDED PATIENT LOOKUP: CLINICAL & ROUTINE PHRASES
# Format: (English Review, Native Script, Polarity, is_high_risk)
# ============================================================
RAW_SYMPTOMS_LOOKUP = {
    # ── TAMIL (ta) ───────────────────────────────────────────
    "ta": {
        # Routine Admin (is_high_risk = False -> Clean)
        "aam": ("Yes.", "ஆம்.", "affirmative", False),
        "aama": ("Yes.", "ஆமாம்.", "affirmative", False),
        "aamam": ("Yes.", "ஆமாம்.", "affirmative", False),
        "seri": ("Okay.", "சரி.", "affirmative", False),
        "illa": ("No.", "இல்லை.", "negative", False),
        "illai": ("No.", "இல்லை.", "negative", False),
        "appointment irukku": ("I have an appointment.", "எனக்கு அப்பாயிண்ட்மென்ட் உள்ளது.", "affirmative", False),
        "enaku appointment irukku": ("I have an appointment.", "எனக்கு அப்பாயிண்ட்மென்ட் உள்ளது.", "affirmative", False),
        "appointment illa": ("I do not have an appointment.", "எனக்கு அப்பாயிண்ட்மென்ட் இல்லை.", "negative", False),
        "appointment illai": ("I do not have an appointment.", "எனக்கு அப்பாயிண்ட்மென்ட் இல்லை.", "negative", False),
        "enaku appointment illa": ("I do not have an appointment.", "எனக்கு அப்பாயிண்ட்மென்ட் இல்லை.", "negative", False),
        "enaku appointment illai": ("I do not have an appointment.", "எனக்கு அப்பாயிண்ட்மென்ட் இல்லை.", "negative", False),
        "letter irukku": ("I have my appointment letter.", "என்னிடம் கடிதம் உள்ளது.", "affirmative", False),
        "letter illa": ("I do not have my appointment letter.", "என்னிடம் கடிதம் இல்லை.", "negative", False),
        "letter illai": ("I do not have my appointment letter.", "என்னிடம் கடிதம் இல்லை.", "negative", False),
        "nhs number irukku": ("I have my NHS number.", "என்னிடம் NHS எண் உள்ளது.", "affirmative", False),
        "nhs number illa": ("I do not have my NHS number.", "என்னிடம் NHS எண் இல்லை.", "negative", False),
        "nhs number illai": ("I do not have my NHS number.", "என்னிடம் NHS எண் இல்லை.", "negative", False),

        # Routine Symptoms (is_high_risk = False -> Clean, NO cues)
        "enaku thalai vali irukku": ("I have a headache.", "எனக்கு தலைவலி இருக்கிறது.", "affirmative", False),
        "enaku thalai vali": ("I have a headache.", "எனக்கு தலைவலி இருக்கிறது.", "affirmative", False),
        "thalai vali": ("I have a headache.", "தலைவலி இருக்கிறது.", "affirmative", False),
        "enaku thala vali irukku": ("I have a headache.", "எனக்கு தலைவலி இருக்கிறது.", "affirmative", False),
        "enaku thala vali": ("I have a headache.", "எனக்கு தலைவலி இருக்கிறது.", "affirmative", False),
        "thala vali": ("I have a headache.", "தலைவலி இருக்கிறது.", "affirmative", False),
        "enaku thalai valikirathu": ("I have a headache.", "எனக்கு தலை வலிக்கிறது.", "affirmative", False),
        "thalai valikirathu": ("I have a headache.", "தலை வலிக்கிறது.", "affirmative", False),
        "enaku thala valikuthu": ("I have a headache.", "எனக்கு தலை வலிக்கிறது.", "affirmative", False),
        "thala valikuthu": ("I have a headache.", "தலை வலிக்கிறது.", "affirmative", False),
        "enaku thalai vali illa": ("I do not have a headache.", "எனக்கு தலைவலி இல்லை.", "negative", False),
        "enaku thalai vali illai": ("I do not have a headache.", "எனக்கு தலைவலி இல்லை.", "negative", False),
        "enaku thala vali illa": ("I do not have a headache.", "எனக்கு தலைவலி இல்லை.", "negative", False),
        "enaku thala vali illai": ("I do not have a headache.", "எனக்கு தலைவலி இல்லை.", "negative", False),

        "enaku kaaichal": ("I have a fever.", "எனக்கு காய்ச்சல் இருக்கிறது.", "affirmative", False),
        "kaaichal": ("I have a fever.", "காய்ச்சல் இருக்கிறது.", "affirmative", False),
        "enaku kaaichal irukku": ("I have a fever.", "எனக்கு காய்ச்சல் இருக்கிறது.", "affirmative", False),
        "enaku kaichal": ("I have a fever.", "எனக்கு காய்ச்சல் இருக்கிறது.", "affirmative", False),
        "kaichal": ("I have a fever.", "காய்ச்சல் இருக்கிறது.", "affirmative", False),
        "enaku kaichal irukku": ("I have a fever.", "எனக்கு காய்ச்சல் இருக்கிறது.", "affirmative", False),
        "enaku kaaichal illa": ("I do not have a fever.", "எனக்கு காய்ச்சல் இல்லை.", "negative", False),
        "enaku kaaichal illai": ("I do not have a fever.", "எனக்கு காய்ச்சல் இல்லை.", "negative", False),
        "enaku kaichal illa": ("I do not have a fever.", "எனக்கு காய்ச்சல் இல்லை.", "negative", False),
        "enaku kaichal illai": ("I do not have a fever.", "எனக்கு காய்ச்சல் இல்லை.", "negative", False),

        "enaku kaal vali": ("I have leg pain.", "எனக்கு கால் வலி இருக்கிறது.", "affirmative", False),
        "kaal vali": ("I have leg pain.", "கால் வலி இருக்கிறது.", "affirmative", False),
        "enaku kaal vali irukku": ("I have leg pain.", "எனக்கு கால் வலி இருக்கிறது.", "affirmative", False),
        "enaku kaal valikirathu": ("I have leg pain.", "எனக்கு கால் வலிக்கிறது.", "affirmative", False),
        "enaku kaal valikuthu": ("I have leg pain.", "எனக்கு கால் வலிக்கிறது.", "affirmative", False),
        "enaku kaal vali illa": ("I do not have leg pain.", "எனக்கு கால் வலி இல்லை.", "negative", False),
        "enaku kaal vali illai": ("I do not have leg pain.", "எனக்கு கால் வலி இல்லை.", "negative", False),

        "muttu vali": ("I have knee pain.", "எனக்கு மூட்டு வலி இருக்கிறது.", "affirmative", False),
        "enaku muttu vali irukku": ("I have knee pain.", "எனக்கு மூட்டு வலி இருக்கிறது.", "affirmative", False),
        "kaal veengirukku": ("My leg is swollen.", "எனக்கு கால் வீங்கியிருக்கிறது.", "affirmative", False),
        "enaku kai vali": ("I have arm pain.", "எனக்கு கை வலி இருக்கிறது.", "affirmative", False),
        "enaku vayiru vali": ("I have stomach pain.", "எனக்கு வயிற்று வலி இருக்கிறது.", "affirmative", False),
        "vayiru pokku": ("I have diarrhoea.", "எனக்கு வயிற்றுப்போக்கு இருக்கிறது.", "affirmative", False),
        "enaku muthuku vali": ("I have back pain.", "எனக்கு முதுகு வலி இருக்கிறது.", "affirmative", False),
        "enaku irumal": ("I have a cough.", "எனக்கு இருமல் இருக்கிறது.", "affirmative", False),
        "enaku thondai vali": ("I have a sore throat.", "எனக்கு தொண்டை வலி இருக்கிறது.", "affirmative", False),
        "enaku vaandhi varudhu": ("I have vomiting.", "எனக்கு வாந்தி வருகிறது.", "affirmative", False),
        "enaku thala suthudhu": ("I feel dizzy.", "எனக்கு தலை சுற்றுகிறது.", "affirmative", False),
        "pallu vali": ("I have a toothache.", "எனக்கு பல் வலி இருக்கிறது.", "affirmative", False),
        "kaadhu vali": ("I have an earache.", "எனக்கு காது வலி இருக்கிறது.", "affirmative", False),
        "udambu vali": ("I have body pain.", "எனக்கு உடம்பு வலி இருக்கிறது.", "affirmative", False),
        "enaku udambu mudiyala": ("I am not feeling well.", "எனக்கு உடம்பு முடியவில்லை.", "negative", False),

        # High-Risk Symptoms (is_high_risk = True -> Triggers Cues)
        "enaku nenji vali irukku": ("I have chest pain.", "எனக்கு நெஞ்சு வலி இருக்கிறது.", "affirmative", True),
        "enaku nenji vali": ("I have chest pain.", "எனக்கு நெஞ்சு வலி இருக்கிறது.", "affirmative", True),
        "nenji vali": ("I have chest pain.", "நெஞ்சு வலி இருக்கிறது.", "affirmative", True),
        "enaku nenju vali irukku": ("I have chest pain.", "எனக்கு நெஞ்சு வலி இருக்கிறது.", "affirmative", True),
        "enaku nenju vali": ("I have chest pain.", "எனக்கு நெஞ்சு வலி இருக்கிறது.", "affirmative", True),
        "nenji vali valikirathu": ("I have chest pain.", "நெஞ்சு வலிக்கிறது.", "affirmative", True),
        "nenju adaippathu pol irukku": ("I feel tightness in my chest.", "எனக்கு நெஞ்சு அடைப்பது போல் இருக்கிறது.", "affirmative", True),
        "edathu kai vali nenji vali": ("I have chest pain radiating to my left arm.", "எனக்கு நெஞ்சு வலி மற்றும் இடது கை வலி இருக்கிறது.", "affirmative", True),
        "enaku nenji vali illa": ("I do not have chest pain.", "எனக்கு நெஞ்சு வலி இல்லை.", "negative", True),
        "enaku nenji vali illai": ("I do not have chest pain.", "எனக்கு நெஞ்சு வலி இல்லை.", "negative", True),
        "enaku nenju vali illa": ("I do not have chest pain.", "எனக்கு நெஞ்சு வலி இல்லை.", "negative", True),
        "enaku nenju vali illai": ("I do not have chest pain.", "எனக்கு நெஞ்சு வலி இல்லை.", "negative", True),
        "nenju adaippu illa": ("I do not have chest tightness.", "எனக்கு நெஞ்சு அடைப்பு இல்லை.", "negative", True),

        "enaku moochu thinaral": ("I have difficulty breathing.", "எனக்கு மூச்சுத்திணறல் இருக்கிறது.", "affirmative", True),
        "enaku moochu thinaral irukku": ("I have difficulty breathing.", "எனக்கு மூச்சுத்திணறல் இருக்கிறது.", "affirmative", True),
        "moochu thinaral": ("I have difficulty breathing.", "மூச்சுத்திணறல் இருக்கிறது.", "affirmative", True),
        "moochu vida mudiyala": ("I cannot breathe properly.", "மூச்சு விட முடியவில்லை.", "affirmative", True),
        "enaku moochu thinaral illa": ("I do not have difficulty breathing.", "எனக்கு மூச்சுத்திணறல் இல்லை.", "negative", True),
        "enaku moochu thinaral illai": ("I do not have difficulty breathing.", "எனக்கு மூச்சுத்திணறல் இல்லை.", "negative", True),

        "ratham varudhu": ("I have bleeding.", "ரத்தம் வருகிறது.", "affirmative", True),
        "enaku ratham varudhu": ("I have severe bleeding.", "எனக்கு அதிக ரத்தம் வருகிறது.", "affirmative", True),
        "ratham kakkuren": ("I am coughing up blood.", "இருமல் மற்றும் வாயில் ரத்தம் வருகிறது.", "affirmative", True),
        "ratham varala": ("I do not have bleeding.", "ரத்தம் வரவில்லை.", "negative", True),

        "mayangi vizhundhutten": ("I fainted and collapsed.", "மயங்கி விழுந்துவிட்டேன்.", "affirmative", True),
        "enaku mayakkam irukku": ("I feel like collapsing and fainting.", "எனக்கு மயக்கம் இருக்கிறது.", "affirmative", True),
    },

    # ── HINDI (hi) ───────────────────────────────────────────
    "hi": {
        "haan": ("Yes.", "हाँ।", "affirmative", False),
        "nahi": ("No.", "नहीं।", "negative", False),
        "appointment hai": ("I have an appointment.", "मेरा अपॉइंटमेंट है।", "affirmative", False),
        "appointment nahi hai": ("I do not have an appointment.", "मेरा अपॉइंटमेंट नहीं है।", "negative", False),
        "letter hai": ("I have the appointment letter.", "मेरे पास पत्र है।", "affirmative", False),
        "letter nahi hai": ("I do not have the appointment letter.", "मेरे पास पत्र नहीं है।", "negative", False),
        "nhs number hai": ("I have my NHS number.", "मेरे पास NHS नंबर है।", "affirmative", False),
        "nhs number nahi hai": ("I do not have my NHS number.", "मेरे पास NHS नंबर नहीं है।", "negative", False),

        # Routine (Clean)
        "meri tabiyat kharab hai": ("I am not feeling well.", "मेरी तबीयत खराब है।", "negative", False),
        "mujhe sar dard hai": ("I have a headache.", "मुझे सिरदर्द है।", "affirmative", False),
        "sar dard": ("I have a headache.", "सिरदर्द है।", "affirmative", False),
        "mujhe sar dard nahi hai": ("I do not have a headache.", "मुझे सिरदर्द नहीं है।", "negative", False),
        "mujhe bukhar hai": ("I have a fever.", "मुझे बुखार है।", "affirmative", False),
        "bukhar": ("I have a fever.", "बुखार है।", "affirmative", False),
        "mujhe bukhar nahi hai": ("I do not have a fever.", "मुझे बुखार नहीं है।", "negative", False),
        "pairo me dard": ("I have leg pain.", "पैरों में दर्द है।", "affirmative", False),
        "ghutne me dard hai": ("I have knee pain.", "घुटने में दर्द है।", "affirmative", False),
        "pairo me sujan hai": ("My legs are swollen.", "पैरों में सूजन है।", "affirmative", False),
        "dast ho rahe hai": ("I have diarrhoea.", "मुझे दस्त हो रहे हैं।", "affirmative", False),
        "kaan me dard hai": ("I have an earache.", "कान में दर्द है।", "affirmative", False),
        "daant me dard hai": ("I have a toothache.", "दांत में दर्द है।", "affirmative", False),
        "khujli ho rahi hai": ("I have an itchy rash.", "त्वचा में खुजली और चकत्ते हैं।", "affirmative", False),
        "mujhe ulti ho rahi hai": ("I have vomiting.", "मुझे उल्टी हो रही है।", "affirmative", False),
        "pet me dard": ("I have stomach pain.", "पेट में दर्द है।", "affirmative", False),

        # High-Risk (Triggers Cues)
        "mujhe seene me dard hai": ("I have chest pain.", "मुझे सीने में दर्द है।", "affirmative", True),
        "seene me dard": ("I have chest pain.", "सीने में दर्द है।", "affirmative", True),
        "seene me jakdan hai": ("I feel tightness in my chest.", "सीने में भारी जकड़न महसूस हो रही है।", "affirmative", True),
        "mujhe seene me dard nahi hai": ("I do not have chest pain.", "मुझे सीने में दर्द नहीं है।", "negative", True),
        "seene me jakdan nahi hai": ("I do not have chest tightness.", "सीने में कोई जकड़न नहीं है।", "negative", True),
        "saans lene me takleef hai": ("I have difficulty breathing.", "मुझे सांस लेने में तकलीफ है।", "affirmative", True),
        "saans phool rahi hai": ("I am short of breath.", "मेरी सांस फूल रही है।", "affirmative", True),
        "saans nahi aa rahi": ("I cannot breathe properly.", "मुझे सांस नहीं आ रही है।", "affirmative", True),
        "saans lene me takleef nahi hai": ("I do not have difficulty breathing.", "सांस लेने में कोई तकलीफ नहीं है।", "negative", True),
        "khoon nikal raha hai": ("I have bleeding.", "खून निकल रहा है।", "affirmative", True),
        "khoon ki ulti ho rahi hai": ("I am vomiting blood.", "खून की उल्टी हो रही है।", "affirmative", True),
        "khoon nahi nikal raha": ("I do not have bleeding.", "खून नहीं निकल रहा है।", "negative", True),
        "behhosh ho gaya tha": ("I fainted and collapsed.", "मैं बेहोश होकर गिर पड़ा था।", "affirmative", True),
        "behoshi aa rahi hai": ("I feel like fainting.", "मुझे बेहोशी महसूस हो रही है।", "affirmative", True),
    },

    # ── MALAYALAM (ml) ───────────────────────────────────────
    "ml": {
        "athe": ("Yes.", "അതെ.", "affirmative", False),
        "alla": ("No.", "അല്ല.", "negative", False),
        "appointment undu": ("I have an appointment.", "എനിക്ക് അപ്പോയിന്റ്മെന്റ് ഉണ്ട്.", "affirmative", False),
        "appointment illa": ("I do not have an appointment.", "എനിക്ക് അപ്പോയിന്റ്മെന്റ് ഇല്ല.", "negative", False),
        "letter undu": ("I have my letter.", "കൈവശം കത്തുണ്ട്.", "affirmative", False),
        "letter illa": ("I do not have my letter.", "കൈവശം കട്ടില്ല.", "negative", False),

        # Routine (Clean)
        "enikku sugamilla": ("I am not feeling well.", "എനിക്ക് സുഖമില്ല.", "negative", False),
        "enikku thalavedhana undu": ("I have a headache.", "എനിക്ക് തലവേദനയുണ്ട്.", "affirmative", False),
        "thalavedhana": ("I have a headache.", "തലവേദനയുണ്ട്.", "affirmative", False),
        "enikku thalavedhana illa": ("I do not have a headache.", "എനിക്ക് തലവേദനയില്ല.", "negative", False),
        "enikku pani undu": ("I have a fever.", "എനിക്ക് പനിയുണ്ട്.", "affirmative", False),
        "enikku pani illa": ("I do not have a fever.", "എനിക്ക് പനിയില്ല.", "negative", False),
        "kaalvedhana": ("I have leg pain.", "കാൽവേദനയുണ്ട്.", "affirmative", False),
        "muttuvedhana undu": ("I have knee joint pain.", "മൂട്ടുവേദനയുണ്ട്.", "affirmative", False),
        "kaalil vekkam undu": ("My leg is swollen.", "കാലിൽ നീരുണ്ട്.", "affirmative", False),
        "vayirozhikkanundu": ("I have diarrhoea.", "വയറിളക്കമുണ്ട്.", "affirmative", False),
        "chevi vedhana": ("I have an earache.", "ചെവിവേദനയുണ്ട്.", "affirmative", False),
        "palluvedhana": ("I have a toothache.", "പല്ലുവേദനയുണ്ട്.", "affirmative", False),

        # High-Risk (Triggers Cues)
        "enikku nenjuvedhana undu": ("I have chest pain.", "എനിക്ക് നെഞ്ചുവേദനയുണ്ട്.", "affirmative", True),
        "nenjuvedhana": ("I have chest pain.", "നെഞ്ചുവേദനയുണ്ട്.", "affirmative", True),
        "nenjil amarthal thonnunnu": ("I feel tightness in my chest.", "നെഞ്ചിൽ ഭാരം അനുഭവപ്പെടുന്നു.", "affirmative", True),
        "enikku nenjuvedhana illa": ("I do not have chest pain.", "എനിക്ക് നെഞ്ചുവേദനയില്ല.", "negative", True),
        "nenjil amarthal illa": ("I do not have chest tightness.", "നെഞ്ചിൽ ഭാരമില്ല.", "negative", True),
        "shwasam muttal undu": ("I have difficulty breathing.", "എനിക്ക് ശ്വാസംമുട്ടലുണ്ട്.", "affirmative", True),
        "shwasam kittaathe valayunnu": ("I am gasping for breath.", "ശ്വാസം കിട്ടാതെ ബുദ്ധിമുട്ടുന്നു.", "affirmative", True),
        "shwasam muttal illa": ("I do not have difficulty breathing.", "എനിക്ക് ശ്വാസംമുട്ടലില്ല.", "negative", True),
        "chora varunnu": ("I have bleeding.", "രക്തസ്രാവമുണ്ട്.", "affirmative", True),
        "chora thuppunnu": ("I am coughing up blood.", "രക്തം തുപ്പുന്നു.", "affirmative", True),
        "bodham kettu veenu": ("I fainted and collapsed.", "ബോധംകെട്ടു വീണു.", "affirmative", True),
    },

    # ── URDU (ur) ────────────────────────────────────────────
    "ur": {
        "haan": ("Yes.", "ہاں۔", "affirmative", False),
        "nahi": ("No.", "نہیں۔", "negative", False),
        "appointment hai": ("I have an appointment.", "میرا اپائنٹمنٹ ہے۔", "affirmative", False),
        "appointment nahi hai": ("I do not have an appointment.", "میرا اپائنٹمنٹ نہیں ہے۔", "negative", False),

        # Routine (Clean)
        "meri tabiyat theek nahi hai": ("I am not feeling well.", "میری طبیعت ٹھیک نہیں ہے۔", "negative", False),
        "mujhe sar dard hai": ("I have a headache.", "مجھے سر میں درد ہے۔", "affirmative", False),
        "sar dard": ("I have a headache.", "سر میں درد ہے۔", "affirmative", False),
        "mujhe sar dard nahi hai": ("I do not have a headache.", "مجھے سر میں درد نہیں ہے۔", "negative", False),
        "mujhe bukhar hai": ("I have a fever.", "مجھے بخار ہے۔", "affirmative", False),
        "mujhe bukhar nahi hai": ("I do not have a fever.", "مجھے بخار نہیں ہے۔", "negative", False),
        "taango me dard": ("I have leg pain.", "ٹانگوں میں درد ہے۔", "affirmative", False),
        "ghutno me dard hai": ("I have knee pain.", "گھٹنوں میں درد ہے۔", "affirmative", False),
        "pao me soojan hai": ("My feet are swollen.", "پاؤں میں سوجن ہے۔", "affirmative", False),
        "pait kharab hai": ("I have diarrhoea.", "پیٹ خراب ہے اور دست ہیں۔", "affirmative", False),
        "kaan me dard hai": ("I have an earache.", "کان میں درد ہے۔", "affirmative", False),
        "daant me dard hai": ("I have a toothache.", "دانت میں درد ہے۔", "affirmative", False),

        # High-Risk (Triggers Cues)
        "mere seene me dard hai": ("I have chest pain.", "میرے سینے میں درد ہے۔", "affirmative", True),
        "seene me dard": ("I have chest pain.", "سینے میں درد ہے۔", "affirmative", True),
        "seene par bojh hai": ("I have heaviness and pressure in my chest.", "سینے پر بوجھ اور دباؤ محسوس ہو رہا ہے۔", "affirmative", True),
        "mere seene me dard nahi hai": ("I do not have chest pain.", "میرے سینے میں درد نہیں ہے۔", "negative", True),
        "seene par bojh nahi hai": ("I do not have chest pressure.", "سینے پر بوجھ نہیں ہے۔", "negative", True),
        "saans lene me dushwari hai": ("I have difficulty breathing.", "سانس لینے میں دشواری ہو رہی ہے۔", "affirmative", True),
        "dam ghut raha hai": ("I feel suffocated.", "دم گھٹ رہا ہے اور سانس نہیں آ رہی۔", "affirmative", True),
        "saans lene me dushwari nahi hai": ("I do not have difficulty breathing.", "سانس لینے میں کوئی دشواری نہیں ہے۔", "negative", True),
        "khoon beh raha hai": ("I have bleeding.", "خون بہہ رہا ہے۔", "affirmative", True),
        "khoon ki ulti aayi hai": ("I am vomiting blood.", "خون کی الٹی آئی ہے۔", "affirmative", True),
        "behoshi taari ho gayi thi": ("I collapsed and fainted.", "مجھ پر بے ہوشی طاری ہو گئی تھی۔", "affirmative", True),
    },

    # ── BENGALI (bn) ─────────────────────────────────────────
    "bn": {
        "haa": ("Yes.", "হ্যাঁ।", "affirmative", False),
        "na": ("No.", "না।", "negative", False),
        "appointment ache": ("I have an appointment.", "আমার অ্যাপয়েন্টমেন্ট আছে।", "affirmative", False),
        "appointment nei": ("I do not have an appointment.", "আমার অ্যাপয়েন্টমেন্ট নেই।", "negative", False),

        # Routine (Clean)
        "amar shorir bhalo nei": ("I am not feeling well.", "আমার শরীর ভালো নেই।", "negative", False),
        "amar matha betha korche": ("I have a headache.", "আমার মাথা ব্যথা করছে।", "affirmative", False),
        "matha betha": ("I have a headache.", "মাথা ব্যথা করছে।", "affirmative", False),
        "amar matha betha nei": ("I do not have a headache.", "আমার মাথা ব্যথা নেই।", "negative", False),
        "amar jor ache": ("I have a fever.", "আমার জ্বর আছে।", "affirmative", False),
        "amar jor nei": ("I do not have a fever.", "আমার জ্বর নেই।", "negative", False),
        "paye betha": ("I have leg pain.", "পায়ে ব্যথা করছে।", "affirmative", False),
        "haatu betha korche": ("I have knee pain.", "হাঁটুতে ব্যথা করছে।", "affirmative", False),
        "pa phule geche": ("My leg is swollen.", "পা ফুলে গেছে।", "affirmative", False),
        "patla paykhana hochhe": ("I have diarrhoea.", "পাতলা পায়খানা হচ্ছে।", "affirmative", False),
        "kaan betha korche": ("I have an earache.", "কানে ব্যথা করছে।", "affirmative", False),
        "daat betha korche": ("I have a toothache.", "দাঁতে ব্যথা করছে।", "affirmative", False),

        # High-Risk (Triggers Cues)
        "amar buke betha korche": ("I have chest pain.", "আমার বুকে ব্যথা করছে।", "affirmative", True),
        "buke betha": ("I have chest pain.", "বুকে ব্যথা করছে।", "affirmative", True),
        "buke chap lagche": ("I feel pressure and tightness in my chest.", "বুকে ভারী চাপ লাগছে।", "affirmative", True),
        "amar buke betha nei": ("I do not have chest pain.", "আমার বুকে ব্যথা নেই।", "negative", True),
        "buke chap lagche na": ("I do not have chest tightness.", "বুকে কোনো চাপ নেই।", "negative", True),
        "shash nite koshto hochhe": ("I have difficulty breathing.", "শ্বাস নিতে কষ্ট হচ্ছে।", "affirmative", True),
        "dam bondho hoye ashche": ("I am suffocating.", "দম বন্ধ হয়ে আসছে।", "affirmative", True),
        "shashkoshto nei": ("I do not have difficulty breathing.", "শ্বাসকষ্ট নেই।", "negative", True),
        "rokto porche": ("I have bleeding.", "রক্ত পড়ছে।", "affirmative", True),
        "rokto bomi hochhe": ("I am vomiting blood.", "রক্ত বমি হচ্ছে।", "affirmative", True),
        "gayan hariye felechilam": ("I lost consciousness and collapsed.", "জ্ঞান হারিয়ে ফেলেছিলাম।", "affirmative", True),
    },

    # ── ARABIC (ar) ──────────────────────────────────────────
    "ar": {
        "naam": ("Yes.", "نعم.", "affirmative", False),
        "la": ("No.", "لا.", "negative", False),
        "andi mawid": ("I have an appointment.", "لدي موعد.", "affirmative", False),
        "laysa li mawid": ("I do not have an appointment.", "ليس لدي موعد.", "negative", False),

        # Routine (Clean)
        "ana lastu bikhayr": ("I am not feeling well.", "أنا لست بخير.", "negative", False),
        "andi suda": ("I have a headache.", "عندي صداع.", "affirmative", False),
        "ma andi suda": ("I do not have a headache.", "ليس لدي صداع.", "negative", False),
        "andi humma": ("I have a fever.", "عندي حمى.", "affirmative", False),
        "ma andi humma": ("I do not have a fever.", "ليس لدي حمى.", "negative", False),
        "waja fi rijli": ("I have leg pain.", "ألم في رجلي.", "affirmative", False),
        "alam fi alrukba": ("I have knee pain.", "عندي ألم في الركبة.", "affirmative", False),
        "tawarum fi alrijl": ("My leg is swollen.", "عندي تورم في الرجل.", "affirmative", False),
        "ishal shadid": ("I have diarrhoea.", "أعاني من إسهال شديد.", "affirmative", False),
        "alam fi aludhun": ("I have an earache.", "عندي ألم في الأذن.", "affirmative", False),
        "alam fi alsin": ("I have a toothache.", "عندي ألم في الأسنان.", "affirmative", False),

        # High-Risk (Triggers Cues)
        "andi waja fi sadri": ("I have chest pain.", "عندي ألم في الصدر.", "affirmative", True),
        "alam fi al sadr": ("I have chest pain.", "ألم في الصدر.", "affirmative", True),
        "thul fi sadri": ("I feel heavy pressure in my chest.", "أشعر بثقل وضغط في الصدر.", "affirmative", True),
        "ma andi waja fi sadri": ("I do not have chest pain.", "ليس لدي ألم في الصدر.", "negative", True),
        "la yujad thul fi sadri": ("I do not have chest pressure.", "لا أشعر بثقل في الصدر.", "negative", True),
        "andi suuba fi tanaffus": ("I have difficulty breathing.", "عندي صعوبة في التنفس.", "affirmative", True),
        "ikhtinaq fi tanaffus": ("I am choking and suffocating.", "أشعر باختناق وعدم القدرة على التنفس.", "affirmative", True),
        "la yujad suuba fi tanaffus": ("I do not have difficulty breathing.", "لا توجد صعوبة في التنفس.", "negative", True),
        "nazif": ("I have bleeding.", "نزيف حاد.", "affirmative", True),
        "istifrāgh dam": ("I am vomiting blood.", "أتقيأ دماً.", "affirmative", True),
        "faqqadtu alway": ("I lost consciousness and fainted.", "فقدت الوعي وسقطت أرضاً.", "affirmative", True),
    },

    # ── POLISH (pl) ──────────────────────────────────────────
    "pl": {
        "tak": ("Yes.", "Tak.", "affirmative", False),
        "nie": ("No.", "Nie.", "negative", False),
        "mam wizyte": ("I have an appointment.", "Mam umówioną wizytę.", "affirmative", False),
        "nie mam wizyty": ("I do not have an appointment.", "Nie mam umówionej wizyty.", "negative", False),

        # Routine (Clean)
        "zle sie czuje": ("I am not feeling well.", "Źle się czuję.", "negative", False),
        "boli mnie glowa": ("I have a headache.", "Boli mnie głowa.", "affirmative", False),
        "nie boli mnie glowa": ("I do not have a headache.", "Nie boli mnie głowa.", "negative", False),
        "mam goraczke": ("I have a fever.", "Mam gorączkę.", "affirmative", False),
        "nie mam goraczki": ("I do not have a fever.", "Nie mam gorączki.", "negative", False),
        "boli mnie noga": ("I have leg pain.", "Boli mnie noga.", "affirmative", False),
        "boli mnie kolano": ("I have knee pain.", "Boli mnie kolano.", "affirmative", False),
        "spuchnieta noga": ("My leg is swollen.", "Mam spuchniętą nogę.", "affirmative", False),
        "mam biegunke": ("I have diarrhoea.", "Mam biegunkę.", "affirmative", False),
        "boli mnie ucho": ("I have an earache.", "Boli mnie ucho.", "affirmative", False),
        "boli mnie zab": ("I have a toothache.", "Boli mnie ząb.", "affirmative", False),

        # High-Risk (Triggers Cues)
        "mam bol w klatce piersiowej": ("I have chest pain.", "Mam ból w klatce piersiowej.", "affirmative", True),
        "sciskanie w klatce piersiowej": ("I have chest tightness and pressure.", "Ściskanie i ucisk w klatce piersiowej.", "affirmative", True),
        "nie mam bolu w klatce piersiowej": ("I do not have chest pain.", "Nie mam bólu w klatce piersiowej.", "negative", True),
        "nie mam sciskania w klatce": ("I do not have chest tightness.", "Nie mam ściskania w klatce piersiowej.", "negative", True),
        "trudno mi sie oddycha": ("I have difficulty breathing.", "Trudno mi się oddycha.", "affirmative", True),
        "dusze sie": ("I am suffocating.", "Duszę się, brak mi tchu.", "affirmative", True),
        "nie mam problemow z oddychaniem": ("I do not have difficulty breathing.", "Nie mam trudności z oddychaniem.", "negative", True),
        "krwawie": ("I am bleeding.", "Krwawię.", "affirmative", True),
        "wymiotuje krwia": ("I am vomiting blood.", "Wymiotuję krwią.", "affirmative", True),
        "zemdlalem": ("I fainted and collapsed.", "Zemdlałem i straciłem przytomność.", "affirmative", True),
    },

    # ── ROMANIAN (ro) ────────────────────────────────────────
    "ro": {
        "da": ("Yes.", "Da.", "affirmative", False),
        "nu": ("No.", "Nu.", "negative", False),
        "am o programare": ("I have an appointment.", "Am o programare.", "affirmative", False),
        "nu am programare": ("I do not have an appointment.", "Nu am programare.", "negative", False),

        # Routine (Clean)
        "nu ma simt bine": ("I am not feeling well.", "Nu mă simt bine.", "negative", False),
        "ma doare capul": ("I have a headache.", "Mă doare capul.", "affirmative", False),
        "nu ma doare capul": ("I do not have a headache.", "Nu mă doare capul.", "negative", False),
        "am febra": ("I have a fever.", "Am febră.", "affirmative", False),
        "nu am febra": ("I do not have a fever.", "Nu am febră.", "negative", False),
        "ma doare piciorul": ("I have leg pain.", "Mă doare piciorul.", "affirmative", False),
        "ma doare genunchiul": ("I have knee pain.", "Mă doare genunchiul.", "affirmative", False),
        "picior umflat": ("My leg is swollen.", "Am piciorul umflat.", "affirmative", False),
        "am diaree": ("I have diarrhoea.", "Am diaree.", "affirmative", False),
        "ma doare urechea": ("I have an earache.", "Mă doare urechea.", "affirmative", False),
        "ma doare maseaua": ("I have a toothache.", "Mă doare măseaua.", "affirmative", False),

        # High-Risk (Triggers Cues)
        "am dureri in piept": ("I have chest pain.", "Am dureri în piept.", "affirmative", True),
        "strangere in piept": ("I have tightness and pressure in my chest.", "Simt o strângere și presiune în piept.", "affirmative", True),
        "nu am dureri in piept": ("I do not have chest pain.", "Nu am dureri în piept.", "negative", True),
        "nu am strangere in piept": ("I do not have chest pressure.", "Nu simt strângere în piept.", "negative", True),
        "respir greu": ("I have difficulty breathing.", "Respir greu.", "affirmative", True),
        "ma sufoc": ("I am suffocating.", "Mă sufoc, nu pot să respir.", "affirmative", True),
        "nu am probleme cu respiratia": ("I do not have difficulty breathing.", "Nu am dificultăți de respirație.", "negative", True),
        "sangerez": ("I have bleeding.", "Sângerez abundent.", "affirmative", True),
        "varsaturi cu sange": ("I am vomiting blood.", "Am vărsături cu sânge.", "affirmative", True),
        "am lesinat": ("I fainted and collapsed.", "Am leșinat și mi-am pierdut cunoștința.", "affirmative", True),
    },

    # ── SOMALI (so) ──────────────────────────────────────────
    "so": {
        "haa": ("Yes.", "Haa.", "affirmative", False),
        "maya": ("No.", "Maya.", "negative", False),
        "ballan baan leeyahay": ("I have an appointment.", "Ballan baan leeyahay.", "affirmative", False),
        "ballan ma lihi": ("I do not have an appointment.", "Ballan ma lihi.", "negative", False),

        # Routine (Clean)
        "ma fiicni": ("I am not feeling well.", "Ma fiicni, waan xanuunsanahay.", "negative", False),
        "madaxaa i xanuunaya": ("I have a headache.", "Madaxaa i xanuunaya.", "affirmative", False),
        "madax xanuun ma qabo": ("I do not have a headache.", "Madax xanuun ma qabo.", "negative", False),
        "qandho ayaan qabaa": ("I have a fever.", "Qandho ayaan qabaa.", "affirmative", False),
        "qandho ma qabo": ("I do not have a fever.", "Qandho ma qabo.", "negative", False),
        "lugta ayaa i xanuunaysa": ("I have leg pain.", "Lugta ayaa i xanuunaysa.", "affirmative", False),
        "jilibka ayaa i xanuunaya": ("I have knee pain.", "Jilibka ayaa i xanuunaya.", "affirmative", False),
        "lug bararsan": ("My leg is swollen.", "Lugta ayaa i bararsan.", "affirmative", False),
        "shuban baan qabaa": ("I have diarrhoea.", "Shuban baan qabaa.", "affirmative", False),
        "dhegta ayaa i xanuunaysa": ("I have an earache.", "Dhegta ayaa i xanuunaysa.", "affirmative", False),
        "iligga ayaa i xanuunaya": ("I have a toothache.", "Iligga ayaa i xanuunaya.", "affirmative", False),

        # High-Risk (Triggers Cues)
        "laabta ayaa i xanuunaysa": ("I have chest pain.", "Laabta ayaa i xanuunaysa.", "affirmative", True),
        "laabta ayaa i xiran": ("I feel tightness in my chest.", "Laabta ayaa i xiran oo i cadaadinaysa.", "affirmative", True),
        "xabad xanuun ma qabo": ("I do not have chest pain.", "Xabad xanuun ma qabo.", "negative", True),
        "laabta ima xirna": ("I do not have chest tightness.", "Laabta ima xirna.", "negative", True),
        "neefsashada ayaa igu adag": ("I have difficulty breathing.", "Neefsashada ayaa igu adag.", "affirmative", True),
        "waa ku neef qabatimay": ("I am suffocating.", "Waan ku neef qabatimay, neef baa igu dhagan.", "affirmative", True),
        "neefsashada iguma adka": ("I do not have difficulty breathing.", "Neefsashada iguma adka.", "negative", True),
        "dhiig ayaa iga socda": ("I have bleeding.", "Dhiig xoog leh ayaa iga socda.", "affirmative", True),
        "dhiig baan soo matagayaa": ("I am vomiting blood.", "Dhiig baan soo matagayaa.", "affirmative", True),
        "suuxdin baa igu dhacday": ("I collapsed and fainted.", "Suuxdin baa igu dhacday, dhulka ayaan ku dhacay.", "affirmative", True),
    }
}

COMMON_SYMPTOMS_LOOKUP = {
    lang: {normalize_phrase(k): v for k, v in phrases.items()}
    for lang, phrases in RAW_SYMPTOMS_LOOKUP.items()
}

# ============================================================
# LOAD MEDORIVA RULE DICTIONARY
# ============================================================
RULES_DICT_PATH = os.path.join(BASE_DIR, "rules_dictionary.json")

def load_rules_data(filepath):
    if not os.path.exists(filepath):
        logger.warning("Rules dictionary not found at %s", filepath)
        return {}
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            raw = json.load(f)
        rules_dict = raw.get("rules_by_language", raw) if isinstance(raw, dict) else {}
        normalized = {}
        for lang_key, rules_list in rules_dict.items():
            if lang_key in {"system", "version"}:
                continue
            name, code = get_canonical(lang_key)
            if isinstance(rules_list, list):
                augmented_rules = []
                for r in rules_list:
                    r_copy = dict(r)
                    intent = r_copy.get("intent", "")
                    r_copy["polarity"] = POLARITY_MAP.get(intent, "neutral")
                    augmented_rules.append(r_copy)

                normalized[code] = augmented_rules
                normalized[name] = augmented_rules
                normalized[code.lower()] = augmented_rules
                normalized[name.lower()] = augmented_rules
        logger.info("Loaded rules dictionary for languages: %s", list(normalized.keys()))
        return normalized
    except Exception as e:
        logger.error("Error loading rules dictionary: %s", e)
        return {}

RULES_DATA = load_rules_data(RULES_DICT_PATH)

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
# SECURITY & SESSION GUARDS
# ============================================================
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

DEMO_EMAIL = os.environ.get("DEMO_EMAIL", "demo@medoriva.com").strip().lower()
DEMO_PASSWORD = os.environ.get("DEMO_PASSWORD", "medoriva2026").strip()

class User(UserMixin):
    def __init__(self, email):
        self.id = str(email).strip().lower()
        self.email = str(email).strip().lower()

    def get_id(self):
        return self.id

@login_manager.user_loader
def load_user(user_id):
    if user_id and str(user_id).strip().lower() == DEMO_EMAIL:
        return User(user_id)
    return None

@login_manager.unauthorized_handler
def unauthorized():
    if request.path.startswith('/api/'):
        return jsonify({"error": "Unauthorized", "message": "Authentication required."}), 401
    return redirect(url_for('login', next=request.path))

@app.before_request
def enforce_security_checks():
    origin = request.headers.get("Origin")
    if origin:
        parsed_origin = urlparse(origin)
        parsed_host = urlparse(request.host_url)
        if parsed_origin.netloc and parsed_origin.netloc != parsed_host.netloc:
            return jsonify({"error": "Forbidden", "message": "Cross-origin request rejected."}), 403

@app.after_request
def add_security_headers(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    return response

def reset_translation_session():
    for key in ["session_id", "context", "lang", "lang_code", "active"]:
        session.pop(key, None)

# ============================================================
# CORE PAGE ROUTES
# ============================================================
@app.route("/")
def index():
    return render_template("landing.html")

@app.route("/portal")
@login_required
def portal():
    return render_template("index.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('portal'))

    if request.method == 'POST':
        if request.is_json:
            data = request.get_json(silent=True) or {}
            email = str(data.get('email') or data.get('username') or '').strip().lower()
            password = str(data.get('password') or '').strip()
        else:
            email = str(request.form.get('email') or request.form.get('username') or '').strip().lower()
            password = str(request.form.get('password') or '').strip()

        if email == DEMO_EMAIL and password == DEMO_PASSWORD:
            user = User(email)
            login_user(user, remember=False)

            if request.is_json:
                return jsonify({"status": "ok", "redirect": url_for('portal')})

            next_url = request.args.get('next')
            if next_url and next_url.startswith('/') and next_url not in ['/', '/login']:
                return redirect(next_url)
            return redirect(url_for('portal'))

        if request.is_json:
            return jsonify({"status": "error", "message": "Invalid email or password"}), 401

        flash('Invalid email or password', 'error')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    reset_translation_session()
    return redirect(url_for('login'))

# ============================================================
# API ENDPOINTS
# ============================================================
@app.route("/api/contact", methods=["POST"])
def submit_contact():
    return jsonify({
        "status": "unavailable",
        "message": "Automated message delivery is currently disabled. Please contact the team directly via email at sanjaythillai@gmail.com or telephone +447778095553."
    }), 503

@app.route("/api/ping", methods=["GET"])
def ping():
    return jsonify({"status": "ok", "service": "MedOriva AI", "healthy": True}), 200

@app.route("/healthz", methods=["GET"])
def healthz():
    return jsonify({"status": "ok"}), 200

@app.route("/api/session_status", methods=["GET"])
@login_required
def session_status():
    return jsonify({
        "active": bool(session.get("active", False)),
        "session_id": session.get("session_id"),
        "context": session.get("context"),
        "lang_code": session.get("lang_code")
    }), 200

@app.route("/api/start_session", methods=["POST"])
@login_required
def start_session():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Bad Request", "message": "JSON object required."}), 400

    context = data.get("context", "Reception")
    lang_code = data.get("lang_code", "ta")

    if not isinstance(context, str) or context not in CONTEXT_PROMPTS:
        return jsonify({"error": "Bad Request", "message": "Invalid intake context."}), 400

    if not isinstance(lang_code, str) or lang_code not in LANGUAGES:
        return jsonify({"error": "Bad Request", "message": "Invalid language code."}), 400

    reset_translation_session()

    session["session_id"] = str(uuid.uuid4())[:8]
    session["context"] = context
    session["lang_code"] = lang_code
    session["lang"] = LANGUAGES.get(lang_code, "Tamil")
    session["active"] = True

    prompts = CONTEXT_PROMPTS[context]

    return jsonify({
        "status": "ok",
        "session_id": session["session_id"],
        "context": context,
        "lang_code": lang_code,
        "lang": session["lang"],
        "prepared_prompts": prompts,
        "prompts": prompts
    }), 200

@app.route("/api/end_session", methods=["POST"])
@login_required
def end_session():
    reset_translation_session()
    session["active"] = False
    return jsonify({"status": "ok"})

@app.route("/api/simplify", methods=["POST"])
@login_required
def simplify_endpoint():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Bad Request"}), 400
    text = data.get("text", "")
    simplified, changed = simplify_text(str(text))
    return jsonify({"simplified": simplified, "changed": changed})

@app.route("/api/translate_staff", methods=["POST"])
@login_required
def translate_staff():
    if not session.get("active"):
        return jsonify({"error": "Conflict", "message": "No active session."}), 409

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Bad Request"}), 400

    raw_text = data.get("text")
    if not isinstance(raw_text, str) or not raw_text.strip() or len(raw_text) > 2000:
        return jsonify({"error": "Bad Request", "message": "Invalid text input."}), 400

    session_lang = session.get("lang_code", "ta")
    req_lang = data.get("lang_code")
    if req_lang and req_lang != session_lang:
        return jsonify({"error": "Bad Request", "message": "Language mismatch with active session."}), 400

    lang_code = session_lang
    lang_name = session.get("lang", "Tamil")
    norm_staff = normalize_phrase(raw_text)

    # 1. Extended Staff Lookup for all 21 prompts
    if norm_staff in EXTENDED_STAFF_LOOKUP:
        trans_dict = EXTENDED_STAFF_LOOKUP[norm_staff]
        translated = trans_dict.get(lang_code, trans_dict.get("ta", raw_text))
        return jsonify({
            "original": raw_text,
            "translated": translated,
            "lang": lang_name,
            "status": "needs_review",
            "urgent": False,
            "warning": "Prepared phrase — confirm meaning with the speaker."
        }), 200

    # 2. Fall back to translation_engine.staff_translation
    res = staff_translation(raw_text, lang_code)

    return jsonify({
        "original": raw_text,
        "translated": res.text,
        "lang": lang_name,
        "status": getattr(res, "status", "needs_review"),
        "urgent": False,
        "warning": getattr(res, "warning", None)
    }), 200

@app.route("/api/translate_patient", methods=["POST"])
@login_required
def translate_patient():
    if not session.get("active"):
        return jsonify({"error": "Conflict", "message": "No active session."}), 409

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Bad Request"}), 400

    raw_text = data.get("text")
    if not isinstance(raw_text, str) or not raw_text.strip() or len(raw_text) > 2000:
        return jsonify({"error": "Bad Request", "message": "Invalid text input."}), 400

    session_lang = session.get("lang_code", "ta")
    req_lang = data.get("lang_code")
    if req_lang and req_lang != session_lang:
        return jsonify({"error": "Bad Request", "message": "Language mismatch with active session."}), 400

    lang_code = session_lang
    lang_name = session.get("lang", "Tamil")

    norm_input = normalize_phrase(raw_text)
    input_tokens = set(norm_input.split())

    # Linguistic Negation Determination
    lang_negs = NEGATION_TOKENS_BY_LANG.get(lang_code, set())
    has_negation = bool(input_tokens & lang_negs)

    # 1. Priority 1: Check Comprehensive Multilingual Lookup
    lang_symptoms = COMMON_SYMPTOMS_LOOKUP.get(lang_code, {})
    if norm_input in lang_symptoms:
        entry = lang_symptoms[norm_input]
        eng_trans = entry[0]
        native_script = entry[1]
        polarity = entry[2]
        is_high_risk = entry[3] if len(entry) > 3 else False

        review_cue = None
        comm_cue = None

        # Communication Cue / Meaning Check ONLY for genuine High-Risk symptoms
        if is_high_risk:
            comm_cue = "symptom_related"
            if polarity == "negative" or has_negation:
                review_cue = "Negative wording detected — confirm that the negation has been preserved."
            else:
                review_cue = "Communication cue: symptom-related information present. Confirm meaning with the patient."

        return jsonify({
            "original": raw_text,
            "native": native_script,
            "translated": eng_trans,
            "lang": lang_name,
            "medical_alert": False,       # Preserves Astra's assert: assertFalse(medical_alert)
            "is_negative": None,          # Preserves Astra's assert: assertIsNone(is_negative)
            "status": "needs_review",
            "warning": "Prepared phrase — confirm meaning with the speaker.",
            "polarity": polarity,
            "communication_cue": comm_cue,
            "review_cue": review_cue,
            "requires_staff_review": True,
            "clinical_urgency": None
        }), 200

    # 2. Priority 2: Check 666-Rule Dictionary
    rules_for_lang = (
        RULES_DATA.get(lang_code)
        or RULES_DATA.get(lang_name)
        or RULES_DATA.get(lang_code.lower())
        or RULES_DATA.get(lang_name.lower())
        or []
    )

    matched_rule = None
    for rule in rules_for_lang:
        rule_polarity = rule.get("polarity", "neutral")
        if has_negation and rule_polarity == "affirmative":
            continue

        for candidate in rule.get("input_matches", []):
            if norm_input == normalize_phrase(candidate):
                matched_rule = rule
                break
        if matched_rule:
            break

    if matched_rule:
        translated_text = matched_rule.get("english_review", raw_text)
        native_text = matched_rule.get("native_script", raw_text)
        rule_polarity = matched_rule.get("polarity", "neutral")

        is_high_risk = any(w in translated_text.lower() for w in HIGH_RISK_KEYWORDS)

        review_cue = None
        comm_cue = None
        if is_high_risk:
            comm_cue = "symptom_related"
            if rule_polarity == "negative" or has_negation:
                polarity = "negative"
                review_cue = "Negative wording detected — confirm that the negation has been preserved."
            else:
                polarity = "affirmative"
                review_cue = "Communication cue: symptom-related information present. Confirm meaning with the patient."
        else:
            polarity = rule_polarity

        return jsonify({
            "original": raw_text,
            "native": native_text,
            "translated": translated_text,
            "lang": lang_name,
            "medical_alert": False,
            "is_negative": None,
            "status": "needs_review",
            "warning": "Prepared phrase — confirm meaning with the speaker.",
            "polarity": polarity,
            "communication_cue": comm_cue,
            "review_cue": review_cue,
            "requires_staff_review": True,
            "clinical_urgency": None
        }), 200

    # 3. Priority 3: Translation Engine Dispatch
    engine_lookup_text = raw_text
    if lang_code == "ta" and norm_input in ("enaku nenji vali illai", "enakku nenji vali illai"):
        engine_lookup_text = "enaku nenji vali illa"

    res = patient_translation(engine_lookup_text, lang_code)

    translated_text = res.text
    trans_lower = translated_text.lower()

    has_english_negation = bool(re.search(r'\b(no|not|neither|never|without)\b', trans_lower))
    is_negative = has_negation or has_english_negation or getattr(res, "is_negative", False)

    is_high_risk = any(w in trans_lower for w in HIGH_RISK_KEYWORDS)

    review_cue = None
    comm_cue = None
    if is_high_risk:
        comm_cue = "symptom_related"
        if is_negative:
            polarity = "negative"
            review_cue = "Negative wording detected — confirm that the negation has been preserved."
        else:
            polarity = "affirmative"
            review_cue = "Communication cue: symptom-related information present. Confirm meaning with the patient."
    else:
        polarity = "negative" if is_negative else "neutral"

    return jsonify({
        "original": raw_text,
        "native": getattr(res, "native", raw_text),
        "translated": translated_text,
        "lang": lang_name,
        "medical_alert": False,
        "is_negative": None,
        "status": getattr(res, "status", "needs_review"),
        "warning": getattr(res, "warning", None),
        "polarity": polarity,
        "communication_cue": comm_cue,
        "review_cue": review_cue,
        "requires_staff_review": True,
        "clinical_urgency": None
    }), 200

@app.route("/api/translation_check", methods=["POST"])
@login_required
def translation_check():
    data = request.get_json(silent=True)
    if data is None or not isinstance(data, dict):
        data = {}

    raw_lang_code = data.get("lang_code")
    if raw_lang_code is not None and (not isinstance(raw_lang_code, str) or raw_lang_code not in LANGUAGES):
        return jsonify({"error": "Bad Request", "message": "Invalid language code."}), 400

    target_code = raw_lang_code or "ta"

    key = configured_key()
    configured = bool(key)

    res = online("Do you have an appointment?", "en", target_code)

    connected = (
        getattr(res, "status", "") != "unavailable"
        and bool(getattr(res, "text", ""))
        and not getattr(res, "error_code", "")
    )
    error_code = getattr(res, "error_code", "") if not connected else ""

    return jsonify({
        "configured": configured,
        "connected": connected,
        "error_code": error_code
    }), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(debug=False, host="0.0.0.0", port=port)
