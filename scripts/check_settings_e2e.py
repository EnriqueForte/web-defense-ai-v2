"""Build a separate frontend and run Chromium against synthetic Flask settings."""

from contextlib import ExitStack
import json
import os
from pathlib import Path
import shutil
import socket
import sys
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.process_owner import ProcessOwner
from scripts.start_application import wait_http, require_free_port


def free_port():
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        return listener.getsockname()[1]


def main():
    node = shutil.which("node")
    if not node:
        raise RuntimeError("Node no disponible")
    frontend = ROOT / "frontend"
    modules = frontend / "node_modules"
    next_cli = modules / "next/dist/bin/next"
    playwright_cli = modules / "@playwright/test/cli.js"
    if not next_cli.is_file() or not playwright_cli.is_file():
        raise RuntimeError("Instala las dependencias frontend y Chromium antes del ensayo")
    # Preserve normal .next and avoid loading any frontend dotenv file.
    parent = ROOT / ".local-state/settings-e2e"
    if parent.resolve() != parent:
        raise RuntimeError("El estado E2E no puede ser un enlace")
    folder = parent / uuid4().hex
    staged = folder / "frontend"
    staged.mkdir(parents=True)
    for name in ("package.json", "pnpm-lock.yaml", "next.config.ts", "tsconfig.json", "next-env.d.ts", "postcss.config.mjs"):
        shutil.copy2(frontend / name, staged / name)
    for name in ("src", "public"):
        shutil.copytree(frontend / name, staged / name)
    if os.name == "nt":
        import _winapi
        _winapi.CreateJunction(str(modules.resolve()), str(staged / "node_modules"))
    else:
        (staged / "node_modules").symlink_to(modules.resolve(), target_is_directory=True)
    api_port, ui_port = free_port(), free_port()
    while api_port == ui_port or api_port in (3000, 5000) or ui_port in (3000, 5000):
        api_port, ui_port = free_port(), free_port()
    for port in (api_port, ui_port):
        require_free_port(port)
    api_url, ui_url = f"http://127.0.0.1:{api_port}", f"http://127.0.0.1:{ui_port}"
    env = {**os.environ, "PYTHON_DOTENV_DISABLED": "1", "PYTHONIOENCODING": "utf-8",
           "GROQ_API_KEY": "", "OPENROUTER_API_KEY": "", "ANALYSIS_MANUAL_ENABLED": "0",
           "NOTIFICATION_DESTINATIONS": "", "NEXT_TELEMETRY_DISABLED": "1",
           "WEB_DEFENSE_API_PORT": str(api_port), "WEB_DEFENSE_E2E_URL": ui_url,
           "WEB_DEFENSE_E2E_API": api_url, "WEB_DEFENSE_E2E_RESULTS": str(folder / "results")}
    with ExitStack() as stack:
        build_log = stack.enter_context((folder / "build.log").open("wb"))
        api_log = stack.enter_context((folder / "flask.log").open("wb"))
        ui_log = stack.enter_context((folder / "next.log").open("wb"))
        owner = ProcessOwner()
        stack.callback(owner.close)
        build = owner.spawn([node, str(next_cli), "build", "--webpack"], cwd=staged, env=env, log=build_log)
        if build.wait(timeout=180) != 0:
            raise RuntimeError(f"Build E2E falló; consulta {folder / 'build.log'}")
        api = owner.spawn([sys.executable, "-B", str(ROOT / "tests/serve_settings_fixture.py"),
            "--base", str(folder / "data"), "--port", str(api_port), "--ui-port", str(ui_port)],
            cwd=ROOT, env=env, log=api_log)
        processes = [("Flask fixture", api)]
        wait_http(api_url + "/api/v1/salud", processes, health=True)
        ui = owner.spawn([node, str(next_cli), "start", "--hostname", "127.0.0.1", "--port", str(ui_port)],
                         cwd=staged, env=env, log=ui_log)
        processes.append(("Next E2E", ui))
        wait_http(ui_url + "/api/v1/salud", processes, health=True)
        wait_http(ui_url + "/", processes)
        result = owner.spawn([node, str(playwright_cli), "test"], cwd=frontend, env=env, log=sys.stdout)
        code = result.wait(timeout=240)
    # Require cleanup by the owner before declaring the run complete.
    for port in (api_port, ui_port):
        require_free_port(port)
    (folder / "result.json").write_text(json.dumps({"exit_code": code, "api_port": api_port,
        "ui_port": ui_port, "shutdown": "ports_free", "data": "synthetic_only"}, indent=2), encoding="utf-8")
    print(f"Configuración E2E: salida {code}; cierre con puertos libres. Recibos: {folder}")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
