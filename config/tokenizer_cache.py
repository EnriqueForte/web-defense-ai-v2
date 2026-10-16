"""Verified bundled BPE resources for LiteLLM, without downloads."""
import hashlib
from importlib.metadata import PackageNotFoundError, distribution
import os
from pathlib import Path
import stat
import tempfile
from threading import Lock

ROOT = Path(__file__).resolve().parents[1]
CACHE_KEY = "9b5ad71b2ce5302211f9c61530b329a4922fc6a4"
SHA256 = "223921b76ee99bde995b7ff738513eef100fb51d18c93597a113bcffe865b2a7"
RESOURCE_DIR = "litellm/litellm_core_utils/tokenizers/"
RESOURCE = RESOURCE_DIR + CACHE_KEY
# Match tiktoken's expected hashes for the three BPE files in LiteLLM 1.105.0.
# o200k_harmony and p50k_edit reuse the o200k_base and p50k_base files.
ASSET_HASHES = {
    CACHE_KEY: SHA256,  # cl100k_base
    "ec7223a39ce59f226a68acc30dc1af2788490e15":
        "94b5ca7dff4d00767bc256fdd1b27e5b17361d7b8a5f968547f9f23eb70d2069",  # p50k_base
    "fb374d419588a4632f3f557e76b4b70aebbca790":
        "446a9538cb6c348e3516120d7c08b09f57c36495e2acfffe59a5bf8b0cfb1a2d",  # o200k_base
}
MAX_BYTES = 4_000_000
_LOCK = Lock()


class TokenizerResourceError(RuntimeError):
    """Local preparation failed before any provider request."""


def _read(path):
    with Path(path).open("rb") as source:
        data = source.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise TokenizerResourceError("tokenizer_asset_invalid")
    return data


def verified_bytes(data, cache_key=CACHE_KEY):
    # The pinned Windows wheel packages this text as CRLF. tiktoken requires
    # the original LF hash; normalization is accepted only for that exact asset.
    canonical = data.replace(b"\r\n", b"\n")
    if hashlib.sha256(canonical).hexdigest() != ASSET_HASHES[cache_key]:
        raise TokenizerResourceError("tokenizer_asset_invalid")
    return canonical


def _valid_cache(path):
    try:
        return hashlib.sha256(_read(path)).hexdigest() == ASSET_HASHES[path.name]
    except FileNotFoundError:
        return False


def _owned_path(cache_key):
    root = ROOT.resolve()
    path = root / ".local-state" / "tokenizers" / "bundled-bpe-v1" / cache_key
    for part in (*reversed(path.relative_to(root).parents), path.relative_to(root)):
        candidate = root / part
        if candidate.exists() or candidate.is_symlink():
            attributes = candidate.lstat()
            if (candidate.is_symlink() or getattr(attributes, "st_file_attributes", 0)
                    & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)):
                raise TokenizerResourceError("tokenizer_cache_link")
    return path


def _publish(target, data):
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=target.parent, prefix=".bpe-", delete=False) as output:
            temporary = Path(output.name)
            output.write(data)
            output.flush()
            os.fsync(output.fileno())
        try:
            os.replace(temporary, target)
        except OSError:
            # Another process may have published the same bytes while Windows
            # prevented replacing its open file. Accept only a verified winner.
            if not _valid_cache(target):
                raise
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def prepare_tokenizer_cache():
    """Select a verified cache before calling LiteLLM; never rewrite its package.

    An explicit CUSTOM_TIKTOKEN_CACHE_DIR remains user-owned: validate it but
    never populate or repair it; all three bundled BPE resources are required.
    With no override, prepare only installation state. Atomic replacement
    allows multiple application processes to start.
    """
    with _LOCK:
        try:
            targets = [_owned_path(key) for key in ASSET_HASHES]
            directory = targets[0].parent
            custom = os.environ.get("CUSTOM_TIKTOKEN_CACHE_DIR")
            if custom and Path(custom).resolve() != directory:
                external = Path(custom).absolute()
                if not all(_valid_cache(external / key) for key in ASSET_HASHES):
                    raise TokenizerResourceError("tokenizer_custom_cache_invalid")
                directory = external
            else:
                missing = [target for target in targets if not _valid_cache(target)]
                if missing:
                    package = distribution("litellm")
                    # Validate every source before creating state or replacing
                    # any file; an incomplete cache must not be selected.
                    copies = [(target, verified_bytes(
                        _read(package.locate_file(RESOURCE_DIR + target.name)), target.name)) for target in missing]
                    directory.mkdir(parents=True, exist_ok=True)
                    for target, data in copies:
                        _publish(target, data)
            # LiteLLM lazily resets TIKTOKEN_CACHE_DIR from CUSTOM_* on import.
            # Set both once preparation succeeded, including already-loaded SDKs.
            os.environ["CUSTOM_TIKTOKEN_CACHE_DIR"] = str(directory)
            os.environ["TIKTOKEN_CACHE_DIR"] = str(directory)
            return directory
        except (OSError, ValueError, PackageNotFoundError):
            raise TokenizerResourceError("tokenizer_cache_unavailable") from None
