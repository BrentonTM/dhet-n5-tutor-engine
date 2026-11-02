"""Build all subject paper/memo indexes while retaining original PDF notation.

Usage: python tools/build_source_questions.py SOURCE_DIRECTORY
Point SOURCE_DIRECTORY at the past_papers folder containing the four subject folders.
Scanned files remain available in the library; only complete, validated question
sequences enter random practice. Memo pairing uses printed cover dates, never names.
"""

import argparse
import hashlib
import json
import logging
import re
import shutil
from pathlib import Path
from datetime import datetime

from pypdf import PdfReader

HEADING = re.compile(r"(?im)^[ \t]*" + r"[ \t\r\n]*".join("QUESTION") + r"[ \t\r\n]+(\d+)\b[^\n]*")
END_PAPER = re.compile(r"(?im)^\s*(?:GRAND\s+)?TOTAL\s*:?\s*100\b")
SUBJECTS = {
    "digital_electronics_n4": ("DIGI-N4", "DIGITALELECTRONICSN4"),
    "industrial_electronics_n5": ("IE-N5", "INDUSTRIALELECTRONICSN5"),
    "industrial_instruments_n5": ("INST-N5", "INDUSTRIALINSTRUMENTSN5"),
    "mathematics_n5": ("MATH-N5", "MATHEMATICSN5"),
}


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
        final = END_PAPER.search(text) if current else None
        if final:
            text = text[:final.end()]
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
        if final:
            break
    return records


def printed_date(text):
    flat = re.sub(r"(20)\s+(\d{2})\b", r"\1\2", " ".join(text.split()))
    flat = flat.replace("Augustus", "August")
    match = re.search(r"\b(\d{1,2}|XX)\s+([A-Za-z]+)\s+(20\d{2})\b", flat, re.I)
    if not match:
        return None
    day, month, year = match.groups()
    try:
        stamp = datetime.strptime(f"{day if day.upper() != 'XX' else '1'} {month} {year}", "%d %B %Y")
    except ValueError:
        return None
    return stamp.strftime("%Y-%m" if day.upper() == "XX" else "%Y-%m-%d")


def printed_marks(text):
    bracketed = re.findall(r"\[\s*(\d{1,3})\s*\]", text)
    if bracketed:
        return int(bracketed[-1])
    terminal = re.search(r"\(\s*(\d{1,3})\s*\)\s*$", text)
    return int(terminal.group(1)) if terminal else None


def build(source_dir, repo_dir):
    destination = repo_dir / "data" / "past_papers"
    overrides = json.loads((repo_dir / "tools/source_metadata_overrides.json").read_text(encoding="utf-8"))
    documents, questions, excluded = [], [], []
    by_digest, groups = {}, {}
    for folder, (subject, expected_title) in SUBJECTS.items():
        for path in sorted((source_dir / folder).glob("*.pdf")):
            signature = hashlib.sha256(path.read_bytes()).hexdigest()
            if signature in by_digest:
                by_digest[signature]["aliases"].append(path.name)
                continue
            reader = PdfReader(path)
            head = "\n".join(page.extract_text() or "" for page in reader.pages[:2])
            compact = re.sub(r"[^A-Z0-9]", "", head.upper())
            if "SYLLABUS" in compact[:200]:
                excluded.append({"filename": path.name, "reason": "Syllabus, not an exam paper"})
                continue
            override = overrides.get(signature)
            language = "af" if "INDUSTRIËLE INSTRUMENTE" in head.upper() else "en"
            if override:
                if override["subject"] != subject:
                    raise ValueError(f"Wrong subject folder: {path.name}")
                date, kind = override["exam_date"], override["kind"]
                verification = override["verified_by"]
            else:
                if expected_title not in compact and language != "af":
                    raise ValueError(f"Cover subject needs review: {path.name}")
                date = printed_date(head)
                kind = "memo" if "MARKINGGUIDELINE" in compact or "MEMORANDUM" in compact else "paper"
                verification = "printed cover text"
            if not date:
                raise ValueError(f"Cover date needs review: {path.name}")
            relative = f"data/past_papers/sources/{subject}/{path.name}"
            document = {
                "id": signature[:16], "subject": subject, "kind": kind, "exam_date": date,
                "language": language, "source_file": relative, "source_label": f"{subject} · {date} · {kind}",
                "source_pages": list(range(1, len(reader.pages) + 1)), "source_sha256": signature,
                "original_filename": path.name, "aliases": [], "metadata_verified_by": verification,
            }
            records = extract_questions(reader) if language == "en" else []
            groups[document["id"]] = records
            # A partial question sequence or inconsistent totals must not become an exam.
            numbers = [int(record["number"]) for record in records]
            totals = [printed_marks(record["text"]) for record in records]
            complete = bool(records) and numbers == list(range(1, len(records) + 1)) and all(totals)
            if kind == "paper":
                complete = complete and sum(totals) == 100
            document["question_indexed"] = kind == "paper" and complete
            if kind == "paper" and not complete:
                if records and all(totals) and sum(totals) != 100:
                    document["index_note"] = f"Printed question totals add to {sum(totals)}; the paper states 100. Use the original paper and memo to review the discrepancy."
                else:
                    document["index_note"] = "Use the complete original paper here; a complete question sequence and mark totals could not be established automatically."
            if document["question_indexed"]:
                last_question_page = max(page for record in records for page in record["pages"])
                document["reference_pages"] = list(range(last_question_page + 1, len(reader.pages) + 1))
                for record, total in zip(records, totals):
                    num = f"Q{record['number']}"
                    questions.append({
                        "id": f"{signature[:12]}-{num}", "document_id": document["id"],
                        "subject": subject, "num": num, "topic": "Original past paper", "marks": total,
                        "exam_date": date, "text": f"Answer original {num} in {document['source_label']}; use the attached PDF pages.",
                        "marking": "No memo with the same printed cover date is attached. Assess the original question without inventing an official marking memo.",
                        "source_file": relative, "source_label": document["source_label"],
                        "source_pages": sorted(record["pages"]), "reference_pages": document["reference_pages"],
                        "source_sha256": signature,
                    })
            target = repo_dir / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, target)
            documents.append(document)
            by_digest[signature] = document

    for paper in (d for d in documents if d["kind"] == "paper" and d["language"] == "en"):
        matches = [d for d in documents if d["kind"] == "memo" and d["subject"] == paper["subject"]
                   and d["exam_date"] == paper["exam_date"] and len(d["exam_date"]) == 10]
        if len(matches) != 1:
            paper["memo_status"] = "No unique memo with the same printed cover date"
            continue
        memo = matches[0]
        paper_totals = {f"Q{group['number']}": printed_marks(group["text"]) for group in groups[paper["id"]]}
        memo_totals = {f"Q{group['number']}": printed_marks(group["text"]) for group in groups[memo["id"]]}
        conflicts = {num: [marks, memo_totals[num]] for num, marks in paper_totals.items()
                     if marks is not None and memo_totals.get(num) is not None and marks != memo_totals[num]}
        if conflicts:
            paper["memo_candidate_id"] = memo["id"]
            paper["memo_total_conflicts"] = conflicts
            paper["memo_status"] = "The same-date memo needs review: some question totals could not be reconciled. It remains available separately in this library."
            for question in (q for q in questions if q["document_id"] == paper["id"]):
                question["memo_status"] = paper["memo_status"]
                question["marking"] = "A same-date memo requires review because extracted question totals conflict. Do not invent or apply an official memo; assess the original question on engineering correctness."
            continue
        paper["memo_id"] = memo["id"]
        for question in (q for q in questions if q["document_id"] == paper["id"]):
            memo_groups = [g for g in groups[memo["id"]] if f"Q{g['number']}" == question["num"]]
            pages = sorted(memo_groups[0]["pages"]) if len(memo_groups) == 1 else memo["source_pages"]
            question.update({"memo_id": memo["id"], "memo_file": memo["source_file"], "memo_pages": pages,
                             "memo_date": memo["exam_date"], "memo_label": memo["source_label"],
                             "marking": "Use the attached original marking guideline, matched by subject and printed cover date. Apply only the selected source question's marks."})

    audit = {"subjects": {subject: {
        "papers": sum(d["subject"] == subject and d["kind"] == "paper" for d in documents),
        "memos": sum(d["subject"] == subject and d["kind"] == "memo" for d in documents),
        "question_groups": sum(q["subject"] == subject for q in questions),
        "paired_papers": sum(d["subject"] == subject and "memo_id" in d for d in documents),
        "library_only_papers": [{"document": d["source_label"], "note": d["index_note"]} for d in documents if d["subject"] == subject and d["kind"] == "paper" and not d["question_indexed"]],
    } for subject, _ in SUBJECTS.values()}, "excluded": excluded,
        "unmatched_memos": [d["source_label"] for d in documents if d["kind"] == "memo" and not any(p.get("memo_id") == d["id"] or p.get("memo_candidate_id") == d["id"] for p in documents)],
        "memo_pairs_requiring_review": [{"paper": d["source_label"], "extracted_totals": d["memo_total_conflicts"]} for d in documents if d.get("memo_candidate_id")]}
    payload = {"version": 2, "subjects": [s for s, _ in SUBJECTS.values()], "questions": questions, "documents": documents}
    for name, data in [("source_questions.json", payload), ("library_audit.json", audit)]:
        (destination / name).write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(audit, indent=2))


if __name__ == "__main__":
    logging.getLogger("pypdf").setLevel(logging.ERROR)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_dir", type=Path)
    parser.add_argument("--repo-dir", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    build(args.source_dir, args.repo_dir)
