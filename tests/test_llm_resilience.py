import unittest

from config.llm_resilience import call_with_model_fallback, is_rate_limit_error, retry_after_seconds


class RateLimitError(Exception):
    status_code = 429


class LLMResilienceTests(unittest.TestCase):
    def test_rate_limit_retry_honors_provider_wait_then_succeeds(self):
        calls = []
        waits = []
        models = []

        def invoke():
            calls.append(models[-1])
            if len(calls) == 1:
                raise RateLimitError("Please try again in 2.5s")
            return "respuesta"

        result = call_with_model_fallback(
            invoke, ["modelo-a"], models.append, sleep=waits.append,
            retries=2, max_wait_seconds=10,
        )
        self.assertEqual(result, "respuesta")
        self.assertEqual(calls, ["modelo-a", "modelo-a"])
        self.assertEqual(waits, [2.5])

    def test_exhausted_primary_uses_fallback_with_bounded_attempts(self):
        calls = []
        waits = []
        models = []

        def invoke():
            calls.append(models[-1])
            if models[-1] == "modelo-a":
                raise RateLimitError("rate limit")
            return "fallback response"

        result = call_with_model_fallback(
            invoke, ["modelo-a", "modelo-b"], models.append, sleep=waits.append,
            retries=1, backoff_seconds=1, max_wait_seconds=3,
        )
        self.assertEqual(result, "fallback response")
        self.assertEqual(calls, ["modelo-a", "modelo-a", "modelo-b"])
        self.assertEqual(waits, [1])

    def test_does_not_retry_non_rate_limit_errors(self):
        calls = []

        def invoke():
            calls.append(True)
            raise ValueError("invalid request")

        with self.assertRaisesRegex(ValueError, "invalid request"):
            call_with_model_fallback(invoke, ["modelo-a", "modelo-b"], lambda _: None,
                                     sleep=lambda _: None)
        self.assertEqual(len(calls), 1)

    def test_wait_budget_skips_too_long_retry_and_tries_fallback(self):
        calls = []
        waits = []
        models = []

        def invoke():
            calls.append(models[-1])
            if models[-1] == "modelo-a":
                raise RateLimitError("try again in 50s")
            return "fallback response"

        result = call_with_model_fallback(
            invoke, ["modelo-a", "modelo-b"], models.append, sleep=waits.append,
            retries=3, max_wait_seconds=10,
        )
        self.assertEqual(result, "fallback response")
        self.assertEqual(calls, ["modelo-a", "modelo-b"])
        self.assertEqual(waits, [])

    def test_rate_limit_classifier_and_retry_after_header(self):
        class HeaderError(Exception):
            status_code = 429
            headers = {"retry-after": "4"}

        error = HeaderError("throttled")
        self.assertTrue(is_rate_limit_error(error))
        self.assertEqual(retry_after_seconds(error), 4.0)
        self.assertFalse(is_rate_limit_error(ValueError("bad input")))


if __name__ == "__main__":
    unittest.main()
