import unittest
from pathlib import Path
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]


class DeviceGuideAppTests(unittest.TestCase):
    def test_first_visit_guide_can_skip_and_replay_without_ai_or_data_changes(self):
        with patch("ui.student_identity.require_student", return_value={"display_name": "Guide tester", "student_id": "guide-test"}), \
             patch("ui.device_guide._cookie_seen", return_value=False), \
             patch("ui.gemini_client.generate_reply") as model:
            app = AppTest.from_file(ROOT / "app.py", default_timeout=30).run()
            self.assertFalse(app.exception)
            self.assertTrue(app.session_state["first_use_guide_open"])
            self.assertEqual(app.session_state["_guide_current_id"], "welcome")
            self.assertEqual(app.session_state["learning_workspace"], "Home")
            app.session_state["guide_test_saved_work"] = "Keep this answer"
            app.button(key="close_first_use_guide").click().run()
            self.assertFalse(app.exception)
            self.assertFalse(app.session_state["first_use_guide_open"])
            app.run()
            self.assertFalse(app.session_state["first_use_guide_open"])
            app.button(key="replay_first_use_guide").click().run()
            self.assertFalse(app.exception)
            self.assertTrue(app.session_state["first_use_guide_open"])
            self.assertEqual(app.session_state["guide_test_saved_work"], "Keep this answer")
            model.assert_not_called()

    def test_returning_browser_does_not_launch_automatically(self):
        with patch("ui.student_identity.require_student", return_value={"display_name": "Returning tester", "student_id": "returning-test"}), \
             patch("ui.device_guide._cookie_seen", return_value=True):
            app = AppTest.from_file(ROOT / "app.py", default_timeout=30).run()
            self.assertFalse(app.exception)
            self.assertFalse(app.session_state["first_use_guide_open"])
            self.assertTrue(any(button.key == "replay_first_use_guide" for button in app.button))
