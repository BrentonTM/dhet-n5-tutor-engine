import assert from 'node:assert/strict';
import fs from 'node:fs';
const source=fs.readFileSync(new URL('../ui/components/puter_voice.js',import.meta.url),'utf8');
const {default:render,encodeWav,microphoneError}=await import('data:text/javascript;base64,'+Buffer.from(source).toString('base64'));
const tick=()=>new Promise(resolve=>setImmediate(resolve));
const flush=async()=>{for(let i=0;i<8;i++)await tick();};
function element(){return{dataset:{},disabled:false,checked:false,hidden:false,value:'',textContent:'',src:'',
  appendChild(item){if(!this.value)this.value=item.value;},replaceChildren(...items){this.value=items[0]?.value||'';},
  pause(){this.paused=true;},removeAttribute(name){if(name==='src')this.src='';},load(){}};}
function fixture(){
  const nodes=new Map(),parentElement={querySelector(id){if(!nodes.has(id))nodes.set(id,element());return nodes.get(id);}};
  const node=id=>parentElement.querySelector('#'+id);node('review').hidden=node('capture').hidden=true;
  let data={text:'A short lesson.',reply_id:'one',voice_id:'voice-test',voice_name:'Test teaching voice'};
  const turns=[],props=()=>({parentElement,data,setTriggerValue:(key,value)=>turns.push({key,value})});
  let cleanup=render(props());
  return{node,turns,rerender(next){data={...data,...next};cleanup=render(props());},cleanup(){cleanup();}};
}
globalThis.document={createElement:element,head:{appendChild(script){queueMicrotask(()=>script.onerror?.());}}};
globalThis.requestAnimationFrame=()=>1;globalThis.cancelAnimationFrame=()=>{};
const requests=[];let speechCalls=0,deferSpeech;
function audio(){return{pause(){this.paused=true;},removeAttribute(){},load(){},play(){speechCalls++;queueMicrotask(()=>this.onended?.());return Promise.resolve();}};}
const puter={auth:{isSignedIn:()=>true,signOut:async()=>{}},ai:{txt2speech:Object.assign(
  async(text,options)=>{requests.push({text,options});return deferSpeech?await deferSpeech:audio();},
  {listVoices:async()=>[{id:'voice-test',name:'Test teaching voice'}]})}};
const streams=[],recorders=[],mediaRequests=[];let micError=null,pendingMic=null,decodeOverride=null;
function stream(){const track={stopped:false,stop(){this.stopped=true;}};const value={track,getTracks:()=>[track]};streams.push(value);return value;}
function decoded(silent=false){const samples=Float32Array.from({length:4800},(_,i)=>silent?0:.2*Math.sin(i/10));return{sampleRate:48000,length:samples.length,numberOfChannels:1,getChannelData:()=>samples};}
let decodedAudio=decoded();
class FakeContext{
  resume(){return Promise.resolve();}close(){this.closed=true;return Promise.resolve();}
  createAnalyser(){return{fftSize:256,getByteTimeDomainData(values){values.fill(140);},disconnect(){}};}
  createMediaStreamSource(){return{connect(){},disconnect(){}};}
  decodeAudioData(){return decodeOverride||Promise.resolve(decodedAudio);}
}
class FakeRecorder{
  static isTypeSupported(type){return type.startsWith('audio/webm');}
  constructor(input,options){this.input=input;this.options=options;this.state='inactive';recorders.push(this);}
  start(){this.state='recording';}
  stop(){this.state='inactive';queueMicrotask(()=>{this.ondataavailable?.({data:new Blob(['fake compressed microphone bytes'])});this.onstop?.();});}
}
Object.defineProperty(globalThis,'navigator',{configurable:true,value:{mediaDevices:{
  async getUserMedia(constraints){mediaRequests.push(constraints);if(micError)throw micError;return pendingMic?await pendingMic:stream();},
  async enumerateDevices(){return[{kind:'audioinput',deviceId:'test-mic',label:'Test microphone'}];}
}}});
globalThis.window={puter,MediaRecorder:FakeRecorder,AudioContext:FakeContext,isSecureContext:true};

// Capture must work with no Web Speech API and without enabling Puter playback.
const capture=fixture();await flush();
assert.equal(requests.length,0,'mount must not use speech credits');
assert.equal(mediaRequests.length,0,'mount must not request microphone permission');
await capture.node('listen').onclick();
assert.equal(capture.node('listen').textContent,'Finish recording');
assert(capture.node('input-level').value>0,'meter must reflect the captured stream');
assert.equal(requests.length,0,'recording must not need Puter');
assert.equal(capture.turns.length,0,'audio must stay local until Send recording');
await capture.node('listen').onclick();await flush();
assert(streams.at(-1).track.stopped,'finishing must release the microphone');
assert.equal(capture.node('review').hidden,false);
assert.equal(capture.node('send-recording').disabled,false);
capture.node('send-recording').onclick();capture.node('send-recording').onclick();
assert.equal(capture.turns.length,1,'double clicks must not send a clip twice');
assert.equal(capture.turns[0].key,'recording');
const payload=capture.turns[0].value,wav=Buffer.from(payload.audio_base64,'base64');
assert.equal(payload.mime_type,'audio/wav');assert.equal(wav.toString('ascii',0,4),'RIFF');
assert.equal(wav.readUInt32LE(24),16000);assert.equal(wav.readUInt16LE(22),1);
capture.cleanup();assert(capture.node('preview').paused,'unmount must stop preview playback');

const chosen=fixture();chosen.node('microphone').value='test-mic';await chosen.node('listen').onclick();
assert.deepEqual(mediaRequests.at(-1).audio.deviceId,{exact:'test-mic'});
chosen.node('stop').onclick();await flush();assert(streams.at(-1).track.stopped);
assert.equal(chosen.turns.length,0);assert.equal(chosen.node('review').hidden,true);chosen.cleanup();

// Specific errors must survive termination instead of becoming "No speech captured".
for(const[name,expected]of[['NotAllowedError','blocked'],['NotFoundError','No microphone'],['NotReadableError','could not be opened'],['OverconstrainedError','selected microphone']]){
  const failed=fixture();micError={name};await failed.node('listen').onclick();await flush();
  assert(failed.node('status').textContent.includes(expected),name);assert.equal(failed.node('listen').disabled,false);
  assert.equal(failed.turns.length,0);failed.cleanup();micError=null;
}
assert(microphoneError({name:'NotSupportedError'}).includes('message box'));
const interrupted=fixture();await interrupted.node('listen').onclick();
recorders.at(-1).onerror({error:{name:'NotReadableError'}});await flush();
assert(interrupted.node('status').textContent.includes('could not be opened'));
assert(streams.at(-1).track.stopped);assert.equal(interrupted.turns.length,0);interrupted.cleanup();

// Silence must be diagnosed before sending.
decodedAudio=decoded(true);const silent=fixture();
await silent.node('listen').onclick();await silent.node('listen').onclick();await flush();
assert(silent.node('status').textContent.includes('No sound'));assert.equal(silent.node('send-recording').disabled,true);
silent.node('send-recording').onclick();assert.equal(silent.turns.length,0);silent.cleanup();decodedAudio=decoded();

// Cancellation while permission is pending must release a late stream.
let resolveMic;pendingMic=new Promise(resolve=>resolveMic=resolve);
const pending=fixture(),waiting=pending.node('listen').onclick();pending.node('stop').onclick();
const lateStream=stream();resolveMic(lateStream);await waiting;await flush();
assert(lateStream.track.stopped);assert.equal(pending.node('review').hidden,true);
assert.equal(pending.turns.length,0);pending.cleanup();pendingMic=null;

// Stop during conversion must suppress late audio and review.
let resolveDecode;decodeOverride=new Promise(resolve=>resolveDecode=resolve);
const converting=fixture();await converting.node('listen').onclick();await converting.node('listen').onclick();await tick();
converting.node('stop').onclick();resolveDecode(decodedAudio);await flush();
assert.equal(converting.node('review').hidden,true);assert.equal(converting.turns.length,0);
converting.cleanup();decodeOverride=null;

// Opposite-phase stereo channels must not cancel speech.
const positive=Float32Array.from({length:4800},(_,i)=>.2*Math.sin(i/10)),negative=Float32Array.from(positive,value=>-value);
assert(encodeWav({sampleRate:48000,length:4800,numberOfChannels:2,getChannelData:i=>i?negative:positive}).peak>.1);
assert.throws(()=>encodeWav({sampleRate:16000,length:16000*62,numberOfChannels:1}),/long/);

// Playback still needs explicit opt-in, chunks replies and cancels late audio.
const playback=fixture();await flush();const beforePlayback=requests.length;
await playback.node('connect').onclick();await playback.node('speak').onclick();
assert.equal(requests[beforePlayback].options.provider,'elevenlabs');assert.equal(requests[beforePlayback].options.voice,'voice-test');
assert(speechCalls>0);playback.node('auto').checked=true;
playback.rerender({text:'A long lesson. '.repeat(600),reply_id:'two'});await flush();
assert(requests.length>beforePlayback+2);assert(requests.every(request=>request.text.length<=2800));
const count=requests.length;playback.rerender({});await flush();assert.equal(requests.length,count,'no duplicate speech charges');
playback.node('auto').checked=false;let resolveSpeech;deferSpeech=new Promise(resolve=>resolveSpeech=resolve);
const speaking=playback.node('speak').onclick();await tick();const beforeLate=speechCalls;
playback.node('stop').onclick();resolveSpeech(audio());await speaking;assert.equal(speechCalls,beforeLate);
assert.equal(playback.node('handsfree').checked,false);playback.cleanup();deferSpeech=null;

// A failed optional playback SDK must not block recording.
window.puter=undefined;const noSdk=fixture();await flush();await noSdk.node('listen').onclick();
assert.equal(recorders.at(-1).state,'recording');noSdk.cleanup();await flush();window.puter=puter;
assert(streams.every(value=>value.track.stopped),'every microphone track must be released');
console.log('Tex voice PASS: direct capture without Puter/Web Speech, WAV handoff, review/send, meter, microphone selection, errors, silence, cancellation, stereo and playback');
