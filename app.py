from flask import Flask, render_template, request, jsonify, session
import uuid
import re

app = Flask(__name__)
app.secret_key = "medoriva-mvp-secret-key"

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
# URGENT PHRASES
# ============================================================

URGENT_PHRASES = [
    # English
    "chest pain", "chest hurt", "can't breathe", "cant breathe",
    "difficulty breathing", "heart pain", "bleeding heavily",
    "unconscious", "stroke", "seizure", "collapsed", "not breathing",
    "heart attack", "severe pain", "unbearable pain", "passing out",
    "faint", "fainting", "severe bleeding", "blood loss",
    
    # Tamil / Thanglish
    "nenji vali", "moochu varadhu", "iratha", "padaippu",
    "nenjil vali", "maarbu vali", "moochu pidikuthu",
    "sugam illai", "romba vali", "enakku romba vali",
    "iratha kottum", "kaal vali", "thalai sutharuthu",
    
    # Hindi
    "seene mein dard", "saans nahi", "khoon", "behosh",
    "chakkar aa raha hai", "saans lene mein takleef",
    "bahut dard", "dard seh nahi sakta", "khoon beh raha",
    
    # Polish
    "bol klatki", "trudnosci z oddychaniem", "krwawienie",
    "bardzo boli", "nie moge oddychac", "bol w klatce piersiowej",
    
    # Malayalam
    "nenjil vali", "shwasam muttunnu", "iratha", "bhodam illa",
    "valiya vali", "shwasam pidikkunnu", 
]

NEGATION_WORDS = [
    # Tamil
    "illai", "illa", "kidaiyathu", "varadhu", "varala", "ila", "mattum",
    # Hindi
    "nahi", "nahin", "mat", "nhi", "na",
    # Polish
    "nie", "brak", "bez",
    # Arabic
    "la", "laysa", "mish", "ma",
    # English
    "no", "not", "don't", "dont", "do not", "never", "none",
    "cannot", "can't", "cant", "doesn't", "doesnt", "does not",
    # Malayalam
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
    # English
    "chest pain", "chest hurt", "heart pain", "cant breathe", "can't breathe",
    "difficulty breathing", "not breathing", "bleeding heavily", "unconscious",
    "stroke", "seizure", "collapsed", "severe pain", "very bad pain",
    "heart attack", "severe bleeding", "unbearable pain", "passing out",
    
    # Tamil / Thanglish
    "nenji vali", "moochu varadhu", "moochu pidikuthu", "iratha",
    "nenjil vali", "maarbu vali", "sugam illai", "romba vali",
    "iratha kottum", "thalai sutharuthu",
    
    # Hindi
    "seene mein dard", "saans nahi", "bahut dard", "behosh", "khoon",
    "chakkar aa raha hai", "saans lene mein takleef",
    
    # Polish
    "bol klatki", "trudnosci z oddychaniem", "krwawienie", "bardzo boli",
    
    # Malayalam
    "nenjil vali", "shwasam muttunnu", "shwasam pidikkunnu",
    "valiya vali", "iratha",
]

def needs_medical_consultation(text):
    lower = text.lower()
    has_urgent = any(phrase in lower for phrase in URGENT_SYMPTOMS)
    has_negation = is_negative(text)
    return has_urgent and not has_negation

# ============================================================
# EXTENSIVE MEDICAL TRANSLATION DICTIONARY
# ============================================================

TRANSLATION_DICT = {
    # ========== TAMIL / THANGHISH ==========
    
    # Pain related
    "enaku nenji vali irukku": "I have chest pain",
    "enaku nenji vali iruku": "I have chest pain",
    "ennaku nenji vali irukku": "I have chest pain",
    "nenji vali irukku": "I have chest pain",
    "nenji vali iruku": "I have chest pain",
    "nenji valikuthu": "I have chest pain",
    "en nenji valikuthu": "my chest is hurting",
    "nenji vali": "chest pain",
    "nenjil vali": "chest pain",
    
    # Breathing related
    "enaku moochu varadhu": "I cannot breathe properly",
    "moochu varadhu": "I cannot breathe properly",
    "moochu pidikuthu": "I am having difficulty breathing",
    "moochu pidikkuthu": "I am having difficulty breathing",
    "sugam illai": "I am not well",
    "moochu": "breath",
    
    # Head related
    "enaku thalai vali irukku": "I have a headache",
    "thalai vali irukku": "I have a headache",
    "thalai vali iruku": "I have a headache",
    "thalai valikuthu": "my head is hurting",
    "enaku thalai vali": "I have a headache",
    "thalai sutharuthu": "I feel dizzy",
    "thalai sutru": "dizziness",
    
    # Fever related
    "enaku kaichal irukku": "I have a fever",
    "kaichal irukku": "I have a fever",
    "kaichal iruku": "I have a fever",
    "enaku kaichal": "I have a fever",
    "kaichal varuthu": "I have a fever",
    
    # Stomach related
    "enaku vayiru vali irukku": "I have stomach pain",
    "vayiru vali irukku": "I have stomach pain",
    "vayiru vali iruku": "I have stomach pain",
    "vayiru valikuthu": "my stomach is hurting",
    "vayiru": "stomach",
    
    # Limb pain
    "kaal vali irukku": "I have leg pain",
    "kaal vali iruku": "I have leg pain",
    "kai vali irukku": "I have arm pain",
    "kai vali iruku": "I have arm pain",
    
    # Other symptoms
    "vanthi varuthu": "I feel like vomiting",
    "vanthi": "vomiting",
    "romba vali irukku": "I have severe pain",
    "vali irukku": "I have pain",
    "vali iruku": "I have pain",
    "theriyala": "I do not know",
    
    # Medication related
    "marundhu": "medicine",
    "enaku marundhu vendum": "I need medicine",
    "marundhu kudungga": "please give me medicine",
    
    # Emergency
    "ambulance": "ambulance",
    "ambulance kudungga": "please call ambulance",
    "doctor": "doctor",
    "doctorai paarpadhu": "I need to see a doctor",
    
    # General
    "aama": "yes",
    "illai": "no",
    "seri": "okay",
    "puriyuthu": "I understand",
    "puriyala": "I do not understand",
    "help pannunga": "please help me",
    "nalla irukken": "I am fine",
    "jolly ah irukken": "I am feeling well",
    
    # ========== TAMIL NEGATIVE ==========
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
    "sugam thaan": "I am fine",
    
    # ========== HINDI ==========
    
    # Pain related
    "mujhe chest mein dard hai": "I have chest pain",
    "seene mein dard hai": "I have chest pain",
    "mujhe seene mein dard hai": "I have chest pain",
    "chest mein dard": "chest pain",
    "seena dard": "chest pain",
    
    # Head related
    "sar dard hai": "I have a headache",
    "mujhe sar dard hai": "I have a headache",
    "sar mein dard": "headache",
    
    # Fever
    "bukhar hai": "I have a fever",
    "mujhe bukhar hai": "I have a fever",
    
    # Stomach
    "pet mein dard hai": "I have stomach pain",
    "pet dard": "stomach pain",
    
    # Breathing
    "saans lene mein takleef hai": "I have difficulty breathing",
    "saans nahi aa rahi": "I cannot breathe",
    
    # Other symptoms
    "chakkar aa raha hai": "I feel dizzy",
    "ulti aa rahi hai": "I feel like vomiting",
    "bahut dard hai": "I have severe pain",
    "dard hai": "I have pain",
    
    # Medication
    "dawa": "medicine",
    "mujhe dawa chahiye": "I need medicine",
    "dawa do": "give me medicine",
    
    # Emergency
    "ambulance": "ambulance",
    "ambulance bulao": "call ambulance",
    "doctor": "doctor",
    "doctor ko dikhao": "see a doctor",
    
    # General
    "theek hoon": "I am fine",
    "haan": "yes",
    "nahi": "no",
    "theek hai": "okay",
    "samajh nahi aaya": "I do not understand",
    "samajh aa gaya": "I understand",
    "help karo": "help me",
    
    # ========== HINDI NEGATIVE ==========
    "chest mein dard nahi hai": "I do not have chest pain",
    "seene mein dard nahi": "I do not have chest pain",
    "sar dard nahi hai": "I do not have a headache",
    "bukhar nahi hai": "I do not have a fever",
    "pet mein dard nahi": "I do not have stomach pain",
    "dard nahi hai": "I have no pain",
    "mujhe dard nahi": "I have no pain",
    "saans nahi aa rahi": "I cannot breathe",
    
    # ========== POLISH ==========
    
    # Pain related
    "mam bol w klatce piersiowej": "I have chest pain",
    "bol w klatce piersiowej": "chest pain",
    "bol w klatce": "chest pain",
    
    # Head related
    "bol glowy": "I have a headache",
    "mam bol glowy": "I have a headache",
    
    # Fever
    "mam goraczke": "I have a fever",
    "goraczka": "fever",
    
    # Stomach
    "mam bol brzucha": "I have stomach pain",
    "bol brzucha": "stomach pain",
    
    # Breathing
    "trudno mi oddychac": "I have difficulty breathing",
    "nie moge oddychac": "I cannot breathe",
    
    # Other symptoms
    "krecimi sie w glowie": "I feel dizzy",
    "bardzo boli": "it hurts a lot",
    "boli mnie": "I have pain",
    
    # Medication
    "lekarstwo": "medicine",
    "potrzebuje lekarstwa": "I need medicine",
    
    # Emergency
    "ambulans": "ambulance",
    "lekarz": "doctor",
    "potrzebuje lekarza": "I need a doctor",
    
    # General
    "tak": "yes",
    "nie": "no",
    "dobrze": "okay",
    "nie rozumiem": "I do not understand",
    "rozumiem": "I understand",
    "pomocy": "help me",
    "czuje sie dobrze": "I feel fine",
    
    # ========== POLISH NEGATIVE ==========
    "nie mam bolu w klatce": "I do not have chest pain",
    "nie mam bolu glowy": "I do not have a headache",
    "nie mam goraczki": "I do not have a fever",
    "nie boli": "it does not hurt",
    "nie mam bolu": "I have no pain",
    
    # ========== MALAYALAM ==========
    
    # Pain related
    "എനിക്ക് നെഞ്ചുവേദന ഉണ്ട്": "I have chest pain",
    "nenjil vali undu": "I have chest pain",
    "nenjil vali und": "I have chest pain",
    "ente nenjil valikkunnu": "my chest is hurting",
    "eniku nenjil vali und": "I have chest pain",
    "nenjil vali": "chest pain",
    
    # Head related
    "eniku thalavalikkunnu": "I have a headache",
    "thalavalikkunnu": "I have a headache",
    "thala valikkunnu": "my head is hurting",
    
    # Fever
    "eniku pani undu": "I have a fever",
    "pani undu": "I have a fever",
    
    # Stomach
    "eniku vayaril vali": "I have stomach pain",
    "vayaril vali undu": "I have stomach pain",
    
    # Breathing
    "shwasam muttunnu": "I am having difficulty breathing",
    "shwasam pidikkunnu": "I am having difficulty breathing",
    
    # Other symptoms
    "thalayan thonum": "I feel dizzy",
    "otti varunnu": "I feel like vomiting",
    "valiya vali undu": "I have severe pain",
    "vali undu": "I have pain",
    
    # Medication
    "marunn": "medicine",
    "eniku marunn vendum": "I need medicine",
    
    # Emergency
    "ambulance": "ambulance",
    "doctor": "doctor",
    "eniku doctor nee vendum": "I need a doctor",
    
    # General
    "athe": "yes",
    "alla": "no",
    "saukaryamayi irikkunnu": "I am fine",
    "manasilayilla": "I do not understand",
    "manasilayi": "I understand",
    "sahayam": "help me",
    
    # ========== MALAYALAM NEGATIVE ==========
    "eniku nenjil vali illa": "I do not have chest pain",
    "nenjil vali illa": "I do not have chest pain",
    "thalavalikkunilla": "I do not have a headache",
    "pani illa": "I do not have a fever",
    "eniku pani illa": "I do not have a fever",
    "vayaril vali illa": "I do not have stomach pain",
    "vali illa": "I have no pain",
    
    # ========== ARABIC ==========
    "عندي ألم في الصدر": "I have chest pain",
    "عندي صداع": "I have a headache",
    "عندي حمى": "I have a fever",
    "عندي ألم في المعدة": "I have stomach pain",
    "لا استطيع التنفس": "I cannot breathe",
    "أشعر بالدوار": "I feel dizzy",
    "أشعر بالغثيان": "I feel like vomiting",
    "الدواء": "medicine",
    "سيارة إسعاف": "ambulance",
    "طبيب": "doctor",
    "نعم": "yes",
    "لا": "no",
    "حسنا": "okay",
    "لا أفهم": "I do not understand",
    "أفهم": "I understand",
    "ساعدني": "help me",
    "أنا بخير": "I am fine",
    
    # ========== URDU ==========
    "میرے سینے میں درد ہے": "I have chest pain",
    "میرا سر درد ہے": "I have a headache",
    "مجھے بخار ہے": "I have a fever",
    "میرے پیٹ میں درد ہے": "I have stomach pain",
    "سانس لینے میں دشواری": "I have difficulty breathing",
    "چکر آ رہا ہے": "I feel dizzy",
    "مجھے دوا چاہیے": "I need medicine",
    "ایمبولینس": "ambulance",
    "ڈاکٹر": "doctor",
    "ہاں": "yes",
    "نہیں": "no",
    "ٹھیک ہے": "okay",
    "مجھے سمجھ نہیں آیا": "I do not understand",
    "مجھے سمجھ آ گیا": "I understand",
    "مدد کرو": "help me",
    
    # ========== BENGALI ==========
    "আমার বুকে ব্যথা": "I have chest pain",
    "আমার মাথা ব্যাথা": "I have a headache",
    "আমার জ্বর": "I have a fever",
    "আমার পেটে ব্যথা": "I have stomach pain",
    "শ্বাস নিতে কষ্ট": "I have difficulty breathing",
    "মাথা ঘোরা": "I feel dizzy",
    "ঔষধ": "medicine",
    "অ্যাম্বুলেন্স": "ambulance",
    "ডাক্তার": "doctor",
    "হ্যাঁ": "yes",
    "না": "no",
    "ঠিক আছে": "okay",
    "বুঝতে পারিনি": "I do not understand",
    "বুঝতে পেরেছি": "I understand",
    "সাহায্য করুন": "help me",
    
    # ========== SOMALI ==========
    "xanuun laabta": "I have chest pain",
    "madax xanuun": "I have a headache",
    "qandho": "I have a fever",
    "xanuun calool": "I have stomach pain",
    "neefsasho dhib": "I have difficulty breathing",
    "madhax wareeg": "I feel dizzy",
    "daawo": "medicine",
    "ambalaas": "ambulance",
    "dhakhtar": "doctor",
    "haa": "yes",
    "maya": "no",
    "waa hagaag": "okay",
    "ma fahmin": "I do not understand",
    "waan fahmay": "I understand",
    "i caawi": "help me",
    
    # ========== ROMANIAN ==========
    "durere in piept": "I have chest pain",
    "durere de cap": "I have a headache",
    "febra": "I have a fever",
    "durere de stomac": "I have stomach pain",
    "dificultate de respiratie": "I have difficulty breathing",
    "amețeală": "I feel dizzy",
    "medicament": "medicine",
    "ambulanta": "ambulance",
    "medic": "doctor",
    "da": "yes",
    "nu": "no",
    "bine": "okay",
    "nu inteleg": "I do not understand",
    "am inteles": "I understand",
    "ajutor": "help me",
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

# ============================================================
# SYMPTOM DETECTION
# ============================================================

SYMPTOM_MAP = {
    "tamil": {
        "nenji vali iruku": "chest pain",
        "nenji vali irukku": "chest pain",
        "nenji vali": "chest pain",
        "moochu varadhu": "breathing difficulty",
        "moochu pidikuthu": "breathing difficulty",
        "thalai vali": "headache",
        "kaichal": "fever",
        "vayiru vali": "stomach pain",
        "kaal vali": "leg pain",
        "kai vali": "arm pain",
        "thalai sutharuthu": "dizziness",
        "vanthi": "vomiting",
        "romba vali": "severe pain",
    },
    "hindi": {
        "seene mein dard": "chest pain",
        "saans lene mein takleef": "breathing difficulty",
        "saans nahi": "breathing difficulty",
        "sar dard": "headache",
        "bukhar": "fever",
        "pet dard": "stomach pain",
        "chakkar": "dizziness",
        "ulti": "vomiting",
        "bahut dard": "severe pain",
    },
    "polish": {
        "bol klatki": "chest pain",
        "trudnosci z oddychaniem": "breathing difficulty",
        "bol glowy": "headache",
        "goraczka": "fever",
        "bol brzucha": "stomach pain",
        "krecimi sie w glowie": "dizziness",
        "bardzo boli": "severe pain",
    },
    "malayalam": {
        "nenjil vali": "chest pain",
        "nenjil vali undu": "chest pain",
        "shwasam muttunnu": "breathing difficulty",
        "shwasam pidikkunnu": "breathing difficulty",
        "thalavalikkunnu": "headache",
        "pani undu": "fever",
        "vayaril vali": "stomach pain",
        "thalayan thonum": "dizziness",
        "otti varunnu": "vomiting",
        "valiya vali": "severe pain",
    },
    "arabic": {
        "ألم في الصدر": "chest pain",
        "صعوبة في التنفس": "breathing difficulty",
        "صداع": "headache",
        "حمى": "fever",
        "ألم في المعدة": "stomach pain",
        "دوار": "dizziness",
        "غثيان": "vomiting",
    },
    "urdu": {
        "سینے میں درد": "chest pain",
        "سانس لینے میں دشواری": "breathing difficulty",
        "سر درد": "headache",
        "بخار": "fever",
        "پیٹ میں درد": "stomach pain",
        "چکر": "dizziness",
    },
    "bengali": {
        "বুকে ব্যথা": "chest pain",
        "শ্বাস নিতে কষ্ট": "breathing difficulty",
        "মাথা ব্যাথা": "headache",
        "জ্বর": "fever",
        "পেটে ব্যথা": "stomach pain",
        "মাথা ঘোরা": "dizziness",
    },
    "somali": {
        "xanuun laabta": "chest pain",
        "neefsasho dhib": "breathing difficulty",
        "madax xanuun": "headache",
        "qandho": "fever",
        "xanuun calool": "stomach pain",
        "madhax wareeg": "dizziness",
    },
    "romanian": {
        "durere in piept": "chest pain",
        "dificultate de respiratie": "breathing difficulty",
        "durere de cap": "headache",
        "febra": "fever",
        "durere de stomac": "stomach pain",
        "amețeală": "dizziness",
    },
}

def detect_symptom(text, lang_code):
    lang_map = {
        "ta": "tamil",
        "hi": "hindi",
        "pl": "polish",
        "ml": "malayalam",
        "ar": "arabic",
        "ur": "urdu",
        "bn": "bengali",
        "so": "somali",
        "ro": "romanian",
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
        "Do you have your appointment letter with you?",
        "Have you been here before?",
        "Do you have any ID with you?",
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
        "Do you need help finding the department?",
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
        "Have you lost your appetite?",
        "Are you feeling nauseous?",
        "Is there any bleeding?",
        "Do you have any underlying conditions?",
        "Have you travelled recently?",
        "Are you pregnant?",
        "What is your medical history?",
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
        except Exception:
            pass
        if lang_code and lang_code != "auto":
            try:
                result = MyMemoryTranslator(source=lang_code, target="en-GB").translate(text)
                if result and result.strip().lower() != text.strip().lower():
                    return result, None
            except Exception:
                pass
        for src in ["ta", "hi", "pl", "ar", "ur", "bn", "so", "ro", "ml"]:
            try:
                result = MyMemoryTranslator(source=src, target="en-GB").translate(text)
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
        result = MyMemoryTranslator(source="en-GB", target=target_lang_code).translate(text)
        return result, None
    except Exception as e:
        return None, str(e)

def convert_to_native_script(text, lang_code):
    try:
        from deep_translator import MyMemoryTranslator
        english, _ = translate_to_english(text, lang_code)
        if not english or english.strip().lower() == text.strip().lower():
            return text
        native = MyMemoryTranslator(source="en-GB", target=lang_code).translate(english)
        if native and native.strip() != text.strip():
            return native
        return text
    except Exception:
        return text

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

    english_text, error = translate_to_english(text, lang_code)
    if error:
        return jsonify({"error": error}), 500

    native_text = text
    try:
        from deep_translator import MyMemoryTranslator
        if english_text and english_text.strip().lower() != text.strip().lower():
            converted = MyMemoryTranslator(source="en-GB", target=lang_code).translate(english_text)
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
