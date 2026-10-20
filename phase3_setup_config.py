
import yaml

# 1. Create default configuration YAML
CONFIG_CONTENT = {
    "system": {
        "app_name": "DHET Tutor & Exam Strategy Engine",
        "version": "1.0.0",
        "environment": "development",
        "log_level": "INFO"
    },
    "paths": {
        "curriculum_dir": "data/dhet_curriculum",
        "timetables_dir": "data/timetables",
        "databases_dir": "data/databases",
        "past_papers_dir": "data/past_papers"
    },
    "databases": {
        "curriculum_db": "data/databases/curriculum.db",
        "mastery_db": "data/databases/mastery.db",
        "error_db": "data/databases/error.db",
        "past_paper_db": "data/databases/past_papers.db"
    },
    "planner": {
        "default_daily_study_hours": 4.0,
        "spaced_repetition_algorithm": "SM2"
    },
    "voice": {
        "enabled": False,
        "engine": "pyttsx3"
    }
}

# 2. Create CONFIGURATION_REQUIRED.md template
REQ_DOC_CONTENT = """# CONFIGURATION_REQUIRED.md

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
"""

def setup_configuration():
    print("=== Phase 3: Setting Up System Configuration ===")
    
    # Save settings.yaml
    config_path = "config/settings.yaml"
    with open(config_path, "w") as f:
        yaml.dump(CONFIG_CONTENT, f, default_flow_style=False)
    print(f"[CREATED] Configuration file: {config_path}")
    
    # Save CONFIGURATION_REQUIRED.md
    doc_path = "CONFIGURATION_REQUIRED.md"
    with open(doc_path, "w") as f:
        f.write(REQ_DOC_CONTENT)
    print(f"[CREATED] User requirement guide: {doc_path}")

if __name__ == "__main__":
    setup_configuration()