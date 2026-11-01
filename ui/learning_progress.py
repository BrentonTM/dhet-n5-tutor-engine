"""Small, private-by-default progress helpers for Trentox Tutor AI."""

from __future__ import annotations

import json
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from typing import Any
from zoneinfo import ZoneInfo


PROGRESS_SCHEMA_VERSION = 1
MAX_PROGRESS_RECORDS = 2000
_REVIEW_INTERVALS = ((0.40, 1), (0.80, 3), (1.00, 7), (float("inf"), 14))
_APP_TIMEZONE = ZoneInfo("Africa/Johannesburg")


def _as_utc(value: str | datetime | None = None) -> datetime:
    if value is None:
        return datetime.now(timezone.utc)
    parsed = value if isinstance(value, datetime) else datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def review_due_date(score: int, total: int, attempted_at: str | datetime | None = None) -> str:
    """Return a gentle retrieval-review date based on the latest quiz result."""
    if total <= 0 or score < 0 or score > total:
        raise ValueError("Quiz score must be between zero and the positive question count.")
    accuracy = score / total
    days = next(days for threshold, days in _REVIEW_INTERVALS if accuracy < threshold or threshold == float("inf"))
    return (_as_utc(attempted_at).astimezone(_APP_TIMEZONE).date() + timedelta(days=days)).isoformat()


def record_quiz_attempt(
    history: list[dict[str, Any]],
    subject: str,
    topic: str,
    score: int,
    total: int,
    gaps: list[str] | None = None,
    attempted_at: str | datetime | None = None,
) -> list[dict[str, Any]]:
    """Append a minimal result; answers and uploaded work are never stored."""
    subject, topic = str(subject).strip(), str(topic).strip()
    if not subject or not topic or len(subject) > 80 or len(topic) > 240:
        raise ValueError("Subject and topic are required and must be short labels.")
    if not isinstance(total, int) or total <= 0 or total > 100:
        raise ValueError("Question count must be between 1 and 100.")
    if not isinstance(score, int) or score < 0 or score > total:
        raise ValueError("Quiz score must be between zero and the question count.")
    moment = _as_utc(attempted_at)
    clean_gaps = list(dict.fromkeys(str(g).strip()[:160] for g in (gaps or []) if str(g).strip()))[:12]
    record = {
        "subject": subject,
        "topic": topic,
        "score": score,
        "total": total,
        "gaps": clean_gaps,
        "attempted_at": moment.isoformat(timespec="seconds"),
        "review_due": review_due_date(score, total, moment),
    }
    return merge_progress(history, [record])


def merge_progress(*histories: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Merge histories deterministically and remove duplicate imported attempts."""
    merged: dict[tuple[Any, ...], dict[str, Any]] = {}
    for history in histories:
        for record in history or []:
            try:
                key = (
                    record["subject"], record["topic"], record["attempted_at"],
                    record["score"], record["total"], tuple(record.get("gaps", [])),
                )
            except (KeyError, TypeError):
                continue
            merged[key] = record
    result = sorted(merged.values(), key=lambda row: row["attempted_at"])
    return result[-MAX_PROGRESS_RECORDS:]


def latest_by_topic(history: list[dict[str, Any]], subject: str | None = None) -> dict[tuple[str, str], dict[str, Any]]:
    latest: dict[tuple[str, str], dict[str, Any]] = {}
    for row in merge_progress(history):
        if subject and row["subject"] != subject:
            continue
        latest[(row["subject"], row["topic"])] = row
    return latest


def topic_status(record: dict[str, Any] | None, today: date | None = None) -> str:
    """Turn one latest attempt into a transparent, non-predictive study status."""
    if not record:
        return "Not checked"
    today = today or datetime.now(_APP_TIMEZONE).date()
    try:
        accuracy = int(record["score"]) / int(record["total"])
        review_due = date.fromisoformat(record["review_due"])
    except (KeyError, TypeError, ValueError, ZeroDivisionError):
        return "Check again"
    if review_due <= today:
        return "Review due"
    if accuracy < 0.60:
        return "Review soon"
    return "On track"


def summarize_progress(history: list[dict[str, Any]], subject: str | None = None, today: date | None = None) -> dict[str, Any]:
    today = today or datetime.now(_APP_TIMEZONE).date()
    rows = [row for row in merge_progress(history) if not subject or row["subject"] == subject]
    latest = latest_by_topic(rows)
    due = []
    for row in latest.values():
        try:
            due_date = date.fromisoformat(row["review_due"])
        except (TypeError, ValueError):
            continue
        if due_date <= today:
            due.append({**row, "days_overdue": max(0, (today - due_date).days)})
    due.sort(key=lambda row: (row["review_due"], row["subject"], row["topic"]))
    gap_counts = Counter(gap for row in rows for gap in row.get("gaps", []))
    latest_scores = [row["score"] / row["total"] * 100 for row in latest.values() if row["total"]]
    return {
        "attempt_count": len(rows),
        "topics_checked": len(latest),
        "average_latest_percent": sum(latest_scores) / len(latest_scores) if latest_scores else None,
        "latest_by_topic": latest,
        "due_reviews": due,
        "gap_counts": gap_counts,
    }


def study_streak(history: list[dict[str, Any]], today: date | None = None) -> int:
    dates = set()
    for row in merge_progress(history):
        try:
            dates.add(_as_utc(row["attempted_at"]).astimezone(_APP_TIMEZONE).date())
        except (KeyError, TypeError, ValueError):
            continue
    if not dates:
        return 0
    today = today or datetime.now(_APP_TIMEZONE).date()
    anchor = today if today in dates else today - timedelta(days=1)
    streak = 0
    while anchor - timedelta(days=streak) in dates:
        streak += 1
    return streak


def export_progress(history: list[dict[str, Any]]) -> str:
    return json.dumps(
        {
            "product": "Trentox Tutor AI",
            "schema_version": PROGRESS_SCHEMA_VERSION,
            "exported_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "records": merge_progress(history),
        },
        ensure_ascii=False,
        indent=2,
    )


def import_progress(payload: str) -> list[dict[str, Any]]:
    """Validate an exported progress file before merging; reject unknown versions."""
    try:
        document = json.loads(payload)
    except (TypeError, json.JSONDecodeError) as exc:
        raise ValueError("That file is not valid progress JSON.") from exc
    if not isinstance(document, dict) or document.get("schema_version") != PROGRESS_SCHEMA_VERSION:
        raise ValueError("This progress file uses an unsupported format version.")
    records = document.get("records")
    if not isinstance(records, list) or len(records) > MAX_PROGRESS_RECORDS:
        raise ValueError("The progress file has an invalid number of records.")
    validated = []
    for row in records:
        if not isinstance(row, dict):
            raise ValueError("A progress record is malformed.")
        try:
            subject, topic = str(row["subject"]).strip(), str(row["topic"]).strip()
            score, total = int(row["score"]), int(row["total"])
            attempted = _as_utc(row["attempted_at"])
            gaps = row.get("gaps", [])
            if not subject or not topic or len(subject) > 80 or len(topic) > 240:
                raise ValueError
            if not 0 <= score <= total <= 100 or not isinstance(gaps, list):
                raise ValueError
            clean_gaps = list(dict.fromkeys(str(g).strip()[:160] for g in gaps if str(g).strip()))[:12]
            validated.append({
                "subject": subject,
                "topic": topic,
                "score": score,
                "total": total,
                "gaps": clean_gaps,
                "attempted_at": attempted.isoformat(timespec="seconds"),
                "review_due": review_due_date(score, total, attempted),
            })
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError("A progress record is malformed or has an invalid score/date.") from exc
    return merge_progress(validated)

