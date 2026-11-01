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
