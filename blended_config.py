# blended_config.py
"""
MedOriva AI Ltd - Multi-Script Colloquial Lexicon & Negation Map
Version: 2.7 Production Lexicon Seed (Expanded)
Coverage: 9 MVP Languages (Tamil, Hindi, Malayalam, Polish, Arabic, Urdu, Bengali, Somali, Romanian)
Framework: Non-clinical administrative reception intake, care-navigation, and safety gating
"""

EXPANDED_LEXICON = {
    # =========================================================================
    # 1. TAMIL (Thanglish - Romanised Tamil)
    # =========================================================================
    "ta": {
        "negation": [
            "illai", "ille", "illa", "kidaiyathu", "vendam", "agathu", 
            "mudiyathu", "theriyathu", "koodathu", "illave illa",
            "therila", "enakku vendaam", "illavillai", "illaiye", "sariyilla", "illanu sonnen"
        ],
        "critical_symptoms": {
            "chest_pain": [
                "nenji vali", "nenju vali", "marbu vali", "nenjil vali", 
                "nenju erichal", "nenju baaram", "nenju adaippu", "heart vali",
                "heart attack vanthurumo", "nenjula valikuthu", "edathu kai vali nenju vali", "marbula vali"
            ],
            "breathing_difficulty": [
                "moochu thinaral", "swasa kolaru", "moochu vidamudiyala", 
                "moochu muttuthu", "moochu kasta", "breath kasta", "moochu idikkuthu",
                "moochu thinaruthu", "moochu vida kashtam", "swasam edukka mudiyala", "asthma problem"
            ],
            "severe_bleeding": [
                "athiga ratham", "rathapokku", "ratham varuthu", "ratham nikkala", 
                "blood vanthute irukku", "thaduka mudiyatha ratham",
                "ratham kottuthu", "ratham nikkave illa", "athiga rathapokku", "ratham thadukka mudiyala"
            ],
            "collapse": [
                "mayakkam", "keezhe vizhunthuten", "mayangi vizhunthuten", 
                "thalaisuthal", "surundu vizhunthuten", "bodham illa",
                "thala suthi vizhunthen", "mayangi vizhunthutaanga", "kan moodi vizhunthen", "bodham poiduchu"
            ],
            "stroke_signs": [
                "kai kaal vilangala", "vaai konita pochu", "pechu kolaru", 
                "kai thookka mudiyala", "orupakkam saanjikiduchu",
                "vaai orukku pochu", "kai kaal seyalpadala", "orupakkam asaikka mudiyala"
            ]
        },
        "routine_admin": {
            "appointment": [
                "appointment irukku", "doctor paakanum", "time enna", "book pannanum", 
                "dr appointment", "token irukka", "varavendiya neram", "appointment check",
                "iniku appointment", "reschedule pannanum", "late aayiduchu", "check-in pannanum", "appointment cancellation"
            ],
            "prescription": [
                "marunthu venum", "tablets", "marunthu seetu", "tablet ezhuthikudukanum", 
                "marunthu theernthupochu", "prescription renewal", "repeat prescription",
                "blood pressure tablet", "sugar marunthu", "inhaler venum", "chemist kitta anupanum", "pharmacy collection"
            ],
            "sample_drop": [
                "urine test", "blood test sample", "bottle kudukanum", "rathaparisothanai", 
                "siruneer sample", "lab sample drop", "sample bottle",
                "urine bottle kudukanum", "stool sample", "lab test kuduka vanthen", "blood test results"
            ],
            "interpreter": [
                "tamil theriyum", "english theriyathu", "translator venum", 
                "tamil pesravanga irukangala", "interpreter thevai", "tamizh translator",
                "bilingual helper", "tamil interpreter podunga", "tamizhil pesa mudiyuma", "mozhipeyarpalar"
            ],
            "registration": [
                "new patient", "register pannanum", "address maathuvathu", 
                "nhs number", "form fill pannanum", "puthiya aal",
                "kudumbathoda register pannanum", "change of address", "proof of address", "new registration"
            ]
        },
        "minor_ailments": {
            "fever_cold": ["kaichal", "kulir", "sali", "irumal", "thondai vali", "fever irukku", "kan vali", "mooku ozhukuthu", "adikkadi thummal", "sali pidichurukku"],
            "stomach_pain": ["vathiru vali", "vayithu vali", "serimanam kolaru", "vanthi", "bedhi", "vayiru porumbal", "acid problem", "serikkala", "vayithu kaduppu"],
            "body_pain": ["kaal vali", "kai vali", "muthugu vali", "udambu vali", "thalai vali", "muthugu pidichirukku", "kazhuthu vali", "moottu theimanum", "asathiya irukku"]
        }
    },

    # =========================================================================
    # 2. HINDI (Hinglish - Romanised Hindi)
    # =========================================================================
    "hi": {
        "negation": [
            "nahi", "nahin", "na", "mat", "kuch nahi", "nahi hai", "manaa", "bilkul nahi",
            "pata nahi", "mujhe nahi chahiye", "nahi maloom", "nhi", "nahi ji", "koi nahi"
        ],
        "critical_symptoms": {
            "chest_pain": [
                "seene me dard", "chaati me dard", "sine me dard", "dil me dard", 
                "seene me chubhan", "chaati me dabav", "heart pain", "chhati dard",
                "seene me jakdan", "dil ka daura", "seene me aag lag rahi hai", "left arm me dard"
            ],
            "breathing_difficulty": [
                "saans lene me takleef", "dam ghutna", "saans phoolna", "saans nahi aa rahi", 
                "dum ghut raha hai", "saans lene me dikkat", "saans atakti hai",
                "saans atak rahi hai", "saans lene me dard", "oxygen ki kami", "asthma ka daura"
            ],
            "severe_bleeding": [
                "zyada khoon", "khoon behna", "khoon nikal raha", "khoon nahi ruk raha", 
                "bahut khoon beh raha hai", "bleeding ruk nahi rahi",
                "khoon ki ulti", "khoon behna band nahi ho raha", "zyada bleeding"
            ],
            "collapse": [
                "behosh", "chakkar aakar girna", "gira pada", "chakkar aa rahe hain", 
                "aankhon ke aage andhera", "behosh ho gaya", "gir gaya",
                "chakkar aakar behosh", "gira pada mila", "hosh nahi hai", "sudh budh kho baitha"
            ],
            "stroke_signs": [
                "chehra aada hona", "haath pair sunn", "bolne me dikkat", 
                "haath utha nahi pa raha", "ek taraf kamzori",
                "muh tedha ho gaya", "ek taraf ka hissa sunn", "bolne me ladkhadahat"
            ]
        },
        "routine_admin": {
            "appointment": [
                "appointment hai", "doctor ko dikhana hai", "mulaqat ka samay", 
                "appointment lena hai", "dr sahab se milna hai", "appointment check karna hai", "time kab hai",
                "aaj ka appointment", "check-in karna hai", "late ho gaya", "appointment badalna hai", "kiosk nahi chala"
            ],
            "prescription": [
                "dawai chahiye", "parchi", "goli", "dawai khatam ho gayi", 
                "repeat parchi", "prescription check karna", "dawa likhwani hai",
                "sugar ki dawai", "bp ki goli", "repeat dawai", "chemist ko bhej do", "parcha renew"
            ],
            "sample_drop": [
                "peshab test", "blood sample dena hai", "bottle jama karni hai", 
                "khoon jaanch", "test ki sheeshi", "lab sample drop",
                "urine sample jama karna", "peshab ki jaanch", "khoon ki bottle", "lab test parchi"
            ],
            "interpreter": [
                "hindi aati hai", "english nahi aati", "tarjuma chahiye", 
                "interpreter chahiye", "hindi bolne wala chahiye", "angrezi samajh nahi aati",
                "hindi interpreter", "dubahshiya chahiye", "tarjumakar"
            ],
            "registration": [
                "naya mareez", "form bharna hai", "naam darj karna hai", 
                "nhs number dena hai", "pata badalna hai",
                "naya registration", "parivar ka form", "address change karna", "id proof"
            ]
        },
        "minor_ailments": {
            "fever_cold": ["bukhar", "sardi", "zukaam", "khansi", "gale me kharash", "bukhar hai", "chheek aana", "naak behna", "thand lagna", "gala kharab"],
            "stomach_pain": ["pet me dard", "gas ban rahi hai", "ulti aa rahi hai", "dast", "pet kharab", "acidity ho rahi hai", "khana hazam nahi hua", "pet phool raha hai"],
            "body_pain": ["sar dard", "kamar dard", "ghutne me dard", "badan dard", "taang me dard", "gardana me dard", "pair sunn hona", "jism toot raha hai"]
        }
    },

    # =========================================================================
    # 3. MALAYALAM (Manglish - Romanised Malayalam)
    # =========================================================================
    "ml": {
        "negation": [
            "illa", "illatha", "alla", "illaa", "vendam", "ariyilla", "pattilla", "illallo",
            "illaathilla", "venda vendam", "alla alla", "illannu", "ariyaan pattilla"
        ],
        "critical_symptoms": {
            "chest_pain": [
                "nenju vedana", "nenjil vedana", "chankil vedana", "nenju kuthal", 
                "nenjil oru bhaaratha", "heart pain", "nenjerichil", "nenjinu kuthu",
                "nenjil bhaaratha", "nenjil idichil", "idathu kai vedana", "nenjerichil kooduthal"
            ],
            "breathing_difficulty": [
                "swasam muttal", "swasamedukkan budhimuttu", "swasam kittaathirikuka", 
                "moochu muttuka", "dam muttal", "swasam nilkkunnathu pole",
                "swasam kittaathe valayunnu", "valiv kooduthal", "swasakosha rogam"
            ],
            "severe_bleeding": [
                "kooduthal chora", "raktham pokku", "raktham nilkkunnilla", 
                "chora pokk nilkunilla", "valiya thothil raktham",
                "chora nilkkatha pokku", "chora thuppal", "raktham thottu nilkilla"
            ],
            "collapse": [
                "bodham kettu", "thala karangi veenu", "thala karakkam", 
                "bodham kettu veenu", "thalakarangi veenu",
                "bodham poyi", "thala pukanju veenu", "kanniruttu keri"
            ],
            "stroke_signs": [
                "kai kaal thalarchia", "mukham kodiya", "samsarikkan pattunnilla", "vaay kodi",
                "vaay orupakkam mukkuka", "kai thaazhthu pova", "pechu muzhumayilla"
            ]
        },
        "routine_admin": {
            "appointment": [
                "appointment undu", "doctore kaananam", "dr appointment check", 
                "time ariyano", "appointment book cheyyanam", "token undonnu ariyaan",
                "innathe appointment", "check-in cheyyanam", "neram thettipoyi", "appointment reschedule"
            ],
            "prescription": [
                "marunnu venam", "prescription", "gulika theernnu", 
                "repeat prescription venam", "marunnu kurikkanam", "marunnu seetu",
                "sugar marunnu", "bp gulika", "marunnu list", "pharmacyilottu vidan"
            ],
            "sample_drop": [
                "urine sample", "blood sample tharan undu", "bottle labil kodukkanam", 
                "raktha parishodhana", "mutra parishodhana",
                "mutra sample", "raktha parishodhana bottle", "lab test kodukkan"
            ],
            "interpreter": [
                "malayalam mathram", "english ariyilla", "malayalam parayunna aal venam", 
                "interpreter venam", "translator sahayikkamo",
                "malayalam translator", "bilingual aal", "malayalam ariyunnavar"
            ],
            "registration": [
                "puthiya aal", "register cheyyanam", "form puripikkanam", 
                "nhs number kodukkanam", "address maattan",
                "puthiya registration", "kudumbam register", "address change"
            ]
        },
        "minor_ailments": {
            "fever_cold": ["pani", "thaduppu", "chuma", "tholayil vedana", "mookkadappu", "mookkolichal", "thondavedana", "thummal", "chuma kooduthal"],
            "stomach_pain": ["vayar vedana", "vayaril kadi", "chadikkal", "vayaril asukham", "vayaru puramottal", "gastro trouble", "charthi"],
            "body_pain": ["thala vedana", "kaal vedana", "nadukku vedana", "kai vedana", "kazhuthu vedana", "moottu thalaru", "udambu muzhuvan vedana"]
        }
    },

    # =========================================================================
    # 4. POLISH (Colloquial Latin / Phonetic without diacritics)
    # =========================================================================
    "pl": {
        "negation": [
            "nie", "brak", "bez", "nie ma", "wcale", "ani", "zadnego",
            "nie chce", "nie wiem", "w ogole nie", "nie mam pojecia", "nigdy"
        ],
        "critical_symptoms": {
            "chest_pain": [
                "bol w klatce", "bolu w klatce", "bol w piersiach", "pieczenie w klatce", 
                "ucisk w klatce piersiowej", "klucie w sercu", "klatka boli", "bol serca",
                "sciskanie w klatce", "silny bol serca", "bol promieniuje do lewej reki", "pieczenie w mostku"
            ],
            "breathing_difficulty": [
                "dusznosc", "problemy z oddychaniem", "brak tchu", "nie moge oddychac", 
                "ciezko oddychac", "duszno mi", "dusze sie",
                "dusze sie w nocy", "atak astmy", "trudno zlapac oddech"
            ],
            "severe_bleeding": [
                "silne krwawienie", "krew leci", "duzo krwi", "krwotok", 
                "krew nie zatrzymuje sie", "krwawi mocno",
                "krwawienie z rany", "wymioty z krwia", "masywny krwotok"
            ],
            "collapse": [
                "zaslabniecie", "omdlenie", "utrata przytomnosci", "upadlem", 
                "kreci mi sie w glowie", "zemdlalem",
                "upadek z utrata przytomnosci", "omdlalem nagle", "mdlosci i ciemno przed oczami"
            ],
            "stroke_signs": [
                "opadanie kacika ust", "dretwienie reki", "belkotliwa mowa", 
                "niedowlad reki", "paraliz twarzy",
                "asymetria twarzy", "niedowlad polowiczy", "zaburzenia mowy"
            ]
        },
        "routine_admin": {
            "appointment": [
                "mam wizyte", "do lekarza", "umowiona wizyta", "jaka godzina wizyty", 
                "sprawdzic wizyte", "chce sie umowic", "godzina wizyty",
                "dzisiejsza wizyta", "przelozyc wizyte", "spozniony na wizyte", "potwierdzic obecnosc", "kiosk nie dziala"
            ],
            "prescription": [
                "recepta", "leki", "powtorka lekow", "skonczyly sie leki", 
                "chce recepte", "zamowic recepte", "lekarstwa",
                "leki stale", "recepta na cisnienie", "odnowic recepte", "leki na cukrzyce", "przeslac do apteki"
            ],
            "sample_drop": [
                "probka moczu", "badanie krwi", "oddac probke", "mocz do badania", 
                "pojemnik z probka", "probka do laboratorium",
                "probka do laboratorium", "pojemnik na kal", "probka krwi", "oddanie moczu"
            ],
            "interpreter": [
                "tlumacz", "nie mowie po angielsku", "potrzebuje tlumacza", 
                "jezyk polski", "tlumacz polski", "pomoc jezykowa",
                "tlumacz jezyka polskiego", "potrzebna pomoc jezykowa", "tlumacz na wizycie"
            ],
            "registration": [
                "nowy pacjent", "formularz rejestracji", "zapisac sie", 
                "numer nhs", "zmiana adresu", "zarejestrowac sie",
                "nowa rejestracja", "zmiana przychodni", "dokument tozsamosci", "aktualizacja danych"
            ]
        },
        "minor_ailments": {
            "fever_cold": ["goraczka", "przeziebienie", "kaszel", "bol gardla", "katar", "dreszcze", "chrypka", "kichanie", "zapalenie zatok"],
            "stomach_pain": ["bol brzucha", "niestrawnosc", "wymioty", "biegunka", "zgaga", "zgage", "wymiotowanie", "zatrucie pokarmowe", "wzdecia"],
            "body_pain": ["bol glowy", "bol plecow", "bol kolana", "bol nogi", "bol kregoslupa", "bol stawow", "bol w krzyzu", "bol miesni", "bol karku"]
        }
    },

    # =========================================================================
    # 5. ARABIC (Arabizi / Franco-Arabic Numbers: 2=hamza, 3='ayn, 7=ha)
    # =========================================================================
    "ar": {
        "negation": [
            "la", "mosh", "ma", "mish", "laa", "mu", "laysa", "wala", "maba",
            "kalla", "la a3rif", "ma baddi", "abadan", "ghayr"
        ],
        "critical_symptoms": {
            "chest_pain": [
                "wajaa bel sadr", "alam fil sadr", "waja3 bel sadr", "sedri biwja3ni", 
                "daght 3al sadr", "alam qalb", "waja3 sadr shadid", "alam bel sadr",
                "alam qalbi", "harqa bel sadr", "waja3 el alb", "thokal 3al sadr"
            ],
            "breathing_difficulty": [
                "diq tanaffus", "deeq tanafos", "mish qader atanfas", "kanka", 
                "tasarou3 tanaffos", "nafasi makhtouq", "so3oubet tanaffos",
                "azmet rabou", "tanaffos sa3b", "e5tenaq", "ma fi hawa"
            ],
            "severe_bleeding": [
                "nazif shadid", "dam kteer", "dem 3am yenzel", "nazif la yatawaqaf", 
                "dam ktir 3am yusil", "nazif qawi",
                "nezif damawi", "istifrāgh dam", "dam la yatawaqaf"
            ],
            "collapse": [
                "ighma", "waqa3t", "ghameyt", "dekhit", "faqad el wa3y", 
                "dawkha shadida", "waqa3 3al ard",
                "ghayboba", "saqatt ardhan", "sodam"
            ],
            "stroke_signs": [
                "shelel nosfi", "i3wijaj bel fam", "so3ouba bel kalam", 
                "id ma bettaharrak", "tanamol bel wajh",
                "falaj", "famm a3waj", "thiql bel lisan"
            ]
        },
        "routine_admin": {
            "appointment": [
                "3andi maw3ed", "maw3ed ma3 el doctor", "jaayt 3al maw3ed", 
                "eza 3andi maw3ed", "baddi chuf el doctor", "tasjil dukhul", "maw3idi",
                "maw3ed el youm", "ta2khir 3al maw3ed", "taghyir el maw3ed", "ta2kid maw3ed"
            ],
            "prescription": [
                "wasfa tibbiya", "adwiya", "baddi dawa", "kholos ed dawa", 
                "tajdid wasfa", "habat dawa", "wasfet dawa",
                "dawa daqet el alb", "dawa el sokkari", "wasfa motakarrira", "irsil lal saydaliya"
            ],
            "sample_drop": [
                "fahs dam", "3aynet bawl", "fahs", "taslim 3ayne", 
                "3olbat fahs", "mokhtabar", "tahlil dam",
                "tahlil bawl", "taslim 3olba", "tahlil mokhtabar", "fahs dam"
            ],
            "interpreter": [
                "motarjem", "ma behki inglizi", "baddi mutarjim", 
                "motarjem 3arabi", "la a3rif engilizi", "motarjima",
                "mutarjem arabi", "la afham englizi", "baddi had ytarjim"
            ],
            "registration": [
                "marid jadid", "ta3biat istimara", "raqam nhs", 
                "taghyir 3onwan", "tasjil marid",
                "tasjil a3ila", "tabdil 3onwan", "awraq el tasjil"
            ]
        },
        "minor_ailments": {
            "fever_cold": ["harara", "sukhuna", "rashih", "sa3la", "wajaa halq", "bard", "zahza", "alam bel hanjara", "zukam"],
            "stomach_pain": ["wajaa batn", "maghs", "istifragh", "is-hal", "hrara bel me3de", "alam me3de", "lu3an nafs", "taqyoo", "hrara"],
            "body_pain": ["wajaa ras", "suda3", "alam zaher", "wajaa rokba", "alam mafasel", "waja3 zahar", "alam mafasel", "suda3 nosfi"]
        }
    },

    # =========================================================================
    # 6. URDU (Roman Urdu)
    # =========================================================================
    "ur": {
        "negation": [
            "nahi", "nahin", "na", "mat", "kuch nahi", "nahi hai", "mana", "hargiz nahi",
            "nahi maloom", "mujhe nahi chahiye", "hargiz nahi", "bilkul nahi"
        ],
        "critical_symptoms": {
            "chest_pain": [
                "seene mein dard", "chati mein dard", "dil mein dard", "seene pe bojh", 
                "chhati mein jalan", "dil ka daura", "chhati dard",
                "dil ka daura", "seene mein ghutan", "baayein baazu mein dard", "chhati mein daban"
            ],
            "breathing_difficulty": [
                "saans lene mein dushwari", "saans phool rahi hai", "dam ghut raha hai", 
                "saans ruk rahi hai", "saans ki takleef", "dam ghutna",
                "dama ka daura", "saans rukh rahi hai", "saans ka masla"
            ],
            "severe_bleeding": [
                "bohot khoon", "khoon beh raha hai", "khoon nahi ruk raha", 
                "zyada khoon nikal raha hai", "shadeed khoon",
                "khoon ki ultiyan", "shadeed khoon behna", "khoon band nahi ho raha"
            ],
            "collapse": [
                "behosh ho gaya", "chakkar aa kar gir gaya", "gira pada", 
                "hosh kho diya", "aankhon ke aage andhera",
                "sudh budh kho baitha", "gir parha", "chakar aa gaye"
            ],
            "stroke_signs": [
                "chehra terha ho gaya", "haath sunn", "awaz ladkhada rahi hai", "zuban band",
                "chehra murna", "zuban band hona", "jism ka hissa sunn"
            ]
        },
        "routine_admin": {
            "appointment": [
                "appointment hai", "doctor se milna hai", "appointment check karni hai", 
                "dr sahab se milne ka time", "appointment book karwani hai",
                "aaj ki appointment", "waqt badalna hai", "late ho gaya", "appointment confirm karna"
            ],
            "prescription": [
                "dawa chahiye", "nuskha", "parchi", "dawaiyan khatam", 
                "repeat prescription", "goli likhwani hai",
                "sugar ki dawai", "blood pressure ki goli", "repeat nuskha", "pharmacy bhejna"
            ],
            "sample_drop": [
                "sample jama karwana hai", "urine test", "khoon ka sample", 
                "test ki bottle", "lab mein dena hai",
                "peshab ka sample", "khoon ki sheeshi", "test ki report"
            ],
            "interpreter": [
                "urdu bolta hoon", "angrezi nahi aati", "interpreter chahiye", 
                "urdu tarjuma", "motarjim chahiye",
                "urdu motarjim", "angrezi samajh nahi aati", "urdu tarjuma karwana"
            ],
            "registration": [
                "naya mareez", "form bharna", "naam register karna", 
                "nhs number", "pata badalna",
                "naya registration", "khandan ka form", "pata tabdeel karna"
            ]
        },
        "minor_ailments": {
            "fever_cold": ["bukhar", "zukam", "khansi", "gale mein kharash", "bukhar charh gaya", "nazla", "zukam", "gale ka dard", "thand lagna"],
            "stomach_pain": ["pait mein dard", "gas", "ulti", "pait kharab", "dast", "hazma kharab", "ulti aana", "pait ka maror"],
            "body_pain": ["sar mein dard", "kamar dard", "jism mein dard", "ghutnay ka dard", "kamar ka dard", "pathon mein dard", "jism tootna"]
        }
    },

    # =========================================================================
    # 7. BENGALI (Banglish - Romanised Bengali)
    # =========================================================================
    "bn": {
        "negation": [
            "na", "nei", "ni", "noy", "lagbe na", "jani na", "parbo na", "kokhono na",
            "na na", "jani na", "lagbe na", "kokhono noi"
        ],
        "critical_symptoms": {
            "chest_pain": [
                "bukey betha", "buker betha", "bukey chap", "buk jole jache", 
                "bukey dhorfor", "heart betha", "bukey betha ache",
                "heart attack er moto", "buker moddhe chap", "baam haath betha", "buk jolche"
            ],
            "breathing_difficulty": [
                "shash kosto", "shash nite koshto", "dam bondho hoye asche", 
                "shash phule jacche", "shash nite parchi na", "dam atke asche",
                "hafe jacchi", "shash pawa jacche na", "asthma problem"
            ],
            "severe_bleeding": [
                "onek rokto", "rokto porche", "rokto thamche na", 
                "rokto kharon", "rokto bondho hocche na",
                "onek beshi rokto", "rokto jhora", "rokto thamche na"
            ],
            "collapse": [
                "ogyan hoye gechi", "matha ghure pore gechi", "matha ghurche", 
                "behosh hoye porechi", "pore gechi",
                "pore gechilam", "matha ghurie pore gechi", "chetona harano"
            ],
            "stroke_signs": [
                "mukh baka hoye geche", "haath pa obosh", "kotha bolte parchi na",
                "mukh beke geche", "kotha ladkhadacche", "ek pash obosh"
            ]
        },
        "routine_admin": {
            "appointment": [
                "appointment ache", "doctor dekhabo", "appointment er somoy", 
                "appointment check korte chai", "dr dekhanor time",
                "ajker appointment", "somoy poriborton", "deri hoye geche", "appointment check kora"
            ],
            "prescription": [
                "aushodh dorkar", "prescription", "aushodh sesh", 
                "repeat prescription", "tablet er kagoj",
                "prescripton sesh", "blood pressure er aushodh", "sugar er tablet", "pharmacy te pathano"
            ],
            "sample_drop": [
                "sample joma dibo", "urine test", "rokter sample", 
                "botol joma", "lab test er jonne",
                "prostab er sample", "rokter botol", "lab test joma"
            ],
            "interpreter": [
                "bangla boli", "english jani na", "dovashi dorkar", 
                "bangla bujhi", "interpreter lagbe",
                "bangla translator", "dovashi lagbe", "english pari na"
            ],
            "registration": [
                "notun patient", "form puron", "nhs number", 
                "thikana poriborton", "registration korte chai",
                "notun form", "thikana change", "family registration"
            ]
        },
        "minor_ailments": {
            "fever_cold": ["jor", "shordi", "kashi", "gola betha", "jor asche", "thanda laga", "kashi hochhe", "gola jola"],
            "stomach_pain": ["pet betha", "bad-hojom", "bomi", "pet kharap", "amashoy", "pet kharap", "ombol", "bomi bomi bhab"],
            "body_pain": ["matha betha", "komor betha", "haatu betha", "gae haat pae betha", "ga betha", "komor betha", "ghaar betha"]
        }
    },

    # =========================================================================
    # 8. SOMALI (Colloquial Latin)
    # =========================================================================
    "so": {
        "negation": [
            "maya", "ma", "ma jiro", "aanan", "ha", "ma rabo", "ma aqaano", "maba jiro",
            "ma jiro", "ma rabo", "ma garanayo", "ma ahan"
        ],
        "critical_symptoms": {
            "chest_pain": [
                "xanuun laabta", "laab xanuun", "feer xanuun", "wadno xanuun", 
                "laabta oo ku culus", "laabta oo gubanaysa", "feero xanuun",
                "wadno qabad", "feeraha oo gubanaya", "laab culus"
            ],
            "breathing_difficulty": [
                "neefsashada oo dhib ah", "neefta oo ku dhagta", "neefsan waayay", 
                "neef qaadasho la'aan", "neefta oo yaraata", "neef qabasho",
                "neef yarida", "neefta qabasho", "neeftii baa dhagtay"
            ],
            "severe_bleeding": [
                "dhiig bax xoog leh", "dhiig badan", "dhiig socda oo joogsan waayay", 
                "dhiig bax daran",
                "dhiig bax joogsi la'aan", "dhiig badan socda"
            ],
            "collapse": [
                "suuxdin", "dhicitaan", "wareer daran", "suuxay", "dhulka ku dhacay",
                "miir daboolan", "dhulka ayaan ku dhacay", "wareer daran"
            ],
            "stroke_signs": [
                "wajiga oo qalloocday", "dhinac qallalan", "hadalka oo xumaaday",
                "dhinac curyaan", "af qalloocan", "hadal la'aan"
            ]
        },
        "routine_admin": {
            "appointment": [
                "ballan baan leeyahay", "dhakhtar aragti", "waqtiga ballanta", 
                "ballan xaqiijin", "dhakhtarka inaan arko",
                "ballanteyda maanta", "bedelida ballanta", "soo daahay", "xaqiijinta ballanta"
            ],
            "prescription": [
                "dawo qoris", "dawooyin", "warqad dawo", "dawooyinkii dhamaaday", 
                "dawo cusboonaysiin",
                "dawooyinka dhiigkarka", "dawooyinka sonkorta", "cusbooneysiin dawo", "farmashiyaha"
            ],
            "sample_drop": [
                "baaritaan dhiig", "kaadi baaris", "dhalo keenis", "muunad la keenay", 
                "baaritaan sheybaar",
                "muunad kaadi", "dhiig baarista", "dhalo sheybaar"
            ],
            "interpreter": [
                "turjubaan baan rabaa", "ingiriisi ma hadlo", "af soomaali keliya", 
                "turjumaan codsi",
                "turjumaan af soomaali", "ingiriis ma aqaano", "qof ii turjuma"
            ],
            "registration": [
                "bukaanka cusub", "form buuxin", "lambarka nhs", "cinwaanka badalid",
                "diwaangelin cusub", "bedelida cinwaanka", "foomka cusub"
            ]
        },
        "minor_ailments": {
            "fever_cold": ["qandho", "hargab", "qufac", "cunaha oo xanuunaya", "duray", "qufac daran", "dhuun xanuun"],
            "stomach_pain": ["calool xanuun", "laab jex", "mataq", "shuban", "calool majiir", "laab qalac", "yalaalugo"],
            "body_pain": ["madax xanuun", "dhabar xanuun", "jilib xanuun", "muruq xanuun", "dhabar xanuun", "madax xanuun daran", "muruqyo xanuun"]
        }
    },

    # =========================================================================
    # 9. ROMANIAN (Colloquial Latin without diacritics)
    # =========================================================================
    "ro": {
        "negation": [
            "nu", "deloc", "fara", "n-am", "nu am", "deloc nu", "nici", "nicidecum",
            "deloc", "nu stiu", "nu vreau", "fara nimic"
        ],
        "critical_symptoms": {
            "chest_pain": [
                "durere in piept", "durere la piept", "intepaturi in piept", "strangere in piept", 
                "apasa pe piept", "durere de inima", "intepatura in piept",
                "infarct", "intepaturi la inima", "arsuri in piept", "durere radiaza in mana stanga"
            ],
            "breathing_difficulty": [
                "respiratie grea", "lipsa de aer", "nu pot respira", "ma sufoc", 
                "greu sa respir", "dificultate respiratorie", "nu am aer",
                "lipsa grava de aer", "criza de astm", "nu pot trage aer"
            ],
            "severe_bleeding": [
                "sangerare puternica", "mult sange", "curge mult sange", "hemoragie", 
                "nu se opreste sangele",
                "hemoragie puternica", "varsaturi cu sange", "sangele nu se opreste"
            ],
            "collapse": [
                "lesin", "am cazut", "pierderea cunostintei", "am ametit si am cazut", 
                "ameteli puternice",
                "am lesinat brusc", "cadere cu pierderea cunostintei", "stare de lesin"
            ],
            "stroke_signs": [
                "fata stramba", "mana amortita", "nu pot vorbi clar", "amorteala pe o parte",
                "paralizie faciala", "amorteala brat", "dificultate la vorbire"
            ]
        },
        "routine_admin": {
            "appointment": [
                "am programare", "la doctor", "ora programarii", "verificare programare", 
                "sa vad doctorul", "fac o programare",
                "programarea de azi", "intarziat la programare", "schimbare programare", "confirmare programare"
            ],
            "prescription": [
                "reteta", "medicamente", "reinnoire reteta", "am ramas fara medicamente", 
                "prescriptie medicala", "pastile",
                "reteta tensiune", "reteta diabet", "reinnoire reteta lunara", "trimitere farmacie"
            ],
            "sample_drop": [
                "proba urina", "analize sange", "aduc proba", "recipient proba", 
                "proba laborator", "analize",
                "aduc proba urina", "proba sange laborator", "recipient analize"
            ],
            "interpreter": [
                "translator", "nu vorbesc engleza", "interpret", "vorbesc doar romana", 
                "am nevoie de traducator",
                "translator romana", "nu inteleg engleza", "asistenta lingvistica"
            ],
            "registration": [
                "pacient nou", "completare formular", "numar nhs", "schimbare adresa",
                "inregistrare pacient nou", "schimbare adresa locuinta", "formular nou"
            ]
        },
        "minor_ailments": {
            "fever_cold": ["febra", "raceala", "tuse", "durere in gat", "nas infundat", "frisoane", "rosu in gat", "stranut", "guturai"],
            "stomach_pain": ["durere de burta", "arsuri la stomac", "varsaturi", "diaree", "greata", "crampe la stomac", "indigestie"],
            "body_pain": ["durere de cap", "durere de spate", "durere de genunchi", "dureri musculare", "durere de ceafa", "durere de articulatii", "spate blocat"]
        }
    }
}
