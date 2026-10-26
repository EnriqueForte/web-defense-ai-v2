"use client";

import { useCallback, useEffect, useRef, useState } from "react";

type Source = {
  source: string;
  status: string;
  mode: string | null;
  captured_at: string | null;
  snapshot_id: string | null;
  sha256: string | null;
  line_count: number | null;
  running_at_capture: boolean | null;
  manual_capture_enabled: boolean;
};

const labels: Record<string, string> = {
  available: "Captura disponible", stale: "Captura antigua", missing: "Sin captura",
  error: "Captura no disponible", changing: "Copia y snapshot no coinciden",
  mode_mismatch: "El modo del perfil ha cambiado", unobserved: "Sin metadatos de captura",
};

function parseSource(body: unknown): Source {
  if (!body || typeof body !== "object" || !("data" in body) || !body.data || typeof body.data !== "object") {
    throw new Error("Respuesta de fuente no válida.");
  }
  const data = body.data as Record<string, unknown>;
  if (typeof data.source !== "string" || typeof data.status !== "string" || typeof data.manual_capture_enabled !== "boolean") {
    throw new Error("Estado de fuente incompleto.");
  }
  return {
    source: data.source, status: data.status, manual_capture_enabled: data.manual_capture_enabled,
    mode: typeof data.mode === "string" ? data.mode : null,
    captured_at: typeof data.captured_at === "string" ? data.captured_at : null,
    snapshot_id: typeof data.snapshot_id === "string" && /^[a-f0-9]{32}$/.test(data.snapshot_id) ? data.snapshot_id : null,
    sha256: typeof data.sha256 === "string" && /^[a-f0-9]{64}$/.test(data.sha256) ? data.sha256 : null,
    line_count: typeof data.line_count === "number" && Number.isInteger(data.line_count) && data.line_count >= 0 ? data.line_count : null,
    running_at_capture: typeof data.running_at_capture === "boolean" ? data.running_at_capture : null,
  };
}

export function LogSourcePanel() {
  const [source, setSource] = useState<Source | null>(null);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const alive = useRef(true);
  const controllers = useRef(new Set<AbortController>());

  const load = useCallback(async (capture = false) => {
    const controller = new AbortController();
    controllers.current.add(controller);
    let timedOut = false;
    const timeout = setTimeout(() => { timedOut = true; controller.abort(); }, capture ? 45000 : 10000);
    setBusy(true);
    setError("");
    setMessage("");
    try {
      const response = await fetch(`/api/v1/fuentes/log${capture ? "/capturar" : ""}`, {
        method: capture ? "POST" : "GET", cache: "no-store", signal: controller.signal,
        headers: { Accept: "application/json", ...(capture ? { "Content-Type": "application/json" } : {}) },
        ...(capture ? { body: "{}" } : {}),
      });
      if (!response.ok) throw new Error(`No se completó la ${capture ? "captura" : "lectura"} (HTTP ${response.status}). Revisa la fuente y el estado del ejecutor.`);
      const next = parseSource(await response.json());
      if (!alive.current || controller.signal.aborted) return;
      setSource(next);
      if (capture) setMessage("Copia actualizada. No se ha solicitado un análisis ni enviado notificaciones. Usa Actualizar para releer la actividad.");
    } catch (failure) {
      if (alive.current && (!controller.signal.aborted || timedOut)) {
        setError(timedOut ? "La solicitud agotó su tiempo. Se conserva el último estado visible." : failure instanceof Error ? failure.message : "Fuente no disponible.");
        if (capture) setSource(previous => previous ? { ...previous, status: "error" } : previous);
      }
    } finally {
      clearTimeout(timeout);
      controllers.current.delete(controller);
      if (alive.current) setBusy(controllers.current.size > 0);
    }
  }, []);

  useEffect(() => {
    alive.current = true;
    void load();
    const active = controllers.current;
    return () => { alive.current = false; for (const controller of active) controller.abort(); };
  }, [load]);

  if (source && source.source !== "puerto-umbral") return null;
  return <section className="panel list-panel" aria-label="Fuente de Puerto Umbral">
    <div className="panel-header"><div><div className="panel-kicker">PUERTO UMBRAL · CAPTURA MANUAL</div><h2>Fuente del laboratorio</h2><p>Leer el estado consulta archivos locales. Capturar obtiene logs de Apache y no inicia un análisis.</p></div></div>
    <p className="status-copy" role="status">{source ? labels[source.status] ?? "Estado pendiente de revisión" : "Consultando metadatos de la fuente…"}{source?.mode ? ` · Modo ${source.mode === "corrected" ? "corregido" : "vulnerable"}` : ""}</p>
    {source?.captured_at && <p className="status-copy">Última captura: {new Date(source.captured_at).toLocaleString("es-ES", { timeZone: "Europe/Madrid" })} (Madrid) · {source.line_count ?? "—"} líneas. Origen {source.running_at_capture ? "en ejecución" : "detenido"} cuando se capturó; no es una comprobación de su estado actual.</p>}
    {source?.snapshot_id && <p className="status-copy">Snapshot <code>{source.snapshot_id}</code></p>}
    {source?.sha256 && <p className="status-copy log-source-digest">SHA-256 <code>{source.sha256}</code></p>}
    <div className="settings-actions"><button className="button-secondary" disabled={busy} onClick={() => void load()}>Actualizar estado de fuente</button><button className="button-primary" disabled={busy || !source?.manual_capture_enabled} onClick={() => void load(true)}>{busy ? "Procesando…" : "Capturar log de Puerto Umbral"}</button></div>
    {message && <p className="status-copy" role="status">{message}</p>}
    {error && <p className="status-copy error-copy" role="alert">{error} No se interpreta como ausencia de incidentes.</p>}
  </section>;
}
