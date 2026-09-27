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
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, jsonify
from dotenv import load_dotenv

# Añadir raíz del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

app = Flask(__name__)

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
            severidad_raw = idx("severidad")
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


def extraer_ips_del_log() -> list[str]:
    """
    Extrae las IPs únicas del access.log ordenadas por frecuencia.
    La IP más frecuente es la más probable atacante.
    """
    from collections import Counter
    import re

    ruta = Path(LOG_PATH)
    if not ruta.exists():
        return []

    lineas = ruta.read_text(encoding="utf-8", errors="replace").splitlines()
    ips = []

    for linea in lineas:
        # La IP siempre es el primer campo en el log de Apache
        match = re.match(r'^(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', linea)
        if match:
            ips.append(match.group(1))

    # Retornar IPs ordenadas por frecuencia (la más activa primero)
    contador = Counter(ips)
    return [ip for ip, _ in contador.most_common()]


def obtener_timeline_ataques() -> dict:
    import re
    from collections import defaultdict

    ruta = Path(LOG_PATH)
    if not ruta.exists():
        return {"horas": [], "counts": [], "sqli": [],
                "xss": [], "path": [], "brute": [], "cmd": []}

    lineas = ruta.read_text(encoding="utf-8", errors="replace").splitlines()

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


def obtener_historial() -> list[dict]:
    """Lista los reportes históricos ordenados por fecha."""
    if not HISTORIAL.exists():
        return []

    # Mostrar solo los 5 más recientes en el dashboard
    # El resto se conserva en disco en reports/historial/
    archivos = sorted(HISTORIAL.glob("*.md"), reverse=True)[:5]
    
    historial = []
    for archivo in archivos:
        contenido = archivo.read_text(encoding="utf-8", errors="replace")
        amenazas  = parsear_amenazas(contenido)
        historial.append({
            "nombre"  : archivo.name,
            "amenazas": len(amenazas),
            "fecha"   : archivo.stem.split("_")[1] if "_" in archivo.stem else "-",
            "hora"    : archivo.stem.split("_")[2] if len(archivo.stem.split("_")) > 2 else "-",
        })

    return historial


def obtener_log_reciente() -> list[str]:
    """Retorna las últimas 8 líneas del log."""
    ruta = Path(LOG_PATH)
    if not ruta.exists():
        return ["Log no disponible"]
    lineas = ruta.read_text(encoding="utf-8", errors="replace").splitlines()
    return lineas[-8:] if lineas else []


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
    reporte_path = REPORT_PATH / "reporte_seguridad.md"
    reporte      = ""
    amenazas     = []
    stats        = {"total": 0, "criticas": 0, "altas": 0, "medias": 0, "ips": 0}
    ultimo_ciclo = "Sin datos"

    if reporte_path.exists():
        reporte  = reporte_path.read_text(encoding="utf-8", errors="replace")
        amenazas = parsear_amenazas(reporte)
        stats    = obtener_estadisticas(amenazas)
        mtime    = datetime.fromtimestamp(reporte_path.stat().st_mtime)
        ultimo_ciclo = mtime.strftime("%d/%m/%Y %H:%M:%S")

    historial = obtener_historial()
    log_lines = obtener_log_reciente()

    stats.setdefault("bajas", 0)
    stats.setdefault("desconocidas", 0)

    return render_template(
        "index.html",
        amenazas     = amenazas,
        stats        = stats,
        historial    = historial,
        log_lines    = log_lines,
        ultimo_ciclo = ultimo_ciclo,
        reporte_md   = reporte,
        timeline     = obtener_timeline_ataques(),
    )


@app.route("/api/estado")
def api_estado():
    """API JSON del estado local; la consulta no sincroniza ni inicia procesos."""

    reporte_path = REPORT_PATH / "reporte_seguridad.md"
    amenazas     = []

    if reporte_path.exists():
        reporte  = reporte_path.read_text(encoding="utf-8", errors="replace")
        amenazas = parsear_amenazas(reporte)

    stats = obtener_estadisticas(amenazas)

    ips_log = extraer_ips_del_log()

    return jsonify({
        "stats"    : stats,
        "amenazas" : amenazas,
        "historial": obtener_historial(),
        "log"      : obtener_log_reciente(),
        "ips_log"  : ips_log[:5],
        "timeline" : obtener_timeline_ataques(),
        "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
    })


@app.route("/api/sincronizar", methods=["POST"])
def api_sincronizar():
    """Sincroniza el log desde Docker; no ejecuta IA ni notifica."""
    try:
        # Paso 1: Sincronizar log
        Path(LOG_PATH).parent.mkdir(parents=True, exist_ok=True)
        sync = subprocess.run(
            ["docker", "cp", "dvwa-app:/var/log/apache2/access.log", LOG_PATH],
            capture_output=True, text=True, timeout=15
        )
        if sync.returncode != 0:
            return jsonify({"ok": False, "error": "Error sincronizando log"}), 500
        return jsonify({"ok": True, "analisis_ejecutado": False,
                        "mensaje": "Log sincronizado. No se ha ejecutado un análisis."})

    except FileNotFoundError:
        return jsonify({"ok": False, "error": "No se encontró Docker para sincronizar el log."}), 503
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
    print("\n  web-defense-ai V2 — Dashboard · T3r0S3c")
    print("  Abre tu navegador en: http://localhost:5000\n")
    app.run(debug=True, host="0.0.0.0", port=5000)
