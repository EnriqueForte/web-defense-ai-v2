"""Comprueba sintaxis de web-defense-ai V2 sin importar ni ejecutar sus modulos."""

import ast
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    paths = list(root.glob("*.py"))
    for folder in ("agents", "config", "dashboard", "scripts", "tests"):
        paths.extend((root / folder).rglob("*.py"))

    failures = 0
    for path in sorted(set(paths)):
        try:
            ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))
        except (SyntaxError, UnicodeError, OSError) as error:
            failures += 1
            print(f"ERROR {path.relative_to(root)}: {error}")

    print(f"web-defense-ai V2: {len(set(paths))} archivos; {failures} errores de sintaxis.")
    print("Esta comprobacion no ejecuta pruebas funcionales ni el motor de IA.")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
