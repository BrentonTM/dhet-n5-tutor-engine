import os
import sqlite3
from datetime import datetime, timedelta


class MasterSchedulerEngine:
	"""Generates automated daily study timetables and balances subject review based on mastery levels."""

	def __init__(self):
		self.mastery_db = os.path.join("data", "databases", "mastery.db")
		self.curriculum_db = os.path.join("data", "databases", "curriculum.db")
		self.subjects = ["INST-N5", "MATH-N5", "IE-N5", "DIGI-N4", "DIGI-N5"]

	def calculate_subject_priorities(self):
		"""Calculates subject priority scores based on current mastery levels."""
		priorities = {}
		if not os.path.exists(self.mastery_db):
			return {sub: 50.0 for sub in self.subjects}

		try:
			conn = sqlite3.connect(self.mastery_db)
			cursor = conn.cursor()

			for sub in self.subjects:
				cursor.execute(
					"""
					SELECT AVG(mastery_level)
					FROM topic_mastery
					WHERE subject_code = ?
					""",
					(sub,),
				)
				row = cursor.fetchone()
				avg_mastery = row[0] if row and row[0] is not None else 50.0
				# Lower mastery gets higher priority weight.
				priorities[sub] = round(100.0 - avg_mastery, 1)

			conn.close()
		except Exception:
			priorities = {sub: 50.0 for sub in self.subjects}

		return priorities

	def generate_daily_timetable(self, study_hours=4):
		"""Constructs a daily study schedule allocated dynamically by subject priority."""
		priorities = self.calculate_subject_priorities()
		sorted_subs = sorted(priorities.items(), key=lambda x: x[1], reverse=True)

		print("\n" + "=" * 70)
		print(f" AUTOMATED DAILY STUDY SCHEDULE ({datetime.now().strftime('%Y-%m-%d')})")
		print(f" Target Hours: {study_hours} hrs | Optimization: SM-2 Priority Weighting")
		print("=" * 70)

		# Allocate time blocks (50 min study + 10 min break per block).
		total_blocks = study_hours
		start_time = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)

		print(f"{'Time Slot':<18} | {'Subject':<10} | {'Focus Mode':<25} | {'Priority Score'}")
		print("-" * 70)

		modes = [
			"Past Paper Practice (Phase 14)",
			"Theory & Formulas (Phase 13)",
			"Weak Topic Review (SM-2)",
		]

		for i in range(total_blocks):
			sub_code, priority = sorted_subs[i % len(sorted_subs)]
			mode = modes[i % len(modes)]

			slot_start = start_time + timedelta(hours=i)
			slot_end = slot_start + timedelta(minutes=50)
			time_str = f"{slot_start.strftime('%H:%M')} - {slot_end.strftime('%H:%M')}"

			print(f"{time_str:<18} | {sub_code:<10} | {mode:<25} | Priority: {priority}/100")

		print("=" * 70)
