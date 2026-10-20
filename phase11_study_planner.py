import os
import sqlite3
import yaml
from datetime import datetime


def load_config():
	config_path = os.path.join("config", "settings.yaml")
	with open(config_path, "r", encoding="utf-8") as f:
		return yaml.safe_load(f)


class DailyStudyPlanner:
	def __init__(self):
		config = load_config()
		self.mastery_db_path = config["databases"]["mastery_db"]
		self.pastpaper_db_path = os.path.join("data", "databases", "past_papers.db")

	def generate_daily_schedule(self, target_hours: float = 4.0):
		conn_mastery = sqlite3.connect(self.mastery_db_path)
		try:
			cursor_m = conn_mastery.cursor()
			today_str = datetime.now().strftime("%Y-%m-%d")

			# Fetch topics due for review (lowest mastery first).
			cursor_m.execute(
				"""
				SELECT topic_id, module_id, topic_name, mastery_score, ease_factor
				FROM topic_mastery
				WHERE next_review_due <= ?
				ORDER BY mastery_score ASC
				LIMIT 3
				""",
				(today_str,),
			)
			due_topics = cursor_m.fetchall()

			# Fetch unreviewed or weak topics for new focus.
			cursor_m.execute(
				"""
				SELECT topic_id, module_id, topic_name, mastery_score
				FROM topic_mastery
				WHERE repetition_count = 0 OR mastery_score < 50.0
				ORDER BY mastery_score ASC
				LIMIT 2
				"""
			)
			new_topics = cursor_m.fetchall()
		finally:
			conn_mastery.close()

		# Fetch past-paper practice questions.
		past_paper_qs = []
		if os.path.exists(self.pastpaper_db_path):
			with sqlite3.connect(self.pastpaper_db_path) as conn_pp:
				cursor_p = conn_pp.cursor()
				cursor_p.execute(
					"""
					SELECT question_number, topic_name, question_text, marks
					FROM paper_questions
					LIMIT 2
					"""
				)
				past_paper_qs = cursor_p.fetchall()

		# Structure a four-hour block schedule (240 minutes total).
		schedule = [
			{
				"block": "Block 1 (08:00 - 09:00)",
				"activity": "Spaced Repetition Review (SM-2)",
				"duration": "60 mins",
				"details": [
					f"Topic {topic[0]}: {topic[2]} (Current Mastery: {topic[3]:.1f}%)"
					for topic in due_topics[:2]
				],
			}
		]

		focus_topic = new_topics[0] if new_topics else (
			due_topics[0] if due_topics else (1, 1, "Flow Measurement", 0.0)
		)
		schedule.append(
			{
				"block": "Block 2 (09:15 - 10:45)",
				"activity": "New Content & Derivations Deep-Dive",
				"duration": "90 mins",
				"details": [
					f"Module {focus_topic[1]} - {focus_topic[2]}: First-principles "
					"derivations, circuit setups, and operating equations."
				],
			}
		)

		schedule.append(
			{
				"block": "Block 3 (11:00 - 12:00)",
				"activity": "Exam Question Application & Marking Guideline Analysis",
				"duration": "60 mins",
				"details": (
					[
						f"Question {question[0]} ({question[1]} - {question[3]} Marks): "
						f"{question[2][:80]}..."
						for question in past_paper_qs
					]
					if past_paper_qs
					else ["Complete past paper exercise from N5 question bank."]
				),
			}
		)

		schedule.append(
			{
				"block": "Block 4 (12:00 - 12:30)",
				"activity": "Self-Assessment & Mastery Logging",
				"duration": "30 mins",
				"details": [
					"Rate understanding on 0-5 scale in SM-2 Engine.",
					"Update error log for missed steps or equation mix-ups.",
				],
			}
		)
		return schedule

	def print_schedule(self):
		schedule = self.generate_daily_schedule()
		print("=================================================================")
		print("        DHET INSTRUMENTATION N5: 4-HOUR DAILY STUDY PLANNER       ")
		print("=================================================================\n")

		for item in schedule:
			print(f"[{item['block']}] - {item['activity']} ({item['duration']})")
			for detail in item["details"]:
				print(f"   • {detail}")
			print("-" * 65)


if __name__ == "__main__":
	print("=== Phase 11: Testing Dynamic Daily Study Planner ===")
	planner = DailyStudyPlanner()
	planner.print_schedule()
