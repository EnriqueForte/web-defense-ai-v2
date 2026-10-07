"""Optional structured-lane publisher: immutable generations, one atomic pointer."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import uuid
from agents.evidence_contracts import ContractError
from agents.structured_reporting import compose
from dashboard.services.read_store import atomic_write_text
from dashboard.services.runtime_lock import exclusive_lock

GENERATION = re.compile(r"^[a-f0-9]{32}-[a-f0-9]{32}$")


def _directory(path):
    path = Path(path).absolute()
    for part in (path, *path.parents):
        if part.is_symlink() or (part.exists() and getattr(part.lstat(), "st_file_attributes", 0) & 1024):
            raise ContractError("linked_publication_path")
    return path


def publish(root, prepared, detection, classification, narrative, *, model, prompt_version):
    # Compose/validate before creating any artifact or touching the current pointer.
    result, markdown = compose(prepared, detection, classification, narrative, model=model, prompt_version=prompt_version)
    root = _directory(root)
    with exclusive_lock(root / "publication.lock"):
        generations = _directory(root / "generations")
        identifier = prepared.bundle.analysis_id + "-" + uuid.uuid4().hex
        generation = generations / identifier
        generation.mkdir(parents=True, exist_ok=False)
        body = json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2)
        atomic_write_text(generation / "result.json", body)
        atomic_write_text(generation / "report.md", markdown)
        # Nothing points at a partial generation. Old pointer remains on any error.
        manifest = {"schema_version": "1", "generation": identifier, "analysis_id": prepared.bundle.analysis_id,
                    "published_at": datetime.now(timezone.utc).isoformat(),
                    "sha256": {"result.json": hashlib.sha256(body.encode()).hexdigest(),
                               "report.md": hashlib.sha256(markdown.encode()).hexdigest()}}
        manifest_text = json.dumps(manifest, sort_keys=True)
        atomic_write_text(generation / "manifest.json", manifest_text)
        atomic_write_text(root / "current.json", manifest_text)
    return manifest


def load_current(root):
    root = _directory(root)
    try:
        manifest = json.loads(_directory(root / "current.json").read_text(encoding="utf-8"))
        if set(manifest) != {"schema_version", "generation", "analysis_id", "published_at", "sha256"} or manifest["schema_version"] != "1":
            raise ContractError("invalid_publication_manifest")
        identifier = manifest["generation"]
        if not isinstance(identifier, str) or not GENERATION.fullmatch(identifier):
            raise ContractError("invalid_generation")
        generation = _directory(root / "generations" / identifier)
        if json.loads(_directory(generation / "manifest.json").read_text(encoding="utf-8")) != manifest:
            raise ContractError("generation_manifest_mismatch")
        values = {}
        for name in ("result.json", "report.md"):
            path = _directory(generation / name)
            body = path.read_bytes()
            if hashlib.sha256(body).hexdigest() != manifest["sha256"][name]:
                raise ContractError("generation_digest_mismatch")
            values[name] = body.decode("utf-8")
        result = json.loads(values["result.json"])
        if result["analysis_id"] != manifest["analysis_id"] or not identifier.startswith(result["analysis_id"] + "-"):
            raise ContractError("generation_analysis_mismatch")
        return manifest, result, values["report.md"]
    except (OSError, ValueError, KeyError, TypeError) as error:
        if isinstance(error, ContractError):
            raise
        raise ContractError("publication_unavailable") from None
