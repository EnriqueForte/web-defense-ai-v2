import type { LucideIcon } from "lucide-react";

type MetricCardProps = {
  label: string;
  value: string;
  note: string;
  source: "Reporte actual" | "Registro de acceso";
  tone: "cyan" | "amber" | "violet" | "green";
  icon: LucideIcon;
};

export function MetricCard({ label, value, note, source, tone, icon: Icon }: MetricCardProps) {
  return (
    <article className={`metric-card metric-${tone}`} aria-label={label}>
      <div className="metric-top">
        <span className="metric-source">{source}</span>
        <span className={`metric-icon ${tone}`}><Icon size={20} strokeWidth={1.75} aria-hidden="true" /></span>
      </div>
      <dl className="metric-reading">
        <dt className="metric-label">{label}</dt>
        <dd className="metric-value">{value}</dd>
      </dl>
      <p className="metric-note">{note}</p>
    </article>
  );
}
