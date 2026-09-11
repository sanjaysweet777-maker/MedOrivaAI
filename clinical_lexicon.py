"""
MedOriva AI — Core Clinical Lexicon & Multilingual Domains
Equal support for all 9 UK community languages + English
"""

# ============================================================
# 1. LANGUAGES
# ============================================================
LANGUAGES = {
    "ta": "Tamil",
    "hi": "Hindi",
    "ml": "Malayalam",
    "bn": "Bengali",
    "ur": "Urdu",
    "ar": "Arabic",
    "pl": "Polish",
    "so": "Somali",
    "ro": "Romanian",
    "en": "English",
}

# ============================================================
# 2. NEGATION DICTIONARY
# ============================================================
NEGATION_DICTIONARY = {
    "ta": ["illai", "illa", "varadhu", "varala", "ila", "kidayathu", "illamal", "இல்லை", "இல்ல", "கிடையாது", "வராது"],
    "hi": ["nahi", "nahin", "nhi", "mat", "na", "bina", "kuch nahi", "नहीं", "ना", "मत", "बिना", "कुछ नहीं", "नहीं है"],
    "ml": ["illa", "alla", "illathe", "illaatha", "illathathu", "ഇല്ല", "അല്ല", "ഇല്ലാതെ"],
    "bn": ["na", "ni", "nay", "chara", "nei", "না", "নেই", "নয়", "ছাড়া", "নাই"],
    "ur": ["nahi", "nahin", "na", "bina", "baghair", "نہیں", "نہ", "بغیر"],
    "ar": ["la", "laysa", "mish", "ma", "bidun", "kalla", "لا", "ليس", "ما", "مش", "بدون", "كلا"],
    "pl": ["nie", "brak", "bez", "nie ma", "ani", "zadnych", "nie czuje", "nigdy"],
    "so": ["ma", "maya", "ma jiro", "ma qabo", "aan", "waxba", "ma hayo"],
    "ro": ["nu", "nici", "fara", "n-am", "nu am", "deloc", "nimic"],
    "en": ["no", "not", "dont", "don't", "doesnt", "doesn't", "denies", "without", "never", "none"]
}

# ============================================================
# 3. STAFF LEXICON (All 17 Queries × 10 Languages)
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
# 4. PATIENT CLINICAL DOMAINS (All 9 Languages)
# ============================================================
PATIENT_CLINICAL_DOMAINS = {
    "chest_pain": {
        "urgent": True,
        "tokens": {
            "ta": ["nenji vali", "nenju vali", "nenjil vali", "maarbu vali", "நெஞ்சு வலி", "நெஞ்சில் வலி"],
            "hi": ["seene mein dard", "chhati mein dard", "seene me dard", "सीने में दर्द"],
            "ml": ["nenju vedana", "nenjil vedana", "നെഞ്ചുവേദന"],
            "bn": ["buke byatha", "buke batha", "বুকে ব্যথা"],
            "ur": ["seene mein dard", "seenay mein dard", "سینے میں درد"],
            "ar": ["alam fi al sadr", "alam fi sadr", "alam sadr", "ألم في الصدر"],
            "pl": ["bol w klatce piersiowej", "bol w klatce", "ból w klatce piersiowej"],
            "so": ["laab xanuun", "xabad xanuun", "xanuunka laabta"],
            "ro": ["durere in piept", "durere în piept", "dureri in piept"],
            "en": ["chest pain", "tight chest", "crushing chest"]
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
            "ta": ["moochu varadhu", "moochu pidikuthu", "moochu thinaral", "மூச்சு திணறல்"],
            "hi": ["saans lene mein takleef", "saans phoolna", "सांस लेने में तकलीफ"],
            "ml": ["shwasam muttunnu", "shwasam muttal", "ശ്വാസതടസ്സം"],
            "bn": ["shas kosto", "shash nite koshto", "শ্বাসকষ্ট"],
            "ur": ["saans lene mein dushwari", "saans phoolna", "سانس لینے میں دشواری"],
            "ar": ["diq tanaffus", "diq fi tanaffus", "ضيق في التنفس"],
            "pl": ["dusznosc", "brak tchu", "duszność"],
            "so": ["neefsasho adag", "neef qabasho"],
            "ro": ["respiratie grea", "lipsa de aer", "dificultati de respiratie"],
            "en": ["difficulty breathing", "shortness of breath", "struggling to breathe"]
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
            "ta": ["iratham", "ratham", "இரத்தப்போக்கு"],
            "hi": ["khoon", "khoon beh raha", "खून"],
            "ml": ["raktham", "chora", "രക്തസ്രാവം"],
            "bn": ["rokto", "রক্তপাত"],
            "ur": ["khoon", "خون"],
            "ar": ["nazif", "dam", "نزيف"],
            "pl": ["krwawienie", "krew"],
            "so": ["dhiig", "dhiig bax"],
            "ro": ["sangerare", "hemoragie", "sângerare"],
            "en": ["bleeding", "heavy blood"]
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
            "ta": ["mayakkam", "mayangi", "மயக்கம்"],
            "hi": ["behosh", "chakkar behosh", "बेहोश"],
            "ml": ["bodhakshayam", "തലകറങ്ങി വീണു"],
            "bn": ["agyan", "অজ্ঞান"],
            "ur": ["be hosh", "بے ہوش"],
            "ar": ["ighma", "إغماء"],
            "pl": ["omdlenie", "stracil przytomnosc"],
            "so": ["miyir beel"],
            "ro": ["lesin", "inconstient", "leșin"],
            "en": ["unconscious", "passed out", "fainted", "collapsed"]
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
            "ta": ["thala vali", "thalai vali", "தலைவலி"],
            "hi": ["sir dard", "sar dard", "सिर दर्द"],
            "ml": ["thala vedana", "തലവേദന"],
            "bn": ["matha byatha", "মাথা ব্যথা"],
            "ur": ["sar dard", "سر درد"],
            "ar": ["suda", "sudaa", "صداع"],
            "pl": ["bol glowy", "ból głowy"],
            "so": ["madax xanuun"],
            "ro": ["durere de cap"],
            "en": ["headache", "head pain"]
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
            "ta": ["kaichal", "kaaichal", "suram", "காய்ச்சல்"],
            "hi": ["bukhar", "tez bukhar", "बुखार"],
            "ml": ["pani", "പനി"],
            "bn": ["jwor", "jor", "জ্বর"],
            "ur": ["bukhar", "بخار"],
            "ar": ["humma", "حمى"],
            "pl": ["goraczka", "gorączka"],
            "so": ["qandho"],
            "ro": ["febra", "febră"],
            "en": ["fever", "high temperature"]
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
            "ur": ("I do not have a fever.", "मुझे بخار نہیں ہے۔"),
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
            "ta": ["vayiru vali", "vayitru vali", "வயிற்று வலி"],
            "hi": ["pet dard", "पेट दर्द"],
            "ml": ["vayaru vedana", "വയറുവേദന"],
            "bn": ["pet byatha", "পেটে ব্যথা"],
            "ur": ["pet mein dard", "pait dard", "پیٹ میں درد"],
            "ar": ["alam batn", "ألم في البطن"],
            "pl": ["bol brzucha", "ból brzucha"],
            "so": ["calool xanuun"],
            "ro": ["durere de stomac"],
            "en": ["stomach pain", "tummy ache", "abdominal pain"]
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
            "ta": ["mayakkam", "thala suttrudhal", "தலைசுற்றல்"],
            "hi": ["chakkar", "chakkar aana", "चक्कर"],
            "ml": ["thalakarakkam", "തലകറക്കം"],
            "bn": ["matha ghora", "মাথা ঘোরা"],
            "ur": ["chakkar", "چکر"],
            "ar": ["dawkha", "دوخة"],
            "pl": ["zawroty glowy", "zawroty głowy"],
            "so": ["wareer"],
            "ro": ["ameteala", "amețeală"],
            "en": ["dizziness", "dizzy", "lightheaded"]
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
            "ur": ("I do not feel dizzy.", "مجھے چکر نہیں آ رہے ہیں۔"),
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
            "ta": ["vaanthi", "வாந்தி"],
            "hi": ["ulti", "उल्टी"],
            "ml": ["chardhi", "ഛർദ്ദി"],
            "bn": ["bomi", "বমি"],
            "ur": ["ulti", "الٹی"],
            "ar": ["qay", "قيء"],
            "pl": ["wymioty", "nudnosci"],
            "so": ["matag"],
            "ro": ["varsaturi", "vărsături"],
            "en": ["vomiting", "throwing up", "sickness"]
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
            "ur": ("I do not have vomiting.", "مجھے الٹی نہیں آ رہی ہے۔"),
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
            "ta": ["irumal", "இருமல்"],
            "hi": ["khansi", "खांसी"],
            "ml": ["chuma", "ചുമ"],
            "bn": ["kashi", "কাশি"],
            "ur": ["khansi", "کھانسی"],
            "ar": ["sual", "سعال"],
            "pl": ["kaszel"],
            "so": ["qufac"],
            "ro": ["tuse"],
            "en": ["cough", "coughing"]
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
            "ur": ("I do not have a cough.", "مجھے کھانسی نہیں ہے۔"),
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
            "ta": ["thondai vali", "தொண்டை வலி"],
            "hi": ["gale mein dard", "गले में दर्द"],
            "ml": ["thonda vedana", "തൊണ്ടവേദന"],
            "bn": ["gola byatha", "গলা ব্যথা"],
            "ur": ["galay mein dard", "گلے میں درد"],
            "ar": ["iltihab halq", "ألم في الحلق"],
            "pl": ["bol gardla", "ból gardła"],
            "so": ["dhuun xanuun"],
            "ro": ["durere in gat", "durere în gât"],
            "en": ["sore throat", "throat pain"]
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
            "ta": ["muthugu vali", "iduppu vali", "முதுகு வலி"],
            "hi": ["peeth dard", "kamar dard", "पीठ दर्द"],
            "ml": ["puram vedana", "naduv vedana", "പുറംവേദന"],
            "bn": ["pither byatha", "komor byatha", "পিঠের ব্যথা"],
            "ur": ["kamar dard", "کمر درد"],
            "ar": ["alam zahr", "ألم في الظهر"],
            "pl": ["bol plecow", "ból pleców"],
            "so": ["dhabar xanuun"],
            "ro": ["durere de spate"],
            "en": ["back pain", "lower back pain"]
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
            "ta": ["thol thadippu", "arippu", "தோல் தடிப்பு"],
            "hi": ["daane", "khujli", "दाने"],
            "ml": ["thadippu", "chorichil", "തടിപ്പ്"],
            "bn": ["chulkani", "fusuri", "ফুসকুড়ি"],
            "ur": ["daanay", "kharish", "خارش"],
            "ar": ["tafah jildi", "hikkah", "طفح جلدي"],
            "pl": ["wysypka", "swedzenie"],
            "so": ["finan", "cuncun"],
            "ro": ["eruptie cutanata", "mancarime"],
            "en": ["skin rash", "rash", "itching"]
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
