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
# MULTI-LANGUAGE AFFIRMATION & NEGATION TOKENS
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
    "en": ["yes", "yeah", "yep", "sure", "correct", "affirmative", "agreed"]
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
# MULTI-LANGUAGE DURATION PATTERNS (Regex -> English conversion)
# ============================================================
DURATION_PATTERNS = [
    # Tamil: "4 naalaga", "rendu naala", "1 vaaramaga"
    (r"(\d+)\s*(?:naalaga|naatkalaga|naala|naatkkala)", r"for \1 days"),
    (r"(?:oru|1)\s*(?:naalaga|naala)", "for 1 day"),
    (r"(?:rendu|2)\s*(?:naalaga|naala)", "for 2 days"),
    (r"(?:moonu|3)\s*(?:naalaga|naala)", "for 3 days"),
    (r"(?:naalu|4)\s*(?:naalaga|naala)", "for 4 days"),
    (r"(?:anji|5)\s*(?:naalaga|naala)", "for 5 days"),
    (r"(\d+)\s*(?:vaaramaga|vaarama)", r"for \1 weeks"),
    (r"(\d+)\s*(?:maasamaga|maasama)", r"for \1 months"),
    (r"(\d+)\s*(?:mani nerama|maninerama)", r"for \1 hours"),

    # Hindi: "4 din se", "2 dino se", "1 hafte se"
    (r"(\d+)\s*(?:din se|dino se|din)", r"for \1 days"),
    (r"(?:ek|1)\s*din se", "for 1 day"),
    (r"(?:do|2)\s*din se", "for 2 days"),
    (r"(?:teen|3)\s*din se", "for 3 days"),
    (r"(?:char|4)\s*din se", "for 4 days"),
    (r"(\d+)\s*(?:hafte se|hafto se)", r"for \1 weeks"),
    (r"(\d+)\s*(?:mahine se|mahino se)", r"for \1 months"),
    (r"(\d+)\s*(?:ghante se|ghanto se)", r"for \1 hours"),

    # Malayalam: "4 divasamayi", "2 aazhchayayi"
    (r"(\d+)\s*(?:divasamayi|divasamaayi|naalayi)", r"for \1 days"),
    (r"(\d+)\s*(?:aazhchayayi|masamayi)", r"for \1 weeks"),

    # Polish: "od 4 dni", "od 2 tygodni"
    (r"od\s*(\d+)\s*dni", r"for \1 days"),
    (r"od\s*(\d+)\s*tygodni", r"for \1 weeks"),

    # Arabic (Arabizi): "min 4 ayam", "sarli 4 ayam"
    (r"(?:min|sarli|baali)\s*(\d+)\s*(?:ayam|tiyam|yom)", r"for \1 days"),

    # Urdu: "4 din se", "2 haftay se"
    (r"(\d+)\s*(?:din say|din se|dino se)", r"for \1 days"),

    # Bengali: "4 din dhore", "2 shoptaho dhore"
    (r"(\d+)\s*(?:din dhore|din jabot)", r"for \1 days"),

    # Somali: "4 maalmood", "2 toddobaad"
    (r"(\d+)\s*(?:maalmood|cisho)", r"for \1 days"),

    # Romanian: "de 4 zile", "de 2 saptamani"
    (r"de\s*(\d+)\s*zile", r"for \1 days"),
]

# ============================================================
# MULTI-LANGUAGE SYMPTOM VOCABULARY
# ============================================================
MULTI_LANG_SYMPTOMS = {
    "chest pain": {
        "english": "chest pain",
        "ta": ("நெஞ்சு வலி", ["nenji vali", "nenju vali", "nenjil vali", "nenjula vali", "maar vali", "நெஞ்சு வலி", "நெஞ்சில் வலி"]),
        "hi": ("सीने में दर्द", ["seene mein dard", "chest mein dard", "chhati mein dard", "seene me dard", "सीने में दर्द"]),
        "ml": ("നെഞ്ചുവേദന", ["nenjil vali", "nenju vali", "nenjile vedana", "നെഞ്ചുവേദന", "നെഞ്ചിൽ വേദന"]),
        "pl": ("ból w klatce piersiowej", ["bol klatki", "bol w klatce", "pieczenie w klatce"]),
        "ar": ("ألم في الصدر", ["alam fi al sadr", "alam sedr", "wagah sedr", "ألم في الصدر"]),
        "ur": ["سینے میں درد", ["seene mein dard", "seene me dard", "dil mein dard", "سینے میں درد"]],
        "bn": ("বুকে ব্যথা", ["buke betha", "buke byatha", "buke batha", "বুকে ব্যথা"]),
        "so": ("xanuunka laabta", ["xanuun laabta", "laab xanuun"]),
        "ro": ("durere în piept", ["durere in piept", "dureri in piept"])
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
        "ta": ("இரத்தப்போக்கு", ["iratham varuthu", "ratham varuthu", "irathapokku", "இரத்தப்போக்கு", "இரத்தம் வருகிறது"]),
        "hi": ("खून बहना", ["khoon nikal raha", "khoon beh raha", "khoon aa raha", "खून आ रहा है", "खून बह रहा है"]),
        "ml": ("രക്തസ്രാവം", ["raktham varunnu", "chora varunnu", "രക്തം വരുന്നു"]),
        "pl": ("krwawienie", ["krwawie", "duzo krwi", "krwotok"]),
        "ar": ("نزيف", ["nazif", "dam yanzif", "نزيف", "خروج دم"]),
        "ur": ("خون بہنا", ["khoon beh raha hai", "khoon nikal raha hai", "خون بہہ رہا ہے"]),
        "bn": ("রক্তপাত", ["rokto porchhe", "rokto ber hochhe", "রক্ত পড়ছে", "রক্তপাত"]),
        "so": ("dhiig bax", ["dhiig ayaa iga socda", "dhiig bax"]),
        "ro": ("sângerare", ["sangerez", "curge sange", "hemoragie"])
    },
    "unconscious": {
        "english": "dizziness or fainting",
        "ta": ("மயக்கம் / தலைச்சுற்றல்", ["thalai sutharuthu", "mayakkam varuthu", "mayakam", "மயக்கம்", "தலை சுற்றல்"]),
        "hi": ("चक्कर या बेहोशी", ["chakkar aa raha", "behosh ho gaya", "चक्कर आ रहा है", "बेहोशी"]),
        "ml": ("തലകറക്കം / ബോധക്ഷയം", ["thalakarakkam", "bodhakshayam", "തലകറക്കം"]),
        "pl": ("omdlenie / zawroty głowy", ["kreci mi sie w glowie", "zemdlalem", "omdlenie"]),
        "ar": ("دوار أو إغماء", ["dayikh", "dawkha", "ighma", "أشعر بالدوار", "إغماء"]),
        "ur": ("چکر یا بے ہوشی", ["chakkar aa rahe hain", "behosh", "چکر آ رہے ہیں"]),
        "bn": ("মাথা ঘোরা বা অজ্ঞান", ["matha ghurche", "oggan", "মাথা ঘুরছে"]),
        "so": ("dawakhaad", ["madhax wareeg", "miyir beel"]),
        "ro": ("amețeală sau leșin", ["ametit", "am lesinat", "ameteli"])
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
    }
}

# ============================================================
# URGENT SYMPTOMS FOR TRIAGE ALERTS
# ============================================================
URGENT_SYMPTOMS_CONFIG = {
    "chest pain": ["chest pain", "heart pain", "heart attack", "crushing chest", "tight chest", "nenji vali", "seene mein dard", "bol klatki", "ألم في الصدر", "سینے میں درد", "বুকে ব্যথা", "xanuun laabta", "durere in piept", "நெஞ்சு வலி"],
    "breathing difficulty": ["can't breathe", "cant breathe", "difficulty breathing", "shortness of breath", "moochu varadhu", "moochu pidikuthu", "saans nahi", "saans lene mein takleef", "shwasam muttunnu", "duszno", "صعوبة في التنفس", "سانس لینے میں دشواری", "শ্বাস নিতে কষ্ট", "neefsasho dhib", "dificultate de respiratie", "மூச்சு திணறல்"],
    "bleeding": ["bleeding", "severe blood", "iratham", "khoon", "krwawienie", "نزيف", "خون", "রক্তপাত", "dhiig", "sângerare", "இரத்தப்போக்கு"],
    "unconscious": ["unconscious", "passed out", "collapsed", "fainted", "mayakkam", "behosh", "omdlenie", "إغماء", "بے ہوش", "অজ্ঞান", "miyir beel", "leșin", "மயக்கம்"]
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
# EXACT CLINICAL MATCH DICTIONARY (For High Precision)
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
        "how long do you have chest pain": ("How long have you had chest pain?", "உங்களுக்கு எவ்வளவு காலமாக நெஞ்சு வலி உள்ளது?", False, "chest pain"),
        "how long have you had this": ("How long have you had this?", "இது உங்களுக்கு எவ்வளவு காலமாக உள்ளது?", False, None),
        "how long": ("How long?", "இது உங்களுக்கு எவ்வளவு காலமாக உள்ளது?", False, None),
        "where is your pain": ("Where is your pain?", "உங்கள் வலி எங்கே இருக்கிறது?", False, None),
        "do you have chest pain": ("Do you have chest pain?", "உங்களுக்கு நெஞ்சு வலி உள்ளதா?", False, "chest pain"),
        "do you have a fever": ("Do you have a fever?", "உங்களுக்கு காய்ச்சல் உள்ளதா?", False, None),
        "are you having difficulty breathing": ("Are you having difficulty breathing?", "உங்களுக்கு மூச்சு விடுவதில் சிரமம் உள்ளதா?", False, "breathing difficulty"),
        "do you feel dizzy or faint": ("Do you feel dizzy or faint?", "நீங்கள் தலை சுற்றல் அல்லது மயக்கத்தை உணர்கிறீர்களா?", False, "unconscious"),
        "is there any bleeding": ("Is there any bleeding?", "ஏதேனும் இரத்தப்போக்கு உள்ளதா?", False, "bleeding"),
    },
    "hi": {
        "good morning how can i help you": ("Good morning. How can I help you?", "सुप्रभात। मैं आपकी कैसे मदद कर सकता हूँ?", False, None),
        "do you have an appointment": ("Do you have an appointment?", "क्या आपका कोई अपॉइंटमेंट है?", False, None),
        "how long do you have chest pain": ("How long have you had chest pain?", "आपको सीने में दर्द कब से है?", False, "chest pain"),
        "how long have you had this": ("How long have you had this?", "यह समस्या आपको कब से है?", False, None),
        "how long": ("How long?", "यह कब से है?", False, None),
        "do you have chest pain": ("Do you have chest pain?", "क्या आपको सीने में दर्द है?", False, "chest pain"),
        "do you have a fever": ("Do you have a fever?", "क्या आपको बुखार है?", False, None),
        "are you having difficulty breathing": ("Are you having difficulty breathing?", "क्या आपको सांस लेने में कठिनाई हो रही है?", False, "breathing difficulty"),
    },
    "ml": {
        "good morning how can i help you": ("Good morning. How can I help you?", "സുപ്രഭാതം. എനിക്ക് നിങ്ങളെ എങ്ങനെ സഹായിക്കാനാകും?", False, None),
        "how long do you have chest pain": ("How long have you had chest pain?", "നിങ്ങൾക്ക് എത്ര നാളായി നെഞ്ചുവേദനയുണ്ട്?", False, "chest pain"),
        "how long have you had this": ("How long have you had this?", "ഇത് നിങ്ങൾക്ക് എത്രകാലമായി ഉണ്ട്?", False, None),
        "do you have chest pain": ("Do you have chest pain?", "നിങ്ങൾക്ക് നെഞ്ചുവേദന ഉണ്ടോ?", False, "chest pain"),
    },
    "pl": {
        "good morning how can i help you": ("Good morning. How can I help you?", "Dzień dobry. W czym mogę pomóc?", False, None),
        "how long do you have chest pain": ("How long have you had chest pain?", "Od jak dawna ma Pan/Pani ból w klatce piersiowej?", False, "chest pain"),
        "how long have you had this": ("How long have you had this?", "Od jak dawna ma Pan/Pani ten problem?", False, None),
        "do you have chest pain": ("Do you have chest pain?", "Czy ma Pan/Pani ból w klatce piersiowej?", False, "chest pain"),
    },
    "ar": {
        "good morning how can i help you": ("Good morning. How can I help you?", "صباح الخير. كيف يمكنني مساعدتك؟", False, None),
        "how long do you have chest pain": ("How long have you had chest pain?", "منذ متى وأنت تعاني من ألم في الصدر؟", False, "chest pain"),
        "how long have you had this": ("How long have you had this?", "منذ متى وأنت تعاني من هذا؟", False, None),
        "do you have chest pain": ("Do you have chest pain?", "هل تعاني من ألم في الصدر؟", False, "chest pain"),
    },
    "ur": {
        "good morning how can i help you": ("Good morning. How can I help you?", "صبح بخیر۔ میں آپ کی کیسے مدد کر سکتا ہوں؟", False, None),
        "how long do you have chest pain": ("How long have you had chest pain?", "آپ کو سینے میں درد کب سے ہے؟", False, "chest pain"),
        "how long have you had this": ("How long have you had this?", "یہ آپ کو کب سے ہے؟", False, None),
        "do you have chest pain": ("Do you have chest pain?", "کیا آپ کو سینے میں درد ہے؟", False, "chest pain"),
    },
    "bn": {
        "good morning how can i help you": ("Good morning. How can I help you?", "সুপ্রভাত। আমি আপনাকে কীভাবে সাহায্য করতে পারি?", False, None),
        "how long do you have chest pain": ("How long have you had chest pain?", "আপনার কতদিন ধরে বুকে ব্যথা হচ্ছে?", False, "chest pain"),
        "how long have you had this": ("How long have you had this?", "আপনার কতদিন ধরে এই সমস্যা?", False, None),
        "do you have chest pain": ("Do you have chest pain?", "আপনার কি বুকে ব্যথা আছে?", False, "chest pain"),
    },
    "so": {
        "good morning how can i help you": ("Good morning. How can I help you?", "Subax wanaagsan. Sideen ku caawin karaa?", False, None),
        "how long do you have chest pain": ("How long have you had chest pain?", "Muddo intee leeg ayaad qabtaa xanuunka laabta?", False, "chest pain"),
        "how long have you had this": ("How long have you had this?", "Muddo intee leeg ayaad tan qabtaa?", False, None),
        "do you have chest pain": ("Do you have chest pain?", "Ma qabtaa xanuun laabta?", False, "chest pain"),
    },
    "ro": {
        "good morning how can i help you": ("Good morning. How can I help you?", "Bună dimineața. Cu ce vă pot ajuta?", False, None),
        "how long do you have chest pain": ("How long have you had chest pain?", "De cât timp aveți dureri în piept?", False, "chest pain"),
        "how long have you had this": ("How long have you had this?", "De cât timp aveți această problemă?", False, None),
        "do you have chest pain": ("Do you have chest pain?", "Aveți dureri în piept?", False, "chest pain"),
    }
}
