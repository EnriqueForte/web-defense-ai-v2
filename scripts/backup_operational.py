"""Local verified backup of known legacy/pilot paths, including SQLite snapshots.

Never loads dotenv, copies credentials, deletes source data or restores in place.
"""
import argparse
from contextlib import ExitStack, closing
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sqlite3
import stat
import sys
import time
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from dashboard.services.read_store import capture_file
from dashboard.services.runtime_lock import AlreadyRunning, exclusive_lock
from dashboard.services.structured_publication import GENERATION

PROFILES = {
    "legacy": {"log": "logs/access.log", "reports": "reports", "db": ".local-state/analysis.sqlite3"},
    "pilot": {"log": ".local-state/dvwa-lab/access.log", "reports": ".local-state/phase6-pilot/reports",
              "db": ".local-state/phase6-pilot/analysis.sqlite3"},
}


def checked_path(root, relative):
    root = Path(root).absolute()
    candidate = root / relative
    if not candidate.resolve().is_relative_to(root.resolve()):
        raise ValueError("Ruta fuera de la instalación")
    for part in (root, *candidate.relative_to(root).parents, candidate.relative_to(root)):
        path = part if part == root else root / part
        if path.exists() or path.is_symlink():
            attributes = path.lstat()
            if path.is_symlink() or getattr(attributes, "st_file_attributes", 0) & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0):
                raise ValueError("No se respaldan enlaces ni puntos de reanálisis")
    return candidate


def collect_sources(root, profiles):
    paths, missing = {}, []
    for profile in profiles:
        definition = PROFILES[profile]
        for key in ("log", "db"):
            relative = definition[key]
            path = checked_path(root, relative)
            if path.is_file():
                paths[relative] = "sqlite" if key == "db" else "file"
            else:
                missing.append(relative)
        report_dir = checked_path(root, definition["reports"])
        if not report_dir.exists():
            missing.append(definition["reports"])
        else:
            if not report_dir.is_dir():
                raise ValueError("La ruta de reportes no es un directorio")
            # Only report artifacts; never arbitrary files or .env in this tree.
            for path in report_dir.rglob("*.md"):
                relative = path.relative_to(root).as_posix()
                if checked_path(root, relative).is_file():
                    paths[relative] = "file"
            structured = checked_path(root, definition["reports"] + "/structured")
            if structured.exists():
                for path in structured.rglob("*.json"):
                    local = path.relative_to(structured)
                    allowed = (local.as_posix() == "current.json" or
                               (len(local.parts) == 3 and local.parts[0] == "generations" and
                                GENERATION.fullmatch(local.parts[1]) and
                                local.parts[2] in {"manifest.json", "result.json"}))
                    relative = path.relative_to(root).as_posix()
                    if allowed and checked_path(root, relative).is_file():
                        paths[relative] = "file"
    return paths, sorted(set(missing))


def snapshot_sqlite(source, target):
    deadline = time.monotonic() + 30
    def progress(_status, _remaining, _total):
        if time.monotonic() > deadline:
            raise TimeoutError("El respaldo SQLite excedió su presupuesto")
    with closing(sqlite3.connect(source.resolve().as_uri() + "?mode=ro", uri=True, timeout=2)) as origin:
        origin.execute("BEGIN")
        if origin.execute("SELECT count(*) FROM jobs WHERE status IN ('queued','running')").fetchone()[0]:
            raise ValueError("No se respalda un coordinador con trabajos activos")
        with closing(sqlite3.connect(target)) as destination:
            origin.backup(destination, pages=64, progress=progress, sleep=.05)
            if destination.execute("PRAGMA integrity_check").fetchall() != [("ok",)]:
                raise ValueError("Integridad SQLite no verificada")


def verify_restore(archive, manifest, destination):
    """Restore only to a new, isolated directory; reject tampering/path escapes."""
    destination = Path(destination)
    if destination.exists():
        raise ValueError("La restauración requiere un directorio nuevo")
    destination.mkdir(parents=True)
    with ZipFile(archive) as zipped:
        names = zipped.namelist()
        if len(names) != len(set(names)) or set(names) != set(manifest["files"]):
            raise ValueError("Contenido del archivo distinto del manifiesto")
        for name in names:
            # Portable ZIP paths; never honor Windows drive/backslash names.
            if "\\" in name or ":" in name or Path(name).is_absolute() or ".." in Path(name).parts:
                raise ValueError("Ruta de restauración inválida")
            target = (destination / name).resolve()
            if not target.is_relative_to(destination.resolve()):
                raise ValueError("Destino fuera de restauración")
            content = zipped.read(name)
            expected = manifest["files"][name]
            if len(content) != expected["bytes"] or hashlib.sha256(content).hexdigest() != expected["sha256"]:
                raise ValueError("SHA-256 de restauración incorrecto")
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)
            if expected["kind"] == "sqlite":
                with closing(sqlite3.connect(target.as_uri() + "?mode=ro", uri=True)) as db:
                    if db.execute("PRAGMA integrity_check").fetchall() != [("ok",)]:
                        raise ValueError("SQLite restaurado inválido")
            if hashlib.sha256(target.read_bytes()).hexdigest() != expected["sha256"]:
                raise ValueError("Archivo restaurado distinto de la copia")


def backup(root=ROOT, profiles=("legacy", "pilot")):
    root = Path(root).absolute()
    paths, missing = collect_sources(root, profiles)
    if not paths:
        raise ValueError("No hay fuentes para respaldar")
    backup_root = checked_path(root, ".local-backups")
    stamp = datetime.now(timezone.utc).strftime("operational-%Y%m%dT%H%M%S%fZ")
    destination = backup_root / stamp
    manifest = {"schema": "web-defense-ai.backup.v1", "profiles": list(profiles),
                "created_at": datetime.now(timezone.utc).isoformat(), "missing": missing,
                "verified": False, "files": {}}
    with ExitStack() as locks:
        for profile in sorted(profiles):
            db = checked_path(root, PROFILES[profile]["db"])
            for suffix in (".cycle.lock", ".engine.lock"):
                locks.enter_context(exclusive_lock(db.with_suffix(suffix)))
            structured = checked_path(root, PROFILES[profile]["reports"] + "/structured")
            if structured.exists():
                locks.enter_context(exclusive_lock(structured / "publication.lock"))
        paths, missing = collect_sources(root, profiles)
        if not paths:
            raise ValueError("No hay fuentes para respaldar")
        manifest["missing"] = missing
        destination.mkdir(parents=True, exist_ok=False)
        staging = destination / "sqlite-snapshots"
        staging.mkdir()
        temporary_archive = destination / "operational.zip.tmp"
        try:
            with ZipFile(temporary_archive, "w", ZIP_DEFLATED) as zipped:
                for index, (relative, kind) in enumerate(sorted(paths.items())):
                    source = checked_path(root, relative)
                    if kind == "sqlite":
                        copy = staging / f"snapshot-{index}.sqlite3"
                        snapshot_sqlite(source, copy)
                        content = copy.read_bytes()
                    else:
                        capture = capture_file(source)
                        if capture.status != "available":
                            raise ValueError("Una fuente cambió o no pudo leerse")
                        content = capture.content
                    manifest["files"][relative] = {"sha256": hashlib.sha256(content).hexdigest(),
                                                   "bytes": len(content), "kind": kind}
                    zipped.writestr(relative, content)
            verify_restore(temporary_archive, manifest, destination / "restore-check")
            manifest["verified"] = True
            temporary_archive.rename(destination / "operational.zip")
        finally:
            # Preserve any failed artifacts with verified=false, never delete sources.
            (destination / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return destination, manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", choices=("legacy", "pilot", "all"), default="all")
    parser.add_argument("--list", action="store_true", help="mostrar solo rutas seleccionadas, sin leer contenidos")
    args = parser.parse_args()
    profiles = tuple(PROFILES) if args.profile == "all" else (args.profile,)
    try:
        if args.list:
            paths, missing = collect_sources(ROOT, profiles)
            print(json.dumps({"sources": paths, "missing": missing}, indent=2))
        else:
            destination, manifest = backup(profiles=profiles)
            print(json.dumps({"destination": str(destination), "files": len(manifest["files"]),
                              "verified": manifest["verified"], "missing": manifest["missing"]}))
    except (OSError, ValueError, sqlite3.Error, TimeoutError, AlreadyRunning) as error:
        # Do not log source content or exception internals from SQLite/files.
        print(f"Respaldo no completado ({type(error).__name__}); conserva las fuentes y revisa su estado.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
