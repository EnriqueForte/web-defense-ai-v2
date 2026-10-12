"""Smoke del lanzador en una copia sin datos operativos; HTTP local y cierre."""
import argparse
import json
import os
from pathlib import Path
import signal
import sys
import time
from urllib.request import ProxyHandler, build_opener

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.process_owner import ProcessOwner
from scripts.start_application import require_free_port


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--isolated-root", required=True, type=Path)
    args = parser.parse_args()
    root = args.isolated_root.resolve()
    for relative in (".local-state/analysis.sqlite3", ".local-state/phase6-pilot/analysis.sqlite3",
                     ".local-state/dvwa-lab/access.log", "logs/access.log"):
        if (root / relative).exists():
            raise SystemExit("Usa una copia de pruebas sin datos operativos.")
    require_free_port(5000)
    require_free_port(3000)
    folder = root / ".local-state/launcher-smoke"
    folder.mkdir(parents=True, exist_ok=True)
    env = {**os.environ, "GROQ_API_KEY": "", "OPENROUTER_API_KEY": "", "PYTHON_DOTENV_DISABLED": "1",
           "CREWAI_TRACING_ENABLED": "false", "ANALYSIS_MANUAL_ENABLED": "0", "NOTIFICATION_DESTINATIONS": ""}
    with (folder / "console.log").open("wb") as log:
        owner = ProcessOwner()
        try:
            process = owner.spawn([sys.executable, "-B", str(root / "webdefense.py"), "start"],
                                  cwd=root, env=env, log=log)
            deadline = time.monotonic() + 60
            while time.monotonic() < deadline:
                if process.poll() is not None:
                    raise RuntimeError("El lanzador terminó antes de estar listo; revisa console.log")
                console = (folder / "console.log").read_text(encoding="utf-8", errors="replace")
                if "Consola lista:" in console:
                    break
                time.sleep(.2)
            else:
                raise RuntimeError("El lanzador no confirmó el arranque a tiempo")
            opener = build_opener(ProxyHandler({}))
            results = {}
            for port in (5000, 3000):
                with opener.open(f"http://127.0.0.1:{port}/api/v1/salud", timeout=5) as response:
                    value = json.load(response)
                    assert response.status == 200 and value["meta"]["api_version"] == "1"
                    assert value["data"]["executor"] == "offline"
                    results[str(port)] = {"http": response.status, "health": value["data"]["status"]}
            if os.name == "nt":
                process.send_signal(signal.CTRL_BREAK_EVENT)
            else:
                os.killpg(process.pid, signal.SIGINT)
            code = process.wait(timeout=15)
            assert code == 0, f"El cierre devolvió {code}"
            # Verify cleanup before the outer test-owner can perform its fallback cleanup.
            require_free_port(5000)
            require_free_port(3000)
            results["shutdown"] = "ports_free"
            (folder / "result.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
            print("Lanzador: API directa/proxy 200, ejecutor offline y cierre con puertos libres.")
        finally:
            owner.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
