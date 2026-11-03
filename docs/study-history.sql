CREATE TABLE IF NOT EXISTS trentox_study_events (
    student_id text NOT NULL,
    kind text NOT NULL CHECK (kind IN ('quiz', 'lab', 'practice', 'mock')),
    event_id text NOT NULL,
    attempted_at timestamptz NOT NULL,
    details jsonb NOT NULL,
    PRIMARY KEY (student_id, kind, event_id)
);

CREATE INDEX IF NOT EXISTS trentox_study_events_recent
    ON trentox_study_events (student_id, kind, attempted_at DESC, event_id DESC);

REVOKE ALL ON trentox_study_events FROM PUBLIC;
