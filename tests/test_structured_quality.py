"""No finding without support; ambiguous evidence stays investigable; no provider."""
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from agents.evidence_contracts import ContractError
from agents.evidence_preparation import prepare_evidence, validate_observed_detection, validate_observed_classification
from dashboard.services.structured_publication import publish
from agents.structured_reporting import compose, no_findings_narrative, render_markdown

ID = "a" * 32


def line(target):
    return f'192.0.2.1 - - [06/Oct/2026:12:00:00 +0000] "GET {target} HTTP/1.1" 200 1'


def detection(prepared, refs=None):
    return {"schema_version": "1", "analysis_id": ID, "candidates": [{"candidate_id": "c_1", "pattern": "other",
        "reason": "Review uncertainty", "evidence_ids": refs or [prepared.bundle.items[0].evidence_id]}]}


def classification(state="requires_investigation"):
    return {"schema_version": "1", "analysis_id": ID, "classifications": [{"candidate_id": "c_1",
        "severity": "unknown", "state": state, "reason": "Uncertain evidence"}]}


class StructuredQualityTests(TestCase):
    def test_normal_requests_cannot_be_promoted_to_other(self):
        for target in ("/index.html", "/health", "/index.html?message=hello", "/login"):
            prepared = prepare_evidence(line(target), ID)
            self.assertEqual(prepared.context()["uncertainty_evidence_ids"], [])
            with self.assertRaisesRegex(ContractError, "other_without_observation"):
                validate_observed_detection(detection(prepared), prepared)

    def test_uninterpretable_evidence_can_be_investigated_without_claiming_observed_attack(self):
        prepared = prepare_evidence("uninterpretable synthetic request record", ID)
        payload = detection(prepared)
        self.assertEqual(prepared.context()["uncertainty_evidence_ids"], payload["candidates"][0]["evidence_ids"])
        validate_observed_classification(classification(), prepared, payload)
        validate_observed_classification(classification("probable_false_positive"), prepared, payload)
        with self.assertRaisesRegex(ContractError, "unobserved_other_state"):
            validate_observed_classification(classification("observed_indicator"), prepared, payload)

    def test_other_on_observed_indicator_preserves_uncertainty_but_cannot_add_unrelated_normal_request(self):
        prepared = prepare_evidence(line('/?q=UNION+SELECT') + "\n" + line('/index.html'), ID)
        validate_observed_classification(classification(), prepared, detection(prepared))
        with self.assertRaisesRegex(ContractError, "other_without_observation"):
            validate_observed_detection(detection(prepared, [item.evidence_id for item in prepared.bundle.items]), prepared)

    def test_false_positive_cannot_replace_a_verified_publication(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            prepared = prepare_evidence(line('/?q=UNION+SELECT'), ID)
            payload = detection(prepared)
            payload["candidates"][0]["pattern"] = "sql_injection"
            narrative = {"schema_version": "1", "analysis_id": ID, "summary": "Synthetic scope",
                         "recommendations": []}
            publish(root, prepared, payload, classification(), narrative, model="offline", prompt_version="test")
            previous = (root / "current.json").read_bytes()
            normal = prepare_evidence(line('/index.html'), ID)
            with self.assertRaisesRegex(ContractError, "other_without_observation"):
                publish(root, normal, detection(normal), classification(), narrative, model="offline", prompt_version="test")
            self.assertEqual((root / "current.json").read_bytes(), previous)

    def test_no_findings_summary_uses_scope_instead_of_useless_model_text(self):
        prepared = prepare_evidence(line('/index.html'), ID)
        result, markdown = compose(prepared,
            {"schema_version": "1", "analysis_id": ID, "candidates": []},
            {"schema_version": "1", "analysis_id": ID, "classifications": []},
            {"schema_version": "1", "analysis_id": ID, "summary": "1", "recommendations": []},
            model="offline", prompt_version="test")
        self.assertEqual(result["narrative_source"], "python_scope")
        self.assertIn("1 línea seleccionada de 1", result["narrative"]["summary"])
        self.assertEqual(result["report_format_version"], "structured-report-4")
        self.assertIn("no demuestra tráfico benigno", markdown)
        self.assertIn(result["narrative"]["summary"], markdown)
        self.assertEqual(sum(result["counts"].values()), 0)

    def test_incomplete_or_omitted_evidence_cannot_be_presented_as_safe(self):
        prepared = prepare_evidence("uninterpretable synthetic request\n" + line('/index.html'), ID,
                                    config={"MAX_LINEAS_LOG": "2"}, max_items=1)
        # Incomplete input remains in scope even when selection may omit it.
        result, _ = compose(prepared,
            {"schema_version": "1", "analysis_id": ID, "candidates": []},
            {"schema_version": "1", "analysis_id": ID, "classifications": []},
            {"schema_version": "1", "analysis_id": ID, "summary": "All safe", "recommendations": []},
            model="offline", prompt_version="test")
        self.assertIn("se omitieron 1", result["narrative"]["summary"])
        incomplete = prepare_evidence("uninterpretable synthetic request", ID)
        result, markdown = compose(incomplete,
            {"schema_version": "1", "analysis_id": ID, "candidates": []},
            {"schema_version": "1", "analysis_id": ID, "classifications": []},
            {"schema_version": "1", "analysis_id": ID, "summary": "All safe", "recommendations": []},
            model="offline", prompt_version="test")
        self.assertIn("1 registro cuya petición", markdown)
        self.assertIn("no permite descartar", markdown)
        self.assertNotIn("All safe", markdown)

    def test_deterministic_summary_does_not_bypass_invalid_narrative_contract(self):
        prepared = prepare_evidence(line('/index.html'), ID)
        with self.assertRaises(ContractError):
            compose(prepared,
                {"schema_version": "1", "analysis_id": ID, "candidates": []},
                {"schema_version": "1", "analysis_id": ID, "classifications": []},
                {"schema_version": "1", "analysis_id": ID, "summary": "", "recommendations": []},
                model="offline", prompt_version="test")

    def test_empty_detection_with_selected_indicators_cannot_replace_current_report(self):
        prepared = prepare_evidence(line('/?q=UNION+SELECT'), ID)
        empty = {"schema_version": "1", "analysis_id": ID, "candidates": []}
        empty_classification = {"schema_version": "1", "analysis_id": ID, "classifications": []}
        narrative = {"schema_version": "1", "analysis_id": ID, "summary": "Nothing suspicious", "recommendations": []}
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            normal = prepare_evidence(line('/index.html'), ID)
            publish(root, normal, empty, empty_classification, narrative, model="offline", prompt_version="test")
            previous = (root / "current.json").read_bytes()
            previous_generations = sorted(p.name for p in (root / "generations").iterdir())
            with self.assertRaisesRegex(ContractError, "^empty_detection_with_observed_indicators$"):
                publish(root, prepared, empty, empty_classification, narrative, model="offline", prompt_version="test")
            self.assertEqual((root / "current.json").read_bytes(), previous)
            self.assertEqual(sorted(p.name for p in (root / "generations").iterdir()), previous_generations)

    def test_empty_detection_rejected_for_each_selected_indicator_family(self):
        inputs = [line(target) for target in ('/?q=UNION+SELECT', '/?q=%3Csvg+onload=confirm(1)%3E',
                                               '/?file=../etc/passwd', '/?host=x%3Bwhoami')]
        inputs.append('\n'.join(line('/vulnerabilities/brute/?username=test&password=x') for _ in range(5)))
        for text in inputs:
            prepared = prepare_evidence(text, ID)
            with self.subTest(families={p for patterns in prepared.indicators.values() for p in patterns}):
                with self.assertRaisesRegex(ContractError, "^empty_detection_with_observed_indicators$"):
                    validate_observed_detection({"schema_version": "1", "analysis_id": ID, "candidates": []}, prepared)

    def test_indicator_can_be_explicitly_classified_as_probable_false_positive(self):
        prepared = prepare_evidence(line('/?q=UNION+SELECT'), ID)
        candidate = detection(prepared)
        candidate['candidates'][0]['pattern'] = 'sql_injection'
        classified = classification('probable_false_positive')
        classified['classifications'][0]['severity'] = 'low'
        result, _ = compose(prepared, candidate, classified,
            {"schema_version": "1", "analysis_id": ID, "summary": "Review possible false positive", "recommendations": []},
            model="offline", prompt_version="test")
        self.assertEqual(result['findings'][0]['state'], 'probable_false_positive')
        self.assertEqual(result['findings'][0]['severity'], 'low')

    def test_indicators_outside_selected_window_do_not_force_invented_candidates(self):
        prepared = prepare_evidence(line('/?q=UNION+SELECT')+'\n'+line('/index.html'), ID,
                                    config={'MAX_LINEAS_LOG':'1'})
        result, _ = compose(prepared,
            {"schema_version": "1", "analysis_id": ID, "candidates": []},
            {"schema_version": "1", "analysis_id": ID, "classifications": []},
            {"schema_version": "1", "analysis_id": ID, "summary": "Review scope", "recommendations": []},
            model="offline", prompt_version="test")
        self.assertEqual(result['findings'], [])
        self.assertIn('se omitieron 1', result['narrative']['summary'])

    def test_historic_empty_indicator_report_keeps_its_omission_warning_readable(self):
        # Existing receipts/publications are immutable data, not newly validated results.
        prepared = prepare_evidence(line('/?q=UNION+SELECT'), ID)
        normal = prepare_evidence(line('/index.html'), ID)
        result, _ = compose(normal,
            {"schema_version": "1", "analysis_id": ID, "candidates": []},
            {"schema_version": "1", "analysis_id": ID, "classifications": []},
            {"schema_version": "1", "analysis_id": ID, "summary": "Review scope", "recommendations": []},
            model="offline", prompt_version="test")
        result['narrative'] = no_findings_narrative(prepared.bundle, preparation=prepared)
        self.assertIn('revisar posibles omisiones', render_markdown(result))
