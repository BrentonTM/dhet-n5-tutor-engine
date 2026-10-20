import os
import sqlite3
import yaml
from datetime import datetime

def load_config():
    config_path = os.path.join("config", "settings.yaml")
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

def init_error_db():
    config = load_config()
    error_db_path = os.path.join("data", "databases", "error_tracker.db")

    os.makedirs(os.path.dirname(error_db_path), exist_ok=True)

    conn = sqlite3.connect(error_db_path)
    cursor = conn.cursor()

    # Table 1: Log of individual user mistakes
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS error_logs (
        error_id INTEGER PRIMARY KEY AUTOINCREMENT,
        topic_id INTEGER NOT NULL,
        subject_code TEXT NOT NULL,
        question_reference TEXT,
        error_type TEXT CHECK(error_type IN (
            'Conceptual Gap', 
            'Calculation Error', 
            'Formula Misapplication', 
            'Definition/Terminology Error', 
            'Misread Question'
        )) NOT NULL,
        user_response TEXT,
        correct_answer TEXT,
        explanation TEXT,
        timestamp TEXT NOT NULL,
        resolved_status INTEGER DEFAULT 0
    )
    """)

    # Table 2: Error frequency summary per topic
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS error_analytics (
        topic_id INTEGER PRIMARY KEY,
        subject_code TEXT NOT NULL,
        total_errors INTEGER DEFAULT 0,
        conceptual_errors INTEGER DEFAULT 0,
        calculation_errors INTEGER DEFAULT 0,
        last_error_date TEXT
    )
    """)

    conn.commit()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]

    conn.close()

    print(f"[SUCCESS] Error Database initialized at: {error_db_path}")
    print(f" -> Tables Created: {', '.join(tables)}")

if __name__ == "__main__":
    print("=== Phase 8: Building Error Database ===")
    init_error_db()