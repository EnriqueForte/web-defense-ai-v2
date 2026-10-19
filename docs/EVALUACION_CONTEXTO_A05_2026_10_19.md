# Evaluación A-05 de contexto de solicitudes — 19/10/2026

Estado: implementación y validación local completadas; publicación y CI pendientes.

La evaluación sintética añade nueve escenarios de fuerza bruta y atribución de
XSS. La matriz pasa de 13 casos/siete controles a **22 casos/ocho controles**.
Las expectativas están escritas en las fixtures; no se obtienen de las reglas
de detección. No se ha ejecutado otra llamada al proveedor ni un ensayo en DVWA.

## Escenarios añadidos

| Caso | Expectativa sobre lo visible en el access.log sintético |
| --- | --- |
| `dvwa_post_burst` | Un XSS en la línea 1 y ocho POST al formulario DVWA en 45 s, líneas 3–10; la visita, el Referer y el avatar no añaden referencias |
| `dvwa_get_visits` | Cinco visitas GET sin credenciales y un avatar no son envíos al formulario |
| `login_below_threshold` | Cuatro POST no alcanzan el umbral predeterminado de cinco |
| `login_boundary` | Cinco POST de la misma IP en exactamente 60 s sí forman una ventana |
| `login_outside_boundary` | Cinco POST cuyo intervalo es 61 s no forman esa ventana |
| `login_multi_ip` | Tres POST de una IP y dos de otra no se suman para alcanzar cinco |
| `login_multi_ip_bursts` | Dos IP con cinco POST cada una conservan dos grupos y referencias separadas |
| `timezone_equivalent` | Distintas representaciones horarias de instantes UTC cercanos conservan la misma ráfaga |
| `header_only_indicators` | SQLi/XSS e instrucciones sintéticas en Referer/User-Agent no son indicadores en el destino de la solicitud |

Los casos usan IP reservadas para documentación y nombres `.invalid`, sin claves
o tráfico de una instalación. `fixture_version=a05-fixtures-2` identifica este
conjunto. Los hashes de entrada de las nueve fixtures anteriores se conservan;
también se contrastan las métricas, checks y hashes JSON/Markdown de los 13 casos
de la revisión previa `20261015T185242433279Z`, excluyendo solo el UUID de generación.

El simulador de respuestas respeta los grupos de referencias escritos en la
fixture. Antes reunía todos los pares de una familia en un candidato; eso no
representaba dos ráfagas de distintas IP. No se altera la agrupación del motor.
El octavo control mezcla deliberadamente una referencia de otra IP y exige
`brute_without_shared_window`, conservando todos los archivos de la publicación
válida anterior. Los siete controles previos se mantienen.

## Evidencia completa en CI

El workflow de compatibilidad conserva durante 30 días el resumen `review.json`
y, para cada publicación sintética, `current.json` y los tres archivos de su
generación: `manifest.json`, `result.json` y `report.md`. La selección se limita
a `.local-state/a05-offline-review/`; no añade datos operativos o diagnósticos
del proveedor. Los artefactos anteriores solo contenían el resumen: no se les
atribuye retroactivamente esta evidencia completa.

Cada fila identifica `fixture_case`; el resumen incluye también la generación
y hashes de la publicación preservada por los ocho controles. Esto permite
contrastar los bytes remotos con sus manifiestos y con la revisión local,
además de recomputar las métricas por familia y par patrón–línea.

## Validación local

- 20 pruebas enfocadas aprobadas, incluidas siete nuevas de contexto.
- Regresión: 365 casos Python, 364 aprobados y uno exclusivo Linux omitido en
  Windows `.p4`, en 32,139 s; tres comprobaciones JavaScript aprobadas.
- Sintaxis: 97 archivos, cero errores.
- Comando reproducible: `.p4/Scripts/python.exe -B scripts/check_a05_offline.py`;
  22 casos/ocho controles aprobados, cero llamadas y conexiones de red bloqueadas.
- Revisión local `20261019T094920683390Z`, con las 23 publicaciones completas
  (22 casos y una publicación base de controles) en la carpeta ignorada
  `.local-state/a05-offline-review/`. Recibos de desarrollo en
  `.local-state/a05-context-20261019/`.

El primer intento enfocado dentro del sandbox falló al reemplazar archivos
temporales por WinError 5. La repetición autorizada fuera del aislamiento pasó;
la regresión y la revisión reproducible también se ejecutaron allí. Se conserva
la publicación atómica del producto.

## Alcance y continuación

Se verifican preparación, atribución, selección, guardas, publicación y el
evaluador con respuestas escritas. `semantic_evaluation_pending` permanece en
los resultados. El caso con instrucciones en User-Agent prueba su tratamiento
como datos por el parser y las guardas; **no prueba resistencia del LLM a prompt
injection**. Las métricas cuentan indicadores y referencias, sin probar ataques
exitosos, fallos de contraseña, precisión semántica general o costes reales.

No cambian prompts, reglas operativas, API, interfaz, pines, Compose o límites
de reintentos. El evaluador real muestra los nuevos nombres como opciones de
caso individual; no los ejecuta en lote, cambia sus límites o reutiliza permisos
de ensayos consumidos. Una prueba con proveedor requiere un alcance nuevo.

La reversión consiste en recuperar los archivos del evaluador, pruebas y
selección del artefacto CI; las generaciones y los datos operativos anteriores
siguen legibles. La VM, sus servicios, volúmenes, buzón y `.env` no se han tocado.
A-05 general, seguridad residual y entrega final conservan los pendientes del
[resumen vigente](ESTADO_FINAL_2026_10_12.md).
