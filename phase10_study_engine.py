import os
import sqlite3
import yaml
from datetime import datetime, timedelta


def load_config():
	config_path = os.path.join("config", "settings.yaml")
	with open(config_path, "r", encoding="utf-8") as config_file:
		return yaml.safe_load(config_file)


class SM2StudyEngine:
	def __init__(self):
		config = load_config()
		self.mastery_db_path = config["databases"]["mastery_db"]

	def calculate_sm2(self, quality: int, repetitions: int, interval: int, ease_factor: float):
		"""Calculate updated SM-2 scheduling values and a mastery score.

		quality: Performance rating from 0 (blackout) to 5 (perfect recall).
		"""
		if quality < 0 or quality > 5:
			raise ValueError("Quality rating must be between 0 and 5.")

		new_ef = ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
		if new_ef < 1.3:
			new_ef = 1.3

		if quality >= 3:
			if repetitions == 0:
				new_interval = 1
			elif repetitions == 1:
				new_interval = 6
			else:
				new_interval = round(interval * new_ef)
			new_repetitions = repetitions + 1
		else:
			new_repetitions = 0
			new_interval = 1

		mastery_score = min(
			100.0,
			max(0.0, (quality / 5.0) * 20.0 + (new_repetitions * 10.0) + (new_ef * 10.0)),
		)
		return new_repetitions, new_interval, new_ef, mastery_score

	def get_valid_topic_id(self, requested_id: int = 1) -> int:
		"""Find requested topic ID or fallback to the first available topic in mastery.db."""
		conn = sqlite3.connect(self.mastery_db_path)
		try:
			cursor = conn.cursor()
			cursor.execute("SELECT topic_id FROM topic_mastery WHERE topic_id = ?", (requested_id,))
			row = cursor.fetchone()
			if row:
				return row[0]

			cursor.execute("SELECT topic_id FROM topic_mastery ORDER BY topic_id ASC LIMIT 1")
			first_row = cursor.fetchone()
			if first_row:
				return first_row[0]
			raise ValueError("No topics found in mastery.db. Please ensure Phase 7 database is populated.")
		finally:
			conn.close()

	def record_topic_review(self, topic_id: int, quality_rating: int, duration_minutes: int = 30, notes: str = ""):
		# Validate before opening a database transaction.
		if quality_rating < 0 or quality_rating > 5:
			raise ValueError("Quality rating must be between 0 and 5.")

		conn = sqlite3.connect(self.mastery_db_path)
		try:
			cursor = conn.cursor()
			cursor.execute(
				"""
				SELECT repetition_count, interval_days, ease_factor, topic_name
				FROM topic_mastery WHERE topic_id = ?
				""",
				(topic_id,),
			)
			row = cursor.fetchone()

			if not row:
				# Resolve to an available topic without leaving the connection open.
				conn.close()
				valid_id = self.get_valid_topic_id(topic_id)
				return self.record_topic_review(valid_id, quality_rating, duration_minutes, notes)

			rep_count, curr_interval, curr_ef, topic_name = row
			new_reps, new_interval, new_ef, mastery_score = self.calculate_sm2(
				quality=quality_rating,
				repetitions=rep_count,
				interval=curr_interval,
				ease_factor=curr_ef,
			)

			today = datetime.now()
			last_reviewed = today.strftime("%Y-%m-%d")
			next_due = (today + timedelta(days=new_interval)).strftime("%Y-%m-%d")

			cursor.execute(
				"""
				UPDATE topic_mastery
				SET mastery_score = ?,
					repetition_count = ?,
					interval_days = ?,
					ease_factor = ?,
					last_reviewed = ?,
					next_review_due = ?
				WHERE topic_id = ?
				""",
				(mastery_score, new_reps, new_interval, new_ef, last_reviewed, next_due, topic_id),
			)
			cursor.execute(
				"""
				INSERT INTO study_logs (topic_id, session_date, duration_minutes, performance_rating, notes)
				VALUES (?, ?, ?, ?, ?)
				""",
				(topic_id, last_reviewed, duration_minutes, quality_rating, notes),
			)
			conn.commit()
		except Exception:
			conn.rollback()
			raise
		finally:
			conn.close()

		print(f"[SM-2 UPDATED] Topic: '{topic_name}' (ID: {topic_id})")
		print(f" -> Rating: {quality_rating}/5 | New Mastery: {mastery_score:.1f}%")
		print(f" -> Next Review Interval: {new_interval} day(s) (Due: {next_due}) | Ease Factor: {new_ef:.2f}")

	def get_due_topics(self):
		conn = sqlite3.connect(self.mastery_db_path)
		try:
			cursor = conn.cursor()
			today_str = datetime.now().strftime("%Y-%m-%d")
			cursor.execute(
				"""
				SELECT topic_id, module_id, topic_name, mastery_score, next_review_due
				FROM topic_mastery
				WHERE next_review_due <= ?
				ORDER BY mastery_score ASC, next_review_due ASC
				""",
				(today_str,),
			)
			return cursor.fetchall()
		finally:
			conn.close()


if __name__ == "__main__":
	print("=== Phase 10: Testing SM-2 Study Engine ===")
	engine = SM2StudyEngine()

	target_topic = engine.get_valid_topic_id(1)
	print(f"\n-- Simulating Review Session on Target Topic (ID: {target_topic}) --")
	engine.record_topic_review(
		topic_id=target_topic,
		quality_rating=4,
		duration_minutes=45,
		notes="Reviewed Bernoulli derivation and differential pressure equations.",
	)

	print("\n-- Fetching Topics Currently Due for Review --")
	due_topics = engine.get_due_topics()
	print(f"Total topics due today or overdue: {len(due_topics)}")
	for topic in due_topics[:3]:
		print(
			f" -> [Topic {topic[0]}] Module {topic[1]}: {topic[2]} "
			f"(Mastery: {topic[3]:.1f}%, Due: {topic[4]})"
		)
