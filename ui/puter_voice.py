"""Keyless ElevenLabs speech through each learner's Puter account, opt-in only."""

import hashlib
import streamlit as st
from ui.tex_voice import VOICE_ID, VOICE_NAME
from ui.tex_app_control import decode_action

_HTML = """
<section class="tex-console" data-mode="off" aria-label="Tex voice tutor">
  <header><span class="wordmark">TEX<span class="dot">.</span></span><span class="phase" id="phase">OFFLINE</span></header>
  <div class="orb-stage" aria-hidden="true"><div class="orbit"></div><div class="orb"><span>T</span></div></div>
  <p class="tagline">Learn out loud.</p>
  <p id="status" class="status" role="status" aria-live="polite">Connecting the voice controls…</p>
  <div class="main-controls">
    <button id="connect" disabled>Enable voice</button>
    <button id="listen" class="primary" title="Interrupt Tex and speak your answer">Talk to Tex</button>
    <button id="stop" title="Stop playback and turn off the microphone">Stop</button>
  </div>
  <button id="speak" class="play-reply" disabled>Play reply <span aria-hidden="true">↗</span></button>
  <p class="meta">ElevenLabs via Puter · account limits apply</p>
  <details class="settings"><summary>Voice settings</summary>
    <div class="playback"><button id="pause">Pause audio</button><button id="resume">Resume audio</button></div>
    <label class="check"><input id="auto" type="checkbox"> Read new replies automatically</label>
    <label class="check"><input id="handsfree" type="checkbox"> Listen after each reply</label>
    <label class="field">Voice <select id="voice"></select></label>
    <label class="field">Speech language <select id="lang"><option value="en-ZA">English (South Africa)</option>
    <option value="af-ZA">Afrikaans</option><option value="zu-ZA">isiZulu</option>
    <option value="xh-ZA">isiXhosa</option><option value="st-ZA">Sesotho</option></select></label>
    <p class="privacy">ElevenLabs voice through Puter. Puter sign-in, account credits and limits apply.
    Spoken replies go to Puter/ElevenLabs. Live speech uses your browser’s transcription service,
    then sends the transcript to Gemini. Headphones are recommended for automatic listening.
    You can always type or use the answer recorder instead.</p>
    <button id="signout" class="signout" disabled>Sign out of Puter</button>
  </details>
</section>
"""

_CSS = """
:host {color:var(--st-text-color, #e7eef6);font-family:var(--st-font,system-ui,sans-serif);}
* {box-sizing:border-box;}
.tex-console {--tex-accent:#6ee7dd;--tex-ink:var(--st-text-color,#e7eef6);width:100%;min-width:0;
  padding:16px;border:1px solid var(--st-border-color,#28384c);border-radius:22px;
  background:var(--st-secondary-background-color,#101b2c);color:var(--tex-ink);overflow:hidden;}
header {display:flex;justify-content:space-between;align-items:center;gap:12px;}
.wordmark {font-size:15px;font-weight:750;letter-spacing:.22em;}.dot{color:var(--tex-accent);}
.phase {font-size:10px;letter-spacing:.14em;opacity:.6;border:1px solid var(--st-border-color,#28384c);border-radius:20px;padding:5px 8px;}
.orb-stage {height:106px;display:grid;place-items:center;position:relative;}
.orb {width:80px;height:80px;border:1px solid #6ee7dd77;border-radius:50%;display:grid;place-items:center;
  background:radial-gradient(circle at 36% 28%,#6ee7dd35,#0f394233 55%,transparent 75%);box-shadow:0 0 35px #6ee7dd13;}
.orb span {font-size:29px;font-weight:350;color:var(--tex-accent);}
.orbit {position:absolute;width:104px;height:104px;border-radius:50%;border:1px solid #6ee7dd22;border-top-color:#6ee7dd88;transform:rotate(-30deg);}
.tagline {text-align:center;font-size:18px;letter-spacing:-.02em;margin:0 0 7px;font-weight:500;}
.status {text-align:center;min-height:28px;font-size:12px;line-height:1.55;opacity:.7;margin:0 auto 12px;max-width:340px;overflow-wrap:anywhere;}
button {font:inherit;font-size:12px;line-height:1.2;color:inherit;border:1px solid var(--st-border-color,#34445a);
  border-radius:12px;background:transparent;padding:10px 9px;cursor:pointer;min-height:40px;transition:background .15s,border-color .15s;}
button:hover:not(:disabled) {border-color:var(--tex-accent);background:#6ee7dd0c;}
button:focus-visible,select:focus-visible,summary:focus-visible,input:focus-visible {outline:2px solid var(--tex-accent);outline-offset:3px;}
button:disabled {opacity:.35;cursor:default;}
.main-controls {display:grid;grid-template-columns:1fr 1.2fr .65fr;gap:7px;}
.primary {background:var(--tex-accent);border-color:var(--tex-accent);color:#082e31;font-weight:650;}
.primary:hover:not(:disabled) {background:#96f3eb;}
.play-reply {width:100%;margin-top:5px;border:0;min-height:30px;padding:6px;opacity:.75;}
.play-reply span{padding-left:8px;color:var(--tex-accent);}
.meta{text-align:center;font-size:10px;opacity:.5;margin:5px 0 0;}
.settings {margin-top:9px;border-top:1px solid var(--st-border-color,#28384c);padding-top:10px;}
summary {cursor:pointer;font-size:12px;opacity:.7;list-style-position:inside;}
.playback{display:flex;gap:8px;margin:14px 0;}.playback button{flex:1;}
.check{display:flex;align-items:center;gap:9px;margin:14px 0;font-size:12px;line-height:1.4;}.check input{accent-color:#45bfb5;}
.field{display:block;font-size:11px;opacity:.85;margin:14px 0;}select{display:block;width:100%;max-width:100%;margin-top:6px;
  color:var(--tex-ink);background:var(--st-background-color,#0a1120);border:1px solid var(--st-border-color,#34445a);
  border-radius:10px;padding:10px;font:inherit;font-size:12px;text-overflow:ellipsis;}
.privacy{font-size:11px;line-height:1.6;opacity:.6;}.signout{width:100%;font-size:11px;}
.tex-console[data-mode="speaking"] .orb,.tex-console[data-mode="listening"] .orb{animation:tex-breathe 1.8s ease-in-out infinite;}
.tex-console[data-mode="thinking"] .orbit{animation:tex-orbit 3s linear infinite;}
.tex-console[data-mode="ready"] .phase,.tex-console[data-mode="speaking"] .phase,.tex-console[data-mode="listening"] .phase{opacity:1;color:var(--tex-accent);border-color:#6ee7dd55;}
.tex-console[data-mode="error"] .phase{opacity:1;color:#e9ac7e;}
@keyframes tex-breathe{50%{box-shadow:0 0 36px #6ee7dd30;transform:scale(1.05);}}
@keyframes tex-orbit{to{transform:rotate(330deg);}}
@media(prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important;}}
@media(max-width:300px){.tex-console{padding:14px}.main-controls{grid-template-columns:1fr 1fr}.main-controls #stop{grid-column:1/-1;min-height:32px;padding:7px;}.orb-stage{height:118px;}}
"""

_JS = r"""
const instances = new WeakMap();
let sdk;
function loadPuter() {
  if (window.puter) return Promise.resolve(window.puter);
  if (!sdk) sdk = new Promise((resolve,reject) => {
    const script = document.createElement('script'); script.src='https://js.puter.com/v2/';
    script.onload=()=>resolve(window.puter); script.onerror=()=>{sdk=null; reject(new Error('sdk'));};
    document.head.appendChild(script);
  });
  return sdk;
}
export default function({parentElement, data, setTriggerValue}) {
  let s = instances.get(parentElement);
  if (!s) {s={audio:null, recognition:null, enabled:false, generation:0, last:null, busy:false, disposed:false}; instances.set(parentElement,s);}
  s.data=data; s.emit=setTriggerValue;
  const el=id=>parentElement.querySelector('#'+id);
  const status=text=>{
    if(s.disposed)return;
    el('status').textContent=text;
    const mode=/speaking/i.test(text)?'speaking':/^Listening/i.test(text)?'listening':/generating|thinking|checking|loading|connecting/i.test(text)?'thinking':/could not|couldn't|unavailable|cancelled|blocked|not understood/i.test(text)?'error':/paused/i.test(text)?'paused':/enabled|Ready for/i.test(text)?'ready':'off';
    const shell=parentElement.querySelector('.tex-console');shell.dataset.mode=mode;
    el('phase').textContent={speaking:'SPEAKING',listening:'LISTENING',thinking:'THINKING',error:'TRY AGAIN',paused:'PAUSED',ready:'READY',off:'VOICE OFF'}[mode];
  };
  const abort=()=>{s.generation++; if(s.settle){s.settle();s.settle=null;} if(s.audio){s.audio.pause();s.audio.removeAttribute('src');s.audio.load();s.audio=null;}
    if(s.recognition){s.recognition.onend=null;s.recognition.abort();s.recognition=null;} s.busy=false;};
  const listen=()=>{
    if(!s.enabled) {status('Enable Tex voice first, or use the recorded-answer input.');return;}
    abort();
    const Recognition=window.SpeechRecognition||window.webkitSpeechRecognition;
    if(!Recognition){status('Live speech recognition is unavailable in this browser. Use the recorded-answer or typed input below.');return;}
    const recognition=new Recognition(); s.recognition=recognition;
    recognition.lang=el('lang').value; recognition.interimResults=false; recognition.continuous=false;
    let words='';
    recognition.onresult=event=>{for(let i=event.resultIndex;i<event.results.length;i++)if(event.results[i].isFinal)words+=event.results[i][0].transcript+' ';};
    recognition.onerror=()=>{status('Microphone unavailable or speech not understood. Try again or record below.');};
    recognition.onend=()=>{s.recognition=null;if(words.trim() && !s.disposed){status('Tex is thinking…');s.emit('utterance',{id:crypto.randomUUID(),text:words.trim().slice(0,6000)});}else if(!s.disposed)status('No speech captured. Try again.');};
    try {recognition.start();status('Listening. Your transcript will be sent to Tex when you finish speaking.');}
    catch {status('Could not start the microphone. Use the recorder below.');}
  };
  const speak=async()=>{
    if(!s.enabled||!s.data.text||s.busy)return;
    abort();const generation=s.generation; s.busy=true;s.last=s.data.reply_id;
    try {
      const puter=await loadPuter();
      let remaining=s.data.text;
      while(remaining && generation===s.generation && !s.disposed) {
        let length=Math.min(2800,remaining.length);if(length<remaining.length){const boundary=remaining.lastIndexOf(' ',length);if(boundary>1400)length=boundary;}
        const chunk=remaining.slice(0,length);remaining=remaining.slice(length).trimStart();
        status('Generating ElevenLabs speech…');
        const audio=await puter.ai.txt2speech(chunk,{provider:'elevenlabs',voice:el('voice').value||data.voice_id,model:'eleven_flash_v2_5',output_format:'mp3_44100_128'});
        if(generation!==s.generation||s.disposed){audio.pause();audio.removeAttribute('src');audio.load();return;}
        s.audio=audio;
        await new Promise((resolve,reject)=>{s.settle=resolve;audio.onended=()=>{s.settle=null;resolve();};audio.onerror=()=>{s.settle=null;reject();};audio.play().then(()=>status('Tex is speaking. You can pause or interrupt.')).catch(reject);});
      }
      s.busy=false;
      if(generation===s.generation&&!s.disposed){status('Ready for your answer.');if(el('handsfree').checked)listen();}
    } catch {s.busy=false;if(generation===s.generation)status('Voice could not play. Check Puter sign-in, credits, voice access or browser audio permissions. Your written answer is still available.');}
  };
  if(!s.initialized){
    s.initialized=true;
    const option=document.createElement('option');option.value=data.voice_id;option.textContent=data.voice_name;el('voice').appendChild(option);
    loadPuter().then(()=>{if(!s.disposed){el('connect').disabled=false;el('signout').disabled=false;status('Ready when you are. Enable voice to connect through Puter.');}}).catch(()=>status('Puter could not load. Typed and recorded lessons still work.'));
  }
  el('connect').onclick=async()=>{
    try {
      const puter=window.puter;
      if(!puter){status('Voice is still loading. Try again shortly.');return;}
      if(!puter.auth.isSignedIn())await puter.auth.signIn();
      s.enabled=true;el('speak').disabled=true;status('Checking available teaching voices…');
      try {
        const result=await puter.ai.txt2speech.listVoices({provider:'elevenlabs'});
        const voices=Array.isArray(result)?result:result.voices;
        if(Array.isArray(voices)&&voices.length){
          const candidates=voices.map(v=>({id:v.id||v.voice_id||v.voice,name:v.name||v.voice_id||v.id})).filter(v=>v.id&&v.name);
          const valid=candidates.filter(v=>v.id===data.voice_id||/professional british male|clear, engaging educator|warm, captivating storyteller|informative, educational|complex concept explainer/i.test(v.name)).slice(0,8);
          if(valid.length){el('voice').replaceChildren();for(const v of valid){const opt=document.createElement('option');opt.value=v.id;opt.textContent=v.name;el('voice').appendChild(opt);}
          const preferred=valid.find(v=>v.id===data.voice_id)||valid.find(v=>/professional british male/i.test(v.name));
          if(preferred)el('voice').value=preferred.id;else status('Preferred voice is unavailable through Puter. Choose an available teaching voice.');}
        }
      }catch{status('Voice enabled; the voice list could not load. Try the selected voice.');}
      el('speak').disabled=!s.data.text;status('Voice enabled. Talk to Tex, or play the latest reply.');
    }catch{status('Puter sign-in was cancelled or blocked. Allow its sign-in popup and try again.');}
  };
  el('speak').onclick=speak;
  el('pause').onclick=()=>{if(s.audio){s.audio.pause();status('Audio paused.');}if(s.recognition){s.recognition.onend=null;s.recognition.abort();s.recognition=null;}};
  el('resume').onclick=()=>{if(s.audio)s.audio.play().then(()=>status('Tex is speaking.')).catch(()=>status('Press Read response to restart playback.'));};
  el('listen').onclick=listen;
  el('stop').onclick=()=>{abort();s.enabled=false;el('auto').checked=false;el('handsfree').checked=false;el('speak').disabled=true;status('Voice stopped. Microphone is off.');};
  el('signout').onclick=async()=>{el('stop').onclick();try{await window.puter.auth.signOut();status('Signed out of Puter. Voice and microphone are off.');}catch{status('Voice stopped. Puter sign-out could not complete; try again.');}};
  if(s.enabled)el('speak').disabled=!data.text;
  if(s.enabled&&data.text&&data.reply_id!==s.last&&el('auto').checked)speak();
  return ()=>{s.disposed=true;abort();instances.delete(parentElement);};
}
"""

_VOICE = st.components.v2.component("tex_puter_voice", html=_HTML, css=_CSS, js=_JS)


def render_puter_voice(text, *, key):
    text = decode_action(text)[0]
    return _VOICE(data={"text": text, "reply_id": hashlib.sha256(text.encode()).hexdigest(),
                        "voice_id": VOICE_ID, "voice_name": VOICE_NAME},
                  key=key, on_utterance_change=lambda: None)
