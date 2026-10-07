# Evaluación ampliada A-05 — 07/10/2026

Estado: lote real terminado, siete casos cumplieron expectativas de familias y
publicaron artefactos verificados. **No es aceptación de activación:** la revisión
encontró mala narrativa en el caso normal y latencia elevada; se corrigió el
resumen sin hallazgos de forma determinista y se conserva el límite observado.

El usuario autorizó los siete casos adicionales al mixto, con máximo total de
42 llamadas lógicas. Router configurado openrouter/openrouter/free, límite 8192,
observed-access-2 y structured-prototype-4. Una invocación por caso, secuencial;
sin repetir casos fallidos, notificaciones, Docker, pipeline o main.py.
Cada invocación conserva sus límites de seis llamadas y 600 s externos. No se
modifica .env ni el modo legacy. Las llamadas HTTP internas no se contabilizan
como llamadas lógicas; los modelos elegidos por el router pueden variar.

| Caso | Expectativa de la fixture | Resultado | Llamadas | Segundos |
| --- | --- | --- | --- | --- |
| mixed (referencia previa, fuera del presupuesto nuevo) | Cinco familias y ninguna sobre /index.html | Pasó | 4 | 81,000 |
| normal | Cero hallazgos en cuatro solicitudes sin criterios observados | Pasó familias; narrativa original insuficiente | 4 | 475,829 |
| missing_body | Cero hallazgos inferidos desde cuerpos POST ausentes | Pasó | 3 | 46,312 |
| encoded | SQLi, XSS, traversal y comandos codificados | Pasó | 3 | 35,719 |
| login_window | Cinco POST /login dentro de 60 s: indicador de frecuencia | Pasó | 3 | 59,953 |
| login_spread | Cinco POST separados por dos minutos: sin ráfaga | Pasó | 3 | 18,562 |
| timezone_split | Fechas con zonas distintas sin ventana de cinco solicitudes | Pasó | 4 | 30,843 |
| incomplete | Sin atribución de IP/fecha; other incierto es opcional | Pasó, sin hallazgos | 3 | 31,953 |

Las expectativas y métricas son de familias/soporte observable. No demuestran
ausencia de ataques desconocidos, explotación, autenticación fallida ni seguridad
de la aplicación. Un caso sin familias esperadas deja precision/recall null,
sin declarar porcentajes ficticios. status=succeeded acredita ejecución y
publicación; el veredicto también revisa pattern_expectations_met y el artefacto.

## Evidencia disponible

- mixed: `.local-state/a05-evaluation/20261007T102336191604Z/evaluation.json`.
- normal: `.local-state/a05-evaluation/20261007T103027780944Z/evaluation.json`.
- missing_body: `.local-state/a05-evaluation/20261007T103928012803Z/evaluation.json`.
- encoded: `.local-state/a05-evaluation/20261007T104018316394Z/evaluation.json`.
- login_window: `.local-state/a05-evaluation/20261007T104057987827Z/evaluation.json`.
- login_spread: `.local-state/a05-evaluation/20261007T104201934055Z/evaluation.json`.
- timezone_split: `.local-state/a05-evaluation/20261007T104224439687Z/evaluation.json`.
- incomplete: `.local-state/a05-evaluation/20261007T104259131884Z/evaluation.json`.
- Consolidación: `.local-state/a05-evaluation/batch-quality-20261007.json`.

Se verificaron puntero/manifiesto, JSON/Markdown y hashes de los siete originales,
además de validar referencias/clasificación con la fixture etiquetada de cada
caso. Se gastaron **23 de 42 llamadas lógicas**; las 19 restantes no autorizan
repetir casos automáticamente ni ejecutar otro lote. Los siete suman 699,171 s
de ejecución (sin inicialización), 56061 tokens de entrada, 40246 de salida,
96307 totales y 37867 de razonamiento informado. Se preservan advertencias de
razonamiento superior a salida; no sumarlo como consumo adicional ni deducir
coste facturado. La prueba mixta previa no está en esos totales.

La latencia del caso normal fue casi ocho minutos. La configuración del SDK
incluye timeout=60, pero no fue una cota global de toda la ejecución; el límite
externo de 600 s sigue siendo necesario. La latencia y los reintentos deben
considerarse en la aceptación, sin prometer respuesta rápida por un solo caso.
El razonamiento informado puede exceder los tokens de salida; usage_warnings
conserva esas incoherencias sin normalizarlas. Los tokens no acreditan facturación.

El ensayo mixto de referencia corrigió una referencia inválida mediante la
guarda; normal requirió un reintento de narrativa y timezone_split uno de
detección por invalid_json. Las guardas no se relajan y no se publica una salida
rechazada. Encoded narra patrones potenciales que requieren investigación;
login_window especifica que HTTP 200 no confirma resultado de autenticación.
El lote no demuestra calidad en todos los logs, idiomas o modelos del router.

## Corrección posterior de informes sin hallazgos

El resumen original normal era la cadena «1»: válido sintácticamente, inútil
como explicación. Missing_body copiaba detalles internos de configuración y
reglas; incomplete no explicaba adecuadamente la petición no interpretable.
La calidad de esos textos no queda aprobada por los porcentajes de familias.

El formato `structured-report-2` valida primero los tres contratos. Cuando no
hay hallazgos, genera el resumen desde Python: líneas seleccionadas/omitidas,
registros no interpretables y advertencia de que no certifica tráfico benigno
ni seguridad global. Mantiene recomendaciones vacías y narrative_source=python_scope.
Cuando hay hallazgos, sigue usando narrativa LLM con semántica pendiente.
No repara JSON inválido ni omite guardas; los informes históricos no cambian.
El modo legacy y la API Markdown continúan compatibles.

Se publicaron revisiones **offline** de los cinco casos sin hallazgos en
`scope-review-20261007/` dentro de cada carpeta de ejecución. Sus hashes y
conteos cero se verificaron; batch-quality-20261007.json contiene las generaciones.
Los originales, incluidos el resumen «1» y los diagnósticos, permanecen intactos.
No se repitieron llamadas reales para esta corrección de formato.

Validación final: 211 pruebas Python, tres diagnósticos JS, 15 escenarios
CrewAI/LiteLLM aislados, sintaxis de 62 archivos y diff sin errores de espacios.

## Decisión pendiente

El lote satisface las expectativas técnicas de estos casos y verifica la
corrección del falso positivo. A-05 continúa abierta para aceptar calidad,
latencia y consumo, y decidir la activación reversible por separado. La latencia
del caso normal sugiere revisar llamadas innecesarias en resultados vacíos;
Se implementó posteriormente la [optimización de etapas sin candidatos](OPTIMIZACION_A05_SIN_HALLAZGOS.md)
y se verificó offline. Una nueva muestra normal autorizada midió 24,000 s y
dos llamadas de detección, con las etapas restantes locales y guardas válidas.
La entrada coincide, pero el router eligió otros modelos; no se acredita p95.
No se altera
la latencia original de este lote ni se oculta la variabilidad del router.
No se comparó el motor legacy con llamadas reales bajo los mismos casos ni se
acredita mejora estadística de p95 a partir de una ejecución por caso. Conservar
Flask, informes previos y límites históricos del piloto. No se retiró legacy,
no se migró .venv y no se modificó la excepción de braces de desarrollo.
