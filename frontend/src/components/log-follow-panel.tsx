"use client";

import { useCallback, useEffect, useRef, useState } from "react";

type Action = "leer" | "iniciar" | "pausar" | "reanudar" | "detener";
type Following = {
  status: string; enabled: boolean; session_active: boolean; owned_here: boolean;
  in_flight: boolean; cycles: number | null; snapshots_published: number | null;
  unchanged_cycles: number | null; interval_seconds: number | null;
  last_success_at: string | null; last_cycle_seconds: number | null;
  expires_at: string | null; last_event: string | null; error_code: string | null;
};
const labels: Record<string, string> = {
  stopped: "Detenido", following: "Siguiendo logs", paused: "Pausado",
  pausing: "Pausa solicitada; esperando al ciclo en curso",
  stopping: "Parada solicitada; esperando confirmación", completed: "Sesión finalizada por duración",
  interrupted: "Sesión interrumpida; no se reanuda automáticamente", error: "Seguimiento con error",
};
const events: Record<string, string> = {
  baseline: "Referencia inicial de la ventana", unchanged: "Sin cambios en la ventana",
  appended: "Nuevas líneas observadas", window_shift: "Ventana desplazada; historial limitado",
  source_changed: "Cambió la identidad o el reinicio del origen; nueva referencia",
  discontinuity: "Discontinuidad: posible rotación, truncado o salida de la ventana",
};
const active = new Set(["following", "paused", "pausing", "stopping"]);
const errors: Record<string, string> = {
  source_unavailable: "La fuente no está disponible.", source_stopped: "La pasarela está detenida.",
  capture_storage_limit: "Se alcanzó el límite de almacenamiento o espacio libre.",
  unexpected_source: "La identidad de la fuente no coincide.",
  source_configuration_changed: "La configuración de la fuente ha cambiado.",
  source_bindings_changed: "Los puertos de la fuente han cambiado.",
  invalid_access_format: "El formato del registro no es válido.",
  incomplete_access_line: "La última línea del registro está incompleta.",
  source_changed_during_capture: "El origen cambió durante la captura.",
  follow_lock_unknown: "No se pudo comprobar el bloqueo de la sesión.",
  invalid_follow_state: "Los metadatos de seguimiento no se pudieron leer.",
};
const date = (value: string) => `${new Date(value).toLocaleString("es-ES", { timeZone: "Europe/Madrid" })} (Madrid)`;
const text = (d: Record<string, unknown>, key: string) => typeof d[key] === "string" ? d[key] as string : null;
const count = (d: Record<string, unknown>, key: string) => typeof d[key] === "number" && Number.isSafeInteger(d[key]) && (d[key] as number) >= 0 ? d[key] as number : null;

function parse(body: unknown): Following {
  if (!body || typeof body !== "object" || !("data" in body) || !body.data || typeof body.data !== "object") throw new Error("Respuesta de seguimiento no válida.");
  const envelope = body.data as Record<string, unknown>;
  const candidate = "following" in envelope ? envelope.following : envelope;
  if (!candidate || typeof candidate !== "object") throw new Error("Estado de seguimiento incompleto.");
  const d = candidate as Record<string, unknown>;
  if (typeof d.status !== "string" || !Object.hasOwn(labels, d.status) || typeof d.enabled !== "boolean" || typeof d.owned_here !== "boolean" || typeof d.session_active !== "boolean") throw new Error("Estado de seguimiento incompleto.");
  return {
    status: d.status, enabled: d.enabled, owned_here: d.owned_here, session_active: d.session_active,
    in_flight: d.in_flight === true, cycles: count(d, "cycles"), snapshots_published: count(d, "snapshots_published"),
    unchanged_cycles: count(d, "unchanged_cycles"), interval_seconds: count(d, "interval_seconds"),
    last_success_at: text(d, "last_success_at"), expires_at: text(d, "expires_at"), last_event: text(d, "last_event"), error_code: text(d, "error_code"),
    last_cycle_seconds: typeof d.last_cycle_seconds === "number" && Number.isFinite(d.last_cycle_seconds) && d.last_cycle_seconds >= 0 ? d.last_cycle_seconds : null,
  };
}

export function LogFollowPanel({ onSourceUpdated }: { onSourceUpdated: () => void }) {
  const [state, setState] = useState<Following | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [interval, setIntervalSeconds] = useState(5);
  const [duration, setDuration] = useState(1800);
  const current = useRef<AbortController | null>(null);
  const updated = useRef(onSourceUpdated);
  useEffect(() => { updated.current = onSourceUpdated; }, [onSourceUpdated]);

  const load = useCallback(async (action: Action = "leer") => {
    if (current.current) return;
    const controller = new AbortController();
    current.current = controller;
    setBusy(true);
    setError("");
    let timedOut = false;
    const timeout = setTimeout(() => { timedOut = true; controller.abort(); }, 10000);
    try {
      const mutate = action !== "leer";
      const body = action === "iniciar" ? { interval_seconds: interval, duration_seconds: duration } : {};
      const response = await fetch(`/api/v1/fuentes/log/seguimiento${mutate ? `/${action}` : ""}`, {
        method: mutate ? "POST" : "GET", cache: "no-store", signal: controller.signal,
        headers: { Accept: "application/json", ...(mutate ? { "Content-Type": "application/json" } : {}) },
        ...(mutate ? { body: JSON.stringify(body) } : {}),
      });
      if (!response.ok) throw new Error(`No se completó el control (HTTP ${response.status}). Actualiza el estado y revisa la sesión y el ejecutor antes de repetir.`);
      const next = parse(await response.json());
      if (controller.signal.aborted) return;
      setState(next);
      updated.current();
    } catch (failure) {
      if (current.current === controller && (!controller.signal.aborted || timedOut)) setError(timedOut ? "La solicitud agotó su tiempo. Consulta el estado antes de repetir: la operación podría haberse completado." : failure instanceof Error ? failure.message : "Seguimiento no disponible.");
    } finally {
      clearTimeout(timeout);
      if (current.current === controller) { current.current = null; setBusy(false); }
    }
  }, [interval, duration]);

  useEffect(() => {
    const initial = window.setTimeout(() => void load(), 0);
    return () => { window.clearTimeout(initial); current.current?.abort(); current.current = null; };
  }, [load]);
  const polling = !!state && active.has(state.status);
  useEffect(() => {
    if (!polling) return;
    // Polling reads metadata only; the explicit server session owns captures.
    const timer = window.setInterval(() => { if (document.visibilityState === "visible") void load(); }, 2000);
    return () => window.clearInterval(timer);
  }, [polling, load]);

  return <div className="log-follow-controls" role="group" aria-labelledby="log-follow-title">
    <h3 id="log-follow-title">Seguimiento de logs</h3>
    <p className="status-copy" role="status">{state ? labels[state.status] : "Consultando estado del seguimiento…"}{state?.in_flight ? " · Lectura en curso" : ""}</p>
    <p className="status-copy">Actualiza la evidencia sin iniciar análisis ni notificaciones. La sesión continúa al cambiar de vista o cerrar esta pestaña, hasta detenerla, cerrar V2 o agotar su duración.</p>
    <p className="status-copy">La pausa mantiene el bloqueo y no amplía la duración. Detén el seguimiento antes de capturar manualmente, analizar o respaldar.</p>
    <div className="settings-actions">
      <label>Intervalo <select aria-label="Intervalo de seguimiento" value={interval} disabled={busy || state?.session_active} onChange={event => setIntervalSeconds(Number(event.target.value))}>{[5, 10, 30, 60].map(value => <option key={value} value={value}>{value} segundos</option>)}</select></label>
      <label>Duración <select aria-label="Duración de seguimiento" value={duration} disabled={busy || state?.session_active} onChange={event => setDuration(Number(event.target.value))}>{[300, 900, 1800].map(value => <option key={value} value={value}>{value / 60} minutos</option>)}</select></label>
    </div>
    <div className="settings-actions">
      <button className="button-primary" disabled={busy || !state?.enabled || state.session_active} onClick={() => void load("iniciar")}>Iniciar seguimiento</button>
      <button className="button-secondary" disabled={busy || !state?.owned_here || state.status !== "following"} onClick={() => void load("pausar")}>Pausar</button>
      <button className="button-secondary" disabled={busy || !state?.owned_here || state.status !== "paused"} onClick={() => void load("reanudar")}>Reanudar</button>
      <button className="button-secondary" disabled={busy || !state?.owned_here || !state.session_active || state.status === "stopping"} onClick={() => void load("detener")}>Detener seguimiento</button>
      <button className="button-secondary" disabled={busy} onClick={() => void load()}>Actualizar seguimiento</button>
    </div>
    {state?.session_active && !state.owned_here && <p className="status-copy error-copy">La sesión pertenece a otro proceso o su estado no pudo comprobarse. Revisa la consola propietaria antes de iniciar otra.</p>}
    {state && !state.enabled && <p className="status-copy">Seguimiento deshabilitado en este perfil.</p>}
    {state && state.cycles !== null && <p className="status-copy">Ciclos válidos: {state.cycles} · Snapshots nuevos: {state.snapshots_published ?? "—"} · Sin cambios: {state.unchanged_cycles ?? "—"} · Intervalo de sesión: {state.interval_seconds ?? "—"} s.</p>}
    {state?.last_success_at && <p className="status-copy">Último ciclo válido: {date(state.last_success_at)} · {state.last_cycle_seconds ?? "—"} s de lectura.</p>}
    {state?.expires_at && <p className="status-copy">Fin de duración: {date(state.expires_at)}</p>}
    {state?.last_event && <p className="status-copy">{events[state.last_event] ?? "Cambio pendiente de revisión"}. Una ventana de log no acredita historial completo.</p>}
    {(state?.status === "pausing" || state?.status === "stopping") && <p className="status-copy">La operación todavía no está confirmada.</p>}
    {(state?.status === "error" || error) && <p className="status-copy error-copy" role="alert">{error || (state?.error_code && errors[state.error_code]) || "No se completó el seguimiento."} Se conserva la última evidencia válida; un error no significa ausencia de eventos.</p>}
  </div>;
}
