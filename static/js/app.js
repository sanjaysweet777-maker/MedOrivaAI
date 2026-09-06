// MedOriva AI — Client Application Script
let selectedContext = null;
let selectedLang = null;
let selectedLangCode = null;
let sessionId = null;

// 1. Context Selection
function selectCtx(btn) {
    const el = btn.closest('.ctx-btn') || btn;
    document.querySelectorAll('.ctx-btn').forEach(b => b.classList.remove('active'));
    el.classList.add('active');
    selectedContext = el.dataset.ctx || el.getAttribute('data-ctx');
    checkReady();
}

// 2. Language Selection
function selectLang(btn) {
    const el = btn.closest('.lang-btn') || btn;
    document.querySelectorAll('.lang-btn').forEach(b => b.classList.remove('active'));
    el.classList.add('active');
    selectedLang = el.dataset.lang || el.getAttribute('data-lang');
    selectedLangCode = el.dataset.code || el.getAttribute('data-code');
    checkReady();
}

function checkReady() {
    const startBtn = document.getElementById('startBtn');
    if (startBtn) {
        startBtn.disabled = !(selectedContext && selectedLang);
    }
}

// 3. Start Session (Defensive against undefined .includes)
async function startSession() {
    const startBtn = document.getElementById('startBtn');
    if (startBtn) startBtn.disabled = true;

    try {
        if (!selectedContext || !selectedLang) {
            alert('Please select both a communication context and a patient language.');
            if (startBtn) startBtn.disabled = false;
            return;
        }

        const response = await fetch('/api/start_session', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                context: selectedContext,
                lang: selectedLang,
                lang_code: selectedLangCode || 'ta'
            })
        });

        if (!response.ok) {
            const errData = await response.json().catch(() => ({}));
            throw new Error(errData.message || errData.error || `Server responded with status ${response.status}`);
        }

        const data = await response.json();
        if (data.status !== 'ok') {
            throw new Error(data.error || 'Failed to start session.');
        }

        // Session State
        sessionId = data.session_id;
        const currentContext = data.context || selectedContext;
        const currentLang = data.lang || selectedLang;
        const currentCode = data.lang_code || data.code || selectedLangCode || 'ta';

        // Update Side Badges
        const sideCtx = document.getElementById('sideCtx');
        const sideLang = document.getElementById('sideLang');
        const sideId = document.getElementById('sideId');
        if (sideCtx) sideCtx.textContent = currentContext;
        if (sideLang) sideLang.textContent = currentLang;
        if (sideId) sideId.textContent = sessionId;

        // Render Prompts
        renderPrompts(data.prompts || []);

        // Safe Direction Setting (Immune to undefined .includes)
        const rtlLanguages = ['ar', 'ur'];
        const isRtl = rtlLanguages.includes(String(currentCode).toLowerCase());
        const chatArea = document.getElementById('chatArea');
        if (chatArea) {
            chatArea.setAttribute('dir', isRtl ? 'rtl' : 'ltr');
        }

        // Switch to Active Session Screen
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

// 4. Render Guided Prompts
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

// 5. Staff Prompt / Free Text
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
            lang: data.lang || 'Patient'
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
    await sendStaffPrompt(text);
}

// 6. Patient Input Translation
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

        // Show Banner for Urgent Symptoms
        const alertBanner = document.getElementById('alertBanner');
        if (alertBanner) {
            alertBanner.style.display = data.medical_alert ? 'flex' : 'none';
        }
    } catch (e) {
        alert('Translation error. Please try again.');
    }
}

// 7. Append Messages to UI
function appendMessage(sender, msg) {
    const chatArea = document.getElementById('chatArea');
    if (!chatArea) return;

    const row = document.createElement('div');
    row.className = `msg-row ${sender}`;

    if (sender === 'staff') {
        row.innerHTML = `
            <div class="msg-bubble staff">
                <div class="msg-title">Staff → Patient</div>
                <div class="msg-text main">${msg.original}</div>
                <div class="msg-text sub"><strong>${msg.lang}:</strong> ${msg.translated}</div>
            </div>
        `;
    } else {
        const badge = msg.alert 
            ? `<div class="triage-tag red">🔴 Medical Attention Needed: ${msg.symptom || 'Urgent Symptom'}</div>`
            : (msg.isNegative ? `<div class="triage-tag green">✅ Patient reports no ${msg.symptom || 'symptom'}</div>` : '');

        row.innerHTML = `
            <div class="msg-bubble patient">
                <div class="msg-title">Patient → Staff</div>
                <div class="msg-text main">${msg.translated}</div>
                <div class="msg-text sub"><strong>Native:</strong> ${msg.native}</div>
                ${badge}
            </div>
        `;
    }

    chatArea.appendChild(row);
    chatArea.scrollTop = chatArea.scrollHeight;
}

// 8. Tab Navigation
function switchTab(tabBtn) {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));

    tabBtn.classList.add('active');
    const tabId = 'tab-' + tabBtn.dataset.tab;
    const target = document.getElementById(tabId);
    if (target) target.classList.add('active');
}

function dismissAlert() {
    const banner = document.getElementById('alertBanner');
    if (banner) banner.style.display = 'none';
}

async function endSession() {
    await fetch('/api/end_session', { method: 'POST' }).catch(() => {});
    window.location.reload();
}
