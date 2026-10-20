import os
import sys
import sqlite3

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from phase13_subject_tutors import SubjectTutorSkill
from phase14_exam_simulation import ExamSimulationEngine
from phase15_master_scheduler import MasterSchedulerEngine
from phase16_analytics_reporter import MasteryAnalyticsReporter


class MultiSubjectTutorCLI:
	def __init__(self):
		self.curriculum_db = os.path.join("data", "databases", "curriculum.db")
		self.mastery_db = os.path.join("data", "databases", "mastery.db")
		self.past_papers_db = os.path.join("data", "databases", "past_papers.db")
		self.active_subject = "INST-N5"
		self.tutor_skill = SubjectTutorSkill(self.active_subject)
		self.exam_engine = ExamSimulationEngine(self.active_subject)
		self.scheduler = MasterSchedulerEngine()
		self.reporter = MasteryAnalyticsReporter()

	def list_subjects(self):
		if not os.path.exists(self.curriculum_db):
			return [
				("INST-N5", "Instrumentation N5", "N5"),
				("MATH-N5", "Mathematics N5", "N5"),
				("IE-N5", "Industrial Electronics N5", "N5"),
				("DIGI-N4", "Digital Electronics N4", "N4"),
				("DIGI-N5", "Digital Electronics N5", "N5"),
			]
		conn = sqlite3.connect(self.curriculum_db)
		cursor = conn.cursor()
		cursor.execute("SELECT subject_code, subject_name, level FROM subjects")
		subjects = cursor.fetchall()
		conn.close()
		return subjects

	def select_subject(self, code):
		self.active_subject = code
		self.tutor_skill.active_subject = code
		self.exam_engine.active_subject = code
		print(f"\n[ACTIVE SUBJECT CHANGED] Now tutoring: {self.active_subject}")

	def show_dashboard(self):
		print(f"\n==================================================")
		print(f" STUDENT MASTERY DASHBOARD: [{self.active_subject}]")
		print(f"==================================================")
		if not os.path.exists(self.mastery_db):
			print("No mastery database found.")
			return

		conn = sqlite3.connect(self.mastery_db)
		cursor = conn.cursor()

		cursor.execute("PRAGMA table_info(topic_mastery)")
		available_cols = [col[1] for col in cursor.fetchall()]

		if not available_cols:
			print(" No topic_mastery table found in mastery.db.")
			conn.close()
			return

		query = f"SELECT {', '.join(available_cols)} FROM topic_mastery WHERE subject_code = ?"
		cursor.execute(query, (self.active_subject,))
		rows = cursor.fetchall()
		conn.close()

		if not rows:
			print(" No topics found for this subject.")
			return

		print(f"Columns: { ' | '.join(available_cols) }")
		print("-" * 80)
		for r in rows[:10]:
			print(" | ".join(str(val) for val in r))

	def show_formula_sheet(self):
		print(f"\n==================================================")
		print(f" FORMULA & CORE CONCEPTS SHEET: [{self.active_subject}]")
		print(f"==================================================")
		formulas = self.tutor_skill.get_subject_formulas()
		if not formulas:
			print("No specific formula entries configured for this subject yet.")
			return

		for topic, formula in formulas.items():
			print(f" • {topic:<25} : {formula}")

	def get_past_paper_question(self):
		if not os.path.exists(self.past_papers_db):
			print("\n[ERROR] past_papers.db not found!")
			return

		conn = sqlite3.connect(self.past_papers_db)
		cursor = conn.cursor()

		base_subject = self.active_subject.split("-")[0] if "-" in self.active_subject else self.active_subject

		cursor.execute("""
			SELECT question_number, topic_name, question_text, marking_guideline, marks
			FROM paper_questions
			WHERE (subject_code LIKE ? OR subject_code LIKE ? OR ? LIKE '%' || subject_code || '%')
			  AND LENGTH(question_text) > 40
			  AND question_text NOT LIKE '%NATIONAL CERTIFICATE%'
			  AND question_text NOT LIKE '%APRIL EXAMINATION%'
			  AND question_text NOT LIKE '%NOVEMBER EXAMINATION%'
			  AND question_text NOT LIKE '%Copyright reserved%'
			  AND question_text NOT LIKE '%consists of%pages%'
			ORDER BY RANDOM() LIMIT 1
		""", (f"%{self.active_subject}%", f"%{base_subject}%", self.active_subject))

		row = cursor.fetchone()
		conn.close()

		if row:
			q_num, topic, q_text, memo, marks = row
			print("\n" + "=" * 65)
			print(f" QUESTION: {q_num} | TOPIC: {topic} | MARKS: {marks}")
			print("=" * 65)
			print(f"\n{q_text.strip()}\n")

			print("-" * 65)
			print(" TUTOR GUIDANCE & APPROACH HINTS")
			print("-" * 65)
			hints = self.tutor_skill.generate_socratic_hint(topic, q_text)
			for hint in hints:
				print(f"  {hint}")
			print("-" * 65)

			input("\nPress [ENTER] to reveal the marking guideline / memo...")

			print("\n" + "=" * 65)
			print(" MARKING GUIDELINE / MEMO")
			print("=" * 65)
			print(f"\n{memo.strip()}\n")
			print("=" * 65)
		else:
			print(f"\n[WARNING] No questions found in past_papers.db matching '{self.active_subject}'.")

	def run_exam_simulation(self):
		print("\n1. Quick Practice Test (3 Questions)")
		print("2. Standard Mock Exam (5 Questions)")
		choice = input("Select exam length (1-2): ").strip()
		count = 5 if choice == "2" else 3
		self.exam_engine.run_mock_exam(question_count=count)

	def generate_timetable(self):
		try:
			hrs = int(input("Enter total planned study hours for today (e.g., 4): ").strip())
		except ValueError:
			hrs = 4
		self.scheduler.generate_daily_timetable(study_hours=hrs)

	def start_cli(self):
		while True:
			print(f"\nActive Subject: [{self.active_subject}]")
			print("1. Switch Active Subject (INST-N5, MATH-N5, IE-N5, DIGI-N4, DIGI-N5)")
			print("2. View Mastery Dashboard for Active Subject")
			print("3. Fetch Exam Practice Question (with Phase 13 Tutor Hints)")
			print("4. View Subject Formula & Concept Reference (Phase 13)")
			print("5. Start Simulated Timed Exam Session (Phase 14)")
			print("6. Generate Automated Daily Study Schedule (Phase 15)")
			print("7. View Comprehensive Progress & Analytics Report (Phase 16)")
			print("8. Exit Engine")

			choice = input("\nSelect Option (1-8): ").strip()

			if choice == "1":
				print("\nAvailable Subjects:")
				for subject in self.list_subjects():
					print(f" - {subject[0]}: {subject[1]} (NATED Level {subject[2]})")
				code = input("Enter Subject Code: ").strip().upper()
				if code:
					self.select_subject(code)
			elif choice == "2":
				self.show_dashboard()
			elif choice == "3":
				self.get_past_paper_question()
			elif choice == "4":
				self.show_formula_sheet()
			elif choice == "5":
				self.run_exam_simulation()
			elif choice == "6":
				self.generate_timetable()
			elif choice == "7":
				self.reporter.generate_full_report()
			elif choice == "8":
				print("\nExiting AI Tutor Engine. Keep studying!")
				break
			else:
				print("\nInvalid choice. Please select 1 through 8.")


if __name__ == "__main__":
	tutor = MultiSubjectTutorCLI()
	tutor.start_cli()
