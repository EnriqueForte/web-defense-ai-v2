"""SDK-independent completion diagnostics, with hostile/partial synthetic payloads."""
import json
from types import SimpleNamespace
from unittest import TestCase

from agents.analysis_diagnostics import AnalysisDiagnostics
from agents.completion_metadata import completion_metadata

SECRET = "synthetic-test-key"


class CompletionMetadataTests(TestCase):
    def test_empty_content_and_reasoning_limit_are_distinguished(self):
        response = {"model": "vendor/test-model:free", "choices": [{"finish_reason": "length",
            "message": {"content": None, "reasoning_content": SECRET}}],
            "usage": {"prompt_tokens": 500, "completion_tokens": 2048, "total_tokens": 2548,
                      "completion_tokens_details": {"reasoning_tokens": 2048}}}
        metadata = completion_metadata(response, requested_model="openrouter/openrouter/free", max_tokens=2048)
        self.assertEqual(metadata["finish_reason"], "length")
        self.assertEqual(metadata["response_model"], "vendor/test-model:free")
        self.assertFalse(metadata["content_present"])
        self.assertIsNone(metadata["content_characters"])
        self.assertTrue(metadata["reasoning_present"])
        self.assertEqual(metadata["usage"]["reasoning_tokens"], 2048)
        self.assertEqual(metadata["max_tokens"], 2048)
        self.assertNotIn(SECRET, json.dumps(metadata))

    def test_normal_output_counts_without_content_headers_or_ids(self):
        response = SimpleNamespace(model="vendor/test-model:free", id=SECRET, headers={"Authorization": SECRET},
            choices=[SimpleNamespace(finish_reason="stop", message=SimpleNamespace(content=SECRET))],
            usage=SimpleNamespace(prompt_tokens=1, completion_tokens=2, total_tokens=3,
                                  completion_tokens_details=SimpleNamespace(reasoning_tokens=0)))
        metadata = completion_metadata(response)
        self.assertEqual(metadata["finish_reason"], "stop")
        self.assertEqual(metadata["content_characters"], len(SECRET))
        self.assertFalse(metadata["reasoning_present"])
        self.assertEqual(metadata["usage"]["reasoning_tokens"], 0)
        self.assertNotIn(SECRET, json.dumps(metadata))

    def test_missing_usage_is_unknown_rather_than_zero(self):
        metadata = completion_metadata({"choices": []})
        self.assertEqual(metadata["choice_count"], 0)
        self.assertEqual(metadata["usage"], {"prompt_tokens": None, "completion_tokens": None,
                                            "total_tokens": None, "reasoning_tokens": None})
        self.assertIsNone(metadata["response_model"])
        self.assertIsNone(metadata["finish_reason"])

    def test_numbers_and_model_fields_do_not_accept_arbitrary_data(self):
        response = {"model": "vendor/" + SECRET, "choices": [{"finish_reason": SECRET,
            "message": {"content": [SECRET], "reasoning_details": [{"text": SECRET}]}}],
            "usage": {"prompt_tokens": True, "completion_tokens": "2048", "total_tokens": float("inf"),
                      "completion_tokens_details": {"reasoning_tokens": -1}}}
        metadata = completion_metadata(response, requested_model=SECRET, max_tokens=SECRET, secrets=(SECRET,))
        self.assertIsNone(metadata["response_model"])
        self.assertIsNone(metadata["requested_model"])
        self.assertIsNone(metadata["finish_reason"])
        self.assertIsNone(metadata["max_tokens"])
        self.assertTrue(all(value is None for value in metadata["usage"].values()))
        self.assertNotIn(SECRET, json.dumps(metadata))

    def test_unexpected_sdk_shape_cannot_replace_completion_error(self):
        class BrokenResponse:
            @property
            def choices(self):
                raise ValueError(SECRET)
        metadata = completion_metadata(BrokenResponse())
        self.assertEqual(metadata, {"metadata_status": "unavailable"})
        self.assertNotIn(SECRET, json.dumps(metadata))

    def test_checkpoint_associates_metadata_with_active_stage_and_logical_call(self):
        checkpoints = []
        diagnostic = AnalysisDiagnostics(checkpoint=checkpoints.append)
        identifier = diagnostic.begin_call("detection")
        diagnostic.completion({"model": "vendor/test-model:free",
            "choices": [{"finish_reason": "stop", "message": {"content": ""}}]})
        diagnostic.finish_call(identifier, "")
        event = checkpoints[-1]["events"][1]
        self.assertEqual(event["event"], "completion_returned")
        self.assertEqual(event["stage"], "detection")
        self.assertEqual(event["call"], identifier)
        self.assertEqual(event["content_characters"], 0)
        self.assertEqual(checkpoints[-1]["events"][-1]["characters"], 0)
