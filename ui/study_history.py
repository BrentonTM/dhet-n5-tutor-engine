"""Store minimal study events under the verified learner ID."""

import hashlib
import json
from datetime import datetime, timezone


HISTORY_LIMITS = {"quiz": 2000, "lab": 300, "practice": 300, "mock": 300}
ACTIVITY_LABELS = {
    "quiz": "Topic check",
    "lab": "Lab reflection",
    "practice": "Practice feedback",
    "mock": "Mock exam submitted",
}


def study_event(kind, record, *, attempt_id=None):
    fingerprint = attempt_id if attempt_id is not None else record
    digest = hashlib.sha256(json.dumps(fingerprint, sort_keys=True).encode()).hexdigest()
    return {"id": digest, "kind": kind, "record": record}


def activity_record(subject, topic):
    return {
        "subject": subject,
        "topic": topic,
        "attempted_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


def sync_events(dsn, student_id, pending, *, load=False):
    """Commit idempotent inserts and optionally read bounded history for this learner."""
    import psycopg
    from psycopg.types.json import Jsonb

    with psycopg.connect(
        dsn, connect_timeout=5, sslmode="verify-full", sslrootcert="system",
        options="-c statement_timeout=5000 -c lock_timeout=5000",
    ) as conn:
        if pending:
            with conn.cursor() as cursor:
                cursor.executemany(
                    """INSERT INTO trentox_study_events
                           (student_id, kind, event_id, attempted_at, details)
                       VALUES (%s, %s, %s, %s, %s)
                       ON CONFLICT (student_id, kind, event_id) DO NOTHING""",
                    [
                        (student_id, event["kind"], event["id"],
                         event["record"]["attempted_at"], Jsonb(event["record"]))
                        for event in pending
                    ],
                )
        history = {}
        if load:
            for kind, limit in HISTORY_LIMITS.items():
                rows = conn.execute(
                    """SELECT event_id, details FROM trentox_study_events
                       WHERE student_id = %s AND kind = %s
                       ORDER BY attempted_at DESC, event_id DESC LIMIT %s""",
                    (student_id, kind, limit),
                )
                history[kind] = {event_id: details for event_id, details in rows}
    return history
