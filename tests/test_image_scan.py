"""Image findings keep package counts and unknown failures distinct; offline only."""
import contextlib
import io
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import patch
from scripts import scan_lab_images as images


class ImageScanTests(TestCase):
    def report(self):
        return {"SchemaVersion": 2, "ArtifactType": "container_image", "ArtifactName": "mariadb:10.11",
                "Metadata": {"RepoDigests": ["mariadb@sha256:" + "a" * 64]},
                "Results": [{"Vulnerabilities": [
                    {"VulnerabilityID": "CVE-synthetic-1", "Severity": "HIGH", "FixedVersion": "2"},
                    {"VulnerabilityID": "CVE-synthetic-1", "Severity": "HIGH"},
                    {"VulnerabilityID": "CVE-synthetic-2", "Severity": "CRITICAL"}]}]}

    def test_package_entries_are_not_unique_exploits_and_unfixed_are_retained(self):
        row = images.summarize_report("lab-mariadb", self.report())
        self.assertEqual(row["entries_by_severity"], {"CRITICAL": 1, "HIGH": 2})
        self.assertEqual(row["distinct_vulnerability_ids"], 2)
        self.assertEqual(row["entries_with_fix"], 1)

    def test_wrong_reference_or_missing_digest_cannot_be_claimed_scanned(self):
        for value in ([], ["mariadb:10.11"], ["mariadb@sha256:invalid"]):
            report = self.report()
            report["Metadata"]["RepoDigests"] = value
            with self.assertRaises(ValueError):
                images.summarize_report("lab-mariadb", report)
        with self.assertRaises(ValueError):
            images.summarize_report("lab-dvwa", self.report())

    def test_failure_does_not_invent_zero_findings_and_all_images_are_attempted(self):
        with TemporaryDirectory() as directory, patch.object(images.subprocess, "run") as runner, \
                contextlib.redirect_stdout(io.StringIO()):
            runner.side_effect = [SimpleNamespace(stdout="Version: synthetic\n"),
                                  *[SimpleNamespace(returncode=1) for _ in images.IMAGES],
                                  SimpleNamespace(stdout="Version: synthetic\n")]
            folder = Path(directory)
            self.assertEqual(images.scan("synthetic-trivy", folder), 1)
            summary = json.loads((folder / "summary.json").read_text())
            self.assertEqual(len(summary["images"]), 6)
            self.assertTrue(all(row["status"] == "scan_failed" for row in summary["images"]))
            self.assertTrue(all("entries_by_severity" not in row for row in summary["images"]))
            self.assertFalse(summary["containers_started"])
