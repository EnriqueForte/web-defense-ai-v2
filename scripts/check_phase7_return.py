"""Real local entry/fallback rehearsal with synthetic fixture and owned servers.

Uses free canonical ports, never stops user servers or executes engine/notifications.
Requires an existing isolated Next production build; leaves no server running.
"""
import argparse
from datetime import datetime, timezone
from http.client import HTTPConnection
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]


def get(port, path="/"):
    connection = HTTPConnection("127.0.0.1", port, timeout=3)
    try:
        connection.request("GET", path)
        response = connection.getresponse()
        return response.status, response.getheader("Location"), response.read()
    finally:
        connection.close()


def wait_ready(process, port):
    deadline = time.monotonic() + 25
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError("El servidor propio terminó durante el inicio")
        try:
            if get(port)[0] in (200, 302):
                return
        except OSError:
            pass
        time.sleep(.1)
    raise TimeoutError("El servidor propio no está disponible")


def stop(process):
    if process is not None and process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)


def rehearse(build):
    build = Path(build).resolve()
    # The isolated snapshot must not carry an operational dotenv file.
    if not build.is_relative_to((ROOT / ".local-state").resolve()) or any(build.glob(".env*")):
        raise ValueError("Usa una copia aislada sin dotenv bajo .local-state")
    if not (build / ".next" / "BUILD_ID").is_file():
        raise ValueError("Falta el build aislado")
    node = shutil.which("node")
    if not node:
        raise ValueError("Node no disponible")
    for port in (3000, 5000):
        with socket.socket() as probe:
            probe.bind(("127.0.0.1", port))
    result = {"scope": "synthetic-local-rehearsal", "checked_at": datetime.now(timezone.utc).isoformat()}
    flask, next_process = None, None
    environment = {**os.environ, "PYTHONIOENCODING": "utf-8", "ANALYSIS_MANUAL_ENABLED": "0",
                   "NEXT_PRIMARY_ENABLED": "1", "GROQ_API_KEY": "", "OPENROUTER_API_KEY": ""}
    options = {"cwd": ROOT, "env": environment, "stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL,
               "creationflags": subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0}
    def start_flask():
        return subprocess.Popen([sys.executable, "-B", "tests/serve_phase4_fixture.py", "--port", "5000"], **options)
    try:
        flask = start_flask()
        wait_ready(flask, 5000)
        next_process = subprocess.Popen([node, str(ROOT / "frontend/node_modules/next/dist/bin/next"),
                                         "start", str(build), "--hostname", "127.0.0.1", "--port", "3000"], **options)
        wait_ready(next_process, 3000)
        status, location, _ = get(5000)
        if (status, location) != (302, "http://127.0.0.1:3000/"):
            raise RuntimeError("No se verificó la redirección")
        state = json.loads(get(5000, "/api/v1/estado")[2])
        proxied = json.loads(get(3000, "/api/v1/estado")[2])
        if state["meta"]["snapshot_id"] != proxied["meta"]["snapshot_id"] or state["data"]["threats_total"] != 28:
            raise RuntimeError("La captura sintética no coincide")
        current = json.loads(get(5000, "/api/v1/analisis/actual")[2])["data"]
        if current["manual_enabled"] or current["llm_ready"]:
            raise RuntimeError("La fixture no está aislada del análisis")
        result.update(primary_status=status, next_status=get(3000)[0], snapshots_equal=True, manual_enabled=False)
        catalog = json.loads(get(5000, "/api/v1/reportes")[2])
        report_id = catalog["data"][0]["id"]
        stop(next_process)
        started = time.perf_counter()
        fallback_status = get(5000)[0]
        result["fallback_ms"] = round((time.perf_counter() - started) * 1000, 1)
        result["fallback_status"] = fallback_status
        result["fallback_api_status"] = get(5000, "/api/v1/estado")[0]
        result["fallback_report_status"] = get(5000, "/api/v1/reportes/" + report_id)[0]
        if any(result[key] != 200 for key in ("fallback_status", "fallback_api_status", "fallback_report_status")):
            raise RuntimeError("El retorno no conserva entrada/API/reporte")
        stop(flask)
        environment["NEXT_PRIMARY_ENABLED"] = "0"
        flask = start_flask()
        wait_ready(flask, 5000)
        status, location, _ = get(5000)
        if status != 200 or location is not None:
            raise RuntimeError("El modo apagado no sirve Flask")
        result["switch_off_status"] = status
        result["passed"] = True
        return result
    finally:
        stop(next_process)
        stop(flask)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", type=Path, default=ROOT / ".local-state/delivery2-frontend")
    args = parser.parse_args()
    try:
        result = rehearse(args.build)
    except (OSError, ValueError, RuntimeError, TimeoutError):
        print("Ensayo no completado: revisa puertos libres y build aislado; no se detuvieron servidores ajenos.", file=sys.stderr)
        return 1
    directory = ROOT / ".local-state" / "phase7" / "checks"
    directory.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    (directory / f"return-{stamp}.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
