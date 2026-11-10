"""Regression tests for course matches, probe points and the study workspace."""

from pathlib import Path
import unittest
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

from ui.diagram_registry import get_spec
from ui.flashcards import DECKS, flashcard_groups
from ui.plant_fault_cases import FAULT_CASES
from ui.plant_fault_lab import fault_scene
from ui.study_visuals import decorate_study_model, study_models


ROOT = Path(__file__).resolve().parents[1]


class StudyVisualTests(unittest.TestCase):
    def test_course_scoped_models_and_exact_matches(self):
        self.assertEqual(study_models("IE-N4", "A full-wave bridge rectifies AC."), ("bridge_rectifier_3d",))
        self.assertEqual(study_models("IE-N5", "A non-inverting op-amp clips."), ("opamp_noninv",))
        self.assertEqual(study_models("DIGI-N5", "M2: Counter Design", lesson=True), ("ripple_counter_3d",))
        self.assertEqual(study_models("INST-N5", "A 4–20 mA transmitter feeds the PLC."), ("current_loop_3d",))
        self.assertEqual(study_models("MATH-N5", "A 4–20 mA transmitter feeds the PLC."), ())
        self.assertEqual(study_models("IE-N5", "See Figure 2."), ())

    def test_every_case_has_matching_physical_probe_points(self):
        self.assertEqual(sum(map(len, FAULT_CASES.values())), 18)
        for family, cases in FAULT_CASES.items():
            self.assertGreater(len(cases), 5, family)
            for case in cases:
                with self.subTest(case=case.id):
                    model = fault_scene(case)
                    names = model["params"][-1]["names"][1:]
                    self.assertEqual(names, [probe.part for probe in case.probes])
                    for index, probe in enumerate(case.probes, 1):
                        self.assertTrue(any(
                            part.get("label") == probe.part and part.get("click") == {"probePoint": index}
                            for part in model["objects"]
                        ), probe.part)
                    self.assertNotIn(case.cause, str(model["readouts"]))

    def test_new_circuits_have_assembly_controls_and_original_decks_survive(self):
        for diagram in ("dc_resistor_network", "current_loop_3d", "ripple_counter_3d", "bridge_rectifier_3d"):
            with self.subTest(diagram=diagram):
                model = decorate_study_model(diagram, get_spec(diagram))
                self.assertTrue(any(control["id"] == "assembly" for control in model["params"]))
                self.assertTrue(any(part.get("outline") and part.get("explode") for part in model["objects"]))
        for subject in DECKS:
            self.assertGreaterEqual(sum(map(len, flashcard_groups(subject).values())), 9)
        self.assertEqual(flashcard_groups("MATH-N5", [{"q": "Original", "a": "Preserved"}])["Course exercises"],
                         (("Original", "Preserved"),))


class StudyWorkspaceTests(unittest.TestCase):
    def test_flashcards_review_and_fault_walkthrough_are_reachable(self):
        with patch("ui.student_identity.require_student", return_value={"display_name": "Test learner", "student_id": "test-visuals"}), \
             patch("ui.device_guide.render_first_use_guide"):
            app = AppTest.from_file(ROOT / "app.py", default_timeout=25).run()
            app.session_state["learning_workspace"] = "🤖 Tutor & lab"
            app.session_state["tutor_section"] = "🧠 Flashcards"
            app.run()
            self.assertFalse(app.exception)
            self.assertTrue(any("23 cards" in item.value for item in app.caption))
            app.button(key="flash_INST-N5_reveal").click().run()
            app.button(key="flash_INST-N5_review").click().run()
            app.selectbox(key="flashcard_filter_INST-N5").select("Flagged for review").run()
            self.assertTrue(any("Card 1 of 1" in item.value for item in app.info))

            app.session_state["learning_workspace"] = "📝 Practice"
            app.run()
            next(radio for radio in app.radio if radio.label == "Select Practice Mode:").set_value("Plant fault diagnosis").run()
            self.assertFalse(app.exception)
            self.assertEqual(len([item for item in app.get("iframe") if item.proto.alt.startswith("3D diagnostic model:")]), 1)
            self.assertFalse(any("Likely cause" in item.value for item in app.markdown))
            app.text_area(key="diagnosis_answer_INST-N5_loop-open").set_value("The isolated junction continuity check is open.")
            app.button(key="diagnosis_check_INST-N5_loop-open").click().run()
            self.assertFalse(app.exception)
            self.assertTrue(any("An open junction" in item.value for item in app.markdown))
