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
from deep_translator import GoogleTranslator, MyMemoryTranslator

from clinical_lexicon import (
    LANGUAGES,
    NEGATION_DICTIONARY,
    PATIENT_CLINICAL_DOMAINS,
    STAFF_LEXICON,
)

logger = logging.getLogger("medoriva.translator")

REVIEW = 'Machine translation · Confirm meaning with speaker.'
PREPARED = 'Verified Clinical Lexicon · Confirmed.'

def normalise(text):
    if not text:
        return ''
    cleaned = re.sub(r'[^\w\s]', ' ', str(text).lower())
    return ' '.join(unicodedata.normalize('NFC', cleaned).casefold().split())

def is_native_script(text):
    # Detects non-Latin scripts (Arabic, Tamil, Devanagari, Bengali, etc.)
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

# ============================================================
# MULTILINGUAL NEGATION PARSING (All 9 MVP Languages)
# ============================================================
SUPPLEMENTAL_NEGATIONS = {
    "ta": ["illai", "illa", "kidayathu", "illamal", "vendam", "thevai illai", "இல்லை", "கிடையாது", "வேண்டாம்"],
    "hi": ["nahi", "nahin", "na", "mat", "नहीं", "ना", "मत"],
    "ml": ["illa", "alla", "venda", "aavashyamilla", "ഇല്ല", "അല്ല", "വേണ്ട"],
    "pl": ["nie", "brak", "bez", "ani"],
    "ar": ["la", "kalla", "laysa", "ma", "mush", "lan", "lam", "لا", "كلا", "ليس", "ما", "مش"],
    "ur": ["nahi", "nahin", "na", "mat", "nhi", "نہیں", "نہ", "مت"],
    "bn": ["na", "nei", "noi", "noy", "না", "নেই", "নয়"],
    "so": ["maya", "ma", "malihi", "ha", "ma jiro"],
    "ro": ["nu", "nici", "fara", "fără"],
    "pa": ["nahi", "nhi", "na", "nahin", "ਨਹੀਂ", "ਨਾ"],
    "gu": ["nathi", "na", "નથી", "ના"]
}

def detect_negation(text, lang_code):
    """
    Strict whole-token negation parsing across all 9 community languages.
    Ensures substrings (e.g. Polish 'mnie') never falsely trigger negation ('nie').
    """
    clean = normalise(text)
    tokens = set(clean.split())
    
    lexicon_negs = NEGATION_DICTIONARY.get(lang_code, [])
    supp_negs = SUPPLEMENTAL_NEGATIONS.get(lang_code, [])
    universal_negs = ["no", "not", "without", "never", "none", "denies"]

    all_neg_words = set(lexicon_negs + supp_negs + universal_negs)
    padded = f" {clean} "

    for word in all_neg_words:
        clean_word = normalise(word)
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
# MULTI-TIER ONLINE TRANSLATION ENGINE
# ============================================================
def configured_key():
    for name in ('GOOGLE_TRANSLATE_API_KEY', 'GOOGLE_CLOUD_TRANSLATION_API_KEY', 'GOOGLE_API_KEY'):
        val = os.environ.get(name, '').strip()
        if val:
            return val
    return ''

def is_error_payload(text):
    """Rejects rate-limit HTML error pages."""
    if not text:
        return True
    lowered = text.lower()
    error_markers = [
        "error 500", "server error", "that’s an error", "that's an error",
        "wystąpił błąd", "błąd 500", "błąd serwera", "try again later"
    ]
    return any(marker in lowered for marker in error_markers)

def online(text, source, target):
    if not text:
        return Translation()

    clean_input = text.strip()
    if source == target:
        return Translation(clean_input, clean_input, 'needs_review', 'pass_through', REVIEW)

    # Tier 1: Google Cloud Translation API (Official Endpoint)
    key = configured_key()
    if key:
        try:
            resp = requests.post(
                'https://translation.googleapis.com/language/translate/v2',
                headers={'X-Goog-Api-Key': key},
                json={'q': clean_input, 'source': source, 'target': target, 'format': 'text'},
                timeout=(2, 4)
            )
            if resp.status_code == 200:
                translated = html.unescape(resp.json()['data']['translations'][0]['translatedText']).strip()
                if translated and not is_error_payload(translated):
                    return Translation(translated, translated, 'needs_review', 'google_cloud', REVIEW)
        except Exception as e:
            logger.debug("Tier 1 Cloud API unavailable: %s", e)

    # Tier 2: Resilient Provider Fallback (Google)
    try:
        translated = GoogleTranslator(source=source, target=target).translate(clean_input)
        if translated and not is_error_payload(translated) and normalise(translated) != normalise(clean_input):
            return Translation(translated, translated, 'needs_review', 'google_translator', REVIEW)
    except Exception as e:
        logger.debug("Tier 2 provider unavailable: %s", e)

    # Tier 3: Resilient Provider Fallback (MyMemory)
    try:
        translated = MyMemoryTranslator(source=source, target=target).translate(clean_input)
        if translated and not is_error_payload(translated) and normalise(translated) != normalise(clean_input):
            return Translation(translated, translated, 'needs_review', 'mymemory', REVIEW)
    except Exception as e:
        logger.debug("Tier 3 provider unavailable: %s", e)

    # All automated translation providers failed: Return transparent status
    return Translation(
        text=f"[Untranslated] {clean_input}",
        native=clean_input,
        status='untranslated',
        source='fallback_failed',
        warning='Automated translation failed. Human interpreter required.'
    )

# ============================================================
# EXACT STAFF PROMPT LOOKUP REGISTRY
# ============================================================
# Standardized prompts mapped to verified lexicon keys.
# Free-text variations ("Your appointment is confirmed/cancelled")
# do NOT match these and fall through directly to full dynamic translation.
EXACT_STAFF_PROMPTS = {
    # Reception & Arrival
    "good morning how can i help you": "GOOD_MORNING",
    "good morning": "GOOD_MORNING",
    "how can i help you": "GOOD_MORNING",
    "do you have an appointment": "APPOINTMENT",
    "can i take your name and date of birth": "NAME_DOB",
    "name and date of birth": "NAME_DOB",
    "please take a seat the doctor will see you shortly": "TAKE_SEAT",
    "please take a seat": "TAKE_SEAT",
    "take a seat": "TAKE_SEAT",
    "do you have your nhs number": "NHS_NUMBER",
    "do you need an interpreter": "INTERPRETER",
    "do you require an interpreter": "INTERPRETER",

    # Appointment & Admin
    "the doctor will see you now": "DOCTOR_NOW",
    "doctor will see you now": "DOCTOR_NOW",
    "please bring your medication list": "MEDICATION_QUERY",
    "do you have your medication list": "MEDICATION_QUERY",
    "please wait in the waiting area": "TAKE_SEAT",

    # Basic Symptoms & Routine Questions
    "where is your pain": "WHERE_IS_PAIN",
    "where does it hurt": "WHERE_IS_PAIN",
    "how long have you had this": "HOW_LONG_PAIN",
    "how long have you had pain": "HOW_LONG_PAIN",
    "how long have you had chest pain": "HOW_LONG_CHEST_PAIN",
    "do you have a fever": "DO_YOU_HAVE_FEVER",
    "are you having difficulty breathing": "DO_YOU_HAVE_BREATHING",
    "do you have chest pain": "DO_YOU_HAVE_CHEST_PAIN",
    "are you in pain": "DO_YOU_HAVE_PAIN",
    "do you have pain": "DO_YOU_HAVE_PAIN",
    "do you have any allergies": "ALLERGIES_QUERY",
    "on a scale of 1 to 10": "SEVERITY_SCALE"
}

def staff_translation(text, language):
    if language not in LANGUAGES:
        return Translation(warning='Unsupported language.')

    clean = normalise(text)

    # 1. Exact prepared prompt match (0ms latency, verified lexicon)
    lexicon_key = EXACT_STAFF_PROMPTS.get(clean)
    if lexicon_key and lexicon_key in STAFF_LEXICON:
        val = STAFF_LEXICON[lexicon_key].get(language)
        if val:
            return Translation(val, val, 'needs_review', 'clinical_lexicon', PREPARED)

    # 2. Dynamic online translation for all custom or non-standard staff messages
    # Prevents "Your appointment is confirmed/cancelled" from collapsing into the appointment question.
    return online(text, 'en', language)

# ============================================================
# PATIENT DISPATCHER
# ============================================================
def patient_translation(text, language):
    if language not in LANGUAGES:
        return Translation(warning='Unsupported language.')

    clean = normalise(text)
    is_neg = detect_negation(text, language)

    # 1. Canned Clinical Domain Check:
    # ONLY triggers if the input matches the symptom phrase alone.
    # If the patient provided extra words (chest, left arm, 3 days),
    # canned substitution is skipped to prevent erasing clinical detail.
    clean_tokens = set(clean.split())
    for domain_name, data in PATIENT_CLINICAL_DOMAINS.items():
        lang_tokens = data["tokens"].get(language, [])
        for token in lang_tokens:
            norm_token = normalise(token)
            token_tokens = set(norm_token.split())
            
            # Exact match or token covers the vast majority of input
            if clean == norm_token or (clean_tokens == token_tokens):
                target_pair = data["negative"][language] if is_neg else data["affirmative"][language]
                return Translation(
                    text=target_pair[0],
                    native=target_pair[1],
                    status='needs_review',
                    source='clinical_lexicon',
                    warning=PREPARED,
                    symptom=domain_name if data.get("urgent", False) else "",
                    is_negative=is_neg
                )

    # 2. Isolated Single-Word Pain Check:
    # ONLY triggers if the patient ONLY said "pain" or "no pain".
    # Complex sentences ("nenji vali 3 naala", "boli od wczoraj") fall through to dynamic translation.
    pain_tokens = {
        "vali", "dard", "vedana", "vedhana", "bol", "boli", "klucie", "kłucie", "pieczenie",
        "alam", "xanuun", "durere", "ব্যথা", "வலி", "درد"
    }
    if clean in pain_tokens or clean_tokens == pain_tokens & clean_tokens:
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

    # 3. Dynamic Online Translation for Multi-word / Descriptive Responses
    src_lang = language if language != 'en' else 'auto'
    res = online(text, src_lang, 'en')
    eng_text = res.text

    if is_error_payload(eng_text):
        eng_text = text

    eng_lower = eng_text.lower()
    is_neg_eng = any(w in eng_lower.split() for w in ['no', 'not', 'none', 'denies', 'without'])
    urgent_flags = ['chest pain', 'breathing difficulty', 'bleeding', 'unconscious']
    detected_sym = next((u for u in urgent_flags if u in eng_lower), '')

    return Translation(
        text=eng_text,
        native=text,
        status=res.status,
        source=res.source,
        warning=res.warning,
        symptom=detected_sym,
        is_negative=is_neg_eng or is_neg
    )
