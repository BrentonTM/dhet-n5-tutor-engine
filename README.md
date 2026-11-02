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

## Original papers and marking memos

Practice, mock exams and the original-document library cover Digital Electronics N4, Industrial Electronics N5, Industrial Instruments N5 and Mathematics N5. Original PDF pages preserve formulas, overbars, subscripts, circuit diagrams, graphs and table layout for both papers and memos. Source dates are read from the printed covers; downloaded filenames can be misleading.

| Subject | Papers | Memos | Indexed question groups |
|---|---:|---:|---:|
| DIGI-N4 | 16 | 17 | 72 |
| IE-N5 | 18 | 17 | 98 |
| INST-N5 | 17 | 17 | 56 |
| MATH-N5 | 15 | 16 | 48 |

The library contains 133 unique original PDFs, retaining aliases for duplicate downloads. A syllabus found in the exam folder is excluded. Image-based papers and papers with inconsistent totals remain usable as complete original documents, with tutor guidance, while random exams use only complete question sequences whose printed totals add to 100. The April 2020 Industrial Electronics paper's extracted printed totals add to 98, so it is kept out of random selection for review. No source mark allocation is silently changed.

Memos are linked only when exactly one original has the same subject and full printed cover date, and available question totals do not conflict. Eight unmatched memos remain separately available. Six same-date candidate pairs require review because extracted question totals could not be reconciled; those memos remain available separately and are excluded from automatic grading. In particular, the Industrial Instruments paper labelled August 2023 is dated 17 August, but the downloaded memo is dated 4 August; these are not automatically paired. Partially dated covers, such as “XX August 2021”, are not treated as exact matches.

In Practice, use **Browse original question papers and memos** to open or download any original, including scans. **Show matched marking memo** displays the available matching memo. Guidance and grading receive original question, formula and memo pages; repeated pages are combined. Without a matched memo, feedback is explicitly an engineering assessment rather than an official marking memo.

`data/past_papers/source_questions.json` records original-file SHA-256 digests, printed dates, page references, question totals and memo links. `library_audit.json` reports coverage and exceptions. Rebuild from the four subject folders with:

```sh
python tools/build_source_questions.py PATH_TO_PAST_PAPERS_ROOT
```

`tools/source_metadata_overrides.json` records cover metadata visually transcribed from scans. It does not infer formulas from OCR or supply guessed exam dates. The native viewer needs the `streamlit[pdf]` extra in `requirements.txt`.

## Gemini troubleshooting

Both `GEMINI_API_KEY` and `GOOGLE_API_KEY` are accepted from the environment or Streamlit Secrets. Keep keys in Secrets, never in GitHub or chat. Text chat and attachment review share the same current-model fallback and limited retries. The app distinguishes rejected keys, project permissions, quota/rate limits, unavailable models, empty replies and temporary service failures. Provider exception bodies and key values are not displayed or logged.

Optional Streamlit Secrets settings:

```toml
GEMINI_MODEL = "gemini-3.8-flash"
GEMINI_FALLBACK_MODELS = "gemini-3.6-flash,gemini-3.1-flash-lite"
```

See Google's [model catalogue](https://aistudio.google.com/docs/models) and [troubleshooting guide](https://aistudio.google.com/docs/troubleshooting). A deployment's actual key permissions and quota must be checked in its Google AI Studio project; the tests use a fake client and do not make billable API calls.

Run regression checks with `python -m unittest discover -s tests -v`.

