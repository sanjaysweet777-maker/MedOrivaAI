# blended_config.py
"""
MedOriva AI Ltd - Multi-Script Colloquial Lexicon & Negation Map
Version: 2.7 Production Lexicon Seed (Comprehensive 1000+ Token Expansion)
Coverage: All 9 MVP Languages (Tamil, Hindi, Malayalam, Polish, Arabic, Urdu, Bengali, Somali, Romanian)
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
            "therila", "enakku vendaam", "illavillai", "illaiye", "sariyilla", 
            "illanu sonnen", "varala", "theriyale", "aagala", "seiyala",
            "kadayathu", "venda", "enakku theriyathu", "mudila", "enakku illa"
        ],
        "critical_symptoms": {
            "chest_pain": [
                "nenji vali", "nenju vali", "marbu vali", "nenjil vali", 
                "nenju erichal", "nenju baaram", "nenju adaippu", "heart vali",
                "heart attack vanthurumo", "nenjula valikuthu", "edathu kai vali nenju vali", 
                "marbula vali", "nenju kuthuthu", "edathu thoal vali", "nenjula oosi kuthura maathiri", 
                "nenju edaikkuthu", "nenjula barama irukku", "nenju eriyuthu", "edathu kai valikuthu",
                "nenjula thik thiknu irukku", "marbu adaippu", "heart vali maathiri irukku"
            ],
            "breathing_difficulty": [
                "moochu thinaral", "swasa kolaru", "moochu vidamudiyala", 
                "moochu muttuthu", "moochu kasta", "breath kasta", "moochu idikkuthu",
                "moochu thinaruthu", "moochu vida kashtam", "swasam edukka mudiyala", 
                "asthma problem", "moochu vanga mudiyala", "moochu vida mudila", 
                "swasam kasta", "moochu ilukuthu", "moochu ninnu pochu", "swasam muttuthu"
            ],
            "severe_bleeding": [
                "athiga ratham", "rathapokku", "ratham varuthu", "ratham nikkala", 
                "blood vanthute irukku", "thaduka mudiyatha ratham",
                "ratham kottuthu", "ratham nikkave illa", "athiga rathapokku", 
                "ratham thadukka mudiyala", "ratham kakuren", "mookula ratham", "kaayathula ratham",
                "blood nillatha alavukku", "ratham vadithu", "perum rathapokku"
            ],
            "collapse": [
                "mayakkam", "keezhe vizhunthuten", "mayangi vizhunthuten", 
                "thalaisuthal", "surundu vizhunthuten", "bodham illa",
                "thala suthi vizhunthen", "mayangi vizhunthutaanga", "kan moodi vizhunthen", 
                "bodham poiduchu", "mayangi vizhunthen", "thidiernu vizhunthuten", "unconscious aayiten",
                "thala suthudhu keela vilunthen", "bodham illama vizhunthuten", "adi pattu vizhunthen"
            ],
            "stroke_signs": [
                "kai kaal vilangala", "vaai konita pochu", "pechu kolaru", 
                "kai thookka mudiyala", "orupakkam saanjikiduchu",
                "vaai orukku pochu", "kai kaal seyalpadala", "orupakkam asaikka mudiyala", 
                "vaai konikiduchu", "pechu varala", "oru pakkam thimiru", "pechu kolaraga irukku"
            ]
        },
        "routine_admin": {
            "appointment": [
                "appointment irukku", "doctor paakanum", "time enna", "book pannanum", 
                "dr appointment", "token irukka", "varavendiya neram", "appointment check",
                "iniku appointment", "reschedule pannanum", "late aayiduchu", "check-in pannanum", 
                "appointment cancellation", "doctor eppo varuvaaru", "token number", 
                "appointment maathanum", "dr paaka neram", "check-in machine velai seiyala",
                "en peyar listla irukka", "iniku slot irukka"
            ],
            "prescription": [
                "marunthu venum", "tablets", "marunthu seetu", "tablet ezhuthikudukanum", 
                "marunthu theernthupochu", "prescription renewal", "repeat prescription",
                "blood pressure tablet", "sugar marunthu", "inhaler venum", "chemist kitta anupanum", 
                "pharmacy collection", "marunthu edukka vanthen", "sugar tablet theernthuduchu",
                "bp marunthu venum", "tablets vanthurucha", "chemistku anupiteengala", "marunthu renew"
            ],
            "sample_drop": [
                "urine test", "blood test sample", "bottle kudukanum", "rathaparisothanai", 
                "siruneer sample", "lab sample drop", "sample bottle",
                "urine bottle kudukanum", "stool sample", "lab test kuduka vanthen", 
                "blood test results", "sample drop panna vanthen", "bottle handover",
                "labku kuduka vendiya sample", "blood test eppo result varum"
            ],
            "interpreter": [
                "tamil theriyum", "english theriyathu", "translator venum", 
                "tamil pesravanga irukangala", "interpreter thevai", "tamizh translator",
                "bilingual helper", "tamil interpreter podunga", "tamizhil pesa mudiyuma", 
                "mozhipeyarpalar", "english pesa mudiyathu", "tamil bhashai mattum", "tamil aal venum"
            ],
            "registration": [
                "new patient", "register pannanum", "address maathuvathu", 
                "nhs number", "form fill pannanum", "puthiya aal",
                "kudumbathoda register pannanum", "change of address", "proof of address", 
                "new registration", "puthiya noyaali", "veetu mugavari maathal", "form kudunga"
            ]
        },
        "minor_ailments": {
            "fever_cold": [
                "kaichal", "kulir", "sali", "irumal", "thondai vali", "fever irukku", 
                "kan vali", "mooku ozhukuthu", "adikkadi thummal", "sali pidichurukku",
                "thondai kandal", "udambu eriyuthu", "severe cold", "mooku adaichirukku"
            ],
            "stomach_pain": [
                "vathiru vali", "vayithu vali", "serimanam kolaru", "vanthi", "bedhi", 
                "vayiru porumbal", "acid problem", "serikkala", "vayithu kaduppu",
                "vayiru valikuthu", "loose motion", "vanthi varuthu", "vayiru erichal"
            ],
            "body_pain": [
                "kaal vali", "kai vali", "muthugu vali", "udambu vali", "thalai vali", 
                "muthugu pidichirukku", "kazhuthu vali", "moottu theimanum", "asathiya irukku",
                "thala valikuthu", "udambu ellam valikuthu", "kaal veengi pochu", "iduppu vali"
            ]
        }
    },

    # =========================================================================
    # 2. HINDI (Hinglish - Romanised Hindi)
    # =========================================================================
    "hi": {
        "negation": [
            "nahi", "nahin", "na", "mat", "kuch nahi", "nahi hai", "manaa", "bilkul nahi",
            "pata nahi", "mujhe nahi chahiye", "nahi maloom", "nhi", "nahi ji", "koi nahi", 
            "kabhi nahi", "aisi baat nahi", "mana kiya", "nahi chahiye", "kuch bhi nahi"
        ],
        "critical_symptoms": {
            "chest_pain": [
                "seene me dard", "chaati me dard", "sine me dard", "dil me dard", 
                "seene me chubhan", "chaati me dabav", "heart pain", "chhati dard",
                "seene me jakdan", "dil ka daura", "seene me aag lag rahi hai", "left arm me dard", 
                "seene me jalan", "dil baitha ja raha hai", "baayein haath me dard",
                "chhati me bojh", "seene me bahut dard", "dil ghabra raha hai", "sine me chubhan"
            ],
            "breathing_difficulty": [
                "saans lene me takleef", "dam ghutna", "saans phoolna", "saans nahi aa rahi", 
                "dum ghut raha hai", "saans lene me dikkat", "saans atakti hai",
                "saans atak rahi hai", "saans lene me dard", "oxygen ki kami", 
                "asthma ka daura", "saans ukhar rahi hai", "haanf raha hoon",
                "dam ghut raha", "saans lene me dikkat ho rahi hai", "saans phoolti hai"
            ],
            "severe_bleeding": [
                "zyada khoon", "khoon behna", "khoon nikal raha", "khoon nahi ruk raha", 
                "bahut khoon beh raha hai", "bleeding ruk nahi rahi",
                "khoon ki ulti", "khoon behna band nahi ho raha", "zyada bleeding", 
                "khoon gir raha hai", "rann se khoon", "khoon beh raha", "bahut zyada khoon"
            ],
            "collapse": [
                "behosh", "chakkar aakar girna", "gira pada", "chakkar aa rahe hain", 
                "aankhon ke aage andhera", "behosh ho gaya", "gir gaya",
                "chakkar aakar behosh", "gira pada mila", "hosh nahi hai", 
                "sudh budh kho baitha", "zameen par gir gaya", "behoshi si aa gayi"
            ],
            "stroke_signs": [
                "chehra aada hona", "haath pair sunn", "bolne me dikkat", 
                "haath utha nahi pa raha", "ek taraf kamzori",
                "muh tedha ho gaya", "ek taraf ka hissa sunn", "bolne me ladkhadahat", 
                "aadhi body sunn", "zubaan ladkhada rahi hai", "haath pair kaam nahi kar rahe"
            ]
        },
        "routine_admin": {
            "appointment": [
                "appointment hai", "doctor ko dikhana hai", "mulaqat ka samay", 
                "appointment lena hai", "dr sahab se milna hai", "appointment check karna hai", "time kab hai",
                "aaj ka appointment", "check-in karna hai", "late ho gaya", 
                "appointment badalna hai", "kiosk nahi chala", "dr se milne ka time",
                "mera naam list me hai", "aaj ka number", "appointment confirm karna hai", "reschedule karna"
            ],
            "prescription": [
                "dawai chahiye", "parchi", "goli", "dawai khatam ho gayi", 
                "repeat parchi", "prescription check karna", "dawa likhwani hai",
                "sugar ki dawai", "bp ki goli", "repeat dawai", "chemist ko bhej do", 
                "parcha renew", "dawai ki list", "chemist ke paas bhejo", "dawai lene aaya hoon"
            ],
            "sample_drop": [
                "peshab test", "blood sample dena hai", "bottle jama karni hai", 
                "khoon jaanch", "test ki sheeshi", "lab sample drop",
                "urine sample jama karna", "peshab ki jaanch", "khoon ki bottle", 
                "lab test parchi", "sample jama karna hai", "lab bottle drop"
            ],
            "interpreter": [
                "hindi aati hai", "english nahi aati", "tarjuma chahiye", 
                "interpreter chahiye", "hindi bolne wala chahiye", "angrezi samajh nahi aati",
                "hindi interpreter", "dubahshiya chahiye", "tarjumakar", "angrezi kam aati hai"
            ],
            "registration": [
                "naya mareez", "form bharna hai", "naam darj karna hai", 
                "nhs number dena hai", "pata badalna hai",
                "naya registration", "parivar ka form", "address change karna", 
                "id proof", "naya form bharna hai", "register karwana hai"
            ]
        },
        "minor_ailments": {
            "fever_cold": [
                "bukhar", "sardi", "zukaam", "khansi", "gale me kharash", "bukhar hai", 
                "chheek aana", "naak behna", "thand lagna", "gala kharab",
                "tez bukhar", "badan tap raha hai", "khansi zukaam", "gale me dard"
            ],
            "stomach_pain": [
                "pet me dard", "gas ban rahi hai", "ulti aa rahi hai", "dast", "pet kharab", 
                "acidity ho rahi hai", "khana hazam nahi hua", "pet phool raha hai",
                "pet me marod", "loose motion ho rahe", "ulti jaisa lag raha"
            ],
            "body_pain": [
                "sar dard", "kamar dard", "ghutne me dard", "badan dard", "taang me dard", 
                "gardana me dard", "pair sunn hona", "jism toot raha hai",
                "sar me bahut dard", "kamar me dard", "ghutna dukh raha hai"
            ]
        }
    },

    # =========================================================================
    # 3. MALAYALAM (Manglish - Romanised Malayalam)
    # =========================================================================
    "ml": {
        "negation": [
            "illa", "illatha", "alla", "illaa", "vendam", "ariyilla", "pattilla", "illallo",
            "illaathilla", "venda vendam", "alla alla", "illannu", "ariyaan pattilla",
            "illilla", "ariyathilla", "venda enikku", "onnum illa"
        ],
        "critical_symptoms": {
            "chest_pain": [
                "nenju vedana", "nenjil vedana", "chankil vedana", "nenju kuthal", 
                "nenjil oru bhaaratha", "heart pain", "nenjerichil", "nenjinu kuthu",
                "nenjil bhaaratha", "nenjil idichil", "idathu kai vedana", "nenjerichil kooduthal",
                "nenjil kuthunnapole", "heart attack aano", "nenjil oru amarthal", "nenjil iduppu"
            ],
            "breathing_difficulty": [
                "swasam muttal", "swasamedukkan budhimuttu", "swasam kittaathirikuka", 
                "moochu muttuka", "dam muttal", "swasam nilkkunnathu pole",
                "swasam kittaathe valayunnu", "valiv kooduthal", "swasakosha rogam",
                "swasam kittaathe", "swasam edukkaan pattunnilla", "valivu"
            ],
            "severe_bleeding": [
                "kooduthal chora", "raktham pokku", "raktham nilkkunnilla", 
                "chora pokk nilkunilla", "valiya thothil raktham",
                "chora nilkkatha pokku", "chora thuppal", "raktham thottu nilkilla",
                "adikkadi chora varunnu", "raktham nilkunnilla", "chora vanne thodangiyathu"
            ],
            "collapse": [
                "bodham kettu", "thala karangi veenu", "thala karakkam", 
                "bodham kettu veenu", "thalakarangi veenu",
                "bodham poyi", "thala pukanju veenu", "kanniruttu keri",
                "bodham illaathe veenu", "thiduthiyil veenu", "thala karangi nilathu veenu"
            ],
            "stroke_signs": [
                "kai kaal thalarchia", "mukham kodiya", "samsarikkan pattunnilla", "vaay kodi",
                "vaay orupakkam mukkuka", "kai thaazhthu pova", "pechu muzhumayilla",
                "orupakkam thalarunnu", "vaay kodi poyi", "samsaram vyakthamalla"
            ]
        },
        "routine_admin": {
            "appointment": [
                "appointment undu", "doctore kaananam", "dr appointment check", 
                "time ariyano", "appointment book cheyyanam", "token undonnu ariyaan",
                "innathe appointment", "check-in cheyyanam", "neram thettipoyi", 
                "appointment reschedule", "doctor eppol varum", "innu slot undo", "token number ariyaan"
            ],
            "prescription": [
                "marunnu venam", "prescription", "gulika theernnu", 
                "repeat prescription venam", "marunnu kurikkanam", "marunnu seetu",
                "sugar marunnu", "bp gulika", "marunnu list", "pharmacyilottu vidan",
                "gulika theernnupoyi", "repeat marunnu", "pharmacyilekku ayakkamo"
            ],
            "sample_drop": [
                "urine sample", "blood sample tharan undu", "bottle labil kodukkanam", 
                "raktha parishodhana", "mutra parishodhana",
                "mutra sample", "raktha parishodhana bottle", "lab test kodukkan",
                "sample bottle labil tharan", "test result eppol varum"
            ],
            "interpreter": [
                "malayalam mathram", "english ariyilla", "malayalam parayunna aal venam", 
                "interpreter venam", "translator sahayikkamo",
                "malayalam translator", "bilingual aal", "malayalam ariyunnavar",
                "english parayaan budhimuttaanu", "malayalathil parayaamo"
            ],
            "registration": [
                "puthiya aal", "register cheyyanam", "form puripikkanam", 
                "nhs number kodukkanam", "address maattan",
                "puthiya registration", "kudumbam register", "address change", "puthiya rogi form"
            ]
        },
        "minor_ailments": {
            "fever_cold": ["pani", "thaduppu", "chuma", "tholayil vedana", "mookkadappu", "mookkolichal", "thondavedana", "thummal", "chuma kooduthal", "kaduutha pani", "paniyum thummalum"],
            "stomach_pain": ["vayar vedana", "vayaril kadi", "chadikkal", "vayaril asukham", "vayaru puramottal", "gastro trouble", "charthi", "vayarozhichil", "vayattil erichil"],
            "body_pain": ["thala vedana", "kaal vedana", "nadukku vedana", "kai vedana", "kazhuthu vedana", "moottu thalaru", "udambu muzhuvan vedana", "thala choril", "kaal muluvan vedana"]
        }
    },

    # =========================================================================
    # 4. POLISH (Colloquial Latin / Phonetic without diacritics)
    # =========================================================================
    "pl": {
        "negation": [
            "nie", "brak", "bez", "nie ma", "wcale", "ani", "zadnego",
            "nie chce", "nie wiem", "w ogole nie", "nie mam pojecia", "nigdy",
            "zupelnie nie", "nie potrzebuje", "zadna", "nie zgadzam sie"
        ],
        "critical_symptoms": {
            "chest_pain": [
                "bol w klatce", "bolu w klatce", "bol w piersiach", "pieczenie w klatce", 
                "ucisk w klatce piersiowej", "klucie w sercu", "klatka boli", "bol serca",
                "sciskanie w klatce", "silny bol serca", "bol promieniuje do lewej reki", 
                "pieczenie w mostku", "piekacy bol w klatce", "dusznosc i bol serca", "zawal serca"
            ],
            "breathing_difficulty": [
                "dusznosc", "problemy z oddychaniem", "brak tchu", "nie moge oddychac", 
                "ciezko oddychac", "duszno mi", "dusze sie",
                "dusze sie w nocy", "atak astmy", "trudno zlapac oddech",
                "plytki oddech", "brak powietrza", "nie moge zlapac tchu"
            ],
            "severe_bleeding": [
                "silne krwawienie", "krew leci", "duzo krwi", "krwotok", 
                "krew nie zatrzymuje sie", "krwawi mocno",
                "krwawienie z rany", "wymioty z krwia", "masywny krwotok", "nie moge zatamowac krwi"
            ],
            "collapse": [
                "zaslabniecie", "omdlenie", "utrata przytomnosci", "upadlem", 
                "kreci mi sie w glowie", "zemdlalem",
                "upadek z utrata przytomnosci", "omdlalem nagle", "mdlosci i ciemno przed oczami",
                "stracilem przytomnosc", "zemdlalam na podloge"
            ],
            "stroke_signs": [
                "opadanie kacika ust", "dretwienie reki", "belkotliwa mowa", 
                "niedowlad reki", "paraliz twarzy",
                "asymetria twarzy", "niedowlad polowiczy", "zaburzenia mowy", "dretwienie ciala"
            ]
        },
        "routine_admin": {
            "appointment": [
                "mam wizyte", "do lekarza", "umowiona wizyta", "jaka godzina wizyty", 
                "sprawdzic wizyte", "chce sie umowic", "godzina wizyty",
                "dzisiejsza wizyta", "przelozyc wizyte", "spozniony na wizyte", 
                "potwierdzic obecnosc", "kiosk nie dziala", "spoznilem sie", "odwolac wizyte", "kiedy lekarz przyjmie"
            ],
            "prescription": [
                "recepta", "leki", "powtorka lekow", "skonczyly sie leki", 
                "chce recepte", "zamowic recepte", "lekarstwa",
                "leki stale", "recepta na cisnienie", "odnowic recepte", 
                "leki na cukrzyce", "przeslac do apteki", "zamowienie recepty", "recepta powtorna"
            ],
            "sample_drop": [
                "probka moczu", "badanie krwi", "oddac probke", "mocz do badania", 
                "pojemnik z probka", "probka do laboratorium",
                "probka do laboratorium", "pojemnik na kal", "probka krwi", "oddanie moczu",
                "wyniki badan", "zostawic probke"
            ],
            "interpreter": [
                "tlumacz", "nie mowie po angielsku", "potrzebuje tlumacza", 
                "jezyk polski", "tlumacz polski", "pomoc jezykowa",
                "tlumacz jezyka polskiego", "potrzebna pomoc jezykowa", "tlumacz na wizycie", "po polsku prosze"
            ],
            "registration": [
                "nowy pacjent", "formularz rejestracji", "zapisac sie", 
                "numer nhs", "zmiana adresu", "zarejestrowac sie",
                "nowa rejestracja", "zmiana przychodni", "dokument tozsamosci", 
                "aktualizacja danych", "zapisac rodzine", "formularz do wypelnienia"
            ]
        },
        "minor_ailments": {
            "fever_cold": ["goraczka", "przeziebienie", "kaszel", "bol gardla", "katar", "dreszcze", "chrypka", "kichanie", "zapalenie zatok", "wysoka goraczka", "cieknacy nos"],
            "stomach_pain": ["bol brzucha", "niestrawnosc", "wymioty", "biegunka", "zgaga", "zgage", "wymiotowanie", "zatrucie pokarmowe", "wzdecia", "skurcze zoladka"],
            "body_pain": ["bol glowy", "bol plecow", "bol kolana", "bol nogi", "bol kregoslupa", "bol stawow", "bol w krzyzu", "bol miesni", "bol karku", "straszny bol glowy"]
        }
    },

    # =========================================================================
    # 5. ARABIC (Arabizi / Franco-Arabic Numbers: 2=hamza, 3='ayn, 7=ha)
    # =========================================================================
    "ar": {
        "negation": [
            "la", "mosh", "ma", "mish", "laa", "mu", "laysa", "wala", "maba",
            "kalla", "la a3rif", "ma baddi", "abadan", "ghayr",
            "mish lazem", "ma fi", "aslan la", "laysat", "ma 3andi"
        ],
        "critical_symptoms": {
            "chest_pain": [
                "wajaa bel sadr", "alam fil sadr", "waja3 bel sadr", "sedri biwja3ni", 
                "daght 3al sadr", "alam qalb", "waja3 sadr shadid", "alam bel sadr",
                "alam qalbi", "harqa bel sadr", "waja3 el alb", "thokal 3al sadr",
                "sedri 3am yewja3ni", "harqan bel sadr", "alam qawi bi sedri", "sadri maskouk"
            ],
            "breathing_difficulty": [
                "diq tanaffus", "deeq tanafos", "mish qader atanfas", "kanka", 
                "tasarou3 tanaffos", "nafasi makhtouq", "so3oubet tanaffos",
                "azmet rabou", "tanaffos sa3b", "e5tenaq", "ma fi hawa",
                "mish 3aref akhod nafasi", "ikhtinaq", "da2 nafasi"
            ],
            "severe_bleeding": [
                "nazif shadid", "dam kteer", "dem 3am yenzel", "nazif la yatawaqaf", 
                "dam ktir 3am yusil", "nazif qawi",
                "nezif damawi", "istifrāgh dam", "dam la yatawaqaf",
                "nazeef qawi", "dam ma bywa2ef", "jere7 3am yenzef"
            ],
            "collapse": [
                "ighma", "waqa3t", "ghameyt", "dekhit", "faqad el wa3y", 
                "dawkha shadida", "waqa3 3al ard",
                "ghayboba", "saqatt ardhan", "sodam",
                "wqe3et 3al ard", "ghameyet men el waja3", "dawkha w oqou3"
            ],
            "stroke_signs": [
                "shelel nosfi", "i3wijaj bel fam", "so3ouba bel kalam", 
                "id ma bettaharrak", "tanamol bel wajh",
                "falaj", "famm a3waj", "thiql bel lisan", "nos wejji ma byemshi"
            ]
        },
        "routine_admin": {
            "appointment": [
                "3andi maw3ed", "maw3ed ma3 el doctor", "jaayt 3al maw3ed", 
                "eza 3andi maw3ed", "baddi chuf el doctor", "tasjil dukhul", "maw3idi",
                "maw3ed el youm", "ta2khir 3al maw3ed", "taghyir el maw3ed", "ta2kid maw3ed",
                "ta2kheer 3al maw3ed", "kiosk kharban", "tasjeel 7oudour", "maw3ed jdid"
            ],
            "prescription": [
                "wasfa tibbiya", "adwiya", "baddi dawa", "kholos ed dawa", 
                "tajdid wasfa", "habat dawa", "wasfet dawa",
                "dawa daqet el alb", "dawa el sokkari", "wasfa motakarrira", "irsil lal saydaliya",
                "tajdeed wasfet el dawa", "dawa el daght", "estelam dawa"
            ],
            "sample_drop": [
                "fahs dam", "3aynet bawl", "fahs", "taslim 3ayne", 
                "3olbat fahs", "mokhtabar", "tahlil dam",
                "tahlil bawl", "taslim 3olba", "tahlil mokhtabar", "fahs dam",
                "tasleem 3aynat", "natijet el fahs", "3elbet tahlil"
            ],
            "interpreter": [
                "motarjem", "ma behki inglizi", "baddi mutarjim", 
                "motarjem 3arabi", "la a3rif engilizi", "motarjima",
                "mutarjem arabi", "la afham englizi", "baddi had ytarjim",
                "tarjama arabiya", "baddi motarjem lil maw3ed"
            ],
            "registration": [
                "marid jadid", "ta3biat istimara", "raqam nhs", 
                "taghyir 3onwan", "tasjil marid",
                "tasjil a3ila", "tabdil 3onwan", "awraq el tasjil",
                "tasjeel jadid", "istimarat tasjeel", "baddi etsajjal"
            ]
        },
        "minor_ailments": {
            "fever_cold": ["harara", "sukhuna", "rashih", "sa3la", "wajaa halq", "bard", "zahza", "alam bel hanjara", "zukam", "harara 3aliya", "sa3leh 2awiyi"],
            "stomach_pain": ["wajaa batn", "maghs", "istifragh", "is-hal", "hrara bel me3de", "alam me3de", "lu3an nafs", "taqyoo", "hrara", "waja3 batni", "es-hal qawi"],
            "body_pain": ["wajaa ras", "suda3", "alam zaher", "wajaa rokba", "alam mafasel", "waja3 zahar", "alam mafasel", "suda3 nosfi", "wajaa raas qawi", "waja3 dahr"]
        }
    },

    # =========================================================================
    # 6. URDU (Roman Urdu)
    # =========================================================================
    "ur": {
        "negation": [
            "nahi", "nahin", "na", "mat", "kuch nahi", "nahi hai", "mana", "hargiz nahi",
            "nahi maloom", "mujhe nahi chahiye", "hargiz nahi", "bilkul nahi",
            "nhi", "nahi ji", "koi nahi", "kuch b nahi", "mujhe nahi lagta"
        ],
        "critical_symptoms": {
            "chest_pain": [
                "seene mein dard", "chati mein dard", "dil mein dard", "seene pe bojh", 
                "chhati mein jalan", "dil ka daura", "chhati dard",
                "dil ka daura", "seene mein ghutan", "baayein baazu mein dard", "chhati mein daban",
                "seene me shadeed dard", "dil pe bojh", "seene me aag", "dil ghabra raha hai"
            ],
            "breathing_difficulty": [
                "saans lene mein dushwari", "saans phool rahi hai", "dam ghut raha hai", 
                "saans ruk rahi hai", "saans ki takleef", "dam ghutna",
                "dama ka daura", "saans rukh rahi hai", "saans ka masla",
                "saans lene me shadeed takleef", "dam ghutne laga", "oxygen kam ho gayi"
            ],
            "severe_bleeding": [
                "bohot khoon", "khoon beh raha hai", "khoon nahi ruk raha", 
                "zyada khoon nikal raha hai", "shadeed khoon",
                "khoon ki ultiyan", "shadeed khoon behna", "khoon band nahi ho raha",
                "khoon nikalta ja raha hai", "khoon jari hai"
            ],
            "collapse": [
                "behosh ho gaya", "chakkar aa kar gir gaya", "gira pada", 
                "hosh kho diya", "aankhon ke aage andhera",
                "sudh budh kho baitha", "gir parha", "chakar aa gaye",
                "behosh parha tha", "chakkar aakar behoshi", "gash aa gaya"
            ],
            "stroke_signs": [
                "chehra terha ho gaya", "haath sunn", "awaz ladkhada rahi hai", "zuban band",
                "chehra murna", "zuban band hona", "jism ka hissa sunn",
                "muh terha ho gaya", "ek taraf ka faalij", "bolne me rukawat"
            ]
        },
        "routine_admin": {
            "appointment": [
                "appointment hai", "doctor se milna hai", "appointment check karni hai", 
                "dr sahab se milne ka time", "appointment book karwani hai",
                "aaj ki appointment", "waqt badalna hai", "late ho gaya", "appointment confirm karna",
                "check-in machine nahi chal rahi", "doctor ka waqt", "naam check karwayen"
            ],
            "prescription": [
                "dawa chahiye", "nuskha", "parchi", "dawaiyan khatam", 
                "repeat prescription", "goli likhwani hai",
                "sugar ki dawai", "blood pressure ki goli", "repeat nuskha", "pharmacy bhejna",
                "dawai khatam ho gayi hai", "parchi renew karwani hai", "chemist ke paas bhejein"
            ],
            "sample_drop": [
                "sample jama karwana hai", "urine test", "khoon ka sample", 
                "test ki bottle", "lab mein dena hai",
                "peshab ka sample", "khoon ki sheeshi", "test ki report",
                "lab me bottle deni hai", "sample jama karna"
            ],
            "interpreter": [
                "urdu bolta hoon", "angrezi nahi aati", "interpreter chahiye", 
                "urdu tarjuma", "motarjim chahiye",
                "urdu motarjim", "angrezi samajh nahi aati", "urdu tarjuma karwana",
                "koi urdu bolne wala", "urdu translator chahiye"
            ],
            "registration": [
                "naya mareez", "form bharna", "naam register karna", 
                "nhs number", "pata badalna",
                "naya registration", "khandan ka form", "pata tabdeel karna",
                "naye mareez ka indiraaj", "form dena"
            ]
        },
        "minor_ailments": {
            "fever_cold": ["bukhar", "zukam", "khansi", "gale mein kharash", "bukhar charh gaya", "nazla", "zukam", "gale ka dard", "thand lagna", "shadeed bukhar", "naak beh rahi hai"],
            "stomach_pain": ["pait mein dard", "gas", "ulti", "pait kharab", "dast", "hazma kharab", "ulti aana", "pait ka maror", "pait me shadeed maror", "badhazmi"],
            "body_pain": ["sar mein dard", "kamar dard", "jism mein dard", "ghutnay ka dard", "kamar ka dard", "pathon mein dard", "jism tootna", "sar me shadeed dard", "ghutno me takleef"]
        }
    },

    # =========================================================================
    # 7. BENGALI (Banglish - Romanised Bengali)
    # =========================================================================
    "bn": {
        "negation": [
            "na", "nei", "ni", "noy", "lagbe na", "jani na", "parbo na", "kokhono na",
            "na na", "jani na", "lagbe na", "kokhono noi",
            "hobe na", "amar nei", "dorkar nei", "kichu na"
        ],
        "critical_symptoms": {
            "chest_pain": [
                "bukey betha", "buker betha", "bukey chap", "buk jole jache", 
                "bukey dhorfor", "heart betha", "bukey betha ache",
                "heart attack er moto", "buker moddhe chap", "baam haath betha", "buk jolche",
                "bukey khub betha", "chati betha", "buker moddhe dhorfor kora", "chati jolche"
            ],
            "breathing_difficulty": [
                "shash kosto", "shash nite koshto", "dam bondho hoye asche", 
                "shash phule jacche", "shash nite parchi na", "dam atke asche",
                "hafe jacchi", "shash pawa jacche na", "asthma problem",
                "dam atke asche", "shash bondho hoye asche", "shash nite pari na"
            ],
            "severe_bleeding": [
                "onek rokto", "rokto porche", "rokto thamche na", 
                "rokto kharon", "rokto bondho hocche na",
                "onek beshi rokto", "rokto jhora", "rokto thamche na",
                "khub beshi rokto", "rokto pora bondho hocche na"
            ],
            "collapse": [
                "ogyan hoye gechi", "matha ghure pore gechi", "matha ghurche", 
                "behosh hoye porechi", "pore gechi",
                "pore gechilam", "matha ghurie pore gechi", "chetona harano",
                "ogyan hoye porechi", "matha ghuriye pore gela"
            ],
            "stroke_signs": [
                "mukh baka hoye geche", "haath pa obosh", "kotha bolte parchi na",
                "mukh beke geche", "kotha ladkhadacche", "ek pash obosh",
                "haath tula jay na", "mukher ek pash beke geche"
            ]
        },
        "routine_admin": {
            "appointment": [
                "appointment ache", "doctor dekhabo", "appointment er somoy", 
                "appointment check korte chai", "dr dekhanor time",
                "ajker appointment", "somoy poriborton", "deri hoye geche", "appointment check kora",
                "doctor er shathe dekha", "kiosk kaj korche na", "appointment confirm kora"
            ],
            "prescription": [
                "aushodh dorkar", "prescription", "aushodh sesh", 
                "repeat prescription", "tablet er kagoj",
                "prescripton sesh", "blood pressure er aushodh", "sugar er tablet", 
                "pharmacy te pathano", "dawai sesh", "notun prescription"
            ],
            "sample_drop": [
                "sample joma dibo", "urine test", "rokter sample", 
                "botol joma", "lab test er jonne",
                "prostab er sample", "rokter botol", "lab test joma",
                "urine bottle joma", "sample handover"
            ],
            "interpreter": [
                "bangla boli", "english jani na", "dovashi dorkar", 
                "bangla bujhi", "interpreter lagbe",
                "bangla translator", "dovashi lagbe", "english pari na",
                "bangla bolte chai", "dovashir sahayyo"
            ],
            "registration": [
                "notun patient", "form puron", "nhs number", 
                "thikana poriborton", "registration korte chai",
                "notun form", "thikana change", "family registration",
                "notun nam lekha", "notun patient registration"
            ]
        },
        "minor_ailments": {
            "fever_cold": ["jor", "shordi", "kashi", "gola betha", "jor asche", "thanda laga", "kashi hochhe", "gola jola", "onek jor", "nak die jol porche"],
            "stomach_pain": ["pet betha", "bad-hojom", "bomi", "pet kharap", "amashoy", "pet kharap", "ombol", "bomi bomi bhab", "pet kamrano", "patla paykhana"],
            "body_pain": ["matha betha", "komor betha", "haatu betha", "gae haat pae betha", "ga betha", "komor betha", "ghaar betha", "khub matha betha"]
        }
    },

    # =========================================================================
    # 8. SOMALI (Colloquial Latin)
    # =========================================================================
    "so": {
        "negation": [
            "maya", "ma", "ma jiro", "aanan", "ha", "ma rabo", "ma aqaano", "maba jiro",
            "ma jiro", "ma rabo", "ma garanayo", "ma ahan",
            "marna", "waxba", "ma doonayo", "ma lihi"
        ],
        "critical_symptoms": {
            "chest_pain": [
                "xanuun laabta", "laab xanuun", "feer xanuun", "wadno xanuun", 
                "laabta oo ku culus", "laabta oo gubanaysa", "feero xanuun",
                "wadno qabad", "feeraha oo gubanaya", "laab culus",
                "xabad xanuun daran", "wadno garaac daran", "laabta oo i xanuunaysa"
            ],
            "breathing_difficulty": [
                "neefsashada oo dhib ah", "neefta oo ku dhagta", "neefsan waayay", 
                "neef qaadasho la'aan", "neefta oo yaraata", "neef qabasho",
                "neef yarida", "neefta qabasho", "neeftii baa dhagtay",
                "neef qaadashada oo adag", "neefta ayaa igu dhagtay"
            ],
            "severe_bleeding": [
                "dhiig bax xoog leh", "dhiig badan", "dhiig socda oo joogsan waayay", 
                "dhiig bax daran",
                "dhiig bax joogsi la'aan", "dhiig badan socda", "dhiig badan ayaa iga socda"
            ],
            "collapse": [
                "suuxdin", "dhicitaan", "wareer daran", "suuxay", "dhulka ku dhacay",
                "miir daboolan", "dhulka ayaan ku dhacay", "wareer daran",
                "miir beelid", "suuxdin daran"
            ],
            "stroke_signs": [
                "wajiga oo qalloocday", "dhinac qallalan", "hadalka oo xumaaday",
                "dhinac curyaan", "af qalloocan", "hadal la'aan", "dhinac baa i qalalay"
            ]
        },
        "routine_admin": {
            "appointment": [
                "ballan baan leeyahay", "dhakhtar aragti", "waqtiga ballanta", 
                "ballan xaqiijin", "dhakhtarka inaan arko",
                "ballanteyda maanta", "bedelida ballanta", "soo daahay", "xaqiijinta ballanta",
                "ballan cusub", "dhakhtarka aragti maanta", "ballan xaqiiji"
            ],
            "prescription": [
                "dawo qoris", "dawooyin", "warqad dawo", "dawooyinkii dhamaaday", 
                "dawo cusboonaysiin",
                "dawooyinka dhiigkarka", "dawooyinka sonkorta", "cusbooneysiin dawo", "farmashiyaha",
                "dawo soo qaadasho", "warqada dawada"
            ],
            "sample_drop": [
                "baaritaan dhiig", "kaadi baaris", "dhalo keenis", "muunad la keenay", 
                "baaritaan sheybaar",
                "muunad kaadi", "dhiig baarista", "dhalo sheybaar",
                "keenista muunada", "baaritaan shaybaar"
            ],
            "interpreter": [
                "turjubaan baan rabaa", "ingiriisi ma hadlo", "af soomaali keliya", 
                "turjumaan codsi",
                "turjumaan af soomaali", "ingiriis ma aqaano", "qof ii turjuma",
                "turjubaan soomaali", "af ingiriis ma fahmo"
            ],
            "registration": [
                "bukaanka cusub", "form buuxin", "lambarka nhs", "cinwaanka badalid",
                "diwaangelin cusub", "bedelida cinwaanka", "foomka cusub",
                "is diiwaangelin", "diiwaangeli qoyska"
            ]
        },
        "minor_ailments": {
            "fever_cold": ["qandho", "hargab", "qufac", "cunaha oo xanuunaya", "duray", "qufac daran", "dhuun xanuun", "qandho xoog leh"],
            "stomach_pain": ["calool xanuun", "laab jex", "mataq", "shuban", "calool majiir", "laab qalac", "yalaalugo", "calool socod"],
            "body_pain": ["madax xanuun", "dhabar xanuun", "jilib xanuun", "muruq xanuun", "dhabar xanuun", "madax xanuun daran", "muruqyo xanuun", "kala goysyo xanuun"]
        }
    },

    # =========================================================================
    # 9. ROMANIAN (Colloquial Latin without diacritics)
    # =========================================================================
    "ro": {
        "negation": [
            "nu", "deloc", "fara", "n-am", "nu am", "deloc nu", "nici", "nicidecum",
            "deloc", "nu stiu", "nu vreau", "fara nimic",
            "niciodata", "nu doresc", "deloc nu am", "nu este"
        ],
        "critical_symptoms": {
            "chest_pain": [
                "durere in piept", "durere la piept", "intepaturi in piept", "strangere in piept", 
                "apasa pe piept", "durere de inima", "intepatura in piept",
                "infarct", "intepaturi la inima", "arsuri in piept", "durere radiaza in mana stanga",
                "presiune pe piept", "apasare in piept", "durere puternica la inima"
            ],
            "breathing_difficulty": [
                "respiratie grea", "lipsa de aer", "nu pot respira", "ma sufoc", 
                "greu sa respir", "dificultate respiratorie", "nu am aer",
                "lipsa grava de aer", "criza de astm", "nu pot trage aer",
                "respir greu", "greutate in respiratie", "senzatie de sufocare"
            ],
            "severe_bleeding": [
                "sangerare puternica", "mult sange", "curge mult sange", "hemoragie", 
                "nu se opreste sangele",
                "hemoragie puternica", "varsaturi cu sange", "sangele nu se opreste",
                "pierdere mare de sange", "curge sange intruna"
            ],
            "collapse": [
                "lesin", "am cazut", "pierderea cunostintei", "am ametit si am cazut", 
                "ameteli puternice",
                "am lesinat brusc", "cadere cu pierderea cunostintei", "stare de lesin",
                "am picat jos", "am lesinat"
            ],
            "stroke_signs": [
                "fata stramba", "mana amortita", "nu pot vorbi clar", "amorteala pe o parte",
                "paralizie faciala", "amorteala brat", "dificultate la vorbire",
                "gura stramba", "amorteala pe jumatate de corp"
            ]
        },
        "routine_admin": {
            "appointment": [
                "am programare", "la doctor", "ora programarii", "verificare programare", 
                "sa vad doctorul", "fac o programare",
                "programarea de azi", "intarziat la programare", "schimbare programare", "confirmare programare",
                "am intarziat", "kioscul nu merge", "anulare programare", "cand ma primeste medicul"
            ],
            "prescription": [
                "reteta", "medicamente", "reinnoire reteta", "am ramas fara medicamente", 
                "prescriptie medicala", "pastile",
                "reteta tensiune", "reteta diabet", "reinnoire reteta lunara", "trimitere farmacie",
                "reteta compensata", "pastile de tensiune", "trimiteti la farmacie"
            ],
            "sample_drop": [
                "proba urina", "analize sange", "aduc proba", "recipient proba", 
                "proba laborator", "analize",
                "aduc proba urina", "proba sange laborator", "recipient analize",
                "las proba", "rezultate analize"
            ],
            "interpreter": [
                "translator", "nu vorbesc engleza", "interpret", "vorbesc doar romana", 
                "am nevoie de traducator",
                "translator romana", "nu inteleg engleza", "asistenta lingvistica",
                "traducator romana", "as dori un translator"
            ],
            "registration": [
                "pacient nou", "completare formular", "numar nhs", "schimbare adresa",
                "inregistrare pacient nou", "schimbare adresa locuinta", "formular nou",
                "inregistrare familie", "schimbare de adresa"
            ]
        },
        "minor_ailments": {
            "fever_cold": ["febra", "raceala", "tuse", "durere in gat", "nas infundat", "frisoane", "rosu in gat", "stranut", "guturai", "febra mare", "tuse seaca"],
            "stomach_pain": ["durere de burta", "arsuri la stomac", "varsaturi", "diaree", "greata", "crampe la stomac", "indigestie", "stomac deranjat", "stare de voma"],
            "body_pain": ["durere de cap", "durere de spate", "durere de genunchi", "dureri musculare", "durere de ceafa", "durere de articulatii", "spate blocat", "durere puternica de cap"]
        }
    }
}
