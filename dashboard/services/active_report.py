"""Shared current-report selector for Flask and the coordinator."""
from pathlib import Path
from agents.evidence_contracts import ContractError
from agents.structured_engine import engine_mode
from dashboard.services.read_store import CapturedFile, capture_file, inspect_file
from dashboard.services.structured_publication import load_current, _directory


def capture_current(report_root):
    return capture_current_details(report_root)[0]


def capture_current_details(report_root):
    root = Path(report_root)
    try:
        if engine_mode() == "legacy":
            return capture_file(root / "reporte_seguridad.md"), None
        pointer = _directory(root / "structured" / "current.json")
        try:
            pointer.lstat()
        except FileNotFoundError:
            # No current publication yet. An existing invalid pointer or a
            # linked path must still reach the error state below.
            return CapturedFile(pointer, None, "missing"), None
        manifest, result, markdown = load_current(root / "structured")
        path = root / "structured" / "generations" / manifest["generation"] / "report.md"
        captured = capture_file(path)
        if captured.status == "available" and captured.text == markdown:
            return captured, result
    except (ContractError, OSError):
        pass
    # Never disguise an invalid structured publication as the previous legacy report.
    return CapturedFile(root / "structured" / "current.json", None, "error"), None


def inspect_current(report_root):
    try:
        if engine_mode() == "legacy":
            return inspect_file(Path(report_root) / "reporte_seguridad.md")
    except ContractError:
        pass
    captured = capture_current(report_root)
    return {"status": captured.status, "modified_at": captured.modified_at, "size_bytes": captured.size}
