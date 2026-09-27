"use client";

import { useMemo, useState } from "react";

type IconName = "grid" | "shield" | "file" | "activity" | "settings" | "search" | "bell" | "chevron" | "arrow" | "clock" | "globe" | "more" | "filter" | "download" | "refresh" | "dots" | "menu";

function Icon({ name, size = 18 }: { name: IconName; size?: number }) {
  const shared = { width: size, height: size, viewBox: "0 0 24 24", fill: "none", stroke: "currentColor", strokeWidth: 1.7, strokeLinecap: "round" as const, strokeLinejoin: "round" as const, "aria-hidden": true as const };
  const paths: Record<IconName, React.ReactNode> = {
    grid: <><rect x="3.5" y="3.5" width="7" height="7" rx="1.5"/><rect x="13.5" y="3.5" width="7" height="7" rx="1.5"/><rect x="3.5" y="13.5" width="7" height="7" rx="1.5"/><rect x="13.5" y="13.5" width="7" height="7" rx="1.5"/></>,
    shield: <><path d="M12 3 19 6v5c0 4.6-3 8-7 10-4-2-7-5.4-7-10V6l7-3Z"/><path d="m9 12 2 2 4-4"/></>,
    file: <><path d="M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9Z"/><path d="M14 3v6h6M8 13h8M8 17h8"/></>,
    activity: <><path d="M3 12h4l3-8 4 16 3-8h4"/></>,
    settings: <><circle cx="12" cy="12" r="3"/><path d="m19.4 15 .1.1 1.4 1.1-1.4 2.4-1.7-.7a8 8 0 0 1-1.8 1l-.3 1.8h-2.8l-.3-1.8a8 8 0 0 1-1.8-1l-1.7.7-1.4-2.4 1.4-1.1a7 7 0 0 1 0-2l-1.4-1.1 1.4-2.4 1.7.7a8 8 0 0 1 1.8-1l.3-1.8h2.8l.3 1.8a8 8 0 0 1 1.8 1l1.7-.7 1.4 2.4-1.4 1.1a7 7 0 0 1 0 2Z" transform="translate(-1 -1) scale(1.08)"/></>,
    search: <><circle cx="10.8" cy="10.8" r="6.8"/><path d="m16 16 4.5 4.5"/></>,
    bell: <><path d="M18 9a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9M10 21h4"/></>,
    chevron: <path d="m9 18 6-6-6-6"/>,
    arrow: <><path d="M7 17 17 7M8 7h9v9"/></>,
    clock: <><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></>,
    globe: <><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18"/></>,
    more: <><circle cx="5" cy="12" r="1"/><circle cx="12" cy="12" r="1"/><circle cx="19" cy="12" r="1"/></>,
    filter: <><path d="M4 6h16M7 12h10m-7 6h4"/></>,
    download: <><path d="M12 3v12m-5-5 5 5 5-5M4 20h16"/></>,
    refresh: <><path d="M20 7v5h-5M4 17v-5h5"/><path d="M5.6 9a7 7 0 0 1 11.6-2L20 12M4 12l2.8 5a7 7 0 0 0 11.6-2"/></>,
    dots: <><circle cx="12" cy="5" r="1"/><circle cx="12" cy="12" r="1"/><circle cx="12" cy="19" r="1"/></>,
    menu: <><path d="M4 6h16M4 12h16M4 18h16"/></>,
  };
  return <svg {...shared}>{paths[name]}</svg>;
}

type Threat = { id: string; name: string; detail: string; ip: string; location: string; severity: "Crítica" | "Alta" | "Media"; time: string; initials: string; color: string };

const threats: Threat[] = [
  { id: "EVT-00842", name: "Intento de inyección SQL", detail: "POST /api/auth/login", ip: "203.0.113.47", location: "Red reservada TEST-NET-3", severity: "Crítica", time: "hace 2 min", initials: "T3", color: "violet" },
  { id: "EVT-00841", name: "Fuerza bruta SSH", detail: "22 intentos en 45 s", ip: "198.51.100.12", location: "Red reservada TEST-NET-2", severity: "Alta", time: "hace 8 min", initials: "T2", color: "amber" },
  { id: "EVT-00840", name: "Escaneo de puertos", detail: "Puertos 22, 80, 443, 8080", ip: "192.0.2.110", location: "Red reservada TEST-NET-1", severity: "Media", time: "hace 14 min", initials: "T1", color: "blue" },
  { id: "EVT-00839", name: "Acceso a ruta sensible", detail: "GET /.env — respuesta 403", ip: "203.0.113.71", location: "Red reservada TEST-NET-3", severity: "Alta", time: "hace 21 min", initials: "T3", color: "rose" },
  { id: "EVT-00838", name: "Prueba de recorrido de ruta", detail: "GET /../../config — respuesta 400", ip: "192.0.2.18", location: "Red reservada TEST-NET-1", severity: "Crítica", time: "hace 29 min", initials: "T1", color: "violet" },
  { id: "EVT-00837", name: "Sondeo de panel administrativo", detail: "GET /admin — respuesta 404", ip: "198.51.100.34", location: "Red reservada TEST-NET-2", severity: "Media", time: "hace 37 min", initials: "T2", color: "blue" },
  { id: "EVT-00836", name: "Patrón de solicitud inusual", detail: "Cabecera sintética de prueba", ip: "203.0.113.55", location: "Red reservada TEST-NET-3", severity: "Crítica", time: "hace 46 min", initials: "T3", color: "rose" },
  { id: "EVT-00835", name: "Ráfaga de inicio de sesión", detail: "11 solicitudes en 30 s", ip: "192.0.2.64", location: "Red reservada TEST-NET-1", severity: "Media", time: "hace 53 min", initials: "T1", color: "amber" },
  { id: "EVT-00834", name: "Método HTTP no habitual", detail: "TRACE / — respuesta 405", ip: "198.51.100.89", location: "Red reservada TEST-NET-2", severity: "Crítica", time: "hace 1 h", initials: "T2", color: "violet" },
  { id: "EVT-00833", name: "Exploración de recursos", detail: "Solicitud repetida a /backup", ip: "203.0.113.93", location: "Red reservada TEST-NET-3", severity: "Media", time: "hace 1 h", initials: "T3", color: "blue" },
  { id: "EVT-00832", name: "Cabecera de referencia atípica", detail: "Valor sintético de laboratorio", ip: "192.0.2.101", location: "Red reservada TEST-NET-1", severity: "Crítica", time: "hace 2 h", initials: "T1", color: "rose" },
];

const navItems: { label: string; icon: IconName }[] = [
  { label: "Resumen", icon: "grid" }, { label: "Amenazas", icon: "shield" }, { label: "Reportes", icon: "file" }, { label: "Actividad", icon: "activity" },
];

const chartValues = [24, 35, 29, 48, 38, 58, 47, 70, 54, 44, 64, 52, 80, 62, 71, 51, 65, 46, 58, 39, 48, 34, 53, 41];

export default function Home() {
  const [activeNav, setActiveNav] = useState("Resumen");
  const [query, setQuery] = useState("");
  const [severity, setSeverity] = useState("Todas");
  const [period, setPeriod] = useState("24 horas");
  const [notice, setNotice] = useState("");
  const [mobileNav, setMobileNav] = useState(false);
  const filtered = useMemo(() => threats.filter((item) => {
    const matchesQuery = `${item.name} ${item.detail} ${item.ip} ${item.id}`.toLowerCase().includes(query.toLowerCase());
    return matchesQuery && (severity === "Todas" || item.severity === severity);
  }), [query, severity]);

  function showDemoNotice(message: string) {
    setNotice(message);
    window.setTimeout(() => setNotice(""), 2600);
  }

  return (
    <main className="app-shell">
      <aside className={`sidebar ${mobileNav ? "sidebar-open" : ""}`}>
        <a className="brand" href="#inicio" aria-label="web-defense-ai V2, inicio">
          <span className="brand-mark"><Icon name="shield" size={21} /></span>
          <span className="brand-name">web<span>defense</span><small>AI <b>V2</b></small></span>
        </a>
        <div className="workspace-switch"><div className="workspace-avatar">WD</div><div className="workspace-copy"><span>Workspace</span><strong>Laboratorio <span className="tiny-chevron">⌄</span></strong></div><span className="workspace-dots"><Icon name="more" size={18} /></span></div>
        <div className="nav-label">PLATAFORMA</div>
        <nav className="primary-nav" aria-label="Navegación principal">
          {navItems.map((item) => <button key={item.label} onClick={() => { setActiveNav(item.label); setMobileNav(false); }} className={`nav-link ${activeNav === item.label ? "nav-active" : ""}`} aria-current={activeNav === item.label ? "page" : undefined}><Icon name={item.icon} /><span>{item.label}</span>{item.label === "Amenazas" && <span className="nav-count">12</span>}</button>)}
        </nav>
        <div className="nav-label nav-label-spaced">SISTEMA</div>
        <nav className="primary-nav" aria-label="Configuración">
          <button className="nav-link" onClick={() => { setActiveNav("Integraciones"); setNotice("Vista de integraciones: disponible en una fase posterior"); }}><Icon name="globe" /><span>Integraciones</span><span className="soon-dot" /></button>
          <button className="nav-link" onClick={() => { setActiveNav("Ajustes"); setNotice("Los ajustes se habilitarán con la configuración del backend"); }}><Icon name="settings" /><span>Ajustes</span></button>
        </nav>
        <div className="sidebar-bottom"><div className="plan-card"><div className="plan-head"><span className="plan-icon"><Icon name="shield" size={15} /></span><span>VISTA DE DEMOSTRACIÓN</span><span className="demo-indicator" /></div><strong>Fuentes sin conexión</strong><p>Se muestran datos de ejemplo</p><div className="plan-progress"><span /></div><div className="plan-foot"><span>12 eventos de muestra</span><span>Solo lectura <Icon name="arrow" size={12} /></span></div></div><button className="profile"><span className="profile-avatar">EF</span><span className="profile-name"><strong>Enrique Forte</strong><small>Administrador</small></span><Icon name="more" size={17} /></button></div>
      </aside>

      <section className="main-column" id="inicio">
        <header className="topbar"><button className="mobile-menu icon-button" aria-label="Abrir menú" onClick={() => setMobileNav(!mobileNav)}><Icon name="menu" /></button><div className="breadcrumbs"><span>Consola</span><Icon name="chevron" size={14} /><strong>{activeNav}</strong></div><div className="topbar-right"><div className="environment"><span className="environment-dot" /> ENTORNO DEMO</div><button className="icon-button notification-button" aria-label="Notificaciones" onClick={() => showDemoNotice("No hay notificaciones nuevas en esta demo")}><Icon name="bell" /><i /></button><div className="top-divider" /><button className="top-avatar" aria-label="Perfil de Enrique Forte">EF</button></div></header>

        <div className="content-wrap">
          <div className="demo-banner"><span className="demo-spark">✳</span><span><strong>Modo demostración</strong> · Todos los eventos y métricas de esta pantalla son datos sintéticos.</span><button onClick={() => showDemoNotice("Esta interfaz todavía no consulta el backend")}>¿Qué significa?</button><button className="banner-close" aria-label="Cerrar aviso" onClick={(event) => event.currentTarget.parentElement?.classList.add("banner-hidden")}>×</button></div>

          <section className="page-heading"><div><div className="eyebrow"><span className="eyebrow-line" /> CENTRO DE OPERACIONES</div><h1>{activeNav === "Resumen" ? "Resumen de seguridad" : activeNav}</h1><p>Una vista clara de lo que ocurre en tu perímetro digital.</p></div><div className="heading-actions"><span className="updated-label"><span className="demo-indicator" /> Datos estáticos de ejemplo</span><button className="button-secondary" onClick={() => showDemoNotice("Esta demo no consulta ni actualiza fuentes de datos")}><Icon name="refresh" size={15} /> Actualizar</button></div></section>

          {activeNav !== "Resumen" && <section className="panel module-placeholder"><div className="placeholder-icon"><Icon name={navItems.find((item) => item.label === activeNav)?.icon ?? "settings"} size={21} /></div><div className="panel-kicker">SIGUIENTE ETAPA</div><h2>{activeNav} estará disponible al conectar la API</h2><p>La navegación forma parte de esta base visual. Esta vista todavía no consulta datos ni servicios del sistema.</p><span className="placeholder-tag">Previsto para la fase 4</span></section>}

          <section className={`metric-grid ${activeNav !== "Resumen" ? "module-hidden" : ""}`} aria-label="Indicadores de seguridad">
            <MetricCard icon="shield" label="Eventos de muestra" value="1,284" change="12.8%" trend="up" foot="vs. periodo de ejemplo" tint="cyan" spark={[15, 24, 19, 32, 24, 40, 35, 47, 37, 50, 42, 61]} />
            <MetricCard icon="activity" label="Tasa de contención (demo)" value="96.4%" change="2.4%" trend="up" foot="vs. periodo de ejemplo" tint="green" spark={[26, 18, 31, 23, 38, 28, 40, 30, 48, 37, 56, 49]} />
            <MetricCard icon="globe" label="Orígenes simulados" value="38" change="4 nuevos" trend="neutral" foot="en el periodo de ejemplo" tint="violet" spark={[12, 21, 16, 28, 22, 33, 26, 39, 31, 46, 38, 50]} />
            <MetricCard icon="clock" label="Latencia de ejemplo" value="142 ms" change="18 ms" trend="down" foot="vs. periodo de ejemplo" tint="amber" spark={[48, 41, 44, 34, 38, 30, 33, 25, 29, 20, 24, 16]} />
          </section>

          <section className={`overview-grid ${activeNav !== "Resumen" ? "module-hidden" : ""}`}>
            <article className="panel trend-panel"><div className="panel-header"><div><div className="panel-kicker">ACTIVIDAD DE RED</div><h2>Eventos a lo largo del tiempo</h2><p>Series sintéticas de referencia</p></div><div className="period-select" role="group" aria-label="Periodo del gráfico">{["24 horas", "7 días", "30 días"].map((item) => <button key={item} onClick={() => setPeriod(item)} className={period === item ? "period-active" : ""}>{item}</button>)}</div></div><div className="chart-legend"><span><i className="legend-cyan" /> Eventos de muestra</span><span><i className="legend-green" /> Serie de referencia</span><span className="chart-note">Datos simulados · {period}</span></div><div className="chart-wrap"><div className="chart-y-labels"><span>800</span><span>600</span><span>400</span><span>200</span><span>0</span></div><div className="chart-canvas"><div className="chart-gridlines"><i/><i/><i/><i/><i/></div><svg className="trend-chart" viewBox="0 0 800 210" preserveAspectRatio="none" role="img" aria-labelledby="chart-title chart-description"><title id="chart-title">{`Series sintéticas de eventos en ${period}`}</title><desc id="chart-description">Gráfico de líneas con dos series generadas para la demostración; no representa telemetría real.</desc><defs><linearGradient id="areaFill" x1="0" x2="0" y1="0" y2="1"><stop offset="0%" stopColor="#36d5cf" stopOpacity=".18"/><stop offset="100%" stopColor="#36d5cf" stopOpacity="0"/></linearGradient></defs><path d={chartPath(chartValues, 800, 190)} fill="none" stroke="#39d9d1" strokeWidth="2.5" vectorEffect="non-scaling-stroke"/><path d={chartArea(chartValues, 800, 190)} fill="url(#areaFill)"/><path d={chartPath(chartValues.map((v, i) => Math.max(9, v * .58 + (i % 4) * 3)), 800, 190)} fill="none" stroke="#61cf9e" strokeWidth="2" strokeDasharray="5 5" vectorEffect="non-scaling-stroke"/><circle cx="800" cy={210 - chartValues[chartValues.length - 1] * 2} r="4" fill="#39d9d1" stroke="#0b171d" strokeWidth="3" vectorEffect="non-scaling-stroke"/></svg><div className="chart-x-labels"><span>00:00</span><span>04:00</span><span>08:00</span><span>12:00</span><span>16:00</span><span>20:00</span><span>Ahora</span></div></div></div></article>
            <article className="panel severity-panel"><div className="panel-header"><div><div className="panel-kicker">CLASIFICACIÓN</div><h2>Eventos por severidad</h2><p>Distribución sintética del periodo</p></div><button className="icon-button subtle-button" aria-label="Más opciones" onClick={() => showDemoNotice("Opciones del gráfico en preparación")}><Icon name="dots" /></button></div><div className="severity-content"><div className="donut-wrap"><svg viewBox="0 0 160 160" role="img" aria-label="Datos sintéticos por severidad: 8 críticos, 24 altos y 68 medios"><circle className="donut-track" cx="80" cy="80" r="62"/><circle className="donut-segment seg-medium" cx="80" cy="80" r="62"/><circle className="donut-segment seg-high" cx="80" cy="80" r="62"/><circle className="donut-segment seg-critical" cx="80" cy="80" r="62"/></svg><div className="donut-center"><strong>100</strong><span>EVENTOS</span></div></div><div className="severity-legend"><SeverityLine color="critical" label="Crítica" amount="08" percent="8%"/><SeverityLine color="high" label="Alta" amount="24" percent="24%"/><SeverityLine color="medium" label="Media" amount="68" percent="68%"/></div></div><div className="severity-foot"><span className="severity-foot-icon"><Icon name="shield" size={15} /></span><span><strong>Clasificación de ejemplo</strong><small>No valida incidentes reales</small></span><Icon name="arrow" size={14} /></div></article>
          </section>

          <section className={`panel incidents-panel ${activeNav !== "Resumen" ? "module-hidden" : ""}`}><div className="panel-header incidents-heading"><div><div className="panel-kicker">EVENTOS DE MUESTRA</div><h2>Eventos recientes <span className="count-chip">{Math.min(filtered.length, 4)}</span></h2><p>Actividad sintética; las IP pertenecen a rangos reservados para documentación</p></div><div className="incidents-actions"><button className="button-secondary compact-button" onClick={() => showDemoNotice("Exportación disponible al conectar la API")}><Icon name="download" size={15} /> Exportar</button><button className="button-secondary compact-button filter-button" onClick={() => document.getElementById("severity-filter")?.focus()}><Icon name="filter" size={15} /> Filtros</button></div></div><div className="table-toolbar"><label className="search-field"><Icon name="search" size={16}/><input aria-label="Buscar eventos" placeholder="Buscar por evento, IP o ID..." value={query} onChange={(event) => setQuery(event.target.value)} /><kbd>⌘ K</kbd></label><label className="severity-filter-label"><span className="sr-only">Filtrar por severidad</span><select id="severity-filter" value={severity} onChange={(event) => setSeverity(event.target.value)}><option>Todas</option><option>Crítica</option><option>Alta</option><option>Media</option></select></label><button className="table-options" aria-label="Opciones de tabla" onClick={() => showDemoNotice("Personalización de tabla en una fase posterior")}><Icon name="dots" /></button></div><div className="table-scroll"><table><thead><tr><th>EVENTO</th><th>ORIGEN DE EJEMPLO</th><th>SEVERIDAD</th><th>HORA</th><th><span className="sr-only">Acciones</span></th></tr></thead><tbody>{filtered.slice(0, 4).map((threat) => <tr key={threat.id}><td><div className="event-cell"><span className={`event-icon ${threat.color}`}><Icon name={threat.severity === "Crítica" ? "shield" : "activity"} size={17}/></span><span><strong>{threat.name}</strong><small>{threat.detail} <span className="event-id">· {threat.id}</span></small></span></div></td><td><div className="origin-cell"><span className={`country-badge ${threat.color}`}>{threat.initials}</span><span><strong>{threat.ip}</strong><small>{threat.location}</small></span></div></td><td><SeverityBadge severity={threat.severity}/></td><td className="time-cell">{threat.time}</td><td><button className="row-more" aria-label={`Más opciones para ${threat.id}`} onClick={() => showDemoNotice(`Detalle ${threat.id}: evento sintético de demostración`)}><Icon name="more" size={17}/></button></td></tr>)}</tbody></table>{filtered.length === 0 && <div className="empty-table">No hay eventos que coincidan con la búsqueda.</div>}</div><div className="table-footer"><span>Mostrando <strong>{Math.min(filtered.length, 4)}</strong> de <strong>{filtered.length}</strong> coincidencias sintéticas</span><button onClick={() => setActiveNav("Amenazas")}>Ver todos los eventos <Icon name="arrow" size={14}/></button></div></section>

          <footer className="page-footer"><span>web-defense-ai V2 <i/> Panel de demostración</span><span><span className="footer-status"/> Fuentes de datos simuladas <span className="footer-divider">·</span> Interfaz Fase 3</span></footer>
        </div>
      </section>
      {notice && <div className="toast" role="status"><span className="toast-check">✓</span>{notice}</div>}
    </main>
  );
}

function chartPath(values: number[], width: number, height: number) {
  return values.map((value, index) => `${index === 0 ? "M" : "L"}${(index / (values.length - 1)) * width},${height - value * 2}`).join(" ");
}

function chartArea(values: number[], width: number, height: number) {
  return `${chartPath(values, width, height)} L${width},${height + 20} L0,${height + 20} Z`;
}

function MetricCard({ icon, label, value, change, trend, foot, tint, spark }: { icon: IconName; label: string; value: string; change: string; trend: "up" | "down" | "neutral"; foot: string; tint: string; spark: number[] }) {
  const sparkLine = spark.map((n, i) => `${(i / (spark.length - 1)) * 96},${44 - n * 0.55}`).join(" ");
  return <article className="metric-card"><div className="metric-top"><span className={`metric-icon ${tint}`}><Icon name={icon} size={18}/></span><span className="metric-label">{label}</span><button className="metric-menu" aria-label={`Opciones de ${label}`}><Icon name="more" size={17}/></button></div><div className="metric-bottom"><div><div className="metric-value">{value}</div><div className="metric-change"><span className={`change-${trend}`}>{trend === "up" ? "↗" : trend === "down" ? "↘" : "+"} {change}</span><span>{foot}</span></div></div><svg className={`sparkline ${tint}`} viewBox="0 0 96 48" preserveAspectRatio="none" aria-hidden="true"><polyline points={sparkLine}/></svg></div></article>;
}

function SeverityLine({ color, label, amount, percent }: { color: string; label: string; amount: string; percent: string }) {
  return <div className="severity-line"><span className={`severity-dot ${color}`}/><span className="severity-name">{label}</span><strong>{amount}</strong><small>{percent}</small></div>;
}

function SeverityBadge({ severity }: { severity: Threat["severity"] }) {
  const className = severity === "Crítica" ? "badge-critical" : severity === "Alta" ? "badge-high" : "badge-medium";
  return <span className={`severity-badge ${className}`}><i/>{severity}</span>;
}
