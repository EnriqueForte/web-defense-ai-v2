// Sin navegador, CDN ni red: dobles de DOM y de Marked para comprobar flujo de datos.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = path.resolve(__dirname, '..');
const scripts = name => [...fs.readFileSync(path.join(root, 'dashboard/templates', name), 'utf8')
  .matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/g)].map(m => m[1]);
const source = scripts('index.html');
const main = source.find(s => s.includes('let countdown'));
const timeline = source.find(s => s.includes('const timelineData'));
assert.ok(main && timeline, 'No se encontraron los scripts que se deben evaluar');
const marker = '<b data-untrusted="fixture">dato sintético</b>';
function context() {
  const terminal = { innerHTML: '', scrollHeight: 0 };
  return { terminal, ctx: vm.createContext({
    document: { getElementById: id => id === 'logTerminal' ? terminal :
      id === 'timeline-data' ? { textContent: '{"horas":[]}' } : null,
      querySelector: () => null },
    setInterval() {}, setTimeout() {}, console: { log() {} },
    fetch: async () => ({ json: async () => ({ log: [marker] }) }),
    Chart: function () {},
  }) };
}
let known = 0;
async function expectedFailure(id, check) {
  try { await check(); }
  catch (error) {
    if (error.code !== 'ERR_ASSERTION') throw error;
    known++;
    console.log(`FALLO CONOCIDO ${id}`);
    return;
  }
  throw new Error(`${id}: comportamiento corregido; retirar marca de fallo conocido`);
}
(async () => {
  const first = context();
  vm.runInContext(main, first.ctx, { timeout: 1000 });
  await vm.runInContext('actualizarLog()', first.ctx, { timeout: 1000 });
  await expectedFailure('H04-log: HTML no confiable llega al terminal', () => {
    assert.ok(!first.terminal.innerHTML.includes(marker));
  });
  vm.runInContext(timeline, first.ctx, { timeout: 1000 });
  await expectedFailure('H03: alias recursivo en refresco', () => {
    assert.equal(vm.runInContext('originalActualizarLog === actualizarLog', first.ctx), false);
  });
  const body = { textContent: marker, innerHTML: '', querySelectorAll: () => [] };
  const reportContext = vm.createContext({ document: { getElementById: () => body },
    marked: { parse: raw => raw } }); // Dobla HTML que Marked puede devolver sin sanear.
  const reportScript = scripts('report.html').find(s => s.includes('marked.parse'));
  assert.ok(reportScript);
  vm.runInContext(reportScript, reportContext, { timeout: 1000 });
  await expectedFailure('H04-report: salida del renderizador sin filtro', () => {
    assert.ok(!body.innerHTML.includes(marker));
  });
  console.log(`3 comprobaciones, ${known} fallos conocidos; no son pruebas de navegador aprobadas.`);
})().catch(error => { console.error(error); process.exitCode = 1; });
