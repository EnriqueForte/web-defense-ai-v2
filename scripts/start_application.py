"""Supervisa Flask y Next en una terminal; lectura local, sin motor ni worker."""
import argparse
from contextlib import ExitStack
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import signal
import socket
import sys
import time
from urllib.error import URLError
from urllib.request import ProxyHandler, build_opener
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from dashboard.services.runtime_lock import AlreadyRunning, exclusive_lock
from scripts.backup_operational import checked_path
from scripts.local_runtime_profile import readiness
from scripts.process_owner import ProcessOwner


def require_free_port(port):
    try:
        with socket.socket() as probe:
            probe.bind(("127.0.0.1", port))
    except OSError:
        raise ValueError(f"El puerto {port} está ocupado. Cierra la instancia anterior antes de iniciar.") from None


def require_build(root):
    frontend = Path(root) / "frontend"
    if not (frontend / "node_modules/next/dist/bin/next").is_file() or not (frontend / ".next/BUILD_ID").is_file():
        raise ValueError("Falta compilar la interfaz. Ejecuta: python webdefense.py install")
    try:
        manifest = json.loads((frontend / ".next/routes-manifest.json").read_text(encoding="utf-8"))
        rewrites = manifest["rewrites"]
        rules = rewrites if isinstance(rewrites, list) else rewrites["afterFiles"]
        expected = {"source": "/api/v1/:path*", "destination": "http://127.0.0.1:5000/api/v1/:path*"}
        if not any(all(rule.get(key) == value for key, value in expected.items()) for rule in rules):
            raise ValueError
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        raise ValueError("El build no apunta a la API local 5000. Ejecuta: python webdefense.py install") from None


def preflight(root, mode):
    if sys.version_info[:2] != (3, 11):
        raise ValueError("El entorno .p2 debe usar Python 3.11. Revisa docs/INICIO_RAPIDO.md.")
    require_build(root)
    require_free_port(3000)
    state = readiness(root=root, profile="pilot", mode=mode, component="flask")
    if not state["ready"]:
        labels = {"environment_differences": "el entorno difiere del contrato; revisa la instalación",
                  "runtime_lock_active_or_unknown": "hay un bloqueo de operación activo",
                  "active_jobs_or_unreadable_store": "hay trabajos activos o la base no se puede leer",
                  "flask_port_in_use": "el puerto 5000 está ocupado",
                  "invalid_current_generation": "la publicación actual no es válida"}
        raise ValueError("; ".join(labels.get(code, code) for code in state["blockers"]))
    return state["plan"]


def check_processes(processes):
    for name, process in processes:
        code = process.poll()
        if code is not None:
            raise RuntimeError(f"{name} terminó antes de tiempo (código {code}). Revisa su log local.")


def wait_http(url, processes, *, health=False, timeout=45):
    # Local probes must not use a system HTTP proxy or accept a redirect to another host.
    from urllib.request import HTTPRedirectHandler

    class NoRedirect(HTTPRedirectHandler):
        def redirect_request(self, *args, **kwargs):
            return None

    opener = build_opener(ProxyHandler({}), NoRedirect())
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        check_processes(processes)
        try:
            with opener.open(url, timeout=min(2, max(.05, deadline - time.monotonic()))) as response:
                if response.status == 200:
                    if not health:
                        return
                    value = json.loads(response.read(65537))
                    if (value.get("meta", {}).get("api_version") == "1" and
                            value.get("data", {}).get("status") in {"ok", "degraded", "unavailable"}):
                        return
        except (OSError, URLError, ValueError, AttributeError):
            pass
        time.sleep(.2)
    raise RuntimeError("La lectura local no respondió a tiempo. Revisa los logs de Flask y Next.")


def serve(root, plan, node):
    root = Path(root)
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid4().hex[:8]
    directory = checked_path(root, Path(".local-state/launcher") / run_id)
    directory.mkdir(parents=True)
    env = {**os.environ, **plan["environment_overrides"], "FLASK_DEBUG": "0", "FLASK_SKIP_DOTENV": "1",
           "NEXT_TELEMETRY_DISABLED": "1", "WEB_DEFENSE_API_PORT": "5000", "NODE_ENV": "production"}
    # .env loading belongs to the application; the supervisor never reads its contents.
    with ExitStack() as stack:
        owner = ProcessOwner()
        # Register after log files so cleanup runs before closing handles on Windows.
        flask_log = stack.enter_context((directory / "flask.log").open("wb"))
        next_log = stack.enter_context((directory / "next.log").open("wb"))
        stack.callback(owner.close)
        print(f"Iniciando consola. Logs locales: {directory}", flush=True)
        processes = [("Flask", owner.spawn(plan["commands"]["flask"], cwd=root, env=env, log=flask_log))]
        wait_http("http://127.0.0.1:5000/api/v1/salud", processes, health=True)
        command = [node, str(root / "frontend/node_modules/next/dist/bin/next"),
                   "start", "--hostname", "127.0.0.1", "--port", "3000"]
        processes.append(("Next", owner.spawn(command, cwd=root / "frontend", env=env, log=next_log)))
        wait_http("http://127.0.0.1:3000/api/v1/salud", processes, health=True)
        wait_http("http://127.0.0.1:3000/", processes)
        check_processes(processes)
        print("Consola lista: http://127.0.0.1:3000\n"
              "Lectura local. Una instalación nueva puede indicar fuentes incompletas.\n"
              "Deja esta terminal abierta; Ctrl+C detiene Flask y Next.", flush=True)
        while True:
            check_processes(processes)
            time.sleep(.5)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--node", required=True)
    parser.add_argument("--mode", choices=("legacy", "structured"), default="legacy")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    def interrupted(*_):
        raise KeyboardInterrupt

    previous = {signal.SIGTERM: signal.signal(signal.SIGTERM, interrupted)}
    if hasattr(signal, "SIGBREAK"):
        previous[signal.SIGBREAK] = signal.signal(signal.SIGBREAK, interrupted)
    try:
        if args.check:
            preflight(ROOT, args.mode)
            print("Preparado: entorno, build y puertos comprobados. Ejecuta: python webdefense.py start")
        else:
            lock = checked_path(ROOT, ".local-state/application.lock")
            with exclusive_lock(lock):
                plan = preflight(ROOT, args.mode)
                serve(ROOT, plan, args.node)
        return 0
    except KeyboardInterrupt:
        print("Consola detenida.")
        return 0
    except (AlreadyRunning, OSError, ValueError, RuntimeError) as error:
        print(f"No se pudo iniciar: {error}", file=sys.stderr)
        return 1
    finally:
        for signum, handler in previous.items():
            signal.signal(signum, handler)


if __name__ == "__main__":
    raise SystemExit(main())
