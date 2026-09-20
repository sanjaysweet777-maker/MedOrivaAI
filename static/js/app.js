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
    
    selectedLang = el.getAttribute('data-lang') || el.dataset.lang;
    selectedLangCode = el.getAttribute('data-code') || el.dataset.code || 'ta';
    
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

        const sideCtx = document.getElementById('sideCtx');
        const sideLang = document.getElementById('sideLang');
        const sideId = document.getElementById('sideId');
        if (sideCtx) sideCtx.textContent = currentContext;
        if (sideLang) {
            sideLang.textContent = currentLang;
            sideLang.setAttribute('data-lang', currentLang);
            sideLang.setAttribute('data-code', selectedLangCode || 'ta');
        }
        if (sideId) sideId.textContent = sessionId;

        renderPrompts(data.prompts || data.prepared_prompts || []);

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
        const res = await fetch('/api/translation_check', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ lang_code: testCode })
        });
        const data = await res.json();
        
        if (res.ok && data.connected) {
            result.textContent = `✓ Connected: Translation services operational (${testCode}).`;
            result.style.color = '#10b981';
        } else {
            result.textContent = `⚠ Service status: ${data.error_code || 'unconfigured / local prepared only'}`;
            result.style.color = '#f59e0b';
        }
    } catch (e) {
        result.textContent = '✕ Connection check failed.';
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
            body: JSON.stringify({
                text: text,
                lang: selectedLang,
                lang_code: selectedLangCode
            })
        });
        const data = await res.json();

        if (!res.ok) {
            alert(data.message || 'Staff translation error.');
            return;
        }

        appendMessage('staff', {
            original: data.original || text,
            translated: data.translated || text,
            lang: data.lang || selectedLang || 'Patient'
        });
    } catch (e) {
        alert('Translation request failed.');
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
            body: JSON.stringify({
                text: text,
                lang: selectedLang,
                lang_code: selectedLangCode
            })
        });
        const data = await res.json();

        if (!res.ok) {
            alert(data.message || 'Patient translation error. Session may have expired.');
            return;
        }

        appendMessage('patient', {
            typedInput: text,
            englishMeaning: data.translated,
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

// ============================================================
// 5. TWO-SIDED CHAT RENDERING
// ============================================================

function appendMessage(sender, msg) {
    const chatArea = document.getElementById('chatArea');
    if (!chatArea) return;

    const isRtl = ['ar', 'ur'].includes(String(selectedLangCode).toLowerCase());
    const dirAttr = isRtl ? 'dir="rtl"' : 'dir="ltr"';

    const row = document.createElement('div');
    row.className = `msg-row ${sender}`;
    row.style.display = 'flex';
    row.style.width = '100%';
    row.style.marginBottom = '12px';
    row.style.justifyContent = (sender === 'staff') ? 'flex-end' : 'flex-start';

    if (sender === 'staff') {
        row.innerHTML = `
            <div class="msg-bubble staff" style="max-width:72%;background:#f0fdf4;border:1px solid #bbf7d0;border-right:4px solid #0F6E56;border-radius:12px 12px 2px 12px;padding:14px 18px;text-align:left;box-shadow:0 2px 6px rgba(15,110,86,0.06);">
                <div style="font-size:11px;font-weight:800;color:#0F6E56;text-transform:uppercase;margin-bottom:4px;letter-spacing:0.5px;" dir="ltr">
                    Staff Question (English)
                </div>
                <div style="font-size:15px;font-weight:700;color:#0f172a;margin-bottom:8px;" dir="ltr">
                    ${escapeHtml(msg.original)}
                </div>
                <div style="font-size:13px;color:#1e293b;background:#ffffff;border:1px solid #dcfce7;border-radius:6px;padding:8px 12px;" ${dirAttr}>
                    <span style="color:#0F6E56;font-weight:700;">${escapeHtml(msg.lang)}:</span> ${escapeHtml(msg.translated)}
                </div>
            </div>
        `;
    } else {
        const badge = msg.alert 
            ? `<div style="margin-top:8px;padding:6px 10px;background:#fef3c7;border:1px solid #fde68a;border-radius:6px;color:#92400e;font-weight:700;font-size:12px;" dir="ltr">
                 ℹ️ Recognised Symptom Phrase: ${escapeHtml(msg.symptom)}
               </div>`
            : '';

        row.innerHTML = `
            <div class="msg-bubble patient" style="max-width:72%;background:#ffffff;border:1px solid #cbd5e1;border-left:4px solid #0284c7;border-radius:12px 12px 12px 2px;padding:14px 18px;text-align:left;box-shadow:0 2px 6px rgba(0,0,0,0.04);">
                <div style="font-size:11px;font-weight:800;color:#0284c7;text-transform:uppercase;margin-bottom:4px;letter-spacing:0.5px;" dir="ltr">
                    Patient Message (English for Staff Review)
                </div>
                <div style="font-size:16px;font-weight:700;color:#0f172a;margin-bottom:8px;" dir="ltr">
                    ${escapeHtml(msg.englishMeaning || 'Translation unavailable')}
                </div>
                <div style="font-size:12px;color:#475569;background:#f8fafc;border:1px dashed #cbd5e1;border-radius:6px;padding:8px 12px;display:flex;flex-direction:column;gap:3px;" dir="ltr">
                    <div><strong style="color:#334155;">Patient Typed:</strong> <em>${escapeHtml(msg.typedInput || '')}</em></div>
                    <div ${dirAttr}><strong style="color:#334155;">Native-Script Mapping:</strong> ${escapeHtml(msg.nativeScript || '')}</div>
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
