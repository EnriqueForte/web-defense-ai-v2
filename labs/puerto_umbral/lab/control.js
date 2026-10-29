'use strict';
const token = document.querySelector('meta[name="umbral-control"]').content;
const $ = id => document.getElementById(id);
const escapeText = v => String(v).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const ports = { vulnerable: 4380, corrected: 4382 };
const evidenceNames = { local_http: 'Respuesta HTTP', http_and_browser: 'HTTP y navegador', application_state: 'Identidad y estado', http_control_browser_pending: 'HTTP; navegador por comprobar', unix_http_canary: 'Señuelo HTTP interno', fixture_review: 'Revisión de artefactos ficticios' };
let definitions = {};
let current = null;
let poller = null;
let framed = null;
let confirming = false;
let busy = false;
async function api(path, body) { const response = await fetch(path, { method: body ? 'POST' : 'GET', headers: { 'X-Umbral-Control': token, ...(body ? { 'Content-Type': 'application/json' } : {}) }, ...(body ? { body: JSON.stringify(body) } : {}) }); const result = await response.json(); if (!response.ok)
    throw new Error(result.error || 'operation_failed'); return result; }
function notice(text) { $('notice').textContent = text; }
function setBusy(value) { busy = value; for (const id of ['scenario', 'mode', 'kind', 'variant', 'run', 'reset'])
    $(id).disabled = value || confirming; $('confirm-csrf').disabled = value || confirming; $('cancel').classList.toggle('hidden', !value || confirming); }
function selection() { return { scenario: $('scenario').value, mode: $('mode').value, variant: Number($('variant').value), kind: $('kind').value }; }
function updateSelection() { const s = selection(), d = definitions[s.scenario]; $('scenario-title').textContent = d?.name || 'Selecciona un escenario'; $('scenario-code').textContent = (d?.phase || 'F2') + ' · ' + (d?.owasp || 'LOCAL'); $('open-portal').href = 'http://127.0.0.1:' + ports[s.mode]; $('run').textContent = d?.phase === 'F7' ? 'Revisar artefacto ficticio' : 'Ejecutar escenario local'; $('evidence-kind').textContent = d?.evidence_kind === 'fixture_review' ? 'Revisión educativa de artefactos ficticios; no explotación real.' : d?.evidence_kind === 'http_control_browser_pending' ? 'Control HTTP de origen/token. La comprobación CSRF en navegador está pendiente.' : d?.phase === 'F6' ? 'Estado e identidad de aplicación; auditoría separada del access.log.' : 'Peticiones HTTP locales con evidencia correlacionada.'; $('reset-scope').textContent = d?.phase === 'F6' || d?.phase === 'F7' ? 'Restablece el módulo avanzado del modo elegido, incluidas sus sesiones, avisos y permisos ficticios. Los recibos anteriores se conservan.' : 'Restablece exclusivamente el contenedor del escenario y modo elegidos. Los recibos y logs anteriores se conservan.'; document.querySelectorAll('[data-scenario]').forEach(b => { b.classList.toggle('active', b.dataset.scenario === s.scenario); b.setAttribute('aria-pressed', b.dataset.scenario === s.scenario); }); }
function download(record) { const url = URL.createObjectURL(new Blob([JSON.stringify(record, null, 2)], { type: 'application/json;charset=utf-8' })); const a = document.createElement('a'); a.href = url; a.download = 'puerto-umbral-real-' + record.id + '.json'; document.body.append(a); a.click(); a.remove(); setTimeout(() => URL.revokeObjectURL(url), 1000); }
function showRecord(record) { current = record; $('run-status').textContent = record.status.toUpperCase(); const running = record.status === 'running'; setBusy(running); const good = record.status === 'completed'; let message = 'Prueba en preparación: verificando y restableciendo el escenario…'; if (!running) {
    if (!good)
        message = 'Ejecución ' + record.status + ': ' + (record.error || 'no se completó la observación.');
    else if (record.kind === 'benign')
        message = record.benign_ok ? 'Uso normal completado correctamente.' : 'Resultado normal no confirmado.';
    else if (record.evidence_kind === 'fixture_review')
        message = record.fixture_effect_observed ? 'Condición educativa observada al revisar el artefacto ficticio.' : 'Control observado en la revisión del artefacto ficticio.';
    else if (record.scenario === 'csrf' && record.browser_csrf_observed)
        message = record.browser_control_outcome === 'state_changed' ? 'Cambio observado tras formulario de otro origen con sesión del navegador.' : 'Formulario de otro origen con sesión del navegador rechazado.';
    else if (record.scenario === 'csrf')
        message = record.http_control_effect_observed ? 'Cambio de estado en la prueba HTTP de origen/token. La comprobación CSRF en navegador sigue pendiente.' : 'Solicitud rechazada en la prueba HTTP de origen/token. Comprobación en navegador pendiente.';
    else if (['xss', 'stored_xss'].includes(record.scenario))
        message = record.browser_execution_confirmed ? 'Ejecución de JavaScript confirmada en el navegador.' : record.reflection_encoded ? 'Entrada codificada como texto en la respuesta.' : 'Reflexión sin codificar observada. Falta confirmar ejecución en el navegador.';
    else
        message = record.functional_effect_confirmed ? 'Efecto funcional observado dentro del laboratorio.' : record.mode === 'corrected' ? 'No se observó el efecto del intento en esta prueba corregida.' : 'No se confirmó el efecto. Revisa y conserva la respuesta.';
} $('effect').textContent = message; $('effect').className = 'result-banner ' + (!good && !running ? 'error' : record.mode === 'corrected' ? 'corrected' : ''); const count = record.requests.length; const snapshot = record.access_snapshot; $('observations').textContent = `Ejecución: ${record.id}\nOrigen: ${record.evidence_kind === 'fixture_review' ? 'revisión de artefacto ficticio mediante HTTP' : 'peticiones HTTP locales reales'}\nFase: ${record.phase || 'F2'} · Modo: ${record.mode} · Tipo: ${record.kind} · Variante: ${record.variant + 1}\nPeticiones del ejecutor: ${count} · V2 consultado: no\nCaptura Apache: ${snapshot ? snapshot.matches.length + ' líneas correlacionadas' : 'pendiente'}\nAuditoría de aplicación: ${record.application_audit ? record.application_audit.events + ' eventos / ' + record.application_audit.correlated_requests + ' referencias HTTP' : 'no disponible'}${record.application_audit_error ? ' · ' + record.application_audit_error : ''}${record.capture_error ? ' · ERROR DE CAPTURA: ' + record.capture_error : ''}`; if (record.browser_expires_at) $('observations').textContent += '\nVentana de navegador hasta: ' + new Date(record.browser_expires_at).toLocaleString('es-ES', { timeZone: 'Europe/Madrid' }) + ' (Madrid), salvo restablecimiento o cuota agotada.'; $('observations').style.whiteSpace = 'pre-line'; const last = Number.isInteger(record.display_request_index) ? record.requests[record.display_request_index] : record.requests.at(-1); $('response').textContent = last ? `${last.method} ${last.target}\nHTTP ${last.status}\nSHA256 ${last.body_sha256}\n\n${last.body_text}` : 'Esperando respuesta del escenario…'; $('export').classList.toggle('hidden', running); const csrfReady = record.scenario === 'csrf' && record.kind === 'attempt' && good; $('csrf-browser').classList.toggle('hidden', !csrfReady); $('confirm-csrf').classList.toggle('hidden', !csrfReady); $('csrf-browser').href = '/csrf-demo?run=' + record.id; $('xss-panel').classList.toggle('hidden', !['xss', 'stored_xss'].includes(record.scenario) || !record.frame_url || !good); if (['xss', 'stored_xss'].includes(record.scenario) && record.frame_url && good && framed !== record.id) {
    framed = record.id;
    $('browser-result').textContent = 'Cargando respuesta en el iframe aislado…';
    $('xss-frame').src = record.frame_url;
} if (record.browser_execution_confirmed)
    $('browser-result').textContent = 'Confirmado: marcador recibido de este iframe con el nonce de la ejecución.';
else if (record.reflection_encoded)
    $('browser-result').textContent = 'Respuesta codificada: el payload se presenta como texto. Sin ejecución confirmada.'; }
function history(records) { $('history').innerHTML = records.length ? records.map(r => `<tr><td>${escapeText(r.id.slice(0, 12))}</td><td>${escapeText(definitions[r.scenario]?.name || r.scenario)}</td><td>${r.mode === 'corrected' ? 'Corregido' : 'Vulnerable'}</td><td>${escapeText(r.status)}</td><td>${r.access_snapshot ? r.access_snapshot.matches.length + ' líneas' : 'Pendiente'}${r.browser_execution_confirmed ? ' · JS confirmado' : ''}</td><td><button class="text-link" data-record="${r.id}">Consultar →</button></td></tr>`).join('') : '<tr><td colspan="6">Todavía no hay ejecuciones locales.</td></tr>'; }
async function refresh() { const s = await api('/api/status'); history(s.runs); $('coverage').innerHTML = (s.coverage || []).map(row => `<tr><td>${escapeText(row.category)} · ${escapeText(row.name)}</td><td>${row.scenarios.map(escapeText).join(' · ')}</td><td>${row.evidence.map(kind => escapeText(evidenceNames[kind] || 'Evidencia por revisar')).join(' · ')}</td><td>Pendiente</td></tr>`).join(''); $('boundary').textContent = `Perímetro verificado al iniciar: ${s.boundary.containers.length} contenedores · targets sin red IP · Apache en loopback · usuario sin privilegios · raíz de solo lectura. La fuente V2 se consulta por separado; este panel no solicita análisis.`; return s; }
async function poll(id) { try {
    const record = await api('/api/runs/' + id);
    showRecord(record);
    if (record.status === 'running')
        poller = setTimeout(() => poll(id), 650);
    else {
        clearTimeout(poller);
        await refresh();
        notice('Evidencias conservadas fuera del contenedor vulnerable.');
    }
}
catch (error) {
    setBusy(false);
    notice('No se pudo consultar la ejecución: ' + error.message);
} }
$('run').addEventListener('click', async () => { try {
    notice('Preparando prueba real…');
    setBusy(true);
    const r = await api('/api/run', selection());
    framed = null;
    await poll(r.id);
}
catch (error) {
    setBusy(false);
    notice('No se inició la prueba: ' + error.message);
} });
$('cancel').addEventListener('click', async () => { try {
    await api('/api/cancel', {});
    notice('Detención solicitada. Se conservarán las respuestas ya recibidas.');
}
catch (error) {
    notice(error.message);
} });
$('reset').addEventListener('click', async () => { try {
    setBusy(true);
    notice('Restableciendo el módulo seleccionado; las ampliaciones comparten estado por modo…');
    await api('/api/reset', selection());
    notice('Escenario restablecido. Historial y logs conservados.');
}
catch (error) {
    notice('No se pudo restablecer: ' + error.message);
}
finally {
    setBusy(false);
} });
$('export').addEventListener('click', () => { if (current)
    download(current); });
$('refresh').addEventListener('click', () => refresh().catch(e => notice(e.message)));
for (const id of ['scenario', 'mode', 'kind', 'variant'])
    $(id).addEventListener('change', updateSelection);
document.addEventListener('click', async (e) => { const b = e.target.closest('[data-scenario]'); if (b && !busy && !confirming) {
    $('scenario').value = b.dataset.scenario;
    updateSelection();
} const r = e.target.closest('[data-record]'); if (r && !busy && !confirming) {
    try {
        showRecord(await api('/api/runs/' + r.dataset.record));
    }
    catch (error) {
        notice(error.message);
    }
} });
window.addEventListener('message', async (event) => { if (event.source !== $('xss-frame').contentWindow || event.origin !== 'null' || !current || !['xss', 'stored_xss'].includes(current.scenario) || event.data?.kind !== 'umbral-xss' || event.data?.nonce !== current.nonce || busy || confirming || current.browser_execution_confirmed)
    return; confirming = true; setBusy(true); try {
    await api('/api/confirm-xss', { id: current.id, nonce: event.data.nonce });
    showRecord(await api('/api/runs/' + current.id));
    await refresh();
}
catch (error) {
    $('browser-result').textContent = 'El marcador no se pudo confirmar: ' + error.message;
}
finally {
    confirming = false; setBusy(false);
} });
async function boot() { try {
    const s = await api('/api/status');
    definitions = s.scenarios;
    $('scenario').innerHTML = Object.entries(definitions).map(([id, s]) => `<option value="${id}">${escapeText(s.phase || 'F2')} · ${escapeText(s.name)}</option>`).join('');
    $('scenario-nav').innerHTML = Object.entries(definitions).map(([id, s], index) => `<button class="nav-link" data-scenario="${id}" aria-pressed="false"><span>${escapeText(s.name)}</span><span class="nav-count">0${index + 1}</span></button>`).join('');
    updateSelection();
    await refresh();
    if (s.current)
        await poll(s.current);
}
catch (error) {
    $('boundary').textContent = 'No se pudo verificar el laboratorio: ' + error.message;
    $('run').disabled = true;
    $('reset').disabled = true;
} }
setInterval(() => { $('clock').textContent = new Date().toLocaleTimeString('es-ES', { timeZone: 'UTC', hour12: false }) + ' UTC'; }, 1000);
boot();
$('confirm-csrf').addEventListener('click', async () => { if (!current || current.scenario !== 'csrf' || current.status !== 'completed' || busy || confirming)
    return; confirming = true; setBusy(true); try {
    await api('/api/confirm-csrf', { id: current.id });
    showRecord(await api('/api/runs/' + current.id));
    notice('Evidencia del navegador revisada mediante la auditoría de aplicación.');
}
catch (error) {
    notice('Sin confirmación de navegador: ' + error.message);
}
finally {
    confirming = false; setBusy(false);
} });
