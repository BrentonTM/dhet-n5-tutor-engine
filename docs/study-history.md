# Enable account study history

The Streamlit app needs a PostgreSQL database reachable from Community Cloud.
Use a dedicated database and run [the schema](study-history.sql) as its owner.
Grant the app's dedicated login role CONNECT to the database, USAGE on the
schema and SELECT and INSERT on trentox_study_events. Keep maintenance and
deletion privileges on a separate operator role.

In Streamlit Cloud App settings, add this section under Secrets, with your
database's real connection URL. Preserve the existing Google auth sections.

    [study_history]
    database_url = "postgresql://APP_ROLE:PASSWORD@HOST:5432/DATABASE"

Use an endpoint with a certificate trusted by the system certificate store.
Use the direct endpoint or a session pooler. Keep the URL in Cloud Secrets.
The app verifies the server certificate and hostname.

Verify with two test accounts. Complete a topic check, request practice
feedback, submit a mock exam and save a course-linked lab reflection. In
Analytics, check the recent activity list, then sign out and sign in again
with the same account. The history and review suggestions should return. The
second test account should start with its own history. If storage is unavailable,
Analytics reports it and current-session activity remains usable.

Before enabling the database in production, verify the host's backup and
retention settings and document them in the privacy policy and Play Data
safety worksheet. For a verified deletion request, use the learner's internal
ID to delete their rows and handle backups according to the provider's
retention settings. Revoke the app's credentials if they are exposed.
