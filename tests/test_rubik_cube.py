"""Legal cube permutations plus the real CCv2 callback/persistence path."""

import json
from pathlib import Path
import shutil
import subprocess
import unittest

from streamlit.proto.WidgetStates_pb2 import WidgetStates
from streamlit.testing.v1 import AppTest


ROOT = Path(__file__).resolve().parents[1]


class RubikCubeTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("node"), "Node is required for cube-engine tests")
    def test_legal_turns_scrambles_and_retraces(self):
        result = subprocess.run(
            [shutil.which("node"), str(ROOT / "tests" / "test_rubik_cube.mjs")],
            cwd=ROOT, text=True, capture_output=True, timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("complete retraces pass", result.stdout)

    def test_frontend_callback_survives_rerun_and_navigation(self):
        # CCv2 is still an UnknownElement in AppTest, so send the exact JSON
        # widget payload used by setStateValue to exercise Streamlit dispatch.
        script = f"""
import sys
sys.path.insert(0, {str(ROOT)!r})
import streamlit as st
from ui.rubik_cube import render_rubik_cube
if st.checkbox("Show cube", value=True, key="show_cube"):
    render_rubik_cube(key="test_cube")
st.button("Another action")
"""
        app = AppTest.from_string(script).run()
        self.assertEqual(len(app.exception), 0)
        component = app.get("bidi_component")[0]
        self.assertTrue(component.proto.isolate_styles)
        puzzle = {
            "history": [{"face": "R", "turns": 1}, {"face": "F", "turns": -1}],
            "selected": "F", "yaw": -0.2, "pitch": 0.8, "revision": 2,
        }
        frontend = WidgetStates()
        frontend.widgets.add(id=component.proto.id, json_value=json.dumps({"puzzle": puzzle}))
        app._run(widget_state=frontend)
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(app.session_state["_test_cube_puzzle_snapshot"], puzzle)
        self.assertEqual(json.loads(app.get("bidi_component")[0].proto.json)["puzzle"], puzzle)

        app.button[0].click().run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(json.loads(app.get("bidi_component")[0].proto.json)["puzzle"], puzzle)

        app.checkbox[0].uncheck().run()
        self.assertEqual(len(app.get("bidi_component")), 0)
        self.assertEqual(app.session_state["_test_cube_puzzle_snapshot"], puzzle)
        app.checkbox[0].check().run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(json.loads(app.get("bidi_component")[0].proto.json)["puzzle"], puzzle)


if __name__ == "__main__":
    unittest.main()
