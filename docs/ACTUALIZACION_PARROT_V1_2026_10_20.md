# V1 — Actualización y recuperación guiadas en Parrot — 20–21/10/2026

**V1 completada el 21/10/2026 en el alcance local acordado.** El usuario pidió iniciar
V1 y eligió ejecutar los pasos en la terminal de Parrot. Codex prepara y revisa
el recorrido desde Windows; no dispone de una conexión operativa a esa VM.
Las instrucciones no cuentan como ejecución ni como evidencia de éxito.

## Destino y alcance

Actualizar la instalación existente a la entrega local `v0.1.0`, cuya etiqueta
apunta a `4c13abd8612d11e843ae5903e89ab97e6c4cbfae`; el código de producto probado
es `0d73ec2`, CI39466610699. [Acta C4](ENTREGA_LOCAL_C4_2026_10_20.md).
Se mantienen las aceptaciones C2/C3, sus límites y riesgos residuales.

V1 comprende respaldo y recuperación verificados antes de aplicar cambios,
actualización controlada, inventario y lectura de los informes conservados.
No incluye nuevos análisis LLM, nuevos ataques DVWA, notificaciones externas,
reinicialización de DVWA o borrado de datos. No se cambia la etiqueta publicada.

## Etapas y evidencia necesaria

| Etapa | Evidencia antes de avanzar | Estado |
| --- | --- | --- |
| 1. Estado inicial | Checkout/cambios locales, intérprete y contenedores reales, con imágenes y estado; sin mostrar variables ni credenciales | Checkout `88e7b8a` sin cambios, Python 3.11.17; tres contenedores detenidos. Segunda inspección acredita ImageID y volumen DB; sin montajes en Mailpit/DVWA |
| 2. Aplicación | Ventana sin trabajos activos, servicios propios detenidos; respaldo `verified=true` y restauración en destino nuevo, conservando fuentes | CLI de respaldo y recuperación verificados, 26 archivos; piloto DB/publicación `verified`, dos trabajos succeeded/tres failed, ninguno activo y entregas vacías. Evidencia por captura, sin lectura de bytes VM por el agente |
| 3. Laboratorio | Identificar base/volumen/imágenes reales; guardar y verificar copia DB, conservar accesos necesarios y correo; ensayar recuperación aislada antes de recrear o reutilizar el volumen | Copia fría DB/imagen, tres sumas coinciden y 455M. Ensayo DB correcto con 10.11.19, cinco usuarios/cuatro tablas OK, clon detenido conservado. Imágenes Mailpit/DVWA, exportación Mailpit y logs conservados: cinco sumas coinciden, 658M; almacenamiento temporal, cero SQLite encontrados, sin leer/enviar correo |
| 4. Actualización de aplicación | Checkout limpio o cambios preservados, destino V2/tag verificado, instalación/build y contrato estricto 172/0/0 en la VM | Captura del 21/10: instalación completada, existing_preserved, ACTUALIZACION_APP_V1=OK, HEAD 4c13abd, Node v24.21.0/pnpm 11.19.0; contrato e instantánea 172/0/0. Recibo VM local, sin bytes/hashes recibidos |
| 5. Aplicación de laboratorio | Confirmar compatibilidad del motor existente y pines; aplicar cambios necesarios con copia verificada y retorno definido, comprobando imagen, volumen, red y puertos reales | DB operativa actualizada/healthy/mismo volumen/cinco usuarios/cuatro tablas OK. DVWA/Mailpit Healthy, pines verificados, redes/montajes comprobados y bindings efectivos loopback 4280/8025/1025. Ambas conservaciones SHA correctas y access.log local sin cambios; SERVICIOS_LAB_V1=OK |
| 6. Lectura y cierre | Arranque de lectura, fuentes/informe anterior conservados y cierre correcto; recibos y límites registrados | Portal funcional confirmado; preflight posterior Preparado, 25 archivos no SQLite iguales al respaldo, mismo análisis/dos grupos y conteos SQLite failed 3/succeeded 2. CIERRE_APP_V1=OK; tres servicios Docker running |

Las etapas son puertas de avance: un fallo se revisa y las fuentes se conservan.
No se fuerza un checkout limpio, se eliminan locks o se modifica la base viva
para conseguir un resultado esperado. La promoción de datos recuperados a una
ruta operativa requiere un procedimiento concreto revisado previamente.

## Conservación separada

La captura del respaldo acredita que el CLI terminó con
`files=26` y `verified=true`, destino
`.local-backups/operational-20261020T212059602675Z`. Registra como ausentes
`.local-state/analysis.sqlite3` y `logs/access.log`, ambas rutas del perfil legacy.
No se han recibido los bytes de esa copia. La captura posterior del CLI de
recuperación acredita `verified=true`, 26 archivos y destino nuevo
`.local-state/recovery/restore-20261020T212238483366Z`. Legacy figura ausente;
piloto DB/publicación verificados, dos trabajos succeeded y tres failed,
sin queued/running ni entregas. Conserva la generación del análisis
`4ca7c97703a44256874e475d64671055`. Esto acredita el recorrido aislado del CLI,
no una sustitución de datos vivos ni una restauración del volumen MariaDB.

La captura inicial del usuario muestra `web-defense-ai-v2-lab-dvwa` con
`ghcr.io/digininja/dvwa:b496a5d`, `web-defense-ai-v2-lab-mailpit-1` con
`axllent/mailpit:v1.31.1` y `web-defense-ai-v2-lab-dvwa-db-1` con
`mariadb:10.11`; los tres `Exited (0) 5 days ago`. Esto acredita referencias
de imagen y contenedores detenidos, sin identificar aún sus ImageID/digests,
montajes, integridad de DB o contenido recuperable del buzón. Tampoco prueba
que Flask/Next/worker estén detenidos o que no existan trabajos activos.

La inspección posterior acredita ImageID con prefijos `41096ae99134` (MariaDB),
`eb6a74c41b32` (Mailpit) y `7c65cc0145a5` (DVWA), con los tres todavía exited.
MariaDB monta el volumen nombrado `web-defense-ai-v2-lab-dvwa-db` en
`/var/lib/mysql`; Mailpit/DVWA no muestran montajes. No se atribuye a estas
imágenes el digest actualizado de C4 ni una versión exacta del servidor aún.

Siguiente puerta: copiar los datos del contenedor DB detenido y guardar su
imagen exacta en una carpeta nueva ignorada, permisos privados, comprobar
lectura de los TAR y SHA-256 y después probar recuperación en un destino DB
aislado. El comando se detiene ante errores y no arranca servicios ni elimina
contenedores/volúmenes. Validar un TAR/hash no demuestra aún integridad de la
base restaurada. Docker documenta [copias de contenedores detenidos](https://docs.docker.com/reference/cli/docker/container/cp/)
y [conservación de imágenes con docker save](https://docs.docker.com/reference/cli/docker/image/save/).

La captura siguiente del usuario acredita tres resultados «La suma coincide»
para `mariadb-data.tar`, `mariadb-image.tar` y `mariadb-image-id.txt` en
`.local-backups/v1-lab-elD9XbwF`, tamaño `455M` informado por `du`. Corresponde
al bloque enviado en el chat (tres archivos en SHA256SUMS); no incluye el cuarto
archivo de metadatos de una variante local del borrador. No se han recibido los
hashes individuales ni los bytes de los TAR. Los archivos quedan conservados.

El ensayo propuesto crea un volumen nuevo con nombre único, extrae allí la
copia y arranca una instancia con el ImageID original, sin red ni publicación
de puertos. No monta el volumen operativo. Comprueba
[InnoDB con healthcheck.sh](https://mariadb.com/docs/server/server-management/automated-mariadb-deployment-and-administration/docker-and-mariadb/using-healthcheck-sh)
y [tablas con mariadb-check](https://mariadb.com/docs/server/clients-and-utilities/table-tools/mariadb-check),
sin repair ni upgrade. La conexión usa el usuario/contraseña de laboratorio DVWA
del Compose histórico, no credenciales de proveedor ni el `.env` de aplicación.
El conteo de usuarios sirve como referencia para comparaciones posteriores,
sin mostrar sus filas. La instancia de ensayo se detiene al terminar; contenedor,
volumen y diagnósticos se conservan. Un fallo no autoriza cambios sobre la DB viva.
El primer intento del bloque de ensayo se detuvo en la línea 6 con carpeta
de respaldo no encontrada: el nombre se había transcrito de la captura como
`v1-lab-elD9XbwF`. La secuencia falla antes de crear el volumen/contenedor;
no acredita una restauración DB. El nombre real se solicitará como texto
mediante listado de directorios, sin renombrar la copia o repetir el respaldo.
El resultado previo de las tres sumas queda conservado como evidencia del
respaldo, pero el nombre transcrito aún no se toma como ruta confirmada.
No se ha actualizado Parrot.

El listado posterior del usuario muestra una única carpeta que coincide con
`.local-backups/v1-lab-*/`. Para evitar otra transcripción desde una imagen,
la receta revisada usa un array Bash de directorios con nullglob y exige una
sola coincidencia; con cero o varias se detiene. Imprime la ruta seleccionada
y valida SHA256SUMS antes de crear recursos Docker. No se elige por fecha ni
se cambia el nombre de la copia. La selección propuesta todavía no acredita
ejecución ni recuperación DB correcta.

La captura posterior sí acredita `RECUPERACION_DB=OK` con selección automática
y tres sumas coincidentes. Instancia
`webdefense-v1-restore-20261020213752-16102`, volumen con el mismo nombre más
`-data`: MariaDB `10.11.19-MariaDB-ubu2204`, cinco usuarios y comprobación OK
de `dvwa.access_log`, `dvwa.guestbook`, `dvwa.security_log` y `dvwa.users`.
Según la receta enviada, el ensayo usó volumen nuevo/red none, detuvo la
instancia al terminar y conservó volumen/contenedor/log. La captura acredita
el recorrido de recuperación reportado, sin recibir los bytes de los datos.
No es una prueba de los pines nuevos ni modifica el volumen operativo.

Para Mailpit, la [documentación de almacenamiento](https://mailpit.axllent.org/docs/configuration/runtime-options/)
indica que el archivo temporal predeterminado se elimina al salir. El contenedor
ya estaba detenido; no se promete recuperar mensajes anteriores. Antes de
recrearlo hay que comprobar qué archivos/configuración de persistencia quedan
y conservar los datos recuperables, sin usar envíos para reconstruir el buzón.

El paso siguiente conserva las imágenes exactas de Mailpit/DVWA, el sistema
de archivos del Mailpit detenido y los logs de ambos contenedores en un
subdirectorio nuevo de la copia existente, con sumas comprobadas. Se verifica
antes que Mailpit siga sin montajes: [docker export no incluye volúmenes](https://docs.docker.com/reference/cli/docker/container/export/).
La revisión local resume modo de almacenamiento y número de archivos con
cabecera SQLite, sin mostrar configuración, mensajes o filas. Una configuración
externa, SQLite recuperable o error requiere revisión antes de recrear Mailpit.
La ausencia de SQLite en la exportación no acredita que nunca existieran correos.
El [código Mailpit 1.31.1](https://github.com/axllent/mailpit/blob/v1.31.1/internal/storage/database.go)
confirma archivo temporal predeterminado y su eliminación al cierre.

La última captura del usuario acredita las cinco sumas coincidentes de
`image-ids.txt`, `imagenes-mailpit-dvwa.tar`, `mailpit-files.tar`,
`dvwa-container.log` y `mailpit-container.log`, en un subdirectorio nuevo
`conservacion-*` de la copia DB existente, con tamaño informado `658M`.
La revisión resume `almacenamiento_mailpit=temporal`,
`archivos_sqlite_en_copia=0` y `correos_leidos_o_enviados=false`.
No se han recibido los archivos ni sus hashes individuales. La revisión
no acredita recuperar mensajes anteriores ni la ausencia histórica de correo.

En la continuación del 21/10 se prepara la etapa 4: exigir checkout limpio y
origen V2, obtener la etiqueta `v0.1.0`, comprobar su commit completo y avanzar
solo mediante fast-forward; preparar Node 24 y pnpm 11.19.0, instalar y compilar
con el lanzador, comprobar el contrato estricto y guardar un inventario nuevo.
El código de `scripts/setup_installation.py` conserva el `.env` existente
mediante creación exclusiva, sin leerlo. El lanzador rechaza puertos ocupados,
trabajos activos o bloqueos incompatibles. No se eliminan bloqueos para forzar
la instalación. Este bloque todavía es una propuesta para ejecutar en Parrot;
no acredita actualización, instalación o inventario VM. La aplicación de
Compose y la compatibilidad del pin DB sobre una copia permanecen pendientes.

La captura recibida el 21/10 acredita `existing_preserved`, instalación
completada, contrato estricto de 172 paquetes/0 diferencias/0 adicionales sin
fijar y la misma cuenta en la instantánea. Termina con
`ACTUALIZACION_APP_V1=OK`, commit corto `4c13abd`, Node `v24.21.0` y pnpm
`11.19.0`; muestra una ruta nueva `.local-state/v1-install-*`.
La receta comprueba el commit completo de destino antes de instalar; la
captura acredita su resultado comunicado, sin recibir el inventario completo
ni verificar directamente sus bytes o los del `.env`.

Próximo paso de la etapa 5: descargar únicamente el pin MariaDB de Compose
y verificar linux/amd64/ImageID contra el registro del 19/10. Ejecutar solo
`mariadbd --version` en un contenedor efímero sin red ni volumen operativo,
antes de preparar el ensayo con datos clonados. No se asume que pertenecer
a la rama 10.11 descarte un descenso de versión frente al servidor original
10.11.19; la versión concreta debe revisarse antes de montar una copia.
Descarga, versión y compatibilidad del candidato todavía pendientes.

La captura siguiente acredita descarga completa del digest
`sha256:0d0945c57f75b3a3b9ebe71aedaaad005fa5305054e8fca3d2e42a8c92b43b5e`,
ImageID `sha256:4e667183d5236dbbecf88167a0f1f49dc0c116aa46990309e920e663e2fdc348`
y `mariadbd Ver 10.11.19-MariaDB-ubu2204` para x86_64, terminando con
`IMAGEN_DB_VERIFICADA=OK`. Se observa un aviso al consultar la dirección MAC;
no impide consultar la versión. El contenedor de versión no monta los datos.
La versión coincide con la de la instancia original, sin acreditar todavía
compatibilidad de los datos con los bytes de esta nueva imagen.

Se prepara un ensayo separado con un volumen nuevo y otra extracción del
respaldo frío, conservando el primer clon de recuperación. Antes de arrancar,
se comprueban sumas, ImageID y ausencia de procesos usando el volumen original.
El candidato usa red none/sin puertos, sin auto-upgrade; se comprueban InnoDB,
cinco usuarios, tablas DVWA y cierre con código 0. Recibos, log y clon quedan
conservados. La receta propuesta no acredita ejecución ni permite concluir
que ya se aplicó Compose sobre el volumen original.

La siguiente captura acredita el ensayo del candidato:
`webdefense-v1-pin-20261021134202-11594`, volumen homónimo más `-data`,
con tres sumas coincidentes, MariaDB `10.11.19-MariaDB-ubu2204`, cinco usuarios
y cuatro tablas DVWA OK. Termina `COMPATIBILIDAD_DB_V1=OK` y
`ESTADO_ENSAYO=exited`; la receta comprueba también código de salida 0.
El volumen original permanece fuera de este ensayo.

Se prepara la aplicación de la imagen fijada a **solo `dvwa-db`**, exigiendo
commit/Compose intactos, fuentes detenidas, backup SHA válido, ImageID y montaje
original esperados, y red interna. La receta Compose especifica proyecto,
archivo y `--env-file /dev/null`, usa `--no-deps --pull never --wait` y conserva
el volumen nombrado. Docker documenta que [up recrea el contenedor conservando
los volúmenes montados](https://docs.docker.com/reference/cli/docker/compose/up/).
Después comprueba imagen, mismo volumen, salud, red interna única sin puertos
publicados y DB/usuarios/tablas. Guarda recibos privados en una carpeta nueva;
DVWA/Mailpit continúan detenidos hasta su paso separado.

Retorno ante fallo: detener `dvwa-db` y conservar log, contenedor, volumen y
recibos. No reintentar automáticamente ni arrancar el ImageID antiguo sobre
el volumen que ya haya abierto el candidato. El retorno utiliza la copia fría
verificada y el ImageID original guardado: extracción a **otro volumen nuevo**
según el procedimiento de recuperación ya probado, healthcheck/usuarios/tablas
y cierre correcto. Una promoción posterior usaría un override local de Compose
que fije ese ImageID y el volumen recuperado como externo; debe revisarse ese
override antes de aplicarlo y conservar el volumen que falló. No requiere
reset, upgrade, borrado de volumen ni sustitución del TAR. La prueba anterior
acredita recuperación aislada con esa imagen; no se ha realizado un retorno
operativo. En ese punto el bloque de actualización DB todavía no se había ejecutado.

El intento siguiente, recibido por dos capturas, muestra tres sumas coincidentes
y `unknown flag: --env-file`, seguido de «Actualización detenida». El error
ocurre al interpretar la invocación Compose, antes de ejecutar `up`; no acredita
recreación ni actualización de DB. La parada del manejador utiliza la misma
invocación incompatible y tampoco se toma como ejecutada. Antes del intento,
la receta exigía contenedores exited; se solicitará una inspección nueva del
estado real. Los recibos privados generados y el ensayo previo se conservan.

La receta asumía soporte de Compose sin comprobarlo en esa VM. Se corrige el
borrador local para validar versión y opciones antes de preparar una mutación.
El siguiente paso es solo lectura de versiones de Docker/Compose con y sin
guion, y estado/ImageID de los tres contenedores. No se repite la actualización,
se elimina `--env-file` sin alternativa revisada, se instala un plugin ni se
declara una causa concreta (ausencia de plugin frente a versión incompatible)
antes de recibir ese diagnóstico.

El diagnóstico recibido después identifica Docker `26.1.5+dfsg1`, build
`a72d7cd`, ausencia del subcomando `docker compose` y ejecutable
`docker-compose` con versión `v5.1.0`. Los tres contenedores continúan exited
con los ImageID originales: DB `41096ae99134...`, DVWA `7c65cc0145a5...` y
Mailpit `eb6a74c41b32...`. Confirma que el intento no actualizó la DB.
El [ejecutable independiente usa docker-compose](https://docs.docker.com/compose/install/standalone/);
no hace falta instalar otro Compose para corregir esta invocación.
La receta se adapta a ese ejecutable y valida `config --quiet`, con archivo
de entorno `/dev/null`, y las opciones de `up --help` antes de cualquier
mutación. Mantiene las comprobaciones de backup, imagen, volumen, red, salud
y tablas, los recibos privados y la parada ante fallo. La ejecución del bloque
corregido sigue pendiente del usuario en Parrot.

La captura posterior acredita ejecución correcta con `docker-compose v5.1.0`:
tres sumas coincidentes, contenedor DB Healthy, MariaDB
`10.11.19-MariaDB-ubu2204`, cinco usuarios y cuatro tablas DVWA OK.
Muestra ImageID `4e667183d5236dbbecf88167a0f1f49dc0c116aa46990309e920e663e2fdc348`,
estado running/salud healthy, `DB_ACTUALIZADA_V1=OK` y el volumen original
`web-defense-ai-v2-lab-dvwa-db`. Los recibos quedan en una carpeta nueva
`.local-state/v1-db-live-*`. La receta verifica además red interna única y
ausencia de puertos publicados. No se recibieron esos archivos de la VM.
Este resultado reemplaza el intento anterior como evidencia de actualización;
no se repite el bloque que exige ImageID antiguo.

Se prepara el paso DVWA/Mailpit: verificar la conservación SHA previa, los
contenedores antiguos detenidos, DB saludable y las redes esperadas; descargar
solo los pines de Compose y comparar sus ImageID con los auditados. Arrancar
esos dos servicios sin dependencias y comprobar imágenes, estados, redes,
bindings efectivos `127.0.0.1:4280/8025/1025` y ausencia de montajes.
Los bindings son una comprobación de configuración real, no una certificación
general de aislamiento. Ante un fallo se detienen solo esos dos servicios y
se conservan logs/recibos; la DB queda separada. El respaldo de sus imágenes
originales y del sistema de archivos Mailpit ya fue verificado.

La copia local `.local-state/dvwa-lab/access.log` se verifica por SHA antes y
después; no se ejecuta `dvwa_lab_capture`, peticiones HTTP al laboratorio,
LLM ni envíos SMTP en este paso. Así no se sustituye esa fuente histórica por
los logs de un contenedor recreado. La siguiente fase de lectura comprobará
la publicación structured conservada, sin worker ni nuevos análisis.
El arranque DVWA/Mailpit de este bloque todavía no se ha acreditado.

El usuario informa después «dio error en línea 15» y aporta captura del mensaje
de parada. En el bloque exacto enviado en el chat (con sus líneas en blanco),
esa línea exige una única subcarpeta `conservacion-*`. Se detiene antes de
validar los cinco SHA, descargar imágenes o ejecutar `up`. El mensaje no
distingue cero de varias coincidencias; no atribuir carpeta ausente ni múltiples
copias sin listado. Se prepara un diagnóstico de nombres/cantidades de carpetas
y estado/ImageID de los tres contenedores. No repetir conservación ni escoger
la primera/última carpeta automáticamente. Las guardas del borrador local se
mejoran para explicar el conteo encontrado; la selección se ajustará después
de recibir el diagnóstico. La DB operativa correcta sigue siendo la última
evidencia disponible, sin una inspección nueva aún.

El listado posterior acredita una carpeta `v1-lab-*` y dos subcarpetas
`conservacion-*`: resuelve la causa de la parada anterior, sin demostrar aún
que ambas estén completas. La misma captura muestra DB running con ImageID
fijado `4e667183d523...`, y DVWA/Mailpit exited con los ImageID anteriores.
No se transcriben sufijos para nuevas órdenes ni se elimina una copia.

Se revisa el bloque para validar **todas** las carpetas de conservación, sin
elegir por orden, fecha ni nombre. Cada una debe contener SHA256SUMS y los cinco
archivos de contenido esperados; sus sumas deben coincidir y los dos ImageID
guardados deben corresponder a los contenedores detenidos. Si una está
incompleta o no verifica, se detiene antes de descargar/recrear y explica
ruta/archivo, sin ocultar el fallo usando otra copia. Si todas pasan, continúa
con los mismos pines, guardas de red/puertos, recibos y hash de access.log del
bloque anterior. Ninguna carpeta se modifica ni se exige que sus TAR tengan
bytes idénticos entre copias. La ejecución revisada aún no está acreditada.

La captura siguiente sí acredita ejecución de ese bloque: las dos carpetas
verifican cinco sumas cada una; los pines DVWA/Mailpit se descargan y ambos
contenedores figuran Healthy. El validador informa running/imagen verificada,
DVWA con `80/tcp -> 127.0.0.1:4280` y Mailpit con
`1025/tcp -> 127.0.0.1:1025`, `8025/tcp -> 127.0.0.1:8025`.
La copia local `.local-state/dvwa-lab/access.log` conserva su suma y termina
`SERVICIOS_LAB_V1=OK`, con recibo nuevo `.local-state/v1-services-*`.
La receta comprueba redes esperadas, ausencia de montajes en ambos servicios
y DB healthy; no se han recibido los archivos de recibo de la VM. Conserva
ambas copias, sin elegir una por orden ni atribuirles igualdad mutua de bytes.

Se prepara lectura: comparar todos los archivos `kind=file` del respaldo de
aplicación ya verificado `operational-20261020T212059602675Z` con las rutas
actuales por SHA. No comparar el archivo SQLite vivo con su snapshot binario
ni leer `.env`. Validar la publicación actual con `load_current` y comprobar
que mantiene el análisis `4ca7c97703a44256874e475d64671055`; contar los grupos
sin volver a clasificarlos o reescribir el informe. Después ejecutar preflight
y lanzador structured con Node 24. El perfil es pilot/lectura, análisis manual
deshabilitado, destinos de notificación vacíos y sin worker.
Falta evidencia del arranque, lectura de Resumen/Reportes y del cierre por
Ctrl+C con puertos libres y datos conservados; la etapa 6 sigue abierta.

La siguiente captura acredita `DATOS_CONSERVADOS=OK` con 25 archivos no SQLite
iguales al respaldo, mismo análisis `4ca7c97703a44256874e475d64671055` y
`GRUPOS_DEL_INFORME=2`. Node `v24.21.0`, preflight Preparado y lanzador
«Consola lista» en `http://127.0.0.1:3000`. El usuario confirma por texto
«accedi al portal y funciona ok». Es evidencia de arranque y navegación
general; no se recibió una captura nueva del detalle visual de Resumen o
Reportes. El SHA de la fuente publicada y su análisis sí se comprobaron.

Queda cerrar la consola con Ctrl+C y comprobar con preflight que los puertos
3000/5000 están libres. Se prepara además comprobación posterior por SHA de
los mismos archivos, `load_current` para el análisis conservado y consulta
SQLite read-only de conteos de trabajos (failed 3/succeeded 2, como en la
recuperación aislada anterior). No comparar el snapshot SQLite binario con
el archivo vivo ni afirmar igualdad de todos sus campos por conteos. El bloque
inspecciona el estado final del laboratorio sin detenerlo: Ctrl+C del lanzador
afecta a Flask/Next, no a los servicios Docker. `CIERRE_APP_V1=OK` aún no se ha
recibido y V1 permanece abierta hasta esa comprobación.

## Resultado final del 21/10 y alcance de la evidencia

La última captura sí acredita preflight posterior **Preparado**,
`DATOS_TRAS_CIERRE=OK` con 25 archivos no SQLite iguales al respaldo,
`ANALISIS_CONSERVADO=4ca7c97703a44256874e475d64671055`, dos grupos e historial
SQLite `failed=3`, `succeeded=2`, seguido de `CIERRE_APP_V1=OK`.
El preflight comprueba puertos 3000/5000 libres, entorno/build y ausencia de
trabajos activos; no se ha comparado el archivo SQLite vivo con su snapshot
binario ni se afirma igualdad de todos sus campos por los conteos.

La inspección final muestra los tres servicios **running** con los ImageID
fijados: DB `4e667183d523...`, DVWA `7c65cc0145a5...` y Mailpit
`978742ab0aca...`. Flask y Next han cerrado; el laboratorio Docker queda
arrancado. La salud y los bindings se comprobaron durante la aplicación de
los pines; la inspección final acredita estados e imágenes, no otra prueba
SMTP/HTTP o de conectividad.

Se cierra V1 en actualización, conservación, recuperación aislada y lectura
local. Las seis etapas de la tabla tienen evidencia del usuario por capturas
y confirmación textual. El agente preparó recetas y documentación desde
Windows; no tuvo acceso operativo a Parrot ni recibió los bytes completos de
sus backups, inventarios o recibos. [Resumen estructurado](ACTUALIZACION_PARROT_V1_2026_10_20.json).

La prueba de recuperación abarca aplicación y datos MariaDB en destinos nuevos,
no una restauración completa de VMware ni una promoción de respaldo a servicio
operativo. Mailpit usaba almacenamiento temporal y su exportación no contenía
SQLite; no se afirma recuperación de correos anteriores. Se conserva el informe
aceptado del 15/10 sin reanalizarlo: no hay nuevos ensayos LLM, ataques o envíos
solicitados por este recorrido. C2/C3 mantienen sus límites y riesgos residuales.

El código/tag `v0.1.0` no se modifica. Tras registrar el cierre local, el usuario
autorizó expresamente el 21/10 el commit y push de estas actas y guías. Se
incorporan en esta actualización documental posterior, sin nueva CI ni nueva
release. No se atribuye a C4 la ejecución posterior de V1. Los recibos privados
y los datos de la VM permanecen excluidos de la publicación.

## Conservación para uso posterior

El [respaldo de aplicación](OPERACION_RECUPERACION_2026_10_14.md) cubre perfiles
conocidos, publicaciones y SQLite; no incluye `.env`, volumen DB, imágenes o
buzón Mailpit. Conservar `.env` existente sin mostrar su contenido. Mailpit
carece de volumen en el Compose actual: exportar el correo que deba conservarse
antes de recrearlo. La captura local no reconstruye todos los logs rotados.

La referencia histórica `88e7b8a` usaba MariaDB 10.11 por etiqueta y Mailpit
1.31.1; no se toma como inventario actual. Hay que identificar lo que ejecuta
la VM antes de decidir cómo respaldar y actualizar. No habilitar
`MARIADB_AUTO_UPGRADE`, reinicializar DVWA o utilizar `down --volumes` como
procedimiento de actualización.

Los respaldos, exportaciones y recibos operativos permanecen locales e
ignorados. Solo se comparte para revisión la salida necesaria, sin credenciales,
contenido de correos, filas DB o registros crudos. El cierre registrado arriba
se limita a las etapas efectivamente acreditadas.
