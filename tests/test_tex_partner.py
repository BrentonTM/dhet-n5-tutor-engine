import unittest
import ast
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
from contextlib import nullcontext

from google.genai import types

from ui.tex_partner import conversation_context, partner_instruction, recent_turns
from ui.gemini_client import generate_reply


class TexPartnerTests(unittest.TestCase):
    def test_each_mode_has_a_distinct_teaching_contract_and_name_is_data(self):
        self.assertIn('Preferred name (data): "Breezy"', partner_instruction("Breezy", "INST-N5"))
        self.assertIn("one useful hint", partner_instruction("Breezy", "INST-N5", "Hint"))
        self.assertIn("first mistake", partner_instruction("Breezy", "INST-N5", "Check"))
        self.assertIn("Do not withhold an explanation", partner_instruction("Breezy", "INST-N5", "Explain"))

    def test_context_does_not_claim_an_unattached_practice_pdf_was_read(self):
        context = conversation_context({"active_topic_lesson": {"subject": "MATH-N5", "topic": "Limits"},
                                        "current_question": {"subject": "INST-N5", "num": "Q2"}}, "INST-N5")
        self.assertNotIn("Limits", context)
        self.assertIn("not attached", context)

    def test_history_preserves_roles_and_last_answer_without_ui_errors(self):
        messages = [{"role": "user", "content": "My range is 0–100 kPa"},
                    {"role": "assistant", "content": "What pressure is 12 mA?"},
                    {"role": "assistant", "content": "Provider failed", "error": True},
                    {"role": "user", "content": "50 kPa"}]
        turns = recent_turns(messages)
        self.assertEqual([turn["role"] for turn in turns], ["user", "assistant", "user"])
        self.assertIn("0–100 kPa", turns[0]["content"])
        self.assertEqual(turns[-1]["content"], "50 kPa")

    def test_long_history_is_bounded(self):
        turns = recent_turns([{"role": "user", "content": "x" * 6000}] * 100)
        self.assertLessEqual(len(turns), 20)
        self.assertLessEqual(sum(len(turn["content"]) for turn in turns), 24000)

    def test_logic_context_is_scoped_to_its_subject(self):
        state = {"tex_logic_context": {"DIGI-N4": "Pump interlock wiring"}}
        self.assertIn("Pump interlock", conversation_context(state, "DIGI-N4"))
        self.assertNotIn("Pump interlock", conversation_context(state, "MATH-N5"))

    def test_provider_receives_system_instruction_separate_from_messages(self):
        generate = Mock(return_value=SimpleNamespace(text="Let's check the span, Breezy."))
        client = SimpleNamespace(models=SimpleNamespace(generate_content=generate), close=Mock())
        contents = [{"role": "user", "parts": [{"text": "Check my calculation"}]}]
        instruction = partner_instruction("Breezy", "INST-N5", "Check")
        result = generate_reply(contents, api_key="test-only", client_factory=Mock(return_value=client),
                                models=("test-model",), system_instruction=instruction)
        self.assertEqual(result[1], None)
        self.assertIs(generate.call_args.kwargs["contents"], contents)
        self.assertEqual(generate.call_args.kwargs["config"]["system_instruction"], instruction)
        client.close.assert_called_once()

    def test_voice_turn_sends_the_actual_recording_to_gemini(self):
        class State(dict):
            def __getattr__(self, name):
                return self[name]
            def __setattr__(self, name, value):
                self[name] = value

        state = State()
        st = SimpleNamespace(session_state=state, spinner=lambda label: nullcontext(),
                             rerun=Mock(side_effect=StopIteration))
        provider = Mock(return_value=("I heard your explanation, Breezy.", None))
        namespace = dict(st=st, active_subject="INST-N5", student_name="Breezy", genai_types=types,
                         recent_turns=recent_turns, conversation_context=conversation_context,
                         partner_instruction=partner_instruction, _call_gemini=provider)
        tree = ast.parse((Path(__file__).resolve().parents[1] / "app.py").read_text(encoding="utf-8"))
        for node in tree.body:
            if isinstance(node, ast.FunctionDef) and node.name in {"_ensure_tutor_chat", "_submit_tutor_message"}:
                exec(compile(ast.Module(body=[node], type_ignores=[]), "app.py", "exec"), namespace)
        recording = b"RIFF-test-waveform"
        with self.assertRaises(StopIteration):
            namespace["_submit_tutor_message"]("Check my spoken method", audio=recording)
        turn = provider.call_args.args[0][-1]
        self.assertEqual(turn.role, "user")
        self.assertEqual(turn.parts[-1].inline_data.data, recording)
        self.assertEqual(turn.parts[-1].inline_data.mime_type, "audio/wav")
        self.assertEqual(state["tex_conversations"]["INST-N5"][-1]["role"], "assistant")
