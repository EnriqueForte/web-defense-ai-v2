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
from flask import Flask, render_template, jsonify, request, g, redirect
from dotenv import load_dotenv
from dashboard.services.read_store import CapturedFile, capture_file, inspect_file, run_atomic_copy
from dashboard.services.analysis_jobs import JobStore, default_db_path
from dashboard.services.runtime_lock import AlreadyRunning, exclusive_lock
from werkzeug.exceptions import HTTPException

# Añadir raíz del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

app = Flask(__name__)


@app.before_request
def asignar_request_id():
    g.request_id = uuid.uuid4().hex
    if request.remote_addr not in {"127.0.0.1", "::1"}:
        if request.path.startswith("/api/"):
            return _api_error(403, "local_only", "El dashboard solo admite conexiones locales.")
        return "Acceso local únicamente.", 403


@app.after_request
def cabeceras_api(response):
    response.headers["X-Request-ID"] = getattr(g, "request_id", "")
    if request.path.startswith("/api/v1/") or request.path == "/api/estado":
        response.headers["Cache-Control"] = "no-store, max-age=0"
        response.headers["Pragma"] = "no-cache"
    return response


@app.errorhandler(HTTPException)
def error_http_api(error):
    if request.path.startswith("/api/v1/"):
        code = "not_found" if error.code == 404 else "method_not_allowed" if error.code == 405 else "http_error"
        message = "No se encontró el recurso solicitado." if error.code == 404 else "La operación no está permitida."
        return _api_error(error.code or 500, code, message)
    return error

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
                # El Markdown no contiene fecha individual de este evento.
                "timestamp": "-",
            })

        # Fin de tabla al encontrar otro heading
        if en_tabla and linea.startswith("##") and "AMENAZAS" not in linea.upper():
            en_tabla = False

    return amenazas


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

    for linea in lineas:
        ll = linea.lower()
        es_sqli  = any(p in ll for p in patrones_sqli)
        es_xss   = any(p in ll for p in patrones_xss)
        es_path  = any(p in ll for p in patrones_path)
        es_brute = any(p in ll for p in patrones_brute)
        es_cmd   = any(p in ll for p in patrones_cmd)

        if not any([es_sqli, es_xss, es_path, es_brute, es_cmd]):
            continue

        match = re.search(r'\[(\d{2}/\w+/\d{4}):(\d{2}):', linea)
        if not match:
            continue

        clave = f"{match.group(1)} {match.group(2)}h"
        if es_sqli:  ataques[clave]["sqli"]  += 1
        if es_xss:   ataques[clave]["xss"]   += 1
        if es_path:  ataques[clave]["path"]  += 1
        if es_brute: ataques[clave]["brute"] += 1
        if es_cmd:   ataques[clave]["cmd"]   += 1

    meses = {nombre: numero for numero, nombre in enumerate(
        ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"), 1
    )}

    def orden_temporal(clave):
        fecha, hora = clave.split()
        dia, mes, anio = fecha.split("/")
        return (int(anio), meses.get(mes, 0), int(dia), int(hora[:-1]))

    horas = sorted(ataques.keys(), key=orden_temporal)

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
    ruta = REPORT_PATH / "reporte_seguridad.md"
    if ruta.exists():
        mtime = datetime.fromtimestamp(ruta.stat().st_mtime)
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


def _capturar_historial(limite: int | None = 5) -> list[dict]:
    """Captura metadatos y contenido de reportes sin seguir enlaces simbólicos."""
    if not HISTORIAL.exists() or HISTORIAL.is_symlink() or not HISTORIAL.is_dir():
        return []
    archivos = [p for p in HISTORIAL.glob("*.md") if p.is_file() and not p.is_symlink()]
    archivos.sort(key=lambda p: p.name, reverse=True)
    if limite is not None:
        archivos = archivos[:limite]
    historial = []
    for archivo in archivos:
        captura = capture_file(archivo)
        if captura.status != "available":
            continue
        partes = archivo.stem.split("_")
        historial.append({
            "nombre": archivo.name,
            "amenazas": len(parsear_amenazas(captura.text or "")),
            "fecha": partes[1] if len(partes) > 1 else "-",
            "hora": partes[2] if len(partes) > 2 else "-",
            "_captura": captura,
        })
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
    reporte = capture_file(REPORT_PATH / "reporte_seguridad.md")
    log = capture_file(Path(LOG_PATH))
    if include_log_views and log.text is not None:
        cached_lines, cached_ips, timeline = _cached_log_views(log.digest, log.text)
        lineas_log = list(cached_lines)
        source_ips = list(cached_ips)
    else:
        lineas_log = []
        source_ips = []
        timeline = {"horas": [], "sqli": [], "xss": [], "path": [], "brute": [], "cmd": [], "counts": []}
    amenazas = parsear_amenazas(reporte.text or "") if reporte.status == "available" else []
    stats = obtener_estadisticas(amenazas)
    historial_capturado = _capturar_historial(5)
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
        "recent_log": (obtener_log_reciente(lineas_log)
                       if include_log_views and log.status == "available"
                       else ["Log no disponible"] if log.status != "available" else []),
        "source_ips": source_ips,
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
        views = (lines, ips, timeline)
        _LOG_VIEWS_CACHE = (digest, views)
        return views


def _api_error(status: int, code: str, message: str):
    return jsonify({"error": {"code": code, "message": message,
                               "request_id": getattr(g, "request_id", "")}}), status


def _threats_v1(snapshot: dict) -> list[dict]:
    report_id = snapshot["report"].file_id
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
            "event_time": None,
            "source_report_id": report_id,
        })
    return results


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
    reports = []
    current = _report_descriptor(REPORT_PATH / "reporte_seguridad.md", current=True)
    if current:
        reports.append(current)
    if HISTORIAL.exists() and not HISTORIAL.is_symlink():
        for path in HISTORIAL.glob("*.md"):
            descriptor = _report_descriptor(path)
            if descriptor:
                reports.append(descriptor)
    return sorted(reports, key=lambda item: (item["_modified_ns"], item["filename"]), reverse=True)


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
    sources = {"report": inspect_file(REPORT_PATH / "reporte_seguridad.md"),
               "log": inspect_file(Path(LOG_PATH))}
    status = "ok" if all(item["status"] == "available" for item in sources.values()) else "degraded"
    if any(item["status"] == "error" for item in sources.values()):
        status = "unavailable"
    return jsonify({"meta": {"api_version": "1",
                              "captured_at": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")},
                    "data": {"status": status, "sources": sources,
                             "executor": _executor_status(), "ingestion": "unobserved"}})


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
    return jsonify({"meta": {"api_version": "1"}, "data": {
        "manual_enabled": os.getenv("ANALYSIS_MANUAL_ENABLED") == "1",
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
    origin = request.headers.get("Origin")
    if origin and origin not in {"http://127.0.0.1:3000", "http://127.0.0.1:5000"}:
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
    captura = capture_file(match["_path"])
    actual = _report_descriptor(match["_path"], current=match["current"])
    if captura.status != "available" or actual is None or actual["id"] != report_id:
        return _api_error(409, "report_changed", "El reporte cambió mientras se consultaba. Vuelve a cargar la lista.")
    descriptor = {key: value for key, value in actual.items() if not key.startswith("_")}
    return jsonify({"meta": {"api_version": "1", "report_id": report_id},
                    "data": {"report": descriptor, "markdown": captura.text}})


@app.route("/api/sincronizar", methods=["POST"])
def api_sincronizar():
    """Sincroniza el log desde Docker; no ejecuta IA ni notifica."""
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
    # Acepta nombres como: reporte_20260427_133534.md
    if not re.match(r'^reporte_[\w]+\.md$', nombre):
        return f"Archivo no valido: {nombre}", 400

    ruta = HISTORIAL / nombre
    if not ruta.exists():
        ruta = REPORT_PATH / nombre
        if not ruta.exists():
            return f"Reporte no encontrado: {nombre}", 404

    contenido = ruta.read_text(encoding="utf-8", errors="replace")
    return render_template("report.html", contenido=contenido, nombre=nombre)


# ============================================================
# ARRANQUE
# ============================================================
if __name__ == "__main__":
    print("web-defense-ai V2 — dashboard local en http://127.0.0.1:5000")
    app.run(debug=False, host="127.0.0.1", port=5000)
