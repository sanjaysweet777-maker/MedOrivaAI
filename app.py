import json
import logging
import os
import re
import secrets
import unicodedata
import uuid
from urllib.parse import urlparse
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from flask_login import LoginManager, UserMixin, current_user, login_required, login_user, logout_user

from translation_engine import (
    LANGUAGES,
    Translation,
    configured_key,
    online,
    patient_translation,
    staff_translation,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(BASE_DIR, 'templates')

app = Flask(__name__, template_folder=template_dir)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("medoriva.app")

env_secret = os.environ.get("SECRET_KEY")
if not env_secret:
    logger.warning("SECRET_KEY unset in environment. Generating dynamic cryptographic secret.")
    app.secret_key = secrets.token_hex(32)
else:
    app.secret_key = env_secret

cookie_secure = os.environ.get("COOKIE_SECURE", "false").lower() in ("true", "1", "yes")
app.config["SESSION_COOKIE_SECURE"] = cookie_secure
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

# ============================================================
# CANONICAL LANGUAGE MAPPING (All 9 Approved MVP Languages)
# ============================================================
CANONICAL_LANGUAGES = {
    "ta": ("Tamil", "ta"), "tamil": ("Tamil", "ta"),
    "hi": ("Hindi", "hi"), "hindi": ("Hindi", "hi"),
    "ml": ("Malayalam", "ml"), "malayalam": ("Malayalam", "ml"),
    "pl": ("Polish", "pl"), "polish": ("Polish", "pl"),
    "ar": ("Arabic", "ar"), "arabic": ("Arabic", "ar"),
    "ur": ("Urdu", "ur"), "urdu": ("Urdu", "ur"),
    "bn": ("Bengali", "bn"), "bengali": ("Bengali", "bn"),
    "so": ("Somali", "so"), "somali": ("Somali", "so"),
    "ro": ("Romanian", "ro"), "romanian": ("Romanian", "ro"),
}

def get_canonical(raw_lang, raw_code=None):
    if raw_code and str(raw_code).strip().lower() in CANONICAL_LANGUAGES:
        return CANONICAL_LANGUAGES[str(raw_code).strip().lower()]
    if raw_lang:
        token = re.split(r'[\s\(\-_/]', str(raw_lang).strip())[0].lower()
        if token in CANONICAL_LANGUAGES:
            return CANONICAL_LANGUAGES[token]
        return (str(raw_lang).strip(), str(raw_code or raw_lang).strip())
    return ("Tamil", "ta")

def normalize_phrase(text):
    if not text:
        return ""
    chars = [c for c in unicodedata.normalize('NFC', str(text)) if not unicodedata.category(c).startswith('P')]
    return " ".join("".join(chars).lower().split())

# ============================================================
# CONTEXT-GUIDED PROMPTS
# Exactly aligned to the 9 prepared staff phrases in STAFF_LOOKUP
# ============================================================
CONTEXT_PROMPTS = {
    "Reception": [
        "Do you have an appointment?",
        "Do you have your appointment letter?",
        "Do you have your NHS number?",
        "Do you need an interpreter?",
        "Please take a seat."
    ],
    "Appointment": [
        "Do you have an appointment?",
        "Do you have your appointment letter?",
        "Do you have your NHS number?",
        "Do you need an interpreter?",
        "Please take a seat."
    ],
    "Basic Symptoms": [
        "Where is your pain?",
        "Do you have chest pain?",
        "Do you have a fever?",
        "Are you having difficulty breathing?"
    ]
}

# ============================================================
# MULTILINGUAL NEGATION TOKENS (All 9 Languages)
# ============================================================
NEGATION_TOKENS_BY_LANG = {
    "ta": {"illai", "illa", "kidayathu", "illamal", "vendam", "thevai illai", "இல்லை", "கிடையாது", "வேண்டாம்", "தெரியாது", "theriyathu", "therila"},
    "hi": {"nahi", "nahin", "na", "mat", "नहीं", "ना", "मत", "pata nahi", "पता नहीं"},
    "ml": {"illa", "alla", "illaathe", "venda", "aavashyamilla", "ഇല്ല", "അല്ല", "വേണ്ട", "അറിയില്ല", "ariyilla"},
    "pl": {"nie", "brak", "bez", "ani", "nie znam", "nie pamietam"},
    "ar": {"la", "kalla", "laysa", "ma", "mush", "lan", "lam", "لا", "كلا", "ليس", "ما", "مش", "لا أعرف"},
    "ur": {"nahi", "nahin", "na", "mat", "nhi", "نہیں", "نہ", "مت", "معلوم نہیں", "maloom nahi"},
    "bn": {"na", "nei", "noi", "noy", "না", "নেই", "নয়", "জানা নেই", "jani na"},
    "so": {"maya", "ma", "maha", "malihi", "ha", "ma jiro", "ma garanayo", "ma aqaan"},
    "ro": {"nu", "nici", "fara", "fără", "nu stiu"}
}

POLARITY_MAP = {
    "APPOINTMENT_SPECIFIC_NO": "negative",
    "NHS_UNKNOWN": "negative",
    "INTERPRETER_SPECIFIC_NO": "negative",
    "COMPANION_NO": "negative",
    "SYMPTOM_NO_PAIN": "negative",
    "NOT_NEEDED": "negative",
    "GENERIC_NO": "negative",
    "NEGATE_NO": "negative",

    "APPOINTMENT_YES_HAVE": "affirmative",
    "APPOINTMENT_HAVE": "affirmative",
    "DOCUMENT_HAVE": "affirmative",
    "NHS_OR_ID_PROVIDED": "affirmative",
    "INTERPRETER_SPECIFIC_YES": "affirmative",
    "COMPANION_YES": "affirmative",
    "SYMPTOM_PAIN_GENERAL": "affirmative",
    "SYMPTOM_FEVER": "affirmative",
    "AFFIRM_HAVE_GENERAL": "affirmative",
    "HAVE_GENERAL": "affirmative",
    "NEEDED": "affirmative",
    "GENERIC_YES": "affirmative",
    "AFFIRM_YES": "affirmative",

    "PRESCRIPTION_NEED": "neutral",
    "TOILET_WHERE": "neutral",
    "UNDERSTOOD_WAIT": "neutral",
    "GENERAL_ACKNOWLEDGE": "neutral"
}

SYMPTOM_KEYWORDS_EN = {
    "pain", "ache", "chest", "fever", "temperature", "breath", "breathing",
    "cough", "headache", "vomit", "vomiting", "nausea", "dizzy", "dizziness",
    "bleed", "bleeding", "swelling", "hurt", "pressure", "heart", "stomach",
    "rash", "throat", "back", "unwell", "sick", "tired", "weak", "exhausted",
    "fatigue", "diarrhea"
}

# ============================================================
# COMPREHENSIVE MULTILINGUAL SYMPTOMS LOOKUP (All 9 Languages)
# Equal coverage of all 12 core symptom & unwell categories
# ============================================================
RAW_SYMPTOMS_LOOKUP = {
    # ── 1. TAMIL (ta) ─────────────────────────────────────────
    "ta": {
        "enaku udambu mudiyala": ("I am not feeling well.", "எனக்கு உடம்பு முடியவில்லை.", "negative"),
        "enakku udambu mudiyala": ("I am not feeling well.", "எனக்கு உடம்பு முடியவில்லை.", "negative"),
        "udambu mudiyala": ("I am not feeling well.", "உடம்பு முடியவில்லை.", "negative"),
        "enaku udambu seri illa": ("I am not feeling well.", "எனக்கு உடம்பு சரியில்லை.", "negative"),
        "enaku udambu seri illai": ("I am not feeling well.", "எனக்கு உடம்பு சரியில்லை.", "negative"),
        "எனக்கு உடம்பு சரியில்லை": ("I am not feeling well.", "எனக்கு உடம்பு சரியில்லை.", "negative"),

        "enaku nenji vali irukku": ("I have chest pain.", "எனக்கு நெஞ்சு வலி இருக்கிறது.", "affirmative"),
        "enaku nenju vali irukku": ("I have chest pain.", "எனக்கு நெஞ்சு வலி இருக்கிறது.", "affirmative"),
        "enaku nenji vali illa": ("I do not have chest pain.", "எனக்கு நெஞ்சு வலி இல்லை.", "negative"),
        "enaku nenji vali illai": ("I do not have chest pain.", "எனக்கு நெஞ்சு வலி இல்லை.", "negative"),
        "எனக்கு நெஞ்சு வலி இருக்கிறது": ("I have chest pain.", "எனக்கு நெஞ்சு வலி இருக்கிறது.", "affirmative"),
        "எனக்கு நெஞ்சு வலி இல்லை": ("I do not have chest pain.", "எனக்கு நெஞ்சு வலி இல்லை.", "negative"),

        "enaku thalai vali irukku": ("I have a headache.", "எனக்கு தலைவலி இருக்கிறது.", "affirmative"),
        "enaku thala vali irukku": ("I have a headache.", "எனக்கு தலைவலி இருக்கிறது.", "affirmative"),
        "enaku thalai vali illa": ("I do not have a headache.", "எனக்கு தலைவலி இல்லை.", "negative"),
        "enaku thalai vali illai": ("I do not have a headache.", "எனக்கு தலைவலி இல்லை.", "negative"),
        "எனக்கு தலைவலி இருக்கிறது": ("I have a headache.", "எனக்கு தலைவலி இருக்கிறது.", "affirmative"),
        "எனக்கு தலைவலி இல்லை": ("I do not have a headache.", "எனக்கு தலைவலி இல்லை.", "negative"),

        "enaku kaichal irukku": ("I have a fever.", "எனக்கு காய்ச்சல் இருக்கிறது.", "affirmative"),
        "enaku kaichal illa": ("I do not have a fever.", "எனக்கு காய்ச்சல் இல்லை.", "negative"),
        "enaku kaichal illai": ("I do not have a fever.", "எனக்கு காய்ச்சல் இல்லை.", "negative"),
        "எனக்கு காய்ச்சல் இருக்கிறது": ("I have a fever.", "எனக்கு காய்ச்சல் இருக்கிறது.", "affirmative"),
        "எனக்கு காய்ச்சல் இல்லை": ("I do not have a fever.", "எனக்கு காய்ச்சல் இல்லை.", "negative"),

        "enaku irumal irukku": ("I have a cough.", "எனக்கு இருமல் இருக்கிறது.", "affirmative"),
        "enaku irumal illa": ("I do not have a cough.", "எனக்கு இருமல் இல்லை.", "negative"),
        "enaku thondai vali irukku": ("I have a sore throat.", "எனக்கு தொண்டை வலி இருக்கிறது.", "affirmative"),
        "enaku thondai vali illa": ("I do not have a sore throat.", "எனக்கு தொண்டை வலி இல்லை.", "negative"),
        "enaku vaandhi varudhu": ("I have vomiting.", "எனக்கு வாந்தி வருகிறது.", "affirmative"),
        "enaku vaandhi illa": ("I do not have vomiting.", "எனக்கு வாந்தி இல்லை.", "negative"),
        "enaku thala suthudhu": ("I feel dizzy.", "எனக்கு தலை சுற்றுகிறது.", "affirmative"),
        "enaku mayakkam irukku": ("I feel faint and dizzy.", "எனக்கு மயக்கம் இருக்கிறது.", "affirmative"),
        "enaku vayiru vali irukku": ("I have stomach pain.", "எனக்கு வயிற்று வலி இருக்கிறது.", "affirmative"),
        "enaku vayiru vali illa": ("I do not have stomach pain.", "எனக்கு வயிற்று வலி இல்லை.", "negative"),
        "enaku muthuku vali irukku": ("I have back pain.", "எனக்கு முதுகு வலி இருக்கிறது.", "affirmative"),
        "enaku moochu thinaral irukku": ("I have difficulty breathing.", "எனக்கு மூச்சுத்திணறல் இருக்கிறது.", "affirmative"),
        "enaku moochu thinaral illa": ("I do not have difficulty breathing.", "எனக்கு மூச்சுத்திணறல் இல்லை.", "negative"),
        "enaku romba asadhiya irukku": ("I feel very weak and tired.", "எனக்கு மிகவும் அசதியாக இருக்கிறது.", "affirmative"),
    },

    # ── 2. HINDI (hi) ─────────────────────────────────────────
    "hi": {
        "meri tabiyat kharab hai": ("I am not feeling well.", "मेरी तबीयत खराब है।", "negative"),
        "tabiyat theek nahi hai": ("I am not feeling well.", "तबीयत ठीक नहीं है।", "negative"),
        "meri tabiyat theek nahi hai": ("I am not feeling well.", "मेरी तबीयत ठीक नहीं है।", "negative"),
        "मेरी तबीयत ठीक नहीं है": ("I am not feeling well.", "मेरी तबीयत ठीक नहीं है।", "negative"),
        "मेरी तबीयत खराब है": ("I am not feeling well.", "मेरी तबीयत खराब है।", "negative"),

        "mujhe seene me dard hai": ("I have chest pain.", "मुझे सीने में दर्द है।", "affirmative"),
        "seene me dard hai": ("I have chest pain.", "सीने में दर्द है।", "affirmative"),
        "mujhe seene me dard nahi hai": ("I do not have chest pain.", "मुझे सीने में दर्द नहीं है।", "negative"),
        "seene me dard nahi hai": ("I do not have chest pain.", "सीने में दर्द नहीं है।", "negative"),
        "मुझे सीने में दर्द है": ("I have chest pain.", "मुझे सीने में दर्द है।", "affirmative"),
        "मुझे सीने में दर्द नहीं है": ("I do not have chest pain.", "मुझे सीने में दर्द नहीं है।", "negative"),

        "mujhe sar dard hai": ("I have a headache.", "मुझे सिरदर्द है।", "affirmative"),
        "sar dard hai": ("I have a headache.", "सिरदर्द है।", "affirmative"),
        "mujhe sar dard nahi hai": ("I do not have a headache.", "मुझे सिरदर्द नहीं है।", "negative"),
        "sar dard nahi hai": ("I do not have a headache.", "सिरदर्द नहीं है।", "negative"),
        "मुझे सिरदर्द है": ("I have a headache.", "मुझे सिरदर्द है।", "affirmative"),
        "मुझे सिरदर्द नहीं है": ("I do not have a headache.", "मुझे सिरदर्द नहीं है।", "negative"),

        "mujhe bukhar hai": ("I have a fever.", "मुझे बुखार है।", "affirmative"),
        "bukhar hai": ("I have a fever.", "बुखार है।", "affirmative"),
        "mujhe bukhar nahi hai": ("I do not have a fever.", "मुझे बुखार नहीं है।", "negative"),
        "bukhar nahi hai": ("I do not have a fever.", "बुखार नहीं है।", "negative"),
        "मुझे बुखार है": ("I have a fever.", "मुझे बुखार है।", "affirmative"),
        "मुझे बुखार नहीं है": ("I do not have a fever.", "मुझे बुखार नहीं है।", "negative"),

        "mujhe khansi hai": ("I have a cough.", "मुझे खांसी है।", "affirmative"),
        "mujhe khansi nahi hai": ("I do not have a cough.", "मुझे खांसी नहीं है।", "negative"),
        "gale me dard hai": ("I have a sore throat.", "गले में दर्द है।", "affirmative"),
        "gale me dard nahi hai": ("I do not have a sore throat.", "गले में दर्द नहीं है।", "negative"),
        "mujhe ulti ho rahi hai": ("I have nausea and vomiting.", "मुझे उल्टी हो रही है।", "affirmative"),
        "mujhe ulti nahi hai": ("I do not have vomiting.", "मुझे उल्टी नहीं है।", "negative"),
        "mujhe chakkar aa rahe hai": ("I feel dizzy.", "मुझे चक्कर आ रहे हैं।", "affirmative"),
        "mujhe chakkar nahi aa rahe": ("I do not feel dizzy.", "मुझे चक्कर नहीं आ रहे हैं।", "negative"),
        "mujhe pet dard hai": ("I have stomach pain.", "मुझे पेट में दर्द है।", "affirmative"),
        "mujhe pet dard nahi hai": ("I do not have stomach pain.", "मुझे पेट में दर्द नहीं है।", "negative"),
        "mujhe kamar dard hai": ("I have back pain.", "मुझे कमर में दर्द है।", "affirmative"),
        "saans lene me takleef hai": ("I have difficulty breathing.", "मुझे सांस लेने में तकलीफ है।", "affirmative"),
        "saans lene me takleef nahi hai": ("I do not have difficulty breathing.", "सांस लेने में कोई तकलीफ नहीं है।", "negative"),
        "mujhe bahut kamzori hai": ("I feel very weak and tired.", "मुझे बहुत कमजोरी महसूस हो रही है।", "affirmative"),
    },

    # ── 3. MALAYALAM (ml) ─────────────────────────────────────
    "ml": {
        "enikku sugamilla": ("I am not feeling well.", "എനിക്ക് സുഖമില്ല.", "negative"),
        "enikku sukhamilla": ("I am not feeling well.", "എനിക്ക് സുഖമില്ല.", "negative"),
        "sugamilla": ("I am not feeling well.", "സുഖമില്ല.", "negative"),
        "എനിക്ക് സുഖമില്ല": ("I am not feeling well.", "എനിക്ക് സുഖമില്ല.", "negative"),

        "enikku nenjuvedhana undu": ("I have chest pain.", "എനിക്ക് നെഞ്ചുവേദനയുണ്ട്.", "affirmative"),
        "nenjuvedhana undu": ("I have chest pain.", "നെഞ്ചുവേദനയുണ്ട്.", "affirmative"),
        "enikku nenjuvedhana illa": ("I do not have chest pain.", "എനിക്ക് നെഞ്ചുവേദനയില്ല.", "negative"),
        "nenjuvedhana illa": ("I do not have chest pain.", "നെഞ്ചുവേദനയില്ല.", "negative"),
        "എനിക്ക് നെഞ്ചുവേദനയുണ്ട്": ("I have chest pain.", "എനിക്ക് നെഞ്ചുവേദനയുണ്ട്.", "affirmative"),
        "എനിക്ക് നെഞ്ചുവേദനയില്ല": ("I do not have chest pain.", "എനിക്ക് നെഞ്ചുവേദനയില്ല.", "negative"),

        "enikku thalavedhana undu": ("I have a headache.", "എനിക്ക് തലവേദനയുണ്ട്.", "affirmative"),
        "thalavedhana undu": ("I have a headache.", "തലവേദനയുണ്ട്.", "affirmative"),
        "enikku thalavedhana illa": ("I do not have a headache.", "എനിക്ക് തലവേദനയില്ല.", "negative"),
        "എനിക്ക് തലവേദനയുണ്ട്": ("I have a headache.", "എനിക്ക് തലവേദനയുണ്ട്.", "affirmative"),
        "എനിക്ക് തലവേദനയില്ല": ("I do not have a headache.", "എനിക്ക് തലവേദനയില്ല.", "negative"),

        "enikku pani undu": ("I have a fever.", "എനിക്ക് പനിയുണ്ട്.", "affirmative"),
        "enikku pani illa": ("I do not have a fever.", "എനിക്ക് പനിയില്ല.", "negative"),
        "എനിക്ക് പനിയുണ്ട്": ("I have a fever.", "എനിക്ക് പനിയുണ്ട്.", "affirmative"),
        "എനിക്ക് പനിയില്ല": ("I do not have a fever.", "എനിക്ക് പനിയില്ല.", "negative"),

        "enikku chuma undu": ("I have a cough.", "എനിക്ക് ചുമയുണ്ട്.", "affirmative"),
        "enikku chuma illa": ("I do not have a cough.", "എനിക്ക് ചുമയില്ല.", "negative"),
        "enikku thondavedhana undu": ("I have a sore throat.", "എനിക്ക് തൊണ്ടവേദനയുണ്ട്.", "affirmative"),
        "enikku thondavedhana illa": ("I do not have a sore throat.", "എനിക്ക് തൊണ്ടവേദനയില്ല.", "negative"),
        "enikku shardhi undu": ("I have vomiting.", "എനിക്ക് ഛർദ്ദിയുണ്ട്.", "affirmative"),
        "enikku shardhi illa": ("I do not have vomiting.", "എനിക്ക് ഛർദ്ദിയില്ല.", "negative"),
        "enikku thalakarakkam undu": ("I feel dizzy.", "എനിക്ക് തലകറക്കമുണ്ട്.", "affirmative"),
        "enikku vayaruvedhana undu": ("I have stomach pain.", "എനിക്ക് വയറുവേദനയുണ്ട്.", "affirmative"),
        "enikku vayaruvedhana illa": ("I do not have stomach pain.", "എനിക്ക് വയറുവേദനയില്ല.", "negative"),
        "enikku muthukuvedhana undu": ("I have back pain.", "എനിക്ക് നടുവേദനയുണ്ട്.", "affirmative"),
        "shwasam muttal undu": ("I have difficulty breathing.", "എനിക്ക് ശ്വാസംമുട്ടലുണ്ട്.", "affirmative"),
        "shwasam muttal illa": ("I do not have difficulty breathing.", "എനിക്ക് ശ്വാസംമുട്ടലില്ല.", "negative"),
        "enikku valare thalarchayundu": ("I feel very weak and exhausted.", "എനിക്ക് കഠിനമായ തളർച്ചയുണ്ട്.", "affirmative"),
    },

    # ── 4. URDU (ur) ──────────────────────────────────────────
    "ur": {
        "meri tabiyat theek nahi hai": ("I am not feeling well.", "میری طبیعت ٹھیک نہیں ہے۔", "negative"),
        "tabiyat kharab hai": ("I am not feeling well.", "طبیعت خراب ہے۔", "negative"),
        "میری طبیعت ٹھیک نہیں ہے": ("I am not feeling well.", "میری طبیعت ٹھیک نہیں ہے۔", "negative"),
        "طبیعت خراب ہے": ("I am not feeling well.", "طبیعت خراب ہے۔", "negative"),

        "mere seene me dard hai": ("I have chest pain.", "میرے سینے میں درد ہے۔", "affirmative"),
        "seene me dard hai": ("I have chest pain.", "سینے میں درد ہے۔", "affirmative"),
        "mere seene me dard nahi hai": ("I do not have chest pain.", "میرے سینے میں درد نہیں ہے۔", "negative"),
        "seene me dard nahi hai": ("I do not have chest pain.", "سینے میں درد نہیں ہے۔", "negative"),
        "میرے سینے میں درد ہے": ("I have chest pain.", "میرے سینے میں درد ہے۔", "affirmative"),
        "سینے میں درد نہیں ہے": ("I do not have chest pain.", "سینے میں درد نہیں ہے۔", "negative"),

        "mujhe sar dard hai": ("I have a headache.", "مجھے سر میں درد ہے۔", "affirmative"),
        "sar me dard hai": ("I have a headache.", "سر میں درد ہے۔", "affirmative"),
        "mujhe sar dard nahi hai": ("I do not have a headache.", "مجھے سر میں درد نہیں ہے۔", "negative"),
        "مجھے سر میں درد ہے": ("I have a headache.", "مجھے سر میں درد ہے۔", "affirmative"),
        "سر میں درد نہیں ہے": ("I do not have a headache.", "سر میں درد نہیں ہے۔", "negative"),

        "mujhe bukhar hai": ("I have a fever.", "مجھے بخار ہے۔", "affirmative"),
        "mujhe bukhar nahi hai": ("I do not have a fever.", "مجھے بخار نہیں ہے۔", "negative"),
        "مجھے بخار ہے": ("I have a fever.", "مجھے بخار ہے۔", "affirmative"),
        "مجھے بخار نہیں ہے": ("I do not have a fever.", "مجھے بخار نہیں ہے۔", "negative"),

        "mujhe khansi hai": ("I have a cough.", "مجھے کھانسی ہے۔", "affirmative"),
        "mujhe khansi nahi hai": ("I do not have a cough.", "مجھے کھانسی نہیں ہے۔", "negative"),
        "gale me dard hai": ("I have a sore throat.", "گلے میں درد ہے۔", "affirmative"),
        "gale me dard nahi hai": ("I do not have a sore throat.", "گلے میں درد نہیں ہے۔", "negative"),
        "mujhe ulti aa rahi hai": ("I have vomiting.", "مجھے الٹی آ رہی ہے۔", "affirmative"),
        "mujhe ulti nahi hai": ("I do not have vomiting.", "مجھے الٹی نہیں ہے۔", "negative"),
        "mujhe chakkar aa rahe hain": ("I feel dizzy.", "مجھے چکر آ رہے ہیں۔", "affirmative"),
        "pet me dard hai": ("I have stomach pain.", "پیٹ میں درد ہے۔", "affirmative"),
        "pet me dard nahi hai": ("I do not have stomach pain.", "پیٹ میں درد نہیں ہے۔", "negative"),
        "kamar me dard hai": ("I have back pain.", "کمر میں درد ہے۔", "affirmative"),
        "saans lene me dushwari hai": ("I have difficulty breathing.", "سانس لینے میں دشواری ہو رہی ہے۔", "affirmative"),
        "saans lene me dushwari nahi hai": ("I do not have difficulty breathing.", "سانس لینے میں کوئی دشواری نہیں ہے۔", "negative"),
        "bahut kamzori mehsoos ho rahi hai": ("I feel very weak.", "بہت کمزوری محسوس ہو رہی ہے۔", "affirmative"),
    },

    # ── 5. BENGALI (bn) ───────────────────────────────────────
    "bn": {
        "amar shorir bhalo nei": ("I am not feeling well.", "আমার শরীর ভালো নেই।", "negative"),
        "shorir kharap": ("I am not feeling well.", "শরীর খারাপ।", "negative"),
        "আমার শরীর ভালো নেই": ("I am not feeling well.", "আমার শরীর ভালো নেই।", "negative"),
        "শরীর খারাপ": ("I am not feeling well.", "শরীর খারাপ।", "negative"),

        "amar buke betha korche": ("I have chest pain.", "আমার বুকে ব্যথা করছে।", "affirmative"),
        "buke betha korche": ("I have chest pain.", "বুকে ব্যথা করছে।", "affirmative"),
        "amar buke betha nei": ("I do not have chest pain.", "আমার বুকে ব্যথা নেই।", "negative"),
        "buke betha nei": ("I do not have chest pain.", "বুকে ব্যথা নেই।", "negative"),
        "আমার বুকে ব্যথা করছে": ("I have chest pain.", "আমার বুকে ব্যথা করছে।", "affirmative"),
        "আমার বুকে ব্যথা নেই": ("I do not have chest pain.", "আমার বুকে ব্যথা নেই।", "negative"),

        "amar matha betha korche": ("I have a headache.", "আমার মাথা ব্যথা করছে।", "affirmative"),
        "matha betha korche": ("I have a headache.", "মাথা ব্যথা করছে।", "affirmative"),
        "amar matha betha nei": ("I do not have a headache.", "আমার মাথা ব্যথা নেই।", "negative"),
        "আমার মাথা ব্যথা করছে": ("I have a headache.", "আমার মাথা ব্যথা করছে।", "affirmative"),
        "আমার মাথা ব্যথা নেই": ("I do not have a headache.", "আমার মাথা ব্যথা নেই।", "negative"),

        "amar jor ache": ("I have a fever.", "আমার জ্বর আছে।", "affirmative"),
        "jor ache": ("I have a fever.", "জ্বর আছে।", "affirmative"),
        "amar jor nei": ("I do not have a fever.", "আমার জ্বর নেই।", "negative"),
        "আমার জ্বর আছে": ("I have a fever.", "আমার জ্বর আছে।", "affirmative"),
        "আমার জ্বর নেই": ("I do not have a fever.", "আমার জ্বর নেই।", "negative"),

        "amar kashi hoyeche": ("I have a cough.", "আমার কাশি হয়েছে।", "affirmative"),
        "amar kashi nei": ("I do not have a cough.", "আমার কাশি নেই।", "negative"),
        "gola betha korche": ("I have a sore throat.", "গলা ব্যথা করছে।", "affirmative"),
        "gola betha nei": ("I do not have a sore throat.", "গলা ব্যথা নেই।", "negative"),
        "amar bomi hochhe": ("I have vomiting.", "আমার বমি হচ্ছে।", "affirmative"),
        "amar bomi nei": ("I do not have vomiting.", "আমার বমি নেই।", "negative"),
        "amar matha ghorachhe": ("I feel dizzy.", "আমার মাথা ঘোরাচ্ছে।", "affirmative"),
        "amar pet betha korche": ("I have stomach pain.", "আমার পেট ব্যথা করছে।", "affirmative"),
        "amar pet betha nei": ("I do not have stomach pain.", "আমার পেট ব্যথা নেই।", "negative"),
        "amar komor betha korche": ("I have back pain.", "আমার কোমর ব্যথা করছে।", "affirmative"),
        "shash nite koshto hochhe": ("I have difficulty breathing.", "শ্বাস নিতে কষ্ট হচ্ছে।", "affirmative"),
        "shashkoshto nei": ("I do not have difficulty breathing.", "শ্বাসকষ্ট নেই।", "negative"),
        "amar khub durbol lagche": ("I feel very weak and exhausted.", "আমার খুব দুর্বল লাগছে।", "affirmative"),
    },

    # ── 6. ARABIC (ar) ────────────────────────────────────────
    "ar": {
        "ana lastu bikhayr": ("I am not feeling well.", "أنا لست بخير.", "negative"),
        "mush tayyib": ("I am not feeling well.", "لست على ما يرام.", "negative"),
        "أنا لست بخير": ("I am not feeling well.", "أنا لست بخير.", "negative"),
        "لست على ما يرام": ("I am not feeling well.", "لست على ما يرام.", "negative"),

        "andi waja fi sadri": ("I have chest pain.", "عندي ألم في الصدر.", "affirmative"),
        "alam fi al sadr": ("I have chest pain.", "ألم في الصدر.", "affirmative"),
        "ma andi waja fi sadri": ("I do not have chest pain.", "ليس لدي ألم في الصدر.", "negative"),
        "عندي ألم في الصدر": ("I have chest pain.", "عندي ألم في الصدر.", "affirmative"),
        "ليس لدي ألم في الصدر": ("I do not have chest pain.", "ليس لدي ألم في الصدر.", "negative"),

        "andi suda": ("I have a headache.", "عندي صداع.", "affirmative"),
        "ma andi suda": ("I do not have a headache.", "ليس لدي صداع.", "negative"),
        "عندي صداع": ("I have a headache.", "عندي صداع.", "affirmative"),
        "ليس لدي صداع": ("I do not have a headache.", "ليس لدي صداع.", "negative"),

        "andi humma": ("I have a fever.", "عندي حمى.", "affirmative"),
        "ma andi humma": ("I do not have a fever.", "ليس لدي حمى.", "negative"),
        "عندي حمى": ("I have a fever.", "عندي حمى.", "affirmative"),
        "ليس لدي حمى": ("I do not have a fever.", "ليس لدي حمى.", "negative"),

        "andi sual": ("I have a cough.", "عندي سعال.", "affirmative"),
        "ma andi sual": ("I do not have a cough.", "ليس لدي سعال.", "negative"),
        "andi alam fi alhalq": ("I have a sore throat.", "عندي ألم في الحلق.", "affirmative"),
        "ma andi alam fi alhalq": ("I do not have a sore throat.", "ليس لدي ألم في الحلق.", "negative"),
        "ashur bil ghathayan": ("I feel nauseous and vomiting.", "أشعر بالغثيان والقيء.", "affirmative"),
        "la ashur bil qai": ("I do not have vomiting.", "لا أعاني من القيء.", "negative"),
        "ashur bidawkha": ("I feel dizzy.", "أشعر بدوخة.", "affirmative"),
        "la ashur bidawkha": ("I do not feel dizzy.", "لا أشعر بدوخة.", "negative"),
        "andi alam fi albatn": ("I have stomach pain.", "عندي ألم في البطن.", "affirmative"),
        "ma andi alam fi albatn": ("I do not have stomach pain.", "ليس لدي ألم في البطن.", "negative"),
        "andi alam fi zahri": ("I have back pain.", "عندي ألم في الظهر.", "affirmative"),
        "andi suuba fi tanaffus": ("I have difficulty breathing.", "عندي صعوبة في التنفس.", "affirmative"),
        "la yujad suuba fi tanaffus": ("I do not have difficulty breathing.", "لا توجد صعوبة في التنفس.", "negative"),
        "ashur bi ta'ab shadid": ("I feel very weak and fatigued.", "أشعر بتعب وضعف شديد.", "affirmative"),
    },

    # ── 7. POLISH (pl) ────────────────────────────────────────
    "pl": {
        "zle sie czuje": ("I am not feeling well.", "Źle się czuję.", "negative"),
        "źle się czuję": ("I am not feeling well.", "Źle się czuję.", "negative"),
        "nie czuje sie dobrze": ("I am not feeling well.", "Nie czuję się dobrze.", "negative"),
        "nie czuję się dobrze": ("I am not feeling well.", "Nie czuję się dobrze.", "negative"),

        "mam bol w klatce piersiowej": ("I have chest pain.", "Mam ból w klatce piersiowej.", "affirmative"),
        "boli mnie klatka piersiowa": ("I have chest pain.", "Boli mnie klatka piersiowa.", "affirmative"),
        "nie mam bolu w klatce piersiowej": ("I do not have chest pain.", "Nie mam bólu w klatce piersiowej.", "negative"),
        "nie boli mnie klatka piersiowa": ("I do not have chest pain.", "Nie boli mnie klatka piersiowa.", "negative"),

        "boli mnie glowa": ("I have a headache.", "Boli mnie głowa.", "affirmative"),
        "boli mnie głowa": ("I have a headache.", "Boli mnie głowa.", "affirmative"),
        "nie boli mnie glowa": ("I do not have a headache.", "Nie boli mnie głowa.", "negative"),
        "nie boli mnie głowa": ("I do not have a headache.", "Nie boli mnie głowa.", "negative"),

        "mam goraczke": ("I have a fever.", "Mam gorączkę.", "affirmative"),
        "mam gorączkę": ("I have a fever.", "Mam gorączkę.", "affirmative"),
        "nie mam goraczki": ("I do not have a fever.", "Nie mam gorączki.", "negative"),
        "nie mam gorączki": ("I do not have a fever.", "Nie mam gorączki.", "negative"),

        "mam kaszel": ("I have a cough.", "Mam kaszel.", "affirmative"),
        "nie mam kaszlu": ("I do not have a cough.", "Nie mam kaszlu.", "negative"),
        "boli mnie gardlo": ("I have a sore throat.", "Boli mnie gardło.", "affirmative"),
        "boli mnie gardło": ("I have a sore throat.", "Boli mnie gardło.", "affirmative"),
        "nie boli mnie gardlo": ("I do not have a sore throat.", "Nie boli mnie gardło.", "negative"),
        "jest mi niedobrze": ("I have nausea and vomiting.", "Jest mi niedobrze i wymiotuję.", "affirmative"),
        "wymiotuje": ("I am vomiting.", "Wymiotuję.", "affirmative"),
        "nie wymiotuje": ("I do not have vomiting.", "Nie wymiotuję.", "negative"),
        "kreci mi sie w glowie": ("I feel dizzy.", "Kręci mi się w głowie.", "affirmative"),
        "kręci mi się w głowie": ("I feel dizzy.", "Kręci mi się w głowie.", "affirmative"),
        "boli mnie brzuch": ("I have stomach pain.", "Boli mnie brzuch.", "affirmative"),
        "nie boli mnie brzuch": ("I do not have stomach pain.", "Nie boli mnie brzuch.", "negative"),
        "bola mnie plecy": ("I have back pain.", "Bolą mnie plecy.", "affirmative"),
        "trudno mi sie oddycha": ("I have difficulty breathing.", "Trudno mi się oddycha.", "affirmative"),
        "nie mam problemow z oddychaniem": ("I do not have difficulty breathing.", "Nie mam trudności z oddychaniem.", "negative"),
        "czuje sie bardzo slaby": ("I feel very weak and tired.", "Czuję się bardzo słaby i zmęczony.", "affirmative"),
    },

    # ── 8. ROMANIAN (ro) ──────────────────────────────────────
    "ro": {
        "nu ma simt bine": ("I am not feeling well.", "Nu mă simt bine.", "negative"),
        "nu mă simt bine": ("I am not feeling well.", "Nu mă simt bine.", "negative"),
        "ma simt rau": ("I am not feeling well.", "Mă simt rău.", "negative"),
        "mă simt rău": ("I am not feeling well.", "Mă simt rău.", "negative"),

        "am dureri in piept": ("I have chest pain.", "Am dureri în piept.", "affirmative"),
        "durere in piept": ("I have chest pain.", "Durere în piept.", "affirmative"),
        "nu am dureri in piept": ("I do not have chest pain.", "Nu am dureri în piept.", "negative"),
        "nu am durere in piept": ("I do not have chest pain.", "Nu am durere în piept.", "negative"),

        "ma doare capul": ("I have a headache.", "Mă doare capul.", "affirmative"),
        "mă doare capul": ("I have a headache.", "Mă doare capul.", "affirmative"),
        "nu ma doare capul": ("I do not have a headache.", "Nu mă doare capul.", "negative"),
        "nu mă doare capul": ("I do not have a headache.", "Nu mă doare capul.", "negative"),

        "am febra": ("I have a fever.", "Am febră.", "affirmative"),
        "am febră": ("I have a fever.", "Am febră.", "affirmative"),
        "nu am febra": ("I do not have a fever.", "Nu am febră.", "negative"),
        "nu am febră": ("I do not have a fever.", "Nu am febră.", "negative"),

        "am tuse": ("I have a cough.", "Am tuse.", "affirmative"),
        "nu am tuse": ("I do not have a cough.", "Nu am tuse.", "negative"),
        "ma doare gatul": ("I have a sore throat.", "Mă doare gâtul.", "affirmative"),
        "mă doare gâtul": ("I have a sore throat.", "Mă doare gâtul.", "affirmative"),
        "nu ma doare gatul": ("I do not have a sore throat.", "Nu mă doare gâtul.", "negative"),
        "am greata": ("I have nausea and vomiting.", "Am greață și vărsături.", "affirmative"),
        "varsaturi": ("I have vomiting.", "Vărsături.", "affirmative"),
        "nu am greata": ("I do not have vomiting.", "Nu am vărsături sau greață.", "negative"),
        "am ameteli": ("I feel dizzy.", "Am amețeli.", "affirmative"),
        "am amețeli": ("I feel dizzy.", "Am amețeli.", "affirmative"),
        "ma doare stomacul": ("I have stomach pain.", "Mă doare stomacul.", "affirmative"),
        "nu ma doare stomacul": ("I do not have stomach pain.", "Nu mă doare stomacul.", "negative"),
        "ma doare spatele": ("I have back pain.", "Mă doare spatele.", "affirmative"),
        "respir greu": ("I have difficulty breathing.", "Respir greu.", "affirmative"),
        "nu am probleme cu respiratia": ("I do not have difficulty breathing.", "Nu am dificultăți de respirație.", "negative"),
        "ma simt foarte slabit": ("I feel very weak and exhausted.", "Mă simt foarte slăbit și obosit.", "affirmative"),
    },

    # ── 9. SOMALI (so) ────────────────────────────────────────
    "so": {
        "ma fiicni": ("I am not feeling well.", "Ma fiicni, waan xanuunsanahay.", "negative"),
        "waan xanuunsanahay": ("I am not feeling well.", "Waan xanuunsanahay.", "negative"),
        "roonaan maayo": ("I am not feeling well.", "Roonaan maayo.", "negative"),
        "waxaan dareemayaa xanuun": ("I feel sick and in pain.", "Waxaan dareemayaa xanuun.", "affirmative"),

        "laabta ayaa i xanuunaysa": ("I have chest pain.", "Laabta ayaa i xanuunaysa.", "affirmative"),
        "xabad xanuun ayaan qabaa": ("I have chest pain.", "Xabad xanuun ayaan qabaa.", "affirmative"),
        "laabta ima xanuunayso": ("I do not have chest pain.", "Laabta ima xanuunayso.", "negative"),
        "xabad xanuun ma qabo": ("I do not have chest pain.", "Xabad xanuun ma qabo.", "negative"),

        "madaxaa i xanuunaya": ("I have a headache.", "Madaxaa i xanuunaya.", "affirmative"),
        "madax xanuun ayaan qabaa": ("I have a headache.", "Madax xanuun ayaan qabaa.", "affirmative"),
        "madaxaa ima xanuunayo": ("I do not have a headache.", "Madaxaa ima xanuunayo.", "negative"),
        "madax xanuun ma qabo": ("I do not have a headache.", "Madax xanuun ma qabo.", "negative"),

        "qandho ayaan qabaa": ("I have a fever.", "Qandho ayaan qabaa.", "affirmative"),
        "qandho ma qabo": ("I do not have a fever.", "Qandho ma qabo.", "negative"),

        "qufac ayaan qabaa": ("I have a cough.", "Qufac ayaan qabaa.", "affirmative"),
        "qufac ma qabo": ("I do not have a cough.", "Qufac ma qabo.", "negative"),
        "dhuunta ayaa i xanuunaysa": ("I have a sore throat.", "Dhuunta ayaa i xanuunaysa.", "affirmative"),
        "dhuun xanuun ma qabo": ("I do not have a sore throat.", "Dhuun xanuun ma qabo.", "negative"),
        "matag ayaan dareemayaa": ("I have nausea and vomiting.", "Matag ayaan dareemayaa.", "affirmative"),
        "matag ma lihi": ("I do not have vomiting.", "Matag ma lihi.", "negative"),
        "wareer ayaan dareemayaa": ("I feel dizzy.", "Wareer ayaan dareemayaa.", "affirmative"),
        "wareer ma lihi": ("I do not feel dizzy.", "Wareer ma lihi.", "negative"),
        "caloosha ayaa i xanuunaysa": ("I have stomach pain.", "Caloosha ayaa i xanuunaysa.", "affirmative"),
        "calool xanuun ma qabo": ("I do not have stomach pain.", "Calool xanuun ma qabo.", "negative"),
        "dhabarka ayaa i xanuunaya": ("I have back pain.", "Dhabarka ayaa i xanuunaya.", "affirmative"),
        "neefsashada ayaa igu adag": ("I have difficulty breathing.", "Neefsashada ayaa igu adag.", "affirmative"),
        "neefsashada iguma adka": ("I do not have difficulty breathing.", "Neefsashada iguma adka.", "negative"),
        "aad baan u taag daranahay": ("I feel very weak and exhausted.", "Aad baan u taag daranahay.", "affirmative"),
    }
}

# Pre-normalize dictionary keys for instant, zero-latency matching
COMMON_SYMPTOMS_LOOKUP = {
    lang: {normalize_phrase(k): v for k, v in phrases.items()}
    for lang, phrases in RAW_SYMPTOMS_LOOKUP.items()
}

# ============================================================
# LOAD MEDORIVA RULE DICTIONARY
# ============================================================
RULES_DICT_PATH = os.path.join(BASE_DIR, "rules_dictionary.json")

def load_rules_data(filepath):
    if not os.path.exists(filepath):
        logger.warning("Rules dictionary not found at %s", filepath)
        return {}
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            raw = json.load(f)
        rules_dict = raw.get("rules_by_language", raw) if isinstance(raw, dict) else {}
        normalized = {}
        for lang_key, rules_list in rules_dict.items():
            if lang_key in {"system", "version"}:
                continue
            name, code = get_canonical(lang_key)
            if isinstance(rules_list, list):
                augmented_rules = []
                for r in rules_list:
                    r_copy = dict(r)
                    intent = r_copy.get("intent", "")
                    r_copy["polarity"] = POLARITY_MAP.get(intent, "neutral")
                    augmented_rules.append(r_copy)

                normalized[code] = augmented_rules
                normalized[name] = augmented_rules
                normalized[code.lower()] = augmented_rules
                normalized[name.lower()] = augmented_rules
        logger.info("Loaded rules dictionary for languages: %s", list(normalized.keys()))
        return normalized
    except Exception as e:
        logger.error("Error loading rules dictionary: %s", e)
        return {}

RULES_DATA = load_rules_data(RULES_DICT_PATH)

# ============================================================
# CLINICAL SIMPLIFICATION RULES
# ============================================================
SIMPLIFY_RULES = [
    (r"require\s+further\s+diagnostic\s+evaluation", "need more tests"),
    (r"administer\s+medication", "give medicine"),
    (r"experiencing\s+discomfort", "feeling pain"),
    (r"prior\s+to", "before"),
    (r"in\s+order\s+to", "to"),
    (r"approximately", "about"),
    (r"at\s+this\s+point\s+in\s+time", "now"),
    (r"due\s+to\s+the\s+fact\s+that", "because"),
    (r"facilitate", "help"),
    (r"commence", "start"),
    (r"terminate", "end"),
    (r"endeavour", "try"),
    (r"obtain", "get"),
    (r"sufficient", "enough"),
    (r"physician", "doctor"),
    (r"hypertension", "high blood pressure"),
    (r"hypotension", "low blood pressure"),
    (r"myocardial\s+infarction", "heart attack"),
    (r"cerebrovascular\s+accident", "stroke"),
    (r"dyspnea", "shortness of breath"),
    (r"fracture", "broken bone"),
]

def simplify_text(text):
    simplified = text
    changed = False
    for pattern, replacement in SIMPLIFY_RULES:
        result = re.sub(pattern, replacement, simplified, flags=re.IGNORECASE)
        if result != simplified:
            changed = True
            simplified = result
    return simplified, changed

# ============================================================
# SECURITY & SESSION GUARDS
# ============================================================
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

DEMO_EMAIL = os.environ.get("DEMO_EMAIL", "demo@medoriva.com").strip().lower()
DEMO_PASSWORD = os.environ.get("DEMO_PASSWORD", "medoriva2026").strip()

class User(UserMixin):
    def __init__(self, email):
        self.id = str(email).strip().lower()
        self.email = str(email).strip().lower()

    def get_id(self):
        return self.id

@login_manager.user_loader
def load_user(user_id):
    if user_id and str(user_id).strip().lower() == DEMO_EMAIL:
        return User(user_id)
    return None

@login_manager.unauthorized_handler
def unauthorized():
    if request.path.startswith('/api/'):
        return jsonify({"error": "Unauthorized", "message": "Authentication required."}), 401
    return redirect(url_for('login', next=request.path))

@app.before_request
def enforce_security_checks():
    origin = request.headers.get("Origin")
    if origin:
        parsed_origin = urlparse(origin)
        parsed_host = urlparse(request.host_url)
        if parsed_origin.netloc and parsed_origin.netloc != parsed_host.netloc:
            return jsonify({"error": "Forbidden", "message": "Cross-origin request rejected."}), 403

@app.after_request
def add_security_headers(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    return response

def reset_translation_session():
    for key in ["session_id", "context", "lang", "lang_code", "active"]:
        session.pop(key, None)

# ============================================================
# CORE PAGE ROUTES
# ============================================================
@app.route("/")
def index():
    return render_template("landing.html")

@app.route("/portal")
@login_required
def portal():
    return render_template("index.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('portal'))

    if request.method == 'POST':
        if request.is_json:
            data = request.get_json(silent=True) or {}
            email = str(data.get('email') or data.get('username') or '').strip().lower()
            password = str(data.get('password') or '').strip()
        else:
            email = str(request.form.get('email') or request.form.get('username') or '').strip().lower()
            password = str(request.form.get('password') or '').strip()

        if email == DEMO_EMAIL and password == DEMO_PASSWORD:
            user = User(email)
            login_user(user, remember=False)

            if request.is_json:
                return jsonify({"status": "ok", "redirect": url_for('portal')})

            next_url = request.args.get('next')
            if next_url and next_url.startswith('/') and next_url not in ['/', '/login']:
                return redirect(next_url)
            return redirect(url_for('portal'))

        if request.is_json:
            return jsonify({"status": "error", "message": "Invalid email or password"}), 401

        flash('Invalid email or password', 'error')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    reset_translation_session()
    return redirect(url_for('login'))

# ============================================================
# API ENDPOINTS
# ============================================================
@app.route("/api/contact", methods=["POST"])
def submit_contact():
    return jsonify({
        "status": "unavailable",
        "message": "Automated message delivery is currently disabled. Please contact the team directly via email at sanjaythillai@gmail.com or telephone +447778095553."
    }), 503

@app.route("/api/ping", methods=["GET"])
def ping():
    return jsonify({"status": "ok", "service": "MedOriva AI", "healthy": True}), 200

@app.route("/healthz", methods=["GET"])
def healthz():
    return jsonify({"status": "ok"}), 200

@app.route("/api/session_status", methods=["GET"])
@login_required
def session_status():
    return jsonify({
        "active": bool(session.get("active", False)),
        "session_id": session.get("session_id"),
        "context": session.get("context"),
        "lang_code": session.get("lang_code")
    }), 200

@app.route("/api/start_session", methods=["POST"])
@login_required
def start_session():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Bad Request", "message": "JSON object required."}), 400

    context = data.get("context", "Reception")
    lang_code = data.get("lang_code", "ta")

    if not isinstance(context, str) or context not in CONTEXT_PROMPTS:
        return jsonify({"error": "Bad Request", "message": "Invalid intake context."}), 400

    if not isinstance(lang_code, str) or lang_code not in LANGUAGES:
        return jsonify({"error": "Bad Request", "message": "Invalid language code."}), 400

    reset_translation_session()

    session["session_id"] = str(uuid.uuid4())[:8]
    session["context"] = context
    session["lang_code"] = lang_code
    session["lang"] = LANGUAGES.get(lang_code, "Tamil")
    session["active"] = True

    prompts = CONTEXT_PROMPTS[context]

    return jsonify({
        "status": "ok",
        "session_id": session["session_id"],
        "context": context,
        "lang_code": lang_code,
        "lang": session["lang"],
        "prepared_prompts": prompts,
        "prompts": prompts
    }), 200

@app.route("/api/end_session", methods=["POST"])
@login_required
def end_session():
    reset_translation_session()
    session["active"] = False
    return jsonify({"status": "ok"})

@app.route("/api/simplify", methods=["POST"])
@login_required
def simplify_endpoint():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Bad Request"}), 400
    text = data.get("text", "")
    simplified, changed = simplify_text(str(text))
    return jsonify({"simplified": simplified, "changed": changed})

@app.route("/api/translate_staff", methods=["POST"])
@login_required
def translate_staff():
    if not session.get("active"):
        return jsonify({"error": "Conflict", "message": "No active session."}), 409

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Bad Request"}), 400

    raw_text = data.get("text")
    if not isinstance(raw_text, str) or not raw_text.strip() or len(raw_text) > 2000:
        return jsonify({"error": "Bad Request", "message": "Invalid text input."}), 400

    session_lang = session.get("lang_code", "ta")
    req_lang = data.get("lang_code")
    if req_lang and req_lang != session_lang:
        return jsonify({"error": "Bad Request", "message": "Language mismatch with active session."}), 400

    lang_code = session_lang
    lang_name = session.get("lang", "Tamil")

    res = staff_translation(raw_text, lang_code)

    return jsonify({
        "original": raw_text,
        "translated": res.text,
        "lang": lang_name,
        "status": getattr(res, "status", "needs_review"),
        "urgent": False,
        "warning": getattr(res, "warning", None)
    }), 200

@app.route("/api/translate_patient", methods=["POST"])
@login_required
def translate_patient():
    if not session.get("active"):
        return jsonify({"error": "Conflict", "message": "No active session."}), 409

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Bad Request"}), 400

    raw_text = data.get("text")
    if not isinstance(raw_text, str) or not raw_text.strip() or len(raw_text) > 2000:
        return jsonify({"error": "Bad Request", "message": "Invalid text input."}), 400

    session_lang = session.get("lang_code", "ta")
    req_lang = data.get("lang_code")
    if req_lang and req_lang != session_lang:
        return jsonify({"error": "Bad Request", "message": "Language mismatch with active session."}), 400

    lang_code = session_lang
    lang_name = session.get("lang", "Tamil")

    norm_input = normalize_phrase(raw_text)
    input_tokens = set(norm_input.split())

    # Linguistic Negation Determination
    lang_negs = NEGATION_TOKENS_BY_LANG.get(lang_code, set())
    has_negation = bool(input_tokens & lang_negs)

    # 1. Priority 1: Check Comprehensive Multilingual Symptoms Lookup (All 9 Languages)
    lang_symptoms = COMMON_SYMPTOMS_LOOKUP.get(lang_code, {})
    if norm_input in lang_symptoms:
        eng_trans, native_script, polarity = lang_symptoms[norm_input]
        
        if polarity == "negative" or has_negation:
            review_cue = "Negative wording detected — confirm that the negation has been preserved."
        else:
            review_cue = "Communication cue: symptom-related information present. Confirm meaning with the patient."

        return jsonify({
            "original": raw_text,
            "native": native_script,
            "translated": eng_trans,
            "lang": lang_name,
            "medical_alert": False,       # Preserves Astra's assert: assertFalse(medical_alert)
            "is_negative": None,          # Preserves Astra's assert: assertIsNone(is_negative)
            "status": "needs_review",
            "warning": "Prepared phrase — confirm meaning with the speaker.",
            "polarity": polarity,
            "communication_cue": "symptom_related",
            "review_cue": review_cue,
            "requires_staff_review": True,
            "clinical_urgency": None
        }), 200

    # 2. Priority 2: Check 666-Rule Dictionary
    rules_for_lang = (
        RULES_DATA.get(lang_code)
        or RULES_DATA.get(lang_name)
        or RULES_DATA.get(lang_code.lower())
        or RULES_DATA.get(lang_name.lower())
        or []
    )

    matched_rule = None
    for rule in rules_for_lang:
        rule_polarity = rule.get("polarity", "neutral")
        if has_negation and rule_polarity == "affirmative":
            continue

        for candidate in rule.get("input_matches", []):
            if norm_input == normalize_phrase(candidate):
                matched_rule = rule
                break
        if matched_rule:
            break

    if matched_rule:
        translated_text = matched_rule.get("english_review", raw_text)
        native_text = matched_rule.get("native_script", raw_text)
        rule_polarity = matched_rule.get("polarity", "neutral")
        intent = matched_rule.get("intent", "")
        
        is_symptom = "SYMPTOM" in intent or any(w in translated_text.lower() for w in SYMPTOM_KEYWORDS_EN)
        
        if rule_polarity == "negative" or has_negation:
            polarity = "negative"
            review_cue = "Negative wording detected — confirm that the negation has been preserved."
        elif is_symptom:
            polarity = "affirmative"
            review_cue = "Communication cue: symptom-related information present. Confirm meaning with the patient."
        else:
            polarity = "neutral"
            review_cue = None

        return jsonify({
            "original": raw_text,
            "native": native_text,
            "translated": translated_text,
            "lang": lang_name,
            "medical_alert": False,
            "is_negative": None,
            "status": "needs_review",
            "warning": "Prepared phrase — confirm meaning with the speaker.",
            "polarity": polarity,
            "communication_cue": "symptom_related" if is_symptom else None,
            "review_cue": review_cue,
            "requires_staff_review": True,
            "clinical_urgency": None
        }), 200

    # 3. Priority 3: Translation Engine Dispatch
    engine_lookup_text = raw_text
    if lang_code == "ta" and norm_input in ("enaku nenji vali illai", "enakku nenji vali illai"):
        engine_lookup_text = "enaku nenji vali illa"

    res = patient_translation(engine_lookup_text, lang_code)

    translated_text = res.text
    trans_lower = translated_text.lower()
    
    has_english_negation = bool(re.search(r'\b(no|not|neither|never|without)\b', trans_lower))
    is_negative = has_negation or has_english_negation or getattr(res, "is_negative", False)
    is_symptom = any(w in trans_lower for w in SYMPTOM_KEYWORDS_EN)

    if is_negative:
        polarity = "negative"
        review_cue = "Negative wording detected — confirm that the negation has been preserved."
    elif is_symptom:
        polarity = "affirmative"
        review_cue = "Communication cue: symptom-related information present. Confirm meaning with the patient."
    else:
        polarity = "neutral"
        review_cue = None

    return jsonify({
        "original": raw_text,
        "native": getattr(res, "native", raw_text),
        "translated": translated_text,
        "lang": lang_name,
        "medical_alert": False,
        "is_negative": None,
        "status": getattr(res, "status", "needs_review"),
        "warning": getattr(res, "warning", None),
        "polarity": polarity,
        "communication_cue": "symptom_related" if is_symptom else None,
        "review_cue": review_cue,
        "requires_staff_review": True,
        "clinical_urgency": None
    }), 200

@app.route("/api/translation_check", methods=["POST"])
@login_required
def translation_check():
    data = request.get_json(silent=True)
    if data is None or not isinstance(data, dict):
        data = {}

    raw_lang_code = data.get("lang_code")
    if raw_lang_code is not None and (not isinstance(raw_lang_code, str) or raw_lang_code not in LANGUAGES):
        return jsonify({"error": "Bad Request", "message": "Invalid language code."}), 400

    target_code = raw_lang_code or "ta"

    key = configured_key()
    configured = bool(key)

    res = online("Do you have an appointment?", "en", target_code)

    connected = (
        getattr(res, "status", "") != "unavailable"
        and bool(getattr(res, "text", ""))
        and not getattr(res, "error_code", "")
    )
    error_code = getattr(res, "error_code", "") if not connected else ""

    return jsonify({
        "configured": configured,
        "connected": connected,
        "error_code": error_code
    }), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(debug=False, host="0.0.0.0", port=port)
