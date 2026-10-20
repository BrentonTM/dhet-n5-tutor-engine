import os
import json
import sqlite3
import yaml


def load_config():
	config_path = os.path.join("config", "settings.yaml")
	with open(config_path, "r") as f:
		return yaml.safe_load(f)


def init_curriculum_db():
	config = load_config()
	db_path = config["databases"]["curriculum_db"]
	curriculum_dir = config["paths"]["curriculum_dir"]

	# Ensure output database folder exists
	os.makedirs(os.path.dirname(db_path), exist_ok=True)

	conn = sqlite3.connect(db_path)
	cursor = conn.cursor()

	# Create Tables
	cursor.execute("""
	CREATE TABLE IF NOT EXISTS subjects (
		subject_code TEXT PRIMARY KEY,
		subject_name TEXT NOT NULL,
		level TEXT NOT NULL
	)
	""")

	cursor.execute("""
	CREATE TABLE IF NOT EXISTS modules (
		module_id INTEGER,
		subject_code TEXT,
		module_name TEXT NOT NULL,
		weight_percentage REAL,
		PRIMARY KEY (module_id, subject_code),
		FOREIGN KEY (subject_code) REFERENCES subjects(subject_code)
	)
	""")

	cursor.execute("""
	CREATE TABLE IF NOT EXISTS topics (
		topic_id INTEGER PRIMARY KEY AUTOINCREMENT,
		module_id INTEGER,
		subject_code TEXT,
		topic_name TEXT NOT NULL,
		FOREIGN KEY (module_id, subject_code) REFERENCES modules(module_id, subject_code)
	)
	""")

	# Clear old entries for fresh population
	cursor.execute("DELETE FROM topics")
	cursor.execute("DELETE FROM modules")
	cursor.execute("DELETE FROM subjects")

	# Read and populate curriculum data
	curriculum_files = [
		f for f in os.listdir(curriculum_dir)
		if f.endswith(".json") or f.endswith(".yaml")
	]

	for file in curriculum_files:
		file_path = os.path.join(curriculum_dir, file)
		with open(file_path, "r") as f:
			data = json.load(f) if file.endswith(".json") else yaml.safe_load(f)

		cursor.execute(
			"INSERT INTO subjects (subject_code, subject_name, level) VALUES (?, ?, ?)",
			(data["subject_code"], data["subject_name"], data["level"])
		)

		for mod in data.get("modules", []):
			cursor.execute(
				"INSERT INTO modules (module_id, subject_code, module_name, weight_percentage) VALUES (?, ?, ?, ?)",
				(mod["module_id"], data["subject_code"], mod["module_name"], mod["weight_percentage"])
			)

			for topic in mod.get("topics", []):
				cursor.execute(
					"INSERT INTO topics (module_id, subject_code, topic_name) VALUES (?, ?, ?)",
					(mod["module_id"], data["subject_code"], topic)
				)

	conn.commit()

	# Query count verification
	cursor.execute("SELECT COUNT(*) FROM subjects")
	sub_count = cursor.fetchone()[0]
	cursor.execute("SELECT COUNT(*) FROM modules")
	mod_count = cursor.fetchone()[0]
	cursor.execute("SELECT COUNT(*) FROM topics")
	top_count = cursor.fetchone()[0]

	conn.close()

	print(f"[SUCCESS] Curriculum Database created at: {db_path}")
	print(f" -> Subjects Populated: {sub_count}")
	print(f" -> Modules Populated: {mod_count}")
	print(f" -> Topics Populated: {top_count}")


if __name__ == "__main__":
	print("=== Phase 6: Building Curriculum Database ===")
	init_curriculum_db()
