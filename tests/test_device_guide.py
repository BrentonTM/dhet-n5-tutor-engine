import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from ui.device_guide import initialize_guide, apply_guide_action, available_steps, prepare_feature_guide
from ui.guide_preferences import guide_cookie_name
from ui.guide_steps import GUIDE_STEPS
from ui.tex_app_control import FEATURES


class DeviceGuideTests(unittest.TestCase):
    def test_account_claim_is_once_even_if_the_first_tour_is_skipped(self):
        claim = Mock(side_effect=[True, False])
        first = {}
        initialize_guide(first, "student-a", "database", False, claim)
        self.assertTrue(first["first_use_guide_open"])
        initialize_guide(first, "student-a", "database", False, claim)
        self.assertEqual(claim.call_count, 1)
        returning = {}
        initialize_guide(returning, "student-a", "database", False, claim)
        self.assertFalse(returning["first_use_guide_open"])
        self.assertEqual(returning["_guide_persistence"], "account")

    def test_cookie_fallback_is_separate_for_each_student(self):
        state = {}
        initialize_guide(state, "student-a", None, True)
        self.assertFalse(state["first_use_guide_open"])
        initialize_guide(state, "student-b", None, False)
        self.assertTrue(state["first_use_guide_open"])
        self.assertNotEqual(guide_cookie_name("student-a"), guide_cookie_name("student-b"))

    def test_store_failure_preserves_browser_seen_choice(self):
        state = {}
        initialize_guide(state, "student-a", "database", True, Mock(side_effect=OSError("private dsn")))
        self.assertFalse(state["first_use_guide_open"])

    def test_every_step_has_a_valid_destination_and_useful_tip(self):
        self.assertGreater(len(GUIDE_STEPS), 20)
        self.assertEqual(len({row["id"] for row in GUIDE_STEPS}), len(GUIDE_STEPS))
        for row in GUIDE_STEPS:
            self.assertIn(row["feature"], FEATURES)
            self.assertTrue(row["target"] and row["tip"] and row["body"])

    def test_unavailable_features_are_skipped_and_tex_routes_to_resources(self):
        rows = available_steps(["Home", "📚 Study materials", "🎮 Games", "💸 Money Class", "🧭 Career readiness"], False, False, "mathematics-N6")
        self.assertFalse(any(row["id"] in {"practice", "lab", "interactive", "mock"} for row in rows))
        tex = next(row for row in rows if row["id"] == "tex")
        self.assertEqual(tex["feature"], "resources")
        self.assertTrue(tex["target"].startswith("resources_mathematics-N6"))

    def test_jump_opens_the_actual_feature_and_skip_restores_navigation(self):
        state = {"first_use_guide_open": True, "learning_workspace": "📚 Study materials"}
        ui = SimpleNamespace(session_state=state, set_page_config=Mock())
        workspaces = list({value[0] for value in FEATURES.values()})
        with patch("ui.device_guide.st", ui):
            data = prepare_feature_guide(workspaces, integrated=True, has_lab=True)
            self.assertEqual(data["step"]["id"], "welcome")
            apply_guide_action(state, {"id": "jump-1", "step": "welcome", "kind": "jump", "target": "lab"})
            data = prepare_feature_guide(workspaces, integrated=True, has_lab=True)
            self.assertEqual(state["tutor_section"], "🧊 3D lab")
            self.assertEqual(state["learning_workspace"], "🤖 Tutor & lab")
            action = {"id": "close-1", "step": "lab", "kind": "stop"}
            self.assertTrue(apply_guide_action(state, action))
            self.assertFalse(apply_guide_action(state, action))
            self.assertIsNone(prepare_feature_guide(workspaces, integrated=True, has_lab=True))
            self.assertEqual(state["learning_workspace"], "📚 Study materials")
            self.assertTrue(state["first_use_guide_complete"])

    def test_stale_or_unknown_navigation_events_cannot_skip_steps(self):
        state = {"first_use_guide_open": True, "_guide_current_id": "welcome", "_guide_step_ids": ["welcome", "lab"], "first_use_guide_step": 0}
        self.assertFalse(apply_guide_action(state, {"id": "x", "step": "lab", "kind": "next"}))
        self.assertFalse(apply_guide_action(state, {"id": "y", "step": "welcome", "kind": "jump", "target": "unknown"}))
        self.assertEqual(state["first_use_guide_step"], 0)


if __name__ == "__main__":
    unittest.main()
