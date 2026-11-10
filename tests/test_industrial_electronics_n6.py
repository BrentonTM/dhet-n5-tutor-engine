"""Check that the attachment-backed course is usable without local PDFs or AI."""

import unittest
from pathlib import Path
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

from ui.industrial_electronics_n6 import BY_TOPIC, CODE, ICASS_URL


class IndustrialElectronicsN6Tests(unittest.TestCase):
    def test_n6_course_uses_the_mapped_lessons_and_practice_bank(self):
        root = Path(__file__).resolve().parents[1]
        with (
            patch("ui.student_identity.require_student", return_value={"display_name": "Course QA", "student_id": "qa"}),
            patch("ui.device_guide.render_first_use_guide"),
        ):
            app = AppTest.from_file(root / "app.py", default_timeout=30).run()
            next(box for box in app.selectbox if box.label == "N-level:").select("N6").run()
            subject = next(box for box in app.selectbox if box.label == "Subject:")
            subject.select("Industrial Electronics — DHET map available").run()
            self.assertFalse(app.exception)
            self.assertEqual(app.selectbox(key="home_live_model_IE-N6").value, "rc_response")

            app.button(key="home_continue").click().run()
            modules = app.selectbox(key="lesson_topic_IE-N6")
            self.assertEqual(modules.options, list(BY_TOPIC))
            modules.select("Robotics").run()
            self.assertTrue(any("Module 9 · Robotics" in item.value for item in app.markdown))

            app.session_state["tutor_section"] = "🧠 Flashcards"
            app.run()
            decks = app.selectbox(key="flashcard_filter_IE-N6")
            self.assertTrue(set(BY_TOPIC) <= set(decks.options))
            decks.select("Robotics").run()
            self.assertFalse(app.exception)

            app.session_state["learning_workspace"] = "📝 Practice"
            app.run()
            next(button for button in app.button if button.label == "Start a 7-question practice set").click().run()
            practice = app.session_state["practice_set"]
            self.assertEqual(len({item["topic"] for item in practice}), 7)
            self.assertTrue(all(item["subject"] == CODE and item["original_practice"] for item in practice))

            app.session_state["learning_workspace"] = "⏱ Mock exam"
            app.run()
            next(slider for slider in app.slider if slider.label == "Number of Questions:").set_value(18).run()
            next(button for button in app.button if button.label == "🚀 Start Mock Exam").click().run()
            self.assertEqual(len({item["id"] for item in app.session_state["exam_paper"]}), 18)
            self.assertFalse(app.exception)

            app.session_state["learning_workspace"] = "📐 Formula hub"
            app.run()
            self.assertTrue(any(element.proto.url == ICASS_URL for element in app.get("link_button")))
            self.assertFalse(app.exception)
