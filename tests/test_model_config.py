import unittest

from config.model_config import configured_model_candidates


class ModelConfigTests(unittest.TestCase):
    def test_defaults_use_current_groq_model_ids(self):
        self.assertEqual(
            configured_model_candidates({}),
            ["groq/openai/gpt-oss-120b", "groq/openai/gpt-oss-20b"],
        )

    def test_environment_model_and_fallbacks_are_trimmed_and_unique(self):
        self.assertEqual(
            configured_model_candidates({
                "LLM_MODEL": " groq/custom/model ",
                "LLM_FALLBACK_MODELS": "groq/fallback/one, groq/fallback/one, ",
            }),
            ["groq/custom/model", "groq/fallback/one"],
        )

    def test_empty_model_uses_default_and_empty_fallback_disables_fallbacks(self):
        self.assertEqual(
            configured_model_candidates({"LLM_MODEL": " ", "LLM_FALLBACK_MODELS": ""}),
            ["groq/openai/gpt-oss-120b"],
        )

    def test_previously_configured_retired_model_is_replaced(self):
        self.assertEqual(
            configured_model_candidates({
                "LLM_MODEL": "groq/meta-llama/llama-4-scout-17b-16e-instruct",
                "LLM_FALLBACK_MODELS": "groq/llama-3.3-70b-versatile,groq/openai/gpt-oss-20b",
            }),
            ["groq/openai/gpt-oss-120b", "groq/openai/gpt-oss-20b"],
        )


if __name__ == "__main__":
    unittest.main()
