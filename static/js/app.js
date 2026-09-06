/* Session-local display; never persist conversation text. */
let selectedCtx=null, selectedLang=null, selectedCode=null, busy=false, generation=0;
async function api(path,payload){
  const res=await fetch(path,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload||{})});
  const data=await res.json();
  if(!res.ok || data.error) throw new Error(data.error || 'Request failed. Please try again.');
  return data;
}
function selectCtx(btn){document.querySelectorAll('.ctx-btn').forEach(b=>{b.classList.toggle('selected',b===btn);b.setAttribute('aria-pressed',b===btn);});selectedCtx=btn.dataset.ctx;updateStartBtn();}
function selectLang(btn){document.querySelectorAll('.lang-btn').forEach(b=>{b.classList.toggle('selected',b===btn);b.setAttribute('aria-pressed',b===btn);});selectedLang=btn.dataset.lang;selectedCode=btn.dataset.code;updateStartBtn();}
function updateStartBtn(){document.getElementById('startBtn').disabled=!(selectedCtx&&selectedCode);}
async function startSession(){
 const btn=document.getElementById('startBtn');btn.disabled=true;
 try{const d=await api('/api/start_session',{context:selectedCtx,lang_code:selectedCode});generation++;
  document.getElementById('sideCtx').textContent=d.context;document.getElementById('sideLang').textContent=d.lang;
  document.getElementById('sideId').textContent=d.session_id.slice(0,8);document.getElementById('chatSubtitle').textContent=d.context+' · '+d.lang;
  buildPromptList(d.prompts,d.prepared_prompts,d.provider_configured);
  document.getElementById('setupScreen').classList.remove('active');document.getElementById('mainScreen').classList.add('active');
  addSystemBubble('Demonstration session. Use fictional information only. '+(d.provider_configured?'Full-text machine translation available; outputs require review.':'Prepared phrases available. Full-text translation needs administrator setup.'));
 }catch(e){alert(e.message);}finally{updateStartBtn();}
}
async function endSession(){
 if(!confirm('End this session and clear the displayed conversation?'))return;
 try{await api('/api/end_session');generation++;
 document.getElementById('mainScreen').classList.remove('active');document.getElementById('setupScreen').classList.add('active');
 document.getElementById('chatArea').replaceChildren();
 ['freeInput','patientInput','confirmInput'].forEach(id=>document.getElementById(id).value='');
 document.getElementById('simplifyNote').style.display='none';document.getElementById('alertBanner').style.display='none';
 document.querySelectorAll('.ctx-btn,.lang-btn').forEach(b=>{b.classList.remove('selected');b.setAttribute('aria-pressed','false');});
 selectedCtx=null;selectedLang=null;selectedCode=null;updateStartBtn();
 }catch(e){addSystemBubble(e.message);}
}
function buildPromptList(prompts,prepared,configured){
 const list=document.getElementById('promptsList');list.replaceChildren();
 prompts.forEach(p=>{const b=document.createElement('button');b.className='prompt-item';b.textContent=p;
 b.title=prepared.includes(p)?'Prepared demo phrase; review required':'Full-text translation; review required';
 b.disabled=!configured&&!prepared.includes(p);b.dataset.available=String(!b.disabled);
 b.onclick=()=>sendGuidedPrompt(p);list.appendChild(b);});
}
function setBusy(value){busy=value;document.querySelectorAll('.action-btn,.prompt-item').forEach(b=>b.disabled=value||b.dataset.available==='false');}
function line(parent,label,value,lang){
 if(!value)return;const block=document.createElement('div');block.className='message-line';
 const caption=document.createElement('span');caption.className='message-caption';caption.textContent=label;
 const content=document.createElement('div');content.textContent=value;content.dir='auto';if(lang)content.lang=lang;
 block.append(caption,content);parent.appendChild(block);
}
function resultBubble(data,kind){
 document.getElementById('emptyChat')?.remove();
 const wrap=document.createElement('article');wrap.className='bubble-wrap '+(kind==='staff'?'staff':'patient');
 const label=document.createElement('div');label.className='bubble-label';label.textContent=kind==='staff'?'Staff → '+data.lang:kind==='confirm'?'Understanding check · staff review required':data.lang+' → Staff';
 const bubble=document.createElement('div');bubble.className='bubble '+(kind==='staff'?'staff':'patient');
 line(bubble,'Original message',data.original,kind==='staff'?'en':selectedCode);
 line(bubble,'Translation',data.translated,kind==='staff'?selectedCode:'en');
 if(data.native && data.native!==data.original)line(bubble,'Prepared native-script form',data.native,selectedCode);
 const status=document.createElement('div');status.className='translation-status '+data.status;status.textContent=data.warning;status.setAttribute('role','status');bubble.appendChild(status);
 if(kind==='confirm')line(bubble,'Next step','Ask the speaker to explain the message in their own words. Staff must assess understanding; this translation does not verify it.');
 wrap.append(label,bubble);document.getElementById('chatArea').appendChild(wrap);scrollChat();
}
async function translate(text,kind,input){
 if(busy||!text.trim())return;const ticket=generation;setBusy(true);
 try{const data=await api(kind==='staff'?'/api/translate_staff':'/api/translate_patient',{text:text.trim()});
 if(ticket!==generation)return;resultBubble(data,kind);if(input&&data.status!=='unavailable')input.value='';
 }catch(e){if(ticket===generation)addSystemBubble(e.message);}finally{setBusy(false);}
}
function sendGuidedPrompt(text){return translate(text,'staff');}
function sendFreeText(){const i=document.getElementById('freeInput');return translate(i.value,'staff',i);}
function translatePatient(){const i=document.getElementById('patientInput');return translate(i.value,'patient',i);}
function checkUnderstanding(){const i=document.getElementById('confirmInput');return translate(i.value,'confirm',i);}
function addSystemBubble(text){document.getElementById('emptyChat')?.remove();const w=document.createElement('div');w.className='bubble-wrap system';const b=document.createElement('div');b.className='bubble system';b.textContent=text;w.appendChild(b);document.getElementById('chatArea').appendChild(w);scrollChat();}
function scrollChat(){const a=document.getElementById('chatArea');a.scrollTop=a.scrollHeight;}
function dismissAlert(){document.getElementById('alertBanner').style.display='none';}
function switchTab(btn){document.querySelectorAll('.tab').forEach(t=>t.classList.toggle('active',t===btn));document.querySelectorAll('.tab-pane').forEach(p=>p.classList.toggle('active',p.id==='tab-'+btn.dataset.tab));}
async function suggestSimplification(){
 const input=document.getElementById('freeInput');if(!input.value.trim()||busy)return;
 try{const original=input.value;const d=await api('/api/simplify',{text:original});if(input.value!==original)return;
 if(d.changed && confirm('Review this suggested wording before using it:\n\n'+d.simplified))input.value=d.simplified;
 else if(!d.changed)addSystemBubble('No prepared wording suggestion. Keep the original meaning when editing.');
 }catch(e){addSystemBubble(e.message);}
}
