# Entrega 5 — A-03/A-04: preparación y publicación validada

Estado: implementación aislada y verificación sintética completadas el
06/10/2026. Responsable: Codex principal, sin delegación. La aplicación
operativa sigue usando el motor y publicación anteriores; activar este
flujo y evaluar proveedores reales corresponde a A-05.

## A-03: selección y agregados trazables

`agents/evidence_preparation.py` examina un tramo acotado de la entrada y
comparte un catálogo de patrones sobre la URL. Decodifica hasta dos capas de
URL encoding para observar payloads codificados, sin afirmar que el servidor
los decodificó o ejecutó. Busca expresiones SQL, etiquetas/atributos XSS,
traversal y separadores de comandos con tokens conocidos. No busca órdenes
en campos arbitrarios del log para convertirlas en instrucciones del agente.
Los textos originales permanecen intactos en la evidencia.

La selección usa una muestra equilibrada por familias y completa con accesos
recientes, respetando máximo de líneas y bytes. Un exceso de peticiones de
autenticación no sustituye automáticamente las otras familias cuando hay
presupuesto para sus representantes. Si el presupuesto es insuficiente,
la omisión queda explícita; no se garantiza que toda familia quepa.

La función recibe configuración explícita, sin cargar `.env`:

| Parámetro | Predeterminado | Alcance |
|---|---|---|
| `MAX_LINEAS_LOG` | 100 | Cola examinada; 1–1000 líneas no vacías |
| `UMBRAL_FUERZA_BRUTA` | 5 | Mínimo inclusivo de peticiones por ventana/IP; 1–100 |
| `VENTANA_FUERZA_BRUTA_SEGUNDOS` | 60 | Duración máxima del agregado; 1–3600 s |
| `max_items` | 30 | Evidencias entregadas; límite del contrato A-01 |
| `max_selected_bytes` | 65536 | Bytes crudos seleccionados, sin estimación de tokens |

Valores de configuración inválidos se rechazan, sin coerción silenciosa de
floats/bools ni fallback a una configuración que pueda esconder un error.
La entrada sigue limitada a 1 MiB y cada línea a 16 KiB. El alcance registra
líneas examinadas, fuera de ventana, sobredimensionadas, seleccionadas y
omitidas. Una muestra incompleta no acredita cobertura completa del log.

Los agregados de autenticación cuentan peticiones POST a endpoints reconocidos
`login`/`login.php`/`signin`/`signin.php`, y GET/POST a la ruta DVWA brute con
campos username/password. Una palabra “login” en otra query no basta.
Esto identifica frecuencia de solicitudes de autenticación, no credenciales
fallidas ni logins exitosos. No se infiere ese resultado de HTTP 200/302.

Las ventanas se calculan en UTC y requieren IP/fecha válidas. Incluyen conteo,
inicio, fin, umbral, duración, posiciones originales y IDs de la parte
seleccionada. Cada agregado respeta realmente su duración; ventanas separadas
no se fusionan en una supuesta ráfaga de 60 s. Se conservan como máximo las
100 ventanas calificadas más recientes y se declara cualquier omisión.
Pueden existir ventanas solapadas: sus conteos no son sumables como intentos
únicos totales. Los IDs que recibe el LLM pueden ser una muestra; el conteo
deriva de Python sobre el tramo elegible, no de contar esa muestra.

## Criterios del flujo nuevo

Las tareas de `structured_prototype.py`, cuando reciben `preparation`,
incluyen esas observaciones y criterios. Los guardrails vuelven a comprobar
patrón/referencias y clasificación; no dependen de que el LLM obedezca la prosa.
Se mantienen tres agentes sin herramientas, delegación o actuación.

- Un patrón canónico debe estar observado en las referencias proporcionadas.
- Fuerza bruta requiere una ventana compartida calculada; una ruta aislada
  o referencias de distintos grupos no satisfacen el criterio.
- `other` conserva candidatos inciertos, con techo low; no se excluyen
  automáticamente por no coincidir con firmas conocidas.
- En esta política para access.log, SQLi/traversal/comandos/ráfaga tienen
  techo high, XSS medium y other low. Unknown siempre puede conservarse.
- No se admite critical solo con estas observaciones de access.log, ni
  probable_false_positive con severidad superior a low.
- No se introduce un estado de éxito confirmado, IP o fecha inventada,
  y una ruta POST exec sin cuerpo/payload observable no confirma comandos.

Estos techos son una decisión conservadora del flujo experimental y no un
estándar universal de severidad. Gravedad y éxito son dimensiones distintas;
la política debe evaluarse por categoría en A-05. Una firma coincidente
tampoco demuestra que la interpretación del ataque sea correcta. “Posible
falso positivo” conserva incertidumbre; no prueba inocuidad.

La versión de reglas es `observed-access-1` y las instrucciones del prototipo
`structured-prototype-2`. El catálogo no sustituye detección genérica,
correlación con otras fuentes o validación de cuerpos/respuestas ausentes.

## Comparación sintética con línea base

Se mantiene intacta `tests/fixtures/traffic.json` y se compara contra el
prefiltro operativo existente. SQLi, XSS, traversal y comandos de esa fixture
conservan sus familias observadas. Tráfico normal, POST sin evidencia de
payload y línea malformada no ganan hechos de ataque. La diferencia explícita
es la ruta brute aislada: el filtro anterior la marca sospechosa, mientras
el agregado nuevo exige frecuencia válida para atribuir fuerza bruta.

Casos adicionales verifican `onerror=confirm(1)`, doble codificación, cuatro
familias conservadas junto a veinte peticiones de autenticación, umbral
configurable y offsets mezclados que no deben formar una ráfaga falsa.
Estas pruebas miden reglas deterministas y cobertura de las fixtures; no
precisión/recall de un LLM real ni de tráfico representativo de producción.

## A-04: reporte determinista

`agents/structured_reporting.py` valida de nuevo contratos y criterios,
ensambla JSON y construye la tabla desde la clasificación validada. El
narrador solo aporta resumen y recomendaciones referenciadas; no escribe
filas, conteos o campos factuales de la tabla.

La tabla mantiene las seis columnas compatibles con Flask. Tipo, severidad
y estado tienen etiquetas canónicas; posiciones, fechas e IP salen de la
evidencia. Si un candidato agrupa distintas fechas/IP o incluye datos
desconocidos, la celda agregada usa `-` en lugar de elegir arbitrariamente
un origen o instante. El JSON conserva las observaciones individuales.
Una fila puede agrupar varios accesos: los conteos son hallazgos, no accesos
ni suma de ventanas de autenticación.

La narrativa se reduce a texto de una línea y escapa HTML y estructura
Markdown, evitando que inserte otra sección/tabla o HTML activo. Sigue siendo
texto del modelo: la forma segura no certifica la veracidad de su resumen.
Referencias y conteos se generan en Python. Texto con codificación inválida
se rechaza antes de publicar. Los tests verifican que el parser y `/api/v1/estado`
de Flask obtienen los mismos conteos desde el Markdown en un directorio de
fixture, sin modificar la API ni sus fuentes operativas.

## Publicación por generaciones

`dashboard/services/structured_publication.py` exige un directorio destino
explícito y usa un bloqueo de publicación. No se importa desde `main.py`,
pipeline o rutas Flask. En esta entrega solo se invoca con directorios
temporales y contenido sintético.

Cada generación nueva tiene nombre independiente de su contenido e incluye
`result.json`, `report.md` y `manifest.json`. El manifiesto registra análisis,
generación, hora de publicación y hashes SHA-256 de ambos artefactos.
Una vez completos, se sustituye atómicamente un único `current.json` que
selecciona la generación. Un lector captura el puntero una vez y carga
ambos archivos de esa misma generación, verificando manifiesto e integridad.
Se rechazan rutas enlazadas, identificadores inválidos o hashes diferentes.

Ante contrato inválido no se crea generación. Ante fallo de escritura de
JSON/Markdown/manifiesto o puntero, se conserva el puntero anterior. Puede
quedar una generación parcial huérfana, pero no se expone como actual ni
se borra automáticamente. Una corrupción posterior se detecta; no se
interpreta como reporte vacío ni se reconcilia por su cuenta.

Republicar contenido idéntico produce una identidad de generación distinta,
manteniendo hashes de contenido iguales. Esto separa publicación y contenido
sin depender de metadatos de archivos. No es un cambio de IDs de la API actual:
el lector y la ruta de compatibilidad para ese almacén se integrarán en A-05.
Los hashes detectan corrupción accidental; no son firmas ni autenticación
frente a alguien que pueda reescribir todos los artefactos localmente.

No se afirma una transacción común con SQLite de trabajos o entregas de
notificación: este publicador solo coordina los artefactos estructurados.
Su integración con fases de trabajo, API, históricos, alertas y respaldo del
nuevo almacén permanece para A-05. Los perfiles de respaldo de entrega 3
no cubren automáticamente un destino estructurado personalizado.

## Verificación del 06/10/2026

- **167 pruebas Python**, cero fallos/expected failures; tres diagnósticos JS.
- **49 archivos Python** sin errores de sintaxis.
- Ensayo con CrewAI 1.14.2 y doble LLM: **cinco escenarios aprobados**.
  Conserva los tres de A-02 y añade el flujo con observaciones y rechazo de
  una clasificación critical no soportada, con reintentos limitados.
- Pruebas de publicación: JSON/Markdown/API concordantes, narrativa hostil,
  campos agregados desconocidos, conservación del puntero ante errores,
  generación incompleta invisible, corrupción, bloqueo y nueva identidad
  para contenido idéntico.
- `git diff --check`: sin errores de espacios.

No se ejecutaron motor/pipeline operativos, proveedores, Docker o transportes.
No se leyeron `.env`, logs o reportes reales en estos ensayos. No cambian
`main.py`, `agents/log_analyst.py`, agentes/prompts operativos, OpenAPI, UI,
dependencias, intérprete o conmutadores. Se añade a `.env.example` la ventana
del flujo nuevo como contrato; no se edita `.env` ni se hace que el motor
antiguo la use. No se repiten lint/build/audit al no cambiar frontend/paquetes.

## Compatibilidad, reversión y siguiente fase

A-03/A-04 quedan completas como componentes aislados y comparación sintética.
Los fallos R-05/R-06/R-07/R-10/R-13/R-14 de la ruta antigua no quedan corregidos
en operación por esta entrega; las garantías nuevas solo aplican al flujo
estructurado comprobado. A-05 debe medir calidad, costes y latencia reales,
ensayar fallos y retorno, y activar por configuración de forma reversible.

Revertir solo módulos, pruebas, cambios del prototipo y estado documental de
esta entrega conserva el producto anterior. No borrar generaciones o copias
del usuario como parte de la reversión. No se hizo commit ni publicación de
repositorio/servicios. Siguiente parte: A-05, evaluación y preparación de
integración/activación; cualquier ejecución real debe tener alcance explícito.
