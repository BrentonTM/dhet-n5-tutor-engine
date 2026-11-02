# Trentox Tutor AI

This repository contains the Streamlit application for the Trentox Tutor AI engineering study workspace.

## Cloud AI setup

The app interface and its AI requests run from Streamlit Community Cloud. **ASK TX sends requests directly to Google Gemini; it does not need OmniRoute or a process running on your laptop.**

Add this key in the deployed app's **Manage app → Settings → Secrets**:

```toml
GEMINI_API_KEY = "your-Google-Gemini-API-key"
```

Keep the real key out of GitHub. The app can display course content without the key, but AI chat and answer review need it.

For local development, copy `.env.example` to `.env` and add your key there.

## Original exam pages

Digital Electronics N4 practice and mock exams now use 72 question groups from 12 bundled question papers in `data/past_papers/sources/DIGI-N4/`. The app displays the original PDF pages so overbars, binary subscripts, tables and circuit diagrams remain intact. Source question numbers and printed question totals are retained. Pages can include adjacent questions; answer the source number shown above the viewer. Memorandum placeholders and cover pages are excluded. Other subjects continue using the legacy database with exact subject and level matching.

`data/past_papers/source_questions.json` records each source file, SHA-256 digest, page range and question total. Rebuild it with `python tools/build_source_questions.py PATH_TO_DIGITAL_N4_PAPERS`. The builder copies original files unchanged and reports scanned papers without extractable question headings; these require manual indexing before inclusion. The four currently unindexed scans are the August 2023, August 2025, November 2025 and April 2026 papers. No verified memo is bundled with this index, so AI feedback is explicitly an engineering assessment rather than an official marking memo. The tutor receives the original question pages for guidance and grading.

The native PDF viewer needs the `streamlit[pdf]` extra included in `requirements.txt`.

## Gemini troubleshooting

Both `GEMINI_API_KEY` and `GOOGLE_API_KEY` are accepted from the environment or Streamlit Secrets. Keep keys in Secrets, never in GitHub or chat. Text chat and attachment review share the same current-model fallback and limited retries. The app distinguishes rejected keys, project permissions, quota/rate limits, unavailable models, empty replies and temporary service failures. Provider exception bodies and key values are not displayed or logged.

Optional Streamlit Secrets settings:

```toml
GEMINI_MODEL = "gemini-3.8-flash"
GEMINI_FALLBACK_MODELS = "gemini-3.6-flash,gemini-3.1-flash-lite"
```

See Google's [model catalogue](https://aistudio.google.com/docs/models) and [troubleshooting guide](https://aistudio.google.com/docs/troubleshooting). A deployment's actual key permissions and quota must be checked in its Google AI Studio project; the tests use a fake client and do not make billable API calls.

Run regression checks with `python -m unittest discover -s tests -v`.

