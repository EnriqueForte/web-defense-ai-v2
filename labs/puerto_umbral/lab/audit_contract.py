"""Application-event contract; no corpus expectations or credentials are permitted."""
from datetime import datetime, timedelta
import re

SCHEMA = "puerto-umbral.application-events.v1"
FIELDS = {"sequence", "observed_at", "run_id", "request_id", "component", "mode", "actor",
          "role", "action", "resource", "owner", "decision", "outcome", "http_status",
          "origin_relation", "csrf_check", "state_before", "state_after", "canary_scope", "render_context", "auth_source"}
COMPONENTS = {"identity", "notice_board", "cargo", "preferences", "beacon", "docking", "artifact_review"}
ENUMS = {
    "decision": {"allow", "deny", "observed"},
    "origin_relation": {"missing", "same", "cross"},
    "csrf_check": {"not_checked", "accepted", "rejected"},
    "canary_scope": {"none", "public", "internal"},
    "render_context": {"none", "plain_text", "encoded_text", "raw_markup"},
    "auth_source": {"none", "bearer", "cookie"},
}


def validate_batch(value, run_id):
    if (type(run_id) is not str or not re.fullmatch(r"[a-f0-9]{32}", run_id) or type(value) is not dict
            or set(value) != {"schema", "run_id", "events", "truncated"}
            or value["schema"] != SCHEMA or value["run_id"] != run_id
            or type(value["truncated"]) is not bool or value["truncated"]
            or type(value["events"]) is not list or len(value["events"]) > 200):
        raise ValueError("invalid_application_audit")
    previous = 0
    for event in value["events"]:
        if (type(event) is not dict or set(event) != FIELDS or event["run_id"] != run_id
                or type(event["sequence"]) is not int or event["sequence"] <= previous
                or type(event["request_id"]) is not str or not re.fullmatch(r"[a-f0-9]{24}", event["request_id"])
                or type(event["component"]) is not str or event["component"] not in COMPONENTS
                or type(event["mode"]) is not str or event["mode"] not in {"vulnerable", "corrected"}
                or type(event["http_status"]) is not int or not 100 <= event["http_status"] <= 599):
            raise ValueError("invalid_application_event")
        if any(type(event[key]) is not str or not re.fullmatch(r"[a-zA-Z0-9_.:/-]{1,100}", event[key])
               for key in ("actor", "role", "action", "resource", "owner", "decision", "outcome",
                           "origin_relation", "csrf_check", "state_before", "state_after", "canary_scope", "render_context", "auth_source")):
            raise ValueError("invalid_application_event_text")
        if any(event[key] not in allowed for key, allowed in ENUMS.items()):
            raise ValueError("invalid_application_event_enum")
        if type(event['observed_at']) is not str or len(event['observed_at']) > 64:
            raise ValueError("invalid_application_event_time")
        stamp = datetime.fromisoformat(event["observed_at"].replace("Z", "+00:00"))
        if stamp.tzinfo is None or stamp.utcoffset() != timedelta(0):
            raise ValueError("application_event_utc_required")
        previous = event["sequence"]
    return value
