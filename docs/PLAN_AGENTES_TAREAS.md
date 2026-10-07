# web-defense-ai V2 — Desarrollo en Codex, agentes y tareas

Revisión inicial: 26 de septiembre de 2026. Estado al 01/10/2026: fases 0–6 completadas; fase 6 cerrada anticipadamente con diez ciclos integrados, medición local, retorno a Flask y 14 h 11 min 46 s saludables. No se alcanzaron las 24 horas ni se generó el resumen automático; ver [FASE_6_PILOTO.md](FASE_6_PILOTO.md). El usuario aceptó esa evidencia parcial para activar localmente en fase 7 el conmutador reversible, que sigue apagado por defecto. Las mejoras A-01–A-05 del motor siguen separadas y pendientes. Todo el desarrollo se realiza en Codex y VSCode permite revisar el mismo proyecto local.

## 1. Decisión y distinciones

Estado posterior de entrega 6, 06/10/2026: integración A-05 implementada por
conmutador reversible, 179 pruebas y seis escenarios CrewAI aislados aprobados.
El primer análisis real falló por autenticación; tras corregir el adaptador,
la repetición autorizada falló con ValueError (dos llamadas, 50,031 s), sin informe.
A-05 sigue abierta por evaluación/aceptación; modo operativo `legacy`.
[Registro y retorno](ENTREGA_6_INTEGRACION_EVALUACION.md).
Diagnóstico por etapa añadido después: 186 pruebas y nueve escenarios CrewAI
offline aprobados. Falta usarlo en un nuevo intento real autorizado para precisar
el ValueError; no inferir la causa a partir de las reproducciones sintéticas.
Intento real posterior con ese diagnóstico: respuesta vacía en detección,
una llamada/35,516 s, ValueError en agent_utils.py:417, sin publicación.
Falta precisar el origen del contenido vacío; A-05 sigue abierta.
Captura de finish_reason/modelo/tokens preparada después sin llamadas reales:
192 pruebas y 11 escenarios SDK offline aprobados. Pendiente prueba autorizada
con esos metadatos; no se cambia el límite ni el proveedor sin evidencia.
Intento posterior: corte `length` al límite de 2048 sin texto final; se preparó
ampliación a 8192 solo en el evaluador. Pendiente ejecución autorizada con el
ajuste; no se activó el motor ni se cerró A-05.
La repetición con 8192 obtuvo JSON, rechazado por IDs inválidos/duplicados,
y el reintento terminó por límite sin texto. Restricciones de ID alineadas
en esquema/instrucciones, revisión structured-prototype-3 y 13 escenarios
offline aprobados. Pendiente evaluar esa corrección; modo operativo legacy.
Ensayo real posterior exitoso: cuatro llamadas/57,625 s, publicación aislada
verificada. Cinco familias esperadas y un falso positivo sobre /index.html;
resumen de razonamiento del SDK discrepante. Calidad, métricas, representatividad
y aceptación siguen pendientes; no activar por una sola fixture exitosa.
Seguimiento posterior: falso positivo bloqueado por política observed-access-2,
incertidumbre preservada y uso conciliado con metadatos/SDK separados. 203 pruebas
y 15 escenarios SDK aislados aprobados, sin llamadas nuevas. Pendiente evaluar
structured-prototype-4 con el proveedor y completar aceptación representativa.
Verificación real del 07/10/2026 de esos cambios: éxito sin candidato normal,
cuatro llamadas/81 s, tokens conciliados. Ocho casos etiquetados preparados y
208 pruebas aprobadas; alcance de la ampliación preguntado al usuario.
El usuario autorizó los siete casos (máximo42); pasaron expectativas de familias
con 23 llamadas. Narrativa normal «1» y latencia475,829 s requieren revisión;
formato sin hallazgos corregido a Python y verificado offline, originales intactos.
211 pruebas y 15 escenarios offline aprobados. [Resultado del lote](EVALUACION_AMPLIADA_A05_2026_10_07.md).
Optimización posterior structured-prototype-5: tareas finales locales con detección
vacía validada, una llamada en el escenario SDK simulado. 212 pruebas y 17
escenarios offline aprobados; medición real/aceptación pendientes.
[Cambio y límites](OPTIMIZACION_A05_SIN_HALLAZGOS.md).
Medición posterior autorizada: normal pasó en 24 s/dos llamadas de detección,
clasificación/narrativa locales y guardas/hashes correctos. Límites 8192/60
alineados en main structured y evaluador; constructor SDK verificado offline.
Aceptación y activación siguen pendientes; comparación no acredita un p95.
Preparación operativa posterior: perfil piloto/.p2 común, preflight pasó sin
procesos nuevos, arranque explícito y manual/notificaciones desactivados.
223 pruebas en ambos entornos y 17 escenarios offline aprobados.
[Activación y retorno](ACTIVACION_LOCAL_A05.md): aceptación y arranque completados
después; worker online, cuatro rutas API HTTP 200, sin nuevos jobs. Salud
unavailable por ausencia del primer informe structured; observación y prueba
real del coordinador pendientes.
El primer job del coordinador se autorizó y completó después: succeeded en
157 s, publicación/histórico/API válidos y salud ok, manual y notificaciones
apagados. [Registro y límites](PRIMER_ANALISIS_COORDINADOR_A05.md).
Quedan observación operativa y aceptación final; A-05 no se cierra por un job.
Estabilización posterior R-14/R-18: refresco por identidad de publicación,
lecturas validadas/acotadas y sondeos sin solapamiento por canal implementados;
14 grupos UI, tipos/lint y contratos reales aprobados, sin nuevas llamadas LLM.
[Registro de lecturas y límites](ROBUSTEZ_LECTURAS_2026_10_07.md).
Objetivo de cierre aclarado: código distribuible por GitHub para instalaciones
propias. [Endurecimiento y pendientes de distribución](ENDURECIMIENTO_DISTRIBUCION_2026_10_07.md)
implementa hosts/cuerpo/errores locales y defaults/exclusiones seguros; 232 Python
aprobados. Clonación limpia final, diagnóstico y publicación no se declaran hechos.

Estado posterior de entrega 5, 06/10/2026: A-01–A-04 completadas como
componentes aislados, con reglas/preparación, reportes deterministas y
publicación generacional. [Registro de A-03/A-04](ENTREGA_5_PREPARACION_PUBLICACION.md).
El flujo operativo sigue intacto; A-05 pendiente de evaluación e integración.

Estado posterior de entrega 4, 06/10/2026: A-01/A-02 completadas solo en
alcance aislado. El flujo operativo no cambia. Registro en
[Contratos y prototipo](ENTREGA_4_CONTRATOS_PROTOTIPO.md); siguientes A-03–A-05.
Los estados de entregas anteriores de esta sección son históricos.

Estado actualizado al 06/10/2026: F7-01 cerrada en alcance local reversible,
con confirmación del usuario de las cuatro vistas, retorno ensayado y respaldo
verificado. Se conserva Flask. No se completaron siete días sugeridos ni
monitorización continua; [evidencia y límites](ENTREGA_3_OPERACION_CIERRE_LOCAL.md).
A-01–A-05, transición del entorno operativo y aviso braces siguen pendientes.
Los estados anteriores fechados se conservan como seguimiento histórico.

Seguimiento del 06/10/2026: el rediseño SOC UI 1–8 y el zoom real al 200 %
están cerrados según su acta. Se completó la entrega 1 de seguridad y línea base
de [la revisión integral](REVISION_INTEGRAL_2026_10_06.md); cambios y aceptación
en [su registro](ENTREGA_1_SEGURIDAD_LINEA_BASE.md). F7-01 y A-01–A-05 siguen
pendientes de su propia evidencia y alcance. Los resultados históricos de las
tablas siguientes se conservan con sus fechas.

La entrega 2 también tiene implementación y verificaciones completadas:
[dependencias y ejecución reproducible](ENTREGA_2_DEPENDENCIAS_EJECUCION.md).
Conserva la excepción de braces sin parche publicado y las cuatro diferencias
de la `.venv` operativa. No activa nuevas fases ni cierra la observación F7-01.

Las fases 0–4 se completaron en Codex sin crear subagentes de desarrollo. Véanse
[línea base](FASE_0_LINEA_BASE.md), [API de lectura](FASE_2_API_LECTURA.md) y
[base visual](FASE_3_BASE_VISUAL.md). La [fase 4](FASE_4_LECTURA_CONECTADA.md)
conectó Next.js con la API Flask en modo lectura.

Realizar todo el desarrollo, las pruebas, la documentación y la coordinación desde Codex sobre este repositorio. VSCode se utilizará de forma continua para abrir y revisar esos mismos archivos mientras avanza el desarrollo. La aplicación se visualizará ejecutándola y abriendo su dirección local en un navegador; abrir el código en un IDE no arranca la aplicación.

Mantener los tres agentes CrewAI del producto, reforzar sus tareas y añadir validaciones deterministas. Para organizar la migración se proponen cuatro responsabilidades especializadas coordinadas desde este chat. No hace falta crear agentes en VSCode ni aumentar ahora el número de llamadas LLM de cada análisis.

Hay tres conceptos diferentes:

| Concepto | Qué hace | Dónde se configura |
|---|---|---|
| Agente y `Task` de CrewAI | Analizan datos del laboratorio en tiempo de ejecución | Código Python del producto |
| Asistente de desarrollo en Codex | Implementa, revisa y prueba los cambios solicitados | Este chat, contexto del repositorio y delegación explícitamente solicitada cuando proceda |
| Tarea del IDE | Ejecuta un comando local conocido | `.vscode/tasks.json`; no equivale a una tarea CrewAI ni a un ticket |

El backlog de este documento asigna responsabilidades de desarrollo; no arranca agentes, no programa ejecuciones y no crea tareas remotas.

## 2. Seguimiento continuo en VSCode

El comando `code` está disponible en el entorno local. La estructura preparada permite abrir la misma carpeta que modifica Codex, sin exportaciones ni copias. La guía de uso está en `docs/GUIA_VSCODE.md`.

| Archivo | Función | Estado |
|---|---|---|
| `web-defense-ai V2.code-workspace` | Nombre oficial y raíz compartida | Preparado |
| `AGENTS.md` | Contexto y reglas del desarrollo en Codex | Actualizado |
| `.vscode/settings.json` | Intérprete, UTF-8, formato manual y exclusiones | Actualizado |
| `.vscode/extensions.json` | Extensiones recomendadas | Preparado; no implica instalación |
| `.vscode/tasks.json` y `run-frontend.ps1` | Sintaxis, dashboards locales y verificaciones del frontend | Preparados; sin arranque automático |
| `.vscode/launch.json` | Dashboard, motor y pipeline separados | Actualizado |
| `scripts/check_syntax.py` | Comprobación estática sin ejecutar la aplicación | Preparado |

No se necesitan agentes de desarrollo dentro del IDE. Se retiraron los archivos de configuración del IDE anterior creados durante esta planificación. Abrir el workspace, seleccionar el intérprete y consultar Control de código fuente para seguir los cambios. Evitar editar simultáneamente un archivo que Codex está modificando.

La visualización web se hace en el navegador con los servidores locales activos. La tarea Flask usa los archivos locales disponibles; la tarea conjunta abre también la interfaz Next.js de lectura. Las tareas del IDE no ejecutan análisis por sí mismas. VSCode no condiciona el inicio de las fases en Codex.

## 3. Auditoría inicial de agentes y tareas del producto

La tabla de hallazgos siguiente conserva la evaluación original del 26/09/2026. Desde la fase 2 el reporter ya no publica el archivo final por su cuenta: `main.py` lo publica de forma atómica. La línea base añadió fixtures de tráfico y pruebas aisladas, pero la calidad de las salidas LLM aún no se ha evaluado en una integración real.

Se revisaron las construcciones `Agent`, `Task` y `Crew` mediante inspección del código y AST, sin ejecutar el motor. CrewAI instalado y declarado: 1.14.2. Los tres agentes usan `allow_delegation=False`, `max_iter=2` y el LLM recibido del orquestador. El Crew es secuencial.

| Agente real | Definición / tarea | Entrada y dependencia | Salida observada al inicio | Evaluación inicial |
|---|---|---|---|---|
| Analista de logs | `main.py`, `crear_agentes()` / `crear_tareas()` | Texto ya seleccionado por `preparar_log_para_agente()` | Lista textual de líneas, tipo e indicador | Mantener; falta identidad estable de evidencia y salida validada |
| Detective de amenazas | `agents/threat_detector.py` | `context=[tarea_analisis]` | Tabla Markdown de cinco columnas | Mantener; alinear categorías, incertidumbre y criterios con evidencia |
| Generador de reportes | `agents/report_generator.py` | `context=[tarea_analisis, tarea_clasificacion]` | Markdown ejecutivo escrito a un archivo | Mantener; evitar que reformule hechos o recuentos y separar publicación de generación |

`agents/log_analyst.py` contiene funciones de lectura, filtrado y fuerza bruta; no define el agente CrewAI que su nombre podría sugerir. `pipeline.py` y las notificaciones son automatizaciones Python, tampoco agentes. Conviene aclarar esta organización antes de añadir archivos.

### Desajustes de responsabilidades

| Hallazgo | Evidencia y efecto | Cambio propuesto |
|---|---|---|
| Selección insuficiente para inferir frecuencia | Se leen 100 líneas y se entregan como máximo cinco de fuerza bruta; el resultado de su detector solo llega como booleano a las estadísticas, no como contexto estructurado al LLM | Calcular conteos, ventana y referencias en Python y entregarlos junto a la muestra; indicar expresamente qué líneas no se enviaron |
| Catálogo de ataques inconsistente | La tarea del detective enumera SQLi, XSS, traversal, fuerza bruta y otro; Command Injection aparece en el prompt pero no en esa lista | Catálogo compartido de tipos y severidades, con validación al terminar la tarea |
| Confirmaciones sin evidencia suficiente | Los prompts equiparan rutas de ejecución o respuestas HTTP con ataques y pueden sugerir éxito | Separar patrón observado, intento probable y éxito confirmado; mantener hallazgos inciertos para investigación |
| Cuerpo POST no garantizado | El prompt solicita razonar sobre comandos del cuerpo; no se encontró configuración que asegure su captura en access.log | No inventar payloads ausentes; modelar qué campos y fuentes estaban disponibles |
| Salida solo textual | Ninguna de las tres tareas configura `output_pydantic`, `output_json` ni validadores de salida | Contratos de datos versionados y validación determinista con errores explícitos |
| Informe como fuente de hechos | El reporter puede reformular clasificación y su tabla se vuelve a parsear para calcular el dashboard | Mantener clasificación validada como fuente y renderizar su tabla de forma determinista |
| Dos responsables del archivo | `output_file` del reporter y guardado final en `main.py` escriben el reporte actual | Artefactos por ejecución; un servicio publica la instantánea al terminar |
| Entrada no confiable mezclada con instrucciones | El log se interpola directamente en la descripción de tarea | Separar instrucciones y datos, advertir que no se obedecen instrucciones del log y comprobar integridad de evidencias al salir |
| Calidad no evaluada | No hay dataset de referencia ni pruebas de tareas | Fixture por familia de ataque, tráfico normal, incertidumbre y entradas malformadas; medir regresiones |
| Fallos sin estado de ejecución robusto | `max_iter=2` no garantiza timeout global, éxito ni reporte válido; fallback del modelo ocurre al construir el objeto | Presupuesto de duración/coste, error por etapa y reintentos limitados antes de publicar |

La protección mediante prompts es complementaria: no elimina por sí sola la inyección de instrucciones. Mantener a los agentes sin herramientas de shell, Docker o notificación y validar referencias y salida en código reduce el impacto de una respuesta desviada.

## 4. Agentes necesarios y trabajo que debe resolver Python

**Primera decisión: conservar tres agentes de producto.** No crear agentes LLM de sincronización, validación de esquema, guardado o envío de avisos: son operaciones deterministas que requieren resultados previsibles.

| Etapa propuesta | Responsable | Salida / condición |
|---|---|---|
| P1. Ingestar | Servicio Python | Instantánea identificada, origen, fecha y estado de lectura |
| P2. Preparar evidencia | Servicio Python | Líneas con ID, datos normalizados y agregados de frecuencia; rango y muestreo explícitos |
| A1. Detectar indicadores | Analista existente | Candidatos con referencias a evidencia y motivo; no clasificar hechos ausentes |
| V1. Validar candidatos | Validador Python | Referencias existentes, campos válidos, límites de tamaño y duplicados |
| A2. Clasificar | Detective existente | Tipo, severidad, estado y justificación trazables para cada candidato |
| V2. Validar clasificación | Validador Python | Enumeraciones correctas, integridad de IDs y ausencia de datos inventados; registrar decisiones incompatibles |
| A3. Explicar y recomendar | Reporter existente | Resumen y recomendaciones basados en resultados validados |
| V3. Componer informe | Renderizador/validador Python | Tabla y conteos calculados desde la clasificación; narrativa comprobada hasta donde sea verificable |
| P3. Publicar | Servicio de trabajos | JSON versionado y Markdown compatibles publicados de forma coherente |
| P4. Notificar | Servicio de alertas | Política compartida y registro de entrega por ejecución/destino |

El esquema valida forma y referencias; no demuestra por sí solo que una interpretación de seguridad sea verdadera. La narrativa del reporter requiere evaluación semántica y no puede convertirse automáticamente en una orden de remediación.

Un cuarto agente de revisión o triage solo se consideraría después de disponer de evaluación: activación por ambigüedad concreta, sin herramientas de actuación, con presupuesto y mejora demostrable frente a los tres agentes. No se incluye en el alcance inicial ni como requisito de la interfaz.

### Contratos mínimos de tareas

- Evidencia: `analysis_id`, `evidence_id`, origen, posición o referencia verificable, fecha opcional, IP opcional, método/ruta/código si existen y alcance del muestreo.
- Candidato: identificador, lista de `evidence_id`, patrón y razonamiento breve. Rechazar referencias inexistentes.
- Clasificación: identificador de candidato, tipo canónico, severidad, estado y explicación. Separar la ausencia de evidencia de un falso positivo demostrado.
- Informe: identificación de análisis, resumen, recomendaciones vinculadas a hallazgos y campos estructurados validados. El código construye tabla y métricas.

Reintentos finitos y observables; después del límite, marcar la etapa fallida o degradada y conservar el último reporte válido. No completar silenciosamente la estructura con IPs, tiempos o severidades inventados. Registrar versión de prompt, modelo efectivo y esquema para comparar resultados.

Se comprobó en el código de CrewAI instalado la existencia de `output_pydantic`, `output_json` y `guardrail`. Su integración debe probarse con la versión 1.14.2 y el proveedor elegido; no requiere actualizar CrewAI para empezar. La documentación pública consultada apunta a una versión posterior y sirve como referencia conceptual, no como prueba de compatibilidad. [Tareas de CrewAI](https://docs.crewai.com/en/concepts/tasks).

## 5. Organización del desarrollo en Codex

Este chat de Codex mantiene decisiones, implementación, dependencias y aceptación. Los cuatro perfiles siguientes describen responsabilidades, no agentes ya creados ni procesos permanentes. Codex puede atenderlas secuencialmente; una eventual delegación se realizará aquí cuando se solicite expresamente y aporte valor.

| Perfil propuesto | Responsabilidades | Entrega y límites |
|---|---|---|
| Coordinador, este chat de Codex | Elegir tarea lista, implementar o asignar trabajo autorizado, resolver dependencias, integrar cambios y actualizar backlog | Entrega integrada con validación y reversión; no sustituye pruebas por informes de agentes |
| `backend-contracts` | Flask, modelos, parsing, coordinación de trabajos y compatibilidad; también contratos CrewAI | Cambios Python y pruebas de contrato; no cambiar prompts sin tarea dedicada |
| `frontend-soc` | Next.js, componentes, accesibilidad, filtros y visualización | UI y pruebas de interacción; no inventar campos ni operaciones del backend |
| `quality-security` | Revisión de diffs, riesgos XSS, evidencias, regresión y ensayos de fallos | Hallazgos y pruebas reproducibles; distinguir revisión de implementación y preservar datos operativos |
| `delivery-ops` | Configuración de ejecución, instalación limpia, observabilidad, respaldo y retorno | Procedimiento reproducible y validado; sin publicar servicios ni activar notificaciones por defecto |

No se crearán agentes de desarrollo dentro del IDE. El trabajo no depende de funciones de IA del IDE. Si se delega una tarea desde Codex, el encargo debe incluir objetivo, archivos permitidos, versión del contrato, criterios de aceptación y exclusiones, sin asumir que el especialista conoce todo el contexto.

Por defecto, secuenciar las ediciones. Solo paralelizar después de fijar contratos y cuando los archivos no se solapen. Si se necesitan ediciones concurrentes sobre el mismo ámbito, aislarlas en ramas/espacios de trabajo y revisar su integración. Ningún agente cierra una tarea únicamente por su propia declaración de éxito.

## 6. Backlog previo y asignación concreta

Estados del backlog: **preparado** significa archivo creado; **pendiente** requiere ejecución futura; **bloqueado por dependencia** describe orden técnico, no una solicitud automática de permiso.

| ID | Trabajo | Responsable / revisor | Dependencia | Aceptación | Estado |
|---|---|---|---|---|---|
| C-01 | Espacio de trabajo y contexto de consulta en VSCode | Codex | Ninguna | Workspace resuelve la raíz; referencias y formato correctos | Preparado |
| C-02 | Verificar IDE al utilizarlo para consulta | Delivery / Quality | C-01 | Archivos y cambios visibles; no arranque automático del motor | Opcional; no bloquea desarrollo |
| C-03 | Crear especialistas en VSCode | — | — | No aplica al flujo aclarado por el usuario | Retirado del alcance |
| C-04 | Atajos de sintaxis, dashboard y depuración del IDE | Codex | Intérprete y extensiones locales | Configuración válida y comandos existentes; sin autoarranque | Preparado; interacción gráfica pendiente |
| F0-01 | Convertir fallos previos en fixtures y pruebas | Codex | Repositorio y entorno local disponibles | Casos fallidos reproducibles sin Docker, IA ni notificaciones; cero pruebas no cuenta como éxito | Completada; 18 casos Python y 3 diagnósticos JS, 11 fallos conocidos |
| F0-02 | Dataset de referencia del motor y límites observables | Codex | Repositorio y entorno local disponibles | Casos normales, cinco ataques, evidencias ausentes y selección truncada etiquetados | Completada; evaluación LLM real fuera de alcance |
| F1-01 | Corregir fallos bloqueantes de interfaz anterior | Codex | F0-01 | Pruebas correspondientes aprobadas; retorno usable | Completada; 26 casos Python y 3 comprobaciones JS aprobados |
| F2-01 | Añadir API versionada de lectura, especificación OpenAPI y capturas estables | Codex | F1-01 | Contrato legado intacto; filtros/paginación/IDs seguros; escritores atómicos | Completada; 39 casos Python y 3 comprobaciones JS aprobados |
| A-01 | Centralizar contratos de evidencia y resultado sin cambiar prompts | Backend / Quality | F0-02 | Validación determinista y adaptación del Markdown histórico; no atribución inventada | Completada aisladamente el 06/10/2026; no integrada en motor/API |
| A-02 | Prototipo aislado de tareas CrewAI con salidas estructuradas | Backend / Quality | A-01 | Respuestas simuladas válidas/inválidas, propagación de contexto y fallo controlado | Completada el 06/10/2026; CrewAI real con doble LLM, tres escenarios; sin activar |
| A-03 | Corregir instrucciones, selección y criterios del motor | Backend / Quality | A-02 y línea base | Comparación por categoría y trazabilidad; cambios de clasificación explicados | Completada aisladamente el 06/10; firmas, agregados UTC y comparación sintética; no activada |
| A-04 | Separar reporte narrativo, tabla y publicación | Backend / Quality | A-02 | Conteos del reporte y API coinciden; salida anterior conservada ante error | Completada aisladamente el 06/10; tabla/JSON/API en fixture y generaciones con puntero atómico |
| A-05 | Evaluar integración real y activar por configuración | Backend + Delivery / Quality | A-03, A-04 | Comparación de calidad/coste/latencia y retorno al flujo previo ensayado | Siete casos reales cumplieron familias; narrativa vacía corregida offline; aceptación/latencia/comparativa/activación pendientes |
| F3-01 | Base visual Next.js con datos simulados | Codex | F2-01 | Consola de resumen, navegación, estados y demo adaptables; build, lint y tipos correctos; motor intacto | Completada; build Next y revisión visual en escritorio/móvil |
| F4-01 | Conectar lectura y reportes | Codex | F3-01 y API estable | Equivalencia por instantánea, filtros persistentes, renderizado seguro | Completada; integración con fixture y navegador local |
| F5-01 | Coordinación manual/periódica y publicación coherente | Codex | API estable y pruebas de concurrencia | Un ejecutor, trabajos persistentes y deduplicación | Completada; pruebas aisladas y diez ciclos integrados en fase 6 |
| F6-LAB-01 | Preparar laboratorio DVWA aislado y captura de logs de prueba | Codex | F5-01 | Red interna; puertos solo loopback; sin montaje del repositorio; correo en sink local; logs separados; inicio y detención documentados | Contenedores y tarea de VSCode comprobados; solicitudes SQLi capturadas y visibles en ambas dashboards |
| F6-01 | Piloto, pruebas completas y retorno | Delivery / Quality + Coordinador | F4-01, F5-01, F6-LAB-01 | Diez ciclos, medición, retorno y observación documentada | Cerrada anticipadamente el 29/09/2026; 14 h 11 min 46 s saludables, sin resumen de 24 h; tres entregas `unknown` |

El prototipo A-02 puede desarrollarse aislado tras A-01; no fue requisito para conectar la interfaz. No activar el nuevo flujo del motor durante el mismo cambio operativo que el nuevo frontend. La opción preferida es mantener el motor original durante el primer cambio de interfaz y evaluar A-03–A-05 después de su estabilización. La fase 4 validó el consumo y la representación segura de los datos del API en React con fixtures sintéticos.

## 7. Ejecución desde Codex: avances y próximos trabajos

| Paso | Acción | Resultado verificable |
|---|---|---|
| Preparación completada | Contexto, inventario, denominación y responsabilidades | Planes y configuración de VSCode disponibles |
| Fases 0–4 completadas | Línea base, estabilización, API y Next.js conectado | Suite aislada, contrato `/api/v1` y vistas de lectura |
| F5-01 completada | Coordinar análisis manual y periódico | Un ejecutor, trabajos persistentes y deduplicación local; diez ciclos integrados |
| F6-LAB-01 completada | Laboratorio DVWA aislado para pilotaje | Compose y tarea VSCode probados en loopback; diez ciclos integrados y benchmark API completados |
| F6-01 cerrada anticipadamente | Piloto y retorno | Diez ciclos, medición p95 y retorno Flask completados; siete alertas confirmadas, tres `unknown`; observación saludable de 14 h 11 min 46 s aceptada con ese límite |
| F7-01 cerrada localmente | Conmutador de entrada reversible | Cierre 06/10/2026: usuario confirma cuatro vistas sin incidencias, retorno 357,4 ms y respaldo/restauración; Flask conservado y siete días sugeridos no completados |
| Contratos del motor A-01 | Pendiente y separado de F2-01 | Evidencia y resultados validados sin cambiar prompts |
| Evolución aislada | A-02–A-04 fuera de la ruta operativa | Tres agentes mejorados y validaciones probadas con simulaciones |
| Evaluación | A-05 en laboratorio previsto | Métricas y decisión de activar o conservar el flujo anterior |

La configuración de VSCode ya está preparada; no se reserva trabajo para agentes del IDE. La evolución completa del motor A-02–A-05 mantiene una estimación orientativa de 5–9 jornadas, según evaluación e integración. A-01 y los fixtures solapan trabajo ya contemplado en fases 0 y 2; no sumar esas jornadas dos veces. Mantener separados los calendarios de migración visual y evolución del motor.

## Demostración de portfolio posterior

Tras aceptar el piloto y estabilizar la entrada principal, ampliar el
laboratorio DVWA aislado preparado en F6 como demo reproducible del portfolio. Debe
usar una red de contenedores dedicada sin exposición pública, datos y tráfico
de ejemplo regenerables, botón de reinicio, destino de notificaciones simulado
por defecto y una guía de inicio/detención. La demo podrá habilitar integraciones
reales solo dentro de ese laboratorio y con destinos dedicados. La ampliación
de portfolio queda para después de la aceptación del piloto; F6 solo añade la
base aislada y utilidades locales de captura.

### Ficha obligatoria de trabajo

Cada tarea tendrá ID, objetivo, propietario, revisor, dependencias, archivos/contratos afectados, evidencia de aceptación, pruebas, límites y reversión. Al cerrarla, registrar cambios concretos, resultados de comandos y asuntos pendientes. Mantener el estado en este backlog inicialmente; no introducir un gestor externo solo para esta migración.

### Comandos actuales y ampliaciones posteriores

- Disponible: verificar sintaxis Python sin importar el motor ni generar reportes.
- Disponible: ejecutar la suite de regresión aislada con `scripts/check_baseline.py`.
- Disponible: iniciar Flask en localhost para visualización o depuración. Pendiente: modo de datos de prueba con transportes externos deshabilitados.
- Disponible: arrancar Flask y Next.js juntos desde la tarea de lectura conectada de VSCode. El ejecutor real se inicia por separado y nunca al abrir el IDE.
- Mantener ejecución real del motor y pipeline como operaciones manuales separadas, con nombres claros; no usar compuestos que los arranquen al abrir VSCode.

Las tareas usan `cwd` explícito. Las tareas Python invocan `.venv/Scripts/python.exe` mediante PowerShell, independientemente del intérprete seleccionado en el editor; las tareas Next.js resuelven Node mediante `run-frontend.ps1`. `.gitignore` permite versionar la configuración compartida y ese script; las preferencias adicionales del IDE permanecen excluidas.

## 8. Criterios de aceptación de la evolución del motor

1. Cada hallazgo referencia evidencia presente en la instantánea de entrada; IP o fecha ausentes siguen siendo desconocidas.
2. Una salida malformada no alcanza publicación ni notificaciones. Los validadores se prueban sin depender de que el LLM reproduzca un error concreto.
3. El dataset diferencia intentos, éxito no demostrado y tráfico normal. Se revisan falsos positivos y falsos negativos por familia de ataque, no solo el número de amenazas.
4. Los conteos temporales provienen de las líneas disponibles y su ventana; la muestra resumida no sustituye esos agregados.
5. Reporte, tabla y API comparten análisis y datos canónicos; las recomendaciones no alteran severidades o hechos.
6. Se registran modelo/prompt/esquema, duración, uso de tokens si está disponible y costes estimados; límites y métricas se fijan después de la línea base.
7. El cambio de flujo puede desactivarse por configuración sin borrar históricos. Los datos estructurados nuevos son aditivos y versionados.
8. Los ensayos en paralelo son comparaciones de lectura o ejecuciones aisladas: nunca dos publicadores/notificadores para el mismo ciclo.

No se ha creado un cuarto agente CrewAI, instalado especialistas de VSCode ni cambiado prompts. Las fases 0–7 están cerradas para el alcance local, con aceptación anticipada y límites expresos de observación en fases 6/7; Flask se mantiene como respaldo. La evolución A-01–A-05 permanece separada. El desarrollo continuará en Codex y VSCode permitirá revisar los mismos archivos.
