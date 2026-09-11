"""
MedOriva AI — Core Clinical & Reception Phrases Library
Classification: Non-Medical Device (Administrative Communication Support)
Languages Supported (9 Core MVP):
  - ta: Tamil (தமிழ்)
  - hi: Hindi (हिन्दी)
  - ml: Malayalam (മലയാളം)
  - bn: Bengali (বাংলা)
  - ur: Urdu (اردو)
  - ar: Arabic (العربية)
  - pl: Polish (Polski)
  - so: Somali (Soomaali)
  - ro: Romanian (Română)
"""

import re

# ============================================================
# 1. PLAIN-LANGUAGE SIMPLIFICATION RULES (Staff English Pre-processing)
# ============================================================
SIMPLIFY_RULES = [
    (r"\bmyocardial infarction\b", "heart attack"),
    (r"\bacute coronary syndrome\b", "severe chest pain"),
    (r"\bhypertension\b", "high blood pressure"),
    (r"\bhypotension\b", "low blood pressure"),
    (r"\bdyspnoea\b|\bdyspnea\b", "shortness of breath"),
    (r"\bcerebrovascular accident\b|\bcva\b", "stroke"),
    (r"\bhaemorrhage\b|\bhemorrhage\b", "heavy bleeding"),
    (r"\boedema\b|\bedema\b", "swelling"),
    (r"\bambulatory\b", "able to walk"),
    (r"\bcontraindicated\b", "not safe to take"),
    (r"\badminister orally\b", "take by mouth"),
    (r"\bcommence pharmacological treatment\b", "start medication"),
    (r"\brequire further diagnostic evaluation\b", "need more tests"),
    (r"\bphlebotomy\b", "blood test"),
    (r"\bpyrexia\b|\bfebrile\b", "high temperature"),
    (r"\bemesis\b", "vomiting"),
    (r"\bvertigo\b", "dizziness"),
    (r"\bpruritus\b", "itching"),
    (r"\berythema\b", "redness of skin"),
    (r"\bcephalalgia\b", "headache")
]

# ============================================================
# 2. AFFIRMATION, NEGATION & DURATION PATTERNS (All 9 Languages)
# ============================================================
AFFIRMATION_PATTERNS = {
    "en": ["yes", "yeah", "yep", "correct", "true", "i do", "i have", "agree"],
    "ta": ["aama", "aam", "sari", "irukku", "koodum", "ஆம்", "ஆமாம்", "சரி", "இருக்கிறது"],
    "hi": ["haan", "ha", "sahi", "theek", "hai", "हाँ", "हा", "सही", "ठीक"],
    "ml": ["athe", "und", "sari", "അതെ", "ഉണ്ട്", "ശരി"],
    "bn": ["haan", "hae", "thik", "aache", "হ্যাঁ", "হাঁ", "ঠিক", "আছে"],
    "ur": ["haan", "ji haan", "sahi", "hai", "ہاں", "جی ہاں", "درست", "ہے"],
    "ar": ["naam", "aywa", "sahih", "نعم", "ايوه", "صحيح", "أجل"],
    "pl": ["tak", "zgadza sie", "prawda", "mam", "jest"],
    "so": ["haa", "waa sax", "waa run", "jiraa"],
    "ro": ["da", "corect", "adevarat", "am", "este"]
}

NEGATION_PATTERNS = {
    "en": ["no", "not", "none", "never", "dont", "don't", "cannot", "cant", "can't", "denies", "without"],
    "ta": ["illai", "illa", "kidayathu", "illamal", "இல்லை", "இல்ல", "கிடையாது"],
    "hi": ["nahi", "nahin", "na", "bina", "नहीं", "ना", "बिना"],
    "ml": ["illa", "illathathu", "illaatha", "ഇല്ല", "ഇല്ലാതെ"],
    "bn": ["na", "nei", "ni", "না", "নেই", "নয়"],
    "ur": ["nahi", "nahin", "na", "نہیں", "نہ", "بغیر"],
    "ar": ["la", "laysa", "ma", "kalla", "لا", "ليس", "ما", "كلا", "بدون"],
    "pl": ["nie", "brak", "nie ma", "bez"],
    "so": ["maya", "ma jiro", "la'aan", "ha"],
    "ro": ["nu", "deloc", "fara", "nu am"]
}

DURATION_PATTERNS = [
    (r"\b(\d+)\s*(day|days|d)\b", r"for \1 days"),
    (r"\b(\d+)\s*(week|weeks|w)\b", r"for \1 weeks"),
    (r"\b(\d+)\s*(month|months|m)\b", r"for \1 months"),
    (r"\b(\d+)\s*(hour|hours|hr|hrs|h)\b", r"for \1 hours"),
    (r"\btoday\b", "since today"),
    (r"\byesterday\b", "since yesterday"),
    (r"\bthis morning\b", "since this morning")
]

# ============================================================
# 3. GUIDED CONTEXT PROMPTS (Locked Workflows)
# ============================================================
GUIDED_PROMPTS = {
    "Reception": [
        "Welcome. Do you have a booked appointment today?",
        "Please provide your full name and date of birth.",
        "Please take a seat in the waiting area. Staff will call you shortly.",
        "Do you need to update your home address or telephone number?",
        "Do you have an NHS number or your registration card with you?",
        "Are you registered as a permanent patient at this practice?"
    ],
    "Appointment": [
        "Are you attending today for a routine follow-up or a new issue?",
        "Can you confirm which regular medications you are currently taking?",
        "Do you have any known allergies to medicines or food?",
        "Have you taken your routine morning medication today?",
        "Are you here for a scheduled blood test or routine vaccination?",
        "Do you require a medical certificate or repeat prescription?"
    ],
    "Basic Symptoms": [
        "Where are you feeling pain or discomfort today?",
        "How many days or hours have you had this feeling?",
        "Do you have a high temperature or fever?",
        "Do you have a new or continuous cough?",
        "Are you experiencing any stomach pain, sickness, or vomiting?",
        "Are you feeling dizzy or lightheaded when standing up?"
    ]
}

# ============================================================
# 4. URGENT SYMPTOMS FOR STAFF AWARENESS (Non-Clinical Detection)
# ============================================================
URGENT_SYMPTOMS_CONFIG = {
    "chest_pain": [
        "chest pain", "tightness in chest", "pressure in chest", "heavy chest",
        "nenji vali", "seene mein dard", "boli w klatce", "alam fi sadr",
        "pait mein dard", "dhabar xanuun", "durere in piept"
    ],
    "shortness_of_breath": [
        "shortness of breath", "struggling to breathe", "cannot breathe", "breathless",
        "swas", "moochu thinaral", "duszno", "diq fi tanaffus", "nefas qabasho", "respiratie grea"
    ],
    "stroke_symptoms": [
        "face drooping", "arm weakness", "slurred speech", "numbness one side",
        "stroke", "paralysis", "falij", "udar", "istirkha"
    ]
}

# ============================================================
# 5. MULTI-LANGUAGE SYMPTOM TOKEN MAPPINGS (Equal Across All 9)
# ============================================================
MULTI_LANG_SYMPTOMS = {
    "ta": {
        "chest_pain": ["nenji vali", "maarbu vali", "நெஞ்சு வலி", "மார்பு வலி"],
        "shortness_of_breath": ["moochu thinaral", "swasa kolaru", "மூச்சு திணறல்"],
        "headache": ["thala vali", "thalai vali", "தலைவலி", "தலை வலி"],
        "fever": ["kaichal", "kaaichal", "suram", "காய்ச்சல்"],
        "cough": ["irumal", "இருமல்"],
        "stomach_pain": ["vayitru vali", "vayiru vali", "வயிற்று வலி", "வயிறு வலி"],
        "dizziness": ["mayakkam", "thala suttrudhal", "மயக்கம்", "தலைசுற்றல்"],
        "vomiting": ["vaanthi", "vandi", "வாந்தி"],
        "sore_throat": ["thondai vali", "தொண்டை வலி"],
        "back_pain": ["muthugu vali", "iduppu vali", "முதுகு வலி", "இடுப்பு வலி"],
        "skin_rash": ["thol thadippu", "arippu", "தோல் தடிப்பு", "அரிப்பு"]
    },
    "hi": {
        "chest_pain": ["seene mein dard", "chhati mein dard", "सीने में दर्द", "छाती में दर्द"],
        "shortness_of_breath": ["saans lene mein takleef", "saans phoolna", "सांस लेने में तकलीफ"],
        "headache": ["sir dard", "sar dard", "सिर दर्द", "सर दर्द"],
        "fever": ["bukhar", "tez bukhar", "बुखार"],
        "cough": ["khansi", "khaansi", "खांसी"],
        "stomach_pain": ["pet dard", "pet mein dard", "पेट दर्द", "पेट में दर्द"],
        "dizziness": ["chakkar", "chakkar aana", "चक्कर आना", "चक्कर"],
        "vomiting": ["ulti", "qay", "उल्टी"],
        "sore_throat": ["gale mein dard", "gala kharab", "गले में दर्द"],
        "back_pain": ["peeth dard", "kamar dard", "पीठ दर्द", "कमर दर्द"],
        "skin_rash": ["daane", "khujli", "chakatte", "दाने", "खुजली"]
    },
    "ml": {
        "chest_pain": ["nenju vedana", "nenjil vedana", "നെഞ്ചുവേദന", "നെഞ്ചിൽ വേദന"],
        "shortness_of_breath": ["shwasam muttal", "shwasam edukkan budhimuttu", "ശ്വാസംമുട്ടൽ"],
        "headache": ["thala vedana", "thalavedana", "തലവേദന"],
        "fever": ["pani", "choodu", "പനി"],
        "cough": ["chuma", "ചുമ"],
        "stomach_pain": ["vayaru vedana", "vayaruvvedana", "വയറുവേദന"],
        "dizziness": ["thalakarakkam", "തലകറക്കം"],
        "vomiting": ["chardhi", "ഛർദ്ദി"],
        "sore_throat": ["thonda vedana", "തൊണ്ടവേദന"],
        "back_pain": ["puram vedana", "naduv vedana", "പുറംവേദന", "നടുവേദന"],
        "skin_rash": ["thadippu", "chorichil", "തടിപ്പ്", "ചൊറിച്ചിൽ"]
    },
    "bn": {
        "chest_pain": ["buke byatha", "buke batha", "বুকে ব্যথা", "বুকে ব্যাথা"],
        "shortness_of_breath": ["shas kosto", "shash nite koshto", "শ্বাসকষ্ট", "শ্বাস নিতে কষ্ট"],
        "headache": ["matha byatha", "matha batha", "মাথা ব্যথা"],
        "fever": ["jwor", "jor", "জ্বর"],
        "cough": ["kashi", "kaashi", "কাশি"],
        "stomach_pain": ["pet byatha", "pete byatha", "পেট ব্যথা", "পেটে ব্যথা"],
        "dizziness": ["matha ghora", "matha ghurche", "মাথা ঘোরা"],
        "vomiting": ["bomi", "বমি"],
        "sore_throat": ["gola byatha", "gola batha", "গলা ব্যথা"],
        "back_pain": ["pither byatha", "komor byatha", "পিঠের ব্যথা", "কোমর ব্যথা"],
        "skin_rash": ["chulkani", "rash", "fusuri", "চুলকানি", "ফুসকুড়ি"]
    },
    "ur": {
        "chest_pain": ["seenay mein dard", "chhati mein dard", "سینے میں درد"],
        "shortness_of_breath": ["saans lene mein dushwari", "saans phoolna", "سانس پھولنا", "سانس لینے میں دشواری"],
        "headache": ["sar dard", "sir mein dard", "سر درد"],
        "fever": ["bukhar", "tez bukhar", "بخار"],
        "cough": ["khansi", "khaansi", "کھانسی"],
        "stomach_pain": ["pait mein dard", "pet dard", "پیٹ میں درد"],
        "dizziness": ["chakkar", "chakkar aana", "چکر آنا"],
        "vomiting": ["ulti", "qay", "الٹی"],
        "sore_throat": ["galay mein dard", "gala kharab", "گلے میں درد"],
        "back_pain": ["kamar dard", "peeth mein dard", "کمر درد", "پیٹھ میں درد"],
        "skin_rash": ["kharish", "daanay", "جلد پر دانے", "خارش"]
    },
    "ar": {
        "chest_pain": ["alam fi sadr", "alam sadr", "ألم في الصدر", "الم في الصدر"],
        "shortness_of_breath": ["diq tanaffus", "diq fi tanaffus", "ضيق في التنفس", "صعوبة في التنفس"],
        "headache": ["sudaa", "waja ras", "صداع", "ألم في الرأس"],
        "fever": ["humma", "harara murtafia", "حمى", "حرارة مرتفعة"],
        "cough": ["sual", "kahha", "سعال", "كحة"],
        "stomach_pain": ["alam batn", "waja batn", "ألم في البطن", "ألم في المعدة"],
        "dizziness": ["dawkha", "duwar", "دوخة", "دوار"],
        "vomiting": ["qay", "istifragh", "قيء", "استفراغ"],
        "sore_throat": ["iltihab halq", "alam fi halq", "التهاب الحلق", "ألم في الحلق"],
        "back_pain": ["alam zahr", "alam fi zahr", "ألم في الظهر"],
        "skin_rash": ["tafah jildi", "hikkah", "طفح جلدي", "حكة"]
    },
    "pl": {
        "chest_pain": ["bol w klatce", "bol w klatce piersiowej", "ból w klatce piersiowej"],
        "shortness_of_breath": ["dusznosc", "brak tchu", "duszność", "trudnosci z oddychaniem"],
        "headache": ["bol glowy", "ból głowy"],
        "fever": ["goraczka", "wysoka temperatura", "gorączka"],
        "cough": ["kaszel", "suchy kaszel", "mokry kaszel"],
        "stomach_pain": ["bol brzucha", "ból brzucha", "skurcze zoladka"],
        "dizziness": ["zawroty glowy", "kręci mi się w głowie", "zawroty głowy"],
        "vomiting": ["wymioty", "mdlosci", "nudności"],
        "sore_throat": ["bol gardla", "ból gardła", "pieczenie w gardle"],
        "back_pain": ["bol plecow", "ból pleców", "ból kręgosłupa"],
        "skin_rash": ["wysypka", "swedzenie", "swędzenie skóry"]
    },
    "so": {
        "chest_pain": ["laab xanuun", "xabad xanuun", "laabta oo i xanuunaysa"],
        "shortness_of_breath": ["neefsasho adag", "neef qabasho", "neefta oo igu dhegaysa"],
        "headache": ["madax xanuun", "madaxa oo i xanuunaya"],
        "fever": ["qandho", "xumad", "kuleyl"],
        "cough": ["qufac", "qufac joogto ah"],
        "stomach_pain": ["calool xanuun", "caloosha oo i xanuunaysa"],
        "dizziness": ["wareer", "madax wareer"],
        "vomiting": ["matag", "lalabbo"],
        "sore_throat": ["dhuun xanuun", "hunguri xanuun"],
        "back_pain": ["dhabar xanuun", "dhabarka oo i xanuunaya"],
        "skin_rash": ["finan", "cuncun", "maqaarka oo cuncunaya"]
    },
    "ro": {
        "chest_pain": ["durere in piept", "durere toracica", "strangere in piept"],
        "shortness_of_breath": ["respiratie grea", "lipsa de aer", "dificultati de respiratie"],
        "headache": ["durere de cap", "migrena"],
        "fever": ["febra", "temperatura ridicata"],
        "cough": ["tuse", "tuse seaca"],
        "stomach_pain": ["durere de stomac", "durere abdominala", "crampe la stomac"],
        "dizziness": ["ameteala", "stare de lesin"],
        "vomiting": ["varsaturi", "stare de greata", "voma"],
        "sore_throat": ["durere in gat", "gat inflamat"],
        "back_pain": ["durere de spate", "durere lombara"],
        "skin_rash": ["eruptie cutanata", "mancarime", "iritatie pe piele"]
    }
}

# ============================================================
# 6. PATIENT CANONICAL BIDIRECTIONAL RESPONSES (All 9 Languages)
# ============================================================
PATIENT_CANONICAL_RESPONSES = {
    "ta": {
        "chest_pain": {
            "pos": ("I have chest pain", "எனக்கு நெஞ்சு வலி இருக்கிறது"),
            "neg": ("I do not have chest pain", "எனக்கு நெஞ்சு வலி இல்லை")
        },
        "shortness_of_breath": {
            "pos": ("I have shortness of breath", "எனக்கு மூச்சு திணறல் இருக்கிறது"),
            "neg": ("I do not have shortness of breath", "எனக்கு மூச்சு திணறல் இல்லை")
        },
        "headache": {
            "pos": ("I have a headache", "எனக்கு தலைவலி இருக்கிறது"),
            "neg": ("I do not have a headache", "எனக்கு தலைவலி இல்லை")
        },
        "fever": {
            "pos": ("I have a fever", "எனக்கு காய்ச்சல் இருக்கிறது"),
            "neg": ("I do not have a fever", "எனக்கு காய்ச்சல் இல்லை")
        },
        "cough": {
            "pos": ("I have a cough", "எனக்கு இருமல் இருக்கிறது"),
            "neg": ("I do not have a cough", "எனக்கு இருமல் இல்லை")
        },
        "stomach_pain": {
            "pos": ("I have stomach pain", "எனக்கு வயிற்று வலி இருக்கிறது"),
            "neg": ("I do not have stomach pain", "எனக்கு வயிற்று வலி இல்லை")
        },
        "dizziness": {
            "pos": ("I feel dizzy", "எனக்கு மயக்கம் இருக்கிறது"),
            "neg": ("I do not feel dizzy", "எனக்கு மயக்கம் இல்லை")
        },
        "vomiting": {
            "pos": ("I have vomiting", "எனக்கு வாந்தி இருக்கிறது"),
            "neg": ("I do not have vomiting", "எனக்கு வாந்தி இல்லை")
        },
        "sore_throat": {
            "pos": ("I have a sore throat", "எனக்கு தொண்டை வலி இருக்கிறது"),
            "neg": ("I do not have a sore throat", "எனக்கு தொண்டை வலி இல்லை")
        },
        "back_pain": {
            "pos": ("I have back pain", "எனக்கு முதுகு வலி இருக்கிறது"),
            "neg": ("I do not have back pain", "எனக்கு முதுகு வலி இல்லை")
        },
        "skin_rash": {
            "pos": ("I have a skin rash", "எனக்கு தோல் தடிப்பு இருக்கிறது"),
            "neg": ("I do not have a skin rash", "எனக்கு தோல் தடிப்பு இல்லை")
        }
    },
    "hi": {
        "chest_pain": {
            "pos": ("I have chest pain", "मुझे सीने में दर्द है"),
            "neg": ("I do not have chest pain", "मुझे सीने में दर्द नहीं है")
        },
        "shortness_of_breath": {
            "pos": ("I have shortness of breath", "मुझे सांस लेने में तकलीफ है"),
            "neg": ("I do not have shortness of breath", "मुझे सांस लेने में तकलीफ नहीं है")
        },
        "headache": {
            "pos": ("I have a headache", "मुझे सिर दर्द है"),
            "neg": ("I do not have a headache", "मुझे सिर दर्द नहीं है")
        },
        "fever": {
            "pos": ("I have a fever", "मुझे बुखार है"),
            "neg": ("I do not have a fever", "मुझे बुखार नहीं है")
        },
        "cough": {
            "pos": ("I have a cough", "मुझे खांसी है"),
            "neg": ("I do not have a cough", "मुझे खांसी नहीं है")
        },
        "stomach_pain": {
            "pos": ("I have stomach pain", "मुझे पेट में दर्द है"),
            "neg": ("I do not have stomach pain", "मुझे पेट में दर्द नहीं है")
        },
        "dizziness": {
            "pos": ("I feel dizzy", "मुझे चक्कर आ रहे हैं"),
            "neg": ("I do not feel dizzy", "मुझे चक्कर नहीं आ रहे हैं")
        },
        "vomiting": {
            "pos": ("I have vomiting", "मुझे उल्टी आ रही है"),
            "neg": ("I do not have vomiting", "मुझे उल्टी नहीं आ रही है")
        },
        "sore_throat": {
            "pos": ("I have a sore throat", "मेरे गले में दर्द है"),
            "neg": ("I do not have a sore throat", "मेरे गले में दर्द नहीं है")
        },
        "back_pain": {
            "pos": ("I have back pain", "मेरी पीठ में दर्द है"),
            "neg": ("I do not have back pain", "मेरी पीठ में दर्द नहीं है")
        },
        "skin_rash": {
            "pos": ("I have a skin rash", "मेरी त्वचा पर दाने हैं"),
            "neg": ("I do not have a skin rash", "मेरी त्वचा पर दाने नहीं हैं")
        }
    },
    "ml": {
        "chest_pain": {
            "pos": ("I have chest pain", "എനിക്ക് നെഞ്ചുവേദനയുണ്ട്"),
            "neg": ("I do not have chest pain", "എനിക്ക് നെഞ്ചുവേദനയില്ല")
        },
        "shortness_of_breath": {
            "pos": ("I have shortness of breath", "എനിക്ക് ശ്വാസംമുട്ടലുണ്ട്"),
            "neg": ("I do not have shortness of breath", "എനിക്ക് ശ്വാസംമുട്ടലില്ല")
        },
        "headache": {
            "pos": ("I have a headache", "എനിക്ക് തലവേദനയുണ്ട്"),
            "neg": ("I do not have a headache", "എനിക്ക് തലവേദനയില്ല")
        },
        "fever": {
            "pos": ("I have a fever", "എനിക്ക് പനിയുണ്ട്"),
            "neg": ("I do not have a fever", "എനിക്ക് പനിയില്ല")
        },
        "cough": {
            "pos": ("I have a cough", "എനിക്ക് ചുമയുണ്ട്"),
            "neg": ("I do not have a cough", "എനിക്ക് ചുമയില്ല")
        },
        "stomach_pain": {
            "pos": ("I have stomach pain", "എനിക്ക് വയറുവേദനയുണ്ട്"),
            "neg": ("I do not have stomach pain", "എനിക്ക് വയറുവേദനയില്ല")
        },
        "dizziness": {
            "pos": ("I feel dizzy", "എനിക്ക് തലകറക്കമുണ്ട്"),
            "neg": ("I do not feel dizzy", "എനിക്ക് തലകറക്കമില്ല")
        },
        "vomiting": {
            "pos": ("I have vomiting", "എനിക്ക് ഛർദ്ദിയുണ്ട്"),
            "neg": ("I do not have vomiting", "എനിക്ക് ഛർദ്ദിയില്ല")
        },
        "sore_throat": {
            "pos": ("I have a sore throat", "എനിക്ക് തൊണ്ടവേദനയുണ്ട്"),
            "neg": ("I do not have a sore throat", "എനിക്ക് തൊണ്ടവേദനയില്ല")
        },
        "back_pain": {
            "pos": ("I have back pain", "എനിക്ക് പുറംവേദനയുണ്ട്"),
            "neg": ("I do not have back pain", "എനിക്ക് പുറംവേദനയില്ല")
        },
        "skin_rash": {
            "pos": ("I have a skin rash", "എനിക്ക് തൊലിപ്പുറത്ത് തടിപ്പുണ്ട്"),
            "neg": ("I do not have a skin rash", "എനിക്ക് തടിപ്പില്ല")
        }
    },
    "bn": {
        "chest_pain": {
            "pos": ("I have chest pain", "আমার বুকে ব্যথা আছে"),
            "neg": ("I do not have chest pain", "আমার বুকে ব্যথা নেই")
        },
        "shortness_of_breath": {
            "pos": ("I have shortness of breath", "আমার শ্বাসকষ্ট হচ্ছে"),
            "neg": ("I do not have shortness of breath", "আমার শ্বাসকষ্ট নেই")
        },
        "headache": {
            "pos": ("I have a headache", "আমার মাথা ব্যথা করছে"),
            "neg": ("I do not have a headache", "আমার মাথা ব্যথা নেই")
        },
        "fever": {
            "pos": ("I have a fever", "আমার জ্বর হয়েছে"),
            "neg": ("I do not have a fever", "আমার জ্বর নেই")
        },
        "cough": {
            "pos": ("I have a cough", "আমার কাশি আছে"),
            "neg": ("I do not have a cough", "আমার কাশি নেই")
        },
        "stomach_pain": {
            "pos": ("I have stomach pain", "আমার পেটে ব্যথা আছে"),
            "neg": ("I do not have stomach pain", "আমার পেটে ব্যথা নেই")
        },
        "dizziness": {
            "pos": ("I feel dizzy", "আমার মাথা ঘুরছে"),
            "neg": ("I do not feel dizzy", "আমার মাথা ঘুরছে না")
        },
        "vomiting": {
            "pos": ("I have vomiting", "আমার বমি হচ্ছে"),
            "neg": ("I do not have vomiting", "আমার বমি হচ্ছে না")
        },
        "sore_throat": {
            "pos": ("I have a sore throat", "আমার গলা ব্যথা করছে"),
            "neg": ("I do not have a sore throat", "আমার গলা ব্যথা নেই")
        },
        "back_pain": {
            "pos": ("I have back pain", "আমার পিঠে ব্যথা আছে"),
            "neg": ("I do not have back pain", "আমার পিঠে ব্যথা নেই")
        },
        "skin_rash": {
            "pos": ("I have a skin rash", "আমার ত্বকে ফুসকুড়ি হয়েছে"),
            "neg": ("I do not have a skin rash", "আমার ত্বকে ফুসকুড়ি নেই")
        }
    },
    "ur": {
        "chest_pain": {
            "pos": ("I have chest pain", "میرے سینے میں درد ہے"),
            "neg": ("I do not have chest pain", "میرے سینے میں درد نہیں ہے")
        },
        "shortness_of_breath": {
            "pos": ("I have shortness of breath", "مجھے سانس لینے میں دشواری ہے"),
            "neg": ("I do not have shortness of breath", "مجھے سانس لینے میں دشواری نہیں ہے")
        },
        "headache": {
            "pos": ("I have a headache", "میرے سر میں درد ہے"),
            "neg": ("I do not have a headache", "میرے سر میں درد نہیں ہے")
        },
        "fever": {
            "pos": ("I have a fever", "مجھے بخار ہے"),
            "neg": ("I do not have a fever", "مجھے بخار نہیں ہے")
        },
        "cough": {
            "pos": ("I have a cough", "مجھے کھانسی ہے"),
            "neg": ("I do not have a cough", "مجھے کھانسی نہیں ہے")
        },
        "stomach_pain": {
            "pos": ("I have stomach pain", "میرے پیٹ میں درد ہے"),
            "neg": ("I do not have stomach pain", "میرے پیٹ میں درد نہیں ہے")
        },
        "dizziness": {
            "pos": ("I feel dizzy", "مجھے چکر آ رہے ہیں"),
            "neg": ("I do not feel dizzy", "مجھے چکر نہیں آ رہے ہیں")
        },
        "vomiting": {
            "pos": ("I have vomiting", "مجھے الٹی آ رہی ہے"),
            "neg": ("I do not have vomiting", "مجھے الٹی نہیں آ رہی ہے")
        },
        "sore_throat": {
            "pos": ("I have a sore throat", "میرے گلے میں درد ہے"),
            "neg": ("I do not have a sore throat", "میرے گلے میں درد نہیں ہے")
        },
        "back_pain": {
            "pos": ("I have back pain", "میری کمر میں درد ہے"),
            "neg": ("I do not have back pain", "میری کمر میں درد نہیں ہے")
        },
        "skin_rash": {
            "pos": ("I have a skin rash", "میری جلد پر دانے ہیں"),
            "neg": ("I do not have a skin rash", "میری جلد پر دانے نہیں ہیں")
        }
    },
    "ar": {
        "chest_pain": {
            "pos": ("I have chest pain", "عندي ألم في الصدر"),
            "neg": ("I do not have chest pain", "ليس عندي ألم في الصدر")
        },
        "shortness_of_breath": {
            "pos": ("I have shortness of breath", "عندي ضيق في التنفس"),
            "neg": ("I do not have shortness of breath", "ليس عندي ضيق في التنفس")
        },
        "headache": {
            "pos": ("I have a headache", "عندي صداع"),
            "neg": ("I do not have a headache", "ليس عندي صداع")
        },
        "fever": {
            "pos": ("I have a fever", "عندي حمى"),
            "neg": ("I do not have a fever", "ليس عندي حمى")
        },
        "cough": {
            "pos": ("I have a cough", "عندي سعال"),
            "neg": ("I do not have a cough", "ليس عندي سعال")
        },
        "stomach_pain": {
            "pos": ("I have stomach pain", "عندي ألم في البطن"),
            "neg": ("I do not have stomach pain", "ليس عندي ألم في البطن")
        },
        "dizziness": {
            "pos": ("I feel dizzy", "أشعر بدوخة"),
            "neg": ("I do not feel dizzy", "لا أشعر بدوخة")
        },
        "vomiting": {
            "pos": ("I have vomiting", "عندي قيء"),
            "neg": ("I do not have vomiting", "ليس عندي قيء")
        },
        "sore_throat": {
            "pos": ("I have a sore throat", "عندي ألم في الحلق"),
            "neg": ("I do not have a sore throat", "ليس عندي ألم في الحلق")
        },
        "back_pain": {
            "pos": ("I have back pain", "عندي ألم في الظهر"),
            "neg": ("I do not have back pain", "ليس عندي ألم في الظهر")
        },
        "skin_rash": {
            "pos": ("I have a skin rash", "عندي طفح جلدي"),
            "neg": ("I do not have a skin rash", "ليس عندي طفح جلدي")
        }
    },
    "pl": {
        "chest_pain": {
            "pos": ("I have chest pain", "Boli mnie w klatce piersiowej"),
            "neg": ("I do not have chest pain", "Nie boli mnie w klatce piersiowej")
        },
        "shortness_of_breath": {
            "pos": ("I have shortness of breath", "Mam duszności"),
            "neg": ("I do not have shortness of breath", "Nie mam duszności")
        },
        "headache": {
            "pos": ("I have a headache", "Boli mnie głowa"),
            "neg": ("I do not have a headache", "Nie boli mnie głowa")
        },
        "fever": {
            "pos": ("I have a fever", "Mam gorączkę"),
            "neg": ("I do not have a fever", "Nie mam gorączki")
        },
        "cough": {
            "pos": ("I have a cough", "Mam kaszel"),
            "neg": ("I do not have a cough", "Nie mam kaszlu")
        },
        "stomach_pain": {
            "pos": ("I have stomach pain", "Boli mnie brzuch"),
            "neg": ("I do not have stomach pain", "Nie boli mnie brzuch")
        },
        "dizziness": {
            "pos": ("I feel dizzy", "Kręci mi się w głowie"),
            "neg": ("I do not feel dizzy", "Nie kręci mi się w głowie")
        },
        "vomiting": {
            "pos": ("I have vomiting", "Mam wymioty"),
            "neg": ("I do not have vomiting", "Nie mam wymiotów")
        },
        "sore_throat": {
            "pos": ("I have a sore throat", "Boli mnie gardło"),
            "neg": ("I do not have a sore throat", "Nie boli mnie gardło")
        },
        "back_pain": {
            "pos": ("I have back pain", "Bolą mnie plecy"),
            "neg": ("I do not have back pain", "Nie bolą mnie plecy")
        },
        "skin_rash": {
            "pos": ("I have a skin rash", "Mam wysypkę na skórze"),
            "neg": ("I do not have a skin rash", "Nie mam wysypki")
        }
    },
    "so": {
        "chest_pain": {
            "pos": ("I have chest pain", "Waxaan qabaa laab xanuun"),
            "neg": ("I do not have chest pain", "Ma qabo laab xanuun")
        },
        "shortness_of_breath": {
            "pos": ("I have shortness of breath", "Waxaan qabaa neefsasho adag"),
            "neg": ("I do not have shortness of breath", "Ma qabo neefsasho adag")
        },
        "headache": {
            "pos": ("I have a headache", "Waxaan qabaa madax xanuun"),
            "neg": ("I do not have a headache", "Ma qabo madax xanuun")
        },
        "fever": {
            "pos": ("I have a fever", "Waxaan qabaa qandho"),
            "neg": ("I do not have a fever", "Ma qabo qandho")
        },
        "cough": {
            "pos": ("I have a cough", "Waxaan qabaa qufac"),
            "neg": ("I do not have a cough", "Ma qabo qufac")
        },
        "stomach_pain": {
            "pos": ("I have stomach pain", "Waxaan qabaa calool xanuun"),
            "neg": ("I do not have stomach pain", "Ma qabo calool xanuun")
        },
        "dizziness": {
            "pos": ("I feel dizzy", "Waxaan dareemayaa wareer"),
            "neg": ("I do not feel dizzy", "Ma dareemayo wareer")
        },
        "vomiting": {
            "pos": ("I have vomiting", "Waxaan qabaa matag"),
            "neg": ("I do not have vomiting", "Ma qabo matag")
        },
        "sore_throat": {
            "pos": ("I have a sore throat", "Waxaan qabaa dhuun xanuun"),
            "neg": ("I do not have a sore throat", "Ma qabo dhuun xanuun")
        },
        "back_pain": {
            "pos": ("I have back pain", "Waxaan qabaa dhabar xanuun"),
            "neg": ("I do not have back pain", "Ma qabo dhabar xanuun")
        },
        "skin_rash": {
            "pos": ("I have a skin rash", "Waxaan leeyahay finan maqaarka ah"),
            "neg": ("I do not have a skin rash", "Ma lihi finan maqaarka ah")
        }
    },
    "ro": {
        "chest_pain": {
            "pos": ("I have chest pain", "Am dureri în piept"),
            "neg": ("I do not have chest pain", "Nu am dureri în piept")
        },
        "shortness_of_breath": {
            "pos": ("I have shortness of breath", "Respir cu greutate"),
            "neg": ("I do not have shortness of breath", "Nu am dificultăți de respirație")
        },
        "headache": {
            "pos": ("I have a headache", "Mă doare capul"),
            "neg": ("I do not have a headache", "Nu mă doare capul")
        },
        "fever": {
            "pos": ("I have a fever", "Am febră"),
            "neg": ("I do not have a fever", "Nu am febră")
        },
        "cough": {
            "pos": ("I have a cough", "Am tuse"),
            "neg": ("I do not have a cough", "Nu am tuse")
        },
        "stomach_pain": {
            "pos": ("I have stomach pain", "Mă doare stomacul"),
            "neg": ("I do not have stomach pain", "Nu mă doare stomacul")
        },
        "dizziness": {
            "pos": ("I feel dizzy", "Am amețeli"),
            "neg": ("I do not feel dizzy", "Nu am amețeli")
        },
        "vomiting": {
            "pos": ("I have vomiting", "Am vărsături"),
            "neg": ("I do not have vomiting", "Nu am vărsături")
        },
        "sore_throat": {
            "pos": ("I have a sore throat", "Mă doare în gât"),
            "neg": ("I do not have a sore throat", "Nu mă doare în gât")
        },
        "back_pain": {
            "pos": ("I have back pain", "Mă doare spatele"),
            "neg": ("I do not have back pain", "Nu mă doare spatele")
        },
        "skin_rash": {
            "pos": ("I have a skin rash", "Am o erupție pe piele"),
            "neg": ("I do not have a skin rash", "Nu am erupții pe piele")
        }
    }
}

# ============================================================
# 7. PARSING & EXTRACTION ENGINE
# ============================================================
def extract_symptom(text: str, lang_code: str):
    """
    Extracts standard symptom key, canonical English term, and native translation
    for any supported language.
    """
    if not text:
        return None, None, None

    clean_text = re.sub(r'[^\w\s]', ' ', text.lower())
    clean_text = " ".join(clean_text.split())
    target_lang = lang_code.lower()[:2] if lang_code else "en"

    # Search in specified language dictionary
    lang_dict = MULTI_LANG_SYMPTOMS.get(target_lang, {})
    for sym_key, phrases in lang_dict.items():
        for phrase in phrases:
            clean_phrase = " ".join(re.sub(r'[^\w\s]', ' ', phrase.lower()).split())
            if clean_phrase in clean_text:
                eng_name = sym_key.replace("_", " ")
                native_name = phrase
                return sym_key, eng_name, native_name

    # Fallback to English symptom terms
    en_dict = MULTI_LANG_SYMPTOMS.get("en", {})
    for sym_key, phrases in en_dict.items():
        for phrase in phrases:
            if phrase in clean_text:
                return sym_key, phrase, phrase

    return None, None, None

def synthesize_staff_question(text: str, target_lang: str):
    """
    Synthesizes standard questions deterministically if matching guided prompts.
    """
    if not text:
        return ""
    clean = " ".join(text.strip().lower().split())
    
    # Fast match for standard check-in greetings
    if "booked appointment" in clean:
        translations = {
            "ta": "வணக்கம். உங்களுக்கு இன்று முன்பதிவு செய்யப்பட்ட அப்பாயிண்ட்மென்ட் உள்ளதா?",
            "hi": "नमस्ते। क्या आज आपका पहले से बुक किया हुआ अपॉइंटमेंट है?",
            "ml": "നമസ്കാരം. നിങ്ങൾക്ക് ഇന്ന് ബുക്ക് ചെയ്ത അപ്പോയിന്റ്മെന്റ് ഉണ്ടോ?",
            "bn": "স্বাগতম। আপনার কি আজ কোনো বুক করা অ্যাপয়েন্টমেন্ট আছে?",
            "ur": "خوش آمدید۔ کیا آج آپ کا پہلے سے بک شدہ اپوائنٹمنٹ ہے؟",
            "ar": "مرحباً. هل لديك موعد محجوز اليوم؟",
            "pl": "Dzień dobry. Czy ma Pan/Pani zarezerwowaną wizytę na dzisiaj?",
            "so": "Soo dhowow. Ballan ma kuu qoran tahay maanta?",
            "ro": "Bună ziua. Aveți o programare făcută pentru astăzi?"
        }
        return translations.get(target_lang[:2], "")

    if "name and date of birth" in clean:
        translations = {
            "ta": "தயவுசெய்து உங்கள் முழுப் பெயர் மற்றும் பிறந்த தேதியைக் கூறுங்கள்.",
            "hi": "कृपया अपना पूरा नाम और जन्म तिथि बताएं।",
            "ml": "ദയവായി നിങ്ങളുടെ മുഴുവൻ പേരും ജനനത്തീയതിയും പറയുക.",
            "bn": "দয়া করে আপনার পুরো নাম এবং জন্ম তারিখ বলুন।",
            "ur": "براہ کرم اپنا پورا نام اور تاریخ پیدائش بتائیں۔",
            "ar": "يرجى ذكر اسمك الكامل وتاريخ ميلادك.",
            "pl": "Proszę podać swoje imię, nazwisko i datę urodzenia.",
            "so": "Fadlan noo sheeg magacaaga oo buuxa iyo taariikhda dhalashadaada.",
            "ro": "Vă rugăm să ne spuneți numele complet și data nașterii."
        }
        return translations.get(target_lang[:2], "")

    return ""
