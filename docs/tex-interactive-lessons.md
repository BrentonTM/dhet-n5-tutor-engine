# Interactive lessons and voice

Generate a lesson in Tutor & lab, then open **Interactive lesson with Tex** and
choose **Start interactive lesson**. Tex uses the lesson and relevant indexed
source excerpts, checks one answer at a time, and offers hints, alternative
explanations, quizzes and recaps. Students can type or submit recorded answers.
Chats are scoped to the subject, topic and lesson content in the current session.
They can be downloaded or cleared. Changing the lesson creates a fresh conversation.

## ElevenLabs through Puter

No ElevenLabs developer API key or separate ElevenLabs agent is required. The
learner enables voice and signs in to Puter. Puter account credits, provider access
and limits apply. The preferred voice is **Eldrin – Crisp British Baritone**,
`6WwXjDDEMyNmFG95zycZ`. The current provider voice list is available after sign-in;
if the preferred voice is unavailable, the learner can choose another listed voice.
Speech uses `eleven_flash_v2_5` and is split into requests of at most 2,800 characters.
The voice panel is also available within the general Tex chat.

Use **Read response**, **Pause audio**, **Resume audio**, **Interrupt / speak** or
**Stop voice**. Automatic playback and listening after each reply are separate
opt-in checkboxes. Speech recognition support depends on the browser and language;
typed input and the existing audio recorder remain available. This is a sequence
of conversational turns through Gemini and ElevenLabs TTS, not an ElevenAgents
full-duplex streaming session. There is a model/synthesis delay between turns.

Tex's spoken text is sent to Puter/ElevenLabs only after voice is enabled and playback
requested. Browser live speech recognition may use the browser vendor's service;
the transcript is then sent to Google Gemini. Typed/recorded lesson messages and
relevant lesson context use the app's existing Gemini service. Puter tokens remain
in the browser's SDK and are never sent to the Python server or placed in source.

## Verification

`python -m unittest tests.test_interactive_lesson tests.test_tex_partner tests.test_gemini_client -q`

`node tests/test_puter_voice.mjs`

The voice unit tests use provider and microphone doubles. A real Puter sign-in and
successful audio playback are separate live acceptance checks. Full Streamlit
AppTest checks cover app startup, lesson start, follow-up and clear/end behavior.
