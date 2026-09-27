# blended_config.py
"""
MedOriva AI Ltd - Multi-Script Colloquial Lexicon & Negation Map
Version: 2.7 Production Seed
Coverage: 9 MVP Languages (660+ total tokens)
Framework: Non-clinical administrative reception intake & safety gating
"""

EXPANDED_LEXICON = {
    # =========================================================================
    # 1. TAMIL (Thanglish - Romanised Tamil)
    # =========================================================================
    "ta": {
        "negation": [
            "illai", "ille", "illa", "kidaiyathu", "vendam", "agathu", 
            "mudiyathu", "theriyathu", "koodathu", "illave illa"
        ],
        "critical_symptoms": {
            "chest_pain": [
                "nenji vali", "nenju vali", "marbu vali", "nenjil vali", 
                "nenju erichal", "nenju baaram", "nenju adaippu", "heart vali"
            ],
            "breathing_difficulty": [
                "moochu thinaral", "swasa kolaru", "moochu vidamudiyala", 
                "moochu muttuthu", "moochu kasta", "breath kasta", "moochu idikkuthu"
            ],
            "severe_bleeding": [
                "athiga ratham", "rathapokku", "ratham varuthu", "ratham nikkala", 
                "blood vanthute irukku", "thaduka mudiyatha ratham"
            ],
            "collapse": [
                "mayakkam", "keezhe vizhunthuten", "mayangi vizhunthuten", 
                "thalaisuthal", "surundu vizhunthuten", "bodham illa"
            ],
            "stroke_signs": [
                "kai kaal vilangala", "vaai konita pochu", "pechu kolaru", 
                "kai thookka mudiyala", "orupakkam saanjikiduchu"
            ]
        },
        "routine_admin": {
            "appointment": [
                "appointment irukku", "doctor paakanum", "time enna", "book pannanum", 
                "dr appointment", "token irukka", "varavendiya neram", "appointment check"
            ],
            "prescription": [
                "marunthu venum", "tablets", "marunthu seetu", "tablet ezhuthikudukanum", 
                "marunthu theernthupochu", "prescription renewal", "repeat prescription"
            ],
            "sample_drop": [
                "urine test", "blood test sample", "bottle kudukanum", "rathaparisothanai", 
                "siruneer sample", "lab sample drop", "sample bottle"
            ],
            "interpreter": [
                "tamil theriyum", "english theriyathu", "translator venum", 
                "tamil pesravanga irukangala", "interpreter thevai", "tamizh translator"
            ],
            "registration": [
                "new patient", "register pannanum", "address maathuvathu", 
                "nhs number", "form fill pannanum", "puthiya aal"
            ]
        },
        "minor_ailments": {
            "fever_cold": ["kaichal", "kulir", "sali", "irumal", "thondai vali", "fever irukku"],
            "stomach_pain": ["vathiru vali", "vayithu vali", "serimanam kolaru", "vanthi", "bedhi"],
            "body_pain": ["kaal vali", "kai vali", "muthugu vali", "udambu vali", "thalai vali"]
        }
    },

    # =========================================================================
    # 2. HINDI (Hinglish - Romanised Hindi)
    # =========================================================================
    "hi": {
        "negation": [
            "nahi", "nahin", "na", "mat", "kuch nahi", "nahi hai", "manaa", "bilkul nahi"
        ],
        "critical_symptoms": {
            "chest_pain": [
                "seene me dard", "chaati me dard", "sine me dard", "dil me dard", 
                "seene me chubhan", "chaati me dabav", "heart pain", "chhati dard"
            ],
            "breathing_difficulty": [
                "saans lene me takleef", "dam ghutna", "saans phoolna", "saans nahi aa rahi", 
                "dum ghut raha hai", "saans lene me dikkat", "saans atakti hai"
            ],
            "severe_bleeding": [
                "zyada khoon", "khoon behna", "khoon nikal raha", "khoon nahi ruk raha", 
                "bahut khoon beh raha hai", "bleeding ruk nahi rahi"
            ],
            "collapse": [
                "behosh", "chakkar aakar girna", "gira pada", "chakkar aa rahe hain", 
                "aankhon ke aage andhera", "behosh ho gaya", "gir gaya"
            ],
            "stroke_signs": [
                "chehra aada hona", "haath pair sunn", "bolne me dikkat", 
                "haath utha nahi pa raha", "ek taraf kamzori"
            ]
        },
        "routine_admin": {
            "appointment": [
                "appointment hai", "doctor ko dikhana hai", "mulaqat ka samay", 
                "appointment lena hai", "dr sahab se milna hai", "appointment check karna hai", "time kab hai"
            ],
            "prescription": [
                "dawai chahiye", "parchi", "goli", "dawai khatam ho gayi", 
                "repeat parchi", "prescription check karna", "dawa likhwani hai"
            ],
            "sample_drop": [
                "peshab test", "blood sample dena hai", "bottle jama karni hai", 
                "khoon jaanch", "test ki sheeshi", "lab sample drop"
            ],
            "interpreter": [
                "hindi aati hai", "english nahi aati", "tarjuma chahiye", 
                "interpreter chahiye", "hindi bolne wala chahiye", "angrezi samajh nahi aati"
            ],
            "registration": [
                "naya mareez", "form bharna hai", "naam darj karna hai", 
                "nhs number dena hai", "pata badalna hai"
            ]
        },
        "minor_ailments": {
            "fever_cold": ["bukhar", "sardi", "zukaam", "khansi", "gale me kharash", "bukhar hai"],
            "stomach_pain": ["pet me dard", "gas ban rahi hai", "ulti aa rahi hai", "dast", "pet kharab"],
            "body_pain": ["sar dard", "kamar dard", "ghutne me dard", "badan dard", "taang me dard"]
        }
    },

    # =========================================================================
    # 3. MALAYALAM (Manglish - Romanised Malayalam)
    # =========================================================================
    "ml": {
        "negation": [
            "illa", "illatha", "alla", "illaa", "vendam", "ariyilla", "pattilla", "illallo"
        ],
        "critical_symptoms": {
            "chest_pain": [
                "nenju vedana", "nenjil vedana", "chankil vedana", "nenju kuthal", 
                "nenjil oru bhaaratha", "heart pain", "nenjerichil", "nenjinu kuthu"
            ],
            "breathing_difficulty": [
                "swasam muttal", "swasamedukkan budhimuttu", "swasam kittaathirikuka", 
                "moochu muttuka", "dam muttal", "swasam nilkkunnathu pole"
            ],
            "severe_bleeding": [
                "kooduthal chora", "raktham pokku", "raktham nilkkunnilla", 
                "chora pokk nilkunilla", "valiya thothil raktham"
            ],
            "collapse": [
                "bodham kettu", "thala karangi veenu", "thala karakkam", 
                "bodham kettu veenu", "thalakarangi veenu"
            ],
            "stroke_signs": [
                "kai kaal thalarchia", "mukham kodiya", "samsarikkan pattunnilla", "vaay kodi"
            ]
        },
        "routine_admin": {
            "appointment": [
                "appointment undu", "doctore kaananam", "dr appointment check", 
                "time ariyano", "appointment book cheyyanam", "token undonnu ariyaan"
            ],
            "prescription": [
                "marunnu venam", "prescription", "gulika theernnu", 
                "repeat prescription venam", "marunnu kurikkanam", "marunnu seetu"
            ],
            "sample_drop": [
                "urine sample", "blood sample tharan undu", "bottle labil kodukkanam", 
                "raktha parishodhana", "mutra parishodhana"
            ],
            "interpreter": [
                "malayalam mathram", "english ariyilla", "malayalam parayunna aal venam", 
                "interpreter venam", "translator sahayikkamo"
            ],
            "registration": [
                "puthiya aal", "register cheyyanam", "form puripikkanam", 
                "nhs number kodukkanam", "address maattan"
            ]
        },
        "minor_ailments": {
            "fever_cold": ["pani", "thaduppu", "chuma", "tholayil vedana", "mookkadappu"],
            "stomach_pain": ["vayar vedana", "vayaril kadi", "chadikkal", "vayaril asukham"],
            "body_pain": ["thala vedana", "kaal vedana", "nadukku vedana", "kai vedana"]
        }
    },

    # =========================================================================
    # 4. POLISH (Colloquial Latin / Phonetic without diacritics)
    # =========================================================================
    "pl": {
        "negation": [
            "nie", "brak", "bez", "nie ma", "wcale", "ani", "zadnego"
        ],
        "critical_symptoms": {
            "chest_pain": [
                "bol w klatce", "bolu w klatce", "bol w piersiach", "pieczenie w klatce", 
                "ucisk w klatce piersiowej", "klucie w sercu", "klatka boli", "bol serca"
            ],
            "breathing_difficulty": [
                "dusznosc", "problemy z oddychaniem", "brak tchu", "nie moge oddychac", 
                "ciezko oddychac", "duszno mi", "dusze sie"
            ],
            "severe_bleeding": [
                "silne krwawienie", "krew leci", "duzo krwi", "krwotok", 
                "krew nie zatrzymuje sie", "krwawi mocno"
            ],
            "collapse": [
                "zaslabniecie", "omdlenie", "utrata przytomnosci", "upadlem", 
                "kreci mi sie w glowie", "zemdlalem"
            ],
            "stroke_signs": [
                "opadanie kacika ust", "dretwienie reki", "belkotliwa mowa", 
                "niedowlad reki", "paraliz twarzy"
            ]
        },
        "routine_admin": {
            "appointment": [
                "mam wizyte", "do lekarza", "umowiona wizyta", "jaka godzina wizyty", 
                "sprawdzic wizyte", "chce sie umowic", "godzina wizyty"
            ],
            "prescription": [
                "recepta", "leki", "powtorka lekow", "skonczyly sie leki", 
                "chce recepte", "zamowic recepte", "lekarstwa"
            ],
            "sample_drop": [
                "probka moczu", "badanie krwi", "oddac probke", "mocz do badania", 
                "pojemnik z probka", "probka do laboratorium"
            ],
            "interpreter": [
                "tlumacz", "nie mowie po angielsku", "potrzebuje tlumacza", 
                "jezyk polski", "tlumacz polski", "pomoc jezykowa"
            ],
            "registration": [
                "nowy pacjent", "formularz rejestracji", "zapisac sie", 
                "numer nhs", "zmiana adresu", "zarejestrowac sie"
            ]
        },
        "minor_ailments": {
            "fever_cold": ["goraczka", "przeziebienie", "kaszel", "bol gardla", "katar"],
            "stomach_pain": ["bol brzucha", "niestrawnosc", "wymioty", "biegunka", "zgaga"],
            "body_pain": ["bol glowy", "bol plecow", "bol kolana", "bol nogi", "bol kregoslupa"]
        }
    },

    # =========================================================================
    # 5. ARABIC (Arabizi / Franco-Arabic Numbers: 2=hamza, 3='ayn, 7=ha)
    # =========================================================================
    "ar": {
        "negation": [
            "la", "mosh", "ma", "mish", "laa", "mu", "laysa", "wala", "maba"
        ],
        "critical_symptoms": {
            "chest_pain": [
                "wajaa bel sadr", "alam fil sadr", "waja3 bel sadr", "sedri biwja3ni", 
                "daght 3al sadr", "alam qalb", "waja3 sadr shadid", "alam bel sadr"
            ],
            "breathing_difficulty": [
                "diq tanaffus", "deeq tanafos", "mish qader atanfas", "kanka", 
                "tasarou3 tanaffos", "nafasi makhtouq", "so3oubet tanaffos"
            ],
            "severe_bleeding": [
                "nazif shadid", "dam kteer", "dem 3am yenzel", "nazif la yatawaqaf", 
                "dam ktir 3am yusil", "nazif qawi"
            ],
            "collapse": [
                "ighma", "waqa3t", "ghameyt", "dekhit", "faqad el wa3y", 
                "dawkha shadida", "waqa3 3al ard"
            ],
            "stroke_signs": [
                "shelel nosfi", "i3wijaj bel fam", "so3ouba bel kalam", 
                "id ma bettaharrak", "tanamol bel wajh"
            ]
        },
        "routine_admin": {
            "appointment": [
                "3andi maw3ed", "maw3ed ma3 el doctor", "jaayt 3al maw3ed", 
                "eza 3andi maw3ed", "baddi chuf el doctor", "tasjil dukhul", "maw3idi"
            ],
            "prescription": [
                "wasfa tibbiya", "adwiya", "baddi dawa", "kholos ed dawa", 
                "tajdid wasfa", "habat dawa", "wasfet dawa"
            ],
            "sample_drop": [
                "fahs dam", "3aynet bawl", "fahs", "taslim 3ayne", 
                "3olbat fahs", "mokhtabar", "tahlil dam"
            ],
            "interpreter": [
                "motarjem", "ma behki inglizi", "baddi mutarjim", 
                "motarjem 3arabi", "la a3rif engilizi", "motarjima"
            ],
            "registration": [
                "marid jadid", "ta3biat istimara", "raqam nhs", 
                "taghyir 3onwan", "tasjil marid"
            ]
        },
        "minor_ailments": {
            "fever_cold": ["harara", "sukhuna", "rashih", "sa3la", "wajaa halq"],
            "stomach_pain": ["wajaa batn", "maghs", "istifragh", "is-hal", "hrara bel me3de"],
            "body_pain": ["wajaa ras", "suda3", "alam zaher", "wajaa rokba", "alam mafasel"]
        }
    },

    # =========================================================================
    # 6. URDU (Roman Urdu)
    # =========================================================================
    "ur": {
        "negation": [
            "nahi", "nahin", "na", "mat", "kuch nahi", "nahi hai", "mana", "hargiz nahi"
        ],
        "critical_symptoms": {
            "chest_pain": [
                "seene mein dard", "chati mein dard", "dil mein dard", "seene pe bojh", 
                "chhati mein jalan", "dil ka daura", "chhati dard"
            ],
            "breathing_difficulty": [
                "saans lene mein dushwari", "saans phool rahi hai", "dam ghut raha hai", 
                "saans ruk rahi hai", "saans ki takleef", "dam ghutna"
            ],
            "severe_bleeding": [
                "bohot khoon", "khoon beh raha hai", "khoon nahi ruk raha", 
                "zyada khoon nikal raha hai", "shadeed khoon"
            ],
            "collapse": [
                "behosh ho gaya", "chakkar aa kar gir gaya", "gira pada", 
                "hosh kho diya", "aankhon ke aage andhera"
            ],
            "stroke_signs": [
                "chehra terha ho gaya", "haath sunn", "awaz ladkhada rahi hai", "zuban band"
            ]
        },
        "routine_admin": {
            "appointment": [
                "appointment hai", "doctor se milna hai", "appointment check karni hai", 
                "dr sahab se milne ka time", "appointment book karwani hai"
            ],
            "prescription": [
                "dawa chahiye", "nuskha", "parchi", "dawaiyan khatam", 
                "repeat prescription", "goli likhwani hai"
            ],
            "sample_drop": [
                "sample jama karwana hai", "urine test", "khoon ka sample", 
                "test ki bottle", "lab mein dena hai"
            ],
            "interpreter": [
                "urdu bolta hoon", "angrezi nahi aati", "interpreter chahiye", 
                "urdu tarjuma", "motarjim chahiye"
            ],
            "registration": [
                "naya mareez", "form bharna", "naam register karna", 
                "nhs number", "pata badalna"
            ]
        },
        "minor_ailments": {
            "fever_cold": ["bukhar", "zukam", "khansi", "gale mein kharash", "bukhar charh gaya"],
            "stomach_pain": ["pait mein dard", "gas", "ulti", "pait kharab", "dast"],
            "body_pain": ["sar mein dard", "kamar dard", "jism mein dard", "ghutnay ka dard"]
        }
    },

    # =========================================================================
    # 7. BENGALI (Banglish - Romanised Bengali)
    # =========================================================================
    "bn": {
        "negation": [
            "na", "nei", "ni", "noy", "lagbe na", "jani na", "parbo na", "kokhono na"
        ],
        "critical_symptoms": {
            "chest_pain": [
                "bukey betha", "buker betha", "bukey chap", "buk jole jache", 
                "bukey dhorfor", "heart betha", "bukey betha ache"
            ],
            "breathing_difficulty": [
                "shash kosto", "shash nite koshto", "dam bondho hoye asche", 
                "shash phule jacche", "shash nite parchi na", "dam atke asche"
            ],
            "severe_bleeding": [
                "onek rokto", "rokto porche", "rokto thamche na", 
                "rokto kharon", "rokto bondho hocche na"
            ],
            "collapse": [
                "ogyan hoye gechi", "matha ghure pore gechi", "matha ghurche", 
                "behosh hoye porechi", "pore gechi"
            ],
            "stroke_signs": [
                "mukh baka hoye geche", "haath pa obosh", "kotha bolte parchi na"
            ]
        },
        "routine_admin": {
            "appointment": [
                "appointment ache", "doctor dekhabo", "appointment er somoy", 
                "appointment check korte chai", "dr dekhanor time"
            ],
            "prescription": [
                "aushodh dorkar", "prescription", "aushodh sesh", 
                "repeat prescription", "tablet er kagoj"
            ],
            "sample_drop": [
                "sample joma dibo", "urine test", "rokter sample", 
                "botol joma", "lab test er jonne"
            ],
            "interpreter": [
                "bangla boli", "english jani na", "dovashi dorkar", 
                "bangla bujhi", "interpreter lagbe"
            ],
            "registration": [
                "notun patient", "form puron", "nhs number", 
                "thikana poriborton", "registration korte chai"
            ]
        },
        "minor_ailments": {
            "fever_cold": ["jor", "shordi", "kashi", "gola betha", "jor asche"],
            "stomach_pain": ["pet betha", "bad-hojom", "bomi", "pet kharap", "amashoy"],
            "body_pain": ["matha betha", "komor betha", "haatu betha", "gae haat pae betha"]
        }
    },

    # =========================================================================
    # 8. SOMALI (Colloquial Latin)
    # =========================================================================
    "so": {
        "negation": [
            "maya", "ma", "ma jiro", "aanan", "ha", "ma rabo", "ma aqaano", "maba jiro"
        ],
        "critical_symptoms": {
            "chest_pain": [
                "xanuun laabta", "laab xanuun", "feer xanuun", "wadno xanuun", 
                "laabta oo ku culus", "laabta oo gubanaysa", "feero xanuun"
            ],
            "breathing_difficulty": [
                "neefsashada oo dhib ah", "neefta oo ku dhagta", "neefsan waayay", 
                "neef qaadasho la'aan", "neefta oo yaraata", "neef qabasho"
            ],
            "severe_bleeding": [
                "dhiig bax xoog leh", "dhiig badan", "dhiig socda oo joogsan waayay", 
                "dhiig bax daran"
            ],
            "collapse": [
                "suuxdin", "dhicitaan", "wareer daran", "suuxay", "dhulka ku dhacay"
            ],
            "stroke_signs": [
                "wajiga oo qalloocday", "dhinac qallalan", "hadalka oo xumaaday"
            ]
        },
        "routine_admin": {
            "appointment": [
                "ballan baan leeyahay", "dhakhtar aragti", "waqtiga ballanta", 
                "ballan xaqiijin", "dhakhtarka inaan arko"
            ],
            "prescription": [
                "dawo qoris", "dawooyin", "warqad dawo", "dawooyinkii dhamaaday", 
                "dawo cusboonaysiin"
            ],
            "sample_drop": [
                "baaritaan dhiig", "kaadi baaris", "dhalo keenis", "muunad la keenay", 
                "baaritaan sheybaar"
            ],
            "interpreter": [
                "turjubaan baan rabaa", "ingiriisi ma hadlo", "af soomaali keliya", 
                "turjumaan codsi"
            ],
            "registration": [
                "bukaanka cusub", "form buuxin", "lambarka nhs", "cinwaanka badalid"
            ]
        },
        "minor_ailments": {
            "fever_cold": ["qandho", "hargab", "qufac", "cunaha oo xanuunaya"],
            "stomach_pain": ["calool xanuun", "laab jex", "mataq", "shuban"],
            "body_pain": ["madax xanuun", "dhabar xanuun", "jilib xanuun", "muruq xanuun"]
        }
    },

    # =========================================================================
    # 9. ROMANIAN (Colloquial Latin without diacritics)
    # =========================================================================
    "ro": {
        "negation": [
            "nu", "deloc", "fara", "n-am", "nu am", "deloc nu", "nici", "nicidecum"
        ],
        "critical_symptoms": {
            "chest_pain": [
                "durere in piept", "durere la piept", "intepaturi in piept", "strangere in piept", 
                "apasa pe piept", "durere de inima", "intepatura in piept"
            ],
            "breathing_difficulty": [
                "respiratie grea", "lipsa de aer", "nu pot respira", "ma sufoc", 
                "greu sa respir", "dificultate respiratorie", "nu am aer"
            ],
            "severe_bleeding": [
                "sangerare puternica", "mult sange", "curge mult sange", "hemoragie", 
                "nu se opreste sangele"
            ],
            "collapse": [
                "lesin", "am cazut", "pierderea cunostintei", "am ametit si am cazut", 
                "ameteli puternice"
            ],
            "stroke_signs": [
                "fata stramba", "mana amortita", "nu pot vorbi clar", "amorteala pe o parte"
            ]
        },
        "routine_admin": {
            "appointment": [
                "am programare", "la doctor", "ora programarii", "verificare programare", 
                "sa vad doctorul", "fac o programare"
            ],
            "prescription": [
                "reteta", "medicamente", "reinnoire reteta", "am ramas fara medicamente", 
                "prescriptie medicala", "pastile"
            ],
            "sample_drop": [
                "proba urina", "analize sange", "aduc proba", "recipient proba", 
                "proba laborator", "analize"
            ],
            "interpreter": [
                "translator", "nu vorbesc engleza", "interpret", "vorbesc doar romana", 
                "am nevoie de traducator"
            ],
            "registration": [
                "pacient nou", "completare formular", "numar nhs", "schimbare adresa"
            ]
        },
        "minor_ailments": {
            "fever_cold": ["febra", "raceala", "tuse", "durere in gat", "nas infundat"],
            "stomach_pain": ["durere de burta", "arsuri la stomac", "varsaturi", "diaree"],
            "body_pain": ["durere de cap", "durere de spate", "durere de genunchi", "dureri musculare"]
        }
    }
}
