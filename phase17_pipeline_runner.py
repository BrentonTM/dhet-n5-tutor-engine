import os
import sys
import sqlite3
import subprocess
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from phase15_master_scheduler import MasterSchedulerEngine
from phase16_analytics_reporter import MasteryAnalyticsReporter


class TutorEnginePipeline:
	"""Automates database checks, daily study plan generation, and engine startup."""

	def __init__(self):
		self.db_folder = os.path.join("data", "databases")
		self.required_dbs = ["curriculum.db", "mastery.db", "past_papers.db"]
		self.scheduler = MasterSchedulerEngine()
		self.reporter = MasteryAnalyticsReporter()

	def check_database_integrity(self):
		print("\n[PIPELINE] Checking Database Integrity...")
		missing = []
		for db in self.required_dbs:
			path = os.path.join(self.db_folder, db)
			if not os.path.exists(path):
				missing.append(db)
			else:
				try:
					conn = sqlite3.connect(path)
					cursor = conn.cursor()
					cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
					tables = cursor.fetchall()
					conn.close()
					print(f"  ✓ {db:<15} : {len(tables)} table(s) operational.")
				except sqlite3.Error as e:
					print(f"  ✗ {db:<15} : CORRUPT - {e}")

		if missing:
			print(f"  [WARNING] Missing databases: {', '.join(missing)}")
			return False
		return True

	def run_daily_startup(self, study_hours=4):
		print("\n" + "=" * 70)
		print(
			f" DHET N5 TUTOR ENGINE - AUTOMATED PIPELINE STARTUP "
			f"({datetime.now().strftime('%Y-%m-%d')})"
		)
		print("=" * 70)

		# 1. Integrity Verification
		all_ok = self.check_database_integrity()
		if not all_ok:
			print("[PIPELINE] Setup incomplete. Proceeding with available modules...\n")

		# 2. Automated Daily Schedule Generation
		print("\n[PIPELINE] Generating Daily Study Schedule...")
		self.scheduler.generate_daily_timetable(study_hours=study_hours)

		# 3. Quick Academic Readiness Snapshot
		print("\n[PIPELINE] Generating Progress Snapshot...")
		self.reporter.generate_full_report()

	def launch_cli(self):
		print("\n[PIPELINE] Handoff to MultiSubjectTutorCLI...\n")
		subprocess.run([sys.executable, "phase12_tutor_cli.py"])


if __name__ == "__main__":
	pipeline = TutorEnginePipeline()
	pipeline.run_daily_startup(study_hours=4)

	input("\nPress [ENTER] to open the Interactive CLI Engine...")
	pipeline.launch_cli()
