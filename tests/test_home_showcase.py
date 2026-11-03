import unittest

from ui.home_showcase import HOME_MODELS, LAB_SUBJECTS
from ui.diagram_registry import get_spec


class HomeShowcaseTests(unittest.TestCase):
    def test_every_home_model_builds_a_real_lab_scene(self):
        self.assertEqual(set(HOME_MODELS), set(LAB_SUBJECTS))
        for subject, models in HOME_MODELS.items():
            for model_id in models:
                with self.subTest(subject=subject, model=model_id):
                    model = get_spec(model_id)
                    self.assertIsNotNone(model)
                    self.assertTrue(model["objects"])
                    self.assertTrue(model["params"])
                    self.assertTrue(model["title"])


if __name__ == "__main__":
    unittest.main()
