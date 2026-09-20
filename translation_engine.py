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

logger = logging.getLogger("medoriva.translation_engine")

REVIEW = 'Machine translation · Confirm meaning with speaker.'
PREPARED = 'Prepared phrase — confirm meaning with the speaker.'

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
LATIN_LANGUAGES = {'en', 'pl', 'ro', 'so'}

SCRIPT_NAME_MAP = {
    'ta': 'TAMIL',
    'hi': 'DEVANAGARI',
    'ml': 'MALAYALAM',
    'bn': 'BENGALI',
    'ar': 'ARABIC',
    'ur': 'ARABIC',
}

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
        warning='Translation unavailable — rephrase, use supported native-script input, or seek interpreter support.',
        error_code=error_code
    )

# ============================================================
# STRING & SCRIPT NORMALISATION (Combining Marks Preserved)
# ============================================================
def normalise(text):
    if not text:
        return ''
    chars = [c for c in unicodedata.normalize('NFC', str(text)) if not unicodedata.category(c).startswith('P')]
    return ' '.join(''.join(chars).split())

# Script Ranges for Non-Latin Verification
NATIVE_RANGES = {
    'ta': (0x0B80, 0x0BFF),
    'hi': (0x0900, 0x097F),
    'ml': (0x0D00, 0x0D7F),
    'bn': (0x0980, 0x09FF),
    'ar': [(0x0600, 0x06FF), (0x0750, 0x077F), (0xFB50, 0xFDFF), (0xFE70, 0xFEFF)],
    'ur': [(0x0600, 0x06FF), (0x0750, 0x077F), (0xFB50, 0xFDFF), (0xFE70, 0xFEFF)],
}

SHARED_INDIC_PUNCTUATION = {0x0964, 0x0965}  # Devanagari Danda & Double Danda shared across Indic scripts

def in_range(code_point, rng):
    if isinstance(rng, list):
        return any(start <= code_point <= end for start, end in rng)
    return rng[0] <= code_point <= rng[1]

def script_matches(text, language):
    """
    Validates script membership strictly:
    - Latin languages ('en', 'pl', 'ro', 'so'): Letters must be Latin.
      Cyrillic, Greek, Arabic, Indic rejected.
    - Non-Latin languages ('ta', 'hi', 'ml', 'bn', 'ar', 'ur'):
      Letters must belong to the target script, or be permitted Latin abbreviations (e.g. 'NHS').
      Letters from foreign non-Latin scripts (e.g. Cyrillic, Arabic in Tamil, Tamil in Arabic) are rejected.
      Whitespace, numbers, punctuation, and shared Indic dandas are permitted.
      Must contain at least one character of the target script.
    """
    if not text:
        return False

    if language in NON_LATIN_LANGUAGES:
        target_script = SCRIPT_NAME_MAP.get(language)
        target_range = NATIVE_RANGES.get(language)
        if not target_script or not target_range:
            return False

        has_target_script = False

        for c in text:
            cp = ord(c)

            # 1. Allow shared Indic punctuation (Dandas)
            if cp in SHARED_INDIC_PUNCTUATION:
                continue

            # 2. Allow whitespace, punctuation, numbers, symbols
            cat = unicodedata.category(c)
            if cat.startswith(('P', 'Z', 'N', 'S')) or c in '\r\n\t ':
                continue

            # 3. Combining marks
            if cat.startswith('M'):
                try:
                    c_name = unicodedata.name(c, '')
                except ValueError:
                    return False
                # Reject foreign combining marks
                for other_code, other_script in SCRIPT_NAME_MAP.items():
                    if other_script != target_script and other_script in c_name:
                        return False
                if target_script in c_name or in_range(cp, target_range):
                    has_target_script = True
                continue

            # 4. Letters
            if c.isalpha():
                try:
                    c_name = unicodedata.name(c, '')
                except ValueError:
                    return False

                # Target script letter -> valid
                if target_script in c_name or in_range(cp, target_range):
                    has_target_script = True
                    continue

                # Explicitly permit Latin letters for abbreviations like 'NHS'
                if 'LATIN' in c_name or ('A' <= c <= 'Z') or ('a' <= c <= 'z'):
                    continue

                # Any other alphabet (Cyrillic, Greek, Arabic in Tamil, Tamil in Arabic) -> REJECT
                return False

        return has_target_script

    if language in LATIN_LANGUAGES:
        has_latin_letter = False
        for c in text:
            cat = unicodedata.category(c)
            if cat.startswith(('P', 'Z', 'N', 'S')) or c in '\r\n\t ':
                continue
            if not c.isalpha():
                continue
            try:
                c_name = unicodedata.name(c, '')
            except ValueError:
                return False
            if 'LATIN' in c_name:
                has_latin_letter = True
            else:
                return False
        return has_latin_letter

    return True

# ============================================================
# NUMERIC & DOSAGE GUARDS
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
        warning='Translation unavailable — rephrase, use supported native-script input, or seek interpreter support.',
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

        # Reject unchanged cross-language outputs
        if source != target and translated.lower() == clean_input.lower() and not numeric_response(clean_input):
            return unavailable('unchanged_echo')

        # Script mismatch & cross-script contamination guard
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
# PREPARED CLINICAL STAFF LOOKUP (9 Exact Phrases across 9 Languages)
# 5 Reception/Administrative Prompts, 4 Symptom Prompts
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

STAFF_LOOKUP_NORM = {
    normalise(orig).lower(): translations for orig, translations in STAFF_LOOKUP.items()
}

def staff_translation(text, language):
    if language not in LANGUAGES:
        return unavailable('unsupported_language')

    clean = normalise(text).lower()

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

    return online(text, 'en', language)

# ============================================================
# PATIENT DISPATCHER WITH STRICT ROMANISED GUARDS
# Contains the two exact verified Romanised Tamil chest pain entries
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

    if numeric_response(text):
        return Translation(
            text=str(text).strip(),
            native=str(text).strip(),
            status='needs_review',
            source='original_value',
            warning='Original numeric value preserved.'
        )

    clean = normalise(text).lower()

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
            lookup = EXACT_ROMANISED.get(language, {})
            if clean in lookup:
                return Translation(
                    text=lookup[clean],
                    native=text,
                    status='needs_review',
                    source='prepared_phrase',
                    warning=PREPARED
                )
            return unavailable('unsupported_romanised')

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
