const instances = new WeakMap();
const MAX_SECONDS = 60;
const MAX_BYTES = 8 * 1024 * 1024;
let sdk;

function loadPuter() {
  if (window.puter) return Promise.resolve(window.puter);
  if (!sdk) sdk = new Promise((resolve, reject) => {
    const script = document.createElement('script');
    script.src = 'https://js.puter.com/v2/';
    script.onload = () => resolve(window.puter);
    script.onerror = () => { sdk = null; reject(new Error('sdk')); };
    document.head.appendChild(script);
  });
  return sdk;
}

export function microphoneError(error) {
  switch (error?.name) {
    case 'NotAllowedError': case 'PermissionDeniedError': case 'SecurityError':
      return 'Microphone access is blocked. Allow microphone access for this site in your browser, then try again.';
    case 'NotFoundError': case 'DevicesNotFoundError':
      return 'No microphone was found. Connect a microphone and try again.';
    case 'NotReadableError': case 'TrackStartError':
      return 'The microphone could not be opened. Close other apps using it and check your system microphone settings.';
    case 'OverconstrainedError':
      return 'The selected microphone is unavailable. Choose Default microphone in Settings and try again.';
    case 'NotSupportedError':
      return 'Recording is unavailable in this browser. Try the microphone in the message box or type your message.';
    default:
      return 'The recording could not be captured. Check your microphone and try again, or use the microphone in the message box.';
  }
}

export function encodeWav(audio) {
  const rate = 16000;
  if (!Number.isFinite(audio.sampleRate) || audio.sampleRate <= 0 ||
      !Number.isInteger(audio.length) || audio.length <= 0 ||
      !Number.isInteger(audio.numberOfChannels) || audio.numberOfChannels < 1 || audio.numberOfChannels > 8) {
    throw new Error('Invalid audio');
  }
  const duration = audio.length / audio.sampleRate;
  if (duration > MAX_SECONDS + 1) throw new Error('Recording too long');
  const frames = Math.min(MAX_SECONDS * rate, Math.floor(duration * rate));
  if (!frames) throw new Error('Empty audio');
  const buffer = new ArrayBuffer(44 + frames * 2);
  const view = new DataView(buffer);
  const write = (offset, text) => { for (let i = 0; i < text.length; i++) view.setUint8(offset + i, text.charCodeAt(i)); };
  write(0, 'RIFF'); view.setUint32(4, 36 + frames * 2, true); write(8, 'WAVE');
  write(12, 'fmt '); view.setUint32(16, 16, true); view.setUint16(20, 1, true);
  view.setUint16(22, 1, true); view.setUint32(24, rate, true); view.setUint32(28, rate * 2, true);
  view.setUint16(32, 2, true); view.setUint16(34, 16, true); write(36, 'data'); view.setUint32(40, frames * 2, true);
  const channels = Array.from({length: audio.numberOfChannels}, (_, index) => audio.getChannelData(index));
  // Choose the strongest channel so opposite-phase stereo cannot cancel speech.
  const stride = Math.max(1, Math.floor(audio.length / 4096));
  const energy = channel => { let sum = 0; for (let i = 0; i < audio.length; i += stride) sum += channel[i] ** 2; return sum; };
  const primary = channels.reduce((best, channel) => energy(channel) > energy(best) ? channel : best);
  let peak = 0;
  for (let i = 0; i < frames; i++) {
    const position = i * audio.sampleRate / rate;
    const lower = Math.floor(position), upper = Math.min(lower + 1, audio.length - 1), fraction = position - lower;
    let sample = primary[lower] * (1 - fraction) + primary[upper] * fraction;
    sample = Number.isFinite(sample) ? Math.max(-1, Math.min(1, sample)) : 0;
    peak = Math.max(peak, Math.abs(sample));
    view.setInt16(44 + i * 2, Math.round(sample * (sample < 0 ? 32768 : 32767)), true);
  }
  return {buffer, peak, durationMs: Math.round(frames / rate * 1000)};
}

function base64(buffer) {
  const bytes = new Uint8Array(buffer);
  let text = '';
  for (let i = 0; i < bytes.length; i += 32768) text += String.fromCharCode(...bytes.subarray(i, i + 32768));
  return btoa(text);
}

export default function({parentElement, data, setTriggerValue}) {
  let s = instances.get(parentElement);
  if (!s) {
    s = {audio: null, enabled: false, generation: 0, last: null, busy: false, disposed: false,
      stream: null, recorder: null, capturePending: false, preparing: false, recording: null, previewUrl: null};
    instances.set(parentElement, s);
  }
  s.data = data; s.emit = setTriggerValue;
  const el = id => parentElement.querySelector('#' + id);
  const status = text => {
    if (s.disposed) return;
    el('status').textContent = text;
    const mode = /Tex is speaking/i.test(text) ? 'speaking' : /^Listening/i.test(text) ? 'listening' :
      /generating|thinking|checking|loading|connecting|preparing|sending/i.test(text) ? 'thinking' :
      /could not|couldn't|unavailable|cancelled|blocked|no sound|no microphone/i.test(text) ? 'error' :
      /paused/i.test(text) ? 'paused' : /enabled|ready/i.test(text) ? 'ready' : 'off';
    parentElement.querySelector('.tex-console').dataset.mode = mode;
    el('phase').textContent = {speaking:'SPEAKING',listening:'RECORDING',thinking:'THINKING',error:'CHECK MIC',paused:'PAUSED',ready:'READY',off:'VOICE OFF'}[mode];
  };
  const releaseCapture = (discard = true) => {
    clearTimeout(s.captureTimer); s.captureTimer = null;
    if (s.levelFrame != null) cancelAnimationFrame(s.levelFrame);
    s.levelFrame = null;
    if (s.recorder) {
      const recorder = s.recorder; s.recorder = null;
      if (discard) recorder.onstop = recorder.ondataavailable = recorder.onerror = null;
      if (recorder.state !== 'inactive') recorder.stop();
    }
    if (s.stream) { for (const track of s.stream.getTracks()) track.stop(); s.stream = null; }
    if (s.meterSource) s.meterSource.disconnect();
    if (s.analyser) s.analyser.disconnect();
    s.meterSource = s.analyser = null;
    if (s.meterContext) { s.meterContext.close().catch(() => {}); s.meterContext = null; }
    s.capturePending = false;
    if (!s.disposed) {
      el('listen').textContent = 'Talk to Tex'; el('listen').disabled = s.preparing;
      el('microphone').disabled = false; el('capture').hidden = true; el('input-level').value = 0;
    }
  };
  const clearReview = () => {
    if (s.previewUrl) { URL.revokeObjectURL(s.previewUrl); s.previewUrl = null; }
    s.recording = null;
    const preview = el('preview');
    if (preview) { preview.pause(); preview.removeAttribute('src'); preview.load(); }
    if (!s.disposed) el('review').hidden = true;
  };
  const abort = () => {
    s.generation++; s.preparing = false;
    releaseCapture(); clearReview();
    if (s.settle) { s.settle(); s.settle = null; }
    if (s.audio) { s.audio.pause(); s.audio.removeAttribute('src'); s.audio.load(); s.audio = null; }
    s.busy = false;
  };
  const refreshMicrophones = async () => {
    try {
      const devices = await navigator.mediaDevices.enumerateDevices();
      if (s.disposed) return;
      const select = el('microphone'), selected = select.value;
      const defaultOption = document.createElement('option'); defaultOption.value = ''; defaultOption.textContent = 'Default microphone';
      select.replaceChildren(defaultOption);
      let index = 0;
      for (const device of devices.filter(device => device.kind === 'audioinput')) {
        if (!device.deviceId) continue;
        const option = document.createElement('option'); option.value = device.deviceId;
        option.textContent = device.label || 'Microphone ' + (++index); select.appendChild(option);
      }
      select.value = devices.some(device => device.deviceId === selected) ? selected : '';
    } catch { /* A device-list failure must not interrupt an active recording. */ }
  };
  const startMeter = stream => {
    try {
      const Context = window.AudioContext || window.webkitAudioContext;
      s.meterContext = new Context(); s.meterContext.resume().catch(() => {});
      s.analyser = s.meterContext.createAnalyser(); s.analyser.fftSize = 256;
      s.meterSource = s.meterContext.createMediaStreamSource(stream); s.meterSource.connect(s.analyser);
      const values = new Uint8Array(s.analyser.fftSize);
      const update = () => {
        if (!s.recorder || s.disposed || !s.analyser) return;
        s.analyser.getByteTimeDomainData(values);
        let squares = 0;
        for (const value of values) squares += ((value - 128) / 128) ** 2;
        el('input-level').value = Math.min(1, Math.sqrt(squares / values.length) * 4);
        s.levelFrame = requestAnimationFrame(update);
      };
      update();
    } catch { /* Recording still works when the optional input meter cannot start. */ }
  };
  const prepareRecording = async (chunks, generation) => {
    let context;
    try {
      if (!chunks.length || !chunks.some(chunk => chunk.size)) throw new Error('Empty audio');
      const Context = window.AudioContext || window.webkitAudioContext;
      context = new Context();
      const decoded = await context.decodeAudioData(await new Blob(chunks).arrayBuffer());
      if (generation !== s.generation || s.disposed) return;
      const wav = encodeWav(decoded);
      const blob = new Blob([wav.buffer], {type:'audio/wav'});
      s.recording = {id:crypto.randomUUID(),audio_base64:base64(wav.buffer),mime_type:'audio/wav',silent:wav.peak < 1 / 32767,sent:false};
      s.previewUrl = URL.createObjectURL(blob); el('preview').src = s.previewUrl;
      el('review').hidden = false; el('send-recording').disabled = s.recording.silent;
      status(s.recording.silent ? 'No sound was detected. Choose another Microphone in Settings and record again.' : 'Recording ready. Play it back, then choose Send recording.');
    } catch {
      if (generation === s.generation && !s.disposed) status('The recording could not be read. Try recording again, or use the microphone in the message box.');
    } finally {
      if (context) await context.close().catch(() => {});
      if (generation === s.generation && !s.disposed) { s.preparing = false; el('listen').disabled = false; }
    }
  };
  const finishRecording = () => {
    if (!s.recorder || s.recorder.state !== 'recording') return;
    const recorder = s.recorder; s.recorder = null; s.preparing = true;
    el('listen').disabled = true; status('Preparing your recording…'); recorder.stop();
  };
  const listen = async () => {
    if (s.recorder) { finishRecording(); return; }
    if (s.capturePending || s.preparing) return;
    abort();
    if (window.isSecureContext === false || !navigator.mediaDevices?.getUserMedia || !window.MediaRecorder || !(window.AudioContext || window.webkitAudioContext)) {
      status(microphoneError({name:'NotSupportedError'})); return;
    }
    const generation = s.generation; s.capturePending = true; el('listen').disabled = true;
    status('Checking your microphone. Allow access if your browser asks.');
    try {
      const selected = el('microphone').value;
      const stream = await navigator.mediaDevices.getUserMedia({audio:{deviceId:selected ? {exact:selected} : undefined,echoCancellation:true,noiseSuppression:true,autoGainControl:true},video:false});
      if (generation !== s.generation || s.disposed) { for (const track of stream.getTracks()) track.stop(); return; }
      s.stream = stream; s.capturePending = false;
      const mimeType = ['audio/webm;codecs=opus','audio/mp4','audio/ogg;codecs=opus'].find(type => window.MediaRecorder.isTypeSupported?.(type));
      const recorder = new window.MediaRecorder(stream, {...(mimeType ? {mimeType} : {}),audioBitsPerSecond:64000});
      const chunks = []; let bytes = 0;
      recorder.ondataavailable = event => {
        if (generation !== s.generation || s.disposed || !event.data?.size) return;
        bytes += event.data.size;
        if (bytes > MAX_BYTES) { abort(); status('The recording is too large. Try a shorter message.'); return; }
        chunks.push(event.data);
      };
      recorder.onerror = event => {
        if (generation !== s.generation || s.disposed) return;
        abort(); status(microphoneError(event.error));
      };
      recorder.onstop = () => {
        if (generation !== s.generation || s.disposed) return;
        s.recorder = null; s.preparing = true; releaseCapture(false);
        status('Preparing your recording…'); void prepareRecording(chunks, generation);
      };
      s.recorder = recorder; recorder.start(250);
      el('capture').hidden = false; el('microphone').disabled = true;
      el('listen').disabled = false; el('listen').textContent = 'Finish recording';
      status('Listening. Check the input meter, then choose Finish recording.');
      startMeter(stream); void refreshMicrophones();
      s.captureTimer = setTimeout(finishRecording, MAX_SECONDS * 1000);
    } catch (error) {
      if (generation === s.generation && !s.disposed) { abort(); status(microphoneError(error)); }
    }
  };
  const speak = async () => {
    if (!s.enabled || !s.data.text || s.busy || s.capturePending || s.recorder || s.preparing) return;
    abort(); const generation = s.generation; s.busy = true; s.last = s.data.reply_id;
    try {
      const puter = await loadPuter(); let remaining = s.data.text;
      while (remaining && generation === s.generation && !s.disposed) {
        let length = Math.min(2800, remaining.length);
        if (length < remaining.length) { const boundary = remaining.lastIndexOf(' ', length); if (boundary > 1400) length = boundary; }
        const chunk = remaining.slice(0, length); remaining = remaining.slice(length).trimStart();
        status('Generating ElevenLabs speech…');
        const audio = await puter.ai.txt2speech(chunk,{provider:'elevenlabs',voice:el('voice').value || data.voice_id,model:'eleven_flash_v2_5',output_format:'mp3_44100_128'});
        if (generation !== s.generation || s.disposed) { audio.pause(); audio.removeAttribute('src'); audio.load(); return; }
        s.audio = audio;
        await new Promise((resolve,reject) => { s.settle = resolve; audio.onended = () => { s.settle = null; resolve(); }; audio.onerror = () => { s.settle = null; reject(); }; audio.play().then(() => status('Tex is speaking. You can pause or interrupt.')).catch(reject); });
      }
      s.busy = false;
      if (generation === s.generation && !s.disposed) { status('Ready for your answer.'); if (el('handsfree').checked) void listen(); }
    } catch { s.busy = false; if (generation === s.generation) status('Voice could not play. Check Puter sign-in, credits, voice access or browser audio permissions. Your written answer is still available.'); }
  };
  if (!s.initialized) {
    s.initialized = true;
    const option = document.createElement('option'); option.value = data.voice_id; option.textContent = data.voice_name; el('voice').appendChild(option);
    status('Ready to record. Talk to Tex, or enable playback for spoken replies.');
    loadPuter().then(() => {
      if (!s.disposed) { el('connect').disabled = false; el('signout').disabled = false; }
    }).catch(() => { if (!s.disposed && !s.recorder && !s.capturePending && !s.recording) status('Spoken replies are unavailable. You can still record a message or type.'); });
  }
  el('connect').onclick = async () => {
    if (s.recorder || s.capturePending || s.preparing) return;
    try {
      const puter = window.puter;
      if (!puter) { status('Playback is still loading. Recording is ready to use.'); return; }
      if (!puter.auth.isSignedIn()) await puter.auth.signIn();
      s.enabled = true; el('speak').disabled = true; status('Checking available teaching voices…');
      try {
        const result = await puter.ai.txt2speech.listVoices({provider:'elevenlabs'});
        const voices = Array.isArray(result) ? result : result.voices;
        if (Array.isArray(voices) && voices.length) {
          const candidates = voices.map(v => ({id:v.id || v.voice_id || v.voice,name:v.name || v.voice_id || v.id})).filter(v => v.id && v.name);
          const valid = candidates.filter(v => v.id === data.voice_id || /professional british male|clear, engaging educator|warm, captivating storyteller|informative, educational|complex concept explainer/i.test(v.name)).slice(0,8);
          if (valid.length) {
            el('voice').replaceChildren();
            for (const v of valid) { const opt = document.createElement('option'); opt.value = v.id; opt.textContent = v.name; el('voice').appendChild(opt); }
            const preferred = valid.find(v => v.id === data.voice_id) || valid.find(v => /professional british male/i.test(v.name));
            if (preferred) el('voice').value = preferred.id;
          }
        }
      } catch { /* The configured voice can still work when listing voices fails. */ }
      el('speak').disabled = !s.data.text; status('Playback enabled. Talk to Tex, or play the latest reply.');
    } catch { status('Puter sign-in was cancelled or blocked. Recording still works without Puter.'); }
  };
  el('listen').onclick = listen;
  el('retry-recording').onclick = listen;
  el('send-recording').onclick = () => {
    const recording = s.recording;
    if (!recording || recording.silent || recording.sent || s.disposed) return;
    recording.sent = true; el('send-recording').disabled = true; el('preview').pause();
    try {
      status('Sending your recording to Tex…');
      s.emit('recording',{id:recording.id,audio_base64:recording.audio_base64,mime_type:recording.mime_type});
    } catch { recording.sent = false; el('send-recording').disabled = false; status('The recording could not be sent. Try Send recording again.'); }
  };
  el('speak').onclick = speak;
  el('pause').onclick = () => { if (s.audio) { s.audio.pause(); status('Audio paused.'); } };
  el('resume').onclick = () => { if (s.audio) s.audio.play().then(() => status('Tex is speaking.')).catch(() => status('Press Play reply to restart playback.')); };
  el('stop').onclick = () => { abort(); s.enabled = false; el('auto').checked = el('handsfree').checked = false; el('speak').disabled = true; status('Voice stopped. Microphone is off.'); };
  el('signout').onclick = async () => { el('stop').onclick(); try { await window.puter.auth.signOut(); status('Signed out of Puter. Voice and microphone are off.'); } catch { status('Voice stopped. Puter sign-out could not complete; try again.'); } };
  if (s.enabled) el('speak').disabled = !data.text || s.capturePending || !!s.recorder || s.preparing;
  if (s.enabled && data.text && data.reply_id !== s.last && el('auto').checked) void speak();
  return () => { s.disposed = true; abort(); instances.delete(parentElement); };
}
