import os
import sqlite3
import yaml
from datetime import datetime


def load_config():
	config_path = os.path.join("config", "settings.yaml")
	with open(config_path, "r") as f:
		return yaml.safe_load(f)


def init_mastery_db():
	config = load_config()
	mastery_db_path = config["databases"]["mastery_db"]
	curriculum_db_path = config["databases"]["curriculum_db"]

	# Ensure output directory exists
	os.makedirs(os.path.dirname(mastery_db_path), exist_ok=True)

	conn_mastery = sqlite3.connect(mastery_db_path)
	cursor_mastery = conn_mastery.cursor()

	# 1. Topic Mastery Table (Stores SM-2 state per topic)
	cursor_mastery.execute("""
	CREATE TABLE IF NOT EXISTS topic_mastery (
		topic_id INTEGER PRIMARY KEY,
		subject_code TEXT NOT NULL,
		module_id INTEGER NOT NULL,
		topic_name TEXT NOT NULL,
		mastery_score REAL DEFAULT 0.0,
		repetition_count INTEGER DEFAULT 0,
		interval_days INTEGER DEFAULT 0,
		ease_factor REAL DEFAULT 2.5,
		last_reviewed TEXT,
		next_review_due TEXT
	)
	""")

	# 2. Study Session Logs Table
	cursor_mastery.execute("""
	CREATE TABLE IF NOT EXISTS study_logs (
		log_id INTEGER PRIMARY KEY AUTOINCREMENT,
		topic_id INTEGER,
		session_date TEXT NOT NULL,
		duration_minutes INTEGER NOT NULL,
		performance_rating INTEGER NOT NULL,
		notes TEXT,
		FOREIGN KEY (topic_id) REFERENCES topic_mastery(topic_id)
	)
	""")

	# Fetch N5 topics from curriculum.db to initialize topic_mastery if empty
	cursor_mastery.execute("SELECT COUNT(*) FROM topic_mastery")
	if cursor_mastery.fetchone()[0] == 0 and os.path.exists(curriculum_db_path):
		conn_curr = sqlite3.connect(curriculum_db_path)
		cursor_curr = conn_curr.cursor()

		cursor_curr.execute("""
			SELECT t.topic_id, t.subject_code, t.module_id, t.topic_name
			FROM topics t
		""")
		topics = cursor_curr.fetchall()
		conn_curr.close()

		today_str = datetime.now().strftime("%Y-%m-%d")
		for top in topics:
			cursor_mastery.execute("""
				INSERT INTO topic_mastery (
					topic_id, subject_code, module_id, topic_name,
					mastery_score, repetition_count, interval_days, ease_factor, next_review_due
				) VALUES (?, ?, ?, ?, 0.0, 0, 0, 2.5, ?)
			""", (top[0], top[1], top[2], top[3], today_str))

	conn_mastery.commit()

	# Query count verification
	cursor_mastery.execute("SELECT COUNT(*) FROM topic_mastery")
	mastery_count = cursor_mastery.fetchone()[0]

	conn_mastery.close()

	print(f"[SUCCESS] Mastery Database initialized at: {mastery_db_path}")
	print(f" -> Tracked N5 Topics Initialized: {mastery_count}")


if __name__ == "__main__":
	print("=== Phase 7: Building Mastery Database ===")
	init_mastery_db()
