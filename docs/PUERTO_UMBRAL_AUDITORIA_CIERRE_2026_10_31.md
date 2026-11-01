# Puerto Umbral integrado en V2 — auditoría de pendientes de cierre

**Estado consolidado al 02/11:** el lanzador conjunto y la revisión básica de
ambas interfaces ya cuentan con recepción posterior en Parrot. No se repiten
estos recorridos para cerrar actas. El
[resumen de entrega](PUERTO_UMBRAL_ENTREGA_2026_11_02.md) distingue tres bloques
técnicos abiertos —funcionamiento/regresión, operación y evaluación— de la
decisión final de aceptación y de la cobertura adicional.

Recepción posterior del 02/11: cinco regresiones aisladas del lanzador
ejecutadas con permiso explícito, **5/5 correctas, exit 0**, Windows/Python
3.11.9; procesos/HTTP simulados, sin modelo. La
[verificación prioritaria](CIERRE_VERIFICACION_PRIORITARIA_2026_11_02.md)
registra alcance y los dos recorridos manuales posteriores de comandos,
completados por capturas: normal corregido y vulnerable representativo de
variante 1 con efecto real, sin `Cannot fork`, timeout o retorno distinto de 0.
No se amplía la suite ni se acepta toda la regresión por este resultado.

Baliza vulnerable mantiene su resultado funcional sin recibir. El historial
estrecho del 01/11 incluye el prefijo `525a2076b8ae`, pero no HTTP, efecto o
recibo evaluable. No se concluye que nunca se ejecutó ni se cuenta como
aprobado. El recorrido aplazado por el propietario no se reejecuta o reformula
para eludir el bloqueo comunicado.

**Último resultado funcional F6 recibido, 31/10:** Cargas vulnerable, Intento, variante 1,
completado por capturas: acceso al señuelo `foreign-1` de otro propietario,
regla V2 observada y copia conservada sin análisis. Run
`176266c5fd701ecdfa637ba14f0d6a34`, HTTP 200, 2 eventos, SHA de auditoría
`2956f103989b75c515c0320b871eb2558cb5b93f425bd6d4b3b2db4cbc6d38d2`.
Comparación puntual con rechazo corregido previo completada, sin aceptación F6
global o métricas del modelo. No repetir caso/copia.

**Respaldo previo, 31/10:** respaldo actualizado del perfil completado según
salida del propietario: 113 archivos, `verified: true`, `missing: []`, destino
`.local-backups/operational-20261031T201154664036Z`. La restauración independiente
adicional sigue aplazada; las propuestas anteriores no autorizan ejecutarla.
El respaldo precede al recorrido Cargas vulnerable recibido después; no se
presenta como copia de todas las evidencias posteriores.

Revisión inicial: 31/10/2026; consolidación: 02/11/2026, Europe/Madrid.
Revisión de código, documentación y evidencias
ya registradas, con recepción posterior de lecturas y respaldo manuales del
propietario. **El agente no accede a Parrot ni inicia escenarios, modelos,
suites o aceptación de fases.** El alcance solicitado sigue siendo
F0–F7; ninguna desviación se acepta por silencio o por la fecha de publicación.
La entrega base V2 v0.1.0 conserva su identidad y validaciones: este documento
revisa la ampliación Puerto Umbral, sin reabrir ni renombrar aquella entrega.

## Fuentes y regla de revisión

- [PRD y criterios originales](PRD_PUERTO_UMBRAL_2026_10_26.md).
- [Prototipo F1 y revisión adaptable inicial](PUERTO_UMBRAL_F1_2026_10_26.md).
- [Revisión del corpus histórico F5](PUERTO_UMBRAL_F5_2026_10_27.md) y sus JSON,
  que permanecen intactos.
- [Ronda operativa básica F4](PUERTO_UMBRAL_F4_2026_10_27.md).
- [Análisis único y recuperación aislada](PUERTO_UMBRAL_ANALISIS_ACOTADO_2026_10_27.md).
- [Acta F6/F7](PUERTO_UMBRAL_F6_F7_2026_10_29.md) y
  [matriz educativa F7](PUERTO_UMBRAL_F7_CIERRE_EDUCATIVO_2026_10_31.md).
- [Límites del proceso de comandos](../labs/puerto_umbral/lab/target.py),
  [topología declarada](../labs/puerto_umbral/lab/compose.yaml) y
  [catálogo de ampliaciones](../labs/puerto_umbral/lab/advanced_catalog.py),
  leídos sin importar o ejecutar la aplicación.

Se distingue requisito literal del PRD, evidencia observada, cobertura adicional
y propuesta de ejecución. Un pendiente histórico queda resuelto por su recepción
posterior dentro del alcance acreditado; no se solicita repetirlo para actualizar
un documento antiguo. «No observado» no significa «fallido» o «obligatorio».

## Recorridos ya completados que no se repetirán por este cierre

| Evidencia | Resultado disponible | Límite que se mantiene |
| --- | --- | --- |
| Archivo histórico F2/F5 | 45 casos tienen recibo y snapshot o causa de fallo; 42 conformes HTTP y 3 comandos con `Cannot fork`; 92 archivos revisados offline | No es 45/45 funcional ni evaluación del código actual o del detector |
| Snapshot → modelo → informe V2 | Un snapshot de 17 líneas, trabajo `f5b674c867994aeba3beeb4a638d7a33`, 3 solicitudes, 8150 tokens, 3 grupos altos y 1 medio; publicación y lectura observadas | No es evaluación de 30 intentos/15 benignos; coste real del proveedor no medido |
| Seguimiento F4 básico | Inicio, reutilización, pausa/reanudación, parada, duración y cierre/reapertura sin auto-resume observados | No aporta veinte latencias individuales o rotación/truncado real |
| Respaldo/restauración básica | 66 archivos, sin faltantes, SQLite y publicación verificados en recuperación aislada del perfil | No cubre por sí solo auditorías creadas después; no es recuperación de toda la VM |
| F6 corregida y comparación Cargas | Cinco normales, cinco intentos de variante 1, formulario CSRF en navegador y reutilización de permiso corregidos; Cargas vulnerable variante 1 con efecto observado; lectura y conservación V2 informadas | Comparación Cargas acreditada a su alcance; otros efectos avanzados y regresión del MVP pendientes |
| F7 representativa | Once recorridos corregidos/variante 1 con lectura y conservación V2 informadas; matriz de objetivos/evidencias/límites preparada | No es 54/54, evaluación del detector o validación de todas las categorías |
| Lanzador y producto, 01/11 | Lectura → manual disponible → parada → lectura; navegación básica de cinco vistas V2, informe anterior abierto, ambas interfaces en vista estrecha y foco confirmado a su alcance | No nuevo análisis, suite ejecutada, revisión exhaustiva de controles o accesibilidad global; detalle en la revisión de producto |

## Cinco grupos de trabajo y estado actualizado

Son grupos de cierre, **no cinco pruebas ni autorizaciones para ejecutarlas**.

| ID | Grupo | Qué falta realmente | Qué no se añade como requisito |
| --- | --- | --- | --- |
| C-01 | Funcionamiento, límites y regresión F2/F6 | Corrección de comandos verificada en recorrido representativo; efectos avanzados distintos, límites funcionales afectados y regresión justificada siguen pendientes | No repetir los dos recorridos de comandos o los normales completados ni ejecutar 99 entradas solo por existir en el catálogo |
| C-02 | Operación F3/F4 | Salud ante fuente inválida/discontinuidad, latencia requerida o desviación revisada, no duplicación/trabajos y regresión de perfiles | El ciclo básico de cierre/retorno a lectura está recibido; no confundir el cierre del backend con desconexión de la fuente ni exigir todas las interrupciones imaginables |
| C-03 | Evaluación y alcance F5 | Medir objetivos del detector con un plan autorizado, o preparar una decisión expresa que cambie el alcance de entrega y deje esa evaluación pendiente | No transformar cuatro grupos del informe en cuatro aciertos de corpus; no iniciar otro Groq con el permiso consumido |
| C-04 | Conservación de evidencias | Respaldo del perfil seleccionado del 31/10 con verificación interna: 113 archivos, sin faltantes; selección de auditorías y hash puntual recibidos | No cubre automáticamente Cargas vulnerable o evidencias posteriores; restauración adicional aplazada; originales bajo `labs/` fuera del perfil; no recuperación de toda la VM |
| C-05 | Producto, documentación y aceptación | Revisión básica de ambas interfaces completada; documentación consolidada; revisión final del propietario y decisión de entrega pendientes | Zoom 200 %, exportación y revisión exhaustiva siguen sin observarse, sin convertirse en cuotas nuevas del PRD; no crear release o publicar LinkedIn por cerrar documentación |

## Matriz de los criterios que condicionan el MVP y F6

Los estados siguientes son dictámenes de esta revisión de evidencia, no una
aceptación del propietario o resultado de pruebas nuevas.

| Criterio PRD | Evidencia y dictamen al 02/11 | Trabajo mínimo pendiente o decisión |
| --- | --- | --- |
| F2-AC1: efecto vulnerable, corrección y uso benigno | Históricos 42/45 preservados; el 02/11 se identifica la fuente corregida en imagen y pasan normal corregido y vulnerable variante 1, con salida real/retorno 0 y sin `Cannot fork` | Incidencia verificada como corregida en el recorrido representativo; no repetirlo ni cambiar a superadas las variantes 2/3 históricas sin reejecución; aceptación y regresión globales siguen separadas |
| F2-AC2: efecto demostrado, no solo HTTP 200 | SQL/traversal, marcador XSS y ahora comandos vulnerable variante 1 con identidad `uid=10001(umbral)` observados | El efecto de este recorrido de comandos está acreditado por cuerpo real, sin puntuar todo el corpus o detector |
| F2-AC3: reset conserva evidencia y separa perfiles | Recibos anteriores visibles mientras se ejecutan nuevos casos; separación implementada | Cotejo acotado de conservación y separación efectiva de datos/perfiles en la versión final |
| F2-AC4: límites XSS/traversal/comandos | Contratos revisados, verificaciones iniciales F2 y después inspección agregada válida de 14 contenedores/red frontal aportada por el propietario | Perímetro configurado actual observado mediante inspector; los límites funcionales afectados y regresión siguen pendientes, sin solicitar destinos ajenos |
| F3-AC1: petición/snapshot con línea y hash | Captura y lectura observadas; revisión offline de snapshots y hashes históricos | Recorrido básico acreditado; no repetir para documentarlo |
| F3-AC2: trabajo consume snapshot identificado y publica referencias | Un análisis identificado y su informe visible completados | Recorrido básico acreditado; no repetir el modelo |
| F3-AC3: ausencia/corrupción/antigüedad no se muestra como ausencia de ataques | Captura antigua y fuentes incompletas visibles; tratamiento de publicación ausente/corrupta revisado en código | Verificación negativa acotada de las ramas no observadas, sin sobrescribir evidencia válida |
| F3-AC4: pilot/legacy conservan comportamiento y datos | Código y contratos compatibles revisados; rondas nuevas usaron el perfil Puerto Umbral | Regresión de perfiles con alcance concreto; instalar o arrancar Puerto no la acredita |
| F4-AC1: veinte ciclos cumplen objetivo de diez segundos o desviación revisada | Historial conserva últimas duraciones, no veinte muestras; observador preparado con cinco pruebas aisladas autorizadas y correctas, sin medición Parrot todavía | Obtener medición y revisar su alcance: el observador conserva cota de disponibilidad API, no paint del navegador; RNF-09/desviación requieren revisión expresa; no afirmar cumplimiento a partir del contador |
| F4-AC2: sin cambios no duplica eventos ni crea trabajos | Contadores de sesiones conservadas respaldan reutilización; lectura SQLite del 02/11 muestra un único trabajo posterior a las dos sesiones cerradas y cero entregas | Relación temporal corroborada para esas dos sesiones con registros conservados; no equivale a deduplicación exhaustiva de archivos/eventos; tercera sesión guardada sin fin requiere consultar estado actual |
| F4-AC3: desconexión/rotación/reinicio visibles, evidencia conservada | Error de red al cerrar V2 y reapertura sin auto-resume; API actual del 02/11 confirma interrupted/process_interrupted, sesión inactiva y checkpoint antiguo conservado | Interrupción de proceso visible corroborada; sigue pendiente comportamiento de la fuente ante discontinuidad/rotación; el checkpoint histórico no prueba salud actual de la pasarela |
| F4-AC4: pausa/parada sin ciclos o procesos propios huérfanos | Secuencia básica completa, supervisor revisado, preflight del 31/10 sin bloqueadores y ciclo del lanzador conjunto lectura/manual/parada/lectura del 01/11 recibidos | Cierre básico y comprobaciones de puertos/locks/contenedores acreditados a ese alcance; no implica inspección exhaustiva del host, cierre durante un trabajo activo o suite de regresión ejecutada; no repetir la secuencia básica |
| F4-AC5: seguimiento sin LLM ni notificaciones | Separación arquitectónica; ningún trabajo conservado coincide con las dos sesiones cerradas del 27/10; cero entregas registradas en SQLite el 02/11 | Corroboración acotada de trabajos/entregas conservados, sin inferir una auditoría del proveedor; tercera sesión sin fin no permite cerrar su intervalo; no iniciar un modelo para comprobarlo |
| F5-AC1: 45 resultados/evidencias o causa de fallo | Los 45 históricos tienen registro y causa, incluidos los tres fallos | **Registro histórico cubierto** en su alcance; el criterio no exige por sí solo otra ejecución completa de 45. Esto no resuelve F2-AC1 o regresión de la versión actual |
| F5-AC2: objetivos de detección o decisión expresa de alcance | Objetivos 27/30 intentos, 5/6 por familia y cero falsas alarmas entre 15 benignos siguen sin medir | Bloqueo de aceptación: evaluación propia autorizada o decisión expresa documentada sobre cambio de alcance; una entrega no evaluada no cumple los objetivos originales por renombrarla |
| F5-AC3: separar intento, bloqueo, efecto y evidencia insuficiente | Actas, informe y matriz educativa distinguen estas clases | Conservar el criterio en la revisión editorial final; no exige repetir casos ya observados |
| F5-AC4: instalación/cierre en plataforma objetivo | Instalación V2 previa, actualización/build/arranque/cierre del laboratorio en Parrot documentados | Acreditado para instalación existente y recorridos observados; no exigir reinstalar de cero por este criterio ni certificar otras plataformas nuevas |
| F5-AC5: originales, presupuesto y límites conservados | Archivos históricos revisados, consumo del único análisis registrado, recuperación aislada de 66 archivos y posterior respaldo de 113 archivos con verificación interna observados | Conservación acreditada para las selecciones y fechas correspondientes, sin extenderla automáticamente a evidencia posterior; originales `labs/` separados y restauración adicional aplazada; coste real no medido |
| F6-AC1: acceso indebido con identidad/recurso/política | Lecturas propias permitidas y ajenas rechazadas; Cargas vulnerable variante 1 devuelve el recurso ajeno y V2 lo registra/conserva según capturas; aprobaciones y consumo corregidos observados | Comparación puntual Cargas completada; otros efectos avanzados vulnerables y regresión siguen pendientes |
| F6-AC2: SSRF confinada al señuelo | Lectura pública y rechazo de recurso interno corregidos; Unix HTTP sin DNS/IP en código; inspección con `valid=True`, 14 contenedores y targets sin red IP; fila vulnerable en historial sin resultado funcional | Perímetro configurado observado; efecto vulnerable sin evidencia recibida y recorrido aplazado; no se solicita repetirlo, probar Internet o host |
| F6-AC3: CSRF entre orígenes sin afectar al control | Formulario normal aceptado y cruzado rechazado en navegador corregido observados | Efecto vulnerable y separación del control aún sin observar; no repetir el recorrido corregido |
| F6-AC4: detector sin etiquetas/veredictos esperados | Separación catálogo/contrato/lector en código, observaciones V2 sobre campos de negocio; fuente distinta del informe LLM | Revisión acotada del lote/recibo real si se exige comprobación operativa completa; no requiere nuevas llamadas LLM para revisar el contrato |
| F6-AC5: positivos/negativos y regresión | Negativos corregidos y normales observados; positivo Cargas vulnerable variante 1 con efecto, regla y conservación observados; corpus base conservado | Otros positivos representativos y regresión justificada pendientes; no interpretar tres variantes declaradas como una orden de 99 ejecuciones |

F1 ya registra vistas adaptables 390/768/1440 en las pantallas del prototipo
comprobadas; no se borra esa evidencia. La interfaz local posterior cuenta ahora
con revisión básica del propietario en vista estrecha y teclado a su alcance,
según el acta de producto; no es accesibilidad global o aprobación final F0–F7.
La matriz F7
prepara sus tres criterios educativos, sin borrar la dependencia de F6 ni las
validaciones reales F4–F5 relacionadas con operación/avisos.

## Cobertura adicional y decisiones pendientes

Completar todas las variantes F6/F7, restaurar toda la VM, repetir el análisis
de 17 líneas o reinstalar todas las plataformas no son requisitos nuevos que
añada esta auditoría. Las variantes conservan estado no observado y no se
puntúan como superadas. Una cobertura representativa debe justificar qué
comportamientos distintos comprueba y mantener los fallos visibles.

F5-AC2 exige una decisión del propietario porque la evaluación está sin medir.
La restricción vigente impide nuevas llamadas al modelo. Se mantiene el
objetivo completo mientras no se decida otra cosa: no se acepta una entrega
piloto o aplazamiento por defecto. Una eventual desviación debe nombrar los
criterios no cumplidos, evidencia disponible y afirmaciones permitidas; no
convertir lo pendiente en aprobado.

El mismo tratamiento se aplica al objetivo temporal de F4: el PRD admite una
desviación revisada, pero todavía no se ha aceptado ninguna. La ausencia de
decisión no equivale a conformidad.

## Orden recomendado para continuar

1. Usar el resumen de entrega como estado vigente. Inspección de perímetro,
   recibo/hash/listado/respaldo y revisión básica de interfaces ya recibidos
   no se reabren por sus instrucciones históricas.
2. Continuar por operación F3/F4, con alcance concreto antes de nuevas
   sesiones o cambios de fuente. Las cinco regresiones aisladas y el bloque
   representativo de comandos están completados a su alcance; no repetirlos.
   El resto del plan funcional/operativo se vincula a criterios abiertos sin
   extender las autorizaciones anteriores a otra suite o al modelo.
3. Resolver separadamente el plan de evaluación/presupuesto F5 o una decisión
   expresa de alcance; el objetivo completo sigue vigente mientras no se decida.
4. Revisar con el propietario resultados, matriz educativa F7 y documentación
   V2 para la decisión final de entrega. Conservación se declara por selección
   y fecha; no se añade una nueva restauración independiente aplazada.

El README y las guías vigentes se sincronizan con las observaciones actuales.
Los JSON históricos y las actas de su momento se conservan; sus enlaces de
actualización remiten aquí. No se ha publicado Git, creado release o alterado
datos operativos por esta revisión documental.

Comprobación documental inicial del paquete: 12 Markdown, 147 referencias locales sin
ausencias, `git diff --check` correcto y ningún JSON histórico modificado.
Es verificación de documentación, no una prueba funcional de la aplicación.

Consolidación del 02/11: nueve Markdown modificados/nuevos, 120 referencias
locales comprobadas sin ausencias; sin cambios en código de aplicación,
corpus JSON o datos operativos. Esta revisión es local y no publica Git.

## Cronología de lecturas y conservación recibidas

Las secciones siguientes conservan la preparación y recepción de cada paso
desde el 31/10. Sus propuestas pendientes se resuelven por las recepciones
posteriores; no son una lista actual de acciones por repetir. Para el estado
vigente se usan las tablas anteriores y el resumen de entrega del 02/11.

### Lectura manual autorizada del perímetro

En una segunda terminal de Parrot, desde la raíz del repositorio y sin cerrar
el lanzador actual, se guía el comando existente:

```bash
.p2/bin/python -B labs/puerto_umbral/labctl.py inspect
```

La lectura de `labctl.py` confirma que `inspect` llama directamente a
`inspect_boundary`, sin adquirir `ProcessLock`, escribir estado o iniciar
servicios. Lee `labs/puerto_umbral/.local-state/f2/images.json`, inspecciona los
catorce contenedores propios y su red frontal. No ejecuta `docker exec`, sondas
HTTP, casos, ciclos de seguimiento o llamadas al modelo. El agente solo revisa
el código local; no opera la VM.

La comprobación compara propiedad e imagen con el manifiesto, usuario,
rootfs de solo lectura, capacidades/privilegios/namespaces/dispositivos,
límites CPU/memoria/PID y montajes. Los targets deben tener red `none` y ningún
puerto publicado; las pasarelas, sus volúmenes de solo lectura, puertos 4380 y
4382 solo en `127.0.0.1`, red frontal exclusiva y opciones de masquerade/ICC
desactivadas. No verifica por sí sola los procesos host Flask/Next/control,
la regresión funcional o todas las formas de aislamiento.

Se ofrece un filtro de presentación de JSON por stdin, sin modificar archivos:

```bash
.p2/bin/python -B labs/puerto_umbral/labctl.py inspect |
.p2/bin/python -B -c '
import json, sys
raw = sys.stdin.read()
if not raw.strip():
    raise SystemExit("Sin informe; conserva el error mostrado antes de esta línea.")
r = json.loads(raw)
for key in ("valid", "targets_network_none", "gateway_masquerade", "gateway_intercontainer_connectivity"):
    print(key, "=", r[key])
print("Contenedores:", len(r["containers"]))
for c in r["containers"]:
    print("{} | activo={} | red={} | solo_lectura={} | usuario={}".format(c["service"], c["running"], c["network"], c["root_readonly"], c["user"]))
'
```

Expectativa: `valid: true`, 14 contenedores, `targets_network_none: true`,
`gateway_masquerade: false`, `gateway_intercontainer_connectivity: false`;
12 targets con red `none` y dos pasarelas en la red frontal, todos activos,
usuario `10001:10001` y raíz de solo lectura. Son expectativas por código;
**resultado actual pendiente de captura del propietario**. El resumen no
conserva el detalle de IDs/imágenes, aunque el inspector los compara.

Si faltan contenedores/manifiesto, están detenidos o una propiedad se rechaza,
se recogerá el error antes de otra acción. Esta autorización de lectura no
inicia `prepare`, `start`, `stop`, reinstalaciones o correcciones automáticas.

## Recepción de la inspección actual — 31/10

La captura del propietario muestra `valid = True`, `targets_network_none = True`,
`gateway_masquerade = False`, `gateway_intercontainer_connectivity = False` y
`Contenedores: 14`. Las once filas visibles (sqli, xss, traversal, command y
brute en ambos modos, más advanced-vulnerable) muestran actividad, red `none`,
raíz de solo lectura y usuario `10001:10001`.

El recorte no incluye advanced-corrected o las dos pasarelas ni IDs/imágenes.
El inspector revisado solo devuelve `valid=True` después de comprobar los
catorce contenedores y la red frontal. Por tanto queda **completada la lectura
del perímetro actual según la salida agregada del inspector aportada**, sin
atribuir una inspección independiente del agente o detalle no visible. No se
pide repetir la lectura para completar el recorte.

Esta evidencia acredita la comprobación de configuración efectiva que hace
el inspector, incluidos bindings/montajes/privilegios/límites/red, dentro del
alcance del código revisado. No completa F2/F6 por sí sola: sigue pendiente
el efecto funcional vulnerable, regresión, procesos host y operación ampliada.

## Lectura siguiente: recibo V2 existente

Se guía en la misma terminal, desde la raíz, sin activar otros servicios:

```bash
.p2/bin/python -B -m json.tool \
  .local-state/puerto-umbral/application-audit/current.json
```

Es lectura y presentación de JSON con la biblioteca estándar, sin importar la
aplicación o escribir archivos. No recaptura, repite casos o consulta un modelo.
Por el último caso conservado se esperan `run_id:
a8a228ff56fc61649041b9740731cc86`, modo `corrected`, 2 eventos, `schema_version:
1`, fuente `puerto-umbral-application`, `analysis_requested: false` y
`notifications_requested: false`. El `original_sha256` esperado es
`119efb666258c11506d5bd44c739de2df4620beb5a47a7434f369abc78034773`.

El `sha256` de la copia puede diferir del original por la serialización canónica
del JSON. Leer el recibo no recalcula los bytes de `events.json` ni verifica
todavía un respaldo. Resultado pendiente de captura. Si falta el archivo o hay
otro resultado, se recoge la salida sin repetir el caso o la copia para hacerlo
coincidir con la expectativa.

## Recepción del recibo local existente — 31/10

La captura de `python -m json.tool` muestra:

| Campo | Valor observado |
| --- | --- |
| `run_id` | `a8a228ff56fc61649041b9740731cc86` |
| `source` / `schema_version` | `puerto-umbral-application` / 1 |
| `mode` / `events` | `corrected` / 2 |
| `evidence_kind` / `execution_status_at_capture` | `fixture_review` / `completed` |
| `observer_version` | `puerto-umbral-audit-observer-1` |
| `captured_at` | `2026-10-31T19:11:24.961181+00:00` |
| `snapshot_id` | `891a00db10ca4bcda8a73f5d33fb10a0` |
| `original_sha256` | `119efb666258c11506d5bd44c739de2df4620beb5a47a7434f369abc78034773` |
| `sha256` de la copia | `bf41223489600b2429eab07b2cd9d08e589372ed9fefa4cd70900e330b1177fa` |
| Solicitud de análisis / notificaciones | `false` / `false` |

Los metadatos coinciden con el último caso conservado y el hash original
mostrado por V2. **Lectura de metadatos completada según captura**; no se
repite caso, copia o esta lectura para documentarla. La diferencia entre hash
original y de copia es compatible con la serialización canónica prevista.
La captura todavía no recalcula el archivo de eventos ni verifica un respaldo.

Se guía la siguiente lectura de bytes del snapshot ya identificado, desde la
raíz y sin escribir archivos:

```bash
sha256sum \
  .local-state/puerto-umbral/application-audit/snapshots/891a00db10ca4bcda8a73f5d33fb10a0/events.json
```

Debe compararse con el `sha256` de la copia:
`bf41223489600b2429eab07b2cd9d08e589372ed9fefa4cd70900e330b1177fa`,
no con `original_sha256`. Esta lectura no importa la aplicación, consulta el
target o repite el caso, y no modifica el snapshot. Resultado pendiente de
captura. Si falta el archivo o difiere el digest, se registra la salida antes
de recapturar, sobrescribir o corregir nada.

## Hash de los bytes guardados recibido — 31/10

La captura del propietario muestra `sha256sum` aplicado a
`application-audit/snapshots/891a00db10ca4bcda8a73f5d33fb10a0/events.json` y
el resultado `bf41223489600b2429eab07b2cd9d08e589372ed9fefa4cd70900e330b1177fa`.
Coincide exactamente con el `sha256` de la copia del recibo observado.

Queda **comprobada la integridad puntual de ese archivo frente a su recibo,
según la salida de la herramienta aportada por el propietario**. No se repite
caso, copia o hash para registrarlo. No se atribuye acceso directo del agente,
validación de todos los snapshots o del esquema de eventos, ni un respaldo o
restauración nuevos. El hash original conserva su vínculo con el recibido por
el controlador; esta lectura verifica los bytes de la copia canónica.

## Consulta siguiente de selección de respaldo, sin crear copia

La lectura del código de `scripts/backup_operational.py` confirma que `--list`
solo llama a `collect_sources` e imprime `sources` y `missing`: enumera rutas
permitidas existentes. No llama a `backup`, adquiere locks, abre una instantánea
SQLite o crea ZIP. Importa auxiliares de almacenamiento/publicación sin iniciar
la aplicación o un modelo; se usa `-B` para evitar archivos de bytecode.

Se guía esta consulta y se filtra su salida para la última auditoría:

```bash
.p2/bin/python -B scripts/backup_operational.py --profile puerto-umbral --list |
.p2/bin/python -B -c '
import json, sys
raw = sys.stdin.read()
if not raw.strip():
    raise SystemExit("Sin listado; conserva el error anterior.")
r = json.loads(raw)
s = r["sources"]
p = ".local-state/puerto-umbral/application-audit/"
last = p + "snapshots/891a00db10ca4bcda8a73f5d33fb10a0/"
print(json.dumps({
    "recibo_actual": s.get(p + "current.json", "NO_INCLUIDO"),
    "eventos_ultima_copia": s.get(last + "events.json", "NO_INCLUIDO"),
    "recibo_ultima_copia": s.get(last + "receipt.json", "NO_INCLUIDO"),
    "archivos_auditoria_en_lista": sum(k.startswith(p) for k in s),
    "faltantes": r["missing"]
}, indent=2))
'
```

Se espera `file` en las tres rutas, sin fijar el total de archivos de auditoría
antes de observarlo. La lista de faltantes se recoge tal cual. Resultado
pendiente de captura; un listado no demuestra respaldo creado o restauración.
Los recibos originales bajo `labs/puerto_umbral/.local-state/f2` son evidencia
separada del perfil V2 y no se consideran incluidos por estas tres rutas.
No ejecutar el comando sin `--list` o crear respaldos/restauraciones por esta
lectura; cualquier escritura se concretará después dentro de su alcance.

## Selección de respaldo recibida — 31/10

La captura posterior del listado filtrado muestra:

| Campo | Valor observado |
| --- | --- |
| `recibo_actual` | `file` |
| `eventos_ultima_copia` | `file` |
| `recibo_ultima_copia` | `file` |
| `archivos_auditoria_en_lista` | 47 |
| `faltantes` | `[]` |

Queda **comprobada la selección de las tres rutas de la última auditoría y
47 archivos de auditoría en el listado**, sin faltantes informados por el
selector del perfil. No demuestra un ZIP creado, integridad de los 47 archivos,
validez de sus esquemas o recuperación nueva. Tampoco transforma el conteo de
archivos en un número de snapshots completos o casos evaluados. Los originales
del laboratorio bajo `labs/puerto_umbral/.local-state/f2` siguen siendo evidencia
separada del perfil V2 y deben conservarse; este listado no afirma respaldarlos.
No se repite esta ronda de lecturas para documentarla.

## Propuesta concreta de escritura para conservar la evidencia posterior

La siguiente propuesta se prepara **sin ejecutarla ni darla por autorizada**.
El bloque acordado hasta ahora era de solo lectura; este paso crea archivos.
Se propone autorizar conjuntamente una copia actualizada del perfil y su
comprobación mediante el restaurador independiente, en una secuencia manual
guiada con capturas:

1. Cerrar la consola propia desde su terminal para dejar inactivas las
   operaciones del perfil, conservando datos y volúmenes.
2. Ejecutar una vez:

   ```bash
   .p2/bin/python -B scripts/backup_operational.py --profile puerto-umbral
   ```

   Crea un directorio nuevo `.local-backups/operational-<fechaUTC>/` con ZIP,
   manifiesto, snapshot SQLite y verificación interna en `restore-check`.
   Comprobar `verified: true`, `missing: []`, el número real de archivos y la
   ruta devuelta antes de continuar; no fijar un total a partir de los 47
   archivos de auditoría, pues el perfil incluye más fuentes.
3. Usar únicamente la ruta real de esa salida para:

   ```bash
   .p2/bin/python -B scripts/restore_operational.py --backup RUTA_REAL_DEL_RESPALDO
   ```

   El restaurador revisado valida manifiesto/archivo, crea un árbol nuevo
   `.local-state/recovery/restore-<fechaUTC>/`, compara hashes y comprueba SQLite
   y publicación estructurada. No permite destino live elegido por el operador
   ni inicia los datos recuperados o reproduce entregas.
4. Leer el resultado y la copia recuperada de la última auditoría para verificar
   inclusión del snapshot `891a00db10ca4bcda8a73f5d33fb10a0` y conservación del
   recibo/eventos. No ejecutar un escenario o modelo para comprobarlo.

Es una copia nueva de la evidencia posterior, no repetición del recorrido de
66 archivos del 29/10. La herramienta conserva originales y no borra copias
fallidas; no se promueven datos recuperados al estado activo. La aprobación
de esta secuencia seguirá pendiente hasta respuesta expresa del propietario;
si se concede, no se vuelve a solicitar por cada subpaso ya incluido. No
autoriza suites, modelos, Git, recuperación de toda la VM o archivo separado
de los originales del laboratorio por inferencia.

## Decisión posterior: solo respaldo nuevo con verificación interna

El propietario pregunta para qué sirve la propuesta y si es necesaria. Se
aclara que la ronda educativa F7 no necesita otra restauración independiente
para avanzar, que la recuperación básica anterior ya fue comprobada y que
el respaldo previo no cubre las auditorías posteriores. Se recomienda una
copia actualizada con la verificación interna existente. El propietario acepta
«ok hagamos eso».

El alcance autorizado es **una ejecución de respaldo del perfil Puerto Umbral
con su verificación interna**, sin restauración independiente adicional. Se
guía cerrar la consola propia con Ctrl+C y esperar el prompt para evitar
operaciones concurrentes; desde la raíz ejecutar una sola vez:

```bash
.p2/bin/python -B scripts/backup_operational.py --profile puerto-umbral
```

Esta vez se omite `--list` porque la escritura ya está autorizada. La herramienta
crea un directorio nuevo bajo `.local-backups`, un ZIP/manifiesto y la instantánea
SQLite, y ejecuta `verify_restore` en `restore-check` dentro del propio respaldo.
Ese control interno compara archivos/hashes y la integridad SQLite antes de
devolver `verified: true`. No sustituye datos activos o elimina originales.

Se solicitará la salida completa con `destination`, `files`, `verified` y
`missing`. Expectativa: `verified: true`, `missing: []`, sin anticipar el total
de archivos. Resultado pendiente de captura. No ejecutar
`restore_operational.py`; el árbol independiente de recuperación y su revisión
adicional quedan aplazados, sin contarlos como verificados.

Si el respaldo falla, conservar originales y artefactos parciales y revisar
la salida antes de repetir o corregir. No se ejecutan suites de escenarios,
modelos, notificaciones, Git o servicios nuevos por esta autorización. El
agente solo guía al propietario en Parrot y registra evidencia aportada.

## Respaldo actualizado completado — 31/10

La captura del propietario muestra la ejecución del comando autorizado y:

| Campo | Valor observado |
| --- | --- |
| Destino, relativo a raíz | `.local-backups/operational-20261031T201154664036Z` |
| Archivos | 113 |
| Verificación interna | `true` |
| Faltantes | `[]` |

Queda **completado el respaldo actualizado del perfil con su verificación
interna según salida de la herramienta**. No se repite para documentarlo.
El resultado es coherente con la selección previa de 47 archivos de auditoría
y más fuentes del perfil; el resumen no es una inspección independiente del
ZIP o manifiesto por el agente. Se conserva la copia y los originales.

La conservación básica del perfil seleccionado queda acreditada a ese alcance.
Los originales de `labs/` siguen fuera de este perfil; la restauración
independiente adicional permanece aplazada. No se atribuyen a esta salida
recuperación de toda la VM, validación funcional de escenarios o aceptación
global F5/F6. La recuperación aislada independiente del 29/10 conserva su
evidencia histórica y tampoco se repite.

## Siguiente comprobación de cierre sin arrancar la aplicación

Se revisa la rama `check` de `webdefense.py` y `scripts/start_application.py`,
el preflight de `PuertoUmbralSession` y la disponibilidad local de puertos.
Se guía, desde la raíz y manteniendo la consola detenida:

```bash
python3 webdefense.py check --mode structured --with-puerto-umbral --lab-mode corrected
```

La comprobación revisa entorno, build existente, disponibilidad de los puertos
3000/5000/4380/4381/4382, locks/trabajos y publicación del perfil, más Compose
y ausencia de contenedores propios en ejecución. La sonda de puertos hace
bind/listen temporal local sin peticiones al portal; el preflight usa el lock
transitorio del controlador. No ejecuta `prepare`, builds, instalación, `serve`,
escenarios o análisis, ni deja los servicios de la aplicación arrancados.

Se espera «Preparado: entorno, build y puertos comprobados» y regreso al
prompt. Resultado pendiente de captura. No se concluye cierre de procesos a
partir del respaldo ni se afirma inspección exhaustiva de todo proceso del
host. Si aparece un bloqueo, conservar la salida antes de instalar, arrancar
o corregir nada.

## Preflight de cierre completado según salida aportada — 31/10

La captura muestra el comando guiado y «Preparado: entorno, build y puertos
comprobados. Ejecuta: python webdefense.py start». Corresponde a la rama
`--check` revisada, que solo imprime esa salida después de pasar el preflight.
Queda **completada la comprobación actual sin bloqueadores visibles**, dentro
de los controles de entorno/build/puertos, locks/trabajos/publicación y estado
de contenedores propios descritos arriba.

No se ven el prompt posterior o código de salida en el recorte; no se solicita
repetición por ello. No se inició la aplicación por ese comando ni se ejecutó
un análisis. El código del propietario de procesos también se ha leído: usa
grupos propios en Linux, señalización y espera/cierre de hijos, sin que esta
lectura equivalga a inspección independiente de todo el host.

El bloque actual de conservación y cierre queda terminado a su alcance:
perímetro inspeccionado, metadatos e integridad puntual de la última auditoría,
selección de 47 archivos de auditoría, respaldo del perfil de 113 archivos con
verificación interna y preflight posterior. No se repiten esas comprobaciones.
La restauración independiente adicional continúa aplazada.

Esto no valida rotación/discontinuidad o veinte latencias F4, regresión de
perfiles, efectos vulnerables F6 o calidad del detector. El siguiente candidato
funcional propuesto es Cargas F6/vulnerable/Intento/variante 1, para contrastar
el efecto con el rechazo corregido ya observado: un caso manual y lectura/copia
V2, sin suites o LLM. Todavía no está autorizado ni ejecutado; no se arranca
la aplicación por registrar esta propuesta. F6/MVP/proyecto siguen abiertos.
