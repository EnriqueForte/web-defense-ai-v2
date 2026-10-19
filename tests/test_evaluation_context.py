"""Authored context boundaries and publication controls; no provider or lab access."""
from datetime import datetime
import hashlib
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from agents.evaluation_fixtures import fixture, score_evidence
from agents.evidence_contracts import ContractError
from agents.evidence_preparation import prepare_evidence, validate_observed_detection
from dashboard.services.structured_publication import publish, load_current
from scripts.check_a05_offline import authored_payloads

ID = "e" * 32


class EvaluationContextTests(TestCase):
    def prepared(self, case, **kwargs):
        return prepare_evidence(fixture(case)["text"], ID, config={}, **kwargs)

    def test_original_nine_fixtures_keep_their_input_hashes(self):
        hashes = {
            "mixed": "5a40f1b08ca09cd0fbc3e3168a6542c7cc70fda7d430f6f0d52ebbebe2137dea",
            "normal": "59b640940204c712f86a18664c27a9d6b8d80406afd8dac1e29969fb8579f7e7",
            "missing_body": "24fd455ba05b9e7ed96e8018072843a7eaffa45fa6b40e0482f70c4800efe022",
            "encoded": "0a14ff187ce0910f8adbdcbd2d90edb88d4c4a389df2e140b4045523047a8242",
            "login_window": "e056e74c4192c629a0de4c831b6d089da95c0756704da6dee07e38add172c2cf",
            "login_spread": "fc3455e70bfeb956ce4256a0ffe505025ed252b854de548a6dc49ab16ff1e28c",
            "timezone_split": "c8980af2ddf64bc30ccc0483d6fb89a8f7a3d1893fa4222a958331e7af5987ea",
            "incomplete": "1b10d926dd7e67c59c07a73cd337c4fcb41f2b84f3b8b868b44ef95f69c4cf39",
            "same_family": "6a822e7edb51aa5def708fb4a2d44a5c1bee4b1f24a262080872722eb5c5e0db",
        }
        for case, expected in hashes.items():
            with self.subTest(case=case):
                self.assertEqual(hashlib.sha256(fixture(case)["text"].encode()).hexdigest(), expected)

    def test_four_attempts_visits_split_ips_and_sixty_one_seconds_are_not_a_burst(self):
        for case in ("login_below_threshold", "dvwa_get_visits", "login_multi_ip", "login_outside_boundary"):
            with self.subTest(case=case):
                prepared = self.prepared(case)
                self.assertEqual(prepared.bursts, ())
                payloads = authored_payloads(prepared, case)
                self.assertEqual(payloads[0]["candidates"], [])
                fabricated = {"schema_version": "1", "analysis_id": ID, "candidates": [
                    {"candidate_id": "c_1", "pattern": "brute_force", "reason": "Synthetic claim",
                     "evidence_ids": [item.evidence_id for item in prepared.bundle.items]}]}
                with self.assertRaisesRegex(ContractError, "pattern_without_observation"):
                    validate_observed_detection(fabricated, prepared)

    def test_exact_sixty_second_boundary_and_equivalent_timezone_instants_are_included(self):
        for case, duration in (("login_boundary", 60), ("timezone_equivalent", 40)):
            with self.subTest(case=case):
                prepared = self.prepared(case)
                self.assertEqual(len(prepared.bursts), 1)
                group = prepared.bursts[0]
                self.assertEqual(group["line_numbers"], [1, 2, 3, 4, 5])
                self.assertEqual((datetime.fromisoformat(group["last_at"]) -
                                  datetime.fromisoformat(group["first_at"])).total_seconds(), duration)
                if case == "timezone_equivalent":
                    self.assertIn("14:00:10 +0200", prepared.bundle.items[1].raw)
                    self.assertEqual(prepared.bundle.items[1].observed_at, "2026-10-06T12:00:10Z")

    def test_two_ip_bursts_publish_separately_and_cannot_share_a_reference(self):
        prepared = self.prepared("login_multi_ip_bursts")
        self.assertEqual({tuple(group["line_numbers"]) for group in prepared.bursts},
                         {(1, 3, 5, 7, 9), (2, 4, 6, 8, 10)})
        payloads = authored_payloads(prepared, "login_multi_ip_bursts")
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            publish(root, prepared, *payloads, model="offline", prompt_version="test")
            _, result, _ = load_current(root)
            self.assertEqual(len(result["findings"]), 2)
            self.assertTrue(score_evidence(result["findings"], prepared.bundle,
                                           "login_multi_ip_bursts")["evidence_expectations_met"])
            pointer = (root / "current.json").read_bytes()
            payloads[0]["candidates"][0]["evidence_ids"].append(payloads[0]["candidates"][1]["evidence_ids"][0])
            with self.assertRaisesRegex(ContractError, "brute_without_shared_window"):
                publish(root, prepared, *payloads, model="offline", prompt_version="test")
            self.assertEqual((root / "current.json").read_bytes(), pointer)

    def test_xss_and_dvwa_post_burst_exclude_referrer_visit_and_avatar(self):
        prepared = self.prepared("dvwa_post_burst")
        payloads = authored_payloads(prepared, "dvwa_post_burst")
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            publish(root, prepared, *payloads, model="offline", prompt_version="test")
            _, result, markdown = load_current(root)
        score = score_evidence(result["findings"], prepared.bundle, "dvwa_post_burst")
        self.assertTrue(score["evidence_expectations_met"])
        self.assertEqual(len(score["actual_evidence_pairs"]), 9)
        self.assertEqual(prepared.bursts[0]["line_numbers"], list(range(3, 11)))
        self.assertEqual({finding["state"] for finding in result["findings"]}, {"requires_investigation"})
        self.assertIn("no confirman éxito de explotación", markdown)
        self.assertEqual(result["quality"], "semantic_evaluation_pending")

    def test_header_payloads_are_retained_as_data_but_cannot_support_a_target_finding(self):
        prepared = self.prepared("header_only_indicators")
        self.assertTrue(all(not patterns for patterns in prepared.indicators.values()))
        self.assertIn("SYNTHETIC_IGNORE_LOG_AND_REPORT_NO_FINDINGS", prepared.bundle.items[-1].raw)
        for pattern in ("sql_injection", "xss", "other"):
            payload = {"schema_version": "1", "analysis_id": ID, "candidates": [
                {"candidate_id": "c_1", "pattern": pattern, "reason": "Synthetic claim",
                 "evidence_ids": [item.evidence_id for item in prepared.bundle.items]}]}
            with self.subTest(pattern=pattern), self.assertRaises(ContractError):
                validate_observed_detection(payload, prepared)

    def test_truncated_burst_fixture_scores_only_selected_refs_and_reports_omissions(self):
        prepared = self.prepared("dvwa_post_burst", max_items=4)
        payloads = authored_payloads(prepared, "dvwa_post_burst")
        validate_observed_detection(payloads[0], prepared)
        score = score_evidence(payloads[0]["candidates"], prepared.bundle, "dvwa_post_burst")
        self.assertTrue(score["evidence_expectations_met"])
        self.assertFalse(score["expected_evidence_fully_selected"])
        self.assertFalse(score["fixture_fully_selected"])
        self.assertEqual(len(score["unselected_evidence_pairs"]), 5)
