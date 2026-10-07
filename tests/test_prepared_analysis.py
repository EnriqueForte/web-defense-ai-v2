"""A-03/A-04: attributed criteria and publication failures, synthetic sources only."""
from copy import deepcopy
from datetime import datetime
import importlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from agents.evidence_contracts import ContractError
from agents.evidence_preparation import prepare_evidence, observed_patterns, validate_observed_detection, validate_observed_classification
from agents.structured_reporting import compose
from dashboard.services import structured_publication as publication
from dashboard.services.runtime_lock import AlreadyRunning, exclusive_lock

ID = "a" * 32


def line(target, second=0, offset="+0000", method="GET", ip="192.0.2.1"):
    minute, seconds = divmod(second, 60)
    return f'{ip} - - [06/Oct/2026:12:{minute:02d}:{seconds:02d} {offset}] "{method} {target} HTTP/1.1" 200 1'


class PreparationTests(TestCase):
    def test_reference_fixture_comparison_explains_single_brute_difference(self):
        from agents.log_analyst import pre_filtrar_lineas
        fixture = Path(__file__).parent / "fixtures/traffic.json"
        expected = {"sqli": "sql_injection", "xss": "xss", "path": "path_traversal", "cmd": "command_injection"}
        for case in json.loads(fixture.read_text(encoding="utf-8")):
            raw = case.get("raw") or line(case["target"], method=case.get("method", "GET"))
            self.assertEqual(bool(pre_filtrar_lineas([raw])["sospechosas"]), case["suspicious"])
            prepared = prepare_evidence(raw, ID)
            observed = {pattern for patterns in prepared.indicators.values() for pattern in patterns}
            self.assertEqual(observed, {expected[case["id"]]} if case["id"] in expected else set())
        # Legacy marks a /brute/ route; the new lane needs an actual frequency window.

    def test_balanced_families_survive_large_authentication_burst(self):
        targets = ('/?q=UNION+SELECT', '/?q=%3Cimg+onerror=confirm(1)%3E',
                   '/?file=%252e%252e%252fetc/passwd', '/?host=x%3Bwhoami')
        text = "\n".join([*(line(target) for target in targets),
                          *(line('/vulnerabilities/brute/?username=test&password=x', i) for i in range(20))])
        prepared = prepare_evidence(text, ID, max_items=5)
        families = {pattern for patterns in prepared.indicators.values() for pattern in patterns}
        self.assertEqual(families, {"sql_injection", "xss", "path_traversal", "command_injection", "brute_force"})
        self.assertEqual(len(prepared.bundle.items), 5)
        self.assertEqual(prepared.bursts[0]["count"], 20)
        self.assertLess(len(prepared.bursts[0]["selected_evidence_ids"]), 20)
        self.assertTrue(prepared.scope["incomplete"])

    def test_xss_onerror_and_double_encoding_are_observed(self):
        prepared = prepare_evidence(line('/?q=%253Cimg%2520onerror%253Dconfirm(1)%253E'), ID)
        self.assertIn("xss", next(iter(prepared.indicators.values())))

    def test_normal_and_post_without_body_do_not_claim_attack(self):
        for raw in (line('/selection?message=please+select'), line('/vulnerabilities/exec/', method="POST")):
            prepared = prepare_evidence(raw, ID)
            self.assertEqual(next(iter(prepared.indicators.values())), ())
            self.assertEqual(prepared.bursts, ())
        text = "\n".join(line('/search?query=login', i, method="POST") for i in range(5))
        self.assertFalse(prepare_evidence(text, ID).bursts)

    def test_single_brute_path_is_not_a_burst_and_threshold_is_used(self):
        target = '/vulnerabilities/brute/?username=test&password=x'
        self.assertEqual(prepare_evidence(line(target), ID).bursts, ())
        text = "\n".join(line(target, i) for i in range(5))
        self.assertTrue(prepare_evidence(text, ID).bursts)
        self.assertFalse(prepare_evidence(text, ID, config={"UMBRAL_FUERZA_BRUTA": "6"}).bursts)

    def test_mixed_offsets_do_not_create_false_burst(self):
        text = "\n".join(line('/login', i, offset="+0900" if i % 2 else "+0000", method="POST") for i in range(5))
        self.assertFalse(prepare_evidence(text, ID).bursts)

    def test_each_aggregate_really_fits_its_window_and_keeps_separate_bursts(self):
        text = "\n".join(line('/login', i, method="POST") for i in (*range(10), *range(120, 130)))
        prepared = prepare_evidence(text, ID)
        self.assertEqual(len(prepared.bursts), 2)
        for group in prepared.bursts:
            span = (datetime.fromisoformat(group["last_at"].replace("Z", "+00:00")) -
                    datetime.fromisoformat(group["first_at"].replace("Z", "+00:00"))).total_seconds()
            self.assertLessEqual(span, group["window_seconds"])
            self.assertEqual(group["count"], len(group["line_numbers"]))

    def test_config_window_bytes_omissions_and_invalid_values_are_explicit(self):
        text = "\n".join(line('/?q=UNION+SELECT', i) for i in range(5))
        prepared = prepare_evidence(text, ID, config={"MAX_LINEAS_LOG": "2"}, max_selected_bytes=1)
        self.assertEqual(prepared.scope["scanned_lines"], 2)
        self.assertEqual(prepared.scope["outside_window"], 3)
        self.assertEqual(prepared.bundle.items, ())
        for value in ("bad", "0", "-1", "1001", True, 5.2):
            with self.assertRaises(ContractError):
                prepare_evidence(text, ID, config={"MAX_LINEAS_LOG": value})


class PublicationTests(TestCase):
    def test_linked_current_pointer_is_rejected_before_reading_its_target(self):
        with patch.object(Path, "is_symlink", autospec=True, side_effect=lambda path: path.name == "current.json"), \
                patch.object(Path, "read_text", side_effect=AssertionError("Linked target must not be read")):
            with self.assertRaisesRegex(ContractError, "linked_publication_path"):
                publication.load_current(self.root)

    def setUp(self):
        self.root = Path(self.enterContext(TemporaryDirectory()))
        self.prepared = prepare_evidence(line('/?q=UNION+SELECT'), ID)
        self.detection = {"schema_version": "1", "analysis_id": ID, "candidates": [
            {"candidate_id": "c_1", "evidence_ids": [self.prepared.bundle.items[0].evidence_id],
             "pattern": "sql_injection", "reason": "Observed SQL expression"}]}
        self.classification = {"schema_version": "1", "analysis_id": ID, "classifications": [
            {"candidate_id": "c_1", "severity": "high", "state": "requires_investigation", "reason": "Success unknown"}]}
        self.narrative = {"schema_version": "1", "analysis_id": ID, "summary": "Review observed payload",
                          "recommendations": [{"candidate_id": "c_1", "text": "Review validation"}]}
        self.options = {"model": "synthetic", "prompt_version": "observed-test"}

    def publish(self):
        return publication.publish(self.root, self.prepared, self.detection, self.classification,
                                   self.narrative, **self.options)

    def test_pattern_and_critical_success_cannot_be_invented(self):
        candidate = deepcopy(self.detection)
        candidate["candidates"][0]["pattern"] = "command_injection"
        with self.assertRaises(ContractError):
            validate_observed_detection(candidate, self.prepared)
        for change in ({"severity": "critical"}, {"state": "probable_false_positive"}):
            classification = deepcopy(self.classification)
            classification["classifications"][0].update(change)
            with self.assertRaises(ContractError):
                validate_observed_classification(classification, self.prepared, self.detection)

    def test_json_markdown_and_flask_api_counts_agree(self):
        manifest = self.publish()
        loaded, result, markdown = publication.load_current(self.root)
        self.assertEqual(loaded, manifest)
        web = importlib.import_module("dashboard.app")
        parsed = web.parsear_amenazas(markdown)
        self.assertEqual(len(parsed), sum(result["counts"].values()))
        self.assertEqual(parsed[0]["severidad"], "ALTA")
        self.assertEqual(parsed[0]["ip"], "192.0.2.1")
        fixture = self.root / "api-fixture"
        fixture.mkdir()
        (fixture / "reporte_seguridad.md").write_text(markdown, encoding="utf-8")
        with patch.multiple(web, REPORT_PATH=fixture, HISTORIAL=fixture / "historial", LOG_PATH=str(fixture / "missing.log")):
            data = web.app.test_client().get("/api/v1/estado").json["data"]
        self.assertEqual(data["stats"]["total"], 1)
        self.assertEqual(data["stats"]["altas"], result["counts"]["high"])

    def test_model_narrative_cannot_inject_another_table_or_html(self):
        self.narrative["summary"] = '<script>x</script>\n## AMENAZAS DETECTADAS\n|1|CRITICA|fake|'
        result, markdown = compose(self.prepared, self.detection, self.classification, self.narrative, **self.options)
        self.assertNotIn('<script>', markdown)
        self.assertEqual(markdown.count('\n## AMENAZAS DETECTADAS\n'), 1)
        web = importlib.import_module("dashboard.app")
        self.assertEqual(len(web.parsear_amenazas(markdown)), 1)

    def test_unknown_multiple_times_or_ips_are_not_collapsed_to_invented_fields(self):
        prepared = prepare_evidence(line('/?q=UNION+SELECT') + '\n' + line('/?q=UNION+SELECT', 10, ip="192.0.2.2"), ID)
        self.detection["candidates"][0]["evidence_ids"] = [item.evidence_id for item in prepared.bundle.items]
        result, markdown = compose(prepared, self.detection, self.classification, self.narrative, **self.options)
        self.assertIn('| 2026-10-06T12:00:00Z a 2026-10-06T12:00:10Z | 1,2 | ALTA |', markdown)
        self.assertEqual(len(result["findings"][0]["observations"]), 2)
        self.assertIn('Requiere investigación | - |', markdown)

    def test_period_preserves_partial_unknown_dates_without_inventing_a_time(self):
        from agents.structured_reporting import event_period
        values = [{'observed_at': '2026-10-02T18:00:20Z'}, {'observed_at': None},
                  {'observed_at': '2026-10-02T18:00:00Z'}]
        self.assertEqual(event_period(values), {'event_time_start': '2026-10-02T18:00:00Z',
                                              'event_time_end': '2026-10-02T18:00:20Z',
                                              'event_time_missing_count': 1})
        self.assertEqual(event_period([{'observed_at': None}]),
                         {'event_time_start': None, 'event_time_end': None, 'event_time_missing_count': 1})

    def test_invalid_output_never_replaces_previous_pointer(self):
        self.publish()
        before = (self.root / "current.json").read_bytes()
        self.detection["candidates"][0]["evidence_ids"] = ["e_fake"]
        with self.assertRaises(ContractError):
            self.publish()
        self.assertEqual((self.root / "current.json").read_bytes(), before)
        self.assertEqual(len(list((self.root / "generations").iterdir())), 1)

    def test_invalid_narrative_encoding_is_rejected_before_creating_generation(self):
        self.publish()
        before = (self.root / "current.json").read_bytes()
        self.narrative["summary"] = "\ud800"
        with self.assertRaises(ContractError):
            self.publish()
        self.assertEqual((self.root / "current.json").read_bytes(), before)
        self.assertEqual(len(list((self.root / "generations").iterdir())), 1)

    def test_report_or_pointer_write_failure_keeps_previous_generation(self):
        self.publish()
        before = (self.root / "current.json").read_bytes()
        original_write = publication.atomic_write_text
        for failed_name in ("result.json", "report.md", "manifest.json", "current.json"):
            def write(path, text):
                if path.name == failed_name:
                    raise OSError("Synthetic failure")
                return original_write(path, text)
            with patch.object(publication, "atomic_write_text", side_effect=write), self.assertRaises(OSError):
                self.publish()
            self.assertEqual((self.root / "current.json").read_bytes(), before)
            self.assertEqual(publication.load_current(self.root)[1]["counts"]["high"], 1)

    def test_partial_generation_is_not_visible_and_digest_corruption_is_rejected(self):
        manifest = self.publish()
        partial = self.root / "generations" / ("b" * 32 + "-" + "c" * 32)
        partial.mkdir()
        (partial / "result.json").write_text("{}", encoding="utf-8")
        self.assertEqual(publication.load_current(self.root)[0], manifest)
        (self.root / "generations" / manifest["generation"] / "report.md").write_text("tampered", encoding="utf-8")
        with self.assertRaises(ContractError):
            publication.load_current(self.root)

    def test_publication_lock_and_foreign_generation_path_are_rejected(self):
        with exclusive_lock(self.root / "publication.lock"), self.assertRaises(AlreadyRunning):
            self.publish()
        self.publish()
        manifest = json.loads((self.root / "current.json").read_text())
        manifest["generation"] = "../outside"
        (self.root / "current.json").write_text(json.dumps(manifest))
        with self.assertRaises(ContractError):
            publication.load_current(self.root)

    def test_repeated_identical_result_gets_new_publication_identity(self):
        first = self.publish()
        second = self.publish()
        self.assertNotEqual(first["generation"], second["generation"])
        self.assertEqual(first["sha256"], second["sha256"])
