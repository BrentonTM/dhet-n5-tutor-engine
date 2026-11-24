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
and limits apply. The preferred voice is **James – Professional British Male**,
`lUTamkMw7gOzZbFIwmq4`. A curated list of teaching voices from the current provider catalog is available after sign-in;
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


## App assistance and conversational style

Tex can explain all educational workspaces using a feature guide, the real programme
catalogue, selected course metadata, current lesson, relevant indexed reference
excerpts and recent session topic checks. Simple commands such as **Open the 3D lab**
run immediately. Richer requests can select a programme, N-level, subject, lesson
topic, available 3D model or game. **Start a lesson on …** can request lesson generation.
Other destinations include practice, papers/resources, progress, formulas, analytics,
flashcards, simulators, exam calendar, career tools, Money Class, display settings,
reminder controls, the guide and the privacy policy. Availability follows the selected
course's implemented features; Tex reports when an action is unavailable.

Actions use a fixed schema and are checked against the actual catalogue and model
list. They apply before Streamlit creates the affected widgets. Navigation receives
an execution receipt. Tex cannot run arbitrary code, read credentials, access another
student, submit/grade exams, change scores or manipulate iframe sliders. It explains
those controls instead. Requested navigation is separate from a how-to question.
Tool markup is removed from displayed and spoken replies.

Tex uses occasional kind humour, clear everyday analogies and engineering puns.
It avoids ridicule and keeps numerical work precise. A student can ask for a serious
tone at any time.

Additional checks: `python -m unittest tests.test_tex_app_control tests.test_home_app -q`.
