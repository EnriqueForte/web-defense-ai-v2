"""Compare installed package metadata with pinned files without importing engines."""
import argparse
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
PIN = re.compile(r'''^([A-Za-z0-9_.-]+)(?:\[[A-Za-z0-9_.,-]+\])?==([^\s;]+)(?:;\s*sys_platform\s*==\s*["']win32["'])?$''')


def read_pins(path, chain=()):
    path = Path(path).resolve()
    if path in chain:
        raise ValueError("Inclusión circular de requisitos")
    pins = {}
    for number, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("-r "):
            incoming = read_pins(path.parent / line[3:].strip(), (*chain, path))
        else:
            match = PIN.fullmatch(line)
            if match is None:
                raise ValueError(f"Requisito no fijado o no admitido: {path.name}:{number}")
            if ";" in line and sys.platform != "win32":
                continue
            name = re.sub(r"[-_.]+", "-", match[1]).lower()
            incoming = {name: match[2]}
        for name, expected in incoming.items():
            if name in pins and pins[name] != expected:
                raise ValueError(f"Versiones contradictorias para {name}")
            pins[name] = expected
    return pins


def compare(pins):
    failures = []
    for name, expected in sorted(pins.items()):
        try:
            installed = version(name)
        except PackageNotFoundError:
            installed = "ausente"
        if installed != expected:
            failures.append((name, expected, installed))
    return failures


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--requirements", type=Path, default=ROOT / "requirements.txt")
    parser.add_argument("--constraints", type=Path, default=ROOT / "constraints-py311.txt")
    args = parser.parse_args()
    try:
        pins = read_pins(args.requirements)
        constraints = read_pins(args.constraints)
        for name, expected in constraints.items():
            if name in pins and pins[name] != expected:
                raise ValueError(f"Contrato y constraints difieren para {name}")
            pins[name] = expected
        failures = compare(pins)
    except (OSError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    for name, expected, installed in failures:
        print(f"DIFERENCIA {name}: declarado={expected}; instalado={installed}")
    print(f"Entorno: {len(pins)} paquetes fijados; {len(failures)} diferencias.")
    print("Solo metadatos; no importa el motor ni contacta servicios.")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
