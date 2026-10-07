type Obj = Record<string, unknown>;
const obj = (x: unknown): x is Obj => x !== null && typeof x === "object" && !Array.isArray(x);
const str = (x: unknown): x is string => typeof x === "string";
const count = (x: unknown): x is number => typeof x === "number" && Number.isSafeInteger(x) && x >= 0;
const textOrNull = (x: unknown) => x === null || str(x);
const date = (x: unknown) => str(x) && /^\d{4}-(?:0[1-9]|1[0-2])-(?:0[1-9]|[12]\d|3[01])T(?:[01]\d|2[0-3]):[0-5]\d:[0-5]\d(?:\.\d+)?(?:Z|[+-](?:[01]\d|2[0-3]):[0-5]\d)$/.test(x) &&
  Number.isFinite(Date.parse(x)) && new Date(x.slice(0,10) + 'T00:00:00Z').toISOString().slice(0,10) === x.slice(0,10);
const dateOrNull = (x: unknown) => x === null || date(x);
const id = (x: unknown, length: number) => str(x) && new RegExp(`^[a-f0-9]{${length}}$`).test(x);
const idOrNull = (x: unknown, length: number) => x === null || id(x, length);
const oneOf = (x: unknown, values: string[]) => str(x) && values.includes(x);
const list = (x: unknown, check: (x: unknown) => boolean) => Array.isArray(x) && x.every(check);
const optional = (x: Obj, key: string, check: (x: unknown) => boolean) => !(key in x) || check(x[key]);

function threat(x: unknown): boolean {
  return obj(x) && id(x.id, 24) && ['number', 'severity', 'type', 'status'].every(k => str(x[k])) &&
    textOrNull(x.source_ip) && dateOrNull(x.event_time) && idOrNull(x.source_report_id, 64) &&
    optional(x, 'event_time_start', dateOrNull) && optional(x, 'event_time_end', dateOrNull) &&
    optional(x, 'event_time_missing_count', count);
}
function report(x: unknown): boolean {
  return obj(x) && id(x.id, 64) && str(x.filename) && date(x.modified_at) && count(x.size_bytes) && typeof x.current === 'boolean';
}
function job(x: unknown): boolean {
  return obj(x) && id(x.id, 32) && oneOf(x.kind, ['manual', 'periodic']) &&
    oneOf(x.status, ['queued', 'running', 'succeeded', 'failed', 'interrupted']) && str(x.phase) && date(x.requested_at) &&
    ['started_at', 'finished_at', 'last_ingested_at', 'last_analyzed_at'].every(k => dateOrNull(x[k])) &&
    idOrNull(x.report_id, 64) && textOrNull(x.error_code) && oneOf(x.executor, ['online', 'offline', 'unavailable']) &&
    obj(x.deliveries) && Object.values(x.deliveries).every(v => oneOf(v, ['attempting', 'sent', 'failed', 'unknown']));
}
function settings(x: unknown): boolean {
  return obj(x) && str(x.provider) && str(x.model) && oneOf(x.pricing_mode, ['free', 'paid']) &&
    typeof x.api_key_configured === 'boolean' && list(x.providers, p => obj(p) &&
      ['id','label','default_model'].every(k => str(p[k])) && list(p.free_models, str) && typeof p.api_key_configured === 'boolean');
}
export function validReadResponse(path: string, value: unknown): boolean {
  if (!obj(value) || !obj(value.meta) || value.meta.api_version !== '1') return false;
  const m = value.meta, d = value.data, route = path.split('?')[0];
  if (route === 'estado') {
    return id(m.snapshot_id,64) && idOrNull(m.report_id,64) && date(m.captured_at) &&
      oneOf(m.health,['ok','degraded','unavailable']) && obj(m.sources) &&
      ['report','log'].every(k => obj(m.sources) && obj(m.sources[k]) && str(m.sources[k].status) && dateOrNull(m.sources[k].modified_at)) &&
      obj(d) && obj(d.stats) && ['total','criticas','altas','medias','bajas','desconocidas','ips'].every(k => obj(d.stats) && count(d.stats[k])) &&
      list(d.threats,threat) && count(d.threats_total) && typeof d.threats_truncated === 'boolean' &&
      list(d.recent_log,str) && list(d.source_ips,str) && list(d.recent_events,e => obj(e) && id(e.id,24) && date(e.observed_at) &&
        ['category','method','path'].every(k => str(e[k])) && textOrNull(e.source_ip) && count(e.http_status) && e.http_status >= 100 && e.http_status <= 599) &&
      obj(d.timeline) && str(d.timeline.source) && str(d.timeline.meaning) && list(d.timeline.periods,p => obj(p) && date(p.period) && count(p.count) &&
        obj(p.matches) && ['sqli','xss','path','brute','cmd'].every(k => obj(p.matches) && count(p.matches[k]))) &&
      list(d.recent_reports,r => obj(r) && str(r.nombre) && str(r.fecha) && count(r.amenazas)) &&
      optional(d,'log_period',p => obj(p) && dateOrNull(p.first_at) && dateOrNull(p.last_at) && count(p.undated_lines));
  }
  if (route === 'amenazas' || route === 'reportes') return count(m.total) && count(m.page) && m.page > 0 &&
    count(m.per_page) && m.per_page > 0 && (route !== 'amenazas' || (id(m.snapshot_id,64) && idOrNull(m.report_id,64))) &&
    list(d, route === 'amenazas' ? threat : report);
  if (/^reportes\/[a-f0-9]{64}$/.test(route)) return id(m.report_id,64) && obj(d) && report(d.report) &&
    obj(d.report) && d.report.id === route.slice(9) && m.report_id === d.report.id && str(d.markdown) && optional(d,'display_markdown',str);
  if (route === 'analisis/actual') return obj(d) && typeof d.manual_enabled === 'boolean' && typeof d.llm_ready === 'boolean' &&
    str(d.llm_provider) && oneOf(d.executor,['online','offline','unavailable']) && (d.job === null || job(d.job));
  if (/^analisis\/[a-f0-9]{32}$/.test(route)) return job(d) && obj(d) && d.id === route.slice(9);
  if (route === 'configuracion/llm') return settings(d);
  return false;
}
