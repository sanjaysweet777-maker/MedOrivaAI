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
    "ta": ["aam", "aama", "aamaam", "seri", "kandippa", "ஆம்", "ஆமாம்", "சரி"],
    "hi": ["haan", "ji haan", "theek hai", "sahi", "हाँ", "जी हाँ", "ठीक है"],
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
# TIME & DURATION CONVERTERS
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
    (r"(\d+)\s*(?:ghante se|ghanto se)", r"for \1 hours"),

    (r"(\d+)\s*(?:divasamayi|divasamaayi|naalayi)", r"for \1 days"),
    (r"(\d+)\s*(?:aazhchayayi|masamayi)", r"for \1 weeks"),

    (r"od\s*(\d+)\s*dni", r"for \1 days"),
    (r"od\s*(\d+)\s*tygodni", r"for \1 weeks"),

    (r"(?:min|sarli|baali)\s*(\d+)\s*(?:ayam|tiyam|yom)", r"for \1 days"),
    (r"(\d+)\s*(?:din say|din se|dino se)", r"for \1 days"),
    (r"(\d+)\s*(?:din dhore|din jabot)", r"for \1 days"),
    (r"(\d+)\s*(?:maalmood|cisho)", r"for \1 days"),
    (r"de\s*(\d+)\s*zile", r"for \1 days"),
]

# ============================================================
# COMPREHENSIVE CLINICAL SYMPTOM REGISTRY (ALL 9 LANGUAGES)
# ============================================================
MULTI_LANG_SYMPTOMS = {
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
    },
    "chest pain": {
        "english": "chest pain",
        "ta": ("நெஞ்சு வலி", ["nenji vali", "nenju vali", "nenjil vali", "nenjula vali", "maar vali", "நெஞ்சு வலி", "நெஞ்சில் வலி"]),
        "hi": ("सीने में दर्द", ["seene mein dard", "chest mein dard", "chhati mein dard", "seene me dard", "सीने में दर्द"]),
        "ml": ("നെഞ്ചുവേദന", ["nenjil vali", "nenju vali", "nenjile vedana", "നെഞ്ചുവേദന", "നെഞ്ചിൽ വേദന"]),
        "pl": ("ból w klatce piersiowej", ["bol klatki", "bol w klatce", "pieczenie w klatce"]),
        "ar": ("ألم في الصدر", ["alam fi al sadr", "alam sedr", "wagah sedr", "ألم في الصدر"]),
        "ur": ("سینے میں درد", ["seene mein dard", "seene me dard", "dil mein dard", "سینے میں درد"]),
        "bn": ("বুকে ব্যথা", ["buke betha", "buke byatha", "buke batha", "বুকে ব্যথা"]),
        "so": ("xanuunka laabta", ["xanuun laabta", "laab xanuun"]),
        "ro": ("durere în piept", ["durere in piept", "dureri in piept"])
    },
    "headache": {
        "english": "headache",
        "ta": ("தலைவலி", ["thalai vali", "thala vali", "thalavali", "தலைவலி"]),
        "hi": ("सिरदर्द", ["sar dard", "sir dard", "sar me dard", "सिरदर्द"]),
        "ml": ("തലവേദന", ["thalavedana", "thalavalikkunnu", "തലവേദന"]),
        "pl": ("ból głowy", ["bol glowy", "boli mnie glowa"]),
        "ar": ("صداع", ["suda", "rasi yowjaani", "صداع"]),
        "ur": ("سر درد", ["sar dard", "sir mein dard", "سر درد"]),
        "bn": ("মাথা ব্যথা", ["matha betha", "matha byatha", "মাথা ব্যথা"]),
        "so": ("madax xanuun", ["madax xanuun"]),
        "ro": ("durere de cap", ["durere de cap", "ma doare capul"])
    },
    "fever": {
        "english": "fever",
        "ta": ("காய்ச்சல்", ["kaichal", "jwaram", "udambu suudu", "காய்ச்சல்"]),
        "hi": ("बुखार", ["bukhar", "tap", "sarir garam", "बुखार"]),
        "ml": ("പനി", ["pani", "panind", "പനി"]),
        "pl": ("gorączka", ["goraczka", "mam temperature"]),
        "ar": ("حمى", ["humma", "sukhuna", "harara", "حمى"]),
        "ur": ("بخار", ["bukhar", "jism garam", "بخار"]),
        "bn": ("জ্বর", ["jhor", "jor", "shorir gorom", "জ্বর"]),
        "so": ("qandho", ["qandho"]),
        "ro": ("febră", ["febra", "am temperatura"])
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
    "stomach pain": {
        "english": "stomach pain",
        "ta": ("வயிற்று வலி", ["vayiru vali", "vathiru valikuthu", "வயிற்று வலி"]),
        "hi": ("पेट दर्द", ["pet dard", "pet me dard", "पेट में दर्द"]),
        "ml": ("വയറുവേദന", ["vayaruvathana", "vayaril vali", "വയറുവേദന"]),
        "pl": ("ból brzucha", ["bol brzucha", "boli mnie brzuch"]),
        "ar": ("ألم في المعدة", ["alam fi al meeda", "batni tuwjaani", "ألم في المعدة"]),
        "ur": ("پیٹ میں درد", ["pet mein dard", "پیٹ میں درد"]),
        "bn": ("পেটে ব্যথা", ["pete betha", "pet betha", "পেটে ব্যথা"]),
        "so": ("xanuun calool", ["calool xanuun"]),
        "ro": ("durere de stomac", ["durere de stomac", "ma doare stomacul"])
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
        "ta": ("தலைசுற்றல்", ["thalai sutharuthu", "mayakkam", "தலை சுற்றல்", "மயக்கம்"]),
        "hi": ("चक्कर आना", ["chakkar aa raha", "behosh", "चक्कर"]),
        "ml": ("തലകറക്കം", ["thalakarakkam", "bodhakshayam", "തലകറക്കം"]),
        "pl": ("zawroty głowy", ["kreci mi sie w glowie", "omdlenie"]),
        "ar": ("دوخة", ["dayikh", "dawkha", "دوار"]),
        "ur": ("چکر آنا", ["chakkar aa rahe hain", "چکر"]),
        "bn": ("মাথা ঘোরা", ["matha ghurche", "মাথা ঘোরা"]),
        "so": ("dawakhaad", ["madhax wareeg"]),
        "ro": ("amețeală", ["ametit", "ameteli"])
    },
    "cough": {
        "english": "cough",
        "ta": ("இருமல்", ["irumal", "irumal irukku", "இருமல்"]),
        "hi": ("खांसी", ["khansi", "khasi", "खांसी"]),
        "ml": ("ചുമ", ["chuma", "chumakkunnu", "ചുമ"]),
        "pl": ("kaszel", ["kaszel", "kaszle"]),
        "ar": ("سعال", ["koha", "kuhha", "sual", "سعال"]),
        "ur": ("کھانسی", ["khansi", "کھانسی"]),
        "bn": ("কাশি", ["kashi", "কাশি"]),
        "so": ("qufac", ["qufac"]),
        "ro": ("tuse", ["tuse", "tusesc"])
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
# CLINICAL QUESTION SYNTHESIZER (STAFF INTENT -> 9 LANGUAGES)
# Guarantees questions NEVER fall back to untranslated English
# ============================================================
CLINICAL_STAFF_SYNTHESIZER = {
    # 1. DURATION: "how long do you have [symptom]?" / "how long have you had this?"
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
    "HOW_LONG_STOMACH": {
        "ta": "உங்களுக்கு எவ்வளவு காலமாக வயிற்று வலி உள்ளது?",
        "hi": "आपको पेट में दर्द कब से है?",
        "ml": "നിങ്ങൾക്ക് എത്ര നാളായി വയറുവേദനയുണ്ട്?",
        "pl": "Od jak dawna ma Pan/Pani ból brzucha?",
        "ar": "منذ متى وأنت تعاني من ألم في المعدة؟",
        "ur": "آپ کو پیٹ میں درد کب سے ہے؟",
        "bn": "আপনার কতদিন ধরে পেটে ব্যথা হচ্ছে?",
        "so": "Muddo intee leeg ayaad calool xanuunka qabtaa?",
        "ro": "De cât timp aveți dureri de stomac?"
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

    # 2. LOCATION: "where is your pain?" / "where does it hurt?"
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

    # 3. PRESENCE: "do you have [symptom]?"
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
    },
    "DO_YOU_HAVE_DIZZINESS": {
        "ta": "நீங்கள் தலை சுற்றல் அல்லது மயக்கத்தை உணர்கிறீர்களா?",
        "hi": "क्या आपको चक्कर या बेहोशी महसूस हो रही है?",
        "ml": "നിങ്ങൾക്ക് തലകറക്കമോ ബോധക്ഷയമോ തോന്നുന്നുണ്ടോ?",
        "pl": "Czy czuje Pan/Pani zawroty głowy lub omdlenia?",
        "ar": "هل تشعر بالدوار أو الإغماء؟",
        "ur": "کیا آپ کو چکر یا بے ہوشی محسوس ہو رہی ہے؟",
        "bn": "আপনার কি মাথা ঘোরা বা অজ্ঞান হওয়ার অনুভূতি হচ্ছে?",
        "so": "Ma dareemaysaa miyir beel ama dawakhaad?",
        "ro": "Vă simțiți amețit sau leșinat?"
    },
    "DO_YOU_HAVE_BLEEDING": {
        "ta": "ஏதேனும் இரத்தப்போக்கு உள்ளதா?",
        "hi": "क्या कोई रक्तस्राव या खून बह रहा है?",
        "ml": "എവിടെയെങ്കിലും രക്തസ്രാവം ഉണ്ടോ?",
        "pl": "Czy występuje krwawienie?",
        "ar": "هل هناك أي نزيف؟",
        "ur": "کیا کہیں سے خون بہہ رہا ہے؟",
        "bn": "কোথাও কি রক্তপাত হচ্ছে?",
        "so": "Dhiig ma kaa socdaa?",
        "ro": "Aveți vreo sângerare?"
    },

    # 4. SEVERITY / SCALE: "on a scale of 1 to 10..."
    "SEVERITY_SCALE": {
        "ta": "1 முதல் 10 வரை, உங்கள் வலி எவ்வளவு தீவிரமாக உள்ளது?",
        "hi": "1 से 10 के पैमाने पर, आपका दर्द कितना गंभीर है?",
        "ml": "1 മുതൽ 10 വരെയുള്ള അളവിൽ നിങ്ങളുടെ വേദന എത്രത്തോളമുണ്ട്?",
        "pl": "W skali od 1 do 10, jak silny jest ten ból?",
        "ar": "على مقياس من 1 إلى 10، ما مدى شدة ألمك؟",
        "ur": "1 سے 10 کے پیمانے پر آپ کا درد کتنا شدید ہے؟",
        "bn": "১ থেকে ১০ এর স্কেলে আপনার ব্যথা কতটা তীব্র?",
        "so": "Qiyaastii 1 ilaa 10, intee in le'eg ayuu xanuunkaagu daran yahay?",
        "ro": "Pe o scară de la 1 la 10, cât de severă este durerea?"
    },

    # 5. ALLERGIES & MEDS
    "ALLERGIES_QUERY": {
        "ta": "உங்களுக்கு ஏதேனும் மருந்து ஒவ்வாமை உள்ளதா?",
        "hi": "क्या आपको किसी दवा से कोई एलर्जी है?",
        "ml": "നിങ്ങൾക്ക് എന്തെങ്കിലും അലർജി ഉണ്ടോ?",
        "pl": "Czy ma Pan/Pani jakieś alergie na leki?",
        "ar": "هل لديك أي حساسية تجاه أي أدوية؟",
        "ur": "کیا آپ کو کسی دوا سے کوئی الرجی ہے؟",
        "bn": "আপনার কি কোনো অ্যালার্জি আছে?",
        "so": "Ma qabtaa wax xasaasiyad ah?",
        "ro": "Aveți alergii la vreun medicament?"
    },
    "MEDICATION_QUERY": {
        "ta": "நீங்கள் தற்போது ஏதேனும் மருந்து உட்கொள்கிறீர்களா?",
        "hi": "क्या आप वर्तमान में कोई दवा ले रहे हैं?",
        "ml": "നിങ്ങൾ നിലവിൽ എന്തെങ്കിലും മരുന്ന് കഴിക്കുന്നുണ്ടോ?",
        "pl": "Czy przyjmuje Pan/Pani obecnie jakieś leki?",
        "ar": "هل تتناول أي أدوية بانتظام حالياً؟",
        "ur": "کیا آپ اس وقت کوئی دوا لے رہے ہیں؟",
        "bn": "আপনি কি বর্তমানে কোনো ওষুধ খাচ্ছেন?",
        "so": "Ma qaadataa wax daawo ah hadda?",
        "ro": "Luați în prezent vreun tratament medicamentos?"
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
# EXACT PHRASEBOOK FOR COMMON RECEPTION UTTERANCES
# ============================================================
CLINICAL_DICTIONARY = {
    "ta": {
        "good morning how can i help you": ("Good morning. How can I help you?", "காலை வணக்கம். நான் உங்களுக்கு எப்படி உதவ முடியும்?", False, None),
        "do you have an appointment": ("Do you have an appointment?", "உங்களுக்கு முன்பதிவு உள்ளதா?", False, None),
        "can i take your name and date of birth": ("Can I take your name and date of birth?", "உங்கள் பெயரையும் பிறந்த தேதியையும் சொல்ல முடியுமா?", False, None),
        "please take a seat the doctor will see you shortly": ("Please take a seat. The doctor will see you shortly.", "தயவு செய்து உட்காருங்கள். மருத்துவர் விரைவில் உங்களை பார்ப்பார்.", False, None),
        "do you need any assistance": ("Do you need any assistance?", "உங்களுக்கு உதவி தேவையா?", False, None),
        "is this your first visit": ("Is this your first visit?", "இது உங்கள் முதல் வருகையா?", False, None),
        "do you have your nhs number": ("Do you have your NHS number?", "உங்களிடம் என்.எச்.எஸ் எண் உள்ளதா?", False, None),
        "please wait the doctor will call you": ("Please wait. The doctor will call you.", "தயவு செய்து காத்திருக்கவும். மருத்துவர் உங்களை அழைப்பார்.", False, None),
        "the doctor will see you now": ("The doctor will see you now.", "மருத்துவர் இப்போது உங்களை பார்ப்பார்.", False, None),
        "your appointment is confirmed": ("Your appointment is confirmed.", "உங்கள் முன்பதிவு உறுதி செய்யப்பட்டுள்ளது.", False, None),
        "please fill in this form": ("Please fill in this form.", "தயவு செய்து இந்த படிவத்தை நிரப்பவும்.", False, None),
    },
    "hi": {
        "good morning how can i help you": ("Good morning. How can I help you?", "सुप्रभात। मैं आपकी कैसे मदद कर सकता हूँ?", False, None),
        "do you have an appointment": ("Do you have an appointment?", "क्या आपका कोई अपॉइंटमेंट है?", False, None),
        "please take a seat the doctor will see you shortly": ("Please take a seat. The doctor will see you shortly.", "कृपया बैठ जाइए। डॉक्टर जल्द ही आपसे मिलेंगे।", False, None),
        "please wait the doctor will call you": ("Please wait. The doctor will call you.", "कृपया प्रतीक्षा करें। डॉक्टर आपको बुलाएंगे।", False, None),
        "the doctor will see you now": ("The doctor will see you now.", "डॉक्टर अब आपसे मिलेंगे।", False, None),
    },
    "ml": {
        "good morning how can i help you": ("Good morning. How can I help you?", "സുപ്രഭാതം. എനിക്ക് നിങ്ങളെ എങ്ങനെ സഹായിക്കാനാകും?", False, None),
        "do you have an appointment": ("Do you have an appointment?", "നിങ്ങൾക്ക് ഒരു അപ്പോയിന്റ്മെന്റ് ഉണ്ടോ?", False, None),
    },
    "pl": {
        "good morning how can i help you": ("Good morning. How can I help you?", "Dzień dobry. W czym mogę pomóc?", False, None),
        "do you have an appointment": ("Do you have an appointment?", "Czy ma Pan/Pani umówioną wizytę?", False, None),
    },
    "ar": {
        "good morning how can i help you": ("Good morning. How can I help you?", "صباح الخير. كيف يمكنني مساعدتك؟", False, None),
        "do you have an appointment": ("Do you have an appointment?", "هل لديك موعد؟", False, None),
    },
    "ur": {
        "good morning how can i help you": ("Good morning. How can I help you?", "صبح بخیر۔ میں آپ کی کیسے مدد کر سکتا ہوں؟", False, None),
        "do you have an appointment": ("Do you have an appointment?", "کیا آپ کا کوئی اپوائنٹمنٹ ہے؟", False, None),
    },
    "bn": {
        "good morning how can i help you": ("Good morning. How can I help you?", "সুপ্রভাত। আমি আপনাকে কীভাবে সাহায্য করতে পারি?", False, None),
        "do you have an appointment": ("Do you have an appointment?", "আপনার কি কোনো অ্যাপয়েন্টমেন্ট আছে?", False, None),
    },
    "so": {
        "good morning how can i help you": ("Good morning. How can I help you?", "Subax wanaagsan. Sideen ku caawin karaa?", False, None),
        "do you have an appointment": ("Do you have an appointment?", "Ma qabtaa ballan?", False, None),
    },
    "ro": {
        "good morning how can i help you": ("Good morning. How can I help you?", "Bună dimineața. Cu ce vă pot ajuta?", False, None),
        "do you have an appointment": ("Do you have an appointment?", "Aveți o programare?", False, None),
    }
}

# ============================================================
# CLINICAL SYNTHESIZER MATCHING FUNCTION
# ============================================================
def synthesize_staff_question(text, lang_code):
    """
    Analyzes staff questions (e.g. 'how long do you have pain?', 'where does it hurt?')
    and returns verified native translations across all 9 languages without relying on web scrapers.
    """
    clean = re.sub(r'[^\w\s]', '', text.lower()).strip()

    # --- 1. DURATION INTENTS ---
    if any(q in clean for q in ["how long", "since when", "how many days", "when did"]) and "pain" in clean:
        if "chest" in clean:
            return CLINICAL_STAFF_SYNTHESIZER["HOW_LONG_CHEST_PAIN"].get(lang_code)
        if "head" in clean:
            return CLINICAL_STAFF_SYNTHESIZER["HOW_LONG_HEADACHE"].get(lang_code)
        if "stomach" in clean or "belly" in clean or "abdomen" in clean or "abdominal" in clean:
            return CLINICAL_STAFF_SYNTHESIZER["HOW_LONG_STOMACH"].get(lang_code)
        return CLINICAL_STAFF_SYNTHESIZER["HOW_LONG_PAIN"].get(lang_code)

    if any(q in clean for q in ["how long", "since when", "when did"]) and ("fever" in clean or "temperature" in clean):
        return CLINICAL_STAFF_SYNTHESIZER["HOW_LONG_FEVER"].get(lang_code)

    if any(q in clean for q in ["how long", "since when", "when did"]) and ("breath" in clean or "breathing" in clean):
        return CLINICAL_STAFF_SYNTHESIZER["HOW_LONG_BREATHING"].get(lang_code)

    if clean in ["how long", "how long have you had this", "how long has this been", "how long is this"]:
        return CLINICAL_STAFF_SYNTHESIZER["HOW_LONG_GENERAL"].get(lang_code)

    # --- 2. LOCATION INTENTS ---
    if any(q in clean for q in ["where is", "where does it hurt", "where are you feeling", "where do you have"]):
        return CLINICAL_STAFF_SYNTHESIZER["WHERE_IS_PAIN"].get(lang_code)

    # --- 3. PRESENCE INTENTS ---
    if any(q in clean for q in ["do you have", "are you having", "is there", "are you feeling"]):
        if "chest" in clean:
            return CLINICAL_STAFF_SYNTHESIZER["DO_YOU_HAVE_CHEST_PAIN"].get(lang_code)
        if "fever" in clean or "temperature" in clean:
            return CLINICAL_STAFF_SYNTHESIZER["DO_YOU_HAVE_FEVER"].get(lang_code)
        if "breath" in clean or "breathing" in clean:
            return CLINICAL_STAFF_SYNTHESIZER["DO_YOU_HAVE_BREATHING"].get(lang_code)
        if "dizzy" in clean or "faint" in clean or "dizziness" in clean:
            return CLINICAL_STAFF_SYNTHESIZER["DO_YOU_HAVE_DIZZINESS"].get(lang_code)
        if "bleed" in clean or "blood" in clean:
            return CLINICAL_STAFF_SYNTHESIZER["DO_YOU_HAVE_BLEEDING"].get(lang_code)
        if "allergy" in clean or "allergies" in clean:
            return CLINICAL_STAFF_SYNTHESIZER["ALLERGIES_QUERY"].get(lang_code)
        if "medication" in clean or "medicine" in clean or "tablets" in clean or "drugs" in clean:
            return CLINICAL_STAFF_SYNTHESIZER["MEDICATION_QUERY"].get(lang_code)
        if "pain" in clean:
            return CLINICAL_STAFF_SYNTHESIZER["DO_YOU_HAVE_PAIN"].get(lang_code)

    # --- 4. SEVERITY INTENTS ---
    if any(q in clean for q in ["scale of 1", "rate your pain", "how severe", "how bad"]):
        return CLINICAL_STAFF_SYNTHESIZER["SEVERITY_SCALE"].get(lang_code)

    return None
