import os
import sqlite3
from datetime import datetime


class MasteryAnalyticsReporter:
	"""Generate mastery analytics and progress reports across NATED subjects."""

	def __init__(self):
		self.mastery_db = os.path.join("data", "databases", "mastery.db")
		self.subjects = ["INST-N5", "MATH-N5", "IE-N5", "DIGI-N4", "DIGI-N5"]

	def generate_full_report(self):
		if not os.path.exists(self.mastery_db):
			print("\n[ERROR] mastery.db not found!")
			return

		with sqlite3.connect(self.mastery_db) as conn:
			cursor = conn.cursor()
			print("\n" + "=" * 75)
			print(
				" AGGREGATED STUDENT MASTERY & PROGRESS REPORT "
				f"({datetime.now().strftime('%Y-%m-%d %H:%M')})"
			)
			print("=" * 75)

			total_mastery = 0.0
			subject_count = 0

			for subject in self.subjects:
				cursor.execute(
					"""
					SELECT COUNT(topic_id), AVG(mastery_score),
						   SUM(CASE WHEN mastery_score >= 70 THEN 1 ELSE 0 END),
						   SUM(CASE WHEN mastery_score < 40 THEN 1 ELSE 0 END)
					FROM topic_mastery
					WHERE subject_code = ?
					""",
					(subject,),
				)
				row = cursor.fetchone()
				total_topics = row[0] or 0
				avg_score = round(row[1] or 0.0, 1)
				mastered_count = row[2] or 0
				weak_count = row[3] or 0

				total_mastery += avg_score
				subject_count += 1

				bar_len = max(0, min(20, int(avg_score / 5)))
				progress_bar = "█" * bar_len + "░" * (20 - bar_len)
				print(f"\nSubject: {subject}")
				print(f" Progress Bar : [{progress_bar}] {avg_score}%")
				print(f" Total Topics : {total_topics}")
				print(f" Mastered     : {mastered_count} topics (≥70%)")
				print(f" Needs Work   : {weak_count} topics (<40%)")

		overall_avg = round(total_mastery / max(subject_count, 1), 1)
		print("\n" + "=" * 75)
		print(f" OVERALL ACADEMIC READINESS SCORE: {overall_avg}%")
		print("=" * 75)
