# Trentox Google Play release preparation

The current evidence comes from the Streamlit web app. Use this worksheet to prepare Play Console answers, then confirm them against the actual Android build, its SDKs, the production hosting setup and the Gemini project before submission.

| Candidate Data safety type | Current evidence and purpose | Draft collection |
| --- | --- | --- |
| Name, email address, user IDs | Google sign-in returns identity claims to Streamlit. Trentox uses the Google subject to derive a learner identifier. A chosen nickname personalizes Tex and can be sent to Gemini. Account management, app functionality and personalization. | Required for current signed-in workflow. Verify exact claims and disclosures in Android. |
| Voice or sound recordings | Optional Tex chat or practice recording. The server receives audio and sends it to Gemini when the learner requests transcription or feedback. App functionality. | Optional. Treat as collected. |
| Photos, files and docs | Optional images, PDFs, documents, text or progress files. Answer review may send a file or extracted text to Gemini. Progress import is processed by Trentox. App functionality. | Optional. Treat as collected. |
| Other user-generated content and app activity | Learner text, transcripts, answers, course selection, progress, preferences and lab reflections. When account history is enabled, minimal study records are stored in PostgreSQL under a pseudonymous learner ID. Selected context can be sent to Gemini. App functionality and personalization. | Collected where sent off device. Confirm which data is required in the shipped flows. |
| Diagnostics, identifiers and other technical data | Review Streamlit, Android SDKs, crash reporting and any analytics. Confirm actual data and purpose from deployed settings. | Pending verification. |

Do not mark the AI flow as ephemeral simply because Trentox uses session memory. Check provider retention and any logging or data-sharing settings. Determine whether each transfer qualifies for Google Play's service-provider exception using the actual Gemini agreement and configuration. Verify HTTPS on all app and SDK paths before declaring encryption in transit. Review the data inventory again before adding billing or analytics.

- Use the public privacy page at `https://dhet-n5-tutor-engine-rxogmong3h45cfoqv7t6sq.streamlit.app/?privacy=1` after verifying signed-out access. Confirm the release operator and that the public privacy inbox is monitored.
- Confirm how Android sign-in creates or uses an app account. If Play's deletion rule applies, provide and test a discoverable request path inside the Android app and on the web, with an owner workflow for verification and deletion. Sign-out only clears the active session.
- Confirm Gemini billing, logging and data use settings. Decide the target age group before the closed test. Gemini Developer API terms restrict clients directed to or likely to be accessed by under-18 users. If younger learners are in scope, resolve that provider and product requirement before launch.
- Add and test in-app reporting of AI responses, and establish a process to review reports and improve safeguards.
- Build a signed Android App Bundle. Test Google sign-in, microphone permission, PDF viewing, 3D rendering and recovery from network loss on real Android devices. Prepare Play app access instructions, content rating, target audience, store assets, and closed testing where required.
- Prepare a 1024 × 500 feature graphic from the cover design, a 512 × 512 Play icon and screenshots from the actual Android build. [Play preview asset requirements](https://support.google.com/googleplay/android-developer/answer/9866151)
- Complete the Play Console declarations for the release build and keep them in sync with later changes.

Sources: [Play Data safety](https://support.google.com/googleplay/android-developer/answer/10787469) · [User Data policy](https://support.google.com/googleplay/android-developer/answer/10144311) · [Account deletion](https://support.google.com/googleplay/android-developer/answer/13327111) · [AI-generated content policy](https://support.google.com/googleplay/android-developer/answer/13985936) · [Gemini API terms](https://ai.google.dev/gemini-api/terms)
