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
                lang_code: selectedLangCode || 'ta'
            })
        });

        const data = await res.json();
        if (!res.ok || data.status !== 'ok') {
            throw new Error(data.error || 'Failed to start session.');
        }

        sessionId = data.session_id;
        const currentCode = String(data.lang_code || data.code || 'en').toLowerCase();

        // Update Side badges
        const sideCtx = document.getElementById('sideCtx');
        const sideLang = document.getElementById('sideLang');
        const sideId = document.getElementById('sideId');
        if (sideCtx) sideCtx.textContent = data.context;
        if (sideLang) sideLang.textContent = data.lang;
        if (sideId) sideId.textContent = sessionId;

        renderPrompts(data.prompts || []);

        const rtlLanguages = ['ar', 'ur'];
        const chatArea = document.getElementById('chatArea');
        if (chatArea) {
            chatArea.setAttribute('dir', rtlLanguages.includes(currentCode) ? 'rtl' : 'ltr');
        }

        document.getElementById('setupScreen').classList.remove('active');
        document.getElementById('mainScreen').classList.add('active');

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
// 3. STAFF & PATIENT CHAT LOGIC
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
    await sendStaffPrompt(text);
}

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
            lang: data.lang || 'English',
            alert: data.medical_alert,
            symptom: data.symptom_detected,
            isNegative: data.is_negative
        });
    } catch (e) {
        alert('Translation verification error.');
    }
}

// ============================================================
// 4. CLEAN CLINICAL BUBBLE RENDERING
// ============================================================
function appendMessage(sender, msg) {
    const chatArea = document.getElementById('chatArea');
    if (!chatArea) return;

    const row = document.createElement('div');
    row.className = `msg-row ${sender}`;

    if (sender === 'staff') {
        row.innerHTML = `
            <div class="msg-bubble staff">
                <div class="msg-title" style="font-size:11px;font-weight:700;color:#0F6E56;text-transform:uppercase;margin-bottom:4px;">
                    Staff Question (English)
                </div>
                <div class="msg-text main" style="font-size:15px;font-weight:600;margin-bottom:6px;">
                    ${escapeHtml(msg.original)}
                </div>
                <div class="msg-text sub" style="font-size:13px;color:#334155;background:rgba(15,110,86,0.08);padding:8px 10px;border-radius:6px;">
                    <strong>${escapeHtml(msg.lang)}:</strong> ${escapeHtml(msg.translated)}
                </div>
            </div>
        `;
    } else {
        const badge = msg.alert 
            ? `<div class="triage-tag red" style="color:#dc2626;background:#fef2f2;border:1px solid #fecaca;padding:6px 10px;border-radius:6px;font-weight:700;font-size:12px;margin-top:8px;">
                 🔴 Urgent Symptom Detected: ${escapeHtml(msg.symptom)}
               </div>`
            : (msg.isNegative && msg.symptom ? `<div class="triage-tag green" style="color:#15803d;background:#f0fdf4;border:1px solid #bbf7d0;padding:6px 10px;border-radius:6px;font-weight:600;font-size:12px;margin-top:8px;">
                 ✅ Patient confirms NO ${escapeHtml(msg.symptom)}
               </div>` : '');

        row.innerHTML = `
            <div class="msg-bubble patient">
                <div class="msg-title" style="font-size:11px;font-weight:700;color:#0369a1;text-transform:uppercase;margin-bottom:4px;">
                    Patient Statement (Translated for Staff)
                </div>
                <div class="msg-text main" style="font-size:16px;font-weight:700;color:#0f172a;margin-bottom:8px;">
                    ${escapeHtml(msg.englishMeaning)}
                </div>
                <div style="font-size:12px;color:#64748b;background:#f8fafc;border:1px solid #e2e8f0;padding:8px 10px;border-radius:6px;display:flex;flex-direction:column;gap:4px;">
                    <div><strong>Patient Typed:</strong> <em>${escapeHtml(msg.typedInput)}</em></div>
                    <div><strong>Verified Native:</strong> ${escapeHtml(msg.nativeScript)}</div>
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
