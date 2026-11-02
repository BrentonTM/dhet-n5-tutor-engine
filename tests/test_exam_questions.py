import ast
import hashlib
import json
import logging
import random
import sqlite3
import tempfile
import unittest
from io import BytesIO
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

from pypdf import PdfReader
from ui.exam_questions import question_pdf, select_questions

ROOT = Path(__file__).resolve().parents[1]


def app_function(name, namespace):
    tree = ast.parse((ROOT / "app.py").read_text(encoding="utf-8"))
    node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name)
    node.decorator_list = []
    exec(compile(ast.Module(body=[node], type_ignores=[]), "app.py", "exec"), namespace)
    return namespace[name]


class SourceQuestionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        logging.getLogger("pypdf").setLevel(logging.ERROR)
        cls.index = json.loads((ROOT / "data/past_papers/source_questions.json").read_text(encoding="utf-8"))
        cls.questions = cls.index["questions"]

    def test_all_indexed_questions_have_original_pages_and_matching_source_digests(self):
        self.assertEqual(len(self.questions), 72)
        self.assertEqual(len({q["id"] for q in self.questions}), 72)
        for question in self.questions:
            with self.subTest(question=question["id"]):
                original = (ROOT / question["source_file"]).read_bytes()
                self.assertEqual(hashlib.sha256(original).hexdigest(), question["source_sha256"])
                reader = PdfReader(BytesIO(question_pdf(ROOT, question)))
                self.assertEqual(len(reader.pages), len(question["source_pages"]))
                self.assertTrue(0 < question["marks"] <= 100)
                self.assertNotIn("MEMO", question["source_file"].upper())

    def test_screenshot_question_uses_full_printed_total_and_original_page(self):
        question = next(q for q in self.questions if q["source_file"].endswith("QP-AUG-2022-ed.pdf") and q["num"] == "Q1")
        self.assertEqual(question["marks"], 16)
        self.assertEqual(question["source_pages"], [3])
        binary = next(q for q in self.questions if q["source_file"].endswith("QP-APRIL-2022.pdf") and q["num"] == "Q4")
        self.assertEqual(binary["marks"], 20)
        self.assertEqual(binary["source_pages"], [6])

    def test_mock_sample_is_unique_and_never_crosses_subject_level(self):
        selected = select_questions(ROOT, "DIGI-N4", 15, random.Random(6))
        self.assertEqual(len(selected), 15)
        self.assertEqual(len({q["id"] for q in selected}), 15)
        self.assertEqual({q["subject"] for q in selected}, {"DIGI-N4"})

    def test_legacy_import_placeholders_and_covers_are_not_questions(self):
        with tempfile.TemporaryDirectory(dir=ROOT / "tests") as tmp:
            root = Path(tmp)
            (root / "data/databases").mkdir(parents=True)
            with sqlite3.connect(root / "data/databases/past_papers.db") as conn:
                conn.execute("CREATE TABLE paper_questions (question_id INTEGER, question_number TEXT, topic_name TEXT, question_text TEXT, marking_guideline TEXT, marks INTEGER, subject_code TEXT)")
                for i, text, marks, subject in [
                    (1, "Refer to question sheet for Q1", 5, "DIGI-N4"),
                    (2, "NATIONAL CERTIFICATE INSTRUCTIONS", 8080354, "DIGI-N4"),
                    (3, "QUESTION 1 Define a synchronous counter.", 5, "DIGI-N4"),
                    (4, "QUESTION 1 Explain the N5 circuit.", 5, "DIGI-N5"),
                ]:
                    conn.execute("INSERT INTO paper_questions VALUES (?, 'Q1', 'Review', ?, '', ?, ?)", (i, text, marks, subject))
            conn.close()
            result = select_questions(root, "DIGI-N4", 15)
            self.assertEqual([q["id"] for q in result], ["legacy-3"])

    def test_source_path_and_page_bounds_are_validated(self):
        with self.assertRaises(ValueError):
            question_pdf(ROOT, {"source_file": "../outside.pdf", "source_pages": [1]})
        invalid = dict(self.questions[0], source_pages=[999])
        with self.assertRaises(ValueError):
            question_pdf(ROOT, invalid)

    def test_display_uses_pdf_instead_of_damaged_transcription(self):
        question = self.questions[0]
        st = SimpleNamespace(caption=Mock(), pdf=Mock(), write=Mock())
        namespace = {"st": st, "cached_question_pdf": lambda *args: b"%PDF-sample"}
        app_function("render_selected_question", namespace)(question, "test")
        st.pdf.assert_called_once()
        st.write.assert_not_called()
        self.assertIn(question["num"], st.caption.call_args.args[0])

    def test_guidance_sends_real_question_pdf_to_model(self):
        question = self.questions[0]
        requests = []
        namespace = {
            "genai_types": SimpleNamespace(Part=SimpleNamespace(from_bytes=lambda **kwargs: kwargs)),
            "cached_question_pdf": lambda ident, source, pages: question_pdf(ROOT, {"source_file": source, "source_pages": pages}),
            "_call_gemini": lambda contents: requests.append(contents) or ("feedback", None),
        }
        reply, error = app_function("query_exam_guidance", namespace)("Review my work", [question, question])
        self.assertEqual(reply, "feedback")
        self.assertIsNone(error)
        attachments = [part for part in requests[0] if isinstance(part, dict)]
        self.assertEqual(len(attachments), 1)
        self.assertEqual(attachments[0]["mime_type"], "application/pdf")
        self.assertTrue(attachments[0]["data"].startswith(b"%PDF"))
        self.assertIn("original question pages", requests[0][0])


if __name__ == "__main__":
    unittest.main()
