"""Plan an isolated Mailpit review; --run explicitly starts disposable Docker fixtures."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
from unittest.mock import patch
from urllib.request import ProxyHandler, build_opener
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.scan_lab_images import IMAGE_SETS


def docker(*arguments):
    result = subprocess.run(["docker", *arguments], check=True, capture_output=True,
                            text=True, timeout=180)
    return (result.stdout + (result.stderr if arguments[0] == "logs" else "")).strip()


def loopback_port(bindings, name):
    values = bindings.get(name + "/tcp")
    if (not isinstance(values, list) or len(values) != 1
            or values[0].get("HostIp") != "127.0.0.1"):
        raise ValueError("fixture_port_not_loopback")
    port = int(values[0]["HostPort"])
    if not 1 <= port <= 65535:
        raise ValueError("fixture_port_invalid")
    return port


def json_get(opener, base, route):
    with opener.open(base + route, timeout=3) as response:
        return json.load(response)


def run_case(label, reference, scan_dir, output):
    if IMAGE_SETS["mailpit-review"].get(label, (None, None))[1] != reference:
        raise ValueError("unreviewed_fixture_reference")
    report = json.loads((scan_dir / (label + ".json")).read_text(encoding="utf-8"))
    if report.get("ArtifactName") != reference:
        raise ValueError("fixture_scan_reference_mismatch")
    token = "webdefense-mailpit-" + uuid4().hex
    owner = "web-defense-ai-v2.review=" + token
    network, container = False, None
    result = {"reference": reference, "label": label, "status": "failed",
              "synthetic_only": True, "external_delivery": False}
    try:
        docker("pull", "--platform", "linux/amd64", reference)
        image = json.loads(docker("image", "inspect", reference))[0]
        if image["Id"] != report["Metadata"]["ImageID"]:
            raise ValueError("fixture_image_differs_from_scanned_image")
        result.update(image_id=image["Id"], repo_digests=image.get("RepoDigests"), same_image_as_scan=True)
        docker("network", "create", "--internal", "--label", owner, token)
        network = True
        identifier = docker("run", "--detach", "--platform", "linux/amd64",
            "--name", token, "--label", owner, "--network", token,
            "--publish", "127.0.0.1::8025", "--publish", "127.0.0.1::1025",
            "--cap-drop", "ALL", "--security-opt", "no-new-privileges", "--read-only",
            "--memory", "256m", "--cpus", "1", "--pids-limit", "128", "--tmpfs", "/tmp:size=64m",
            "--env", "MP_DATABASE=/tmp/mailpit.db", "--env", "MP_MAX_MESSAGES=500",
            "--env", "MP_SMTP_AUTH_ACCEPT_ANY=true", "--env", "MP_SMTP_AUTH_ALLOW_INSECURE=true", reference)
        if not re.fullmatch(r"[a-f0-9]{64}", identifier):
            raise ValueError("fixture_container_id_invalid")
        container = identifier
        state = json.loads(docker("container", "inspect", container))[0]
        if state["Config"]["Labels"].get("web-defense-ai-v2.review") != token:
            raise ValueError("fixture_owner_mismatch")
        bindings = state["NetworkSettings"]["Ports"]
        http_port, smtp_port = loopback_port(bindings, "8025"), loopback_port(bindings, "1025")
        result["loopback_only"] = True
        opener = build_opener(ProxyHandler({}))
        base = "http://127.0.0.1:" + str(http_port)
        deadline = time.monotonic() + 40
        while True:
            try:
                info = json_get(opener, base, "/api/v1/info")
                break
            except OSError:
                if time.monotonic() >= deadline:
                    raise TimeoutError("fixture_http_not_ready") from None
                time.sleep(1)
        if info["Version"].lstrip("v") != reference.rsplit(":", 1)[1].lstrip("v"):
            raise ValueError("fixture_version_mismatch")
        if json_get(opener, base, "/api/v1/messages")["total"] != 0:
            raise ValueError("fixture_mailbox_not_empty")
        subject = "Prueba sintética " + token
        body = "Informe de compatibilidad: XSS y fuerza bruta. Solo datos sintéticos."
        # Exercise the real application email function with only synthetic
        # loopback configuration; dotenv remains disabled throughout imports.
        with patch("dotenv.load_dotenv", return_value=False), patch.dict(os.environ, {
            "EMAIL_REMITENTE": "sender@example.invalid", "EMAIL_DESTINATARIO": "recipient@example.invalid",
            "EMAIL_PASSWORD": "", "EMAIL_SMTP_SERVER": "127.0.0.1", "EMAIL_SMTP_PORT": str(smtp_port),
            "EMAIL_SMTP_STARTTLS": "0", "EMAIL_SMTP_TIMEOUT_SECONDS": "5"}, clear=True):
            from config.notifications import enviar_email
            if not enviar_email(subject, body):
                raise ValueError("fixture_smtp_delivery_failed")
        message = json_get(opener, base, "/api/v1/message/latest")
        if message["Subject"] != subject or body not in message["Text"]:
            raise ValueError("fixture_message_roundtrip_mismatch")
        with opener.open(base + "/api/v1/message/latest/raw", timeout=3) as response:
            raw = response.read()
        if json_get(opener, base, "/api/v1/messages")["total"] != 1:
            raise ValueError("fixture_message_count_mismatch")
        result.update(status="passed", version=info["Version"], api_readback=True, smtp_roundtrip=True,
                      raw_export=True, raw_sha256=hashlib.sha256(raw).hexdigest(), message_count=1)
    except Exception as error:
        result.update(error_type=type(error).__name__, error=str(error))
    finally:
        # Inspect ownership before removing only the resources created here.
        try:
            if container:
                state = json.loads(docker("container", "inspect", container))[0]
                if state["Config"]["Labels"].get("web-defense-ai-v2.review") != token:
                    raise ValueError("fixture_cleanup_owner_mismatch")
                (output / (label + ".log")).write_text(docker("logs", container), encoding="utf-8")
                docker("rm", "--force", container)
            if network:
                state = json.loads(docker("network", "inspect", token))[0]
                if state["Labels"].get("web-defense-ai-v2.review") != token:
                    raise ValueError("fixture_cleanup_network_owner_mismatch")
                docker("network", "rm", token)
            result["owned_resources_removed"] = True
        except Exception as error:
            result.update(status="failed", cleanup_error_type=type(error).__name__)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--scan-dir", type=Path, default=Path(".local-state/image-audit"))
    parser.add_argument("--output-dir", type=Path, default=Path(".local-state/mailpit-review"))
    args = parser.parse_args()
    references = IMAGE_SETS["mailpit-review"]
    if not args.run:
        print(json.dumps({"images": references, "containers_started": False, "requires_explicit_run": True}, indent=2))
        return 0
    args.output_dir.mkdir(parents=True, exist_ok=True)
    rows = [run_case(label, reference, args.scan_dir, args.output_dir) for label, (_, reference) in references.items()]
    result = {"schema_version": 1, "captured_at": datetime.now(timezone.utc).isoformat(),
              "scope": "disposable_synthetic_mailpit_fixtures", "operational_instances_changed": False,
              "images": rows, "passed": all(row["status"] == "passed" for row in rows)}
    (args.output_dir / "compatibility.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
