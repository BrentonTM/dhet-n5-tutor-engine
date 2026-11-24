import json
import unittest
from pathlib import Path

from ui.tex_app_control import action_requested, assistance_instruction, decode_action, direct_navigation, validate_action
from ui.tex_partner import partner_instruction
from ui.tex_voice import lesson_instruction


class TexAppControlTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = json.loads((Path(__file__).resolve().parents[1] / "config/programme_catalog.json").read_text())

    def validate(self, action):
        return validate_action(action, self.catalog, programme_id="electrical_instrumentation", level="N5", subject_id="industrial_instruments")

    def test_simple_navigation_does_not_need_an_ai_request(self):
        self.assertEqual(direct_navigation("Please open the 3D lab."), {"feature": "lab"})
        self.assertEqual(direct_navigation("Open study reminders"), {"feature": "reminders"})
        self.assertIsNone(direct_navigation("Show me how a venturi works"))

    def test_questions_and_negative_requests_do_not_authorize_navigation(self):
        self.assertFalse(action_requested("How do I open the lab?"))
        self.assertFalse(action_requested("Don't switch subjects. Explain current."))
        self.assertFalse(action_requested("Explain the textbook"))
        self.assertTrue(action_requested("Switch to Mathematics N4"))
        self.assertTrue(action_requested("", audio=True))

    def test_arbitrary_state_code_and_unknown_features_are_rejected(self):
        for action in ({"feature": "lab", "api_key": "x"}, {"feature": "delete_account"},
                       {"feature": "lab", "model": ["venturi"]}, {"feature": "lessons", "start_lesson": "yes"},
                       {"feature": "lab", "topic": "Flow"}):
            self.assertIsNotNone(self.validate(action)[1])

    def test_course_selection_is_validated_against_the_real_catalog(self):
        plan, error = self.validate({"feature": "lessons", "level": "N4", "subject_id": "mathematics", "topic": "Integration"})
        self.assertIsNone(error)
        self.assertEqual(plan["level"], "N4")
        for action in ({"level": "N7"}, {"subject_id": "medicine"}, {"programme_id": "imaginary"}):
            self.assertIsNotNone(self.validate(action)[1])

    def test_actions_are_not_shown_or_read_aloud_and_multiple_actions_are_rejected(self):
        text, action = decode_action('I will open the lab. <tex_action>{"feature":"lab"}</tex_action>')
        self.assertEqual(text, "I will open the lab.")
        self.assertEqual(action, {"feature": "lab"})
        text, action = decode_action('Opening Venturi. <text_action>{"feature":"lab","model":"venturi"}</text_action>')
        self.assertEqual(action, {"feature": "lab", "model": "venturi"})
        self.assertNotIn("action", text)
        self.assertIsNone(decode_action('<tex_action>{"feature":"lab"}</tex_action><tex_action>{}</tex_action>')[1])
        self.assertEqual(decode_action('Hello <tex_action>bad JSON')[0], 'Hello')

    def test_help_context_and_humour_do_not_claim_unavailable_powers(self):
        prompt = assistance_instruction(self.catalog, {"name": "Instruments"}, programme_id="electrical_instrumentation",
                                         level="N5", subject_id="industrial_instruments", workspace="Home")
        self.assertIn("practice", prompt)
        self.assertIn("browser-dependent", prompt)
        self.assertIn("Do not claim to adjust a 3D slider", prompt)
        self.assertIn("Actions allowed for this turn: False", prompt)
        for instruction in (partner_instruction("Sam", "INST-N5"), lesson_instruction("INST-N5", "Flow", "notes")):
            self.assertIn("Never tease", instruction)
            self.assertIn("serious tone", instruction)


if __name__ == "__main__":
    unittest.main()
