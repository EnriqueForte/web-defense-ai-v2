"""Lecturas estables y publicación atómica de texto Markdown."""
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import os
from pathlib import Path
import subprocess
import tempfile


@dataclass(frozen=True)
class CapturedFile:
    path: Path
    content: bytes | None
    status: str
    modified_ns: int | None = None
    changed_ns: int | None = None
    size: int | None = None
    inode: int | None = None

    @property
    def text(self) -> str | None:
        return self.content.decode("utf-8", errors="replace") if self.content is not None else None

    @property
    def digest(self) -> str | None:
        return hashlib.sha256(self.content).hexdigest() if self.content is not None else None

    @property
    def modified_at(self) -> str | None:
        if self.modified_ns is None:
            return None
        value = datetime.fromtimestamp(self.modified_ns / 1_000_000_000, timezone.utc)
        return value.isoformat(timespec="seconds").replace("+00:00", "Z")

    @property
    def file_id(self) -> str | None:
        if self.content is None or self.modified_ns is None:
            return None
        identity = f"{self.path.name}\0{self.modified_ns}\0{self.changed_ns}\0{self.size}\0{self.inode}".encode()
        return hashlib.sha256(identity).hexdigest()


def capture_file(path: Path, attempts: int = 3) -> CapturedFile:
    """Captura bytes que no cambian durante la lectura; no propaga errores de I/O al cliente."""
    path = Path(path)
    for _ in range(attempts):
        try:
            before = path.stat()
            content = path.read_bytes()
            after = path.stat()
        except FileNotFoundError:
            return CapturedFile(path, None, "missing")
        except OSError:
            return CapturedFile(path, None, "error")

        stable = (before.st_size == after.st_size == len(content)
                  and before.st_mtime_ns == after.st_mtime_ns
                  and before.st_ctime_ns == after.st_ctime_ns
                  and before.st_ino == after.st_ino)
        if stable:
            return CapturedFile(path, content, "available", after.st_mtime_ns,
                                after.st_ctime_ns, after.st_size, after.st_ino)
    return CapturedFile(path, None, "changing")


def inspect_file(path: Path) -> dict:
    """Consulta solo metadatos para health checks ligeros."""
    path = Path(path)
    try:
        stat = path.stat()
        if not path.is_file():
            return {"status": "error", "modified_at": None, "size_bytes": None}
        modified = datetime.fromtimestamp(stat.st_mtime_ns / 1_000_000_000, timezone.utc)
        return {"status": "available", "modified_at": modified.isoformat(timespec="seconds").replace("+00:00", "Z"),
                "size_bytes": stat.st_size}
    except FileNotFoundError:
        return {"status": "missing", "modified_at": None, "size_bytes": None}
    except OSError:
        return {"status": "error", "modified_at": None, "size_bytes": None}


def atomic_write_text(path: Path, content: str) -> None:
    """Reemplaza un texto completo en el mismo sistema de archivos o conserva el anterior."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", newline="", dir=path.parent,
            prefix=f".{path.name}.", suffix=".tmp", delete=False,
        ) as temp_file:
            temp_path = Path(temp_file.name)
            temp_file.write(content)
            temp_file.flush()
            os.fsync(temp_file.fileno())
        os.replace(temp_path, path)
    finally:
        if temp_path is not None and temp_path.exists():
            temp_path.unlink()


def run_atomic_copy(command: list[str], target: Path, timeout: int = 30) -> subprocess.CompletedProcess:
    """Ejecuta una copia externa a un temporal y publica el fichero con replace."""
    target = Path(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(dir=target.parent, prefix=f".{target.name}.",
                                         suffix=".tmp", delete=False) as temp_file:
            temp_path = Path(temp_file.name)
        result = subprocess.run([*command, str(temp_path)], capture_output=True,
                                text=True, timeout=timeout)
        if result.returncode == 0:
            if not temp_path.is_file() or temp_path.is_symlink():
                return subprocess.CompletedProcess(result.args, 1, result.stdout,
                                                   "La copia no produjo un archivo regular.")
            os.replace(temp_path, target)
        return result
    finally:
        if temp_path is not None and temp_path.exists():
            temp_path.unlink()
