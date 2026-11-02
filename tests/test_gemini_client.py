import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from ui.gemini_client import configured_models, generate_reply


class ProviderError(Exception):
    def __init__(self, code, text="provider details that must not be displayed"):
        self.code = code
        super().__init__(text)


class GeminiClientTests(unittest.TestCase):
    def invoke(self, outcomes, models=("primary", "fallback")):
        self.generate = Mock(side_effect=outcomes)
        self.close = Mock()
        self.sleep = Mock()
        client = SimpleNamespace(models=SimpleNamespace(generate_content=self.generate), close=self.close)
        self.factory = Mock(return_value=client)
        return generate_reply("question", api_key="test-only-key", client_factory=self.factory, models=models, sleep=self.sleep)

    def test_success_closes_client(self):
        self.assertEqual(self.invoke([SimpleNamespace(text="answer")]), ("answer", None))
        self.close.assert_called_once()

    def test_missing_model_uses_next_supported_model(self):
        self.assertEqual(self.invoke([ProviderError(404), SimpleNamespace(text="answer")]), ("answer", None))
        self.assertEqual([call.kwargs["model"] for call in self.generate.call_args_list], ["primary", "fallback"])

    def test_key_rejection_stops_without_retry_or_secret_leak(self):
        with self.assertLogs("ui.gemini_client", "WARNING") as logs:
            reply, error = self.invoke([ProviderError(400, "API_KEY_INVALID secret-provider-body")])
        self.assertIsNone(reply)
        self.assertIn("rejected", error)
        self.assertNotIn("secret-provider-body", error + str(logs.output))
        self.assertEqual(self.generate.call_count, 1)
        self.sleep.assert_not_called()

    def test_quota_is_not_hidden_by_final_model_not_found(self):
        reply, error = self.invoke([ProviderError(429), ProviderError(429), ProviderError(404)])
        self.assertIsNone(reply)
        self.assertIn("429", error)
        self.assertEqual(self.generate.call_count, 3)
        self.sleep.assert_called_once()

    def test_temporary_service_failure_is_retried_and_can_recover(self):
        self.assertEqual(self.invoke([ProviderError(503), SimpleNamespace(text="answer")]), ("answer", None))
        self.sleep.assert_called_once()

    def test_empty_reply_is_not_treated_as_success(self):
        self.assertEqual(self.invoke([SimpleNamespace(text="  "), SimpleNamespace(text="answer")]), ("answer", None))

    def test_permission_error_has_owner_action_and_does_not_retry(self):
        reply, error = self.invoke([ProviderError(403)])
        self.assertIsNone(reply)
        self.assertIn("403", error)
        self.assertEqual(self.generate.call_count, 1)

    def test_missing_key_does_not_create_client(self):
        factory = Mock()
        reply, error = generate_reply("question", api_key="", client_factory=factory)
        self.assertIsNone(reply)
        self.assertIn("Secrets", error)
        factory.assert_not_called()

    def test_configured_primary_keeps_current_fallbacks_and_removes_duplicates(self):
        models = configured_models("gemini-3.8-flash")
        self.assertEqual(len(models), len(set(models)))
        self.assertNotIn("gemini-1.5-flash", models)
        self.assertEqual(configured_models("custom", "custom, fallback "), ("custom", "fallback"))


if __name__ == "__main__":
    unittest.main()
