import { ShieldAlert } from "lucide-react";
import type { Threat } from "@/lib/api";

const names: Record<string, string> = { CRITICA: "Crítica", ALTA: "Alta", MEDIA: "Media", BAJA: "Baja", DESCONOCIDA: "Desconocida" };
function severity(value: string) {
  const code = value.toUpperCase().replaceAll("Í", "I");
  return names[code] ? code : "DESCONOCIDA";
}

export function ThreatTable({ items, dateLabel, sourceAvailable = true }: { items: Threat[]; dateLabel: (value: string | null) => string; sourceAvailable?: boolean }) {
  if (!items.length) return <div className="table-empty"><ShieldAlert size={24} aria-hidden="true" /><p>{sourceAvailable ? "No hay amenazas para esta selección." : "Reporte no disponible."}</p><span>{sourceAvailable ? "Prueba a quitar filtros o consulta otra captura." : "Las amenazas aparecerán cuando se pueda leer el reporte."}</span></div>;
  return <div className="table-scroll threat-table" tabIndex={0} role="region" aria-label="Tabla de amenazas; desplazamiento horizontal disponible">
    <table><caption className="sr-only">Amenazas observadas en el reporte; los estados y fechas se muestran solo cuando están disponibles.</caption>
      <thead><tr><th scope="col">TIPO / REFERENCIA</th><th scope="col">IP OBSERVADA</th><th scope="col">SEVERIDAD</th><th scope="col">ESTADO</th><th scope="col">FECHA DEL EVENTO</th></tr></thead>
      <tbody>{items.map((item) => <tr key={item.id}>
        <td><div className="event-cell"><span className="event-icon blue" aria-hidden="true"><ShieldAlert size={18} /></span><strong>{item.type || "Tipo no disponible"}</strong></div>
          <details className="threat-reference"><summary>Referencia {item.number || "sin número"}</summary><dl>
            <dt>ID de amenaza</dt><dd>{item.id}</dd>
            <dt>ID de reporte de origen</dt><dd>{item.source_report_id || "No disponible"}</dd>
          </dl><p>Referencia de la clasificación; no demuestra que el ataque tuviera éxito.</p></details>
        </td>
        <td>{item.source_ip && item.source_ip !== "-" ? item.source_ip : "Desconocida"}</td>
        <td><span className={`severity-badge severity-${severity(item.severity).toLowerCase()}`}>{names[severity(item.severity)]}</span></td>
        <td>{item.status || "No disponible"}</td><td>{item.event_time ? dateLabel(item.event_time) : "Sin dato en el reporte"}</td>
      </tr>)}</tbody>
    </table>
  </div>;
}
