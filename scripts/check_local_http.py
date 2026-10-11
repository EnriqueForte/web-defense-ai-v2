"""Arranque HTTP efímero con fixtures; sin .env, motor, Docker o notificaciones."""
from contextlib import closing
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
from urllib.error import URLError
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]


def main():
    with closing(socket.socket()) as reservation:
        reservation.bind(("127.0.0.1", 0))
        port = reservation.getsockname()[1]
    command = [sys.executable, "-B", str(ROOT / "tests/serve_phase4_fixture.py"), "--port", str(port)]
    process = subprocess.Popen(command, cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                               creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
    origin = f"http://127.0.0.1:{port}"
    try:
        deadline = time.monotonic() + 15
        while True:
            if process.poll() is not None:
                raise RuntimeError("fixture_server_stopped")
            try:
                with urlopen(origin, timeout=1) as response:
                    assert response.status == 200
                    assert response.headers["X-Frame-Options"] == "DENY"
                    assert "script-src 'self' 'nonce-" in response.headers["Content-Security-Policy"]
                    html = response.read().decode("utf-8")
                    assert "/static/vendor/chart.js-4.4.1.umd.js" in html
                break
            except URLError:
                if time.monotonic() >= deadline:
                    raise RuntimeError("fixture_server_unavailable")
                time.sleep(0.1)
        manifest = json.loads((ROOT / "dashboard/static/vendor/manifest.json").read_text(encoding="utf-8"))
        import hashlib
        for package in manifest:
            for filename, expected in package["files_sha256"].items():
                with urlopen(origin + "/static/vendor/" + filename, timeout=3) as response:
                    assert response.status == 200
                    assert hashlib.sha256(response.read()).hexdigest() == expected
        with urlopen(origin + "/report/reporte_sintetico_22.md", timeout=3) as response:
            assert response.status == 200
            assert "/static/vendor/marked-9.1.6.umd.js" in response.read().decode("utf-8")
        print("HTTP sintético: Flask, CSP, informe y recursos/hash verificados; sin servicios externos.")
        return 0
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)


if __name__ == "__main__":
    raise SystemExit(main())
