// MedOriva AI — Client Application Script
let selectedContext = null;
let selectedLang = null;
let selectedLangCode = null;
let sessionId = null;

// ============================================================
// 1. SELECTION HANDLERS
// ============================================================

function selectCtx(btn) {
    const el = btn.closest('.ctx-btn') || btn;
    document.querySelectorAll('.ctx-btn').forEach(b => b.classList.remove('active'));
    el.classList.add('active');
    selectedContext = el.getAttribute('data-ctx') || el.dataset.ctx;
    checkReady();
}

function selectLang(btn) {
    const el = btn.closest('.lang-btn') || btn;
    document.querySelectorAll('.lang-btn').forEach(b => b.classList.remove('active'));
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
        const currentCode = String(data.lang_code || data.code || selectedLangCode || 'en').toLowerCase();

        // Update sidebar state badges
        const sideCtx = document.getElementById('sideCtx');
        const sideLang = document.getElementById('sideLang');
        const sideId = document.getElementById('sideId');
        if (sideCtx) sideCtx.textContent = currentContext;
        if (sideLang) sideLang.textContent = currentLang;
        if (sideId) sideId.textContent = sessionId;

        // Render guided prompts in sidebar
        renderPrompts(data.prompts || []);

        // Safe RTL script direction handling
        const rtlLanguages = ['ar', 'ur'];
        const isRtl = rtlLanguages.includes(currentCode);
        const chatArea = document.getElementById('chatArea');
        if (chatArea) {
            chatArea.setAttribute('dir', isRtl ? 'rtl' : 'ltr');
        }

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
    } catch (e) {
        // Continue reload on network failure
    }
    window.location.reload();
}

// ============================================================
// 3. TRANSLATION CONNECTION TEST (For index.html accordion)
// ============================================================

async function checkTranslationConnection() {
    const btn = document.getElementById('checkConnectionBtn');
    const result = document.getElementById('connectionResult');
    if (!result) return;

    if (btn) btn.disabled = true;
    result.textContent = 'Testing translation connection...';
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
    } catch (e) {
        // Keep current input if simplify fails
    }
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
            original: text,
            native: data.native || text,
            translated: data.translated || text,
            lang: data.lang || 'English',
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
            original: text,
            native: data.native || text,
            translated: `[Understanding Check]: ${data.translated || text}`,
            lang: data.lang || 'English',
            alert: data.medical_alert,
            symptom: data.symptom_detected,
            isNegative: data.is_negative
        });
    } catch (e) {
        alert('Translation verification error. Please try again.');
    }
}

// ============================================================
// 5. DOM HELPERS
// ============================================================

function appendMessage(sender, msg) {
    const chatArea = document.getElementById('chatArea');
    if (!chatArea) return;

    const row = document.createElement('div');
    row.className = `msg-row ${sender}`;

    if (sender === 'staff') {
        row.innerHTML = `
            <div class="msg-bubble staff">
                <div class="msg-title">Staff → Patient</div>
                <div class="msg-text main">${escapeHtml(msg.original)}</div>
                <div class="msg-text sub"><strong>${escapeHtml(msg.lang)}:</strong> ${escapeHtml(msg.translated)}</div>
            </div>
        `;
    } else {
        const badge = msg.alert 
            ? `<div class="triage-tag red" style="color:#ef4444;font-weight:600;margin-top:6px;">🔴 Symptom detected: ${escapeHtml(msg.symptom || 'Urgent')}</div>`
            : (msg.isNegative && msg.symptom ? `<div class="triage-tag green" style="color:#10b981;font-weight:600;margin-top:6px;">✅ Patient reports no ${escapeHtml(msg.symptom)}</div>` : '');

        row.innerHTML = `
            <div class="msg-bubble patient">
                <div class="msg-title">Patient → Staff</div>
                <div class="msg-text main">${escapeHtml(msg.translated)}</div>
                <div class="msg-text sub"><strong>Original:</strong> ${escapeHtml(msg.native || msg.original)}</div>
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
