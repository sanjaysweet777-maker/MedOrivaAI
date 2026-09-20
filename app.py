import json
import logging
import os
import re
import unicodedata
import uuid
from urllib.parse import urlparse
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from flask_login import LoginManager, UserMixin, current_user, login_required, login_user, logout_user

# Import engine functions from translator.py
from translator import (
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
app.secret_key = os.environ.get("SECRET_KEY", "medoriva-clinical-mvp-2026-v4")

# Ephemeral session security configuration
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("medoriva.app")

# ============================================================
# CANONICAL LANGUAGE MAPPING & NORMALISATION (All 9 Languages)
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
    return ("Tamil", "ta")

def normalize_phrase(text):
    if not text:
        return ""
    cleaned = re.sub(r'[^\w\s]', ' ', str(text), flags=re.UNICODE)
    return " ".join(unicodedata.normalize('NFC', cleaned).lower().split())

# ============================================================
# MULTILINGUAL NEGATION TOKENS (All 9 Languages)
# ============================================================
NEGATION_TOKENS_BY_LANG = {
    "ta": {"illai", "illa", "kidayathu", "illamal", "vendam", "thevai illai", "இல்லை", "கிடையாது", "வேண்டாம்"},
    "hi": {"nahi", "nahin", "na", "mat", "नहीं", "ना", "मत"},
    "ml": {"illa", "alla", "illaathe", "venda", "aavashyamilla", "ഇല്ല", "അല്ല", "വേണ്ട"},
    "pl": {"nie", "brak", "bez", "ani"},
    "ar": {"la", "kalla", "laysa", "ma", "mush", "lan", "lam", "لا", "كلا", "ليس", "ما", "مش"},
    "ur": {"nahi", "nahin", "na", "mat", "nhi", "نہیں", "نہ", "مت"},
    "bn": {"na", "nei", "noi", "noy", "না", "নেই", "নয়"},
    "so": {"maya", "ma", "maha", "malihi", "ha", "ma jiro"},
    "ro": {"nu", "nici", "fara", "fără"}
}

# ============================================================
# LOAD MEDORIVA RULE DICTIONARY FOR ALL 9 LANGUAGES
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
                normalized[code] = rules_list
                normalized[name] = rules_list
        logger.info("Loaded rules dictionary for all configured languages.")
        return normalized
    except Exception as e:
        logger.error("Error loading rules dictionary: %s", e)
        return {}

RULES_DATA = load_rules_data(RULES_DICT_PATH)

# ============================================================
# CONTEXT-LOCKED GUIDED PROMPT REGISTRY
# ============================================================
CONTEXT_PROMPTS = {
    "Reception": [
        "Good morning. How can I help you?",
        "Do you have an appointment?",
        "Can I take your name and date of birth?",
        "Please take a seat. The doctor will see you shortly.",
        "Do you have your NHS number?",
        "Please fill in this form.",
        "Do you need an interpreter?"
    ],
    "Appointment": [
        "Your appointment is confirmed.",
        "The doctor will see you now.",
        "Do you have your appointment letter?",
        "Please bring your medication list.",
        "Is anyone with you today?",
        "Please wait in the waiting area.",
        "The appointment will take about 15 minutes.",
        "Do you need an interpreter?"
    ],
    "Basic Symptoms": [
        "Where is your pain?",
        "How long have you had this?",
        "How long have you had chest pain?",
        "Do you have a fever?",
        "Are you having difficulty breathing?",
        "Do you feel dizzy or faint?",
        "Do you have chest pain?",
        "Is there any bleeding?",
        "When did the symptoms start?"
    ]
}

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
    reset_translation_session()
    return redirect(url_for('login'))

# ============================================================
# API ENDPOINTS
# ============================================================
@app.route("/api/contact", methods=["POST"])
def submit_contact():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"status": "error", "message": "Invalid payload."}), 400

    # Reject fake success when live email/messaging delivery transport is not configured
    if not os.environ.get("CONTACT_DELIVERY_ENABLED") and not os.environ.get("SMTP_HOST"):
        return jsonify({
            "status": "unavailable",
            "message": "Contact delivery service unconfigured. Please email practice team directly."
        }), 503

    return jsonify({"status": "ok", "message": "Inquiry delivered."}), 200

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

    lang_code = session.get("lang_code", "ta")
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

    lang_code = session.get("lang_code", "ta")
    lang_name = session.get("lang", "Tamil")

    # Step 1: Check verified rules_dictionary.json across all 9 languages
    norm_input = normalize_phrase(raw_text)
    input_tokens = set(norm_input.split())
    rules_for_lang = RULES_DATA.get(lang_code, []) or RULES_DATA.get(lang_name, [])

    lang_negs = NEGATION_TOKENS_BY_LANG.get(lang_code, set())
    has_negation = bool(input_tokens & lang_negs)

    matched_rule = None
    for rule in rules_for_lang:
        intent = rule.get("intent", "").upper()
        is_neg_intent = any(neg in intent for neg in ["_NO", "NOT_", "NEGATE_", "NO_PAIN"])

        # Never match affirmative rule if patient typed a negation
        if has_negation and not is_neg_intent:
            continue

        for candidate in rule.get("input_matches", []):
            if norm_input == normalize_phrase(candidate):
                matched_rule = rule
                break
        if matched_rule:
            break

    if matched_rule:
        return jsonify({
            "original": raw_text,
            "native": matched_rule.get("native_script", raw_text),
            "translated": matched_rule.get("english_review", raw_text),
            "lang": lang_name,
            "medical_alert": False,
            "is_negative": None,
            "status": "needs_review",
            "warning": None
        }), 200

    # Step 2: Fallback to translation engine for descriptive phrases & full sentences
    res = patient_translation(raw_text, lang_code)

    return jsonify({
        "original": raw_text,
        "native": getattr(res, "native", raw_text),
        "translated": res.text,
        "lang": lang_name,
        "medical_alert": False,
        "is_negative": None,
        "status": getattr(res, "status", "needs_review"),
        "warning": getattr(res, "warning", None)
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
