"""Fixture partition scores catch count inflation hidden by pair coverage."""
from copy import deepcopy
import contextlib
import io
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from agents.evaluation_fixtures import fixture
from agents.evaluation_scoring import score_groups, score_fixture_result
from agents.evidence_preparation import prepare_evidence
from dashboard.services.structured_publication import publish
from scripts.check_a05_offline import authored_payloads, fingerprints
from scripts.score_structured_fixture import main

ID = "e" * 32
ROOT = Path(__file__).resolve().parents[1]


class EvaluationGroupTests(TestCase):
    def prepared(self, case="dvwa_post_burst", **kwargs):
        return prepare_evidence(fixture(case)["text"], ID, config={}, **kwargs)

    def split(self, prepared, overlap=False):
        detection, classification, narrative = authored_payloads(prepared, "dvwa_post_burst")
        burst = detection["candidates"][1]
        refs = burst["evidence_ids"]
        burst["evidence_ids"] = refs[:5] if overlap else refs[:4]
        detection["candidates"].append({**burst, "candidate_id": "c_3",
                                       "evidence_ids": refs[3:] if overlap else refs[4:]})
        classification["classifications"].append({**classification["classifications"][1], "candidate_id": "c_3"})
        return detection, classification, narrative

    def test_split_and_overlapping_bursts_keep_pair_coverage_but_fail_group_conformance(self):
        prepared = self.prepared()
        for overlap in (False, True):
            with self.subTest(overlap=overlap):
                findings = self.split(prepared, overlap)[0]["candidates"]
                score = score_fixture_result(findings, prepared.bundle, "dvwa_post_burst")
                self.assertTrue(score["pattern_expectations_met"])
                self.assertTrue(score["evidence_expectations_met"])
                self.assertEqual(score["evidence_precision"], 1)
                self.assertEqual(score["evidence_recall"], 1)
                self.assertFalse(score["group_expectations_met"])
                self.assertFalse(score["fixture_expectations_met"])
                self.assertEqual(score["expected_selected_group_count"], 2)
                self.assertEqual(score["actual_group_count"], 3)
                self.assertEqual(score["group_recall"], 0.5)
                self.assertEqual(score["group_precision"], 1 / 3)

    def test_group_identity_ignores_ids_order_and_order_of_references(self):
        prepared = self.prepared()
        original = authored_payloads(prepared, "dvwa_post_burst")[0]["candidates"]
        reordered = deepcopy(original[::-1])
        for index, item in enumerate(reordered):
            item["candidate_id"] = f"different_{index}"
            item["evidence_ids"].reverse()
        self.assertEqual(score_groups(original, prepared.bundle, "dvwa_post_burst"),
                         score_groups(reordered, prepared.bundle, "dvwa_post_burst"))

    def test_duplicate_findings_are_counted_once_as_matches_and_again_as_excess(self):
        prepared = self.prepared()
        findings = authored_payloads(prepared, "dvwa_post_burst")[0]["candidates"]
        findings.append(deepcopy(findings[1]))
        score = score_groups(findings, prepared.bundle, "dvwa_post_burst")
        self.assertEqual(score["group_recall"], 1)
        self.assertEqual(score["group_precision"], 2 / 3)
        self.assertEqual(len(score["unexpected_groups"]), 1)
        self.assertFalse(score["group_expectations_met"])

    def test_merged_two_ip_bursts_do_not_match_the_authored_partitions(self):
        prepared = self.prepared("login_multi_ip_bursts")
        findings = [{"pattern": "brute_force", "evidence_ids": [item.evidence_id for item in prepared.bundle.items]}]
        score = score_fixture_result(findings, prepared.bundle, "login_multi_ip_bursts")
        self.assertTrue(score["evidence_expectations_met"])
        self.assertFalse(score["group_expectations_met"])
        self.assertEqual(score["group_precision"], 0)
        self.assertEqual(score["group_recall"], 0)

    def test_partial_selection_keeps_projected_groups_and_a_failed_full_fixture_verdict(self):
        prepared = self.prepared(max_items=4)
        findings = authored_payloads(prepared, "dvwa_post_burst")[0]["candidates"]
        score = score_fixture_result(findings, prepared.bundle, "dvwa_post_burst")
        self.assertTrue(score["group_expectations_met"])
        self.assertFalse(score["fixture_expectations_met"])
        self.assertFalse(score["fixture_fully_selected"])

    def test_optional_uncertainty_and_empty_negatives_do_not_invent_required_groups(self):
        normal = self.prepared("normal")
        score = score_groups([], normal.bundle, "normal")
        self.assertTrue(score["group_expectations_met"])
        self.assertIsNone(score["group_recall"])
        self.assertIsNone(score["group_precision"])
        incomplete = self.prepared("incomplete")
        findings = [{"pattern": "other", "evidence_ids": [incomplete.bundle.items[0].evidence_id]}]
        score = score_groups(findings, incomplete.bundle, "incomplete")
        self.assertTrue(score["group_expectations_met"])
        self.assertEqual(score["group_precision"], 1)
        self.assertIsNone(score["group_recall"])

    def test_wrong_fixture_and_foreign_references_are_not_group_scores(self):
        prepared = self.prepared()
        with self.assertRaisesRegex(ValueError, "evaluation_fixture_mismatch"):
            score_groups([], prepared.bundle, "normal")
        with self.assertRaisesRegex(ValueError, "evaluation_foreign_reference"):
            score_groups([{"pattern": "xss", "evidence_ids": ["e_foreign"]}], prepared.bundle, "dvwa_post_burst")
        for pattern, refs in (("SYNTHETIC_UNTRUSTED_PATTERN", [prepared.bundle.items[0].evidence_id]),
                              ("xss", []), ("xss", [prepared.bundle.items[0].evidence_id] * 2)):
            with self.subTest(pattern=pattern, refs=refs), self.assertRaisesRegex(ValueError, "evaluation_invalid_group"):
                score_groups([{"pattern": pattern, "evidence_ids": refs}], prepared.bundle, "dvwa_post_burst")

    def test_read_only_cli_distinguishes_matching_split_and_corrupt_publications(self):
        prepared = self.prepared()
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            for name, payloads, expected in (("valid", authored_payloads(prepared, "dvwa_post_burst"), 0),
                                             ("split", self.split(prepared), 2)):
                publication = root / name
                publish(publication, prepared, *payloads, model="offline", prompt_version="test")
                if name == "valid":
                    pointer = publication / "current.json"
                    manifest = json.loads(pointer.read_text())
                    manifest["sha256"]["synthetic_extra"] = "SYNTHETIC_UNTRUSTED_METADATA"
                    for target in (pointer, publication / "generations" / manifest["generation"] / "manifest.json"):
                        target.write_text(json.dumps(manifest), encoding="utf-8")
                previous = fingerprints(publication)
                output = io.StringIO()
                with contextlib.redirect_stdout(output), \
                        patch("dotenv.load_dotenv", side_effect=AssertionError("dotenv_forbidden")), \
                        patch("config.model_config.load_local_env", side_effect=AssertionError("settings_forbidden")):
                    self.assertEqual(main(["--publication", str(publication), "--case", "dvwa_post_burst"]), expected)
                self.assertEqual(fingerprints(publication), previous)
                report = json.loads(output.getvalue())
                self.assertEqual(report["status"], "reviewed")
                self.assertEqual(report["provider_calls"], 0)
                self.assertFalse(report["semantic_acceptance"])
                self.assertEqual(report["fixture_expectations_met"], expected == 0)
                self.assertNotIn("Synthetic/1", output.getvalue())
                self.assertNotIn("SYNTHETIC_UNTRUSTED_METADATA", output.getvalue())
                self.assertEqual(set(report["sha256"]), {"result.json", "report.md"})
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(main(["--publication", str(root / "valid"), "--case", "normal"]), 1)
            self.assertEqual(json.loads(output.getvalue())["status"], "rejected")
            manifest = json.loads((root / "valid/current.json").read_text())
            body = root / "valid/generations" / manifest["generation"] / "result.json"
            body.write_bytes(body.read_bytes() + b" ")
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(main(["--publication", str(root / "valid"), "--case", "dvwa_post_burst"]), 1)
            self.assertEqual(json.loads(output.getvalue())["status"], "rejected")
            (root / "split/current.json").write_text("{synthetic-invalid", encoding="utf-8")
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(main(["--publication", str(root / "split"), "--case", "dvwa_post_burst"]), 1)
            self.assertEqual(json.loads(output.getvalue()), {"status": "rejected", "reason": "fixture_review_unavailable"})

    def test_cli_in_a_fresh_process_reads_existing_publication_without_writes_or_provider_imports(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            prepared = self.prepared()
            publish(root, prepared, *authored_payloads(prepared, "dvwa_post_burst"), model="offline", prompt_version="test")
            previous = fingerprints(root)
            program = (
                "import runpy,sys; from unittest.mock import patch; "
                "p=patch('dotenv.load_dotenv',side_effect=AssertionError('dotenv_forbidden'));p.start(); "
                "sys.argv=['score_structured_fixture.py','--publication',sys.argv[1],'--case','dvwa_post_burst']; "
                "code=runpy.run_path('scripts/score_structured_fixture.py'); "
                "assert code['main']()==0; "
                "assert not {'crewai','litellm','main','pipeline','config.model_config'} & sys.modules.keys()"
            )
            completed = subprocess.run([sys.executable, "-B", "-c", program, str(root)],
                                       cwd=ROOT, capture_output=True, text=True, timeout=20)
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertEqual(json.loads(completed.stdout)["metrics_version"], "a05-metrics-2")
            self.assertEqual(fingerprints(root), previous)
