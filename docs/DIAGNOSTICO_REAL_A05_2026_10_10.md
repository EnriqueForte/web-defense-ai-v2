# A-05 — Diagnóstico real autorizado, 10/10/2026

Seguimiento: la [corrección de la detección vacía](CORRECCION_OMISION_A05_2026_10_10.md)
ya está implementada y aprobada offline. No se repitió este job ni se reescribieron
sus resultados. Falta una evaluación real con nuevo alcance autorizado.

Los diagnósticos del motor y del coordinador están **verificados en un análisis
real**. El resultado revela un pendiente de calidad: **cero hallazgos sobre una
muestra con indicadores observados por Python en 26 líneas**, mientras el análisis
anterior de las mismas 30 líneas produjo cinco grupos. A-05 continúa abierta
por esta omisión; el análisis manual de la interfaz permanece desactivado.

## Autorización y alcance ejecutado

El usuario confirmó que había revisado el dashboard y dio su aprobación. Se
registra su aceptación de la revisión operativa previa, sin atribuirle aceptación
del nuevo informe, que aún no existía. Ante la distinción entre aprobar esa
revisión y ejecutar un diagnóstico nuevo, respondió expresamente:
«Sí, ejecutar un análisis y verificar sus diagnósticos».

El alcance presentado y aceptado fue **un único análisis nuevo sobre la copia
actual del log, OpenRouter gratuito, sin notificaciones ni repeticiones automáticas**.
No se utilizó saldo de evaluaciones anteriores. No se encolaron otros trabajos.

Se mantuvo la copia de 112 líneas del 1–2 de octubre, con hash de entrada
`ffddfade5cc0d2d5ffa435b1ced317353decdd3a74e48733605a1c0f83a71034`.
No se sincronizó Docker ni se inventó tráfico actual. La selección fue de
30 líneas; 82 quedaron omitidas. Los metadatos `last_ingested_at` del coordinador
marcan la validación de esa copia en esta operación, no una captura nueva.

Se detuvo solamente el árbol del worker propio tras comprobar ruta, argumentos,
fecha de creación, parentesco, admisión manual falsa y ausencia de trabajos activos.
Flask y Next continuaron disponibles. Se creó el respaldo
`.local-backups/operational-20261010T160708765122Z`: 22 archivos y restauración
aislada verificada, con la misma cobertura limitada de aplicación descrita en
[la operación anterior](OPERACION_A05_2026_10_10.md).

La operación temporal adquirió el lock de worker, creó/reclamó un job manual
idempotente y utilizó **`pipeline.execute_job` y `pipeline.run_engine -> main.py`
reales**. Solo la sincronización se sustituyó mediante el punto de extensión
existente `sync=` por la comprobación del hash de la copia local. La publicación,
archivo histórico, guardas, etapas, wrapper y recibo del proceso son del producto.
No hubo cambio de código del producto, prompts o configuración persistente.
Esto valida la ejecución del coordinador sobre una copia existente, no la ingesta
Docker ni la solicitud desde el botón de la interfaz.

Los primeros controles se detuvieron antes de crear un trabajo o llamar al
proveedor: la comparación PowerShell de fechas perdía precisión y la herramienta
temporal no contemplaba la base legacy ausente. Ambas condiciones se corrigieron
en los helpers locales antes del único job. No se repitió un análisis fallido.

## Resultado y diagnóstico

| Dato | Valor observado |
|---|---|
| Job | `5fc8c314bed04e4eac504f3d2ae45f67` |
| Resultado coordinador y motor | succeeded |
| Tiempo coordinador | 10,719 s |
| Llamadas lógicas / intentos de transporte | 1 / 1 |
| Modelo solicitado | `openrouter/openrouter/free` |
| Modelo informado en el completado | `nvidia/nemotron-3-super-120b-a12b:free` |
| Finish reason / límite solicitado | stop / 8192 |
| Longitud de contenido final | 100 caracteres; contenido no adjuntado |
| Prompt / completado / total de tokens | 12725 / 654 / 13379 |
| Tokens de razonamiento informados | 601 |
| SDK reasoning_tokens | 0; discrepancia explícita frente a 601, no afirmar cero |
| Entregas del nuevo job | `{}` |
| Hallazgos / líneas con indicadores Python | 0 / 26 |

El checkpoint, `receipt.json` y `process.json` existen y coinciden en analysis_id.
La generación del recibo coincide con la publicación verificada:
`5fc8c314bed04e4eac504f3d2ae45f67-d8bceab7216745bba17907263eb57a5b`.
Report_id actual:
`4994e2912ae24e55e790aed15d9ee676fefd265ef79d6cc1fc3a5518755d8faa`.

Metadatos de completado capturados, cero intentos descartados y sin fallo de
escritura del checkpoint. Uso conciliado completo desde el completado, SDK aparte
y discrepancia de razonamiento preservada. Las tres etapas cumplen su contrato;
clasificación y narrativa se resolvieron localmente tras la detección vacía, como
prevé la optimización existente. No se confunden esas etapas locales con llamadas
al proveedor. No se guardan stdout/stderr, prompts o respuestas crudas en los
recibos structured. Los datos ausentes no se convierten en cero.

No se presentan estos tiempos como p95 ni como mejora de detección o disponibilidad.
El análisis anterior no adquiere métricas retroactivas por esta operación.

## Pendiente de calidad y botón manual

El JSON vacío pasó las guardas existentes, que permiten `candidates=[]`.
El informe usa narrativa de alcance generada por Python y **advierte expresamente
de posibles omisiones**, porque la preparación encontró indicadores. El resultado
no demuestra tráfico benigno ni ausencia de amenazas.

La copia y el contenido de las mismas 30 líneas seleccionadas coinciden con el
análisis del 07/10. Los evidence_id incorporan analysis_id, por lo que los objetos
completos y referencias de preparación difieren legítimamente. La comparación
excluyendo esos IDs confirma la igualdad del contenido; el histórico de cinco
grupos y su generación se conservaron íntegros. No se atribuye el resultado a
las actualizaciones de dependencias, a una clave incorrecta o a una causa concreta
del modelo sin investigación adicional.

**El botón se podrá habilitar tras revisar/corregir esta omisión y aceptar el
resultado del piloto.** Técnicamente la API ya admite el conmutador:
`scripts/local_runtime_profile.py --enable-manual`, aplicado al arranque Flask.
Habilitarlo no encola un trabajo por sí solo. Requiere un arranque operacional
controlado, con worker online y sin trabajos activos; `.env` puede permanecer
intacto. El worker puede conservar `--manual-only` y las notificaciones vacías.
No se ha activado el conmutador en esta tarea, cuyo alcance real era un job.

El siguiente trabajo pertinente para A-05 es revisar cómo tratar una detección
vacía cuando la preparación aporta indicadores, manteniendo el alcance y las
guardas. Cualquier nueva evaluación real requiere otro alcance autorizado.
No se cambian prompts o guardas ni se realizan nuevas llamadas para ocultar este
resultado. La instalación limpia Windows/Linux/Parrot y los residuales de
dependencias continúan pendientes independientes.

## Estado restaurado y conservación

Después del job se arrancó de nuevo el worker con `.p3`, pilot/structured,
`--manual-only`, admisión manual falsa y destinos de notificación vacíos.
Cadena verificada: **12448 → 30468 → 34140 → 10268**, creada a las 16:09:32 UTC;
12448 es el lanzador y 10268 el proceso efectivo. Los PID del worker de la
operación anterior dejaron de ser vigentes. Verificar siempre identidad/fecha
antes de operar. Flask 24400 y Next 1312 se conservaron.

Comprobación posterior, directa y por Next:

- Salud `ok`, worker `online`, cero queued/running y admisión manual falsa.
- Último job succeeded y entregas `{}`; informe actual y su hash coinciden con
  la generación nueva, con advertencia de omisiones en `display_markdown`.
- **25 trabajos**: 24 históricos preservados y uno nuevo; entregas históricas
  iguales (11 sent, 3 unknown), sin reclasificación.
- Hashes históricos conservados; solo cambió el puntero actual y se añadieron
  la generación, el histórico y los diagnósticos del job autorizado.
- Copia del log intacta; `.env` con tamaño/mtime intactos, sin leer ni comparar
  sus bytes. Base legacy ausente antes/después, sin crearla para esta operación.

Recibos locales excluidos de Git en `.local-state/a05-real-20261010/`:
`authorized-attempt.json`, `backup.json`, `before.json`, `outcome.json`,
`diagnostic-summary.json`, `post-check.json`, `stopped-worker.json`,
`worker-restoration-preflight.json`, `worker-restored.json` y
`restored-worker-identities.json`. Los helpers acotan la operación a un intento
persistido y no sirven como autorización reutilizable.

Diagnósticos de producto en
`.local-state/phase6-pilot/reports/analysis-diagnostics/5fc8c314bed04e4eac504f3d2ae45f67-4250793144d2446caa813b6be752af56/`.
No hubo commit, push, publicación GitHub, acceso Docker o envío de notificaciones.

Para revertir la presentación a una generación anterior, preparar una operación
explícita con locks, validación de manifiestos y preservación del nuevo histórico;
no borrar el resultado nuevo ni restaurar SQLite automáticamente. El análisis
ejecutado y su consumo no son reversibles. El worker ya quedó restaurado; no
reiniciarlo rutinariamente por esta acta.
