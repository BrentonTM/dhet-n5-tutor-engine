import os
import re
import sqlite3
import yaml
from pypdf import PdfReader


def load_config():
	config_path = os.path.join("config", "settings.yaml")
	if os.path.exists(config_path):
		with open(config_path, "r", encoding="utf-8") as f:
			return yaml.safe_load(f)
	return {}


# Target folder in your Documents directory
PDF_SOURCE_DIR = os.path.expanduser(
	r"C:\Users\user\Documents\N5_AI_ENGINEERING_TUTOR\examinations\past_papers"
)


def infer_subject_code(filename_or_path):
	name = filename_or_path.upper()
	if "MATH" in name or "MATHEMATICS" in name:
		return "MATH-N5"
	elif "DIGI" in name and "N4" in name:
		return "DIGI-N4"
	elif "DIGI" in name and "N5" in name:
		return "DIGI-N5"
	elif "IE" in name or "INDUSTRIAL ELECTRONICS" in name:
		return "IE-N5"
	elif "INST" in name or "INSTRUMENTATION" in name:
		return "INST-N5"
	return "INST-N5"


def extract_pdf_text(pdf_path):
	try:
		reader = PdfReader(pdf_path)
		text = ""
		for page in reader.pages:
			extracted = page.extract_text()
			if extracted:
				text += extracted + "\n"
		return text
	except Exception as e:
		print(f"[ERROR] Reading {pdf_path}: {e}")
		return ""


def build_pdf_past_papers_db():
	db_path = os.path.join("data", "databases", "past_papers.db")
	os.makedirs(os.path.dirname(db_path), exist_ok=True)

	conn = sqlite3.connect(db_path)
	cursor = conn.cursor()

	# Reset table schema
	cursor.execute("DROP TABLE IF EXISTS paper_questions")
	cursor.execute(
		"""
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
		"""
	)

	if not os.path.exists(PDF_SOURCE_DIR):
		print(f"[ERROR] Directory not found: {PDF_SOURCE_DIR}")
		print("Please verify that the path exists in your Documents folder.")
		conn.close()
		return

	total_pdf_files = 0
	total_questions = 0

	print(f"Scanning directory: {PDF_SOURCE_DIR}\n")

	for root, _, files in os.walk(PDF_SOURCE_DIR):
		for file in files:
			if file.lower().endswith(".pdf"):
				pdf_path = os.path.join(root, file)
				subject_code = infer_subject_code(pdf_path)

				date_match = re.search(r"(20\d{2})", file)
				exam_date = date_match.group(1) if date_match else "Unknown"

				full_text = extract_pdf_text(pdf_path)
				if not full_text.strip():
					continue

				raw_questions = re.split(r"(?i)\n(?=QUESTION\s+\d+)", full_text)
				is_memo = (
					"MEMORANDUM" in file.upper()
					or "MEMO" in file.upper()
					or "MARKING" in file.upper()
				)

				for idx, q_block in enumerate(raw_questions):
					q_block = q_block.strip()
					if not q_block:
						continue

					q_num_match = re.search(r"(?i)QUESTION\s+(\d+)", q_block)
					q_num = f"Q{q_num_match.group(1)}" if q_num_match else f"Q{idx + 1}"

					mark_match = re.search(r"\[(\d+)\]|\((\d+)\)", q_block)
					marks = (
						int(mark_match.group(1) or mark_match.group(2))
						if mark_match
						else 5
					)

					q_text = (
						q_block
						if not is_memo
						else f"Refer to question sheet for {q_num}"
					)
					memo_text = (
						q_block if is_memo else "See attached marking guideline PDF."
					)

					cursor.execute(
						"""
						INSERT INTO paper_questions
						(subject_code, exam_date, question_number, topic_name,
						 question_text, marking_guideline, marks)
						VALUES (?, ?, ?, ?, ?, ?, ?)
						""",
						(
							subject_code,
							exam_date,
							q_num,
							"Past Paper Review",
							q_text,
							memo_text,
							marks,
						),
					)

					total_questions += 1

				total_pdf_files += 1
				print(f" -> Processed PDF [{subject_code}]: {file}")

	conn.commit()
	conn.close()

	print("\n=================================================================")
	print("      PDF EXAM PAPERS & MEMORANDUMS INGESTION COMPLETE          ")
	print("=================================================================")
	print(f" -> PDF Files Processed : {total_pdf_files}")
	print(f" -> Questions Ingested   : {total_questions}")
	print(f" -> Database Path        : {db_path}")


if __name__ == "__main__":
	build_pdf_past_papers_db()
