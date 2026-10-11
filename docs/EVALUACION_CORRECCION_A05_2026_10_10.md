# A-05 — Evaluación real de la corrección, 10/10/2026

Seguimiento posterior: la [corrección narrativa](NARRATIVA_VALIDADA_A05_2026_10_10.md)
está implementada y validada offline, con vista previa sobre estos hallazgos.
Este informe/recibos reales se conservan íntegros, sin nueva llamada o publicación.
Las limitaciones narrativas de abajo describen el resultado original del ensayo.

El único análisis autorizado terminó **succeeded** en **287,188 s (4 min 47 s)**
con cinco grupos: SQLi, XSS y tres ráfagas de fuerza bruta; cuatro altos y uno
medio. Las referencias cubren los 26 indicadores de la selección y coinciden
con la muestra del primer análisis del 07/10. Los diagnósticos, publicación y API
están verificados. **A-05 sigue abierta por narrativa/aceptación**: el resumen
añade un detalle sin soporte y sus recomendaciones reiteran observaciones.
El botón manual permanece desactivado.

## Alcance autorizado y operación

El usuario respondió «si autorizo» a la propuesta de un único análisis real con
OpenRouter gratuito sobre la misma copia, sin Docker, notificaciones o repetición
del trabajo. Esta autorización se utilizó en el job
`4b37542ec9f6494d9982e4591ac8529e`; no autoriza otros jobs o nuevas evaluaciones.
Se conservaron los reintentos internos acotados del motor.

El worker anterior, lanzador 12448 y árbol 30468/34140/10268, se detuvo tras
verificar ejecutables, fecha de creación, parentesco, argumentos, admisión manual
falsa y ausencia de trabajos activos. Flask y Next se conservaron. Se creó
`.local-backups/operational-20261010T205248588078Z`: **26 archivos**, restauración
aislada y hashes/integridad SQLite verificados por la herramienta operacional.
Su cobertura sigue excluyendo `.env`, volúmenes Docker y buzón Mailpit.

La operación temporal adquirió el lock de worker y ejecutó
`pipeline.execute_job -> pipeline.run_engine -> main.py` reales. El adaptador
`sync=` únicamente validó el hash de la copia existente; no hubo captura nueva.
Fuente: 112 líneas del 1–2 de octubre, hash
`ffddfade5cc0d2d5ffa435b1ced317353decdd3a74e48733605a1c0f83a71034`,
30 seleccionadas y 82 omitidas. `last_ingested_at` representa esa validación,
no ingesta Docker actual. Proveedor/candidato gratuito exclusivo y versiones
observed-access-3 / structured-prototype-6 comprobados antes del job.

La ejecución comenzó a las **22:52:48 Europe/Madrid (20:52:48 UTC)** del 10/10.
Se observaron cinco llamadas lógicas/cinco intentos de transporte y dos rechazos
de guarda corregidos por los reintentos existentes. No se creó otro trabajo.

## Diagnóstico y publicación

| Intento | Etapa | Modelo informado | Finish reason | Duración transporte | Resultado de guarda |
|---|---|---|---|---|---|
| 1 | detección | dots-studio/dots-3-note-preview:free | stop | 33,031 s | brute_without_shared_window |
| 2 | detección | nvidia/nemotron-3-super-120b-a12b:free | stop | 19,922 s | aceptada |
| 3 | clasificación | nvidia/nemotron-3.5-lightning:free | length | 154,641 s | invalid_json |
| 4 | clasificación | poolside/laguna-xs-2.1:free | stop | 3,625 s | aceptada |
| 5 | narrativa | nvidia/nemotron-3.5-lightning:free | stop | 71,891 s | aceptada contractual |

Todos solicitaron `openrouter/openrouter/free`, max_tokens=8192. Los distintos
modelos son los informados por el router; no se atribuye el resultado únicamente
a la modificación del prompt o de la guarda. En este ensayo la detección no fue
vacía: **la rama nueva de rechazo de vacío no se activó con el proveedor**. Su
rechazo y fallo conservando el puntero se acreditaron en los 20 escenarios
offline de [la corrección](CORRECCION_OMISION_A05_2026_10_10.md).

Checkpoint/receipt/process existen y coinciden en analysis_id. Motor y coordinador
succeeded; sin fallos de escritura ni intentos descartados. Los cinco completados
tienen metadatos capturados. Uso informado: **74472 prompt + 23238 completado =
97710 tokens totales**; razonamiento informado 20621. No sumar razonamiento otra
vez. El SDK indica cero en razonamiento: se conserva la discrepancia explícita.
El intento 3 informa razonamiento 8847 frente a completado 8192, con warning
`reasoning_exceeds_completion`. Disponibilidad completa de campos no certifica
la exactitud de las cifras del proveedor.

Los tiempos de etapas registrados son detección 53 s, clasificación 158,297 s y
narrativa 71,907 s, más preparación/construcción/publicación. La duración medida
del transporte supera los 60 s solicitados en dos llamadas; **no acreditar un
deadline estricto de 60 s por llamada**. La causa y el comportamiento interno
del SDK/proveedor no se atribuyen desde estos metadatos. No hubo timeout del
coordinador de 900 s en este ensayo. No se presentan los tiempos como p95 ni como
garantía para otra ejecución.

Generación nueva:
`4b37542ec9f6494d9982e4591ac8529e-4efe3d95cbb1490ab32f68eed6426b27`.
Report_id:
`9e1cea29c9b52450d7e5293bbae469415f38eb72ed1b56c31f9a588e00ce3b99`.
Manifiesto, JSON, Markdown original y detalle API coinciden en hash/identidad.
La generación previa de cero hallazgos y el primer informe de cinco grupos
permanecen íntegros; no se reescribieron para ocultar resultados anteriores.

## Revisión de contenido

La selección coincide con el primer análisis excluyendo los evidence_id propios
de cada job. Los tres patrones observados en esta selección están representados;
los cinco grupos cubren **26/26 pares indicador–evidencia seleccionados**:

- SQLi: líneas 26,28,41,43,57,58,59,61,79; alta.
- XSS: línea 111; media.
- Fuerza bruta: líneas 30–35, 51–55 y 70,81–84; tres grupos altos.

Todos tienen estado `requires_investigation`, conservando incertidumbre y sin
afirmar explotación exitosa. Las ventanas y referencias pasan las guardas
observadas; conteos/severidades son deterministas y coinciden en Flask/Next.
Esto acredita el recorrido de esta muestra seleccionada, no la cobertura de las
82 líneas omitidas o la calidad general de cualquier tráfico.

La revisión de la narrativa encontró límites concretos:

- El resumen menciona consultas `SUBSTRING`, aunque no aparece esa función ni
  sus variantes SUBSTR/MID en los targets seleccionados y referenciados para SQLi.
  OR/AND 1=1 y la etiqueta script de XSS sí tienen soporte observado.
- Las cinco entradas de recomendaciones describen los hallazgos; no aportan
  medidas de mitigación accionables.
- El texto del modelo está en inglés. No se registra conformidad del usuario
  con esta narrativa; no confundir su aprobación de la revisión previa con
  aceptación del informe recién generado.

La detección dejó de ser vacía en este ensayo, pero las guardas narrativas siguen
siendo contractuales. El siguiente pendiente A-05 es anclar el resumen a los
hechos validados y mejorar las recomendaciones antes de aceptar la salida final
o habilitar manual. No se cambiaron prompts/guardas durante esta operación ni se
hizo otra llamada para corregir retrospectivamente el informe.

## Estado después y conservación

El worker se restauró con `.p3`, pilot/structured, `--manual-only`, admisión manual
falsa y destinos vacíos. Cadena actual verificada:
**23412 → 17220 → 24240 → 26404**, creada a las 22:58:25 Madrid / 20:58:25 UTC.
23412 es el lanzador, 26404 el proceso efectivo. No usar los PID históricos sin
comprobar ruta, fecha, argumentos y parentesco. Flask 24400 y Next 1312 se
conservaron.

API directa 5000 y proxy Next 3000: salud `ok`, executor `online`, mismo snapshot
y reporte, último job succeeded, manual_enabled=false y entregas `{}`.
Cero queued/running; **26 trabajos** (25 previos intactos + uno nuevo), entregas
históricas intactas (11 sent, 3 unknown). Base legacy ausente antes/después.
Hashes históricos y copia del log intactos; `.env` con tamaño/mtime preservados,
sin leer ni comparar sus bytes. El heartbeat SQLite cambia como se espera.

Recibos locales en `.local-state/a05-guard-real-20261010/`:
`authorized-attempt.json`, `backup.json`, `before.json`, `outcome.json`,
`diagnostic-summary.json`, `post-check.json`, `narrative-review.json`,
`stopped-worker.json`, `worker-restoration-preflight.json`, `worker-restored.json`
y `restored-worker-identities.json`.

Diagnósticos de producto en
`.local-state/phase6-pilot/reports/analysis-diagnostics/4b37542ec9f6494d9982e4591ac8529e-59bd94a32c2c4d72b3bf29d7ccdd0029/`.
Los recibos no incluyen prompts/respuestas crudas o credenciales.
Sin Docker, envíos, cambio de `.env`, habilitación del botón, commit o push.

El análisis y su consumo ya realizado no son reversibles. El worker está
restaurado; no reiniciarlo rutinariamente por esta acta. Una restauración de
puntero o de datos requeriría operación específica con locks y preservación
del nuevo resultado. El botón manual requiere una operación explícita posterior
de perfil/arranque; esta autorización cubrió solo un job y ya se utilizó.
