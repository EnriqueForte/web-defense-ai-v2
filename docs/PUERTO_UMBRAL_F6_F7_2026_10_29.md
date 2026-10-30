# Puerto Umbral — preparación de código F6/F7

Fecha: 29/10/2026, Europe/Madrid. Estado: **implementación revisada en código;
sin ejecutar escenarios, servicios o suites y sin aceptación de fases**.
El propietario solicita cerrar F0–F7 antes del martes 03/11 y elige expresamente
continuar por ahora solo con desarrollo y revisión de código. La planificación
y los criterios que siguen abiertos están en el
[plan de cierre de V2 y Puerto Umbral](CIERRE_V2_PUERTO_UMBRAL_2026_11_03.md).

## Alcance y separación del histórico

El corpus original de F2 permanece en 45 entradas y conserva su resultado
histórico 42/45. No se ha repetido, renombrado o ajustado para incorporar estas
ampliaciones. F6 y F7 tienen catálogo y semilla propios en
[advanced_catalog.py](../labs/puerto_umbral/lab/advanced_catalog.py) y un
[manifiesto separado](../labs/puerto_umbral/lab/extensions-corpus.json):
99 entradas declaradas, 45 para F6 y 54 para F7. Cada módulo define tres
variantes, seis intentos entre dos modos y tres controles normales corregidos.
Son expectativas fijadas antes de ejecutar, no resultados de una evaluación.

Las once ampliaciones comparten un target avanzado por modo y se restablecen
antes de cada ejecución individual. Se conservan los diez targets base y las
dos pasarelas: la topología preparada pasa de 12 a 14 contenedores. Los dos
targets nuevos utilizan usuario 10001, raíz de solo lectura, límites de recursos,
sin privilegios o montajes del host, y `network_mode: none`. Las pasarelas montan
solo el socket del módulo de su modo. El código de inspección contempla esta
topología; todavía no se ha construido o comprobado en Docker.

El mismo comando de arranque construirá las imágenes al distribuir esta fuente,
pero **no se solicita arrancarlo o actualizar la VM para probarla en este bloque**.
No cambian los digests base, dependencias Python/Node, `.env` o el Site privado.

## F6: escenarios con estado e identidad

| Módulo | Comparación preparada | Evidencia y límite |
| --- | --- | --- |
| XSS almacenado | Guarda un aviso y lo vuelve a presentar; salida sin codificar frente a codificación HTML | POST/GET, auditoría de almacenamiento/lectura e iframe. Solo el marcador del iframe y nonce acreditan ejecución; renderizar no basta |
| IDOR | Sesión de estibador, objeto de su propiedad y objeto de supervisor; autorización por propietario | Actor/rol, recurso, propietario, decisión y respuesta. Identidades y datos ficticios |
| CSRF | Preferencias de cuenta; control de origen y token ligado a sesión | Prueba HTTP separada de formulario real entre 4381 y el portal. Confirmación requiere cookie y evento de origen cruzado que no proceda del ejecutor HTTP |
| SSRF acotada | URL lógica del señuelo, recurso público frente a interno | HTTP real sobre socket Unix privado a un pequeño servidor dentro del target. Destinos enumerados, sin IP, DNS, redirecciones o URL arbitraria |
| Permisos de atraque | Ejecutar sin aprobación y reutilizar un permiso consumido, frente a aprobación de supervisor y uso único | Estado anterior/posterior y actor. La autorización corregida requiere estado aprobado y consume el permiso |

Los tokens de sesión/CSRF se conservan en memoria durante la secuencia y se
omiten del texto de respuesta guardado por el controlador. El recibo distingue
hash de respuesta original y hash del texto redactado. No guarda cabeceras
Authorization, contraseñas del formulario o cookies. Las sesiones son
exclusivamente ficticias y se pierden al restablecer el módulo.
Las cookies tienen nombres separados por modo. Cada target avanzado queda
ligado al primer identificador de ejecución recibido después del reset y
rechaza otro identificador; una referencia anterior no se incorpora al lote
de la ejecución siguiente. Los identificadores de recurso desconocidos se
normalizan y no copian entradas arbitrarias a la auditoría.

El ejercicio CSRF de navegador es una página estática del origen de control,
sin scripts ni token del panel. El operador crea la sesión ficticia en el
portal y envía un formulario desde el otro origen. La comprobación posterior
consulta la auditoría capturada; la prueba HTTP inicial no se presenta como
prueba de navegador. Ambos pasos quedan pendientes de ejecución autorizada.
El ejecutor conserva su límite de 30 segundos. Solo el target avanzado dispone
de una ventana máxima de cinco minutos desde su primera petición para completar
los pasos manuales, sin ampliar las 20 solicitudes ni la frecuencia máxima de
dos por segundo. La fecha límite queda en el recibo y se muestra en el panel;
un reset o agotar la cuota puede invalidar antes esa ventana. Los targets base
mantienen sus 30 segundos. Las confirmaciones usan el mismo bloqueo que el
ejecutor y el reset, y conservan los fallos de captura sin marcar una
confirmación exitosa antes de obtener la evidencia correspondiente.

Las páginas del target avanzado permiten conservar su origen para los
formularios normales. El iframe XSS del panel mantiene `sandbox="allow-scripts"`
sin `allow-same-origin`; la confirmación sigue validando `event.source`, origen
opaco y nonce. El CSP del target limita conexiones y formularios; el formulario
CSRF del controlador tiene una excepción de CSP solo para los dos portales
loopback. No se amplía el acceso del portal a la API de control.

## F7: revisiones de artefactos ficticios

| Categoría OWASP 2025 | Ejercicio preparado | Qué no acredita |
| --- | --- | --- |
| A02 — Configuración | Réplica de diagnóstico con detalle ficticio frente a respuesta mínima | Una auditoría de configuración de Apache o de producción |
| A03 — Suministro | Artefacto local modificado frente a un digest de referencia fijo | Un análisis de dependencias reales, firma de proveedor o instalación de malware |
| A04 — Criptografía | Codificación base64 reversible frente a derivación scrypt con sal | Certificación criptográfica o parámetros recomendados para cualquier despliegue |
| A08 — Integridad | Manifiesto ficticio modificado frente a comprobación HMAC | Firma de todos los datos o de toda la cadena de publicación |
| A09 — Registro y alertas | Secuencia ficticia con un hueco y advertencia local | Continuidad de Apache, entrega de notificaciones o validación ampliada F4 |
| A10 — Excepciones | Detalle de error ficticio frente a respuesta controlada | Recuperación exhaustiva ante fallos del sistema real |

El panel muestra `fixture_review` como revisión de artefactos y ofrece un mapa
de las diez categorías. Las restantes se relacionan con los escenarios de
F2/F6. Todas las categorías conservan aceptación pendiente. Un catálogo
educativo completo no implica detección completa por V2 o explotación real.

## Auditoría y observador de V2

El [contrato de eventos](../labs/puerto_umbral/lab/audit_contract.py) fija una
lista cerrada de campos: secuencia, UTC, ejecución/petición, componente/modo,
actor/rol, acción/recurso/propietario, decisión/resultado/HTTP, origen, mecanismo
de sesión y estados observados. Rechaza campos adicionales, truncado y valores
fuera de formato. No admite etiquetas esperadas del corpus, credenciales,
tokens o cuerpos arbitrarios. La auditoría se obtiene por HTTP local, se
valida y guarda fuera del target con hash y correlación de peticiones.
Los componentes se denominan por su función de negocio (carga, preferencias,
baliza, etc.), sin nombres de vulnerabilidad, categoría OWASP o caso esperado.

El [lector de V2](../dashboard/services/application_audit.py) valida el recibo
del controlador, versión, ruta y digest antes de procesar el lote. Sus reglas
describen acceso a recursos de otro propietario, aprobación ausente, lectura
del señuelo interno, control de origen y contenido almacenado sin codificar.
No consultan resultados esperados del corpus ni el veredicto funcional del
ejecutor. Un evento de renderizado no se transforma en ejecución XSS.

La auditoría procede de la aplicación observada: no equivale a una afirmación
independiente de compromiso. La nueva vista en Actividad muestra esas
observaciones por reglas separadas del informe LLM. No modifica los cuatro
grupos ya publicados ni produce métricas del detector.

Rutas preparadas:

- `GET /api/v1/fuentes/auditoria`: solo lectura de la última auditoría disponible
  del modo seleccionado. No usa Docker ni llama al modelo.
- `POST /api/v1/fuentes/auditoria/capturar`: acción explícita local para conservar
  un lote validado en el perfil V2. Fija `run_id` y `sha256`, requiere perfil
  Puerto Umbral y captura manual habilitada; rechaza una auditoría cuyo hash
  cambió y respeta bloqueos de ciclo/motor y operaciones activas.

La copia conservada usa `.local-state/puerto-umbral/application-audit/` con
`current.json` y snapshots inmutables `events.json`/`receipt.json`. La lista del
backup y del restaurador reconoce exclusivamente esos nombres y UUID. Los
recibos originales bajo `labs/` siguen requiriendo conservación separada.
Los 66 archivos recuperados anteriormente no acreditan esta cobertura nueva.
Repetir la conservación del mismo modo, ejecución y hash reutiliza la copia
íntegra identificada por esos datos; no genera otra generación ni sobrescribe
una copia incompleta o distinta. El recibo conserva el estado de la ejecución
en el momento de la copia. La interfaz advierte si el lote es parcial y bloquea
la conservación durante lectura, errores, seguimiento o captura manual
deshabilitada. Un plazo de red agotado se presenta como resultado sin confirmar,
porque la escritura del servidor puede haber terminado.

## Revisión de código solicitada, paso 1 — 29/10/2026

Recorrido de lectura manual de target, controlador, contrato, lector de V2,
rutas Flask, panel React, JavaScript del laboratorio, configuración declarada
y lista compartida de respaldo/restauración. Se aplicaron estas correcciones
locales; su comportamiento todavía debe comprobarse cuando se autorice ejecutar:

| Punto encontrado | Corrección en código |
| --- | --- |
| Confirmación podía coincidir con otra ejecución/reset | Bloqueo compartido para confirmaciones, UI bloqueada durante la operación y vínculo de target a ejecución |
| Ventana de 30 segundos poco práctica para pasos humanos | Ventana avanzada de cinco minutos; ejecutor/base, frecuencia y cuota conservan sus límites |
| Captura de navegador podía fallar después de marcar confirmación | Capturar/persistir antes de confirmar; errores y nuevas evidencias quedan registrados incluso si no aparece el evento esperado |
| Lectura previa comprobaba tamaño, pero después cargaba el archivo sin límite | Lectura acotada antes de decodificar, UTF-8 estricto y comparación de identidad/tamaño/fechas tras la lectura |
| Valores libres en campos semánticos del contrato | Enumeraciones para decisión, origen, control CSRF, alcance del señuelo, renderizado y mecanismo de sesión |
| Una recaptura fallida podía dejar seleccionable el lote anterior | Estado de fuente inválida cuando el último intento registrado falla; conteo, esquema y modo comprobados |
| La interfaz podía conservar datos antiguos tras una actualización fallida | Error visible, conservación deshabilitada y validación de identificadores, hashes, conteos y filas; cancelación al salir de la vista |
| Repetir una solicitud podía crear copias duplicadas | Identificador estable por modo/ejecución/hash y reutilización solo tras verificar contenido y recibo completos |

La revisión estática del paso 1 queda completada con estas correcciones. No
equivale a revisión exhaustiva, ausencia de defectos, validación funcional o
aceptación F6/F7. Permanecen pendientes navegador real, compatibilidad de la
topología Docker, permisos efectivos de volúmenes, límites de tiempo/cuota,
cancelación, concurrencia, regresión y recuperación de estas copias nuevas.
No se ejecutó ninguna de esas comprobaciones operativas.

## Estado de aceptación y revisión pendiente

| Criterio | Preparación actual | Pendiente para cerrarlo |
| --- | --- | --- |
| F6-AC1 | Identidades, objetos, propietarios y flujo de permisos implementados | Observar positivos y controles normales de cada variante |
| F6-AC2 | Señuelo Unix HTTP y destinos enumerados, targets sin red IP | Construcción e inspección real de la topología y caso SSRF |
| F6-AC3 | Página entre orígenes y confirmación por auditoría de cookie/origen | Revisión real de navegador en ambos modos |
| F6-AC4 | Lector por esquema/hash; sin lectura de etiquetas esperadas | Verificación operativa y evaluación independiente de la nueva fuente |
| F6-AC5 | Corpus de ampliación separado y corpus base intacto | Positivos, normales y regresión autorizados |
| F7-AC1 | Mapa de diez categorías y tipo de evidencia por módulo | Revisar artefactos y correspondencia con el propietario |
| F7-AC2 | Revisiones ficticias y límites visibles en panel/recibos/docs | Comprobar esas pantallas en el producto actual |
| F7-AC3 | No se declaran categorías completas detectadas | Evaluación propia antes de cualquier afirmación de detección |

Las comprobaciones estáticas no acreditan comportamiento en navegador,
compatibilidad de Docker, efectos funcionales, regresión o calidad de detección.
No hay un resultado nuevo 99/99 ni cierre de F6/F7. El siguiente bloque de
ejecución se decidirá con el propietario; la restricción actual es solo código.

Revisión estática completada en este bloque: sintaxis/compilación en memoria de
ocho archivos Python sin importarlos; sintaxis JavaScript sin ejecutarlo;
TypeScript sin emisión; JSON OpenAPI y manifiesto de ampliación legibles; YAML
de 14 servicios con las propiedades de aislamiento declaradas; referencias
entre IDs HTML y selectores JS coherentes; 184 enlaces locales comprobados sin
ausencias en la preparación inicial; la comprobación posterior del paso 1
abarca 180 enlaces locales actuales sin ausencias y `git diff --check` correcto.
El corpus base se comparó con HEAD y
permanece sin cambios. Durante la revisión local no se realizó build Docker,
preview, compilación Next.js completa o pruebas funcionales. La compilación
posterior del propietario en Parrot se registra a continuación. El primer recorrido de validación
está pendiente de autorización posterior.

## Distribución autorizada del código revisado

El 29/10 el propietario solicita expresamente commit/push de este paquete antes
de continuar. Se prepara una publicación de 34 archivos sobre `main`, con base
`c8abcaf` comprobada frente a `origin/main` y mensaje `[skip ci]`. Incluye la
fuente F6/F7, su integración en V2, documentación y las actas pendientes de la
recuperación previamente observada. La identidad de entrega es el commit que
incorpora esta nota; el resultado del push y su coincidencia remota se verifican
al terminar la operación Git. No se crea una release o etiqueta nueva.

Publicar la fuente no construye o activa la topología nueva, actualiza Parrot,
ejecuta suites o consume la autorización de otro análisis. El corpus base y los
JSON históricos F5 se mantienen sin cambios. Esta entrega conserva la revisión
funcional, las métricas del detector y la aceptación de F6/F7 como pendientes.

## Recepción de publicación y compilación en Parrot — paso 3

El commit de entrega es `cc363aff5e663bcacf0daf7205f18696b30c158a`, publicado
en `origin/main` y comprobado contra el remoto con árbol Windows limpio al
terminar el push. Incluye 34 archivos y `[skip ci]`; no se atribuye una nueva
ejecución CI, etiqueta o release.

Después de autorizar el paso 3, el propietario aporta dos capturas:

| Evidencia | Resultado visible |
| --- | --- |
| `git log -1 --oneline` en Parrot | `cc363af`, `HEAD -> main`, `origin/main` y `origin/HEAD`, con el título del paquete F6/F7 |
| `node node_modules/next/dist/bin/next build --webpack` | Next.js 16.3.8; compilación correcta en 2,8 s y TypeScript en 2,8 s |
| Fases finales de compilación | Páginas estáticas 4/4, trazas y optimización terminadas en 11,8 s; rutas `/` y `/_not-found` |

El paso 3, actualización de código y compilación del frontend, queda
**completado según las capturas del propietario**. El agente no accedió a la VM
ni ejecutó la compilación; no se muestra código de salida del proceso en el
recorte. No se deducen de la compilación el arranque de V2, construcción de
imágenes, disponibilidad de los 14 servicios o validación de escenarios.

El siguiente bloque es el arranque conjunto y comprobación de disponibilidad,
separado de cualquier escenario o análisis. No se solicita repetir el análisis
Groq ya realizado. Esta recepción documental es local posterior a `cc363af`;
todavía no tiene otro commit/push.

El propietario autoriza a continuación el bloque de arranque y disponibilidad:
inicio conjunto en perfil `structured` y fuente `corrected`, revisión de la
consola V2 y panel del laboratorio. Esa autorización incluye la preparación de
imágenes y servicios propios del lanzador, sin escenarios, suites, seguimiento
activado, nuevas llamadas al modelo o notificaciones. El arranque todavía está
pendiente de la salida real del propietario; no se atribuye éxito por facilitar
el comando. Se conserva la configuración Groq y el informe anteriores.

## Arranque informado, panel visible y autoría — 29/10/2026

Las capturas posteriores del propietario muestran el comando conjunto con
`--lab-mode corrected` y la salida «Consola lista» en 3000, panel en 4381 y
portales en 4380/4382. El panel se muestra accesible e informa de 14 contenedores,
targets sin red IP, usuario sin privilegios y raíz de solo lectura. Se ven las
ampliaciones del catálogo, el resultado «SIN EJECUCIÓN» de la selección actual y
filas del historial anterior. Se acredita el arranque informado por el lanzador
y el acceso al panel, sin inspección Docker independiente por el agente.

No hay captura de la vista Actividad de V2 en este envío. No se infieren de
estas imágenes lectura de la auditoría avanzada, nuevos escenarios, resultados
del modelo, revisión móvil/teclado o aceptación F6/F7. La selección «Vulnerable»
del panel es independiente de la fuente corregida elegida al arrancar V2.

El propietario solicita incorporar su autoría en la cabecera de Puerto Umbral,
como en V2. Se añaden en `lab/control.html` Enrique Forte, `@T3r0S3c`,
«Developer & Maintainer» y los enlaces GitHub/LinkedIn ya presentes en V2, con
los mismos SVG, etiquetas accesibles y apertura segura en otra pestaña. La
identificación inferior de la barra lateral muestra también nombre y alias.
`lab/control.css` adapta el bloque a distintas anchuras. El cambio es de
presentación, sin modificar JavaScript, APIs, escenarios o dependencias.

La modificación de autoría y estas actas siguen locales posteriores a
`cc363af`, sin commit/push o actualización de Parrot. No se ha iniciado un
preview o repetido el arranque desde Windows; la revisión visual del cambio
queda para su recepción en la VM. El Site privado F1 se conserva.

Distribución posterior autorizada: el propietario solicita commit/push de la
autoría para verificarla en Parrot. Se incluyen los siete archivos de HTML/CSS
y actas pendientes, sobre `cc363af`, con `[skip ci]`. La identidad es el commit
que incorpora esta nota y la comprobación remota se realiza tras el push. Las
referencias a estado local anteriores corresponden a la preparación.

El panel lee `control.html` y `control.css` desde el checkout en cada GET. Para
recibir esta modificación basta actualizar con `git pull --ff-only` y recargar
4381 con Ctrl+Shift+R; no necesita compilar Next o reconstruir imágenes. Una
revisión visual posterior sigue pendiente de la captura del propietario. Esta
distribución no ejecuta escenarios o modelos ni cambia el backend del laboratorio.

### Recepción visual de la cabecera

La entrega de autoría se publicó en
`5bf154a7a3c8657735f2157e80a3bb3e6eb256ff`, siete archivos, con `[skip ci]`.
Tras el push se verificaron coincidencia con `origin/main` y árbol Windows
limpio. El propietario aporta después una captura de la cabecera donde se ven
Enrique Forte, `@T3r0S3c`, «Developer & Maintainer», los iconos de GitHub y
LinkedIn, la insignia del laboratorio y el reloj.

La autoría queda **confirmada visualmente en ese encuadre de escritorio**.
El recorte no muestra apertura de enlaces, vista móvil, navegación con teclado,
identificación inferior o HEAD de la VM; no se atribuyen esas comprobaciones.
No hacen falta otra compilación o escenarios para cerrar esta recepción visual.
La vista Actividad de V2 sigue pendiente dentro del bloque de disponibilidad.
Esta acta posterior a `5bf154a` permanece local, sin nuevo commit/push.

### Recepción de Actividad V2 y fin del bloque de disponibilidad

Dos capturas posteriores muestran las secciones solicitadas en Actividad:

| Sección | Evidencia visible |
| --- | --- |
| Fuente del laboratorio | «Captura antigua · Modo corregido», 17 líneas, última captura 27/10 a las 17:50:51 y última lectura válida a las 18:04:52, ambas Madrid |
| Identidad del snapshot | `df39623de3684fa7932edf6b688b2f04`, SHA-256 `2f891446d512be3a31ee858db5f3318156f74b3d2348b40a7ee41dd8c59f2b4a` |
| Auditoría de aplicación | Panel «Identidad, recursos y estado», con «Sin auditoría de aplicación disponible para el modo seleccionado», sin error visible |

La identidad coincide visualmente con el snapshot histórico ya analizado; no
se recalculan bytes de la VM por leer la captura. El estado antiguo describe
esa copia conservada y no acredita una captura reciente ni fallo del conector.
La fuente avanzada sin datos es coherente con no haber ejecutado nuevos casos
F6/F7; no se presenta como un resultado de detección o una prueba con eventos.

Con las capturas anteriores del lanzador/panel y estas vistas de V2, el bloque
acordado de **disponibilidad y revisión básica de pantallas queda completado**.
No es aceptación funcional F6/F7, revisión completa UX o evaluación del detector.
No se pide recapturar el log histórico ni repetir el análisis Groq para cerrar
este recorrido. Una validación manual nueva requiere acordar su alcance;
todavía no queda autorizada por aportar estas imágenes. Registro local
posterior a `5bf154a`, sin nuevo commit/push.

### Autorización del primer caso manual normal F6

El propietario autoriza expresamente un único caso manual y la lectura de su
auditoría en V2: **Cargas · autorización por objeto**, modo **corregido**, tipo
**Uso normal**, **variante 1**, entrada `ext-idor-b1-corrected`. Se facilita el
recorrido desde el panel, sin ejecución de la VM por el agente ni resultados
atribuidos todavía. El botón restablece el módulo avanzado corregido, conserva
recibos anteriores, crea una sesión ficticia y consulta el recurso propio.

Expectativa derivada del código: HTTP 200, `document: own-1`, propietario
`estibador.demo` y marcador `UMBRAL_OWN_CARGO`; dos eventos de aplicación
(sesión y lectura). El ejecutor obtiene también auditoría y evidencia Apache
como parte de ese caso. La vista V2 se consulta con «Actualizar auditoría»;
puede mostrar eventos válidos sin coincidencias de reglas, porque es uso normal.
Las expectativas no son resultados observados ni métricas del detector.

La autorización no incluye otro caso, repetir este, suites, captura manual
adicional de Apache, seguimiento, conservar copia V2, modelos o notificaciones.
Se esperan capturas del resultado y de la auditoría antes de decidir cualquier
continuación. Los registros históricos y la autorización Groq consumida se
conservan. Acta local, sin nuevo commit/push.

### Resultado del caso normal y recepción de su auditoría en V2

Las dos capturas siguientes del propietario acreditan este recorrido único:

| Campo | Valor visible |
| --- | --- |
| Caso | Cargas, F6, `corrected`, `benign`, variante 1 (`ext-idor-b1-corrected`) |
| Ejecución | `10fea5f6cbef9d88320ca767cc11e0b4` |
| Resultado del panel | «Uso normal completado correctamente» |
| Solicitud mostrada | `GET /avanzado/carga?documento=own-1`, HTTP 200 |
| Respuesta | `document: own-1`, `owner: estibador.demo`, `fixture: UMBRAL_OWN_CARGO` |
| Captura del ejecutor | 3 peticiones, 3 líneas Apache correlacionadas; V2 consultado: no |
| Auditoría del panel | 2 eventos y 2 referencias HTTP |
| Auditoría visible en V2 | Modo corregido, mismo identificador y 2 eventos |
| SHA-256 de auditoría mostrado por V2 | `1fbf865d130e66e22ebbef765f3e06f1f6a6b6b3d21e795ab4577d625a607c3c` |
| Observaciones por reglas | «No hay coincidencias de estas reglas» |

El recorrido **un caso normal → auditoría capturada → lectura en V2** queda
completado dentro del alcance de esas capturas. La ausencia de coincidencias
es coherente con el control normal, pero no se convierte en una tasa global de
falsas alarmas ni evaluación LLM. La auditoría se consulta por separado desde
V2: «V2 consultado: no» describe al ejecutor, no contradice su lectura posterior.

El agente no accedió a la VM ni verificó bytes, líneas originales o hashes de
forma independiente. Los botones de exportar y conservar están visibles, sin
evidencia de haberlos pulsado: no se acredita JSON exportado, copia conservada
en V2, respaldo/restauración de esta auditoría o lectura por el modelo.
Este resultado no cierra las variantes de Cargas, las otras familias, F6/F7,
los 99 casos o los criterios ampliados del detector.

La autorización del único caso y su lectura queda cumplida. No se solicita
repetirlo o iniciar otro caso; cualquier ampliación se decidirá por separado.
Registro local posterior a `5bf154a`, sin nuevo commit/push.

### Autorización de conservación de esta auditoría y lectura del recibo

El propietario autoriza después conservar en V2 la auditoría de esa ejecución
y comprobar su recibo local, sin repetir el caso o llamar al modelo. Se guía
el botón «Conservar copia de auditoría en V2» y la lectura en otra terminal de
`.local-state/puerto-umbral/application-audit/current.json` con
`.p2/bin/python -B -m json.tool`. El panel debe informar de copia conservada.

Se comprobarán modo corregido, ejecución `10fea5f6cbef9d88320ca767cc11e0b4`,
2 eventos, `original_sha256` igual al observado y las banderas
`analysis_requested: false` / `notifications_requested: false`. Por el cálculo
estable del código, el identificador esperado de esa copia es
`ed70066797f1f68f7df55b7ecb18247d`; derivarlo no acredita su creación. El campo
`sha256` corresponde a los bytes JSON normalizados de la copia y puede diferir
del original; leer el recibo por sí solo no verifica el hash de esos bytes.

Conservación y lectura quedan pendientes de capturas reales. No se autoriza
por este paso crear un ZIP de respaldo, restaurar, activar seguimiento o
notificaciones, repetir casos o iniciar otra evaluación. Acta local sin push.

### Conservación confirmada y recibo local observado

Las capturas posteriores muestran el mensaje «Copia de auditoría conservada en
V2 para su respaldo. No se ha solicitado un análisis» y la lectura del archivo
`application-audit/current.json` con `json.tool`:

| Campo | Valor observado |
| --- | --- |
| `schema_version` / `source` | `1` / `puerto-umbral-application` |
| `run_id` | `10fea5f6cbef9d88320ca767cc11e0b4` |
| `snapshot_id` | `ed70066797f1f68f7df55b7ecb18247d`, coincide con el cálculo esperado |
| `mode` / `events` | `corrected` / `2` |
| `evidence_kind` / `execution_status_at_capture` | `application_state` / `completed` |
| `observer_version` | `puerto-umbral-audit-observer-1` |
| `original_sha256` | `1fbf865d130e66e22ebbef765f3e06f1f6a6b6b3d21e795ab4577d625a607c3c` |
| `sha256` de la copia | `5ce5ba9f249d6104bad53ee4b2bbf9de66259147ff3c9d4d669d53c4c0aa7d1a` |
| `captured_at` | `2026-10-29T21:46:07.257702+00:00` |
| `analysis_requested` / `notifications_requested` | `false` / `false` |

La referencia al caso, el conteo, el modo, el hash original y el identificador
de copia coinciden con la evidencia anterior. La diferencia entre hash original
y hash de copia es coherente con la normalización JSON descrita en el código;
la captura del recibo no supone recalcular los hashes de los archivos.

El recorrido limitado **un control normal → auditoría en V2 → conservación →
recibo local** queda completado según estas capturas. No se ha acreditado
lectura independiente de `events.json`, ZIP de respaldo nuevo, restauración de
esa auditoría, pruebas de idempotencia o recuperación ante interrupciones.
La copia queda preparada para incluirse en el perfil de respaldo existente;
los 66 archivos recuperados anteriormente no acreditan su recuperación.

No se pide repetir el caso o la copia para cerrar este recorrido. La
autorización queda cumplida y las demás variantes/familias F6/F7 y métricas
globales permanecen pendientes. Se actualiza documentación local sin otro
commit/push o nueva ejecución del agente.

### Pausa y siguiente bloque guardados

Tras proponer los cuatro controles normales restantes de F6 (Bitácora,
Preferencias, Baliza y Atraque, corregido/variante 1, con lectura y conservación
de auditorías), el propietario indica que continuará mañana y pide guardar el
paso. No se ejecuta ese bloque ni se interpreta el aplazamiento como permiso
para iniciarlo durante su ausencia. No se crea una automatización.

El [punto de reanudación del plan](CIERRE_V2_PUERTO_UMBRAL_2026_11_03.md)
conserva la secuencia. Cargas y su copia/recibo ya están completados; no se
repiten. Los demás casos, familias y aceptación global siguen pendientes.
El trabajo de esta sesión queda guardado en las cinco actas locales posteriores
a `5bf154a`, sin commit/push nuevo.

### Reanudación guiada — 30/10/2026

El propietario solicita continuar donde se dejó y reiniciar la aplicación en
la VM para seguir con las pruebas. Se retoma el bloque pendiente de cuatro
controles normales, uno a uno: Bitácora, Preferencias, Baliza y Atraque; modo
corregido, variante 1, con lectura y conservación de auditorías V2, sin suites
o llamadas al modelo. Esta continuación no repite Cargas ni su copia.

El arranque lo realiza el propietario con la instalación existente y el mismo
perfil. No se solicita reinstalar, recompilar o actualizar Git por actas que
siguen locales. Antes de cualquier caso debe terminar el arranque. El primer
control será Bitácora, cuyo texto normal esperado según catálogo es «Revisión
de baliza» con HTTP 200. Arranque y resultados nuevos continúan pendientes de
capturas; ningún resultado se infiere por proporcionar las instrucciones.

### Bitácora: primer control normal del bloque reanudado

El propietario aporta una captura del resultado:

| Campo | Evidencia visible |
| --- | --- |
| Ejecución | `a6af8974ce18f60314f8ad9c888fe4d2` |
| Selección | F6, `corrected`, `benign`, variante 1; Bitácora por la ruta mostrada |
| Estado | `COMPLETED`, «Uso normal completado correctamente» |
| Solicitud/respuesta | `GET /avanzado/tablon?_run=a6af8974ce18f60314f8ad9c888fe4d2`, HTTP 200; HTML con «Revisión de baliza» |
| Ejecutor y Apache | 4 peticiones, 4 líneas correlacionadas; V2 consultado: no |
| Auditoría capturada | 3 eventos / 3 referencias HTTP |

El control normal de esta variante queda observado en el panel. No acredita
ejecución JavaScript, protección general ante contenido malicioso, las otras
variantes o aceptación F6/F7. El recorte tampoco muestra la terminal del nuevo
arranque ni una inspección independiente de la VM por el agente.

Sigue pendiente ver el mismo identificador, modo corregido y tres eventos en
V2, y conservar esa auditoría. Ambos pasos están incluidos en la continuación
manual autorizada: «Actualizar auditoría», comprobar identidad/conteo y luego
«Conservar copia de auditoría en V2», recogiendo el mensaje de éxito. No se
repite el caso para ello. Preferencias, Baliza y Atraque siguen pendientes.
Registro local posterior a `5bf154a`, sin nueva publicación o ejecución del agente.

### Bitácora: lectura y conservación confirmadas en V2

La captura posterior de V2 muestra modo corregido, la misma ejecución
`a6af8974ce18f60314f8ad9c888fe4d2`, tres eventos y hash de auditoría
`bf38bcbbb142908a1fb8878fb75b37b45212302a2138fefb744888212b318bdc`.
La vista no muestra coincidencias de sus reglas y confirma «Copia de auditoría
conservada en V2 para su respaldo. No se ha solicitado un análisis».

El recorrido normal de Bitácora, variante 1 corregida, con lectura y
conservación informada en V2 queda completado dentro del alcance de estas
capturas. No se aporta recibo en disco de esta copia, verificación independiente
de bytes o respaldo/restauración de la auditoría. No hace falta repetir el caso.

Sigue Preferencias, corregido/Uso normal/variante 1, dentro del bloque manual
autorizado. La expectativa por código es HTTP 200 con `channel: demo-1` y
`changed: true`, dos eventos de aplicación y tres peticiones del ejecutor,
incluida la captura. Es un control HTTP legítimo de origen/token; no equivale
a comprobar CSRF de navegador entre orígenes. Se recogerá resultado y lectura
en V2, conservando su auditoría antes de continuar a Baliza. Los resultados de
Preferencias, Baliza y Atraque siguen pendientes. Acta local sin nuevo push.

### Preferencias: control normal, lectura y conservación en V2

Las dos capturas posteriores del propietario muestran:

| Campo | Evidencia visible |
| --- | --- |
| Ejecución | `683fa423e04a76f45aa19d081369a1a2` |
| Selección/estado | F6, `corrected`, `benign`, variante 1; `COMPLETED`, uso normal correcto |
| Respuesta | `POST /avanzado/preferencias`, HTTP 200, `channel: demo-1`, `changed: true` |
| Ejecutor y Apache | 3 peticiones, 3 líneas correlacionadas; V2 consultado: no |
| Auditoría del panel | 2 eventos / 2 referencias HTTP |
| V2 | Mismo identificador, modo corregido, 2 eventos; sin coincidencias de reglas |
| SHA-256 de auditoría mostrado en V2 | `91feab4fe25667a85b0c2563881a759b17bd9eb8541fb16aa1a99f0eb702cb8b` |
| Conservación | Mensaje de copia conservada para respaldo, sin análisis solicitado |

El recorrido normal de Preferencias, con lectura y conservación informada en
V2, queda completado a este alcance. Es un control HTTP legítimo: no acredita
CSRF en navegador entre orígenes o protección general, otras variantes,
lectura de recibo local, verificación independiente de hashes o recuperación.
No se repite este caso. La documentación sigue local posterior a `5bf154a`.

Continúa Baliza/corregido/Uso normal/variante 1. El destino está fijado por el
catálogo al recurso público del señuelo HTTP sobre Unix; se espera HTTP 200,
`resource: /public`, `fixture: UMBRAL_PUBLIC_BEACON` y 2 eventos. Se verificará
lectura y conservación en V2 antes de pasar a Atraque. Estas expectativas no
atribuyen resultados nuevos; Baliza y Atraque siguen pendientes de capturas.

### Baliza: recurso público, lectura y conservación en V2

Las capturas del propietario muestran el control normal corregido, variante 1:

| Campo | Evidencia visible |
| --- | --- |
| Ejecución | `9bf63cd2fa87781bb0fc7741d6b02f22` |
| Estado | `COMPLETED`, «Uso normal completado correctamente» |
| Solicitud | `GET /avanzado/baliza?destino=umbral%3A%2F%2Fbeacon%2Fpublic`, HTTP 200 |
| Respuesta | `resource: /public`, `fixture: UMBRAL_PUBLIC_BEACON` |
| Ejecutor y Apache | 3 peticiones, 3 líneas correlacionadas; V2 consultado: no |
| Auditoría del panel | 2 eventos / 2 referencias HTTP |
| V2 | Mismo identificador, modo corregido y 2 eventos; sin coincidencias de reglas |
| SHA-256 de auditoría mostrado en V2 | `a6def6eba59bb18901104b736ebede15117c74660fcce1d1db73d3ee9bb5e4cf` |
| Conservación | Mensaje de copia conservada, sin análisis solicitado |

El recorrido normal de lectura pública de Baliza, con lectura y conservación
informada en V2, queda completado a este alcance. No demuestra denegación de
recursos internos, protección SSRF general, aislamiento inspeccionado por el
agente, verificación independiente de hashes o recuperación de la copia.

Queda Atraque/corregido/Uso normal/variante 1 como último control del bloque
actual. El ejecutor prepara las sesiones ficticias, solicita aprobación de
supervisor para `dock-1` y ejecuta el permiso. Se espera HTTP 200 con
`previous_state: approved` y `permit_state: consumed`; cuatro eventos de
aplicación y cinco peticiones contando la captura. Lectura y conservación de
esa auditoría están autorizadas dentro del mismo bloque y siguen pendientes
de resultados reales. No se repiten los controles anteriores. Actas locales
posteriores a `5bf154a`, sin nuevo commit/push o llamadas al modelo.

### Atraque: aprobación normal, lectura y conservación en V2

Las capturas del propietario muestran:

| Campo | Evidencia visible |
| --- | --- |
| Ejecución | `7114fc01324c2531fac5eca89e131cbb` |
| Selección/estado | F6, `corrected`, `benign`, variante 1; `COMPLETED`, uso normal correcto |
| Solicitud/respuesta | `POST /avanzado/atraque`, HTTP 200; `previous_state: approved`, `permit_state: consumed` |
| Ejecutor y Apache | 5 peticiones, 5 líneas correlacionadas; V2 consultado: no |
| Auditoría del panel | 4 eventos / 4 referencias HTTP |
| V2 | Mismo identificador, modo corregido y 4 eventos; sin coincidencias de reglas |
| SHA-256 de auditoría mostrado en V2 | `0e18490747cd7527ac9a1c5db4459de31320efa222a04f28f7dcf4db4069f9d1` |
| Conservación | Mensaje de copia conservada, sin análisis solicitado |

Queda completado el control normal de aprobación y uso de permiso, con lectura
y conservación informada en V2. No acredita rechazo de una operación sin
aprobación, reutilización de permiso, las otras variantes, recibo local de esa
copia, hash independiente o respaldo/restauración de la nueva auditoría.

### Cierre del bloque de cuatro controles normales del 30/10

Los cuatro controles autorizados, modo corregido y variante 1, quedan
completados según capturas, cada uno con su lectura y mensaje de conservación
en V2. El control Cargas del día anterior permanece completado y no se repitió.

| Control normal | Fecha de recepción | Peticiones del ejecutor | Líneas Apache correlacionadas informadas | Eventos capturados y visibles en V2 |
| --- | --- | --- | --- | --- |
| Cargas | 29/10 | 3 | 3 | 2 |
| Bitácora | 30/10 | 4 | 4 | 3 |
| Preferencias | 30/10 | 3 | 3 | 2 |
| Baliza | 30/10 | 3 | 3 | 2 |
| Atraque | 30/10 | 5 | 5 | 4 |

El bloque reanudado suma 15 peticiones, 15 líneas correlacionadas informadas y
11 eventos. Incluido Cargas, son 18 peticiones, 18 líneas y 13 eventos. Estas
sumas proceden de las pantallas de cinco controles independientes: no se
ejecutó una suite nueva ni se verificaron los archivos de la VM por el agente.
Solo para Cargas se observó además el recibo local de la copia; para los otros
cuatro se observó la confirmación de conservación de la interfaz.

Se cierra **este bloque de controles normales**, no la fase F6 completa. Siguen
pendientes positivos/denegaciones por variante, comprobaciones de navegador,
aislamiento/regresión, recuperación de auditorías nuevas, evaluación del
detector y criterios de aceptación del PRD. No se reescriben el histórico
42/45, los JSON F5 o el análisis Groq previo. No hay una tasa global de falsas
alarmas derivada de estas cinco pantallas.

El alcance autorizado queda atendido: no se pide repetir los controles normales
ni se inicia otro caso o modelo sin acordar la continuación. Las cinco actas
locales permanecen posteriores a `5bf154a`, pendientes de commit/push; el código
operativo y los datos de la VM no se modifican por documentar este cierre.

### Publicación documental autorizada al cerrar el bloque normal

El 30/10 el propietario acepta publicar estas actas antes de ampliar las
pruebas. Se prepara commit/push con `[skip ci]` de cinco documentos: contexto
AGENTS, plan de cierre, estado consolidado, esta acta y guía de Parrot. La base
`5bf154a` coincide con `origin/main` tras fetch. No se incluyen código operativo,
datos, credenciales, imágenes, recibos originales de la VM o JSON históricos F5.

La identidad de esta entrega es el commit que incorpora esta nota; el push,
coincidencia de HEAD remoto y árbol local limpio se comprueban al terminar.
Las referencias anteriores a actas locales describen su estado en cada momento
de recepción. No se crea release, etiqueta o validación CI nueva.

Esta distribución no inicia escenarios, servicios, suites, llamadas al modelo
o notificaciones. Parrot puede recibirla con `git pull --ff-only`; al ser solo
documentación no requiere reinstalar, recompilar o reiniciar. No se repiten
los controles normales ni el análisis Groq para actualizar las actas.

### Continuación: primer control manual de rechazo corregido

La publicación documental se completó en
`d3e0b148bb1bc50c6430080dccd98456d04455e0`, con remoto coincidente y árbol
local limpio tras el push. El propietario solicita después «sigamos entonces
con lo siguiente». Se continúa la validación manual de rechazos, sin repetir
los controles normales, ejecutar suites o llamar al modelo.

El primer paso guiado es Cargas, modo corregido, tipo Intento de ataque,
variante 1 (`ext-idor-a1-corrected`). El ejecutor usa la identidad ficticia y
solicita `foreign-1`. Expectativa por código: HTTP 403 con
`error: object_not_authorized`, dos eventos capturados y, en el observador por
reglas de V2, «Acceso al objeto rechazado». En este caso 403 es el resultado
esperado del control, no un fallo por sí mismo. Se solicita lectura y
conservación de su auditoría después de comparar identificadores y conteos.

El resultado sigue pendiente de capturas reales; no se atribuye detección LLM,
explotación, protección universal o aceptación global a una expectativa. Este
paso no cambia a modo vulnerable, otras variantes o autoriza un nuevo análisis.
Notas locales posteriores a `d3e0b14`, sin otra publicación por continuar.

### Cargas: rechazo observado, regla visible y conservación confirmada

El propietario aporta resultado y auditoría V2; una captura adicional confirma
después la conservación que no aparecía en el primer recorte de V2:

| Campo | Evidencia visible |
| --- | --- |
| Ejecución | `808f223ac979bd1f3f60ca47ec3a31a1` |
| Selección/estado | F6, `corrected`, `attempt`, variante 1; `COMPLETED` |
| Solicitud/respuesta | `GET /avanzado/carga?documento=foreign-1`, HTTP 403, `error: object_not_authorized` |
| Ejecutor y Apache | 3 peticiones, 3 líneas correlacionadas; V2 consultado: no |
| Auditoría del panel | 2 eventos / 2 referencias HTTP |
| V2 | Mismo identificador, modo corregido y 2 eventos |
| SHA-256 mostrado por V2 | `60651569e6830b5c6032425f04514f3b64538afff307f59352521f3234844b24` |
| Regla visible | «Acceso al objeto rechazado», componente `cargo`, actor `estibador.demo`, recurso `foreign-1` |
| Conservación | Captura posterior con mensaje de copia conservada, sin análisis solicitado |

Se completa este recorrido manual de rechazo y conservación informada. Junto
con el control normal `own-1` anterior, se observa para variante 1 corregida
lectura propia permitida y recurso ajeno rechazado. No se extrapola a otras
variantes, modo vulnerable, protección universal o métricas del detector. La
observación de V2 procede de reglas sobre auditoría de aplicación, no del LLM.
No se ha aportado recibo local de esta copia o verificación independiente de
los archivos de la VM. No es necesario repetir Cargas.

Sigue el control HTTP de Preferencias, corregido/Intento de ataque/variante 1.
Expectativa por código: HTTP 403, `channel: normal`, `changed: false`, dos
eventos y la regla «Solicitud de otro origen rechazada» en V2. Se guía lectura
y conservación de la auditoría. La página de formulario entre orígenes y su
confirmación de navegador no forman parte de este paso HTTP; esa comprobación
sigue pendiente. Resultado de Preferencias pendiente de capturas reales.
Actas locales posteriores a `d3e0b14`, sin nueva publicación o llamadas al modelo.

### Preferencias: rechazo HTTP de origen/token y regla visible

Las dos capturas del propietario muestran:

| Campo | Evidencia visible |
| --- | --- |
| Ejecución | `1acb45412fdc9aa6ee6cb908da777a42` |
| Selección/estado | F6, `corrected`, `attempt`, variante 1; `COMPLETED` |
| Solicitud/respuesta | `POST /avanzado/preferencias`, HTTP 403; `channel: normal`, `changed: false` |
| Banner del panel | «Solicitud rechazada en la prueba HTTP de origen/token. Comprobación en navegador pendiente» |
| Ejecutor y Apache | 3 peticiones, 3 líneas correlacionadas; V2 consultado: no |
| Auditoría del panel | 2 eventos / 2 referencias HTTP |
| V2 | Mismo identificador, modo corregido y 2 eventos |
| SHA-256 mostrado por V2 | `4d36d94f3944815832d243192a3f7d1d74f8fc15b346d134967b3770fd2be43f` |
| Regla visible | «Solicitud de otro origen rechazada», componente `preferences`, actor `estibador.demo`, recurso `arrival_preferences` |
| Conservación | Mensaje de copia conservada, sin análisis solicitado |

Queda completado el rechazo HTTP de esta variante y su lectura/conservación
informada en V2. El resultado complementa el caso normal anterior; no separa
la eficacia individual de origen y token ni acredita un formulario real con
cookie, CSRF de navegador, otras variantes o protección universal. Los botones
de ejercicio/confirmación de navegador están visibles, sin evidencia de usarlos.
La comprobación de navegador permanece pendiente, como indica el panel.

Continúa Baliza/corregido/Intento de ataque/variante 1. El caso fijo solicita el
recurso lógico de diagnóstico; se espera HTTP 403,
`error: canary_resource_not_authorized`, dos eventos y «Lectura del señuelo
rechazada» en V2. Se guía lectura y conservación de esa auditoría, sin repetir
los casos ya observados. Baliza aún no tiene resultado de rechazo acreditado.
No hay ejecución de suites/LLM o de la VM por el agente; actas locales sin push.

### Baliza: diagnóstico rechazado, regla y conservación en V2

El propietario aporta las dos capturas del resultado y la auditoría:

| Campo | Evidencia visible |
| --- | --- |
| Ejecución | `1ee95d713c3577e55088ecc4cc083bba` |
| Selección/estado | F6, `corrected`, `attempt`, variante 1; `COMPLETED` |
| Solicitud/respuesta | `GET /avanzado/baliza?destino=umbral%3A%2F%2Fbeacon%2Fdiagnostic`, HTTP 403, `error: canary_resource_not_authorized` |
| Ejecutor y Apache | 3 peticiones, 3 líneas correlacionadas; V2 consultado: no |
| Auditoría del panel | 2 eventos / 2 referencias HTTP |
| V2 | Mismo identificador, modo corregido y 2 eventos |
| SHA-256 mostrado por V2 | `8baa6edbf9aa926f6aa29beb402c54857384f2b37992d7add7ed19c380fb6983` |
| Regla visible | «Lectura del señuelo rechazada», componente `beacon`, actor `estibador.demo`, recurso `umbral://beacon/diagnostic` |
| Conservación | Mensaje de copia conservada, sin análisis solicitado |

Queda completado este control corregido de rechazo, su lectura y conservación
informada en V2. Complementa la lectura pública permitida del control normal.
No acredita los otros destinos/variantes, protección SSRF general, inspección
independiente del aislamiento, comprobación de los bytes o recuperación de
esta copia. No se repite el caso ni se atribuye el resultado al modelo.

Sigue Atraque/corregido/Intento de ataque/variante 1. El caso predefinido intenta
utilizar `dock-1` sin aprobación previa; expectativa por código: HTTP 409,
`previous_state: pending`, `permit_state: pending`, dos eventos y «Aprobación
exigida» en V2, con posterior conservación. Este caso no comprueba reutilización
de un permiso consumido. Resultado de Atraque todavía pendiente de capturas.
Documentación local posterior a `d3e0b14`, sin nueva publicación o ejecución.

### Atraque: operación sin aprobación rechazada y conservada

Las capturas del propietario muestran:

| Campo | Evidencia visible |
| --- | --- |
| Ejecución | `554c8de8300762ce559b9aa38db564ff` |
| Selección/estado | F6, `corrected`, `attempt`, variante 1; `COMPLETED` |
| Solicitud/respuesta | `POST /avanzado/atraque`, HTTP 409; `previous_state: pending`, `permit_state: pending` |
| Ejecutor y Apache | 3 peticiones, 3 líneas correlacionadas; V2 consultado: no |
| Auditoría del panel | 2 eventos / 2 referencias HTTP |
| V2 | Mismo identificador, modo corregido y 2 eventos |
| SHA-256 mostrado por V2 | `42db1bc86a73e8bad691ac32177d9125ed4ce22abc7d8b3168d1f05462913bec` |
| Regla visible | «Aprobación exigida», componente `docking`, actor `estibador.demo`, recurso `dock-1` |
| Conservación | Mensaje de copia conservada, sin análisis solicitado |

Queda observado el rechazo sin aprobación de variante 1, junto a su regla y
conservación informada en V2. Complementa la aprobación/uso normal anterior;
no comprueba reutilización de un permiso ya consumido, otras variantes,
protección universal, recibo local o recuperación de esta copia.

Los rechazos HTTP corregidos de variante 1 de Cargas, Preferencias, Baliza y
Atraque quedan observados y conservados en pantalla. Preferencias sigue siendo
solo prueba HTTP de origen/token; su comprobación de navegador está pendiente.
No se declara F6 aceptada o evaluado el detector sobre todo el corpus.

Se continúa con Bitácora/corregido/Intento de ataque/variante 1, como control de
codificación, no de estado HTTP de denegación. Expectativa por código: HTTP
200, «Entrada codificada como texto en la respuesta», entidades HTML visibles
y entrada literal en el iframe opaco, sin ejecución JavaScript confirmada.
La vista V2 debe referir al mismo caso y tres eventos capturados; puede no
haber coincidencias al ser `encoded_text`. Se guía lectura y conservación,
recogiendo también el iframe para no deducir comportamiento de navegador del
HTTP 200 por sí solo. Esas observaciones nuevas todavía no están acreditadas.
Actas locales posteriores a `d3e0b14`, sin suites, modelos o nueva publicación.

### Bitácora: codificación observada en respuesta e iframe y copia en V2

Las tres capturas del propietario muestran:

| Campo | Evidencia visible |
| --- | --- |
| Ejecución | `d9d05054f32aae24a76b6fe5b2167552` |
| Selección/estado | F6, `corrected`, `attempt`, variante 1; `COMPLETED` |
| Solicitud/respuesta | `GET /avanzado/tablon?_run=d9d05054f32aae24a76b6fe5b2167552`, HTTP 200; entrada con entidades HTML |
| Banner del panel | «Entrada codificada como texto en la respuesta» |
| Ejecutor y Apache | 4 peticiones, 4 líneas correlacionadas; V2 consultado: no |
| Auditoría del panel | 3 eventos / 3 referencias HTTP |
| Iframe | «Bitácora de turno», entrada literal visible como texto y «Sin ejecución confirmada» |
| V2 | Mismo identificador, modo corregido y 3 eventos; sin coincidencias de reglas |
| SHA-256 mostrado por V2 | `ccff12955e46717b15e2c39af5854c0975681dbef9075defd75234e6aa84fc3e` |
| Conservación | Mensaje de copia conservada, sin análisis solicitado |

Se completa este recorrido de codificación observada y presentación como texto
en el iframe, con lectura y conservación informada de la auditoría en V2. No
se deduce ausencia universal de JavaScript ni protección de otras entradas o
variantes. La ausencia de coincidencias de estas reglas no es una métrica del
modelo o del detector completo. No se ha leído un recibo local o verificado
independientemente los bytes de esta copia.

### Cierre de la ronda corregida de variante 1

| Caso predefinido, modo corregido | Resultado observado | Auditoría V2 y conservación |
| --- | --- | --- |
| Cargas, intento variante 1 | 403, recurso ajeno rechazado | 2 eventos, regla de acceso rechazado, copia confirmada en pantalla |
| Preferencias, intento variante 1 | 403, `changed: false` en prueba HTTP de origen/token | 2 eventos, regla de otro origen rechazado, copia confirmada en pantalla |
| Baliza, intento variante 1 | 403, diagnóstico del señuelo rechazado | 2 eventos, regla de lectura rechazada, copia confirmada en pantalla |
| Atraque, intento variante 1 | 409, permiso sin aprobación sigue pendiente | 2 eventos, regla de aprobación exigida, copia confirmada en pantalla |
| Bitácora, intento variante 1 | 200, respuesta codificada e iframe con texto literal | 3 eventos, sin coincidencias de reglas, copia confirmada en pantalla |

Queda completada esta ronda específica de cuatro rechazos HTTP y un control de
codificación, a partir de las capturas. Se conservan los cinco controles
normales previos y no se repiten para cerrar esta ronda. No se declara
aceptación F6 completa: siguen pendientes CSRF de navegador, reutilización de
permiso, modo vulnerable y otras variantes, aislamiento/regresión del MVP,
recuperación de auditorías nuevas y evaluación independiente del detector.

El siguiente candidato es CSRF de navegador en modo corregido. Necesitará una
ejecución nueva que prepare sesión y ventana temporal: el último reset de
Bitácora invalida el contexto antiguo de Preferencias. No se reutiliza aquel
identificador ni se inicia la nueva ejecución sin acordar su alcance. La
autorización Groq previa continúa consumida; no se plantean nuevas llamadas.
Documentación local posterior a `d3e0b14`, sin commit/push o suites nuevas.

### Recorrido CSRF de navegador corregido expresamente autorizado

El propietario responde afirmativamente a un único recorrido manual con sesión
ficticia, control normal del portal, formulario desde el otro origen y lectura/
conservación de auditoría en V2. Incluye una preparación nueva de Preferencias,
corregido/Intento de ataque/variante 1, porque el contexto anterior quedó
invalidado por el reset posterior. No es una repetición del control HTTP para
reescribir su resultado: genera otro identificador para la comprobación de
navegador y conserva los recibos previos. No incluye suites o modelo.

Se guían los pasos seguidos dentro de los cinco minutos desde la primera
petición del caso: ejecutar preparación una vez, abrir el ejercicio entre
orígenes, crear sesión en el portal, usar «Control normal desde este origen»,
volver al ejercicio y enviar el formulario del otro origen, y confirmar en el
panel con «Comprobar evidencia del navegador». No se restablece ni cambia de
escenario entre esos pasos. Las respuestas esperadas son `changed: true` para
el formulario normal y `changed: false` para el cruzado, conservando `normal`.

La confirmación del controlador exige un evento de preferencias con cookie,
origen cruzado e identificador de petición ajeno al ejecutor HTTP. La secuencia
única descrita produciría cinco eventos de aplicación: dos de preparación,
sesión de navegador, formulario normal y formulario cruzado. Recapturar para
confirmar lleva el contador del ejecutor a cuatro; las peticiones del navegador
no se contabilizan como solicitudes de ese ejecutor. Son expectativas del
código, no resultados observados. Pueden verse dos observaciones de rechazo
distintas, la del control HTTP y la del formulario, bajo el mismo título.

Se solicitarán capturas de las dos respuestas, del panel confirmado y de V2
tras actualizar y conservar la auditoría del identificador nuevo. La cookie y
tokens se gestionan desde el propio formulario; no se piden credenciales o
cabeceras al propietario. Resultado y aceptación continúan pendientes. El
agente no opera la VM; acta local posterior a `d3e0b14`, sin nuevo commit/push.

### Recepción del recorrido CSRF en navegador corregido — 30/10/2026

Las cuatro capturas posteriores del propietario acreditan el recorrido autorizado:

| Campo | Evidencia visible |
| --- | --- |
| Ejecución nueva | `fe73eb53a5030885bb395eeb7613ac5c` |
| Formulario normal del portal | URL del portal corregido 4382 con ese `_run`; `channel: normal`, `changed: true` |
| Formulario desde el otro origen | Misma URL e identificador; `channel: normal`, `changed: false` |
| Selección y confirmación | F6, `corrected`, `attempt`, variante 1, `COMPLETED`; «Formulario de otro origen con sesión del navegador rechazado» |
| Respuesta mostrada en panel | `POST /avanzado/preferencias`, HTTP 403, `changed: false` |
| Ejecutor y Apache | 4 peticiones del ejecutor, 7 líneas correlacionadas; V2 consultado por el ejecutor: no |
| Auditoría en panel | 5 eventos / 2 referencias HTTP |
| Lectura V2 | Misma ejecución, modo corregido y 5 eventos |
| SHA-256 mostrado en V2 | `8a20bd0c954eca1f91e4fa667c386c8412abb333af8aabc00ee17790b304f2ae` |
| Observaciones V2 | Dos entradas «Solicitud de otro origen rechazada», componente `preferences`, actor `estibador.demo`, recurso `arrival_preferences` |
| Conservación | «Copia de auditoría conservada en V2 para su respaldo. No se ha solicitado un análisis» |

Queda **completado este recorrido manual corregido de navegador**, incluida
la respuesta normal, el rechazo cruzado, la confirmación del panel y la lectura/
conservación informada en V2. Los contadores son coherentes con la preparación,
las tres peticiones del navegador y la recaptura descritas antes. Las peticiones
del navegador no se suman al contador del ejecutor; las dos referencias HTTP
del lote no representan todo el tráfico del recorrido.

Las dos observaciones del mismo título son coherentes con el rechazo de la
sonda HTTP inicial y el del formulario de navegador. Las capturas no muestran
los identificadores individuales de esos eventos, por lo que no se afirma una
comparación independiente del lote ni un defecto de duplicación. El SHA es el
mostrado por V2; no se han leído los bytes, recalculado su hash, inspeccionado
el recibo local o restaurado esta copia desde Windows.

Esta recepción resuelve el pendiente específico de CSRF en navegador corregido,
variante 1. No acepta toda F6/F7 ni demuestra protección universal o métricas
del modelo. Siguen pendientes reutilización de permiso, modo vulnerable,
otras variantes, aislamiento/regresión y evaluación. No repetir este recorrido;
el siguiente candidato es Atraque corregido, intento variante 3, con alcance
manual por acordar antes de iniciarlo. Solo se actualizan actas locales,
posteriores a `d3e0b14`; sin nueva ejecución, modelo, suite o commit/push.

### Siguiente caso autorizado: reutilización de permiso corregida

Tras completar CSRF de navegador, el propietario solicita seguir con el
siguiente caso propuesto. Se guía un único caso manual Atraque/corregido/
Intento de ataque/variante 3 (`ext-workflow-a3-corrected`), con lectura y
conservación de su auditoría en V2, sin suites o llamadas al modelo.

La revisión del controlador y el target muestra esta preparación interna al
pulsar una sola vez «Ejecutar escenario local»: sesión de operador, sesión de
supervisor, aprobación de `dock-3`, primer uso permitido y segundo uso. La
última respuesta esperada es HTTP 409 con `previous_state: consumed` y
`permit_state: consumed`. No se pide ejecutar dos veces el caso desde el panel:
la reutilización ya está incluida en esta variante predefinida.

Incluida la captura de auditoría, se esperan 6 peticiones del ejecutor y 5
eventos / 5 referencias HTTP. V2 debe mostrar el nuevo identificador, modo
corregido y «Reutilización del permiso rechazada» para `dock-3`. Se solicitarán
capturas del resultado y de V2 tras actualizar y conservar la copia. Son
expectativas de código; la ejecución y conservación siguen pendientes de
evidencia del propietario. Este alcance no acepta F6 completa ni autoriza
otras variantes, modo vulnerable, suites, modelo o publicación Git.

### Recepción: reutilización de permiso corregida — 30/10/2026

Las dos capturas del propietario muestran:

| Campo | Evidencia visible |
| --- | --- |
| Ejecución | `b1aa23bd017b47ec814fe8d3c52ecd2e` |
| Selección y estado | F6, `corrected`, `attempt`, variante 3; `COMPLETED` |
| Solicitud final | `POST /avanzado/atraque`, HTTP 409 |
| Estado del permiso | `previous_state: consumed`, `permit_state: consumed` |
| Ejecutor y Apache | 6 peticiones, 6 líneas correlacionadas; V2 consultado por el ejecutor: no |
| Auditoría del panel | 5 eventos / 5 referencias HTTP |
| V2 | Misma ejecución, modo corregido y 5 eventos |
| SHA-256 mostrado por V2 | `4403bb5865d9ed8ba2180a7c5eaa2a207ca727ac5733fa82e89cbce23f3d56b` |
| Observación por reglas | «Reutilización del permiso rechazada», `docking`, actor `estibador.demo`, recurso `dock-3` |
| Conservación | Copia de auditoría conservada en V2 para respaldo; sin análisis solicitado |

Se completa el recorrido manual autorizado de reutilización corregida:
la segunda utilización se rechaza y el permiso permanece consumido. Los
contadores coinciden con la preparación y captura previstas; las pantallas
no sustituyen una inspección independiente de cada evento. No se ha leído
el recibo local, recalculado el hash de los bytes o restaurado esta copia.
No se repite el caso ni los controles normales o CSRF ya observados.

Los pendientes específicos de navegador CSRF corregido y reutilización de
permiso corregida quedan resueltos a sus respectivos alcances. **F6 completa
sigue abierta**: otros modos/variantes, aislamiento/regresión y evaluación
siguen pendientes. F7 permanece desarrollada sin ejecución observada. El
próximo bloque propuesto es comenzar su revisión manual por Configuración,
modo corregido, Uso normal, variante 1; requiere acordar ese nuevo alcance.
Son revisiones educativas de artefactos ficticios, no aceptación global de
categorías OWASP ni detección completa por el modelo. Solo se actualizan
actas locales posteriores a `d3e0b14`, sin suites, modelos o publicación Git.

### Distribución documental autorizada tras reutilización — 30/10/2026

El propietario solicita commit/push antes de continuar. La entrega incorpora
cuatro archivos: esta acta, el plan de cierre, el estado consolidado y AGENTS.
Recoge las observaciones manuales posteriores a `d3e0b14` y actualiza la tabla
vigente del plan para reflejar CSRF en navegador y reutilización corregida ya
observados. Las notas de preparación anteriores conservan su orden histórico;
no se interpretan como pendientes actuales cuando existe una recepción posterior.

Se publica con `[skip ci]`; su identidad será la del commit que contiene esta
nota. Se comprueban base remota, contenido preparado, coincidencia de HEAD
remoto y limpieza local al terminar. No incluye código operativo, datos de la
VM, secretos o nuevas ejecuciones. Parrot puede recibir esta entrega con
`git pull --ff-only`; al ser documental no necesita recompilar, reinstalar o
reiniciar por estos cambios. No se repiten casos o el análisis Groq. Esta
distribución no acepta F6 global o F7 ni inicia el siguiente caso propuesto.

### Primer recorrido F7 autorizado: Configuración normal corregida

La entrega documental anterior se publicó en
`dc9fb1746a8c43be2324d5c78cf072df36a3f6ab`, con remoto coincidente y árbol
local limpio tras el push. El propietario solicita seguir con el siguiente
bloque propuesto: un caso manual Configuración · réplica de diagnóstico,
modo corregido, Uso normal, variante 1 (`ext-configuration-b1-corrected`),
seguido de lectura y conservación de auditoría en V2. No incluye suites o LLM.

Se revisa el código sin importarlo o ejecutarlo. El botón del panel pasa a
«Revisar artefacto ficticio». Se espera una respuesta HTTP 200 con
`provenance: fictional_artifact_review`, `topic: configuration`, `fixture:
fixture-1`, `debug_enabled: false`, configuración con `service: beacon-demo`
y `observation: minimal_configuration`. Los indicadores
`production_security_claim` y `observed_fixture_effect` deben ser `false`.
Se trata de una revisión educativa de un artefacto, no de una comprobación
de la configuración real del despliegue o de una explotación.

La secuencia incluye sesión ficticia, revisión y captura: expectativa de 3
peticiones del ejecutor y 2 eventos / 2 referencias HTTP. V2 puede mostrar
«No hay coincidencias de estas reglas»: sus reglas de estado F6 no evalúan el
contenido del artefacto F7. Se comparará el identificador nuevo y se conservará
su copia. Resultado pendiente de capturas del panel y de V2 con confirmación
de conservación; no se da por aceptada F7. Notas locales posteriores a
`dc9fb17`, sin nueva publicación, servicios, suites o llamadas al modelo.

### Configuración normal corregida: ejecución y lectura observadas

Las dos capturas del propietario muestran:

| Campo | Evidencia visible |
| --- | --- |
| Ejecución | `608700e1fe2c6d7d91f4f275a770a56a` |
| Selección y estado | F7, `corrected`, `benign`, variante 1; `COMPLETED`, «Uso normal completado correctamente» |
| Origen y solicitud | Revisión de artefacto ficticio mediante HTTP; `GET /avanzado/revision?topic=configuration&variant=0&kind=benign`, HTTP 200 |
| Contenido | `fictional_artifact_review`, `configuration`, `fixture-1`; `debug_enabled: false`, `service: beacon-demo`, `minimal_configuration` |
| Límites declarados en respuesta | `production_security_claim: false`, `observed_fixture_effect: false` |
| Ejecutor y Apache | 3 peticiones, 3 líneas correlacionadas; V2 consultado por el ejecutor: no |
| Auditoría en panel | 2 eventos / 2 referencias HTTP |
| Lectura V2 | Misma ejecución, modo corregido y 2 eventos; sin coincidencias de estas reglas |
| SHA-256 mostrado en V2 | `86170cfde0364edc7b16a05999b091f1d9a10bdb8636e63c601285673650bf16` |
| Conservación | Botón visible, sin mensaje de copia conservada en el recorte aportado |

La ejecución y la lectura en V2 quedan completadas a este alcance. **Falta
confirmar la conservación**: se guía únicamente el botón «Conservar copia de
auditoría en V2» para esta auditoría y la captura del mensaje de confirmación.
No se repite el caso ni se solicita análisis. La ausencia de coincidencias
de las reglas F6 no evalúa el artefacto F7; tampoco se demuestra configuración
de producción o aceptación global de F7. Sin inspección independiente de bytes
o recibo local nuevo. Notas locales posteriores a `dc9fb17`, sin commit/push.

### Configuración: conservación confirmada y recorrido normal completado

La captura posterior de V2 muestra el mismo identificador
`608700e1fe2c6d7d91f4f275a770a56a`, modo corregido, 2 eventos y SHA
`86170cfde0364edc7b16a05999b091f1d9a10bdb8636e63c601285673650bf16`.
Incluye el mensaje «Copia de auditoría conservada en V2 para su respaldo.
No se ha solicitado un análisis».

Queda **completado el recorrido Configuración/corregido/Uso normal/variante 1**
según capturas: respuesta esperada del artefacto ficticio, lectura en V2 y
conservación informada. No se repite ni se requieren más capturas de este
recorrido. No se ha inspeccionado un recibo local nuevo o verificado de forma
independiente el contenido de la copia. La ausencia de coincidencias de reglas
F6 no evalúa el contenido F7 ni la seguridad del despliegue real.

F7 global continúa pendiente. El siguiente candidato propuesto es Suministro ·
procedencia del artefacto, modo corregido, Uso normal, variante 1; su ejecución
no se inicia por recibir esta captura. Actas locales posteriores a `dc9fb17`,
sin nuevo commit/push, suite, servicio o llamada al modelo.

### Siguiente recorrido autorizado F7: Suministro normal corregido

El propietario acepta continuar con el siguiente caso propuesto: Suministro ·
procedencia del artefacto, modo corregido, Uso normal, variante 1
(`ext-supply_chain-b1-corrected`), con lectura y conservación de auditoría en V2.
Se guía una pulsación de «Revisar artefacto ficticio», sin suites o LLM.

La revisión de código muestra una comparación SHA-256 con una referencia local
fija para el artefacto ficticio sin modificar. Se espera HTTP 200,
`expected_sha256` igual a `received_sha256`, `accepted: true`,
`trusted_reference: fixed_local_fixture`, `observation: digest_comparison` y
`observed_fixture_effect: false`. La respuesta identifica `supply_chain`,
`fixture-1`, `fictional_artifact_review` y `production_security_claim: false`.
Esto no instala paquetes ni verifica la procedencia de una dependencia real;
la referencia confiable es parte del ejercicio local.

Se esperan 3 peticiones del ejecutor y 2 eventos / 2 referencias HTTP. V2 puede
quedar sin coincidencias porque las reglas F6 no evalúan ese contenido F7.
Se solicitarán resultado y lectura V2 del mismo identificador nuevo, con el
mensaje de conservación visible. Resultado pendiente de capturas; no se repite
Configuración ni se declara F7 aceptada. Notas locales posteriores a `dc9fb17`,
sin commit/push o ejecución de servicios/VM por el agente.

### Suministro normal corregido: resultado y conservación observados

Las dos capturas del propietario muestran:

| Campo | Evidencia visible |
| --- | --- |
| Ejecución | `d34aba7e1dfae17f750c1ac7c8722be1` |
| Selección y estado | F7, `corrected`, `benign`, variante 1; `COMPLETED`, «Uso normal completado correctamente» |
| Solicitud | `GET /avanzado/revision?topic=supply_chain&variant=0&kind=benign`, HTTP 200 |
| Artefacto | `fictional_artifact_review`, `supply_chain`, `fixture-1`, referencia `fixed_local_fixture` |
| Comparación | Hashes esperado y recibido iguales, `accepted: true`, `observation: digest_comparison` |
| Límites de respuesta | `production_security_claim: false`, `observed_fixture_effect: false` |
| Ejecutor y Apache | 3 peticiones, 3 líneas correlacionadas; V2 consultado por el ejecutor: no |
| Auditoría del panel | 2 eventos / 2 referencias HTTP |
| Lectura V2 | Misma ejecución, modo corregido y 2 eventos; sin coincidencias de reglas |
| SHA-256 mostrado por V2 | `7228d4f84c4a97a2624a31595e4846d15bf510e16d80c0fdd03890c77a0667d9` |
| Conservación | Copia de auditoría conservada en V2 para respaldo; sin análisis solicitado |

Queda **completado el recorrido normal de Suministro corregido, variante 1**,
con lectura y conservación informada en V2. No se repite ni se solicitan más
capturas para este recorrido. La comparación visual del artefacto no verifica
procedencia de paquetes reales; no se han recalculado sus bytes o inspeccionado
el recibo local de esta copia. La ausencia de observaciones F6 no evalúa el
contenido F7 ni aporta métricas del modelo.

Configuración y Suministro normales corregidos quedan observados y conservados
según capturas. F7 global permanece abierta. El siguiente candidato propuesto
es Criptografía · codificar o proteger, corregido/Uso normal/variante 1; su
ejecución requiere la continuación del propietario y no se inicia por recibir
estas imágenes. Solo actas locales posteriores a `dc9fb17`, sin nuevo
commit/push, suites o llamadas al modelo.

### Siguiente recorrido autorizado F7: Criptografía normal corregida

El propietario acepta el siguiente caso propuesto: Criptografía · codificar o
proteger, corregido/Uso normal/variante 1 (`ext-cryptography-b1-corrected`),
con lectura y conservación de auditoría en V2. Se guía una pulsación de
«Revisar artefacto ficticio», sin suites o LLM. Configuración y Suministro no
se repiten.

La lectura del código muestra una derivación `scrypt` sobre una contraseña
ficticia, con sal aleatoria. Se espera HTTP 200, `storage_method: scrypt`,
`salt` y `stored_fixture` con valores, `observation: salted_password_derivation`,
`provenance: fictional_artifact_review`, `topic: cryptography`, `fixture-1`,
`production_security_claim: false` y `observed_fixture_effect: false`. No se
fija el valor de sal o derivación ni se repite el caso para compararlos.
La respuesta declara parámetros educativos; no es una auditoría criptográfica
de producción.

Se esperan 3 peticiones del ejecutor y 2 eventos / 2 referencias HTTP. Las
reglas F6 de V2 pueden quedar sin coincidencias, sin evaluar el contenido F7.
Resultado y copia pendientes de capturas del panel y V2 con el mismo nuevo
identificador y confirmación de conservación. Actas locales `dc9fb17`+, sin
commit/push, servicios, modelos o ejecución de la VM por el agente.

### Criptografía normal corregida: ejecución y lectura observadas

Las dos capturas aportadas muestran:

| Campo | Evidencia visible |
| --- | --- |
| Ejecución | `8fa4ffafefc52573988c36dd75fbcbb5` |
| Selección y resultado | F7, `corrected`, `benign`, variante 1; «Uso normal completado correctamente» |
| Solicitud | `GET /avanzado/revision?topic=cryptography&variant=0&kind=benign`, HTTP 200 |
| Artefacto | `fictional_artifact_review`, `cryptography`, `fixture-1` |
| Derivación mostrada | `storage_method: scrypt`, `salt` y `stored_fixture` con valores; `salted_password_derivation` |
| Límites de respuesta | `production_security_claim: false`, `observed_fixture_effect: false`; nota de parámetros educativos |
| Ejecutor y Apache | 3 peticiones, 3 líneas correlacionadas; V2 consultado por el ejecutor: no |
| Auditoría del panel | 2 eventos / 2 referencias HTTP |
| Lectura V2 | Misma ejecución, modo corregido y 2 eventos; sin coincidencias de reglas |
| SHA-256 mostrado por V2 | `76632c81fba7f53964684bf7effe03c281ec1a9330846862e20727fcd9dd7052` |
| Conservación | Botón visible, sin mensaje de copia conservada en el recorte |

Ejecución y lectura quedan observadas. **Conservación pendiente de confirmación
visual**: se guía solo «Conservar copia de auditoría en V2» y la captura del
mensaje para esta auditoría, sin repetir el caso. No se recalcula la derivación
o compara con una ejecución nueva; la sal es aleatoria. La respuesta no supone
una auditoría criptográfica de producción, y las reglas F6 no evalúan el
contenido F7. No se han inspeccionado bytes o recibo local nuevos. Actas locales
posteriores a `dc9fb17`, sin commit/push, suites o llamadas al modelo.

### Criptografía: conservación confirmada y recorrido normal completado

La captura posterior de V2 muestra la misma ejecución
`8fa4ffafefc52573988c36dd75fbcbb5`, modo corregido, 2 eventos y SHA
`76632c81fba7f53964684bf7effe03c281ec1a9330846862e20727fcd9dd7052`.
Incluye «Copia de auditoría conservada en V2 para su respaldo. No se ha
solicitado un análisis».

Queda **completado el recorrido Criptografía/corregido/Uso normal/variante 1**
según capturas: respuesta esperada del artefacto ficticio, lectura y conservación
informada en V2. No se repite ni se solicitan más capturas para este recorrido.
No se han inspeccionado bytes o recibo local nuevos; no equivale a una auditoría
criptográfica de producción o evaluación del contenido F7 por las reglas F6.

Configuración, Suministro y Criptografía normales corregidos, variante 1,
quedan observados y conservados en pantalla. F7 global sigue abierta. El
siguiente candidato propuesto es Integridad · manifiesto de carga, corregido/
Uso normal/variante 1; no se inicia otro caso por recibir esta captura. Solo
actas locales posteriores a `dc9fb17`, sin commit/push, suites o llamadas LLM.

### Siguiente recorrido autorizado F7: Integridad normal corregida

El propietario acepta el caso propuesto Integridad · manifiesto de carga,
corregido/Uso normal/variante 1 (`ext-integrity-b1-corrected`), con lectura y
conservación de auditoría en V2, sin suites o modelo. Se guía una pulsación de
«Revisar artefacto ficticio». No se repiten los tres casos normales anteriores.

Por lectura del código se espera HTTP 200, `accepted: true`,
`verification: hmac_sha256`, `observation: manifest_checked`,
`provenance: fictional_artifact_review`, `topic: integrity`, `fixture-1`,
`production_security_claim: false` y `observed_fixture_effect: false`.
Es una comprobación HMAC del manifiesto ficticio sin modificar, con una clave
interna en memoria; no se pide mostrarla ni se verifican manifiestos reales.

Se esperan 3 peticiones del ejecutor y 2 eventos / 2 referencias HTTP. V2
puede quedar sin coincidencias porque las reglas F6 no evalúan el contenido F7.
Resultado y copia pendientes de capturas del panel y V2 con el mismo nuevo
identificador y mensaje de conservación. Actas locales posteriores a `dc9fb17`,
sin commit/push, servicios, suites, LLM o ejecución de la VM por el agente.

### Integridad normal corregida: resultado y conservación observados

Las dos capturas del propietario muestran:

| Campo | Evidencia visible |
| --- | --- |
| Ejecución | `38d690cd4161439e73f4d38df256e0d1` |
| Selección y estado | F7, `corrected`, `benign`, variante 1; `COMPLETED`, «Uso normal completado correctamente» |
| Solicitud | `GET /avanzado/revision?topic=integrity&variant=0&kind=benign`, HTTP 200 |
| Artefacto y verificación | `fictional_artifact_review`, `integrity`, `fixture-1`; `accepted: true`, `verification: hmac_sha256`, `observation: manifest_checked` |
| Límites de respuesta | `production_security_claim: false`, `observed_fixture_effect: false` |
| Ejecutor y Apache | 3 peticiones, 3 líneas correlacionadas; V2 consultado por el ejecutor: no |
| Auditoría del panel | 2 eventos / 2 referencias HTTP |
| Lectura V2 | Misma ejecución, modo corregido y 2 eventos; sin coincidencias de reglas |
| SHA-256 mostrado por V2 | `6f76a58a30318cdb1ae9fce21d0b553db0fc2bbd8ee5fe498cedea5cf35061f1` |
| Conservación | Copia de auditoría conservada en V2 para respaldo; sin análisis solicitado |

Queda **completado el recorrido normal de Integridad corregida, variante 1**,
con lectura y conservación informada en V2. No se repite ni se solicitan más
capturas para este recorrido. No se verifican manifiestos reales ni se han
inspeccionado los bytes o recibo local de esta copia. La ausencia de
observaciones de reglas F6 no evalúa el contenido F7.

Configuración, Suministro, Criptografía e Integridad normales corregidos,
variante 1, quedan observados y conservados en pantalla. F7 global permanece
abierta. El siguiente candidato propuesto es Registro · huecos y avisos,
corregido/Uso normal/variante 1; no se inicia por recibir estas capturas.
Actas locales posteriores a `dc9fb17`, sin commit/push, suites o llamadas LLM.

### Siguiente recorrido autorizado F7: Registro normal corregido

El propietario acepta el caso propuesto Registro · huecos y avisos, corregido/
Uso normal/variante 1 (`ext-logging-b1-corrected`), con lectura y conservación
de auditoría en V2, sin suites o modelo. Se guía una pulsación de «Revisar
artefacto ficticio» y no se repiten los cuatro controles normales anteriores.

La lectura de código muestra una secuencia ficticia completa. Se espera HTTP
200, `sequence_fixture: [1, 2, 3, 4, 5]`, `missing_sequence: []`,
`warning_recorded: false` y `observation: no_warning`; además de
`fictional_artifact_review`, `logging`, `fixture-1` y ambos indicadores
`production_security_claim` / `observed_fixture_effect` en `false`.
La ausencia de aviso es la expectativa del control normal sin huecos. No
comprueba continuidad real de Apache, rotación o entrega de notificaciones.

Se esperan 3 peticiones del ejecutor y 2 eventos / 2 referencias HTTP. V2
puede mostrar ausencia de coincidencias de reglas F6, sin evaluar el contenido
F7. Resultado y copia pendientes de capturas del panel y V2 con el mismo nuevo
identificador y mensaje de conservación. Notas locales posteriores a `dc9fb17`,
sin commit/push, servicios, suites, LLM o ejecución de la VM por el agente.

### Registro normal corregido: resultado y conservación observados

Las dos capturas del propietario muestran:

| Campo | Evidencia visible |
| --- | --- |
| Ejecución | `2c26ab55cda7b3e95eccfbf5080580b2` |
| Selección y estado | F7, `corrected`, `benign`, variante 1; `COMPLETED`, «Uso normal completado correctamente» |
| Solicitud | `GET /avanzado/revision?topic=logging&variant=0&kind=benign`, HTTP 200 |
| Artefacto | `fictional_artifact_review`, `logging`, `fixture-1` |
| Secuencia y aviso | `sequence_fixture: [1,2,3,4,5]`, `missing_sequence: []`, `warning_recorded: false`, `observation: no_warning` |
| Límites declarados | `production_security_claim: false`, `observed_fixture_effect: false`; nota de secuencia ficticia |
| Ejecutor y Apache | 3 peticiones, 3 líneas correlacionadas; V2 consultado por el ejecutor: no |
| Auditoría del panel | 2 eventos / 2 referencias HTTP |
| Lectura V2 | Misma ejecución, modo corregido y 2 eventos; sin coincidencias de reglas |
| SHA-256 mostrado por V2 | `141d4822e72b628901569cd0c888504a6de982e1ccff084f8e7cab07e1b25800` |
| Conservación | Copia de auditoría conservada en V2 para respaldo; sin análisis solicitado |

Queda **completado el recorrido normal de Registro corregido, variante 1**,
con lectura y conservación informada en V2. No se repite ni se solicitan más
capturas para este recorrido. La secuencia es ficticia: no verifica continuidad
real de Apache, rotación o entrega de avisos. Tampoco se ha inspeccionado el
recibo local o recalculado el hash de los bytes de esta copia. La ausencia de
observaciones de reglas F6 no evalúa el contenido F7.

Quedan observados y conservados en pantalla cinco controles normales F7
corregidos, variante 1: Configuración, Suministro, Criptografía, Integridad y
Registro. El siguiente candidato propuesto es Excepciones · respuesta
controlada, corregido/Uso normal/variante 1; todavía sin iniciar. F7 global
sigue abierta. Solo actas locales posteriores a `dc9fb17`, sin commit/push,
suites o llamadas al modelo.

### Último control normal autorizado: Excepciones y cierre de la sesión

El propietario solicita realizar Excepciones · respuesta controlada,
corregido/Uso normal/variante 1 (`ext-exceptions-b1-corrected`), seguido de
commit/push y continuar mañana. El caso incluye lectura y conservación de
auditoría en V2, sin suites o modelo. Se guía una pulsación de «Revisar
artefacto ficticio». Los cinco controles normales anteriores no se repiten.

Por lectura del código se espera HTTP 200, `observation: controlled_response`,
`error: null`, `provenance: fictional_artifact_review`, `topic: exceptions`,
`fixture-1`, `production_security_claim: false` y
`observed_fixture_effect: false`; 3 peticiones del ejecutor y 2 eventos /
2 referencias HTTP. Puede no haber coincidencias de reglas F6. Resultado y
conservación siguen pendientes de capturas. Este uso normal no comprueba aún
la respuesta ante una condición de error o la ausencia universal de filtraciones.

Tras recibir las capturas se registrará el resultado observado, se revisarán
y publicarán las cuatro actas pendientes con `[skip ci]`, y se verificará HEAD
remoto y árbol limpio. Esta publicación está expresamente autorizada; no se
ejecuta antes de documentar el caso. Después se guardará el punto para mañana
y se detendrá el trabajo sin iniciar otros casos, servicios o modelos, ni
crear recordatorios automáticos. F7 global y demás criterios siguen abiertos.

### Excepciones normal corregida: resultado y conservación observados

Las dos capturas del propietario muestran:

| Campo | Evidencia visible |
| --- | --- |
| Ejecución | `b4ca524b483be65d9549d6b132f25fe7` |
| Selección y estado | F7, `corrected`, `benign`, variante 1; `COMPLETED`, «Uso normal completado correctamente» |
| Solicitud | `GET /avanzado/revision?topic=exceptions&variant=0&kind=benign`, HTTP 200 |
| Artefacto | `fictional_artifact_review`, `exceptions`, `fixture-1` |
| Respuesta | `observation: controlled_response`, `error: null` |
| Límites declarados | `production_security_claim: false`, `observed_fixture_effect: false` |
| Ejecutor y Apache | 3 peticiones, 3 líneas correlacionadas; V2 consultado por el ejecutor: no |
| Auditoría del panel | 2 eventos / 2 referencias HTTP |
| Lectura V2 | Misma ejecución, modo corregido y 2 eventos; sin coincidencias de reglas |
| SHA-256 mostrado por V2 | `986bd32dd2af9aa895727d63a325b73d79b3c1eb904f3f46dea787b57e00a012` |
| Conservación | Copia de auditoría conservada en V2 para respaldo; sin análisis solicitado |

Queda **completado el recorrido normal de Excepciones corregida, variante 1**,
con lectura y conservación informada en V2. No se repite. El uso normal no
demuestra todavía respuesta ante errores o ausencia universal de filtraciones.
No se han inspeccionado bytes o recibo local de esta copia; las reglas F6 no
evalúan el contenido F7.

### Cierre de la ronda normal F7 y pausa solicitada

Los seis controles siguientes, todos corregido/Uso normal/variante 1, quedan
completados según capturas, con lectura y conservación informada en V2:

| Control | Ejecución observada |
| --- | --- |
| Configuración | `608700e1fe2c6d7d91f4f275a770a56a` |
| Suministro | `d34aba7e1dfae17f750c1ac7c8722be1` |
| Criptografía | `8fa4ffafefc52573988c36dd75fbcbb5` |
| Integridad | `38d690cd4161439e73f4d38df256e0d1` |
| Registro | `2c26ab55cda7b3e95eccfbf5080580b2` |
| Excepciones | `b4ca524b483be65d9549d6b132f25fe7` |

Cada caso informa HTTP 200, 3 peticiones del ejecutor, 3 líneas correlacionadas
y 2 eventos / 2 referencias HTTP; no se consideran una suite automática o una
evaluación de detección. Los resultados específicos y sus límites están arriba.
**La ronda normal queda cerrada; F7 global permanece abierta.** No repetir
estos casos para cerrar la sesión. Siguen pendientes condiciones adversas,
otros modos/variantes, validaciones ampliadas y evaluación del contenido.

El propietario ya autorizó publicar las cuatro actas con `[skip ci]` tras
este caso y continuar mañana. La entrega se identifica por el commit que
contiene esta nota; se revisan base remota/diff/staging y se verifica HEAD
remoto y árbol limpio al terminar. Solo documentación: actualizar Parrot por
`git pull --ff-only` no requiere recompilar, reinstalar o reiniciar por esta
entrega. Las notas anteriores «local/sin publicar» conservan su contexto histórico.

Después de publicar se pausa el trabajo. Al retomar, leer el punto del plan
de cierre y el estado que comunique el propietario, sin asumir servicios VM
abiertos. El siguiente bloque propuesto son condiciones adversas de los
artefactos F7 en modo corregido, variante 1, con alcance manual por acordar;
todavía no están autorizadas ni se ejecutan durante la pausa. Sin modelos,
suites, nuevos servicios o recordatorios automáticos.

## Referencias de diseño

- [OWASP Top 10:2025](https://top10.owasp.org/2025/): categorías del mapa educativo.
- [Prevención de IDOR](https://cheatsheetseries.owasp.org/cheatsheets/Insecure_Direct_Object_Reference_Prevention_Cheat_Sheet.html): autorización por objeto y usuario.
- [Prevención de CSRF](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html): token y comprobación de origen.
- [Prevención de SSRF](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html): destinos permitidos y límites de conectividad.

Consultadas el 29/10/2026. Son referencias de diseño; no certifican esta
implementación. La guía de Sites se aplica en modalidad local, preservando el
Site privado F1 y sin desplegar allí el backend del laboratorio.
