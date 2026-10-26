"""Trusted loopback controller; target input is never executed on the host."""
from datetime import datetime, timezone
from functools import lru_cache
import hashlib
import html
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import re
import secrets
import shutil
import socket
import subprocess
import threading
import time
from urllib.error import HTTPError
from urllib.parse import urlencode, urlsplit
from urllib.request import Request, ProxyHandler, build_opener

from lab.catalog import MODES, PASSWORD, SCENARIOS, SEED, VERSION, cases

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / ".local-state" / "f2"
PROJECT = "puerto-umbral-f2"
SERVICES = [f"{scenario}-{mode}" for scenario in SCENARIOS for mode in MODES] + [f"gateway-{mode}" for mode in MODES]
PORTS = {"vulnerable": 4380, "corrected": 4382}
ORIGIN = "http://127.0.0.1:4381"
OPENER = build_opener(ProxyHandler({}))


class ProcessLock:
    """One CLI/controller owner; OS releases the lock after an interrupted process."""
    def __enter__(self):
        STATE.mkdir(parents=True, exist_ok=True)
        self.handle = (STATE / "controller.lock").open("a+b")
        self.handle.seek(0, 2)
        if self.handle.tell() == 0:
            self.handle.write(b"0")
            self.handle.flush()
        self.handle.seek(0)
        try:
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(self.handle.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(self.handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            self.handle.close()
            raise RuntimeError("another_controller_is_active") from None
        return self

    def __exit__(self, *_):
        self.handle.close()


def utc():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def atomic(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + "." + secrets.token_hex(6) + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(temporary, path)


def command(args, timeout=30, *, check=True):
    result = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout)
    if check and result.returncode:
        # Docker operations use only fixed arguments and never contain credentials.
        raise RuntimeError("docker_operation_failed: " + result.stderr[-1500:])
    return result


@lru_cache(maxsize=1)
def compose_command():
    """Support the installed Compose CLI; never install or switch a Docker context."""
    docker = shutil.which("docker")
    if not docker:
        raise RuntimeError("docker_cli_missing")
    if command([docker, "compose", "version"], timeout=10, check=False).returncode == 0:
        prefix = [docker, "compose"]
    else:
        standalone = shutil.which("docker-compose")
        if not standalone or command([standalone, "version"], timeout=10, check=False).returncode:
            raise RuntimeError("compose_cli_missing")
        prefix = [standalone]
    help_text = command([*prefix, "--help"], timeout=10).stdout
    if "--env-file" not in help_text or "--project-name" not in help_text:
        raise RuntimeError("compose_options_not_supported")
    return [*prefix, "--env-file", str(ROOT / "lab/empty.env"), "--file", str(ROOT / "lab/compose.yaml"), "--project-name", PROJECT]


def preflight():
    command(compose_command() + ["config", "--quiet"])
    found = owned_containers()
    if any(info["State"]["Running"] for info in found.values()):
        raise RuntimeError("puerto_umbral_already_running_stop_its_own_session_first")
    return {"project": PROJECT, "ready_to_prepare": True, "existing_stopped": list(found)}


def owned_containers(*, require_all=False):
    found = {}
    for service in SERVICES:
        name = PROJECT + "-" + service
        result = command(["docker", "inspect", name], check=False)
        if result.returncode:
            if require_all:
                raise RuntimeError("missing_container:" + service)
            continue
        info = json.loads(result.stdout)[0]
        labels = info["Config"].get("Labels") or {}
        if labels.get("org.puerto-umbral.lab") != "f2-v1" or labels.get("com.docker.compose.project") != PROJECT:
            raise RuntimeError("foreign_container_collision:" + name)
        found[service] = info
    return found


def inspect_boundary():
    containers = owned_containers(require_all=True)
    images = json.loads((STATE / "images.json").read_text(encoding="utf-8"))
    summary = []
    for service, info in containers.items():
        cfg, host = info["Config"], info["HostConfig"]
        gateway = service.startswith("gateway-")
        expected_image = images["apache" if gateway else "target"]
        failures = []
        if info["Image"] != expected_image:
            failures.append("image_changed")
        if not info["State"]["Running"] or cfg.get("User") != "10001:10001":
            failures.append("state_or_user")
        if not host.get("ReadonlyRootfs") or host.get("Privileged") or host.get("CapAdd"):
            failures.append("privilege_or_rootfs")
        if "ALL" not in (host.get("CapDrop") or []) or not any("no-new-privileges" in x for x in (host.get("SecurityOpt") or [])):
            failures.append("capability_boundary")
        if host.get("PidMode") == "host" or host.get("IpcMode") == "host" or host.get("Devices"):
            failures.append("host_namespace_or_device")
        if not 0 < host.get("Memory", 0) <= 128 * 1024 * 1024 or not 0 < host.get("PidsLimit", 0) <= 96:
            failures.append("resource_limits")
        if not 0 < host.get("NanoCpus", 0) <= 500000000:
            failures.append("cpu_limit")
        mounts = info.get("Mounts") or []
        if gateway:
            mode = service.split("-", 1)[1]
            expected_volumes = {f"{PROJECT}-{s}-{mode}" for s in SCENARIOS}
            if {m.get("Name") for m in mounts} != expected_volumes or any(m["Type"] != "volume" or m["RW"] for m in mounts):
                failures.append("gateway_mounts")
            bindings = host.get("PortBindings") or {}
            if bindings != {"8080/tcp": [{"HostIp": "127.0.0.1", "HostPort": str(PORTS[mode])}]}:
                failures.append("gateway_bindings")
            if info["NetworkSettings"].get("Ports", {}).get("8080/tcp") != bindings.get("8080/tcp"):
                failures.append("gateway_effective_bindings")
            if set(info["NetworkSettings"]["Networks"]) != {PROJECT + "-front"}:
                failures.append("gateway_network")
        else:
            if host.get("NetworkMode") != "none" or host.get("PortBindings"):
                failures.append("target_network")
            if len(mounts) != 1 or mounts[0]["Type"] != "volume" or mounts[0].get("Name") != PROJECT + "-" + service or mounts[0]["Destination"] != "/run/umbral":
                failures.append("target_mount")
        if failures:
            raise RuntimeError("boundary_rejected:" + service + ":" + ",".join(failures))
        summary.append({"service": service, "id": info["Id"], "image": info["Image"], "running": True,
                        "network": host["NetworkMode"], "root_readonly": True, "user": cfg["User"]})
    network = json.loads(command(["docker", "network", "inspect", PROJECT + "-front"]).stdout)[0]
    options = network.get("Options") or {}
    if options.get("com.docker.network.bridge.enable_ip_masquerade") != "false" or options.get("com.docker.network.bridge.enable_icc") != "false":
        raise RuntimeError("front_network_options_rejected")
    if set(network.get("Containers", {})) != {containers["gateway-" + m]["Id"] for m in MODES}:
        raise RuntimeError("front_network_not_exclusive")
    return {"checked_at": utc(), "valid": True, "containers": summary, "targets_network_none": True,
            "gateway_masquerade": False, "gateway_intercontainer_connectivity": False}


def wait_target(service):
    # This command is fixed. No payload or user input is supplied to docker exec.
    program = "import socket; s=socket.socket(socket.AF_UNIX); s.settimeout(2); s.connect('/run/umbral/backend.sock'); s.sendall(b'GET /health HTTP/1.0\\r\\nHost: localhost\\r\\n\\r\\n'); assert b'200' in s.recv(1024).split(b'\\r\\n')[0]"
    for _ in range(20):
        result = command(["docker", "exec", PROJECT + "-" + service, "python", "-B", "-c", program], timeout=5, check=False)
        if result.returncode == 0:
            return
        time.sleep(0.15)
    raise RuntimeError("target_not_ready:" + service)


def prepare():
    found = owned_containers()  # Reject unrelated name collisions before build/up.
    for service in found:
        if service.startswith("gateway-"):
            logs = command(["docker", "logs", "--timestamps=false", PROJECT + "-" + service])
            atomic(STATE / "setup-history" / (service + "-" + secrets.token_hex(6) + ".json"),
                   {"captured_at": utc(), "stdout": logs.stdout, "stderr": logs.stderr})
    command(compose_command() + ["config", "--quiet"])
    command(compose_command() + ["build"], timeout=240)
    images = {}
    for kind in ("target", "apache"):
        data = json.loads(command(["docker", "image", "inspect", f"puerto-umbral-{kind}:f2-1"]).stdout)[0]
        images[kind] = data["Id"]
    atomic(STATE / "images.json", images)
    try:
        command(compose_command() + ["up", "--detach", "--no-build"], timeout=90)
        for service in SERVICES:
            if not service.startswith("gateway-"):
                wait_target(service)
        result = inspect_boundary()
        atomic(STATE / "boundary.json", result)
        return result
    except BaseException:
        stop()
        raise


def stop():
    found = owned_containers()
    if found:
        command(compose_command() + ["stop", "--timeout", "3", *found], timeout=60)
    return {"stopped": list(found), "evidence_preserved": True, "volumes_removed": False}


def reset(scenario, mode):
    if scenario not in SCENARIOS or mode not in MODES:
        raise ValueError("invalid_selection")
    inspect_boundary()
    service = scenario + "-" + mode
    command(compose_command() + ["restart", "--no-deps", "--timeout", "2", service], timeout=20)
    wait_target(service)


class Runtime:
    def __init__(self):
        self.lock = threading.Lock()
        self.data_lock = threading.RLock()
        self.cancel = threading.Event()
        self.current = None
        self.records = {}
        self.token = secrets.token_urlsafe(32)  # Memory only; never shared with targets.
        self.boundary = inspect_boundary()
        self.thread = None
        for path in sorted((STATE / "runs").glob("*/receipt.json")):
            try:
                record = json.loads(path.read_text(encoding="utf-8"))
                if re.fullmatch(r"[a-f0-9]{32}", record.get("id", "")):
                    if record.get("status") == "running":
                        record["status"] = "interrupted"
                        record["error"] = "controller_restarted"
                    self.records[record["id"]] = record
            except (OSError, ValueError):
                continue

    def save(self, record):
        with self.data_lock:
            self.records[record["id"]] = record
            atomic(STATE / "runs" / record["id"] / "receipt.json", record)

    def launch(self, selection):
        scenario, mode = selection.get("scenario"), selection.get("mode")
        variant, kind = selection.get("variant", 0), selection.get("kind", "attempt")
        if scenario not in SCENARIOS or mode not in MODES or type(variant) is not int or variant not in range(3) or kind not in {"attempt", "benign"}:
            raise ValueError("invalid_selection")
        size = sum(p.stat().st_size for p in STATE.rglob("*") if p.is_file())
        if size > 128 * 1024 * 1024 or shutil.disk_usage(STATE).free < 100 * 1024 * 1024:
            raise RuntimeError("evidence_storage_limit")
        if not self.lock.acquire(blocking=False):
            raise ValueError("execution_busy")
        self.cancel.clear()
        record = {"id": secrets.token_hex(16), "schema_version": 1, "version": VERSION, "seed": SEED,
                  "scenario": scenario, "mode": mode, "variant": variant, "kind": kind,
                  "provenance": "local_http_observation", "status": "running", "started_at": utc(),
                  "v2_consulted": False, "requests": [], "functional_effect_confirmed": False,
                  "browser_execution_confirmed": False, "nonce": secrets.token_hex(16)}
        self.current = record["id"]
        self.save(record)
        self.thread = threading.Thread(target=self.execute, args=(record,), daemon=True)
        self.thread.start()
        return record["id"]

    def request(self, record, path, *, form=None):
        if self.cancel.is_set():
            raise InterruptedError("operator_stopped")
        if record["requests"]:
            self.cancel.wait(0.6)
        if self.cancel.is_set():
            raise InterruptedError("operator_stopped")
        if len(record["requests"]) >= 20:
            raise RuntimeError("runner_request_limit")
        rid = secrets.token_hex(12)
        url = f"http://127.0.0.1:{PORTS[record['mode']]}" + path
        req = Request(url, data=urlencode(form).encode() if form is not None else None,
                      headers={"X-Request-ID": rid, "Content-Type": "application/x-www-form-urlencoded"})
        started = utc()
        try:
            response = OPENER.open(req, timeout=5)
        except HTTPError as error:
            response = error
        with response:
            raw = response.read(65537)
            if len(raw) > 65536:
                raise RuntimeError("response_limit")
            item = {"request_id": rid, "method": req.get_method(), "target": path, "observed_at": started,
                    "status": response.code, "body_sha256": hashlib.sha256(raw).hexdigest(),
                    "body_text": raw.decode("utf-8", "replace")}
        # Passwords are neither retained here nor added to target URLs or logs.
        record["requests"].append(item)
        self.save(record)
        return item

    def execute(self, record):
        try:
            reset(record["scenario"], record["mode"])
            start = time.monotonic()
            s = SCENARIOS[record["scenario"]]
            value = s["attacks" if record["kind"] == "attempt" else "benign"][record["variant"]]
            if record["scenario"] == "brute":
                if record["kind"] == "attempt":
                    for _ in range(5):
                        self.request(record, "/login", form={"username": value, "password": "wrong-demo"})
                last = self.request(record, "/login", form={"username": value, "password": PASSWORD})
                record["functional_effect_confirmed"] = record["kind"] == "attempt" and last["status"] == 200 and json.loads(last["body_text"]).get("authenticated") is True
                record["benign_ok"] = record["kind"] == "benign" and last["status"] == 200
                record["control_observation"] = "login_limited" if last["status"] == 429 else "authentication_response"
            else:
                value = value.replace("__NONCE__", record["nonce"])
                query = {s["field"]: value}
                if record["scenario"] == "xss":
                    query["_request"] = record["id"]
                path = s["path"] + "?" + urlencode(query)
                last = self.request(record, path)
                text = last["body_text"]
                if record["scenario"] == "sqli":
                    record["functional_effect_confirmed"] = "UM-9000" in text
                elif record["scenario"] == "traversal":
                    record["functional_effect_confirmed"] = "PU_RESERVED_FIXTURE_20261026" in text
                elif record["scenario"] == "command":
                    result = json.loads(text)
                    output = result.get("stdout", "")
                    record["functional_effect_confirmed"] = record["kind"] == "attempt" and ("uid=10001" in output or "\numbral\n" in output or output.strip() == "/srv/fixtures/public")
                elif record["scenario"] == "xss":
                    record["reflection_unencoded"] = record["kind"] == "attempt" and value in text
                    record["reflection_encoded"] = record["kind"] == "attempt" and html.escape(value) in text
                    record["frame_url"] = f"http://127.0.0.1:{PORTS[record['mode']]}" + path
                    record["control_observation"] = "unencoded_reflection_not_execution" if record["reflection_unencoded"] else "encoded_as_text"
                    # A second real request will load the browser frame; preserve the server rate limit.
                    self.cancel.wait(0.6)
                record["benign_ok"] = record["kind"] == "benign" and last["status"] == 200
            expected_status = 200
            if record["kind"] == "attempt" and record["mode"] == "corrected":
                expected_status = {"traversal": 403, "command": 400, "brute": 429}.get(record["scenario"], 200)
            if last["status"] != expected_status:
                raise RuntimeError("unexpected_http_status:" + str(last["status"]))
            if time.monotonic() - start > 30:
                raise RuntimeError("execution_time_limit")
            if self.cancel.is_set():
                raise InterruptedError("operator_stopped")
            record["status"] = "completed"
        except InterruptedError:
            record["status"] = "stopped"
        except Exception as error:
            record["status"] = "failed"
            record["error"] = str(error)[:180]
        finally:
            record["finished_at"] = utc()
            try:
                self.capture(record)
            except Exception as error:
                record["capture_error"] = str(error)[:180]
            self.save(record)
            self.current = None
            self.lock.release()

    def capture(self, record):
        result = command(["docker", "logs", "--timestamps=false", PROJECT + "-gateway-" + record["mode"]])
        content = result.stdout.encode("utf-8")
        if len(content) > 4 * 1024 * 1024:
            raise RuntimeError("capture_limit")
        root = STATE / "runs" / record["id"]
        root.mkdir(parents=True, exist_ok=True)
        filename = "access-" + secrets.token_hex(8) + ".log"
        (root / filename).write_bytes(content)
        identifiers = [r["request_id"] for r in record["requests"]] + [record["id"]]
        matches = [{"line": index, "sha256": hashlib.sha256(line.encode()).hexdigest()} for index, line in enumerate(result.stdout.splitlines(), 1)
                   if any(identifier in line for identifier in identifiers)]
        record["access_snapshot"] = {"file": filename, "sha256": hashlib.sha256(content).hexdigest(), "bytes": len(content), "matches": matches}
        record.setdefault("access_snapshots", []).append(record["access_snapshot"])

    def confirm_xss(self, run_id, nonce):
        with self.data_lock:
            record = self.records.get(run_id)
            if not record or record["scenario"] != "xss" or record["status"] != "completed" or not secrets.compare_digest(record["nonce"], str(nonce)):
                raise ValueError("invalid_browser_observation")
            if not record.get("reflection_unencoded"):
                raise ValueError("unexpected_browser_observation")
            record["browser_execution_confirmed"] = True
            record["functional_effect_confirmed"] = True
            record["browser_observed_at"] = utc()
            record["browser_observer"] = "control_origin_message_source_and_nonce"
            record["browser_frame_loaded"] = True
            self.capture(record)
            self.save(record)


def serve():
    runtime = Runtime()

    class Control(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass

        def reply(self, status, value, content_type="application/json; charset=utf-8"):
            data = value if isinstance(value, bytes) else value.encode() if isinstance(value, str) else json.dumps(value, ensure_ascii=False).encode()
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
                             "font-src 'self' https://fonts.gstatic.com; frame-src http://127.0.0.1:4380 http://127.0.0.1:4382; "
                             "connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'none'")
            self.end_headers()
            self.wfile.write(data)

        def guard(self, *, api=False):
            if self.headers.get("Host") != "127.0.0.1:4381":
                self.reply(403, {"error": "invalid_host"})
                return False
            if self.headers.get("Origin") not in (None, ORIGIN):
                self.reply(403, {"error": "invalid_origin"})
                return False
            if api and not secrets.compare_digest(self.headers.get("X-Umbral-Control", ""), runtime.token):
                self.reply(403, {"error": "invalid_control_token"})
                return False
            return True

        def do_GET(self):
            path = urlsplit(self.path).path
            if not self.guard(api=path.startswith("/api/")):
                return
            if path == "/":
                content = (ROOT / "lab/control.html").read_text(encoding="utf-8").replace("__CONTROL_TOKEN__", runtime.token)
                self.reply(200, content, "text/html; charset=utf-8")
            elif path in {"/control.js", "/control.css", "/assets/styles.css", "/assets/favicon.svg"}:
                source = ROOT / ("lab/" + path[1:] if path.startswith("/control.") else "assets/" + path.rsplit("/", 1)[1])
                suffix = source.suffix
                self.reply(200, source.read_bytes(), {".js": "text/javascript; charset=utf-8", ".css": "text/css; charset=utf-8", ".svg": "image/svg+xml"}[suffix])
            elif path == "/api/status":
                self.reply(200, {"version": VERSION, "current": runtime.current, "boundary": runtime.boundary,
                                 "scenarios": {key: {"name": value["name"], "path": value["path"], "owasp": value["owasp"]} for key, value in SCENARIOS.items()},
                                 "runs": sorted(runtime.records.values(), key=lambda r: r["started_at"], reverse=True)[:100]})
            elif re.fullmatch(r"/api/runs/[a-f0-9]{32}", path):
                record = runtime.records.get(path.rsplit("/", 1)[1])
                self.reply(200 if record else 404, record or {"error": "not_found"})
            else:
                self.reply(404, {"error": "not_found"})

        def do_POST(self):
            if not self.guard(api=True):
                return
            try:
                size = int(self.headers.get("Content-Length", "0"))
                if not 0 < size <= 2048:
                    raise ValueError("body_limit")
                selection = json.loads(self.rfile.read(size))
                if not isinstance(selection, dict):
                    raise ValueError("invalid_body")
                path = urlsplit(self.path).path
                if path == "/api/run":
                    self.reply(202, {"id": runtime.launch(selection)})
                elif path == "/api/cancel":
                    runtime.cancel.set()
                    self.reply(200, {"requested": True})
                elif path == "/api/reset":
                    if not runtime.lock.acquire(blocking=False):
                        raise ValueError("execution_busy")
                    try:
                        reset(selection.get("scenario"), selection.get("mode"))
                    finally:
                        runtime.lock.release()
                    self.reply(200, {"reset": True, "evidence_preserved": True})
                elif path == "/api/confirm-xss":
                    runtime.confirm_xss(selection.get("id"), selection.get("nonce"))
                    self.reply(200, {"confirmed": True})
                else:
                    self.reply(404, {"error": "not_found"})
            except (ValueError, TypeError):
                self.reply(400, {"error": "invalid_or_busy_request"})
            except Exception:
                self.reply(503, {"error": "operation_failed"})

    with ThreadingHTTPServer(("127.0.0.1", 4381), Control) as server:
        server.daemon_threads = True
        server.timeout = 1
        print(ORIGIN, flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            runtime.cancel.set()
        finally:
            if runtime.thread:
                runtime.thread.join(timeout=35)


def check_suite():
    # Functional observations only, not V2 classifications or an LLM evaluation.
    manifest = {"version": VERSION, "seed": SEED, "cases": cases()}
    corpus_path = ROOT / "lab/corpus.json"
    expected = json.loads(corpus_path.read_text(encoding="utf-8"))
    if expected != manifest:
        raise RuntimeError("corpus_changed_or_missing")
    runtime = Runtime()
    results = []
    for case in expected["cases"]:
        run_id = runtime.launch(case)
        runtime.thread.join(timeout=35)
        if runtime.thread.is_alive():
            runtime.cancel.set()
            raise RuntimeError("suite_execution_timeout")
        record = runtime.records[run_id]
        if case["kind"] == "benign":
            matched = record.get("benign_ok", False)
        elif case["scenario"] == "xss":
            matched = record.get("reflection_unencoded" if case["expected_effect"] else "reflection_encoded", False)
        else:
            matched = record["functional_effect_confirmed"] == case["expected_effect"]
        passed = record["status"] == "completed" and matched and bool(record.get("access_snapshot", {}).get("matches"))
        item = {**case, "run_id": run_id, "passed": passed,
                "browser_confirmation_pending": case["scenario"] == "xss" and case["kind"] == "attempt"}
        results.append(item)
        print(json.dumps(item), flush=True)
    result = {"checked_at": utc(), "version": VERSION, "corpus_sha256": hashlib.sha256(corpus_path.read_bytes()).hexdigest(),
              "kind": "functional_http_not_v2_evaluation", "cases": results,
              "passed": sum(r["passed"] for r in results), "total": len(results), "xss_browser_pending": 6}
    atomic(STATE / "suite.json", result)
    return result
