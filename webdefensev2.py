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
    parser.add_argument(
        "--enable-manual", action="store_true",
        help="habilitar solicitudes de análisis desde V2 e iniciar su ejecutor; no solicita un análisis",
    )
    args = parser.parse_args(argv)
    if args.action == "install" and args.lab_mode is not None:
        parser.error("--lab-mode se utiliza con start o check, no con install.")
    if args.action == "install" and args.enable_manual:
        parser.error("--enable-manual se utiliza con start o check, no con install.")

    # Reuse the existing prerequisites, supervisor and cleanup; help needs only argparse.
    from webdefense import main as launch

    if args.action == "install":
        return launch(["install"])

    mode = args.lab_mode or "corrected"
    label = "corregido" if mode == "corrected" else "vulnerable"
    print(f"Web Defense AI V2 + Puerto Umbral · fuente V2: modo {label}.", flush=True)
    command = [
        args.action, "--mode", "structured", "--with-puerto-umbral", "--lab-mode", mode,
    ]
    if args.enable_manual:
        command.append("--enable-manual")
    return launch(command)


if __name__ == "__main__":
    raise SystemExit(main())
