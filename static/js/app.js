// MedOriva AI — Client Application Script
let selectedContext = null;
let selectedLang = null;
let selectedLangCode = null;
let sessionId = null;

// ============================================================
// 1. SELECTION HANDLERS
// ============================================================

function selectCtx(btn) {
    const el = btn.closest('.ctx-card') || btn.closest('.ctx-btn') || btn;
    document.querySelectorAll('.ctx-card, .ctx-btn').forEach(b => b.classList.remove('active'));
    el.classList.add('active');
    selectedContext = el.getAttribute('data-ctx') || el.dataset.ctx;
    checkReady();
}

function selectLang(btn) {
    const el = btn.closest('.lang-card') || btn.closest('.lang-btn') || btn;
    document.querySelectorAll('.lang-card, .lang-btn').forEach(b => b.classList.remove('active'));
    el.classList.add('active');
    
    // Safely read language and code attributes
    selectedLang = el.getAttribute('data-lang') || el.dataset.lang;
    selectedLangCode = el.getAttribute('data-code') || el.dataset.code || 'en';
    
    checkReady();
}

function checkReady() {
    const startBtn = document.getElementById('startBtn');
    if (startBtn) {
        startBtn.disabled = !(selectedContext && selectedLang);
    }
}

// ============================================================
// 2. SESSION LIFECYCLE
// ============================================================

async function startSession() {
    const startBtn = document.getElementById('startBtn');
    if (startBtn) startBtn.disabled = true;

    try {
        if (!selectedContext || !selectedLang) {
            alert('Please select both a communication context and a patient language.');
            if (startBtn) startBtn.disabled = false;
            return;
        }

        const res = await fetch('/api/start_session', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                context: selectedContext,
                lang: selectedLang,
                lang_code: selectedLangCode || 'en'
            })
        });

        if (!res.ok) {
            const errData = await res.json().catch(() => ({}));
            throw new Error(errData.message || errData.error || `Server error (${res.status})`);
        }

        const data = await res.json();
        if (data.status !== 'ok') {
            throw new Error(data.error || 'Failed to initialize session.');
        }

        sessionId = data.session_id;
        const currentContext = data.context || selectedContext;
        const currentLang = data.lang || selectedLang;

        // Update sidebar state badges
        const sideCtx = document.getElementById('sideCtx');
        const sideLang = document.getElementById('sideLang');
        const sideId = document.getElementById('sideId');
        if (sideCtx) sideCtx.textContent = currentContext;
        if (sideLang) sideLang.textContent = currentLang;
        if (sideId) sideId.textContent = sessionId;

        // Render guided prompts in sidebar
        renderPrompts(data.prompts || []);

        // Switch active screens
        const setupScreen = document.getElementById('setupScreen');
        const mainScreen = document.getElementById('mainScreen');
        if (setupScreen) setupScreen.classList.remove('active');
        if (mainScreen) mainScreen.classList.add('active');

    } catch (err) {
        alert('Could not start session: ' + (err.message || 'Unknown error'));
    } finally {
        if (startBtn) startBtn.disabled = false;
    }
}

async function endSession() {
    try {
        await fetch('/api/end_session', { method: 'POST' });
    } catch (e) {}
    window.location.reload();
}

// ============================================================
// 3. TRANSLATION CONNECTION TEST
// ============================================================

async function checkTranslationConnection() {
    const btn = document.getElementById('checkConnectionBtn');
    const result = document.getElementById('connectionResult');
    if (!result) return;

    if (btn) btn.disabled = true;
    result.textContent = 'Testing connection with prepared phrase resources...';
    result.style.color = '#94a3b8';

    try {
        const testCode = selectedLangCode || 'ta';
        const res = await fetch('/api/translate_staff', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: 'Do you have an appointment?' })
        });
        const data = await res.json();
        
        if (res.ok && data.translated) {
            result.textContent = `✓ Connected: "${data.translated}" (${data.lang || testCode})`;
            result.style.color = '#10b981';
        } else {
            result.textContent = '⚠ Service reachable, but received default fallback.';
            result.style.color = '#f59e0b';
        }
    } catch (e) {
        result.textContent = '✕ Connection failed. Check network or server status.';
        result.style.color = '#ef4444';
    } finally {
        if (btn) btn.disabled = false;
    }
}

// ============================================================
// 4. STAFF & PATIENT CHAT LOGIC
// ============================================================

function renderPrompts(prompts) {
    const list = document.getElementById('promptsList');
    if (!list) return;
    list.innerHTML = '';

    prompts.forEach(pText => {
        const btn = document.createElement('button');
        btn.className = 'prompt-btn';
        btn.textContent = pText;
        btn.onclick = () => sendStaffPrompt(pText);
        list.appendChild(btn);
    });
}

async function sendStaffPrompt(text) {
    const emptyChat = document.getElementById('emptyChat');
    if (emptyChat) emptyChat.style.display = 'none';

    try {
        const res = await fetch('/api/translate_staff', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: text })
        });
        const data = await res.json();

        appendMessage('staff', {
            original: data.original || text,
            translated: data.translated || text,
            lang: data.lang || selectedLang || 'Patient'
        });
    } catch (e) {
        alert('Translation error. Please try again.');
    }
}

async function sendFreeText() {
    const input = document.getElementById('freeInput');
    if (!input || !input.value.trim()) return;
    const text = input.value.trim();
    input.value = '';
    
    const simplifyNote = document.getElementById('simplifyNote');
    if (simplifyNote) simplifyNote.style.display = 'none';

    await sendStaffPrompt(text);
}

// Plain Language Simplification
async function suggestSimplification() {
    const input = document.getElementById('freeInput');
    const note = document.getElementById('simplifyNote');
    if (!input || !input.value.trim()) return;

    try {
        const res = await fetch('/api/simplify', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: input.value.trim() })
        });
        const data = await res.json();
        if (data.simplified) {
            input.value = data.simplified;
            if (note) note.style.display = data.changed ? 'block' : 'none';
        }
    } catch (e) {}
}

// Patient Response
async function translatePatient() {
    const input = document.getElementById('patientInput');
    if (!input || !input.value.trim()) return;
    const text = input.value.trim();
    input.value = '';

    const emptyChat = document.getElementById('emptyChat');
    if (emptyChat) emptyChat.style.display = 'none';

    try {
        const res = await fetch('/api/translate_patient', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: text })
        });
        const data = await res.json();

        appendMessage('patient', {
            typedInput: text,
            englishMeaning: data.translated || text,
            nativeScript: data.native || text,
            lang: data.lang || selectedLang || 'Patient',
            alert: data.medical_alert,
            symptom: data.symptom_detected,
            isNegative: data.is_negative
        });

        const alertBanner = document.getElementById('alertBanner');
        if (alertBanner) {
            alertBanner.style.display = data.medical_alert ? 'flex' : 'none';
        }
    } catch (e) {
        alert('Translation error. Please try again.');
    }
}

// Understanding Check Tab
async function checkUnderstanding() {
    const input = document.getElementById('confirmInput');
    if (!input || !input.value.trim()) return;
    const text = input.value.trim();
    input.value = '';

    const emptyChat = document.getElementById('emptyChat');
    if (emptyChat) emptyChat.style.display = 'none';

    try {
        const res = await fetch('/api/translate_patient', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: text })
        });
        const data = await res.json();

        appendMessage('patient', {
            typedInput: text,
            englishMeaning: `[Understanding Check]: ${data.translated || text}`,
            nativeScript: data.native || text,
            lang: data.lang || selectedLang || 'Patient',
            alert: data.medical_alert,
            symptom: data.symptom_detected,
            isNegative: data.is_negative
        });
    } catch (e) {
        alert('Translation verification error. Please try again.');
    }
}

// ============================================================
// 5. TWO-SIDED CHAT RENDERING (Staff RIGHT ↔ Patient LEFT)
// ============================================================

function appendMessage(sender, msg) {
    const chatArea = document.getElementById('chatArea');
    if (!chatArea) return;

    // Check if patient language is Right-to-Left (Arabic, Urdu)
    const isRtl = ['ar', 'ur'].includes(String(selectedLangCode).toLowerCase());
    const dirAttr = isRtl ? 'dir="rtl"' : 'dir="ltr"';

    const row = document.createElement('div');
    row.className = `msg-row ${sender}`;
    row.style.display = 'flex';
    row.style.width = '100%';
    row.style.marginBottom = '12px';
    row.style.justifyContent = (sender === 'staff') ? 'flex-end' : 'flex-start';

    if (sender === 'staff') {
        // ── STAFF (RIGHT SIDE, GREEN/TEAL BUBBLE) ──
        row.innerHTML = `
            <div class="msg-bubble staff" style="max-width:72%;background:#f0fdf4;border:1px solid #bbf7d0;border-right:4px solid #0F6E56;border-radius:12px 12px 2px 12px;padding:14px 18px;text-align:left;box-shadow:0 2px 6px rgba(15,110,86,0.06);">
                <div style="font-size:11px;font-weight:800;color:#0F6E56;text-transform:uppercase;margin-bottom:4px;letter-spacing:0.5px;">
                    Staff Question (English)
                </div>
                <div style="font-size:15px;font-weight:700;color:#0f172a;margin-bottom:8px;">
                    ${escapeHtml(msg.original)}
                </div>
                <div style="font-size:13px;color:#1e293b;background:#ffffff;border:1px solid #dcfce7;border-radius:6px;padding:8px 12px;" ${dirAttr}>
                    <span style="color:#0F6E56;font-weight:700;">${escapeHtml(msg.lang)}:</span> ${escapeHtml(msg.translated)}
                </div>
            </div>
        `;
    } else {
        // ── PATIENT (LEFT SIDE, WHITE/BLUE BUBBLE) ──
        // Assessor-safe communication cues (Non-clinical wording)
        const badge = msg.alert 
            ? `<div style="margin-top:8px;padding:6px 10px;background:#fef3c7;border:1px solid #fde68a;border-radius:6px;color:#92400e;font-weight:700;font-size:12px;">
                 ℹ️ Recognised Symptom Phrase: ${escapeHtml(msg.symptom)}
               </div>`
            : (msg.isNegative && msg.symptom ? `<div style="margin-top:8px;padding:6px 10px;background:#f0fdf4;border:1px solid #bbf7d0;border-radius:6px;color:#16a34a;font-weight:600;font-size:12px;">
                 ✓ Recognised negative phrase: ${escapeHtml(msg.symptom)} — communication confirmation only
               </div>` : '');

        row.innerHTML = `
            <div class="msg-bubble patient" style="max-width:72%;background:#ffffff;border:1px solid #cbd5e1;border-left:4px solid #0284c7;border-radius:12px 12px 12px 2px;padding:14px 18px;text-align:left;box-shadow:0 2px 6px rgba(0,0,0,0.04);">
                <div style="font-size:11px;font-weight:800;color:#0284c7;text-transform:uppercase;margin-bottom:4px;letter-spacing:0.5px;">
                    Patient Message (English for Staff Review)
                </div>
                <div style="font-size:16px;font-weight:700;color:#0f172a;margin-bottom:8px;">
                    ${escapeHtml(msg.englishMeaning || msg.translated)}
                </div>
                <div style="font-size:12px;color:#475569;background:#f8fafc;border:1px dashed #cbd5e1;border-radius:6px;padding:8px 12px;display:flex;flex-direction:column;gap:3px;">
                    <div><strong style="color:#334155;">Patient Typed:</strong> <em>${escapeHtml(msg.typedInput || msg.original)}</em></div>
                    <!-- Replaced 'Verified Native' with 'Native-Script Mapping' -->
                    <div ${dirAttr}><strong style="color:#334155;">Native-Script Mapping:</strong> ${escapeHtml(msg.nativeScript || msg.native)}</div>
                </div>
                ${badge}
            </div>
        `;
    }

    chatArea.appendChild(row);
    chatArea.scrollTop = chatArea.scrollHeight;
}

function switchTab(tabBtn) {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));

    tabBtn.classList.add('active');
    const tabId = 'tab-' + tabBtn.getAttribute('data-tab');
    const target = document.getElementById(tabId);
    if (target) target.classList.add('active');
}

function dismissAlert() {
    const banner = document.getElementById('alertBanner');
    if (banner) banner.style.display = 'none';
}

function escapeHtml(text) {
    if (!text) return '';
    return String(text)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}
