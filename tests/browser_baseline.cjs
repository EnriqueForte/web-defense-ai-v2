// Pruebas de DOM con dobles locales; no abre navegador ni consulta CDNs.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = path.resolve(__dirname, '..');
const scripts = name => [...fs.readFileSync(path.join(root, 'dashboard/templates', name), 'utf8')
  .matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/g)].map(m => m[1]);
const source = scripts('index.html');
const main = source.find(s => s.includes('function sincronizarLog'));
const timeline = source.find(s => s.includes('const timelineData'));
assert.ok(main && timeline, 'No se encontraron los scripts del dashboard');
const marker = '<img src=x onerror=alert(1)> dato sintético';

function element(tag) {
  return {
    nodeType: 1, tagName: tag.toUpperCase(), nodeValue: null, childNodes: [], children: [], attrs: {},
    append(...items) { items.forEach(item => this.appendChild(item)); },
    appendChild(item) { this.childNodes.push(item); if (item.nodeType === 1) this.children.push(item); return item; },
    replaceChildren(...items) { this.childNodes = []; this.children = []; this.append(...items); },
    setAttribute(key, value) { this.attrs[key] = value; },
    getAttribute(key) { return this.attrs[key] || null; },
    addEventListener(name, handler) { this.listeners ??= {}; this.listeners[name] = handler; },
    querySelectorAll() { return []; },
    insertAdjacentHTML() {},
    update() { this.updated = true; },
    get textContent() { return this.childNodes.map(item => item.textContent ?? item.nodeValue ?? '').join(''); },
    set textContent(value) { this.replaceChildren({ nodeType: 3, nodeValue: String(value), textContent: String(value) }); },
  };
}

const terminal = element('div');
const syncButton = element('button');
const metricControl = element('div');
metricControl.dataset = { filter: 'alta' };
const chartCanvas = element('canvas');
const labels = element('span');
const status = element('span');
const time = element('span');
const timelineWrapper = element('div');
const data = { log: [marker], timeline: { horas: ['30/Apr/2026 23h'], sqli: [1], xss: [0], path: [0], brute: [0], cmd: [0] }, timestamp: 'dato sintético' };
const timelineElement = element('script');
timelineElement.textContent = JSON.stringify({ horas: [], sqli: [], xss: [], path: [], brute: [], cmd: [] });
const chartNode = { data: { labels: [], datasets: Array.from({ length: 5 }, () => ({ data: [] })) }, update() { this.updated = true; } };
let fetchCount = 0;
const ctx = vm.createContext({
  document: {
    getElementById: id => ({ btnSincronizar: syncButton, logTerminal: terminal, 'timeline-data': timelineElement,
      timelineChart: chartCanvas, timelineCount: labels, estadoSistema: status, reportBody: null }[id] || null),
    querySelector: selector => selector === '.timeline-wrapper' ? timelineWrapper : selector === '.status-time' ? time : null,
    querySelectorAll: selector => selector === '[data-filter]' ? [metricControl] : [],
    createElement: tag => element(tag),
    createTextNode: value => ({ nodeType: 3, nodeValue: String(value), textContent: String(value) }),
    createDocumentFragment: () => element('fragment'),
  },
  Node: { TEXT_NODE: 3, ELEMENT_NODE: 1 },
  setInterval() {}, setTimeout() {}, console: { log() {} },
  fetch: async () => { fetchCount++; return { ok: true, json: async () => data }; },
  Chart: function (_canvas, config) { chartNode.data = config.data; return chartNode; },
  marked: { parse: raw => raw },
});

class SyntheticNode {
  constructor(tag, children = [], attrs = {}) {
    this.nodeType = 1; this.tagName = tag.toUpperCase(); this.childNodes = children; this.attrs = attrs;
  }
  getAttribute(name) { return this.attrs[name] || null; }
}
const textNode = value => ({ nodeType: 3, nodeValue: value });
const unsafeTree = [new SyntheticNode('p', [textNode('reporte'),
  new SyntheticNode('script', [textNode('alert(1)')]),
  new SyntheticNode('a', [textNode('malicioso')], { href: 'javascript:alert(1)', onclick: 'alert(2)' }),
  new SyntheticNode('a', [textNode('referencia')], { href: 'https://example.test/evidence', onclick: 'alert(3)' }),
])];
ctx.DOMParser = function () { return { parseFromString: () => ({ body: { childNodes: unsafeTree } }) }; };

(async () => {
  vm.runInContext(main, ctx, { timeout: 1000 });
  assert.equal(syncButton.listeners.click, ctx.sincronizarLog);
  assert.equal(typeof metricControl.listeners.click, 'function');
  vm.runInContext(timeline, ctx, { timeout: 1000 });
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(fetchCount, 1, 'El panel consulta el estado una sola vez por ciclo');
  assert.equal(terminal.textContent, '$' + marker, 'El log se presenta como texto literal');
  assert.equal(terminal.children[0].children.length, 1, 'El payload no crea elementos HTML');
  assert.deepEqual(Array.from(chartNode.data.labels), data.timeline.horas);
  assert.equal(chartNode.updated, true, 'El timeline actualiza sus series con la misma respuesta');
  assert.equal(labels.textContent, '1 periodos');

  const reportBody = element('div');
  reportBody.textContent = '\n        reporte sintético\n    ';
  ctx.marked.parse = raw => { assert.equal(raw, 'reporte sintético'); return raw; };
  ctx.document.getElementById = id => id === 'reportBody' ? reportBody : null;
  const reportScript = scripts('report.html').find(s => s.includes('copiarNodoSeguro'));
  assert.ok(reportScript, 'No se encontró el renderizado seguro del reporte');
  vm.runInContext(reportScript, ctx, { timeout: 1000 });
  assert.equal(reportBody.children.length, 1);
  assert.equal(reportBody.children[0].tagName, 'P');
  assert.equal(reportBody.children[0].textContent, 'reportemaliciosoreferencia');
  const links = reportBody.children[0].children.filter(child => child.tagName === 'A');
  assert.equal(links[0].getAttribute('href'), null, 'Se elimina el esquema javascript:');
  assert.equal(links[0].getAttribute('onclick'), null, 'Se descartan atributos de evento');
  assert.equal(links[1].getAttribute('href'), 'https://example.test/evidence');
  console.log('3 comprobaciones JavaScript aprobadas: XSS de log, renderizado de Markdown y refresco de timeline.');
})().catch(error => { console.error(error); process.exitCode = 1; });
