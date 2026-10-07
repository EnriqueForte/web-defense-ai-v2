"""Reported usage remains unknown when incomplete; SDK discrepancies are explicit."""
from copy import deepcopy
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from agents.usage_summary import summarize_usage


def diagnostics(usages):
    return {"calls": len(usages), "dropped_events": 0, "events": [
        {"event": "completion_returned", "call": index, "usage": usage} for index, usage in enumerate(usages, 1)]}


class UsageSummaryTests(TestCase):
    def test_real_recorded_usage_discrepancy_reconciles_without_changing_sdk_values(self):
        source = diagnostics([
            {"prompt_tokens": 3299, "completion_tokens": 1967, "total_tokens": 5266, "reasoning_tokens": 1374},
            {"prompt_tokens": 1872, "completion_tokens": 2190, "total_tokens": 4062, "reasoning_tokens": 1813},
            {"prompt_tokens": 4431, "completion_tokens": 360, "total_tokens": 4791, "reasoning_tokens": 0},
            {"prompt_tokens": 2344, "completion_tokens": 753, "total_tokens": 3097, "reasoning_tokens": 216}])
        before = deepcopy(source)
        sdk = {"prompt_tokens": 11946, "completion_tokens": 5270, "total_tokens": 17216, "reasoning_tokens": 0}
        result = summarize_usage(source, sdk)
        self.assertEqual(result["usage"]["reasoning_tokens"], 3403)
        self.assertEqual(result["usage"]["total_tokens"], 17216)
        self.assertTrue(result["usage"]["complete"])
        self.assertEqual(result["usage_discrepancies"], [{"field": "reasoning_tokens", "sdk": 0, "completion_metadata": 3403}])
        self.assertEqual(result["usage_sdk"]["reasoning_tokens"], 0)
        self.assertEqual(source, before)

    def test_unknown_reasoning_is_not_converted_to_zero_or_sdk_fallback(self):
        result = summarize_usage(diagnostics([{"prompt_tokens": 1, "completion_tokens": 2, "total_tokens": 3}]),
                                 {"reasoning_tokens": 0})
        self.assertIsNone(result["usage"]["reasoning_tokens"])
        self.assertEqual(result["usage"]["total_tokens"], 3)
        self.assertFalse(result["usage"]["complete"])
        self.assertEqual(result["usage_discrepancies"], [])

    def test_duplicate_missing_or_dropped_calls_cannot_claim_complete_totals(self):
        source = diagnostics([{"prompt_tokens": 1, "completion_tokens": 2, "total_tokens": 3, "reasoning_tokens": 0}] * 2)
        for change in ("duplicate", "missing", "dropped"):
            case = deepcopy(source)
            if change == "duplicate":
                case["events"][1]["call"] = 1
            elif change == "missing":
                case["calls"] = 3
            else:
                case["dropped_events"] = 1
            result = summarize_usage(case)
            self.assertFalse(result["usage"]["complete"])
            self.assertIsNone(result["usage"]["total_tokens"])

    def test_inconsistent_provider_numbers_are_preserved_and_flagged(self):
        result = summarize_usage(diagnostics([{"prompt_tokens": 1, "completion_tokens": 2048,
                                               "total_tokens": 2048, "reasoning_tokens": 2267}]))
        self.assertEqual(result["usage"]["reasoning_tokens"], 2267)
        self.assertEqual({item["code"] for item in result["usage_warnings"]},
                         {"reasoning_exceeds_completion", "total_token_mismatch"})

    def test_invalid_values_and_extra_sdk_fields_do_not_leak(self):
        secret = "synthetic-private-value"
        result = summarize_usage({"calls": 1, "events": [{"event": "completion_returned", "call": secret,
                                 "usage": {"prompt_tokens": True, "completion_tokens": 2, "total_tokens": 0,
                                           "reasoning_tokens": 3}}]},
                                 {"api_key": secret, "prompt_tokens": secret})
        self.assertNotIn(secret, json.dumps(result))
        self.assertIsNone(result["usage"]["prompt_tokens"])

    def test_no_observations_are_unknown_not_zero_tokens(self):
        result = summarize_usage({"calls": 0, "events": []})
        self.assertFalse(result["usage"]["complete"])
        self.assertIsNone(result["usage"]["total_tokens"])

    def test_timeout_checkpoint_reports_partial_usage_without_claiming_success(self):
        from scripts.evaluate_structured_openrouter import failed_child_report
        source = diagnostics([{"prompt_tokens": 1, "completion_tokens": 2, "total_tokens": 3, "reasoning_tokens": 0}])
        source["calls"] = 2  # Second call is still pending when the child is stopped.
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "diagnostics.json").write_text(json.dumps(source), encoding="utf-8")
            report = failed_child_report(root, "deadline_600_seconds")
        self.assertEqual(report["status"], "failed")
        self.assertEqual(report["usage"]["observed_completions"], 1)
        self.assertFalse(report["usage"]["complete"])
        self.assertIsNone(report["usage"]["total_tokens"])
