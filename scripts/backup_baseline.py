"""Copia local de logs/reportes y restauración aislada verificada por SHA-256.

No lee .env, no borra datos y no sobrescribe copias anteriores.
"""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]


def main():
    destination = ROOT / ".local-backups" / datetime.now(timezone.utc).strftime("phase0-data-%Y%m%dT%H%M%S%fZ")
    destination.mkdir(parents=True, exist_ok=False)
    manifest = {}
    with ZipFile(destination / "operational.zip", "w", ZIP_DEFLATED) as archive:
        for folder in (ROOT / "logs", ROOT / "reports"):
            if folder.is_symlink():
                raise ValueError("No se respaldan directorios enlazados")
            for file in sorted(folder.rglob("*")):
                if not file.is_file():
                    continue
                resolved = file.resolve()
                if file.is_symlink() or not resolved.is_relative_to(folder.resolve()):
                    raise ValueError("Archivo enlazado fuera de su directorio")
                if file.suffix not in {".log", ".md"}:
                    continue
                relative = file.relative_to(ROOT).as_posix()
                content = file.read_bytes()
                manifest[relative] = hashlib.sha256(content).hexdigest()
                archive.writestr(relative, content)
    restored = destination / "restored"
    restored.mkdir()
    with ZipFile(destination / "operational.zip") as archive:
        for member in archive.infolist():
            target = (restored / member.filename).resolve()
            if not target.is_relative_to(restored.resolve()):
                raise ValueError("Destino fuera de la restauración")
            target.parent.mkdir(parents=True, exist_ok=True)
            content = archive.read(member)
            target.write_bytes(content)
            if hashlib.sha256(target.read_bytes()).hexdigest() != manifest[member.filename]:
                raise ValueError("Restauración distinta del respaldo")
    (destination / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"{len(manifest)} archivos restaurados y verificados. Copia local: {destination.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
