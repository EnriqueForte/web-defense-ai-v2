"""Read and score one existing synthetic publication; no settings, provider or writes."""
import argparse
import json
from pathlib import Path
import socket
import sys
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from agents.evaluation_fixtures import CASES
from agents.evaluation_scoring import score_fixture_result
from dashboard.services.structured_publication import load_current


def review_publication(publication, case):
    manifest, result, _ = load_current(publication)
    scores = score_fixture_result(result["findings"], result["evidence"], case)
    return {"status": "reviewed", "generation": manifest["generation"],
            "sha256": {name: manifest["sha256"][name] for name in ("result.json", "report.md")},
            "scope": "existing_synthetic_fixture_publication_not_semantic_acceptance",
            "provider_calls": 0, **scores}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--publication", required=True, type=Path, help="directory containing current.json")
    parser.add_argument("--case", required=True, choices=CASES)
    args = parser.parse_args(argv)
    try:
        with patch.object(socket.socket, "connect", side_effect=RuntimeError("offline_network_forbidden")), \
                patch.object(socket, "create_connection", side_effect=RuntimeError("offline_network_forbidden")):
            report = review_publication(args.publication, args.case)
    except (OSError, ValueError, KeyError, TypeError, RecursionError):
        print(json.dumps({"status": "rejected", "reason": "fixture_review_unavailable"}))
        return 1
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["fixture_expectations_met"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
