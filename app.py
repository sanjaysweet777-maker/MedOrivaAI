import json
import logging
import os
import re
import uuid
from datetime import datetime, timezone
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from flask_login import LoginManager, UserMixin, current_user, login_required, login_user, logout_user
from translator import LANGUAGES, patient_translation, staff_translation

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
# CANONICAL LANGUAGE ALIAS REGISTRY (All 9 MVP Languages + Extras)
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
    "pa": ("Punjabi", "pa"), "punjabi": ("Punjabi", "pa"),
    "gu": ("Gujarati", "gu"), "gujarati": ("Gujarati", "gu"),
}

def get_canonical_language(raw_lang, raw_code=None):
    """Resolves arbitrary display strings or codes to canonical (Name, Code)."""
    if raw_code and str(raw_code).strip().lower() in CANONICAL_LANGUAGES:
        return CANONICAL_LANGUAGES[str(raw_code).strip().lower()]
    
    if raw_lang:
        # Extract first word to cleanly strip brackets like 'Tamil (தமிழ்)'
        first_token = re.split(r'[\s\(\-_/]', str(raw_lang).strip())[0].lower()
        if first_token in CANONICAL_LANGUAGES:
            return CANONICAL_LANGUAGES[first_token]
            
    return ("Tamil", "ta")

# ============================================================
# MULTILINGUAL NEGATION TOKENS (All 9 MVP Languages)
# ============================================================
NEGATION_TOKENS_BY_LANG = {
    "Tamil": {"illai", "illa", "kidayathu", "illamal", "vendam", "thevai illai", "இல்லை", "கிடையாது", "வேண்டாம்"},
    "Hindi": {"nahi", "nahin", "na", "mat", "नहीं", "ना", "मत"},
    "Malayalam": {"illa", "alla", "illaathe", "venda", "aavashyamilla", "ഇല്ല", "അല്ല", "വേണ്ട"},
    "Polish": {"nie", "brak", "bez", "ani"},
    "Arabic": {"la", "kalla", "laysa", "ma", "mush", "lan", "lam", "لا", "كلا", "ليس", "ما", "مش"},
    "Urdu": {"nahi", "nahin", "na", "mat", "nhi", "نہیں", "نہ", "مت"},
    "Bengali": {"na", "nei", "noi", "noy", "না", "নেই", "নয়"},
    "Somali": {"maya", "ma", "maha", "malihi", "ha", "ma jiro"},
    "Romanian": {"nu", "nici", "fara", "fără"},
    "Punjabi": {"nahi", "nhi", "na", "nahin", "ਨਹੀਂ", "ਨਾ"},
    "Gujarati": {"nathi", "na", "નથી", "ના"}
}

def normalize_phrase(text):
    """Strips punctuation, normalizes unicode, and collapses whitespace."""
    if not text:
        return ""
    cleaned = re.sub(r'[^\w\s]', ' ', str(text), flags=re.UNICODE).lower()
    return " ".join(cleaned.split())

# ============================================================
# SCHEMA-VALIDATED RULE DICTIONARY LOADER
# ============================================================
RULES_DICT_PATH = os.path.join(BASE_DIR, "rules_dictionary.json")

def load_rules_data(filepath):
    if not os.path.exists(filepath):
        logger.warning("Rules file not found at %s", filepath)
        return {}
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            raw = json.load(f)
        
        # Support both {"rules_by_language": {...}} and flat {...}
        rules_dict = raw.get("rules_by_language", raw) if isinstance(raw, dict) else {}
        
        normalized = {}
        for lang_key, rules_list in rules_dict.items():
            if lang_key in {"system", "version"}:
                continue
            canonical_name, _ = get_canonical_language(lang_key)
            if isinstance(rules_list, list):
                normalized[canonical_name] = rules_list
                
        logger.info("Loaded verified rules for %d languages.", len(normalized))
        return normalized
    except Exception as e:
        logger.error("Failed to load rules from %s: %s", filepath, e)
        return {}

RULES_DATA = load_rules_data(RULES_DICT_PATH)

# ============================================================
# LOGIN & SESSION SECURITY
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
        return jsonify({"error": "Unauthorized", "message": "Session expired."}), 401
    return redirect(url_for('login', next=request.path))

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

# ============================================================
# API ENDPOINTS
# ============================================================
@app.route("/api/contact", methods=["POST"])
def submit_contact():
    data = request.get_json() or {}
    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    org = (data.get("organization") or data.get("org") or "").strip()
    message = data.get("message", "").strip()

    if not name or not email or not message:
        return jsonify({"status": "error", "message": "All fields are required."}), 400

    inquiry_record = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "name": name,
        "email": email,
        "organization": org,
        "message": message,
        "status": "pending_pilot_review"
    }

    # Persist inquiry to append-only storage
    inquiries_file = os.path.join(BASE_DIR, "contact_inquiries.jsonl")
    try:
        with open(inquiries_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(inquiry_record, ensure_ascii=False) + "\n")
        logger.info("Contact inquiry stored successfully: %s", inquiry_record["id"])
    except Exception as e:
        logger.error("Failed to persist contact inquiry: %s", e)
        return jsonify({"status": "error", "message": "Unable to save inquiry. Please try again later."}), 500

    return jsonify({
        "status": "ok",
        "message": "Inquiry received. Our practice pilot team will contact you within 24 hours.",
        "reference_id": inquiry_record["id"][:8]
    }), 200

@app.route("/api/ping", methods=["GET"])
def ping():
    return jsonify({"status": "ok", "service": "MedOriva AI", "healthy": True}), 200

@app.route("/healthz", methods=["GET"])
def healthz():
    return jsonify({"status": "ok"}), 200

@app.route("/api/start_session", methods=["POST"])
@login_required
def start_session():
    data = request.get_json() or {}
    reset_translation_session()
    
    raw_context = data.get("context", "Reception")
    context_key = "Reception"
    for k in CONTEXT_PROMPTS.keys():
        if k.lower() in raw_context.lower():
            context_key = k
            break

    raw_lang = data.get("lang", "Tamil")
    raw_code = data.get("lang_code") or data.get("code")
    canonical_lang, canonical_code = get_canonical_language(raw_lang, raw_code)

    session["session_id"] = str(uuid.uuid4())[:8]
    session["context"] = context_key
    session["lang"] = canonical_lang
    session["lang_code"] = canonical_code
    session["active"] = True

    prompts = CONTEXT_PROMPTS.get(context_key, CONTEXT_PROMPTS["Reception"])

    return jsonify({
        "status": "ok",
        "session_id": session["session_id"],
        "prompts": prompts,
        "context": session["context"],
        "lang": session["lang"],
        "lang_code": session["lang_code"],
        "code": session["lang_code"]
    })

@app.route("/api/end_session", methods=["POST"])
@login_required
def end_session():
    reset_translation_session()
    return jsonify({"status": "ok"})

@app.route("/api/simplify", methods=["POST"])
@login_required
def simplify_endpoint():
    data = request.get_json() or {}
    text = data.get("text", "")
    simplified, changed = simplify_text(text)
    return jsonify({"simplified": simplified, "changed": changed})

@app.route("/api/translate_staff", methods=["POST"])
@login_required
def translate_staff():
    data = request.get_json() or {}
    raw_text = data.get("text", "").strip()
    if not raw_text:
        return jsonify({"error": "No text provided"}), 400

    lang_code = session.get("lang_code", "ta")
    lang_name = session.get("lang", "Tamil")

    simplified_text, was_simplified = simplify_text(raw_text)
    text_to_translate = simplified_text if was_simplified else raw_text

    res = staff_translation(text_to_translate, lang_code)

    return jsonify({
        "original": raw_text,
        "simplified": simplified_text,
        "was_simplified": was_simplified,
        "translated": res.text,
        "lang": lang_name,
        "urgent": False,
        "warning": res.warning
    })

@app.route("/api/translate_patient", methods=["POST"])
@login_required
def translate_patient():
    data = request.get_json() or {}
    raw_text = data.get("text", "").strip()
    if not raw_text:
        return jsonify({"error": "No text provided"}), 400

    canonical_lang, lang_code = get_canonical_language(
        session.get("lang", "Tamil"),
        session.get("lang_code", "ta")
    )

    norm_input = normalize_phrase(raw_text)
    input_tokens = set(norm_input.split())
    rules_for_lang = RULES_DATA.get(canonical_lang, [])

    # Identify if patient input contains any known negation token for this language
    lang_negations = NEGATION_TOKENS_BY_LANG.get(canonical_lang, set())
    has_negation_in_input = bool(input_tokens & lang_negations)

    matched_rule = None

    # Step 1: Strict exact phrase matching only.
    # A rule will only match if the normalized utterance EXACTLY equals a registered match phrase.
    # Partial fragments are rejected to prevent erasing clinical words, durations, or negations.
    for rule in rules_for_lang:
        intent = rule.get("intent", "").upper()
        is_negative_intent = any(neg in intent for neg in ["_NO", "NOT_", "NEGATE_", "NO_PAIN"])

        # Prevent affirmative rules from matching utterances containing negation
        if has_negation_in_input and not is_negative_intent:
            continue

        for candidate in rule.get("input_matches", []):
            norm_candidate = normalize_phrase(candidate)
            if norm_input == norm_candidate:
                matched_rule = rule
                break
        if matched_rule:
            break

    if matched_rule:
        intent = matched_rule.get("intent", "").upper()
        is_negative = any(neg in intent for neg in ["_NO", "NOT_", "NEGATE_", "NO_PAIN"])
        symptom_detected = "SYMPTOM_" in intent
        medical_alert = bool(symptom_detected and not is_negative)

        return jsonify({
            "original": raw_text,
            "native": matched_rule["native_script"],
            "translated": matched_rule["english_review"],
            "lang": canonical_lang,
            "symptom_detected": symptom_detected,
            "is_negative": is_negative,
            "medical_alert": medical_alert,
            "warning": None,
            "match_type": "verified_rule"
        })

    # Step 2: Fallback to translator engine whenever the utterance contains additional words,
    # anatomical terms, durations, or unmapped expressions.
    res = patient_translation(raw_text, lang_code)
    medical_alert = bool(res.symptom and not res.is_negative)

    return jsonify({
        "original": raw_text,
        "native": res.native,
        "translated": res.text,
        "lang": canonical_lang,
        "symptom_detected": res.symptom,
        "is_negative": res.is_negative,
        "medical_alert": medical_alert,
        "warning": res.warning,
        "match_type": "translation_engine"
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(debug=False, host="0.0.0.0", port=port)
