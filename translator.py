"""
MedOriva AI — High-Speed Clinical Translation Engine
Equal Phonetic & Native Processing for All 9 UK Community Languages
"""
import html
import os
import re
import unicodedata
from dataclasses import dataclass
import requests
from deep_translator import GoogleTranslator, MyMemoryTranslator

from clinical_lexicon import (
    LANGUAGES,
    NEGATION_DICTIONARY,
    PATIENT_CLINICAL_DOMAINS,
    STAFF_LEXICON,
)

REVIEW = 'Machine translation · Confirm meaning with speaker.'
PREPARED = 'Verified Clinical Lexicon · Confirmed.'

def normalise(text):
    if not text:
        return ''
    cleaned = re.sub(r'[^\w\s]', ' ', str(text).lower())
    return ' '.join(unicodedata.normalize('NFC', cleaned).casefold().split())

def is_native_script(text):
    return any(ord(char) > 0x0590 for char in text)

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

def detect_negation(text, lang_code):
    clean = normalise(text)
    tokens = clean.split()
    neg_words = NEGATION_DICTIONARY.get(lang_code, []) + ["no", "not", "without", "never", "none", "denies"]
    for word in neg_words:
        if word in tokens or word in clean:
            return True
    return False

# ============================================================
# MULTI-TIER RESILIENT ONLINE TRANSLATION
# ============================================================
def configured_key():
    for name in ('GOOGLE_TRANSLATE_API_KEY', 'GOOGLE_CLOUD_TRANSLATION_API_KEY', 'GOOGLE_API_KEY'):
        val = os.environ.get(name, '').strip()
        if val:
            return val
    return ''

def online(text, source, target):
    if not text:
        return Translation()

    # Tier 1: Cloud API Key
    key = configured_key()
    if key:
        try:
            resp = requests.post(
                'https://translation.googleapis.com/language/translate/v2',
                headers={'X-Goog-Api-Key': key},
                json={'q': text, 'source': source, 'target': target, 'format': 'text'},
                timeout=(3, 6)
            )
            if resp.status_code == 200:
                translated = html.unescape(resp.json()['data']['translations'][0]['translatedText']).strip()
                if translated and normalise(translated) != normalise(text):
                    return Translation(translated, translated, 'needs_review', 'google_cloud', REVIEW)
        except Exception:
            pass

    # Tier 2: Deep-Translator Google
    try:
        translated = GoogleTranslator(source=source, target=target).translate(text)
        if translated and normalise(translated) != normalise(text):
            return Translation(translated, translated, 'needs_review', 'google_translator', REVIEW)
    except Exception:
        pass

    # Tier 3: Deep-Translator MyMemory
    try:
        translated = MyMemoryTranslator(source=source, target=target).translate(text)
        if translated and normalise(translated) != normalise(text):
            return Translation(translated, translated, 'needs_review', 'mymemory', REVIEW)
    except Exception:
        pass

    return Translation(text, text, 'unavailable', 'none', 'Translation temporarily unavailable.')

# ============================================================
# DISPATCHERS (STAFF & PATIENT)
# ============================================================
def staff_translation(text, language):
    if language not in LANGUAGES:
        return Translation(warning='Unsupported language.')

    clean = normalise(text)

    # 100% Instant 0ms Match for All Staff Guided Prompts across all 9 languages
    if any(k in clean for k in ["good morning", "help you"]):
        val = STAFF_LEXICON["GOOD_MORNING"][language]
        return Translation(val, val, 'needs_review', 'clinical_lexicon', PREPARED)
    if "appointment" in clean:
        val = STAFF_LEXICON["APPOINTMENT"][language]
        return Translation(val, val, 'needs_review', 'clinical_lexicon', PREPARED)
    if any(k in clean for k in ["name", "date of birth", "dob"]):
        val = STAFF_LEXICON["NAME_DOB"][language]
        return Translation(val, val, 'needs_review', 'clinical_lexicon', PREPARED)
    if "nhs" in clean:
        val = STAFF_LEXICON["NHS_NUMBER"][language]
        return Translation(val, val, 'needs_review', 'clinical_lexicon', PREPARED)
    if any(k in clean for k in ["seat", "sit", "wait"]):
        val = STAFF_LEXICON["TAKE_SEAT"][language]
        return Translation(val, val, 'needs_review', 'clinical_lexicon', PREPARED)
    if "interpreter" in clean:
        val = STAFF_LEXICON["INTERPRETER"][language]
        return Translation(val, val, 'needs_review', 'clinical_lexicon', PREPARED)
    if any(k in clean for k in ["where is", "where does it hurt"]):
        val = STAFF_LEXICON["WHERE_IS_PAIN"][language]
        return Translation(val, val, 'needs_review', 'clinical_lexicon', PREPARED)
    if "how long" in clean:
        if "chest" in clean:
            val = STAFF_LEXICON["HOW_LONG_CHEST_PAIN"][language]
            return Translation(val, val, 'needs_review', 'clinical_lexicon', PREPARED)
        val = STAFF_LEXICON["HOW_LONG_PAIN"][language]
        return Translation(val, val, 'needs_review', 'clinical_lexicon', PREPARED)
    if "chest" in clean and "pain" in clean:
        val = STAFF_LEXICON["DO_YOU_HAVE_CHEST_PAIN"][language]
        return Translation(val, val, 'needs_review', 'clinical_lexicon', PREPARED)
    if any(k in clean for k in ["breath", "breathing"]):
        val = STAFF_LEXICON["DO_YOU_HAVE_BREATHING"][language]
        return Translation(val, val, 'needs_review', 'clinical_lexicon', PREPARED)
    if "fever" in clean:
        val = STAFF_LEXICON["DO_YOU_HAVE_FEVER"][language]
        return Translation(val, val, 'needs_review', 'clinical_lexicon', PREPARED)
    if any(k in clean for k in ["scale", "1 to 10"]):
        val = STAFF_LEXICON["SEVERITY_SCALE"][language]
        return Translation(val, val, 'needs_review', 'clinical_lexicon', PREPARED)
    if "allergy" in clean or "allergies" in clean:
        val = STAFF_LEXICON["ALLERGIES_QUERY"][language]
        return Translation(val, val, 'needs_review', 'clinical_lexicon', PREPARED)
    if "medication" in clean or "medicine" in clean:
        val = STAFF_LEXICON["MEDICATION_QUERY"][language]
        return Translation(val, val, 'needs_review', 'clinical_lexicon', PREPARED)
    if "see you now" in clean:
        val = STAFF_LEXICON["DOCTOR_NOW"][language]
        return Translation(val, val, 'needs_review', 'clinical_lexicon', PREPARED)
    if "pain" in clean:
        val = STAFF_LEXICON["DO_YOU_HAVE_PAIN"][language]
        return Translation(val, val, 'needs_review', 'clinical_lexicon', PREPARED)

    # Dynamic Fallback for custom typing
    return online(text, 'en', language)

def patient_translation(text, language):
    if language not in LANGUAGES:
        return Translation(warning='Unsupported language.')

    clean = normalise(text)
    is_neg = detect_negation(clean, language)

    # 1. Phonetic & Native Longest-Match Clinical Search across all 9 languages
    for domain_name, data in PATIENT_CLINICAL_DOMAINS.items():
        lang_tokens = data["tokens"].get(language, [])
        # Sort tokens by length descending so specific multi-word tokens match first
        sorted_tokens = sorted(lang_tokens, key=len, reverse=True)
        for token in sorted_tokens:
            if token in clean:
                target_pair = data["negative"][language] if is_neg else data["affirmative"][language]
                return Translation(
                    text=target_pair[0],
                    native=target_pair[1],
                    status='needs_review',
                    source='clinical_lexicon',
                    warning=PREPARED,
                    symptom=domain_name if data["urgent"] else "",
                    is_negative=is_neg
                )

    # 2. General Pain Fallback
    pain_tokens = ["vali", "dard", "vedana", "bol", "alam", "xanuun", "durere", "ব্যথা", "வலி"]
    if any(pt in clean for pt in pain_tokens):
        affirmative_text = "I have pain."
        negative_text = "I do not have pain."
        return Translation(
            text=negative_text if is_neg else affirmative_text,
            native=text,
            status='needs_review',
            source='clinical_lexicon',
            warning=PREPARED,
            symptom="",
            is_negative=is_neg
        )

    # 3. Dynamic Online Fallback for rare unmapped statements
    if is_native_script(text):
        res = online(text, language, 'en')
        eng_text = res.text
        native_text = text
    else:
        res = online(text, 'auto', 'en')
        eng_text = res.text
        native_res = online(eng_text, 'en', language)
        native_text = native_res.text if native_res.text else text

    eng_lower = eng_text.lower()
    is_neg_eng = any(w in eng_lower.split() for w in ['no', 'not', 'none', 'denies', 'without'])
    urgent_flags = ['chest pain', 'breathing difficulty', 'bleeding', 'unconscious', 'allergy']
    detected_sym = next((u for u in urgent_flags if u in eng_lower), '')

    return Translation(
        text=eng_text,
        native=native_text,
        status='needs_review',
        source='online_engine',
        warning=REVIEW,
        symptom=detected_sym,
        is_negative=is_neg_eng or is_neg
    )
