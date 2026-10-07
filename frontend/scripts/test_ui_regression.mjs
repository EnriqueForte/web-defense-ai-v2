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
  const baseRequire = loaded.require.bind(loaded);
  loaded.require = (specifier) => {
    const candidate = path.resolve(path.dirname(filename), specifier) + ".ts";
    if (specifier.startsWith(".") && fs.existsSync(candidate)) {
      return loadTsx(path.relative(path.resolve(scriptDirectory, ".."), candidate));
    }
    return baseRequire(specifier);
  };
  loaded._compile(output.outputText, filename);
  return loaded.exports;
}

function render(Component, props) {
  return renderToStaticMarkup(React.createElement(Component, props));
}

const { MetricCard } = loadTsx("src/components/metric-card.tsx");
const { SeverityChart, TimelineChart } = loadTsx("src/components/security-charts.tsx");
const { ThreatTable } = loadTsx("src/components/threat-table.tsx");
const { refreshedReportSelection } = loadTsx("src/lib/report-selection.ts");
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
const datedGroup = render(ThreatTable, { items: [{ ...hostileThreat, number: "1,2", event_time_start: "2026-10-02T18:00:00Z", event_time_end: "2026-10-02T18:00:20Z", event_time_missing_count: 1 }], dateLabel });
assert.match(datedGroup, /2026-10-02T18:00:00Z.*2026-10-02T18:00:20Z/);
assert.match(datedGroup, /1 peticiones sin fecha/);
assert.match(datedGroup, /Líneas del log: 1,2/);
assert.doesNotMatch(datedGroup, /Sin fecha conocida/);
checks++;
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

const oldCurrent = { id: "a".repeat(64), current: true, filename: "report.md" };
const newCurrent = { ...oldCurrent, id: "b".repeat(64) };
const historical = { ...oldCurrent, id: "c".repeat(64), current: false };
assert.equal(refreshedReportSelection(oldCurrent.id, [oldCurrent, historical], [newCurrent, historical]), newCurrent.id);
assert.equal(refreshedReportSelection(historical.id, [oldCurrent, historical], [newCurrent, historical]), historical.id);
assert.equal(refreshedReportSelection(oldCurrent.id, [oldCurrent], [historical]), oldCurrent.id);
assert.equal(refreshedReportSelection("", [oldCurrent], [newCurrent]), "");
checks++;

const { getApi } = loadTsx("src/lib/api.ts");
const originalFetch = globalThis.fetch;
try {
  const controller = new AbortController();
  let finishBody;
  const body = new Promise((resolve) => { finishBody = resolve; });
  globalThis.fetch = async () => ({ ok: true, json: () => body });
  const pending = getApi("reportes/old", controller.signal);
  await Promise.resolve();
  controller.abort();
  finishBody({ meta: { api_version: "1" }, data: { markdown: "obsolete" } });
  await assert.rejects(pending, (error) => error.name === "AbortError");
  globalThis.fetch = async () => ({ ok: true, json: async () => ({ meta: { api_version: "1", total: 0, page: 1, per_page: 20 }, data: [] }) });
  assert.deepEqual((await getApi("reportes")).data, []);
} finally {
  globalThis.fetch = originalFetch;
}
checks++;
const { validReadResponse } = loadTsx("src/lib/api-contracts.ts");
const hex = (n) => 'a'.repeat(n), at = '2026-10-07T12:00:00Z';
const validThreat = { id: hex(24), number: '1', severity: 'ALTA', type: 'SQLi', status: 'Indicador observado', source_ip: null, event_time: null, source_report_id: hex(64) };
const validReport = { id: hex(64), filename: 'report.md', modified_at: at, size_bytes: 10, current: true };
const validJob = { id: hex(32), kind: 'manual', status: 'succeeded', phase: 'finished', requested_at: at,
  started_at: at, finished_at: at, last_ingested_at: at, last_analyzed_at: at, report_id: hex(64), error_code: null, executor: 'online', deliveries: {} };
const validSettings = { provider: 'openrouter', model: 'openrouter/openrouter/free', pricing_mode: 'free', api_key_configured: false,
  providers: [{ id: 'openrouter', label: 'OpenRouter', default_model: 'openrouter/openrouter/free', free_models: ['openrouter/openrouter/free'], api_key_configured: false }] };
const envelope = (data, extra = {}) => ({ meta: { api_version: '1', ...extra }, data });
const stateFixture = envelope({ stats: { total: 1, criticas: 0, altas: 1, medias: 0, bajas: 0, desconocidas: 0, ips: 0 },
  threats: [validThreat], threats_total: 1, threats_truncated: false, recent_log: [], recent_events: [], source_ips: [],
  timeline: { source: 'access.log', meaning: 'pattern_matches', periods: [] }, recent_reports: [] },
  { snapshot_id: hex(64), report_id: hex(64), captured_at: at, health: 'ok', sources: { report: { status: 'available', modified_at: at }, log: { status: 'missing', modified_at: null } } });
const cases = [
  ['estado', stateFixture], ['amenazas', envelope([validThreat], { total: 1, page: 1, per_page: 25, snapshot_id: hex(64), report_id: hex(64) })],
  ['reportes', envelope([validReport], { total: 1, page: 1, per_page: 20 })],
  [`reportes/${hex(64)}`, envelope({ report: validReport, markdown: 'text', display_markdown: 'view' }, { report_id: hex(64) })],
  ['analisis/actual', envelope({ manual_enabled: false, llm_ready: false, llm_provider: 'openrouter', executor: 'online', job: validJob })],
  [`analisis/${hex(32)}`, envelope(validJob)], ['configuracion/llm', envelope(validSettings)],
];
for (const [route, fixture] of cases) {
  assert.equal(validReadResponse(route, fixture), true, route);
  for (const malformed of [null, [], {}, { meta: null, data: null }, { ...fixture, data: null }]) {
    assert.equal(validReadResponse(route, malformed), false, route);
  }
}
const brokenState = structuredClone(stateFixture);
brokenState.data.stats.total = NaN;
assert.equal(validReadResponse('estado', brokenState), false);
brokenState.data.stats.total = 1;
brokenState.data.threats[0].event_time_end = 'today';
assert.equal(validReadResponse('estado', brokenState), false);
brokenState.data.threats[0].event_time_end = '2026-02-31T12:00:00Z';
assert.equal(validReadResponse('estado', brokenState), false);
assert.equal(validReadResponse(`reportes/${'b'.repeat(64)}`, cases[3][1]), false);
checks++;

try {
  let sentSignal;
  globalThis.fetch = async (_url, options) => { sentSignal = options.signal; return new Promise(() => {}); };
  await assert.rejects(getApi('estado', undefined, 10), (error) => error.status === 408);
  assert.equal(sentSignal.aborted, true);
  globalThis.fetch = async () => ({ ok: true, json: () => new Promise(() => {}) });
  await assert.rejects(getApi('estado', undefined, 10), (error) => error.status === 408);
  globalThis.fetch = async () => ({ ok: true, json: async () => ({ meta: { api_version: '1' }, data: null }) });
  await assert.rejects(getApi('estado'), (error) => error.status === 502);
  globalThis.fetch = async () => ({ ok: true, json: async () => { throw new Error('untrusted body'); } });
  await assert.rejects(getApi('estado'), (error) => error.status === 502 && !error.message.includes('untrusted'));
  globalThis.fetch = async () => ({ ok: true, json: async () => stateFixture });
  assert.equal((await getApi('estado')).data.stats.total, 1);
} finally { globalThis.fetch = originalFetch; }
checks++;

const { startReadPolling } = loadTsx('src/lib/read-polling.ts');
const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
let releases = [], observedSignals = [], calls = 0;
const polling = startReadPolling(async (signal) => { calls++; observedSignals.push(signal); await new Promise((resolve) => releases.push(resolve)); }, 5);
try {
  await Promise.resolve();
  await polling.request(); await polling.request();
  await sleep(15);
  assert.equal(calls, 1, 'slow read must not overlap manual/visibility/timer triggers');
  releases.shift()();
  await sleep(15);
  assert.equal(calls, 2, 'completion schedules the next read');
  polling.stop();
  assert.equal(observedSignals.at(-1).aborted, true);
  releases.shift()();
  await sleep(10);
  assert.equal(calls, 2, 'stopping prevents further requests');
} finally { polling.stop(); releases.forEach((finish) => finish()); }
checks++;
let recoveredCalls = 0, finishRecovery;
const recovering = startReadPolling(async () => {
  if (++recoveredCalls === 1) throw new Error('simulated disconnected');
  await new Promise((resolve) => { finishRecovery = resolve; });
}, 5);
try { await sleep(20); assert.equal(recoveredCalls, 2); }
finally { recovering.stop(); finishRecovery?.(); }
checks++;
let visible = false, visibleCalls = 0;
const visibilityPolling = startReadPolling(async () => { visibleCalls++; }, 100000, () => visible);
try {
  await Promise.resolve();
  await visibilityPolling.request();
  assert.equal(visibleCalls, 0);
  visible = true;
  await visibilityPolling.request();
  assert.equal(visibleCalls, 1);
  visibilityPolling.stop();
  await visibilityPolling.request();
  assert.equal(visibleCalls, 1);
} finally { visibilityPolling.stop(); }
checks++;
console.log(`${checks} grupos de regresión de UI aprobados.`);
