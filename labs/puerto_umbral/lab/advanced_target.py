"""F6 stateful fixtures and F7 artifact reviews, only inside the existing sandbox.

No destinations supplied by the operator are opened. The SSRF exercise makes
HTTP requests through one private Unix socket to a fictitious internal canary.
"""
import base64
from datetime import datetime, timezone
import hashlib
import hmac
import html
import http.client
from http.server import BaseHTTPRequestHandler
import json
from http.cookies import SimpleCookie
from pathlib import Path
import re
import secrets
import socket
import socketserver
import tempfile
import threading
from urllib.parse import parse_qs, urlsplit

from audit_contract import SCHEMA


class State:
    def __init__(self, mode):
        self.mode = mode
        self.sessions = {}
        self.posts = []
        self.preferences = {}
        self.permits = {}
        self.events = []
        self.key = secrets.token_bytes(32)
        self.canary = None
        self.run_id = None

    def event(self, run, request_id, scenario, actor, role, action, resource, owner, decision, outcome, status, context):
        component = {"session": "identity", "stored_xss": "notice_board", "idor": "cargo",
                     "csrf": "preferences", "ssrf": "beacon", "workflow": "docking"}.get(scenario, "artifact_review")
        self.events.append({"sequence": len(self.events) + 1,
            "observed_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "run_id": run, "request_id": request_id, "component": component, "mode": self.mode,
            "actor": actor, "role": role, "action": action, "resource": resource, "owner": owner,
            "decision": decision, "outcome": outcome, "http_status": status, **context})

    def beacon(self, resource):
        if self.canary is None:
            # No IP listener or DNS: even this canary stays in this target.
            directory = tempfile.TemporaryDirectory(prefix="umbral-canary-")
            path = str(Path(directory.name) / "canary.sock")

            class Canary(BaseHTTPRequestHandler):
                def log_message(self, *_):
                    pass

                def do_GET(self):
                    allowed = self.path in {"/public", "/internal/diagnostic", "/internal/manifest", "/internal/status"}
                    body = json.dumps({"resource": self.path, "fixture":
                        "UMBRAL_INTERNAL_CANARY" if self.path.startswith("/internal/") else "UMBRAL_PUBLIC_BEACON"}).encode()
                    self.send_response(200 if allowed else 404)
                    self.send_header("Content-Length", str(len(body)))
                    self.end_headers()
                    self.wfile.write(body)

            server = socketserver.ThreadingUnixStreamServer(path, Canary)
            server.daemon_threads = True
            threading.Thread(target=server.serve_forever, daemon=True).start()
            self.canary = (directory, path, server)

        class UnixHTTP(http.client.HTTPConnection):
            def connect(connection):
                connection.sock = socket.socket(socket.AF_UNIX)
                connection.sock.settimeout(1)
                connection.sock.connect(self.canary[1])

        connection = UnixHTTP("canary", timeout=1)
        try:
            connection.request("GET", resource)
            response = connection.getresponse()
            return response.status, json.loads(response.read(4096))
        finally:
            connection.close()


def review(topic, variant, kind, mode, key):
    """F7 uses controlled artifact reviews; never installs a package or malware."""
    corrected = mode == "corrected"
    attempt = kind == "attempt"
    label = f"fixture-{variant + 1}"
    body = {"provenance": "fictional_artifact_review", "topic": topic, "fixture": label,
            "production_security_claim": False}
    status, effect = 200, False
    if topic == "configuration":
        expose = attempt and not corrected
        body.update(debug_enabled=expose, configuration={"service": "beacon-demo", "debug_trace": label}
                    if expose else {"service": "beacon-demo"},
                    observation="debug_fixture_exposed" if expose else "minimal_configuration")
        effect = expose
    elif topic == "supply_chain":
        original = ("umbral-demo-artifact-" + str(variant)).encode()
        received = original + (b"-changed" if attempt else b"")
        expected = hashlib.sha256(original).hexdigest()
        valid = hmac.compare_digest(expected, hashlib.sha256(received).hexdigest())
        accepted = valid or not corrected
        body.update(expected_sha256=expected, received_sha256=hashlib.sha256(received).hexdigest(),
                    accepted=accepted, trusted_reference="fixed_local_fixture", observation="digest_comparison")
        status, effect = (200 if accepted else 422), attempt and accepted
    elif topic == "cryptography":
        password = ("fictional-password-" + str(variant)).encode()
        weak = attempt and not corrected
        salt = secrets.token_bytes(16)
        body.update(storage_method="base64_encoding" if weak else "scrypt",
                    stored_fixture=base64.b64encode(password).decode() if weak else
                    hashlib.scrypt(password, salt=salt, n=16384, r=8, p=1).hex(),
                    salt=salt.hex() if not weak else None,
                    observation="encoding_is_reversible" if weak else "salted_password_derivation",
                    note="Parámetros educativos; no es una auditoría criptográfica de producción.")
        effect = weak
    elif topic == "integrity":
        original = ("cargo-approved-" + str(variant)).encode()
        received = original + (b"-changed" if attempt else b"")
        signature = hmac.new(key, original, hashlib.sha256).digest()
        valid = hmac.compare_digest(signature, hmac.new(key, received, hashlib.sha256).digest())
        accepted = valid or not corrected
        body.update(accepted=accepted, verification="hmac_sha256" if corrected else "not_checked",
                    observation="changed_manifest_accepted" if attempt and accepted else "manifest_checked")
        status, effect = (200 if accepted else 422), attempt and accepted
    elif topic == "logging":
        sequence = [1, 2, 4, 5] if attempt else [1, 2, 3, 4, 5]
        gaps = sorted(set(range(1, max(sequence) + 1)) - set(sequence))
        detected = bool(gaps) and corrected
        body.update(sequence_fixture=sequence, missing_sequence=gaps if corrected else [],
                    warning_recorded=detected, observation="gap_identified" if detected else "no_warning",
                    note="Secuencia ficticia; no prueba rotación, continuidad real de Apache o entrega de avisos.")
        effect = attempt and bool(gaps) and not detected
    elif topic == "exceptions":
        leak = attempt and not corrected
        status = (400 if corrected else 500) if attempt else 200
        body.update(observation="fictional_error_details_exposed" if leak else "controlled_response",
                    error={"code": "invalid_fixture", "fictional_trace": "demo_config.py:42"}
                    if leak else {"code": "invalid_fixture"} if attempt else None)
        effect = leak
    else:
        return 404, {"error": "unknown_review"}
    body["observed_fixture_effect"] = effect
    return status, body


def handler_class(base, mode):
    """Called only by target.py after verify_boundary, never by host import."""
    state = State(mode)

    class Advanced(base):
        # Manual browser steps need a bounded human-scale window. The base
        # scenarios keep 30 seconds; the runner itself still stops after 30.
        execution_seconds = 300

        def reply(self, status, value, content_type="application/json; charset=utf-8", headers=None):
            data = value.encode() if isinstance(value, str) else json.dumps(value, ensure_ascii=False).encode()
            self.send_response(status)
            for key, value in {"Content-Type": content_type, "Content-Length": str(len(data)),
                    "Cache-Control": "no-store", "X-Content-Type-Options": "nosniff",
                    "Content-Security-Policy": "default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; "
                    "img-src data:; connect-src 'none'; form-action 'self'; base-uri 'none'; "
                    "frame-ancestors http://127.0.0.1:4381; sandbox allow-scripts allow-forms allow-same-origin",
                    **(headers or {})}.items():
                self.send_header(key, value)
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            self.handle_request("GET")

        def do_POST(self):
            self.handle_request("POST")

        def handle_request(self, method):
            if len(self.path.encode()) > 4096:
                self.reply(414, {"error": "target_too_long"})
                return
            parsed = urlsplit(self.path)
            if parsed.path == "/health" and method == "GET":
                self.reply(200, {"status": "ready", "version": "puerto-umbral-extensions-1"})
                return
            if not self.guard():
                return
            fields = parse_qs(parsed.query, keep_blank_values=True)
            if method == "POST":
                try:
                    size = int(self.headers.get("Content-Length", "0"))
                except ValueError:
                    size = -1
                if not 0 <= size <= 2048:
                    self.reply(413, {"error": "body_limit"})
                    return
                try:
                    fields.update(parse_qs(self.rfile.read(size).decode("utf-8", "strict"), keep_blank_values=True))
                except UnicodeError:
                    self.reply(400, {"error": "invalid_body_encoding"})
                    return
            get = lambda name, default="": fields.get(name, [default])[0][:512]
            run = self.headers.get("X-Umbral-Run", get("_run"))
            if not re.fullmatch(r"[a-f0-9]{32}", run):
                self.reply(400, {"error": "explicit_run_id_required"})
                return
            if state.run_id is None:
                state.run_id = run
            elif state.run_id != run:
                self.reply(409, {"error": "different_execution_reset_required"})
                return
            request_id = self.headers.get("X-Request-ID", secrets.token_hex(12))
            if not re.fullmatch(r"[a-f0-9]{24}", request_id):
                self.reply(400, {"error": "invalid_request_id"})
                return
            if parsed.path == "/avanzado/auditoria" and method == "GET":
                events = [item for item in state.events if item["run_id"] == run]
                self.reply(200, {"schema": SCHEMA, "run_id": run, "events": events[:200], "truncated": len(events) > 200})
                return
            actor, role, owner = "anonymous", "visitor", "none"
            cookie = SimpleCookie()
            try:
                cookie.load(self.headers.get("Cookie", ""))
            except Exception:
                self.reply(400, {"error": "invalid_cookie"})
                return
            token = self.headers.get("Authorization", "").removeprefix("Bearer ")
            auth_source = "bearer" if token else "none"
            cookie_name = "umbral_session_" + mode
            if not token and cookie_name in cookie:
                token = cookie[cookie_name].value
                auth_source = "cookie"
            session = state.sessions.get(token)
            if session:
                actor, role = session["actor"], session["role"]
            status, body, extra, scenario = 404, {"error": "unknown_endpoint"}, {}, "session"
            action, resource, decision, outcome = "read", "unknown", "deny", "not_found"
            expected_origin = "http://127.0.0.1:" + ("4380" if mode == "vulnerable" else "4382")
            origin = self.headers.get("Origin")
            context = {"origin_relation": "missing" if origin is None else "same" if origin == expected_origin else "cross",
                       "csrf_check": "not_checked", "state_before": "none", "state_after": "none",
                       "canary_scope": "none", "render_context": "none", "auth_source": auth_source}
            if parsed.path == "/avanzado/sesion" and method == "POST":
                actor = get("actor")
                if actor not in {"estibador.demo", "supervisor.demo"} or get("password") != "umbral-demo":
                    actor, status, body = "anonymous", 401, {"error": "invalid_fixture_identity"}
                else:
                    role = "supervisor" if actor == "supervisor.demo" else "operator"
                    token, csrf = secrets.token_urlsafe(24), secrets.token_urlsafe(24)
                    state.sessions[token] = {"actor": actor, "role": role, "csrf": csrf}
                    status, body = 200, {"actor": actor, "role": role, "session_token": token, "csrf_token": csrf}
                    extra = {"Set-Cookie": cookie_name + "=" + token + "; HttpOnly; SameSite=Lax; Path=/avanzado"}
                    decision, outcome = "allow", "session_created"
                    if get("view") == "browser":
                        body = '<!doctype html><html lang="es"><meta charset="utf-8"><title>Sesión ficticia</title><h1>Sesión ficticia creada</h1><p>Cuenta de práctica; vuelve a la ventana del ejercicio para enviar el formulario de otro origen.</p>' + '<form method="post" action="/avanzado/preferencias?_run=' + run + '"><input type="hidden" name="csrf_token" value="' + csrf + '"><input type="hidden" name="channel" value="normal"><button>Control normal desde este origen</button></form></html>'
                action, resource = "authenticate", "fixture_identity"
            elif parsed.path == "/avanzado/tablon" and method == "GET":
                scenario, resource, decision, outcome = "stored_xss", "notice_board", "allow", "rendered"
                status = 200
                context["render_context"] = ("encoded_text" if mode == "corrected" else "raw_markup") if any("<" in item for item in state.posts) else "plain_text"
                body = '<!doctype html><html lang="es"><meta charset="utf-8"><title>Bitácora / Puerto Umbral</title><h1>Bitácora de turno</h1>' + ''.join(
                    '<p>' + (html.escape(item) if mode == "corrected" else item) + '</p>' for item in state.posts) + '</html>'
            elif session is None:
                status, body = 401, {"error": "fixture_session_required"}
            elif parsed.path == "/avanzado/tablon" and method == "POST":
                state.posts.append(get("message"))
                scenario, action, resource = "stored_xss", "store", "notice_board"
                status, body, decision, outcome = 200, {"stored": True, "messages": len(state.posts)}, "allow", "stored"
            elif parsed.path == "/avanzado/carga" and method == "GET":
                scenario, resource = "idor", get("documento")
                owned = {"own-1", "own-2", "own-3"}
                foreign = {"foreign-1", "foreign-2", "foreign-3"}
                owner = "estibador.demo" if resource in owned else "supervisor.demo" if resource in foreign else "none"
                allowed = resource in owned | foreign and (mode == "vulnerable" or actor == owner)
                status = 200 if allowed else 403
                decision, outcome = ("allow", "served") if allowed else ("deny", "withheld")
                body = {"document": resource, "owner": owner, "fixture": "UMBRAL_FOREIGN_CARGO" if resource in foreign else "UMBRAL_OWN_CARGO"} if allowed else {"error": "object_not_authorized"}
                if owner == "none":
                    resource = "invalid_fixture"
            elif parsed.path == "/avanzado/preferencias" and method == "POST":
                scenario, action, resource, owner = "csrf", "update", "arrival_preferences", actor
                allowed = mode == "vulnerable" or (self.headers.get("Origin") == expected_origin
                    and secrets.compare_digest(self.headers.get("X-CSRF-Token", get("csrf_token")).encode(), session["csrf"].encode()))
                if allowed:
                    state.preferences[actor] = get("channel")
                status, decision, outcome = (200, "allow", "updated") if allowed else (403, "deny", "unchanged")
                body = {"channel": state.preferences.get(actor, "normal"), "changed": allowed}
                context.update(csrf_check="not_checked" if mode == "vulnerable" else "accepted" if allowed else "rejected",
                               state_before="previous_preference", state_after="updated" if allowed else "unchanged")
            elif parsed.path == "/avanzado/baliza" and method == "GET":
                scenario, action, resource = "ssrf", "fetch", get("destino")
                paths = {"umbral://beacon/public": "/public", "umbral://beacon/diagnostic": "/internal/diagnostic",
                         "umbral://beacon/manifest": "/internal/manifest", "umbral://beacon/status": "/internal/status"}
                allowed = resource in paths and (mode == "vulnerable" or resource == "umbral://beacon/public")
                if allowed:
                    status, body = state.beacon(paths[resource])
                    decision, outcome = "allow", "canary_read"
                    context["canary_scope"] = "internal" if paths[resource].startswith("/internal/") else "public"
                else:
                    status, body, outcome = 403, {"error": "canary_resource_not_authorized"}, "withheld"
                    if resource not in paths:
                        resource = "invalid_fixture"
            elif parsed.path == "/avanzado/atraque" and method == "POST":
                scenario, resource, action = "workflow", get("permit"), get("action")
                if resource not in {"dock-1", "dock-2", "dock-3"} or action not in {"approve", "execute"}:
                    status, body = 400, {"error": "invalid_docking_operation"}
                    resource, action = "invalid_fixture", "invalid_operation"
                elif action == "approve":
                    context["state_before"] = state.permits.get(resource, "pending")
                    allowed = role == "supervisor"
                    if allowed:
                        state.permits[resource] = "approved"
                    status, decision, outcome = (200, "allow", "approved") if allowed else (403, "deny", "unchanged")
                    body = {"permit_state": state.permits.get(resource, "pending")}
                    context["state_after"] = state.permits.get(resource, "pending")
                else:
                    before = state.permits.get(resource, "pending")
                    context["state_before"] = before
                    allowed = mode == "vulnerable" or before == "approved"
                    if allowed:
                        state.permits[resource] = "consumed"
                    status, decision, outcome = (200, "allow", "executed") if allowed else (409, "deny", "unchanged")
                    body = {"previous_state": before, "permit_state": state.permits.get(resource, "pending")}
                    context["state_after"] = state.permits.get(resource, "pending")
            elif parsed.path == "/avanzado/revision" and method == "GET":
                try:
                    variant = int(get("variant", "0"))
                except ValueError:
                    variant = -1
                topic, kind = get("topic"), get("kind")
                allowed_topics = {"configuration", "supply_chain", "cryptography", "integrity", "logging", "exceptions"}
                if topic in allowed_topics and variant in range(3) and kind in {"attempt", "benign"}:
                    scenario, action, resource = topic, "review", "artifact-" + str(variant + 1)
                    status, body = review(topic, variant, kind, mode, state.key)
                    decision, outcome = "observed", body.get("observation", "reviewed")
                else:
                    status, body = 400, {"error": "invalid_review_selection"}
            # No body, session/CSRF tokens, credentials or expected corpus labels.
            state.event(run, request_id, scenario, actor, role, action, resource, owner, decision, outcome, status, context)
            self.reply(status, body, "text/html; charset=utf-8" if isinstance(body, str) else "application/json; charset=utf-8", extra)

    return Advanced
