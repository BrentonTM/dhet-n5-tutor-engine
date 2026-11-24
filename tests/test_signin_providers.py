import time
import unittest

from ui.student_identity import additional_provider_ready, identity_from_configured_provider
from tests.test_student_identity import auth_settings, verified_claims

TENANT = "12345678-1234-1234-1234-123456789abc"


def settings():
    result = auth_settings()
    result["auth"]["microsoft"] = {"client_id": "ms-test-app", "client_secret": "test-secret",
        "server_metadata_url": f"https://login.microsoftonline.com/{TENANT}/v2.0/.well-known/openid-configuration"}
    result["auth"]["apple"] = {"client_id": "apple-broker-test", "client_secret": "test-secret",
        "expected_issuer": "https://identity.example.test/",
        "server_metadata_url": "https://identity.example.test/.well-known/openid-configuration"}
    return result


class SignInProviderTests(unittest.TestCase):
    def test_missing_or_placeholder_configuration_never_enables_buttons(self):
        self.assertFalse(additional_provider_ready(auth_settings(), "microsoft"))
        configured = settings()
        configured["auth"]["apple"]["client_secret"] = "REPLACE_WITH_SECRET"
        self.assertFalse(additional_provider_ready(configured, "apple"))

    def test_microsoft_issuer_and_app_are_pinned(self):
        configured = settings()
        self.assertTrue(additional_provider_ready(configured, "microsoft"))
        now = time.time()
        claims = {"iss": f"https://login.microsoftonline.com/{TENANT}/v2.0", "sub": "subject",
                  "aud": "ms-test-app", "iat": now, "exp": now + 3600}
        student, provider = identity_from_configured_provider(claims, configured)
        self.assertEqual(provider, "Microsoft")
        self.assertEqual(len(student), 64)
        for key, value in (("aud", "wrong-app"), ("iss", "https://evil.example.test"), ("iat", now - 13 * 3600)):
            with self.assertRaises(ValueError):
                identity_from_configured_provider({**claims, key: value}, configured)

    def test_apple_uses_a_compatible_trusted_broker_and_separate_identity(self):
        configured = settings()
        self.assertTrue(additional_provider_ready(configured, "apple"))
        now = time.time()
        claims = {"iss": "https://identity.example.test/", "sub": "subject", "aud": "apple-broker-test", "iat": now, "exp": now + 3600}
        apple_id, provider = identity_from_configured_provider(claims, configured)
        self.assertEqual(provider, "Apple")
        google_id, _ = identity_from_configured_provider(verified_claims("subject"), configured)
        self.assertNotEqual(apple_id, google_id)
        configured["auth"]["apple"].update(expected_issuer="https://appleid.apple.com", server_metadata_url="https://appleid.apple.com/.well-known/openid-configuration")
        self.assertFalse(additional_provider_ready(configured, "apple"))

    def test_tenant_independent_microsoft_metadata_is_not_silently_trusted(self):
        configured = settings()
        configured["auth"]["microsoft"]["server_metadata_url"] = "https://login.microsoftonline.com/common/v2.0/.well-known/openid-configuration"
        self.assertFalse(additional_provider_ready(configured, "microsoft"))
