# Cierre de Web Defense AI V2 y Puerto Umbral para el 03/11/2026

Estado al 30/10/2026, Europe/Madrid: **desarrollo en curso; cierre F0–F7 solicitado,
todavía no aceptado**. El propietario quiere terminar antes del martes 3 de
noviembre para preparar su publicación en LinkedIn. Confirma expresamente que
incluye F6 y F7, además del MVP F0–F5. El objetivo de revisión final es el lunes
2 de noviembre. El calendario es una previsión, no una validación anticipada.

## Punto de partida comprobado

### Punto de reanudación guardado — cierre del 30/10 y pausa

**Ronda de seis controles normales F7 completada según capturas**, todos
corregido/Uso normal/variante 1: Configuración, Suministro, Criptografía,
Integridad, Registro y Excepciones. Los seis tienen respuesta esperada,
lectura en V2 y mensaje de copia conservada sin análisis. No repetirlos.
Último caso: `b4ca524b483be65d9549d6b132f25fe7`, HTTP 200,
`controlled_response`, `error: null`, 3 peticiones/3 líneas, 2 eventos /
2 referencias HTTP; misma ejecución y 2 eventos en V2, con copia conservada.
Detalle e identificadores en el [acta F6/F7](PUERTO_UMBRAL_F6_F7_2026_10_29.md).

El propietario autoriza commit/push documental con `[skip ci]` y pide seguir
mañana. Se completa esa publicación y se verifica remoto/árbol limpio antes
de parar. La identidad de la entrega es la del commit que contiene este punto.
**Después de publicar, pausa hasta que el propietario retome.** No hay tareas
programadas; no se inician servicios, casos, suites o modelos durante la pausa.

Al retomar, revisar este punto y la situación de la VM comunicada por el
propietario. No asumir servicios abiertos ni arrancarlos desde Windows. El
siguiente bloque propuesto es revisar condiciones adversas de artefactos F7,
modo corregido, variante 1, manualmente y con alcance por acordar; todavía sin
ejecutar o autorizar. F6/F7 globales, validaciones ampliadas del MVP y evaluación
del detector siguen pendientes. La autorización Groq anterior sigue consumida.
La entrega actual solo modifica documentación: Parrot puede actualizarse con
`git pull --ff-only`, sin build, reinstalación o reinicio por estos cambios.
Las notas inferiores recogen la secuencia histórica y sus pendientes de entonces.

### Último caso de esta sesión y pausa solicitada

El propietario autoriza Excepciones/corregido/Uso normal/variante 1, con
lectura y conservación en V2, sin suites o modelo. Expectativa por código:
HTTP 200, `controlled_response`, `error: null` y 2 eventos. Resultado y copia
pendientes de capturas. Después autoriza commit/push de las cuatro actas
pendientes con `[skip ci]` y pide seguir mañana. Primero se documentará el
resultado, luego se publicará y verificará el remoto/árbol limpio; finalmente
se guardará el punto de reanudación y se detendrá el trabajo. No se inician
otros casos o recordatorios por esa petición. Los cinco normales anteriores
no se repiten; F7 global y demás validaciones continúan pendientes.

### Siguiente revisión manual F7: Registro normal corregido

El propietario acepta un caso Registro/corregido/Uso normal/variante 1,
con lectura y conservación V2, sin suites o modelo. Se guía la revisión de
una secuencia ficticia completa: expectativa HTTP 200, `[1,2,3,4,5]`, lista
de huecos vacía, `warning_recorded: false` y `no_warning`. No comprueba
continuidad real de Apache o entrega de avisos. Se esperan 2 eventos y puede
no haber coincidencias F6. Resultado y conservación pendientes de capturas;
los cuatro controles normales anteriores no se repiten. F7 sigue abierta.
Las capturas posteriores muestran `2c26ab55cda7b3e95eccfbf5080580b2`, HTTP
200, secuencia ficticia completa, sin huecos o aviso; 3 peticiones, 3 líneas y
2 eventos / 2 referencias HTTP. V2 muestra misma ejecución y 2 eventos, sin
coincidencias, con copia conservada sin análisis. **Registro normal corregido,
variante 1, completado a ese alcance**. No repetir. Siguiente candidato
Excepciones/corregido/Uso normal/variante 1, todavía propuesto sin ejecutar.
F7 global y comprobaciones de continuidad real o entrega de avisos siguen abiertas.

### Siguiente revisión manual F7: Integridad normal corregida

El propietario acepta un caso Integridad/corregido/Uso normal/variante 1,
con lectura y conservación V2, sin suites o modelo. Se guía una revisión del
manifiesto ficticio: expectativa HTTP 200, `accepted: true`, `hmac_sha256` y
`manifest_checked`; no verifica manifiestos reales. Se esperan 2 eventos y
puede no haber coincidencias de reglas F6. Resultado y conservación pendientes
de capturas. Los tres casos normales anteriores no se repiten; F7 sigue abierta.
Las capturas posteriores muestran `38d690cd4161439e73f4d38df256e0d1`, HTTP
200, manifiesto ficticio aceptado, `hmac_sha256` y `manifest_checked`; 3
peticiones, 3 líneas y 2 eventos / 2 referencias HTTP. V2 muestra misma
ejecución y 2 eventos, sin coincidencias, con copia conservada sin análisis.
**Integridad normal corregida, variante 1, completada a ese alcance**. No se
repite. Siguiente candidato Registro/corregido/Uso normal/variante 1, todavía
propuesto sin ejecutar. F7 global y evaluación del contenido siguen pendientes.

### Siguiente revisión manual F7: Criptografía normal corregida

El propietario acepta un caso Criptografía/corregido/Uso normal/variante 1,
con lectura y conservación V2, sin suites o modelo. Se guía una revisión del
artefacto ficticio: expectativa HTTP 200, `scrypt`, sal y derivación con valor,
`salted_password_derivation`; la sal aleatoria impide fijar una respuesta
idéntica entre casos. No repetir para comparar hashes. Se esperan 2 eventos;
las reglas F6 no evalúan el contenido F7. Resultado y conservación pendientes
de capturas; no acepta F7 global o criptografía de producción.
Recepción posterior: `8fa4ffafefc52573988c36dd75fbcbb5`, HTTP 200, `scrypt`,
sal y derivación con valor, `salted_password_derivation`; 3 peticiones, 3 líneas
y 2 eventos / 2 referencias HTTP. V2 muestra misma ejecución y 2 eventos, sin
coincidencias. Ejecución y lectura observadas; conservación pendiente de
confirmación visual, sin banner de copia en la captura. Se guía solo conservar
esa auditoría, sin repetir caso o comparar hashes con ejecuciones nuevas.
La captura posterior confirma copia conservada sin análisis, con la misma
ejecución, 2 eventos y SHA. **Recorrido normal de Criptografía corregida,
variante 1, completado según capturas**. No repetir. Configuración, Suministro
y Criptografía normales tienen lectura y conservación informada en V2;
resto de cobertura y aceptación F7 pendientes. Siguiente candidato Integridad/
corregido/Uso normal/variante 1, todavía propuesto sin ejecutar.

### Siguiente revisión manual F7: Suministro normal corregido

El propietario acepta continuar con un único caso Suministro/corregido/Uso
normal/variante 1 y su lectura/conservación en V2, sin suites o modelo. Se guía
«Revisar artefacto ficticio» una vez; expectativa HTTP 200, hashes esperado y
recibido iguales y `accepted: true`, sobre referencia local ficticia. No se
verifican paquetes o proveedores reales. Se esperan 2 eventos; la ausencia de
coincidencias de reglas F6 no evalúa el artefacto F7. Resultado y conservación
pendientes de capturas. Configuración normal anterior no se repite.
Las capturas posteriores confirman HTTP 200 con hashes iguales y artefacto
aceptado, ejecución `d34aba7e1dfae17f750c1ac7c8722be1`; 3 peticiones, 3 líneas
y 2 eventos / 2 referencias HTTP. V2 muestra la misma ejecución y 2 eventos,
sin coincidencias, con copia conservada sin análisis. **Suministro normal
corregido, variante 1, completado a ese alcance**. No se repite. El siguiente
candidato es Criptografía/corregido/Uso normal/variante 1, todavía propuesto
sin iniciar. F7 global y evaluación del contenido siguen pendientes.

### Siguiente revisión manual F7: Configuración normal corregida

La entrega de actas se publicó en `dc9fb17`, con remoto coincidente y árbol
limpio. El propietario solicita continuar: se guía un único caso manual
Configuración/corregido/Uso normal/variante 1, lectura y conservación en V2,
sin suites o modelo. Se espera HTTP 200, `debug_enabled: false` y
`minimal_configuration` en un artefacto ficticio; no una auditoría real del
despliegue. La ausencia de observaciones en V2 no evalúa el contenido F7.
Resultado pendiente de capturas y copia informada, sin ejecución desde Windows.
Los recorridos completados de F6 no se repiten; aceptación global pendiente.
Las capturas siguientes muestran Configuración normal corregida completada:
`608700e1fe2c6d7d91f4f275a770a56a`, HTTP 200, depuración desactivada y
configuración mínima; 3 peticiones/3 líneas y 2 eventos. V2 muestra la misma
ejecución y 2 eventos, sin coincidencias. Ejecución y lectura observadas;
**conservación pendiente de confirmación visual**, pues el recorte no incluye
su mensaje. Se guía solo conservar esta copia, sin repetir caso o análisis.
La captura posterior confirma copia conservada sin análisis, con la misma
ejecución, 2 eventos y SHA. **Recorrido normal de Configuración corregida
completado según capturas**, sin recibo local o verificación independiente
nuevos. No repetir. El siguiente candidato es Suministro/corregido/Uso normal/
variante 1; todavía propuesto, sin ejecutar. F7 global sigue abierta.

### Siguiente validación manual: rechazos corregidos

Las cinco actas se publicaron en `d3e0b14`, con remoto verificado y árbol
limpio. El propietario solicita continuar con lo siguiente: se guía primero
Cargas/corregido/Intento de ataque/variante 1, seguido de lectura y conservación
de auditoría en V2, sin suites o modelo. El resultado esperado es HTTP 403 y
observación por reglas de acceso rechazado. Todavía no hay captura de ese
caso; no modifica las aceptaciones pendientes ni repite los controles normales.
Las capturas posteriores muestran Cargas rechazado con HTTP 403 y dos eventos
en V2, con «Acceso al objeto rechazado» para `foreign-1`. Una captura adicional
confirma copia conservada sin análisis. Se completa ese recorrido de variante 1
corregida; sigue Preferencias como control HTTP de rechazo. No se repite Cargas
ni se atribuyen métricas LLM o protección universal.
Después se observa Preferencias rechazado en la prueba HTTP de origen/token:
403, `changed: false`, misma ejecución y 2 eventos en V2, con la regla de
solicitud de otro origen rechazada y copia conservada. La comprobación de
navegador sigue pendiente; continúa Baliza, rechazo corregido de variante 1.
La siguiente recepción muestra Baliza rechazado con 403 para diagnóstico,
misma ejecución y 2 eventos en V2, regla «Lectura del señuelo rechazada» y
copia conservada sin análisis. Sigue Atraque sin aprobación, variante 1
corregida; los demás criterios y comprobaciones de navegador siguen pendientes.
Las capturas siguientes confirman Atraque sin aprobación rechazado con 409 y
permiso pendiente, dos eventos y «Aprobación exigida» en V2, con copia
conservada. Se observan así los cuatro rechazos HTTP corregidos de variante 1.
Sigue Bitácora, control de codificación con HTTP 200 esperado y revisión del
iframe; no es aceptación de F6 ni prueba de navegador CSRF.
La recepción de Bitácora confirma HTTP 200 con entrada codificada, iframe
mostrando el texto literal sin ejecución confirmada y 3 eventos en V2, con
copia conservada. Termina la ronda corregida de variante 1: cuatro rechazos
HTTP y un control de codificación, todos con lectura y conservación informada.
Sigue pendiente F6 completa, en particular navegador CSRF, reutilización de
permiso, otros modos/variantes, aislamiento/regresión y evaluación del detector.
El candidato siguiente es una sesión nueva para comprobar el formulario CSRF
en navegador; su alcance debe acordarse antes de prepararla.
El propietario autoriza expresamente ese recorrido manual corregido: una
preparación nueva, sesión ficticia, formulario normal y formulario del otro
origen, confirmación en el panel y lectura/conservación en V2, sin suites o
modelo. Se guían los pasos dentro de su ventana de cinco minutos; los
resultados nuevos siguen pendientes de capturas y no se declaran aceptados.

Recepción posterior: las cuatro capturas de la ejecución
`fe73eb53a5030885bb395eeb7613ac5c` muestran formulario normal con
`changed: true`, formulario cruzado con `changed: false`, confirmación de
rechazo en navegador y cinco eventos coincidentes en V2, con copia conservada
sin análisis. **Recorrido CSRF corregido en navegador completado a ese alcance**;
no repetirlo. El panel informa 4 peticiones del ejecutor y 7 líneas Apache
correlacionadas. Las dos observaciones de rechazo son coherentes con la sonda
HTTP y el formulario, sin inspección de eventos crudos o recibo local nuevo.
El detalle y el SHA mostrado están en el [acta F6/F7](PUERTO_UMBRAL_F6_F7_2026_10_29.md).
El siguiente candidato manual es reutilización de permiso en Atraque corregido,
intento variante 3; todavía sin ejecutar ni acordar ese nuevo alcance. F6/F7 y
el cierre global siguen abiertos. Sin llamadas al modelo o publicación Git.
El propietario acepta después continuar con ese único caso manual y su lectura/
conservación en V2. Se guía una pulsación de ejecutar, ya que la variante 3
incluye aprobación, consumo y segundo uso de `dock-3`. Se espera 409 con el
permiso todavía consumido y observación «Reutilización del permiso rechazada».
Resultado pendiente de capturas, sin ejecutar el caso desde Windows ni iniciar
suites o modelo. El recorrido CSRF anterior no se repite.
Recepción posterior: Atraque variante 3 corregida se muestra completado,
ejecución `b1aa23bd017b47ec814fe8d3c52ecd2e`, HTTP 409 y permiso consumido
antes y después; 6 peticiones, 6 líneas correlacionadas y 5 eventos. V2 muestra
la misma ejecución y conteo, «Reutilización del permiso rechazada» para `dock-3`
y copia conservada sin análisis. **Recorrido de reutilización corregida
completado según capturas**, sin recibo local o hash independiente nuevo.
No se repite este caso ni CSRF. F6 global continúa abierta por cobertura,
aislamiento/regresión y evaluación. El siguiente bloque propuesto es revisión
manual F7, comenzando Configuración/corregido/Uso normal/variante 1; todavía
sin ejecutar ni acordar ese nuevo alcance. Detalle en el acta F6/F7.

### Reanudación del 30/10

El propietario vuelve y solicita continuar desde el punto guardado, reiniciando
la aplicación en Parrot y siguiendo las pruebas. Se levanta la pausa para el
bloque manual descrito: Bitácora, Preferencias, Baliza y Atraque, todos en modo
corregido, Uso normal y variante 1, uno a uno, con lectura y conservación de sus
auditorías en V2. No se incluyen suites, otros casos, modelo o notificaciones.

Primero se guía el arranque conjunto desde la instalación existente; su éxito
todavía no se atribuye sin salida real. No se presupone que los servicios
siguieran abiertos ni se ejecuta la VM desde Windows. No hay cambios de código
operativo desde `5bf154a` que requieran reinstalar o recompilar por estas actas.
El primer caso pendiente será Bitácora. Cargas y su copia/recibo anteriores
permanecen completados, sin repetición. Los cuatro casos y el nuevo arranque
están pendientes de evidencia del propietario.
Primera recepción del bloque: Bitácora/corregido/Uso normal/variante 1 se
muestra completada con HTTP 200 y «Revisión de baliza»; 4 peticiones, 4 líneas
Apache y 3 eventos capturados. Su lectura/conservación en V2 aún están
pendientes. Preferencias, Baliza y Atraque no se declaran ejecutados.
La captura siguiente confirma lectura de Bitácora en V2, misma ejecución y
3 eventos, y mensaje de copia conservada sin análisis. Se completa ese
recorrido normal con conservación informada en pantalla. El siguiente control
es Preferencias; Baliza y Atraque continúan después, todos con la misma
selección corregido/Uso normal/variante 1. No se repite Cargas o Bitácora.
Después se observa Preferencias completado, HTTP 200 con `demo-1` y
`changed: true`; mismo identificador y 2 eventos en V2, con copia conservada
sin análisis. Este control normal HTTP queda completado a ese alcance;
Baliza y Atraque son los dos controles pendientes del bloque reanudado.
La recepción siguiente completa Baliza normal: HTTP 200 para `/public` con
`UMBRAL_PUBLIC_BEACON`, misma ejecución y 2 eventos en V2, copia conservada
sin análisis. Atraque es el único control pendiente de este bloque normal.
La última recepción completa Atraque: HTTP 200, permiso aprobado y después
consumido; misma ejecución y 4 eventos en V2 con copia conservada. Queda
**completado el bloque de cuatro controles normales del 30/10**, con lectura
y conservación informada en V2. Son 15 peticiones/15 líneas informadas/11
eventos; incluido Cargas del 29/10, cinco controles, 18/18/13. No se considera
una suite nueva o evaluación del detector. No se repiten los casos normales.
El propietario acepta después publicar las cinco actas pendientes mediante
commit/push `[skip ci]`, sobre `5bf154a` comprobado con el remoto. La identidad
se obtiene del commit que incorpora la nota de distribución del acta F6/F7;
el resultado de Git se verifica al terminar. Es una entrega documental sin
ejecuciones nuevas o aceptación de criterios pendientes; en Parrot basta
actualizar por Git, sin reinstalar, recompilar o reiniciar servicios.

### Punto de reanudación guardado — pausa del 29/10

El propietario indica que continuará mañana (30/10 según la fecha de esta
sesión) y pide guardar el siguiente paso. Se detiene el trabajo tras registrar
este punto, sin ejecutar nuevos casos, servicios, modelos o publicaciones.
No se ha solicitado ni creado un recordatorio automático.

- **Completado:** un control normal Cargas, modo corregido, variante 1;
  auditoría de 2 eventos visible en V2, copia conservada y recibo local observado.
  Ejecución `10fea5f6cbef9d88320ca767cc11e0b4`; copia
  `ed70066797f1f68f7df55b7ecb18247d`. No repetir este recorrido.
- **Siguiente bloque propuesto, todavía sin ejecutar:** Bitácora, Preferencias,
  Baliza y Atraque; los cuatro en modo corregido, **Uso normal**, variante 1,
  manualmente uno a uno, con lectura y conservación de sus auditorías en V2.
  No incluye suites ni llamadas al modelo. La respuesta recibida aplaza el
  bloque; no autoriza iniciarlo durante la pausa.
- **Al retomar:** revisar este punto y el [acta F6/F7](PUERTO_UMBRAL_F6_F7_2026_10_29.md),
  acordar la continuación y comprobar el estado que comunique el propietario.
  No se presupone que la VM o sus servicios sigan abiertos.
- **Distribución:** último commit publicado `5bf154a`; las cinco actas actuales
  siguen guardadas localmente, sin commit/push posterior. El código no cambia
  por este registro. La configuración Groq y su análisis anterior se conservan.

### Resumen de evidencia disponible

| Área | Evidencia disponible | Límite |
| --- | --- | --- |
| Distribución V2 | Repositorio público, versión local anterior v0.1.0; F6/F7 en `cc363af` y autoría/actas en `5bf154a`, ambos con remoto verificado | No nueva release o CI atribuida a los commits `[skip ci]` |
| Puerto Umbral F1/F2 | Prototipo privado, cinco familias locales y dos modos | Corpus histórico 42/45; tres fallos de comandos preservados |
| F3, recorrido de integración | Un snapshot de 17 líneas, análisis Groq, publicación y lectura en V2 | No evaluación de los 45 casos |
| F4 | Inicio, pausa, reanudación, parada, vencimiento y reapertura sin auto-resume | Condiciones ampliadas y latencias individuales pendientes |
| F5, conservación | Copia y recuperación aislada de 66 archivos, SQLite e informe verificados en Parrot | Sin promover datos recuperados ni restaurar la VM completa |
| Interfaz | Autoría visible en cabecera y vistas Fuente/Auditoría de Actividad V2 observadas por capturas | No revisión actual completa de móvil/teclado o enlaces abiertos |
| F6/F7 | [Código de ampliación revisado y publicado](PUERTO_UMBRAL_F6_F7_2026_10_29.md); los cinco controles normales de variante 1 corregida leídos y conservados en V2; recibo local observado para Cargas | F6 completa no aceptada; otros tipos/variantes, navegador, regresión, recuperación de auditorías nuevas y evaluación ampliada pendientes |

El [estado consolidado](PUERTO_UMBRAL_ESTADO_ACTUAL_2026_10_26.md), el
[acta del análisis y recuperación](PUERTO_UMBRAL_ANALISIS_ACOTADO_2026_10_27.md)
y la [evaluación histórica F5](PUERTO_UMBRAL_F5_2026_10_27.md) contienen los
resultados originales. Este documento no reemplaza sus denominadores ni
reescribe los JSON históricos.

## Trabajo de cierre, en orden

| ID | Trabajo | Evidencia necesaria para cerrarlo | Estado |
| --- | --- | --- | --- |
| DOC-01 | Sincronizar README, arquitectura, inicio y plan V2 | Enlaces válidos y distinción entre estado actual e historia | Actualizado localmente; revisión final conjunta pendiente |
| F6-01 | Contrato de auditoría de aplicación y correlación | Actor, recurso, acción, decisión y secuencia; sin claves, tokens o etiquetas esperadas del corpus | Cinco normales, cinco intentos de variante 1 corregida, CSRF de navegador corregido y reutilización corregida leídos y conservados en V2 según capturas; recibo local del normal Cargas observado; criterios ampliados pendientes |
| F6-02 | XSS almacenado, IDOR, CSRF, SSRF y permisos de atraque | Modos vulnerable/corregido, controles normales, reset, evidencia HTTP/negocio y prueba de navegador cuando corresponda | Cinco normales y cinco intentos de variante 1 corregida, CSRF en navegador corregido y reutilización corregida variante 3 observados; otros modos/variantes, aislamiento/regresión y evaluación pendientes |
| F7-01 | Ejercicios para configuración, suministro, criptografía, integridad, registro y excepciones | Catálogo con tipo de ejercicio explícito y artefactos ficticios verificables | Ronda normal de los seis módulos/corregido/variante 1 completada con lectura y copias conservadas en V2 según capturas; condiciones adversas, otros modos/variantes y aceptación global pendientes |
| EVAL-01 | Resolver o conservar con causa los fallos del corpus actual | Resultados actuales trazables; el histórico 42/45 permanece intacto | Pendiente de ejecución autorizada |
| EVAL-02 | Evaluar detección y falsas alarmas del corpus definido | Expectativas fijadas antes de puntuar, resultados por caso, presupuesto, modelo y uso | Pendiente de alcance/budget de nuevas llamadas |
| OPS-01 | Condiciones ampliadas F4 y regresión de aislamiento | Observaciones reproducibles de rotación, truncado, fallo, cuotas y ausencia de actividad automática | Pendiente de ejecución autorizada |
| UX-01 | Lectura final, móvil, teclado y exportación de evidencias | Comprobación del producto actual y ausencia de contenido sin fuente | Pendiente |
| DOC-02 | Revisar documentación completa de V2 con el propietario | README/manual/estado/catálogo/actas coherentes y enlaces comprobados | Después de terminar el laboratorio |
| ACC-01 | Decisión de cierre y alcance de comunicación | Criterios F0–F7 revisados expresamente, limitaciones pendientes visibles | No aceptado |

F6 y F7 pueden prepararse en código sin declarar superado su requisito de
aceptación del MVP. Las dependencias del PRD siguen vigentes para el cierre.
La fecha objetivo no autoriza declarar completado un criterio no observado.

El propietario elige después mantener solo desarrollo y revisión de código;
decidirá las pruebas más adelante. No se interpretará la petición de todas las
fases o la fecha de LinkedIn como permiso para iniciar suites o llamadas LLM.
La primera preparación de F6/F7 y la sincronización documental pasan revisión
estática de sintaxis, tipos, configuración y enlaces; no se confunde esa revisión
con los recorridos de aceptación que aún deben decidirse.
El propietario autoriza a continuación el paso 1 de revisión de código. Se
completa localmente con correcciones de concurrencia, ventana manual,
validación/lectura acotada y conservación de evidencias, registradas en el
[acta F6/F7](PUERTO_UMBRAL_F6_F7_2026_10_29.md). Los criterios operativos siguen
pendientes. Después el propietario autoriza commit/push del paquete revisado
con `[skip ci]`; su identidad queda en el commit que incorpora la nota de
distribución del acta F6/F7. Publicar no ejecuta la validación ni actualiza la VM.
La publicación se completa en `cc363af`, con remoto coincidente y árbol limpio.
El propietario autoriza después el paso 3 y sus capturas confirman ese commit
en Parrot y la compilación completa del frontend con Webpack y TypeScript.
**Paso 3 completado**; no acredita todavía arranque de V2, construcción o
disponibilidad de la topología nueva, escenarios o métricas del detector.
El siguiente bloque de arranque y revisión de pantallas queda autorizado por
el propietario, limitado a disponibilidad y navegación en el perfil corregido;
su resultado permanece pendiente. No autoriza recorrer casos ni repetir LLM.
Las capturas siguientes acreditan salida «Consola lista» y acceso al panel de
Puerto Umbral, que informa 14 contenedores. El alcance de disponibilidad del
panel queda observado; falta la captura de Actividad V2 y no se validan casos.
La petición adicional de autoría en cabecera se implementa en HTML/CSS local;
su recepción en Parrot y revisión visual quedan pendientes de distribución.
Recepciones posteriores: autoría visible y vistas de Actividad V2 acreditadas
por capturas. La fuente conserva el snapshot corregido histórico de 17 líneas
y se muestra antigua; la auditoría avanzada se muestra sin datos, sin error.
El bloque de disponibilidad y revisión básica de pantallas queda completado.
No cambia la aceptación de escenarios, F4 ampliada o métricas de detección.

## Calendario propuesto

| Fecha | Prioridad de trabajo |
| --- | --- |
| Jueves 29/10 | Documentación V2 al día y contrato de ampliación F6 |
| Viernes 30/10 | Escenarios F6 y recibos de estado/identidad |
| Sábado 31/10 | Ejercicios F7 y matriz de categorías/evidencias |
| Domingo 01/11 | Validación acotada, correcciones y métricas si su ejecución se autoriza |
| Lunes 02/11 | Congelación de alcance, revisión del laboratorio y documentación V2 con el propietario |
| Martes 03/11 | Publicación del propietario en LinkedIn con afirmaciones respaldadas |

Si una validación no está disponible a tiempo, se registrará como pendiente y
se revisará la fecha o el alcance con el propietario; no se omitirá para dar
el proyecto por terminado. Este plan no configura tareas programadas ni
publica mensajes en LinkedIn.

## Límites de ejecución que siguen vigentes

La única autorización de análisis Groq ya se consumió. No se inician llamadas,
escenarios, suites o recorridos automáticos nuevos por este documento. Antes
de ejecutar el siguiente bloque se necesita concretar su alcance y, si usa
modelo, número máximo de solicitudes, proveedor/modelo y presupuesto. No
solicitar ni publicar claves; utilizar la configuración propia de Parrot.

Los escenarios permanecen locales y confinados. El prototipo privado de Sites
mantiene su identidad y audiencia; no se despliega el backend vulnerable allí.
F7 distinguirá ejercicio HTTP real, demostración con datos ficticios y revisión
de artefactos. Un mapa educativo de diez categorías no acredita detección de
todas ellas por V2 ni explotación real de todos los ejemplos.

## Qué respaldará la comunicación final

Podrán describirse las funciones implementadas y los recorridos observados,
con sus versiones y límites. Los porcentajes de detección solo procederán de
la evaluación identificada del detector; no del corpus funcional 42/45.
La nueva ampliación no será una actualización de la release v0.1.0 hasta que
se decida expresamente una entrega identificada. El texto de LinkedIn y la
revisión documental final se prepararán tras cerrar el laboratorio, como
solicita el propietario.
