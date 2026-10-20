# CONFIGURATION_REQUIRED.md

This file tracks external dependencies, API keys, and user inputs required for full multi-phase system operation.

## 1. Required User Inputs & Files
- [ ] **DHET Curriculum Documents:** Place PDF/JSON curriculum files into `data/dhet_curriculum/`.
- [ ] **Exam Timetables:** Place timetable PDFs/CSV files into `data/timetables/`.
- [ ] **Past Exam Papers:** Place past paper PDFs and memo files into `data/past_papers/`.

## 2. API Keys & Credentials (If needed in future phases)
- [ ] **LLM / Tutor Engine API Key:** Set `OPENAI_API_KEY` or custom LLM endpoint in `config/settings.yaml` if external AI service is used.
- [ ] **Voice Synthesis Model:** Optional voice model selection in `config/settings.yaml`.

## 3. Next Steps
Once you add curriculum or timetable files to their respective folders, run the respective ingestion scripts in Phase 4 and Phase 5.
