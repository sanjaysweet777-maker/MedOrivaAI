"""Exact phrase lookup and complete-message translation. No symptom reconstruction."""
import html
import os
import re
import unicodedata
from dataclasses import dataclass
import requests
from clinical_phrases import CLINICAL_STAFF_SYNTHESIZER

LANGUAGES = {'ta':'Tamil','hi':'Hindi','ml':'Malayalam','pl':'Polish','ar':'Arabic','ur':'Urdu','bn':'Bengali','so':'Somali','ro':'Romanian'}
SCRIPT_RANGES = {'ta':(0x0B80,0x0BFF),'hi':(0x0900,0x097F),'ml':(0x0D00,0x0D7F),'bn':(0x0980,0x09FF),'ar':(0x0600,0x06FF),'ur':(0x0600,0x06FF)}
REVIEW = 'Machine translation · Confirm meaning with the speaker.'
PREPARED = 'Prepared phrase · Confirm meaning with the speaker.'

def normalise(text):
    # Preserve vowel signs, combining marks, punctuation and numeric separators.
    return ' '.join(unicodedata.normalize('NFC', text).casefold().split())

EXACT_STAFF = {
    'Where is your pain?':'WHERE_IS_PAIN',
    'How long have you had this?':'HOW_LONG_GENERAL',
    'How long have you had pain?':'HOW_LONG_PAIN',
    'How long have you had chest pain?':'HOW_LONG_CHEST_PAIN',
    'Do you have a fever?':'DO_YOU_HAVE_FEVER',
    'Are you having difficulty breathing?':'DO_YOU_HAVE_BREATHING',
    'Do you have chest pain?':'DO_YOU_HAVE_CHEST_PAIN',
    'Do you have pain?':'DO_YOU_HAVE_PAIN',
}
STAFF_LOOKUP = {normalise(k): CLINICAL_STAFF_SYNTHESIZER[v] for k,v in EXACT_STAFF.items()}
# Finite prepared administrative phrases; these are not a certified phrase bank.
ADMIN_PHRASES = {
 'Do you have an appointment?': ['உங்களுக்கு முன்பதிவு செய்யப்பட்ட சந்திப்பு உள்ளதா?', 'क्या आपकी अपॉइंटमेंट है?', 'നിങ്ങൾക്ക് അപ്പോയിന്റ്മെന്റ് ഉണ്ടോ?', 'Czy ma Pan/Pani umówioną wizytę?', 'هل لديك موعد؟', 'کیا آپ کی اپائنٹمنٹ ہے؟', 'আপনার কি অ্যাপয়েন্টমেন্ট আছে?', 'Ballan ma leedahay?', 'Aveți o programare?'],
 'Do you need any assistance?': ['உங்களுக்கு ஏதேனும் உதவி தேவையா?', 'क्या आपको किसी सहायता की आवश्यकता है?', 'നിങ്ങൾക്ക് എന്തെങ്കിലും സഹായം വേണോ?', 'Czy potrzebuje Pan/Pani pomocy?', 'هل تحتاج إلى أي مساعدة؟', 'کیا آپ کو کسی مدد کی ضرورت ہے؟', 'আপনার কি কোনো সাহায্য দরকার?', 'Ma u baahan tahay wax caawimo ah?', 'Aveți nevoie de ajutor?'],
 'Do you need an interpreter?': ['உங்களுக்கு மொழிபெயர்ப்பாளர் தேவையா?', 'क्या आपको दुभाषिए की आवश्यकता है?', 'നിങ്ങൾക്ക് ഒരു ദ്വിഭാഷിയുടെ സഹായം ആവശ്യമുണ്ടോ?', 'Czy potrzebuje Pan/Pani tłumacza ustnego?', 'هل تحتاج إلى مترجم شفهي؟', 'کیا آپ کو ترجمان کی ضرورت ہے؟', 'আপনার কি দোভাষী দরকার?', 'Ma u baahan tahay turjubaan?', 'Aveți nevoie de un interpret?'],
 'The doctor will see you now.': ['மருத்துவர் இப்போது உங்களைச் சந்திப்பார்.', 'डॉक्टर अब आपसे मिलेंगे।', 'ഡോക്ടർ ഇപ്പോൾ നിങ്ങളെ കാണും.', 'Lekarz przyjmie teraz Pana/Panią.', 'سيقابلك الطبيب الآن.', 'ڈاکٹر اب آپ سے ملیں گے۔', 'ডাক্তার এখন আপনাকে দেখবেন।', 'Dhakhtarka ayaa hadda ku arki doona.', 'Medicul vă va primi acum.'],
}
ADMIN_LANGUAGE_ORDER = ('ta','hi','ml','pl','ar','ur','bn','so','ro')
for english, translations in ADMIN_PHRASES.items():
    STAFF_LOOKUP[normalise(english)] = dict(zip(ADMIN_LANGUAGE_ORDER, translations))

# Deliberately finite whole utterances. Never apply these to a substring.
TAMIL_ROMANISED = {
    'enaku nenji vali irukku': ('I have chest pain.', 'எனக்கு நெஞ்சு வலி இருக்கிறது.'),
    'enakku nenju vali irukku': ('I have chest pain.', 'எனக்கு நெஞ்சு வலி இருக்கிறது.'),
    'enaku nenji vali illa': ('I do not have chest pain.', 'எனக்கு நெஞ்சு வலி இல்லை.'),
    'enakku nenju vali illai': ('I do not have chest pain.', 'எனக்கு நெஞ்சு வலி இல்லை.'),
}

@dataclass(frozen=True)
class Translation:
    text: str = ''
    native: str = ''
    status: str = 'unavailable'
    source: str = 'none'
    warning: str = 'Translation is temporarily unavailable. Please try again.'
    error_code: str = ''


def script_matches(text, language):
    if language not in SCRIPT_RANGES:
        return any('LATIN' in unicodedata.name(c, '') for c in text)
    low, high = SCRIPT_RANGES[language]
    return any(low <= ord(c) <= high and unicodedata.category(c).startswith('L') for c in text)


def numeric_tokens(text):
    # Preserve numeric values conservatively; reject changed decimal separators too.
    text = ''.join(str(unicodedata.digit(c)) if c.isdigit() else c for c in text)
    return sorted(re.findall(r'\d+(?:[.,:/]\d+)*', text))


def configured_key():
    # Accept common deployment names; never expose the value in a response or log.
    for name in ('GOOGLE_TRANSLATE_API_KEY', 'GOOGLE_CLOUD_TRANSLATION_API_KEY', 'GOOGLE_API_KEY'):
        value = os.environ.get(name, '').strip()
        if value:
            return value
    return ''

ERROR_MESSAGES = {
    'not_configured': 'Translation service setup is pending. Prepared phrases are available.',
    'invalid_key': 'The translation service could not authenticate. Ask the administrator to check the API key.',
    'api_disabled': 'The translation API needs to be enabled in the connected Google Cloud project.',
    'billing': 'The translation service needs an active Google Cloud billing account.',
    'access_denied': 'The translation service could not authorise this request. Ask the administrator to check API permissions and key restrictions.',
    'quota': 'The translation service has reached its current usage limit. Please try again later.',
    'timeout': 'The translation service took too long to respond. Please try again.',
    'connection': 'The translation service could not be reached. Please try again.',
    'provider_error': 'The translation service is temporarily unavailable. Please try again.',
    'invalid_response': 'A complete translation was not returned. Please try again.',
    'unchanged': 'Please check the selected language and rephrase this message.',
    'script_mismatch': 'Please check the selected language and try this message again.',
    'numbers_changed': 'Please confirm the numbers and rephrase this message before continuing.',
    'input_script': 'Enter the response in the selected language’s usual writing system. Selected Thanglish phrases are also available for Tamil.',
}


def unavailable(code):
    return Translation(warning=ERROR_MESSAGES[code], error_code=code)


def provider_error(response):
    # Read only reason codes, never return raw provider errors (which may contain
    # input, project identifiers or credentials). Keep logs free of request text.
    try:
        error = response.json().get('error', {})
        reasons = {detail.get('reason', '') for detail in error.get('details', []) if isinstance(detail, dict)}
        reasons.update(detail.get('reason', '') for detail in error.get('errors', []) if isinstance(detail, dict))
    except (ValueError, AttributeError, TypeError):
        reasons = set()
    if reasons & {'API_KEY_INVALID', 'API_KEY_EXPIRED'} or response.status_code == 401:
        return unavailable('invalid_key')
    if reasons & {'SERVICE_DISABLED', 'accessNotConfigured'}:
        return unavailable('api_disabled')
    if reasons & {'BILLING_DISABLED', 'PROJECT_BILLING_INFO_NOT_FOUND'}:
        return unavailable('billing')
    if reasons & {'RATE_LIMIT_EXCEEDED', 'QUOTA_EXCEEDED', 'dailyLimitExceeded', 'userRateLimitExceeded'} or response.status_code == 429:
        return unavailable('quota')
    return unavailable('access_denied' if response.status_code == 403 else 'provider_error')


def online(text, source, target):
    key = configured_key()
    if not key:
        return unavailable('not_configured')
    try:
        response = requests.post('https://translation.googleapis.com/language/translate/v2',
            headers={'X-Goog-Api-Key':key},
            json={'q':text,'source':source,'target':target,'format':'text'}, timeout=(3,12))
        response.raise_for_status()
        translated = html.unescape(response.json()['data']['translations'][0]['translatedText']).strip()
        if not translated:
            return unavailable('invalid_response')
        if normalise(translated) == normalise(text):
            return unavailable('unchanged')
        if not script_matches(translated, target):
            return unavailable('script_mismatch')
        if numeric_tokens(text) != numeric_tokens(translated):
            return unavailable('numbers_changed')
        return Translation(translated, status='needs_review',source='google_cloud',warning=REVIEW)
    except requests.HTTPError as exc:
        return provider_error(exc.response) if exc.response is not None else unavailable('provider_error')
    except requests.Timeout:
        return unavailable('timeout')
    except requests.RequestException:
        return unavailable('connection')
    except (ValueError, KeyError, IndexError, TypeError, AttributeError):
        return unavailable('invalid_response')


def numeric_response(text):
    # An answer consisting only of digits and separators needs no language model.
    # Preserve its exact spelling: do not interpret ambiguous dates or times.
    return bool(re.fullmatch(r"[0-9٠-٩۰-۹०-९০-৯௦-௯൦-൯]+(?:[ .,:/–—-][0-9٠-٩۰-۹०-९০-৯௦-௯൦-൯]+)*", text))


def staff_translation(text, language):
    if language not in LANGUAGES:
        return Translation(warning='Unsupported language.')
    phrase = STAFF_LOOKUP.get(normalise(text), {}).get(language)
    if phrase:
        return Translation(phrase, status='needs_review',source='prepared_phrase',warning=PREPARED)
    return online(text,'en',language)


def patient_translation(text, language):
    if language not in LANGUAGES:
        return Translation(warning='Unsupported language.')
    if numeric_response(text):
        return Translation(text,text,'needs_review','original_value','Number or time · Confirm its meaning with the speaker.')
    if language == 'ta' and normalise(text).rstrip('.!?') in TAMIL_ROMANISED:
        english, native = TAMIL_ROMANISED[normalise(text).rstrip('.!?')]
        return Translation(english,native,'needs_review','prepared_phrase',PREPARED)
    if not script_matches(text,language):
        return unavailable('input_script')
    result = online(text,language,'en')
    return Translation(result.text,text,result.status,result.source,result.warning,result.error_code)
