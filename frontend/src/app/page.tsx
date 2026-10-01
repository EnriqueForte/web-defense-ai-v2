"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import Link from "next/link";
import { Activity, FileText, LayoutDashboard, Menu, Network, RefreshCw, Shield, ShieldAlert, TriangleAlert, X } from "lucide-react";
import { ThreatTable } from "@/components/threat-table";
import { MetricCard } from "@/components/metric-card";
import { SeverityChart, TimelineChart } from "@/components/security-charts";
import { getApi, requestAnalysis, validState, type AnalysisCurrent, type ObservedEvent, type PageResponse, type Report, type ReportDetail, type StateResponse, type Threat } from "@/lib/api";

type View = "Resumen" | "Amenazas" | "Reportes" | "Actividad";
const views: View[] = ["Resumen", "Amenazas", "Reportes", "Actividad"];
const viewDescriptions: Record<View, string> = {
  Resumen: "Visión general del reporte actual y de los patrones observados en el log.",
  Amenazas: "Consulta eventos observados en el log y amenazas clasificadas en el último informe.",
  Reportes: "Consulta los informes generados; su fecha corresponde al archivo, no a cada evento.",
  Actividad: "Revisa las últimas líneas disponibles del registro de acceso.",
};
const navigationIcons = { Resumen: LayoutDashboard, Amenazas: ShieldAlert, Reportes: FileText, Actividad: Activity };
const severities = ["Todas", "CRITICA", "ALTA", "MEDIA", "BAJA", "DESCONOCIDA"];
const names: Record<string, string> = { CRITICA: "Crítica", ALTA: "Alta", MEDIA: "Media", BAJA: "Baja", DESCONOCIDA: "Desconocida" };
const severityCodes = ["CRITICA", "ALTA", "MEDIA", "BAJA", "DESCONOCIDA"];

function dateLabel(value: string | null | undefined) {
  if (!value) return "Fecha no disponible";
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? "Fecha no disponible" : new Intl.DateTimeFormat("es-ES", { dateStyle: "medium", timeStyle: "short", timeZone: "Europe/Madrid" }).format(date) + " (Madrid)";
}

function number(value: number) { return new Intl.NumberFormat("es-ES").format(value); }

function ObservedEvents({ items }: { items: ObservedEvent[] }) {
  return <section className="panel list-panel"><div className="panel-header"><div><div className="panel-kicker">ACCESS.LOG · EUROPE/MADRID</div><h2>Eventos observados recientemente</h2><p>Coincidencias del registro; tras cada tanda en DVWA, sincroniza el log. La consola vuelve a leerlo cada 15 segundos. No confirma que un ataque tuviera éxito.</p></div></div>
    {!items.length ? <p className="empty-copy">No hay eventos recientes que coincidan con los patrones vigilados.</p> : <div className="table-scroll event-table-wrap" tabIndex={0} role="region" aria-label="Eventos observados; desplazamiento horizontal disponible"><table><thead><tr><th>FECHA LOCAL</th><th>OBSERVACIÓN</th><th>IP OBSERVADA</th><th>SOLICITUD</th><th>HTTP</th></tr></thead><tbody>{items.map((item) => <tr key={item.id}><td>{dateLabel(item.observed_at)}</td><td>{item.category}</td><td>{item.source_ip ?? "Desconocida"}</td><td><code>{item.method} {item.path}</code></td><td>{item.http_status}</td></tr>)}</tbody></table></div>}
  </section>;
}

function GithubMark() {
  return <svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 .9a11.1 11.1 0 0 0-3.51 21.63c.55.1.76-.24.76-.53v-2.06c-3.1.67-3.76-1.32-3.76-1.32-.5-1.29-1.24-1.64-1.24-1.64-1.02-.7.08-.69.08-.69 1.13.08 1.72 1.16 1.72 1.16 1 .1.76 2.03 3.14 1.44.1-.72.4-1.22.69-1.5-2.48-.28-5.09-1.24-5.09-5.52 0-1.22.44-2.22 1.16-3-.12-.28-.5-1.42.11-2.96 0 0 .95-.3 3.05 1.15a10.6 10.6 0 0 1 5.56 0c2.1-1.45 3.05-1.15 3.05-1.15.61 1.54.23 2.68.11 2.96.72.78 1.16 1.78 1.16 3 0 4.29-2.61 5.23-5.1 5.51.4.35.75 1.03.75 2.08V22c0 .29.2.63.77.52A11.1 11.1 0 0 0 12 .9Z" /></svg>;
}

function LinkedinMark() {
  return <svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M20.45 20.45h-3.55v-5.57c0-1.33-.03-3.04-1.85-3.04-1.85 0-2.14 1.45-2.14 2.94v5.67H9.36V9h3.41v1.56h.05c.48-.9 1.64-1.85 3.37-1.85 3.6 0 4.27 2.37 4.27 5.46v6.28ZM5.34 7.43a2.06 2.06 0 1 1 0-4.12 2.06 2.06 0 0 1 0 4.12ZM7.12 20.45H3.56V9h3.56v11.45ZM22.23 0H1.77C.79 0 0 .77 0 1.72v20.56C0 23.23.79 24 1.77 24h20.45c.98 0 1.78-.77 1.78-1.72V1.72C24 .77 23.2 0 22.23 0Z" /></svg>;
}

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
  const reportsRef = useRef<PageResponse<Report> | null>(null);
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
  const sidebarRef = useRef<HTMLElement>(null);
  const headingRef = useRef<HTMLHeadingElement>(null);
  const snapshotId = state?.meta.snapshot_id;

  useEffect(() => { document.title = `${view} · web-defense-ai V2`; }, [view]);

  useEffect(() => {
    if (!mobileNav) return;
    const sidebar = sidebarRef.current;
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    const focusFrame = requestAnimationFrame(() => sidebar?.querySelector<HTMLButtonElement>(".drawer-close")?.focus());
    const close = () => { setMobileNav(false); requestAnimationFrame(() => mobileMenuRef.current?.focus()); };
    const onKey = (event: KeyboardEvent) => {
      if (event.key === "Escape") { event.preventDefault(); close(); }
      if (event.key !== "Tab") return;
      const items = sidebar?.querySelectorAll<HTMLElement>("a[href], button:not([disabled])");
      if (!items?.length) return;
      const first = items[0], last = items[items.length - 1];
      if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
      else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
    };
    const media = window.matchMedia("(max-width: 650px)");
    const onResize = () => { if (!media.matches) { setMobileNav(false); headingRef.current?.focus(); } };
    document.addEventListener("keydown", onKey);
    media.addEventListener("change", onResize);
    return () => { cancelAnimationFrame(focusFrame); document.body.style.overflow = previousOverflow; document.removeEventListener("keydown", onKey); media.removeEventListener("change", onResize); };
  }, [mobileNav]);

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
        const wasCurrentReportSelected = reportsRef.current?.data.some((item) => item.id === reportId && item.current) ?? false;
        const newestCurrent = result.data.find((item) => item.current);
        reportsRef.current = result;
        if (wasCurrentReportSelected && newestCurrent && newestCurrent.id !== reportId) {
          setReportId(newestCurrent.id);
          setDetail(null);
        }
        const last = Math.max(1, Math.ceil(result.meta.total / 20));
        if (reportPage > last) { setReportPage(last); return; }
        setReports(result);
      })
      .catch((error) => { if (!controller.signal.aborted) setReportError(error instanceof Error ? error.message : "No se pudieron leer los reportes."); })
      .finally(() => { if (!controller.signal.aborted) setReportLoading(false); });
    return () => controller.abort();
  }, [hydrated, view, reportPage, refresh, snapshotId, reportId]);

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
    requestAnimationFrame(() => headingRef.current?.focus());
    if (next !== "Reportes") { setReportId(""); setDetail(null); }
  }
  function requestRefresh() { setRefresh((value) => value + 1); }
  const stats = state?.data.stats;
  const reportAvailable = state?.meta.sources.report?.status === "available";
  const logAvailable = state?.meta.sources.log?.status === "available";
  const periods = state?.data.timeline.periods ?? [];
  const fresh = !stateError && state?.meta.health === "ok";
  const connectionLabel = stateError ? "Sin conexión con Flask" : !state ? "Conectando a Flask" : state.meta.health === "ok" ? "Fuentes disponibles" : "Fuentes incompletas";

  return <div className="app-shell">
    <a className="skip-link" href="#main-content" inert={mobileNav}>Saltar al contenido</a>
    {mobileNav && <div className="nav-backdrop" aria-hidden="true" onClick={() => { setMobileNav(false); requestAnimationFrame(() => mobileMenuRef.current?.focus()); }} />}
    <aside ref={sidebarRef} id="navigation-panel" aria-label="Menú de la consola" className={`sidebar ${mobileNav ? "sidebar-open" : ""}`}>
      <button className="drawer-close button-secondary" onClick={() => { setMobileNav(false); requestAnimationFrame(() => mobileMenuRef.current?.focus()); }}>Cerrar menú <X size={18} aria-hidden="true" /></button>
      <Link className="brand" href="/" aria-label="web-defense-ai V2, volver al Resumen" onClick={() => { navigate("Resumen"); setSeverity("Todas"); setTypeFilter(""); setIpFilter(""); setPage(1); setReportPage(1); setReportId(""); setDetail(null); }}><span className="brand-mark" aria-hidden="true"><Shield size={22} /></span><span className="brand-name">web<span>defense</span><small>AI <b>V2</b></small></span></Link>
      <div className="workspace-switch"><div className="workspace-avatar" aria-hidden="true">WD</div><div className="workspace-copy"><span>ENTORNO</span><strong>Laboratorio local</strong></div></div>
      <div className="nav-label">PLATAFORMA</div>
      <nav id="primary-nav" className="primary-nav" aria-label="Navegación principal">{views.map((item) => { const Icon = navigationIcons[item]; return <button key={item} className={`nav-link ${view === item ? "nav-active" : ""}`} aria-current={view === item ? "page" : undefined} onClick={() => navigate(item)}><span className="nav-glyph" aria-hidden="true"><Icon size={19} strokeWidth={1.75} /></span><span>{item}</span>{item === "Amenazas" && <span className="nav-count">{state?.data.threats_total ?? "—"}</span>}</button>; })}</nav>
      <div className="sidebar-bottom"><div className="plan-card"><div className="plan-head"><span className="environment-dot" /> LECTURA LOCAL</div><strong>{connectionLabel}</strong><p>Datos de archivos observados por la API. No indica que el análisis esté activo.</p><div className="plan-foot"><span>Solo lectura</span><span>API v1</span></div></div></div>
    </aside>

    <div className="main-column" inert={mobileNav}>
      <header className="topbar"><button ref={mobileMenuRef} className="mobile-menu icon-button" aria-label={mobileNav ? "Cerrar menú" : "Abrir menú"} aria-expanded={mobileNav} aria-controls="navigation-panel" onClick={() => setMobileNav(!mobileNav)}>{mobileNav ? <X size={20} aria-hidden="true" /> : <Menu size={20} aria-hidden="true" />}</button><nav className="breadcrumbs" aria-label="Ubicación"><span>Consola SOC</span><span aria-hidden="true">/</span><strong aria-current="page">{view}</strong></nav><div className="topbar-right"><div className="author-profile"><div className="author-copy"><span className="author-name">Enrique Forte</span><span className="author-handle">@T3r0S3c</span></div><span className="author-role">Developer &amp; Maintainer</span><nav className="author-social" aria-label="Perfiles de Enrique Forte"><a href="https://github.com/EnriqueForte" target="_blank" rel="noopener noreferrer" aria-label="GitHub de Enrique Forte (abre en una pestaña nueva)" title="GitHub"><GithubMark /></a><a href="https://linkedin.com/in/enriqueforte" target="_blank" rel="noopener noreferrer" aria-label="LinkedIn de Enrique Forte (abre en una pestaña nueva)" title="LinkedIn"><LinkedinMark /></a></nav></div><span className={`environment ${stateError || (state && !fresh) ? "environment-warning" : ""}`}><span className="environment-dot" /> {stateError ? "SIN CONEXIÓN" : state ? fresh ? "LECTURA LOCAL" : "REVISAR FUENTES" : "CONECTANDO"}</span></div></header>
      <main id="main-content" className="content-wrap" tabIndex={-1}>
        <div className={`source-banner ${stateError ? "source-error" : ""}`} role={stateError ? "alert" : "status"}><strong>{stateError ? "Lectura interrumpida" : state?.meta.health === "ok" ? "Lectura conectada" : "Estado de fuentes"}</strong><span>{stateError ? `${stateError} ${state ? "Se conserva la última captura visible." : "Inicia Flask en 127.0.0.1:5000."}` : state ? `Captura ${state.meta.snapshot_id.slice(0, 12)} · ${state.meta.health === "ok" ? "archivos disponibles" : "faltan fuentes o están cambiando"}` : "Cargando datos del backend…"}</span></div>
        <section className="page-heading"><div><div className="eyebrow"><span className="eyebrow-line" /> CENTRO DE OPERACIONES</div><h1 ref={headingRef} tabIndex={-1}>{view === "Resumen" ? "Resumen de seguridad" : view}</h1><p>{viewDescriptions[view]}</p></div><div className="heading-actions"><span className="updated-label"><span>Última captura</span>{state ? dateLabel(state.meta.captured_at) : "Sin captura"}</span><button className="button-secondary" onClick={requestRefresh}><RefreshCw size={15} aria-hidden="true" /> Actualizar</button></div></section>

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
            <MetricCard label="Amenazas del reporte" value={reportAvailable ? number(stats?.total ?? 0) : "—"} note={reportAvailable ? "Amenazas clasificadas; no incluye históricos." : "Reporte no disponible en esta captura."} source="Reporte actual" icon={ShieldAlert} tone="cyan" />
            <MetricCard label="Críticas y altas" value={reportAvailable ? number((stats?.criticas ?? 0) + (stats?.altas ?? 0)) : "—"} note={reportAvailable ? "Suma de severidades crítica y alta." : "Reporte no disponible en esta captura."} source="Reporte actual" icon={TriangleAlert} tone="amber" />
            <MetricCard label="IP observadas en reporte" value={reportAvailable ? number(stats?.ips ?? 0) : "—"} note={reportAvailable ? "IP observadas; no equivale a atacantes." : "Reporte no disponible en esta captura."} source="Reporte actual" icon={Network} tone="violet" />
            <MetricCard label="Coincidencias en log" value={logAvailable ? number(periods.reduce((sum, item) => sum + item.count, 0)) : "—"} note={logAvailable ? "Coincidencias de patrones; pueden solaparse." : "Registro de acceso no disponible en esta captura."} source="Registro de acceso" icon={Activity} tone="green" />
          </section>
          <section className="overview-grid">
            <article className="panel trend-panel"><div className="panel-header"><div><div className="panel-kicker">ACCESS.LOG</div><h2>Coincidencias de patrones</h2><p>Periodo disponible en el log; no son incidentes confirmados</p></div></div><TimelineChart periods={periods} available={logAvailable} /></article>
            <article className="panel severity-panel"><div className="panel-header"><div><div className="panel-kicker">REPORTE ACTUAL</div><h2>Severidades</h2><p>{reportAvailable ? `${number(stats?.total ?? 0)} amenazas clasificadas` : "Reporte no disponible"}</p></div></div><SeverityChart stats={state.data.stats} available={reportAvailable} /></article>
          </section>
          <section className="panel incidents-panel"><div className="panel-header incidents-heading"><div><div className="panel-kicker">REPORTE ACTUAL</div><h2>Amenazas recientes</h2><p>{reportAvailable ? state.data.threats_truncated ? `Se muestran 10 de ${number(state.data.threats_total)}` : `${number(state.data.threats_total)} en la captura` : "Reporte no disponible"}</p></div></div><ThreatTable items={state.data.threats} dateLabel={dateLabel} sourceAvailable={reportAvailable} /><div className="table-footer"><span>Captura {state.meta.snapshot_id.slice(0, 12)}</span><button onClick={() => navigate("Amenazas")}>Ver lista completa →</button></div></section>
          <section className="summary-bottom"><article className="panel"><div className="panel-header"><div><div className="panel-kicker">LECTURA RECIENTE</div><h2>Terminal</h2></div></div><LogLines lines={state.data.recent_log} /></article><article className="panel"><div className="panel-header"><div><div className="panel-kicker">ARCHIVO</div><h2>Reportes recientes</h2></div></div>{state.data.recent_reports.length ? <ul className="simple-list">{state.data.recent_reports.map((item, index) => <li key={`${item.nombre}-${index}`}><span>{item.nombre}</span><small>{item.amenazas} amenazas · fecha del evento no verificada</small></li>)}</ul> : <p className="empty-copy">No hay reportes históricos disponibles.</p>}<button className="plain-link" onClick={() => navigate("Reportes")}>Explorar todos los reportes →</button></article></section>
        </>}

        {view === "Amenazas" && <><ObservedEvents items={state?.data.recent_events ?? []} /><section className="panel list-panel"><div className="panel-header"><div><div className="panel-kicker">CLASIFICACIÓN DEL ÚLTIMO INFORME</div><h2>Amenazas clasificadas</h2><p>Esta tabla cambia cuando se genera un informe nuevo; los eventos observados aparecen arriba.</p></div></div><div className="filter-row"><label>Severidad<select value={severity} onChange={(event) => { setSeverity(event.target.value); setPage(1); }}><option value="Todas">Todas</option>{severityCodes.map((code) => <option key={code} value={code}>{names[code]}</option>)}</select></label><label>Tipo<input value={typeFilter} onChange={(event) => { setTypeFilter(event.target.value); setPage(1); }} placeholder="Buscar tipo" /></label><label>IP exacta<input value={ipFilter} onChange={(event) => { setIpFilter(event.target.value); setPage(1); }} placeholder="IP observada" /></label><button className="button-secondary filter-reset" disabled={severity === "Todas" && !typeFilter && !ipFilter} onClick={() => { setSeverity("Todas"); setTypeFilter(""); setIpFilter(""); setPage(1); }}>Limpiar filtros</button></div><p className="filter-context">{severity === "Todas" && !typeFilter && !ipFilter ? "Sin filtros activos" : `Filtros activos: ${[severity !== "Todas" ? names[severity] : "", typeFilter ? `Tipo: ${typeFilter}` : "", ipFilter ? `IP: ${ipFilter}` : ""].filter(Boolean).join(" · ")}`}</p>{threatLoading && <p className="status-copy" role="status">Consultando amenazas…</p>}{threatError && <p className="status-copy error-copy" role="alert">{threatError}</p>}{!threatLoading && !threatError && threats && <><p className="status-copy" role="status">{number(threats.meta.total)} coincidencias · captura {threats.meta.snapshot_id?.slice(0, 12)} · página {threats.meta.page}</p><ThreatTable items={threats.data} dateLabel={dateLabel} sourceAvailable={reportAvailable} /><Pager page={page} total={threats.meta.total} size={25} change={setPage} /></>}</section></>}

        {view === "Reportes" && <><section className="reports-layout"><article className="panel list-panel"><div className="panel-header"><div><div className="panel-kicker">ACTUAL E HISTÓRICOS</div><h2>Reportes</h2><p>Archivos disponibles; fecha local de modificación, no fecha de cada evento</p></div></div>{reportLoading && <p className="status-copy" role="status">Cargando catálogo…</p>}{reportError && <p className="status-copy error-copy" role="alert">{reportError}</p>}{!reportLoading && !reportError && reports && <>{reports.data.length ? <ul className="report-list">{reports.data.map((item) => <li key={item.id}><button aria-pressed={reportId === item.id} className={reportId === item.id ? "selected-report" : ""} onClick={() => { setDetail(null); setReportId(item.id); }}><strong>{item.current ? "Reporte actual" : item.filename}</strong><small>{dateLabel(item.modified_at)} · {number(item.size_bytes)} bytes</small></button></li>)}</ul> : <p className="empty-copy">No hay reportes disponibles.</p>}<Pager page={reportPage} total={reports.meta.total} size={20} change={setReportPage} /></>}</article><article className="panel report-detail"><div className="panel-header"><div><div className="panel-kicker">LECTURA SEGURA</div><h2>{detail?.data.report.filename ?? "Selecciona un reporte"}</h2></div></div>{detailError && <p className="status-copy error-copy" role="alert">{detailError} Actualiza el catálogo si el archivo cambió.</p>}{reportId && !detail && !detailError && <p className="status-copy" role="status">Abriendo reporte…</p>}{detail && <><p className="status-copy">Modificado: {dateLabel(detail.data.report.modified_at)}</p><pre className="report-markdown" tabIndex={0} aria-label="Contenido del reporte en texto">{detail.data.markdown}</pre></>}{!reportId && <p className="empty-copy">Elige un reporte para leer su contenido. Los eventos recientes del log se muestran abajo; aparecerán en el informe cuando se ejecute un análisis.</p>}</article></section><ObservedEvents items={state?.data.recent_events ?? []} /></>}

        {view === "Actividad" && <section className="panel list-panel"><div className="panel-header"><div><div className="panel-kicker">ACCESS.LOG</div><h2>Actividad reciente</h2><p>Ventana limitada que entrega la API; no es un registro histórico completo</p></div></div><LogLines lines={state?.data.recent_log ?? []} /><p className="status-copy">Origen: {state?.meta.sources.log?.status ?? "sin lectura"} · última modificación {dateLabel(state?.meta.sources.log?.modified_at)}</p></section>}

        <footer className="system-status-bar" aria-label="Estado del sistema"><div className="system-status-items"><span className={`system-status-item system-health ${stateError || (state && state.meta.health !== "ok") ? "status-warning" : ""}`}><span className="environment-dot" aria-hidden="true" /><span className="status-label">ESTADO</span><strong className="status-value">{stateError ? "SIN CONEXIÓN" : state ? state.meta.health === "ok" ? "FUENTES DISPONIBLES" : "FUENTES INCOMPLETAS" : "CONECTANDO"}</strong></span><span className="system-status-item"><span className="status-label">API</span><span className="status-value">v1</span></span><span className="system-status-item"><span className="status-label">ENTORNO</span><span className="status-value">LOCAL</span></span><span className="system-status-item status-capture"><span className="status-label">CAPTURA</span><span className="status-value">{state ? dateLabel(state.meta.captured_at) : "SIN CAPTURA"}</span></span></div><span className="system-status-brand">WEB-DEFENSE-AI V2</span></footer>
      </main>
    </div>
  </div>;
}

function LogLines({ lines }: { lines: string[] }) {
  return <pre className="log-lines" tabIndex={0} aria-label="Líneas recientes del registro">{lines.length ? lines.join("\n") : "No hay líneas de log disponibles."}</pre>;
}

function Pager({ page, total, size, change }: { page: number; total: number; size: number; change: (value: number) => void }) {
  const last = Math.max(1, Math.ceil(total / size));
  return <nav className="pager" aria-label="Paginación"><span className="pager-range">{total ? `${number((page - 1) * size + 1)}–${number(Math.min(page * size, total))} de ${number(total)}` : "0 resultados"}</span><button disabled={page <= 1} onClick={() => change(page - 1)}>Anterior</button><span>Página {page} de {last}</span><button disabled={page >= last} onClick={() => change(page + 1)}>Siguiente</button></nav>;
}
