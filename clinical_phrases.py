import re

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

# ============================================================
# AFFIRMATIONS & NEGATIONS (ALL 9 LANGUAGES)
# ============================================================
AFFIRMATION_PATTERNS = {
    "ta": ["aam", "aama", "aamaam", "seri", "kandippa", "aamanga", "ஆம்", "ஆமாம்", "சரி"],
    "hi": ["haan", "ji haan", "theek hai", "sahi", "haanji", "हाँ", "जी हाँ", "ठीक है"],
    "ml": ["athe", "atheyo", "sherikkum", "ശരി", "അതെ"],
    "pl": ["tak", "zgadza sie", "dokladnie", "jasne"],
    "ar": ["naam", "na'am", "aiwa", "sah", "نعم", "أيوا", "أجل"],
    "ur": ["haan", "jee", "jee haan", "ہاں", "جی", "جی ہاں"],
    "bn": ["hae", "hyan", "thik achhe", "হ্যাঁ", "ঠিক আছে"],
    "so": ["haa", "waa sax", "haye"],
    "ro": ["da", "exact", "sigur", "corect"],
    "en": ["yes", "yeah", "yep", "sure", "correct", "affirmative"]
}

NEGATION_PATTERNS = {
    "ta": ["illai", "illa", "varadhu", "varala", "ila", "kidayathu", "illamal", "இல்லை", "இல்ல", "கிடையாது", "வராது", "இல்லாமல்"],
    "hi": ["nahi", "nahin", "nhi", "mat", "na", "bina", "kuch nahi", "नहीं", "ना", "मत", "बिना", "कुछ नहीं", "नहीं है"],
    "ml": ["illa", "alla", "illathe", "illaatha", "ഇല്ല", "അല്ല", "ഇല്ലാതെ"],
    "pl": ["nie", "brak", "bez", "nie ma", "ani", "zadnych", "nie czuje", "nigdy"],
    "ar": ["la", "laysa", "mish", "ma", "bidun", "لا", "ليس", "ما", "مش", "بدون", "كلا"],
    "ur": ["nahi", "nahin", "na", "bina", "baghair", "نہیں", "نہ", "بغیر"],
    "bn": ["na", "ni", "nay", "chara", "nei", "না", "নেই", "নয়", "ছাড়া", "নাই"],
    "so": ["ma", "maya", "ma jiro", "ma qabo", "aan", "waxba", "ma hayo"],
    "ro": ["nu", "nici", "fara", "n-am", "nu am", "deloc", "nimic"],
    "en": ["no", "not", "dont", "don't", "doesnt", "doesn't", "denies", "denied", "without", "never", "didnt", "didn't", "free of", "negative", "none", "no pain"]
}

# ============================================================
# DURATION CONVERTERS
# ============================================================
DURATION_PATTERNS = [
    (r"(\d+)\s*(?:naalaga|naatkalaga|naala|naatkkala)", r"for \1 days"),
    (r"(?:oru|1)\s*(?:naalaga|naala)", "for 1 day"),
    (r"(?:rendu|2)\s*(?:naalaga|naala)", "for 2 days"),
    (r"(?:moonu|3)\s*(?:naalaga|naala)", "for 3 days"),
    (r"(?:naalu|4)\s*(?:naalaga|naala)", "for 4 days"),
    (r"(?:anji|5)\s*(?:naalaga|naala)", "for 5 days"),
    (r"(\d+)\s*(?:vaaramaga|vaarama)", r"for \1 weeks"),
    (r"(\d+)\s*(?:maasamaga|maasama)", r"for \1 months"),
    (r"(\d+)\s*(?:mani nerama|maninerama)", r"for \1 hours"),

    (r"(\d+)\s*(?:din se|dino se|din)", r"for \1 days"),
    (r"(?:ek|1)\s*din se", "for 1 day"),
    (r"(?:do|2)\s*din se", "for 2 days"),
    (r"(?:teen|3)\s*din se", "for 3 days"),
    (r"(?:char|4)\s*din se", "for 4 days"),
    (r"(\d+)\s*(?:hafte se|hafto se)", r"for \1 weeks"),
    (r"(\d+)\s*(?:mahine se|mahino se)", r"for \1 months"),

    (r"(\d+)\s*(?:divasamayi|divasamaayi|naalayi)", r"for \1 days"),
    (r"od\s*(\d+)\s*dni", r"for \1 days"),
    (r"(?:min|sarli)\s*(\d+)\s*(?:ayam|yom)", r"for \1 days"),
    (r"(\d+)\s*(?:din say|din se)", r"for \1 days"),
    (r"(\d+)\s*(?:din dhore|din jabot)", r"for \1 days"),
    (r"(\d+)\s*(?:maalmood|cisho)", r"for \1 days"),
    (r"de\s*(\d+)\s*zile", r"for \1 days"),
]

# ============================================================
# COMPREHENSIVE CLINICAL SYMPTOM REGISTRY (ALL 9 LANGUAGES)
# Explicit specific anatomical phrases included with phonetic typos
# ============================================================
MULTI_LANG_SYMPTOMS = {
    "chest pain": {
        "english": "chest pain",
        "ta": ("நெஞ்சு வலி", ["nenji vali", "nenju vali", "nenjil vali", "nenjula vali", "enji vali", "enju vali", "maar vali", "நெஞ்சு வலி", "நெஞ்சில் வலி"]),
        "hi": ("सीने में दर्द", ["seene mein dard", "chest mein dard", "chhati mein dard", "seene me dard", "sene me dard", "sine mein dard", "सीने में दर्द"]),
        "ml": ("നെഞ്ചുവേദന", ["nenjil vali", "nenju vali", "nenjile vedana", "നെഞ്ചുവേദന", "നെഞ്ചിൽ വേദന"]),
        "pl": ("ból w klatce piersiowej", ["bol w klatce piersiowej", "bol klatki piersiowej", "bol klatki", "bol w klatce", "pieczenie w klatce"]),
        "ar": ("ألم في الصدر", ["alam fi al sadr", "alam fi sadr", "alam sedr", "wagah sedr", "وجع في الصدر", "ألم في الصدر"]),
        "ur": ("سینے میں درد", ["seene mein dard", "seene me dard", "dil mein dard", "سینے میں درد"]),
        "bn": ("বুকে ব্যথা", ["buke betha", "buke byatha", "buke batha", "বুকে ব্যথা"]),
        "so": ("xanuunka laabta", ["xanuun laabta", "xanuunka laabta", "laab xanuun"]),
        "ro": ("durere în piept", ["durere in piept", "durere în piept", "dureri in piept"])
    },
    "headache": {
        "english": "headache",
        "ta": ("தலைவலி", ["thalai vali", "thala vali", "thalavali", "thalai valikuthu", "தலைவலி", "தலை வலிக்கிறது"]),
        "hi": ("सिरदर्द", ["sar dard", "sir dard", "sar me dard", "sir me dard", "sar dard hai", "सिरदर्द", "सिर में दर्द"]),
        "ml": ("തലവേദന", ["thalavedana", "thalavalikkunnu", "thala vedana", "തലവേദന"]),
        "pl": ("ból głowy", ["bol glowy", "boli mnie glowa", "bol glowa"]),
        "ar": ("صداع", ["suda", "alam fi al ras", "alam rasi", "rasi yowjaani", "صداع", "ألم في الرأس"]),
        "ur": ("سر درد", ["sar dard", "sir mein dard", "sar me dard", "سر درد"]),
        "bn": ("মাথা ব্যথা", ["matha betha", "matha byatha", "matha batha", "মাথা ব্যথা"]),
        "so": ("madax xanuun", ["madax xanuun", "madax xanoon"]),
        "ro": ("durere de cap", ["durere de cap", "ma doare capul", "dureri de cap"])
    },
    "stomach pain": {
        "english": "stomach pain",
        "ta": ("வயிற்று வலி", ["vayiru vali", "vathiru vali", "vayaru vali", "vayiru valikuthu", "வயிற்று வலி"]),
        "hi": ("पेट दर्द", ["pet dard", "pet me dard", "pet mein dard", "पेट में दर्द", "पेट दर्द"]),
        "ml": ("വയറുവേദന", ["vayaruvathana", "vayaril vali", "vayar vedana", "വയറുവേദന"]),
        "pl": ("ból brzucha", ["bol brzucha", "boli mnie brzuch"]),
        "ar": ("ألم في المعدة", ["alam fi al batan", "alam fi al meeda", "batni tuwjaani", "ألم في المعدة", "وجع بطن"]),
        "ur": ("پیٹ میں درد", ["pet mein dard", "pait dard", "پیٹ میں درد"]),
        "bn": ("পেটে ব্যথা", ["pete betha", "pet byatha", "pet betha", "পেটে ব্যথা"]),
        "so": ("calool xanuun", ["xanuun calool", "calool xanuun"]),
        "ro": ("durere de stomac", ["durere de stomac", "ma doare stomacul", "durere abdominala"])
    },
    "back pain": {
        "english": "back pain",
        "ta": ("முதுகு வலி", ["muthugu vali", "mudhugu vali", "iduppu vali", "முதுகு வலி"]),
        "hi": ("पीठ दर्द", ["kamar dard", "peeth dard", "peeth mein dard", "kamar mein dard", "पीठ में दर्द"]),
        "ml": ("നടുവേദന", ["naduvedana", "puram vedana", "നടുവേദന"]),
        "pl": ("ból pleców", ["bol plecow", "bola mnie plecy"]),
        "ar": ("ألم في الظهر", ["alam fi al dhahr", "alam dhahr", "ألم في الظهر"]),
        "ur": ("کمر درد", ["kamar dard", "peeth mein dard", "کمر میں درد"]),
        "bn": ("পিঠে ব্যথা", ["pithe betha", "komor betha", "পিঠে ব্যথা"]),
        "so": ("dhabar xanuun", ["dhabar xanuun"]),
        "ro": ("durere de spate", ["durere de spate", "ma doare spatele"])
    },
    "throat pain": {
        "english": "sore throat",
        "ta": ("தொண்டை வலி", ["thondai vali", "thonda vali", "தொண்டை வலி"]),
        "hi": ("गले में दर्द", ["gale mein dard", "gala kharab", "gale me dard", "गले में दर्द"]),
        "ml": ("തണ്ടവേദന", ["thondavedana", "തൊണ്ടവേദന"]),
        "pl": ("ból gardła", ["bol gardla", "boli mnie gardlo"]),
        "ar": ("ألم في الحلق", ["alam fi al halq", "alam halq", "ألم في الحلق"]),
        "ur": ("گلے میں درد", ["galay mein dard", "gala kharab", "گلے میں درد"]),
        "bn": ("গলায় ব্যথা", ["golar betha", "gola betha", "গলায় ব্যথা"]),
        "so": ("cunaha xanuun", ["cunaha xanuun"]),
        "ro": ("durere în gât", ["durere in gat", "durere în gât", "ma doare in gat"])
    },
    "leg pain": {
        "english": "leg pain",
        "ta": ("கால் வலி", ["kaal vali", "kaalu vali", "கால் வலி"]),
        "hi": ("पैर में दर्द", ["pair dard", "taang mein dard", "pair mein dard", "पैर में दर्द"]),
        "ml": ("കാൽ വേദന", ["kaal vedana", "kaalu vedana", "കാൽ വേദന"]),
        "pl": ("ból nogi", ["bol nogi", "boli mnie noga"]),
        "ar": ("ألم في الساق", ["alam fi al saq", "alam rijli", "ألم في الساق"]),
        "ur": ("ٹانگ میں درد", ["taang mein dard", "paon mein dard", "ٹانگ میں درد"]),
        "bn": ("পায়ে ব্যথা", ["payer betha", "pa betha", "পায়ে ব্যথা"]),
        "so": ("lug xanuun", ["lug xanuun"]),
        "ro": ("durere de picior", ["durere de picior", "ma doare piciorul"])
    },
    "fever": {
        "english": "fever",
        "ta": ("காய்ச்சல்", ["kaichal", "jwaram", "udambu suudu", "kaachal", "காய்ச்சல்"]),
        "hi": ("बुखार", ["bukhar", "tap", "sarir garam", "bukhar hai", "बुखार"]),
        "ml": ("പനി", ["pani", "panind", "പനി"]),
        "pl": ("gorączka", ["goraczka", "mam temperature", "gorączka"]),
        "ar": ("حمى", ["humma", "sukhuna", "harara", "حمى"]),
        "ur": ("بخار", ["bukhar", "jism garam", "بخار"]),
        "bn": ("জ্বর", ["jhor", "jor", "shorir gorom", "জ্বর"]),
        "so": ("qandho", ["qandho", "qando"]),
        "ro": ("febră", ["febra", "am temperatura", "febră"])
    },
    "breathing difficulty": {
        "english": "difficulty breathing",
        "ta": ("மூச்சு திணறல்", ["moochu varadhu", "moochu pidikuthu", "moochu thinaral", "moochu vida mudiyala", "மூச்சு திணறல்", "மூச்சு விட முடியவில்லை"]),
        "hi": ("सांस लेने में तकलीफ", ["saans lene mein takleef", "saans nahi aa rahi", "dam ghut raha", "saans phoolna", "सांस लेने में तकलीफ"]),
        "ml": ("ശ്വാസതടസ്സം", ["shwasam muttunnu", "shwasam edukkal budhimuttu", "ശ്വാസം മുട്ടൽ", "ശ്വാസതടസ്സം"]),
        "pl": ("duszności", ["trudnosci z oddychaniem", "duszno mi", "brak powietrza"]),
        "ar": ("صعوبة في التنفس", ["dheeq tanfus", "diq f tanaffus", "mushkila bil nafas", "صعوبة في التنفس"]),
        "ur": ("سانس لینے میں دشواری", ["saans lene mein dushwari", "saans ruk rahi hai", "سانس لینے میں دشواری"]),
        "bn": ("শ্বাসকষ্ট", ["shwash nite koshto", "shwaskoshto", "dom bondho", "শ্বাস নিতে কষ্ট"]),
        "so": ("dhibaatada neefsashada", ["neefsasho dhib", "neefta igu dhegaysa"]),
        "ro": ("dificultăți de respirație", ["dificultate de respiratie", "lipsa de aer", "greu de respirat"])
    },
    "bleeding": {
        "english": "bleeding",
        "ta": ("இரத்தப்போக்கு", ["iratham varuthu", "ratham varuthu", "irathapokku", "இரத்தப்போக்கு"]),
        "hi": ("खून बहना", ["khoon nikal raha", "khoon beh raha", "khoon aa raha", "खून आ रहा है"]),
        "ml": ("രക്തസ്രാവം", ["raktham varunnu", "chora varunnu", "രക്തം വരുന്നു"]),
        "pl": ("krwawienie", ["krwawie", "duzo krwi", "krwotok"]),
        "ar": ("نزيف", ["nazif", "dam yanzif", "نزيف"]),
        "ur": ("خون بہنا", ["khoon beh raha hai", "خون بہہ رہا ہے"]),
        "bn": ("রক্তপাত", ["rokto porchhe", "rokto ber hochhe", "রক্ত পড়ছে"]),
        "so": ("dhiig bax", ["dhiig ayaa iga socda", "dhiig bax"]),
        "ro": ("sângerare", ["sangerez", "curge sange", "hemoragie"])
    },
    "dizziness": {
        "english": "dizziness",
        "ta": ("தலைசுற்றல்", ["thalai sutharuthu", "thala suthuthu", "mayakkam", "தலை சுற்றல்", "மயக்கம்"]),
        "hi": ("चक्कर आना", ["chakkar aa raha", "behosh", "chakkar", "चक्कर"]),
        "ml": ("തലകറക്കം", ["thalakarakkam", "bodhakshayam", "തലകറക്കം"]),
        "pl": ("zawroty głowy", ["kreci mi sie w glowie", "omdlenie", "zawroty glowy"]),
        "ar": ("دوخة", ["dayikh", "dawkha", "dawar", "دوار", "دوخة"]),
        "ur": ("چکر آنا", ["chakkar aa rahe hain", "chakkar", "چکر"]),
        "bn": ("মাথা ঘোরা", ["matha ghurche", "matha ghora", "মাথা ঘোরা"]),
        "so": ("dawakhaad", ["madhax wareeg", "dawakhaad"]),
        "ro": ("amețeală", ["ametit", "ameteli", "amețeală"])
    },
    # GENERIC FALLBACK - only matches if no specific anatomy was identified
    "pain": {
        "english": "pain",
        "ta": ("வலி", ["vali", "valikuthu", "valikirathu", "vali irukku", "நோவு", "வலி"]),
        "hi": ("दर्द", ["dard", "dard ho raha", "peeda", "दर्द"]),
        "ml": ("വേദന", ["vedana", "vedanayaanu", "valikunnu", "വേദന"]),
        "pl": ("ból", ["bol", "boli", "bole"]),
        "ar": ("ألم", ["alam", "waja", "wajah", "ألم", "وجع"]),
        "ur": ("درد", ["dard", "takleef", "درد"]),
        "bn": ("ব্যথা", ["betha", "byatha", "batha", "ব্যথা"]),
        "so": ("xanuun", ["xanuun", "dawaaf"]),
        "ro": ("durere", ["durere", "doare", "dureri"])
    }
}

# ============================================================
# DETERMINISTIC CANONICAL PATIENT TRANSLATIONS (ALL 9 LANGUAGES)
# Guarantees verified native clinical output without external API failures
# ============================================================
PATIENT_CANONICAL_RESPONSES = {
    "ta": {
        "chest pain": {
            "pos": ("I have chest pain", "எனக்கு நெஞ்சு வலி இருக்கிறது"),
            "neg": ("I do not have chest pain", "எனக்கு நெஞ்சு வலி இல்லை")
        },
        "headache": {
            "pos": ("I have a headache", "எனக்கு தலைவலி இருக்கிறது"),
            "neg": ("I do not have a headache", "எனக்கு தலைவலி இல்லை")
        },
        "stomach pain": {
            "pos": ("I have stomach pain", "எனக்கு வயிற்று வலி இருக்கிறது"),
            "neg": ("I do not have stomach pain", "எனக்கு வயிற்று வலி இல்லை")
        },
        "back pain": {
            "pos": ("I have back pain", "எனக்கு முதுகு வலி இருக்கிறது"),
            "neg": ("I do not have back pain", "எனக்கு முதுகு வலி இல்லை")
        },
        "throat pain": {
            "pos": ("I have a sore throat", "எனக்கு தொண்டை வலி இருக்கிறது"),
            "neg": ("I do not have a sore throat", "எனக்கு தொண்டை வலி இல்லை")
        },
        "leg pain": {
            "pos": ("I have leg pain", "எனக்கு கால் வலி இருக்கிறது"),
            "neg": ("I do not have leg pain", "எனக்கு கால் வலி இல்லை")
        },
        "fever": {
            "pos": ("I have a fever", "எனக்கு காய்ச்சல் இருக்கிறது"),
            "neg": ("I do not have a fever", "எனக்கு காய்ச்சல் இல்லை")
        },
        "breathing difficulty": {
            "pos": ("I have difficulty breathing", "எனக்கு மூச்சு விடுவதில் சிரமம் உள்ளது"),
            "neg": ("I do not have difficulty breathing", "எனக்கு மூச்சுத் திணறல் இல்லை")
        },
        "bleeding": {
            "pos": ("I am bleeding", "எனக்கு இரத்தப்போக்கு உள்ளது"),
            "neg": ("I am not bleeding", "எனக்கு இரத்தப்போக்கு இல்லை")
        },
        "dizziness": {
            "pos": ("I feel dizzy", "எனக்கு தலை சுற்றுகிறது"),
            "neg": ("I do not feel dizzy", "எனக்கு தலை சுற்றல் இல்லை")
        },
        "pain": {
            "pos": ("I have pain", "எனக்கு வலி இருக்கிறது"),
            "neg": ("I do not have pain", "எனக்கு வலி இல்லை")
        }
    },
    "hi": {
        "chest pain": {
            "pos": ("I have chest pain", "मुझे सीने में दर्द है"),
            "neg": ("I do not have chest pain", "मुझे सीने में दर्द नहीं है")
        },
        "headache": {
            "pos": ("I have a headache", "मुझे सिरदर्द है"),
            "neg": ("I do not have a headache", "मुझे सिरदर्द नहीं है")
        },
        "stomach pain": {
            "pos": ("I have stomach pain", "मुझे पेट में दर्द है"),
            "neg": ("I do not have stomach pain", "मुझे पेट में दर्द नहीं है")
        },
        "back pain": {
            "pos": ("I have back pain", "मुझे पीठ में दर्द है"),
            "neg": ("I do not have back pain", "मुझे पीठ में दर्द नहीं है")
        },
        "throat pain": {
            "pos": ("I have a sore throat", "मुझे गले में दर्द है"),
            "neg": ("I do not have a sore throat", "मुझे गले में दर्द नहीं है")
        },
        "leg pain": {
            "pos": ("I have leg pain", "मुझे पैर में दर्द है"),
            "neg": ("I do not have leg pain", "मुझे पैर में दर्द नहीं है")
        },
        "fever": {
            "pos": ("I have a fever", "मुझे बुखार है"),
            "neg": ("I do not have a fever", "मुझे बुखार नहीं है")
        },
        "breathing difficulty": {
            "pos": ("I have difficulty breathing", "मुझे सांस लेने में तकलीफ है"),
            "neg": ("I do not have difficulty breathing", "मुझे सांस लेने में कोई तकलीफ नहीं है")
        },
        "bleeding": {
            "pos": ("I am bleeding", "खून बह रहा है"),
            "neg": ("I am not bleeding", "खून नहीं बह रहा है")
        },
        "dizziness": {
            "pos": ("I feel dizzy", "मुझे चक्कर आ रहा है"),
            "neg": ("I do not feel dizzy", "मुझे चक्कर नहीं आ रहा है")
        },
        "pain": {
            "pos": ("I have pain", "मुझे दर्द हो रहा है"),
            "neg": ("I do not have pain", "मुझे दर्द नहीं है")
        }
    },
    "ml": {
        "chest pain": {
            "pos": ("I have chest pain", "എനിക്ക് നെഞ്ചുവേദനയുണ്ട്"),
            "neg": ("I do not have chest pain", "എനിക്ക് നെഞ്ചുവേദനയില്ല")
        },
        "headache": {
            "pos": ("I have a headache", "എനിക്ക് തലവേദനയുണ്ട്"),
            "neg": ("I do not have a headache", "എനിക്ക് തലവേദനയില്ല")
        },
        "stomach pain": {
            "pos": ("I have stomach pain", "എനിക്ക് വയറുവേദനയുണ്ട്"),
            "neg": ("I do not have stomach pain", "എനിക്ക് വയറുവേദനയില്ല")
        },
        "fever": {
            "pos": ("I have a fever", "എനിക്ക് പനിയുണ്ട്"),
            "neg": ("I do not have a fever", "എനിക്ക് പനിയില്ല")
        },
        "breathing difficulty": {
            "pos": ("I have difficulty breathing", "എനിക്ക് ശ്വാസതടസ്സമുണ്ട്"),
            "neg": ("I do not have difficulty breathing", "എനിക്ക് ശ്വാസതടസ്സമില്ല")
        },
        "pain": {
            "pos": ("I have pain", "എനിക്ക് വേദനയുണ്ട്"),
            "neg": ("I do not have pain", "എനിക്ക് വേദനയില്ല")
        }
    },
    "pl": {
        "chest pain": {
            "pos": ("I have chest pain", "Mam ból w klatce piersiowej"),
            "neg": ("I do not have chest pain", "Nie mam bólu w klatce piersiowej")
        },
        "headache": {
            "pos": ("I have a headache", "Boli mnie głowa"),
            "neg": ("I do not have a headache", "Nie boli mnie głowa")
        },
        "stomach pain": {
            "pos": ("I have stomach pain", "Mam ból brzucha"),
            "neg": ("I do not have stomach pain", "Nie mam bólu brzucha")
        },
        "fever": {
            "pos": ("I have a fever", "Mam gorączkę"),
            "neg": ("I do not have a fever", "Nie mam gorączki")
        },
        "breathing difficulty": {
            "pos": ("I have difficulty breathing", "Mam trudności z oddychaniem"),
            "neg": ("I do not have difficulty breathing", "Nie mam trudności z oddychaniem")
        },
        "pain": {
            "pos": ("I have pain", "Odczuwam ból"),
            "neg": ("I do not have pain", "Nie odczuwam bólu")
        }
    },
    "ar": {
        "chest pain": {
            "pos": ("I have chest pain", "أشعر بألم في الصدر"),
            "neg": ("I do not have chest pain", "لا أشعر بألم في الصدر")
        },
        "headache": {
            "pos": ("I have a headache", "أعاني من صداع"),
            "neg": ("I do not have a headache", "ليس لدي صداع")
        },
        "stomach pain": {
            "pos": ("I have stomach pain", "أعاني من ألم في المعدة"),
            "neg": ("I do not have stomach pain", "ليس لدي ألم في المعدة")
        },
        "fever": {
            "pos": ("I have a fever", "أعاني من الحمى"),
            "neg": ("I do not have a fever", "ليس لدي حمى")
        },
        "breathing difficulty": {
            "pos": ("I have difficulty breathing", "أواجه صعوبة في التنفس"),
            "neg": ("I do not have difficulty breathing", "لا أواجه صعوبة في التنفس")
        },
        "pain": {
            "pos": ("I have pain", "أشعر بالألم"),
            "neg": ("I do not have pain", "لا أشعر بأي ألم")
        }
    },
    "ur": {
        "chest pain": {
            "pos": ("I have chest pain", "میرے سینے میں درد ہے"),
            "neg": ("I do not have chest pain", "میرے سینے میں درد نہیں ہے")
        },
        "headache": {
            "pos": ("I have a headache", "میرے سر میں درد ہے"),
            "neg": ("I do not have a headache", "میرے سر میں درد نہیں ہے")
        },
        "stomach pain": {
            "pos": ("I have stomach pain", "میرے پیٹ میں درد ہے"),
            "neg": ("I do not have stomach pain", "میرے پیٹ میں درد نہیں ہے")
        },
        "fever": {
            "pos": ("I have a fever", "मुझे بخار ہے"),
            "neg": ("I do not have a fever", "مجھے بخار نہیں ہے")
        },
        "breathing difficulty": {
            "pos": ("I have difficulty breathing", "مجھے سانس لینے میں دشواری ہے"),
            "neg": ("I do not have difficulty breathing", "مجھے سانس لینے میں کوئی دشواری نہیں ہے")
        },
        "pain": {
            "pos": ("I have pain", "مجھے درد ہو رہا ہے"),
            "neg": ("I do not have pain", "مجھے کوئی درد نہیں ہے")
        }
    },
    "bn": {
        "chest pain": {
            "pos": ("I have chest pain", "আমার বুকে ব্যথা আছে"),
            "neg": ("I do not have chest pain", "আমার বুকে ব্যথা নেই")
        },
        "headache": {
            "pos": ("I have a headache", "আমার মাথা ব্যথা করছে"),
            "neg": ("I do not have a headache", "আমার মাথা ব্যথা নেই")
        },
        "stomach pain": {
            "pos": ("I have stomach pain", "আমার পেটে ব্যথা করছে"),
            "neg": ("I do not have stomach pain", "আমার পেটে ব্যথা নেই")
        },
        "fever": {
            "pos": ("I have a fever", "আমার জ্বর আছে"),
            "neg": ("I do not have a fever", "আমার জ্বর নেই")
        },
        "breathing difficulty": {
            "pos": ("I have difficulty breathing", "আমার শ্বাস নিতে কষ্ট হচ্ছে"),
            "neg": ("I do not have difficulty breathing", "আমার শ্বাসকষ্ট নেই")
        },
        "pain": {
            "pos": ("I have pain", "আমার ব্যথা আছে"),
            "neg": ("I do not have pain", "আমার কোনো ব্যথা নেই")
        }
    },
    "so": {
        "chest pain": {
            "pos": ("I have chest pain", "Waxaan dareemayaa xanuunka laabta"),
            "neg": ("I do not have chest pain", "Ma qabo wax xanuun laabta ah")
        },
        "headache": {
            "pos": ("I have a headache", "Waxaan qabaa madax xanuun"),
            "neg": ("I do not have a headache", "Ma qabo madax xanuun")
        },
        "stomach pain": {
            "pos": ("I have stomach pain", "Waxaan qabaa calool xanuun"),
            "neg": ("I do not have stomach pain", "Ma qabo calool xanuun")
        },
        "fever": {
            "pos": ("I have a fever", "Waxaan qabaa qandho"),
            "neg": ("I do not have a fever", "Ma qabo wax qandho ah")
        },
        "breathing difficulty": {
            "pos": ("I have difficulty breathing", "Waxaan dhib ku qabaa neefsashada"),
            "neg": ("I do not have difficulty breathing", "Dhib kuma qabo neefsashada")
        },
        "pain": {
            "pos": ("I have pain", "Xanuun ayaan dareemayaa"),
            "neg": ("I do not have pain", "Wax xanuun ah ma dareemayo")
        }
    },
    "ro": {
        "chest pain": {
            "pos": ("I have chest pain", "Am dureri în piept"),
            "neg": ("I do not have chest pain", "Nu am dureri în piept")
        },
        "headache": {
            "pos": ("I have a headache", "Am o durere de cap"),
            "neg": ("I do not have a headache", "Nu am dureri de cap")
        },
        "stomach pain": {
            "pos": ("I have stomach pain", "Am dureri de stomac"),
            "neg": ("I do not have stomach pain", "Nu am dureri de stomac")
        },
        "fever": {
            "pos": ("I have a fever", "Am febră"),
            "neg": ("I do not have a fever", "Nu am febră")
        },
        "breathing difficulty": {
            "pos": ("I have difficulty breathing", "Am dificultăți de respirație"),
            "neg": ("I do not have difficulty breathing", "Nu am dificultăți de respirație")
        },
        "pain": {
            "pos": ("I have pain", "Am o durere"),
            "neg": ("I do not have pain", "Nu am nicio durere")
        }
    }
}

# ============================================================
# TRIAGE RED FLAGS CONFIGURATION
# ============================================================
URGENT_SYMPTOMS_CONFIG = {
    "chest pain": ["chest pain", "heart pain", "heart attack", "crushing chest", "tight chest", "nenji vali", "seene mein dard", "bol klatki", "ألم في الصدر", "سینے میں درد", "বুকে ব্যথা", "xanuun laabta", "durere in piept", "நெஞ்சு வலி"],
    "breathing difficulty": ["can't breathe", "cant breathe", "difficulty breathing", "shortness of breath", "moochu varadhu", "moochu pidikuthu", "saans nahi", "saans lene mein takleef", "shwasam muttunnu", "duszno", "صعوبة في التنفس", "سانس لینے میں دشواری", "শ্বাস নিতে কষ্ট", "neefsasho dhib", "dificultate de respiratie", "மூச்சு திணறல்"],
    "bleeding": ["bleeding", "severe blood", "iratham", "khoon", "krwawienie", "نزيف", "خون", "রক্তপাত", "dhiig", "sângerare", "இரத்தப்போக்கு"],
    "unconscious": ["unconscious", "passed out", "collapsed", "fainted", "mayakkam", "behosh", "omdlenie", "إغماء", "بے ہوش", "অজ্ঞান", "miyir beel", "leșin", "மயக்கம்"]
}

# ============================================================
# STAFF QUESTION SYNTHESIZER
# ============================================================
CLINICAL_STAFF_SYNTHESIZER = {
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
    "HOW_LONG_HEADACHE": {
        "ta": "உங்களுக்கு எவ்வளவு காலமாக தலைவலி உள்ளது?",
        "hi": "आपको सिरदर्द कब से है?",
        "ml": "നിങ്ങൾക്ക് എത്ര നാളായി തലവേദനയുണ്ട്?",
        "pl": "Od jak dawna boli Pana/Panią głowa?",
        "ar": "منذ متى وأنت تعاني من الصداع؟",
        "ur": "آپ کو سر درد کب سے ہے؟",
        "bn": "আপনার কতদিন ধরে মাথা ব্যথা হচ্ছে?",
        "so": "Muddo intee leeg ayaad madax xanuunka qabtaa?",
        "ro": "De cât timp aveți această durere de cap?"
    },
    "HOW_LONG_FEVER": {
        "ta": "உங்களுக்கு எவ்வளவு காலமாக காய்ச்சல் உள்ளது?",
        "hi": "आपको बुखार कब से है?",
        "ml": "നിങ്ങൾക്ക് എത്ര നാളായി പനിയുണ്ട്?",
        "pl": "Od jak dawna ma Pan/Pani gorączkę?",
        "ar": "منذ متى وأنت تعاني من الحمى؟",
        "ur": "آپ کو بخار کب سے ہے؟",
        "bn": "আপনার কতদিন ধরে জ্বর আছে?",
        "so": "Muddo intee leeg ayaad qandhada qabtaa?",
        "ro": "De cât timp aveți febră?"
    },
    "HOW_LONG_BREATHING": {
        "ta": "உங்களுக்கு எவ்வளவு காலமாக மூச்சுத் திணறல் உள்ளது?",
        "hi": "आपको सांस लेने में तकलीफ कब से है?",
        "ml": "നിങ്ങൾക്ക് എത്ര നാളായി ശ്വാസതടസ്സമുണ്ട്?",
        "pl": "Od jak dawna ma Pan/Pani trudności z oddychaniem?",
        "ar": "منذ متى وأنت تعاني من صعوبة في التنفس؟",
        "ur": "آپ کو سانس لینے میں دشواری کب سے ہے؟",
        "bn": "আপনার কতদিন ধরে শ্বাস নিতে কষ্ট হচ্ছে?",
        "so": "Muddo intee leeg ayaad dhibaatada neefsashada qabtaa?",
        "ro": "De cât timp aveți dificultăți de respirație?"
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
    }
}

# ============================================================
# GUIDED CLINICAL PROMPTS
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
        "How long do you have pain?",
        "How long do you have chest pain?",
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
# LONGEST-FIRST SYMPTOM PARSER (FIXES GREEDY OVERLAP BUG)
# ============================================================
def extract_symptom(text, lang_code):
    """
    Scans text against all known symptom aliases across languages.
    CRITICAL: Evaluates aliases sorted by length DESCENDING so specific phrases
    like 'nenji vali' or 'thalai vali' match before generic single tokens like 'vali' or 'dard'.
    """
    clean_text = re.sub(r'[^\w\s]', ' ', text.lower()).strip()
    norm = f" {' '.join(clean_text.split())} "

    # Build candidates: (alias, symptom_key, english_name, native_name)
    candidates = []
    for sym_key, sym_data in MULTI_LANG_SYMPTOMS.items():
        if lang_code in sym_data:
            native_label, aliases = sym_data[lang_code]
            for alias in aliases:
                candidates.append((alias.lower().strip(), sym_key, sym_data["english"], native_label))
        
        # Universal English aliases
        candidates.append((sym_data["english"].lower().strip(), sym_key, sym_data["english"], sym_data.get(lang_code, (sym_data["english"], []))[0]))

    # Sort candidates by length in descending order (longest match first)
    candidates.sort(key=lambda x: len(x[0]), reverse=True)

    for alias, sym_key, english_name, native_label in candidates:
        if f" {alias} " in norm or norm.strip().startswith(alias) or norm.strip().endswith(alias):
            return sym_key, english_name, native_label

    # Fallback to direct substring search for remaining items
    for alias, sym_key, english_name, native_label in candidates:
        if alias in norm:
            return sym_key, english_name, native_label

    return None, None, None

def synthesize_staff_question(text, lang_code):
    """
    Analyzes staff inquiries and deterministically returns verified translations
    for all 9 languages without relying on external web APIs.
    """
    clean = re.sub(r'[^\w\s]', '', text.lower()).strip()

    # DURATION
    if any(q in clean for q in ["how long", "since when", "how many days", "when did"]) and "pain" in clean:
        if "chest" in clean:
            return CLINICAL_STAFF_SYNTHESIZER["HOW_LONG_CHEST_PAIN"].get(lang_code)
        if "head" in clean:
            return CLINICAL_STAFF_SYNTHESIZER["HOW_LONG_HEADACHE"].get(lang_code)
        return CLINICAL_STAFF_SYNTHESIZER["HOW_LONG_PAIN"].get(lang_code)

    if any(q in clean for q in ["how long", "since when", "when did"]) and ("fever" in clean or "temperature" in clean):
        return CLINICAL_STAFF_SYNTHESIZER["HOW_LONG_FEVER"].get(lang_code)

    if any(q in clean for q in ["how long", "since when", "when did"]) and ("breath" in clean or "breathing" in clean):
        return CLINICAL_STAFF_SYNTHESIZER["HOW_LONG_BREATHING"].get(lang_code)

    if clean in ["how long", "how long have you had this", "how long has this been", "how long is this"]:
        return CLINICAL_STAFF_SYNTHESIZER["HOW_LONG_GENERAL"].get(lang_code)

    # LOCATION
    if any(q in clean for q in ["where is", "where does it hurt", "where do you have"]):
        return CLINICAL_STAFF_SYNTHESIZER["WHERE_IS_PAIN"].get(lang_code)

    # PRESENCE
    if any(q in clean for q in ["do you have", "are you having", "is there", "are you feeling"]):
        if "chest" in clean:
            return CLINICAL_STAFF_SYNTHESIZER["DO_YOU_HAVE_CHEST_PAIN"].get(lang_code)
        if "fever" in clean or "temperature" in clean:
            return CLINICAL_STAFF_SYNTHESIZER["DO_YOU_HAVE_FEVER"].get(lang_code)
        if "breath" in clean or "breathing" in clean:
            return CLINICAL_STAFF_SYNTHESIZER["DO_YOU_HAVE_BREATHING"].get(lang_code)
        if "pain" in clean:
            return CLINICAL_STAFF_SYNTHESIZER["DO_YOU_HAVE_PAIN"].get(lang_code)

    return None
