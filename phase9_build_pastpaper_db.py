import os
import json
import sqlite3
import yaml


def load_config():
	config_path = os.path.join("config", "settings.yaml")
	with open(config_path, "r") as f:
		return yaml.safe_load(f)


def init_pastpaper_db():
	config = load_config()
	db_path = os.path.join("data", "databases", "past_papers.db")
	past_papers_dir = config["paths"]["past_papers_dir"]

	os.makedirs(os.path.dirname(db_path), exist_ok=True)
	os.makedirs(past_papers_dir, exist_ok=True)

	conn = sqlite3.connect(db_path)
	cursor = conn.cursor()

	cursor.execute("""
	CREATE TABLE IF NOT EXISTS exam_papers (
		paper_id INTEGER PRIMARY KEY AUTOINCREMENT,
		subject_code TEXT NOT NULL,
		exam_year INTEGER NOT NULL,
		exam_trimester TEXT NOT NULL,
		paper_code TEXT
	)
	""")

	cursor.execute("""
	CREATE TABLE IF NOT EXISTS paper_questions (
		question_id INTEGER PRIMARY KEY AUTOINCREMENT,
		paper_id INTEGER NOT NULL,
		question_number TEXT NOT NULL,
		module_id INTEGER NOT NULL,
		topic_name TEXT,
		question_text TEXT NOT NULL,
		marks INTEGER NOT NULL,
		solution_guide TEXT NOT NULL,
		FOREIGN KEY (paper_id) REFERENCES exam_papers(paper_id)
	)
	""")

	conn.commit()

	# Create a sample N5 past paper if it does not already exist.
	sample_paper_path = os.path.join(past_papers_dir, "inst_n5_nov2023.json")
	if not os.path.exists(sample_paper_path):
		sample_data = {
			"subject_code": "INST-N5",
			"exam_year": 2023,
			"exam_trimester": "T3",
			"paper_code": "8080205",
			"questions": [
				{
					"question_number": "Q1.1",
					"module_id": 1,
					"topic_name": "Differential Pressure Meters",
					"question_text": "Derive the basic flow equation for an orifice plate, stating all assumptions regarding incompressible fluid flow through a pipe constriction.",
					"marks": 8,
					"solution_guide": "1. Apply Bernoulli's equation between upstream and throat.\n2. Apply continuity equation (A1*V1 = A2*V2).\n3. Express velocity in terms of differential pressure (delta P).\n4. Introduce discharge coefficient (Cd) to account for energy losses."
				},
				{
					"question_number": "Q2.1",
					"module_id": 2,
					"topic_name": "Resistance Temperature Detectors (RTDs)",
					"question_text": "Explain why a three-wire RTD configuration is preferred over a two-wire circuit in precision industrial temperature measurement.",
					"marks": 6,
					"solution_guide": "1. Two-wire circuits add lead wire resistance directly to the sensor reading, causing positive temperature errors.\n2. Three-wire circuits place lead wires in opposing arms of a Wheatstone bridge, canceling lead wire resistance when calibrated."
				}
			]
		}
		with open(sample_paper_path, "w") as f:
			json.dump(sample_data, f, indent=2)

	# Ingest JSON past-paper files into the database.
	cursor.execute("DELETE FROM paper_questions")
	cursor.execute("DELETE FROM exam_papers")

	paper_files = [f for f in os.listdir(past_papers_dir) if f.endswith(".json")]
	for file in paper_files:
		file_path = os.path.join(past_papers_dir, file)
		with open(file_path, "r") as f:
			pdata = json.load(f)

		cursor.execute("""
			INSERT INTO exam_papers (subject_code, exam_year, exam_trimester, paper_code)
			VALUES (?, ?, ?, ?)
		""", (
			pdata["subject_code"],
			pdata["exam_year"],
			pdata["exam_trimester"],
			pdata.get("paper_code", "")
		))
		paper_id = cursor.lastrowid

		for question in pdata.get("questions", []):
			cursor.execute("""
				INSERT INTO paper_questions (
					paper_id, question_number, module_id, topic_name,
					question_text, marks, solution_guide
				)
				VALUES (?, ?, ?, ?, ?, ?, ?)
			""", (
				paper_id,
				question["question_number"],
				question["module_id"],
				question["topic_name"],
				question["question_text"],
				question["marks"],
				question["solution_guide"]
			))

	conn.commit()

	cursor.execute("SELECT COUNT(*) FROM exam_papers")
	paper_count = cursor.fetchone()[0]
	cursor.execute("SELECT COUNT(*) FROM paper_questions")
	question_count = cursor.fetchone()[0]
	conn.close()

	print(f"[SUCCESS] Past-Paper Database created at: {db_path}")
	print(f" -> Exam Papers Ingested: {paper_count}")
	print(f" -> Exam Questions Indexed: {question_count}")


if __name__ == "__main__":
	print("=== Phase 9: Building Past-Paper Database ===")
	init_pastpaper_db()
