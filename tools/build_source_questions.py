"""Build the Digital Electronics N4 source index without guessing PDF notation.

Usage: python tools/build_source_questions.py SOURCE_DIRECTORY
Scanned papers without extractable QUESTION headings are reported and left out.
Original PDFs are copied unchanged; memorandums and cover pages are never questions.
"""

import argparse
import hashlib
import json
import logging
import re
import shutil
from pathlib import Path

from pypdf import PdfReader

HEADING = re.compile(r"(?im)^[ \t]*QUESTION[ \t\r\n]+(\d+)\b[^\n]*")


def has_body(text):
    lines = []
    for line in text.splitlines():
        line = line.strip()
        if re.search(r"Copyright|Please turn over|NATED GO|^\(?\d{7}\)?|^SECTION [AB]$", line, re.I):
            continue
        if re.search(r"[A-Za-z0-9]", line):
            lines.append(line)
    return bool(lines)


def extract_questions(reader):
    records = []
    current = None
    for page_number, page in enumerate(reader.pages, 1):
        text = page.extract_text() or ""
        pos = 0
        for match in HEADING.finditer(text):
            segment = text[pos:match.start()]
            if current and has_body(segment):
                current["text"] += segment
                current["pages"].add(page_number)
            number = match.group(1)
            if not current or current["number"] != number:
                current = {"number": number, "text": "", "pages": set()}
                records.append(current)
            pos = match.start()
        if current and has_body(text[pos:]):
            current["text"] += text[pos:]
            current["pages"].add(page_number)
    return records


def build(source_dir, repo_dir):
    destination = repo_dir / "data" / "past_papers"
    source_output = destination / "sources" / "DIGI-N4"
    source_output.mkdir(parents=True, exist_ok=True)
    questions = []
    skipped = []
    files = sorted(path for path in source_dir.glob("*.pdf") if "QP" in path.name.upper())
    for path in files:
        reader = PdfReader(path)
        records = extract_questions(reader)
        if not records:
            skipped.append(path.name)
            continue
        signature = hashlib.sha256(path.read_bytes()).hexdigest()
        for record in records:
            totals = re.findall(r"\[\s*(\d{1,3})\s*\]", record["text"])
            if not totals or not 0 < int(totals[-1]) <= 100:
                raise ValueError(f"Cannot establish total marks: {path.name} Q{record['number']}")
            num = f"Q{record['number']}"
            questions.append({
                "id": f"{signature[:12]}-{num}", "subject": "DIGI-N4", "num": num,
                "topic": "Original past paper", "marks": int(totals[-1]),
                "text": f"Answer original {num} in {path.name}; use the attached original PDF pages.",
                "marking": "No verified marking memo is attached. Assess against the original question and its printed marks; do not invent an official memo.",
                "source_file": f"data/past_papers/sources/DIGI-N4/{path.name}",
                "source_label": path.stem, "source_pages": sorted(record["pages"]),
                "source_sha256": signature,
            })
        shutil.copyfile(path, source_output / path.name)
    payload = {"version": 1, "subjects": ["DIGI-N4"], "questions": questions}
    (destination / "source_questions.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"papers": len(files) - len(skipped), "questions": len(questions), "unindexed_scans": skipped}, indent=2))


if __name__ == "__main__":
    logging.getLogger("pypdf").setLevel(logging.ERROR)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_dir", type=Path)
    parser.add_argument("--repo-dir", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    build(args.source_dir, args.repo_dir)
