/* MedOriva AI — Frontend Logic */

let selectedCtx = null;
let selectedLang = null;
let selectedCode = null;

function selectCtx(btn) {
  document.querySelectorAll('.ctx-btn').forEach(b => b.classList.remove('selected'));
  btn.classList.add('selected');
  selectedCtx = btn.dataset.ctx;
  updateStartBtn();
}

function selectLang(btn) {
  document.querySelectorAll('.lang-btn').forEach(b => b.classList.remove('selected'));
  btn.classList.add('selected');
  selectedLang = btn.dataset.lang;
  selectedCode = btn.dataset.code;
  updateStartBtn();
}

function updateStartBtn() {
  document.getElementById('startBtn').disabled = !(selectedCtx && selectedLang);
}

async function startSession() {
  const btn = document.getElementById('startBtn');
  btn.textContent = 'Starting...';
  btn.disabled = true;
  try {
    const res = await fetch('/api/start_session', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ context: selectedCtx, lang: selectedLang, lang_code: selectedCode })
    });
    const data = await res.json();
    document.getElementById('sideCtx').textContent = data.context;
    document.getElementById('sideLang').textContent = data.lang;
    document.getElementById('sideId').textContent = data.session_id;
    document.getElementById('chatSubtitle').textContent = data.context + ' · ' + data.lang;
    buildPromptList(data.prompts);
    document.getElementById('setupScreen').classList.remove('active');
    document.getElementById('mainScreen').classList.add('active');
    addSystemBubble('Session started — Context: ' + data.context + ' | Language: ' + data.lang + '. No patient data stored.');
  } catch (e) {
    btn.textContent = 'Start session';
    btn.disabled = false;
    alert('Could not start session. Is Flask running?');
  }
}

async function endSession() {
  if (!confirm('End session? All data will be cleared.')) return;
  await fetch('/api/end_session', { method: 'POST' });
  document.getElementById('mainScreen').classList.remove('active');
  document.getElementById('setupScreen').classList.add('active');
  document.getElementById('chatArea').innerHTML =
    '<div class="empty-chat" id="emptyChat">' +
    '<div class="empty-icon">💬</div>' +
    '<div class="empty-title">Ready to communicate</div>' +
    '<div class="empty-hint">Use guided prompts or type below.</div>' +
    '</div>';
  document.getElementById('alertBanner').style.display = 'none';
  document.getElementById('freeInput').value = '';
  document.getElementById('patientInput').value = '';
  document.getElementById('confirmInput').value = '';
  document.getElementById('startBtn').disabled = true;
  document.getElementById('startBtn').textContent = 'Start session';
  document.querySelectorAll('.ctx-btn, .lang-btn').forEach(b => b.classList.remove('selected'));
  selectedCtx = null; selectedLang = null; selectedCode = null;
  switchTab(document.querySelector('.tab'));
}

function buildPromptList(prompts) {
  const list = document.getElementById('promptsList');
  list.innerHTML = '';
  prompts.forEach(function(p) {
    const btn = document.createElement('button');
    btn.className = 'prompt-item';
    btn.textContent = p;
    btn.onclick = function() { sendGuidedPrompt(p, btn); };
    list.appendChild(btn);
  });
}

async function sendGuidedPrompt(text, btn) {
  if (btn) { btn.disabled = true; btn.style.opacity = '0.5'; }
  addStaffBubble(text, null, false, true);
  try {
    const res = await fetch('/api/translate_staff', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: text })
    });
    const data = await res.json();
    if (data.error) { addSystemBubble('Error: ' + data.error); return; }
    updateLastStaffBubble(data.simplified, data.translated, data.lang, data.was_simplified);
  } finally {
    if (btn) { btn.disabled = false; btn.style.opacity = '1'; }
  }
}

document.addEventListener('DOMContentLoaded', function() {
  const fi = document.getElementById('freeInput');
  if (fi) {
    fi.addEventListener('input', async function() {
      const text = fi.value.trim();
      if (!text) { document.getElementById('simplifyNote').style.display = 'none'; return; }
      const res = await fetch('/api/simplify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: text })
      });
      const data = await res.json();
      document.getElementById('simplifyNote').style.display = data.changed ? 'block' : 'none';
    });
  }
});

async function sendFreeText() {
  const input = document.getElementById('freeInput');
  const text = input.value.trim();
  if (!text) return;
  const btn = document.getElementById('freeBtn');
  btn.innerHTML = '<span class="spinner"></span>Translating...';
  btn.disabled = true;
  input.value = '';
  document.getElementById('simplifyNote').style.display = 'none';
  try {
    const res = await fetch('/api/translate_staff', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: text })
    });
    const data = await res.json();
    if (data.error) { addSystemBubble('Error: ' + data.error); return; }
    addStaffBubble(data.simplified, data.translated, data.was_simplified, false);
  } finally {
    btn.innerHTML = 'Translate &amp; send';
    btn.disabled = false;
  }
}

async function translatePatient() {
  const input = document.getElementById('patientInput');
  const text = input.value.trim();
  if (!text) return;
  const btn = document.getElementById('patientBtn');
  btn.innerHTML = '<span class="spinner"></span>Translating...';
  btn.disabled = true;
  try {
    const res = await fetch('/api/translate_patient', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: text })
    });
    const data = await res.json();
    if (data.error) { addSystemBubble('Error: ' + data.error); return; }
    // data.original  = what patient typed  (e.g. enaku nenji vali irukku)
    // data.native    = proper native script (e.g. எனக்கு நெஞ்சு வலி இருக்கு)
    // data.translated = English for staff   (e.g. I have chest pain)
    addPatientBubble(data.original, data.native, data.translated, data.lang, data.symptom_detected, data.medical_alert);
    input.value = '';
  } finally {
    btn.innerHTML = 'Translate to English';
    btn.disabled = false;
  }
}

async function checkUnderstanding() {
  const input = document.getElementById('confirmInput');
  const text = input.value.trim();
  if (!text) return;
  const btn = document.getElementById('confirmBtn');
  btn.innerHTML = '<span class="spinner"></span>Verifying...';
  btn.disabled = true;
  try {
    const res = await fetch('/api/translate_patient', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: text })
    });
    const data = await res.json();
    if (data.error) { addSystemBubble('Error: ' + data.error); return; }
    addConfirmBubble(data.original, data.native, data.translated);
    input.value = '';
  } finally {
    btn.innerHTML = 'Verify understanding';
    btn.disabled = false;
  }
}

// ── Bubble helpers ────────────────────────────────────────────────────────

function removeEmpty() {
  const e = document.getElementById('emptyChat');
  if (e) e.remove();
}

function scrollChat() {
  const area = document.getElementById('chatArea');
  area.scrollTop = area.scrollHeight;
}

let lastStaffBubble = null;

function addStaffBubble(text, translated, wasSimplified, pending) {
  removeEmpty();
  const wrap = document.createElement('div');
  wrap.className = 'bubble-wrap staff';
  const label = document.createElement('div');
  label.className = 'bubble-label';
  label.textContent = pending ? 'Staff (sending...)' : 'Staff → Patient';
  wrap.appendChild(label);
  const bub = document.createElement('div');
  bub.className = 'bubble staff';
  bub.textContent = text;
  if (wasSimplified) {
    const note = document.createElement('div');
    note.className = 'simplified-note';
    note.textContent = '✓ Simplified';
    bub.appendChild(note);
  }
  if (translated) {
    const tr = document.createElement('div');
    tr.className = 'translated-line';
    tr.textContent = '→ ' + translated;
    bub.appendChild(tr);
  }
  wrap.appendChild(bub);
  document.getElementById('chatArea').appendChild(wrap);
  lastStaffBubble = { label: label, bub: bub };
  scrollChat();
}

function updateLastStaffBubble(text, translated, lang, wasSimplified) {
  if (!lastStaffBubble) return;
  lastStaffBubble.label.textContent = 'Staff → Patient';
  lastStaffBubble.bub.textContent = text;
  if (wasSimplified) {
    const note = document.createElement('div');
    note.className = 'simplified-note';
    note.textContent = '✓ Simplified';
    lastStaffBubble.bub.appendChild(note);
  }
  const tr = document.createElement('div');
  tr.className = 'translated-line';
  tr.textContent = '→ ' + lang + ': ' + translated;
  lastStaffBubble.bub.appendChild(tr);
  scrollChat();
}

function addPatientBubble(original, native, translated, lang, symptom, medicalAlert) {
  removeEmpty();
  const wrap = document.createElement('div');
  wrap.className = 'bubble-wrap patient';

  // Label
  const label = document.createElement('div');
  label.className = 'bubble-label';
  label.textContent = 'Patient (' + lang + ') → Staff';
  wrap.appendChild(label);

  const bub = document.createElement('div');
  bub.className = 'bubble patient';

  // 1. ENGLISH — big and bold for staff
  const engDiv = document.createElement('div');
  engDiv.style.cssText = 'font-size:15px;font-weight:700;color:#0a3d52;line-height:1.5;margin-bottom:6px;';
  engDiv.textContent = (translated && translated.trim() !== '') ? translated : original;
  bub.appendChild(engDiv);

  // 2. NATIVE SCRIPT — proper Tamil/Hindi/Malayalam/Polish script
  const nativeDiv = document.createElement('div');
  nativeDiv.style.cssText = 'font-size:13px;color:#1a4a5a;margin-top:4px;padding-top:5px;border-top:1px solid #b8d8ea;font-weight:500;';
  nativeDiv.textContent = lang + ': ' + (native && native.trim() !== '' ? native : original);
  bub.appendChild(nativeDiv);

  // 3. TYPED INPUT — tiny, only shown if different from native
  if (original && native && original.trim().toLowerCase() !== native.trim().toLowerCase()) {
    const typedDiv = document.createElement('div');
    typedDiv.style.cssText = 'font-size:10px;color:#6a8a9a;font-style:italic;margin-top:3px;';
    typedDiv.textContent = 'Typed: ' + original;
    bub.appendChild(typedDiv);
  }

  wrap.appendChild(bub);
  document.getElementById('chatArea').appendChild(wrap);

  // Medical alert — positive symptom
  if (medicalAlert) {
    const alertWrap = document.createElement('div');
    alertWrap.className = 'bubble-wrap system';
    const alertBub = document.createElement('div');
    alertBub.className = 'bubble medical-alert';
    alertBub.innerHTML =
      '<div style="font-size:15px;font-weight:700;margin-bottom:4px;">🔴 Medical consultation needed</div>' +
      '<div style="font-size:12.5px;">Patient has reported a symptom that requires staff attention. Please follow your clinical protocol.</div>' +
      (symptom ? '<div style="margin-top:6px;font-size:12px;opacity:0.85;">Symptom detected: <strong>' + symptom + '</strong></div>' : '');
    alertWrap.appendChild(alertBub);
    document.getElementById('chatArea').appendChild(alertWrap);
  }

  // Green confirmation — negative symptom
  if (!medicalAlert && symptom) {
    const okWrap = document.createElement('div');
    okWrap.className = 'bubble-wrap system';
    const okBub = document.createElement('div');
    okBub.className = 'bubble no-alert';
    okBub.innerHTML =
      '<div style="font-size:13px;font-weight:600;">✅ Patient reports no ' + symptom + '</div>' +
      '<div style="font-size:11.5px;margin-top:3px;opacity:0.8;">No immediate action required for this symptom.</div>';
    okWrap.appendChild(okBub);
    document.getElementById('chatArea').appendChild(okWrap);
  }

  scrollChat();
}

function addConfirmBubble(original, native, translated) {
  removeEmpty();
  const wrap = document.createElement('div');
  wrap.className = 'bubble-wrap system';
  const label = document.createElement('div');
  label.className = 'bubble-label';
  label.textContent = 'Understanding check — English for staff';
  wrap.appendChild(label);
  const bub = document.createElement('div');
  bub.className = 'bubble confirm-result';
  bub.innerHTML =
    '<div style="font-size:14px;font-weight:700;color:#0a3d52;margin-bottom:4px;">English: ' + (translated || original) + '</div>' +
    '<div style="font-size:12px;color:#1a4a5a;margin-bottom:3px;">' + (native && native !== original ? native : '') + '</div>' +
    '<div style="font-size:11px;color:#6a8a9a;font-style:italic;">Typed: ' + original + '</div>';
  wrap.appendChild(bub);
  document.getElementById('chatArea').appendChild(wrap);
  scrollChat();
}

function addSystemBubble(text) {
  removeEmpty();
  const wrap = document.createElement('div');
  wrap.className = 'bubble-wrap system';
  const bub = document.createElement('div');
  bub.className = 'bubble system';
  bub.textContent = text;
  wrap.appendChild(bub);
  document.getElementById('chatArea').appendChild(wrap);
  scrollChat();
}

function showAlert() {
  document.getElementById('alertBanner').style.display = 'flex';
}

function dismissAlert() {
  document.getElementById('alertBanner').style.display = 'none';
}

function switchTab(clickedTab) {
  document.querySelectorAll('.tab').forEach(function(t) { t.classList.remove('active'); });
  document.querySelectorAll('.tab-pane').forEach(function(p) { p.classList.remove('active'); });
  clickedTab.classList.add('active');
  document.getElementById('tab-' + clickedTab.dataset.tab).classList.add('active');
}
