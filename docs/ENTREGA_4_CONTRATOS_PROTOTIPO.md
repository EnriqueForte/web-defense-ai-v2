# Entrega 4 — A-01/A-02: contratos y prototipo estructurado

Estado: A-01 y A-02 completadas en alcance aislado el 06/10/2026.
Responsable: Codex principal, sin delegación. El flujo operativo anterior
permanece activo; no se integra este prototipo en `main.py`, pipeline o API.

## A-01: evidencia, validación y resultado

`agents/evidence_contracts.py` contiene contratos deterministas de versión `1`,
sin dependencias CrewAI/Pydantic, I/O ni publicación. Se comparte un catálogo
de tipos (SQLi, XSS, traversal, comandos, fuerza bruta y otro), severidades y
estados inciertos. El prototipo Pydantic deriva sus enumeraciones del catálogo.

La evidencia tiene `analysis_id`, digest del texto de entrada, origen,
posición original e identificador derivado de análisis/digest/línea/contenido.
Conserva el texto original y extrae únicamente campos explícitos de una línea
Apache reconocible: IP válida, fecha con zona normalizada a UTC, método,
target y código HTTP válido. Si faltan o no son válidos, permanecen `null`.
No se infiere identidad atacante, cuerpo POST, datos devueltos o explotación.
Una fecha/IP extraída del log sigue siendo una observación, no confirmación
de que el cliente identificado sea el atacante real.

La muestra del prototipo conserva una cola acotada, posiciones originales,
total de líneas no vacías, omitidas y bytes seleccionados. Por defecto: 100
líneas, máximo 16 KiB por línea y 64 KiB de texto seleccionado. La entrada
está limitada a 1 MiB; las opciones tienen límites superiores de 1000 líneas,
16 KiB por línea y 256 KiB seleccionados. Los bytes declarados son del texto
crudo seleccionado, no del JSON serializado ni un cálculo de tokens/coste.
Líneas demasiado grandes o que no caben quedan omitidas, sin cortar su texto.
No se modifica la selección de `agents/log_analyst.py`; su corrección es A-03.

Cada etapa acepta solo los campos definidos y rechaza versiones/analysis_id
ajenos, JSON con claves repetidas, constantes no JSON, tamaño excesivo,
referencias inexistentes/vacías/repetidas, candidatos duplicados y tipos
inválidos. La clasificación debe cubrir exactamente una vez cada candidato.
No recibe IP/fechas del modelo ni admite estado `confirmed_success`.
Las recomendaciones deben referenciar candidatos existentes.

`assemble_result` vuelve a validar las etapas, incorpora observaciones desde
la evidencia original y calcula conteos desde la clasificación. Copia los
contenedores para impedir que cambios posteriores de payloads alteren el
resultado ya ensamblado. Registra versión de contrato, análisis, modelo
aportado explícitamente y versión de instrucciones del prototipo.

La procedencia `validated_references` indica integridad referencial, no verdad
semántica. El resultado conserva `quality=semantic_evaluation_pending`.
Un modelo puede asignar mal tipo/severidad o inventar afirmaciones en prosa
que cumplan el esquema: esto requiere evaluación A-03/A-05. No se afirma que
un esquema o instrucciones eliminen la inyección de prompts.

## Adaptación histórica independiente

`agents/legacy_report_adapter.py` lee la tabla de amenazas del Markdown
histórico, admite cabeceras con énfasis, orden diferente y pipes escapados,
y señala cabeceras/filas ambiguas, IP/fechas inválidas o severidades desconocidas.
Conserva valores reportados originales y normalizados cuando son válidos.
No ejecuta ni interpreta como instrucciones el HTML contenido en las celdas.

Los registros llevan `legacy_unverified`, sin evidence_ids fabricados ni
campos que los conviertan en observaciones verificadas. Un heading o tabla
ausentes y una fila desalineada producen estado `degraded` y avisos; no se
transforman silenciosamente en un análisis nuevo válido con cero amenazas.
Una tabla histórica vacía bien formada permanece `adapted_unverified`.

Este adaptador es nuevo y aislado; `dashboard.app.parsear_amenazas` sigue
intacto. Por tanto los defectos de parsing del flujo operativo no quedan
corregidos todavía. La adaptación es deliberadamente conservadora y no
cubre todas las variantes posibles de Markdown ni prueba procedencia factual
de las clasificaciones antiguas.

## A-02: tareas CrewAI reales y salidas Pydantic

`agents/structured_prototype.py` crea tres agentes y tareas secuenciales:
analista → clasificador → narrador. Las tareas definen `output_pydantic`,
contexto explícito (analista para clasificación; ambas etapas para narrativa)
y guardrails con un único reintento. Los agentes no tienen herramientas,
delegación ni acceso a shell, Docker o notificaciones. Sus instrucciones
aisladas tratan el tráfico como datos y prohíben inventar campos factuales.
No se cambian `config/prompts.py` ni los agentes/tareas operativos.

Los guardrails validan el JSON original y después construyen el objeto
Pydantic; no reparan silenciosamente JSON ni se apoyan en coerción de tipos.
Ante rechazo definitivo se detiene la secuencia. No hay escritor de reportes,
archivo de salida, integración de avisos o activación por configuración.
El caller aporta explícitamente el LLM; el único ensayo incluido utiliza
respuestas programadas, nunca un proveedor real.

CrewAI persiste resultados de tareas incluso con `memory=False`. Para aislar
esa característica se deriva un Crew con handler de resultados en memoria.
Esta adaptación usa el atributo privado `_task_output_handler` de CrewAI
1.14.2; es un límite de compatibilidad que deberá verificarse al cambiar su
versión. No constituye el diseño de persistencia final de A-04.

La factory no llama `kickoff`. `result_from_tasks` valida otra vez las tres
salidas antes de ensamblar el resultado. El prototipo es una pieza de desarrollo,
no una nueva ruta activa del producto ni un cuarto agente de revisión.

## Comprobación sin proveedores

El comando opcional para el entorno completo es:

```powershell
.p2/Scripts/python.exe -B scripts/check_structured_prototype.py
```

Se ejecutó con CrewAI 1.14.2 y Pydantic 2.11.10 reales del entorno limpio.
El LLM doble entrega `Final Answer` con JSON sintético. Se verificaron:

| Escenario | Resultado |
|---|---|
| Tres etapas válidas | Tres llamadas al doble, tres salidas Pydantic, contexto propagado y un hallazgo contado |
| Referencia ajena corregida en el reintento | Cuatro llamadas al doble; resultado válido después de un rechazo |
| Referencia ajena en ambos intentos | Dos llamadas al doble; fallo controlado y etapas posteriores sin salida |

La comprobación bloquea carga dotenv y conexiones de servicio, desactiva
tracing/telemetría y sustituye la emisión de eventos. En Windows permite
únicamente la conexión interna que implementa `socket.socketpair` para asyncio;
no permite conexiones arbitrarias a loopback o proveedores. No hay llamadas
al motor operativo. El almacenamiento de fallback del framework se dirige
a `.local-state/structured-prototype`, excluido de Git; los primeros intentos
de prueba dejaron solo artefactos sintéticos allí. La versión final del Crew
emplea el handler en memoria.

Los primeros intentos del ensayo expusieron dos detalles de integración:
el bloqueo indiscriminado de conexiones impedía el socketpair interno de
asyncio, y devolver TaskOutput desde guardrail no construía automáticamente
su salida Pydantic. Se ajustó la barrera del ensayo y se hace validación
Pydantic explícita tras la validación referencial. Los tres escenarios
finales terminaron correctamente; estos detalles no afectaron al producto.

## Validación y límites

- Suite mínima: **149 pruebas Python**, cero fallos/expected failures,
  y tres diagnósticos JavaScript aprobados.
- Sintaxis: **45 archivos**, cero errores.
- Ensayo CrewAI completo: tres escenarios aprobados sin proveedor ni publicación.
- `git diff --check`: sin errores de espacios.
- Sin cambios en `main.py`, preprocesamiento operativo, agentes originales,
  prompts operativos, OpenAPI o componentes React en esta entrega.

Las pruebas deterministas cubren identidad y muestreo, posiciones/UTC,
ausencia de cuerpo POST, campos desconocidos, referencias inventadas,
duplicados, cobertura completa de candidatos, estado de éxito no admitido,
recomendaciones ajenas, conteos comunes, mutación posterior, resultados vacíos
válidos frente a respuestas inválidas y adaptación histórica insegura/ambigua.
La prueba del catálogo cubre aceptación de enumeraciones, no calidad de
detección de cada familia. No se han medido precisión, recall, coste o
latencia de proveedores reales ni resistencia semántica ante prompt injection.

No se lee `.env` ni datos operativos en los ensayos, ni se ejecuta `main.py`,
pipeline real, Docker o transportes. No hay actualización de dependencias,
intérprete operativo, esquema SQLite, API, UI, reportes o conmutadores.
No se repiten build/audit de frontend porque no cambian sus fuentes o paquetes.

## Compatibilidad, reversión y siguiente parte

La aplicación sigue usando el flujo previo y sus contratos. Retirar únicamente
los módulos, pruebas, comprobación y estado documental de esta entrega revierte
el prototipo sin modificar históricos, datos, configuración o credenciales.
No se hizo commit ni publicación. El cierre local de fase 7 sigue vigente.

La siguiente parte es A-03/A-04: selección y agregados verificables, criterios
atribuibles a evidencia, composición determinista de tabla/conteos y publicación
coherente conservando el último resultado válido. La activación del motor nuevo
y comparación real con proveedores corresponden a A-05. Hasta entonces,
R-05/R-06/R-07 y demás defectos del motor operativo siguen abiertos aunque el
prototipo ya rechace los casos contractuales correspondientes.
