"""Select exam questions and preserve notation through original PDF pages."""

import json
import random
import re
import sqlite3
from contextlib import closing
from io import BytesIO
from pathlib import Path

from ui.n4_courses import starter_questions

CONTENT_VERSION = "all-subject-papers-and-memos-v3"


def list_documents(base_dir, subject_code):
    path = Path(base_dir) / "data" / "past_papers" / "source_questions.json"
    if not path.is_file():
        return []
    index = json.loads(path.read_text(encoding="utf-8"))
    return sorted(
        [document for document in index.get("documents", []) if document["subject"] == subject_code],
        key=lambda document: (document["exam_date"], document["kind"] == "paper"), reverse=True,
    )


def guidance_documents(questions):
    """Combine repeated source pages and keep original memos distinct from papers."""
    grouped = {}
    for question in questions:
        for source_file, pages, label in [
            (question.get("source_file"), question.get("source_pages", []) + question.get("reference_pages", []), question.get("source_label")),
            (question.get("memo_file"), question.get("memo_pages", []), question.get("memo_label")),
        ]:
            if not source_file:
                continue
            group = grouped.setdefault(source_file, {"source_file": source_file, "source_pages": set(), "label": label})
            group["source_pages"].update(pages)
    return [dict(group, source_pages=sorted(group["source_pages"])) for group in grouped.values()]


def question_pdf(base_dir, question):
    """Return only the referenced pages, preserving the original PDF graphics."""
    from pypdf import PdfReader, PdfWriter

    root = Path(base_dir).resolve()
    source = (root / question["source_file"]).resolve()
    if not source.is_relative_to(root / "data" / "past_papers" / "sources"):
        raise ValueError("Question source must be in the bundled paper library")
    reader = PdfReader(source)
    writer = PdfWriter()
    for page_number in question["source_pages"]:
        if not isinstance(page_number, int) or not 1 <= page_number <= len(reader.pages):
            raise ValueError("Question refers to an invalid source page")
        writer.add_page(reader.pages[page_number - 1])
    output = BytesIO()
    writer.write(output)
    return output.getvalue()


def original_pdf(base_dir, source_file):
    root = Path(base_dir).resolve()
    source = (root / source_file).resolve()
    if not source.is_relative_to(root / "data" / "past_papers" / "sources"):
        raise ValueError("Document source must be in the bundled paper library")
    return source.read_bytes()


def select_questions(base_dir, subject_code, limit=1, rng=None):
    """Prefer the source index; legacy queries match the exact subject and level."""
    root = Path(base_dir)
    index_path = root / "data" / "past_papers" / "source_questions.json"
    if index_path.exists():
        index = json.loads(index_path.read_text(encoding="utf-8"))
        if subject_code in index["subjects"]:
            candidates = [q for q in index["questions"] if q["subject"] == subject_code]
            for question in candidates:
                if not (root / question["source_file"]).is_file():
                    raise FileNotFoundError("An original question paper is missing from the deployment")
            return (rng or random).sample(candidates, min(limit, len(candidates)))

    starter = starter_questions(subject_code)
    if starter:
        return (rng or random).sample(starter, min(limit, len(starter)))

    database = root / "data" / "databases" / "past_papers.db"
    if not database.is_file():
        return []
    with closing(sqlite3.connect(database.resolve().as_uri() + "?mode=ro", uri=True)) as conn:
        rows = conn.execute(
            "SELECT question_id, question_number, topic_name, question_text, "
            "marking_guideline, marks FROM paper_questions WHERE subject_code = ?",
            (subject_code,),
        ).fetchall()
    candidates = []
    for ident, num, topic, text, marking, marks in rows:
        # The old importer indexed cover pages and memorandum placeholders.
        if (
            not text or not re.match(r"\s*QUESTION\s+\d+\b", text, re.IGNORECASE)
            or "refer to question sheet" in text.lower()
            or not isinstance(marks, int) or not 0 < marks <= 100
        ):
            continue
        candidates.append({
            "id": f"legacy-{ident}", "subject": subject_code, "num": num,
            "topic": topic, "text": text, "marking": marking, "marks": marks,
        })
    return (rng or random).sample(candidates, min(limit, len(candidates)))
