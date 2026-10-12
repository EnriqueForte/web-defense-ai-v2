"""Plan de instalación Windows/Linux; --install explícito, sin cargar .env o motor."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def installation_plan(root=ROOT, *, platform=None, frontend=False, build=False):
    platform = platform or sys.platform
    if platform not in {"win32", "linux"}:
        raise ValueError("Solo Windows y Linux están contemplados")
    root = Path(root).resolve()
    environment = root / ".p2"
    if environment.is_symlink():
        raise ValueError("El entorno no puede ser un enlace")
    interpreter = environment / ("Scripts/python.exe" if platform == "win32" else "bin/python")
    commands = []
    if environment.exists():
        if not (environment / "pyvenv.cfg").is_file() or not interpreter.is_file():
            raise ValueError(".p2 existe y no es un entorno válido; no se sobrescribe")
    else:
        commands.append([sys.executable, "-m", "venv", str(environment)])
    commands.extend([
        [str(interpreter), "-m", "pip", "install", "-r", str(root / "requirements-bootstrap.txt")],
        [str(interpreter), "-m", "pip", "install", "-r", str(root / "requirements.txt"),
         "-c", str(root / "constraints-py311.txt")],
        [str(interpreter), "-m", "pip", "check"],
        [str(interpreter), "-B", str(root / "scripts/check_environment.py")],
    ])
    frontend_commands = []
    if build and not frontend:
        raise ValueError("El build requiere --frontend")
    if frontend:
        pnpm = shutil.which("pnpm")
        if pnpm is None:
            raise ValueError("Instala pnpm 11.19.0 y Node 24 antes de usar --frontend")
        frontend_commands = [[pnpm, "install", "--frozen-lockfile"]]
        if build:
            frontend_commands.append([pnpm, "run", "build"])
    return {"platform": platform, "cwd": str(root), "python": str(interpreter),
            "commands": commands, "frontend_commands": frontend_commands,
            "frontend_cwd": str(root / "frontend")}


def execute(plan):
    # Refuse an existing environment built with another Python before pip mutates it.
    interpreter = Path(plan["python"])
    if interpreter.exists():
        result = subprocess.run([str(interpreter), "-c",
                                 "import sys; sys.exit(0 if sys.version_info[:2] == (3, 11) else 1)"],
                                cwd=plan["cwd"], check=False)
        if result.returncode:
            raise ValueError(".p2 requiere Python 3.11; no se modifica")
    for command in plan["commands"]:
        subprocess.run(command, cwd=plan["cwd"], check=True)
    for command in plan["frontend_commands"]:
        subprocess.run(command, cwd=plan["frontend_cwd"], check=True,
                       env={**os.environ, "NEXT_TELEMETRY_DISABLED": "1", "WEB_DEFENSE_API_PORT": "5000"})


def initialize_env(root=ROOT):
    # Exclusive creation preserves an existing .env without reading its contents.
    root = Path(root)
    try:
        with (root / ".env").open("x", encoding="utf-8") as target:
            target.write((root / ".env.example").read_text(encoding="utf-8"))
    except FileExistsError:
        return "existing_preserved"
    if os.name != "nt":
        (root / ".env").chmod(0o600)
    return "created"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--install", action="store_true", help="crear/reutilizar .p2 e instalar dependencias fijadas")
    parser.add_argument("--frontend", action="store_true", help="incluir pnpm install --frozen-lockfile")
    parser.add_argument("--build", action="store_true", help="compilar la interfaz para el arranque de producción")
    parser.add_argument("--init-env", action="store_true", help="con --install: crear .env solo si no existe")
    args = parser.parse_args()
    try:
        if sys.version_info[:2] != (3, 11):
            raise ValueError("Ejecuta este instalador con Python 3.11")
        if args.init_env and not args.install:
            raise ValueError("--init-env requiere --install")
        plan = installation_plan(frontend=args.frontend, build=args.build)
        print(json.dumps(plan, indent=2, ensure_ascii=False), flush=True)
        if args.install:
            execute(plan)
            if args.init_env:
                print(initialize_env())
            if args.build:
                print("Instalación completada. Inicia con: python webdefense.py start")
        return 0
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print(f"Instalación no completada: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
