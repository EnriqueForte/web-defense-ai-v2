"""Entrada conjunta: python3 webdefensev2.py [start|check|install]."""
import argparse


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Inicia Web Defense AI V2 y Puerto Umbral desde una terminal.",
        epilog="Deja la terminal abierta. Ctrl+C cierra los servicios propios y conserva los datos.",
    )
    parser.add_argument(
        "action", nargs="?", choices=("start", "check", "install"), default="start",
        help="start: iniciar ambas apps (predeterminado); check: comprobar sin iniciar; install: preparar la instalación",
    )
    parser.add_argument(
        "--lab-mode", choices=("corrected", "vulnerable"),
        help="fuente de Puerto Umbral que lee V2 (predeterminado: corrected); se preparan ambos portales",
    )
    args = parser.parse_args(argv)
    if args.action == "install" and args.lab_mode is not None:
        parser.error("--lab-mode se utiliza con start o check, no con install.")

    # Reuse the existing prerequisites, supervisor and cleanup; help needs only argparse.
    from webdefense import main as launch

    if args.action == "install":
        return launch(["install"])

    mode = args.lab_mode or "corrected"
    label = "corregido" if mode == "corrected" else "vulnerable"
    print(f"Web Defense AI V2 + Puerto Umbral · fuente V2: modo {label}.", flush=True)
    return launch([
        args.action, "--mode", "structured", "--with-puerto-umbral", "--lab-mode", mode,
    ])


if __name__ == "__main__":
    raise SystemExit(main())
