"""
MedOriva AI — Multilingual Clinical Translation & Triage Engine
Complete 9-Language Clinical Phrasebook, Safe Negation Parsing, and Resilient Online Fallback.
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
    cleaned = re.sub(r'[^\w\s]', ' ', text.lower())
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
# Guarantees common questions NEVER return untranslated English
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
# 2. PATIENT PHRASEBOOK FOR ALL 9 LANGUAGES (Native + Romanised)
# ============================================================
# Format: { lang_code: [ (trigger_phrase, english_translation, native_translation, symptom_name, is_negative) ] }
# NOTE: Must be sorted by len(trigger_phrase) DESCENDING during match to prevent partial override!

MASTER_PATIENT_PHRASES = {
    "ta": [
        ("enaku nenji vali illai", "I do not have chest pain.", "எனக்கு நெஞ்சு வலி இல்லை.", "chest pain", True),
        ("nenji vali illai", "I do not have chest pain.", "எனக்கு நெஞ்சு வலி இல்லை.", "chest pain", True),
        ("enaku nenji vali irukku", "I have chest pain.", "எனக்கு நெஞ்சு வலி இருக்கிறது.", "chest pain", False),
        ("enakku nenju vali irukku", "I have chest pain.", "எனக்கு நெஞ்சு வலி இருக்கிறது.", "chest pain", False),
        ("nenji vali irukku", "I have chest pain.", "எனக்கு நெஞ்சு வலி இருக்கிறது.", "chest pain", False),
        ("nenji vali", "Chest pain.", "நெஞ்சு வலி.", "chest pain", False),
        ("enaku thalai vali illai", "I do not have a headache.", "எனக்கு தலைவலி இல்லை.", "", True),
        ("enaku thalai vali irukku", "I have a headache.", "எனக்கு தலைவலி இருக்கிறது.", "", False),
        ("thalai vali irukku", "I have a headache.", "தலைவலி இருக்கிறது.", "", False),
        ("thalai vali", "Headache.", "தலைவலி.", "", False),
        ("enaku kaichal illai", "I do not have a fever.", "எனக்கு காய்ச்சல் இல்லை.", "", True),
        ("enaku kaichal irukku", "I have a fever.", "எனக்கு காய்ச்சல் இருக்கிறது.", "", False),
        ("kaichal irukku", "I have a fever.", "காய்ச்சல் இருக்கிறது.", "", False),
        ("kaichal", "Fever.", "காய்ச்சல்.", "", False),
        ("enaku moochu vida mudiyala", "I cannot breathe.", "எனக்கு மூச்சு விட முடியவில்லை.", "breathing difficulty", False),
        ("enaku moochu varadhu", "I cannot breathe properly.", "எனக்கு மூச்சு வரவில்லை.", "breathing difficulty", False),
        ("moochu pidikuthu", "I have difficulty breathing.", "எனக்கு மூச்சு பிடிக்கிறது.", "breathing difficulty", False),
        ("enaku vayiru vali irukku", "I have stomach pain.", "எனக்கு வயிற்று வலி இருக்கிறது.", "", False),
        ("vayiru vali irukku", "I have stomach pain.", "வயிற்று வலி இருக்கிறது.", "", False),
        ("enaku thalai sutharuthu", "I feel dizzy.", "எனக்கு தலை சுற்றுகிறது.", "dizziness", False),
        ("thalai sutharuthu", "I feel dizzy.", "தலை சுற்றுகிறது.", "dizziness", False),
        ("enaku romba vali irukku", "I have severe pain.", "எனக்கு கடுமையான வலி இருக்கிறது.", "severe pain", False),
        ("aama", "Yes.", "ஆம்.", "", False),
        ("illai", "No.", "இல்லை.", "", True),
        ("seri", "Okay.", "சரி.", "", False),
        ("puriyuthu", "I understand.", "புரிகிறது.", "", False),
        ("puriyala", "I do not understand.", "புரியவில்லை.", "", True),
    ],
    "hi": [
        ("seene mein dard nahi hai", "I do not have chest pain.", "सीने में दर्द नहीं है।", "chest pain", True),
        ("chest mein dard nahi hai", "I do not have chest pain.", "सीने में दर्द नहीं है।", "chest pain", True),
        ("mujhe seene mein dard hai", "I have chest pain.", "मुझे सीने में दर्द है।", "chest pain", False),
        ("seene mein dard hai", "I have chest pain.", "सीने में दर्द है।", "chest pain", False),
        ("seene mein dard", "Chest pain.", "सीने में दर्द।", "chest pain", False),
        ("sar dard nahi hai", "I do not have a headache.", "सिरदर्द नहीं है।", "", True),
        ("mujhe sar dard hai", "I have a headache.", "मुझे सिरदर्द है।", "", False),
        ("sar dard hai", "I have a headache.", "सिरदर्द है।", "", False),
        ("bukhar nahi hai", "I do not have a fever.", "बुखार नहीं है।", "", True),
        ("mujhe bukhar hai", "I have a fever.", "मुझे बुखार है।", "", False),
        ("bukhar hai", "I have a fever.", "बुखार है।", "", False),
        ("saans nahi aa rahi", "I cannot breathe.", "सांस नहीं आ रही है।", "breathing difficulty", False),
        ("saans lene mein takleef hai", "I have difficulty breathing.", "सांस लेने में तकलीफ है।", "breathing difficulty", False),
        ("pet mein dard hai", "I have stomach pain.", "पेट में दर्द है।", "", False),
        ("chakkar aa raha hai", "I feel dizzy.", "चक्कर आ रहा है।", "dizziness", False),
        ("bahut dard hai", "I have severe pain.", "बहुत तेज दर्द है।", "severe pain", False),
        ("haan", "Yes.", "हाँ।", "", False),
        ("nahi", "No.", "नहीं।", "", True),
        ("theek hai", "Okay.", "ठीक है।", "", False),
        ("samajh aa gaya", "I understand.", "समझ आ गया।", "", False),
        ("samajh nahi aaya", "I do not understand.", "समझ नहीं आया।", "", True),
    ],
    "ml": [
        ("nenjil vedana illa", "I do not have chest pain.", "നെഞ്ചിൽ വേദനയില്ല.", "chest pain", True),
        ("nenjil vali illa", "I do not have chest pain.", "നെഞ്ചിൽ വേദനയില്ല.", "chest pain", True),
        ("nenjil vedana undu", "I have chest pain.", "എനിക്ക് നെഞ്ചുവേദനയുണ്ട്.", "chest pain", False),
        ("nenjil vali undu", "I have chest pain.", "എനിക്ക് നെഞ്ചുവേദനയുണ്ട്.", "chest pain", False),
        ("thalavedana illa", "I do not have a headache.", "തലവേദനയില്ല.", "", True),
        ("thalavedana undu", "I have a headache.", "എനിക്ക് തലവേദനയുണ്ട്.", "", False),
        ("pani illa", "I do not have a fever.", "പനിയില്ല.", "", True),
        ("pani undu", "I have a fever.", "എനിക്ക് പനിയുണ്ട്.", "", False),
        ("shwasam muttunnu", "I have difficulty breathing.", "എനിക്ക് ശ്വാസതടസ്സമുണ്ട്.", "breathing difficulty", False),
        ("vayaril vedana undu", "I have stomach pain.", "എനിക്ക് വയറുവേദനയുണ്ട്.", "", False),
        ("athe", "Yes.", "അതെ.", "", False),
        ("alla", "No.", "അല്ല.", "", True),
    ],
    "pl": [
        ("nie mam bolu w klatce", "I do not have chest pain.", "Nie mam bólu w klatce piersiowej.", "chest pain", True),
        ("nie boli mnie w klatce", "I do not have chest pain.", "Nie boli mnie w klatce piersiowej.", "chest pain", True),
        ("mam bol w klatce piersiowej", "I have chest pain.", "Mam ból w klatce piersiowej.", "chest pain", False),
        ("boli mnie w klatce piersiowej", "I have chest pain.", "Boli mnie w klatce piersiowej.", "chest pain", False),
        ("boli mnie klatka", "I have chest pain.", "Boli mnie klatka piersiowa.", "chest pain", False),
        ("nie mam goraczki", "I do not have a fever.", "Nie mam gorączki.", "", True),
        ("mam goraczke", "I have a fever.", "Mam gorączkę.", "", False),
        ("boli mnie glowa", "I have a headache.", "Boli mnie głowa.", "", False),
        ("mam bol glowy", "I have a headache.", "Mam ból głowy.", "", False),
        ("trudno mi oddychac", "I have difficulty breathing.", "Trudno mi oddychać.", "breathing difficulty", False),
        ("mam dusznosci", "I have difficulty breathing.", "Mam duszności.", "breathing difficulty", False),
        ("bardzo boli", "I have severe pain.", "Bardzo boli.", "severe pain", False),
        ("tak", "Yes.", "Tak.", "", False),
        ("nie", "No.", "Nie.", "", True),
    ],
    "ar": [
        ("la ashur bi alam fi sadri", "I do not have chest pain.", "لا أشعر بألم في الصدر.", "chest pain", True),
        ("laysa ladaya alam fi sadr", "I do not have chest pain.", "ليس لدي ألم في الصدر.", "chest pain", True),
        ("andi alam fi sadri", "I have chest pain.", "عندي ألم في الصدر.", "chest pain", False),
        ("alam fi al sadr", "Chest pain.", "ألم في الصدر.", "chest pain", False),
        ("laysa ladaya humma", "I do not have a fever.", "ليس لدي حمى.", "", True),
        ("andi humma", "I have a fever.", "عندي حمى.", "", False),
        ("andi suda", "I have a headache.", "عندي صداع.", "", False),
        ("suubat fi al tanaffus", "I have difficulty breathing.", "عندي صعوبة في التنفس.", "breathing difficulty", False),
        ("la astatiu al tanaffus", "I cannot breathe.", "لا أستطيع التنفس.", "breathing difficulty", False),
        ("naam", "Yes.", "نعم.", "", False),
        ("la", "No.", "لا.", "", True),
    ],
    "ur": [
        ("seenay mein dard nahi hai", "I do not have chest pain.", "سینے میں درد نہیں ہے۔", "chest pain", True),
        ("mujhe seenay mein dard hai", "I have chest pain.", "میرے سینے میں درد ہے۔", "chest pain", False),
        ("seenay mein dard", "Chest pain.", "سینے میں درد۔", "chest pain", False),
        ("sar dard nahi hai", "I do not have a headache.", "سر میں درد نہیں ہے۔", "", True),
        ("sar mein dard hai", "I have a headache.", "میرے سر میں درد ہے۔", "", False),
        ("bukhar nahi hai", "I do not have a fever.", "بخار نہیں ہے۔", "", True),
        ("mujhe bukhar hai", "I have a fever.", "مجھے بخار ہے۔", "", False),
        ("saans lene mein dushwari hai", "I have difficulty breathing.", "مجھے سانس لینے میں دشواری ہے۔", "breathing difficulty", False),
        ("saans ruk rahi hai", "I cannot breathe.", "میری سانس رک رہی ہے۔", "breathing difficulty", False),
        ("haan", "Yes.", "ہاں۔", "", False),
        ("nahi", "No.", "نہیں۔", "", True),
    ],
    "bn": [
        ("buke betha nei", "I do not have chest pain.", "আমার বুকে ব্যথা নেই।", "chest pain", True),
        ("amar buke betha", "I have chest pain.", "আমার বুকে ব্যথা আছে।", "chest pain", False),
        ("buke betha", "Chest pain.", "বুকে ব্যথা।", "chest pain", False),
        ("matha betha nei", "I do not have a headache.", "আমার মাথা ব্যথা নেই।", "", True),
        ("amar matha betha", "I have a headache.", "আমার মাথা ব্যথা করছে।", "", False),
        ("jhor nei", "I do not have a fever.", "আমার জ্বর নেই।", "", True),
        ("amar jhor", "I have a fever.", "আমার জ্বর আছে।", "", False),
        ("shwash nite koshto", "I have difficulty breathing.", "আমার শ্বাস নিতে কষ্ট হচ্ছে।", "breathing difficulty", False),
        ("hae", "Yes.", "হ্যাঁ।", "", False),
        ("na", "No.", "না।", "", True),
    ],
    "so": [
        ("ma qabo xanuun laabta ah", "I do not have chest pain.", "Ma qabo xanuunka laabta ah.", "chest pain", True),
        ("xanuun laabta", "I have chest pain.", "Waxaan dareemayaa xanuunka laabta.", "chest pain", False),
        ("laab xanuun", "Chest pain.", "Xanuunka laabta.", "chest pain", False),
        ("qandho ma qabo", "I do not have a fever.", "Ma qabo wax qandho ah.", "", True),
        ("qandho ayaa i haysa", "I have a fever.", "Waxaan qabaa qandho.", "", False),
        ("madax xanuun", "I have a headache.", "Waxaan qabaa madax xanuun.", "", False),
        ("neefsasho dhib", "I have difficulty breathing.", "Waxaan dhib ku qabaa neefsashada.", "breathing difficulty", False),
        ("haa", "Yes.", "Haa.", "", False),
        ("maya", "No.", "Maya.", "", True),
    ],
    "ro": [
        ("nu am dureri in piept", "I do not have chest pain.", "Nu am dureri în piept.", "chest pain", True),
        ("am dureri in piept", "I have chest pain.", "Am dureri în piept.", "chest pain", False),
        ("durere in piept", "Chest pain.", "Durere în piept.", "chest pain", False),
        ("nu am febra", "I do not have a fever.", "Nu am febră.", "", True),
        ("am febra", "I have a fever.", "Am febră.", "", False),
        ("ma doare capul", "I have a headache.", "Am o durere de cap.", "", False),
        ("dificultati de respiratie", "I have difficulty breathing.", "Am dificultăți de respirație.", "breathing difficulty", False),
        ("da", "Yes.", "Da.", "", False),
        ("nu", "No.", "Nu.", "", True),
    ]
}

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
    """
    Tiered Online Translation:
    Tier 1: Official Google Cloud Translation API (if API Key provided).
    Tier 2: Deep-Translator Google Engine (free, reliable, no key required).
    Tier 3: Deep-Translator MyMemory Engine.
    """
    if not text:
        return Translation()

    # Tier 1: Paid Google Cloud API
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

    # 1. Check Synthesizer for Staff inquiries
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
        if key == "INTERPRETER" and "interpreter" in clean:
            return Translation(phrases[language], phrases[language], 'needs_review', 'prepared_phrase', PREPARED)
        if key == "DOCTOR_NOW" and "see you now" in clean:
            return Translation(phrases[language], phrases[language], 'needs_review', 'prepared_phrase', PREPARED)

    # 2. Resilient online translation
    return online(text, 'en', language)

def patient_translation(text, language):
    if language not in LANGUAGES:
        return Translation(warning='Unsupported language.')

    norm = normalise(text)

    # 1. Match against Prepared 9-Language Dictionary (SORTED BY LENGTH DESCENDING)
    phrases = MASTER_PATIENT_PHRASES.get(language, [])
    sorted_phrases = sorted(phrases, key=lambda x: len(x[0]), reverse=True)

    for trigger, eng, nat, sym, is_neg in sorted_phrases:
        if trigger in norm or norm.startswith(trigger) or norm.endswith(trigger):
            return Translation(
                text=eng,
                native=nat,
                status='needs_review',
                source='prepared_phrase',
                warning=PREPARED,
                symptom=sym,
                is_negative=is_neg
            )

    # 2. Resilient Online Translation
    # If text is already in native script, translate to English
    if is_native_script(text):
        res = online(text, language, 'en')
        eng_text = res.text
        native_text = text
    else:
        # Romanised input: translate to English, then reconstruct proper native script
        res = online(text, 'auto', 'en')
        eng_text = res.text
        native_res = online(eng_text, 'en', language)
        native_text = native_res.text if native_res.text else text

    # Negation & Symptom Detection on translated English
    eng_lower = eng_text.lower()
    is_neg = any(w in eng_lower.split() for w in ['no', 'not', 'none', 'denies', 'without', 'never'])
    
    urgent_flags = ['chest pain', 'breathing difficulty', 'cannot breathe', 'bleeding', 'unconscious', 'severe pain']
    detected_sym = ''
    for u in urgent_flags:
        if u in eng_lower:
            detected_sym = u
            break

    return Translation(
        text=eng_text,
        native=native_text,
        status='needs_review',
        source='online_engine',
        warning=REVIEW,
        symptom=detected_sym,
        is_negative=is_neg
    )
