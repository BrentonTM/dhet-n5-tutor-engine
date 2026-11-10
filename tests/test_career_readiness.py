"""Regression checks for the games and first career-readiness release."""

from pathlib import Path
import unittest
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

from ui.money_class import BUDGET_ITEMS, budget_result, trade_result


ROOT = Path(__file__).resolve().parents[1]


class CareerReadinessTests(unittest.TestCase):
    def open_app(self):
        identity = patch("ui.student_identity.require_student", return_value={
            "display_name": "Test learner", "student_id": "test-career-student",
        })
        guide = patch("ui.device_guide.render_first_use_guide")
        reply = patch("ui.gemini_client.generate_reply", return_value=("Example explanation", None))
        for mock in (identity, guide, reply):
            mock.start()
            self.addCleanup(mock.stop)
        app = AppTest.from_file(ROOT / "app.py", default_timeout=30).run()
        self.assertFalse(app.exception)
        return app

    def test_games_are_reachable_and_quiz_checks_an_answer(self):
        app = self.open_app()
        app.button(key="home_open_🎮 Games").click().run()
        self.assertFalse(app.exception)
        self.assertEqual(len(app.get("bidi_component")), 1)

        app.session_state["games_workspace"] = "Logic Builder"
        app.run()
        self.assertFalse(app.exception)
        self.assertTrue(any("Logic Builder" in item.value for item in app.subheader))

        app.session_state["games_workspace"] = "Resistor Decoder"
        app.run()
        app.radio(key="resistor_game_answer_0").set_value("1 kΩ ±5%").run()
        app.button(key="resistor_game_check_0").click().run()
        self.assertTrue(any("Correct" in item.value for item in app.success))

        app.session_state["games_workspace"] = "Fault Finder"
        app.run()
        self.assertFalse(app.exception)
        self.assertTrue(any("Fault Finder" in item.value for item in app.subheader))

    def test_money_budget_and_cv_update_the_meter_without_saving_draft_text(self):
        app = self.open_app()
        app.button(key="home_open_💸 Money Class").click().run()
        next(button for button in app.button if button.label == "Ask Tex about Gross pay").click().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.session_state["learning_workspace"], "💸 Money Class")
        self.assertEqual(len(app.session_state["tex_conversations"]["CAREER"]), 2)
        app.session_state["quick_tex"] = False
        app.selectbox(key="money_module").select("budget").run()
        next(button for button in app.button if button.label == "Test my month").click().run()
        self.assertFalse(app.exception)
        self.assertTrue(any(item.label == "After surprise" and item.value == "-R400" for item in app.metric))

        app.session_state["learning_workspace"] = "🧭 Career readiness"
        app.run()
        values = {"Target role": "Electrical apprentice", "Relevant training": "N5",
                  "Technical skills": "Circuit reading", "One project or work example": "Built a rectifier"}
        for widget in (*app.text_input, *app.text_area):
            if widget.label in values:
                widget.set_value(values[widget.label])
        next(button for button in app.button if button.label == "Build my drafts").click().run()
        self.assertFalse(app.exception)
        self.assertIn("Built a rectifier", app.session_state["career_application_drafts"][0])
        records = list(app.session_state["study_events"]["practice"].values())
        self.assertEqual({row["topic"] for row in records}, {"budget", "cv"})
        self.assertNotIn("rectifier", str(records))

    def test_fictional_budget_and_flat_trade_math(self):
        remaining, after_surprise, checks = budget_result(BUDGET_ITEMS, 900)
        self.assertEqual((remaining, after_surprise, sum(checks.values())), (500, -400, 3))
        self.assertEqual(trade_result(50, 50, 5, 10), (260, 240, -20))
