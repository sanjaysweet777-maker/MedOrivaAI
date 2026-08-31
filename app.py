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
# LANGUAGE CODE MAPPING (for MyMemory API)
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
# URGENT PHRASES & DETECTION
# ============================================================

URGENT_SYMPTOMS = [
    # English
    "chest pain", "heart pain", "can't breathe", "cant breathe",
    "difficulty breathing", "not breathing", "bleeding",
    "unconscious", "stroke", "seizure", "collapsed", "heart attack",
    # Tamil
    "nenji vali", "moochu varadhu", "moochu pidikuthu", "iratha",
    # Hindi
    "seene mein dard", "saans nahi", "saans lene mein takleef", "khoon",
    # Malayalam
    "nenjil vali", "shwasam muttunnu", "shwasam pidikkunnu", "iratha",
    # Polish
    "bol klatki", "trudnosci z oddychaniem", "krwawienie",
    # Arabic
    "ألم في الصدر", "صعوبة في التنفس", "نزيف",
    # Urdu
    "سینے میں درد", "سانس لینے میں دشواری", "خون",
    # Bengali
    "বুকে ব্যথা", "শ্বাস নিতে কষ্ট", "রক্তপাত",
    # Somali
    "xanuun laabta", "neefsasho dhib", "dhiig",
    # Romanian
    "durere in piept", "dificultate de respiratie", "sângerare",
]

NEGATION_WORDS = {
    "ta": ["illai", "illa", "varadhu", "varala", "ila"],
    "hi": ["nahi", "nahin", "nhi", "mat", "na"],
    "ml": ["illa", "alla", "illathe"],
    "pl": ["nie", "brak", "bez"],
    "ar": ["la", "laysa", "mish", "ma"],
    "ur": ["nahi", "nahin", "na"],
    "bn": ["na", "ni", "nay"],
    "so": ["ma", "maya"],
    "ro": ["nu", "nici"],
}

def is_negative(text, lang_code):
    lower = text.lower()
    for word in NEGATION_WORDS.get(lang_code, []):
        if word in lower:
            return True
    return False

def needs_medical_consultation(text, lang_code=None):
    lower = text.lower()
    has_urgent = any(phrase in lower for phrase in URGENT_SYMPTOMS)
    has_negation = False
    for words in NEGATION_WORDS.values():
        for word in words:
            if word in lower:
                has_negation = True
                break
        if has_negation:
            break
    return has_urgent and not has_negation

# ============================================================
# TRANSLATION DICTIONARY (Nested per language)
# ============================================================

translations = {
    "ta": {},
    "hi": {},
    "ml": {},
    "pl": {},
    "ar": {},
    "ur": {},
    "bn": {},
    "so": {},
    "ro": {},
}

# ========== TAMIL ==========
translations["ta"] = {
    # Staff prompts
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
    "where is your pain": "உங்கள் வலி எங்கே?",
    "how long have you had this": "இது உங்களுக்கு எவ்வளவு காலமாக உள்ளது?",
    "do you have a fever": "உங்களுக்கு காய்ச்சல் உள்ளதா?",
    "are you having difficulty breathing": "உங்களுக்கு மூச்சு விடுவதில் சிரமம் உள்ளதா?",
    "do you feel dizzy or faint": "நீங்கள் தலை சுற்றல் அல்லது மயக்கத்தை உணர்கிறீர்களா?",
    "do you have chest pain": "உங்களுக்கு மார்பு வலி உள்ளதா?",
    "do you have any allergies": "உங்களுக்கு ஏதேனும் ஒவ்வாமை உள்ளதா?",
    "are you taking any medication": "நீங்கள் ஏதேனும் மருந்து எடுத்துக்கொள்கிறீர்களா?",
    "have you had this before": "இது உங்களுக்கு முன்பு ஏற்பட்டதா?",
    "do you have any other symptoms": "உங்களுக்கு வேறு ஏதேனும் அறிகுறிகள் உள்ளனவா?",
    "does anything make it better or worse": "ஏதாவது அதை சிறப்பாக அல்லது மோசமாக்குகிறதா?",
    "is there any bleeding": "ஏதேனும் இரத்தப்போக்கு உள்ளதா?",
    "when did the symptoms start": "அறிகுறிகள் எப்போது தொடங்கின?",
    # Patient responses
    "enaku nenji vali irukku": "I have chest pain",
    "enaku nenji vali iruku": "I have chest pain",
    "nenji vali irukku": "I have chest pain",
    "nenji vali": "chest pain",
    "enaku moochu varadhu": "I cannot breathe properly",
    "moochu varadhu": "I cannot breathe properly",
    "moochu pidikuthu": "I am having difficulty breathing",
    "enaku thalai vali irukku": "I have a headache",
    "enaku thalai valikuthu": "I have a headache",
    "thalai vali irukku": "I have a headache",
    "thalai valikuthu": "my head is hurting",
    "kaichal irukku": "I have a fever",
    "enaku kaichal irukku": "I have a fever",
    "enaku vayiru vali irukku": "I have stomach pain",
    "vayiru vali irukku": "I have stomach pain",
    "enaku kaal vali irukku": "I have leg pain",
    "kaal vali": "leg pain",
    "enaku kai vali irukku": "I have arm pain",
    "thalai sutharuthu": "I feel dizzy",
    "vanthi varuthu": "I feel like vomiting",
    "romba vali irukku": "I have severe pain",
    "enala moochu vida mudiyala": "I cannot breathe",
    "enaku nenji vali illai": "I do not have chest pain",
    "nenji vali illai": "I do not have chest pain",
    "enaku thalai vali illai": "I do not have a headache",
    "thalai vali illai": "I do not have a headache",
    "kaichal illai": "I do not have a fever",
    "vali illai": "I have no pain",
    "aama": "yes",
    "illai": "no",
    "seri": "okay",
    "puriyuthu": "I understand",
    "puriyala": "I do not understand",
    "help pannunga": "please help me",
    "nalla irukken": "I am fine",
}

# ========== HINDI (COMPLETE - FIXED) ==========
translations["hi"] = {
    # Staff prompts
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
    "where is your pain": "आपको दर्द कहाँ हो रहा है?",
    "how long have you had this": "यह आपको कितने दिनों से है?",
    "do you have a fever": "क्या आपको बुखार है?",
    "are you having difficulty breathing": "क्या आपको सांस लेने में कठिनाई हो रही है?",
    "do you feel dizzy or faint": "क्या आपको चक्कर या बेहोशी महसूस हो रही है?",
    "do you have chest pain": "क्या आपको सीने में दर्द है?",
    "do you have any allergies": "क्या आपको कोई एलर्जी है?",
    "are you taking any medication": "क्या आप कोई दवा ले रहे हैं?",
    "have you had this before": "क्या आपको यह पहले भी हुआ है?",
    "do you have any other symptoms": "क्या आपको कोई अन्य लक्षण हैं?",
    "does anything make it better or worse": "क्या किसी चीज़ से यह बेहतर या बदतर होता है?",
    "is there any bleeding": "क्या कोई रक्तस्राव है?",
    "when did the symptoms start": "लक्षण कब शुरू हुए?",

    # Patient responses (Roman script)
    "mujhe chest mein dard hai": "I have chest pain",
    "seene mein dard hai": "I have chest pain",
    "mujhe seene mein dard hai": "I have chest pain",
    "chest mein dard": "I have chest pain",
    "sar dard hai": "I have a headache",
    "mujhe sar dard hai": "I have a headache",
    "sar mein dard": "I have a headache",
    "bukhar hai": "I have a fever",
    "mujhe bukhar hai": "I have a fever",
    "pet mein dard hai": "I have stomach pain",
    "mujhe pet mein dard hai": "I have stomach pain",
    "paaon mein dard hai": "I have leg pain",
    "mere pair mein dard ho raha hai": "I have leg pain",
    "pair mein dard": "I have leg pain",
    "haath mein dard hai": "I have arm pain",
    "saans lene mein takleef hai": "I have difficulty breathing",
    "saans nahi aa rahi": "I cannot breathe",
    "chakkar aa raha hai": "I feel dizzy",
    "ulti aa rahi hai": "I feel like vomiting",
    "bahut dard hai": "I have severe pain",
    "dard hai": "I have pain",
    "mujhe dard": "I have pain",

    # Patient responses (Devanagari script)
    "मुझे सीने में दर्द है": "I have chest pain",
    "सीने में दर्द है": "I have chest pain",
    "सर दर्द है": "I have a headache",
    "मुझे सर दर्द है": "I have a headache",
    "बुखार है": "I have a fever",
    "मुझे बुखार है": "I have a fever",
    "पेट में दर्द है": "I have stomach pain",
    "मुझे पेट में दर्द है": "I have stomach pain",
    "मेरे पैर में दर्द हो रहा है": "I have leg pain",
    "पैर में दर्द": "I have leg pain",
    "हाथ में दर्द है": "I have arm pain",
    "सांस लेने में तकलीफ है": "I have difficulty breathing",
    "सांस नहीं आ रही": "I cannot breathe",
    "चक्कर आ रहा है": "I feel dizzy",
    "उल्टी आ रही है": "I feel like vomiting",
    "बहुत दर्द है": "I have severe pain",
    "दर्द है": "I have pain",
    "मुझे दर्द": "I have pain",

    # Negatives (Roman script)
    "chest mein dard nahi hai": "I do not have chest pain",
    "seene mein dard nahi hai": "I do not have chest pain",
    "sar dard nahi hai": "I do not have a headache",
    "bukhar nahi hai": "I do not have a fever",
    "pet mein dard nahi hai": "I do not have stomach pain",
    "dard nahi hai": "I have no pain",
    "pair mein dard nahi hai": "I do not have leg pain",

    # Negatives (Devanagari script)
    "सीने में दर्द नहीं है": "I do not have chest pain",
    "सर दर्द नहीं है": "I do not have a headache",
    "बुखार नहीं है": "I do not have a fever",
    "पेट में दर्द नहीं है": "I do not have stomach pain",
    "दर्द नहीं है": "I have no pain",
    "पैर में दर्द नहीं है": "I do not have leg pain",

    # General
    "theek hoon": "I am fine",
    "haan": "yes",
    "nahi": "no",
    "theek hai": "okay",
    "samajh nahi aaya": "I do not understand",
    "samajh aa gaya": "I understand",
    "meri madad karo": "please help me",
}

# ========== MALAYALAM ==========
translations["ml"] = {
    "good morning how can i help you": "സുപ്രഭാതം. എനിക്ക് നിങ്ങളെ എങ്ങനെ സഹായിക്കാനാകും?",
    "do you have an appointment": "നിങ്ങൾക്ക് ഒരു അപ്പോയിന്റ്മെന്റ് ഉണ്ടോ?",
    "please take a seat the doctor will see you shortly": "ദയവായി ഇരിക്കുക. ഡോക്ടർ ഉടൻ നിങ്ങളെ കാണും.",
    "do you need any assistance": "നിങ്ങൾക്ക് എന്തെങ്കിലും സഹായം വേണോ?",
    "is this your first visit": "ഇത് നിങ്ങളുടെ ആദ്യ സന്ദർശനമാണോ?",
    "do you have your nhs number": "നിങ്ങൾക്ക് എൻഎച്ച്എസ് നമ്പർ ഉണ്ടോ?",
    "would you like to speak to someone": "നിങ്ങൾക്ക് ആരോടെങ്കിലും സംസാരിക്കാൻ ആഗ്രഹമുണ്ടോ?",
    "please fill in this form": "ദയവായി ഈ ഫോം പൂരിപ്പിക്കുക.",
    "have you been here before": "നിങ്ങൾ മുമ്പ് ഇവിടെ വന്നിട്ടുണ്ടോ?",
    "please wait the doctor will call you": "ദയവായി കാത്തിരിക്കുക. ഡോക്ടർ നിങ്ങളെ വിളിക്കും.",
    "your appointment is confirmed": "നിങ്ങളുടെ അപ്പോയിന്റ്മെന്റ് സ്ഥിരീകരിച്ചു.",
    "the doctor will see you now": "ഡോക്ടർ ഇപ്പോൾ നിങ്ങളെ കാണും.",
    "where is your pain": "നിങ്ങളുടെ വേദന എവിടെയാണ്?",
    "how long have you had this": "ഇത് നിങ്ങൾക്ക് എത്രകാലമായി?",
    "do you have a fever": "നിങ്ങൾക്ക് പനി ഉണ്ടോ?",
    "are you having difficulty breathing": "നിങ്ങൾക്ക് ശ്വസിക്കാൻ ബുദ്ധിമുട്ട് ഉണ്ടോ?",
    "do you feel dizzy or faint": "നിങ്ങൾക്ക് തലകറക്കമോ ബോധക്ഷയമോ തോന്നുന്നുണ്ടോ?",
    "do you have chest pain": "നിങ്ങൾക്ക് നെഞ്ചുവേദന ഉണ്ടോ?",
    "do you have any allergies": "നിങ്ങൾക്ക് എന്തെങ്കിലും അലർജി ഉണ്ടോ?",
    "are you taking any medication": "നിങ്ങൾ എന്തെങ്കിലും മരുന്ന് കഴിക്കുന്നുണ്ടോ?",
    "have you had this before": "ഇത് നിങ്ങൾക്ക് മുമ്പ് ഉണ്ടായിട്ടുണ്ടോ?",
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

# ========== POLISH ==========
translations["pl"] = {
    "good morning how can i help you": "Dzień dobry. Jak mogę pomóc?",
    "do you have an appointment": "Czy ma pan umówioną wizytę?",
    "please take a seat the doctor will see you shortly": "Proszę usiąść. Lekarz wkrótce pana przyjmie.",
    "do you need any assistance": "Czy potrzebuje pan pomocy?",
    "is this your first visit": "Czy to pana pierwsza wizyta?",
    "do you have your nhs number": "Czy ma pan numer NHS?",
    "would you like to speak to someone": "Czy chciałby pan z kimś porozmawiać?",
    "please fill in this form": "Proszę wypełnić ten formularz.",
    "have you been here before": "Czy był pan tu wcześniej?",
    "please wait the doctor will call you": "Proszę czekać. Lekarz pana zawoła.",
    "your appointment is confirmed": "Pana wizyta jest potwierdzona.",
    "the doctor will see you now": "Lekarz teraz pana przyjmie.",
    "where is your pain": "Gdzie pan odczuwa ból?",
    "how long have you had this": "Jak długo ma pan ten problem?",
    "do you have a fever": "Czy ma pan gorączkę?",
    "are you having difficulty breathing": "Czy ma pan trudności z oddychaniem?",
    "do you feel dizzy or faint": "Czy czuje pan zawroty głowy lub omdlenia?",
    "do you have chest pain": "Czy ma pan ból w klatce piersiowej?",
    "do you have any allergies": "Czy ma pan alergie?",
    "are you taking any medication": "Czy przyjmuje pan leki?",
    "have you had this before": "Czy miał pan to wcześniej?",
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
}

# ========== ARABIC ==========
translations["ar"] = {
    "good morning how can i help you": "صباح الخير. كيف يمكنني مساعدتك؟",
    "do you have an appointment": "هل لديك موعد؟",
    "please take a seat the doctor will see you shortly": "يرجى الجلوس. سيراك الطبيب قريباً.",
    "do you need any assistance": "هل تحتاج إلى أي مساعدة؟",
    "is this your first visit": "هل هذه زيارتك الأولى؟",
    "do you have your nhs number": "هل لديك رقم NHS الخاص بك؟",
    "would you like to speak to someone": "هل ترغب في التحدث إلى شخص ما؟",
    "please fill in this form": "يرجى ملء هذا النموذج.",
    "have you been here before": "هل أتيت إلى هنا من قبل؟",
    "please wait the doctor will call you": "يرجى الانتظار. سيتصل بك الطبيب.",
    "your appointment is confirmed": "تم تأكيد موعدك.",
    "the doctor will see you now": "سيراك الطبيب الآن.",
    "where is your pain": "أين الألم؟",
    "how long have you had this": "منذ متى وأنت تعاني من هذا؟",
    "do you have a fever": "هل لديك حمى؟",
    "are you having difficulty breathing": "هل تواجه صعوبة في التنفس؟",
    "do you feel dizzy or faint": "هل تشعر بالدوار أو الإغماء؟",
    "do you have chest pain": "هل تعاني من ألم في الصدر؟",
    "do you have any allergies": "هل لديك أي حساسية؟",
    "are you taking any medication": "هل تتناول أي دواء؟",
    "have you had this before": "هل حدث لك هذا من قبل؟",
    "عندي ألم في الصدر": "I have chest pain",
    "عندي صداع": "I have a headache",
    "عندي حمى": "I have a fever",
    "عندي ألم في المعدة": "I have stomach pain",
    "لا استطيع التنفس": "I cannot breathe",
    "أشعر بالدوار": "I feel dizzy",
    "لدي ألم شديد": "I have severe pain",
    "ليس لدي ألم في الصدر": "I do not have chest pain",
    "ليس لدي صداع": "I do not have a headache",
    "ليس لدي حمى": "I do not have a fever",
    "ليس لدي ألم": "I have no pain",
    "أنا بخير": "I am fine",
    "نعم": "yes",
    "لا": "no",
}

# ========== URDU ==========
translations["ur"] = {
    "good morning how can i help you": "صبح بخیر۔ میں آپ کی کیسے مدد کر سکتا ہوں؟",
    "do you have an appointment": "کیا آپ کا کوئی اپوائنٹمنٹ ہے؟",
    "please take a seat the doctor will see you shortly": "براہ کرم بیٹھ جائیں۔ ڈاکٹر جلد آپ سے ملیں گے۔",
    "do you need any assistance": "کیا آپ کو کسی مدد کی ضرورت ہے؟",
    "is this your first visit": "کیا یہ آپ کا پہلا دورہ ہے؟",
    "do you have your nhs number": "کیا آپ کے پاس این ایچ ایس نمبر ہے؟",
    "would you like to speak to someone": "کیا آپ کسی سے بات کرنا چاہیں گے؟",
    "please fill in this form": "براہ کرم یہ فارم پُر کریں۔",
    "have you been here before": "کیا آپ پہلے یہاں آ چکے ہیں؟",
    "please wait the doctor will call you": "براہ کرم انتظار کریں۔ ڈاکٹر آپ کو بلائیں گے۔",
    "your appointment is confirmed": "آپ کا اپوائنٹمنٹ تصدیق ہو گیا ہے۔",
    "the doctor will see you now": "ڈاکٹر اب آپ سے ملیں گے۔",
    "where is your pain": "آپ کو درد کہاں ہے؟",
    "how long have you had this": "یہ آپ کو کب سے ہے؟",
    "do you have a fever": "کیا آپ کو بخار ہے؟",
    "are you having difficulty breathing": "کیا آپ کو سانس لینے میں دشواری ہے؟",
    "do you feel dizzy or faint": "کیا آپ کو چکر یا بے ہوشی محسوس ہو رہی ہے؟",
    "do you have chest pain": "کیا آپ کو سینے میں درد ہے؟",
    "do you have any allergies": "کیا آپ کو کوئی الرجی ہے؟",
    "are you taking any medication": "کیا آپ کوئی دوا لے رہے ہیں؟",
    "have you had this before": "کیا آپ کو یہ پہلے بھی ہوا ہے؟",
    "میرے سینے میں درد ہے": "I have chest pain",
    "میرا سر درد ہے": "I have a headache",
    "مجھے بخار ہے": "I have a fever",
    "میرے پیٹ میں درد ہے": "I have stomach pain",
    "سانس لینے میں دشواری": "I have difficulty breathing",
    "چکر آ رہا ہے": "I feel dizzy",
    "مجھے شدید درد ہے": "I have severe pain",
    "میرے سینے میں درد نہیں": "I do not have chest pain",
    "مجھے بخار نہیں": "I do not have a fever",
    "مجھے درد نہیں": "I have no pain",
    "میں ٹھیک ہوں": "I am fine",
    "ہاں": "yes",
    "نہیں": "no",
}

# ========== BENGALI ==========
translations["bn"] = {
    "good morning how can i help you": "সুপ্রভাত। আমি আপনাকে কীভাবে সাহায্য করতে পারি?",
    "do you have an appointment": "আপনার কি কোনো অ্যাপয়েন্টমেন্ট আছে?",
    "please take a seat the doctor will see you shortly": "দয়া করে বসুন। ডাক্তার শীঘ্রই আপনাকে দেখবেন।",
    "do you need any assistance": "আপনার কি কোনো সাহায্যের প্রয়োজন?",
    "is this your first visit": "এটি কি আপনার প্রথম দর্শন?",
    "do you have your nhs number": "আপনার কি এনএইচএস নম্বর আছে?",
    "would you like to speak to someone": "আপনি কি কারও সাথে কথা বলতে চান?",
    "please fill in this form": "দয়া করে এই ফর্মটি পূরণ করুন।",
    "have you been here before": "আপনি কি আগে এখানে এসেছেন?",
    "please wait the doctor will call you": "দয়া করে অপেক্ষা করুন। ডাক্তার আপনাকে ডাকবেন।",
    "your appointment is confirmed": "আপনার অ্যাপয়েন্টমেন্ট নিশ্চিত করা হয়েছে।",
    "the doctor will see you now": "ডাক্তার এখন আপনাকে দেখবেন।",
    "where is your pain": "আপনার ব্যথা কোথায়?",
    "how long have you had this": "আপনার কতদিন ধরে এই সমস্যা?",
    "do you have a fever": "আপনার কি জ্বর আছে?",
    "are you having difficulty breathing": "আপনার কি শ্বাস নিতে কষ্ট হচ্ছে?",
    "do you feel dizzy or faint": "আপনার কি মাথা ঘোরা বা অজ্ঞান হওয়ার অনুভূতি হচ্ছে?",
    "do you have chest pain": "আপনার কি বুকে ব্যথা আছে?",
    "do you have any allergies": "আপনার কি কোনো অ্যালার্জি আছে?",
    "are you taking any medication": "আপনি কি কোনো ওষুধ খাচ্ছেন?",
    "have you had this before": "আপনার কি আগেও এই সমস্যা হয়েছিল?",
    "আমার বুকে ব্যথা": "I have chest pain",
    "আমার মাথা ব্যাথা": "I have a headache",
    "আমার জ্বর": "I have a fever",
    "আমার পেটে ব্যথা": "I have stomach pain",
    "শ্বাস নিতে কষ্ট": "I have difficulty breathing",
    "মাথা ঘোরা": "I feel dizzy",
    "আমার তীব্র ব্যথা": "I have severe pain",
    "আমার বুকে ব্যথা নেই": "I do not have chest pain",
    "আমার জ্বর নেই": "I do not have a fever",
    "আমার ব্যথা নেই": "I have no pain",
    "আমি ভাল আছি": "I am fine",
    "হ্যাঁ": "yes",
    "না": "no",
}

# ========== SOMALI ==========
translations["so"] = {
    "good morning how can i help you": "Subax wanaagsan. Sideen ku caawin karaa?",
    "do you have an appointment": "Ma qabataa ballan?",
    "please take a seat the doctor will see you shortly": "Fadlan fadhiiso. Dhakhtarka ayaa si dhaar ku arki doona.",
    "do you need any assistance": "Ma u baahan tahay caawimaad?",
    "is this your first visit": "Kani ma booqashadaada koowaad?",
    "do you have your nhs number": "Ma haysataa lambarka NHS?",
    "would you like to speak to someone": "Ma jeceshahay inaad qof la hadasho?",
    "please fill in this form": "Fadlan buuxi foomkan.",
    "have you been here before": "Ma horay u timid halkan?",
    "please wait the doctor will call you": "Fadlan sug. Dhakhtarka ayaa kuu yeedhi doona.",
    "your appointment is confirmed": "Ballaankaaga waa la xaqiijiyay.",
    "the doctor will see you now": "Dhakhtarka ayaa hadda ku arki doona.",
    "where is your pain": "Xanuunkaagu xaggee kuu jiraa?",
    "how long have you had this": "Muddo intee leeg ayaad tan qabtaa?",
    "do you have a fever": "Ma qabtaa qandho?",
    "are you having difficulty breathing": "Ma adag tahay neefsashada?",
    "do you feel dizzy or faint": "Ma dareemaysaa miyir beel ama dawakhaad?",
    "do you have chest pain": "Ma qabtaa xanuun laabta?",
    "do you have any allergies": "Ma qabtaa xasaasiyad?",
    "are you taking any medication": "Ma qaadataa daawo?",
    "have you had this before": "Ma horay kuu dhacday tan?",
    "xanuun laabta": "I have chest pain",
    "madax xanuun": "I have a headache",
    "qandho": "I have a fever",
    "xanuun calool": "I have stomach pain",
    "neefsasho dhib": "I have difficulty breathing",
    "madhax wareeg": "I feel dizzy",
    "xanuun daran": "I have severe pain",
    "ma laha xanuun laabta": "I do not have chest pain",
    "ma qabo qandho": "I do not have a fever",
    "ma laha xanuun": "I have no pain",
    "waan fiicanahay": "I am fine",
    "haa": "yes",
    "maya": "no",
}

# ========== ROMANIAN ==========
translations["ro"] = {
    "good morning how can i help you": "Bună dimineața. Cum vă pot ajuta?",
    "do you have an appointment": "Aveți o programare?",
    "please take a seat the doctor will see you shortly": "Vă rog să luați loc. Medicul vă va vedea în curând.",
    "do you need any assistance": "Aveți nevoie de ajutor?",
    "is this your first visit": "Este prima dvs. vizită?",
    "do you have your nhs number": "Aveți numărul NHS?",
    "would you like to speak to someone": "Doriți să vorbiți cu cineva?",
    "please fill in this form": "Vă rugăm să completați acest formular.",
    "have you been here before": "Ați mai fost aici înainte?",
    "please wait the doctor will call you": "Vă rugăm să așteptați. Medicul vă va chema.",
    "your appointment is confirmed": "Programarea dvs. este confirmată.",
    "the doctor will see you now": "Medicul vă vede acum.",
    "where is your pain": "Unde vă doare?",
    "how long have you had this": "De cât timp aveți această problemă?",
    "do you have a fever": "Aveți febră?",
    "are you having difficulty breathing": "Aveți dificultăți de respirație?",
    "do you feel dizzy or faint": "Vă simțiți amețit sau leșinat?",
    "do you have chest pain": "Aveți durere în piept?",
    "do you have any allergies": "Aveți alergii?",
    "are you taking any medication": "Luați vreun medicament?",
    "have you had this before": "Ați mai avut asta înainte?",
    "durere in piept": "I have chest pain",
    "durere de cap": "I have a headache",
    "febra": "I have a fever",
    "durere de stomac": "I have stomach pain",
    "dificultate de respiratie": "I have difficulty breathing",
    "amețeală": "I feel dizzy",
    "durere severă": "I have severe pain",
    "nu am durere in piept": "I do not have chest pain",
    "nu am febra": "I do not have a fever",
    "nu am durere": "I have no pain",
    "sunt bine": "I am fine",
    "da": "yes",
    "nu": "no",
}

# ============================================================
# HELPER: Lookup translation in the selected language's dictionary
# ============================================================

def lookup_translation(text, lang_code):
    if not lang_code or lang_code not in translations:
        return None
    lang_dict = translations[lang_code]
    text_lower = text.lower().strip()
    if text_lower in lang_dict:
        return lang_dict[text_lower]
    best_match = None
    best_length = 0
    for phrase, translation in lang_dict.items():
        if phrase in text_lower and len(phrase) > best_length:
            best_match = translation
            best_length = len(phrase)
    return best_match

# ============================================================
# SYMPTOM DETECTION (PER LANGUAGE)
# ============================================================

SYMPTOM_MAP = {
    "ta": {
        "nenji vali": "chest pain",
        "moochu varadhu": "breathing difficulty",
        "thalai vali": "headache",
        "kaichal": "fever",
        "vayiru vali": "stomach pain",
        "thalai sutharuthu": "dizziness",
    },
    "hi": {
        "seene mein dard": "chest pain",
        "saans lene mein takleef": "breathing difficulty",
        "saans nahi": "breathing difficulty",
        "sar dard": "headache",
        "bukhar": "fever",
        "pet dard": "stomach pain",
        "chakkar": "dizziness",
        "pair mein dard": "leg pain",
    },
    "ml": {
        "nenjil vali": "chest pain",
        "shwasam muttunnu": "breathing difficulty",
        "thalavalikkunnu": "headache",
        "pani undu": "fever",
        "vayaril vali": "stomach pain",
    },
    "pl": {
        "bol klatki": "chest pain",
        "trudnosci z oddychaniem": "breathing difficulty",
        "bol glowy": "headache",
        "goraczka": "fever",
        "bol brzucha": "stomach pain",
    },
    "ar": {
        "ألم في الصدر": "chest pain",
        "صعوبة في التنفس": "breathing difficulty",
        "صداع": "headache",
        "حمى": "fever",
        "ألم في المعدة": "stomach pain",
    },
    "ur": {
        "سینے میں درد": "chest pain",
        "سانس لینے میں دشواری": "breathing difficulty",
        "سر درد": "headache",
        "بخار": "fever",
        "پیٹ میں درد": "stomach pain",
    },
    "bn": {
        "বুকে ব্যথা": "chest pain",
        "শ্বাস নিতে কষ্ট": "breathing difficulty",
        "মাথা ব্যাথা": "headache",
        "জ্বর": "fever",
        "পেটে ব্যথা": "stomach pain",
    },
    "so": {
        "xanuun laabta": "chest pain",
        "neefsasho dhib": "breathing difficulty",
        "madax xanuun": "headache",
        "qandho": "fever",
        "xanuun calool": "stomach pain",
    },
    "ro": {
        "durere in piept": "chest pain",
        "dificultate de respiratie": "breathing difficulty",
        "durere de cap": "headache",
        "febra": "fever",
        "durere de stomac": "stomach pain",
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
# GUIDED PROMPTS (English only)
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

def translate_to_english(text, lang_code):
    builtin = lookup_translation(text, lang_code)
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
        for src in ["ta", "hi", "ml", "pl", "ar", "ur", "bn", "so", "ro"]:
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
    builtin = lookup_translation(text, target_lang_code)
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
        return jsonify({"status": "error", "error": f"Could not start session: {str(e)}"}), 500

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

    translation = lookup_translation(raw_text, lang_code)
    if translation:
        set_cached_translation(raw_text, lang_code, translation)
        return jsonify({
            "original": raw_text,
            "simplified": raw_text,
            "was_simplified": False,
            "translated": translation,
            "lang": lang_name,
            "urgent": False,
        })

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

    english_text = lookup_translation(text, lang_code)
    if not english_text:
        english_text, error = translate_to_english(text, lang_code)
        if error:
            return jsonify({"error": "Could not translate. Please try again."}), 500

    symptom = detect_symptom(text, lang_code)
    medical_alert = needs_medical_consultation(text, lang_code) or needs_medical_consultation(english_text, lang_code)
    native_text = text

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
