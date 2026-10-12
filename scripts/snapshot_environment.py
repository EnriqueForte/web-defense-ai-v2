"""Capture and verify the full Python environment without engine imports or URLs."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.check_environment import installed_pins, read_pins

FREEZE_PIN = re.compile(r"([A-Za-z0-9][A-Za-z0-9_.-]*)==([A-Za-z0-9][A-Za-z0-9.!+_-]*)")


def freeze_pins(text):
    pins = {}
    for line in text.splitlines():
        if not line.strip():
            continue
        match = FREEZE_PIN.fullmatch(line.strip())
        if not match:
            # Do not expose raw freeze entries: direct URLs can contain credentials.
            raise ValueError("Freeze contiene un formato no fijado o una URL; no se exporta")
        name = re.sub(r"[-_.]+", "-", match[1]).lower()
        if name in pins:
            raise ValueError("Freeze contiene un paquete duplicado")
        pins[name] = match[2]
    return pins


def snapshot(output_dir):
    expected = read_pins(ROOT / "constraints-py311.txt")
    requirements = read_pins(ROOT / "requirements.txt")
    if any(expected.get(name) != value for name, value in requirements.items()):
        raise ValueError("Los requisitos difieren del contrato")
    installed = installed_pins()
    result = subprocess.run([sys.executable, "-m", "pip", "freeze", "--all"],
                            capture_output=True, text=True, timeout=60, check=True)
    frozen = freeze_pins(result.stdout)
    if frozen != installed:
        raise ValueError("Freeze y metadatos completos no coinciden")
    if frozen != expected:
        raise ValueError("El inventario completo difiere del contrato; ejecuta check_environment.py --strict")
    folder = Path(output_dir)
    if not folder.is_absolute():
        folder = ROOT / folder
    folder = folder.absolute()
    if not folder.is_relative_to(ROOT) or folder.resolve() != folder:
        raise ValueError("El inventario debe guardarse dentro del proyecto, sin enlaces")
    paths = [folder / name for name in ("requirements-freeze.txt", "environment.json")]
    if any(path.resolve() != path for path in paths):
        raise ValueError("Los archivos de inventario no pueden ser enlaces")
    freeze = "".join(f"{name}=={value}\n" for name, value in sorted(frozen.items()))
    report = {"schema_version": 1, "platform": sys.platform,
              "python": ".".join(map(str, sys.version_info[:3])),
              "installed_count": len(installed), "contract_count": len(expected),
              "differences": 0, "additional_unpinned": 0,
              "freeze_sha256": hashlib.sha256(freeze.encode("utf-8")).hexdigest(),
              "packages": dict(sorted(installed.items()))}
    folder.mkdir(parents=True, exist_ok=True)
    paths[0].write_text(freeze, encoding="utf-8", newline="\n")
    paths[1].write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"Instantánea: {len(installed)} paquetes; 0 diferencias; 0 adicionales sin fijar.")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path(".local-state/environment"))
    args = parser.parse_args()
    try:
        snapshot(args.output_dir)
        return 0
    except (OSError, ValueError, subprocess.SubprocessError):
        print("Instantánea no exportada: revisa el contrato, el freeze y la ruta local.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
