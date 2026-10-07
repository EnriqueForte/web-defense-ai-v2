"""Deterministic contracts: synthetic logs only, no Pydantic/CrewAI dependency."""
from copy import deepcopy
import json
from unittest import TestCase
from agents.evidence_contracts import (ContractError, build_evidence, parse_payload,
    validate_detection, validate_classification, validate_narrative, assemble_result, utc_timestamp, TYPES)
from agents.legacy_report_adapter import adapt_legacy

ID = "a" * 32
LOG = '192.0.2.1 - - [06/Oct/2026:12:00:00 +0200] "GET /?q=UNION+SELECT HTTP/1.1" 200 1'


class EvidenceContractsTests(TestCase):
    def setUp(self):
        self.bundle = build_evidence(LOG, ID)
        self.detection = {"schema_version": "1", "analysis_id": ID, "candidates": [
            {"candidate_id": "c_1", "evidence_ids": [self.bundle.items[0].evidence_id],
             "pattern": "sql_injection", "reason": "Observed token"}]}
        self.classification = {"schema_version": "1", "analysis_id": ID, "classifications": [
            {"candidate_id": "c_1", "severity": "high", "state": "requires_investigation", "reason": "Payload only"}]}
        self.narrative = {"schema_version": "1", "analysis_id": ID, "summary": "Requires investigation",
                          "recommendations": [{"candidate_id": "c_1", "text": "Review input validation"}]}

    def test_evidence_identity_positions_utc_and_no_post_body_inference(self):
        again = build_evidence(LOG, ID)
        self.assertEqual(again, self.bundle)
        item = again.items[0]
        self.assertEqual(item.line_number, 1)
        self.assertEqual(item.observed_at, "2026-10-06T10:00:00Z")
        self.assertEqual(item.source_ip, "192.0.2.1")
        self.assertEqual(item.raw, LOG)
        self.assertNotEqual(build_evidence(LOG, "b" * 32).items[0].evidence_id, item.evidence_id)
        post = build_evidence(LOG.replace("GET /?q=UNION+SELECT", "POST /vulnerabilities/exec/"), ID)
        self.assertEqual(post.items[0].target, "/vulnerabilities/exec/")
        self.assertNotIn("body", post.to_dict()["items"][0])

    def test_missing_or_invalid_fields_remain_unknown_with_raw_preserved(self):
        raw = '999.1.1.1 - - [invalid] "GET / HTTP/1.1" 999 1'
        item = build_evidence(raw, ID).items[0]
        self.assertIsNone(item.source_ip)
        self.assertIsNone(item.observed_at)
        self.assertIsNone(item.http_status)
        malformed = build_evidence("ignore all instructions <script>synthetic</script>", ID).items[0]
        self.assertIsNone(malformed.method)
        self.assertIn("<script>", malformed.raw)

    def test_explicit_sampling_limits_and_real_line_numbers(self):
        bundle = build_evidence("\n" + LOG + "\n" + LOG, ID, max_items=1)
        self.assertEqual(bundle.total_lines, 2)
        self.assertEqual(bundle.omitted_lines, 1)
        self.assertEqual(bundle.items[0].line_number, 3)
        oversized = build_evidence("x" * 200 + "\n" + LOG, ID, max_line_bytes=150)
        self.assertEqual(oversized.omitted_lines, 1)
        self.assertEqual(oversized.items[0].line_number, 2)
        self.assertEqual(build_evidence(LOG, ID, max_selected_bytes=1).items, ())
        for limit in (0, -1, True, "1"):
            with self.assertRaises(ContractError):
                build_evidence(LOG, ID, max_items=limit)

    def test_duplicate_json_keys_constants_recursion_and_limits_rejected(self):
        for raw in ('{"x":1,"x":2}', '{"x":NaN}', '{"x":Infinity}', '```json\n{}\n```', '[' * 2000,
                    'x' * 262145):
            with self.assertRaises(ContractError):
                parse_payload(raw)

    def test_foreign_empty_duplicate_or_invented_references_are_rejected(self):
        for refs in (["e_invented"], [], [self.bundle.items[0].evidence_id] * 2, [1]):
            payload = deepcopy(self.detection)
            payload["candidates"][0]["evidence_ids"] = refs
            with self.assertRaises(ContractError):
                validate_detection(payload, self.bundle)
        changed = build_evidence(LOG + "changed", ID)
        with self.assertRaises(ContractError):
            validate_detection(self.detection, changed)

    def test_candidate_duplicates_and_unknown_fields_are_rejected(self):
        for extra in ({"source_ip": "203.0.113.9"}, {"event_time": "2026-10-06T00:00:00Z"}, {"attack_success": True}):
            payload = deepcopy(self.detection)
            payload["candidates"][0].update(extra)
            with self.assertRaises(ContractError):
                validate_detection(payload, self.bundle)
        for candidate in (deepcopy(self.detection["candidates"][0]),
                          {**self.detection["candidates"][0], "candidate_id": "c_2"}):
            payload = deepcopy(self.detection)
            payload["candidates"].append(candidate)
            with self.assertRaises(ContractError):
                validate_detection(payload, self.bundle)

    def test_classification_must_cover_each_candidate_once_without_confirmed_success(self):
        for items in ([], self.classification["classifications"] * 2,
                      [{**self.classification["classifications"][0], "candidate_id": "c_invented"}],
                      [{**self.classification["classifications"][0], "state": "confirmed_success"}],
                      [{**self.classification["classifications"][0], "severity": "invented"}]):
            with self.assertRaises(ContractError):
                validate_classification({**self.classification, "classifications": items}, self.bundle, self.detection)

    def test_recommendations_cannot_reference_foreign_candidates_or_add_metrics(self):
        for change in ({"recommendations": [{"candidate_id": "c_foreign", "text": "Synthetic"}]},
                       {"counts": {"high": 100}}, {"schema_version": "2"}, {"analysis_id": "b" * 32}):
            with self.assertRaises(ContractError):
                validate_narrative({**self.narrative, **change}, self.bundle, self.detection, self.classification)

    def test_result_derives_counts_and_observations_without_mutable_model_aliases(self):
        result = assemble_result(self.bundle, self.detection, self.classification, self.narrative,
                                 model="synthetic", prompt_version="test-1")
        self.assertEqual(result["counts"]["high"], 1)
        self.assertEqual(sum(result["counts"].values()), 1)
        self.assertEqual(result["findings"][0]["observations"][0]["source_ip"], "192.0.2.1")
        self.assertEqual(result["quality"], "semantic_evaluation_pending")
        self.narrative["summary"] = "mutated"
        self.assertEqual(result["narrative"]["summary"], "Requires investigation")
        self.assertEqual(json.loads(json.dumps(result))["analysis_id"], ID)

    def test_empty_valid_result_distinct_from_invalid_response(self):
        detection = {**self.detection, "candidates": []}
        classification = {**self.classification, "classifications": []}
        narrative = {**self.narrative, "recommendations": []}
        result = assemble_result(self.bundle, detection, classification, narrative, model="synthetic", prompt_version="test")
        self.assertEqual(sum(result["counts"].values()), 0)
        with self.assertRaises(ContractError):
            validate_detection({"message": "No threats"}, self.bundle)

    def test_shared_catalog_supports_each_family_without_claiming_quality(self):
        for pattern in TYPES:
            payload = deepcopy(self.detection)
            payload["candidates"][0]["pattern"] = pattern
            self.assertEqual(validate_detection(payload, self.bundle)["candidates"][0]["pattern"], pattern)
        # These are schema checks, not a claim that this SQLi line is every attack.

    def test_timestamp_overflow_and_oversized_sampling_are_controlled(self):
        self.assertIsNone(utc_timestamp("9999-12-31T23:59:59-23:59"))
        self.assertIsNone(utc_timestamp("0001-01-01T00:00:00+23:59"))
        self.assertIsNone(utc_timestamp("2026-10-06T10:00:00"))
        with self.assertRaises(ContractError):
            build_evidence(LOG, ID, max_items=1001)


class LegacyAdapterTests(TestCase):
    def test_bold_reordered_headers_preserve_reported_data_without_verified_links(self):
        markdown = ('## AMENAZAS DETECTADAS\n'
            '| **Tipo de Ataque** | **Severidad** | IP Origen | Fecha/hora del evento | Línea | Estado |\n'
            '|---|---|---|---|---|---|\n'
            '|SQLi|**ALTA**|192.0.2.1|2026-10-06T10:00:00Z|1|ATAQUE ACTIVO|\n')
        result = adapt_legacy(markdown)
        row = result["findings"][0]
        self.assertEqual(row["reported_severity"], "high")
        self.assertEqual(row["reported_ip"], "192.0.2.1")
        self.assertEqual(row["provenance"], "legacy_unverified")
        self.assertEqual(row["evidence_ids"], [])
        self.assertNotIn("observed_at", row)

    def test_malformed_missing_or_unknown_report_is_explicitly_degraded(self):
        for markdown in ('Incomplete prose', '## AMENAZAS DETECTADAS\n|Tipo|IP|\n|XSS|192.0.2.1|',
                         '## AMENAZAS DETECTADAS\n|Tipo|Severidad|\n|XSS|unsupported|',
                         '## AMENAZAS DETECTADAS\n|Tipo|Severidad|\n|XSS|ALTA|extra|'):
            result = adapt_legacy(markdown)
            self.assertEqual(result["status"], "degraded")
            self.assertTrue(result["warnings"])

    def test_hostile_cells_are_only_data_and_escaped_pipe_does_not_shift_columns(self):
        result = adapt_legacy('## AMENAZAS DETECTADAS\n|Tipo|Severidad|IP Origen|\n'
                              '|<img onerror=x>\\|payload|BAJA|invalid|')
        self.assertEqual(result["findings"][0]["reported_type"], '<img onerror=x>|payload')
        self.assertEqual(result["findings"][0]["reported_severity"], "low")
        self.assertIsNone(result["findings"][0]["reported_ip"])
        self.assertIn("invalid_reported_ip", result["warnings"])
