# Puerto Umbral — estado consolidado y cierre de la ronda manual

Fecha: 26/10/2026, Europe/Madrid.

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
