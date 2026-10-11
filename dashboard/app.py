# dashboard/app.py
# ============================================================
# web-defense-ai V2 — Dashboard Flask · T3r0S3c
# ============================================================

import os
import json
import ipaddress
import re
import sys
import subprocess
import sqlite3
import threading
from http.client import HTTPConnection
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import uuid
import secrets
from urllib.parse import unquote_plus, urlsplit
from flask import render_template, jsonify, request, g, redirect
from dotenv import load_dotenv
from dashboard.services.read_store import CapturedFile, capture_file, inspect_file, run_atomic_copy
from dashboard.services.active_report import capture_current, capture_current_details, inspect_current
from agents.structured_reporting import event_period, render_markdown
from dashboard.services.analysis_jobs import JobStore, default_db_path
from dashboard.services.runtime_lock import AlreadyRunning, exclusive_lock
from dashboard.services.llm_settings import InvalidLLMSettings, public_llm_settings, save_llm_settings
from dashboard.services.local_hosts import LocalHostFlask
from werkzeug.exceptions import HTTPException

# Añadir raíz del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

app = LocalHostFlask(__name__)
app.config.update(TRUSTED_HOSTS=["localhost", "127.0.0.1", "[::1]"],
                  MAX_CONTENT_LENGTH=16 * 1024)

LOCAL_BROWSER_ORIGINS = {
    "http://127.0.0.1:3000", "http://127.0.0.1:5000",
    "http://localhost:3000", "http://localhost:5000",
}


def _local_origin_allowed(*, required=True):
    origin = request.headers.get("Origin")
    return origin in LOCAL_BROWSER_ORIGINS or (origin is None and not required)


@app.before_request
def asignar_request_id():
    g.request_id = uuid.uuid4().hex
    g.csp_nonce = secrets.token_urlsafe(24)
    if request.remote_addr not in {"127.0.0.1", "::1"}:
        if request.path.startswith("/api/"):
            return _api_error(403, "local_only", "El dashboard solo admite conexiones locales.")
        return "Acceso local únicamente.", 403


@app.after_request
def cabeceras_api(response):
    response.headers["X-Request-ID"] = getattr(g, "request_id", "")
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "same-origin"
    nonce = getattr(g, 'csp_nonce', '')
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        f"script-src 'self' 'nonce-{nonce}'; "
        "style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; "
        "connect-src 'self'; object-src 'none'; base-uri 'none'; "
        "frame-ancestors 'none'; form-action 'self'"
    )
    response.headers["X-Frame-Options"] = "DENY"
    if request.path.startswith("/api/v1/") or request.path == "/api/estado":
        response.headers["Cache-Control"] = "no-store, max-age=0"
        response.headers["Pragma"] = "no-cache"
    return response


@app.context_processor
def contexto_csp():
    return {"csp_nonce": getattr(g, 'csp_nonce', '')}


@app.errorhandler(HTTPException)
def error_http_api(error):
    if request.path.startswith("/api/"):
        code = ("not_found" if error.code == 404 else "method_not_allowed" if error.code == 405
                else "request_too_large" if error.code == 413 else "http_error")
        message = ("No se encontró el recurso solicitado." if error.code == 404
                   else "La solicitud supera el límite de tamaño." if error.code == 413
                   else "La operación no está permitida.")
        return _api_error(error.code or 500, code, message)
    return error


@app.errorhandler(Exception)
def error_interno(error):
    # No exception messages/tracebacks: transports or configuration errors can
    # contain credentials, URLs, SQL details or untrusted input.
    app.logger.error("Fallo interno del dashboard; respuesta sin detalles sensibles.")
    if request.path.startswith("/api/"):
        return _api_error(500, "internal_error", "No se pudo completar la operación local.")
    return "No se pudo completar la operación local.", 500, {"Content-Type": "text/plain; charset=utf-8"}

# ============================================================
# CONFIGURACIÓN
# ============================================================
REPORT_PATH  = Path(os.getenv("REPORT_PATH", "./reports"))
LOG_PATH     = os.getenv("LOG_PATH", "./logs/access.log")
HISTORIAL    = REPORT_PATH / "historial"
VENV_PYTHON  = os.path.join(".venv", "Scripts", "python.exe")


# ============================================================
# FUNCIONES DE SOPORTE
# ============================================================
def parsear_amenazas(reporte: str) -> list[dict]:
    """
    Extrae amenazas del reporte. Detecta el orden de columnas
    dinamicamente leyendo la cabecera real de la tabla.
    """
    amenazas  = []
    lineas    = reporte.splitlines()
    en_tabla  = False
    cabeceras = []
    for linea in lineas:
        if "AMENAZAS DETECTADAS" in linea.upper():
            en_tabla  = True
            cabeceras = []
            continue

        if not en_tabla:
            continue

        # Leer cabeceras de la primera fila de la tabla
        if linea.startswith("|") and not cabeceras:
            celdas = linea.split("|")[1:-1]
            cabeceras = [
                c.strip().lower()
                .replace("á","a").replace("é","e")
                .replace("í","i").replace("ó","o")
                .replace("ú","u").replace("ã","a")
                .replace("lã\xadnea","linea")
                for c in celdas
            ]
            continue

        # Procesar filas de datos
        if linea.startswith("|") and cabeceras:
            partes = [p.strip() for p in linea.split("|")[1:-1]]
            if len(partes) < 3:
                continue
            if all(re.fullmatch(r":?-{3,}:?", p) for p in partes if p):
                continue

            # Buscar índice de cada columna por nombre
            def idx(*nombres):
                for nombre in nombres:
                    for i, cab in enumerate(cabeceras):
                        if cab == nombre or cab.startswith(nombre + " "):
                            return partes[i].strip() if i < len(partes) and partes[i].strip() else "-"
                return "-"

            # Validar IP con regex
            ip_raw = idx("ip", "origen").strip("`")
            try:
                ipaddress.ip_address(ip_raw)
                ip_final = ip_raw
            except ValueError:
                ip_final = "-"

            # Normalizar severidad con encoding roto
            severidad_raw = idx("severidad").strip().strip("*_` ")
            severidad_normalizada = (severidad_raw
                .replace("CRÃTICA", "CRÍTICA")
                .replace("CRÃ\x8dTICA", "CRÍTICA")
                .replace("CR\u00c3\u008dTICA", "CRÍTICA")
                .upper()
                .strip()
            )

            amenazas.append({
                "numero"   : idx("linea", "número", "numero", "#"),
                "severidad": severidad_normalizada,
                "tipo"     : idx("tipo"),
                "estado"   : idx("estado"),
                "ip"       : ip_final,
                "timestamp": idx("fecha/hora del evento", "fecha del evento", "timestamp", "fecha hora"),
            })

        # Fin de tabla al encontrar otro heading
        if en_tabla and linea.startswith("##") and "AMENAZAS" not in linea.upper():
            en_tabla = False

    return sorted(amenazas, key=lambda item: (
        normalizar_fecha_evento(item.get("timestamp")) is not None,
        normalizar_fecha_evento(item.get("timestamp")) or "",
    ), reverse=True)


def normalizar_fecha_evento(valor: str | None) -> str | None:
    """Valida marcas explícitas del reporte y normaliza a UTC; no deduce fechas."""
    if not valor or valor.strip() in {"-", "—", "N/A", "No disponible"}:
        return None
    texto = valor.strip().strip("`[] ").strip()
    try:
        fecha = datetime.fromisoformat(texto.replace("Z", "+00:00"))
    except ValueError:
        try:
            fecha = datetime.strptime(texto, "%d/%b/%Y:%H:%M:%S %z")
        except ValueError:
            return None
    if fecha.tzinfo is None:
        return None
    return fecha.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def parsear_fecha_access_log(linea: str) -> datetime | None:
    """Lee la hora Apache con su offset y devuelve una fecha consciente de zona."""
    match = re.search(r"\[([^\]]+)\]", linea)
    if not match:
        return None
    try:
        return datetime.strptime(match.group(1), "%d/%b/%Y:%H:%M:%S %z")
    except ValueError:
        return None


def obtener_eventos_recientes(lineas: list[str], limite: int = 100) -> list[dict]:
    """Extrae observaciones de patrones del access log sin afirmar éxito de ataque."""
    eventos = []
    for index, linea in enumerate(lineas):
        match = re.match(r'^([^ ]+) [^ ]+ [^ ]+ \[[^\]]+\] "([A-Z]+) ([^ ]+) HTTP/[^\"]+" (\d{3})', linea)
        if not match:
            continue
        timestamp = parsear_fecha_access_log(linea)
        if timestamp is None:
            continue
        ip, method, target, status = match.groups()
        try:
            ip = str(ipaddress.ip_address(ip))
        except ValueError:
            ip = None
        decoded = unquote_plus(target).casefold()
        category = None
        if "/vulnerabilities/brute/" in decoded and method == "GET" and "username=" in decoded and "password=" in decoded:
            category = "Fuerza bruta"
        # An encoded apostrophe alone is not a SQL indicator: XSS and ordinary
        # names can contain it. Require the decoded SQL pattern itself.
        elif any(pattern in decoded for pattern in ("union select", "select ", "' or '", "or 1=1")):
            category = "SQL injection"
        elif any(pattern in decoded for pattern in ("<script", "alert(", "onerror", "javascript:")):
            category = "XSS"
        elif any(pattern in decoded for pattern in ("../", "..\\", "/etc/passwd")):
            category = "Traversal de rutas"
        elif any(pattern in decoded for pattern in (";cat ", "|cat ", "&&whoami", ";whoami")):
            category = "Inyección de comandos"
        if category is None:
            continue
        request_path = urlsplit(target).path[:180]
        observed_at = timestamp.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
        identity = hashlib.sha256(f"{index}\0{linea}".encode("utf-8", errors="replace")).hexdigest()[:24]
        eventos.append({"id": identity, "observed_at": observed_at, "category": category,
                        "source_ip": ip, "method": method, "path": request_path, "http_status": int(status)})
    eventos.sort(key=lambda item: item["observed_at"], reverse=True)
    return eventos[:limite]


def extraer_ips_del_log(lineas: list[str] | None = None) -> list[str]:
    """
    Extrae direcciones IP observadas en access.log, ordenadas por frecuencia.
    La frecuencia no identifica por sí sola un origen como atacante.
    """
    from collections import Counter
    import re

    if lineas is None:
        captura = capture_file(Path(LOG_PATH))
        lineas = captura.text.splitlines() if captura.text else []
    ips = []

    for linea in lineas:
        campo = linea.split(maxsplit=1)[0] if linea.split(maxsplit=1) else ""
        try:
            ipaddress.ip_address(campo)
            ips.append(campo)
        except ValueError:
            continue

    # Retornar IPs ordenadas por frecuencia (la más activa primero)
    contador = Counter(ips)
    return [ip for ip, _ in contador.most_common()]


def obtener_timeline_ataques(lineas: list[str] | None = None) -> dict:
    import re
    from collections import defaultdict

    if lineas is None:
        captura = capture_file(Path(LOG_PATH))
        lineas = captura.text.splitlines() if captura.text else []

    patrones_sqli  = ["union", "select", "%27", "or+1", "or+%27"]
    patrones_xss   = ["<script", "%3cscript", "alert(", "%3calert", "onerror"]
    patrones_path  = ["../", "%2e%2e", "etc/passwd", "etc%2fpasswd"]
    patrones_brute = ["/vulnerabilities/brute/", "/brute/?username"]
    patrones_cmd   = ["/vulnerabilities/exec/", "%3b", "%7c", "%26%26"]

    ataques = defaultdict(lambda: {
        "sqli": 0, "xss": 0, "path": 0, "brute": 0, "cmd": 0
    })
    periodos = {}

    for linea in lineas:
        ll = linea.lower()
        es_sqli  = any(p in ll for p in patrones_sqli)
        es_xss   = any(p in ll for p in patrones_xss)
        es_path  = any(p in ll for p in patrones_path)
        es_brute = any(p in ll for p in patrones_brute)
        es_cmd   = any(p in ll for p in patrones_cmd)

        if not any([es_sqli, es_xss, es_path, es_brute, es_cmd]):
            continue

        timestamp = parsear_fecha_access_log(linea)
        if not timestamp:
            continue
        hora_utc = timestamp.astimezone(timezone.utc).replace(minute=0, second=0, microsecond=0)
        clave = hora_utc.isoformat(timespec="seconds").replace("+00:00", "Z")
        periodos[clave] = hora_utc
        if es_sqli:  ataques[clave]["sqli"]  += 1
        if es_xss:   ataques[clave]["xss"]   += 1
        if es_path:  ataques[clave]["path"]  += 1
        if es_brute: ataques[clave]["brute"] += 1
        if es_cmd:   ataques[clave]["cmd"]   += 1

    horas = sorted(ataques.keys(), key=lambda clave: periodos[clave])

    return {
        "horas" : horas,
        "counts": [sum(ataques[h].values()) for h in horas],
        "sqli"  : [ataques[h]["sqli"]  for h in horas],
        "xss"   : [ataques[h]["xss"]   for h in horas],
        "path"  : [ataques[h]["path"]  for h in horas],
        "brute" : [ataques[h]["brute"] for h in horas],
        "cmd"   : [ataques[h]["cmd"]   for h in horas],
    }


def obtener_timestamp_reporte() -> str:
    """Retorna la fecha de modificación del reporte actual."""
    captured = capture_current(REPORT_PATH)
    if captured.modified_ns is not None:
        mtime = datetime.fromtimestamp(captured.modified_ns / 1_000_000_000)
        return mtime.strftime("%d/%m %H:%M")
    return "--/-- --:--"


def obtener_estadisticas(amenazas: list[dict]) -> dict:
    """Calcula estadísticas resumen de las amenazas."""
    severidades = [a.get("severidad", "").strip().upper().replace("Í", "I") for a in amenazas]
    criticas = sum(s == "CRITICA" for s in severidades)
    altas = sum(s == "ALTA" for s in severidades)
    medias = sum(s == "MEDIA" for s in severidades)
    bajas = sum(s == "BAJA" for s in severidades)
    reconocidas = criticas + altas + medias + bajas
    ips = len({a.get("ip") for a in amenazas if a.get("ip") not in (None, "", "-")})

    return {
        "total"   : len(amenazas),
        "criticas": criticas,
        "altas"   : altas,
        "medias"  : medias,
        "bajas"   : bajas,
        "desconocidas": len(amenazas) - reconocidas,
        "ips"     : ips,
    }


def _capturar_historial(limite: int | None = 5, *, current: CapturedFile | None = None) -> list[dict]:
    """Captura metadatos y contenido de reportes sin seguir enlaces simbólicos."""
    if not HISTORIAL.exists() or HISTORIAL.is_symlink() or not HISTORIAL.is_dir():
        return []
    archivos = [p for p in HISTORIAL.glob("*.md") if p.is_file() and not p.is_symlink()]
    archivos.sort(key=lambda p: p.name, reverse=True)
    if current is None:
        current = capture_current(REPORT_PATH)
    current_content = current.content if current.status == "available" else None
    historial = []
    for archivo in archivos:
        captura = capture_file(archivo)
        if captura.status != "available":
            continue
        # Cada análisis archiva una copia exacta del informe actual. No contar
        # esa misma publicación dos veces en las vistas de históricos.
        if current_content is not None and captura.content == current_content:
            continue
        partes = archivo.stem.split("_")
        historial.append({
            "nombre": archivo.name,
            "amenazas": len(parsear_amenazas(captura.text or "")),
            "fecha": partes[1] if len(partes) > 1 else "-",
            "hora": partes[2] if len(partes) > 2 else "-",
            "_captura": captura,
        })
        if limite is not None and len(historial) >= limite:
            break
    return historial


def obtener_historial() -> list[dict]:
    """Lista los cinco reportes históricos más recientes para el dashboard anterior."""
    return [{key: value for key, value in item.items() if not key.startswith("_")}
            for item in _capturar_historial(5)]


def obtener_log_reciente(lineas: list[str] | None = None) -> list[str]:
    """Retorna las últimas 8 líneas del log."""
    if lineas is None:
        captura = capture_file(Path(LOG_PATH))
        if captura.status == "missing":
            return ["Log no disponible"]
        lineas = captura.text.splitlines() if captura.text else []
    return lineas[-8:] if lineas else []


def _snapshot_estado(*, include_log_views: bool = True) -> dict:
    """Compone la respuesta desde una captura estable de cada archivo fuente."""
    reporte, structured_result = capture_current_details(REPORT_PATH)
    log = capture_file(Path(LOG_PATH))
    if include_log_views and log.text is not None:
        cached_lines, cached_ips, timeline, recent_events, log_period = _cached_log_views(log.digest, log.text)
        lineas_log = list(cached_lines)
        source_ips = list(cached_ips)
    else:
        lineas_log = []
        source_ips = []
        timeline = {"horas": [], "sqli": [], "xss": [], "path": [], "brute": [], "cmd": [], "counts": []}
        recent_events = []
        log_period = {"first_at": None, "last_at": None, "undated_lines": 0}
    amenazas = parsear_amenazas(reporte.text or "") if reporte.status == "available" else []
    stats = obtener_estadisticas(amenazas)
    historial_capturado = _capturar_historial(5, current=reporte)
    historial = [{key: value for key, value in item.items() if not key.startswith("_")}
                 for item in historial_capturado]

    identity = json.dumps({
        "report": reporte.digest,
        "log": log.digest,
        "history": [item["_captura"].file_id for item in historial_capturado],
    }, sort_keys=True, separators=(",", ":")).encode("utf-8")
    snapshot_id = hashlib.sha256(identity).hexdigest()
    sources = {
        "report": {"status": reporte.status, "modified_at": reporte.modified_at},
        "log": {"status": log.status, "modified_at": log.modified_at},
    }
    health = "ok" if all(item["status"] == "available" for item in sources.values()) else "degraded"
    if any(item["status"] in ("error", "changing") for item in sources.values()):
        health = "unavailable"

    return {
        "snapshot_id": snapshot_id,
        "captured_at": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "health": health,
        "sources": sources,
        "report": reporte,
        "log_capture": log,
        "threats": amenazas,
        "stats": stats,
        "history": historial,
        "history_captures": historial_capturado,
        "log_lines": lineas_log,
        "log_period": dict(log_period),
        "recent_log": (obtener_log_reciente(lineas_log)
                       if include_log_views and log.status == "available"
                       else ["Log no disponible"] if log.status != "available" else []),
        "source_ips": source_ips,
        "recent_events": recent_events,
        "structured_result": structured_result,
        "timeline": timeline,
    }


_LOG_VIEWS_LOCK = threading.Lock()
_LOG_VIEWS_CACHE = None


def _cached_log_views(digest: str | None, content: str):
    """Reuse expensive timeline/IP scans while an immutable log snapshot is unchanged."""
    global _LOG_VIEWS_CACHE
    with _LOG_VIEWS_LOCK:
        if _LOG_VIEWS_CACHE is not None and _LOG_VIEWS_CACHE[0] == digest:
            return _LOG_VIEWS_CACHE[1]
        lines = tuple(content.splitlines())
        ips = tuple(extraer_ips_del_log(list(lines)))
        timeline = obtener_timeline_ataques(list(lines))
        recent_events = tuple(obtener_eventos_recientes(list(lines)))
        dates = sorted(date.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
                       for line in lines if (date := parsear_fecha_access_log(line)) is not None)
        period = {"first_at": dates[0] if dates else None, "last_at": dates[-1] if dates else None,
                  "undated_lines": len(lines) - len(dates)}
        views = (lines, ips, timeline, recent_events, period)
        _LOG_VIEWS_CACHE = (digest, views)
        return views


def _api_error(status: int, code: str, message: str):
    return jsonify({"error": {"code": code, "message": message,
                               "request_id": getattr(g, "request_id", "")}}), status


def _threats_v1(snapshot: dict) -> list[dict]:
    report_id = snapshot["report"].file_id
    structured = snapshot.get("structured_result")
    periods = {",".join(str(o["line_number"]) for o in f["observations"]): event_period(f["observations"])
               for f in structured["findings"]} if structured else {}
    results = []
    for index, threat in enumerate(snapshot["threats"], start=1):
        identity = f"{report_id or 'no-report'}:{index}:{threat.get('numero', '-')}:"
        threat_id = hashlib.sha256(identity.encode("utf-8")).hexdigest()[:24]
        results.append({
            "id": threat_id,
            "number": threat.get("numero", "-"),
            "severity": threat.get("severidad", ""),
            "type": threat.get("tipo", ""),
            "status": threat.get("estado", "-"),
            "source_ip": threat.get("ip", "-"),
            "event_time": normalizar_fecha_evento(threat.get("timestamp")),
            "source_report_id": report_id,
            **periods.get(threat.get("numero", "-"), {}),
        })
    # Las amenazas con fecha verificable aparecen primero; las antiguas que no
    # incluyen fecha quedan al final conservando su orden original.
    return sorted(results, key=lambda item: (bool(item.get("event_time_end") or item["event_time"]),
                                            item.get("event_time_end") or item["event_time"] or ""), reverse=True)


def _state_v1(snapshot: dict) -> dict:
    timeline = snapshot["timeline"]
    periods = []
    keys = ("sqli", "xss", "path", "brute", "cmd")
    for index, period in enumerate(timeline["horas"]):
        periods.append({"period": period, "count": timeline["counts"][index],
                        "matches": {key: timeline[key][index] for key in keys}})
    return {
        "meta": {
            "api_version": "1",
            "schema": "web-defense-ai.estado.v1",
            "snapshot_id": snapshot["snapshot_id"],
            "captured_at": snapshot["captured_at"],
            "consistency": "stable_file_captures",
            "health": snapshot["health"],
            "sources": snapshot["sources"],
            "report_id": snapshot["report"].file_id,
        },
        "data": {
            "stats": snapshot["stats"],
            "threats": _threats_v1(snapshot)[:10],
            "threats_total": len(snapshot["threats"]),
            "threats_truncated": len(snapshot["threats"]) > 10,
            "recent_log": snapshot["recent_log"],
            "log_period": snapshot["log_period"],
            "recent_events": snapshot["recent_events"],
            "source_ips": snapshot["source_ips"][:5],
            "timeline": {"source": "access.log", "meaning": "pattern_matches",
                         "periods": periods},
            "recent_reports": snapshot["history"],
        },
    }


def _pagination(default_size: int = 25, max_size: int = 100):
    try:
        page = int(request.args.get("page", "1"))
        per_page = int(request.args.get("per_page", str(default_size)))
    except (TypeError, ValueError):
        return None, _api_error(400, "invalid_pagination", "page y per_page deben ser números enteros.")
    if page < 1 or per_page < 1 or per_page > max_size:
        return None, _api_error(400, "invalid_pagination", f"page debe ser positivo y per_page estar entre 1 y {max_size}.")
    return {"page": page, "per_page": per_page, "offset": (page - 1) * per_page}, None


def _report_descriptor(path: Path, current: bool = False) -> dict | None:
    if path.is_symlink() or not path.is_file():
        return None
    try:
        stat = path.stat()
    except OSError:
        return None
    modified = datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    identity = f"{path.name}\0{stat.st_mtime_ns}\0{stat.st_ctime_ns}\0{stat.st_size}\0{stat.st_ino}".encode("utf-8")
    return {"id": hashlib.sha256(identity).hexdigest(), "filename": path.name,
            "modified_at": modified, "size_bytes": stat.st_size, "current": current,
            "_path": path, "_modified_ns": stat.st_mtime_ns}


def _catalogo_reportes() -> list[dict]:
    captured = capture_current(REPORT_PATH)
    current = _report_descriptor(captured.path, current=True) if captured.status == "available" else None
    reports = []
    current_content = None
    if current:
        reports.append(current)
        captured_current = captured
        if captured_current.status == "available":
            current_content = captured_current.content
    history = []
    if HISTORIAL.exists() and not HISTORIAL.is_symlink():
        for path in HISTORIAL.glob("*.md"):
            descriptor = _report_descriptor(path)
            if descriptor:
                if current_content is not None and descriptor["size_bytes"] == len(current_content):
                    captured_history = capture_file(descriptor["_path"])
                    if (captured_history.status == "available"
                            and captured_history.content == current_content):
                        continue
                history.append(descriptor)
    history.sort(key=lambda item: (item["_modified_ns"], item["filename"]), reverse=True)
    return reports + history


def limpiar_historial_antiguo(max_reportes: int = 20):
    """
    Mantiene solo los N reportes más recientes en disco.
    El resto se elimina automáticamente.
    """
    if not HISTORIAL.exists():
        return

    archivos = sorted(HISTORIAL.glob("*.md"), reverse=True)

    if len(archivos) > max_reportes:
        for archivo_antiguo in archivos[max_reportes:]:
            archivo_antiguo.unlink()
            print(f"   Reporte antiguo eliminado: {archivo_antiguo.name}")


# ============================================================
# RUTAS FLASK
# ============================================================

@app.route("/")
def index():
    """Página principal del dashboard."""
    if os.getenv("NEXT_PRIMARY_ENABLED") == "1" and _next_primary_ready():
        return redirect("http://127.0.0.1:3000/", code=302)

    snapshot = _snapshot_estado()
    reporte = snapshot["report"].text or ""
    amenazas = snapshot["threats"]
    stats = snapshot["stats"]
    historial = snapshot["history"]
    log_lines = snapshot["recent_log"]
    ultimo_ciclo = (datetime.fromtimestamp(snapshot["report"].modified_ns / 1_000_000_000)
                    .strftime("%d/%m/%Y %H:%M:%S") if snapshot["report"].modified_ns else "Sin datos")

    return render_template(
        "index.html",
        amenazas     = amenazas,
        stats        = stats,
        historial    = historial,
        log_lines    = log_lines,
        ultimo_ciclo = ultimo_ciclo,
        reporte_md   = reporte,
        timeline     = snapshot["timeline"],
    )


def _next_primary_ready():
    """Comprueba Next.js en loopback sin seguir redirecciones ni salir a red."""
    connection = HTTPConnection("127.0.0.1", 3000, timeout=0.35)
    try:
        connection.request("GET", "/")
        response = connection.getresponse()
        return response.status == 200
    except OSError:
        return False
    finally:
        connection.close()


@app.route("/api/estado")
def api_estado():
    """API JSON del estado local; la consulta no sincroniza ni inicia procesos."""
    snapshot = _snapshot_estado()
    return jsonify({
        "stats": snapshot["stats"],
        "amenazas": snapshot["threats"],
        "historial": snapshot["history"],
        "log": snapshot["recent_log"],
        "ips_log": snapshot["source_ips"][:5],
        "timeline": snapshot["timeline"],
        "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
    })


@app.get("/api/v1/openapi.json")
def api_v1_openapi():
    """Contrato OpenAPI publicado junto con la versión inicial de lectura."""
    return jsonify(json.loads((Path(__file__).parent / "openapi-v1.json").read_text(encoding="utf-8")))


@app.get("/api/v1/estado")
def api_v1_estado():
    return jsonify(_state_v1(_snapshot_estado()))


@app.get("/api/v1/salud")
def api_v1_salud():
    sources = {"report": inspect_current(REPORT_PATH),
               "log": inspect_file(Path(LOG_PATH))}
    status = "ok" if all(item["status"] == "available" for item in sources.values()) else "degraded"
    if any(item["status"] == "error" for item in sources.values()):
        status = "unavailable"
    return jsonify({"meta": {"api_version": "1",
                              "captured_at": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")},
                    "data": {"status": status, "sources": sources,
                             "executor": _executor_status(), "ingestion": "unobserved"}})


@app.get("/api/v1/configuracion/llm")
def api_v1_configuracion_llm():
    return jsonify({"meta": {"api_version": "1"}, "data": public_llm_settings()})


@app.put("/api/v1/configuracion/llm")
def api_v1_configuracion_llm_actualizar():
    if request.remote_addr not in {"127.0.0.1", "::1"}:
        return _api_error(403, "local_only", "La configuración solo admite solicitudes locales.")
    if not _local_origin_allowed():
        return _api_error(403, "invalid_origin", "El origen de la solicitud no está autorizado.")
    if not request.is_json:
        return _api_error(415, "json_required", "Envía la configuración como JSON.")
    try:
        settings = save_llm_settings(request.get_json(silent=True))
    except InvalidLLMSettings as error:
        return _api_error(400, "invalid_llm_config", str(error))
    except AlreadyRunning:
        return _api_error(409, "analysis_active", "La configuración no se cambió porque hay un análisis activo.")
    except (OSError, RuntimeError):
        return _api_error(500, "llm_config_save_failed", "No se pudo guardar la configuración local.")
    return jsonify({"meta": {"api_version": "1"}, "data": settings})


def _executor_status():
    db_path = default_db_path()
    if not db_path.is_file() or not db_path.with_suffix(".worker.lock").is_file():
        return "offline"
    try:
        worker = JobStore().worker()
        if worker is None:
            return "offline"
        heartbeat = datetime.fromisoformat(worker["heartbeat_at"].replace("Z", "+00:00"))
        if (datetime.now(timezone.utc) - heartbeat).total_seconds() > 10:
            return "offline"
        with exclusive_lock(db_path.with_suffix(".worker.lock")):
            return "offline"
    except AlreadyRunning:
        return "online"
    except (OSError, ValueError, sqlite3.Error):
        return "unavailable"


def _job_response(job, worker_status=None):
    return {"meta": {"api_version": "1"}, "data": {
        "id": job["id"], "kind": job["kind"], "status": job["status"],
        "phase": job["phase"], "requested_at": job["requested_at"],
        "started_at": job["started_at"], "finished_at": job["finished_at"],
        "last_ingested_at": job["last_ingested_at"], "last_analyzed_at": job["last_analyzed_at"],
        "report_id": job["report_id"], "error_code": job["error_code"],
        "executor": worker_status if worker_status is not None else _executor_status(),
        "deliveries": JobStore().deliveries(job["id"])}}


@app.get("/api/v1/analisis/actual")
def api_v1_analisis_actual():
    job = JobStore().latest() if default_db_path().is_file() else None
    llm = public_llm_settings()
    return jsonify({"meta": {"api_version": "1"}, "data": {
        "manual_enabled": os.getenv("ANALYSIS_MANUAL_ENABLED") == "1",
        "llm_ready": llm["api_key_configured"], "llm_provider": llm["provider"],
        "executor": _executor_status(), "job": _job_response(job)["data"] if job else None}})


@app.get("/api/v1/analisis/<job_id>")
def api_v1_analisis_detalle(job_id):
    if not re.fullmatch(r"[a-f0-9]{32}", job_id):
        return _api_error(400, "invalid_job_id", "El identificador del trabajo no es válido.")
    job = JobStore().get(job_id) if default_db_path().is_file() else None
    if job is None:
        return _api_error(404, "job_not_found", "No se encontró el trabajo.")
    return jsonify(_job_response(job))


@app.post("/api/v1/analisis")
def api_v1_analisis_crear():
    if request.remote_addr not in {"127.0.0.1", "::1"}:
        return _api_error(403, "local_only", "El análisis manual solo admite solicitudes locales.")
    # Preserve local CLI clients using Idempotency-Key without Origin.
    if not _local_origin_allowed(required=False):
        return _api_error(403, "invalid_origin", "El origen de la solicitud no está autorizado.")
    if os.getenv("ANALYSIS_MANUAL_ENABLED") != "1":
        return _api_error(403, "manual_disabled", "El análisis manual está desactivado.")
    if _executor_status() != "online":
        return _api_error(503, "executor_offline", "Inicia el ejecutor antes de solicitar un análisis.")
    key = request.headers.get("Idempotency-Key")
    if not key:
        return _api_error(400, "missing_idempotency_key", "Falta la clave de idempotencia.")
    try:
        job, outcome = JobStore().enqueue("manual", key)
    except ValueError:
        return _api_error(400, "invalid_idempotency_key", "La clave de idempotencia no es válida.")
    if outcome == "busy":
        return jsonify(_job_response(job)), 409
    response = jsonify(_job_response(job))
    response.status_code = 202
    response.headers["Location"] = f"/api/v1/analisis/{job['id']}"
    return response


@app.get("/api/v1/amenazas")
def api_v1_amenazas():
    pagination, error = _pagination()
    if error:
        return error
    # Este recurso filtra filas del reporte; evita recorrer el log completo para
    # calcular timeline e IPs y conserva los mismos hashes de la instantánea.
    snapshot = _snapshot_estado(include_log_views=False)
    items = _threats_v1(snapshot)
    tipo = request.args.get("tipo", "").strip().casefold()
    ip = request.args.get("ip", "").strip().casefold()
    severidad = request.args.get("severidad", "").strip().upper().replace("Í", "I")
    allowed = {"CRITICA", "ALTA", "MEDIA", "BAJA", "DESCONOCIDA"}
    if severidad and severidad not in allowed:
        return _api_error(400, "invalid_severity", "severidad debe ser CRITICA, ALTA, MEDIA, BAJA o DESCONOCIDA.")

    if tipo:
        items = [item for item in items if tipo in item["type"].casefold()]
    if ip:
        items = [item for item in items if ip == item["source_ip"].casefold()]
    if severidad:
        items = [item for item in items if (
            item["severity"].upper().replace("Í", "I") == severidad
            or (severidad == "DESCONOCIDA" and item["severity"].upper() not in {"CRITICA", "CRÍTICA", "ALTA", "MEDIA", "BAJA"})
        )]
    total = len(items)
    start = pagination["offset"]
    selected = items[start:start + pagination["per_page"]]
    return jsonify({"meta": {"api_version": "1", "snapshot_id": snapshot["snapshot_id"],
                              "report_id": snapshot["report"].file_id,
                              "scope": "reporte_actual", "total": total,
                              "page": pagination["page"], "per_page": pagination["per_page"]},
                    "data": selected})


@app.get("/api/v1/reportes")
def api_v1_reportes():
    pagination, error = _pagination(default_size=25, max_size=100)
    if error:
        return error
    items = _catalogo_reportes()
    total = len(items)
    start = pagination["offset"]
    visible = [{key: value for key, value in item.items() if not key.startswith("_")}
               for item in items[start:start + pagination["per_page"]]]
    return jsonify({"meta": {"api_version": "1", "total": total,
                              "page": pagination["page"], "per_page": pagination["per_page"]},
                    "data": visible})


@app.get("/api/v1/reportes/<report_id>")
def api_v1_reporte(report_id):
    if not re.fullmatch(r"[a-f0-9]{64}", report_id):
        return _api_error(400, "invalid_report_id", "El identificador del reporte no tiene un formato válido.")
    match = next((item for item in _catalogo_reportes() if item["id"] == report_id), None)
    if match is None:
        return _api_error(404, "report_not_found", "No se encontró el reporte solicitado.")
    captura, structured = capture_current_details(REPORT_PATH) if match["current"] else (capture_file(match["_path"]), None)
    actual = _report_descriptor(match["_path"], current=match["current"])
    if (captura.status != "available" or captura.path != match["_path"]
            or actual is None or actual["id"] != report_id):
        return _api_error(409, "report_changed", "El reporte cambió mientras se consultaba. Vuelve a cargar la lista.")
    descriptor = {key: value for key, value in actual.items() if not key.startswith("_")}
    return jsonify({"meta": {"api_version": "1", "report_id": report_id},
                    "data": {"report": descriptor, "markdown": captura.text,
                             **({"display_markdown": render_markdown(structured)} if structured else {})}})


@app.route("/api/sincronizar", methods=["POST"])
def api_sincronizar():
    """Sincroniza el log desde Docker; no ejecuta IA ni notifica."""
    if not _local_origin_allowed():
        return jsonify({"ok": False, "error": "El origen de la solicitud no está autorizado."}), 403
    if _executor_status() == "online":
        return jsonify({"ok": False, "error": "El ejecutor coordina la sincronización; deténlo antes de usar esta acción anterior."}), 409
    try:
        # Paso 1: Sincronizar log
        with exclusive_lock(default_db_path().with_suffix(".cycle.lock")):
            sync = run_atomic_copy(
                ["docker", "cp", "dvwa-app:/var/log/apache2/access.log"], Path(LOG_PATH), timeout=15
            )
        if sync.returncode != 0:
            return jsonify({"ok": False, "error": "Error sincronizando log"}), 500
        return jsonify({"ok": True, "analisis_ejecutado": False,
                        "mensaje": "Log sincronizado. No se ha ejecutado un análisis."})

    except FileNotFoundError:
        return jsonify({"ok": False, "error": "No se encontró Docker para sincronizar el log."}), 503
    except AlreadyRunning:
        return jsonify({"ok": False, "error": "Hay una operación coordinada en curso."}), 409
    except subprocess.TimeoutExpired:
        return jsonify({"ok": False, "error": "La sincronización del log superó el tiempo límite."}), 504

    except Exception:
        app.logger.exception("Fallo interno al sincronizar el log")
        return jsonify({"ok": False, "error": "No se pudo completar la sincronización."}), 500
    
@app.route("/report/<nombre>")
def ver_reporte(nombre):
    """Muestra un reporte histórico en formato legible."""
    import re
    if nombre == "reporte_seguridad.md":
        captured = capture_current(REPORT_PATH)
        if captured.status != "available":
            return "Reporte no encontrado.", 404, {"Content-Type": "text/plain; charset=utf-8"}
        return render_template("report.html", contenido=captured.text, nombre=nombre)
    # Acepta nombres como: reporte_20260427_133534.md
    if not re.match(r'^reporte_[\w]+\.md$', nombre):
        return "Archivo no valido.", 400, {"Content-Type": "text/plain; charset=utf-8"}

    ruta = HISTORIAL / nombre
    if not ruta.exists():
        ruta = REPORT_PATH / nombre
        if not ruta.exists():
            return "Reporte no encontrado.", 404, {"Content-Type": "text/plain; charset=utf-8"}

    contenido = ruta.read_text(encoding="utf-8", errors="replace")
    return render_template("report.html", contenido=contenido, nombre=nombre)


# ============================================================
# ARRANQUE
# ============================================================
if __name__ == "__main__":
    print("web-defense-ai V2 — dashboard local en http://127.0.0.1:5000")
    app.run(debug=False, host="127.0.0.1", port=5000)
