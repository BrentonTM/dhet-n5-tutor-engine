# Feature guide

The full guide opens 29 feature views, highlights their real controls and displays
an attached pop-up. It includes Back, Next, Skip, close, Escape and a feature jump list.
Unavailable course features are filtered out. The tour does not submit work, start a
timed exam, enable the microphone or send AI requests automatically. It restores the
previous navigation when stopped or completed.

The automatic launch is claimed as soon as the first authenticated workspace loads.
Skipping, closing and finishing all count as seen. Replay remains available from the
sidebar and Tex's app guide starter prompt.

With `[study_history].database_url` configured, the app atomically inserts a row into
`trentox_app_onboarding` under the verified pseudonymous student ID. Only the first
insert returns an automatic-launch claim, including across concurrent tabs/devices.
The runtime database role must be able to create/access that small table. A schema
example is supplied below for installations with separate migration permissions.

If the database is unavailable, an account-specific browser cookie prevents repeat
automatic tours in that browser. This fallback cannot synchronize the choice to another
device or survive cleared cookies. The sidebar reports whether account or browser
storage is in use. The flag is independent of whether all guide steps were completed.

The overlay bundles Driver.js 1.14.0 and its MIT license locally in `ui/vendor/driver`.
No runtime CDN request is needed. It only reads app DOM locations to position the
pop-up and opens the sidebar/voice disclosure when needed. Step events are validated
against the current step and available feature IDs before navigation changes.

```sql
CREATE TABLE IF NOT EXISTS trentox_app_onboarding (
    student_id text PRIMARY KEY,
    first_shown_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP
);
REVOKE ALL ON trentox_app_onboarding FROM PUBLIC;
```
