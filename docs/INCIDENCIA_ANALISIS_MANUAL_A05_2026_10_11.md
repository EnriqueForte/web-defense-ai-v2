# A-05 — Diagnóstico del análisis manual fallido, 11/10/2026

El segundo intento manual llegó al motor: la ingesta terminó y la detección fue
aceptada tras un reintento. Falló en **clasificación**, al no obtener una respuesta
JSON válida en ninguno de sus dos intentos. El proceso terminó con
`ValidationError` durante la conversión de salida de CrewAI/Pydantic y el
coordinador registró `analysis_failed`. No llegó a narrativa ni publicación.
El primer intento manual registrado falló antes, en ingesta.

La revisión solicitada por el usuario se realizó sobre SQLite en modo solo
lectura, los recibos existentes y el código instalado. **No se ejecutó otro
análisis, ninguna llamada al proveedor, Docker, envío o reinicio.** No se cambió
el modelo, `.env`, las guardas, el presupuesto de reintentos ni la admisión manual.

## Dos intentos distintos

Horas del 11/10/2026 en Madrid (UTC+2):

| Trabajo | Inicio → fin | Resultado | Etapa alcanzada |
|---|---|---|---|
| `b2d7ac776fd84215be43f38d7932dd94` | 18:31:27 → 18:31:28 | `failed / ingestion_failed` | Sin `last_ingested_at`; sin recibo del motor |
| `331efe77ad3c40fb8eb876f8b84bf260` | 18:35:29 → 18:38:04 | `failed / analysis_failed` | Ingesta registrada 18:35:29; clasificación fallida |

La captura `dvwa-lab` devuelve fallo ante error al invocar Docker, timeout,
retorno no exitoso o ausencia de líneas Apache reconocidas. El primer registro
no distingue estas condiciones: **su causa concreta no queda acreditada**.
La UI puede mostrar una copia anterior del log aunque una nueva captura falle;
ver líneas en pantalla no acredita la ingesta de cada trabajo.

El segundo trabajo sí tiene `last_ingested_at` y cuatro llamadas del motor.
Por tanto, su fallo posterior no se explica por la ausencia de ingesta.

## Recibo del segundo trabajo

Duración de trabajo: 155 s según timestamps del coordinador. Recibo del motor:
147,671 s, cuatro llamadas lógicas y cuatro intentos de transporte observados,
metadatos capturados, proceso fallido, sin generación. Los cuatro completados
informaron `finish_reason=stop`; esto no acredita conformidad JSON.

| Llamada | Etapa | Modelo informado | Resultado observado |
|---|---|---|---|
| 1 | Detección | `dots-studio/dots-3-note-preview:free` | JSON/esquema válido; guarda rechaza `brute_without_shared_window` |
| 2 | Detección, reintento | `nvidia/nemotron-3-super-120b-a12b:free` | Detección aceptada |
| 3 | Clasificación | `nvidia/nemotron-3.5-content-safety:free` | JSON inválido; guarda rechaza `invalid_json` |
| 4 | Clasificación, reintento | `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free` | JSON inválido; `ValidationError` al convertir la salida del reintento |

CrewAI reexporta la salida corregida por la guarda mediante `_export_output` y
`convert_to_model`. La excepción de conversión explica la terminación de este
recorrido; no demuestra por qué el proveedor produjo una respuesta inválida.
El frame reducido `main.py/model_validate_json` pertenece a la ruta de validación
de Pydantic; no debe atribuirse por su nombre al `main.py` del proyecto.

No se registran `AuthenticationError`, timeout del proceso ni error de
transporte en este recibo. Las respuestas completas no se conservan por diseño:
no se puede afirmar rechazo de seguridad, defecto sintáctico específico o causa
basándose solo en el nombre del modelo o la longitud del contenido.

Uso informado por completados: 49.547 tokens de entrada, 12.255 de salida,
61.802 totales y 8.821 de razonamiento. SDK informa razonamiento 0 y el recibo
mantiene esa discrepancia; no se afirma cero ni se suma razonamiento al total.
Las llamadas 3 y 4 advierten `reasoning_exceeds_completion`. Los modelos variaron
entre llamadas; estos datos no acreditan una regresión causada por versiones.

## Publicación y estado preservados

- 28 trabajos: 17 `succeeded`, 11 `failed`, cero `queued/running` en la lectura.
- Los dos trabajos carecen de `report_id` y de entregas; no tienen generación
  publicada. Entregas históricas: 11 `sent`, 3 `unknown`.
- La publicación actual continúa en
  `4b37542ec9f6494d9982e4591ac8529e-4efe3d95cbb1490ab32f68eed6426b27`,
  del 10/10/2026. Hashes reales iguales al puntero y al registro anterior:
  `report.md`: `c73a0b5954fcb9a2bde9874317cc121749a36c90c1e6fc38b1a3dd797e32be48`;
  `result.json`: `208b66f27dd9738a7be644df49cf172ac350209b9cb6e888be7b56beb1fc7202`.
- La copia actual del log tiene 151 líneas; se leyó para conteo/hash sin mostrar
  su contenido. Es actividad posterior del usuario, no se restaura a la copia
  histórica de 112 líneas.
- Heartbeat registrado en la lectura. Esta revisión no ejecutó una nueva prueba
  de ingesta ni verificó recursos Docker actuales.

La UI muestra el estado y `error_code` genérico del coordinador; los detalles de
etapa están en los recibos locales. **El botón admitió y ejecutó los trabajos**;
eso no acredita un recorrido completo exitoso. Las guardas/conversión detuvieron
el resultado inválido y la publicación previa quedó intacta.

## Pendiente antes de continuar

A-05 sigue abierta: debe endurecerse y verificarse offline la salida de
clasificación y el manejo de la conversión fallida, preservando validación
estricta, tres tareas, límite de reintentos y ausencia de publicaciones inválidas.
Conviene distinguir los motivos seguros de ingesta para localizar un futuro
fallo sin exponer logs o excepciones crudas. No basta con aumentar reintentos,
tratar el fallo como cero hallazgos o repetir clics para declarar corregido el
recorrido. Cualquier evaluación nueva del agente con proveedor requiere alcance
expreso; los intentos del usuario no autorizan repeticiones del agente.

La narrativa determinista aceptada aún no se ejercitó en una nueva publicación
real: este trabajo se detuvo antes. Los pendientes independientes de dependencias,
instalación Windows/Linux/Parrot y entrega GitHub permanecen abiertos.

Evidencia local excluida de Git:
`.local-state/a05-incident-20261011/diagnostic-summary.json` y `state-readonly.json`.
Recibos originales del segundo trabajo:
`.local-state/phase6-pilot/reports/analysis-diagnostics/331efe77ad3c40fb8eb876f8b84bf260-50828df2cc5447219bac4b4eff2a54fd/`
(`checkpoint.json`, `receipt.json`, `process.json`). Se preservan sin salidas
crudas ni credenciales adjuntas. No se aplicó todavía una corrección funcional.
