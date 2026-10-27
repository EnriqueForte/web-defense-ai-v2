"""Explicit local log ingestion for Puerto Umbral; no HTTP, dotenv or model calls.

The functions in this module do nothing until called. Immutable snapshots are
separate from the dashboard copy and from the educational scenario's receipts.
"""
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import ipaddress
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import time
import uuid

from dashboard.services.read_store import atomic_write_text, capture_file
from dashboard.services.runtime_lock import AlreadyRunning, exclusive_lock

ROOT = Path(__file__).resolve().parents[2]
STATE = ROOT / ".local-state" / "puerto-umbral"
DEFAULT_DESTINATION = STATE / "access.log"
PROJECT = "puerto-umbral-f2"
MODES = ("vulnerable", "corrected")
MAX_BYTES = 1048576
MAX_CAPTURE_BYTES = 4 * MAX_BYTES
TAIL_LINES = 1000
ACCESS = re.compile(r'^(\S+) \S+ \S+ \[([^\]]+)\] "([A-Z]+) ([^ ]+) HTTP/[^" ]+" ([0-9]{3})(?: |$)')


class CaptureError(ValueError):
    """Only fixed safe codes; never include source contents or process stderr."""


class CaptureCancelled(CaptureError):
    pass


def _check_cancel(cancelled):
    if cancelled is not None and cancelled():
        raise CaptureCancelled("capture_cancelled")


def _cancellable_run(args, *, capture_output, timeout, cancelled):
    """Own only this Docker CLI child; it remains in the launcher's process group."""
    _check_cancel(cancelled)
    with subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as process:
        deadline = time.monotonic() + timeout
        try:
            while True:
                _check_cancel(cancelled)
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise subprocess.TimeoutExpired(args, timeout)
                try:
                    stdout, stderr = process.communicate(timeout=min(.2, remaining))
                    return subprocess.CompletedProcess(args, process.returncode, stdout, stderr)
                except subprocess.TimeoutExpired:
                    continue
        finally:
            if process.poll() is None:
                process.kill()
                process.communicate()


@dataclass(frozen=True)
class CapturedLog:
    snapshot_path: Path
    digest: str
    line_count: int
    snapshot_id: str
    changed: bool


def _now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _root_safe(target=STATE):
    candidate = ROOT
    for part in Path(target).relative_to(ROOT).parts:
        candidate = candidate / part
        if candidate.exists() or candidate.is_symlink():
            info = candidate.lstat()
            if candidate.is_symlink() or getattr(info, "st_file_attributes", 0) & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0):
                raise CaptureError("unsafe_state_directory")


def _bytes(value):
    return value.encode("utf-8") if isinstance(value, str) else value


def _docker(args, run):
    result = run(["docker", *args], capture_output=True, timeout=20)
    if result.returncode:
        raise CaptureError("source_unavailable")
    return _bytes(result.stdout)


def _gateway(info, mode):
    config = info.get("Config") or {}
    labels = config.get("Labels") or {}
    service = "gateway-" + mode
    if (labels.get("com.docker.compose.project") != PROJECT
            or labels.get("com.docker.compose.service") != service
            or labels.get("org.puerto-umbral.lab") != "f2-v1"):
        raise CaptureError("unexpected_source")
    host = info.get("HostConfig") or {}
    port = "4380" if mode == "vulnerable" else "4382"
    expected = [{"HostIp": "127.0.0.1", "HostPort": port}]
    if (host.get("Privileged") or not host.get("ReadonlyRootfs")
            or config.get("User") != "10001:10001"
            or host.get("PortBindings") != {"8080/tcp": expected}):
        raise CaptureError("source_configuration_changed")
    if info.get("State", {}).get("Running"):
        if info.get("NetworkSettings", {}).get("Ports", {}).get("8080/tcp") != expected:
            raise CaptureError("source_bindings_changed")
    return {"container_id": info.get("Id"), "image_id": info.get("Image"),
            "started_at": info.get("State", {}).get("StartedAt"),
            "running_at_capture": bool(info.get("State", {}).get("Running"))}


def _access_lines(content, *, allow_empty=False):
    if not content and allow_empty:
        return "", 0, 0
    if not content or len(content) > MAX_CAPTURE_BYTES:
        raise CaptureError("empty_or_oversized_source")
    if allow_empty and not content.endswith(b"\n"):
        raise CaptureError("incomplete_access_line")
    lines = content.decode("utf-8", errors="strict").splitlines()
    lines = [line for line in lines if line.strip()]
    for line in lines:
        match = ACCESS.match(line)
        if (not match or len(line.encode()) > 16384
                or any(ord(char) < 32 for char in line)):
            raise CaptureError("invalid_access_format")
        try:
            ipaddress.ip_address(match[1])
            datetime.strptime(match[2], "%d/%b/%Y:%H:%M:%S %z")
        except ValueError:
            raise CaptureError("invalid_access_metadata") from None
        if not 100 <= int(match[5]) <= 599:
            raise CaptureError("invalid_http_status")
    if not lines and allow_empty:
        return "", 0, 0
    if not lines:
        raise CaptureError("empty_source")
    selected, size = [], 0
    for line in reversed(lines):
        length = len(line.encode()) + 1
        if size + length > MAX_BYTES:
            break
        selected.append(line)
        size += length
    selected.reverse()
    if not selected:
        raise CaptureError("source_limit")
    return "\n".join(selected) + "\n", len(lines), len(lines) - len(selected)


def _attempt(status, *, mode, error=None, snapshot_id=None, digest=None):
    atomic_write_text(STATE / "last-attempt.json", json.dumps({"attempted_at": _now(), "status": status,
                      "mode": mode, "error_code": error, "snapshot_id": snapshot_id,
                      "sha256": digest}, ensure_ascii=False))


def capture_access_log(destination=DEFAULT_DESTINATION, *, mode=None, run=None,
                       reuse_unchanged=False, require_running=False, cancelled=None):
    """Read only the selected gateway's logs; never start a container or analysis.

    On failure, previous generations remain intact. Publication uses an immutable
    generation plus a dashboard copy; readers detect interrupted pointer/copy updates.
    """
    mode = mode or os.getenv("PUERTO_UMBRAL_MODE", "vulnerable")
    if mode not in MODES or Path(destination).absolute() != DEFAULT_DESTINATION.absolute():
        return None
    try:
        _root_safe()
        STATE.mkdir(parents=True, exist_ok=True)
        for target in (STATE / ".capture.lock", STATE / "current.json", STATE / "last-attempt.json", DEFAULT_DESTINATION):
            _root_safe(target)
        with exclusive_lock(STATE / ".capture.lock"):
            _check_cancel(cancelled)
            size = sum(path.stat().st_size for path in STATE.rglob("*") if path.is_file())
            if size > 128 * MAX_BYTES or shutil.disk_usage(STATE).free < 100 * MAX_BYTES:
                raise CaptureError("capture_storage_limit")
            execute = run or (subprocess.run if cancelled is None else
                             lambda args, **kwargs: _cancellable_run(args, cancelled=cancelled, **kwargs))
            name = PROJECT + "-gateway-" + mode
            inspected = json.loads(_docker(["inspect", name], execute))
            if not isinstance(inspected, list) or len(inspected) != 1 or not isinstance(inspected[0], dict):
                raise CaptureError("unexpected_source")
            source = _gateway(inspected[0], mode)
            if require_running and not source["running_at_capture"]:
                raise CaptureError("source_stopped")
            original = _docker(["logs", "--timestamps=false", "--tail", str(TAIL_LINES), name], execute)
            if require_running:
                checked = json.loads(_docker(["inspect", name], execute))
                if (not isinstance(checked, list) or len(checked) != 1 or not isinstance(checked[0], dict)
                        or _gateway(checked[0], mode) != source):
                    raise CaptureError("source_changed_during_capture")
            text, returned, omitted = _access_lines(original, allow_empty=reuse_unchanged and require_running)
            digest = hashlib.sha256(text.encode()).hexdigest()
            current = capture_file(DEFAULT_DESTINATION)
            changed = current.digest != digest
            if reuse_unchanged and not changed:
                status = source_status(mode=mode)
                if (status["status"] in {"available", "stale", "error"}
                        and status.get("snapshot_mode") == mode and status.get("sha256") == digest
                        and status.get("gateway") == source and status.get("snapshot_id")):
                    identifier = status["snapshot_id"]
                    snapshot = STATE / "snapshots" / identifier / "access.log"
                    _check_cancel(cancelled)
                    _attempt("available", mode=mode, snapshot_id=identifier, digest=digest)
                    return CapturedLog(snapshot, digest, returned - omitted, identifier, False)
            _check_cancel(cancelled)
            identifier = uuid.uuid4().hex
            generation = STATE / "snapshots" / identifier
            _root_safe(generation)
            generation.mkdir(parents=True, exist_ok=False)
            snapshot = generation / "access.log"
            atomic_write_text(snapshot, text)
            receipt = {"schema_version": 1, "snapshot_id": identifier, "source": "puerto-umbral", "mode": mode,
                       "captured_at": _now(), "sha256": digest, "line_count": returned - omitted,
                       "bytes": len(text.encode()), "changed": changed, "gateway": source,
                       "scope": {"requested_tail_lines": TAIL_LINES, "returned_lines": returned,
                                 "omitted_returned_lines": omitted, "complete_history": False},
                       "analysis_requested": False, "notifications_requested": False}
            encoded = json.dumps(receipt, ensure_ascii=False, indent=2)
            atomic_write_text(generation / "receipt.json", encoded)
            _check_cancel(cancelled)
            atomic_write_text(STATE / "current.json", encoded)
            if changed:
                atomic_write_text(DEFAULT_DESTINATION, text)
            _attempt("available", mode=mode, snapshot_id=identifier, digest=digest)
            return CapturedLog(snapshot, digest, returned - omitted, identifier, changed)
    except CaptureCancelled:
        return None  # Cancellation is not an observation of a source failure.
    except (OSError, ValueError, TypeError, KeyError, UnicodeError, subprocess.TimeoutExpired, AlreadyRunning) as error:
        code = str(error) if isinstance(error, CaptureError) else "capture_failed"
        try:
            _root_safe()
            _attempt("error", mode=mode, error=code)
        except (OSError, ValueError):
            pass
        return None


def source_status(*, mode=None):
    """Read local metadata only. Does not inspect Docker, write, or trigger work."""
    mode = mode or os.getenv("PUERTO_UMBRAL_MODE", "vulnerable")
    result = {"source": "puerto-umbral", "mode": mode, "status": "missing", "captured_at": None,
              "snapshot_id": None, "sha256": None, "line_count": None, "changed": None,
              "running_at_capture": None, "error_code": None}
    try:
        _root_safe()
        _root_safe(STATE / "current.json")
        _root_safe(STATE / "last-attempt.json")
        pointer = capture_file(STATE / "current.json")
        if pointer.status != "available":
            attempt = capture_file(STATE / "last-attempt.json")
            if attempt.status == "available":
                last = json.loads(attempt.text)
                if last.get("status") == "error" and last.get("mode") == mode:
                    result.update(status="error", error_code=last.get("error_code", "capture_failed"))
            return result
        receipt = json.loads(pointer.text)
        identifier, digest = receipt["snapshot_id"], receipt["sha256"]
        if (receipt.get("schema_version") != 1 or not re.fullmatch(r"[a-f0-9]{32}", identifier)
                or not re.fullmatch(r"[a-f0-9]{64}", digest) or receipt.get("source") != "puerto-umbral"
                or receipt.get("mode") not in MODES):
            raise CaptureError("invalid_capture_receipt")
        _root_safe(STATE / "snapshots" / identifier / "access.log")
        _root_safe(DEFAULT_DESTINATION)
        snapshot = capture_file(STATE / "snapshots" / identifier / "access.log")
        copy = capture_file(DEFAULT_DESTINATION)
        if snapshot.status != "available" or snapshot.digest != digest or snapshot.size > MAX_BYTES:
            raise CaptureError("snapshot_integrity_error")
        captured = datetime.fromisoformat(receipt["captured_at"].replace("Z", "+00:00"))
        age = (datetime.now(timezone.utc) - captured).total_seconds()
        status = "stale" if age > 300 else "available"
        if copy.digest != digest:
            status = "changing"
        if receipt["mode"] != mode:
            status = "mode_mismatch"
        result.update(status=status, captured_at=receipt["captured_at"], snapshot_id=identifier, sha256=digest,
                      snapshot_mode=receipt["mode"], gateway=receipt["gateway"], last_checked_at=None,
                      line_count=receipt["line_count"], changed=receipt["changed"],
                      running_at_capture=receipt["gateway"]["running_at_capture"], scope=receipt["scope"])
        attempt = capture_file(STATE / "last-attempt.json")
        if attempt.status == "available":
            last = json.loads(attempt.text)
            if last.get("status") == "error" and last.get("mode") == mode:
                result.update(status="error", error_code=last.get("error_code", "capture_failed"))
            elif (last.get("status") == "available" and last.get("mode") == mode == receipt["mode"]
                  and last.get("snapshot_id") == identifier and last.get("sha256") == digest):
                checked = datetime.fromisoformat(last["attempted_at"].replace("Z", "+00:00"))
                result["last_checked_at"] = last["attempted_at"]
                if status in {"available", "stale"}:
                    result["status"] = "stale" if (datetime.now(timezone.utc) - checked).total_seconds() > 300 else "available"
        return result
    except (OSError, ValueError, TypeError, KeyError) as error:
        result.update(status="error", error_code=str(error) if isinstance(error, CaptureError) else "invalid_capture_metadata")
        return result


def verify_analysis_input(snapshot):
    if not isinstance(snapshot, CapturedLog):
        return False
    expected = STATE / "snapshots" / snapshot.snapshot_id / "access.log"
    try:
        if not re.fullmatch(r"[a-f0-9]{32}", snapshot.snapshot_id) or snapshot.snapshot_path != expected:
            return False
        _root_safe(expected)
        captured = capture_file(expected)
        return captured.status == "available" and captured.size <= MAX_BYTES and captured.digest == snapshot.digest
    except (OSError, ValueError):
        return False


def record_analysis_input(snapshot, analysis_id):
    if not isinstance(analysis_id, str) or not re.fullmatch(r"[a-f0-9]{32}", analysis_id) or not verify_analysis_input(snapshot):
        raise CaptureError("invalid_analysis_input")
    path = STATE / "analysis-inputs" / (analysis_id + ".json")
    _root_safe(path)
    if path.exists():
        raise CaptureError("analysis_input_already_recorded")
    atomic_write_text(path, json.dumps({"schema_version": 1, "analysis_id": analysis_id,
                      "snapshot_id": snapshot.snapshot_id, "sha256": snapshot.digest,
                      "line_count": snapshot.line_count, "recorded_at": _now()}))


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=MODES, default="vulnerable")
    parser.add_argument("--status", action="store_true", help="Solo leer metadatos locales; no contactar con Docker")
    args = parser.parse_args()
    if args.status:
        print(json.dumps(source_status(mode=args.mode), ensure_ascii=False, indent=2))
        return 0
    result = capture_access_log(mode=args.mode)
    if result is None:
        print("Captura no completada. Se conservan las generaciones anteriores.")
        return 1
    print(json.dumps({"snapshot_id": result.snapshot_id, "sha256": result.digest,
                      "line_count": result.line_count, "changed": result.changed, "analysis_requested": False}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
