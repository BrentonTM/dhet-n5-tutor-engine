"""Keyless ElevenLabs speech through each learner's Puter account, opt-in only."""

import hashlib
from pathlib import Path
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
    <button id="connect" disabled>Enable playback</button>
    <button id="listen" class="primary" title="Interrupt Tex and speak your answer">Talk to Tex</button>
    <button id="stop" title="Stop playback and turn off the microphone">Stop</button>
  </div>
  <div id="capture" class="capture-feedback" hidden>
    <label class="level-label">Microphone input <meter id="input-level" min="0" max="1" value="0" aria-label="Microphone input level"></meter></label>
    <p class="capture-note">Speak, then choose Finish recording. Up to 60 seconds.</p>
  </div>
  <div id="review" class="recording-review" hidden>
    <audio id="preview" controls aria-label="Your recorded message"></audio>
    <div class="review-controls"><button id="send-recording" class="primary">Send recording</button><button id="retry-recording">Record again</button></div>
  </div>
  <button id="speak" class="play-reply" disabled>Play reply</button>
  <p class="meta">ElevenLabs via Puter · account limits apply</p>
  <details class="settings"><summary>Settings</summary>
    <div class="playback"><button id="pause">Pause audio</button><button id="resume">Resume audio</button></div>
    <label class="check"><input id="auto" type="checkbox"> Read new replies automatically</label>
    <label class="check"><input id="handsfree" type="checkbox"> Record after each reply</label>
    <label class="field">Voice <select id="voice"></select></label>
    <label class="field">Microphone <select id="microphone"><option value="">Default microphone</option></select></label>
    <p class="privacy">ElevenLabs voice through Puter. Puter sign-in, account credits and limits apply.
    Puter is only needed for spoken replies. Recording does not need a Puter account.
    Your recording stays in this browser until you choose Send recording; it then goes to Google Gemini.
    If the input meter stays empty, choose another microphone here. Headphones are recommended.
    You can also use the microphone in the message box or type.</p>
    <button id="signout" class="signout" disabled>Sign out of Puter</button>
  </details>
</section>
"""

_CSS = """
:host {color:var(--st-text-color, #e7eef6);font-family:var(--st-font,system-ui,sans-serif);}
* {box-sizing:border-box;}
.tex-console {--tex-accent:#6ee7dd;--tex-ink:var(--st-text-color,#e7eef6);width:100%;min-width:0;position:relative;
  padding:16px;border:1px solid var(--st-border-color,#28384c);border-radius:22px;
  background:var(--st-secondary-background-color,#101b2c);color:var(--tex-ink);overflow:hidden;}
header {padding-right:72px;display:flex;justify-content:space-between;align-items:center;gap:12px;}
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
.capture-feedback,.recording-review{margin-top:14px;}.capture-note{font-size:12px;line-height:1.5;opacity:.75;}
.level-label{display:flex;align-items:center;gap:10px;font-size:12px;}.level-label meter{flex:1;min-width:0;height:12px;}
.recording-review audio{width:100%;height:40px;}.review-controls{display:flex;gap:8px;margin-top:10px;}.review-controls button{flex:1;}
[hidden]{display:none!important;}
.meta{text-align:center;font-size:10px;opacity:.5;margin:5px 0 0;}
.settings {margin:0;padding:0;border:0;}
.settings[open] {margin-top:10px;border-top:1px solid var(--st-border-color,#28384c);padding-top:10px;}
summary {position:absolute;top:14px;right:14px;cursor:pointer;font-size:11px;opacity:.7;list-style:none;padding:4px;}
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

_JS = (Path(__file__).with_name("components") / "puter_voice.js").read_text(encoding="utf-8")

_VOICE = st.components.v2.component("tex_puter_voice", html=_HTML, css=_CSS, js=_JS)


def render_puter_voice(text, *, key):
    text = decode_action(text)[0]
    return _VOICE(data={"text": text, "reply_id": hashlib.sha256(text.encode()).hexdigest(),
                        "voice_id": VOICE_ID, "voice_name": VOICE_NAME},
                  key=key, on_utterance_change=lambda: None, on_recording_change=lambda: None)
