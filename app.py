"""MedOriva AI: demonstration of multilingual communication support."""
import os
import re
import secrets
import uuid
from datetime import timedelta, datetime, timezone
from urllib.parse import urlsplit
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from flask_login import LoginManager, UserMixin, current_user, login_required, login_user, logout_user
from clinical_phrases import GUIDED_PROMPTS
from translation_engine import LANGUAGES, STAFF_LOOKUP, normalise, staff_translation, patient_translation, configured_key, online

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
app.config.update(SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE='Lax',
    SESSION_COOKIE_SECURE=os.environ.get('COOKIE_SECURE','false').lower()=='true',
    MAX_CONTENT_LENGTH=16384, PERMANENT_SESSION_LIFETIME=timedelta(minutes=30))
DEMO_EMAIL = os.environ.get('DEMO_EMAIL','demo@medoriva.com')
DEMO_PASSWORD = os.environ.get('DEMO_PASSWORD','medoriva2026')
DISCLAIMER = 'Demonstration only. Use fictional information. Translation supports communication and does not establish clinical meaning, urgency or patient understanding.'
login_manager = LoginManager(app)
login_manager.login_view = 'login'
class User(UserMixin):
    def __init__(self,email): self.id = email
@login_manager.user_loader
def load_user(user_id):
    return User(user_id) if user_id == DEMO_EMAIL else None
@login_manager.unauthorized_handler
def unauthorized():
    if request.path.startswith('/api/'):
        return jsonify(error='Session expired. Please sign in again.'),401
    return redirect(url_for('login'))
@app.before_request
def request_safeguards():
    if request.method == 'POST':
        origin = request.headers.get('Origin')
        if origin and urlsplit(origin).netloc != request.host:
            return jsonify(error='Cross-origin request rejected.'),403
        if request.path.startswith('/api/') and not request.is_json:
            return jsonify(error='JSON request required.'),415
        if request.is_json and not isinstance(request.get_json(silent=True),dict):
            return jsonify(error='A JSON object is required.'),400
@app.after_request
def headers(response):
    response.headers.update({'Cache-Control':'no-store','X-Content-Type-Options':'nosniff','X-Frame-Options':'DENY','Referrer-Policy':'same-origin'})
    return response
@app.route('/')
def index(): return render_template('landing.html', year=datetime.now(timezone.utc).year)
@app.route('/portal')
@login_required
def portal(): return render_template('index.html')
@app.route('/login',methods=['GET','POST'])
def login():
    if current_user.is_authenticated: return redirect(url_for('portal'))
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        email, password = data.get('email',''),data.get('password','')
        if isinstance(email,str) and isinstance(password,str) and email.strip().lower()==DEMO_EMAIL.lower() and secrets.compare_digest(password,DEMO_PASSWORD):
            session.clear()
            login_user(User(DEMO_EMAIL))
            session.permanent = True
            return jsonify(status='ok',redirect='/portal') if request.is_json else redirect(url_for('portal'))
        if request.is_json: return jsonify(error='Invalid email or password'),401
        flash('Invalid email or password')
    return render_template('login.html',public_demo=DEMO_PASSWORD=='medoriva2026' and DEMO_EMAIL=='demo@medoriva.com')
@app.route('/logout')
@login_required
def logout():
    logout_user(); session.clear()
    return redirect(url_for('login'))
@app.route('/healthz')
def healthz(): return jsonify(status='ok')
@app.route('/api/ping')
def ping(): return jsonify(status='ok',service='MedOriva AI',disclaimer=DISCLAIMER)
@app.route('/api/contact',methods=['POST'])
def contact():
    return jsonify(error='Online enquiries are not connected. Please use the contact email displayed on this website.'),503
@app.route('/api/start_session',methods=['POST'])
@login_required
def start_session():
    data=request.get_json()
    context,code=data.get('context'),data.get('lang_code')
    if not isinstance(code,str) or code not in LANGUAGES or not isinstance(context,str) or context not in GUIDED_PROMPTS:
        return jsonify(error='Select a supported context and language.'),400
    session.update(session_id=str(uuid.uuid4()),context=context,lang_code=code,lang=LANGUAGES[code],active=True)
    prompts=[p.replace('How long do you have pain?','How long have you had pain?').replace('How long do you have chest pain?','How long have you had chest pain?') for p in GUIDED_PROMPTS[context] if '[time]' not in p]
    return jsonify(status='ok',session_id=session['session_id'],context=context,lang=session['lang'],prompts=prompts,
        prepared_prompts=[p for p in prompts if normalise(p) in STAFF_LOOKUP],provider_configured=bool(configured_key()),disclaimer=DISCLAIMER)
@app.route('/api/translation_check', methods=['POST'])
@login_required
def translation_check():
    code = request.get_json().get('lang_code', 'ta')
    if not isinstance(code,str) or code not in LANGUAGES:
        return jsonify(error='Select a supported language.'),400
    # Fixed fictional text only; this deliberately bypasses the prepared lookup.
    result = online('Do you have an appointment?', 'en', code)
    return jsonify(configured=bool(configured_key()),connected=result.source=='google_cloud',
        message='Translation service connected.' if result.source=='google_cloud' else result.warning,
        error_code=result.error_code,language=LANGUAGES[code],
        translated=result.text, build='compact-workspace-v2')

@app.route('/api/end_session',methods=['POST'])
@login_required
def end_session():
    for key in ('session_id','context','lang_code','lang','active'): session.pop(key,None)
    return jsonify(status='ok',message='Conversation closed. This browser view can now be cleared.')
@app.route('/api/session_status')
@login_required
def session_status():
    return jsonify(active=session.get('active',False),context=session.get('context'),lang=session.get('lang'))
def validate_text():
    if not session.get('active'): return None,(jsonify(error='Start a session first.'),409)
    text=request.get_json().get('text')
    if not isinstance(text,str) or not text.strip() or len(text)>2000:
        return None,(jsonify(error='Enter between 1 and 2,000 characters.'),400)
    return text.strip(),None
@app.route('/api/translate_staff',methods=['POST'])
@login_required
def translate_staff():
    text,error=validate_text()
    if error is not None: return error
    result=staff_translation(text,session['lang_code'])
    return jsonify(original=text,simplified=text,was_simplified=False,translated=result.text,lang=session['lang'],
        status=result.status,translation_source=result.source,warning=result.warning,error_code=result.error_code,urgent=False,disclaimer=DISCLAIMER)
@app.route('/api/translate_patient',methods=['POST'])
@login_required
def translate_patient():
    text,error=validate_text()
    if error is not None: return error
    result=patient_translation(text,session['lang_code'])
    return jsonify(original=text,native=result.native,translated=result.text,lang=session['lang'],status=result.status,
        translation_source=result.source,warning=result.warning,error_code=result.error_code,symptom_detected=None,is_negative=None,medical_alert=False,
        staff_notification=None,disclaimer=DISCLAIMER)
@app.route('/api/simplify',methods=['POST'])
@login_required
def simplify():
    text,error=validate_text()
    if error is not None: return error
    # Suggestions only; staff must edit/approve before a changed sentence is translated.
    suggestion=text
    for source,target in ((r'\bprior to\b','before'),(r'\bapproximately\b','about'),(r'\bcommence\b','start')):
        suggestion=re.sub(source,target,suggestion,flags=re.I)
    return jsonify(simplified=suggestion,changed=suggestion!=text)
if __name__=='__main__':
    app.run(host='0.0.0.0',port=int(os.environ.get('PORT',10000)),debug=False)
