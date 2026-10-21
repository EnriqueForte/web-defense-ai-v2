# Análisis de lo pendiente para finalizar — 20/10/2026

El proyecto dispone de una aplicación local implementada y una base técnica
verificada. Tras la continuación del 20/10, la aceptación acotada A-05 está
cerrada por decisión expresa del usuario y C3 tiene tratamiento residual aceptado
para uso local aislado. C4 dispone de código/CI/artefactos verificados e identidad
de entrega [v0.1.0](ENTREGA_LOCAL_C4_2026_10_20.md), con actualización de VM
separada de V1. La continuación del 21/10 completó [V1 en Parrot](ACTUALIZACION_PARROT_V1_2026_10_20.md)
con actualización, conservación/recuperación aislada y lectura/cierre acreditados
por el usuario. Sus actas y guías se incorporan en una actualización documental
posterior, con commit/push autorizados expresamente por el usuario el 21/10.
No se ha identificado en la revisión inicial
un fallo nuevo reproducido que obligue a rehacer la arquitectura. Esto no es una
auditoría exhaustiva ni una declaración de ausencia de defectos.

Base examinada: `ca2f6af6ceba7af7b5d1fe78bff2bdf0c740ef4c`, árbol limpio al
comenzar, código y documentación del repositorio, actas de ensayos previos y
logs/artefactos completos de la CI. La continuación C3 corrigió aiohttp/yarl y C4
publicó el código `0d73ec2`, con CI39466610699 y artefactos completos verificados.
Las actas posteriores conservan ese árbol de producto; no se ejecutó otro
análisis real. El estado de distribución se registra en el acta C4 enlazada.

## Qué está terminado y no debe reabrirse sin causa

| Bloque | Evidencia y alcance confirmado |
| --- | --- |
| Interfaz, API y ejecución | Migración SOC/Next, respaldo Flask, lectura versionada, configuración, instalación/arranque/cierre y coordinación de trabajos implementados. [Estado vigente](ESTADO_FINAL_2026_10_12.md) y [guía](INICIO_RAPIDO.md). |
| Regresión e instalación | [CI 39466610699](https://github.com/EnriqueForte/web-defense-ai-v2/actions/runs/39466610699), código `0d73ec2`, intento 1, ambos OS aprobados con el parche aiohttp/yarl. Ubuntu: 376 Python aprobadas; Windows: 375 y una exclusiva Linux omitida; tres JS, 101 sintaxis, 27 SDK offline, lint/tipos, 17 UI y nueve E2E por OS. Inventarios 172/0/0; API/proxy 200 y cierre de puertos; artefactos completos revisados. |
| Evaluador A-05 offline | [Grupos y revisión sin proveedor](EVALUACION_GRUPOS_A05_2026_10_19.md): 24 casos/ocho controles; 25 publicaciones/101 archivos por OS, manifiestos/hashes/métricas y bytes JSON/Markdown contrastados. La verificación remota pendiente del bloque anterior queda cerrada. |
| Muestras reales aceptadas | [Ensayos del 14/10](ENSAYO_REAL_A05_2026_10_14.md) y muestra guiada Parrot del 15/10 XSS/fuerza bruta: dos grupos, XSS línea 31 y ráfaga 39–46, coherentes con informe y dashboard. [Acta Groq 413](INCIDENCIA_GROQ_413_2026_10_15.md). No acreditan calidad general ni autenticación exitosa. |
| Conservación de aplicación | [Respaldo y restauración aislada](OPERACION_RECUPERACION_2026_10_14.md) verificados; no equivale a restauración de volúmenes Docker o del buzón de la VM. |
| Reproducibilidad del laboratorio | [Pins e inventario del 19/10](FIJACION_IMAGENES_LAB_2026_10_19.md) publicados y verificados. El escáner rechaza un digest distinto; conserva vulnerabilidades. No implica actualizar contenedores de Parrot. |

En la revisión documental inicial no se repitieron pruebas completas ya
aprobadas: no había cambios de código que lo justificaran. El parche posterior
aiohttp/yarl pasó validación local y después CI nueva verificada en C4. Los fallos
históricos de Groq/formato/tokenizadores conservan sus
registros y correcciones; no se presentan como fallos actuales por aparecer en
actas antiguas.

## Estado de los bloques y condiciones de cierre

| ID | Trabajo restante | Condición verificable de cierre |
| --- | --- | --- |
| C1 — Documentación vigente | Consolidación y publicación completadas con el código de entrega | README, guías, plan y resumen coherentes; cronologías conservadas en archivos históricos. La comprobación documental no equivale a aceptación del producto. |
| C2 — Aceptación A-05 | Cerrada el 20/10 por respuesta expresa del usuario; [revisión y decisión](REVISION_ACEPTACION_A05_2026_10_20.md), doce recibos/once publicaciones y 56 archivos preservados | Primera versión local con límites y comparación legacy expresamente diferida; no certifica calidad general ni autoriza ensayos/publicación/VM |
| C3 — Seguridad residual | [Tratamiento aceptado20/10](TRATAMIENTO_RIESGOS_C3_2026_10_20.md): parche aiohttp/yarl y respuesta expresa del usuario sobre R1–R8 | Cerrado en tratamiento local, sin eliminar avisos o certificar seguridad global; CI del parche aprobada y verificada en C4 |
| C4 — Entrega | [v0.1.0](ENTREGA_LOCAL_C4_2026_10_20.md), código `0d73ec2`, CI39466610699 y artefactos completos verificados; contenido y notas revisados | Identidad de distribución vinculada al código probado. Las actas posteriores conservan su árbol de producto; no se atribuye CI nueva a commits documentales |
| V1 — Parrot actualizado | [Completado el 21/10](ACTUALIZACION_PARROT_V1_2026_10_20.md); registro y guías incorporados en esta actualización documental posterior | App/DB recuperadas en destinos aislados, código/pines aplicados, 172/0/0, 25 archivos conservados, mismo informe/dos grupos y cierre con puertos libres. No equivale a recuperar toda la VM ni el correo temporal anterior. |

V1 acredita ahora el checkout `4c13abd` de `v0.1.0` en la VM, con pines y datos
comprobados por el usuario. `88e7b8a` era su estado inicial, conservado en la
cronología. La evidencia no invalida el ensayo aceptado del 15/10 ni lo repite
con otro LLM. El agente no dispone de acceso operativo a esa VM: las capturas
y confirmaciones recibidas son la base de la aceptación, sin bytes VM completos.
No se usaron `down --volumes`, reset ni auto-upgrade. C1–C4/V1 quedan cerrados
en su alcance, con actas V1 incorporadas en esta actualización documental.

## C2: brecha semántica concreta

Esta sección conserva el análisis que motivó la matriz. Su resolución posterior
es la aceptación local acotada del usuario, registrada en el acta enlazada.
Las limitaciones de evidencia descritas siguen siendo limitaciones; no son
ahora requisitos indefinidos de cierre de esa primera versión.

Los [criterios originales](PLAN_AGENTES_TAREAS.md) incluyen calidad por familia,
tráfico normal, trazabilidad, clasificación y medición. Las guardas y fixtures
prueban referencias, límites, conteos, conservación y el funcionamiento del
evaluador; el resultado mantiene `quality=semantic_evaluation_pending`.

Las muestras reales disponibles sí aportan aceptación parcial. Falta un acta
final que diga qué categorías y condiciones quedan cubiertas, qué se acepta de
severidades/estados y qué no puede concluirse. No hay una comparación controlada
suficiente para declarar superioridad general frente a legacy, un p95 estable
o un coste universal. Duraciones y tokens observados son muestras; las
discrepancias SDK y la variación de modelos del router impiden extrapolarlos.

Propuesta de siguiente trabajo, antes de consumir proveedor:

1. Reutilizar las actas y resultados ya conservados; inventariar cobertura y
   discrepancias por caso sin regenerar informes ni tocar la publicación viva.
2. Fijar una matriz de cierre con positivos y negativos pertinentes al alcance
   ofrecido; separar lo verificable en código de lo que requiere juicio humano.
   Debe incluir la distinción entre indicador, ráfaga e inicio de sesión exitoso
   no demostrado. Una prueba no representada queda sin acreditar.
3. Para cada brecha, decidir si se corrige, se limita la afirmación del producto
   o se necesita un ensayo acotado. No convertir cada límite en una ampliación
   automática del detector o en otra ronda indefinida de fixtures.
4. Si se necesita un ensayo real, preparar primero caso, proveedor/modelo,
   presupuesto de llamadas/tiempo y criterio de parada para autorización nueva.
   No repetir automáticamente ni reutilizar autorizaciones consumidas.

Las métricas exactas de grupos son expectativas de fixtures, no la definición
universal de incidente. El ensayo `same_family` del 14/10 aceptó dos grupos SQLi
para dos eventos. No se revoca esa aceptación por aplicar después una política
sintética que espera uno; una diferencia de agrupación necesita interpretación.
Una exigencia de comparación legacy/structured deberá conservarse como tarea
explícita o diferirse expresamente en el alcance, sin afirmar que ya se midió.

## C3: riesgos conocidos, sin confundir fechas

El análisis inicial usó paquetes del18/10 e imágenes del19/10. La continuación
del [20/10](TRATAMIENTO_RIESGOS_C3_2026_10_20.md) sí consulta paquetes/avisos:
añade tres de aiohttp y corrige localmente el par aiohttp/yarl. Las imágenes
conservan la evidencia19/10, sin Docker nuevo. La lista siguiente describe la
base histórica, no una negación de esa consulta posterior.

- [Dependencias](REVISION_DEPENDENCIAS_SECRETOS_2026_10_18.md): seis entradas y
  cinco IDs principales Chroma/MCP por OS; frontend producción: cero; braces de
  desarrollo: uno alto en esos audits. Las resoluciones comprobadas de CrewAI no
  admiten la versión MCP corregida. La migración requiere un conjunto compatible
  y comprobación posterior; aún no hay solución validada.
- [Imágenes](FIJACION_IMAGENES_LAB_2026_10_19.md): MariaDB: 102 entradas, una crítica
  y 24 altas; DVWA: 4011 entradas, 16 críticas y 276 altas; Mailpit conserva un UNKNOWN.
  Los pins fijan contenido, no eliminan avisos. DVWA es un laboratorio vulnerable:
  aislamiento, uso local y exposición limitada deben formar parte de la decisión.
  El Compose legacy conserva una advertencia de exposición diferente y no es la
  instalación recomendada.
- [Secretos/historial](REVISION_DEPENDENCIAS_SECRETOS_2026_10_18.md): existen
  revisiones con Gitleaks y triage. Se mantienen hashes públicos y un CSRF opaco
  histórico de procedencia no acreditada; el fixture actual está anonimizado.
  Falta consolidar el tratamiento final y actualizar la revisión al contenido
  de entrega. No se ha demostrado una credencial válida ni se probará contra un
  servicio para resolver esa incertidumbre.

Una decisión de entrega puede declarar riesgos residuales y límites locales;
esa decisión no se toma implícitamente en esta auditoría ni se sustituye por
una afirmación de seguridad global. No es útil exigir cero avisos a DVWA sin
distinguir el laboratorio vulnerable del proceso que analiza sus datos.

## C1: incoherencias localizadas al iniciar el análisis

Las siguientes observaciones describen el estado previo. La continuación
documental del 20/10 las corrige: las cronologías del README y del plan se
conservan en sus archivos históricos, las guías enlazan el estado vigente y
la matriz queda preparada. La continuación posterior añade revisión técnica
y aceptación expresa de A-05 en alcance local, con comparación diferida.

- README, sección «Estado de esta versión»: todavía dice que Docker e
  ingesta/análisis real en Parrot siguen pendientes, aunque el recorrido guiado
  del 15/10 está aceptado en el resumen vigente.
- Instalación autoalojada: apertura y lista de cierre mezclan pruebas antiguas
  con actuales; citan escaneo pendiente, laboratorio/ingesta pendientes y
  procedimiento de recuperación pendiente, sin distinguir el alcance ya cerrado.
- Plan de agentes/tareas: el backlog mantiene A-01–A-04 aisladas y una fila
  «Contratos A-01: pendiente», aunque están integradas. A-05 debe conservar su
  brecha de aceptación, no confundirse con falta de implementación.
- El acta de grupos y el resumen aún decían publicación/CI pendiente al iniciar
  esta revisión. Se actualizan con la verificación completa ya realizada.

## Orden de trabajo y límite de la entrega

1. Cerrar el acta técnica anterior y registrar este análisis: realizado localmente.
2. Consolidar guías y preparar la matriz de aceptación C1/C2 usando evidencia
   existente: realizado localmente en la continuación documental del 20/10.
   La [matriz](MATRIZ_ACEPTACION_A05_2026_10_20.md) registra cuatro decisiones ya
   resueltas para el alcance local, sin llamadas nuevas.
3. C2 y C3 resueltas el20/10 con revisiones y respuestas expresas separadas.
   Se conserva el alcance local; el parche aiohttp/yarl se validó en la CI de C4
   antes de preparar la versión de entrega.
4. V1 completada el 21/10 en actualización/conservación y recuperación aislada:
   preparación y ejecución registradas por separado, sin ensayo LLM nuevo.
5. C4: código publicado y CI/artefactos verificados; identidad `v0.1.0` y notas
   de la entrega en V2. El registro C4 conserva las referencias exactas.

No se añaden como requisitos de cierre un cuarto agente, remediación automática,
despliegue público/multiusuario, servicio permanente, soporte macOS/ARM, retención
automatizada, CSP completa de scripts Next o demostración de portfolio. Son
alcances posteriores. Tampoco se certifica una observación de 24 horas o siete
días que históricamente se aceptó cerrar antes.

La revisión inicial no consultó tags/releases remotos. C4 sí comprobó después
que no había ninguno al iniciar su trabajo y prepara `v0.1.0` como primera
identidad de entrega para el alcance ya aceptado. La publicación formal se
comprueba en GitHub y no se deduce de la existencia de archivos documentales.

La revisión no ejecutó LLM, Docker, envíos, servicios operativos o cambios en
Parrot, ni leyó bytes del `.env` operativo. La comprobación de artefactos GitHub
es una lectura de evidencia sintética y no un ensayo nuevo de la aplicación.
