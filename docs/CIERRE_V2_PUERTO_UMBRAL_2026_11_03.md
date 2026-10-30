# Cierre de Web Defense AI V2 y Puerto Umbral para el 03/11/2026

Estado al 30/10/2026, Europe/Madrid: **desarrollo en curso; cierre F0–F7 solicitado,
todavía no aceptado**. El propietario quiere terminar antes del martes 3 de
noviembre para preparar su publicación en LinkedIn. Confirma expresamente que
incluye F6 y F7, además del MVP F0–F5. El objetivo de revisión final es el lunes
2 de noviembre. El calendario es una previsión, no una validación anticipada.

## Punto de partida comprobado

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
| F6-01 | Contrato de auditoría de aplicación y correlación | Actor, recurso, acción, decisión y secuencia; sin claves, tokens o etiquetas esperadas del corpus | Cinco controles normales con 13 eventos en total leídos y conservados en V2; recibo local de Cargas observado; criterios ampliados pendientes |
| F6-02 | XSS almacenado, IDOR, CSRF, SSRF y permisos de atraque | Modos vulnerable/corregido, controles normales, reset, evidencia HTTP/negocio y prueba de navegador cuando corresponda | Cinco controles normales de variante 1 corregida observados; otros tipos/variantes, navegador y regresión pendientes |
| F7-01 | Ejercicios para configuración, suministro, criptografía, integridad, registro y excepciones | Catálogo con tipo de ejercicio explícito y artefactos ficticios verificables | Código preparado; ejecución pendiente |
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
