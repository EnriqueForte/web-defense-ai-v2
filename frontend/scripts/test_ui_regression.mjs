import assert from "node:assert/strict";
import fs from "node:fs";
import Module from "node:module";
import path from "node:path";
import { fileURLToPath } from "node:url";
import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { ShieldAlert } from "lucide-react";
import ts from "typescript";

const scriptDirectory = path.dirname(fileURLToPath(import.meta.url));

function loadTsx(relativePath) {
  const filename = path.resolve(scriptDirectory, "..", relativePath);
  const source = fs.readFileSync(filename, "utf8");
  const output = ts.transpileModule(source, {
    compilerOptions: {
      jsx: ts.JsxEmit.ReactJSX,
      module: ts.ModuleKind.CommonJS,
      target: ts.ScriptTarget.ES2022,
    },
    reportDiagnostics: true,
  });
  const errors = (output.diagnostics ?? []).filter((item) => item.category === ts.DiagnosticCategory.Error);
  assert.equal(errors.length, 0, `TypeScript transpilation failed for ${relativePath}`);
  const loaded = new Module(filename);
  loaded.filename = filename;
  loaded.paths = Module._nodeModulePaths(path.dirname(filename));
  loaded._compile(output.outputText, filename);
  return loaded.exports;
}

function render(Component, props) {
  return renderToStaticMarkup(React.createElement(Component, props));
}

const { MetricCard } = loadTsx("src/components/metric-card.tsx");
const { SeverityChart, TimelineChart } = loadTsx("src/components/security-charts.tsx");
const { ThreatTable } = loadTsx("src/components/threat-table.tsx");
const stats = { total: 0, criticas: 0, altas: 0, medias: 0, bajas: 0, desconocidas: 0, ips: 0 };
const dateLabel = (value) => value ?? "No disponible";

let checks = 0;

const splitSeverity = render(SeverityChart, {
  available: true,
  stats: { ...stats, total: 28, altas: 14, bajas: 14 },
});
assert.equal((splitSeverity.match(/stroke-dasharray="50 50"/g) ?? []).length, 2);
assert.match(splitSeverity, /50 %/);
assert.match(splitSeverity, /14/);
checks++;

const noThreats = render(SeverityChart, { available: true, stats });
assert.match(noThreats, /Sin amenazas clasificadas/);
assert.doesNotMatch(noThreats, /NaN|Infinity/);
const missingReport = render(SeverityChart, { available: false, stats });
assert.match(missingReport, /Reporte no disponible/);
assert.doesNotMatch(missingReport, /severity-donut/);
checks++;

const timeline = render(TimelineChart, {
  available: true,
  periods: [
    { period: "30/Apr/2026 22h", count: 0, matches: {} },
    { period: "30/Apr/2026 23h", count: 3, matches: { sqli: 3 } },
  ],
});
assert.match(timeline, /height:0%/);
assert.match(timeline, /height:75%/);
assert.match(timeline, /Consultar datos por periodo/);
assert.match(timeline, /Coincidencias de patrones en el registro de acceso/);
const noPeriods = render(TimelineChart, { available: true, periods: [] });
assert.match(noPeriods, /No hay periodos de log/);
const missingLog = render(TimelineChart, { available: false, periods: [] });
assert.match(missingLog, /Registro de acceso no disponible/);
checks++;

const hostileThreat = {
  id: "<svg onload=alert(1)>",
  number: "1",
  severity: "UNKNOWN",
  type: "<img src=x onerror=alert(1)>",
  status: "<script>alert(1)</script>",
  source_ip: null,
  event_time: null,
  source_report_id: "<b>source</b>",
};
const threatTable = render(ThreatTable, { items: [hostileThreat], dateLabel });
assert.match(threatTable, /&lt;img src=x onerror=alert\(1\)&gt;/);
assert.match(threatTable, /&lt;script&gt;alert\(1\)&lt;\/script&gt;/);
assert.match(threatTable, /&lt;svg onload=alert\(1\)&gt;/);
assert.doesNotMatch(threatTable, /<img |<script>|<svg onload/);
assert.match(threatTable, /Desconocida/);
assert.match(threatTable, /ID de reporte de origen/);
assert.match(threatTable, /desplazamiento horizontal disponible/);
checks++;

const emptyThreats = render(ThreatTable, { items: [], dateLabel, sourceAvailable: true });
const missingThreats = render(ThreatTable, { items: [], dateLabel, sourceAvailable: false });
assert.match(emptyThreats, /No hay amenazas para esta selección/);
assert.match(missingThreats, /Reporte no disponible/);
assert.doesNotMatch(missingThreats, /<table/);
checks++;

const metric = render(MetricCard, {
  label: "Amenazas del reporte",
  value: "—",
  note: "Reporte no disponible en esta captura.",
  source: "Reporte actual",
  tone: "cyan",
  icon: ShieldAlert,
});
assert.match(metric, /aria-label="Amenazas del reporte"/);
assert.match(metric, /Reporte actual/);
assert.match(metric, /Reporte no disponible/);
assert.match(metric, />—</);
checks++;

console.log(`${checks} grupos de regresión de UI aprobados.`);
