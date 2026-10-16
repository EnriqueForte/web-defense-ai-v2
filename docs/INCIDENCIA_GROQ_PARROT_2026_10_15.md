# Incidencia Groq en el primer análisis Parrot — 15/10/2026

## Evidencia recibida

El usuario opera la VM; no hay acceso directo desde el agente. El recorrido y
las capturas anteriores se conservan en
[validación Parrot](VALIDACION_PARROT_2026_10_12.md). HEAD de la actualización
visible: `292e812`; sin nuevo inventario/hash completo de la VM recibido.

Un único trabajo manual fue autorizado con Groq, principal
`groq/openai/gpt-oss-120b`, reintentos internos y posible alternativa 20b ante
rate limit; sin repetición del trabajo fallido, ciclos o notificaciones.

El fragmento del recibo aportado por el usuario identifica:

- `analysis_id`: `f217a6210aa3447084193573b5449a97`.
- Estado failed; terminado `2026-10-15T16:44:50.114079+00:00` (18:44 Madrid).
- Duración del motor 5,511 s; generation null.
- Una llamada lógica y un intento de transporte observado, en detection.
- Intento fallido en 0,609 s, cadena `other_exception` tres veces y
  `HTTPStatusError`. No hay resultado de detección ni rechazo de guardas
  acreditado en los fragmentos.
- Usage completo false, cero completions observadas, tokens null. SDK informa
  ceros; esto no acredita consumo ni coste cero.

La UI muestra `analysis_failed`; por el flujo del coordinador, la ingesta pasó
y el motor no terminó con éxito. No hay informe disponible. El HTTPStatusError
procede de la llamada observada a litellm, no del anterior 500 Next/Flask que se
resolvió al arrancar correctamente la API. El recibo antiguo no guarda el número
HTTP: no permite atribuir la causa a parámetros, clave, cuota o disponibilidad.
No se dispone del cuerpo original ni se puede reconstruir desde este JSON.

### Evidencia posterior del gráfico Groq

El usuario aportó una captura del gráfico de métricas: a las 6:44pm muestra
`HTTP 400`, conteo 1. Es compatible con el minuto del trabajo; la imagen no
incluye ID de petición, proyecto, fecha, zona horaria ni mensaje para una
correlación independiente completa. Acota la investigación a una respuesta 400
visible en la cuenta; por sí sola no identifica parámetros, formato del modelo
o cualquier otra causa concreta. Se solicita el detalle de la petición en Logs
(error.message/type/code), sin claves, prompts, respuestas o failed_generation.
No se solicita ni se ejecuta un nuevo análisis.

## Corrección local del diagnóstico

`agents/analysis_diagnostics.py` conserva ahora un `http_status` opcional:
primer entero válido 300–599 encontrado en la cadena de hasta ocho excepciones,
desde status_code o response.status_code. Las propiedades que fallen no
reemplazan el error original. Se amplía la lista cerrada de tipos SDK conocidos
(BadRequestError, NotFoundError, PermissionDeniedError y otros); las clases
desconocidas siguen siendo other_exception.

No se leen ni serializan mensajes de excepción, cuerpos HTTP, URLs, cabeceras,
claves, prompts o respuestas para obtener ese dato. Se conserva en eventos de
fallo, intentos, checkpoints y recibo mediante las rutas existentes. No altera
proveedores, modelos, prompts, payloads, límites, guardas, pines ni reintentos.
La mejora no recupera el número omitido del ensayo anterior ni corrige por sí
misma su causa HTTP. No está publicada ni instalada en la VM en este registro.

Cuatro pruebas nuevas verifican SDK real con error HTTP sintético encadenado,
estados inválidos y propiedades adversas, persistencia segura en recibo y
checkpoint, restauración del hook y propagación de la excepción original.
22 pruebas focalizadas pasaron; regresión completa 326 casos (325 aprobados y
uno exclusivo Linux omitido), tres comprobaciones JS y 91 archivos sin errores
de sintaxis; diff check correcto. Recibo local ignorado:
`.local-state/parrot-http-20261015/baseline.log`.

La primera prueba focalizada en sandbox falló en reemplazos temporales y el
import de LiteLLM intentó obtener su mapa público de costes de GitHub, con DNS
fallido. La repetición autorizada fuera del sandbox usó explícitamente el mapa
local y pasó, igual que la regresión completa. No hubo nuevas llamadas a Groq,
ensayos de proveedor, trabajos operativos ni servicios Windows iniciados.
No se realizó comparación nueva del inventario operativo Windows.

## Comprobación histórica propuesta

Consultar el registro ya existente en Dashboard → Logs del proyecto Groq
correspondiente a la clave de la VM, alrededor de 18:44–18:45 Madrid del 15/10
(16:44–16:45 UTC), si aparece. Solicitar únicamente el código HTTP y el error
breve, sin credenciales ni contenido del prompt/respuesta. Es una lectura,
no un nuevo ensayo. Si no hay registro accesible, no inferir una causa; publicar
la mejora y cualquier nueva ejecución real requieren continuar con alcance
explícito. El permiso del trabajo anterior está consumido.

Fuentes primarias consultadas: [errores Groq](https://console.groq.com/docs/errors)
y [proyectos y registros](https://console.groq.com/docs/projects). Ninguna tabla
de errores acredita cuál recibió esta ejecución concreta. A-05 y el recorrido
de análisis/publicación Parrot permanecen abiertos.

## Causa identificada en Logs y corrección local del transporte

La captura posterior de Logs muestra una entrada del 15/10/2026 a las 18:44:49,
HTTP 400, tipo invalid_request_error. El mensaje identifica `messages.0` de
rol system y rechaza la propiedad `cache_breakpoint` como no soportada. Es
coherente con el intento HTTP observado en el recibo; no es el anterior error
500 de conexión local ni una salida rechazada por nuestras guardas.

La inspección de CrewAI 1.15.27 confirma el origen: CrewAgentExecutor añade esa
marca interna al prefijo estable del sistema/usuario. BaseLLM._format_messages
la retira, pero la ruta LLM LiteLLM usa _format_messages_for_provider y no hace
esa limpieza. El adaptador RateLimitResilientLLM hereda esta última ruta.

Corrección en `main.py`: se sobreescribe _format_messages_for_provider para
modelos con prefijo groq/. Crea copias de los diccionarios de mensaje retirando
únicamente el campo de primer nivel cache_breakpoint; después invoca el
formateador original. No elimina ese texto si aparece dentro del contenido,
no muta los mensajes del ejecutor, no toca dependencias instaladas y conserva
los demás campos. Para otros proveedores se conserva el camino original.
No cambia modelos, claves, formato JSON, prompts, guardas, pines o política de
reintentos; mantiene los límites existentes 8192 tokens/60 s por petición.

Cuatro pruebas nuevas usan CrewAI/LiteLLM reales, interceptan httpx.Client.send
y bloquean sockets externos. El SDK sin adaptar envía la marca y recibe 400
sintético; el adaptador corregido envía el mismo contenido sin la marca y recibe
200 sintético. Se verifica también el recorrido completo CrewAI con marcas
generadas por el framework y publicación temporal sin hallazgos, cuerpo HTTP
OpenRouter idéntico al anterior, alternativa Groq 120b→20b ante 429 y un único
intento ante 400 con mensajes originales conservados. Son respuestas simuladas:
no acreditan aceptación del proveedor real ni semántica del modelo.

Las cuatro pruebas HTTP pasaron. Regresión completa posterior: 330 Python
(329 aprobados y uno Linux omitido), tres comprobaciones JS, 92 archivos sin
errores de sintaxis y 27 escenarios SDK anteriores aprobados. Se revisó diff.
Recibos ignorados en `.local-state/parrot-http-20261015/`: groq-transport.log,
baseline-cache-fix.log y sdk-cache-fix.log.

La primera prueba HTTP en sandbox quedó esperando y fue detenida comprobando
argumentos, ejecutables y fechas de los dos procesos propios (PID históricos
19056/31500); no se operaron servicios ajenos. La ejecución autorizada fuera
del sandbox permitió verificar el transporte; se completó la respuesta ficticia
con service_tier requerido por el SDK antes de obtener las cuatro aprobaciones.
No hubo llamadas reales a Groq ni repetición del trabajo Parrot.

Estado al cerrar esta revisión local: causa identificada y corrección/pruebas
preparadas, sin commit/push/CI nuevos ni instalación en Parrot. Próximo paso:
publicar el cambio verificado, actualizar la VM con sus servicios detenidos y
preparar un nuevo ensayo único con autorización concreta. El ensayo anterior
no se reutiliza. A-05 y el cierre del informe real Parrot permanecen pendientes.

## Publicación autorizada y primera CI

El usuario autorizó commit/push. Se verificó origin/main V2 sin divergencia;
original-readonly conserva push bloqueado. Revisión acotada: 246 candidatos,
628 blobs/59 commits, exclusiones privadas y formatos específicos de credenciales
sin hallazgos, vendor íntegro. No es una auditoría exhaustiva. Índice revisado:
246 archivos, nueve cambios y fuentes coincidentes.

Se publicó `eefa51ce465003b523b8ca7ef5c8640c1b4489e8`.
[CI 38775156492/attempt1](https://github.com/EnriqueForte/web-defense-ai-v2/actions/runs/38775156492)
terminó Ubuntu success y Windows failure. Logs finales revisados: Ubuntu pasó
330 Python, 3 JS, 92 sintaxis/HTTP/27 SDK/13 A05+7 controles/lint/tipos/17 UI,
9 E2E y smoke/cierre; Windows pasó instalación 172/0 diferencias y build,
pero falló cuatro pruebas HTTP nuevas en Offline Python and browser contracts.
No se atribuye éxito completo a esta ejecución.

El trace Windows muestra carga diferida de cl100k_base por LiteLLM, caída al
tokenizador Python y descarga intentada por tiktoken bloqueada por los sockets
de prueba. No hubo llamada al proveedor. El bloqueo de red no se relajó.
El RECORD del wheel Windows instalado registra el recurso
9b5ad71b2ce5302211f9c61530b329a4922fc6a4 con 1781382 bytes y hash base64
WdLa9mCers5efIHcqPJ1ImpU7kZEkTupmVzGCT6jqLc. El recurso local leído tiene
1681126 bytes LF y SHA256 223921b76ee99bde995b7ff738513eef100fb51d18c93597a113bcffe865b2a7;
reconstruir sus finales CRLF reproduce exactamente el tamaño/hash de RECORD.
Esto identifica la incompatibilidad de representación con el hash LF de
tiktoken; no se afirma descarga/verificación nueva del wheel completo ni que
su recurso original intacto funcione offline en una instalación Windows fría.
Las pruebas SDK anteriores interceptaban litellm.completion antes de esta ruta
HTTP diferida; sus aprobaciones históricas no acreditaban este tramo.

Ajuste limitado a pruebas: se toma el recurso empaquetado, normalizan CRLF a LF
en memoria y se exige el SHA256 exacto anterior antes de copiarlo a una caché
temporal privada. CUSTOM_TIKTOKEN_CACHE_DIR y TIKTOKEN_CACHE_DIR se fijan solo
durante cada prueba; se fuerza el tokenizador Python real con LITELLM_RUST=false
para verificar esa ruta en ambos sistemas. No se modifica el paquete, su asset
original ni una caché global; no se usa un doble de tokenizador ni se autoriza
descarga. Un caso nuevo verifica LF/CRLF válidos y rechazo de un asset truncado.
La limitación del recurso Windows original queda documentada por separado y
no se presenta esta fixture como corrección del empaquetado del proveedor.

Regresión local: 331 Python (330 aprobados y uno Linux omitido)/3 JS aprobados;
cinco pruebas HTTP/fixture en proceso nuevo con backend Python forzado aprobadas.
El código productivo Groq/diagnóstico sigue siendo el publicado en eefa51c;
el nuevo ajuste de pruebas y su CI están pendientes de publicación/verificación
en el momento de este apartado. No se repitió el ensayo Parrot.

## Publicación final y CI verificada

El ajuste de pruebas se publicó como
`646aaf20646854e4665f55f285cedfe2a06d45f5`, sin cambios productivos respecto a
eefa51c. Revisión acotada previa: 246 candidatos, 637 blobs/60 commits, sin
hallazgos en exclusiones privadas/formatos de credenciales; vendor íntegro.
El índice coincidía con los 246 archivos revisados y tres cambios esperados.

[CI 38776623228/attempt1](https://github.com/EnriqueForte/web-defense-ai-v2/actions/runs/38776623228)
terminó completed/success en Windows y Ubuntu. Se descargaron los logs finales
y se verificaron los estados y pasos requeridos, no solo el estado agregado:

- Instalación nueva, pip check, build Next y contrato estricto 172/0 diferencias.
- Ubuntu 331 Python aprobados; Windows 330 aprobados y uno exclusivo Linux omitido.
- Los nueve casos nuevos aparecen ejecutados: cuatro diagnósticos y cinco de
  transporte HTTP/fixture. El bloqueo de red permaneció activo.
- Tres comprobaciones JS, 92 archivos sin errores de sintaxis, HTTP sintético,
  27 escenarios SDK anteriores, lint/tipos y 17 grupos UI aprobados por OS.
- Matriz A-05 de 13 casos/siete controles sin proveedor, nueve E2E por OS
  (Ubuntu 10,4 s, Windows 40,9 s) y smoke API/proxy 200, ejecutor offline,
  cierre con puertos libres. La instalación del navegador Windows tardó más;
  esta CI no fue cancelada ni reejecutada.

Inventarios descargados y verificados contra contrato y metadatos:
Windows artefacto 11993708267, Python 3.11.9; Ubuntu 11993014560, Python 3.11.17.
Ambos 172 paquetes/cero diferencias/cero extras. Freeze SHA256 anteriores
conservados: Windows 4444efe4144b1000fc66679788ca32dbd9d4685da2fd1161f7eb726fbd93553d,
Ubuntu 2a89e0601de6126ec0449a723bcb0cf67f9b00af092e9abc60264439aa9127fa.

Resúmenes A-05 descargados: Windows 11993783351 y Ubuntu 11994531078. Métricas,
checks y hashes de publicaciones coinciden con el recibo local offline del
13/10, excluyendo únicamente el UUID de generación. Los bytes de los informes
remotos no están incluidos en esos resúmenes. Recibos/logs/artefactos se guardan
en `.local-state/parrot-http-20261015/`, excluidos de Git.

La corrección de cache_breakpoint y el diagnóstico HTTP quedan publicados y
verificados en ese alcance offline. La fixture privada no certifica el recurso
Windows original intacto en frío: ese punto del empaquetado permanece pendiente.
No se hicieron llamadas reales al proveedor, trabajos operativos, envíos o
arranques de servicios Windows. No se releyó el inventario operativo Windows.
La VM todavía debe detener sus tres componentes, hacer pull y verificar el SHA;
sin cambios de dependencias/frontend en esta corrección, no se pide reinstalar
ni recompilar. Un nuevo análisis en Parrot requiere un nuevo alcance explícito.
El siguiente commit contiene solo actas [skip ci]; código de CI: 646aaf2.

## Seguimiento de distribución — 16/10/2026

El pendiente de carga BPE de la aplicación Windows en frío se corrigió después
mediante una caché propia con los tres recursos empaquetados verificados por
SHA-256. Código `976af10`/CI38886025823 Windows/Ubuntu success, logs e inventarios
revisados. El wheel original permanece intacto; los límites y la primera CI
fallida por rutas de fixtures se documentan en
[Tokenizadores offline](TOKENIZADORES_OFFLINE_2026_10_16.md).
La referencia anterior a pendiente de distribución conserva el estado del 15/10.
