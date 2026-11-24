# Sign-in provider setup

Google remains compatible with the app's existing named or unnamed Google configuration.
The entry page displays locally bundled Google, Microsoft and Apple symbols. A provider
button is enabled only when its configuration passes validation. No passwords are collected
by Trentox. Identity tokens are verified by Streamlit/Authlib; the app then checks the
configured issuer, audience, issuance time and authorized party.

## Microsoft

Register a web application in Microsoft Entra with the existing Trentox callback:

`https://dhet-n5-tutor-engine-rxogmong3h45cfoqv7t6sq.streamlit.app/oauth2callback`

Add the application ID, secret and a **tenant-specific** v2 OIDC discovery URL under
`[auth.microsoft]`. This implementation pins the tenant issuer. It does not silently
trust a tenant-independent `common` issuer. Choose the tenant/account audience required
for your students and verify an actual sign-in before announcing availability.

## Apple

The installed Streamlit callback accepts GET requests, while Apple's scoped web flow
uses a form POST callback. For Apple, use a compatible OIDC broker (for example, a
dedicated Auth0 application with Apple enabled) to handle Apple's exchange and return
a standard authorization-code GET callback to Streamlit. Configure the Apple Services ID,
key and connection in that broker; configure the broker client under `[auth.apple]`.
Set `expected_issuer` to the broker's exact issuer, including its trailing slash when
present. The discovery URL must equal that issuer plus `.well-known/openid-configuration`.
Direct Apple metadata is intentionally rejected by this implementation.

The example TOML contains placeholders only. Add real values to Streamlit Secrets, never
source control or chat. Preserve the existing shared `auth.redirect_uri`, `cookie_secret`
and Google settings. Additional providers remain disabled until configured. Credentials
alone are not proof of successful sign-in: test the redirect, callback and logout flows.

Accounts from different issuers are separate. Matching email addresses do not link
accounts or merge study history automatically.

References: [Streamlit authentication](https://docs.streamlit.io/develop/concepts/connections/authentication),
[Microsoft OIDC](https://learn.microsoft.com/entra/identity-platform/v2-protocols-oidc),
[Apple web configuration](https://developer.apple.com/documentation/signinwithapple/configuring-your-environment-for-sign-in-with-apple).
