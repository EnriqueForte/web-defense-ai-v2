# Puerto Umbral — estado consolidado y cierre de la ronda manual

Fecha: 26/10/2026, Europe/Madrid.

## Entrada simplificada para ambas apps — 01/11

Se desarrolla `webdefensev2.py` por petición del propietario. Comando habitual:
`python3 webdefensev2.py`; usa el lanzador existente con informes `structured`,
Puerto Umbral incluido y fuente V2 `corrected` por defecto. Admite `start`,
`check`, `install`, `--help` y `--lab-mode vulnerable`; preserva las
comprobaciones y el supervisor con cierre conjunto por `Ctrl+C`.
Sintaxis de ambos archivos Python modificados revisada con AST y ayuda CLI
exit 0, sin iniciar servicios, preflight, instalaciones, suites o modelos.
Primer arranque de esta entrada en Parrot aún no observado; no se extrapola
del arranque anterior con argumentos explícitos. Documentación de uso actualizada;
cambios locales posteriores a `cd6b34d`, sin publicación Git nueva.

## Recepción visual posterior al cambio — 31/10

Entrega `cd6b34d` publicada y verificada contra `origin/main`. La captura del
propietario muestra el nuevo Resumen en Parrot a zoom 60 %, aprovechando el
ancho y distribuyendo los bloques en paralelo. Informa desplazamiento vertical
a 100 % y prioriza la legibilidad de los datos. Se recomienda mantener el
diseño actual y usar 100 % con desplazamiento natural; no se fuerza el encaje
mediante más compactación. Sin nuevo cambio frontend o compilación por esta
recepción. No acredita móvil/teclado ni encaje sin scroll a 100 %.

## Distribución del Resumen V2 implementada — 31/10

El propietario aporta capturas de escritorio y autoriza una distribución que
aproveche el ancho lateral. Resumen pasa a ancho fluido y cuadrícula adaptable,
con bloques compactos, gráficas/reportes y amenazas/terminal en paralelo en
escritorio amplio. Incluye vistas previas con cantidades y enlaces al detalle.
Build de producción/TypeScript/rutas y ESLint de `page.tsx` completados sin
errores; resultado visual posterior en Parrot pendiente. Las capturas previas
no acreditan la nueva versión ni móvil/teclado. No escenarios, suites, servicios
o modelo por agente; cambios aún locales, sin publicación Git nueva.
Detalle en [revisión de producto](PUERTO_UMBRAL_REVISION_PRODUCTO_2026_10_31.md).

## Prioridad de trabajo actualizada — 31/10

Por indicación del propietario, Baliza vulnerable no se realiza y queda
pendiente sin resultado. Se continúa con documentación y la
[revisión de producto](PUERTO_UMBRAL_REVISION_PRODUCTO_2026_10_31.md), centrada en
navegación, presentación móvil y teclado, sin escenarios ni llamadas al modelo.
Cargas está completado a su alcance; no se repite. Revisión visual nueva aún
pendiente, sin aceptación anticipada del proyecto.

## Cargas F6 vulnerable, variante 1 — resultado recibido el 31/10

Capturas del propietario: run `176266c5fd701ecdfa637ba14f0d6a34`, COMPLETED,
HTTP 200 para `foreign-1`, propietario `supervisor.demo` y fixture
`UMBRAL_FOREIGN_CARGO`; 3 peticiones, 3 líneas Apache, 2 eventos y 2 referencias.
V2 muestra mismo run/modo vulnerable, 2 eventos, observación «Recurso de otro
propietario devuelto» (`cargo`, `estibador.demo`, `foreign-1`) y confirma copia
conservada sin análisis. SHA mostrado:
`2956f103989b75c515c0320b871eb2558cb5b93f425bd6d4b3b2db4cbc6d38d2`.
Recorrido completado según pantallas; comparación puntual con rechazo corregido
previo completada. No repetir caso/copia. F6 global sigue abierta; sin nueva
inspección de recibo/bytes, respaldo posterior o llamada al modelo. Siguiente
candidato propuesto Baliza vulnerable/Intento/variante 1, aún no autorizado.

## Preflight de cierre recibido — 31/10/2026

La captura del comando `webdefense.py check` con structured/with-puerto-umbral/
lab-mode corrected muestra «Preparado: entorno, build y puertos comprobados».
Comprobación actual completada dentro de su alcance; no pedir repetición por
prompt/exitcode no visibles, ni inferir arranque o auditoría exhaustiva del host.
El bloque de perímetro/recibo/hash/selección/respaldo113/preflight queda
terminado a ese alcance, sin repetirlo. Restauración independiente adicional
aplazada; F4 ampliada, positivos/regresión F6, evaluación F5 y UX/docs/aceptación
siguen pendientes. Próximo candidato propuesto Cargas/vulnerable/Intento/
variante 1 con lectura/copia V2, todavía sin autorizar o ejecutar.
Actas locales `1fdfed1`+, sin Git nuevo o servicios iniciados por el agente.

## Respaldo actualizado completado — 31/10/2026

Salida aportada: `.local-backups/operational-20261031T201154664036Z`, 113
archivos, `verified: true`, `missing: []`. Conservación básica del perfil
seleccionado completada según verificación interna; no repetir el respaldo.
La restauración independiente adicional permanece aplazada; no atribuir
originales bajo `labs/` o recuperación VM completa a esta copia. Sin inspección
independiente del archivo por el agente o aceptación global F6/MVP.
Sigue preflight de cierre con `webdefense.py check`, perfil Puerto Umbral/
structured/corrected, sin arrancar servicios; resultado pendiente de captura.
Detalle en la [auditoría](PUERTO_UMBRAL_AUDITORIA_CIERRE_2026_10_31.md).

## Respaldo nuevo autorizado — 31/10/2026

El propietario acepta la recomendación de crear únicamente un respaldo
actualizado del perfil con la verificación interna existente; aplaza la
restauración independiente adicional. Se guía cerrar consola propia y ejecutar
una vez `backup_operational.py --profile puerto-umbral` sin `--list`.
Resultado pendiente de captura de ruta/conteo/`verified`/`missing`. La escritura
incluye ZIP/manifiesto/snapshot SQLite y `restore-check` interno, sin sustituir
datos activos o borrar originales. No ejecutar `restore_operational.py`, casos
o modelos por esta autorización. Actas locales `1fdfed1`+, sin Git nuevo.

## Selección de respaldo confirmada — 31/10/2026

Captura del listado: recibo actual, eventos y recibo de la última copia son
`file`, 47 archivos de auditoría en la selección y `faltantes: []`. Selección
comprobada; no ZIP o recuperación nuevos, hash de todos los archivos o inclusión
de originales bajo `labs/`. La ronda de lecturas queda completada y no se repite.
Preparada propuesta de un respaldo nuevo del perfil y su restauración aislada
con revisión de la última auditoría recuperada; autorización pendiente porque
crea archivos y el bloque anterior era solo lectura. No repetir el respaldo
antiguo de 66 archivos, promover datos live o iniciar modelos. Alcance en la
[auditoría](PUERTO_UMBRAL_AUDITORIA_CIERRE_2026_10_31.md), notas locales `1fdfed1`+.

## Integridad puntual de la copia observada — 31/10/2026

La captura de `sha256sum` para el `events.json` del snapshot
`891a00db10ca4bcda8a73f5d33fb10a0` devuelve
`bf41223489600b2429eab07b2cd9d08e589372ed9fefa4cd70900e330b1177fa`,
idéntico al SHA canónico del recibo. Integridad puntual comprobada según
salida del propietario, sin acceso VM propio del agente. No repetirlo ni
extrapolar a otros snapshots o respaldo nuevo. Sigue listado de selección
`backup_operational.py --profile puerto-umbral --list`, filtrado a la última
auditoría, sin crear copia; resultado pendiente de captura. Procedimiento
en la [auditoría de cierre](PUERTO_UMBRAL_AUDITORIA_CIERRE_2026_10_31.md).

## Recibo local de la última auditoría leído — 31/10/2026

Captura de `current.json`: mismo último run Excepciones
`a8a228ff56fc61649041b9740731cc86`, corregido/2 eventos/`fixture_review`/
estado completado, fuente y esquema correctos, flags de análisis/notificaciones
falsos. Original SHA coincide con V2; snapshot
`891a00db10ca4bcda8a73f5d33fb10a0`, SHA de copia
`bf41223489600b2429eab07b2cd9d08e589372ed9fefa4cd70900e330b1177fa`.
Metadatos comprobados según captura, sin hash de bytes o respaldo verificados
todavía. No repetir caso/copia/lectura. Sigue lectura `sha256sum` de su
`events.json` y comparación con SHA de copia, resultado pendiente de captura;
sin escribir o ejecutar la aplicación. Detalle en la
[auditoría](PUERTO_UMBRAL_AUDITORIA_CIERRE_2026_10_31.md), notas locales `1fdfed1`+.

## Lectura autorizada del perímetro — 31/10/2026

Recepción posterior: captura del inspector con `valid=True`, 14 contenedores,
targets sin red IP, masquerade/ICC desactivados; once filas visibles activas,
de solo lectura y usuario `10001:10001`. El resultado agregado se emite tras
revisar los catorce contenedores y la red frontal según el código leído.
Inspección actual completada a ese alcance; no pedir repetir por filas
recortadas. No atribuye acceso VM independiente del agente o cierre funcional
F6. Sigue lectura del recibo V2 existente con `python -m json.tool`:
`application-audit/current.json`, esperado último run Excepciones/2 eventos/
corrected y flags de análisis/notificaciones falsos. Resultado pendiente de
captura, sin repetir casos o copia. Detalles en la auditoría enlazada debajo.

El propietario acepta la inspección de estado/perímetro de Parrot. Se guía
`labctl.py inspect` existente, con resumen JSON por stdin en otra terminal,
sin cerrar el lanzador, escribir archivos, iniciar servicios o ejecutar casos,
seguimiento o modelo. El código inspecciona 14 contenedores y la red frontal;
compara imágenes, propiedad, permisos, límites, montajes, red y puertos.
Resultado pendiente de captura; no hay nueva comprobación operativa por el
agente. Si la inspección falla, se recoge el error sin preparar/arrancar o
corregir automáticamente. Detalles en la
[auditoría](PUERTO_UMBRAL_AUDITORIA_CIERRE_2026_10_31.md). Notas locales
`1fdfed1`+, sin Git nuevo.

## Auditoría de cierre del 31/10/2026

El propietario solicita revisar pendientes reales después de la ronda educativa
F7. Preparada la [auditoría F6/MVP](PUERTO_UMBRAL_AUDITORIA_CIERRE_2026_10_31.md)
con criterios PRD, evidencia y propuestas separadas. Cinco grupos de trabajo:
funcionamiento/límites/regresión, operación, evaluación/alcance F5, conservación
nueva y producto/documentación/aceptación. No son cinco pruebas ni autorizaciones.

F5-AC1 tiene los 45 registros históricos con resultado/evidencia o causa;
no impone repetir45 por sí solo. Eso no resuelve la incidencia funcional de
comandos o regresión. Análisis único hasta informe y recuperación aislada de
66 archivos siguen completados y no se repiten. F4-AC1 necesita veinte muestras
o desviación expresamente revisada; F5-AC2 sigue sin métricas y exige evaluación
autorizada o decisión expresa de alcance, sin aceptar piloto por defecto.

README e instrucciones de inicio/instalación/repositorios sincronizados con
observaciones actuales. JSON históricos y entrega base V2 conservados. Próximo
paso propuesto: lectura manual de estado/perímetro y recibos existentes en Parrot,
sin casos nuevos, seguimiento o modelos; todavía no autorizada o ejecutada.
Notas locales posteriores a `1fdfed1`, sin commit/push nuevo.

## Reanudación del 31/10/2026

Última recepción: Excepciones/corregido/Intento/variante 1 completada según
capturas, `a8a228ff56fc61649041b9740731cc86`, HTTP 400, `controlled_response`,
error solo `code: invalid_fixture`, sin traza en el cuerpo mostrado. 3 peticiones,
3 líneas y 2 eventos / 2 referencias; V2 muestra mismo identificador y 2 eventos,
sin coincidencias, con copia conservada sin análisis. SHA mostrado:
`119efb666258c11506d5bd44c739de2df4620beb5a47a7434f369abc78034773`.
No repetir o pedir más capturas de este recorrido. El bloque representativo F7
propuesto está terminado: 11 entradas observadas de 54, 43 no observadas sin
cuota obligatoria; Criptografía/Intento/corregido sigue no ejecutado.

Preparada y revisada documentalmente la
[matriz de cierre educativo F7](PUERTO_UMBRAL_F7_CIERRE_EDUCATIVO_2026_10_31.md),
con objetivos, tipos de evidencia, límites y revisión F7-AC1/2/3. Ronda manual
terminada y propuesta de aceptación de ese alcance lista; F7 global y
dependencias F6/MVP siguen abiertas. Siguiente trabajo: revisar matriz y
pendientes reales del proyecto con evidencia existente, sin añadir ejecuciones,
suites, modelos o servicios por estas capturas. Notas locales `1fdfed1`+.

Último caso autorizado del bloque representativo: Excepciones/corregido/
Intento/variante 1, manual una vez, lectura/conservación V2, sin suites o modelo.
Esperado HTTP 400, `controlled_response`, error `code: invalid_fixture` sin
`fictional_trace`; 2 eventos. Resultado y copia pendientes de capturas. Después
revisar matriz y límites para proponer cierre educativo, sin aceptar F7 global
de antemano, repetir anteriores o ejecutar casos adicionales. Actas locales
`1fdfed1`+, sin nuevo Git o ejecución de VM por el agente.

Última recepción: Registro/corregido/Intento/variante 1 completado según
capturas, `6a0648c2fed5d6b50f5d08e1a7db6db1`, HTTP 200, secuencia ficticia
`[1,2,4,5]`, hueco `[3]`, advertencia registrada y `gap_identified`;
3 peticiones, 3 líneas y 2 eventos / 2 referencias. V2 muestra misma ejecución
y 2 eventos, sin coincidencias, con copia conservada sin análisis. SHA mostrado:
`76804d1f6a19ec99c348af78bef8768dabc43fbc95d2531e38ab9b53a56bc999`.
No repetir ni pedir más capturas de este recorrido. No acredita continuidad
real de Apache, rotación o entrega de avisos; sin inspección de bytes/recibo
local nuevos. Recuento actual F7: 10 entradas observadas de 54, 44 sin observar,
sin cuota obligatoria. Queda solo Excepciones del bloque representativo
propuesto, aún sin autorizar o iniciar; Criptografía/Intento/corregido no
ejecutado. Después revisar matriz para decidir cierre educativo. F7/proyecto
siguen abiertos; actas locales `1fdfed1`+.

Siguiente caso autorizado: Registro/corregido/Intento/variante 1, manual una
vez con lectura y conservación V2, sin suites o modelo. Esperado HTTP 200,
secuencia ficticia `[1,2,4,5]`, hueco `[3]`, `warning_recorded: true` y
`gap_identified`; 2 eventos. El indicador no acredita entrega de avisos,
rotación o continuidad de Apache. Resultado y copia pendientes de capturas;
después quedaría Excepciones del bloque propuesto, aún sin autorizar. Actas
locales `1fdfed1`+, sin nuevo Git, servicios o ejecución de VM por el agente.

Última recepción: Integridad/corregido/Intento/variante 1 completada según
capturas, `cc7cdd171465527bc6cd31497755c38a`, HTTP 422, `accepted: false`,
`hmac_sha256`, `manifest_checked`; 3 peticiones, 3 líneas y 2 eventos /
2 referencias. V2 muestra misma ejecución y 2 eventos, sin coincidencias;
captura posterior confirma copia conservada sin análisis. SHA mostrado:
`d27ed4473691ba6f98429cf03d60f2cac538ccf72aa475534aa42f3922cf1af2`.
No repetir ni pedir más capturas de este recorrido. Recuento actual: 9 entradas
F7 observadas de 54, 45 sin observar, sin cuota obligatoria del PRD. Quedan
Registro y Excepciones del bloque representativo propuesto, todavía sin
autorizar o iniciar. Criptografía/Intento/corregido sigue no ejecutado;
F7/proyecto abiertos. Sin inspección de bytes/recibo local nuevos o verificación
de manifiestos reales; actas locales `1fdfed1`+.

Siguiente caso autorizado: Integridad/corregido/Intento/variante 1, manual una
vez con lectura y conservación V2, sin suites o modelo. Esperado HTTP 422,
manifiesto ficticio rechazado (`accepted: false`), `hmac_sha256` y
`manifest_checked`; 2 eventos. Resultado y copia pendientes de capturas. No
repetir anteriores o iniciar otros casos por este paso. Al completarlo quedarían
dos controles representativos (Registro y Excepciones), sin cierre F7 global.
Actas locales `1fdfed1`+, sin nuevo commit/push o ejecución de VM por el agente.

Última recepción: Suministro/corregido/Intento/variante 1 completado según
capturas, `3708b145de707ced3497dbb37883f07d`, HTTP 422, hashes distintos y
`accepted: false`; 3 peticiones, 3 líneas y 2 eventos / 2 referencias HTTP.
V2 muestra misma ejecución y 2 eventos, sin coincidencias, con copia conservada
sin análisis. SHA mostrado:
`59630ac763bb87574b748afd714ef3baffd00de459466c0533884cd30bd2be0f`.
No repetir. Recuento actual: 8 entradas observadas de 54, 46 sin observar; no
cuota obligatoria F7. Quedan tres controles del bloque representativo propuesto
(Integridad, Registro, Excepciones), con Criptografía/Intento/corregido todavía
no ejecutado y equivalencia por código propuesta. Próximo candidato Integridad/
corregido/Intento/variante 1, aún sin autorizar o iniciar. F7/proyecto siguen
abiertos; sin inspección de bytes/recibo local nuevos o procedencia real de
paquetes. Solo actas locales `1fdfed1`+.

Recuento solicitado: F7 tiene 7 entradas observadas de 54; 47 no observadas,
sin que el PRD exija ejecutar las 54 para su cierre educativo. En la ronda
corregida variante 1 faltan 5 intentos; 4 cambian comportamiento (Suministro,
Integridad, Registro y Excepciones). Se propone cubrir por revisión de código
la equivalencia de Criptografía corregida con el normal ya observado, dejando
el intento como no ejecutado. Completar esos cuatro y revisar la matriz final
permitirá decidir el alcance educativo, sin aceptar de antemano F7 o el proyecto
ni eliminar dependencias/pruebas F6/MVP y evaluación pendientes.

Siguiente caso autorizado: Suministro/corregido/Intento/variante 1, manual una
vez con lectura y conservación V2, sin suites o modelo. Esperado HTTP 422,
hashes distintos y artefacto ficticio rechazado (`accepted: false`); 2 eventos.
Resultado y copia pendientes de capturas; notas locales `1fdfed1`+.

Última recepción: Configuración/corregido/Intento/variante 1 completada según
capturas, `9370f0028216a9926d2ca38ef0c2b1ee`, HTTP 200, configuración mínima,
depuración desactivada y sin `debug_trace`. 3 peticiones, 3 líneas y 2 eventos /
2 referencias; V2 muestra misma ejecución y 2 eventos, sin coincidencias, con
copia conservada sin análisis. SHA mostrado:
`ac7375d71c4b62b5e6ea297da69d1a3c20a322ce367bd8fe7a0c8c48cc96dd1a`.
No repetir este recorrido ni los seis controles normales. No es denegación HTTP
o configuración real verificada; sin inspección de bytes/recibo local nuevos.
Siguiente candidato Suministro/corregido/Intento/variante 1, aún sin iniciar o
autorizar; aceptación F7 global pendiente. Notas locales `1fdfed1`+.

El propietario solicita continuar desde el punto guardado tras la publicación
`1fdfed1`, verificada al cierre anterior; HEAD local coincide y árbol limpio al
retomar. Se guía un caso Configuración/corregido/Intento de ataque/variante 1,
manual una vez, con lectura/conservación V2 y sin suites o modelo. Los seis
controles normales F7 no se repiten. No se asumen servicios VM abiertos: si la
aplicación está detenida se facilita el arranque manual existente, sin instalar,
recompilar o operar la VM desde Windows.

Por código se espera HTTP 200, depuración desactivada y configuración mínima,
sin `debug_trace`; 2 eventos y posible ausencia de observaciones F6. Es otra
selección (`attempt`), cuyo contenido corregido coincide con el control normal;
no supone rechazo HTTP o configuración real verificada. Resultado y copia
pendientes de capturas. Notas locales nuevas; aceptación global pendiente.

## Cierre del 30/10/2026 y punto de pausa

Los seis controles normales F7, corregido/variante 1, quedan completados según
capturas, con lectura y conservación informada en V2: Configuración, Suministro,
Criptografía, Integridad, Registro y Excepciones. Último caso
`b4ca524b483be65d9549d6b132f25fe7`, HTTP 200, `controlled_response`, `error:
null`; 3 peticiones, 3 líneas y 2 eventos / 2 referencias HTTP. V2 muestra
misma ejecución, modo corregido y 2 eventos, sin coincidencias, con copia
conservada sin análisis. SHA mostrado:
`986bd32dd2af9aa895727d63a325b73d79b3c1eb904f3f46dea787b57e00a012`.

No repetir estos recorridos. No se han inspeccionado bytes o recibos locales
nuevos ni evaluado contenido F7 mediante las reglas F6. F7 global sigue abierta.
El propietario autoriza commit/push de las cuatro actas con `[skip ci]` y pide
seguir mañana; se verifica la publicación y después se pausa. La entrega es el
commit que incorpora esta nota, solo documental. Parrot puede recibirla con
`git pull --ff-only`, sin recompilar, reinstalar o reiniciar por estos cambios.
Punto de reanudación al inicio del [plan de cierre](CIERRE_V2_PUERTO_UMBRAL_2026_11_03.md):
revisar alcance manual de condiciones adversas F7 corregidas, variante 1,
todavía sin autorización o ejecución. No nuevos casos/modelos/servicios o
recordatorios durante la pausa. Las notas inferiores son historia previa.

## Continuación autorizada F7 — 30/10/2026

Última instrucción: realizar Excepciones/corregido/Uso normal/variante 1 con
lectura/conservación V2, después commit/push de las cuatro actas y continuar
mañana. Se guía el caso una vez; expectativa HTTP 200, `controlled_response`,
`error: null` y 2 eventos. Resultado y copia aún pendientes de capturas. La
publicación documental `[skip ci]` ya está autorizada para después de registrar
esa recepción; se verificará remoto/árbol limpio y se guardará el punto de pausa.
Sin nuevos casos, servicios, suites, modelos o recordatorios tras ese cierre.

Última recepción: Registro/corregido/Uso normal/variante 1 completado según
capturas, `2c26ab55cda7b3e95eccfbf5080580b2`, HTTP 200, secuencia ficticia
completa, sin huecos o aviso. 3 peticiones, 3 líneas y 2 eventos / 2 referencias;
V2 muestra misma ejecución y 2 eventos, sin coincidencias, con copia conservada
sin análisis. SHA mostrado:
`141d4822e72b628901569cd0c888504a6de982e1ccff084f8e7cab07e1b25800`.
No repetir este caso o los cuatro normales anteriores. No verifica continuidad
real de Apache, rotación o entrega de avisos; sin recibo local o hash independiente
nuevos. Siguiente candidato Excepciones/corregido/Uso normal/variante 1, sin
iniciar todavía; F7 global abierta. Actas locales `dc9fb17`+.

Siguiente caso autorizado: Registro/corregido/Uso normal/variante 1, manual
una vez con lectura y conservación V2, sin suites o modelo. Expectativa HTTP
200, secuencia ficticia completa `[1,2,3,4,5]`, huecos vacíos, sin aviso y
`no_warning`; 2 eventos esperados. No verifica continuidad real de Apache o
entrega de notificaciones. Resultado y copia pendientes de capturas; no repetir
los cuatro controles normales anteriores. Actas locales `dc9fb17`+.

Última recepción: Integridad/corregido/Uso normal/variante 1 completada según
capturas, `38d690cd4161439e73f4d38df256e0d1`, HTTP 200, manifiesto ficticio
aceptado, `hmac_sha256` y `manifest_checked`. 3 peticiones, 3 líneas y 2 eventos /
2 referencias; V2 muestra misma ejecución y 2 eventos, sin coincidencias,
con copia conservada sin análisis. SHA mostrado:
`6f76a58a30318cdb1ae9fce21d0b553db0fc2bbd8ee5fe498cedea5cf35061f1`.
No repetir este caso o los tres normales anteriores. Sin inspección de bytes
o recibo local nuevos ni verificación de manifiestos reales. Próximo candidato
Registro/corregido/Uso normal/variante 1, todavía sin iniciar. F7 global abierta;
actas locales `dc9fb17`+.

Siguiente caso autorizado: Integridad/corregido/Uso normal/variante 1, manual
una vez con lectura y conservación V2, sin suites o modelo. Expectativa HTTP
200, manifiesto ficticio aceptado, `hmac_sha256` y `manifest_checked`; 2 eventos
esperados y posible ausencia de observaciones F6. Resultado y copia pendientes
de capturas. No se repiten los tres casos normales anteriores ni se verifica
un manifiesto real. Actas locales `dc9fb17`+; aceptación F7 global pendiente.

Última recepción: captura posterior confirma copia conservada sin análisis
para Criptografía, `8fa4ffafefc52573988c36dd75fbcbb5`, modo corregido,
2 eventos y mismo SHA indicado debajo. Recorrido normal variante 1 completado
según capturas; no repetir ni pedir más capturas de este recorrido.
Configuración, Suministro y Criptografía normales corregidos tienen lectura
y conservación informada en V2. Sin recibo local nuevo o hash independiente.
Siguiente candidato Integridad/corregido/Uso normal/variante 1, todavía sin
iniciar; F7 global sigue abierta. Notas locales `dc9fb17`+.

Última recepción: Criptografía/corregido/Uso normal/variante 1 observada,
`8fa4ffafefc52573988c36dd75fbcbb5`, HTTP 200, `scrypt`, sal y valor derivado
presentes y `salted_password_derivation`. 3 peticiones, 3 líneas y 2 eventos /
2 referencias; V2 muestra misma ejecución y 2 eventos, sin coincidencias.
SHA mostrado: `76632c81fba7f53964684bf7effe03c281ec1a9330846862e20727fcd9dd7052`.
El recorte no incluye mensaje de copia conservada: queda pendiente esa
confirmación. Se guía solo conservar esta auditoría, sin repetir caso o
comparar hashes mediante ejecuciones nuevas. No evalúa criptografía de
producción ni acepta F7 global; actas locales `dc9fb17`+.

Siguiente caso autorizado: Criptografía/corregido/Uso normal/variante 1,
manual una vez, con lectura y conservación V2, sin suites o modelo. Se espera
HTTP 200, `scrypt`, sal y derivación con valor y `salted_password_derivation`.
Son parámetros educativos sobre datos ficticios, sin auditoría de producción.
Resultado y copia aún pendientes de capturas; no repetir casos anteriores o
comparar hashes mediante ejecuciones nuevas. Actas locales `dc9fb17`+.

Última recepción: Suministro/corregido/Uso normal/variante 1 completado por
capturas, `d34aba7e1dfae17f750c1ac7c8722be1`, HTTP 200, hashes iguales y
artefacto ficticio aceptado. 3 peticiones, 3 líneas y 2 eventos / 2 referencias;
V2 muestra misma ejecución y 2 eventos, sin coincidencias, con copia conservada
sin análisis. SHA mostrado:
`7228d4f84c4a97a2624a31595e4846d15bf510e16d80c0fdd03890c77a0667d9`.
No repetir Suministro o Configuración. No se verifica procedencia de paquetes
reales ni bytes/recibo local nuevos. Siguiente candidato Criptografía/corregido/
Uso normal/variante 1, todavía sin iniciar; F7 global continúa abierta.

Siguiente caso autorizado por el propietario: Suministro/corregido/Uso normal/
variante 1, manual una vez, con lectura y conservación V2, sin suites o modelo.
Expectativa HTTP 200, hashes iguales y artefacto ficticio aceptado con referencia
local fija. Resultado todavía pendiente de capturas, incluidos identificador,
2 eventos esperados y mensaje de copia conservada. No se repite Configuración
ni se instalan paquetes o verifica procedencia real. Actas locales `dc9fb17`+.

Última recepción: captura posterior confirma copia conservada sin análisis
para `608700e1fe2c6d7d91f4f275a770a56a`, modo corregido, 2 eventos y mismo
SHA indicado debajo. Queda completado el recorrido normal Configuración
variante 1 a este alcance. No se repite ni se requieren más capturas de este
recorrido. F7 global sigue pendiente; siguiente candidato Suministro/corregido/
Uso normal/variante 1, todavía sin iniciar. Sin recibo local nuevo o inspección
independiente de bytes; actas locales posteriores a `dc9fb17`.

Recepción posterior: Configuración/corregido/Uso normal/variante 1 completada,
ejecución `608700e1fe2c6d7d91f4f275a770a56a`, HTTP 200, depuración desactivada
y configuración mínima del artefacto ficticio. 3 peticiones, 3 líneas y 2
eventos / 2 referencias HTTP; V2 muestra misma ejecución y 2 eventos sin
coincidencias. La captura no incluye confirmación de conservación: queda
pendiente solo esa confirmación de la copia autorizada, sin repetir el caso.
La lectura por reglas F6 no evalúa el contenido F7. SHA mostrado por V2:
`86170cfde0364edc7b16a05999b091f1d9a10bdb8636e63c601285673650bf16`.

Tras publicar las actas en `dc9fb17` (remoto verificado y árbol limpio), el
propietario solicita continuar con el primer caso propuesto F7: Configuración,
modo corregido, Uso normal, variante 1, con lectura/conservación en V2, sin
suites o modelo. Se guía el botón «Revisar artefacto ficticio» una vez. Se
espera HTTP 200, configuración mínima y depuración desactivada en el artefacto
ficticio. Ejecución y copia todavía pendientes de capturas; no acepta F7 ni
evalúa configuración de producción. V2 puede no mostrar coincidencias porque
sus reglas de auditoría F6 no evalúan este contenido F7. Notas locales nuevas,
sin publicación adicional o ejecución de servicios/VM por el agente.

## Distribución documental del 30/10/2026

El propietario autoriza publicar las cuatro actas pendientes antes de seguir
con F7. El commit que incorpora esta nota identifica la entrega: rechazos
corregidos, comprobación CSRF en navegador y reutilización de permiso con sus
auditorías observadas y conservación informada. Solo documentación; en Parrot
se recibe con `git pull --ff-only`, sin build, reinstalación o reinicio por esta
entrega. La coincidencia del commit con el remoto se comprueba tras el push.
Las referencias inferiores a notas locales sin publicar describen su momento
histórico. F6 global y F7 siguen pendientes; no se ejecutan casos por publicar.

## Última recepción — reutilización de permiso corregida, 30/10/2026

Completado por capturas el caso Atraque/corregido/Intento de ataque/variante 3:
ejecución `b1aa23bd017b47ec814fe8d3c52ecd2e`, HTTP 409 con estado consumido
antes y después; 6 peticiones del ejecutor, 6 líneas correlacionadas y 5 eventos /
5 referencias HTTP. V2 muestra el mismo identificador, modo y 5 eventos,
«Reutilización del permiso rechazada» para `dock-3` y copia conservada sin
análisis. SHA mostrado:
`4403bb5865d9ed8ba2180a7c5eaa2a207ca727ac5733fa82e89cbce23f3d56b`.

No se repite este recorrido ni CSRF de navegador ya completado. F6 global
permanece abierta por otros modos/variantes, aislamiento/regresión y evaluación;
F7 aún sin ejecución observada. El siguiente bloque propuesto es Configuración
F7/corregido/Uso normal/variante 1, con alcance nuevo por acordar. No hay lectura
del recibo local o verificación independiente de bytes de esta copia. Actas
locales posteriores a `d3e0b14`, sin commit/push, suites o llamadas al modelo.

## Última recepción — CSRF en navegador corregido, 30/10/2026

Continuación posterior autorizada: un caso manual Atraque corregido/intento/
variante 3 y su lectura/conservación en V2. La variante incorpora aprobación,
primer uso y reutilización; se guía una sola ejecución del panel. Expectativa:
409, estado consumido conservado y regla de reutilización rechazada. Resultado
todavía pendiente de capturas, sin suites, modelo o ejecución de VM por el agente.

El recorrido manual expresamente autorizado queda completado por capturas:
ejecución `fe73eb53a5030885bb395eeb7613ac5c`, formulario normal con
`changed: true`, formulario desde el otro origen con `changed: false` y
confirmación del panel «Formulario de otro origen con sesión del navegador
rechazado». El panel informa HTTP 403, 4 peticiones del ejecutor, 7 líneas
Apache correlacionadas y 5 eventos / 2 referencias HTTP. V2 muestra el mismo
identificador, modo corregido y 5 eventos, dos observaciones de rechazo y copia
conservada sin análisis. SHA mostrado:
`8a20bd0c954eca1f91e4fa667c386c8412abb333af8aabc00ee17790b304f2ae`.

Se resuelve el pendiente de navegador CSRF de esta variante corregida; las
notas inferiores conservan la secuencia histórica previa. No se repite el
recorrido ni el análisis Groq. No hay inspección independiente de los bytes o
recibo local de esta copia. Reutilización de permiso en Atraque, otros modos/
variantes, F7 y aceptación global continúan pendientes. El siguiente candidato
es Atraque corregido/intento/variante 3, sin iniciar otro caso por estas actas.
Detalle en el [acta F6/F7](PUERTO_UMBRAL_F6_F7_2026_10_29.md). Documentación local
posterior a `d3e0b14`, sin nuevo commit/push, suites o llamadas al modelo.

## Primer rechazo corregido observado — 30/10/2026

Después de publicar las actas normales en `d3e0b14`, se continúa manualmente
con Cargas/corregido/Intento de ataque/variante 1. Las capturas muestran
HTTP 403 para `foreign-1`, `object_not_authorized`, ejecución
`808f223ac979bd1f3f60ca47ec3a31a1`, dos eventos y regla «Acceso al objeto
rechazado» en V2. Una captura posterior confirma copia conservada sin análisis.
Se completa ese recorrido a este alcance, sin evaluación LLM, hash independiente,
recibo local de esa copia o aceptación global. Sigue Preferencias, control HTTP
de rechazo corregido; navegador entre orígenes permanece pendiente.
La recepción siguiente acredita Preferencias rechazado por HTTP, 403 y
`changed: false`, ejecución `1acb45412fdc9aa6ee6cb908da777a42`, dos eventos
en V2 y «Solicitud de otro origen rechazada», con copia conservada sin análisis.
Es el control HTTP de origen/token; el formulario de navegador sigue pendiente.
Continúa Baliza, rechazo corregido de variante 1, todavía sin resultado nuevo.
Después se observa Baliza corregido rechazando diagnóstico, HTTP 403 y
`canary_resource_not_authorized`, ejecución `1ee95d713c3577e55088ecc4cc083bba`;
dos eventos y «Lectura del señuelo rechazada» en V2, con copia conservada sin
análisis. Completa ese control limitado y continúa Atraque sin aprobación,
variante 1 corregida; no demuestra rechazo de todos los destinos o variantes.
Después se observa Atraque sin aprobación rechazado, HTTP 409 y permiso
pendiente, ejecución `554c8de8300762ce559b9aa38db564ff`, dos eventos y
«Aprobación exigida» en V2, con copia conservada sin análisis. Quedan observados
los cuatro rechazos HTTP de variante 1 corregida. Sigue Bitácora, codificación
de texto e iframe, todavía pendiente; CSRF de navegador y demás criterios
siguen abiertos, incluida reutilización de permiso y otras variantes.
La recepción de Bitácora confirma respuesta codificada con HTTP 200 e iframe
mostrando la entrada literal sin ejecución confirmada; ejecución
`d9d05054f32aae24a76b6fe5b2167552`, tres eventos en V2 y copia conservada sin
análisis. Se completa la ronda de cuatro rechazos HTTP más codificación de
Bitácora, variante 1 corregida. No cierra F6 completa: quedan navegador CSRF,
reutilización de permiso, otros modos/variantes, aislamiento/regresión y
evaluación. Una prueba CSRF de navegador requiere nueva preparación, porque
el reset de Bitácora invalida la sesión de Preferencias anterior.

## Recepción del bloque reanudado el 30/10/2026

Se retoman cuatro controles normales F6, corregido/variante 1, manualmente
uno a uno y con lectura/conservación de auditorías, sin suites o LLM. La primera
captura de Bitácora muestra `COMPLETED`, HTTP 200 y «Revisión de baliza», ejecución
`a6af8974ce18f60314f8ad9c888fe4d2`; 4 peticiones/4 líneas y 3 eventos de
auditoría. Su lectura/copia en V2 sigue pendiente, igual que Preferencias,
Baliza y Atraque. Cargas y su copia anteriores no se repiten. No es aceptación
global de F6/F7. Detalle en el [acta F6/F7](PUERTO_UMBRAL_F6_F7_2026_10_29.md).
Una captura posterior de V2 muestra la misma ejecución de Bitácora y 3 eventos,
sin coincidencias, con confirmación de copia conservada sin análisis. El
recorrido normal de Bitácora queda completado a ese alcance, sin recibo local
o respaldo/restauración nuevos. Sigue Preferencias; después Baliza y Atraque.
Preferencias se observa después completado, HTTP 200 con `demo-1` y
`changed: true`; ejecución `683fa423e04a76f45aa19d081369a1a2`, 2 eventos
coincidentes en V2 y copia conservada sin análisis. Cierra ese control normal
HTTP, sin acreditar CSRF de navegador. Baliza y Atraque siguen pendientes.
Después se observa Baliza normal, HTTP 200 para `/public` con el marcador
`UMBRAL_PUBLIC_BEACON`, ejecución `9bf63cd2fa87781bb0fc7741d6b02f22`;
2 eventos coincidentes en V2 y copia conservada sin análisis. Cierra ese
control público normal; queda Atraque en este bloque. No acredita controles
de denegación, variantes restantes, aislamiento independiente o aceptación F6/F7.
Atraque se observa después completado, HTTP 200 y transición de aprobado a
consumido, ejecución `7114fc01324c2531fac5eca89e131cbb`; 4 eventos coincidentes
en V2 y copia conservada sin análisis. Termina el bloque de cuatro controles
normales del 30/10. Incluido Cargas del 29/10, quedan observados los cinco
controles normales de variante 1 corregida con lectura y conservación en V2.
La fase F6 completa sigue pendiente de otros tipos/variantes, navegador,
aislamiento/regresión y evaluación; no se repiten estos controles para cerrarlos.

## Actualización vigente del 29/10/2026

Objetivo vigente: cerrar **todas las fases F0–F7 antes del martes 03/11**, según
respuesta expresa del propietario. Tras desarrollar y revisar el código,
autoriza publicar y después actualizar Parrot y compilar la interfaz (paso 3);
las pruebas de escenarios se decidirán por separado. El
[plan de cierre de V2/laboratorio](CIERRE_V2_PUERTO_UMBRAL_2026_11_03.md) ordena
el trabajo y la revisión final de documentación con el propietario. La
[ampliación F6/F7](PUERTO_UMBRAL_F6_F7_2026_10_29.md) tiene fuente preparada
sin ejecución o aceptación: no se convierte una fecha objetivo en cumplimiento.
El paquete F6/F7 se publica en `cc363af` con remoto verificado. Las capturas
posteriores muestran ese HEAD en Parrot y compilación completa Webpack y
TypeScript: el paso 3 queda completado según esa evidencia, sin acreditar
todavía arranque o disponibilidad de los nuevos servicios. El detalle se
conserva en el acta F6/F7; la recepción documental posterior sigue local.
Las capturas posteriores muestran «Consola lista» del arranque conjunto y el
panel Puerto Umbral accesible, informando 14 contenedores. Es evidencia de la
salida del lanzador y acceso al panel, sin inspección independiente de Docker
ni captura de Actividad V2 en ese envío. Los escenarios siguen sin validar.
La autoría en la cabecera del panel se incorpora después por petición del
propietario como cambio HTML/CSS local, todavía sin distribuir a Parrot.
Recepción posterior: autoría publicada en `5bf154a` y confirmada visualmente.
Actividad V2 muestra la fuente corregida con el snapshot histórico de 17 líneas
marcado antiguo y el nuevo panel de auditoría sin datos, sin error visible.
La revisión básica de disponibilidad del lanzador/panel/V2 queda completada
por estas capturas; no acredita captura nueva, casos F6/F7 o detección.
Después se autoriza y observa un único caso normal F6 Cargas/corregido/variante 1:
HTTP 200 con `own-1`, propietario `estibador.demo` y `UMBRAL_OWN_CARGO`.
La auditoría de aplicación muestra 2 eventos en el panel y V2 con la misma
ejecución `10fea5f6cbef9d88320ca767cc11e0b4`, sin coincidencias de reglas.
Ese recorrido limitado queda completado por capturas, sin acreditar todavía
copia conservada, recuperación de la auditoría, otros casos o métricas globales.
La conservación se autoriza después y sus capturas muestran confirmación en V2
y recibo local para esa misma ejecución, 2 eventos, modo corregido y copia
`ed70066797f1f68f7df55b7ecb18247d`, con análisis/notificaciones en `false`.
El recorrido de conservación y lectura del recibo queda completado según esas
capturas, sin acreditar todavía respaldo/restauración de esta copia nueva o
recalcular sus hashes de forma independiente. No se requiere repetir el caso.

El ejecutor acotado se publicó en `1403f8d` y la corrección de nombres de fuente
en `9e71c0c`. Ambas publicaciones se verificaron contra main remoto y el árbol
local quedó limpio en sus respectivos cierres. El propietario confirma ahora
que comprobó la corrección en Parrot; es una confirmación del propietario, sin
una nueva captura de HEAD, compilación o procesos.

El recorrido **snapshot guardado → análisis Groq → publicación → informe visible
en V2** está comprobado para el análisis
`f5b674c867994aeba3beeb4a638d7a33`: 17 líneas de 17, tres llamadas, 8150 tokens
reportados y cuatro grupos que requieren investigación (tres altos y uno medio).
El coste real del proveedor sigue sin medirse. El
[acta del análisis](PUERTO_UMBRAL_ANALISIS_ACOTADO_2026_10_27.md) conserva los
identificadores, hashes, alcance y origen de la evidencia. La autorización de
ese único análisis está consumida y no se repite.

Se publican después en `c8abcaf` dos ajustes: incluir `manual-validation.json`
en la lista de respaldo/restauración y distinguir la ausencia de publicación
(`missing`) de una publicación inválida (`error`). Las capturas posteriores
muestran ese recibo en la selección, lectura conectada e informe conservado.
No se borra el informe para ensayar la rama de ausencia.

El propietario crea una copia de 66 archivos sin faltantes y ejecuta el
restaurador independiente en un árbol nuevo. Ambas salidas devuelven
`verified: true`; la recuperación verifica SQLite, un trabajo `succeeded`,
ninguna entrega y la misma generación del informe observado. El recorrido
básico de respaldo y recuperación aislada del perfil queda completado según
esas capturas. No se promovieron datos al estado vivo ni se arrancó la copia
recuperada; no constituye restauración completa de la VM. Los destinos y el
alcance se conservan en el acta enlazada, sin inspección independiente del
agente sobre los archivos de Parrot.

Quedan abiertos la calidad del detector sobre los 45 casos, los tres fallos
funcionales históricos, las condiciones ampliadas de F4, cualquier promoción
o arranque de datos recuperados y la aceptación global del MVP. La continuación del desarrollo no
acepta esos criterios ni autoriza escenarios, suites o nuevas llamadas al LLM.

## Cronología anterior

Actualización del 27/10: [F4 implementada](PUERTO_UMBRAL_F4_2026_10_27.md), sin
activar seguimiento durante su desarrollo. El propietario autoriza después su
publicación y revisión operativa guiada con logs existentes. La ronda anterior
de escenarios sigue finalizada; no se reabren sus casos aplazados.
La ronda operativa básica F4 queda después completada mediante capturas del
propietario, incluida la reapertura sin reanudación automática. La aceptación
ampliada conserva sus pendientes; no se solicitan nuevos casos para este cierre.
El [bloque F5](PUERTO_UMBRAL_F5_2026_10_27.md) consolida después las evidencias
existentes y la documentación de entrega, sin nuevos ensayos o análisis. Su
evaluación del detector y la aceptación del MVP siguen pendientes.

El propietario da margen para terminar las pruebas y continuar con el trabajo
que no requiera nuevas ejecuciones. Se da por finalizada esta ronda manual:
no se solicitan más casos, capturas, suites ni análisis del modelo. Los pasos
propuestos anteriormente que aún no se realizaron quedan aplazados. Esta
decisión no constituye aceptación de los criterios de las fases pendientes.

## Evidencia disponible

La evidencia de Parrot procede de capturas de pantalla y de la confirmación
del propietario. El agente no tiene acceso operativo a la VM ni ha recibido
los archivos completos de recibos o snapshots para recalcular sus hashes.
La cronología y los detalles están en la [guía de Parrot](PUERTO_UMBRAL_PARROT_2026_10_26.md).

| Familia / control | Resultado observado en el laboratorio | Recepción visible en V2 | Pendientes |
| --- | --- | --- | --- |
| SQL, intento variante 1 | Vulnerable devuelve `UM-9000`; corregido devuelve una lista vacía | Peticiones de ambos modos visibles | Resto de variantes, recibos completos y análisis |
| SQL, búsqueda normal `Asteria` | Corregido devuelve `UM-1284` y `UM-1287`; también se observó la solicitud normal vulnerable | Búsquedas normales visibles | No generalizar al resto de entradas |
| XSS, intento variante 1 | Corregido codifica y muestra texto literal; vulnerable confirma ejecución mediante el marcador del iframe | Peticiones de ambos modos visibles | Resto de variantes; el recorte corregido no incluye su mensaje final de estado del navegador |
| Path traversal, intento variante 1 | Vulnerable devuelve el documento señuelo; corregido responde 403 con `document_not_authorized` | Peticiones de ambos modos visibles | Resto de variantes |
| Archivo público `atraque.txt` | Corregido responde 200 con el protocolo ficticio | Petición visible | No generalizar a todo el archivo |
| Comandos, intento variante 1 | Corregido responde 400 con `invalid_component` | Petición visible | Comparación vulnerable, uso normal y fallo histórico de creación de procesos |
| Autenticación | Sin nueva observación manual en Parrot | Sin nueva evidencia aportada para este escenario | Revisión aplazada |

Una petición en Actividad demuestra recepción del registro, no que el analizador
la haya clasificado. El estado HTTP tampoco demuestra por sí solo un efecto.
Las imágenes de fuente que muestran snapshot y SHA-256 acreditan que esos datos
se presentan en la interfaz; no sustituyen una comprobación de los archivos.

El primer corpus histórico conserva su resultado **42/45**, con tres fallos en
comandos. Esta revisión parcial no lo convierte en 45/45 ni descarta el fallo
histórico por haber observado un rechazo en el modo corregido.

## Estado de las fases

| Fase | Desarrollo y observación actuales | Estado de aceptación |
| --- | --- | --- |
| F1 | Prototipo privado publicado en Sites | Conservar el alcance del registro F1 |
| F2 | Cinco familias en código; revisión manual parcial de Parrot documentada | Abierta: cobertura funcional y verificaciones pendientes |
| F3 | Conector, perfil, API y vista de fuente implementados; captura y lectura observadas en ambos modos; un recorrido de snapshot guardado a informe visible completado después | Abierta: validación básica limitada a ese snapshot; errores, regresión y evaluación ampliada pendientes |
| F4 | Seguimiento publicado en 02d2638 y frontend compilado en Parrot | Ronda operativa básica completada, incluida reapertura sin auto-resume; aceptación ampliada pendiente |
| F5 | Archivo histórico de 45 entradas revisado offline, nueve observaciones manuales relacionadas, análisis acotado y respaldo/restauración aislada posteriores documentados | Revisión documental y recorridos básicos de integración y recuperación completados; evaluación del corpus y aceptación del MVP pendientes |

El frontend se compiló en Windows con Webpack. La evidencia posterior F4
acredita actualización a `02d2638`, compilación, acceso y cierre/reapertura en
Parrot. No se atribuyen IDs actuales de contenedores o una instalación limpia
a esas imágenes. El informe F5 mantiene separado el alcance de cada fuente.

La fuente anterior estaba publicada hasta `abab01d`, posterior a `fdffd08`.
El propietario autoriza después publicar F4 junto con las actas de esta ronda;
su identificación queda en el historial Git. No se crea una release ni se
atribuye nueva CI a esta publicación.

## Alcance F4 preparado el 26/10 (histórico)

Puede prepararse e implementarse sin ejecutar escenarios ni llamar al modelo.
Sus criterios de aceptación seguirán pendientes hasta una revisión posterior;
su desarrollo no cierra retroactivamente F2/F3.

Alcance previsto:

- Inicio explícito por el operador, con duración y frecuencia limitadas según
  el PRD; abrir una página o arrancar V2 no activa el seguimiento.
- Estados visibles de detenido, siguiendo, pausado, finalizado y error, con
  último ciclo válido y causa de parada diferenciados de ausencia de eventos.
- Captura de una sola pasarela elegida en el perfil. El selector de escenario
  del laboratorio no cambia esa fuente.
- Reutilizar snapshots inmutables y conservar el último válido ante fallo.
  Registrar checkpoint, modo y procedencia; no mezclar reinicios o cambios de
  origen sin señalarlos.
- Si no cambian los datos, no publicar duplicados ni crear trabajos nuevos.
- Excluir captura/seguimiento de operaciones incompatibles mediante el bloqueo
  existente. Pausar o detener debe impedir nuevas capturas.
- Mantener el análisis y las notificaciones separados y desactivados. El
  seguimiento solo actualiza evidencia; no solicita análisis automáticamente.

La preparación inicial pedía resolver cancelación durante una captura,
identidad del contenedor, rotación/truncado y conservación del checkpoint antes
de activar el seguimiento. El registro F4 del 27/10 enlazado al inicio describe
su implementación posterior. En el momento de aquella preparación aún no se
habían ejecutado ciclos F4. La ronda básica posterior está documentada; el
objetivo completo de latencia sigue sin medirse. F5 no habilita nuevos servicios.

## Conservación

Los recibos, snapshots, logs y datos existentes no se borran ni se reescriben.
No se modifica el Site alojado, el detector, las dependencias o la configuración
operativa por este cierre. Se mantiene la separación entre datos del laboratorio
y resultados esperados del evaluador. La [especificación original](PRD_PUERTO_UMBRAL_2026_10_26.md)
conserva sus criterios; las verificaciones aplazadas no se presentan como realizadas.
