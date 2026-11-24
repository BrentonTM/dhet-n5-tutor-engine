"""Retrieve relevant, attributed pages from the bundled study-resource index."""

import gzip
import json
import re
import unicodedata
from pathlib import Path

import streamlit as st


def terms(text):
    text = unicodedata.normalize("NFKC", str(text)).casefold()
    words = re.findall(r"[a-z0-9]{2,}", text)
    stop = {"and", "the", "for", "with", "from", "original", "module", "chapter", "general",
            "principles", "introduction", "applications", "application", "theory",
            "of", "in", "to", "by", "is", "as", "an", "on", "at", "or"}
    return {word.rstrip("s") for word in words if word not in stop}


@st.cache_data(show_spinner=False, max_entries=4)
def _read_index(path, modified):
    with gzip.open(path, "rt", encoding="utf-8") as source:
        return json.load(source)


def lesson_resources(base_dir, subject, topic, focus=""):
    """Search all indexed sources for this subject, then fairly budget relevant pages."""
    path = Path(base_dir) / "data" / "lesson_library.json.gz"
    if not path.is_file():
        return {"context": "", "sources": [], "scanned": [], "available": 0}
    library = _read_index(str(path), path.stat().st_mtime_ns)
    query = terms(topic)
    expanded = query | terms(focus)
    candidates = []
    available = 0
    scanned = []
    for document in library["documents"]:
        if subject not in document["subjects"]:
            continue
        available += 1
        title_hits = len(query & terms(document["title"]))
        if not document["pages"]:
            if title_hits:
                scanned.append(document["title"])
            continue
        ranked = []
        for page in document["pages"]:
            vocabulary = terms(page["text"])
            direct_hits = len(query & vocabulary)
            focus_hits = len(expanded & vocabulary)
            if not direct_hits and not (title_hits and focus_hits):
                continue
            score = 5 * direct_hits + focus_hits + 2 * title_hits
            # Cover and contents pages can mention every topic without teaching it.
            if "contents" in page["text"][:180].casefold():
                score *= 0.2
            ranked.append((score, page))
        ranked.sort(key=lambda row: (-row[0], row[1]["page"]))
        if ranked:
            candidates.append((ranked[0][0], document, ranked[:3]))
    candidates.sort(key=lambda row: (-row[0], row[1]["title"]))
    excerpts = []
    sources = []
    remaining = 32000
    # Take one best page from each relevant document before adding more pages.
    for depth in range(3):
        for _, document, pages in candidates:
            if len(pages) <= depth or remaining < 500:
                continue
            page = pages[depth][1]
            reference = f"{document['title']} — page/slide {page['page']}"
            limit = min(1800, remaining - len(reference) - 60)
            matches = [
                match.start() for match in re.finditer(r"\b[a-zA-Z0-9]{2,}\b", page["text"])
                if match.group().casefold().rstrip("s") in query
            ]
            start = max(0, (matches[0] if matches else 0) - 450)
            excerpt = page["text"][start:start + limit]
            excerpts.append(f"SOURCE: {reference}\n{excerpt}")
            remaining -= len(excerpt) + len(reference) + 60
            sources.append({
                "title": document["title"], "page": page["page"], "kind": document["kind"],
                "url": document.get("url", ""), "path": document.get("path", ""),
            })
    return {
        "context": "\n\n".join(excerpts), "sources": sources,
        "scanned": scanned, "available": available,
    }
