"""Negative checks against only the explicitly named Puerto Umbral containers."""
import hashlib
import json
import time
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request

from lab.controller import OPENER, PROJECT, STATE, atomic, command, inspect_boundary, owned_containers, reset, utc


def get(port, path):
    try:
        response = OPENER.open(f"http://127.0.0.1:{port}" + path, timeout=5)
    except HTTPError as error:
        response = error
    with response:
        return response.status, response.read(65536).decode("utf-8", "replace")


def check_boundary():
    boundary = inspect_boundary()
    original = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in (STATE / "runs").glob("*/access*.log")}
    before = owned_containers(require_all=True)
    checks = []

    def record(name, passed, detail=None):
        checks.append({"name": name, "passed": bool(passed), "detail": detail})
        print(json.dumps(checks[-1]), flush=True)
        if not passed:
            raise AssertionError(name)

    probe = """import errno,json,os,pathlib,socket
s=socket.socket();s.settimeout(1)
try:
 s.connect(('192.0.2.1',9));network=False
except OSError as e:
 network=e.errno in (errno.ENETUNREACH,errno.EHOSTUNREACH,errno.EPERM)
finally:s.close()
try:
 pathlib.Path('/srv/umbral-write-test').write_text('fixture');readonly=False
except OSError:readonly=True
print(json.dumps({'uid':os.getuid(),'interfaces':sorted(p.name for p in pathlib.Path('/sys/class/net').iterdir()),'network_denied':network,'root_write_denied':readonly}))
"""
    result = json.loads(command(["docker", "exec", PROJECT + "-command-vulnerable", "python", "-B", "-c", probe]).stdout)
    record("actual_nonroot_no_ip_network_readonly", result == {"uid": 10001, "interfaces": ["lo"], "network_denied": True, "root_write_denied": True}, result)

    for mode, port in (("vulnerable", 4380), ("corrected", 4382)):
        reset("traversal", mode)
        status, _ = get(port, "/archivo?" + urlencode({"documento": "/etc/passwd"}))
        record("traversal_hard_perimeter_" + mode, status == 403, status)

    reset("command", "vulnerable")
    start = time.monotonic()
    status, body = get(4380, "/mantenimiento?" + urlencode({"equipo": "baliza-07; sleep 5"}))
    elapsed = time.monotonic() - start
    record("command_timeout_kills_group", status == 408 and elapsed < 3.5 and json.loads(body)["timed_out"], {"status": status, "elapsed": round(elapsed, 3)})
    processes = command(["docker", "top", PROJECT + "-command-vulnerable", "-eo", "args"]).stdout
    record("no_sleep_process_remains", "sleep 5" not in processes)

    reset("sqli", "corrected")
    start = time.monotonic()
    status, _ = get(4382, "/mercancias?q=Asteria")
    rapid, _ = get(4382, "/mercancias?q=Asteria")
    record("server_rate_limit", status == 200 and rapid == 429, {"first": status, "rapid": rapid})
    for _ in range(19):
        time.sleep(0.55)
        status, _ = get(4382, "/mercancias?q=Asteria")
        if status != 200:
            raise AssertionError("unexpected_quota_status:" + str(status))
    time.sleep(0.55)
    status, _ = get(4382, "/mercancias?q=Asteria")
    record("server_twenty_request_limit", status == 429, status)
    print("Checking the real 30 second execution expiry; no extra attacks are sent while waiting.", flush=True)
    time.sleep(max(0, 30.4 - (time.monotonic() - start)))
    status, _ = get(4382, "/mercancias?q=Asteria")
    record("server_thirty_second_expiry", status == 410, status)

    reset("sqli", "vulnerable")
    after = owned_containers(require_all=True)
    untouched = [s for s in before if s not in {"sqli-vulnerable", "sqli-corrected", "command-vulnerable", "traversal-vulnerable", "traversal-corrected"}]
    record("other_scenarios_not_restarted", all(before[s]["State"]["StartedAt"] == after[s]["State"]["StartedAt"] for s in untouched), untouched)
    record("previous_access_snapshots_unchanged", all(p.exists() and hashlib.sha256(p.read_bytes()).hexdigest() == digest for p, digest in original.items()), len(original))
    result = {"checked_at": utc(), "kind": "local_isolation_and_limits", "checks": checks, "boundary": boundary}
    atomic(STATE / "isolation.json", result)
    return {"passed": len(checks), "total": len(checks), "evidence": str(STATE / "isolation.json")}
