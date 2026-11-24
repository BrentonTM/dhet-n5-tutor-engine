"""Keyless ElevenLabs speech through each learner's Puter account, opt-in only."""

import hashlib
import streamlit as st
from ui.tex_voice import VOICE_ID, VOICE_NAME
from ui.tex_app_control import decode_action

_HTML = """
<div><button id="connect" disabled>Enable Tex voice</button>
<button id="speak" disabled>Read response</button>
<button id="pause">Pause audio</button><button id="resume">Resume audio</button>
<button id="listen">Interrupt / speak</button><button id="stop">Stop voice</button><button id="signout" disabled>Sign out of Puter</button></div>
<label><input id="auto" type="checkbox"> Read new replies automatically</label>
<label><input id="handsfree" type="checkbox"> Listen after each reply (headphones recommended)</label>
<label>Voice <select id="voice"></select></label>
<label>Speech language <select id="lang"><option value="en-ZA">English (South Africa)</option>
<option value="af-ZA">Afrikaans</option><option value="zu-ZA">isiZulu</option>
<option value="xh-ZA">isiXhosa</option><option value="st-ZA">Sesotho</option></select></label>
<p id="status" role="status" aria-live="polite">Loading voice connection…</p>
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
  const status=text=>{if(!s.disposed) el('status').textContent=text;};
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
    loadPuter().then(()=>{if(!s.disposed){el('connect').disabled=false;el('signout').disabled=false;status('Voice is off. Enable it to sign in to Puter; account credits and limits apply.');}}).catch(()=>status('Puter could not load. Typed and recorded lessons still work.'));
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
      el('speak').disabled=!s.data.text;status('Voice enabled. Click Read response or Interrupt / speak.');
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

_VOICE = st.components.v2.component("tex_puter_voice", html=_HTML, js=_JS)


def render_puter_voice(text, *, key):
    text = decode_action(text)[0]
    st.caption("Optional ElevenLabs voice through Puter. Enabling it requires Puter sign-in; your account's credits and limits apply. Only Tex's spoken reply goes to Puter/ElevenLabs. Live microphone transcription uses your browser's speech service, then sends the transcript to Gemini. You can always type or record below.")
    return _VOICE(data={"text": text, "reply_id": hashlib.sha256(text.encode()).hexdigest(),
                        "voice_id": VOICE_ID, "voice_name": VOICE_NAME},
                  key=key, on_utterance_change=lambda: None)
