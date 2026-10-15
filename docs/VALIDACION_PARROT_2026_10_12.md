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
