"""Test control-origin boundaries; prints no token, password, or raw page content."""
import json
import re
import time
from urllib.error import HTTPError
from urllib.request import Request
from lab.controller import OPENER, ORIGIN, STATE, atomic, utc


def request(path, body=None, headers=None):
    req = Request(ORIGIN + path, data=json.dumps(body).encode() if body is not None else None,
                  headers={"Content-Type": "application/json", **(headers or {})})
    try:
        response = OPENER.open(req, timeout=8)
    except HTTPError as error:
        response = error
    with response:
        return response.status, response.read(1024 * 1024).decode()


def check():
    status, page = request("/")
    assert status == 200
    token = re.search(r'name="umbral-control" content="([^"]+)"', page)[1]
    trusted = {"X-Umbral-Control": token}
    checks = []
    for name, headers in (("missing_token", {}), ("foreign_host", {**trusted, "Host": "untrusted.invalid"}),
                          ("target_origin_denied", {**trusted, "Origin": "http://127.0.0.1:4380"}),
                          ("arbitrary_origin_denied", {**trusted, "Origin": "https://example.invalid"})):
        status, _ = request("/api/status", headers=headers)
        assert status == 403, name
        checks.append({"name": name, "passed": True})
    status, _ = request("/api/run", {"scenario": "../../dvwa", "mode": "vulnerable"}, trusted)
    assert status == 400
    checks.append({"name": "unknown_scenario_rejected", "passed": True})
    status, value = request("/api/run", {"scenario": "brute", "mode": "corrected", "variant": 0, "kind": "attempt"}, trusted)
    assert status == 202
    run_id = json.loads(value)["id"]
    busy, _ = request("/api/run", {"scenario": "sqli", "mode": "vulnerable"}, trusted)
    assert busy == 400
    request("/api/cancel", {}, trusted)
    for _ in range(40):
        _, value = request("/api/runs/" + run_id, headers=trusted)
        record = json.loads(value)
        if record["status"] != "running":
            break
        time.sleep(0.4)
    assert record["status"] == "stopped", record["status"]
    checks.extend([{"name": "concurrent_run_rejected", "passed": True}, {"name": "cancel_preserves_partial_record", "passed": True}])
    result = {"checked_at": utc(), "checks": checks, "passed": len(checks), "total": len(checks), "stopped_run": run_id}
    atomic(STATE / "control-checks.json", result)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    check()
