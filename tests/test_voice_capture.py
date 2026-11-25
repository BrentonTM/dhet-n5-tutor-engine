import base64
import ast
from io import BytesIO
from pathlib import Path
import struct
from types import SimpleNamespace
import unittest
from unittest.mock import Mock
import wave

from ui.voice_capture import MAX_RECORDING_BYTES, decode_voice_recording


def wav_bytes(*, silent=False, channels=1, rate=16000, frames=1600):
    target = BytesIO()
    with wave.open(target, "wb") as clip:
        clip.setnchannels(channels)
        clip.setsampwidth(2)
        clip.setframerate(rate)
        clip.writeframes(struct.pack("<h", 0 if silent else 1200) * frames * channels)
    return target.getvalue()


def event(audio):
    return {"id": "test-recording", "mime_type": "audio/wav",
            "audio_base64": base64.b64encode(audio).decode("ascii")}


class VoiceCaptureTests(unittest.TestCase):
    def controls(self, payload):
        result = SimpleNamespace(recording=payload, utterance=None)
        st = SimpleNamespace(session_state={}, warning=Mock())
        submit = Mock()
        namespace = dict(st=st, latest_reply="", widget_prefix="test", subject="INST-N5",
                         render_puter_voice=Mock(return_value=result),
                         decode_voice_recording=decode_voice_recording, _submit_tutor_message=submit)
        tree = ast.parse((Path(__file__).resolve().parents[1] / "app.py").read_text(encoding="utf-8"))
        control = next(node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and node.name == "voice_controls")
        exec(compile(ast.Module(body=[control], type_ignores=[]), "app.py", "exec"), namespace)
        return namespace["voice_controls"], st, submit

    def test_real_component_handler_submits_audio_once_to_the_selected_subject(self):
        audio = wav_bytes()
        controls, st, submit = self.controls(event(audio))
        controls()
        controls()
        submit.assert_called_once_with(audio=audio, subject="INST-N5")
        st.warning.assert_not_called()

    def test_real_component_handler_reports_silence_without_sending_it(self):
        controls, st, submit = self.controls(event(wav_bytes(silent=True)))
        controls()
        submit.assert_not_called()
        self.assertIn("No sound", st.warning.call_args.args[0])

    def test_valid_recording_reaches_the_tutor_as_original_wav_bytes(self):
        original = wav_bytes()
        audio, error = decode_voice_recording(event(original))
        self.assertIsNone(error)
        self.assertEqual(audio, original)

    def test_silence_has_an_actionable_microphone_error(self):
        audio, error = decode_voice_recording(event(wav_bytes(silent=True)))
        self.assertIsNone(audio)
        self.assertIn("No sound", error)
        self.assertIn("Settings", error)

    def test_bad_payloads_do_not_echo_data_or_reach_the_model(self):
        for payload in (None, {}, {"id": 3}, {"id": "test", "mime_type": "audio/wav", "audio_base64": "private-not-base64"},
                        event(b"not a recording"), event(wav_bytes()[:-3]), event(wav_bytes(channels=2)),
                        event(wav_bytes(rate=48000)), event(wav_bytes(frames=0))):
            with self.subTest(payload_type=type(payload).__name__):
                audio, error = decode_voice_recording(payload)
                self.assertIsNone(audio)
                self.assertIsInstance(error, str)
                self.assertNotIn("private-not-base64", error)

    def test_size_duration_mime_and_identity_are_bounded(self):
        valid = event(wav_bytes())
        excessive_duration = bytearray(wav_bytes())
        excessive_duration[40:44] = struct.pack("<I", 16000 * 2 * 61)
        for payload in (
            {**valid, "audio_base64": "A" * (MAX_RECORDING_BYTES * 2)},
            {**valid, "mime_type": "text/html"}, {**valid, "id": "x" * 81},
            event(excessive_duration),
        ):
            with self.subTest(fields=list(payload)):
                audio, error = decode_voice_recording(payload)
                self.assertIsNone(audio)
                self.assertIsNotNone(error)


if __name__ == "__main__":
    unittest.main()
