# web-defense-ai V2 — Desarrollo en Codex, agentes y tareas

Revisión inicial: 26 de septiembre de 2026. Estado al 28/09/2026: fases 0–4 completadas; fase 5 implementada y verificada con dobles; preparación local de fase 6 completada, con piloto sostenido aplazado hasta disponer de laboratorio aislado. Las mejoras A-01–A-05 del motor siguen separadas y pendientes. Todo el desarrollo se realiza en Codex y VSCode permite revisar el mismo proyecto local.

## 1. Decisión y distinciones

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
| A-01 | Centralizar contratos de evidencia y resultado sin cambiar prompts | Backend / Quality | F0-02 | Validación determinista y adaptación del Markdown histórico; no atribución inventada | Pendiente, evolución separada del motor; no incluida en F2-01 |
| A-02 | Prototipo aislado de tareas CrewAI con salidas estructuradas | Backend / Quality | A-01 | Respuestas simuladas válidas/inválidas, propagación de contexto y fallo controlado | Pendiente, evolución del motor |
| A-03 | Corregir instrucciones, selección y criterios del motor | Backend / Quality | A-02 y línea base | Comparación por categoría y trazabilidad; cambios de clasificación explicados | Pendiente, evolución del motor |
| A-04 | Separar reporte narrativo, tabla y publicación | Backend / Quality | A-02 | Conteos del reporte y API coinciden; salida anterior conservada ante error | Pendiente, evolución del motor |
| A-05 | Evaluar integración real y activar por configuración | Backend + Delivery / Quality | A-03, A-04 | Comparación de calidad/coste/latencia y retorno al flujo previo ensayado | Pendiente, evolución del motor |
| F3-01 | Base visual Next.js con datos simulados | Codex | F2-01 | Consola de resumen, navegación, estados y demo adaptables; build, lint y tipos correctos; motor intacto | Completada; build Next y revisión visual en escritorio/móvil |
| F4-01 | Conectar lectura y reportes | Codex | F3-01 y API estable | Equivalencia por instantánea, filtros persistentes, renderizado seguro | Completada; integración con fixture y navegador local |
| F5-01 | Coordinación manual/periódica y publicación coherente | Codex | API estable y pruebas de concurrencia | Un ejecutor, trabajos persistentes y deduplicación | Implementada localmente; pruebas aisladas, piloto real en fase 6 |
| F6-01 | Piloto, pruebas completas y retorno | Delivery / Quality + Coordinador | F4-01, F5-01 | Se cumplen las condiciones de fase 6 del plan principal | Preparación local y pruebas sintéticas completadas; piloto sostenido e integraciones reales aplazadas |

El prototipo A-02 puede desarrollarse aislado tras A-01; no fue requisito para conectar la interfaz. No activar el nuevo flujo del motor durante el mismo cambio operativo que el nuevo frontend. La opción preferida es mantener el motor original durante el primer cambio de interfaz y evaluar A-03–A-05 después de su estabilización. La fase 4 validó el consumo y la representación segura de los datos del API en React con fixtures sintéticos.

## 7. Ejecución desde Codex: avances y próximos trabajos

| Paso | Acción | Resultado verificable |
|---|---|---|
| Preparación completada | Contexto, inventario, denominación y responsabilidades | Planes y configuración de VSCode disponibles |
| Fases 0–4 completadas | Línea base, estabilización, API y Next.js conectado | Suite aislada, contrato `/api/v1` y vistas de lectura |
| F5-01 implementada | Coordinar análisis manual y periódico | Un ejecutor, trabajos persistentes y deduplicación local |
| Pendiente externo: F6-01 | Piloto y retorno | Cuando haya laboratorio aislado: carga representativa, integración en destinos de prueba, observación de 24–48 horas y ensayo de retorno |
| F7-01 en preparación | Conmutador de entrada reversible | Implementado y probado apagado/activo/Next no disponible; revisión de lectura, teclado y contraste local; activación habitual pendiente de aceptación de fase 6 |
| Contratos del motor A-01 | Pendiente y separado de F2-01 | Evidencia y resultados validados sin cambiar prompts |
| Evolución aislada | A-02–A-04 fuera de la ruta operativa | Tres agentes mejorados y validaciones probadas con simulaciones |
| Evaluación | A-05 en laboratorio previsto | Métricas y decisión de activar o conservar el flujo anterior |

La configuración de VSCode ya está preparada; no se reserva trabajo para agentes del IDE. La evolución completa del motor A-02–A-05 mantiene una estimación orientativa de 5–9 jornadas, según evaluación e integración. A-01 y los fixtures solapan trabajo ya contemplado en fases 0 y 2; no sumar esas jornadas dos veces. Mantener separados los calendarios de migración visual y evolución del motor.

## Demostración de portfolio posterior

Tras aceptar el piloto y estabilizar la entrada principal, planificar un
laboratorio DVWA interno y aislado como demo reproducible del portfolio. Debe
usar una red de contenedores dedicada sin exposición pública, datos y tráfico
de ejemplo regenerables, botón de reinicio, destino de notificaciones simulado
por defecto y una guía de inicio/detención. La demo podrá habilitar integraciones
reales solo dentro de ese laboratorio y con destinos dedicados. No forma parte
de la fase actual ni se ha añadido Docker o infraestructura al proyecto todavía.

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

No se ha creado un cuarto agente CrewAI, instalado especialistas de VSCode ni cambiado prompts. Las fases 0–4 están cerradas; F5-01 está implementada localmente y pendiente de validación real en fase 6. La evolución A-01–A-05 sigue separada. El desarrollo continuará en Codex y VSCode permitirá revisar los mismos archivos.
