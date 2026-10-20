import os
import sqlite3
import time
from datetime import datetime

class ExamSimulationEngine:
    """Simulates timed past paper examinations and records scores to update student mastery."""

    def __init__(self, active_subject="INST-N5"):
        self.active_subject = active_subject
        self.past_papers_db = os.path.join("data", "databases", "past_papers.db")
        self.mastery_db = os.path.join("data", "databases", "mastery.db")

    def generate_exam_paper(self, total_marks_target=100):
        """Assembles a full balanced mock exam paper up to target marks."""
        if not os.path.exists(self.past_papers_db):
            print("\n[ERROR] past_papers.db not found!")
            return []

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
            ORDER BY RANDOM() LIMIT 15
        """, (f"%{self.active_subject}%", f"%{base_subject}%", self.active_subject))

        rows = cursor.fetchall()
        conn.close()

        exam_questions = []
        accumulated_marks = 0

        for r in rows:
            q_num, topic, q_text, memo, marks = r
            try:
                mark_val = int(marks) if marks else 10
            except ValueError:
                mark_val = 10

            exam_questions.append({
                "q_num": q_num,
                "topic": topic,
                "q_text": q_text,
                "memo": memo,
                "marks": mark_val
            })
            accumulated_marks += mark_val
            if accumulated_marks >= total_marks_target:
                break

        return exam_questions

    def run_mock_exam(self, question_count=3):
        """Runs an interactive mini exam, collects user self-assessment scores, and logs results."""
        questions = self.generate_exam_paper(total_marks_target=question_count * 10)
        
        if not questions:
            print(f"\n[WARNING] Could not construct exam session for {self.active_subject}.")
            return

        print("\n" + "="*70)
        print(f" EXAM SIMULATION MODE: [{self.active_subject}]")
        print(f" Questions: {len(questions)} | Started: {datetime.now().strftime('%H:%M:%S')}")
        print("="*70)

        total_possible = 0
        total_earned = 0
        start_time = time.time()

        for idx, q in enumerate(questions, 1):
            print(f"\n--- QUESTION {idx} of {len(questions)} [{q['marks']} Marks] ---")
            print(f"Topic: {q['topic']}\n")
            print(q['q_text'].strip())
            print("\n" + "-"*40)
            
            input("Press [ENTER] when you have finished writing your answer to check memo...")
            
            print("\n--- OFFICIAL MEMO ---")
            print(q['memo'].strip())
            print("-" * 40)

            while True:
                try:
                    score = float(input(f"Enter marks achieved for Question {idx} (0 - {q['marks']}): "))
                    if 0 <= score <= q['marks']:
                        total_earned += score
                        total_possible += q['marks']
                        break
                    print(f"Please enter a score between 0 and {q['marks']}.")
                except ValueError:
                    print("Invalid input. Enter a numeric mark.")

        elapsed_mins = round((time.time() - start_time) / 60, 1)
        percentage = round((total_earned / total_possible) * 100, 1) if total_possible > 0 else 0

        print("\n" + "="*70)
        print(" SIMULATED EXAM RESULTS SUMMARY")
        print("="*70)
        print(f" Subject        : {self.active_subject}")
        print(f" Score          : {total_earned} / {total_possible} ({percentage}%)")
        print(f" Time Taken     : {elapsed_mins} minutes")
        print("="*70)

        self._log_exam_result(percentage)

    def _log_exam_result(self, percentage):
        """Persists session score back into student mastery records."""
        if not os.path.exists(self.mastery_db):
            return

        try:
            conn = sqlite3.connect(self.mastery_db)
            cursor = conn.cursor()

            # Dynamic update to avoid missing schema columns
            cursor.execute("PRAGMA table_info(topic_mastery)")
            cols = [c[1] for c in cursor.fetchall()]

            if "mastery_level" in cols:
                cursor.execute("""
                    UPDATE topic_mastery 
                    SET mastery_level = ROUND((mastery_level + ?) / 2, 1)
                    WHERE subject_code = ?
                """, (percentage, self.active_subject))
                conn.commit()
                print(f"[MASTERY UPDATED] Adjusted subject mastery levels for {self.active_subject}.")

            conn.close()
        except Exception as e:
            print(f"[NOTE] Mastery update skipped: {e}")