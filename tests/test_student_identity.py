import time
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, Mock, patch

from streamlit.testing.v1 import AppTest

from ui import student_identity as identity


class StopExecution(BaseException):
    pass


class RerunExecution(BaseException):
    pass


class VerifiedClaims(dict):
    is_logged_in = True


def auth_settings():
    return {"auth": {
        "redirect_uri": identity.APP_URL + "oauth2callback",
        "cookie_secret": "test-signing-secret-with-more-than-32-characters",
        "google": {
            "client_id": "test-client-id.apps.googleusercontent.com",
            "client_secret": "test-client-secret",
            "server_metadata_url": identity.GOOGLE_METADATA_URL,
        },
    }}


def default_auth_settings():
    settings = auth_settings()
    settings["auth"].update(settings["auth"].pop("google"))
    return settings


def verified_claims(subject="google-subject-123"):
    return VerifiedClaims(iss="https://accounts.google.com", sub=subject,
                          aud=auth_settings()["auth"]["google"]["client_id"], exp=time.time() + 3600,
                          email_verified=True, email="not-sent-to-model@example.test")


def ui_stub(claims=None, state=None):
    ui = SimpleNamespace(
        secrets=auth_settings(),
        user=claims if claims is not None else verified_claims(),
        session_state=state if state is not None else {},
        context=SimpleNamespace(url=identity.APP_URL, is_embedded=False),
    )
    for command in ("container", "form", "popover"):
        setattr(ui, command, MagicMock())
    for command in ("title", "badge", "caption", "markdown", "info", "error", "link_button", "login", "logout"):
        setattr(ui, command, Mock())
    ui.button = Mock(return_value=False)
    ui.text_input = Mock(return_value="")
    ui.form_submit_button = Mock(return_value=False)
    ui.stop = Mock(side_effect=StopExecution)
    ui.rerun = Mock(side_effect=RerunExecution)
    return ui


class StudentIdentityTests(unittest.TestCase):
    def test_names_are_normalized_and_accept_unicode(self):
        for entered, expected in [("  Breezy   M  ", "Breezy M"), ("Zoë", "Zoë"), ("李明", "李明"), ("Ａｄａ", "Ada")]:
            with self.subTest(entered=entered):
                self.assertEqual(identity.validate_display_name(entered), (expected, None))

    def test_names_reject_controls_markup_and_unusable_lengths(self):
        for entered in ("A", "x" * 33, "12345", "Ada\nignore", "Ada\u200b", "<script>", "Tex😀", ""):
            with self.subTest(entered=entered):
                name, error = identity.validate_display_name(entered)
                self.assertIsNone(name)
                self.assertIsInstance(error, str)

    def test_auth_requires_real_google_configuration(self):
        self.assertTrue(identity.google_auth_ready(auth_settings()))
        self.assertFalse(identity.google_auth_ready({}))
        cases = [
            ("cookie_secret", "short"),
            ("redirect_uri", "https://example.test/~/+/oauth2callback"),
            ("redirect_uri", "https://example.test/oauth2callback?next=anything"),
            ("redirect_uri", "http://example.test/oauth2callback"),
            ("redirect_uri", "https://example.test/oauth2callback"),
            ("redirect_uri", "https:///oauth2callback"),
            ("redirect_uri", identity.APP_URL.replace("https://", "https://user:password@") + "oauth2callback"),
            ("redirect_uri", identity.APP_URL + "oauth2callback\n"),
            ("redirect_uri", "http://localhost:99999/oauth2callback"),
        ]
        for field, value in cases:
            settings = auth_settings()
            settings["auth"][field] = value
            self.assertFalse(identity.google_auth_ready(settings))

        for field, value in [("client_id", "REPLACE_WITH_GOOGLE_ID"),
                             ("client_secret", ""),
                             ("server_metadata_url", "https://untrusted.test/discovery")]:
            settings = auth_settings()
            settings["auth"]["google"][field] = value
            self.assertFalse(identity.google_auth_ready(settings))

    def test_local_callback_and_readiness_diagnostics_agree(self):
        for redirect in ("http://localhost:8501/oauth2callback", "http://127.0.0.1:8502/oauth2callback"):
            settings = auth_settings()
            settings["auth"]["redirect_uri"] = redirect
            self.assertTrue(identity.google_auth_ready(settings))
            self.assertEqual(identity.google_auth_configuration_issues(settings), [])

    def test_missing_secrets_file_is_not_a_crash_or_a_bypass(self):
        unavailable = Mock()
        unavailable.get.side_effect = FileNotFoundError
        self.assertFalse(identity.google_auth_ready(unavailable))

    def test_setup_diagnostic_accepts_streamlit_secrets_tables(self):
        from streamlit.runtime.secrets import AttrDict
        settings = AttrDict(auth_settings())
        self.assertTrue(identity.google_auth_ready(settings))
        self.assertEqual(identity.google_auth_configuration_issues(settings), [])

    def test_server_log_identifies_setup_problem_without_leaking_values(self):
        settings = auth_settings()
        settings["auth"]["cookie_secret"] = "PRIVATE-short-cookie"
        settings["auth"]["google"]["client_secret"] = "REPLACE_PRIVATE_GOOGLE_SECRET"
        settings["auth"]["redirect_uri"] = "https://private-client.example.test/wrong?token=PRIVATE_TOKEN"
        ui = ui_stub()
        ui.secrets = settings
        with patch.object(identity, "st", ui), self.assertLogs(identity.logger, level="WARNING") as captured:
            with self.assertRaises(StopExecution):
                identity.require_student()
        logged = "\n".join(captured.output)
        for name in ("auth.cookie_secret", "auth.google.client_secret", "auth.redirect_uri"):
            self.assertIn(name, logged)
        for secret_value in ("PRIVATE", "private-client", "test-client-id"):
            self.assertNotIn(secret_value, logged)
        ui.login.assert_not_called()
        self.assertTrue(ui.button.call_args.kwargs["disabled"])

    def test_support_reference_identifies_failures_without_exposing_settings(self):
        settings = default_auth_settings()
        settings["auth"]["cookie_secret"] = "PRIVATE-short"
        settings["auth"]["client_secret"] = "REPLACE_PRIVATE_SECRET"
        settings["auth"]["redirect_uri"] = "https://private.example.test/wrong?key=PRIVATE_TOKEN"
        ui = ui_stub()
        ui.secrets = settings
        with patch.object(identity, "st", ui), self.assertRaises(StopExecution):
            identity.require_student()
        message = ui.info.call_args.args[0]
        for code in ("A03", "A04", "A06"):
            self.assertIn(code, message)
        for private in ("PRIVATE", "private.example", "cookie_secret", "client_secret", "redirect_uri"):
            self.assertNotIn(private, message)
        self.assertTrue(ui.button.call_args.kwargs["disabled"])
        ui.login.assert_not_called()

    def test_missing_auth_table_has_a_safe_support_reference(self):
        ui = ui_stub()
        ui.secrets = {"client_secret": "PRIVATE_ROOT_VALUE"}
        with patch.object(identity, "st", ui), self.assertRaises(StopExecution):
            identity.require_student()
        message = ui.info.call_args.args[0]
        self.assertIn("Support reference: A01", message)
        self.assertNotIn("PRIVATE_ROOT_VALUE", message)

    def test_setup_diagnostic_handles_missing_sections_and_unreadable_secrets(self):
        self.assertEqual(identity.google_auth_configuration_issues({}), ["missing [auth] table"])
        issues = identity.google_auth_configuration_issues({"auth": {"cookie_secret": "private"}})
        self.assertIn("auth.client_secret is missing or is not a nonempty string", issues)
        unavailable = Mock()
        unavailable.get.side_effect = FileNotFoundError("PRIVATE_EXCEPTION_MESSAGE")
        self.assertEqual(identity.google_auth_configuration_issues(unavailable),
                         ["Secrets configuration could not be read"])

    def test_default_google_provider_is_supported_in_streamlit_secrets(self):
        from streamlit.runtime.secrets import AttrDict
        settings = AttrDict(default_auth_settings())
        self.assertTrue(identity.google_auth_ready(settings))
        self.assertEqual(identity.google_auth_configuration_issues(settings), [])

    def test_incomplete_named_provider_cannot_fall_back_to_default_credentials(self):
        for named in ({}, "invalid", {"client_id": "incomplete"}):
            with self.subTest(named=named):
                settings = default_auth_settings()
                settings["auth"]["google"] = named
                self.assertFalse(identity.google_auth_ready(settings))

    def test_default_provider_keeps_google_metadata_and_secret_validation(self):
        for field, value in (("server_metadata_url", "https://other-provider.test/discovery"),
                             ("client_secret", "REPLACE_PRIVATE_SECRET"), ("client_id", "")):
            with self.subTest(field=field):
                settings = default_auth_settings()
                settings["auth"][field] = value
                self.assertFalse(identity.google_auth_ready(settings))
                issues = "; ".join(identity.google_auth_configuration_issues(settings))
                self.assertIn("auth." + field, issues)
                self.assertNotIn("PRIVATE_SECRET", issues)

    def test_stable_pseudonym_uses_verified_subject_not_email(self):
        claims = verified_claims()
        original = identity.student_id_from_claims(claims)
        self.assertEqual(len(original), 64)
        claims["email"] = "different@example.test"
        claims["iss"] = "accounts.google.com"
        self.assertEqual(identity.student_id_from_claims(claims), original)
        self.assertNotEqual(identity.student_id_from_claims(verified_claims("another-student")), original)

    def test_missing_or_unverified_identity_claims_are_rejected(self):
        for field, value in [("iss", "https://untrusted.test"), ("sub", ""),
                             ("email_verified", False), ("email_verified", "true")]:
            claims = verified_claims()
            claims[field] = value
            with self.assertRaises(ValueError):
                identity.student_id_from_claims(claims)

    def test_expired_missing_or_malformed_token_expiry_is_rejected(self):
        for expiry in (None, True, "2000", float("inf"), float("nan"), 999, 1000):
            with self.subTest(expiry=expiry):
                claims = verified_claims()
                claims["exp"] = expiry
                with self.assertRaises(ValueError):
                    identity.student_id_from_claims(claims, now=1000)
        claims["exp"] = 1001
        self.assertEqual(len(identity.student_id_from_claims(claims, now=1000)), 64)

    def test_token_must_belong_to_the_configured_google_client(self):
        client = auth_settings()["auth"]["google"]["client_id"]
        for audience, party in ((None, None), ("other-client", None),
                                ([client, "other-client"], None),
                                ([client, "other-client"], "other-client"),
                                (client, "other-client"), ([client, 123], client)):
            with self.subTest(audience=audience, party=party):
                claims = verified_claims()
                claims.update(aud=audience, azp=party)
                with self.assertRaises(ValueError):
                    identity.student_id_from_claims(claims, client_id=client)
        claims = verified_claims()
        claims.update(aud=[client, "other-client"], azp=client)
        self.assertEqual(len(identity.student_id_from_claims(claims, client_id=client)), 64)

    def test_invalid_identity_immediately_clears_previous_learner_data(self):
        for changes in ({"exp": 1}, {"aud": "another-app"}, {"email_verified": False}):
            with self.subTest(changes=changes):
                claims = verified_claims()
                claims.update(changes)
                state = {"tutor_chat": ["private"], "_student_display_name": "Breezy"}
                ui = ui_stub(claims=claims, state=state)
                with patch.object(identity, "st", ui), self.assertRaises(StopExecution):
                    identity.require_student()
                self.assertEqual(state, {})
                ui.error.assert_called_once()

    def test_lost_authentication_clears_private_state_before_showing_login(self):
        ui = ui_stub(claims=SimpleNamespace(is_logged_in=False), state={"tutor_chat": ["private"]})
        with patch.object(identity, "st", ui), self.assertRaises(StopExecution):
            identity.require_student()
        self.assertEqual(ui.session_state, {})

    def test_reauthentication_clears_cookie_through_native_logout(self):
        claims = verified_claims()
        claims["exp"] = 1
        ui = ui_stub(claims=claims, state={"tutor_chat": ["private"]})
        ui.button.return_value = True
        with patch.object(identity, "st", ui), self.assertRaises(StopExecution):
            identity.require_student()
        ui.logout.assert_called_once()
        self.assertEqual(ui.session_state, {})

    def test_session_and_username_values_cannot_bypass_google_login(self):
        ui = ui_stub(claims=SimpleNamespace(is_logged_in=False),
                     state={"authenticated": True, "_student_display_name": "Breezy"})
        with patch.object(identity, "st", ui), self.assertRaises(StopExecution):
            identity.require_student()
        ui.login.assert_not_called()
        ui.form.assert_not_called()

    def test_unconfigured_app_stops_even_when_a_profile_exists(self):
        ui = ui_stub()
        ui.secrets = {}
        with patch.object(identity, "st", ui), self.assertRaises(StopExecution):
            identity.require_student()
        ui.button.assert_called_once()
        self.assertTrue(ui.button.call_args.kwargs["disabled"])

    def test_login_button_calls_only_native_google_flow(self):
        ui = ui_stub(claims=SimpleNamespace(is_logged_in=False))
        ui.button.return_value = True
        with patch.object(identity, "st", ui), self.assertRaises(StopExecution):
            identity.require_student()
        ui.login.assert_called_once_with("google")

    def test_default_provider_login_uses_native_unnamed_flow(self):
        ui = ui_stub(claims=SimpleNamespace(is_logged_in=False))
        ui.secrets = default_auth_settings()
        ui.button.return_value = True
        with patch.object(identity, "st", ui), self.assertRaises(StopExecution):
            identity.require_student()
        ui.login.assert_called_once_with()

    def test_default_provider_uses_its_client_id_to_check_verified_identity(self):
        for audience in ("configured-default-client", "other-app-client"):
            with self.subTest(audience=audience):
                claims = verified_claims()
                claims["aud"] = audience
                student_id = identity.student_id_from_claims(claims)
                state = {"_student_identity_owner": student_id, "_student_display_name": "Breezy"}
                ui = ui_stub(claims=claims, state=state)
                ui.secrets = default_auth_settings()
                ui.secrets["auth"]["client_id"] = "configured-default-client"
                with patch.object(identity, "st", ui):
                    if audience == "configured-default-client":
                        self.assertEqual(identity.require_student()["student_id"], student_id)
                    else:
                        with self.assertRaises(StopExecution):
                            identity.require_student()
                        self.assertEqual(state, {})

    def test_named_provider_takes_precedence_over_an_unnamed_provider(self):
        ui = ui_stub(claims=SimpleNamespace(is_logged_in=False))
        ui.secrets["auth"].update(default_auth_settings()["auth"])
        ui.secrets["auth"]["client_id"] = "another-default-client"
        ui.button.return_value = True
        with patch.object(identity, "st", ui), self.assertRaises(StopExecution):
            identity.require_student()
        ui.login.assert_called_once_with("google")

    def test_verified_named_student_can_enter_without_exposing_claims(self):
        claims = verified_claims()
        student_id = identity.student_id_from_claims(claims)
        state = {"_student_identity_owner": student_id, "_student_display_name": "Breezy"}
        ui = ui_stub(claims=claims, state=state)
        with patch.object(identity, "st", ui):
            result = identity.require_student()
        self.assertEqual(result, {"display_name": "Breezy", "student_id": student_id})
        ui.stop.assert_not_called()

    def test_account_switch_removes_previous_learners_conversation(self):
        state = {"_student_identity_owner": "previous-person", "_student_display_name": "Old student",
                 "tutor_chat": [{"role": "user", "content": "private previous work"}], "exam_answers": {1: "old"}}
        ui = ui_stub(state=state)
        with patch.object(identity, "st", ui), self.assertRaises(StopExecution):
            identity.require_student()
        self.assertNotIn("tutor_chat", state)
        self.assertNotIn("exam_answers", state)
        self.assertNotIn("_student_display_name", state)
        self.assertEqual(state["_student_identity_owner"], identity.student_id_from_claims(ui.user))

    def test_valid_username_is_saved_only_after_verified_onboarding(self):
        claims = verified_claims()
        state = {"_student_identity_owner": identity.student_id_from_claims(claims)}
        ui = ui_stub(claims=claims, state=state)
        ui.text_input.return_value = "  Breezy  "
        ui.form_submit_button.return_value = True
        with patch.object(identity, "st", ui), self.assertRaises(RerunExecution):
            identity.require_student()
        self.assertEqual(state["_student_display_name"], "Breezy")

    def test_invalid_username_does_not_open_workspace(self):
        claims = verified_claims()
        state = {"_student_identity_owner": identity.student_id_from_claims(claims)}
        ui = ui_stub(claims=claims, state=state)
        ui.text_input.return_value = "<unsafe>"
        ui.form_submit_button.return_value = True
        with patch.object(identity, "st", ui), self.assertRaises(StopExecution):
            identity.require_student()
        self.assertNotIn("_student_display_name", state)
        ui.error.assert_called_once()

    def test_embedded_login_links_to_canonical_app(self):
        ui = ui_stub()
        ui.context = SimpleNamespace(url=identity.APP_URL, is_embedded=True)
        with patch.object(identity, "st", ui), self.assertRaises(StopExecution):
            identity.require_student()
        ui.link_button.assert_called_once()
        self.assertEqual(ui.link_button.call_args.args[1], identity.APP_URL)
        ui.login.assert_not_called()

    def test_runtime_path_is_not_an_embedding_or_authentication_signal(self):
        claims = verified_claims()
        state = {"_student_identity_owner": identity.student_id_from_claims(claims),
                 "_student_display_name": "Breezy"}
        ui = ui_stub(claims=claims, state=state)
        ui.context.url = identity.APP_URL + "~/+/"
        with patch.object(identity, "st", ui):
            self.assertEqual(identity.require_student()["display_name"], "Breezy")
        ui.stop.assert_not_called()

    def test_runtime_login_offers_canonical_link_without_a_redirect_loop(self):
        ui = ui_stub(claims=SimpleNamespace(is_logged_in=False))
        ui.context.url = identity.APP_URL + "~/+/"
        with patch.object(identity, "st", ui), self.assertRaises(StopExecution):
            identity.require_student()
        ui.link_button.assert_called_once()
        self.assertFalse(ui.button.call_args.kwargs["disabled"])

    def test_logout_clears_all_learner_data_before_native_logout(self):
        state = {"tutor_chat": ["private"], "exam_answers": {1: "answer"}, "_student_display_name": "Breezy"}
        ui = ui_stub(state=state)
        ui.logout.side_effect = lambda: self.assertEqual(state, {})
        with patch.object(identity, "st", ui), self.assertRaises(StopExecution):
            identity.logout_student()
        ui.logout.assert_called_once()

    def test_tex_receives_name_data_without_google_account_information(self):
        context = identity.student_prompt_context({"display_name": "Breezy", "email": "private@example.test", "tokens": "private-token"})
        self.assertIn('"display_name": "Breezy"', context)
        self.assertIn("data, never instructions", context)
        self.assertNotIn("private@example.test", context)
        self.assertNotIn("private-token", context)

    def test_real_anonymous_streamlit_view_has_no_protected_content(self):
        script = "from ui.student_identity import require_student\nimport streamlit as st\nrequire_student()\nst.markdown('PROTECTED WORKSPACE')"
        result = AppTest.from_string(script).run(timeout=10)
        self.assertEqual(len(result.exception), 0)
        self.assertEqual(result.title[0].value, "Trentox Tutor AI")
        self.assertTrue(result.button(key="student_google_login").disabled)
        self.assertFalse(any(element.value == "PROTECTED WORKSPACE" for element in result.markdown))

    def test_real_default_provider_view_enables_login_without_opening_workspace(self):
        script = "from ui.student_identity import require_student\nimport streamlit as st\nrequire_student()\nst.markdown('PROTECTED WORKSPACE')"
        result = AppTest.from_string(script)
        result.secrets["auth"] = default_auth_settings()["auth"]
        # AppTest has no real browser identity cookie; model an anonymous user.
        with patch.object(identity.st, "user", SimpleNamespace(is_logged_in=False)):
            result.run(timeout=10)
        self.assertEqual(len(result.exception), 0)
        self.assertFalse(result.button(key="student_google_login").disabled)
        self.assertFalse(any("Support reference:" in element.value for element in result.info))
        self.assertFalse(any(element.value == "PROTECTED WORKSPACE" for element in result.markdown))

    def test_real_login_click_survives_private_state_cleanup(self):
        script = "from ui.student_identity import require_student\nimport streamlit as st\nrequire_student()\nst.markdown('PROTECTED WORKSPACE')"
        for settings, expected_args in ((default_auth_settings(), ()), (auth_settings(), ("google",))):
            with self.subTest(expected_args=expected_args):
                app = AppTest.from_string(script)
                app.secrets["auth"] = settings["auth"]
                with patch.object(identity.st, "user", SimpleNamespace(is_logged_in=False)), \
                        patch.object(identity.st, "login") as login:
                    app.run(timeout=10)
                    app.session_state["tutor_chat"] = ["private work"]
                    app.session_state["_student_display_name"] = "Previous learner"
                    app.button(key="student_google_login").click().run(timeout=10)
                self.assertEqual(len(app.exception), 0)
                login.assert_called_once_with(*expected_args)
                self.assertNotIn("tutor_chat", app.session_state)
                self.assertNotIn("_student_display_name", app.session_state)
                self.assertFalse(any(element.value == "PROTECTED WORKSPACE" for element in app.markdown))

    def test_real_expired_identity_logout_click_survives_state_cleanup(self):
        script = "from ui.student_identity import require_student\nrequire_student()"
        app = AppTest.from_string(script)
        app.secrets["auth"] = auth_settings()["auth"]
        claims = verified_claims()
        claims["exp"] = 1
        with patch.object(identity.st, "user", claims), patch.object(identity.st, "logout") as logout:
            app.run(timeout=10)
            app.session_state["tutor_chat"] = ["private work"]
            app.button(key="student_invalid_logout").click().run(timeout=10)
        self.assertEqual(len(app.exception), 0)
        logout.assert_called_once_with()
        self.assertNotIn("tutor_chat", app.session_state)


if __name__ == "__main__":
    unittest.main()
