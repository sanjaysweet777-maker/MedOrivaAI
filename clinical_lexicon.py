"""
MedOriva AI — Core Clinical Lexicon & Multilingual Domains
Equal support for all 9 UK community languages + English
Includes comprehensive noun/verb declensions, locatives, and phonetic variants.
"""
import re

# ============================================================
# 1. SUPPORTED LANGUAGES REGISTRY
# ============================================================
class _LangEntry(str):
    def __new__(cls, name, native, code):
        obj = str.__new__(cls, name)
        obj.name = name
        obj.native = native
        obj.code = code
        return obj

    def __getitem__(self, key):
        if key == "name":
            return self.name
        if key == "native":
            return self.native
        if key == "code":
            return self.code
        return super().__getitem__(key)

    def get(self, key, default=None):
        if key == "name":
            return self.name
        if key == "native":
            return self.native
        if key == "code":
            return self.code
        return default

LANGUAGES = {
    "ta": _LangEntry("Tamil", "தமிழ்", "ta"),
    "hi": _LangEntry("Hindi", "हिन्दी", "hi"),
    "ml": _LangEntry("Malayalam", "മലയാളം", "ml"),
    "bn": _LangEntry("Bengali", "বাংলা", "bn"),
    "ur": _LangEntry("Urdu", "اردو", "ur"),
    "ar": _LangEntry("Arabic", "العربية", "ar"),
    "pl": _LangEntry("Polish", "Polski", "pl"),
    "so": _LangEntry("Somali", "Soomaali", "so"),
    "ro": _LangEntry("Romanian", "Română", "ro"),
    "en": _LangEntry("English", "English", "en"),
}

# ============================================================
# 2. STRICT TOKEN-LEVEL NEGATION & AFFIRMATION DICTIONARIES
# ============================================================
AFFIRMATION_PATTERNS = {
    "en": ["yes", "yeah", "yep", "sure", "correct", "affirmative", "true", "i do", "i have", "agree"],
    "ta": ["aam", "aama", "aamaam", "seri", "kandippa", "aamanga", "sari", "irukku", "koodum", "ஆம்", "ஆமாம்", "சரி", "இருக்கிறது"],
    "hi": ["haan", "ji haan", "theek hai", "sahi", "haanji", "ha", "theek", "hai", "हाँ", "जी हाँ", "ठीक है", "हा", "सही", "ठीक"],
    "ml": ["athe", "atheyo", "sherikkum", "und", "sari", "ശരി", "അതെ", "ഉണ്ട്"],
    "bn": ["hae", "hyan", "thik achhe", "haan", "thik", "aache", "হ্যাঁ", "ঠিক আছে", "হাঁ", "ঠিক", "আছে"],
    "ur": ["haan", "jee", "jee haan", "sahi", "hai", "ہاں", "جی", "جی ہاں", "درست", "ہے"],
    "ar": ["naam", "na'am", "aiwa", "sah", "sahih", "aywa", "نعم", "أيوا", "أجل", "صحيح", "ايوه"],
    "pl": ["tak", "zgadza sie", "dokladnie", "jasne", "prawda", "mam", "jest"],
    "so": ["haa", "waa sax", "haye", "waa run", "jiraa"],
    "ro": ["da", "exact", "sigur", "corect", "adevarat", "am", "este"]
}

NEGATION_PATTERNS = {
    "en": ["no", "not", "dont", "don't", "doesnt", "doesn't", "denies", "without", "never", "none", "no pain", "cannot", "cant", "can't"],
    "ta": ["illai", "illa", "varadhu", "varala", "ila", "kidayathu", "illamal", "mudiyala", "இல்லை", "இல்ல", "கிடையாது", "வராது", "இல்லாமல்"],
    "hi": ["nahi", "nahin", "nhi", "mat", "na", "bina", "kuch nahi", "nahi hai", "नहीं", "ना", "मत", "बिना", "कुछ नहीं", "नहीं है"],
    "ml": ["illa", "alla", "illathe", "illaatha", "illathathu", "ഇല്ല", "അല്ല", "ഇല്ലാതെ"],
    "bn": ["na", "ni", "nay", "chara", "nei", "না", "নেই", "নয়", "ছাড়া", "নাই"],
    "ur": ["nahi", "nahin", "na", "bina", "baghair", "نہیں", "نہ", "بغیر"],
    "ar": ["la", "laysa", "mish", "ma", "bidun", "kalla", "لا", "ليس", "ما", "مش", "بدون", "كلا"],
    "pl": ["nie", "brak", "bez", "nie ma", "ani", "zadnych", "nie czuje", "nigdy"],
    "so": ["ma", "maya", "ma jiro", "ma qabo", "aan", "waxba", "ma hayo", "la'aan"],
    "ro": ["nu", "nici", "fara", "n-am", "nu am", "deloc", "nimic"]
}

AFFIRMATION_DICTIONARY = AFFIRMATION_PATTERNS
NEGATION_DICTIONARY = NEGATION_PATTERNS

# ============================================================
# 3. CLINICAL SIMPLIFICATION & DURATION HELPERS
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
CLINICAL_SIMPLIFICATION_RULES = SIMPLIFY_RULES

def simplify_text(text):
    simplified = text
    changed = False
    for pattern, replacement in SIMPLIFY_RULES:
        result = re.sub(pattern, replacement, simplified, flags=re.IGNORECASE)
        if result != simplified:
            changed = True
            simplified = result
    return simplified, changed

DURATION_PATTERNS = [
    (r"(\d+)\s*(?:naalaga|naatkalaga|naala|naatkkala)", r"for \1 days"),
    (r"(?:oru|1)\s*(?:naalaga|naala)", "for 1 day"),
    (r"(?:rendu|2)\s*(?:naalaga|naala)", "for 2 days"),
    (r"(?:moonu|3)\s*(?:naalaga|naala)", "for 3 days"),
    (r"(\d+)\s*(?:din se|dino se|din)", r"for \1 days"),
    (r"od\s*(\d+)\s*dni", r"for \1 days"),
    (r"de\s*(\d+)\s*zile", r"for \1 days"),
    (r"\b(\d+)\s*(day|days|d)\b", r"for \1 days"),
    (r"\b(\d+)\s*(week|weeks|w)\b", r"for \1 weeks"),
    (r"\b(\d+)\s*(month|months|m)\b", r"for \1 months"),
    (r"\b(\d+)\s*(hour|hours|hr|hrs|h)\b", r"for \1 hours"),
    (r"\btoday\b", "since today"),
    (r"\byesterday\b", "since yesterday"),
    (r"\bthis morning\b", "since this morning")
]
DURATION_RULES = DURATION_PATTERNS
DURATION_CONVERTERS = DURATION_PATTERNS

# ============================================================
# 4. STAFF RECEPTION LEXICON (All 17 Standard Clinical Prompts)
# ============================================================
STAFF_LEXICON = {
    "GOOD_MORNING": {
        "ta": "வணக்கம். நான் உங்களுக்கு எப்படி உதவ முடியும்?",
        "hi": "नमस्ते। मैं आपकी क्या मदद कर सकता हूँ?",
        "ml": "നമസ്കാരം. ഞാൻ നിങ്ങളെ എങ്ങനെ സഹായിക്കണം?",
        "bn": "সুপ্রভাত। আমি আপনাকে কীভাবে সাহায্য করতে পারি?",
        "ur": "صبح بخیر۔ میں آپ کی کیا مدد کر سکتا ہوں؟",
        "ar": "صباح الخير. كيف يمكنني مساعدتك؟",
        "pl": "Dzień dobry. W czym mogę pomóc?",
        "so": "Subax wanaagsan. Sideen kuu caawin karaa?",
        "ro": "Bună dimineața. Cu ce vă pot ajuta?",
        "en": "Good morning. How can I help you?"
    },
    "APPOINTMENT": {
        "ta": "உங்களுக்கு இன்று அப்பாயிண்ட்மென்ட் உள்ளதா?",
        "hi": "क्या आपका आज अपॉइंटमेंट है?",
        "ml": "നിങ്ങൾക്ക് ഇന്ന് അപ്പോയിന്റ്മെന്റ് ഉണ്ടോ?",
        "bn": "আপনার কি আজ কোনো অ্যাপয়েন্টমেন্ট আছে?",
        "ur": "کیا آپ کا آج کوئی اپوائنٹمنٹ ہے؟",
        "ar": "هل لديك موعد اليوم؟",
        "pl": "Czy ma Pan/Pani dziś wizytę?",
        "so": "Ballan ma kuu qoran tahay maanta?",
        "ro": "Aveți o programare astăzi?",
        "en": "Do you have an appointment today?"
    },
    "NAME_DOB": {
        "ta": "தயவுசெய்து உங்கள் பெயர் மற்றும் பிறந்த தேதியைக் கூறுங்கள்.",
        "hi": "कृपया अपना नाम और जन्म तिथि बताएं।",
        "ml": "ദയവായി നിങ്ങളുടെ പേരും ജനനത്തീയതിയും പറയുക.",
        "bn": "দয়া করে আপনার নাম এবং জন্ম তারিখ বলুন।",
        "ur": "براہ کرم اپنا نام اور تاریخ پیدائش بتائیں۔",
        "ar": "يرجى ذكر اسمك وتاريخ ميلادك.",
        "pl": "Proszę podać imię, nazwisko i datę urodzenia.",
        "so": "Fadlan sheeg magacaaga iyo taariikhda dhalashadaada.",
        "ro": "Vă rugăm să ne spuneți numele și data nașterii.",
        "en": "Please provide your name and date of birth."
    },
    "NHS_NUMBER": {
        "ta": "உங்களிடம் NHS எண் உள்ளதா?",
        "hi": "क्या आपके पास अपना एनएचएस (NHS) नंबर है?",
        "ml": "നിങ്ങളുടെ പക്കൽ എൻഎച്ച്എസ് (NHS) നമ്പർ ഉണ്ടോ?",
        "bn": "আপনার কি এনএইচএস (NHS) নম্বর আছে?",
        "ur": "کیا آپ کے پاس اپنا این ایچ ایس (NHS) نمبر ہے؟",
        "ar": "هل لديك رقم NHS الخاص بك؟",
        "pl": "Czy posiada Pan/Pani swój numer NHS?",
        "so": "Miyaad haysataa lambarkaaga NHS?",
        "ro": "Aveți numărul dumneavoastră NHS?",
        "en": "Do you have your NHS number?"
    },
    "TAKE_SEAT": {
        "ta": "தயவுசெய்து காத்திருப்பு அறையில் அமருங்கள்.",
        "hi": "कृपया प्रतीक्षा कक्ष में बैठें।",
        "ml": "ദയവായി കാത്തിരിപ്പ് മുറിയിൽ ഇരിക്കുക.",
        "bn": "দয়া করে অপেক্ষাগারে বসুন।",
        "ur": "براہ کرم انتظار گاہ میں تشریف رکھیں۔",
        "ar": "يرجى الجلوس في غرفة الانتظار.",
        "pl": "Proszę usiąść w poczekalni.",
        "so": "Fadlan fariiso qolka sugitaanka.",
        "ro": "Vă rugăm să luați loc în sala de așteptare.",
        "en": "Please take a seat in the waiting area."
    },
    "INTERPRETER": {
        "ta": "உங்களுக்கு மொழிபெயர்ப்பாளர் தேவையா?",
        "hi": "क्या आपको दुभाषिए (इंटरप्रेटर) की आवश्यकता है?",
        "ml": "നിങ്ങൾക്ക് ഒരു ദ്വിഭാഷിയെ ആവശ്യമുണ്ടോ?",
        "bn": "আপনার কি দোভাষীর প্রয়োজন আছে?",
        "ur": "کیا آپ کو مترجم کی ضرورت ہے؟",
        "ar": "هل تحتاج إلى مترجم فوري؟",
        "pl": "Czy potrzebuje Pan/Pani tłumacza?",
        "so": "Ma u baahan tahay turjubaan?",
        "ro": "Aveți nevoie de un interpret?",
        "en": "Do you need an interpreter?"
    },
    "WHERE_IS_PAIN": {
        "ta": "உங்கள் வலி எங்கே இருக்கிறது?",
        "hi": "आपको दर्द कहाँ हो रहा है?",
        "ml": "നിങ്ങൾക്ക് എവിടെയാണ് വേദന?",
        "bn": "আপনার ব্যথা কোথায় হচ্ছে?",
        "ur": "آپ کو درد کہاں ہے؟",
        "ar": "أين تشعر بالألم بالضبط؟",
        "pl": "Gdzie dokładnie odczuwa Pan/Pani ból?",
        "so": "Xanuunku xaggee ku hayaa?",
        "ro": "Unde vă doare mai exact?",
        "en": "Where is your pain located?"
    },
    "HOW_LONG_CHEST_PAIN": {
        "ta": "உங்களுக்கு எவ்வளவு காலமாக நெஞ்சு வலி உள்ளது?",
        "hi": "आपको सीने में दर्द कब से है?",
        "ml": "നിങ്ങൾക്ക് എത്ര നാളായി നെഞ്ചുവേദനയുണ്ട്?",
        "bn": "আপনার কতদিন ধরে বুকে ব্যথা হচ্ছে?",
        "ur": "آپ کو سینے میں درد کب سے ہے؟",
        "ar": "منذ متى وأنت تعاني من ألم في الصدر؟",
        "pl": "Od jak dawna ma Pan/Pani ból w klatce piersiowej?",
        "so": "Muddo intee leeg ayaad qabtaa laab xanuunka?",
        "ro": "De cât timp aveți dureri în piept?",
        "en": "How long have you had chest pain?"
    },
    "HOW_LONG_PAIN": {
        "ta": "உங்களுக்கு எவ்வளவு காலமாக வலி இருக்கிறது?",
        "hi": "आपको कितने समय से दर्द हो रहा है?",
        "ml": "നിങ്ങൾക്ക് എത്ര നാളായി വേദനയുണ്ട്?",
        "bn": "আপনার কতদিন ধরে ব্যথা হচ্ছে?",
        "ur": "آپ کو کب سے درد ہو رہا ہے؟",
        "ar": "منذ متى وأنت تشعر بالألم؟",
        "pl": "Od jak dawna odczuwa Pan/Pani ból?",
        "so": "Muddo intee leeg ayaad xanuunka dareemaysay?",
        "ro": "De cât timp aveți această durere?",
        "en": "How long have you had this pain?"
    },
    "DO_YOU_HAVE_CHEST_PAIN": {
        "ta": "உங்களுக்கு நெஞ்சு வலி உள்ளதா?",
        "hi": "क्या आपको सीने में दर्द है?",
        "ml": "നിങ്ങൾക്ക് നെഞ്ചുവേദന ഉണ്ടോ?",
        "bn": "আপনার কি বুকে ব্যথা আছে?",
        "ur": "کیا آپ کو سینے میں درد ہے؟",
        "ar": "هل تعاني من ألم في الصدر؟",
        "pl": "Czy ma Pan/Pani ból w klatce piersiowej?",
        "so": "Ma qabtaa laab xanuun?",
        "ro": "Aveți dureri în piept?",
        "en": "Do you have chest pain?"
    },
    "DO_YOU_HAVE_BREATHING": {
        "ta": "உங்களுக்கு மூச்சு விடுவதில் சிரமம் உள்ளதா?",
        "hi": "क्या आपको सांस लेने में कठिनाई हो रही है?",
        "ml": "നിങ്ങൾക്ക് ശ്വാസമെടുക്കാൻ ബുദ്ധിമുട്ടുണ്ടോ?",
        "bn": "আপনার কি শ্বাস নিতে কষ্ট হচ্ছে?",
        "ur": "کیا آپ کو سانس لینے میں دشواری ہے؟",
        "ar": "هل تواجه صعوبة في التنفس؟",
        "pl": "Czy ma Pan/Pani trudności z oddychaniem?",
        "so": "Ma kugu adag tahay neefsashadu?",
        "ro": "Aveți dificultăți de respirație?",
        "en": "Are you having difficulty breathing?"
    },
    "DO_YOU_HAVE_FEVER": {
        "ta": "உங்களுக்கு காய்ச்சல் உள்ளதா?",
        "hi": "क्या आपको बुखार है?",
        "ml": "നിങ്ങൾക്ക് പനി ഉണ്ടോ?",
        "bn": "আপনার কি জ্বর আছে?",
        "ur": "کیا آپ کو بخار ہے؟",
        "ar": "هل لديك حمى؟",
        "pl": "Czy ma Pan/Pani gorączkę?",
        "so": "Ma qabtaa qandho?",
        "ro": "Aveți febră?",
        "en": "Do you have a fever?"
    },
    "SEVERITY_SCALE": {
        "ta": "1 முதல் 10 வரை, உங்கள் வலி எவ்வளவு தீவிரமாக உள்ளது?",
        "hi": "1 से 10 के पैमाने पर, आपका दर्द कितना गंभीर है?",
        "ml": "1 മുതൽ 10 വരെയുള്ള അളവിൽ വേദന എത്രത്തോളമുണ്ട്?",
        "bn": "১ থেকে ১০ এর স্কেলে আপনার ব্যথা কতটা তীব্র?",
        "ur": "1 سے 10 کے پیمانے پر آپ کا درد کتنا شدید ہے؟",
        "ar": "على مقياس من 1 إلى 10، ما مدى شدة الألم؟",
        "pl": "W skali od 1 do 10, jak silny jest ból?",
        "so": "Qiyaastii 1 ilaa 10, xanuunku intee le'eg yahay?",
        "ro": "Pe o scară de la 1 la 10, cât de severă este durerea?",
        "en": "On a scale of 1 to 10, how severe is your pain?"
    },
    "ALLERGIES_QUERY": {
        "ta": "உங்களுக்கு மருந்து அல்லது உணவு ஒவ்வாமை (அலர்ஜி) உள்ளதா?",
        "hi": "क्या आपको किसी दवा या भोजन से एलर्जी है?",
        "ml": "നിങ്ങൾക്ക് എന്തെങ്കിലും അലർജി ഉണ്ടോ?",
        "bn": "আপনার কি কোনো ওষুধ বা খাবারে অ্যালার্জি আছে?",
        "ur": "کیا آپ کو کسی دوا یا خوراک سے الرجی ہے؟",
        "ar": "هل تعاني من أي حساسية تجاه أدوية أو أطعمة؟",
        "pl": "Czy ma Pan/Pani jakieś alergie na leki lub pokarmy?",
        "so": "Xasaasiyad ma ku leedahay dawooyinka ama cuntada?",
        "ro": "Aveți alergii la medicamente sau alimente?",
        "en": "Do you have any allergies to medications or food?"
    },
    "MEDICATION_QUERY": {
        "ta": "நீங்கள் தற்போது ஏதேனும் வழக்கமான மருந்துகளை எடுத்துக்கொள்கிறீர்களா?",
        "hi": "क्या आप वर्तमान में कोई नियमित दवाएं ले रहे हैं?",
        "ml": "നിങ്ങൾ സ്ഥിരമായി എന്തെങ്കിലും മരുന്ന് കഴിക്കുന്നുണ്ടോ?",
        "bn": "আপনি কি বর্তমানে কোনো নিয়মিত ওষুধ খাচ্ছেন?",
        "ur": "کیا آپ اس وقت کوئی باقاعدہ ادویات لے رہے ہیں؟",
        "ar": "هل تتناول أي أدوية منتظمة حالياً؟",
        "pl": "Czy przyjmuje Pan/Pani obecnie jakieś stałe leki?",
        "so": "Ma qaadataa wax dawooyin joogto ah hadda?",
        "ro": "Luați vreun tratament medicamentos în mod regulat?",
        "en": "Are you currently taking any regular medication?"
    },
    "DOCTOR_NOW": {
        "ta": "மருத்துவர் இப்போது உங்களைப் பார்ப்பார்.",
        "hi": "डॉक्टर अब आपको देखेंगे।",
        "ml": "ഡോക്ടർ ഇപ്പോൾ നിങ്ങളെ പരിശോധിക്കും.",
        "bn": "ডাক্তার এখন আপনাকে দেখবেন।",
        "ur": "ڈاکٹر اب آپ کا معائنہ کریں گے۔",
        "ar": "الطبيب سيراك الآن.",
        "pl": "Lekarz przyjmie Pana/Panią teraz.",
        "so": "Dhakhtarku hadda ayuu ku arkayaa.",
        "ro": "Medicul vă va consulta acum.",
        "en": "The doctor will see you now."
    },
    "DO_YOU_HAVE_PAIN": {
        "ta": "உங்களுக்கு வலி இருக்கிறதா?",
        "hi": "क्या आपको दर्द हो रहा है?",
        "ml": "നിങ്ങൾക്ക് വേദനയുണ്ടോ?",
        "bn": "আপনার কি কোনো ব্যথা আছে?",
        "ur": "کیا آپ کو درد ہے؟",
        "ar": "هل تشعر بأي ألم؟",
        "pl": "Czy odczuwa Pan/Pani ból?",
        "so": "Xanuun ma dareemaysaa?",
        "ro": "Aveți dureri în acest moment?",
        "en": "Are you feeling any pain?"
    }
}

# ============================================================
# 5. PATIENT CLINICAL DOMAINS (Expanded Spoken Declensions & Case Endings)
# ============================================================
PATIENT_CLINICAL_DOMAINS = {
    "chest_pain": {
        "urgent": True,
        "tokens": {
            "ta": [
                "nenjula valikuthu", "nenjil valikuthu", "nenji valikuthu", "maarbu valikuthu",
                "nenju valikuthu", "nenjula vali", "nenjil vali", "nenji vali", "nenju vali",
                "maarbu vali", "maar vali", "enji vali", "enju vali", "nenju edukkuthu",
                "நெஞ்சில் வலிக்கிறது", "நெஞ்சு வலிக்கிறது", "நெஞ்சு வலி", "நெஞ்சில் வலி", "மார்பு வலி"
            ],
            "hi": [
                "seene mein dard ho raha", "seene me dard ho raha", "chhati mein dard ho raha",
                "seene mein dard hai", "seene me dard hai", "seene mein dard", "seene me dard",
                "chhati mein dard", "chhati me dard", "chati mein dard", "chati me dard",
                "sine mein dard", "sine me dard", "seene mein jalan", "seene mein dabav",
                "सीने में दर्द हो रहा है", "सीने में दर्द है", "सीने में दर्द", "छाती में दर्द"
            ],
            "ml": [
                "nenjil vedana edukkunnu", "nenjil vedana und", "nenju vedana edukkunnu",
                "nenjil vali", "nenju vali", "nenju vedana", "nenjil vedana", "nenjile vedana",
                "നെഞ്ചിൽ വേദനയുണ്ട്", "നെഞ്ചിൽ വേദന", "നെഞ്ചുവേദന"
            ],
            "bn": [
                "buke byatha korchhe", "buke batha korchhe", "buke betha korchhe",
                "buke byatha achhe", "buke byatha", "buke batha", "buke betha", "buke chap",
                "বুকে ব্যথা করছে", "বুকে ব্যাথা করছে", "বুকে ব্যথা আছে", "বুকে ব্যথা", "বুকে ব্যাথা"
            ],
            "ur": [
                "seene mein dard ho raha", "seenay mein dard ho raha", "seene mein dard hai",
                "seenay mein dard hai", "seene mein dard", "seenay mein dard", "seene me dard",
                "dil mein dard", "chhati mein dard", "سینے میں درد ہو رہا ہے", "سینے میں درد ہے", "سینے میں درد"
            ],
            "ar": [
                "sadri yu'limuni", "alam fi al sadr", "alam fi sadr", "alam sadri", "alam sadr",
                "wagah fi al sadr", "wagah sadr", "alam bi sadri", "waja sedr", "sidri yuwjaani",
                "صدري يؤلمني", "ألم في الصدر", "ألم صدري", "الم في الصدر", "وجع في الصدر"
            ],
            "pl": [
                "boli mnie w piersiach", "boli mnie klatka piersiowa", "boli mnie klatka",
                "boli w piersiach", "boli w klatce piersiowej", "boli w klatce",
                "czuje klucie w piersiach", "czuję kłucie w piersiach", "klucie w piersiach", "kłucie w piersiach",
                "pieczenie w klatce piersiowej", "pieczenie w klatce", "ucisk w klatce piersiowej", "ucisk w klatce",
                "bol w klatce piersiowej", "ból w klatce piersiowej", "bol klatki piersiowej", "ból klatki piersiowej",
                "bol w klatce", "ból w klatce", "bol klatki", "ból klatki", "w piersiach", "piersiach"
            ],
            "so": [
                "laabta oo i xanuunaysa", "xabadka oo i xanuunaya", "laab xanuun daran",
                "laab xanuun", "xabad xanuun", "xanuunka laabta", "xanuun laabta"
            ],
            "ro": [
                "ma doare in piept", "mă doare în piept", "ma doare pieptul", "mă doare pieptul",
                "durere in piept", "durere în piept", "dureri in piept", "dureri în piept",
                "durere toracica", "durere toracică", "intepaturi in piept", "înțepături în piept",
                "strangere in piept", "strângere în piept"
            ],
            "en": [
                "chest pain", "tight chest", "crushing chest pain", "heavy chest", "pressure in chest", "pain in my chest"
            ]
        },
        "affirmative": {
            "ta": ("I have chest pain.", "எனக்கு நெஞ்சு வலி இருக்கிறது."),
            "hi": ("I have chest pain.", "मुझे सीने में दर्द है।"),
            "ml": ("I have chest pain.", "എനിക്ക് നെഞ്ചുവേദനയുണ്ട്."),
            "bn": ("I have chest pain.", "আমার বুকে ব্যথা আছে।"),
            "ur": ("I have chest pain.", "میرے سینے میں درد ہے۔"),
            "ar": ("I have chest pain.", "عندي ألم في الصدر."),
            "pl": ("I have chest pain.", "Mam ból w klatce piersiowej."),
            "so": ("I have chest pain.", "Waxaan qabaa laab xanuun."),
            "ro": ("I have chest pain.", "Am dureri în piept."),
            "en": ("I have chest pain.", "I have chest pain.")
        },
        "negative": {
            "ta": ("I do not have chest pain.", "எனக்கு நெஞ்சு வலி இல்லை."),
            "hi": ("I do not have chest pain.", "मुझे सीने में दर्द नहीं है।"),
            "ml": ("I do not have chest pain.", "എനിക്ക് നെഞ്ചുവേദനയില്ല."),
            "bn": ("I do not have chest pain.", "আমার বুকে ব্যথা নেই।"),
            "ur": ("I do not have chest pain.", "میرے سینے میں درد نہیں ہے۔"),
            "ar": ("I do not have chest pain.", "ليس عندي ألم في الصدر."),
            "pl": ("I do not have chest pain.", "Nie mam bólu w klatce piersiowej."),
            "so": ("I do not have chest pain.", "Ma qabo laab xanuun."),
            "ro": ("I do not have chest pain.", "Nu am dureri în piept."),
            "en": ("I do not have chest pain.", "I do not have chest pain.")
        }
    },
    "breathing_difficulty": {
        "urgent": True,
        "tokens": {
            "ta": [
                "moochu vida mudiyala", "moochu thinaral irukku", "moochu muttuthu", "moochu varala",
                "moochu varadhu", "moochu pidikuthu", "moochu thinaral", "swasa kolaru",
                "மூச்சு விட முடியவில்லை", "மூச்சு திணறல்", "மூச்சு முட்டுகிறது"
            ],
            "hi": [
                "saans lene mein takleef ho rahi", "saans nahi li ja rahi", "saans nahi aa rahi",
                "saans lene mein takleef", "saans lene me dikkat", "saans phool rahi", "saans phoolna",
                "dam ghut raha", "saans ruk rahi", "सांस लेने में तकलीफ", "सांस फूलना", "दम घुट रहा है"
            ],
            "ml": [
                "shwasam edukkal budhimuttu", "shwasam muttunnu", "shwasam muttal",
                "ശ്വാസം എടുക്കാൻ ബുദ്ധിമുട്ട്", "ശ്വാസം മുട്ടൽ", "ശ്വാസതടസ്സം"
            ],
            "bn": [
                "shwash nite koshto hochhe", "shwash nite koshto", "shas kosto", "shash nite koshto", "dom bondho",
                "শ্বাস নিতে কষ্ট হচ্ছে", "শ্বাস নিতে কষ্ট", "শ্বাসকষ্ট"
            ],
            "ur": [
                "saans lene mein dushwari ho rahi", "saans nahi aa rahi", "saans lene mein dushwari",
                "saans phool rahi hai", "saans phoolna", "دم گھٹ رہا ہے", "سانس لینے میں دشواری"
            ],
            "ar": [
                "dheeq fi al nafas", "diq fi tanaffus", "diq tanaffus", "mushkila bil nafas", "la astatee al tanaffus",
                "صعوبة في التنفس", "ضيق في التنفس", "ضيق تنفس"
            ],
            "pl": [
                "trudno mi oddychac", "trudno mi oddychać", "ciezko mi oddychac", "ciężko mi oddychać",
                "dusze sie", "duszę się", "brak mi tchu", "brak tchu", "brak powietrza",
                "dusznosc", "duszność", "dusznosci", "duszności", "duszno mi", "trudnosci z oddychaniem"
            ],
            "so": [
                "neefsashada ayaa igu adag", "neefta oo igu dhegaysa", "neefsasho adag", "neef qabasho", "neefsasho dhib"
            ],
            "ro": [
                "respir foarte greu", "nu pot sa respir", "nu pot să respir", "respiratie grea", "respirație grea",
                "lipsa de aer", "lipsă de aer", "dificultati de respiratie", "dificultăți de respirație"
            ],
            "en": [
                "difficulty breathing", "shortness of breath", "struggling to breathe", "cannot breathe", "breathless"
            ]
        },
        "affirmative": {
            "ta": ("I have difficulty breathing.", "எனக்கு மூச்சு விடுவதில் சிரமம் உள்ளது."),
            "hi": ("I have difficulty breathing.", "मुझे सांस लेने में तकलीफ है।"),
            "ml": ("I have difficulty breathing.", "എനിക്ക് ശ്വാസതടസ്സമുണ്ട്."),
            "bn": ("I have difficulty breathing.", "আমার শ্বাস নিতে কষ্ট হচ্ছে।"),
            "ur": ("I have difficulty breathing.", "مجھے سانس لینے میں دشواری ہے۔"),
            "ar": ("I have difficulty breathing.", "عندي ضيق في التنفس."),
            "pl": ("I have difficulty breathing.", "Mam trudności z oddychaniem."),
            "so": ("I have difficulty breathing.", "Waxaan dhib ku qabaa neefsashada."),
            "ro": ("I have difficulty breathing.", "Am dificultăți de respirație."),
            "en": ("I have difficulty breathing.", "I have difficulty breathing.")
        },
        "negative": {
            "ta": ("I do not have difficulty breathing.", "எனக்கு மூச்சுத் திணறல் இல்லை."),
            "hi": ("I do not have difficulty breathing.", "मुझे सांस लेने में तकलीफ नहीं है।"),
            "ml": ("I do not have difficulty breathing.", "എനിക്ക് ശ്വാസതടസ്സമില്ല."),
            "bn": ("I do not have difficulty breathing.", "আমার শ্বাসকষ্ট নেই।"),
            "ur": ("I do not have difficulty breathing.", "مجھے سانس لینے میں دشواری نہیں ہے۔"),
            "ar": ("I do not have difficulty breathing.", "ليس عندي ضيق في التنفس."),
            "pl": ("I do not have difficulty breathing.", "Nie mam trudności z oddychaniem."),
            "so": ("I do not have difficulty breathing.", "Dhib kuma qabo neefsashada."),
            "ro": ("I do not have difficulty breathing.", "Nu am dificultăți de respirație."),
            "en": ("I do not have difficulty breathing.", "I do not have difficulty breathing.")
        }
    },
    "bleeding": {
        "urgent": True,
        "tokens": {
            "ta": ["iratham varuthu", "ratham varuthu", "iratham kottuthu", "iratham", "ratham", "irathapokku", "இரத்தம் வருகிறது", "இரத்தப்போக்கு"],
            "hi": ["khoon beh raha hai", "khoon nikal raha hai", "khoon beh raha", "khoon nikal raha", "khoon aa raha", "khoon", "rakt", "खून बह रहा है", "खून आ रहा है", "खून"],
            "ml": ["raktham varunnu", "chora varunnu", "raktham", "chora", "രക്തം വരുന്നു", "രക്തസ്രാവം"],
            "bn": ["rokto porchhe", "rokto ber hochhe", "rokto", "রক্ত পড়ছে", "রক্তপাত"],
            "ur": ["khoon beh raha hai", "khoon nikal raha hai", "khoon beh raha", "khoon", "خون بہہ رہا ہے", "خون"],
            "ar": ["dam yanzif", "nazif shadid", "nazif", "dam", "نزيف حاد", "دم ينزف", "نزيف"],
            "pl": ["krwawie mocno", "krwawię mocno", "leci mi krew", "leci krew", "krwawienie", "krwawie", "krwawię", "krew", "krwotok"],
            "so": ["dhiig ayaa iga socda", "dhiig badan", "dhiig bax", "dhiig"],
            "ro": ["sangerez abundent", "sângerez abundent", "curge sange", "curge sânge", "sangerare", "sângerare", "hemoragie", "sange", "sânge"],
            "en": ["bleeding heavily", "bleeding", "heavy bleeding", "losing blood", "blood"]
        },
        "affirmative": {
            "ta": ("I am bleeding.", "எனக்கு இரத்தப்போக்கு உள்ளது."),
            "hi": ("I am bleeding.", "खून बह रहा है।"),
            "ml": ("I am bleeding.", "രക്തസ്രാവം ഉണ്ട്."),
            "bn": ("I am bleeding.", "রক্তপাত হচ্ছে।"),
            "ur": ("I am bleeding.", "خون بہہ رہا ہے۔"),
            "ar": ("I am bleeding.", "أعاني من نزيف."),
            "pl": ("I am bleeding.", "Mam krwawienie."),
            "so": ("I am bleeding.", "Dhiig ayaa iga socda."),
            "ro": ("I am bleeding.", "Sângerez."),
            "en": ("I am bleeding.", "I am bleeding.")
        },
        "negative": {
            "ta": ("I am not bleeding.", "எனக்கு இரத்தப்போக்கு இல்லை."),
            "hi": ("I am not bleeding.", "खून नहीं बह रहा है।"),
            "ml": ("I am not bleeding.", "രക്തസ്രാവം ഇല്ല."),
            "bn": ("I am not bleeding.", "রক্তপাত হচ্ছে না।"),
            "ur": ("I am not bleeding.", "خون نہیں بہہ رہا ہے۔"),
            "ar": ("I am not bleeding.", "لا أعاني من نزيف."),
            "pl": ("I am not bleeding.", "Nie mam krwawienia."),
            "so": ("I am not bleeding.", "Dhiig igama socdo."),
            "ro": ("I am not bleeding.", "Nu sângerez."),
            "en": ("I am not bleeding.", "I am not bleeding.")
        }
    },
    "unconscious": {
        "urgent": True,
        "tokens": {
            "ta": ["mayangi vizhunthuten", "mayakkam vanthiruchu", "mayangi vizhunthen", "mayakkam", "mayangi", "மயக்கம்", "மயங்கி விழுந்துவிட்டேன்"],
            "hi": ["behosh ho gaya", "chakkar kha kar gir gaya", "behosh", "be hosh", "बेहोश हो गया", "बेहोश"],
            "ml": ["bodham kettu veenu", "bodhakshayam undayi", "bodhakshayam", "ബോധക്ഷയം"],
            "bn": ["agyan hoye gechhilam", "matha ghure pore gechhi", "agyan", "অজ্ঞান হয়ে গেছি"],
            "ur": ["behosh ho gaya tha", "chakkar kha kar gir gaya", "be hosh", "behosh", "بے ہوش"],
            "ar": ["ughmiya alayya", "faqadt al waey", "ighma", "غمي علي", "إغماء"],
            "pl": ["zemdlalem", "zemdlałam", "zemdlalam", "stracilem przytomnosc", "straciłem przytomność", "stracilam przytomnosc", "straciłam przytomność", "omdlenie"],
            "so": ["waa miyir beelay", "waad miyir beeshay", "miyir beel"],
            "ro": ["am lesinat", "am leșinat", "mi-am pierdut cunostinta", "mi-am pierdut cunoștința", "stare de lesin", "leșin", "inconstient"],
            "en": ["passed out", "fainted", "collapsed", "lost consciousness", "unconscious"]
        },
        "affirmative": {
            "ta": ("I feel faint or fainted.", "எனக்கு மயக்கமாக இருக்கிறது."),
            "hi": ("I felt faint or passed out.", "मुझे बेहोशी जैसा महसूस हुआ।"),
            "ml": ("I feel faint.", "എനിക്ക് ബോധക്ഷയം പോലെ തോന്നുന്നു."),
            "bn": ("I feel faint.", "আমার অজ্ঞান লাগছে।"),
            "ur": ("I feel faint.", "مجھے بے ہوشی محسوس ہو رہی ہے۔"),
            "ar": ("I feel faint.", "أشعر بإغماء."),
            "pl": ("I feel faint.", "Czuję, że mdleję."),
            "so": ("I feel faint.", "Miyir beel ayaan dareemayaa."),
            "ro": ("I feel faint.", "Mă simt pe cale de leșin."),
            "en": ("I feel faint or passed out.", "I feel faint or passed out.")
        },
        "negative": {
            "ta": ("I did not faint.", "எனக்கு மயக்கம் வரவில்லை."),
            "hi": ("I did not pass out.", "मैं बेहोश नहीं हुआ।"),
            "ml": ("I did not faint.", "എനിക്ക് ബോധക്ഷയം ഉണ്ടായിട്ടില്ല."),
            "bn": ("I did not faint.", "আমি অজ্ঞান হইনি।"),
            "ur": ("I did not faint.", "میں بے ہوش نہیں ہوا۔"),
            "ar": ("I did not faint.", "لم يغمَ علي."),
            "pl": ("I did not faint.", "Nie zemdlałem."),
            "so": ("I did not faint.", "Ma miyir beelin."),
            "ro": ("I did not faint.", "Nu am leșinat."),
            "en": ("I did not faint.", "I did not faint.")
        }
    },
    "headache": {
        "urgent": False,
        "tokens": {
            "ta": [
                "thalai valikuthu", "thala valikuthu", "mandai valikuthu", "mandai idikkuthu",
                "thalai vali", "thala vali", "mandai vali", "thalavali", "தலை வலிக்கிறது", "தலைவலி", "தலை வலி"
            ],
            "hi": [
                "sar phat raha hai", "sir dard kar raha hai", "sar dard kar raha hai", "sir me dard hai", "sar me dard hai",
                "sir dard", "sar dard", "sar me dard", "sir me dard", "सिर में दर्द है", "सिरदर्द", "सर दर्द", "सिर दर्द"
            ],
            "ml": [
                "thala vedana edukkunnu", "thala valikkunnu", "thalavedana", "thala vedana", "തലവേദന"
            ],
            "bn": [
                "matha byatha korchhe", "matha batha korchhe", "matha byatha", "matha batha", "matha betha", "মাথা ব্যথা করছে", "মাথা ব্যথা"
            ],
            "ur": [
                "sar mein shadeed dard hai", "sar dard kar raha hai", "sar mein dard hai", "sar dard", "sir mein dard", "sar me dard", "سر میں شدید درد ہے", "سر درد"
            ],
            "ar": [
                "rasi yuwjaani", "alam fi al ras", "alam rasi", "waja ras", "suda", "sudaa", "راسي يوجعني", "صداع", "ألم في الرأس"
            ],
            "pl": [
                "peka mi glowa", "pęka mi głowa", "boli mnie glowa", "boli mnie głowa", "boli glowa", "boli głowa",
                "bol glowy", "ból głowy", "bol w glowie", "ból w głowie"
            ],
            "so": [
                "madaxa oo aad ii xanuunaya", "madaxa oo i xanuunaya", "madax xanuun daran", "madax xanuun", "madax xanoon"
            ],
            "ro": [
                "ma doare capul foarte tare", "mă doare capul foarte tare", "ma doare capul", "mă doare capul",
                "durere de cap", "dureri de cap", "migrena", "migrenă"
            ],
            "en": [
                "headache", "head pain", "my head hurts", "severe headache", "throbbing head"
            ]
        },
        "affirmative": {
            "ta": ("I have a headache.", "எனக்கு தலைவலி இருக்கிறது."),
            "hi": ("I have a headache.", "मुझे सिर दर्द है।"),
            "ml": ("I have a headache.", "എനിക്ക് തലവേദനയുണ്ട്."),
            "bn": ("I have a headache.", "আমার মাথা ব্যথা করছে।"),
            "ur": ("I have a headache.", "میرے سر میں درد ہے۔"),
            "ar": ("I have a headache.", "عندي صداع."),
            "pl": ("I have a headache.", "Boli mnie głowa."),
            "so": ("I have a headache.", "Waxaan qabaa madax xanuun."),
            "ro": ("I have a headache.", "Am dureri de cap."),
            "en": ("I have a headache.", "I have a headache.")
        },
        "negative": {
            "ta": ("I do not have a headache.", "எனக்கு தலைவலி இல்லை."),
            "hi": ("I do not have a headache.", "मुझे सिर दर्द नहीं है।"),
            "ml": ("I do not have a headache.", "എനിക്ക് തലവേദനയില്ല."),
            "bn": ("I do not have a headache.", "আমার মাথা ব্যথা নেই।"),
            "ur": ("I do not have a headache.", "میرے سر میں درد نہیں ہے۔"),
            "ar": ("I do not have a headache.", "ليس عندي صداع."),
            "pl": ("I do not have a headache.", "Nie boli mnie głowa."),
            "so": ("I do not have a headache.", "Ma qabo madax xanuun."),
            "ro": ("I do not have a headache.", "Nu am dureri de cap."),
            "en": ("I do not have a headache.", "I do not have a headache.")
        }
    },
    "fever": {
        "urgent": False,
        "tokens": {
            "ta": [
                "udambu kaayuthu", "kaichal adikuthu", "udambu suudu", "kaichal", "kaaichal", "jwaram", "suram",
                "காய்ச்சல் அடிக்கிறது", "காய்ச்சல்", "சுரம்"
            ],
            "hi": [
                "tez bukhar hai", "sarir tap raha hai", "bukhar aa raha hai", "tez bukhar", "bukhar", "taap",
                "तेज बुखार है", "बुखार आ रहा है", "बुखार"
            ],
            "ml": [
                "choodu kooduthal aanu", "pani edukkunnu", "choodu", "pani", "പനി"
            ],
            "bn": [
                "shorir gorom hoye achhe", "jhor eshechhe", "tez jor", "jwor", "jor", "জ্বর এসেছে", "জ্বর"
            ],
            "ur": [
                "tez bukhar hai", "jism tap raha hai", "tez bukhar", "bukhar", "تیز بخار ہے", "بخار"
            ],
            "ar": [
                "hararati murtafia", "harara murtafia", "sukhuna", "humma", "harara", "حرارتي مرتفعة", "حمى"
            ],
            "pl": [
                "mam wysoka temperature", "mam wysoką temperaturę", "mam goraczke", "mam gorączkę",
                "wysoka temperatura", "temperatura", "goraczka", "gorączka"
            ],
            "so": [
                "qandho daran", "jidhka oo aad u kulul", "qandho", "xumad", "kuleyl"
            ],
            "ro": [
                "am temperatura mare", "am temperatură mare", "am febra mare", "am febră mare",
                "temperatura ridicata", "temperatură ridicată", "temperatura", "febra", "febră"
            ],
            "en": [
                "fever", "high temperature", "running a temperature", "chills and fever"
            ]
        },
        "affirmative": {
            "ta": ("I have a fever.", "எனக்கு காய்ச்சல் இருக்கிறது."),
            "hi": ("I have a fever.", "मुझे बुखार है।"),
            "ml": ("I have a fever.", "എനിക്ക് പനിയുണ്ട്."),
            "bn": ("I have a fever.", "আমার জ্বর আছে।"),
            "ur": ("I have a fever.", "مجھے بخار ہے۔"),
            "ar": ("I have a fever.", "عندي حمى."),
            "pl": ("I have a fever.", "Mam gorączkę."),
            "so": ("I have a fever.", "Waxaan qabaa qandho."),
            "ro": ("I have a fever.", "Am febră."),
            "en": ("I have a fever.", "I have a fever.")
        },
        "negative": {
            "ta": ("I do not have a fever.", "எனக்கு காய்ச்சல் இல்லை."),
            "hi": ("I do not have a fever.", "मुझे बुखार नहीं है।"),
            "ml": ("I do not have a fever.", "എനിക്ക് പനിയില്ല."),
            "bn": ("I do not have a fever.", "আমার জ্বর নেই।"),
            "ur": ("I do not have a fever.", "मुझे بخار ਨਹੀਂ ہے۔"),
            "ar": ("I do not have a fever.", "ليس عندي حمى."),
            "pl": ("I do not have a fever.", "Nie mam gorączki."),
            "so": ("I do not have a fever.", "Ma qabo wax qandho ah."),
            "ro": ("I do not have a fever.", "Nu am febră."),
            "en": ("I do not have a fever.", "I do not have a fever.")
        }
    },
    "stomach_pain": {
        "urgent": False,
        "tokens": {
            "ta": [
                "vayiru valikuthu", "vayathula vali", "vayitru vali", "vayiru vali", "vathiru vali",
                "வயிறு வலிக்கிறது", "வயிற்று வலி", "வயிறு வலி"
            ],
            "hi": [
                "pet mein dard ho raha hai", "pet me dard ho raha hai", "pet mein marod", "pet kharab hai",
                "pet dard", "pet mein dard", "pet me dard", "पेट में दर्द हो रहा है", "पेट दर्द", "पेट में दर्द"
            ],
            "ml": [
                "vayaru vedana edukkunnu", "vayaril vali", "vayaruvathana", "vayaru vedana", "വയറുവേദന"
            ],
            "bn": [
                "pete byatha korchhe", "pete batha korchhe", "pet byatha", "pet batha", "pete byatha", "pete batha",
                "পেটে ব্যথা করছে", "পেট ব্যথা", "পেটে ব্যথা"
            ],
            "ur": [
                "pait mein marod hai", "pait mein dard ho raha hai", "pet mein dard", "pait mein dard", "pait dard", "pet dard",
                "پیٹ میں درد ہو رہا ہے", "پیٹ میں درد"
            ],
            "ar": [
                "batni tuwjaani", "alam fi al batan", "alam fi al meeda", "alam batn", "waja batn",
                "بطني توجعني", "ألم في البطن", "ألم في المعدة"
            ],
            "pl": [
                "boli mnie brzuch", "boli brzuch", "skurcze brzucha", "skurcze zoladka", "skurcze żołądka",
                "boli mnie zoladek", "boli mnie żołądek", "bol brzucha", "ból brzucha", "bol zoladka", "ból żołądka"
            ],
            "so": [
                "caloosha oo aad ii xanuunaysa", "caloosha oo i xanuunaysa", "calool xanuun daran", "calool xanuun"
            ],
            "ro": [
                "ma doare stomacul foarte tare", "mă doare stomacul foarte tare", "ma doare stomacul", "mă doare stomacul",
                "crampe la stomac", "durere abdominala", "durere abdominală", "durere de stomac", "dureri de stomac"
            ],
            "en": [
                "stomach pain", "abdominal pain", "tummy ache", "stomach cramps", "belly pain", "my stomach hurts"
            ]
        },
        "affirmative": {
            "ta": ("I have stomach pain.", "எனக்கு வயிற்று வலி இருக்கிறது."),
            "hi": ("I have stomach pain.", "मुझे पेट में दर्द है।"),
            "ml": ("I have stomach pain.", "എനിക്ക് വയറുവേദനയുണ്ട്."),
            "bn": ("I have stomach pain.", "আমার পেটে ব্যথা আছে।"),
            "ur": ("I have stomach pain.", "میرے پیٹ میں درد ہے۔"),
            "ar": ("I have stomach pain.", "عندي ألم في البطن."),
            "pl": ("I have stomach pain.", "Mam ból brzucha."),
            "so": ("I have stomach pain.", "Waxaan qabaa calool xanuun."),
            "ro": ("I have stomach pain.", "Am dureri de stomac."),
            "en": ("I have stomach pain.", "I have stomach pain.")
        },
        "negative": {
            "ta": ("I do not have stomach pain.", "எனக்கு வயிற்று வலி இல்லை."),
            "hi": ("I do not have stomach pain.", "मुझे पेट में दर्द नहीं है।"),
            "ml": ("I do not have stomach pain.", "എനിക്ക് വയറുവേദനയില്ല."),
            "bn": ("I do not have stomach pain.", "আমার পেটে ব্যথা নেই।"),
            "ur": ("I do not have stomach pain.", "میرے پیٹ میں درد نہیں ہے۔"),
            "ar": ("I do not have stomach pain.", "ليس عندي ألم في البطن."),
            "pl": ("I do not have stomach pain.", "Nie mam bólu brzucha."),
            "so": ("I do not have stomach pain.", "Ma qabo calool xanuun."),
            "ro": ("I do not have stomach pain.", "Nu am dureri de stomac."),
            "en": ("I do not have stomach pain.", "I do not have stomach pain.")
        }
    },
    "dizziness": {
        "urgent": False,
        "tokens": {
            "ta": ["thala suthuthu", "thala suttrudhal", "mayakkama irukku", "mayakkam", "தலை சுற்றுகிறது", "தலைசுற்றல்", "மயக்கம்"],
            "hi": ["chakkar aa rahe hain", "chakkar aa raha hai", "chakkar", "chakkar aana", "चक्कर आ रहे हैं", "चक्कर आना", "चक्कर"],
            "ml": ["thalakarakkam thonnunnu", "thalakarakkam", "തലകറക്കം"],
            "bn": ["matha ghurche", "matha ghora", "মাথা ঘুরছে", "মাথা ঘোরা"],
            "ur": ["chakkar aa rahe hain", "chakkar aana", "chakkar", "چکر آ رہے ہیں", "چکر"],
            "ar": ["ashur bi dawran", "dawkha", "duwar", "أشعر بدوخة", "دوخة", "دوار"],
            "pl": ["kreci mi sie w glowie", "kręci mi się w głowie", "kreci w glowie", "kręci w głowie", "zawroty glowy", "zawroty głowy", "slabo mi", "słabo mi"],
            "so": ["madax wareer daran", "wareer", "madax wareer"],
            "ro": ["ametesc foarte tare", "amețesc foarte tare", "ma simt ametit", "mă simt amețit", "ameteala", "amețeală", "stare de lesin"],
            "en": ["dizziness", "feeling dizzy", "lightheaded", "head spinning", "dizzy"]
        },
        "affirmative": {
            "ta": ("I feel dizzy.", "எனக்கு மயக்கமாக இருக்கிறது."),
            "hi": ("I feel dizzy.", "मुझे चक्कर आ रहे हैं।"),
            "ml": ("I feel dizzy.", "എനിക്ക് തലകറക്കമുണ്ട്."),
            "bn": ("I feel dizzy.", "আমার মাথা ঘুরছে।"),
            "ur": ("I feel dizzy.", "مجھے چکر آ رہے ہیں۔"),
            "ar": ("I feel dizzy.", "أشعر بدوخة."),
            "pl": ("I feel dizzy.", "Kręci mi się w głowie."),
            "so": ("I feel dizzy.", "Waxaan dareemayaa wareer."),
            "ro": ("I feel dizzy.", "Am amețeli."),
            "en": ("I feel dizzy.", "I feel dizzy.")
        },
        "negative": {
            "ta": ("I do not feel dizzy.", "எனக்கு மயக்கம் இல்லை."),
            "hi": ("I do not feel dizzy.", "मुझे चक्कर नहीं आ रहे हैं।"),
            "ml": ("I do not feel dizzy.", "എനിക്ക് തലകറക്കമില്ല."),
            "bn": ("I do not feel dizzy.", "আমার মাথা ঘুরছে না।"),
            "ur": ("I do not feel dizzy.", "मुझे چکر نہیں آ رہے ہیں۔"),
            "ar": ("I do not feel dizzy.", "لا أشعر بدوخة."),
            "pl": ("I do not feel dizzy.", "Nie kręci mi się w głowie."),
            "so": ("I do not feel dizzy.", "Ma dareemayo wareer."),
            "ro": ("I do not feel dizzy.", "Nu am amețeli."),
            "en": ("I do not feel dizzy.", "I do not feel dizzy.")
        }
    },
    "vomiting": {
        "urgent": False,
        "tokens": {
            "ta": ["vaanthi varuthu", "vaanthi edukuthu", "vaanthi", "vandi", "வாந்தி வருகிறது", "வாந்தி"],
            "hi": ["ulti aa rahi hai", "ulti ho rahi hai", "ji machal raha hai", "ulti", "qay", "उल्टी आ रही है", "उल्टी"],
            "ml": ["chardhikan thonnunnu", "chardhi varunnu", "chardhi", "ഛർദ്ദി"],
            "bn": ["bomi hochhe", "bomi bhab", "bomi", "বমি হচ্ছে", "বমি"],
            "ur": ["ulti aa rahi hai", "ji matla raha hai", "ulti", "qay", "الٹی آ رہی ہے", "الٹی"],
            "ar": ["astafregh kathiran", "istifragh", "arjaa", "qay", "قيء", "استفراغ"],
            "pl": ["wymiotuje", "wymiotuję", "niedobrze mi", "chce mi sie wymiotowac", "chce mi się wymiotować", "wymioty", "mdlosci", "mdłości", "nudnosci", "nudności"],
            "so": ["matag joogto ah", "lalabbo daran", "matag", "lalabbo"],
            "ro": ["imi vine sa vomit", "îmi vine să vomit", "am varsat", "am vărsat", "varsaturi", "vărsături", "stare de greata", "stare de greață", "voma", "vomă"],
            "en": ["vomiting", "throwing up", "feeling sick", "nauseous", "vomit"]
        },
        "affirmative": {
            "ta": ("I have vomiting.", "எனக்கு வாந்தி இருக்கிறது."),
            "hi": ("I have vomiting.", "मुझे उल्टी आ रही है।"),
            "ml": ("I have vomiting.", "എനിക്ക് ഛർദ്ദിയുണ്ട്."),
            "bn": ("I have vomiting.", "আমার বমি হচ্ছে।"),
            "ur": ("I have vomiting.", "مجھے الٹی آ رہی ہے۔"),
            "ar": ("I have vomiting.", "عندي قيء."),
            "pl": ("I have vomiting.", "Mam wymioty."),
            "so": ("I have vomiting.", "Waxaan qabaa matag."),
            "ro": ("I have vomiting.", "Am vărsături."),
            "en": ("I have vomiting.", "I have vomiting.")
        },
        "negative": {
            "ta": ("I do not have vomiting.", "எனக்கு வாந்தி இல்லை."),
            "hi": ("I do not have vomiting.", "मुझे उल्टी नहीं आ रही है।"),
            "ml": ("I do not have vomiting.", "എനിക്ക് ഛർദ്ദിയില്ല."),
            "bn": ("I do not have vomiting.", "আমার বমি হচ্ছে না।"),
            "ur": ("I do not have vomiting.", "मुझे الٹی नहीं आ रही ہے۔"),
            "ar": ("I do not have vomiting.", "ليس عندي قيء."),
            "pl": ("I do not have vomiting.", "Nie mam wymiotów."),
            "so": ("I do not have vomiting.", "Ma qabo matag."),
            "ro": ("I do not have vomiting.", "Nu am vărsături."),
            "en": ("I do not have vomiting.", "I do not have vomiting.")
        }
    },
    "cough": {
        "urgent": False,
        "tokens": {
            "ta": ["irumal varuthu", "irumala irukku", "varattu irumal", "irumal", "இருமல் வருகிறது", "இருமல்"],
            "hi": ["khansi aa rahi hai", "sukhi khansi", "khansi", "khaansi", "खांसी आ रही है", "खांसी"],
            "ml": ["chuma varunnu", "chumakkunnu", "chuma", "ചുമ"],
            "bn": ["kashi hochhe", "shukno kashi", "kashi", "কাশি হচ্ছে", "কাশি"],
            "ur": ["khansi aa rahi hai", "sookhi khansi", "khansi", "کھانسی آ رہی ہے", "کھانسی"],
            "ar": ["sual shadid", "kahha shadida", "sual", "kahha", "سعال شديد", "سعال", "كحة"],
            "pl": ["kaszle mocno", "kaszlę mocno", "suchy kaszel", "mokry kaszel", "duszacy kaszel", "duszący kaszel", "kaszel", "kaszle", "kaszlę"],
            "so": ["qufac daran", "qufac qallalan", "qufac joogto ah", "qufac"],
            "ro": ["tusesc foarte rau", "tușesc foarte rău", "tuse seaca", "tuse seacă", "tuse productiva", "tuse productivă", "tuse"],
            "en": ["coughing a lot", "cough", "dry cough", "persistent cough", "bad cough"]
        },
        "affirmative": {
            "ta": ("I have a cough.", "எனக்கு இருமல் இருக்கிறது."),
            "hi": ("I have a cough.", "मुझे खांसी है।"),
            "ml": ("I have a cough.", "എനിക്ക് ചുമയുണ്ട്."),
            "bn": ("I have a cough.", "আমার কাশি আছে।"),
            "ur": ("I have a cough.", "مجھے کھانسی ہے۔"),
            "ar": ("I have a cough.", "عندي سعال."),
            "pl": ("I have a cough.", "Mam kaszel."),
            "so": ("I have a cough.", "Waxaan qabaa qufac."),
            "ro": ("I have a cough.", "Am tuse."),
            "en": ("I have a cough.", "I have a cough.")
        },
        "negative": {
            "ta": ("I do not have a cough.", "எனக்கு இருமல் இல்லை."),
            "hi": ("I do not have a cough.", "मुझे खांसी नहीं है।"),
            "ml": ("I do not have a cough.", "എനിക്ക് ചുമയില്ല."),
            "bn": ("I do not have a cough.", "আমার কাশি নেই।"),
            "ur": ("I do not have a cough.", "मुझे کھانسی نہیں ہے۔"),
            "ar": ("I do not have a cough.", "ليس عندي سعال."),
            "pl": ("I do not have a cough.", "Nie mam kaszlu."),
            "so": ("I do not have a cough.", "Ma qabo qufac."),
            "ro": ("I do not have a cough.", "Nu am tuse."),
            "en": ("I do not have a cough.", "I do not have a cough.")
        }
    },
    "sore_throat": {
        "urgent": False,
        "tokens": {
            "ta": ["thondai valikuthu", "thonda valikuthu", "thondaila vali", "thondai vali", "thonda vali", "தொண்டை வலிக்கிறது", "தொண்டை வலி"],
            "hi": ["gale mein dard ho raha hai", "gala kharab hai", "gale mein jalan", "gale mein dard", "gale me dard", "गले में दर्द है", "गले में दर्द"],
            "ml": ["thonda vedana edukkunnu", "thonda vedana", "തൊണ്ടവേദന"],
            "bn": ["gola byatha korchhe", "gola betha", "golar betha", "gola byatha", "গলায় ব্যথা করছে", "গলা ব্যথা"],
            "ur": ["galay mein dard hai", "gala kharab hai", "galay mein dard", "گلے میں درد ہے", "گلے میں درد"],
            "ar": ["halqi yuwjaani", "alam fi al halq", "iltihab halq", "alam halq", "حلقي يوجعني", "ألم في الحلق", "التهاب الحلق"],
            "pl": ["boli mnie gardlo", "boli mnie gardło", "piecze w gardle", "drapie w gardle", "bol gardla", "ból gardła"],
            "so": ["dhuunta oo i xanuunaysa", "dhuun xanuun daran", "cunaha xanuun", "dhuun xanuun"],
            "ro": ["ma doare in gat", "mă doare în gât", "ma doare gâtul", "gat inflamat", "gât inflamat", "durere in gat", "durere în gât"],
            "en": ["sore throat", "throat pain", "pain swallowing", "my throat hurts"]
        },
        "affirmative": {
            "ta": ("I have a sore throat.", "எனக்கு தொண்டை வலி இருக்கிறது."),
            "hi": ("I have a sore throat.", "मेरे गले में दर्द है।"),
            "ml": ("I have a sore throat.", "എനിക്ക് തൊണ്ടവേദനയുണ്ട്."),
            "bn": ("I have a sore throat.", "আমার গলা ব্যথা করছে।"),
            "ur": ("I have a sore throat.", "میرے گلے میں درد ہے۔"),
            "ar": ("I have a sore throat.", "عندي ألم في الحلق."),
            "pl": ("I have a sore throat.", "Boli mnie gardło."),
            "so": ("I have a sore throat.", "Waxaan qabaa dhuun xanuun."),
            "ro": ("I have a sore throat.", "Mă doare în gât."),
            "en": ("I have a sore throat.", "I have a sore throat.")
        },
        "negative": {
            "ta": ("I do not have a sore throat.", "எனக்கு தொண்டை வலி இல்லை."),
            "hi": ("I do not have a sore throat.", "मेरे गले में दर्द नहीं है।"),
            "ml": ("I do not have a sore throat.", "എനിക്ക് തൊണ്ടവേദനയില്ല."),
            "bn": ("I do not have a sore throat.", "আমার গলা ব্যথা নেই।"),
            "ur": ("I do not have a sore throat.", "میرے گلے میں درد نہیں ہے۔"),
            "ar": ("I do not have a sore throat.", "ليس عندي ألم في الحلق."),
            "pl": ("I do not have a sore throat.", "Nie boli mnie gardło."),
            "so": ("I do not have a sore throat.", "Ma qabo dhuun xanuun."),
            "ro": ("I do not have a sore throat.", "Nu mă doare în gât."),
            "en": ("I do not have a sore throat.", "I do not have a sore throat.")
        }
    },
    "back_pain": {
        "urgent": False,
        "tokens": {
            "ta": ["muthugu valikuthu", "iduppu valikuthu", "muthukula vali", "iduppula vali", "muthugu vali", "mudhugu vali", "iduppu vali", "முதுகு வலிக்கிறது", "முதுகு வலி", "இடுப்பு வலி"],
            "hi": ["peeth mein dard ho raha hai", "kamar mein dard ho raha hai", "kamar dard", "peeth dard", "peeth mein dard", "kamar mein dard", "पीठ में दर्द", "कमर दर्द", "पीठ दर्द"],
            "ml": ["nadu vedana edukkunnu", "puram vedana", "naduvedana", "naduv vedana", "നടുവേദന", "പുറംവേദന"],
            "bn": ["pithe byatha korchhe", "komore byatha", "pithe byatha", "komor betha", "pither byatha", "পিঠে ব্যথা", "কোমর ব্যথা"],
            "ur": ["kamar mein dard ho raha hai", "peeth mein dard", "kamar dard", "کمر میں درد ہو رہا ہے", "کمر درد", "پیٹھ میں درد"],
            "ar": ["dhahri yuwjaani", "alam fi al dhahr", "alam dhahr", "alam zahr", "ظهري يوجعني", "ألم في الظهر"],
            "pl": ["bola mnie plecy", "bolą mnie plecy", "lupie w krzyzu", "łupie w krzyżu", "bol kregoslupa", "ból kręgosłupa", "bol krzyza", "ból krzyża", "bol plecow", "ból pleców"],
            "so": ["dhabarka oo aad ii xanuunaya", "dhabarka oo i xanuunaya", "dhabar xanuun daran", "dhabar xanuun"],
            "ro": ["ma doare spatele foarte tare", "mă doare spatele foarte tare", "ma doare spatele", "mă doare spatele", "durere lombara", "durere lombară", "durere de spate", "dureri de spate"],
            "en": ["back pain", "lower back pain", "bad back", "my back hurts", "spine pain"]
        },
        "affirmative": {
            "ta": ("I have back pain.", "எனக்கு முதுகு வலி இருக்கிறது."),
            "hi": ("I have back pain.", "मेरी पीठ में दर्द है।"),
            "ml": ("I have back pain.", "എനിക്ക് പുറംവേദനയുണ്ട്."),
            "bn": ("I have back pain.", "আমার পিঠে ব্যথা আছে।"),
            "ur": ("I have back pain.", "میری کمر میں درد ہے۔"),
            "ar": ("I have back pain.", "عندي ألم في الظهر."),
            "pl": ("I have back pain.", "Bolą mnie plecy."),
            "so": ("I have back pain.", "Waxaan qabaa dhabar xanuun."),
            "ro": ("I have back pain.", "Am dureri de spate."),
            "en": ("I have back pain.", "I have back pain.")
        },
        "negative": {
            "ta": ("I do not have back pain.", "எனக்கு முதுகு வலி இல்லை."),
            "hi": ("I do not have back pain.", "मेरी पीठ में दर्द नहीं है।"),
            "ml": ("I do not have back pain.", "എനിക്ക് പുറംവേദനയില്ല."),
            "bn": ("I do not have back pain.", "আমার পিঠে ব্যথা নেই।"),
            "ur": ("I do not have back pain.", "میری کمر میں درد نہیں ہے۔"),
            "ar": ("I do not have back pain.", "ليس عندي ألم في الظهر."),
            "pl": ("I do not have back pain.", "Nie bolą mnie plecy."),
            "so": ("I do not have back pain.", "Ma qabo dhabar xanuun."),
            "ro": ("I do not have back pain.", "Nu am dureri de spate."),
            "en": ("I do not have back pain.", "I do not have back pain.")
        }
    },
    "skin_rash": {
        "urgent": False,
        "tokens": {
            "ta": ["thol thadippu", "arippu edukkuthu", "udambula arippu", "thol arippu", "arippu", "thadippu", "தோல் தடிப்பு", "அரிப்பு"],
            "hi": ["khujli ho rahi hai", "daane nikal aaye hain", "daane", "khujli", "chakatte", "दाने निकल आए हैं", "खुजली", "दाने"],
            "ml": ["thadippu und", "chorichil und", "chorichil", "thadippu", "ചൊറിച്ചിൽ", "തടിപ്പ്"],
            "bn": ["chulkani hochhe", "fusuri beriyechhe", "chulkani", "fusuri", "চুলকানি হচ্ছে", "ফুসকুড়ি", "চুলকানি"],
            "ur": ["kharish ho rahi hai", "daanay nikal aaye hain", "daanay", "kharish", "خارش ہو رہی ہے", "جلد پر دانے", "خارش"],
            "ar": ["hikkah shadida", "hakkah", "tafah jildi", "hikkah", "حكة شديدة", "طفح جلدي", "حكة"],
            "pl": ["skora mnie swedzi", "skóra mnie swędzi", "czerwone plamy na skorze", "czerwone plamy na skórze", "wysypka na skorze", "wysypka na skórze", "swedzenie", "swędzenie", "wysypka"],
            "so": ["cuncun daran", "maqaarka oo cuncunaya", "finan", "cuncun"],
            "ro": ["ma mananca pielea", "mă mănâncă pielea", "pete rosii pe piele", "pete roșii pe piele", "iritatie pe piele", "iritație pe piele", "eruptie cutanata", "erupție cutanată", "mancarime", "mâncărime", "eruptie", "erupție"],
            "en": ["skin rash", "itchy rash", "rash on my skin", "itchy skin", "spots on skin"]
        },
        "affirmative": {
            "ta": ("I have a skin rash.", "எனக்கு தோல் தடிப்பு இருக்கிறது."),
            "hi": ("I have a skin rash.", "मेरी त्वचा पर दाने हैं।"),
            "ml": ("I have a skin rash.", "എനിക്ക് തടിപ്പുണ്ട്."),
            "bn": ("I have a skin rash.", "আমার ত্বকে ফুসকুড়ি আছে।"),
            "ur": ("I have a skin rash.", "میری جلد پر دانے ہیں۔"),
            "ar": ("I have a skin rash.", "عندي طفح جلدي."),
            "pl": ("I have a skin rash.", "Mam wysypkę na skórze."),
            "so": ("I have a skin rash.", "Waxaan leeyahay finan."),
            "ro": ("I have a skin rash.", "Am o erupție pe piele."),
            "en": ("I have a skin rash.", "I have a skin rash.")
        },
        "negative": {
            "ta": ("I do not have a skin rash.", "எனக்கு தோல் தடிப்பு இல்லை."),
            "hi": ("I do not have a skin rash.", "मेरी त्वचा पर दाने नहीं हैं।"),
            "ml": ("I do not have a skin rash.", "എനിക്ക് തടിപ്പില്ല."),
            "bn": ("I do not have a skin rash.", "আমার ত্বকে ফুসকুড়ি নেই।"),
            "ur": ("I do not have a skin rash.", "میری جلد پر دانے نہیں ہیں۔"),
            "ar": ("I do not have a skin rash.", "ليس عندي طفح جلدي."),
            "pl": ("I do not have a skin rash.", "Nie mam wysypki."),
            "so": ("I do not have a skin rash.", "Ma lihi finan."),
            "ro": ("I do not have a skin rash.", "Nu am erupții pe piele."),
            "en": ("I do not have a skin rash.", "I do not have a skin rash.")
        }
    }
}

CANONICAL_RESPONSES = PATIENT_CLINICAL_DOMAINS

# ============================================================
# 6. URGENT SYMPTOMS CONFIG & GUIDED PROMPTS
# ============================================================
URGENT_SYMPTOMS_CONFIG = {
    "chest pain": ["chest pain", "tight chest", "crushing chest", "nenji vali", "seene mein dard", "bol w klatce", "alam fi sadr", "laab xanuun", "durere in piept"],
    "breathing difficulty": ["difficulty breathing", "shortness of breath", "moochu thinaral", "saans lene mein takleef", "shwasam muttal", "dusznosc", "diq fi tanaffus", "respiratie grea"],
    "bleeding": ["bleeding", "heavy bleeding", "iratham", "khoon", "krwawienie", "nazif", "dhiig", "sangerare"],
    "unconscious": ["unconscious", "passed out", "fainted", "mayakkam", "behosh", "omdlenie", "ighma", "miyir beel", "lesin"]
}
URGENT_SYMPTOMS = URGENT_SYMPTOMS_CONFIG
RED_FLAGS = URGENT_SYMPTOMS_CONFIG

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
CONTEXT_PROMPTS = GUIDED_PROMPTS

# ============================================================
# 7. PARSER & SYNTHESIZER UTILITIES
# ============================================================
def extract_symptom(text, lang_code):
    if not text:
        return None, None, None

    clean_text = re.sub(r'[^\w\s]', ' ', text.lower()).strip()
    norm = f" {' '.join(clean_text.split())} "

    candidates = []
    for sym_key, sym_data in PATIENT_CLINICAL_DOMAINS.items():
        tokens = sym_data["tokens"].get(lang_code, [])
        for token in tokens:
            candidates.append((token.lower().strip(), sym_key))

    candidates.sort(key=lambda x: len(x[0]), reverse=True)

    for token, sym_key in candidates:
        if f" {token} " in norm or norm.strip().startswith(token) or norm.strip().endswith(token):
            return sym_key, sym_key.replace('_', ' '), token

    return None, None, None

def synthesize_staff_question(text, target_lang):
    if not text:
        return ""
    clean = " ".join(text.strip().lower().split())

    if "booked appointment" in clean or "appointment" in clean:
        return STAFF_LEXICON["APPOINTMENT"].get(target_lang[:2], "")
    if "name and date of birth" in clean or "dob" in clean:
        return STAFF_LEXICON["NAME_DOB"].get(target_lang[:2], "")
    if "nhs" in clean:
        return STAFF_LEXICON["NHS_NUMBER"].get(target_lang[:2], "")
    if "seat" in clean or "wait" in clean:
        return STAFF_LEXICON["TAKE_SEAT"].get(target_lang[:2], "")
    if "chest" in clean and "pain" in clean:
        return STAFF_LEXICON["DO_YOU_HAVE_CHEST_PAIN"].get(target_lang[:2], "")
    if "breath" in clean:
        return STAFF_LEXICON["DO_YOU_HAVE_BREATHING"].get(target_lang[:2], "")
    if "fever" in clean:
        return STAFF_LEXICON["DO_YOU_HAVE_FEVER"].get(target_lang[:2], "")

    return ""
