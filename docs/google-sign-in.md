# Connect secure Google sign-in

Trentox uses Streamlit's native Google OpenID Connect login. Google verifies the
student account; Trentox never collects a Google password. The workspace stays
closed until authentication succeeds and the learner chooses a Tex username.

## Owner setup

1. In [Google Cloud's Google Auth Platform](https://console.cloud.google.com/auth/clients),
   configure the app's branding and audience, then create an OAuth client with
   application type **Web application**. If the app is in Testing, add the
   intended student accounts as test users. Publish the audience when ready for
   the intended students.
   Use **Trentox Tutor AI** as the app name on the Google branding screen.
2. Add this exact **Authorized redirect URI** to that client:

   `https://dhet-n5-tutor-engine-rxogmong3h45cfoqv7t6sq.streamlit.app/oauth2callback`

3. Copy `.streamlit/secrets.toml.example` into the app's **Streamlit Cloud >
   Settings > Secrets**, retaining any existing Gemini settings. Replace the
   client ID and client secret with the values from the Google Web client.
   Generate a random cookie signing secret locally, for example:

   ```shell
   python -c "import secrets; print(secrets.token_urlsafe(48))"
   ```

   Paste the generated value into `cookie_secret`. Do not paste credentials into
   a chat, commit them to GitHub, or include them in screenshots. The example is
   intentionally unusable until its placeholder values are replaced.
   The `client_secret` must be the actual secret for that same Google Web client;
   a client ID, API key or placeholder cannot replace it. Leave `expose_tokens = []`.
4. Ensure the deployment installs `streamlit[auth,pdf]>=1.66`. The auth extra
   provides Authlib. Restart the app after changing its authentication secrets.
5. Open the **canonical app URL** directly, choose **Continue with Google**, and
   sign in using an allowed test account. Choose a Tex username, enter the
   workspace, then verify sign-out returns to the login page. Reopen in a second
   browser profile and confirm that the other learner's conversation is absent.

No sign-in credentials have been created, read, or configured by the code change.
The app shows a disabled sign-in button while configuration is incomplete; there
is no guest flag, password shortcut, URL bypass or simulated identity in the
production flow.

For local development, register and use
`http://localhost:8501/oauth2callback` instead, with a separate local secrets file
and the same `google` provider name. Never commit that file.

Streamlit's single-provider layout is also supported: when `[auth.google]` is
absent, `client_id`, `client_secret` and Google's `server_metadata_url` can sit
directly under `[auth]` alongside `redirect_uri` and `cookie_secret`. Trentox
then calls the native default-provider login. When `[auth.google]` exists,
Trentox uses that named provider consistently for login and audience validation;
an incomplete named provider is rejected instead of falling back to root
credentials. Both layouts require the exact Google discovery URL and the same
callback, cookie-strength and verified-identity checks.

## Username and privacy behavior

After Google authentication the student chooses the name Tex will use. Names
allow 2-32 Unicode characters (letters, numbers, spaces and common name
punctuation). A name is personalization data, never an authentication credential
or a set of model instructions. Tex receives the chosen name, not the student's
Google email, ID token or account claims.

The app derives an internal pseudonymous student ID from Google's verified issuer
and subject. Changing accounts or signing out clears the session's learner data.
Names, conversations and study state are session-scoped; this change does not add
a database or promise cross-device profile/history sync. Students can change the
Tex username through the account menu.

Streamlit's identity cookie can persist for 30 days. Trentox additionally checks
the Google identity's `exp` on every full app run and requires sign-in again once
it expires. It also checks that `aud` (and `azp` when present or required) match
the configured Google Web client. These checks supplement Streamlit/Authlib's
signature, state and nonce validation at the callback; no raw token is accepted
from a URL, form or session-state value.

Loss of authentication, an invalid/expired identity, account changes and logout
clear the current session's learner data before any learning modules load. There
is no background session revocation timer: the expiry check runs when the app
reruns. Sign out on shared devices; other already-open sessions can remain
authenticated until separately signed out or checked on their next app run.
Signing out of Trentox does not sign out of the underlying Google account.

Configuration checks accept only the canonical deployed callback above, or an
HTTP callback on `localhost`/`127.0.0.1` for development. If the production domain
changes, update `APP_URL` in `ui/student_identity.py`, the Google Web client and
the Streamlit secrets together. URLs with credentials, query strings, missing
hosts or runtime paths are rejected. Diagnostics report fixed field names only.

Authentication is not supported in apps configured with `embed=true`. These
views link back to the canonical app for sign-in. A `/~/+/` runtime view also
offers the canonical link; the path itself is not treated as an embedding or
authentication signal. Do not register the runtime path as the Google OAuth
callback or disable XSRF/CORS protections.

## Verification scope

Automated checks cover missing configuration, unauthenticated access, username
validation, verified-claim requirements, expiry and audience checks, rejected
callback destinations, account-switch cleanup and logout. Real
Google consent and callback verification requires the owner-configured OAuth
client and a student signing in. The app must not claim that live Google login
has been verified before that step succeeds.

References: [Streamlit authentication](https://docs.streamlit.io/develop/concepts/connections/authentication),
[st.login configuration](https://docs.streamlit.io/develop/api-reference/user/st.login),
[Google OpenID Connect setup](https://developers.google.com/identity/openid-connect/openid-connect).
