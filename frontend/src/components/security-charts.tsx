import type { StateResponse } from "@/lib/api";

type Period = StateResponse["data"]["timeline"]["periods"][number];
const format = (value: number) => new Intl.NumberFormat("es-ES").format(value);
const periodLabel = (value: string) => {
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value : new Intl.DateTimeFormat("es-ES", { day: "2-digit", month: "2-digit", year: "numeric", hour: "2-digit", timeZone: "Europe/Madrid" }).format(date) + " (Madrid)";
};
const categories = [
  ["sqli", "SQLi"], ["xss", "XSS"], ["path", "Rutas"],
  ["brute", "Fuerza bruta"], ["cmd", "Comandos"],
] as const;
const severities = [
  ["criticas", "Crítica", "critical"], ["altas", "Alta", "high"],
  ["medias", "Media", "medium"], ["bajas", "Baja", "low"],
  ["desconocidas", "Desconocida", "unknown"],
] as const;

export function SeverityChart({ stats, available }: { stats: StateResponse["data"]["stats"]; available: boolean }) {
  if (!available) return <div className="chart-empty"><p>Reporte no disponible.</p><span>La distribución aparecerá cuando exista una clasificación.</span></div>;
  const total = severities.reduce((sum, [key]) => sum + stats[key], 0);
  const segments = severities.map(([key, label, tone], index) => {
    const percent = total > 0 ? stats[key] / total * 100 : 0;
    const offset = total > 0 ? severities.slice(0, index).reduce((sum, [previous]) => sum + stats[previous], 0) / total * 100 : 0;
    return { key, label, tone, percent, offset, count: stats[key] };
  });
  return <div className="severity-chart">
    <div className="severity-donut" aria-hidden="true">
      <svg viewBox="0 0 120 120">
        <circle className="donut-track" cx="60" cy="60" r="48" fill="none" strokeWidth="12" />
        {segments.filter((item) => item.count > 0).map((item) => <circle key={item.key}
          cx="60" cy="60" r="48" fill="none" strokeWidth="12" pathLength="100"
          stroke={`var(--severity-${item.tone})`} strokeDasharray={`${item.percent} ${100 - item.percent}`}
          strokeDashoffset={-item.offset} transform="rotate(-90 60 60)" />)}
      </svg>
      <div className="donut-caption"><strong>{format(total)}</strong><span>clasificadas</span></div>
    </div>
    {total === 0 && <p className="empty-copy">Sin amenazas clasificadas en esta captura.</p>}
    <ul className="severity-legend" aria-label="Distribución por severidad">
      {segments.map((item) => <li key={item.key}>
        <span className="chart-swatch" style={{ background: `var(--severity-${item.tone})` }} aria-hidden="true" />
        <span>{item.label}</span><strong>{format(item.count)}</strong>
        <span className="chart-percent">{new Intl.NumberFormat("es-ES", { maximumFractionDigits: 1 }).format(item.percent)} %</span>
      </li>)}
    </ul>
  </div>;
}

export function TimelineChart({ periods, available }: { periods: Period[]; available: boolean }) {
  if (!available) return <div className="chart-empty"><p>Registro de acceso no disponible.</p><span>La serie aparecerá cuando el log pueda leerse.</span></div>;
  if (!periods.length) return <div className="chart-empty"><p>No hay periodos de log disponibles.</p><span>El gráfico aparecerá cuando la captura contenga datos.</span></div>;
  const maximum = Math.max(1, ...periods.map((item) => item.count));
  const ceiling = Math.max(2, Math.ceil(maximum / 2) * 2);
  return <>
    <div className="timeline-unit">Coincidencias por periodo · hora local Europe/Madrid · escala 0–{format(ceiling)}</div>
    <div className="timeline-plot">
      <div className="timeline-axis"><span>{format(ceiling)}</span><span>{format(ceiling / 2)}</span><span>0</span></div>
      <div className="timeline-scroll" tabIndex={0} role="region" aria-label="Gráfico de coincidencias por periodo; desplazamiento horizontal disponible"><div className="timeline-columns" aria-hidden="true">
        {periods.map((item, index) => <div className="timeline-column" key={`${item.period}-${index}`} title={`${periodLabel(item.period)}: ${format(item.count)}`}>
          <div className="timeline-bar-space"><div className="timeline-bar" style={{ height: `${item.count / ceiling * 100}%` }}><span>{format(item.count)}</span></div></div>
          <span className="timeline-period">{periodLabel(item.period)}</span>
        </div>)}
      </div></div>
    </div>
    <p className="chart-help">{format(periods.length)} periodos disponibles. No se completan intervalos ausentes.</p>
    <ul className="pattern-summary" aria-label="Coincidencias por patrón">{categories.map(([key, label]) => <li key={key}><span>{label}</span><strong>{format(periods.reduce((sum, item) => sum + (item.matches[key] ?? 0), 0))}</strong></li>)}</ul>
    <details className="chart-data"><summary>Consultar datos por periodo</summary><div className="table-scroll" tabIndex={0} role="region" aria-label="Datos por periodo">
      <table><caption className="sr-only">Coincidencias de patrones en el registro de acceso, en hora local Europe/Madrid</caption><thead><tr><th scope="col">Periodo (Madrid)</th><th scope="col">Total</th>{categories.map(([key, label]) => <th scope="col" key={key}>{label}</th>)}</tr></thead>
        <tbody>{periods.map((item, index) => <tr key={`${item.period}-${index}`}><th scope="row">{periodLabel(item.period)}</th><td>{format(item.count)}</td>{categories.map(([key]) => <td key={key}>{format(item.matches[key] ?? 0)}</td>)}</tr>)}</tbody>
      </table>
    </div></details>
  </>;
}
