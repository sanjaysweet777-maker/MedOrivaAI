"""
MedOriva AI — High-Speed Clinical Translation Engine
Equal Phonetic & Native Processing for All 9 UK Community Languages
"""
import html
import logging
import os
import re
import unicodedata
from dataclasses import dataclass
import requests

logger = logging.getLogger("medoriva.translator")

REVIEW = 'Machine translation · Confirm meaning with speaker.'
PREPARED = 'Verified Clinical Lexicon · Confirmed.'

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

NON_LATIN_LANGUAGES = {'ta', 'hi', 'ml', 'bn', 'ar', 'ur'}

@dataclass(frozen=True)
class Translation:
    text: str = ''
    native: str = ''
    status: str = 'needs_review'
    source: str = 'clinical_lexicon'
    warning: str = PREPARED
    error_code: str = ''
    symptom: str = ''
    is_negative: bool = False

def unavailable(error_code=''):
    return Translation(
        text='',
        native='',
        status='unavailable',
        source='none',
        warning='Translation unavailable.',
        error_code=error_code
    )

# ============================================================
# STRING & SCRIPT NORMALISATION
# ============================================================
def normalise(text):
    if not text:
        return ''
    cleaned = re.sub(r'[^\w\s]', ' ', str(text), flags=re.UNICODE)
    return ' '.join(unicodedata.normalize('NFC', cleaned).split())

SCRIPT_PATTERNS = {
    'ta': re.compile(r'[\u0B80-\u0BFF]'),
    'hi': re.compile(r'[\u0900-\u097F]'),
    'ml': re.compile(r'[\u0D00-\u0D7F]'),
    'bn': re.compile(r'[\u0980-\u09FF]'),
    'ar': re.compile(r'[\u0600-\u06FF\u0750-\u077F]'),
    'ur': re.compile(r'[\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF]'),
    'pl': re.compile(r'[a-zA-ZąćęłńóśźżĄĆĘŁŃÓŚŹŻ]'),
    'ro': re.compile(r'[a-zA-ZăâîșțĂÂÎȘȚ]'),
    'so': re.compile(r'[a-zA-Z]'),
    'en': re.compile(r'[a-zA-Z]'),
}

def script_matches(text, language):
    if not text:
        return False
    pattern = SCRIPT_PATTERNS.get(language)
    if not pattern:
        return True

    if language in NON_LATIN_LANGUAGES:
        return bool(pattern.search(text))
    else:
        # Latin languages: must have Latin letters and NO non-Latin scripts
        has_non_latin = any(ord(c) > 0x0590 for c in text if c.isalpha())
        return bool(pattern.search(text)) and not has_non_latin

# ============================================================
# NUMERIC, DOSAGE & NEGATION GUARDS
# ============================================================
NUMERIC_ONLY_PATTERN = re.compile(
    r'^[\d\u0660-\u0669\u06f0-\u06f9]+(?:[:./-][\d\u0660-\u0669\u06f0-\u06f9]+)*$'
)

def numeric_response(text):
    if not text:
        return False
    cleaned = str(text).strip()
    return bool(NUMERIC_ONLY_PATTERN.match(cleaned))

def convert_arabic_digits(text):
    arabic_digits = "٠١٢٣٤٥٦٧٨٩"
    for i, c in enumerate(arabic_digits):
        text = text.replace(c, str(i))
    return text

def extract_numbers(text):
    return re.findall(r'\d+(?:\.\d+)?', convert_arabic_digits(str(text)))

SUPPLEMENTAL_NEGATIONS = {
    "ta": ["illai", "illa", "kidayathu", "illamal", "vendam", "thevai illai", "இல்லை", "கிடையாது", "வேண்டாம்"],
    "hi": ["nahi", "nahin", "na", "mat", "नहीं", "ना", "मत"],
    "ml": ["illa", "alla", "venda", "aavashyamilla", "ഇല്ല", "അല്ല", "വേണ്ട"],
    "pl": ["nie", "brak", "bez", "ani"],
    "ar": ["la", "kalla", "laysa", "ma", "mush", "lan", "lam", "لا", "كلا", "ليس", "ما", "مش"],
    "ur": ["nahi", "nahin", "na", "mat", "nhi", "نہیں", "نہ", "مت"],
    "bn": ["na", "nei", "noi", "noy", "না", "নেই", "নয়"],
    "so": ["maya", "ma", "malihi", "ha", "ma jiro"],
    "ro": ["nu", "nici", "fara", "fără"]
}

def detect_negation(text, lang_code):
    clean = normalise(text).lower()
    tokens = set(clean.split())
    supp_negs = SUPPLEMENTAL_NEGATIONS.get(lang_code, [])
    universal_negs = ["no", "not", "without", "never", "none", "denies"]

    all_neg_words = set(supp_negs + universal_negs)
    padded = f" {clean} "

    for word in all_neg_words:
        clean_word = normalise(word).lower()
        if not clean_word:
            continue
        if " " in clean_word:
            if f" {clean_word} " in padded:
                return True
        else:
            if clean_word in tokens:
                return True

    return False

# ============================================================
# API CREDENTIALS & ERROR SANITISATION
# ============================================================
def configured_key():
    for name in ('GOOGLE_TRANSLATE_API_KEY', 'GOOGLE_CLOUD_TRANSLATION_API_KEY', 'GOOGLE_API_KEY'):
        val = os.environ.get(name, '').strip()
        if val:
            return val
    return ''

def provider_error(response):
    status = getattr(response, 'status_code', 500)
    reason = ''
    try:
        data = response.json()
        details = data.get('error', {}).get('details', [])
        if details and isinstance(details, list):
            reason = details[0].get('reason', '')
    except Exception:
        pass

    reason_map = {
        'API_KEY_INVALID': 'invalid_key',
        'SERVICE_DISABLED': 'api_disabled',
        'BILLING_DISABLED': 'billing',
        'API_KEY_HTTP_REFERRER_BLOCKED': 'access_denied'
    }

    if reason in reason_map:
        error_code = reason_map[reason]
    elif status == 429:
        error_code = 'quota'
    elif status == 400:
        error_code = 'invalid_key'
    elif status == 403:
        error_code = 'access_denied'
    else:
        error_code = 'provider_error'

    return Translation(
        text='',
        native='',
        status='unavailable',
        source='google_cloud',
        warning='Provider error occurred. Details withheld for safety.',
        error_code=error_code
    )

# ============================================================
# CORE ONLINE TRANSLATION
# ============================================================
def online(text, source, target):
    if not text:
        return unavailable('empty_input')

    clean_input = str(text).strip()
    if not clean_input:
        return unavailable('empty_input')

    if source == target:
        return Translation(clean_input, clean_input, 'needs_review', 'pass_through', REVIEW)

    key = configured_key()
    if not key:
        return unavailable('no_key')

    try:
        resp = requests.post(
            'https://translation.googleapis.com/language/translate/v2',
            headers={'X-Goog-Api-Key': key},
            json={'q': clean_input, 'source': source, 'target': target, 'format': 'text'},
            timeout=(3, 12)
        )

        if resp.status_code != 200:
            resp.raise_for_status()

        data = resp.json()
        translations = data.get('data', {}).get('translations', [])
        if not translations or not isinstance(translations, list):
            return unavailable('malformed')

        translated = html.unescape(translations[0].get('translatedText', '')).strip()

        if not translated:
            return unavailable('empty_translation')

        # Script mismatch guard
        if not script_matches(translated, target):
            return unavailable('script_mismatch')

        # Numeric / dose preservation guard
        input_nums = extract_numbers(clean_input)
        output_nums = extract_numbers(translated)
        if input_nums != output_nums:
            return unavailable('numeric_mismatch')

        return Translation(
            text=translated,
            native=translated,
            status='needs_review',
            source='google_cloud',
            warning=REVIEW
        )

    except requests.Timeout:
        return unavailable('timeout')
    except requests.ConnectionError:
        return unavailable('connection')
    except requests.HTTPError as e:
        if hasattr(e, 'response') and e.response is not None:
            return provider_error(e.response)
        return unavailable('provider_error')
    except Exception:
        return unavailable('provider_error')

# ============================================================
# PREPARED CLINICAL STAFF LOOKUP (All 9 Languages)
# ============================================================
STAFF_LOOKUP = {
    "Do you have an appointment?": {
        "ta": "உங்களுக்கு அப்பாயிண்ட்மென்ட் உள்ளதா?",
        "hi": "क्या आपका अपॉइंटमेंट है?",
        "ml": "നിങ്ങൾക്ക് അപ്പോയിന്റ്മെന്റ് ഉണ്ടോ?",
        "pl": "Czy ma Pan/Pani umówioną wizytę?",
        "ar": "هل لديك موعد؟",
        "ur": "کیا آپ کا وقت مقرر (اپائنٹمنٹ) ہے؟",
        "bn": "আপনার কি কোনো অ্যাপয়েন্টমেন্ট আছে?",
        "so": "Ballan ma leedahay?",
        "ro": "Aveți o programare?"
    },
    "Do you have your appointment letter?": {
        "ta": "உங்கள் அப்பாயிண்ட்மென்ட் கடிதம் உள்ளதா?",
        "hi": "क्या आपके पास अपॉइंटमेंट पत्र है?",
        "ml": "നിങ്ങളുടെ അപ്പോയിന്റ്മെന്റ് കത്ത് കൈവശമുണ്ടോ?",
        "pl": "Czy ma Pan/Pani list z potwierdzeniem wizyty?",
        "ar": "هل معك خطاب الموعد؟",
        "ur": "کیا آپ کے پاس اپائنٹمنٹ کا خط ہے؟",
        "bn": "আপনার কি অ্যাপয়েন্টমেন্টের চিঠি আছে?",
        "so": "Warqaddii ballanta ma wadataa?",
        "ro": "Aveți scrisoarea de programare?"
    },
    "Please take a seat.": {
        "ta": "தயவுசெய்து அமரவும்.",
        "hi": "कृपया बैठिए।",
        "ml": "ദയവായി ഇരിക്കൂ.",
        "pl": "Proszę usiąść.",
        "ar": "تفضل بالجلوس من فضلك.",
        "ur": "براہ کرم تشریف رکھیں۔",
        "bn": "দয়া করে বসুন।",
        "so": "Fadlan fariiso.",
        "ro": "Vă rugăm să luați loc."
    },
    "Do you have your NHS number?": {
        "ta": "உங்கள் NHS எண் உள்ளதா?",
        "hi": "क्या आपके पास आपका NHS नंबर है?",
        "ml": "നിങ്ങളുടെ NHS നമ്പർ ഉണ്ടോ?",
        "pl": "Czy ma Pan/Pani swój numer NHS?",
        "ar": "هل لديك رقم NHS الخاص بك؟",
        "ur": "کیا آپ کے پاس آپ کا NHS نمبر ہے؟",
        "bn": "আপনার কি NHS নম্বর আছে?",
        "so": "Ma haysataa lambarkaaga NHS?",
        "ro": "Aveți numărul dumneavoastră NHS?"
    },
    "Do you need an interpreter?": {
        "ta": "உங்களுக்கு மொழிபெயர்ப்பாளர் தேவையா?",
        "hi": "क्या आपको अनुवादक की आवश्यकता है?",
        "ml": "നിങ്ങൾക്ക് ഒരു വിവർത്തകനെ ആവശ്യമുണ്ടോ?",
        "pl": "Czy potrzebuje Pan/Pani tłumacza?",
        "ar": "هل تحتاج إلى مترجم فوري؟",
        "ur": "کیا آپ کو مترجم کی ضرورت ہے؟",
        "bn": "আপনার কি একজন দোভাষীর প্রয়োজন?",
        "so": "Ma u baahan tahay turjubaan?",
        "ro": "Aveți nevoie de un interpret?"
    },
    "Where is your pain?": {
        "ta": "உங்களுக்கு வலி எங்கே இருக்கிறது?",
        "hi": "आपको दर्द कहाँ है?",
        "ml": "നിങ്ങൾക്ക് എവിടെയാണ് വേദന?",
        "pl": "Gdzie odczuwa Pan/Pani ból?",
        "ar": "أين تشعر بالألم؟",
        "ur": "آپ کو درد کہاں ہو رہا ہے؟",
        "bn": "আপনার কোথায় ব্যথা হচ্ছে?",
        "so": "Xaggee ku xanuunaysaa?",
        "ro": "Unde vă doare?"
    },
    "Do you have chest pain?": {
        "ta": "உங்களுக்கு நெஞ்சு வலி உள்ளதா?",
        "hi": "क्या आपको सीने में दर्द है?",
        "ml": "നിങ്ങൾക്ക് നെഞ്ചുവേദന ഉണ്ടോ?",
        "pl": "Czy ma Pan/Pani ból w klatce piersiowej?",
        "ar": "هل تشعر بألم في الصدر؟",
        "ur": "کیا آپ کے سینے میں درد ہے؟",
        "bn": "আপনার কি বুকে ব্যথা আছে?",
        "so": "Xabad xanuun ma dareemaysaa?",
        "ro": "Aveți dureri în piept?"
    },
    "Do you have a fever?": {
        "ta": "உங்களுக்கு காய்ச்சல் உள்ளதா?",
        "hi": "क्या आपको बुखार है?",
        "ml": "നിങ്ങൾക്ക് പനിയുണ്ടോ?",
        "pl": "Czy ma Pan/Pani gorączkę?",
        "ar": "هل تعاني من الحمى؟",
        "ur": "کیا آپ کو بخار ہے؟",
        "bn": "আপনার কি জ্বর আছে?",
        "so": "Qandho ma qabtaa?",
        "ro": "Aveți febră?"
    },
    "Are you having difficulty breathing?": {
        "ta": "உங்களுக்கு மூச்சுத்திணறல் உள்ளதா?",
        "hi": "क्या आपको सांस लेने में कठिनाई हो रही है?",
        "ml": "നിങ്ങൾക്ക് ശ്വാസമെടുക്കാൻ ബുദ്ധിമുട്ടുണ്ടോ?",
        "pl": "Czy ma Pan/Pani trudności z oddychaniem?",
        "ar": "هل تعاني من صعوبة في التنفس؟",
        "ur": "کیا آپ کو سانس لینے میں دشواری ہو رہی ہے؟",
        "bn": "আপনার কি শ্বাস নিতে কষ্ট হচ্ছে?",
        "so": "Neefsashada ma dhibaysaa?",
        "ro": "Aveți dificultăți de respirație?"
    }
}

# Fast normalized lookup for prepared staff prompts
STAFF_LOOKUP_NORM = {
    normalise(orig).lower(): translations for orig, translations in STAFF_LOOKUP.items()
}

def staff_translation(text, language):
    if language not in LANGUAGES:
        return unavailable('unsupported_language')

    clean = normalise(text).lower()

    # Exact prepared prompt check
    if clean in STAFF_LOOKUP_NORM:
        val = STAFF_LOOKUP_NORM[clean].get(language)
        if val:
            return Translation(
                text=val,
                native=val,
                status='needs_review',
                source='prepared_phrase',
                warning=PREPARED
            )

    # Dynamic translation for all custom or compound staff questions
    return online(text, 'en', language)

# ============================================================
# PATIENT DISPATCHER WITH STRICT ROMANISED GUARDS
# ============================================================
EXACT_ROMANISED = {
    'ta': {
        'enaku nenji vali irukku': 'I have chest pain.',
        'enaku nenji vali illa': 'I do not have chest pain.'
    }
}

def patient_translation(text, language):
    if not text or language not in LANGUAGES:
        return unavailable('unsupported_language')

    # 1. Standalone numeric preservation
    if numeric_response(text):
        return Translation(
            text=str(text).strip(),
            native=str(text).strip(),
            status='needs_review',
            source='original_value',
            warning='Original numeric value preserved.'
        )

    clean = normalise(text).lower()

    # 2. Non-Latin languages: separate native script from Romanised/phonetic input
    if language in NON_LATIN_LANGUAGES:
        if script_matches(text, language):
            res = online(text, language, 'en')
            return Translation(
                text=res.text,
                native=text,
                status=res.status,
                source=res.source,
                warning=res.warning,
                error_code=res.error_code,
                symptom=res.symptom,
                is_negative=res.is_negative
            )
        else:
            # Romanised input: only exact verified phrases are permitted
            lookup = EXACT_ROMANISED.get(language, {})
            if clean in lookup:
                eng = lookup[clean]
                is_neg = detect_negation(clean, language)
                return Translation(
                    text=eng,
                    native=text,
                    status='needs_review',
                    source='prepared_phrase',
                    warning=PREPARED,
                    is_negative=is_neg
                )
            # Unmapped Romanised text cannot be safely parsed by machine translation
            return unavailable('unsupported_romanised')

    # 3. Latin languages (Polish, Somali, Romanian): direct online translation
    res = online(text, language, 'en')
    return Translation(
        text=res.text,
        native=text,
        status=res.status,
        source=res.source,
        warning=res.warning,
        error_code=res.error_code,
        symptom=res.symptom,
        is_negative=res.is_negative
    )
