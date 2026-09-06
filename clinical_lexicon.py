"""
MedOriva AI — Comprehensive 9-Language Clinical Lexicon
Equal, in-depth phonetic (Romanized) and native script coverage for:
1. Tamil (ta)     2. Hindi (hi)     3. Malayalam (ml)
4. Polish (pl)    5. Arabic (ar)    6. Urdu (ur)
7. Bengali (bn)   8. Somali (so)    9. Romanian (ro)
"""

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

# ============================================================
# 1. NEGATION DICTIONARY (PHONETIC & NATIVE SCRIPT)
# Checked first to prevent false triage alarms across all 9 languages
# ============================================================
NEGATION_DICTIONARY = {
    "ta": ["illai", "illa", "ila", "varadhu", "varala", "kidayathu", "illamal", "இல்லை", "இல்ல", "கிடையாது"],
    "hi": ["nahi", "nahin", "nhi", "na", "mat", "bina", "kuch nahi", "नहीं", "ना", "नहीं है"],
    "ml": ["illa", "alla", "illathe", "illaatha", "koodilla", "ഇല്ല", "അല്ല", "ഇല്ലാതെ"],
    "pl": ["nie", "brak", "bez", "nie ma", "ani", "zadnych", "nie czuje", "nigdy"],
    "ar": ["la", "laysa", "mish", "mesh", "ma", "mashi", "bidun", "kalla", "لا", "ليس", "ما", "مش"],
    "ur": ["nahi", "nahin", "na", "bina", "baghair", "نہیں", "نہ", "بغیر"],
    "bn": ["na", "ni", "nay", "chara", "nei", "nai", "না", "নেই", "নয়", "নাই"],
    "so": ["ma", "maya", "ma jiro", "ma qabo", "aan", "waxba", "ma hayo", "la'aan"],
    "ro": ["nu", "nici", "fara", "fără", "n-am", "nu am", "deloc", "nimic"]
}

# ============================================================
# 2. STAFF CLINICAL INTAKE PROMPTS (16 Core Questions x 9 Languages)
# Guaranteed 0ms offline response for live demos
# ============================================================
STAFF_LEXICON = {
    "GOOD_MORNING": {
        "ta": "காலை வணக்கம். நான் உங்களுக்கு எப்படி உதவ முடியும்?",
        "hi": "सुप्रभात। मैं आपकी कैसे मदद कर सकता हूँ?",
        "ml": "സുപ്രഭാതം. എനിക്ക് നിങ്ങളെ എങ്ങനെ സഹായിക്കാനാകും?",
        "pl": "Dzień dobry. W czym mogę Panu/Pani pomóc?",
        "ar": "صباح الخير. كيف يمكنني مساعدتك اليوم؟",
        "ur": "صبح بخیر۔ میں آپ کی کیسے مدد کر سکتا ہوں؟",
        "bn": "সুপ্রভাত। আমি আপনাকে কীভাবে সাহায্য করতে পারি?",
        "so": "Subax wanaagsan. Sideen kuu caawin karaa maanta?",
        "ro": "Bună dimineața. Cu ce vă pot ajuta astăzi?"
    },
    "APPOINTMENT": {
        "ta": "உங்களுக்கு முன்பதிவு செய்யப்பட்ட சந்திப்பு உள்ளதா?",
        "hi": "क्या आपकी पहले से अपॉइंटमेंट है?",
        "ml": "നിങ്ങൾക്ക് മുൻകൂട്ടി നിശ്ചയിച്ച അപ്പോയിന്റ്മെന്റ് ഉണ്ടോ?",
        "pl": "Czy ma Pan/Pani zarezerwowaną wizytę?",
        "ar": "هل لديك موعد مسبق محجوز؟",
        "ur": "کیا آپ کی پہلے سے کوئی اپائنٹمنٹ بک ہے؟",
        "bn": "আপনার কি আগে থেকে বুক করা অ্যাপয়েন্টমেন্ট আছে?",
        "so": "Ballan ma leedahay mise waad iska timid?",
        "ro": "Aveți o programare făcută în prealabil?"
    },
    "NAME_DOB": {
        "ta": "உங்கள் முழுப் பெயரையும் பிறந்த தேதியையும் சொல்ல முடியுமா?",
        "hi": "क्या मैं आपका पूरा नाम और जन्म तिथि जान सकता हूँ?",
        "ml": "നിങ്ങളുടെ മുഴുവൻ പേരും ജനനത്തീയതിയും ദയവായി പറയാമോ?",
        "pl": "Czy mogę prosić o Pana/Pani imię, nazwisko i datę urodzenia?",
        "ar": "هل يمكنني معرفة اسمك الكامل وتاريخ ميلادك من فضلك؟",
        "ur": "براہ کرم اپنا پورا نام اور تاریخ پیدائش بتائیں۔",
        "bn": "আপনার পুরো নাম এবং জন্ম তারিখ দয়া করে বলবেন?",
        "so": "Fadlan ma ii sheegi kartaa magacaaga buuxa iyo taariikhda dhalashadaada?",
        "ro": "Îmi puteți spune numele complet și data nașterii, vă rog?"
    },
    "NHS_NUMBER": {
        "ta": "உங்களிடம் என்.எச்.எஸ் (NHS) எண் உள்ளதா?",
        "hi": "क्या आपके पास आपका एनएचएस (NHS) नंबर है?",
        "ml": "നിങ്ങളുടെ പക്കൽ എൻ.എച്ച്.എസ് (NHS) നമ്പർ ഉണ്ടോ?",
        "pl": "Czy ma Pan/Pani przy sobie swój numer NHS?",
        "ar": "هل لديك رقم NHS الوطني الخاص بك؟",
        "ur": "کیا آپ کے پاس آپ کا این ایچ ایس (NHS) نمبر ہے؟",
        "bn": "আপনার কাছে কি আপনার এনএইচএস (NHS) নম্বর আছে?",
        "so": "Ma haysataa lambarkaaga caafimaadka ee NHS?",
        "ro": "Aveți la dumneavoastră numărul de înregistrare NHS?"
    },
    "TAKE_SEAT": {
        "ta": "தயவு செய்து காத்திருப்பு அறையில் உட்காருங்கள். மருத்துவர் விரைவில் அழைப்பார்.",
        "hi": "कृपया प्रतीक्षा कक्ष में बैठिए। डॉक्टर जल्द ही आपको बुलाएंगे।",
        "ml": "ദയവായി വെയ്റ്റിംഗ് ഏരിയയിൽ ഇരിക്കുക. ഡോക്ടർ ഉടൻ വിളിക്കും.",
        "pl": "Proszę usiąść w poczekalni. Lekarz wkrótce Pana/Panią poprosi.",
        "ar": "يرجى الانتظار والجلوس في القاعة. سيناديك الطبيب بعد قليل.",
        "ur": "براہ کرم انتظار گاہ میں تشریف رکھیں۔ ڈاکٹر جلد آپ کو بلا لیں گے۔",
        "bn": "দয়া করে অপেক্ষা করার স্থানে বসুন। ডাক্তার শীঘ্রই আপনাকে ডাকবেন।",
        "so": "Fadlan fadhiiso qolka sugitaanka. Dhakhtarka ayaa hadhow kuu yeeri doona.",
        "ro": "Vă rugăm să luați loc în sala de așteptare. Medicul vă va striga în curând."
    },
    "INTERPRETER": {
        "ta": "மருத்துவ ஆலோசனைக்கு உங்களுக்கு மொழிபெயர்ப்பாளர் தேவையா?",
        "hi": "क्या आपको डॉक्टर से बात करने के लिए दुभाषिए की आवश्यकता है?",
        "ml": "ഡോക്ടറുമായി സംസാരിക്കാൻ ഒരു ദ്വിഭാഷിയുടെ സഹായം ആവശ്യമുണ്ടോ?",
        "pl": "Czy potrzebuje Pan/Pani profesjonalnego tłumacza ustnego?",
        "ar": "هل تحتاج إلى مترجم فوري لمساعدتك أثناء الاستشارة؟",
        "ur": "کیا آپ کو ڈاکٹر سے معائنے کے دوران ترجمان کی ضرورت ہے؟",
        "bn": "ডাক্তারের সাথে কথা বলার জন্য আপনার কি কোনো দোভাষীর প্রয়োজন?",
        "so": "Ma u baahan tahay turjubaan xirfadle ah oo ku caawiya?",
        "ro": "Aveți nevoie de un interpret pentru consultația medicală?"
    },
    "WHERE_IS_PAIN": {
        "ta": "உங்கள் வலி உடலின் எந்தப் பகுதியில் இருக்கிறது?",
        "hi": "आपको शरीर के किस हिस्से में दर्द हो रहा है?",
        "ml": "ശരീരത്തിൽ എവിടെയാണ് കൃത്യമായി വേദന അനുഭവപ്പെടുന്നത്?",
        "pl": "W którym miejscu dokładnie odczuwa Pan/Pani ból?",
        "ar": "أين تشعر بالألم بالضبط في جسمك؟",
        "ur": "آپ کو جسم کے کس حصے میں درد محسوس ہو رہا ہے؟",
        "bn": "শরীরের ঠিক কোন অংশে আপনার ব্যথা হচ্ছে?",
        "so": "Xanuunku xaggee buu si sax ah kuugu hayaa?",
        "ro": "Unde anume în corp simțiți această durere?"
    },
    "HOW_LONG_PAIN": {
        "ta": "உங்களுக்கு எவ்வளவு காலமாக இந்த வலி இருக்கிறது?",
        "hi": "आपको कितने समय (दिनों या घंटों) से यह दर्द हो रहा है?",
        "ml": "നിങ്ങൾക്ക് എത്ര ദിവസമായി അല്ലെങ്കിൽ സമയമായി ഈ വേദനയുണ്ട്?",
        "pl": "Od jak dawna (godzin, dni) odczuwa Pan/Pani ten ból?",
        "ar": "منذ متى وأنت تعاني من هذا الألم؟",
        "ur": "آپ کو کتنے گھنٹوں یا دنوں سے یہ درد ہو رہا ہے؟",
        "bn": "আপনার কতক্ষণ বা কতদিন ধরে এই ব্যথা হচ্ছে?",
        "so": "Muddo intee leeg ayaad xanuunkan dareemaysay?",
        "ro": "De cât timp (ore sau zile) aveți această durere?"
    },
    "DO_YOU_HAVE_CHEST_PAIN": {
        "ta": "உங்களுக்கு நெஞ்சு வலி, அழுத்தம் அல்லது பாரம் உள்ளதா?",
        "hi": "क्या आपको सीने में दर्द, भारीपन या दबाव महसूस हो रहा है?",
        "ml": "നിങ്ങൾക്ക് നെഞ്ചിൽ വേദനയോ കടുത്ത ഭാരമോ തോന്നുന്നുണ്ടോ?",
        "pl": "Czy odczuwa Pan/Pani ból, ucisk lub pieczenie w klatce piersiowej?",
        "ar": "هل تشعر بألم، ثقل أو ضغط حاد في الصدر؟",
        "ur": "کیا آپ کو سینے میں درد، جلن یا دباؤ محسوس ہو رہا ہے؟",
        "bn": "আপনার কি বুকে ব্যথা, ভারি ভাব বা চাপ অনুভূত হচ্ছে?",
        "so": "Ma dareemaysaa xanuun, cadaadis ama culeys laabta ah?",
        "ro": "Simțiți durere, presiune sau apăsare în piept?"
    },
    "DO_YOU_HAVE_BREATHING": {
        "ta": "உங்களுக்கு மூச்சு விடுவதில் சிரமம் அல்லது மூச்சுத் திணறல் உள்ளதா?",
        "hi": "क्या आपको सांस लेने में कोई कठिनाई या घुटन हो रही है?",
        "ml": "നിങ്ങൾക്ക് ശ്വാസമെടുക്കാൻ എന്തെങ്കിലും ബുദ്ധിമുട്ടുണ്ടോ?",
        "pl": "Czy ma Pan/Pani trudności ze złapaniem tchu lub duszności?",
        "ar": "هل تعاني من صعوبة أو ضيق شديد في التنفس؟",
        "ur": "کیا آپ کو سانس لینے میں کوئی دشواری یا تنگی پیش آ رہی ہے؟",
        "bn": "আপনার কি শ্বাস নিতে কোনো সমস্যা বা শ্বাসকষ্ট হচ্ছে?",
        "so": "Dhib ma kugu tahay neefsashadu mise neeftaada ayaa kugu dhegaysa?",
        "ro": "Aveți dificultăți de respirație sau senzație de sufocare?"
    },
    "DO_YOU_HAVE_FEVER": {
        "ta": "உங்களுக்கு காய்ச்சல் அல்லது உடல் நடுக்கம் உள்ளதா?",
        "hi": "क्या आपको तेज बुखार या कंपकंपी महसूस हो रही है?",
        "ml": "നിങ്ങൾക്ക് പനിയോ വിറയലോ ഉണ്ടോ?",
        "pl": "Czy ma Pan/Pani gorączkę lub dreszcze?",
        "ar": "هل تعاني من حمى أو ارتفاع في درجة الحرارة؟",
        "ur": "کیا آپ کو تیز بخار یا کپکپی ہو رہی ہے؟",
        "bn": "আপনার কি জ্বর বা কাঁপুনি অনুভূত হচ্ছে?",
        "so": "Ma qabtaa xumad ama qandho daran?",
        "ro": "Aveți febră mare sau frisoane?"
    },
    "SEVERITY_SCALE": {
        "ta": "1 முதல் 10 வரை, உங்கள் வலி எவ்வளவு தீவிரமாக உள்ளது? (10 என்பது மிகத் தீவிரமானது).",
        "hi": "1 से 10 के पैमाने पर आपका दर्द कितना तीव्र है? (10 असहनीय दर्द है)।",
        "ml": "1 മുതൽ 10 വരെയുള്ള അളവിൽ നിങ്ങളുടെ വേദന എത്രത്തോളമുണ്ട്?",
        "pl": "W skali od 1 do 10, jak silny jest ten ból? (10 to ból nie do zniesienia).",
        "ar": "على مقياس من 1 إلى 10، ما مدى شدة ألمك؟ (10 تعني ألم شديد جداً).",
        "ur": "1 سے 10 کے پیمانے پر آپ کا درد کتنا شدید ہے؟ (10 شدید ترین درد ہے)۔",
        "bn": "১ থেকে ১০ এর স্কেলে আপনার ব্যথা কতটা তীব্র? (১০ মানে তীব্র অসহনীয় ব্যথা)।",
        "so": "Qiyaastii 1 ilaa 10, intee in le'eg ayuu xanuunkaagu daran yahay?",
        "ro": "Pe o scară de la 1 la 10, cât de severă este durerea dumneavoastră?"
    },
    "ALLERGIES_QUERY": {
        "ta": "உங்களுக்கு பென்சிலின் அல்லது ஏதேனும் மருந்துகளால் ஒவ்வாமை (Allergy) உள்ளதா?",
        "hi": "क्या आपको किसी दवा (जैसे पेनिसिलिन) से कोई एलर्जी है?",
        "ml": "നിങ്ങൾക്ക് എന്തെങ്കിലും മരുന്നുകളോട് അലർജി ഉണ്ടോ?",
        "pl": "Czy ma Pan/Pani uczulenie na jakiekolwiek leki, np. penicylinę?",
        "ar": "هل لديك أي حساسية تجاه أدوية معينة مثل البنسلين؟",
        "ur": "کیا آپ کو کسی دوائی، جیسے پینسلین سے الرجی ہے؟",
        "bn": "আপনার কি কোনো ওষুধ বা পেনিসিলিনে অ্যালার্জি আছে?",
        "so": "Ma qabtaa wax xasaasiyad ah oo ku saabsan daawooyinka?",
        "ro": "Sunteți alergic la vreun medicament, de exemplu la penicilină?"
    },
    "MEDICATION_QUERY": {
        "ta": "நீங்கள் தற்போது ஏதேனும் வழக்கமான மாத்திரைகள் எடுத்துக்கொள்கிறீர்களா?",
        "hi": "क्या आप वर्तमान में नियमित रूप से कोई दवाइयां ले रहे हैं?",
        "ml": "നിങ്ങൾ നിലവിൽ എന്തെങ്കിലും മരുന്നുകൾ പതിവായി കഴിക്കുന്നുണ്ടോ?",
        "pl": "Czy przyjmuje Pan/Pani obecnie jakiekolwiek stałe leki?",
        "ar": "هل تتناول حالياً أي أدوية بوصفة طبية بانتظام؟",
        "ur": "کیا آپ اس وقت باقاعدگی سے کوئی دوائیں لے رہے ہیں؟",
        "bn": "আপনি কি বর্তমানে কোনো প্রেসক্রিপশন ওষুধ নিয়মিত খাচ্ছেন?",
        "so": "Ma qaadataa wax daawooyin joogto ah xilligan?",
        "ro": "Luați în mod regulat vreun tratament medicamentos în prezent?"
    },
    "DOCTOR_NOW": {
        "ta": "மருத்துவர் இப்போது உங்களை ஆலோசனை அறையில் சந்திப்பார்.",
        "hi": "डॉक्टर अब आपको परामर्श कक्ष में बुला रहे हैं।",
        "ml": "ഡോക്ടർ ഇപ്പോൾ കൺസൾട്ടേഷൻ റൂമിൽ നിങ്ങളെ കാണും.",
        "pl": "Lekarz prosi teraz Pana/Panią do gabinetu.",
        "ar": "الطبيب مستعد لاستقبالك الآن في غرفة الكشف.",
        "ur": "ڈاکٹر اب آپ کو معائنے کے کمرے میں دیکھ رہے ہیں۔",
        "bn": "ডাক্তার এখন আপনাকে কনসাল্টেশন রুমে ডাকছেন।",
        "so": "Dhakhtarka ayaa hadda kugu qaabilaya qolka baaritaanka.",
        "ro": "Medicul vă va primi acum în cabinetul de consultații."
    },
    "DO_YOU_HAVE_PAIN": {
        "ta": "உங்களுக்கு உடலில் ஏதேனும் வலி இருக்கிறதா?",
        "hi": "क्या आपको कहीं कोई दर्द हो रहा है?",
        "ml": "നിങ്ങൾക്ക് എവിടെയെങ്കിലും വേദനയുണ്ടോ?",
        "pl": "Czy odczuwa Pan/Pani w tej chwili jakikolwiek ból?",
        "ar": "هل تشعر بأي ألم حالياً في جسمك؟",
        "ur": "کیا آپ کو جسم میں کہیں درد محسوس ہو رہا ہے؟",
        "bn": "আপনার কি শরীরে কোনো ব্যথা আছে?",
        "so": "Xanuun ma dareemaysaa meel jirkaaga ka mid ah?",
        "ro": "Aveți vreo durere în acest moment?"
    }
}

# ============================================================
# 3. PATIENT CLINICAL VOCABULARY ACROSS ALL 9 LANGUAGES
# 10 Clinical Domains with rich Romanized & Native stems
# ============================================================
PATIENT_CLINICAL_DOMAINS = {
    # ── 1. CARDIAC & CHEST (CRITICAL TRIAGE) ──
    "chest pain": {
        "urgent": True,
        "tokens": {
            "ta": ["nenji", "nenju", "nenjil", "enji", "enju", "maar", "marbu", "நெஞ்சு", "நெஞ்சில்", "மார்பு"],
            "hi": ["seene", "sene", "chhati", "chest", "chati", "dil", "सीने", "छाती", "दिल"],
            "ml": ["nenjil", "nenju", "hridaya", "maril", "നെഞ്ചിൽ", "നെഞ്ചു", "ഹൃദയം"],
            "pl": ["klatce", "klatki", "klatka", "sercu", "piersiowej", "dusznica", "sciska"],
            "ar": ["sadr", "sadri", "sedr", "qalb", "qalbi", "waja3", "waga3", "الصدر", "صدري", "قلب"],
            "ur": ["seenay", "seene", "chhati", "dil", "سینے", "دل", "چھاتی"],
            "bn": ["buke", "buk", "buker", "hridoy", "বুকে", "বুক", "হৃদয়"],
            "so": ["laab", "laabta", "wadnaha", "wadne", "xabad", "xabadka"],
            "ro": ["piept", "pieptului", "inima", "torace", "stern", "apasa"]
        },
        "affirmative": {
            "ta": ("I have chest pain.", "எனக்கு நெஞ்சு வலி இருக்கிறது."),
            "hi": ("I have chest pain.", "मुझे सीने में दर्द है।"),
            "ml": ("I have chest pain.", "എനിക്ക് നെഞ്ചുവേദനയുണ്ട്."),
            "pl": ("I have chest pain.", "Mam silny ból w klatce piersiowej."),
            "ar": ("I have chest pain.", "أشعر بألم وضغط في الصدر."),
            "ur": ("I have chest pain.", "میرے سینے میں درد ہے۔"),
            "bn": ("I have chest pain.", "আমার বুকে ব্যথা আছে।"),
            "so": ("I have chest pain.", "Waxaan dareemayaa xanuunka laabta."),
            "ro": ("I have chest pain.", "Am dureri în piept.")
        },
        "negative": {
            "ta": ("I do not have chest pain.", "எனக்கு நெஞ்சு வலி இல்லை."),
            "hi": ("I do not have chest pain.", "मुझे सीने में कोई दर्द नहीं है।"),
            "ml": ("I do not have chest pain.", "എനിക്ക് നെഞ്ചുവേദനയില്ല."),
            "pl": ("I do not have chest pain.", "Nie mam bólu w klatce piersiowej."),
            "ar": ("I do not have chest pain.", "ليس لدي أي ألم في الصدر."),
            "ur": ("I do not have chest pain.", "میرے سینے میں کوئی درد نہیں ہے۔"),
            "bn": ("I do not have chest pain.", "আমার বুকে কোনো ব্যথা নেই।"),
            "so": ("I do not have chest pain.", "Ma qabo wax xanuun laabta ah."),
            "ro": ("I do not have chest pain.", "Nu am dureri în piept.")
        }
    },

    # ── 2. RESPIRATORY & BREATHING (CRITICAL TRIAGE) ──
    "breathing difficulty": {
        "urgent": True,
        "tokens": {
            "ta": ["moochu", "swasam", "moochu vida", "thinaral", "திணறல்", "மூச்சு", "சுவாசம்"],
            "hi": ["saans", "sans", "dam", "saans phool", "ghutan", "सांस", "दम", "घुटन"],
            "ml": ["shwasam", "shwasam mutt", "shwasa", "ശ്വാസം", "ശ്വാസതടസ്സം"],
            "pl": ["oddychac", "oddychanie", "dusznosc", "dusznosci", "duszno", "tchu", "dusze"],
            "ar": ["tanaffus", "nafas", "diq", "tanaffos", "makhnouq", "atnaffas", "تنفس", "ضيق"],
            "ur": ["saans", "sans ruk", "dum", "sans lene", "سانس", "دم"],
            "bn": ["shwash", "dom", "hapan", "shwaskoshto", "শ্বাস", "দম", "হাঁপানি"],
            "so": ["neefsasho", "neefso", "neefta", "dhegaysa", "neefsashada"],
            "ro": ["respiratie", "aer", "respira", "sufocare", "respir", "sufoc"]
        },
        "affirmative": {
            "ta": ("I have difficulty breathing.", "எனக்கு மூச்சு விடுவதில் சிரமம் உள்ளது."),
            "hi": ("I am having difficulty breathing.", "मुझे सांस लेने में बहुत तकलीफ हो रही है।"),
            "ml": ("I have difficulty breathing.", "എനിക്ക് ശ്വാസമെടുക്കാൻ ബുദ്ധിമുട്ടുണ്ട്."),
            "pl": ("I have difficulty breathing.", "Mam trudności z oddychaniem i duszności."),
            "ar": ("I have difficulty breathing.", "أعاني من صعوبة شديدة في التنفس."),
            "ur": ("I have difficulty breathing.", "مجھے سانس لینے میں دشواری ہو رہی ہے۔"),
            "bn": ("I have difficulty breathing.", "আমার শ্বাস নিতে কষ্ট হচ্ছে।"),
            "so": ("I have difficulty breathing.", "Waxaan dhib ku qabaa neefsashada."),
            "ro": ("I have difficulty breathing.", "Am dificultăți mari de respirație.")
        },
        "negative": {
            "ta": ("I do not have difficulty breathing.", "எனக்கு மூச்சுத் திணறல் இல்லை."),
            "hi": ("I do not have difficulty breathing.", "मुझे सांस लेने में कोई तकलीफ नहीं है।"),
            "ml": ("I do not have difficulty breathing.", "എനിക്ക് ശ്വാസതടസ്സമില്ല."),
            "pl": ("I do not have difficulty breathing.", "Nie mam trudności z oddychaniem."),
            "ar": ("I do not have difficulty breathing.", "لا أواجه أي صعوبة في التنفس."),
            "ur": ("I do not have difficulty breathing.", "مجھے سانس لینے میں کوئی مسئلہ نہیں ہے۔"),
            "bn": ("I do not have difficulty breathing.", "আমার কোনো শ্বাসকষ্ট নেই।"),
            "so": ("I do not have difficulty breathing.", "Dhib kuma qabo neefsashada."),
            "ro": ("I do not have difficulty breathing.", "Nu am dificultăți de respirație.")
        }
    },

    # ── 3. SEVERE BLEEDING (CRITICAL TRIAGE) ──
    "bleeding": {
        "urgent": True,
        "tokens": {
            "ta": ["iratham", "ratham", "rathapokku", "இரத்தம்", "இரத்தப்போக்கு"],
            "hi": ["khoon", "rakht", "lahu", "खून", "रक्तस्राव"],
            "ml": ["raktham", "chora", "rakthasravam", "രക്തം", "രക്തസ്രാവം"],
            "pl": ["krwawienie", "krew", "krwawi", "krwotok", "krwawie"],
            "ar": ["dam", "nazif", "yanzif", "nazf", "دم", "نزيف"],
            "ur": ["khoon", "lahu", "خون", "خون بہنا"],
            "bn": ["rokto", "rokter", "rokto pata", "রক্ত", "রক্তপাত"],
            "so": ["dhiig", "dhiigbax", "dhiig badan"],
            "ro": ["sange", "sangerare", "hemoragie", "sângerez", "sânge"]
        },
        "affirmative": {
            "ta": ("I have bleeding.", "எனக்கு இரத்தப்போக்கு உள்ளது."),
            "hi": ("I have bleeding.", "खून बह रहा है।"),
            "ml": ("I have bleeding.", "രക്തസ്രാവം ഉണ്ടാകുന്നുണ്ട്."),
            "pl": ("I am bleeding.", "Mocno krwawię."),
            "ar": ("I am bleeding.", "أعاني من نزيف دموي."),
            "ur": ("I am bleeding.", "خون بہہ رہا ہے۔"),
            "bn": ("I am bleeding.", "রক্তপাত হচ্ছে।"),
            "so": ("I am bleeding.", "Dhiig ayaa iga socda."),
            "ro": ("I am bleeding.", "Am o sângerare abundentă.")
        },
        "negative": {
            "ta": ("There is no bleeding.", "இரத்தப்போக்கு எதுவும் இல்லை."),
            "hi": ("There is no bleeding.", "कोई खून नहीं बह रहा है।"),
            "ml": ("There is no bleeding.", "രക്തസ്രാവമില്ല."),
            "pl": ("There is no bleeding.", "Nie ma krwawienia."),
            "ar": ("There is no bleeding.", "لا يوجد أي نزيف."),
            "ur": ("There is no bleeding.", "خون نہیں بہہ رہا ہے۔"),
            "bn": ("There is no bleeding.", "কোনো রক্তপাত নেই।"),
            "so": ("There is no bleeding.", "Wax dhiig ah ma socdo."),
            "ro": ("There is no bleeding.", "Nu sângerez.")
        }
    },

    # ── 4. STROKE, FAINT & DIZZINESS ──
    "dizziness": {
        "urgent": False,
        "tokens": {
            "ta": ["mayakkam", "thalai suthu", "sutharuthu", "மயக்கம்", "சுற்றல்"],
            "hi": ["chakkar", "behosh", "chakar", "behoshi", "चक्कर", "बेहोशी"],
            "ml": ["thalakarakkam", "bodhakshayam", "തലകറക്കം", "ബോധക്ഷയം"],
            "pl": ["zawroty", "omdlenie", "kreci mi sie", "slabo", "omdlec"],
            "ar": ["dawkha", "dawar", "ighma", "dayekh", "دوخة", "دوار", "إغماء"],
            "ur": ["chakkar", "behosh", "ghashi", "چکر", "غشی", "بے ہوش"],
            "bn": ["matha ghora", "ogyan", "matha ghurche", "মাথা ঘোরা", "অজ্ঞান"],
            "so": ["dawakhaad", "wareer", "miyir beel", "wareeraya"],
            "ro": ["ameteala", "ametit", "lesin", "amețeală", "leșin"]
        },
        "affirmative": {
            "ta": ("I feel dizzy and faint.", "எனக்கு தலை சுற்றல் மற்றும் மயக்கம் வருகிறது."),
            "hi": ("I feel dizzy and faint.", "मुझे चक्कर और बेहोशी जैसा महसूस हो रहा है।"),
            "ml": ("I feel dizzy.", "എനിക്ക് തലകറക്കം തോന്നുന്നു."),
            "pl": ("I feel dizzy.", "Kręci mi się w głowie i jest mi słabo."),
            "ar": ("I feel dizzy.", "أشعر بدوار ودوخة شديدة."),
            "ur": ("I feel dizzy.", "مجھے چکر اور غشی محسوس ہو رہی ہے۔"),
            "bn": ("I feel dizzy.", "আমার মাথা ঘুরছে এবং দুর্বল লাগছে।"),
            "so": ("I feel dizzy.", "Waxaan dareemayaa dawakhaad iyo wareer."),
            "ro": ("I feel dizzy.", "Mă simt foarte amețit.")
        },
        "negative": {
            "ta": ("I do not feel dizzy.", "எனக்கு தலை சுற்றல் இல்லை."),
            "hi": ("I do not feel dizzy.", "मुझे चक्कर नहीं आ रहे हैं।"),
            "ml": ("I do not feel dizzy.", "എനിക്ക് തലകറക്കമില്ല."),
            "pl": ("I do not feel dizzy.", "Nie kręci mi się w głowie."),
            "ar": ("I do not feel dizzy.", "لا أشعر بأي دوخة."),
            "ur": ("I do not feel dizzy.", "مجھے چکر نہیں آ رہے ہیں۔"),
            "bn": ("I do not feel dizzy.", "আমার মাথা ঘুরছে না।"),
            "so": ("I do not feel dizzy.", "Ma dareemayo wax dawakhaad ah."),
            "ro": ("I do not feel dizzy.", "Nu mă simt amețit.")
        }
    },

    # ── 5. HEADACHE & MIGRAINE ──
    "headache": {
        "urgent": False,
        "tokens": {
            "ta": ["thalai", "thala", "thali", "thalavali", "mandai", "தலை", "தலைவலி"],
            "hi": ["sar", "sir", "matha", "mathay", "सिरदर्द", "सर दर्द"],
            "ml": ["thala", "thalavedana", "തലവേദന", "തല"],
            "pl": ["glowa", "glowy", "glowie", "głowa", "głowy", "migrena"],
            "ar": ["ras", "rasi", "suda", "sudaa", "صداع", "رأس"],
            "ur": ["sar", "sir", "درد سر", "سر"],
            "bn": ["matha", "mathay", "মাথা ব্যথা", "মাথা"],
            "so": ["madax", "madaxa", "madax xanuun"],
            "ro": ["cap", "capul", "migrena", "durere de cap"]
        },
        "affirmative": {
            "ta": ("I have a headache.", "எனக்கு தலைவலி இருக்கிறது."),
            "hi": ("I have a headache.", "मुझे सिरदर्द हो रहा है।"),
            "ml": ("I have a headache.", "എനിക്ക് തലവേദനയുണ്ട്."),
            "pl": ("I have a headache.", "Boli mnie głowa."),
            "ar": ("I have a headache.", "أعاني من صداع في الرأس."),
            "ur": ("I have a headache.", "میرے سر میں درد ہے۔"),
            "bn": ("I have a headache.", "আমার মাথা ব্যথা করছে।"),
            "so": ("I have a headache.", "Waxaan qabaa madax xanuun."),
            "ro": ("I have a headache.", "Mă doare capul.")
        },
        "negative": {
            "ta": ("I do not have a headache.", "எனக்கு தலைவலி இல்லை."),
            "hi": ("I do not have a headache.", "मुझे सिरदर्द नहीं है।"),
            "ml": ("I do not have a headache.", "എനിക്ക് തലവേദനയില്ല."),
            "pl": ("I do not have a headache.", "Nie boli mnie głowa."),
            "ar": ("I do not have a headache.", "ليس لدي صداع."),
            "ur": ("I do not have a headache.", "میرے سر میں درد نہیں ہے۔"),
            "bn": ("I do not have a headache.", "আমার মাথা ব্যথা নেই।"),
            "so": ("I do not have a headache.", "Ma qabo wax madax xanuun ah."),
            "ro": ("I do not have a headache.", "Nu mă doare capul.")
        }
    },

    # ── 6. ABDOMINAL & STOMACH PAIN ──
    "stomach pain": {
        "urgent": False,
        "tokens": {
            "ta": ["vayiru", "vayaru", "vathiru", "thoppai", "வயிறு", "வயிற்று வலி"],
            "hi": ["pet", "pait", "udar", "पेट", "पेट दर्द"],
            "ml": ["vayar", "vayaril", "വയറുവേദന", "വയർ"],
            "pl": ["brzuch", "brzucha", "zoladek", "brzuszny", "brzuchu"],
            "ar": ["batan", "batni", "meeda", "maghas", "بطن", "معدة"],
            "ur": ["pet", "pait", "پیٹ", "معدہ"],
            "bn": ["pet", "pete", "tolpet", "পেটে ব্যথা", "পেট"],
            "so": ["calool", "calosha", "calool xanuun"],
            "ro": ["stomac", "stomacul", "burta", "burtă", "abdominal"]
        },
        "affirmative": {
            "ta": ("I have stomach pain.", "எனக்கு வயிற்று வலி இருக்கிறது."),
            "hi": ("I have stomach pain.", "मुझे पेट में दर्द हो रहा है।"),
            "ml": ("I have stomach pain.", "എനിക്ക് വയറുവേദനയുണ്ട്."),
            "pl": ("I have stomach pain.", "Mam silny ból brzucha."),
            "ar": ("I have stomach pain.", "أشعر بألم ومغص في البطن."),
            "ur": ("I have stomach pain.", "میرے پیٹ میں درد ہو رہا ہے۔"),
            "bn": ("I have stomach pain.", "আমার পেটে ব্যথা করছে।"),
            "so": ("I have stomach pain.", "Waxaan qabaa calool xanuun."),
            "ro": ("I have stomach pain.", "Am dureri de stomac.")
        },
        "negative": {
            "ta": ("I do not have stomach pain.", "எனக்கு வயிற்று வலி இல்லை."),
            "hi": ("I do not have stomach pain.", "मुझे पेट में दर्द नहीं है।"),
            "ml": ("I do not have stomach pain.", "എനിക്ക് വയറുവേദനയില്ല."),
            "pl": ("I do not have stomach pain.", "Nie mam bólu brzucha."),
            "ar": ("I do not have stomach pain.", "ليس لدي أي ألم في البطن."),
            "ur": ("I do not have stomach pain.", "میرے پیٹ میں درد نہیں ہے۔"),
            "bn": ("I do not have stomach pain.", "আমার পেটে কোনো ব্যথা নেই।"),
            "so": ("I do not have stomach pain.", "Ma qabo wax calool xanuun ah."),
            "ro": ("I do not have stomach pain.", "Nu am dureri de stomac.")
        }
    },

    # ── 7. SICKNESS & VOMITING ──
    "vomiting": {
        "urgent": False,
        "tokens": {
            "ta": ["vanthi", "kakka", "வாந்தி"],
            "hi": ["ulti", "qay", "matli", "उल्टी"],
            "ml": ["chardhi", "chardi", "ഛർദ്ദി"],
            "pl": ["wymioty", "wymiotuje", "mdlosci", "niedobrze"],
            "ar": ["istifragh", "qay", "tarjee", "استفراغ", "قيء"],
            "ur": ["ulti", "qay", "matli", "الٹی"],
            "bn": ["bomi", "বমি"],
            "so": ["matag", "mataq", "lalabbo"],
            "ro": ["vomit", "greata", "greață", "varsaturi", "voma"]
        },
        "affirmative": {
            "ta": ("I have been vomiting.", "எனக்கு வாந்தி வருகிறது."),
            "hi": ("I have been vomiting.", "मुझे उल्टियां हो रही हैं।"),
            "ml": ("I have been vomiting.", "എനിക്ക് ഛർദ്ദിയുണ്ട്."),
            "pl": ("I have been vomiting.", "Wymiotuję i mam silne nudności."),
            "ar": ("I have been vomiting.", "أعاني من القيء والغثيان المستمر."),
            "ur": ("I have been vomiting.", "مجھے الٹیاں آ رہی ہیں۔"),
            "bn": ("I have been vomiting.", "আমার বমি হচ্ছে।"),
            "so": ("I have been vomiting.", "Waxaan dareemayaa matag."),
            "ro": ("I have been vomiting.", "Am stări de vomă și greață.")
        },
        "negative": {
            "ta": ("I have not been vomiting.", "எனக்கு வாந்தி இல்லை."),
            "hi": ("I have not been vomiting.", "मुझे उल्टी नहीं हो रही है।"),
            "ml": ("I have not been vomiting.", "എനിക്ക് ഛർദ്ദിയില്ല."),
            "pl": ("I have not been vomiting.", "Nie wymiotuję."),
            "ar": ("I have not been vomiting.", "لا أعاني من أي قيء."),
            "ur": ("I have not been vomiting.", "मुझे الٹی نہیں آ رہی ہے۔"),
            "bn": ("I have not been vomiting.", "আমার বমি হচ্ছে না।"),
            "so": ("I have not been vomiting.", "Ma lihi wax matag ah."),
            "ro": ("I have not been vomiting.", "Nu am vărsături.")
        }
    },

    # ── 8. FEVER & INFECTION ──
    "fever": {
        "urgent": False,
        "tokens": {
            "ta": ["kaichal", "kaachal", "jwaram", "juram", "காய்ச்சல்"],
            "hi": ["bukhar", "tap", "garam", "बुखार"],
            "ml": ["pani", "പനി"],
            "pl": ["goraczka", "gorączka", "temperatura", "dreszcze"],
            "ar": ["humma", "harara", "sukhuna", "7arara", "حمى", "حرارة"],
            "ur": ["bukhar", "بخار"],
            "bn": ["jhor", "jor", "shorir gorom", "জ্বর"],
            "so": ["qandho", "qando", "xumad"],
            "ro": ["febra", "febră", "frisoane", "temperatura"]
        },
        "affirmative": {
            "ta": ("I have a fever and chills.", "எனக்கு அதிக காய்ச்சல் மற்றும் நடுக்கம் உள்ளது."),
            "hi": ("I have a high fever.", "मुझे तेज बुखार आ रहा है।"),
            "ml": ("I have a fever.", "എനിക്ക് കഠിനമായ പനിയുണ്ട്."),
            "pl": ("I have a high fever.", "Mam wysoką gorączkę i dreszcze."),
            "ar": ("I have a high fever.", "أعاني من ارتفاع شديد في درجة الحرارة."),
            "ur": ("I have a fever.", "مجھے تیز بخار ہے۔"),
            "bn": ("I have a high fever.", "আমার প্রচণ্ড জ্বর আছে।"),
            "so": ("I have a fever.", "Waxaan qabaa qandho daran."),
            "ro": ("I have a high fever.", "Am febră mare și frisoane.")
        },
        "negative": {
            "ta": ("I do not have a fever.", "எனக்கு காய்ச்சல் இல்லை."),
            "hi": ("I do not have a fever.", "मुझे कोई बुखार नहीं है।"),
            "ml": ("I do not have a fever.", "എനിക്ക് പനിയില്ല."),
            "pl": ("I do not have a fever.", "Nie mam gorączki."),
            "ar": ("I do not have a fever.", "ليس لدي أي حمى."),
            "ur": ("I do not have a fever.", "مجھے بخار نہیں ہے۔"),
            "bn": ("I do not have a fever.", "আমার কোনো জ্বর নেই।"),
            "so": ("I do not have a fever.", "Ma lihi wax qandho ah."),
            "ro": ("I do not have a fever.", "Nu am febră.")
        }
    },

    # ── 9. INJURY, FALL & FRACTURE ──
    "injury": {
        "urgent": False,
        "tokens": {
            "ta": ["kaayam", "adi", "udanjiduchu", "elumbu", "காயம்", "அடி"],
            "hi": ["chot", "haddee", "toot", "gir gaya", "चोट", "हड्डी टूटना"],
            "ml": ["murivu", "asthi", "potti", "veenu", "മുറിവ്", "അസ്ഥിപൊട്ടൽ"],
            "pl": ["zlamanie", "skrecenie", "uraz", "upadlem", "zlamana", "noga"],
            "ar": ["kasr", "jurh", "iltoaa", "waqaat", "كسر", "جرح", "إصابة"],
            "ur": ["chot", "haddi", "toot", "gir pada", "چوٹ", "فریکچر"],
            "bn": ["aaghat", "har", "bhenge", "pore gechhi", "আঘাত", "হাড় ভাঙা"],
            "so": ["dhaawac", "jabniin", "dhacay", "laf"],
            "ro": ["fractura", "rupt", "cazut", "entorsa", "fractură", "rană"]
        },
        "affirmative": {
            "ta": ("I had a fall and suspect a broken bone.", "எனக்கு அடிபட்டு எலும்பு முறிந்துவிட்டது போல் உள்ளது."),
            "hi": ("I had a fall and think a bone is broken.", "मुझे चोट लगी है और शायद हड्डी टूट गई है।"),
            "ml": ("I had a fall and injury.", "എനിക്ക് വീണ് പരിക്കേറ്റു."),
            "pl": ("I fell and suspect a broken bone.", "Upadłem i podejrzewam złamanie kości."),
            "ar": ("I fell and think I have a fracture.", "سقطت وأعتقد أن لدي كسراً في العظام."),
            "ur": ("I had a fall and suspect a fracture.", "مجھے چوٹ لگی ہے اور ہڈی ٹوٹنے کا شبہ ہے۔"),
            "bn": ("I had an injury from a fall.", "আমি আঘাত পেয়েছি এবং মনে হচ্ছে হাড় ভেঙেছে।"),
            "so": ("I fell and have an injury.", "Waan dhacay waxaana iga jabay laf."),
            "ro": ("I had a fall and suspect a broken bone.", "Am căzut și suspectez o fractură.")
        },
        "negative": {
            "ta": ("I have no broken bone or injury.", "எலும்பு முறிவு அல்லது பெரிய காயம் எதுவும் இல்லை."),
            "hi": ("I have no injury or fracture.", "कोई चोट या फ्रैक्चर नहीं है।"),
            "ml": ("I have no fracture.", "പരിക്കോ പൊട്ടലോ ഇല്ല."),
            "pl": ("No broken bones or injury.", "Nie mam złamań ani urazów."),
            "ar": ("No fracture or injury.", "لا يوجد أي كسر أو إصابة."),
            "ur": ("No fracture or injury.", "کوئی فریکچر یا چوٹ نہیں ہے۔"),
            "bn": ("No fracture or injury.", "কোনো ভাঙা বা আঘাত নেই।"),
            "so": ("No fracture or injury.", "Wax jabniin ah ma jiro."),
            "ro": ("No fracture or injury.", "Nu am fracturi sau răni grave.")
        }
    },

    # ── 10. ALLERGIC REACTION ──
    "allergy": {
        "urgent": True,
        "tokens": {
            "ta": ["allergy", "aripu", "thadhipu", "ஒவ்வாமை", "அரிப்பு"],
            "hi": ["allergy", "khujli", "rash", "एलर्जी", "खुजली"],
            "ml": ["chorichil", "thadichil", "allergy", "അലർജി"],
            "pl": ["alergia", "alergiczna", "uczulenie", "wysypka", "swedzi"],
            "ar": ["hasasiya", "7asasiye", "tahassos", "hikkah", "حساسية"],
            "ur": ["allergy", "kharish", "surkhi", "الرجی", "خارش"],
            "bn": ["allergy", "chulkani", "lalche", "অ্যালার্জি", "চুলকানি"],
            "so": ["xasaasiyad", "cuncun", "finan"],
            "ro": ["alergie", "alergica", "mancarime", "eruptie"]
        },
        "affirmative": {
            "ta": ("I am having an allergic reaction.", "எனக்கு ஒவ்வாமை (Allergy) ஏற்பட்டுள்ளது."),
            "hi": ("I am having an allergic reaction.", "मुझे एलर्जी का दौरा पड़ा है।"),
            "ml": ("I have an allergic reaction.", "എനിക്ക് അലർജി അനുഭവപ്പെടുന്നു."),
            "pl": ("I am having an allergic reaction.", "Mam silną reakcję alergiczną."),
            "ar": ("I am having an allergic reaction.", "أعاني من رد فعل تحسسي شديد."),
            "ur": ("I am having an allergic reaction.", "مجھے الرجی کا ردعمل ہو رہا ہے۔"),
            "bn": ("I am having an allergic reaction.", "আমার তীব্র অ্যালার্জির সমস্যা হচ্ছে।"),
            "so": ("I am having an allergic reaction.", "Waxaan qabaa xasaasiyad daran."),
            "ro": ("I am having an allergic reaction.", "Am o reacție alergică severă.")
        },
        "negative": {
            "ta": ("I have no allergies.", "எனக்கு எந்த ஒவ்வாமையும் இல்லை."),
            "hi": ("I have no allergies.", "मुझे कोई एलर्जी नहीं है।"),
            "ml": ("I have no allergies.", "എനിക്ക് അലർജികളൊന്നുമില്ല."),
            "pl": ("I have no allergies.", "Nie mam żadnych alergii."),
            "ar": ("I have no allergies.", "ليس لدي أي حساسية."),
            "ur": ("I have no allergies.", "مجھے کوئی الرجی نہیں ہے۔"),
            "bn": ("I have no allergies.", "আমার কোনো অ্যালার্জি নেই।"),
            "so": ("I have no allergies.", "Ma lihi wax xasaasiyad ah."),
            "ro": ("I have no allergies.", "Nu am nicio alergie cunoscută.")
        }
    }
}
