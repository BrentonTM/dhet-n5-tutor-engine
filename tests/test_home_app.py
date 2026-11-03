"""Exercise the real workspace with an explicitly mocked, already verified identity.

The production entry gate is tested separately; no bypass ships in the app.
"""
import unittest
from pathlib import Path
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]


class HomeAppTests(unittest.TestCase):
    def setUp(self):
        self.identity = patch("ui.student_identity.require_student", return_value={"display_name": "Breezy", "student_id": "test-student"})
        self.guide = patch("ui.device_guide.render_first_use_guide")
        self.reply = patch("ui.gemini_client.generate_reply", return_value=("Let's check the span together, Breezy.", None))
        self.identity.start()
        self.guide.start()
        self.model = self.reply.start()
        self.addCleanup(self.identity.stop)
        self.addCleanup(self.guide.stop)
        self.addCleanup(self.reply.stop)

    def home(self):
        app = AppTest.from_file(ROOT / "app.py", default_timeout=25).run()
        self.assertEqual(len(app.exception), 0)
        return app

    def test_home_shortcuts_open_practice_and_native_recorder(self):
        app = self.home()
        self.assertTrue(any("Breezy" in title.value for title in app.title))
        self.assertEqual(len(app.chat_input), 1)
        self.assertEqual(len(app.audio_input), 0)
        app.button(key="home_shortcut_📝 Practice_None").click().run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(app.session_state["learning_workspace"], "📝 Practice")
        self.assertEqual(len(app.audio_input), 1)
        self.assertFalse(any("Live engineering model:" in node.proto.alt for node in app.get("iframe")))
        app.button[0]  # Native controls remain present after navigation.

    def test_live_model_and_tips_are_restored_and_full_lab_keeps_selected_model(self):
        app = self.home()
        models = [node for node in app.get("iframe") if node.proto.alt.startswith("Live engineering model:")]
        tips = [node for node in app.get("iframe") if node.proto.alt.startswith("Live engineering tips:")]
        self.assertEqual(len(models), 1)
        self.assertEqual(len(tips), 1)
        self.assertIn("Rotameter", models[0].proto.alt)
        self.assertNotIn("__SLIDES_JSON__", tips[0].proto.srcdoc)
        self.assertNotIn("__AUTO_PLAY__", tips[0].proto.srcdoc)
        app.selectbox(key="home_live_model_INST-N5").select("venturi").run()
        self.assertEqual(len(app.exception), 0)
        app.button(key="home_open_model_lab").click().run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(app.session_state["learning_workspace"], "🤖 Tutor & lab")
        self.assertEqual(app.selectbox(key="interactive_3d_lab_diagram_Industrial Instruments N5").value, "venturi")

    def test_course_change_updates_the_live_gallery_and_tip_content(self):
        app = self.home()
        subject = next(box for box in app.selectbox if box.label == "Subject:")
        subject.select(next(option for option in subject.options if option.startswith("Mathematics"))).run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(app.selectbox(key="home_live_model_MATH-N5").value, "derivative")
        tips = next(node for node in app.get("iframe") if node.proto.alt.startswith("Live engineering tips:"))
        self.assertIn("Power rule for differentiation", tips.proto.srcdoc)

    def test_model_discussion_opens_tex_with_the_selected_model_context(self):
        app = self.home()
        app.selectbox(key="home_live_model_INST-N5").select("venturi").run()
        app.button(key="home_discuss_model").click().run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(app.session_state["learning_workspace"], "🤖 Tutor & lab")
        self.assertEqual(self.model.call_count, 1)
        request = self.model.call_args.args[0][0].parts[0].text
        self.assertIn("Venturi", request)
        self.assertIn("report the settings and readings", request)

    def test_tex_sends_real_turn_roles_and_remembers_across_navigation(self):
        app = self.home()
        app.chat_input(key="home_tex_chat_input").set_value("My transmitter range is 0–100 kPa.").run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(len(app.session_state["tex_conversations"]["INST-N5"]), 2)
        app.chat_input(key="home_tex_chat_input").set_value("What does 12 mA represent?").run()
        self.assertEqual(len(app.exception), 0)
        contents = self.model.call_args.args[0]
        self.assertEqual([turn.role for turn in contents], ["user", "model", "user"])
        self.assertIn("0–100 kPa", contents[0].parts[0].text)
        self.assertIn("Breezy", self.model.call_args.kwargs["system_instruction"])
        app.button(key="home_progress").click().run()
        self.assertEqual(len(app.exception), 0)
        app.session_state["learning_workspace"] = "Home"
        app.run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(len(app.chat_message), 4)

    def test_real_anonymous_entry_renders_login_and_no_workspace(self):
        # Undo only the identity test double for this check of the real entry.
        self.identity.stop()
        app = AppTest.from_file(ROOT / "app.py", default_timeout=25).run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(len(app.chat_input), 0)
        self.assertTrue(app.button(key="student_google_login").disabled)

    def test_continue_restores_a_saved_custom_lesson(self):
        app = self.home()
        app.session_state["active_topic_lesson"] = {"subject": "INST-N5", "topic": "My custom flow problem", "notes": "Saved lesson content"}
        app.run()
        app.button(key="home_continue").click().run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(app.text_input(key="custom_topic_INST-N5").value, "My custom flow problem")
        self.assertTrue(any("Saved lesson content" in element.value for element in app.markdown))

    def test_planned_course_keeps_the_account_controls(self):
        app = self.home()
        next(box for box in app.selectbox if box.label == "N-level:").select("N6").run()
        self.assertEqual(len(app.exception), 0)
        self.assertTrue(any("not been integrated" in message.value for message in app.info))
        self.assertEqual(app.button(key="student_logout").label, "Sign out")

    def test_new_n4_courses_route_to_their_own_models_and_questions(self):
        app = self.home()
        next(box for box in app.selectbox if box.label == "N-level:").select("N4").run()
        self.assertFalse(app.exception)
        self.assertEqual(app.selectbox(key="home_live_model_MATH-N4").value, "unit_circle")
        app.button(key="home_shortcut_📝 Practice_None").click().run()
        next(button for button in app.button if button.label == "Start a 7-question practice set").click().run()
        self.assertEqual(app.session_state.current_question["subject"], "MATH-N4")
        self.assertTrue(app.session_state.current_question["original_practice"])
        seen = {app.session_state.current_question["id"]}
        for _ in range(6):
            next(button for button in app.button if button.label == "Next practice question").click().run()
            seen.add(app.session_state.current_question["id"])
        self.assertEqual(len(seen), 7)

        subject = next(box for box in app.selectbox if box.label == "Subject:")
        subject.select(next(option for option in subject.options if option.startswith("Industrial Electronics"))).run()
        self.assertIsNone(app.session_state.current_question)
        next(button for button in app.button if button.label == "Start a 7-question practice set").click().run()
        self.assertEqual(app.session_state.current_question["subject"], "IE-N4")
        self.assertFalse(app.exception)
        app.session_state["learning_workspace"] = "Home"
        app.run()
        app.button(key="home_shortcut_⏱ Mock exam_None").click().run()
        count = next(slider for slider in app.slider if slider.label == "Number of Questions:")
        self.assertEqual(count.value, 7)
        count.set_value(12).run()
        next(button for button in app.button if "Start Mock Exam" in button.label).click().run()
        paper = app.session_state.exam_paper
        self.assertEqual(len({item["id"] for item in paper}), 12)
        self.assertEqual({item["subject"] for item in paper}, {"IE-N4"})
        self.assertFalse(app.exception)
