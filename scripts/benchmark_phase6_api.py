"""Benchmark the local Flask read API with synthetic logs and reports only."""

import concurrent.futures
import ctypes
import json
import math
import os
import platform
import tempfile
import sys
import threading
import time
import urllib.request
from pathlib import Path

from werkzeug.serving import WSGIRequestHandler, make_server

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class QuietRequestHandler(WSGIRequestHandler):
    def log(self, _type, _message, *args):
        pass


def synthetic_log(count):
    lines = []
    for index in range(count):
        minute, second = divmod(index, 60)
        target = ("/vulnerabilities/sqli/?id=1%20UNION%20SELECT"
                  if index % 5 == 0 else "/index.php")
        ip = f"198.51.100.{index % 200 + 1}"
        lines.append(
            f'{ip} - - [28/Sep/2026:12:{minute % 60:02d}:{second:02d} +0000] '
            f'"GET {target} HTTP/1.1" 200 512'
        )
    return "\n".join(lines) + "\n"


def synthetic_report():
    rows = [
        "## AMENAZAS DETECTADAS",
        "| Línea | Severidad | Tipo | Estado | IP Origen |",
        "| --- | --- | --- | --- | --- |",
    ]
    for index in range(1, 101):
        severity = "ALTA" if index % 2 else "MEDIA"
        rows.append(
            f"| {index} | {severity} | SQLi sintética | Prueba | "
            f"198.51.100.{index % 200 + 1} |"
        )
    return "\n".join(rows) + "\n"


def total_memory_gb():
    if not hasattr(ctypes, "windll"):
        return None

    class MemoryStatus(ctypes.Structure):
        _fields_ = [
            ("length", ctypes.c_ulong), ("memory_load", ctypes.c_ulong),
            ("total_phys", ctypes.c_ulonglong), ("avail_phys", ctypes.c_ulonglong),
            ("total_page_file", ctypes.c_ulonglong), ("avail_page_file", ctypes.c_ulonglong),
            ("total_virtual", ctypes.c_ulonglong), ("avail_virtual", ctypes.c_ulonglong),
            ("avail_extended_virtual", ctypes.c_ulonglong),
        ]

    status = MemoryStatus()
    status.length = ctypes.sizeof(status)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
        return None
    return round(status.total_phys / 1024 ** 3, 1)


def measure(url, requests_count):
    durations = []
    for _ in range(requests_count):
        started = time.perf_counter()
        with urllib.request.urlopen(url, timeout=20) as response:
            response.read()
            if response.status != 200:
                raise RuntimeError(f"HTTP {response.status}")
        durations.append((time.perf_counter() - started) * 1000)
    return durations


def main():
    with tempfile.TemporaryDirectory(prefix="phase6-bench-") as temp:
        root = Path(temp)
        report_dir = root / "reports"
        history = report_dir / "historial"
        report_dir.mkdir()
        history.mkdir()
        log_path = root / "access.log"
        (report_dir / "reporte_seguridad.md").write_text(synthetic_report(), encoding="utf-8")
        os.environ["REPORT_PATH"] = str(report_dir)
        os.environ["LOG_PATH"] = str(log_path)
        os.environ["ANALYSIS_DB_PATH"] = str(root / "analysis.sqlite3")
        os.environ["NEXT_PRIMARY_ENABLED"] = "0"
        os.environ["ANALYSIS_MANUAL_ENABLED"] = "0"

        from dashboard import app as dashboard
        dashboard.REPORT_PATH = report_dir
        dashboard.HISTORIAL = history
        dashboard.LOG_PATH = str(log_path)

        server = make_server("127.0.0.1", 0, dashboard.app, threaded=True,
                             request_handler=QuietRequestHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        with urllib.request.urlopen(f"http://127.0.0.1:{server.server_port}/", timeout=10) as response:
            rollback_status = response.status
            response.read()
        if rollback_status != 200:
            raise RuntimeError(f"Flask rollback entry returned HTTP {rollback_status}")
        endpoints = (
            ("/api/v1/estado", 500),
            ("/api/v1/amenazas?severidad=ALTA&per_page=25", 200),
        )
        results = []
        try:
            for label, line_count in (("actual-88-lineas", 88),
                                      ("ampliado-10000-lineas", 10000)):
                log_path.write_text(synthetic_log(line_count), encoding="utf-8")
                for clients in (1, 5, 10):
                    for endpoint, threshold in endpoints:
                        url = f"http://127.0.0.1:{server.server_port}{endpoint}"
                        with concurrent.futures.ThreadPoolExecutor(max_workers=clients) as pool:
                            samples = [
                                sample
                                for batch in pool.map(
                                    lambda _: measure(url, 20), range(clients)
                                )
                                for sample in batch
                            ]
                        ordered = sorted(samples)
                        p95 = ordered[math.ceil(0.95 * len(ordered)) - 1]
                        results.append({
                            "dataset": label,
                            "clients": clients,
                            "endpoint": endpoint.split("?", 1)[0],
                            "requests": len(samples),
                            "p50_ms": round(ordered[len(ordered) // 2], 1),
                            "p95_ms": round(p95, 1),
                            "threshold_ms": threshold,
                            "pass": p95 < threshold,
                        })
        finally:
            server.shutdown()
            thread.join(timeout=2)
            server.server_close()

        print(json.dumps({
            "python": platform.python_version(),
            "platform": platform.platform(),
            "processor": platform.processor(),
            "cpu_count": os.cpu_count(),
            "memory_gb": total_memory_gb(),
            "flask_rollback_http_status": rollback_status,
            "results": results,
        }))
        return 0 if all(item["pass"] for item in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
