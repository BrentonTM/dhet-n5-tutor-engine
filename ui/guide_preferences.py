"""Claim the once-only automatic guide under the verified learner ID."""

import hashlib


def guide_cookie_name(student_id):
    return "trentox_guide_" + hashlib.sha256(str(student_id).encode()).hexdigest()[:20]


def claim_first_guide(dsn, student_id):
    """Return True for the first login only, including concurrent tabs/devices."""
    import psycopg
    with psycopg.connect(dsn, connect_timeout=5, sslmode="verify-full", sslrootcert="system",
                         options="-c statement_timeout=5000 -c lock_timeout=5000") as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS trentox_app_onboarding (
            student_id text PRIMARY KEY,
            first_shown_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP
        )""")
        row = conn.execute("""INSERT INTO trentox_app_onboarding (student_id) VALUES (%s)
            ON CONFLICT (student_id) DO NOTHING RETURNING student_id""", (student_id,)).fetchone()
        return row is not None
