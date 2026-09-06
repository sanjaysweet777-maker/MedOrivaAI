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
REVIEW = 'Machine translation — not independently reviewed. Confirm the complete meaning with the speaker; use a qualified interpreter if uncertain.'
PREPARED = 'Prepared demo phrase — independent bilingual review is still required.'

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
    warning: str = 'Translation unavailable. Rephrase or use a qualified interpreter.'


def script_matches(text, language):
    if language not in SCRIPT_RANGES:
        return any('LATIN' in unicodedata.name(c, '') for c in text)
    low, high = SCRIPT_RANGES[language]
    return any(low <= ord(c) <= high and unicodedata.category(c).startswith('L') for c in text)


def numeric_tokens(text):
    # Preserve numeric values conservatively; reject changed decimal separators too.
    text = ''.join(str(unicodedata.digit(c)) if c.isdigit() else c for c in text)
    return sorted(re.findall(r'\d+(?:[.,:/]\d+)*', text))


def online(text, source, target):
    key = os.environ.get('GOOGLE_TRANSLATE_API_KEY')
    if not key:
        return Translation(warning='Full-text translation is not configured. Use a prepared demo phrase or ask the administrator to configure the translation service.')
    try:
        response = requests.post('https://translation.googleapis.com/language/translate/v2',
            headers={'X-Goog-Api-Key':key},
            json={'q':text,'source':source,'target':target,'format':'text'}, timeout=(3,12))
        response.raise_for_status()
        translated = html.unescape(response.json()['data']['translations'][0]['translatedText']).strip()
        if not translated or normalise(translated) == normalise(text):
            return Translation(warning='The service did not return a distinct translation. Confirm the input language or use an interpreter.')
        if not script_matches(translated, target):
            return Translation(warning='The output writing system did not match the selected language. Translation withheld.')
        if numeric_tokens(text) != numeric_tokens(translated):
            return Translation(warning='Numbers changed during translation. Translation withheld; confirm the numbers with an interpreter.')
        return Translation(translated, status='needs_review',source='google_cloud',warning=REVIEW)
    except (requests.RequestException, ValueError, KeyError, IndexError, TypeError, AttributeError):
        # Do not log provider bodies or input, or send to an undisclosed fallback.
        return Translation()


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
    if language == 'ta' and normalise(text).rstrip('.!?') in TAMIL_ROMANISED:
        english, native = TAMIL_ROMANISED[normalise(text).rstrip('.!?')]
        return Translation(english,native,'needs_review','prepared_phrase',PREPARED)
    if not script_matches(text,language):
        return Translation(warning='Please enter the selected language in its normal written form. Romanised Tamil is limited to the prepared demo phrases.')
    result = online(text,language,'en')
    return Translation(result.text,text,result.status,result.source,result.warning)
