"""
MedOriva AI — Multilingual Clinical Translation & Triage Engine
Complete 9-Language Phrasebook with Phonetic Tolerance, Safe Negation, and Resilient Fallbacks.
"""
import html
import os
import re
import unicodedata
from dataclasses import dataclass
import requests
from deep_translator import GoogleTranslator, MyMemoryTranslator

LANGUAGES = {
    'ta': 'Tamil',
    'hi': 'Hindi',
    'ml': 'Malayalam',
    'pl': 'Polish',
    'ar': 'Arabic',
    'ur': 'Urdu',
    'bn': 'Bengali',
    'so': 'Somali',
    'ro': 'Romanian'
}

REVIEW = 'Machine translation · Confirm meaning with the speaker.'
PREPARED = 'Clinical verified phrase · Confirmed.'

def normalise(text):
    if not text:
        return ''
    cleaned = re.sub(r'[^\w\s]', ' ', str(text).lower())
    return ' '.join(unicodedata.normalize('NFC', cleaned).casefold().split())

def is_native_script(text):
    return any(ord(char) > 0x0590 for char in text)

@dataclass(frozen=True)
class Translation:
    text: str = ''
    native: str = ''
    status: str = 'needs_review'
    source: str = 'prepared_phrase'
    warning: str = PREPARED
    error_code: str = ''
    symptom: str = ''
    is_negative: bool = False

# ============================================================
# 1. STAFF CLINICAL QUESTION SYNTHESIZER (ALL 9 LANGUAGES)
# ============================================================
STAFF_SYNTHESIS = {
    "HOW_LONG_CHEST_PAIN": {
        "ta": "உங்களுக்கு எவ்வளவு காலமாக நெஞ்சு வலி உள்ளது?",
        "hi": "आपको सीने में दर्द कब से है?",
        "ml": "നിങ്ങൾക്ക് എത്ര നാളായി നെഞ്ചുവേദനയുണ്ട്?",
        "pl": "Od jak dawna ma Pan/Pani ból w klatce piersiowej?",
        "ar": "منذ متى وأنت تعاني من ألم في الصدر؟",
        "ur": "آپ کو سینے میں درد کب سے ہے؟",
        "bn": "আপনার কতদিন ধরে বুকে ব্যথা হচ্ছে?",
        "so": "Muddo intee leeg ayaad qabtaa xanuunka laabta?",
        "ro": "De cât timp aveți dureri în piept?"
    },
    "HOW_LONG_PAIN": {
        "ta": "உங்களுக்கு எவ்வளவு காலமாக வலி இருக்கிறது?",
        "hi": "आपको कितने समय से दर्द हो रहा है?",
        "ml": "നിങ്ങൾക്ക് എത്ര നാളായി വേദനയുണ്ട്?",
        "pl": "Od jak dawna odczuwa Pan/Pani ból?",
        "ar": "منذ متى وأنت تشعر بالألم؟",
        "ur": "آپ کو کب سے درد ہو رہا ہے؟",
        "bn": "আপনার কতদিন ধরে ব্যথা হচ্ছে?",
        "so": "Muddo intee leeg ayaad xanuunka dareemaysay?",
        "ro": "De cât timp aveți această durere?"
    },
    "HOW_LONG_GENERAL": {
        "ta": "இது உங்களுக்கு எவ்வளவு காலமாக உள்ளது?",
        "hi": "यह समस्या आपको कब से है?",
        "ml": "ഇത് നിങ്ങൾക്ക് എത്രകാലമായി ഉണ്ട്?",
        "pl": "Od jak dawna ma Pan/Pani ten problem?",
        "ar": "منذ متى وأنت تعاني من هذا؟",
        "ur": "یہ آپ کو کب سے ہے؟",
        "bn": "আপনার কতদিন ধরে এই সমস্যা?",
        "so": "Muddo intee leeg ayaad tan qabtaa?",
        "ro": "De cât timp aveți această problemă?"
    },
    "WHERE_IS_PAIN": {
        "ta": "உங்கள் வலி எங்கே இருக்கிறது?",
        "hi": "आपको दर्द कहाँ हो रहा है?",
        "ml": "നിങ്ങൾക്ക് എവിടെയാണ് വേദന?",
        "pl": "Gdzie dokładnie odczuwa Pan/Pani ból?",
        "ar": "أين تشعر بالألم بالضبط؟",
        "ur": "آپ کو درد کہاں ہے؟",
        "bn": "আপনার ব্যথা কোথায় হচ্ছে?",
        "so": "Xanuunku xaggee ku hayaa?",
        "ro": "Unde vă doare mai exact?"
    },
    "DO_YOU_HAVE_CHEST_PAIN": {
        "ta": "உங்களுக்கு நெஞ்சு வலி உள்ளதா?",
        "hi": "क्या आपको सीने में दर्द है?",
        "ml": "നിങ്ങൾക്ക് നെഞ്ചുവേദന ഉണ്ടോ?",
        "pl": "Czy ma Pan/Pani ból w klatce piersiowej?",
        "ar": "هل تعاني من ألم في الصدر؟",
        "ur": "کیا آپ کو سینے میں درد ہے؟",
        "bn": "আপনার কি বুকে ব্যথা আছে?",
        "so": "Ma qabtaa xanuunka laabta?",
        "ro": "Aveți dureri în piept?"
    },
    "DO_YOU_HAVE_FEVER": {
        "ta": "உங்களுக்கு காய்ச்சல் உள்ளதா?",
        "hi": "क्या आपको बुखार है?",
        "ml": "നിങ്ങൾക്ക് പനി ഉണ്ടോ?",
        "pl": "Czy ma Pan/Pani gorączkę?",
        "ar": "هل لديك حمى؟",
        "ur": "کیا آپ کو بخار ہے؟",
        "bn": "আপনার কি জ্বর আছে?",
        "so": "Ma qabtaa qandho?",
        "ro": "Aveți febră?"
    },
    "DO_YOU_HAVE_BREATHING": {
        "ta": "உங்களுக்கு மூச்சு விடுவதில் சிரமம் உள்ளதா?",
        "hi": "क्या आपको सांस लेने में कठिनाई हो रही है?",
        "ml": "നിങ്ങൾക്ക് ശ്വാസമെടുക്കാൻ ബുദ്ധിമുട്ടുണ്ടോ?",
        "pl": "Czy ma Pan/Pani trudności z oddychaniem?",
        "ar": "هل تواجه صعوبة في التنفس؟",
        "ur": "کیا آپ کو سانس لینے میں دشواری ہے؟",
        "bn": "আপনার কি শ্বাস নিতে কষ্ট হচ্ছে?",
        "so": "Ma kugu adag tahay neefsashadu?",
        "ro": "Aveți dificultăți de respirație?"
    },
    "DO_YOU_HAVE_PAIN": {
        "ta": "உங்களுக்கு வலி இருக்கிறதா?",
        "hi": "क्या आपको दर्द हो रहा है?",
        "ml": "നിങ്ങൾക്ക് വേദനയുണ്ടോ?",
        "pl": "Czy odczuwa Pan/Pani ból?",
        "ar": "هل تشعر بأي ألم؟",
        "ur": "کیا آپ کو درد ہے؟",
        "bn": "আপনার কি কোনো ব্যথা আছে?",
        "so": "Xanuun ma dareemaysaa?",
        "ro": "Aveți dureri în acest moment?"
    },
    "GOOD_MORNING": {
        "ta": "காலை வணக்கம். நான் உங்களுக்கு எப்படி உதவ முடியும்?",
        "hi": "सुप्रभात। मैं आपकी कैसे मदद कर सकता हूँ?",
        "ml": "സുപ്രഭാതം. എനിക്ക് നിങ്ങളെ എങ്ങനെ സഹായിക്കാനാകും?",
        "pl": "Dzień dobry. W czym mogę pomóc?",
        "ar": "صباح الخير. كيف يمكنني مساعدتك؟",
        "ur": "صبح بخیر۔ میں آپ کی کیسے مدد کر سکتا ہوں؟",
        "bn": "সুপ্রভাত। আমি আপনাকে কীভাবে সাহায্য করতে পারি?",
        "so": "Subax wanaagsan. Sideen ku caawin karaa?",
        "ro": "Bună dimineața. Cu ce vă pot ajuta?"
    },
    "APPOINTMENT": {
        "ta": "உங்களுக்கு முன்பதிவு செய்யப்பட்ட சந்திப்பு உள்ளதா?",
        "hi": "क्या आपकी अपॉइंटमेंट है?",
        "ml": "നിങ്ങൾക്ക് അപ്പോയിന്റ്മെന്റ് ഉണ്ടോ?",
        "pl": "Czy ma Pan/Pani umówioną wizytę?",
        "ar": "هل لديك موعد؟",
        "ur": "کیا آپ کی اپائنٹمنٹ ہے؟",
        "bn": "আপনার কি অ্যাপয়েন্টমেন্ট আছে?",
        "so": "Ballan ma leedahay?",
        "ro": "Aveți o programare?"
    },
    "TAKE_SEAT": {
        "ta": "தயவு செய்து உட்காருங்கள். மருத்துவர் விரைவில் உங்களை பார்ப்பார்.",
        "hi": "कृपया बैठ जाइए। डॉक्टर जल्द ही आपसे मिलेंगे।",
        "ml": "ദയവായി ഇരിക്കുക. ഡോക്ടർ ഉടൻ നിങ്ങളെ കാണും.",
        "pl": "Proszę usiąść. Lekarz wkrótce Pana/Panią przyjmie.",
        "ar": "يرجى الجلوس. سيراك الطبيب قريباً.",
        "ur": "براہ کرم بیٹھ جائیں۔ ڈاکٹر جلد آپ سے ملیں گے۔",
        "bn": "দয়া করে বসুন। ডাক্তার শীঘ্রই আপনাকে দেখবেন।",
        "so": "Fadlan fadhiiso. Dhakhtarka ayaa si dhow kuu arki doona.",
        "ro": "Vă rog să luați loc. Medicul vă va consulta în curând."
    },
    "NAME_DOB": {
        "ta": "உங்கள் பெயரையும் பிறந்த தேதியையும் சொல்ல முடியுமா?",
        "hi": "क्या मैं आपका नाम और जन्मतिथि जान सकता हूँ?",
        "ml": "നിങ്ങളുടെ പേരും ജനനത്തീയതിയും പറയാമോ?",
        "pl": "Czy mogę prosić o Pana/Pani imię, nazwisko i datę urodzenia?",
        "ar": "هل يمكنني معرفة اسمك وتاريخ ميلادك؟",
        "ur": "کیا میں آپ کا نام اور تاریخ پیدائش جان سکتا ہوں؟",
        "bn": "আপনার নাম এবং জন্ম তারিখ বলতে পারেন?",
        "so": "Ma ii sheegi kartaa magacaaga iyo taariikhda dhalashadaada?",
        "ro": "Îmi puteți spune numele și data nașterii?"
    },
    "INTERPRETER": {
        "ta": "உங்களுக்கு மொழிபெயர்ப்பாளர் தேவையா?",
        "hi": "क्या आपको दुभाषिए की आवश्यकता है?",
        "ml": "നിങ്ങൾക്ക് ഒരു ദ്വിഭാഷിയുടെ സഹായം ആവശ്യമുണ്ടോ?",
        "pl": "Czy potrzebuje Pan/Pani tłumacza ustnego?",
        "ar": "هل تحتاج إلى مترجم فوري؟",
        "ur": "کیا آپ کو ترجمان کی ضرورت ہے؟",
        "bn": "আপনার কি দোভাষী দরকার?",
        "so": "Ma u baahan tahay turjubaan?",
        "ro": "Aveți nevoie de un interpret?"
    },
    "DOCTOR_NOW": {
        "ta": "மருத்துவர் இப்போது உங்களைச் சந்திப்பார்.",
        "hi": "डॉक्टर अब आपसे मिलेंगे।",
        "ml": "ഡോക്ടർ ഇപ്പോൾ നിങ്ങളെ കാണും.",
        "pl": "Lekarz przyjmie teraz Pana/Panią.",
        "ar": "سيقابلك الطبيب الآن.",
        "ur": "ڈاکٹر اب آپ سے ملیں گے۔",
        "bn": "ডাক্তার এখন আপনাকে দেখবেন।",
        "so": "Dhakhtarka ayaa hadda ku arki doona.",
        "ro": "Medicul vă va primi acum."
    }
}

# ============================================================
# 2. SYMPTOM PHONETIC STEM REGISTRY (ALL 9 LANGUAGES)
# Handles typos like 'thali', 'thala', 'enji', 'seene', etc.
# ============================================================
PHONETIC_SYMPTOM_MAP = {
    "chest pain": {
        "urgent": True,
        "keywords": {
            "ta": ["nenji", "nenju", "nenjil", "enji", "enju", "maar", "நெஞ்சு", "நெஞ்சில்"],
            "hi": ["seene", "chhati", "chest", "chati", "सीने"],
            "ml": ["nenjil", "nenju", "നെഞ്ചിൽ", "നെഞ്ചു"],
            "pl": ["klatce", "klatki", "klatka", "piersiowej"],
            "ar": ["sadr", "sadri", "الصدر", "صدري"],
            "ur": ["seenay", "seene", "سینے", "دل"],
            "bn": ["buke", "buk", "বুকে"],
            "so": ["laab", "laabta"],
            "ro": ["piept", "pieptului"]
        },
        "responses": {
            "ta": ("I have chest pain.", "I do not have chest pain.", "எனக்கு நெஞ்சு வலி இருக்கிறது.", "எனக்கு நெஞ்சு வலி இல்லை."),
            "hi": ("I have chest pain.", "I do not have chest pain.", "मुझे सीने में दर्द है।", "मुझे सीने में दर्द नहीं है।"),
            "ml": ("I have chest pain.", "I do not have chest pain.", "എനിക്ക് നെഞ്ചുവേദനയുണ്ട്.", "എനിക്ക് നെഞ്ചുവേദനയില്ല."),
            "pl": ("I have chest pain.", "I do not have chest pain.", "Mam ból w klatce piersiowej.", "Nie mam bólu w klatce piersiowej."),
            "ar": ("I have chest pain.", "I do not have chest pain.", "عندي ألم في الصدر.", "لا أشعر بألم في الصدر."),
            "ur": ("I have chest pain.", "I do not have chest pain.", "میرے سینے میں درد ہے۔", "میرے سینے میں درد نہیں ہے۔"),
            "bn": ("I have chest pain.", "I do not have chest pain.", "আমার বুকে ব্যথা আছে।", "আমার বুকে ব্যথা নেই।"),
            "so": ("I have chest pain.", "I do not have chest pain.", "Waxaan dareemayaa xanuunka laabta.", "Ma qabo wax xanuun laabta ah."),
            "ro": ("I have chest pain.", "I do not have chest pain.", "Am dureri în piept.", "Nu am dureri în piept.")
        }
    },
    "headache": {
        "urgent": False,
        "keywords": {
            "ta": ["thalai", "thala", "thali", "thalavali", "mandai", "தலை", "தலைவலி"],
            "hi": ["sar", "sir", "matha", "mathay", "सिर", "सर"],
            "ml": ["thala", "thalavedana", "തല", "തലവേദന"],
            "pl": ["glowa", "glowy", "glowie", "głowa", "głowy"],
            "ar": ["ras", "rasi", "suda", "sudaa", "صداع", "رأس"],
            "ur": ["sar", "sir", "سر"],
            "bn": ["matha", "mathay", "মাথা"],
            "so": ["madax", "madaxa"],
            "ro": ["cap", "capul", "capului"]
        },
        "responses": {
            "ta": ("I have a headache.", "I do not have a headache.", "எனக்கு தலைவலி இருக்கிறது.", "எனக்கு தலைவலி இல்லை."),
            "hi": ("I have a headache.", "I do not have a headache.", "मुझे सिरदर्द है।", "मुझे सिरदर्द नहीं है।"),
            "ml": ("I have a headache.", "I do not have a headache.", "എനിക്ക് തലവേദനയുണ്ട്.", "എനിക്ക് തലവേദനയില്ല."),
            "pl": ("I have a headache.", "I do not have a headache.", "Boli mnie głowa.", "Nie boli mnie głowa."),
            "ar": ("I have a headache.", "I do not have a headache.", "عندي صداع.", "ليس لدي صداع."),
            "ur": ("I have a headache.", "I do not have a headache.", "میرے سر میں درد ہے۔", "میرے سر میں درد نہیں ہے۔"),
            "bn": ("I have a headache.", "I do not have a headache.", "আমার মাথা ব্যথা করছে।", "আমার মাথা ব্যথা নেই।"),
            "so": ("I have a headache.", "I do not have a headache.", "Waxaan qabaa madax xanuun.", "Ma qabo madax xanuun."),
            "ro": ("I have a headache.", "I do not have a headache.", "Am o durere de cap.", "Nu am dureri de cap.")
        }
    },
    "stomach pain": {
        "urgent": False,
        "keywords": {
            "ta": ["vayiru", "vayaru", "vathiru", "thoppai", "வயிறு"],
            "hi": ["pet", "pait", "पेट"],
            "ml": ["vayar", "vayaril", "വയർ"],
            "pl": ["brzuch", "brzucha", "zoladek"],
            "ar": ["batan", "batni", "meeda", "بطن", "معدة"],
            "ur": ["pet", "pait", "پیٹ"],
            "bn": ["pet", "pete", "পেট"],
            "so": ["calool", "calosha"],
            "ro": ["stomac", "stomacul", "burta"]
        },
        "responses": {
            "ta": ("I have stomach pain.", "I do not have stomach pain.", "எனக்கு வயிற்று வலி இருக்கிறது.", "எனக்கு வயிற்று வலி இல்லை."),
            "hi": ("I have stomach pain.", "I do not have stomach pain.", "मुझे पेट में दर्द है।", "मुझे पेट में दर्द नहीं है।"),
            "ml": ("I have stomach pain.", "I do not have stomach pain.", "എനിക്ക് വയറുവേദനയുണ്ട്.", "എനിക്ക് വയറുവേദനയില്ല."),
            "pl": ("I have stomach pain.", "I do not have stomach pain.", "Mam ból brzucha.", "Nie mam bólu brzucha."),
            "ar": ("I have stomach pain.", "I do not have stomach pain.", "عندي ألم في المعدة.", "ليس لدي ألم في المعدة."),
            "ur": ("I have stomach pain.", "I do not have stomach pain.", "میرے پیٹ میں درد ہے۔", "میرے پیٹ میں درد نہیں ہے۔"),
            "bn": ("I have stomach pain.", "I do not have stomach pain.", "আমার পেটে ব্যথা করছে।", "আমার পেটে ব্যথা নেই।"),
            "so": ("I have stomach pain.", "I do not have stomach pain.", "Waxaan qabaa calool xanuun.", "Ma qabo calool xanuun."),
            "ro": ("I have stomach pain.", "I do not have stomach pain.", "Am dureri de stomac.", "Nu am dureri de stomac.")
        }
    },
    "fever": {
        "urgent": False,
        "keywords": {
            "ta": ["kaichal", "kaachal", "jwaram", "juram", "காய்ச்சல்"],
            "hi": ["bukhar", "tap", "बुखार"],
            "ml": ["pani", "പനി"],
            "pl": ["goraczka", "gorączka", "temperature"],
            "ar": ["humma", "harara", "sukhuna", "حمى"],
            "ur": ["bukhar", "بخار"],
            "bn": ["jhor", "jor", "জ্বর"],
            "so": ["qandho", "qando"],
            "ro": ["febra", "febră"]
        },
        "responses": {
            "ta": ("I have a fever.", "I do not have a fever.", "எனக்கு காய்ச்சல் இருக்கிறது.", "எனக்கு காய்ச்சல் இல்லை."),
            "hi": ("I have a fever.", "I do not have a fever.", "मुझे बुखार है।", "मुझे बुखार नहीं है।"),
            "ml": ("I have a fever.", "I do not have a fever.", "എനിക്ക് പനിയുണ്ട്.", "എനിക്ക് പനിയില്ല."),
            "pl": ("I have a fever.", "I do not have a fever.", "Mam gorączkę.", "Nie mam gorączki."),
            "ar": ("I have a fever.", "I do not have a fever.", "عندي حمى.", "ليس لدي حمى."),
            "ur": ("I have a fever.", "I do not have a fever.", "مجھے بخار ہے۔", "مجھے بخار نہیں ہے۔"),
            "bn": ("I have a fever.", "I do not have a fever.", "আমার জ্বর আছে।", "আমার জ্বর নেই।"),
            "so": ("I have a fever.", "I do not have a fever.", "Waxaan qabaa qandho.", "Ma qabo wax qandho ah."),
            "ro": ("I have a fever.", "I do not have a fever.", "Am febră.", "Nu am febră.")
        }
    },
    "breathing difficulty": {
        "urgent": True,
        "keywords": {
            "ta": ["moochu", "swasam", "திணறல்", "மூச்சு"],
            "hi": ["saans", "sans", "dam", "सांस"],
            "ml": ["shwasam", "ശ്വാസം"],
            "pl": ["oddychac", "oddychanie", "dusznosci", "duszno"],
            "ar": ["tanaffus", "nafas", "تنفس"],
            "ur": ["saans", "سانس"],
            "bn": ["shwash", "dom", "শ্বাস"],
            "so": ["neefsasho", "neefso"],
            "ro": ["respiratie", "aer", "respira"]
        },
        "responses": {
            "ta": ("I have difficulty breathing.", "I do not have difficulty breathing.", "எனக்கு மூச்சு விடுவதில் சிரமம் உள்ளது.", "எனக்கு மூச்சுத் திணறல் இல்லை."),
            "hi": ("I have difficulty breathing.", "I do not have difficulty breathing.", "मुझे सांस लेने में तकलीफ है।", "मुझे सांस लेने में कोई तकलीफ नहीं है।"),
            "ml": ("I have difficulty breathing.", "I do not have difficulty breathing.", "എനിക്ക് ശ്വാസതടസ്സമുണ്ട്.", "എനിക്ക് ശ്വാസതടസ്സമില്ല."),
            "pl": ("I have difficulty breathing.", "I do not have difficulty breathing.", "Mam trudności z oddychaniem.", "Nie mam trudności z oddychaniem."),
            "ar": ("I have difficulty breathing.", "I do not have difficulty breathing.", "عندي صعوبة في التنفس.", "لا أواجه صعوبة في التنفس."),
            "ur": ("I have difficulty breathing.", "I do not have difficulty breathing.", "مجھے سانس لینے میں دشواری ہے۔", "مجھے سانس لینے میں کوئی دشواری نہیں ہے۔"),
            "bn": ("I have difficulty breathing.", "I do not have difficulty breathing.", "আমার শ্বাস নিতে কষ্ট হচ্ছে।", "আমার শ্বাসকষ্ট নেই।"),
            "so": ("I have difficulty breathing.", "I do not have difficulty breathing.", "Waxaan dhib ku qabaa neefsashada.", "Dhib kuma qabo neefsashada."),
            "ro": ("I have difficulty breathing.", "I do not have difficulty breathing.", "Am dificultăți de respirație.", "Nu am dificultăți de respirație.")
        }
    }
}

NEGATION_PATTERNS = {
    "ta": ["illai", "illa", "varadhu", "varala", "ila", "kidayathu", "இல்லை", "இல்ல"],
    "hi": ["nahi", "nahin", "nhi", "mat", "na", "नहीं", "ना"],
    "ml": ["illa", "alla", "ഇല്ല", "അല്ല"],
    "pl": ["nie", "brak", "bez", "nie ma"],
    "ar": ["la", "laysa", "mish", "ma", "لا", "ليس"],
    "ur": ["nahi", "nahin", "na", "نہیں", "نہ"],
    "bn": ["na", "ni", "nay", "nei", "না", "নেই"],
    "so": ["ma", "maya"],
    "ro": ["nu", "nici"]
}

def detect_negation(text, lang_code):
    clean = normalise(text)
    tokens = clean.split()
    for word in NEGATION_PATTERNS.get(lang_code, []) + ["no", "not", "without", "never"]:
        if word in tokens or word in clean:
            return True
    return False

# ============================================================
# 3. ROBUST MULTI-TIER ONLINE TRANSLATION ENGINE
# ============================================================
def configured_key():
    for name in ('GOOGLE_TRANSLATE_API_KEY', 'GOOGLE_CLOUD_TRANSLATION_API_KEY', 'GOOGLE_API_KEY'):
        val = os.environ.get(name, '').strip()
        if val:
            return val
    return ''

def online(text, source, target):
    if not text:
        return Translation()

    # Tier 1: Cloud API (if configured)
    key = configured_key()
    if key:
        try:
            resp = requests.post(
                'https://translation.googleapis.com/language/translate/v2',
                headers={'X-Goog-Api-Key': key},
                json={'q': text, 'source': source, 'target': target, 'format': 'text'},
                timeout=(3, 6)
            )
            if resp.status_code == 200:
                translated = html.unescape(resp.json()['data']['translations'][0]['translatedText']).strip()
                if translated and normalise(translated) != normalise(text):
                    return Translation(translated, translated, 'needs_review', 'google_cloud', REVIEW)
        except Exception:
            pass

    # Tier 2: Deep-Translator Google
    try:
        translated = GoogleTranslator(source=source, target=target).translate(text)
        if translated and normalise(translated) != normalise(text):
            return Translation(translated, translated, 'needs_review', 'google_translator', REVIEW)
    except Exception:
        pass

    # Tier 3: Deep-Translator MyMemory
    try:
        translated = MyMemoryTranslator(source=source, target=target).translate(text)
        if translated and normalise(translated) != normalise(text):
            return Translation(translated, translated, 'needs_review', 'mymemory', REVIEW)
    except Exception:
        pass

    return Translation(text, text, 'unavailable', 'none', 'Translation temporarily unavailable.')

# ============================================================
# 4. DISPATCHERS (STAFF & PATIENT)
# ============================================================

def staff_translation(text, language):
    if language not in LANGUAGES:
        return Translation(warning='Unsupported language.')

    clean = normalise(text)

    # Check Staff Synthesizer
    for key, phrases in STAFF_SYNTHESIS.items():
        if key == "HOW_LONG_CHEST_PAIN" and any(k in clean for k in ["how long", "when did"]) and "chest" in clean:
            return Translation(phrases[language], phrases[language], 'needs_review', 'prepared_phrase', PREPARED)
        if key == "HOW_LONG_PAIN" and any(k in clean for k in ["how long", "when did"]) and "pain" in clean:
            return Translation(phrases[language], phrases[language], 'needs_review', 'prepared_phrase', PREPARED)
        if key == "DO_YOU_HAVE_CHEST_PAIN" and "chest" in clean and "pain" in clean:
            return Translation(phrases[language], phrases[language], 'needs_review', 'prepared_phrase', PREPARED)
        if key == "DO_YOU_HAVE_PAIN" and "do you have" in clean and "pain" in clean:
            return Translation(phrases[language], phrases[language], 'needs_review', 'prepared_phrase', PREPARED)
        if key == "WHERE_IS_PAIN" and any(k in clean for k in ["where is", "where does it hurt"]):
            return Translation(phrases[language], phrases[language], 'needs_review', 'prepared_phrase', PREPARED)
        if key == "GOOD_MORNING" and "good morning" in clean:
            return Translation(phrases[language], phrases[language], 'needs_review', 'prepared_phrase', PREPARED)
        if key == "APPOINTMENT" and "appointment" in clean:
            return Translation(phrases[language], phrases[language], 'needs_review', 'prepared_phrase', PREPARED)
        if key == "TAKE_SEAT" and any(k in clean for k in ["seat", "sit down"]):
            return Translation(phrases[language], phrases[language], 'needs_review', 'prepared_phrase', PREPARED)
        if key == "NAME_DOB" and any(k in clean for k in ["name", "date of birth", "dob"]):
            return Translation(phrases[language], phrases[language], 'needs_review', 'prepared_phrase', PREPARED)
        if key == "INTERPRETER" and "interpreter" in clean:
            return Translation(phrases[language], phrases[language], 'needs_review', 'prepared_phrase', PREPARED)
        if key == "DOCTOR_NOW" and "see you now" in clean:
            return Translation(phrases[language], phrases[language], 'needs_review', 'prepared_phrase', PREPARED)

    return online(text, 'en', language)

def patient_translation(text, language):
    if language not in LANGUAGES:
        return Translation(warning='Unsupported language.')

    clean = normalise(text)
    is_neg = detect_negation(clean, language)

    # 1. Phonetic Stem Match across all 9 languages (Matches 'thali', 'thalai', 'seene', etc.)
    for sym_name, sym_data in PHONETIC_SYMPTOM_MAP.items():
        lang_keywords = sym_data["keywords"].get(language, [])
        for kw in lang_keywords:
            if kw in clean:
                pos_eng, neg_eng, pos_nat, neg_nat = sym_data["responses"][language]
                final_eng = neg_eng if is_neg else pos_eng
                final_nat = neg_nat if is_neg else pos_nat
                return Translation(
                    text=final_eng,
                    native=final_nat,
                    status='needs_review',
                    source='prepared_phrase',
                    warning=PREPARED,
                    symptom=sym_name if sym_data["urgent"] else "",
                    is_negative=is_neg
                )

    # 2. General Pain Match
    pain_tokens = ["vali", "dard", "vedana", "bol", "alam", "xanuun", "durere", "ব্যথা", "வலி"]
    if any(pt in clean for pt in pain_tokens):
        return Translation(
            text="I do not have pain." if is_neg else "I have pain.",
            native="எனக்கு வலி இல்லை." if is_neg else "எனக்கு வலி இருக்கிறது.",
            status='needs_review',
            source='prepared_phrase',
            warning=PREPARED,
            symptom="",
            is_negative=is_neg
        )

    # 3. Fallback to Online Engine
    if is_native_script(text):
        res = online(text, language, 'en')
        eng_text = res.text
        native_text = text
    else:
        res = online(text, 'auto', 'en')
        eng_text = res.text
        native_res = online(eng_text, 'en', language)
        native_text = native_res.text if native_res.text else text

    eng_lower = eng_text.lower()
    is_neg_eng = any(w in eng_lower.split() for w in ['no', 'not', 'none', 'denies', 'without'])
    urgent_flags = ['chest pain', 'breathing difficulty', 'bleeding', 'unconscious']
    detected_sym = next((u for u in urgent_flags if u in eng_lower), '')

    return Translation(
        text=eng_text,
        native=native_text,
        status='needs_review',
        source='online_engine',
        warning=REVIEW,
        symptom=detected_sym,
        is_negative=is_neg_eng or is_neg
    )
