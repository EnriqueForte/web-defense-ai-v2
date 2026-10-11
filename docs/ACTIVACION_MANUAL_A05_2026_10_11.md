# A-05 — Activación manual aceptada, 11/10/2026

La admisión manual del piloto está **habilitada** en Flask y disponible por el
proxy Next, con worker online. Las condiciones que habilitan el botón de la UI
están verificadas mediante API y código. El usuario aceptó la vista previa de
narrativa corregida y autorizó habilitar el botón. **No se pulsó el botón ni se
creó un trabajo** durante la activación.

## Aceptación y alcance

El usuario respondió expresamente: «Sí, acepto la vista previa y habilitar el botón»
a la pregunta que mantenía ciclos automáticos y notificaciones apagados y excluía
iniciar análisis durante esta operación. Esta aceptación corresponde a la
[vista previa de narrativa](NARRATIVA_VALIDADA_A05_2026_10_10.md), no a un informe
nuevo generado por proveedor o una prueba de ingesta Docker que no se realizaron.

La operación se limita a arrancar los servicios con `--enable-manual` en el mismo
perfil pilot/structured/.p3. El worker sigue **`--manual-only`** y los destinos de
notificación están vacíos. La admisión no encola nada por sí sola; la interfaz
requiere una pulsación explícita para solicitar un análisis.

## Estado previo, respaldo y arranque

El inventario actual confirmó **cero procesos de servicio del proyecto y cero
listeners en 5000/3000**. No se detuvo ni reutilizó ningún PID de las operaciones
anteriores. Preflight con admisión manual: `.p3` 158 pines/0 diferencias,
locks libres, queued/running=0, puerto 5000 libre y generación structured verificada.

Respaldo nuevo `.local-backups/operational-20261011T162246002052Z`: **30 archivos**,
sin fuentes ausentes, restauración aislada, hashes e integridad SQLite verificados.
La cobertura es la enumerada por `scripts/backup_operational.py`; no incluye
`.env`, volúmenes Docker, Mailpit o todos los archivos futuros de diagnóstico.

Flask y worker se iniciaron a las **18:23:49–50 Madrid / 16:23:49–50 UTC**;
Next a las **18:23:55 Madrid / 16:23:55 UTC**. Procesos sin ventana visible.
No se modificó `.env`: las variables de perfil son overrides de proceso.
Next usa la instalación/build existente de 16.3.8 en modo producción.

| Servicio | Cadena verificada | Restricción |
|---|---|---|
| Flask | 15840 → 19388 → 33696 → **29408** | pilot, structured, .p3, manual=1, loopback 5000, sin debugger |
| Worker | 32856 → 10616 → 32520 → **4592** | pilot, structured, .p3, manual-only, destinos vacíos |
| Next | **28120** | 16.3.8 producción, loopback 3000, API 5000 |

Son identidades de esta sesión, no permisos para detener PID que se reutilicen.
Antes de operar comprobar ejecutable, fecha de creación, argumentos, parentesco
y listener. Windows utiliza lanzadores venv y procesos del Python 3.11 base;
la cadena confirma la selección de `.p3`.

Comandos de los componentes utilizados por los lanzadores locales. **No repetir
mientras estén activos**:

```powershell
.p3/Scripts/python.exe -B scripts/local_runtime_profile.py --profile pilot --mode structured --component flask --enable-manual --start
.p3/Scripts/python.exe -B scripts/local_runtime_profile.py --profile pilot --mode structured --component worker --enable-manual --start
```

El flag `--enable-manual` no cambia el comando manual-only del worker. Next se
inició con su CLI instalado, `start --hostname 127.0.0.1 --port 3000`, cwd
`frontend`, API en 5000 y telemetría de Next desactivada en ese proceso.
No se cambió el conmutador de entrada principal o el modo predeterminado de una
instalación nueva. Flask conserva su retorno HTML local.

## Evidencia de verificación

- Salud, estado, último análisis y detalle actual responden HTTP 200 en Flask y
  por Next; salud `ok`, executor `online`, `manual_enabled=true`, `llm_ready=true`.
  El último job sigue siendo `4b37542ec9f6494d9982e4591ac8529e`, succeeded,
  entregas `{}`. Snapshot y report_id coinciden entre ambas rutas.
- La condición `disabled` de `frontend/src/app/page.tsx` queda falsa con esos
  datos: admisión y LLM listos, executor online, sin queued/running. No se envió
  una petición con Idempotency-Key que pudiera encolar un trabajo.
- POST directo y por proxy **sin Idempotency-Key**: 400 `missing_idempotency_key`,
  demostrando que la ruta pasó la guarda de manual apagado y conserva la guarda
  previa a enqueue. Origen ajeno: 403 `invalid_origin`.
- El heartbeat avanza en la misma instancia; cero trabajos activos en ambas
  comprobaciones. Ambos listeners son exclusivamente `127.0.0.1`.
- Raíz Next HTTP 200 con el control de análisis en el HTML; cabecera nosniff
  presente en las lecturas. Esto no es una prueba de pulsación del botón ni de
  hidratación visual completa.
- Hashes de **59 archivos**, filas de **26 trabajos** y entregas históricas
  **11 sent / 3 unknown** iguales antes/después y tras observar. Generación,
  log, originales e históricos intactos. El heartbeat modifica SQLite, por lo
  que no se exige igualdad de bytes de toda la base.
- `.env` mantiene tamaño/mtime, comprobados sin leer sus contenidos; no se
  presenta como comparación de bytes del archivo secreto. Fuentes del runtime
  verificadas iguales durante esta operación.

Se intentó verificación visual con la habilidad Computer Use y Firefox existente.
La herramienta **detuvo Computer Use porque no soporta la aplicación de su política
de URL en ese navegador Windows**. No se siguió con acciones de interfaz ni se
pulsó el botón. No afirmar que se obtuvo captura o verificación visual del botón:
se acreditan admisión API y condiciones de UI, con esa limitación explícita.

Recibos locales excluidos de Git en `.local-state/a05-manual-20261011/`:
`acceptance.json`, `processes-before.json`, `preflight-before.json`, `backup.json`,
`started-backend.json`, `started-next.json`, `processes-effective.json`,
`http-verification.json`, `ui-verification-limit.json` y tres `invariants-*.json`.
Logs de procesos locales preservados, sin adjuntar stdout/stderr crudos.

## Uso, límites y reversión

La persona puede abrir [el dashboard local](http://127.0.0.1:3000/) y solicitar
manualmente un análisis cuando decida hacerlo. Esa pulsación utiliza la ingesta
del perfil (`dvwa-lab`) y el proveedor configurado; puede acceder a Docker y
consumir llamadas de API. **Esta activación no probó Docker, una ingesta nueva
o un análisis desde el botón**. No se ejecutan como comprobación rutinaria.

El informe vigente sigue siendo la generación
`4b37542ec9f6494d9982e4591ac8529e-4efe3d95cbb1490ab32f68eed6426b27`,
report_id `9e1cea29c9b52450d7e5293bbae469415f38eb72ed1b56c31f9a588e00ce3b99`,
con la narrativa original. **La vista previa aceptada no se publicó retroactivamente**.
Un futuro hijo `main.py` utiliza prototype-7/report-4 y la narrativa determinista;
esta operación no crea un nuevo recibo de proveedor para esa versión.

Se registra aceptación de presentación y activación manual, pero **A-05 no se
cierra como validación integral**: queda comprobar el recorrido operativo que
incluya ingesta y publicación actual, dentro del alcance real que se autorice,
y confirmar uso en navegador. Las cifras de razonamiento/latencia contradictorias
del ensayo anterior siguen documentadas; no se convierten en cero ni en deadline
cumplido. Instalación limpia Windows/Linux/Parrot, avisos residuales y publicación
GitHub siguen pendientes independientes.

Para deshabilitar manual: comprobar cero trabajos activos y verificar estas
identidades, detener exclusivamente los árboles propios de Flask/worker e iniciar
el mismo perfil sin `--enable-manual`; mantener worker manual-only y destinos
vacíos. El preflight rechaza locks activos, por lo que requiere esa parada
controlada antes del arranque. No modificar `.env` ni restaurar SQLite/reportes
por cambiar la admisión. Next puede conservarse.

Para volver al estado exacto anterior a esta operación, detener también Next,
tras verificar que sigue siendo el servicio propio: todos estaban detenidos al
inicio. Si hay actividad posterior iniciada por el usuario, reevaluar antes de
detener o restaurar. No hubo jobs, LLM, Docker, envíos, commit, push o publicación
nuevos durante esta activación; respaldos, logs e informes se conservan.
