"""Intentionally vulnerable target. Refuses operation outside its Docker boundary.

HTTP travels over a Unix socket, not an IP network. The control process and its
records live outside this container. Never run this service on the host.
"""
import html
from http.server import BaseHTTPRequestHandler
import json
import os
from pathlib import Path
import re
import signal
import socketserver
import sqlite3
import subprocess
import tempfile
import time
from urllib.parse import parse_qs, urlsplit

ROOT = Path("/srv/fixtures")
SOCKET = Path("/run/umbral/backend.sock")
MODE = os.environ.get("UMBRAL_MODE", "corrected")
SCENARIO = os.environ.get("UMBRAL_SCENARIO", "")
PATHS = {"sqli": "/mercancias", "xss": "/comunicaciones", "traversal": "/archivo", "command": "/mantenimiento", "brute": "/login", "advanced": "/avanzado"}
MAX_REQUESTS = 20
MAX_SECONDS = 30
MAX_BYTES = 2048
USERS = {"operador.demo", "ingenieria.demo", "control.demo"}


def verify_boundary():
    if os.name != "posix" or os.environ.get("UMBRAL_SANDBOX") != "isolated-v1":
        raise RuntimeError("isolated_container_required")
    if not Path("/.dockerenv").is_file() or os.getuid() != 10001:
        raise RuntimeError("non_root_container_required")
    status = Path("/proc/self/status").read_text()
    if not re.search(r"NoNewPrivs:\s+1", status) or not re.search(r"CapEff:\s+0+\b", status):
        raise RuntimeError("privilege_boundary_missing")
    if {p.name for p in Path("/sys/class/net").iterdir()} != {"lo"}:
        raise RuntimeError("network_none_required")
    if MODE not in {"vulnerable", "corrected"}:
        raise RuntimeError("invalid_mode")
    if SCENARIO not in PATHS:
        raise RuntimeError("invalid_scenario")


def database():
    db = sqlite3.connect(":memory:")
    db.executescript("CREATE TABLE cargo(id TEXT, name TEXT, visible INTEGER);"
                     "INSERT INTO cargo VALUES('UM-1284','Núcleos de navegación Asteria',1);"
                     "INSERT INTO cargo VALUES('UM-1286','Celdas de energía',1);"
                     "INSERT INTO cargo VALUES('UM-1287','Soporte vital Asteria',1);"
                     "INSERT INTO cargo VALUES('UM-9000','SEÑUELO-RESERVADO-UMBRAL',0);")
    allowed = {sqlite3.SQLITE_SELECT, sqlite3.SQLITE_READ, sqlite3.SQLITE_FUNCTION}
    db.set_authorizer(lambda action, *_: sqlite3.SQLITE_OK if action in allowed else sqlite3.SQLITE_DENY)
    deadline = time.monotonic() + 0.2
    db.set_progress_handler(lambda: int(time.monotonic() > deadline), 500)
    db.setlimit(sqlite3.SQLITE_LIMIT_LENGTH, 65536)
    db.setlimit(sqlite3.SQLITE_LIMIT_SQL_LENGTH, 4096)
    return db


def command_limits():
    import resource
    resource.setrlimit(resource.RLIMIT_CPU, (1, 1))
    resource.setrlimit(resource.RLIMIT_FSIZE, (65536, 65536))
    resource.setrlimit(resource.RLIMIT_NOFILE, (32, 32))
    # RLIMIT_NPROC counts this UID across containers. The container's cgroup
    # pids_limit=32 provides the process ceiling without cross-scenario interference.
    resource.setrlimit(resource.RLIMIT_AS, (64 * 1024 * 1024, 64 * 1024 * 1024))


def diagnose(value, *, corrected):
    verify_boundary()
    if corrected and value not in {"baliza-07", "esclusa-02", "enlace-comms"}:
        return 400, {"error": "invalid_component"}
    args = ["/usr/bin/printf", "DIAG:%s\n", value] if corrected else ["/bin/sh", "-c", "printf 'DIAG:%s\\n' " + value]
    with tempfile.TemporaryFile() as output:
        process = subprocess.Popen(args, stdout=output, stderr=subprocess.STDOUT,
                                   cwd="/srv/fixtures/public", env={"PATH": "/usr/bin:/bin", "LANG": "C.UTF-8"},
                                   start_new_session=True, preexec_fn=command_limits)
        timed_out = False
        try:
            process.wait(timeout=1.5)
        except subprocess.TimeoutExpired:
            timed_out = True
        finally:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.wait(timeout=2)
        output.seek(0)
        text = output.read(8192).decode("utf-8", "replace")
    return (408 if timed_out else 200), {"stdout": text, "timed_out": timed_out, "returncode": process.returncode}


class Target(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.0"
    execution_seconds = MAX_SECONDS
    started = None
    request_count = 0
    last_request = 0.0
    failures = {}

    def log_message(self, *_):
        pass  # Apache alone records actual access lines; no synthetic access logs.

    def reply(self, status, value, content_type="application/json; charset=utf-8"):
        data = value.encode() if isinstance(value, str) else json.dumps(value, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; "
                         "img-src data:; connect-src 'none'; form-action 'none'; base-uri 'none'; "
                         "frame-ancestors http://127.0.0.1:4381; sandbox allow-scripts")
        self.end_headers()
        self.wfile.write(data)

    def guard(self):
        now = time.monotonic()
        if Target.started is None:
            Target.started = now
        if now - Target.started > self.execution_seconds:
            self.reply(410, {"error": "execution_expired", "reset_required": True})
            return False
        if Target.request_count >= MAX_REQUESTS:
            self.reply(429, {"error": "execution_request_limit", "reset_required": True})
            return False
        if now - Target.last_request < 0.5:
            self.reply(429, {"error": "execution_rate_limit"})
            return False
        Target.last_request = now
        Target.request_count += 1
        return True

    def do_GET(self):
        if len(self.path.encode()) > 4096:
            self.reply(414, {"error": "target_too_long"})
            return
        parsed = urlsplit(self.path)
        if parsed.path == "/health":
            self.reply(200, {"status": "ready", "version": "puerto-umbral-f2-1"})
            return
        if not self.guard():
            return
        if parsed.path != PATHS[SCENARIO]:
            self.reply(404, {"error": "unknown_endpoint"})
            return
        fields = parse_qs(parsed.query, keep_blank_values=True)
        value = lambda key, default="": fields.get(key, [default])[0][:512]
        if parsed.path == "/mercancias":
            q = value("q")
            db = database()
            try:
                query = "SELECT id,name FROM cargo WHERE visible=1 AND name LIKE "
                rows = db.execute(query + "?", ("%" + q + "%",)).fetchmany(100) if MODE == "corrected" else db.execute(query + "'%" + q + "%'").fetchmany(100)
                self.reply(200, {"cargo": [{"id": row[0], "name": row[1]} for row in rows]})
            except sqlite3.Error:
                self.reply(400, {"error": "invalid_query"})
            finally:
                db.close()
        elif parsed.path == "/comunicaciones":
            q = value("q", "Bienvenida a Puerto Umbral")
            reflected = html.escape(q) if MODE == "corrected" else q
            self.reply(200, '<!doctype html><html lang="es"><meta charset="utf-8"><title>Comunicaciones / Puerto Umbral</title>'
                       '<style>body{background:#141c20;color:#c4dfd1;font:16px monospace;padding:25px}h1{font-size:19px}</style>'
                       '<h1>Comunicaciones · escenario local</h1><p id="reflection">' + reflected + '</p></html>', "text/html; charset=utf-8")
        elif parsed.path == "/archivo":
            public = (ROOT / "public").resolve()
            destination = (public / value("documento", "atraque.txt")).resolve()
            perimeter = public if MODE == "corrected" else ROOT.resolve()
            if not destination.is_relative_to(perimeter) or not destination.is_file():
                self.reply(403, {"error": "document_not_authorized"})
            else:
                self.reply(200, destination.read_text(encoding="utf-8"), "text/plain; charset=utf-8")
        elif parsed.path == "/mantenimiento":
            status, output = diagnose(value("equipo", "baliza-07"), corrected=MODE == "corrected")
            self.reply(status, output)
        elif parsed.path == "/":
            self.reply(200, {"station": "Puerto Umbral", "endpoints": ["/mercancias", "/comunicaciones", "/archivo", "/mantenimiento", "/login"]})
        else:
            self.reply(404, {"error": "unknown_endpoint"})

    def do_POST(self):
        if SCENARIO != "brute" or urlsplit(self.path).path != "/login":
            self.reply(404, {"error": "unknown_endpoint"})
            return
        try:
            size = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            size = -1
        if size < 0 or size > MAX_BYTES:
            self.reply(413, {"error": "body_limit"})
            return
        if not self.guard():
            return
        body = parse_qs(self.rfile.read(size).decode("utf-8", "replace"))
        user = body.get("username", [""])[0][:80]
        count = Target.failures.get(user, 0)
        if MODE == "corrected" and count >= 3:
            self.reply(429, {"authenticated": False, "error": "login_attempt_limit"})
            return
        valid = user in USERS and body.get("password", [""])[0] == "umbral-demo"
        if not valid:
            Target.failures[user] = count + 1
        self.reply(200 if valid else 401, {"authenticated": valid, "operator": user if valid else None})


if __name__ == "__main__":
    verify_boundary()
    handler = Target
    if SCENARIO == "advanced":
        from advanced_target import handler_class
        handler = handler_class(Target, MODE)
    if SOCKET.exists():
        SOCKET.unlink()  # Exact socket in this container's dedicated named volume.
    with socketserver.UnixStreamServer(str(SOCKET), handler) as server:
        SOCKET.chmod(0o660)
        server.serve_forever()
