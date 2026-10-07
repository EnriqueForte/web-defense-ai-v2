"""Labeled synthetic A-05 cases; no logs, configuration, provider or transport reads."""
from datetime import datetime, timedelta, timezone

CASES = ("mixed", "normal", "missing_body", "encoded", "login_window", "login_spread", "timezone_split", "incomplete")
CANONICAL_TARGETS = ('/?q=UNION+SELECT', '/?q=%3Cimg+onerror=confirm(1)%3E',
                     '/?file=../../etc/passwd', '/?host=x%3Bwhoami')
CANONICAL_PATTERNS = ("sql_injection", "xss", "path_traversal", "command_injection")


def fixture(case="mixed"):
    """Return text plus authored expectations; neither is derived from the detector."""
    if case not in CASES:
        raise ValueError("invalid_evaluation_case")
    required, optional = set(), set()
    requests = []
    if case == "mixed":
        targets = (*CANONICAL_TARGETS, *(['/login'] * 5), '/index.html')
        requests = [(target, "POST" if target == "/login" else "GET", index, "+0000")
                    for index, target in enumerate(targets)]
        required = {*CANONICAL_PATTERNS, "brute_force"}
    elif case == "normal":
        requests = [(target, "GET", index, "+0000") for index, target in enumerate(
            ('/index.html', '/health', '/assets/app.css', '/search?q=hello'))]
    elif case == "missing_body":
        requests = [('/vulnerabilities/exec/', 'POST', 0, '+0000'), ('/login.php', 'POST', 1, '+0000')]
    elif case == "encoded":
        requests = [(target, "GET", index, "+0000") for index, target in enumerate((
            '/?q=%55NION%20SELECT', '/?q=%253Cimg%2520onerror%253Dconfirm(1)%253E',
            '/?file=%252e%252e%252fetc/passwd', '/?host=x%253Bwhoami'))]
        required = set(CANONICAL_PATTERNS)
    elif case in {"login_window", "login_spread", "timezone_split"}:
        for index in range(5):
            seconds = index * (120 if case == "login_spread" else 10)
            offset = "+0900" if case == "timezone_split" and index % 2 else "+0000"
            requests.append(('/login', 'POST', seconds, offset))
        if case == "login_window":
            required = {"brute_force"}
    else:
        optional = {"other"}
        return {"case": case, "text": "synthetic uninterpretable request record", "required_patterns": [],
                "optional_patterns": sorted(optional), "expected_input_lines": 1}
    base = datetime(2026, 10, 6, 12, tzinfo=timezone.utc)
    lines = []
    for target, method, seconds, offset in requests:
        stamp = (base + timedelta(seconds=seconds)).strftime("%d/Oct/%Y:%H:%M:%S")
        lines.append(f'192.0.2.1 - - [{stamp} {offset}] "{method} {target} HTTP/1.1" 200 1')
    return {"case": case, "text": "\n".join(lines), "required_patterns": sorted(required),
            "optional_patterns": sorted(optional), "expected_input_lines": len(lines)}


def score_patterns(findings, case):
    expected = fixture(case)
    required = set(expected["required_patterns"])
    allowed = required | set(expected["optional_patterns"])
    actual = {finding["pattern"] for finding in findings}
    return {"case": case, "metrics_scope": "pattern_families_not_event_accuracy",
            "expected_patterns": sorted(required), "optional_patterns": sorted(allowed - required),
            "actual_patterns": sorted(actual), "missing_patterns": sorted(required - actual),
            "unexpected_patterns": sorted(actual - allowed),
            "pattern_recall": len(required & actual) / len(required) if required else None,
            "pattern_precision": len(allowed & actual) / len(actual) if actual else None,
            "pattern_expectations_met": not (required - actual or actual - allowed)}
