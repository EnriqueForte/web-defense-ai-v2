"use client";

import { useEffect, useRef, useState } from "react";

type Observation = { id: string; component: string; actor: string; resource: string; observation: string; effect: string };
type Audit = {
  status: "available" | "missing" | "error" | "disabled";
  mode: "vulnerable" | "corrected" | null;
  run_id: string | null;
  sha256: string | null;
  events: number;
  execution_status: string | null;
  observations: Observation[];
};
const labels: Record<string, string> = {
  foreign_resource_served: "Recurso de otro propietario devuelto", object_access_denied: "Acceso al objeto rechazado",
  docking_without_approval: "Atraque ejecutado sin aprobación", approval_required: "Aprobación exigida",
  permit_reused: "Permiso de atraque reutilizado", permit_reuse_denied: "Reutilización del permiso rechazada",
  internal_canary_read: "Lectura del señuelo interno", canary_fetch_denied: "Lectura del señuelo rechazada",
  cross_origin_cookie_state_change: "Cambio desde otro origen declarado y cookie de sesión",
  http_origin_control_probe: "Cambio en prueba HTTP de origen; navegador no acreditado",
  cross_origin_request_denied: "Solicitud de otro origen rechazada", stored_markup_rendered: "Contenido almacenado sin codificar; ejecución no acreditada",
};
function object(value: unknown): value is Record<string, unknown> {
  return !!value && typeof value === "object" && !Array.isArray(value);
}
function parseAudit(body: unknown): Audit {
  if (!object(body) || !object(body.data)) throw new Error("invalid_audit");
  const data = body.data;
  if (!["available", "missing", "error", "disabled"].includes(String(data.status))) throw new Error("invalid_status");
  const status = data.status as Audit["status"];
  const mode = data.mode === "vulnerable" || data.mode === "corrected" ? data.mode : null;
  if (status !== "available") return {status, mode, run_id: null, sha256: null, events: 0, execution_status: null, observations: []};
  if (!mode || typeof data.run_id !== "string" || !/^[a-f0-9]{32}$/.test(data.run_id)
      || typeof data.sha256 !== "string" || !/^[a-f0-9]{64}$/.test(data.sha256)
      || typeof data.events !== "number" || !Number.isInteger(data.events) || data.events < 1 || data.events > 200
      || typeof data.execution_status !== "string" || !["running", "completed", "failed", "stopped", "interrupted"].includes(data.execution_status)
      || !Array.isArray(data.observations) || data.observations.length > data.events) throw new Error("invalid_capture");
  const observations = data.observations.map((row: unknown) => {
    if (!object(row) || ["id", "component", "actor", "resource", "observation", "effect"].some(key => typeof row[key] !== "string" || (row[key] as string).length > 200)
        || typeof row.id !== "string" || !/^[a-f0-9]{24}$/.test(row.id)) throw new Error("invalid_observation");
    return row as Observation;
  });
  if (new Set(observations.map(row => row.id)).size !== observations.length) throw new Error("duplicate_observation");
  return {status, mode, run_id: data.run_id, sha256: data.sha256, events: data.events, execution_status: data.execution_status, observations};
}

export function ApplicationAuditPanel({captureEnabled}: {captureEnabled: boolean}) {
  const [audit, setAudit] = useState<Audit | null>(null);
  const [error, setError] = useState("");
  const [refresh, setRefresh] = useState(0);
  const [saving, setSaving] = useState(false);
  const [notice, setNotice] = useState("");
  const [loading, setLoading] = useState(true);
  const alive = useRef(true);
  const mutation = useRef<AbortController | null>(null);
  useEffect(() => {
    alive.current = true;
    return () => { alive.current = false; mutation.current?.abort(); };
  }, []);
  async function preserve() {
    if (mutation.current || !captureEnabled || loading || error || audit?.status !== "available" || !audit.run_id || !audit.sha256) return;
    const selected = {run_id: audit.run_id, sha256: audit.sha256};
    const controller = new AbortController();
    mutation.current = controller;
    setSaving(true); setNotice("");
    const timeout = window.setTimeout(() => controller.abort(), 10000);
    try {
      const response = await fetch("/api/v1/fuentes/auditoria/capturar", {method: "POST",
        headers: {"Content-Type": "application/json"}, body: JSON.stringify(selected), signal: controller.signal});
      if (!response.ok) throw new Error("capture_failed");
      const body: unknown = await response.json();
      if (!object(body) || !object(body.data) || typeof body.data.snapshot_id !== "string" || !/^[a-f0-9]{32}$/.test(body.data.snapshot_id)
          || body.data.run_id !== selected.run_id || body.data.original_sha256 !== selected.sha256
          || body.data.analysis_requested !== false || body.data.notifications_requested !== false) throw new Error("invalid_capture");
      if (alive.current) setNotice("Copia de auditoría conservada en V2 para su respaldo. No se ha solicitado un análisis.");
    } catch {
      if (alive.current) setNotice(controller.signal.aborted
        ? "No se confirmó la conservación dentro del plazo. La solicitud puede haberse completado; repetir el mismo lote reutiliza su copia íntegra."
        : "No se confirmó la conservación. Actualiza la fuente y revisa las operaciones activas; el último estado visible se conserva.");
    } finally {
      window.clearTimeout(timeout);
      if (mutation.current === controller) mutation.current = null;
      if (alive.current) setSaving(false);
    }
  }
  useEffect(() => {
    let active = true;
    const controller = new AbortController();
    const timer = window.setTimeout(() => controller.abort(), 10000);
    void (async () => {
      try {
        const response = await fetch("/api/v1/fuentes/auditoria", {cache: "no-store", signal: controller.signal});
        if (!response.ok) throw new Error("audit_failed");
        const next = parseAudit(await response.json());
        if (active && !controller.signal.aborted) { setAudit(next); setError(""); }
      } catch {
        if (active) setError("No se pudo consultar la auditoría. Se conserva la última lectura visible; no se ofrece conservarla hasta actualizarla correctamente.");
      } finally { window.clearTimeout(timer); if (active) setLoading(false); }
    })();
    return () => { active = false; window.clearTimeout(timer); controller.abort(); };
  }, [refresh]);
  return <section className="panel list-panel" aria-label="Auditoría de aplicación de Puerto Umbral">
    <div className="panel-header"><div><div className="panel-kicker">PUERTO UMBRAL · AUDITORÍA DE APLICACIÓN</div><h2>Identidad, recursos y estado</h2>
      <p>Observaciones de eventos capturados por el panel del laboratorio. Reglas separadas del informe del modelo; esta lectura no ejecuta escenarios ni análisis.</p></div>
      <button className="button-secondary" disabled={loading || saving} onClick={() => {setLoading(true); setNotice(""); setRefresh(value => value + 1);}}>Actualizar auditoría</button></div>
    {loading && <p className="status-copy" role="status">Consultando la última auditoría capturada…</p>}
    {error && <p className="status-copy error-copy" role="alert">{error}</p>}
    {!error && !loading && (!audit || audit.status === "missing") && <p className="status-copy">Sin auditoría de aplicación disponible para el modo seleccionado. Las ampliaciones requieren su validación propia.</p>}
    {audit?.status === "disabled" && <p className="status-copy">La fuente de auditoría no está habilitada en este perfil.</p>}
    {audit?.status === "error" && <p className="status-copy error-copy" role="alert">La auditoría no pudo validarse. Conserva las evidencias y revisa su origen.</p>}
    {audit?.status === "available" && <><p className="status-copy log-source-digest">Modo {audit.mode === "corrected" ? "corregido" : "vulnerable"} · Ejecución {audit.run_id} · {audit.events} eventos. SHA-256 {audit.sha256}</p>
      {audit.execution_status !== "completed" && <p className="status-copy">La ejecución del laboratorio no está completada. Este lote puede contener evidencia parcial.</p>}
      <button className="button-secondary" disabled={saving || loading || !!error || !captureEnabled} onClick={() => void preserve()}>{saving ? "Conservando…" : "Conservar copia de auditoría en V2"}</button>
      {!captureEnabled && <p className="status-copy">Para conservar una copia, habilita la captura manual y detén el seguimiento de logs.</p>}
      {audit.observations.length ? <ul className="report-list">{audit.observations.map(row => <li key={row.id}><strong>{labels[row.observation] ?? "Observación pendiente de revisión"}</strong><p className="status-copy">{row.component} · Actor: {row.actor} · Recurso: {row.resource}</p></li>)}</ul>
        : <p className="status-copy">No hay coincidencias de estas reglas. No equivale a ausencia de actividad ni a una evaluación del artefacto F7.</p>}</>}
    {notice && <p className="status-copy" role="status">{notice}</p>}
  </section>;
}
