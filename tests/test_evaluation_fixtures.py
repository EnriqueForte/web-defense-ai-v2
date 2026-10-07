"""Authored A-05 expectations include negatives, windows, encoding and unknown fields."""
from unittest import TestCase
from agents.evaluation_fixtures import CASES, fixture, score_patterns
from agents.evidence_preparation import prepare_evidence


class EvaluationFixturesTests(TestCase):
    def test_all_labeled_cases_match_preparation_criteria_without_claiming_semantic_quality(self):
        for case in CASES:
            with self.subTest(case=case):
                source = fixture(case)
                prepared = prepare_evidence(source["text"], "a" * 32, config={})
                observed = {pattern for patterns in prepared.indicators.values() for pattern in patterns}
                self.assertEqual(observed, set(source["required_patterns"]))
                self.assertEqual(prepared.bundle.total_lines, source["expected_input_lines"])
                if case == "incomplete":
                    self.assertIsNone(prepared.bundle.items[0].source_ip)
                    self.assertIsNone(prepared.bundle.items[0].observed_at)

    def test_default_mixed_fixture_preserves_previous_input_bytes(self):
        targets = ['/?q=UNION+SELECT', '/?q=%3Cimg+onerror=confirm(1)%3E',
                   '/?file=../../etc/passwd', '/?host=x%3Bwhoami', *(['/login'] * 5), '/index.html']
        original = "\n".join(f'192.0.2.1 - - [06/Oct/2026:12:00:{i:02d} +0000] '
            f'"{"POST" if target == "/login" else "GET"} {target} HTTP/1.1" 200 1' for i, target in enumerate(targets))
        self.assertEqual(fixture()["text"], original)

    def test_negative_case_needs_no_findings_and_does_not_invent_precision(self):
        score = score_patterns([], "normal")
        self.assertTrue(score["pattern_expectations_met"])
        self.assertIsNone(score["pattern_recall"])
        self.assertIsNone(score["pattern_precision"])
        rejected = score_patterns([{"pattern": "other"}], "normal")
        self.assertFalse(rejected["pattern_expectations_met"])
        self.assertEqual(rejected["unexpected_patterns"], ["other"])

    def test_ambiguous_case_allows_optional_other_without_requiring_invented_finding(self):
        self.assertTrue(score_patterns([], "incomplete")["pattern_expectations_met"])
        self.assertTrue(score_patterns([{"pattern": "other"}], "incomplete")["pattern_expectations_met"])
        self.assertFalse(score_patterns([{"pattern": "sql_injection"}], "incomplete")["pattern_expectations_met"])

    def test_missing_canonical_pattern_is_explicit_and_unknown_case_is_rejected(self):
        score = score_patterns([{"pattern": "xss"}], "encoded")
        self.assertFalse(score["pattern_expectations_met"])
        self.assertIn("sql_injection", score["missing_patterns"])
        with self.assertRaises(ValueError):
            fixture("not-a-case")
