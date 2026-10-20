import os
import sqlite3
import json
import yaml

def load_config():
	config_path = os.path.join("config", "settings.yaml")
	with open(config_path, "r", encoding="utf-8") as f:
		return yaml.safe_load(f)

def build_past_papers_db():
	db_path = os.path.join("data", "databases", "past_papers.db")
	papers_dir = os.path.join("data", "past_papers")
	os.makedirs(os.path.dirname(db_path), exist_ok=True)
	os.makedirs(papers_dir, exist_ok=True)

	conn = sqlite3.connect(db_path)
	cursor = conn.cursor()

	# Reset table schema
	cursor.execute("DROP TABLE IF EXISTS paper_questions")
	cursor.execute("""
	CREATE TABLE paper_questions (
		question_id INTEGER PRIMARY KEY AUTOINCREMENT,
		subject_code TEXT NOT NULL,
		exam_date TEXT NOT NULL,
		question_number TEXT NOT NULL,
		topic_name TEXT NOT NULL,
		question_text TEXT NOT NULL,
		marking_guideline TEXT NOT NULL,
		marks INTEGER NOT NULL
	)
	""")

	total_loaded = 0

	# 1. Scan data/past_papers/ for JSON payload files
	for root, _, files in os.walk(papers_dir):
		for file in files:
			if file.endswith(".json"):
				file_path = os.path.join(root, file)
				with open(file_path, "r", encoding="utf-8") as f:
					try:
						questions = json.load(f)
						if isinstance(questions, list):
							for q in questions:
								cursor.execute("""
									INSERT INTO paper_questions
									(subject_code, exam_date, question_number, topic_name, question_text, marking_guideline, marks)
									VALUES (?, ?, ?, ?, ?, ?, ?)
								""", (
									q.get("subject_code", "UNKNOWN"),
									q.get("exam_date", "N/A"),
									q.get("question_number", "Q1"),
									q.get("topic_name", "General"),
									q.get("question_text", ""),
									q.get("marking_guideline", ""),
									q.get("marks", 0)
								))
								total_loaded += 1
					except Exception as e:
						print(f"[WARNING] Could not parse {file_path}: {e}")

	conn.commit()
	conn.close()

	print("=================================================================")
	print("         MULTI-SUBJECT PAST PAPERS DATABASE INGESTED             ")
	print("=================================================================")
	print(f" -> Total Exam Questions Loaded from Files: {total_loaded}")
	print(f" -> Source Directory: {papers_dir}")
	print(f" -> Database Path: {db_path}")

if __name__ == "__main__":
	build_past_papers_db()
