"""Evaluation catches event omissions hidden by family scores; no provider."""
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from agents.evaluation_fixtures import fixture, score_patterns, score_evidence
from agents.evidence_preparation import prepare_evidence
from dashboard.services.structured_publication import load_current
from scripts.check_a05_offline import review_matrix

ID = "e" * 32


class EvaluationEvidenceTests(TestCase):
    def prepared(self, case="same_family", **kwargs):
        return prepare_evidence(fixture(case)["text"], ID, config={}, **kwargs)

    def test_family_pass_does_not_hide_missing_same_family_event(self):
        prepared = self.prepared()
        findings = [{"pattern": "sql_injection", "evidence_ids": [prepared.bundle.items[0].evidence_id]}]
        self.assertTrue(score_patterns(findings, "same_family")["pattern_expectations_met"])
        score = score_evidence(findings, prepared.bundle, "same_family")
        self.assertFalse(score["evidence_expectations_met"])
        self.assertEqual(score["evidence_recall"], 0.5)
        self.assertEqual(score["missing_evidence_pairs"], [{"pattern": "sql_injection", "line_number": 2}])

    def test_grouping_and_overlap_do_not_inflate_pair_scores(self):
        prepared = self.prepared()
        first, second = [item.evidence_id for item in prepared.bundle.items[:2]]
        score = score_evidence([{"pattern": "sql_injection", "evidence_ids": [first, second]},
                                {"pattern": "sql_injection", "evidence_ids": [first]}], prepared.bundle, "same_family")
        self.assertTrue(score["evidence_expectations_met"])
        self.assertEqual(len(score["actual_evidence_pairs"]), 2)
        self.assertEqual(score["evidence_precision"], 1)

    def test_normal_request_attribution_reduces_precision(self):
        prepared = self.prepared()
        score = score_evidence([{"pattern": "sql_injection", "evidence_ids": [
            item.evidence_id for item in prepared.bundle.items]}], prepared.bundle, "same_family")
        self.assertEqual(score["evidence_precision"], 2 / 3)
        self.assertEqual(score["unexpected_evidence_pairs"], [{"pattern": "sql_injection", "line_number": 3}])
        self.assertFalse(score["evidence_expectations_met"])

    def test_selection_omissions_are_separate_from_model_omissions(self):
        prepared = self.prepared(max_items=1)
        score = score_evidence([{"pattern": "sql_injection", "evidence_ids": [
            prepared.bundle.items[0].evidence_id]}], prepared.bundle, "same_family")
        self.assertTrue(score["evidence_expectations_met"])
        self.assertFalse(score["fixture_fully_selected"])
        self.assertEqual(len(score["unselected_evidence_pairs"]), 1)
        self.assertEqual(score["missing_evidence_pairs"], [])

    def test_negatives_keep_undefined_metrics_and_uncertainty_is_optional(self):
        normal = score_evidence([], self.prepared("normal").bundle, "normal")
        self.assertIsNone(normal["evidence_recall"])
        self.assertIsNone(normal["evidence_precision"])
        prepared = self.prepared("incomplete")
        score = score_evidence([{"pattern": "other", "evidence_ids": [prepared.bundle.items[0].evidence_id]}],
                               prepared.bundle, "incomplete")
        self.assertTrue(score["evidence_expectations_met"])
        self.assertIsNone(score["evidence_recall"])

    def test_truncated_negative_fixture_is_not_reported_as_fully_selected(self):
        score = score_evidence([], self.prepared("normal", max_items=1).bundle, "normal")
        self.assertTrue(score["evidence_expectations_met"])
        self.assertTrue(score["expected_evidence_fully_selected"])
        self.assertFalse(score["fixture_fully_selected"])
        self.assertEqual(score["selected_input_lines"], 1)

    def test_foreign_refs_wrong_source_and_corrupted_line_maps_fail_closed(self):
        prepared = self.prepared()
        with self.assertRaisesRegex(ValueError, "evaluation_foreign_reference"):
            score_evidence([{"pattern": "sql_injection", "evidence_ids": ["e_foreign"]}], prepared.bundle, "same_family")
        with self.assertRaisesRegex(ValueError, "evaluation_fixture_mismatch"):
            score_evidence([], prepared.bundle, "mixed")
        original = prepared.bundle.to_dict()
        for field, value in (("raw", "wrong"), ("line_number", 0), ("line_number", True)):
            corrupted = deepcopy(original)
            corrupted["items"][0][field] = value
            with self.subTest(field=field, value=value), self.assertRaisesRegex(ValueError, "evaluation_fixture_mismatch"):
                score_evidence([], corrupted, "same_family")

    def test_offline_matrix_checks_publications_and_rejects_negative_controls(self):
        with TemporaryDirectory() as temporary:
            result = review_matrix(Path(temporary))
            for row in [*result["cases"], result["guard_publication"]]:
                manifest, _, _ = load_current(Path(temporary) / row["name"])
                self.assertEqual(manifest["generation"], row["generation"])
                self.assertEqual(manifest["sha256"], row["sha256"])
        self.assertTrue(result["passed"], result)
        self.assertEqual(result["provider_calls"], 0)
        self.assertEqual(result["fixture_version"], "a05-fixtures-2")
        self.assertEqual(len(result["cases"]), 22)
        self.assertEqual(len(result["guard_controls"]), 8)
