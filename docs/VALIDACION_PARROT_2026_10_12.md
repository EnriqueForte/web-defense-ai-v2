# Validación guiada en Parrot — 12/10/2026

Seguimiento 14/10: capturas acreditan Docker26.1.5+dfsg1 respondiendo Linux/x86_64,
Compose independiente `docker-compose` v5.1.0 y validación de `compose.lab.yaml`
con salida 0, en `e5af1a6`. El usuario informa laboratorio todavía no preparado.
Registro y límites en [operación/recuperación](OPERACION_RECUPERACION_2026_10_14.md).
No se acredita arranque de contenedores o análisis real por esas consultas.

El usuario clonó `EnriqueForte/web-defense-ai-v2` en el disco local de su VM
y ejecutó las instrucciones desde una terminal de Parrot. Evidencia: capturas
aportadas en la conversación y confirmación explícita de navegación correcta.
No se dispuso de acceso remoto a la VM ni se obtuvieron logs completos.
El commit comprobado en el ensayo inicial fue `df40ad8`, con `main` y `origin/main`
coincidentes. El ensayo posterior del lanzador unificado se recoge al final;
su SHA no aparece en las nuevas capturas.

## Entorno y preparación

- VMware Workstation Pro 26H1, versión 26.0.1 según captura.
- Parrot Security 7.3 (echo), x86_64; `/etc/os-release` informa Debian 13.5.
- Memoria total 15 GiB y 37 GiB de disco disponibles en la comprobación inicial.
- Git 2.47.3. Inicialmente Python 3.13.5 y Node 20.19.2; pnpm y Python 3.11 ausentes.
- Se guio instalación de Python 3.11 con uv y Node 24 con nvm en el usuario.
  Las capturas finales confirman Python 3.11.17, Node 24.21.0, npm 11.19.0 y
  pnpm 11.19.0. No se solicitó reemplazar el Python de Parrot.
- Instalador común con `--install --frontend --init-env`: entorno `.p2`,
  dependencias frontend y plantilla local `.env`; salida final `created`.

## Resultados observados

| Comprobación | Evidencia recibida |
| --- | --- |
| Python del entorno | 3.11.17 |
| `pip check` | No broken requirements found |
| Contrato Linux | 157 paquetes fijados, cero diferencias |
| Baseline | 269 Python aprobadas y tres comprobaciones JS aprobadas |
| HTTP sintético | Flask, CSP, informe y recursos/hash verificados |
| CrewAI/LiteLLM offline | 25 escenarios aprobados, sin proveedor |
| Frontend | lint/tipos sin errores visibles, 15 grupos UI y build Next 16.3.8 completados |
| Arranque | Perfil pilot/legacy, Flask en 127.0.0.1:5000 y Next producción en 127.0.0.1:3000 |
| API directa/proxy | Salud HTTP 200 en ambos puertos |
| Navegación | Captura de Resumen; usuario confirma Amenazas, Reportes, Actividad y Configuración sin errores |

Se indicó ejecutar `check_syntax.py`, pero su resumen no aparece en las capturas;
no se atribuye una comprobación visual independiente de sus 71 archivos en esta VM.

La primera lectura de Next devolvía 500 y el acceso directo a 5000 rechazaba
la conexión. Después de arrancar Flask, la API directa y el proxy dieron 200.
La navegación inicial a 5000 mostraba la interfaz Flask conservada; 3000 muestra
la nueva interfaz. No fue necesario cambiar código para resolver la incidencia.

El estado final «Fuentes incompletas» corresponde a la ausencia de logs e informes
en este clon. No hay datos del mantenedor copiados. Manual deshabilitado y worker
sin arrancar; no se solicitaron llamadas reales al proveedor, Docker o envíos.
Las terminales Flask y Next quedaron abiertas al terminar el ensayo inicial.
La comprobación posterior del cierre corresponde al lanzador unificado descrito abajo.

## Alcance y siguiente entrega

Quedan acreditados instalación, pruebas offline, build, arranque y lectura en
esta VM Parrot. No se acredita Docker/DVWA, ingesta ni análisis real en Parrot,
otras distribuciones/versiones/arquitecturas o calidad semántica A-05.
El [seguimiento del contrato Linux](CONTRATO_LINUX_2026_10_12.md) capturó el
inventario completo Ubuntu y fijó `uvloop==0.23.0`. La comprobación posterior
del inventario en esta VM también pasó, según el apartado final.

La batería de pruebas pertenece a la validación de desarrollo. Para usuarios,
el instalador unificado posterior automatiza dependencias y build, pero requiere
Python 3.11, Node 24 y pnpm 11.19.0 previamente disponibles.

## Ensayo posterior: instalación y arranque unificados

Tras indicar actualización a `f8318d6`, el usuario aportó estas evidencias.
No se recibió una captura del SHA actualizado; no se certifica ese SHA en la VM.

- Instalación finalizada: pip check correcto, 157 paquetes fijados sin diferencias,
  pnpm 11.19.0, build Next 16.3.8 y `existing_preserved` para configuración existente.
- `python3 webdefense.py start` confirmó «Consola lista» en 127.0.0.1:3000.
  El usuario confirmó que la web funciona y que cambió entre vistas.
- Tras indicar Ctrl+C, dejó de cargar la web. Tres comprobaciones `check`
  mostraron puerto 3000 ocupado: el reinicio inmediato no quedó validado.
- Más tarde `ss -ltnp` y `ss -tan state time-wait`, filtrados por 3000/5000,
  mostraron únicamente cabeceras. `python3 webdefense.py check` terminó preparado.
  Queda confirmado el cierre con puertos libres después de la espera.

La duración de la espera no se midió. No se capturó el estado de sockets durante
el fallo; TIME_WAIT es una explicación compatible, no una causa probada de ese
episodio. La [corrección del comprobador](CORRECCION_PUERTOS_2026_10_12.md)
se publicó como `2a73ff0` y pasó Windows/Ubuntu CI, incluida la regresión real
de sockets residuales en Ubuntu. Su ensayo posterior en la VM se recoge a continuación.
No se solicitaron motor, proveedor, Docker ni notificaciones para este recorrido.

## Confirmación posterior del ajuste de puertos

Tras indicar `git pull --ff-only` hasta `e1f7383` (documentación; código probado
`2a73ff0`) y el recorrido de cierre/comprobación/arranque inmediato, el usuario
confirmó «perfecto ya funciona correctamente». La captura muestra:

1. `python3 webdefense.py check`: «Preparado».
2. `python3 webdefense.py start`: «Consola lista» en 127.0.0.1:3000.
3. Ctrl+C: «Consola detenida».
4. `python3 webdefense.py check`: «Preparado», sin aviso de puerto ocupado.

Entre comandos aparecen dos intentos de ejecutar una ruta Windows en zsh,
rechazados como comando inexistente; las órdenes de la herramienta terminan
correctamente. No se midió la demora entre comandos, ni se recibió la salida
Git del SHA actualizado. El segundo arranque después del último check no aparece
en la captura. La aceptación explícita del usuario completa la validación guiada
del ajuste en esta VM, con esos límites de evidencia. El último estado visible
es consola detenida y preflight preparado; no se afirma servicio activo.

La instalación, lectura entre vistas, arranque y cierre del flujo unificado quedan
aceptados en esta VM. Docker/ingesta/análisis real siguen fuera de esta validación;
el inventario Linux se comprobó posteriormente.

## Contrato completo e inventario de dependencias

Nueva captura del usuario: commit `86c21b5`, con main/originmain/originHEAD
coincidentes. `.p2/bin/python -m pip check` termina sin requisitos rotos;
`check_environment.py --strict` informa158pines/0diferencias/0adicionalessinfixar;
`snapshot_environment.py` informa instantánea158/0diferencias/0adicionales.

El contrato Linux completo y la exportación del inventario quedan comprobados en
esta VM, incluyendo uvloop0.23.0 por la validación estricta. No se recibieron
los archivos exportados ni su hash desde la VM: la evidencia recibida es la
captura de ejecución satisfactoria. El freeze Ubuntu conservado sigue siendo
evidencia independiente. No fue necesario reinstalar paquetes para esta prueba.

## Actualización CrewAI — evidencia del 13/10/2026

Las nuevas capturas muestran instalación completada, `existing_preserved`,
CrewAI 1.15.27 y build Next 16.3.8 correcto. La comprobación posterior de pip
termina sin requisitos rotos; `check_environment.py --strict` y
`snapshot_environment.py` informan 172 paquetes, cero diferencias y cero extras.

El siguiente recorrido queda visible: `python3 webdefense.py start` anuncia la
consola lista en 127.0.0.1:3000; Ctrl+C anuncia consola detenida; el `check`
posterior anuncia preparado sin aviso de puerto ocupado. El estado final visible
es detenido y preparado. No se midió el intervalo entre cierre y comprobación.

El usuario confirmó que las vistas también cargaron correctamente tras esta
migración. Queda aceptado el recorrido de instalación, lectura, arranque y cierre
con el contrato de 172 paquetes en esta VM.
El SHA Git actualizado no aparece y no se recibieron los archivos freeze ni sus
hashes de esta VM. La aceptación de navegación anterior se conserva como evidencia
histórica, y la nueva confirmación acredita el recorrido posterior a la actualización. Véase el
[registro de migración](MIGRACION_CREWAI_2026_10_12.md). Docker, ingesta y análisis
real con proveedor siguen pendientes por separado.

## Laboratorio Parrot — evidencia recibida el 15/10/2026

La captura anterior de actualización muestra instalación completada,
`existing_preserved`, build Next 16.3.8 correcto y HEAD `292e812`. No aporta
un nuevo freeze ni sus hashes; no se trasladan los inventarios Ubuntu a esta VM.

Las nuevas capturas del usuario muestran `docker-compose --file compose.lab.yaml ps`:
DVWA está activo con imagen `ghcr.io/digininja/dvwa:b496a5d` y publicación
`127.0.0.1:4280`; MariaDB `10.11` y Mailpit `v1.31.1` aparecen activos y
saludables. Mailpit publica SMTP `127.0.0.1:1025` y web `127.0.0.1:8025`.
El puerto `1110/tcp` listado no muestra mapeo al host.

DVWA presenta Database Setup con servidor `dvwa-db`, base y usuario `dvwa`,
módulos mysqli/pdo_mysql instalados y carpetas escribibles. La advertencia
reCAPTCHA Missing corresponde al módulo Insecure CAPTCHA; no acredita un fallo
de conexión a MariaDB. Todavía no se recibió evidencia de creación de tablas,
inicio de sesión ni apertura de la bandeja web de Mailpit. La página de setup
por sí sola tampoco prueba la inicialización de la base.

El siguiente paso guiado es inicializar la base de este laboratorio declarado
nuevo mediante Create / Reset Database y entrar con las credenciales de prueba
documentadas por DVWA. No se ha ejecutado ese paso desde este equipo ni se
han iniciado servicios Windows, ingesta, análisis LLM o envíos. Captura de logs,
recorrido integrado y restauración del laboratorio siguen pendientes.

### Confirmación posterior de acceso y bandeja

El usuario aportó después una captura de la página Home de DVWA con menú de
módulos y Logout, compatible con sesión iniciada tras el paso de configuración.
No se recibió la salida de creación de tablas ni una consulta de integridad de
MariaDB; se acredita el acceso funcional visible, no esos controles internos.
La segunda captura muestra Mailpit en `http://127.0.0.1:8025/`, con bandeja
vacía (0 mensajes). Esto acredita la apertura de su interfaz, no una entrega
SMTP ni persistencia del buzón. El siguiente paso es capturar los accesos Apache
mediante `dashboard.services.dvwa_lab_capture`; todavía no consta su ejecución
en la VM. No se inició análisis, envío o servicio Windows en este seguimiento.

### Captura de accesos Apache

La siguiente captura del usuario acredita la ejecución satisfactoria de
`.p2/bin/python -B -m dashboard.services.dvwa_lab_capture`: informa 36 líneas
guardadas en `.local-state/dvwa-lab/access.log`. `wc -l` confirma 36 líneas en
esa ruta. No se recibieron los bytes ni el hash del archivo; no se atribuye
todavía validación de su contenido o lectura desde la consola. El perfil pilot
del lanzador usa esa ruta; se indica como siguiente paso el arranque en modo
structured de lectura, con manual desactivado y sin worker.

### Arranque pendiente por selección de Node en la sesión

El intento posterior `python3 webdefense.py start --mode structured` fue
rechazado por el requisito Node 24 o posterior, antes de iniciar los servicios.
El diagnóstico del usuario muestra Node `v20.19.2` en `/usr/bin/node` y
`zsh: command not found: nvm`. Esto acredita que nvm no está cargado en esa
sesión; no prueba que sus archivos ni Node 24 se hayan eliminado. La instalación
previa de Node 24 con nvm consta en este registro. Se propone cargar el script
del usuario y seleccionar la versión ya instalada antes de repetir el arranque;
la lectura de las 36 líneas en la consola sigue pendiente.

### Recuperación de Node y consola structured lista

Una captura intermedia mostró que la sesión buscaba nvm en `/root/.nvm`, donde
no existía el script. La captura posterior acredita cambio al usuario habitual
`qu1qu3h4ck`, carga de `$HOME/.nvm/nvm.sh` y selección con `nvm use 24`:
Node `v24.21.0`, npm `11.19.0`. No se acredita reinstalación de Node.
Un comando aislado `V` fue rechazado por zsh sin impedir el arranque posterior.

`python3 webdefense.py start --mode structured` muestra «Consola lista» en
`http://127.0.0.1:3000`, con logs de ejecución
`.local-state/launcher/20261015T162550Z-42138859`. El lanzador anuncia lectura
local y mantenimiento de la terminal abierta. El estado final visible es consola
activa; no se recibió todavía captura de Actividad ni confirmación de lectura
de las 36 líneas desde la interfaz. El arranque no habilita manual ni inicia
worker; tampoco se acredita análisis LLM o envío. La corrección fue en la sesión
de la VM, sin cambios de código, instalación o servicios Windows.

### Lectura de Actividad confirmada y corrección de propietario

Tras el arranque, Actividad mostraba `Origen: error` y «Log no disponible».
El diagnóstico aportado por el usuario mostró las carpetas `.local-state` y
`dvwa-lab` pertenecientes a su usuario habitual, pero `access.log` perteneciente
a `root:root` con permisos `600`. `wc -l` desde el usuario habitual falló por
permiso denegado. Se indicó cambiar únicamente el propietario de ese archivo
al usuario y grupo de la sesión habitual mediante chown, conservando sus
permisos restringidos.

El usuario confirmó la corrección y aportó captura de Actividad con
`Origen: available`, líneas Apache visibles, última petición 15/10/2026
18:20:43 (Madrid), última copia 18:20:52 y captura de interfaz 18:29:04.
Constan accesos a módulos SQLi/XSS/brute y una consulta con marcador XSS;
visitar una ruta o registrar un payload no acredita explotación ni un ataque
brute force por sí solo. No se recibió el archivo completo ni su hash.

Queda comprobado en esta VM el recorrido contenedores, acceso DVWA/bandeja,
captura de 36 líneas y lectura desde Actividad con consola structured. No se
acreditan todavía análisis, publicación de informe, entrega SMTP, cierre de
este arranque o restauración Docker. «Fuentes incompletas» permanece visible;
no se infiere un fallo de lectura del log a partir de ese estado agregado.
El siguiente paso previo al análisis es comprobar el estado del proveedor sin
mostrar credenciales. Las autorizaciones A-05 anteriores no se reutilizan.

### Proveedor guardado en la VM

El usuario aportó captura de Configuración tras guardar Groq con modelo
`groq/openai/gpt-oss-120b`: aviso «Configuración guardada. Se usará en el próximo
análisis» y estado «Hay una clave guardada». No se muestra la clave ni se ha
verificado su validez, disponibilidad del modelo o cuota mediante llamada real.
El guardado no contacta al proveedor. Esta elección de Groq en Parrot es distinta
de los ensayos OpenRouter anteriores y no hereda sus autorizaciones.

Antes de proponer la ejecución manual se debe comprobar que el usuario habitual
puede consultar Docker: el worker de ingesta requiere ese acceso y la captura
previa produjo un archivo root. El siguiente ensayo propuesto será un único
trabajo manual sobre el log del laboratorio, con el proveedor seleccionado,
reintentos internos del motor y sin repetir el trabajo si falla; destinos de
notificación vacíos y worker manual-only. Su autorización concreta está pendiente.

### Acceso Docker del usuario habitual pendiente

La comprobación `docker inspect --format '{{.State.Status}}'
web-defense-ai-v2-lab-dvwa` falló por permiso denegado sobre
`/var/run/docker.sock`. No demuestra caída del contenedor; bloquea la ingesta
desde ese usuario. Se indica añadir el usuario habitual al grupo docker y
activar el grupo mediante `newgrp docker`, siguiendo las instrucciones oficiales
de Docker para Linux. Este grupo concede privilegios equivalentes a root en
la VM. La verificación posterior y la ejecución de esos cambios no constan
todavía en la evidencia recibida. Los procesos ya abiertos no adquieren grupos
nuevos; el futuro worker deberá iniciarse desde una sesión con acceso verificado.

### Acceso Docker confirmado tras activar el grupo

La nueva captura acredita `sudo usermod -aG docker "$(id -un)"`, `newgrp docker`
y la repetición de docker inspect con resultado `running`, sin sudo en esa
consulta. Queda comprobado el acceso en la nueva shell; no se atribuyen grupos
nuevos a la consola que ya estaba abierta. El futuro worker se iniciará desde
una sesión con este acceso. Ninguna llamada LLM se ha acreditado en Parrot.

Alcance propuesto para autorización: un único trabajo manual del laboratorio
con Groq, modelo principal `groq/openai/gpt-oss-120b`, posibles reintentos internos
y alternativa `groq/openai/gpt-oss-20b` del catálogo ante rate limit. Incluye
sincronización del log del contenedor, análisis estructurado y publicación si
pasa las guardas; sin ciclos periódicos, notificaciones o repetición del trabajo
fallido. El timeout del subproceso del motor es 900 segundos, distinto del
límite de 600 segundos de los ensayos aislados anteriores. No se ha aprobado
ni iniciado esta propuesta; el estado de proveedor guardado no valida su cuota
o sus condiciones de uso. La evidencia de Actividad no garantiza hallazgos.

### Autorización del ensayo manual en Parrot

El usuario aceptó expresamente la propuesta anterior («sí») y preguntó quién
realizará los pasos. La ejecución será guiada: el usuario opera su VM; el agente
no dispone de acceso directo a ella. Se autoriza un único trabajo manual Groq
con el alcance y reintentos internos ya descritos, no repetirlo si falla ni
activar ciclos periódicos o notificaciones. Primero se sustituirá la consola
de lectura por Flask manual, worker manual-only y Next en terminales separadas.
Arrancar esos componentes no encola por sí solo el trabajo. Queda pendiente
evidencia de activación, solicitud única, resultado y revisión del informe.

### Activación manual comprobada

El primer intento mostró error de lectura 500 en Next. El curl directo del
usuario no pudo conectar a 127.0.0.1:5000; las terminales no mostraban salida de
Flask/worker tras el bloque con newgrp. No hubo evidencia de llamada LLM ni de
fallo del proveedor. Se indicó ejecutar los comandos de cada componente por
separado, en las shells ya abiertas.

La captura posterior muestra Flask con debug off en 127.0.0.1:5000 y respuestas
HTTP 200 a `/api/v1/estado` y `/api/v1/analisis/actual`. El panel del worker
confirma «ejecutor activo (solo solicitudes manuales)». Su preflight muestra
fuente structured ausente, jobs ausentes con queued/running cero y bloqueos
cycle/engine libres antes de arrancar. La ausencia del informe es compatible
con una instalación sin primer análisis. Todavía no se recibió evidencia del
POST de solicitud, consumo Groq o resultado. Se guía al usuario para actualizar
Resumen en Next 127.0.0.1:3000 y pulsar Iniciar análisis una única vez dentro
del alcance autorizado, sin repetir el trabajo si falla.

### Resultado del único trabajo manual: analysis_failed

El usuario aportó después captura de Resumen: trabajo `f217a6210aa3` (prefijo
visible), manual, failed, finished, `analysis_failed`; informe actual no
disponible. Ejecutor activo, solicitudes manuales habilitadas y proveedor groq.
La última copia del log figura a las 18:44:40 del 15/10/2026 (Madrid), con última
petición 18:20:43. Según el flujo del coordinador, `analysis_failed` se registra
tras sincronización satisfactoria cuando el subproceso del motor no termina
con éxito. No determina si hubo llamada al proveedor, autenticación, límite de
uso, formato inválido o rechazo de guardas. El ensayo no se repetirá con la
autorización ya consumida. Siguiente paso: lectura del receipt/checkpoint/process
del trabajo existente, sin nueva ejecución ni cambio de proveedor/modelo.

El usuario aportó después fragmentos del recibo: ID completo
`f217a6210aa3447084193573b5449a97`, 5,511 segundos, una llamada lógica y un intento
observado en detection; fallo HTTPStatusError en 0,609 s, sin número HTTP
retenido. La mejora local del diagnóstico y sus pruebas, el límite de evidencia
y la lectura propuesta de registros históricos Groq se documentan en
[incidencia Groq Parrot](INCIDENCIA_GROQ_PARROT_2026_10_15.md). No se repitió el
ensayo ni se instaló esa mejora en la VM.

La siguiente captura de Groq muestra una respuesta HTTP 400, conteo 1, a las
6:44pm en el gráfico. Coincide con el minuto esperado, sin ID de petición o
mensaje visibles; queda pendiente abrir su detalle en Logs. No se infiere la
causa concreta ni se repite el ensayo.

Logs de Groq aporta después la entrada 15/10/2026 18:44:49, HTTP 400,
invalid_request_error: `messages.0` de rol system contiene cache_breakpoint,
propiedad no soportada. Se identificó su origen en CrewAI y se preparó la
limpieza acotada al transporte Groq en main.py. Cuatro pruebas HTTP simuladas
y regresión 330 Python/3 JS/92 sintaxis/27 SDK pasaron localmente; no se repitió
el trabajo ni se actualizó todavía la VM. La [incidencia Groq](INCIDENCIA_GROQ_PARROT_2026_10_15.md)
recoge el mecanismo y los límites del arreglo. No se cierra A-05 por pruebas
sintéticas ni se solicita repetir con la autorización ya consumida.

La corrección fue después publicada como eefa51c y el ajuste de fixture de
pruebas como `646aaf20646854e4665f55f285cedfe2a06d45f5`. La primera CI tuvo
Ubuntu success y Windows fallo por tokenizador offline; la
[CI final 38776623228](https://github.com/EnriqueForte/web-defense-ai-v2/actions/runs/38776623228)
pasó ambos sistemas con 331 casos Python (Windows 330+1 omitido), 3 JS,
92 sintaxis, 27 SDK, nueve E2E por OS y smoke/cierre. Logs/estados/artefactos
verificados; véase el registro de incidencia para el alcance de la fixture
temporal y la limitación del recurso Windows original.
Pendiente actualizar esta VM con Flask, worker y Next detenidos y comprobar
el SHA recibido. No se solicitó reinstalar pines ni build por esta corrección
Python. La publicación/CI no repite ni autoriza otro análisis real.

### Actualización de la corrección recibida en Parrot

La nueva captura del usuario muestra fast-forward `292e812..3947554`, nueve
archivos actualizados, y `git rev-parse --short HEAD` devuelve `3947554`.
Queda acreditada la recepción del código y de las actas en el clon de la VM.
La captura no incluye estado de procesos/puertos, nuevo inventario de paquetes,
arranque posterior ni resultado de proveedor; no se extiende la evidencia a
esas comprobaciones. El código de CI sigue siendo 646aaf2; 3947554 solo añade
el acta final de verificación. No se pidió reinstalar ni recompilar.

El ensayo anterior `f217a6210aa3447084193573b5449a97` permanece fallido y su
autorización consumida. Se propone un nuevo trabajo manual único del log DVWA
con Groq 120b, alternativa 20b ante rate limit y reintentos internos existentes,
timeout del motor 900 s, sin ciclos, notificaciones o repetición automática si
falla. Su autorización está pendiente; actualizar Git no la concede.

El usuario autorizó después expresamente este nuevo ensayo («sí»). Se limita
a un trabajo manual nuevo con el alcance anterior, independiente del fallido
f217a6210aa3447084193573b5449a97. El usuario operará la VM y el agente guiará
la activación y revisión; no se encoló ningún trabajo desde este equipo. Se
indica reutilizar las tres terminales detenidas (Flask/worker con grupo Docker
ya activado), ejecutar cada comando por separado y solicitar el análisis una
sola vez cuando el ejecutor figure activo. Resultado todavía pendiente.

### Segundo trabajo: publicación visible y revisión de cobertura

Capturas posteriores muestran `6356df80e4994602ba3004fd2841e6a8`
succeeded/finished, referencia abreviada 9dd17c72e247 e informe publicado a
las 19:51:52 Madrid. El usuario confirma que se lee en Reportes; lo que falta
es su entrada en la tarjeta de Resumen, dedicada hasta ahora solo al historial.
Se observa un grupo XSS bajo, requiere investigación, línea 31; 30 líneas
seleccionadas de 36/seis omitidas. No se recibieron bytes/recibo/consumo de la
VM ni se acredita cobertura semántica general. Esta autorización queda consumida.

El usuario esperaba XSS y fuerza bruta. El último fragmento muestra tres POST
al formulario DVWA en 16 segundos y después GET de admin.jpg. La imagen no
registra el resultado de autenticación; tres envíos no alcanzan el umbral
predeterminado de cinco en 60 s, sin conocer aquí la configuración de la VM.
Además se identificó que la preparación estructurada ignoraba los POST DVWA
sin credenciales en la URL. Arreglo local y botón del reporte actual en
Resumen preparados, probados offline y documentados en
[corrección DVWA POST y Resumen](CORRECCION_DVWA_POST_RESUMEN_2026_10_15.md).
335 casos Python (334+1 omitido), 3 JS, lint/tipos/17 UI/92 sintaxis y builds
pasaron. Cambios sin publicar/CI nueva/instalar en Parrot; no nuevo LLM ni
recalcular el informe existente. Confirmación de acceso exitoso mediante
evidencia de aplicación y aceptación A-05 siguen pendientes.

La corrección se publicó posteriormente como
`4c2e032308066e6afbc1030887c6d55580f1fe51`. Su
[CI 38783207354, attempt 1](https://github.com/EnriqueForte/web-defense-ai-v2/actions/runs/38783207354)
terminó success en Windows y Ubuntu; estados, pasos, logs e inventarios/artefactos
comprobados. 335 casos Python (Windows 334+1 omitido), cuatro nuevos visibles,
3 JS/92 sintaxis/27 SDK/13 A-05+7 controles/lint/tipos/17 UI/nueve E2E por OS
y smoke API/proxy/cierre aprobados. El registro de corrección contiene los IDs
y límites de los artefactos. No acredita el enlace nuevo en navegador ni en VM.

Próximo paso guiado: detener las tres terminales de la VM, pull --ff-only,
activar Node 24, compilar frontend y arrancar la consola de lectura structured
para abrir el informe existente desde Resumen. El usuario aún no ha aportado
la actualización ni su aceptación en Parrot. No se solicitó otro trabajo real.

El usuario confirma después «ok ya aparece»: la entrada del reporte actual ya
es visible en Resumen de su VM. Confirmación textual sin captura/SHA/salidas;
no se atribuye una revisión de esos bytes o de cada comando. Pendiente abrir
el informe mediante el botón y comprobar el contenido existente. No se inició
ni autorizó otro análisis real; fuerza bruta en VM y aceptación A-05 pendientes.

Confirmación posterior: «sí es el mismo, sigamos con la prueba de fuerza bruta».
El enlace abre el informe esperado según el usuario, sin nueva captura/SHA.
Se prepara un ensayo nuevo: cinco envíos fallidos al formulario DVWA local en
menos de 60 s, captura y revisión offline; después un único trabajo manual Groq
con la configuración/límites ya descritos (900 s, sin ciclos/envíos/repetición).
La solicitud actual cubre este ensayo independiente, no reabre los anteriores.
Ningún tráfico o trabajo ha sido ejecutado desde este equipo. La preparación
y la activación manual de la consola de lectura aún están pendientes.

La captura siguiente acredita captura del log con 46 líneas y ocho POST nuevos
al formulario DVWA desde 172.18.0.1 entre 18:29:46 y 18:30:31 UTC (45 s).
Superan el umbral predeterminado 5/60, sin acreditar resultado de autenticación
por sus respuestas HTTP 200. No se piden más envíos. Pendiente ejecutar en la
VM la preparación offline con configuración local y mostrar regla/ráfagas;
después se activará el único trabajo manual ya solicitado. Sin salida de esa
preparación ni nuevo resultado LLM todavía.

La captura posterior sí verifica preparación offline: observed-access-4,
una ráfaga de ocho intentos, umbral cinco/ventana 60 s, intervalo 45 s,
líneas 39–46 y ocho referencias seleccionadas. Esta comprobación no llama al
proveedor ni publica. Se guía ahora el cambio de la consola unificada de
lectura a Flask manual, worker manual-only y Next en terminales separadas,
reutilizando para el worker la terminal con captura Docker correcta. Pendientes
activación y único análisis autorizado; no se repite automáticamente si falla.

El ensayo de fuerza bruta termina después failed/analysis_failed, prefijo
50f0fcc91e82. Groq muestra 413 para 120b/20b; detalle 20b TPM 8000/Requested
8103, type=tokens/code=rate_limit_exceeded. El informe anterior permanece en
la captura. Autorización consumida. Corrección local de prompt compacto y
normalización terminal del 413 probada: 339 Python/3 JS/92 sintaxis/27 SDK/
13 A-05+7 controles, sin proveedor real. Véase [incidencia Groq 413](INCIDENCIA_GROQ_413_2026_10_15.md).
Pendientes publicación/CI/VM; no más tráfico ni repetición del ensayo.

La corrección 413 se publicó después como
`33d987bf86e10b272adc79e57013bd504e958c0f`. CI 38790268742/attempt 1 success
Windows/Ubuntu, estados/pasos/logs/cuatro pruebas nuevas comprobados: 339
Python (Windows 338+1 omitido), 3 JS/92 sintaxis/27 SDK/13 A-05+7 controles/
lint/tipos/17 UI/nueve E2E por OS y smoke/cierre correctos. Inventarios y
resúmenes A-05 verificados; IDs y límites en el registro de incidencia.
Pendiente actualizar Parrot tras detener tres terminales; comprobar prompt9 e
iniciar lectura. Corrección solo Python, sin reinstalar o recompilar frontend.
La actualización no repite el ensayo ni autoriza un nuevo trabajo real.

Captura posterior acredita fast-forward 5c567d1..88e7b8a, HEAD88e7b8a,
structured-prototype-9 por import, Node24.21.0 e inicio unificado structured
de lectura con Consola lista en 127.0.0.1:3000. Sin nuevo inventario/hash VM o
análisis real. Se propone un único trabajo nuevo con Groq y alcance anterior
sobre la copia de 46 líneas/ocho POST, timeout 900 s, sin ciclos/envíos/repetición;
su autorización sigue pendiente y no reutiliza la del trabajo fallido.

El usuario responde después «sí» a un trabajo manual nuevo, con ese alcance:
captura existente 46 líneas/ocho POST, Groq120b/alternativa20b ante429,
reintentos internos y timeout 900 s, sin ciclos/envíos/repetición automática.
Se guía activación Flask manual/worker manual-only/Next y una solicitud única;
resultado y cobertura aún pendientes. No se encola ni llama al proveedor desde
este equipo, ni se pide más tráfico DVWA.

Resultado posterior: usuario confirma informe correcto; capturas muestran
4ca7c97703a4 (prefijo), manual/succeeded/finished, referencia 275469b7e38b e
informe 22:31:59 Madrid, dos grupos (alta1/media1), IP1 y 19 patrones en log.
La autorización única queda consumida. Sin receipt/usage/bytes o filas de
tipos/referencias recibidos todavía; cobertura BF de líneas39–46 por verificar.

Los ocho POST que pega de Actividad conservan 18:29:46–18:30:31 UTC,
equivalentes al intervalo local de la prueba; es el log reutilizado. API muestra
las últimas ocho líneas. Pipeline sincroniza antes del análisis y conserva
fechas de las solicitudes; el informe nuevo no genera tráfico. No se ha aportado
evidencia de nuevas peticiones DVWA ausentes ni se ha modificado ingesta.

La siguiente tabla aportada confirma XSS línea31, MEDIA/requiere investigación,
2026-10-15T16:20:17Z; Fuerza Bruta líneas39–46 completas, ALTA/requiere
investigación, 18:29:46–18:30:31 UTC, IP observada172.18.0.1 en ambos grupos.
Las ocho referencias y 45 s coinciden con la preparación offline; dos grupos y
una alta/una media coinciden con Resumen. Se valida esta muestra guiada de
captura/preparación/análisis/publicación/lectura en Parrot, sin acreditar acceso
exitoso ni semántica general A-05. No se recibieron bytes/hashes/receipt/usage
completos de la VM. Ensayo único consumido; solo actas locales y ninguna nueva
llamada/tráfico/job del agente.
