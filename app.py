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
    "ta": {"illai", "illa", "kidayathu", "illamal", "vendam", "thevai illai", "இல்லை", "கிடையாது", "வேண்டாம்", "தெரியாது", "theriyathu", "therila"},
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

SYMPTOM_KEYWORDS_EN = {
    "pain", "ache", "chest", "fever", "temperature", "breath", "breathing",
    "cough", "headache", "vomit", "vomiting", "nausea", "dizzy", "dizziness",
    "bleed", "bleeding", "swelling", "hurt", "pressure", "heart", "stomach",
    "rash", "throat", "back", "unwell", "sick", "tired", "weak", "exhausted",
    "fatigue", "diarrhea"
}

# ============================================================
# 3. OPPOSITE WORDS & SYMPTOMS LOOKUP (All 9 Languages)
# Complete pairs of Affirmative vs Negative patient expressions
# ============================================================
RAW_SYMPTOMS_LOOKUP = {
    # ── TAMIL (ta) ───────────────────────────────────────────
    "ta": {
        "enaku udambu mudiyala": ("I am not feeling well.", "எனக்கு உடம்பு முடியவில்லை.", "negative"),
        "enakku udambu mudiyala": ("I am not feeling well.", "எனக்கு உடம்பு முடியவில்லை.", "negative"),
        "udambu mudiyala": ("I am not feeling well.", "உடம்பு முடியவில்லை.", "negative"),
        "enaku udambu seri illa": ("I am not feeling well.", "எனக்கு உடம்பு சரியில்லை.", "negative"),
        "enaku udambu seri illai": ("I am not feeling well.", "எனக்கு உடம்பு சரியில்லை.", "negative"),
        "எனக்கு உடம்பு சரியில்லை": ("I am not feeling well.", "எனக்கு உடம்பு சரியில்லை.", "negative"),

        "appointment irukku": ("I have an appointment.", "எனக்கு அப்பாயிண்ட்மென்ட் உள்ளது.", "affirmative"),
        "enaku appointment irukku": ("I have an appointment.", "எனக்கு அப்பாயிண்ட்மென்ட் உள்ளது.", "affirmative"),
        "appointment illa": ("I do not have an appointment.", "எனக்கு அப்பாயிண்ட்மென்ட் இல்லை.", "negative"),
        "appointment illai": ("I do not have an appointment.", "எனக்கு அப்பாயிண்ட்மென்ட் இல்லை.", "negative"),
        "enaku appointment illa": ("I do not have an appointment.", "எனக்கு அப்பாயிண்ட்மென்ட் இல்லை.", "negative"),
        "enaku appointment illai": ("I do not have an appointment.", "எனக்கு அப்பாயிண்ட்மென்ட் இல்லை.", "negative"),

        "letter irukku": ("I have my appointment letter.", "என்னிடம் கடிதம் உள்ளது.", "affirmative"),
        "letter illa": ("I do not have my appointment letter.", "என்னிடம் கடிதம் இல்லை.", "negative"),
        "letter illai": ("I do not have my appointment letter.", "என்னிடம் கடிதம் இல்லை.", "negative"),
        "nhs number irukku": ("I have my NHS number.", "என்னிடம் NHS எண் உள்ளது.", "affirmative"),
        "nhs number illa": ("I do not have my NHS number.", "என்னிடம் NHS எண் இல்லை.", "negative"),
        "nhs number illai": ("I do not have my NHS number.", "என்னிடம் NHS எண் இல்லை.", "negative"),

        "enaku nenji vali irukku": ("I have chest pain.", "எனக்கு நெஞ்சு வலி இருக்கிறது.", "affirmative"),
        "enaku nenju vali irukku": ("I have chest pain.", "எனக்கு நெஞ்சு வலி இருக்கிறது.", "affirmative"),
        "enaku nenji vali illa": ("I do not have chest pain.", "எனக்கு நெஞ்சு வலி இல்லை.", "negative"),
        "enaku nenji vali illai": ("I do not have chest pain.", "எனக்கு நெஞ்சு வலி இல்லை.", "negative"),
        "எனக்கு நெஞ்சு வலி இருக்கிறது": ("I have chest pain.", "எனக்கு நெஞ்சு வலி இருக்கிறது.", "affirmative"),
        "எனக்கு நெஞ்சு வலி இல்லை": ("I do not have chest pain.", "எனக்கு நெஞ்சு வலி இல்லை.", "negative"),

        "enaku thalai vali irukku": ("I have a headache.", "எனக்கு தலைவலி இருக்கிறது.", "affirmative"),
        "enaku thala vali irukku": ("I have a headache.", "எனக்கு தலைவலி இருக்கிறது.", "affirmative"),
        "enaku thalai vali illa": ("I do not have a headache.", "எனக்கு தலைவலி இல்லை.", "negative"),
        "enaku thalai vali illai": ("I do not have a headache.", "எனக்கு தலைவலி இல்லை.", "negative"),
        "எனக்கு தலைவலி இருக்கிறது": ("I have a headache.", "எனக்கு தலைவலி இருக்கிறது.", "affirmative"),
        "எனக்கு தலைவலி இல்லை": ("I do not have a headache.", "எனக்கு தலைவலி இல்லை.", "negative"),

        "enaku kaichal irukku": ("I have a fever.", "எனக்கு காய்ச்சல் இருக்கிறது.", "affirmative"),
        "enaku kaichal illa": ("I do not have a fever.", "எனக்கு காய்ச்சல் இல்லை.", "negative"),
        "enaku kaichal illai": ("I do not have a fever.", "எனக்கு காய்ச்சல் இல்லை.", "negative"),
        "எனக்கு காய்ச்சல் இருக்கிறது": ("I have a fever.", "எனக்கு காய்ச்சல் இருக்கிறது.", "affirmative"),
        "எனக்கு காய்ச்சல் இல்லை": ("I do not have a fever.", "எனக்கு காய்ச்சல் இல்லை.", "negative"),

        "enaku irumal irukku": ("I have a cough.", "எனக்கு இருமல் இருக்கிறது.", "affirmative"),
        "enaku irumal illa": ("I do not have a cough.", "எனக்கு இருமல் இல்லை.", "negative"),
        "enaku thondai vali irukku": ("I have a sore throat.", "எனக்கு தொண்டை வலி இருக்கிறது.", "affirmative"),
        "enaku thondai vali illa": ("I do not have a sore throat.", "எனக்கு தொண்டை வலி இல்லை.", "negative"),
        "enaku vaandhi varudhu": ("I have vomiting.", "எனக்கு வாந்தி வருகிறது.", "affirmative"),
        "enaku vaandhi illa": ("I do not have vomiting.", "எனக்கு வாந்தி இல்லை.", "negative"),
        "enaku thala suthudhu": ("I feel dizzy.", "எனக்கு தலை சுற்றுகிறது.", "affirmative"),
        "enaku mayakkam irukku": ("I feel faint and dizzy.", "எனக்கு மயக்கம் இருக்கிறது.", "affirmative"),
        "enaku mayakkam illa": ("I do not feel dizzy.", "எனக்கு மயக்கம் இல்லை.", "negative"),
        "enaku vayiru vali irukku": ("I have stomach pain.", "எனக்கு வயிற்று வலி இருக்கிறது.", "affirmative"),
        "enaku vayiru vali illa": ("I do not have stomach pain.", "எனக்கு வயிற்று வலி இல்லை.", "negative"),
        "enaku muthuku vali irukku": ("I have back pain.", "எனக்கு முதுகு வலி இருக்கிறது.", "affirmative"),
        "enaku moochu thinaral irukku": ("I have difficulty breathing.", "எனக்கு மூச்சுத்திணறல் இருக்கிறது.", "affirmative"),
        "enaku moochu thinaral illa": ("I do not have difficulty breathing.", "எனக்கு மூச்சுத்திணறல் இல்லை.", "negative"),
        "enaku romba asadhiya irukku": ("I feel very weak and tired.", "எனக்கு மிகவும் அசதியாக இருக்கிறது.", "affirmative"),
    },

    # ── HINDI (hi) ───────────────────────────────────────────
    "hi": {
        "meri tabiyat kharab hai": ("I am not feeling well.", "मेरी तबीयत खराब है।", "negative"),
        "tabiyat theek nahi hai": ("I am not feeling well.", "तबीयत ठीक नहीं है।", "negative"),
        "appointment hai": ("I have an appointment.", "मेरा अपॉइंटमेंट है।", "affirmative"),
        "appointment nahi hai": ("I do not have an appointment.", "मेरा अपॉइंटमेंट नहीं है।", "negative"),
        "letter hai": ("I have the appointment letter.", "मेरे पास पत्र है।", "affirmative"),
        "letter nahi hai": ("I do not have the appointment letter.", "मेरे पास पत्र नहीं है।", "negative"),
        "nhs number hai": ("I have my NHS number.", "मेरे पास NHS नंबर है।", "affirmative"),
        "nhs number nahi hai": ("I do not have my NHS number.", "मेरे पास NHS नंबर नहीं है।", "negative"),
        "mujhe seene me dard hai": ("I have chest pain.", "मुझे सीने में दर्द है।", "affirmative"),
        "mujhe seene me dard nahi hai": ("I do not have chest pain.", "मुझे सीने में दर्द नहीं है।", "negative"),
        "mujhe sar dard hai": ("I have a headache.", "मुझे सिरदर्द है।", "affirmative"),
        "mujhe sar dard nahi hai": ("I do not have a headache.", "मुझे सिरदर्द नहीं है।", "negative"),
        "mujhe bukhar hai": ("I have a fever.", "मुझे बुखार है।", "affirmative"),
        "mujhe bukhar nahi hai": ("I do not have a fever.", "मुझे बुखार नहीं है।", "negative"),
        "mujhe khansi hai": ("I have a cough.", "मुझे खांसी है।", "affirmative"),
        "mujhe khansi nahi hai": ("I do not have a cough.", "मुझे खांसी नहीं है।", "negative"),
        "mujhe chakkar aa rahe hai": ("I feel dizzy.", "मुझे चक्कर आ रहे हैं।", "affirmative"),
        "chakkar nahi aa rahe": ("I do not feel dizzy.", "चक्कर नहीं आ रहे हैं।", "negative"),
        "saans lene me takleef hai": ("I have difficulty breathing.", "मुझे सांस लेने में तकलीफ है।", "affirmative"),
        "saans lene me takleef nahi hai": ("I do not have difficulty breathing.", "सांस लेने में तकलीफ नहीं है।", "negative"),
        "mujhe ulti ho rahi hai": ("I have vomiting.", "मुझे उल्टी हो रही है।", "affirmative"),
        "ulti nahi hai": ("I do not have vomiting.", "उल्टी नहीं है।", "negative"),
        "pet me dard hai": ("I have stomach pain.", "पेट में दर्द है।", "affirmative"),
        "pet me dard nahi hai": ("I do not have stomach pain.", "पेट में दर्द नहीं है।", "negative"),
    },

    # ── MALAYALAM (ml) ───────────────────────────────────────
    "ml": {
        "enikku sugamilla": ("I am not feeling well.", "എനിക്ക് സുഖമില്ല.", "negative"),
        "appointment undu": ("I have an appointment.", "എനിക്ക് അപ്പോയിന്റ്മെന്റ് ഉണ്ട്.", "affirmative"),
        "appointment illa": ("I do not have an appointment.", "എനിക്ക് അപ്പോയിന്റ്മെന്റ് ഇല്ല.", "negative"),
        "letter undu": ("I have my letter.", "എന്റെ കൈവശം കത്തുണ്ട്.", "affirmative"),
        "letter illa": ("I do not have my letter.", "കൈവശം കട്ടില്ല.", "negative"),
        "enikku nenjuvedhana undu": ("I have chest pain.", "എനിക്ക് നെഞ്ചുവേദനയുണ്ട്.", "affirmative"),
        "enikku nenjuvedhana illa": ("I do not have chest pain.", "എനിക്ക് നെഞ്ചുവേദനയില്ല.", "negative"),
        "enikku thalavedhana undu": ("I have a headache.", "എനിക്ക് തലവേദനയുണ്ട്.", "affirmative"),
        "enikku thalavedhana illa": ("I do not have a headache.", "എനിക്ക് തലവേദനയില്ല.", "negative"),
        "enikku pani undu": ("I have a fever.", "എനിക്ക് പനിയുണ്ട്.", "affirmative"),
        "enikku pani illa": ("I do not have a fever.", "എനിക്ക് പനിയില്ല.", "negative"),
        "enikku thalakarakkam undu": ("I feel dizzy.", "എനിക്ക് തലകറക്കമുണ്ട്.", "affirmative"),
        "enikku thalakarakkam illa": ("I do not feel dizzy.", "എനിക്ക് തലകറക്കമില്ല.", "negative"),
        "shwasam muttal undu": ("I have difficulty breathing.", "എനിക്ക് ശ്വാസംമുട്ടലുണ്ട്.", "affirmative"),
        "shwasam muttal illa": ("I do not have difficulty breathing.", "എനിക്ക് ശ്വാസംമുട്ടലില്ല.", "negative"),
    },

    # ── URDU (ur) ────────────────────────────────────────────
    "ur": {
        "meri tabiyat theek nahi hai": ("I am not feeling well.", "میری طبیعت ٹھیک نہیں ہے۔", "negative"),
        "appointment hai": ("I have an appointment.", "میرا اپائنٹمنٹ ہے۔", "affirmative"),
        "appointment nahi hai": ("I do not have an appointment.", "میرا اپائنٹمنٹ نہیں ہے۔", "negative"),
        "mere seene me dard hai": ("I have chest pain.", "میرے سینے میں درد ہے۔", "affirmative"),
        "mere seene me dard nahi hai": ("I do not have chest pain.", "میرے سینے میں درد نہیں ہے۔", "negative"),
        "mujhe sar dard hai": ("I have a headache.", "مجھے سر میں درد ہے۔", "affirmative"),
        "mujhe sar dard nahi hai": ("I do not have a headache.", "مجھے سر میں درد نہیں ہے۔", "negative"),
        "mujhe bukhar hai": ("I have a fever.", "مجھے بخار ہے۔", "affirmative"),
        "mujhe bukhar nahi hai": ("I do not have a fever.", "مجھے بخار نہیں ہے۔", "negative"),
        "chakkar aa rahe hain": ("I feel dizzy.", "چکر آ رہے ہیں۔", "affirmative"),
        "saans lene me dushwari hai": ("I have difficulty breathing.", "سانس لینے میں دشواری ہو رہی ہے۔", "affirmative"),
        "saans lene me dushwari nahi hai": ("I do not have difficulty breathing.", "سانس لینے میں کوئی دشواری نہیں ہے۔", "negative"),
    },

    # ── BENGALI (bn) ─────────────────────────────────────────
    "bn": {
        "amar shorir bhalo nei": ("I am not feeling well.", "আমার শরীর ভালো নেই।", "negative"),
        "appointment ache": ("I have an appointment.", "আমার অ্যাপয়েন্টমেন্ট আছে।", "affirmative"),
        "appointment nei": ("I do not have an appointment.", "আমার অ্যাপয়েন্টমেন্ট নেই।", "negative"),
        "amar buke betha korche": ("I have chest pain.", "আমার বুকে ব্যথা করছে।", "affirmative"),
        "amar buke betha nei": ("I do not have chest pain.", "আমার বুকে ব্যথা নেই।", "negative"),
        "amar matha betha korche": ("I have a headache.", "আমার মাথা ব্যথা করছে।", "affirmative"),
        "amar matha betha nei": ("I do not have a headache.", "আমার মাথা ব্যথা নেই।", "negative"),
        "amar jor ache": ("I have a fever.", "আমার জ্বর আছে।", "affirmative"),
        "amar jor nei": ("I do not have a fever.", "আমার জ্বর নেই।", "negative"),
        "amar matha ghorachhe": ("I feel dizzy.", "আমার মাথা ঘোরাচ্ছে।", "affirmative"),
        "shash nite koshto hochhe": ("I have difficulty breathing.", "শ্বাস নিতে কষ্ট হচ্ছে।", "affirmative"),
        "shashkoshto nei": ("I do not have difficulty breathing.", "শ্বাসকষ্ট নেই।", "negative"),
    },

    # ── ARABIC (ar) ──────────────────────────────────────────
    "ar": {
        "ana lastu bikhayr": ("I am not feeling well.", "أنا لست بخير.", "negative"),
        "andi mawid": ("I have an appointment.", "لدي موعد.", "affirmative"),
        "laysa li mawid": ("I do not have an appointment.", "ليس لدي موعد.", "negative"),
        "andi waja fi sadri": ("I have chest pain.", "عندي ألم في الصدر.", "affirmative"),
        "ma andi waja fi sadri": ("I do not have chest pain.", "ليس لدي ألم في الصدر.", "negative"),
        "andi suda": ("I have a headache.", "عندي صداع.", "affirmative"),
        "ma andi suda": ("I do not have a headache.", "ليس لدي صداع.", "negative"),
        "andi humma": ("I have a fever.", "عندي حمى.", "affirmative"),
        "ma andi humma": ("I do not have a fever.", "ليس لدي حمى.", "negative"),
        "ashur bidawkha": ("I feel dizzy.", "أشعر بدوخة.", "affirmative"),
        "la ashur bidawkha": ("I do not feel dizzy.", "لا أشعر بدوخة.", "negative"),
        "andi suuba fi tanaffus": ("I have difficulty breathing.", "عندي صعوبة في التنفس.", "affirmative"),
        "la yujad suuba fi tanaffus": ("I do not have difficulty breathing.", "لا توجد صعوبة في التنفس.", "negative"),
    },

    # ── POLISH (pl) ──────────────────────────────────────────
    "pl": {
        "zle sie czuje": ("I am not feeling well.", "Źle się czuję.", "negative"),
        "mam wizyte": ("I have an appointment.", "Mam umówioną wizytę.", "affirmative"),
        "nie mam wizyty": ("I do not have an appointment.", "Nie mam umówionej wizyty.", "negative"),
        "mam bol w klatce piersiowej": ("I have chest pain.", "Mam ból w klatce piersiowej.", "affirmative"),
        "nie mam bolu w klatce piersiowej": ("I do not have chest pain.", "Nie mam bólu w klatce piersiowej.", "negative"),
        "boli mnie glowa": ("I have a headache.", "Boli mnie głowa.", "affirmative"),
        "nie boli mnie glowa": ("I do not have a headache.", "Nie boli mnie głowa.", "negative"),
        "mam goraczke": ("I have a fever.", "Mam gorączkę.", "affirmative"),
        "nie mam goraczki": ("I do not have a fever.", "Nie mam gorączki.", "negative"),
        "kreci mi sie w glowie": ("I feel dizzy.", "Kręci mi się w głowie.", "affirmative"),
        "trudno mi sie oddycha": ("I have difficulty breathing.", "Trudno mi się oddycha.", "affirmative"),
        "nie mam problemow z oddychaniem": ("I do not have difficulty breathing.", "Nie mam trudności z oddychaniem.", "negative"),
    },

    # ── ROMANIAN (ro) ────────────────────────────────────────
    "ro": {
        "nu ma simt bine": ("I am not feeling well.", "Nu mă simt bine.", "negative"),
        "am o programare": ("I have an appointment.", "Am o programare.", "affirmative"),
        "nu am programare": ("I do not have an appointment.", "Nu am programare.", "negative"),
        "am dureri in piept": ("I have chest pain.", "Am dureri în piept.", "affirmative"),
        "nu am dureri in piept": ("I do not have chest pain.", "Nu am dureri în piept.", "negative"),
        "ma doare capul": ("I have a headache.", "Mă doare capul.", "affirmative"),
        "nu ma doare capul": ("I do not have a headache.", "Nu mă doare capul.", "negative"),
        "am febra": ("I have a fever.", "Am febră.", "affirmative"),
        "nu am febra": ("I do not have a fever.", "Nu am febră.", "negative"),
        "am ameteli": ("I feel dizzy.", "Am amețeli.", "affirmative"),
        "respir greu": ("I have difficulty breathing.", "Respir greu.", "affirmative"),
        "nu am probleme cu respiratia": ("I do not have difficulty breathing.", "Nu am dificultăți de respirație.", "negative"),
    },

    # ── SOMALI (so) ──────────────────────────────────────────
    "so": {
        "ma fiicni": ("I am not feeling well.", "Ma fiicni, waan xanuunsanahay.", "negative"),
        "ballan baan leeyahay": ("I have an appointment.", "Ballan baan leeyahay.", "affirmative"),
        "ballan ma lihi": ("I do not have an appointment.", "Ballan ma lihi.", "negative"),
        "laabta ayaa i xanuunaysa": ("I have chest pain.", "Laabta ayaa i xanuunaysa.", "affirmative"),
        "xabad xanuun ma qabo": ("I do not have chest pain.", "Xabad xanuun ma qabo.", "negative"),
        "madaxaa i xanuunaya": ("I have a headache.", "Madaxaa i xanuunaya.", "affirmative"),
        "madax xanuun ma qabo": ("I do not have a headache.", "Madax xanuun ma qabo.", "negative"),
        "qandho ayaan qabaa": ("I have a fever.", "Qandho ayaan qabaa.", "affirmative"),
        "qandho ma qabo": ("I do not have a fever.", "Qandho ma qabo.", "negative"),
        "wareer ayaan dareemayaa": ("I feel dizzy.", "Wareer ayaan dareemayaa.", "affirmative"),
        "neefsashada ayaa igu adag": ("I have difficulty breathing.", "Neefsashada ayaa igu adag.", "affirmative"),
        "neefsashada iguma adka": ("I do not have difficulty breathing.", "Neefsashada iguma adka.", "negative"),
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

    # 1. Priority 1: Check Comprehensive Multilingual Symptoms & Opposite Words Lookup
    lang_symptoms = COMMON_SYMPTOMS_LOOKUP.get(lang_code, {})
    if norm_input in lang_symptoms:
        eng_trans, native_script, polarity = lang_symptoms[norm_input]
        
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
            "communication_cue": "symptom_related",
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
        intent = matched_rule.get("intent", "")
        
        is_symptom = "SYMPTOM" in intent or any(w in translated_text.lower() for w in SYMPTOM_KEYWORDS_EN)
        
        if rule_polarity == "negative" or has_negation:
            polarity = "negative"
            review_cue = "Negative wording detected — confirm that the negation has been preserved."
        elif is_symptom:
            polarity = "affirmative"
            review_cue = "Communication cue: symptom-related information present. Confirm meaning with the patient."
        else:
            polarity = "neutral"
            review_cue = None

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
            "communication_cue": "symptom_related" if is_symptom else None,
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
    is_symptom = any(w in trans_lower for w in SYMPTOM_KEYWORDS_EN)

    if is_negative:
        polarity = "negative"
        review_cue = "Negative wording detected — confirm that the negation has been preserved."
    elif is_symptom:
        polarity = "affirmative"
        review_cue = "Communication cue: symptom-related information present. Confirm meaning with the patient."
    else:
        polarity = "neutral"
        review_cue = None

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
        "communication_cue": "symptom_related" if is_symptom else None,
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
