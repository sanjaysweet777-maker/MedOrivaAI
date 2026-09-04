"""
MedOriva AI Ltd — Multilingual Communication Support Backend
Classification: Strictly Confidential / Non-Medical Device
Purpose: Ephemeral, structured multilingual communication facilitation for NHS-style healthcare environments.
Regulatory Position: Administrative communication tool. Does not provide clinical diagnosis,
triage scoring, or clinical treatment advice.
"""

from datetime import timedelta
import os
import re
import secrets
import uuid

from clinical_phrases import (
    AFFIRMATION_PATTERNS,
    DURATION_PATTERNS,
    GUIDED_PROMPTS,
    MULTI_LANG_SYMPTOMS,
    NEGATION_PATTERNS,
    PATIENT_CANONICAL_RESPONSES,
    SIMPLIFY_RULES,
    URGENT_SYMPTOMS_CONFIG,
    extract_symptom,
    synthesize_staff_question,
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
app.secret_key = os.environ.get("SECRET_KEY", "medoriva-clinical-mvp-secret-2026")

app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

# ============================================================
# REGULATORY & INFORMATION GOVERNANCE SAFEGUARDS (UK GDPR)
# ============================================================

NON_CLINICAL_DISCLAIMER = (
    "MedOriva AI is an administrative communication facilitation tool. "
    "It is not a medical device and does not provide clinical diagnosis, triage scoring, "
    "or treatment advice."
)

ALERT_SYMPTOM_POSITIVE = (
    "Symptom-related phrase identified; staff to follow practice communication protocol."
)
ALERT_SYMPTOM_NEGATIVE = (
    "Patient reports no symptom; staff noted per practice communication protocol."
)

@app.after_request
def set_security_and_governance_headers(response):
    """
    Enforces UK GDPR data-minimisation and zero-retention principles.
    Prevents browsers, proxies, and intermediate nodes from caching ephemeral consultation strings.
    """
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    return response

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

# Static prompt translation cache (staff standard questions only — zero patient payload retention)
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
    if target_lang != "en" and normalize_text(text) == normalize_text(result):
        return
    cache_key = f"{normalize_text(text)}_{target_lang}"
    translation_cache[cache_key] = result

def reset_translation_session():
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
# PARSING ENGINE (AFFIRMATIONS, NEGATIONS, DURATIONS)
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
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return match.expand(replacement)
    return None

def evaluate_medical_triage(original_text, english_text, lang_code):
    """
    Keyword-based staff notification generator.
    Provides non-clinical visual alerts to assist staff workflow.
    Strictly non-diagnostic and non-prescriptive.
    """
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
            
    # Positive flag triggered only when phrase is present and unnegated
    medical_alert = bool(is_urgent and not is_neg)
    
    # Generate non-clinical safe word notification for practice staff
    if medical_alert:
        staff_notification = ALERT_SYMPTOM_POSITIVE
    elif detected_symptom and is_neg:
        staff_notification = ALERT_SYMPTOM_NEGATIVE
    else:
        staff_notification = None
    
    return {
        "symptom_detected": detected_symptom,
        "is_negative": is_neg,
        "medical_alert": medical_alert,
        "staff_notification": staff_notification
    }

# ============================================================
# TRANSLATION HANDLERS (ALL 9 CORE LANGUAGES)
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
        if res and res.strip().lower() != text.strip().lower():
            return res
    except Exception:
        pass

    return ""

def translate_staff_to_native(text, target_lang_code):
    if not text:
        return "", None

    target = get_clean_lang_code(target_lang_code)

    # 1. Deterministic Synthesizer check
    synthesized = synthesize_staff_question(text, target)
    if synthesized:
        set_cached_translation(text, target, synthesized)
        return synthesized, None

    # 2. Check Cache
    cached = get_cached_translation(text, target)
    if cached and normalize_text(cached) != normalize_text(text):
        return cached, None

    # 3. Dynamic Translation
    translated = execute_online_translation(text, "en", target)
    if translated and normalize_text(translated) != normalize_text(text):
        set_cached_translation(text, target, translated)
        return translated, None

    # 4. Fallback: Identify anatomical symptom and form question
    _, sym_eng, sym_native = extract_symptom(text, target)
    if sym_native:
        return f"{sym_native}?", None

    return text, "Translation unavailable"

def translate_patient_input(text, lang_code):
    """
    Translates Patient input (Romanized, Thanglish, or Native script) across all 9 languages into:
    1. Clean English for Staff
    2. Pure Native Script for UI display
    """
    if not text:
        return "", "", None

    target_clean = get_clean_lang_code(lang_code)

    # If already typed in pure Native Script
    if is_native_script(text):
        english_trans = execute_online_translation(text, target_clean, "en")
        if not english_trans:
            _, sym_eng, _ = extract_symptom(text, target_clean)
            english_trans = f"Reported: {sym_eng}" if sym_eng else text
        return english_trans, text, None

    # Parse components from Romanized/phonetic text (e.g., Thanglish)
    has_affirmation = detect_affirmation(text, target_clean)
    has_negation = detect_negation(text, target_clean)
    duration_str = extract_duration(text)
    sym_key, sym_english, sym_native = extract_symptom(text, target_clean)

    # 1. Check Deterministic Canonical Patient Response Registry
    if sym_key and target_clean in PATIENT_CANONICAL_RESPONSES:
        lang_responses = PATIENT_CANONICAL_RESPONSES[target_clean]
        if sym_key in lang_responses:
            mode = "neg" if has_negation else "pos"
            base_english, base_native = lang_responses[sym_key][mode]

            # Append affirmations
            if has_affirmation and not has_negation:
                base_english = f"Yes, {base_english.lower()}"
                affirm_word = AFFIRMATION_PATTERNS.get(target_clean, ["Yes"])[0]
                base_native = f"{affirm_word}, {base_native}"

            # Append duration
            if duration_str and not has_negation:
                base_english = base_english.replace("I have", "I have had") + f" {duration_str}"

            return base_english, base_native, None

    # 2. Reconstruct dynamically if symptom is recognized
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
        reconstructed_native = execute_online_translation(constructed_english, "en", target_clean)
        if not reconstructed_native:
            reconstructed_native = sym_native

        return constructed_english, reconstructed_native, None

    # 3. Final Fallback for unmapped text
    english_trans = execute_online_translation(text, "auto", "en")
    if not english_trans:
        english_trans = text

    native_trans = execute_online_translation(english_trans, "en", target_clean)
    if not native_trans:
        native_trans = text

    return english_trans, native_trans, None

# ============================================================
# PUBLIC & WORKSPACE ROUTES
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
            data = request.get_json() or {}
            email = str(data.get('email') or data.get('username') or '').strip().lower()
            password = str(data.get('password') or '').strip()
        else:
            email = str(request.form.get('email') or request.form.get('username') or '').strip().lower()
            password = str(request.form.get('password') or '').strip()

        if email == DEMO_EMAIL.lower() and password == DEMO_PASSWORD:
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
    session.clear()
    return redirect(url_for('login'))

@app.route("/api/contact", methods=["POST"])
def submit_contact():
    data = request.get_json() or {}
    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    message = data.get("message", "").strip()

    if not name or not email or not message:
        return jsonify({"status": "error", "message": "All required fields must be completed."}), 400

    return jsonify({
        "status": "ok",
        "message": "Thank you. Your practice pilot inquiry has been received. Our team will contact you within 24 hours."
    }), 200

# ============================================================
# HEALTH CHECKS & REGULATORY AUDIT ENDPOINTS
# ============================================================

@app.route("/api/ping", methods=["GET"])
def ping():
    return jsonify({
        "status": "ok",
        "service": "MedOriva AI",
        "healthy": True,
        "regulatory_status": "Non-Medical Device (Administrative Communication Support)",
        "governance": "UK GDPR Data Minimisation Enforced",
        "disclaimer": NON_CLINICAL_DISCLAIMER
    }), 200

@app.route("/healthz", methods=["GET"])
def healthz():
    return jsonify({"status": "ok"}), 200

# ============================================================
# CLINICAL TRANSLATION & SESSION APIS (Protected)
# ============================================================

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
            "disclaimer": NON_CLINICAL_DISCLAIMER
        })
    except Exception as e:
        return jsonify({"status": "error", "error": f"Could not start session: {str(e)}"}), 500

@app.route("/api/end_session", methods=["POST"])
@login_required
def end_session():
    reset_translation_session()
    session.clear()
    return jsonify({
        "status": "ok",
        "message": "Session closed. Active memory purged under data-minimisation controls."
    })

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
        "warning": error,
        "disclaimer": NON_CLINICAL_DISCLAIMER
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
        "staff_notification": triage["staff_notification"],
        "warning": error,
        "disclaimer": NON_CLINICAL_DISCLAIMER
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
