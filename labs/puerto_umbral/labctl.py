"""Explicit commands for the local laboratory. Never starts on import."""
import argparse
import json
from lab import controller

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prepare", "serve", "inspect", "stop", "preflight", "check-suite", "check-boundary"))
    parser.add_argument("--allow-automated-checks", action="store_true", help="Autorización explícita de una comprobación automatizada; no es el recorrido de revisión manual")
    args = parser.parse_args()
    if args.command.startswith("check-") and not args.allow_automated_checks:
        parser.error("Las comprobaciones automáticas están desactivadas. Revisa los escenarios manualmente en la web.")
    operations = {"prepare": controller.prepare, "serve": controller.serve,
                  "inspect": controller.inspect_boundary, "stop": controller.stop, "preflight": controller.preflight,
                  "check-suite": controller.check_suite}
    if args.command == "check-boundary":
        from lab.verify import check_boundary
        operations["check-boundary"] = check_boundary
    if args.command == "inspect":
        result = operations[args.command]()
    else:
        with controller.ProcessLock():
            result = operations[args.command]()
    if result is not None:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    if args.command == "check-suite" and result["passed"] != result["total"]:
        raise SystemExit(1)
