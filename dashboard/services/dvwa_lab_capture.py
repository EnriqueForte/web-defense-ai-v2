"""Captura acotada del access log del contenedor DVWA local de fase 6."""

from pathlib import Path
import re
import subprocess
import sys

from dashboard.services.read_store import atomic_write_text


CONTAINER_NAME = "web-defense-ai-v2-lab-dvwa"
DEFAULT_DESTINATION = (Path(__file__).resolve().parents[2]
                       / ".local-state" / "dvwa-lab" / "access.log")
ACCESS_LINE = re.compile(r"^\S+ \S+ \S+ \[[^\]]+\] ")


def capture_access_log(destination: Path = DEFAULT_DESTINATION, *, run=None) -> int | None:
    """Copy Apache access lines from Docker stdout without replacing on failure."""
    if run is None:
        run = subprocess.run
    try:
        result = run(
            ["docker", "logs", "--timestamps=false", CONTAINER_NAME],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=60,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None

    if result.returncode != 0:
        return None

    lines = [line for line in result.stdout.splitlines() if ACCESS_LINE.match(line)]
    if not lines:
        return None

    atomic_write_text(Path(destination), "\n".join(lines) + "\n")
    return len(lines)


def main() -> int:
    count = capture_access_log()
    if count is None:
        print("No se pudo capturar el access log de DVWA o no contiene accesos.", file=sys.stderr)
        return 1
    print(f"Log de laboratorio capturado en .local-state\\dvwa-lab\\access.log ({count} líneas)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
