"""Entrada de usuario: python webdefense.py install|start|check (Windows/Linux)."""
import argparse
from contextlib import ExitStack, contextmanager
from pathlib import Path
import re
import shutil
import signal
import errno
import sqlite3
import subprocess
import sys
from scripts.local_port import probe_port

ROOT = Path(__file__).resolve().parent
GUIDE = "docs/INICIO_RAPIDO.md"


def install_lock_path(root):
    root = Path(root).resolve()
    state = root / ".local-state"
    lock = state / "application.lock"
    if state.resolve() != state or lock.resolve() != lock:
        raise ValueError("El estado local de instalación no puede ser un enlace.")
    return lock


def require_stopped():
    for port in (5000, 3000):
        try:
            probe_port(port)
        except OSError as error:
            if error.errno == errno.EADDRINUSE:
                raise ValueError(f"El puerto {port} está ocupado. Detén la consola antes de instalar.") from None
            raise ValueError(f"No se pudo comprobar el puerto {port}. Revisa los permisos de red local.") from None


@contextmanager
def installation_locks(root):
    from dashboard.services.runtime_lock import exclusive_lock
    root = Path(root).resolve()
    with ExitStack() as stack:
        stack.enter_context(exclusive_lock(install_lock_path(root)))
        for relative in (".local-state/analysis.sqlite3", ".local-state/phase6-pilot/analysis.sqlite3"):
            db = root / relative
            if db.resolve() != db:
                raise ValueError("La base local no puede ser un enlace durante la instalación.")
            for component in ("worker", "cycle", "engine"):
                lock = db.with_suffix(f".{component}.lock")
                if lock.resolve() != lock:
                    raise ValueError("El bloqueo local no puede ser un enlace.")
                if lock.exists():
                    if lock.stat().st_size == 0:
                        raise ValueError("Hay un bloqueo local desconocido. Revisa la operación anterior.")
                    stack.enter_context(exclusive_lock(lock))
            if db.is_file():
                try:
                    connection = sqlite3.connect(db.as_uri() + "?mode=ro", uri=True, timeout=1)
                    try:
                        active = connection.execute("SELECT count(*) FROM jobs WHERE status IN ('queued','running')").fetchone()[0]
                    finally:
                        connection.close()
                except sqlite3.Error:
                    raise ValueError("No se pudo comprobar la base de trabajos; instalación detenida.") from None
                if active:
                    raise ValueError("Hay análisis pendientes o activos. Finalízalos antes de instalar.")
        yield


def output(command):
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=15)
        return result.stdout.strip() if result.returncode == 0 else ""
    except (OSError, subprocess.TimeoutExpired):
        return ""


def python_command():
    candidates = [[sys.executable]]
    for name in ("python3.11", "python3", "python"):
        executable = shutil.which(name)
        if executable:
            candidates.append([executable])
    if sys.platform == "win32" and shutil.which("py"):
        candidates.append([shutil.which("py"), "-3.11"])
    for candidate in candidates:
        version = output(candidate + ["-c", "import sys, venv, ensurepip; print('%s.%s' % sys.version_info[:2])"])
        if version == "3.11":
            return candidate
    raise ValueError("Falta Python 3.11 con venv y ensurepip. Consulta " + GUIDE)


def frontend_tools(*, installing=False):
    node = shutil.which("node")
    version = output([node, "--version"]) if node else ""
    match = re.fullmatch(r"v(\d+)\.\d+\.\d+", version)
    if not match or int(match[1]) < 24:
        raise ValueError("Se necesita Node 24 o posterior. Consulta " + GUIDE)
    if installing:
        pnpm = shutil.which("pnpm")
        if not pnpm or output([pnpm, "--version"]) != "11.19.0":
            raise ValueError("Se necesita pnpm 11.19.0. Con Node preparado: npm install --global pnpm@11.19.0")
    return node


def environment_python(root=ROOT):
    return Path(root) / ".p2" / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Instala y arranca web-defense-ai V2 en tu equipo.")
    parser.add_argument("action", choices=("install", "start", "check"))
    parser.add_argument("--mode", choices=("legacy", "structured"), default="legacy",
                        help="fuente de informes al arrancar (predeterminado: legacy)")
    args = parser.parse_args(argv)
    try:
        if sys.platform not in {"win32", "linux"}:
            raise ValueError("Esta entrada admite Windows y Linux.")
        if args.action == "install":
            python = python_command()
            frontend_tools(installing=True)
            with installation_locks(ROOT):
                require_stopped()
                print("Requisitos disponibles. Preparando entorno, dependencias e interfaz...", flush=True)
                return subprocess.call(python + ["-B", str(ROOT / "scripts/setup_installation.py"),
                                       "--install", "--frontend", "--build", "--init-env"], cwd=ROOT)
        python = environment_python()
        if not python.is_file():
            raise ValueError("Falta la instalación. Ejecuta primero: python webdefense.py install")
        node = frontend_tools()
        command = [str(python), "-B", str(ROOT / "scripts/start_application.py"),
                   "--node", node, "--mode", args.mode]
        if args.action == "check":
            command.append("--check")
        # The supervisor owns cleanup. Ignore Ctrl+C here until it has stopped its children.
        process = subprocess.Popen(command, cwd=ROOT)
        previous_term = signal.signal(signal.SIGTERM, lambda *_: process.terminate())
        previous_break = None
        if hasattr(signal, "SIGBREAK"):
            previous_break = signal.signal(signal.SIGBREAK, lambda *_: None)
        while True:
            try:
                result = process.wait()
                signal.signal(signal.SIGTERM, previous_term)
                if previous_break is not None:
                    signal.signal(signal.SIGBREAK, previous_break)
                return result
            except KeyboardInterrupt:
                continue
    except (OSError, ValueError, RuntimeError) as error:
        print(f"No se pudo continuar: {error}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("Instalación interrumpida.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
