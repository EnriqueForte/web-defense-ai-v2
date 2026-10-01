"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import Link from "next/link";
import { getApi, requestAnalysis, validState, type AnalysisCurrent, type PageResponse, type Report, type ReportDetail, type StateResponse, type Threat } from "@/lib/api";

type View = "Resumen" | "Amenazas" | "Reportes" | "Actividad";
const views: View[] = ["Resumen", "Amenazas", "Reportes", "Actividad"];
const severities = ["Todas", "CRITICA", "ALTA", "MEDIA", "BAJA", "DESCONOCIDA"];
const names: Record<string, string> = { CRITICA: "Crítica", ALTA: "Alta", MEDIA: "Media", BAJA: "Baja", DESCONOCIDA: "Desconocida" };
const severityKeys = ["criticas", "altas", "medias", "bajas", "desconocidas"] as const;
const severityCodes = ["CRITICA", "ALTA", "MEDIA", "BAJA", "DESCONOCIDA"];

function dateLabel(value: string | null | undefined) {
  if (!value) return "Fecha no disponible";
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? "Fecha no disponible" : new Intl.DateTimeFormat("es-ES", { dateStyle: "medium", timeStyle: "short", timeZone: "Europe/Madrid" }).format(date) + " (Madrid)";
}

function normalizeSeverity(value: string) {
  const code = value.toUpperCase().replaceAll("Í", "I");
  return names[code] ? code : "DESCONOCIDA";
}

function number(value: number) { return new Intl.NumberFormat("es-ES").format(value); }

export default function Home() {
  const [view, setView] = useState<View>("Resumen");
  const [severity, setSeverity] = useState("Todas");
  const [typeFilter, setTypeFilter] = useState("");
  const [ipFilter, setIpFilter] = useState("");
  const [page, setPage] = useState(1);
  const [reportPage, setReportPage] = useState(1);
  const [reportId, setReportId] = useState("");
  const [hydrated, setHydrated] = useState(false);
  const [refresh, setRefresh] = useState(0);
  const [state, setState] = useState<StateResponse | null>(null);
  const [stateError, setStateError] = useState("");
  const [stateLoading, setStateLoading] = useState(true);
  const [threats, setThreats] = useState<PageResponse<Threat> | null>(null);
  const [threatError, setThreatError] = useState("");
  const [threatLoading, setThreatLoading] = useState(false);
  const [reports, setReports] = useState<PageResponse<Report> | null>(null);
  const [reportError, setReportError] = useState("");
  const [reportLoading, setReportLoading] = useState(false);
  const [detail, setDetail] = useState<ReportDetail | null>(null);
  const [detailError, setDetailError] = useState("");
  const [mobileNav, setMobileNav] = useState(false);
  const [analysis, setAnalysis] = useState<AnalysisCurrent["data"] | null>(null);
  const [analysisError, setAnalysisError] = useState("");
  const [analysisSubmitting, setAnalysisSubmitting] = useState(false);
  const analysisKey = useRef<string | null>(null);
  const mobileMenuRef = useRef<HTMLButtonElement>(null);
  const snapshotId = state?.meta.snapshot_id;

  useEffect(() => {
    let active = true;
    const params = new URLSearchParams(window.location.search);
    queueMicrotask(() => {
      if (!active) return;
      const requestedView = params.get("vista") as View;
      if (views.includes(requestedView)) setView(requestedView);
      const requestedSeverity = params.get("severidad") || "Todas";
      if (severities.includes(requestedSeverity)) setSeverity(requestedSeverity);
      setTypeFilter(params.get("tipo") || "");
      setIpFilter(params.get("ip") || "");
      const requestedPage = Number(params.get("pagina"));
      if (Number.isSafeInteger(requestedPage) && requestedPage > 0) setPage(requestedPage);
      const requestedReportPage = Number(params.get("pagina_reporte"));
      if (Number.isSafeInteger(requestedReportPage) && requestedReportPage > 0) setReportPage(requestedReportPage);
      const requestedReport = params.get("reporte") || "";
      if (/^[a-f0-9]{64}$/.test(requestedReport)) { setReportId(requestedReport); setView("Reportes"); }
      setHydrated(true);
    });
    return () => { active = false; };
  }, []);

  useEffect(() => {
    if (!hydrated) return;
    const params = new URLSearchParams();
    if (view !== "Resumen") params.set("vista", view);
    if (severity !== "Todas") params.set("severidad", severity);
    if (typeFilter) params.set("tipo", typeFilter);
    if (ipFilter) params.set("ip", ipFilter);
    if (page > 1) params.set("pagina", String(page));
    if (reportPage > 1) params.set("pagina_reporte", String(reportPage));
    if (reportId) params.set("reporte", reportId);
    const query = params.toString();
    window.history.replaceState(null, "", `${window.location.pathname}${query ? `?${query}` : ""}`);
  }, [hydrated, view, severity, typeFilter, ipFilter, page, reportPage, reportId]);

  const loadState = useCallback(async (signal?: AbortSignal) => {
    try {
      const next = await getApi<StateResponse>("estado", signal);
      if (!validState(next)) throw new Error("La respuesta de estado no coincide con el contrato v1.");
      if (!signal?.aborted) { setState(next); setStateError(""); }
    } catch (error) {
      if (!signal?.aborted) setStateError(error instanceof Error ? error.message : "No se pudo leer el estado.");
    } finally {
      if (!signal?.aborted) setStateLoading(false);
    }
  }, []);

  useEffect(() => {
    const controller = new AbortController();
    queueMicrotask(() => { if (!controller.signal.aborted) void loadState(controller.signal); });
    const timer = window.setInterval(() => { if (document.visibilityState === "visible") void loadState(controller.signal); }, 15000);
    const onVisible = () => { if (document.visibilityState === "visible") void loadState(controller.signal); };
    document.addEventListener("visibilitychange", onVisible);
    return () => { controller.abort(); window.clearInterval(timer); document.removeEventListener("visibilitychange", onVisible); };
  }, [loadState, refresh]);

  const loadAnalysis = useCallback(async (signal?: AbortSignal) => {
    try {
      const response = await getApi<AnalysisCurrent>("analisis/actual", signal);
      if (!signal?.aborted) { setAnalysis(response.data); setAnalysisError(""); }
    } catch {
      if (!signal?.aborted) setAnalysisError("No se pudo consultar el estado del ejecutor.");
    }
  }, []);

  useEffect(() => {
    const controller = new AbortController();
    queueMicrotask(() => { if (!controller.signal.aborted) void loadAnalysis(controller.signal); });
    const timer = window.setInterval(() => {
      if (document.visibilityState === "visible") void loadAnalysis(controller.signal);
    }, 5000);
    return () => { controller.abort(); window.clearInterval(timer); };
  }, [loadAnalysis]);

  async function startAnalysis() {
    if (analysisSubmitting || !analysis?.manual_enabled || analysis.executor !== "online" ||
        analysis.job?.status === "queued" || analysis.job?.status === "running") return;
    setAnalysisSubmitting(true);
    setAnalysisError("");
    analysisKey.current ??= crypto.randomUUID();
    try {
      const result = await requestAnalysis(analysisKey.current);
      setAnalysis((current) => current ? { ...current, job: result.job } : current);
      analysisKey.current = null;
      if (result.busy) setAnalysisError("Ya hay un análisis en curso. Se muestra el trabajo existente.");
      else void loadAnalysis();
    } catch (error) {
      setAnalysisError(`${error instanceof Error ? error.message : "No se pudo enviar la solicitud."} Consulta el estado antes de reintentar; se conservará la misma clave.`);
    } finally {
      setAnalysisSubmitting(false);
    }
  }

  useEffect(() => {
    if (!hydrated || view !== "Amenazas" || !snapshotId) return;
    const controller = new AbortController();
    const params = new URLSearchParams({ page: String(page), per_page: "25" });
    if (severity !== "Todas") params.set("severidad", severity);
    if (typeFilter) params.set("tipo", typeFilter);
    if (ipFilter) params.set("ip", ipFilter);
    queueMicrotask(() => { if (!controller.signal.aborted) { setThreatLoading(true); setThreatError(""); } });
    void getApi<PageResponse<Threat>>(`amenazas?${params}`, controller.signal)
      .then((result) => {
        if (result.meta.snapshot_id !== snapshotId) {
          setThreatError("La captura cambió durante la lectura. Actualiza para comparar los datos.");
          setThreats(null);
          return;
        }
        const last = Math.max(1, Math.ceil(result.meta.total / 25));
        if (page > last) { setPage(last); return; }
        setThreats(result);
      })
      .catch((error) => { if (!controller.signal.aborted) setThreatError(error instanceof Error ? error.message : "No se pudieron leer las amenazas."); })
      .finally(() => { if (!controller.signal.aborted) setThreatLoading(false); });
    return () => controller.abort();
  }, [hydrated, view, page, severity, typeFilter, ipFilter, snapshotId]);

  useEffect(() => {
    if (!hydrated || view !== "Reportes" || !snapshotId) return;
    const controller = new AbortController();
    queueMicrotask(() => { if (!controller.signal.aborted) { setReportLoading(true); setReportError(""); } });
    void getApi<PageResponse<Report>>(`reportes?page=${reportPage}&per_page=20`, controller.signal)
      .then((result) => {
        const last = Math.max(1, Math.ceil(result.meta.total / 20));
        if (reportPage > last) { setReportPage(last); return; }
        setReports(result);
      })
      .catch((error) => { if (!controller.signal.aborted) setReportError(error instanceof Error ? error.message : "No se pudieron leer los reportes."); })
      .finally(() => { if (!controller.signal.aborted) setReportLoading(false); });
    return () => controller.abort();
  }, [hydrated, view, reportPage, refresh, snapshotId]);

  useEffect(() => {
    if (!hydrated || view !== "Reportes" || !reportId) return;
    const controller = new AbortController();
    queueMicrotask(() => { if (!controller.signal.aborted) setDetailError(""); });
    void getApi<ReportDetail>(`reportes/${reportId}`, controller.signal)
      .then(setDetail)
      .catch((error) => { if (!controller.signal.aborted) setDetailError(error instanceof Error ? error.message : "No se pudo abrir el reporte."); });
    return () => controller.abort();
  }, [hydrated, view, reportId, refresh]);

  function navigate(next: View) {
    setView(next);
    setMobileNav(false);
    if (window.matchMedia("(max-width: 650px)").matches) {
      requestAnimationFrame(() => mobileMenuRef.current?.focus());
    }
    if (next !== "Reportes") { setReportId(""); setDetail(null); }
  }
  function requestRefresh() { setRefresh((value) => value + 1); }
  const stats = state?.data.stats;
  const periods = state?.data.timeline.periods ?? [];
  const maxCount = Math.max(1, ...periods.map((item) => item.count));
  const fresh = !stateError && state?.meta.health === "ok";
  const connectionLabel = stateError ? "Sin conexión con Flask" : !state ? "Conectando a Flask" : state.meta.health === "ok" ? "Fuentes disponibles" : "Fuentes incompletas";

  return <main className="app-shell">
    <aside className={`sidebar ${mobileNav ? "sidebar-open" : ""}`}>
      <Link className="brand" href="/" aria-label="web-defense-ai V2, inicio"><span className="brand-mark" aria-hidden="true">◇</span><span className="brand-name">web<span>defense</span><small>AI <b>V2</b></small></span></Link>
      <div className="workspace-switch"><div className="workspace-avatar">WD</div><div className="workspace-copy"><span>Workspace</span><strong>Laboratorio local</strong></div></div>
      <div className="nav-label">PLATAFORMA</div>
      <nav id="primary-nav" className="primary-nav" aria-label="Navegación principal">{views.map((item) => <button key={item} className={`nav-link ${view === item ? "nav-active" : ""}`} aria-current={view === item ? "page" : undefined} onClick={() => navigate(item)}><span className="nav-glyph" aria-hidden="true">{item === "Resumen" ? "▦" : item === "Amenazas" ? "◇" : item === "Reportes" ? "▤" : "▥"}</span><span>{item}</span>{item === "Amenazas" && <span className="nav-count">{state?.data.threats_total ?? "—"}</span>}</button>)}</nav>
      <div className="sidebar-bottom"><div className="plan-card"><div className="plan-head"><span className="environment-dot" /> LECTURA LOCAL</div><strong>{connectionLabel}</strong><p>Datos de archivos observados por la API. No indica que el análisis esté activo.</p><div className="plan-foot"><span>Solo lectura</span><span>API v1</span></div></div></div>
    </aside>

    <section className="main-column">
      <header className="topbar"><button ref={mobileMenuRef} className="mobile-menu icon-button" aria-label={mobileNav ? "Cerrar menú" : "Abrir menú"} aria-expanded={mobileNav} aria-controls="primary-nav" onClick={() => setMobileNav(!mobileNav)}>{mobileNav ? "×" : "☰"}</button><div className="breadcrumbs"><span>Consola</span><span>›</span><strong>{view}</strong></div><div className="topbar-right"><span className={`environment ${state && !fresh ? "environment-warning" : ""}`}><span className="environment-dot" /> {state ? fresh ? "LECTURA LOCAL" : "REVISAR FUENTES" : "CONECTANDO"}</span></div></header>
      <div className="content-wrap">
        <div className={`source-banner ${stateError ? "source-error" : ""}`} role="status"><strong>{stateError ? "Lectura interrumpida" : state?.meta.health === "ok" ? "Lectura conectada" : "Estado de fuentes"}</strong><span>{stateError ? `${stateError} ${state ? "Se conserva la última captura visible." : "Inicia Flask en 127.0.0.1:5000."}` : state ? `Captura ${state.meta.snapshot_id.slice(0, 12)} · ${state.meta.health === "ok" ? "archivos disponibles" : "faltan fuentes o están cambiando"}` : "Cargando datos del backend…"}</span></div>
        <section className="page-heading"><div><div className="eyebrow"><span className="eyebrow-line" /> CENTRO DE OPERACIONES</div><h1>{view === "Resumen" ? "Resumen de seguridad" : view}</h1><p>Lectura de archivos locales. Las coincidencias del log no demuestran ataques exitosos.</p></div><div className="heading-actions"><span className="updated-label">{state ? dateLabel(state.meta.captured_at) : "Sin captura"}</span><button className="button-secondary" onClick={requestRefresh}>↻ Actualizar</button></div></section>

        {view === "Resumen" && <section className="panel analysis-panel" aria-label="Coordinación de análisis">
          <div><div className="panel-kicker">EJECUTOR LOCAL</div><h2>Análisis coordinado</h2>
            <p>{analysis?.executor === "online" ? "Ejecutor activo" : "Ejecutor no disponible"} · {analysis?.manual_enabled ? "solicitudes manuales habilitadas" : "solicitudes manuales desactivadas"}</p>
            {analysis?.job && <p role="status">Último trabajo {analysis.job.id.slice(0, 12)} · {analysis.job.kind === "manual" ? "manual" : "periódico"} · {analysis.job.status} · {analysis.job.phase}{analysis.job.error_code ? ` · ${analysis.job.error_code}` : ""}</p>}
            {analysis?.job && Object.keys(analysis.job.deliveries ?? {}).length > 0 && <p>Entregas: {Object.entries(analysis.job.deliveries).map(([destination, status]) => `${destination}: ${status}`).join(" · ")}</p>}
            {analysisError && <p className="error-copy" role="alert">{analysisError}</p>}
          </div>
          <button className="button-secondary" disabled={!analysis?.manual_enabled || analysis.executor !== "online" || analysisSubmitting || analysis.job?.status === "queued" || analysis.job?.status === "running"} onClick={() => void startAnalysis()}>{analysisSubmitting ? "Solicitando…" : "Iniciar análisis"}</button>
        </section>}

        {stateLoading && !state && <div className="panel state-panel" role="status">Cargando la primera captura…</div>}
        {!stateLoading && !state && <div className="panel state-panel">No hay datos disponibles. Comprueba que el dashboard Flask esté iniciado y vuelve a actualizar.</div>}

        {view === "Resumen" && state && <>
          <section className="metric-grid" aria-label="Indicadores del reporte actual">
            <Metric label="Amenazas del reporte" value={number(stats?.total ?? 0)} note="No incluye históricos" tone="cyan" />
            <Metric label="Críticas y altas" value={number((stats?.criticas ?? 0) + (stats?.altas ?? 0))} note="Clasificación del reporte" tone="amber" />
            <Metric label="IP observadas en reporte" value={number(stats?.ips ?? 0)} note="No equivale a atacantes" tone="violet" />
            <Metric label="Coincidencias en log" value={number(periods.reduce((sum, item) => sum + item.count, 0))} note="Patrones; pueden solaparse" tone="green" />
          </section>
          <section className="overview-grid">
            <article className="panel trend-panel"><div className="panel-header"><div><div className="panel-kicker">ACCESS.LOG</div><h2>Coincidencias de patrones</h2><p>Periodo disponible en el log; no son incidentes confirmados</p></div></div><Timeline periods={periods} maxCount={maxCount} /></article>
            <article className="panel severity-panel"><div className="panel-header"><div><div className="panel-kicker">REPORTE ACTUAL</div><h2>Severidades</h2><p>{number(stats?.total ?? 0)} amenazas clasificadas</p></div></div><div className="live-severity-list">{severityKeys.map((key, index) => <div key={key} className="live-severity-row"><span>{names[severityCodes[index]]}</span><div className="severity-track"><i style={{ width: `${stats?.total ? Math.round((stats[key] / stats.total) * 100) : 0}%` }} /></div><strong>{number(stats?.[key] ?? 0)}</strong></div>)}</div></article>
          </section>
          <section className="panel incidents-panel"><div className="panel-header incidents-heading"><div><div className="panel-kicker">REPORTE ACTUAL</div><h2>Amenazas recientes</h2><p>{state.data.threats_truncated ? `Se muestran 10 de ${number(state.data.threats_total)}` : `${number(state.data.threats_total)} en la captura`}</p></div></div><ThreatTable items={state.data.threats} /><div className="table-footer"><span>Captura {state.meta.snapshot_id.slice(0, 12)}</span><button onClick={() => navigate("Amenazas")}>Ver lista completa →</button></div></section>
          <section className="summary-bottom"><article className="panel"><div className="panel-header"><div><div className="panel-kicker">LECTURA RECIENTE</div><h2>Terminal</h2></div></div><LogLines lines={state.data.recent_log} /></article><article className="panel"><div className="panel-header"><div><div className="panel-kicker">ARCHIVO</div><h2>Reportes recientes</h2></div></div>{state.data.recent_reports.length ? <ul className="simple-list">{state.data.recent_reports.map((item, index) => <li key={`${item.nombre}-${index}`}><span>{item.nombre}</span><small>{item.amenazas} amenazas · fecha del evento no verificada</small></li>)}</ul> : <p className="empty-copy">No hay reportes históricos disponibles.</p>}<button className="plain-link" onClick={() => navigate("Reportes")}>Explorar todos los reportes →</button></article></section>
        </>}

        {view === "Amenazas" && <section className="panel list-panel"><div className="panel-header"><div><div className="panel-kicker">REPORTE ACTUAL</div><h2>Amenazas</h2><p>Filtros y página guardados en la dirección del navegador</p></div></div><div className="filter-row"><label>Severidad<select value={severity} onChange={(event) => { setSeverity(event.target.value); setPage(1); }}><option value="Todas">Todas</option>{severityCodes.map((code) => <option key={code} value={code}>{names[code]}</option>)}</select></label><label>Tipo<input value={typeFilter} onChange={(event) => { setTypeFilter(event.target.value); setPage(1); }} placeholder="Buscar tipo" /></label><label>IP exacta<input value={ipFilter} onChange={(event) => { setIpFilter(event.target.value); setPage(1); }} placeholder="IP observada" /></label></div>{threatLoading && <p className="status-copy" role="status">Consultando amenazas…</p>}{threatError && <p className="status-copy error-copy" role="alert">{threatError}</p>}{!threatLoading && !threatError && threats && <><p className="status-copy">{number(threats.meta.total)} coincidencias · captura {threats.meta.snapshot_id?.slice(0, 12)} · página {threats.meta.page}</p><ThreatTable items={threats.data} /><Pager page={page} total={threats.meta.total} size={25} change={setPage} /></>}</section>}

        {view === "Reportes" && <section className="reports-layout"><article className="panel list-panel"><div className="panel-header"><div><div className="panel-kicker">ACTUAL E HISTÓRICOS</div><h2>Reportes</h2><p>Archivos disponibles; fecha de modificación, no fecha del evento</p></div></div>{reportLoading && <p className="status-copy" role="status">Cargando catálogo…</p>}{reportError && <p className="status-copy error-copy" role="alert">{reportError}</p>}{!reportLoading && !reportError && reports && <>{reports.data.length ? <ul className="report-list">{reports.data.map((item) => <li key={item.id}><button className={reportId === item.id ? "selected-report" : ""} onClick={() => { setDetail(null); setReportId(item.id); }}><strong>{item.current ? "Reporte actual" : item.filename}</strong><small>{dateLabel(item.modified_at)} · {number(item.size_bytes)} bytes</small></button></li>)}</ul> : <p className="empty-copy">No hay reportes disponibles.</p>}<Pager page={reportPage} total={reports.meta.total} size={20} change={setReportPage} /></>}</article><article className="panel report-detail"><div className="panel-header"><div><div className="panel-kicker">LECTURA SEGURA</div><h2>{detail?.data.report.filename ?? "Selecciona un reporte"}</h2></div></div>{detailError && <p className="status-copy error-copy" role="alert">{detailError} Actualiza el catálogo si el archivo cambió.</p>}{reportId && !detail && !detailError && <p className="status-copy" role="status">Abriendo reporte…</p>}{detail && <><p className="status-copy">Modificado: {dateLabel(detail.data.report.modified_at)}</p><pre className="report-markdown">{detail.data.markdown}</pre></>}{!reportId && <p className="empty-copy">Elige un reporte para leer su contenido. El Markdown se muestra como texto, sin ejecutar HTML.</p>}</article></section>}

        {view === "Actividad" && <section className="panel list-panel"><div className="panel-header"><div><div className="panel-kicker">ACCESS.LOG</div><h2>Actividad reciente</h2><p>Ventana limitada que entrega la API; no es un registro histórico completo</p></div></div><LogLines lines={state?.data.recent_log ?? []} /><p className="status-copy">Origen: {state?.meta.sources.log?.status ?? "sin lectura"} · última modificación {dateLabel(state?.meta.sources.log?.modified_at)}</p></section>}

        <footer className="page-footer"><span>web-defense-ai V2 · Consola local</span><span>API v1 · Flask disponible como retorno</span></footer>
      </div>
    </section>
  </main>;
}

function Metric({ label, value, note, tone }: { label: string; value: string; note: string; tone: string }) {
  return <article className="metric-card"><div className="metric-top"><span className={`metric-icon ${tone}`} aria-hidden="true">◇</span><span className="metric-label">{label}</span></div><div className="metric-bottom"><div><div className="metric-value">{value}</div><div className="metric-change">{note}</div></div></div></article>;
}

function Timeline({ periods, maxCount }: { periods: StateResponse["data"]["timeline"]["periods"]; maxCount: number }) {
  if (!periods.length) return <p className="empty-copy">No hay periodos de log disponibles.</p>;
  const categories = [
    ["sqli", "SQLi"], ["xss", "XSS"], ["path", "Rutas"],
    ["brute", "Fuerza bruta"], ["cmd", "Comandos"],
  ];
  return <><div className="live-chart" role="img" aria-label={`Coincidencias por periodo: ${periods.map((item) => `${item.period}: ${item.count}`).join(", ")}`}><div className="live-bars">{periods.map((item, index) => <div className="live-bar-column" key={`${item.period}-${index}`} title={`${item.period}: ${item.count}`}><span>{item.count}</span><i style={{ height: `${Math.max(2, (item.count / maxCount) * 100)}%` }} /></div>)}</div><div className="live-chart-labels"><span>{periods[0]?.period}</span><span>{periods[periods.length - 1]?.period}</span></div></div><div className="pattern-summary">{categories.map(([key, label]) => <span key={key}>{label}: <strong>{periods.reduce((sum, item) => sum + (item.matches[key] ?? 0), 0)}</strong></span>)}</div></>;
}

function ThreatTable({ items }: { items: Threat[] }) {
  return <div className="table-scroll"><table><thead><tr><th>TIPO / ID</th><th>IP OBSERVADA</th><th>SEVERIDAD</th><th>ESTADO</th><th>FECHA DEL EVENTO</th></tr></thead><tbody>{items.map((item) => <tr key={item.id}><td><div className="event-cell"><span className="event-icon blue" aria-hidden="true">◇</span><span><strong>{item.type || "Tipo no disponible"}</strong><small>{item.number} · {item.id.slice(0, 12)}</small></span></div></td><td>{item.source_ip && item.source_ip !== "-" ? item.source_ip : "Desconocida"}</td><td><span className={`severity-badge severity-${normalizeSeverity(item.severity).toLowerCase()}`}>{names[normalizeSeverity(item.severity)]}</span></td><td>{item.status || "No disponible"}</td><td>{item.event_time ? dateLabel(item.event_time) : "No disponible"}</td></tr>)}</tbody></table>{!items.length && <p className="empty-copy">No hay amenazas para esta selección.</p>}</div>;
}

function LogLines({ lines }: { lines: string[] }) {
  return <pre className="log-lines">{lines.length ? lines.join("\n") : "No hay líneas de log disponibles."}</pre>;
}

function Pager({ page, total, size, change }: { page: number; total: number; size: number; change: (value: number) => void }) {
  const last = Math.max(1, Math.ceil(total / size));
  return <div className="pager"><button disabled={page <= 1} onClick={() => change(page - 1)}>Anterior</button><span>Página {page} de {last}</span><button disabled={page >= last} onClick={() => change(page + 1)}>Siguiente</button></div>;
}
