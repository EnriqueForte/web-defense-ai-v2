"""Scan declared image references remotely; never start containers or use local Docker."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import subprocess

IMAGES = {
    "lab-mariadb": ("recommended", "mariadb:10.11@sha256:0d0945c57f75b3a3b9ebe71aedaaad005fa5305054e8fca3d2e42a8c92b43b5e"),
    "lab-dvwa": ("recommended", "ghcr.io/digininja/dvwa:b496a5d@sha256:ed35515e9111801e6e386a6fbb11165508cc7f72e0cb8da4dbb3df70182986c6"),
    "lab-mailpit": ("recommended", "axllent/mailpit:v1.31.6@sha256:23fe39e81bde596a918000b3135c0f85dc8bb4c9ea6be274b051143f3e300387"),
    "legacy-mysql": ("legacy", "mysql:8.0"),
    "legacy-dvwa": ("legacy", "vulnerables/web-dvwa:latest"),
    "legacy-python": ("legacy", "python:3.11-slim"),
}
MAILPIT_CANDIDATE = "axllent/mailpit:v1.31.6"
IMAGE_SETS = {
    "inventory": IMAGES,
    "mailpit-review": {
        "lab-mailpit": ("recommended", "axllent/mailpit:v1.31.1"),  # Historical comparison baseline.
        "candidate-mailpit": ("candidate", MAILPIT_CANDIDATE),
    },
}


def summarize_report(label, report, image_set="inventory"):
    scope, reference = IMAGE_SETS[image_set][label]
    if report.get("SchemaVersion") != 2 or report.get("ArtifactType") != "container_image" or report.get("ArtifactName") != reference:
        raise ValueError("Unsupported image report")
    metadata = report["Metadata"]
    digests = metadata.get("RepoDigests", [])
    if not digests or not all(re.fullmatch(r"[^\s@]+@sha256:[a-f0-9]{64}", value) for value in digests):
        raise ValueError("Image report lacks resolved digests")
    pinned_digest = reference.split("@", 1)[1] if "@" in reference else None
    if pinned_digest is not None:
        if not re.fullmatch(r"sha256:[a-f0-9]{64}", pinned_digest) or not any(
                value.split("@", 1)[1] == pinned_digest for value in digests):
            raise ValueError("Image report does not match the pinned digest")
    counts = Counter()
    ids = set()
    fixed_entries = 0
    for result in report.get("Results", []):
        for vulnerability in result.get("Vulnerabilities", []) or []:
            counts[vulnerability["Severity"]] += 1
            ids.add(vulnerability["VulnerabilityID"])
            fixed_entries += bool(vulnerability.get("FixedVersion"))
    return {"label": label, "scope": scope, "requested_reference": reference,
            "status": "scanned", "repo_digests": digests,
            "requested_digest_verified": True if pinned_digest is not None else None,
            "image_id": metadata.get("ImageID"), "os": metadata.get("OS"),
            "platform": "linux/amd64", "entries_by_severity": dict(sorted(counts.items())),
            "distinct_vulnerability_ids": len(ids), "entries_with_fix": fixed_entries,
            "counts_are_package_findings_not_proven_exploits": True}


def scan(trivy, folder, image_set="inventory"):
    selected = IMAGE_SETS[image_set]
    folder.mkdir(parents=True, exist_ok=True)
    cache = folder / "cache"
    version = subprocess.run([trivy, "--cache-dir", str(cache), "--version"], capture_output=True, text=True, timeout=30, check=True)
    (folder / "scanner-version.txt").write_text(version.stdout, encoding="utf-8")
    rows = []
    for label, (scope, reference) in selected.items():
        print(f"Escaneando {label}: {reference}", flush=True)
        destination = folder / f"{label}.json"
        try:
            result = subprocess.run([trivy, "image", "--image-src", "remote", "--platform", "linux/amd64",
                "--scanners", "vuln", "--cache-dir", str(cache), "--timeout", "10m", "--exit-code", "0",
                "--format", "json", "--output", str(destination), reference],
                capture_output=True, timeout=660)
            if result.returncode:
                raise ValueError("Scanner failed")
            row = summarize_report(label, json.loads(destination.read_text(encoding="utf-8")), image_set)
        except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError):
            row = {"label": label, "scope": scope, "requested_reference": reference,
                   "status": "scan_failed", "no_zero_vulnerabilities_claimed": True}
        rows.append(row)
        print(f"Resultado {label}: {row['status']}", flush=True)
    version = subprocess.run([trivy, "--cache-dir", str(cache), "--version"], capture_output=True, text=True, timeout=30, check=True)
    (folder / "scanner-version.txt").write_text(version.stdout, encoding="utf-8")
    summary = {"schema_version": 1, "captured_at": datetime.now(timezone.utc).isoformat(),
               "image_set": image_set,
               "scanner_version_output": version.stdout, "images": rows,
               "source": "remote_registry", "local_installed_images_not_verified": True,
               "containers_started": False, "findings_fail_policy": "review_required; all severities retained"}
    (folder / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return 1 if any(row["status"] != "scanned" for row in rows) else 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trivy", default="trivy")
    parser.add_argument("--output-dir", type=Path, default=Path(".local-state/image-audit"))
    parser.add_argument("--image-set", choices=sorted(IMAGE_SETS), default="inventory")
    args = parser.parse_args()
    try:
        return scan(args.trivy, args.output_dir, args.image_set)
    except (OSError, ValueError, subprocess.SubprocessError):
        print("Scanner no disponible; no se acredita auditoría de imágenes.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
