from datetime import timedelta
import os
import re
import uuid

from clinical_phrases import (
    AFFIRMATION_PATTERNS,
    CLINICAL_DICTIONARY,
    DURATION_PATTERNS,
    GUIDED_PROMPTS,
    MULTI_LANG_SYMPTOMS,
    NEGATION_PATTERNS,
    SIMPLIFY_RULES,
    URGENT_SYMPTOMS_CONFIG,
)
from deep_translator import GoogleTranslator, MyMemoryTranslator
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from flask_login import LoginManager, UserMixin, current_user, login_required, login_user, logout_user

# ============================================================
# APP INITIALIZATION & SECURITY CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(BASE_DIR, 'templates')

app = Flask(__name__, template_folder=template_dir)
# Change this key to invalidate all old browser cookies
app.secret_key = "medoriva-reset-force-login-2026-v2"
# Standard session security settings (expires on browser close or logout)
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

# ============================================================
# FLASK-LOGIN AUTHENTICATION
# ============================================================

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = "Please log in to access MedOriva AI."

DEMO_EMAIL = "demo@medoriva.com"
DEMO_PASSWORD = "medoriva2026"

class User(UserMixin):
    def __init__(self, email):
        self.id = str(email).strip().lower()
        self.email = str(email).strip().lower()

    def get_id(self):
        return self.id

@login_manager.user_loader
def load_user(user_id):
    if user_id and str(user_id).strip().lower() == DEMO_EMAIL.lower():
        return User(user_id)
    return None

@login_manager.unauthorized_handler
def unauthorized():
    if request.path.startswith('/api/'):
        return jsonify({"error": "Unauthorized", "message": "Session expired. Please log in again."}), 401
    return redirect(url_for('login', next=request.path))

# ============================================================
# CACHE & STRING NORMALIZATION
# ============================================================

translation_cache = {}

def normalize_text(text):
    if not text:
        return ""
    cleaned = re.sub(r'[^\w\s]', ' ', str(text).lower())
    return " ".join(cleaned.split())

def is_native_script(text):
    if not text:
        return False
    return any(ord(char) > 0x0590 for char in text)

def get_cached_translation(text, target_lang):
    cache_key = f"{normalize_text(text)}_{target_lang}"
    return translation_cache.get(cache_key)

def set_cached_translation(text, target_lang, result):
    cache_key = f"{normalize_text(text)}_{target_lang}"
    translation_cache[cache_key] = result

def reset_translation_session():
    """Clears translation context without logging out the authenticated user."""
    keys_to_clear = ["session_id", "context", "lang", "lang_code", "active"]
    for key in keys_to_clear:
        session.pop(key, None)

LANG_MAP = {
    "ta": "ta", "hi": "hi", "ml": "ml", "bn": "bn",
    "ur": "ur", "ar": "ar", "pl": "pl", "so": "so", "ro": "ro",
}

def get_clean_lang_code(lang_code):
    if not lang_code:
        return "en"
    return LANG_MAP.get(lang_code.lower()[:2], lang_code.lower()[:2])

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
# EXACT & HIGH-CONFIDENCE DICTIONARY LOOKUP
# ============================================================

def lookup_clinical_phrase(text, lang_code):
    """Performs strict matching to avoid substring collisions."""
    if not lang_code or lang_code not in CLINICAL_DICTIONARY:
        return None
    
    lang_dict = CLINICAL_DICTIONARY[lang_code]
    norm_input = normalize_text(text)
    
    # 1. Exact match
    if norm_input in lang_dict:
        return lang_dict[norm_input]
    
    # 2. Strict matching without partial question collisions
    for phrase_key, data in lang_dict.items():
        norm_key = normalize_text(phrase_key)
        if norm_input == norm_key:
            return data
            
    return None

# ============================================================
# MULTI-LANGUAGE PARSING ENGINE (For Phonetic / Romanized Text)
# ============================================================

def detect_affirmation(text, lang_code):
    norm = f" {normalize_text(text)} "
    tokens = norm.split()
    for word in AFFIRMATION_PATTERNS.get(lang_code, []) + AFFIRMATION_PATTERNS["en"]:
        if f" {normalize_text(word)} " in norm or word in tokens:
            return True
    return False

def detect_negation(text, lang_code=None):
    norm = f" {normalize_text(text)} "
    tokens = norm.split()
    if lang_code and lang_code in NEGATION_PATTERNS:
        for word in NEGATION_PATTERNS[lang_code]:
            clean_word = normalize_text(word)
            if f" {clean_word} " in norm or clean_word in tokens:
                return True

    for word in NEGATION_PATTERNS["en"]:
        if f" {word} " in norm or word in tokens:
            return True

    return False

def extract_duration(text):
    for pattern, replacement in DURATION_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            return re.search(pattern, text, flags=re.IGNORECASE).expand(replacement)
    return None

def extract_symptom(text, lang_code):
    norm = normalize_text(text)
    for sym_key, sym_data in MULTI_LANG_SYMPTOMS.items():
        if lang_code in sym_data:
            native_label, aliases = sym_data[lang_code]
            for alias in aliases:
                if normalize_text(alias) in norm:
                    return sym_key, sym_data["english"], native_label
        if sym_data["english"] in norm or sym_key in norm:
            native_label = sym_data.get(lang_code, (sym_data["english"], []))[0]
            return sym_key, sym_data["english"], native_label
    return None, None, None

def evaluate_medical_triage(original_text, english_text, lang_code):
    combined = f"{normalize_text(original_text)} {normalize_text(english_text)}"
    is_neg = detect_negation(original_text, lang_code) or detect_negation(english_text, "en")
    
    detected_symptom = None
    is_urgent = False
    
    for symptom_name, phrase_list in URGENT_SYMPTOMS_CONFIG.items():
        for phrase in phrase_list:
            if normalize_text(phrase) in combined:
                detected_symptom = symptom_name
                is_urgent = True
                break
        if is_urgent:
            break
            
    medical_alert = bool(is_urgent and not is_neg)
    
    return {
        "symptom_detected": detected_symptom,
        "is_negative": is_neg,
        "medical_alert": medical_alert
    }

# ============================================================
# TRANSLATION HANDLERS
# ============================================================

def execute_online_translation(text, src, target):
    if not text:
        return ""
    try:
        res = GoogleTranslator(source=src, target=target).translate(text)
        if res and res.strip().lower() != text.strip().lower():
            return res
    except Exception:
        pass

    try:
        res = MyMemoryTranslator(source=src, target=target).translate(text)
        if res:
            return res
    except Exception:
        pass

    return text

def translate_staff_to_native(text, target_lang_code):
    if not text:
        return "", None

    lookup = lookup_clinical_phrase(text, target_lang_code)
    if lookup:
        return lookup[1], None

    cached = get_cached_translation(text, target_lang_code)
    if cached:
        return cached, None

    target = get_clean_lang_code(target_lang_code)
    translated = execute_online_translation(text, "en", target)
    
    if translated:
        set_cached_translation(text, target_lang_code, translated)
        return translated, None

    return text, "Translation unavailable"

def translate_patient_input(text, lang_code):
    """
    Translates Patient input (Romanized or Native script) across all languages into:
    1. Clean English for Staff
    2. Pure Native Script for UI display
    """
    if not text:
        return "", "", None

    # 1. Exact match in phrasebook
    lookup = lookup_clinical_phrase(text, lang_code)
    if lookup:
        return lookup[0], lookup[1], None

    # 2. If already written in Native Script (Non-Latin)
    if is_native_script(text):
        target_src = get_clean_lang_code(lang_code)
        english_trans = execute_online_translation(text, target_src, "en")
        return english_trans, text, None

    # 3. Intelligent Semantic Parser for Romanized / Phonetic Text
    has_affirmation = detect_affirmation(text, lang_code)
    has_negation = detect_negation(text, lang_code)
    duration_str = extract_duration(text)
    sym_key, sym_english, sym_native = extract_symptom(text, lang_code)

    if sym_english:
        english_parts = []
        if has_affirmation:
            english_parts.append("Yes,")
        
        if has_negation:
            english_parts.append(f"I do not have {sym_english}")
        else:
            if duration_str:
                english_parts.append(f"I have had {sym_english} {duration_str}")
            else:
                english_parts.append(f"I have {sym_english}")
                
        constructed_english = " ".join(english_parts)
        target_clean = get_clean_lang_code(lang_code)
        reconstructed_native = execute_online_translation(constructed_english, "en", target_clean)
        
        return constructed_english, reconstructed_native, None

    # 4. Fallback for unlisted Romanized text
    english_trans = execute_online_translation(text, "auto", "en")
    target_clean = get_clean_lang_code(lang_code)
    native_trans = execute_online_translation(english_trans, "en", target_clean)
    
    return english_trans, native_trans, None

# ============================================================
# FLASK ROUTES
# ============================================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        if request.is_json:
            data = request.get_json() or {}
            email = str(data.get('email') or data.get('username') or '').strip().lower()
            password = str(data.get('password') or '').strip()
        else:
            email = str(request.form.get('email') or request.form.get('username') or '').strip().lower()
            password = str(request.form.get('password') or '').strip()

        if email == DEMO_EMAIL.lower() and password == DEMO_PASSWORD:
            user = User(email)
            # remember=False requires login after closing the browser / logging out
            login_user(user, remember=False)

            if request.is_json:
                return jsonify({"status": "ok", "redirect": url_for('index')})

            next_url = request.args.get('next')
            if next_url and next_url.startswith('/'):
                return redirect(next_url)
            return redirect(url_for('index'))

        if request.is_json:
            return jsonify({"status": "error", "message": "Invalid email or password"}), 401

        flash('Invalid email or password', 'error')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('login'))

@app.route("/")
@login_required
def index():
    return render_template("index.html")

@app.route("/api/ping", methods=["GET"])
@login_required
def ping():
    return jsonify({"status": "Flask is running", "session": dict(session)})

@app.route("/api/start_session", methods=["POST"])
@login_required
def start_session():
    try:
        data = request.get_json() or {}
        reset_translation_session()
        session["session_id"] = str(uuid.uuid4())[:8]
        session["context"] = data.get("context", "Reception")
        session["lang"] = data.get("lang", "Tamil")
        session["lang_code"] = data.get("lang_code", "ta")
        session["active"] = True
        prompts = GUIDED_PROMPTS.get(session["context"], [])
        return jsonify({
            "status": "ok",
            "session_id": session["session_id"],
            "prompts": prompts,
            "context": session["context"],
            "lang": session["lang"],
        })
    except Exception as e:
        return jsonify({"status": "error", "error": f"Could not start session: {str(e)}"}), 500

@app.route("/api/end_session", methods=["POST"])
@login_required
def end_session():
    reset_translation_session()
    return jsonify({"status": "ok"})

@app.route("/api/translate_staff", methods=["POST"])
@login_required
def translate_staff():
    data = request.get_json() or {}
    raw_text = data.get("text", "").strip()
    if not raw_text:
        return jsonify({"error": "No text provided"}), 400

    lang_code = session.get("lang_code", "ta")
    lang_name = session.get("lang", "Tamil")

    simplified, was_simplified = simplify_text(raw_text)
    translated_native, error = translate_staff_to_native(simplified, lang_code)
    
    if not translated_native:
        translated_native = raw_text

    return jsonify({
        "original": raw_text,
        "simplified": simplified,
        "was_simplified": was_simplified,
        "translated": translated_native,
        "lang": lang_name,
        "urgent": False,
        "warning": error
    })

@app.route("/api/translate_patient", methods=["POST"])
@login_required
def translate_patient():
    data = request.get_json() or {}
    raw_text = data.get("text", "").strip()
    if not raw_text:
        return jsonify({"error": "No text provided"}), 400

    lang_code = session.get("lang_code", "ta")
    lang_name = session.get("lang", "Tamil")

    english_translation, native_script, error = translate_patient_input(raw_text, lang_code)
    triage = evaluate_medical_triage(raw_text, english_translation, lang_code)

    return jsonify({
        "original": raw_text,
        "native": native_script,
        "translated": english_translation,
        "lang": lang_name,
        "symptom_detected": triage["symptom_detected"],
        "is_negative": triage["is_negative"],
        "medical_alert": triage["medical_alert"],
        "warning": error
    })

@app.route("/api/simplify", methods=["POST"])
@login_required
def simplify_endpoint():
    data = request.get_json() or {}
    text = data.get("text", "")
    simplified, changed = simplify_text(text)
    return jsonify({"simplified": simplified, "changed": changed})

@app.route("/api/session_status")
@login_required
def session_status():
    return jsonify({
        "active": session.get("active", False),
        "context": session.get("context"),
        "lang": session.get("lang"),
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(debug=False, host="0.0.0.0", port=port)
