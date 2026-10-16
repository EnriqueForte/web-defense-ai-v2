# Groq HTTP 413 en la prueba de fuerza bruta — 15/10/2026

Seguimiento: corrección publicada como 33d987b, CI Windows/Ubuntu aprobada y
artefactos verificados. Actualización/arranque de lectura Parrot confirmados;
el ensayo autorizado posterior termina succeeded y su tabla confirma las ocho
referencias de fuerza bruta. Alcance y límites al final de este registro.
Los apartados iniciales conservan el estado previo a publicar.

## Evidencia y alcance

Tras comprobar observed-access-4 (ocho POST en 45 s, referencias 39–46
seleccionadas, umbral 5/60), el usuario solicitó el único trabajo manual previsto.
La captura muestra el prefijo `50f0fcc91e82`, manual, failed/finished/
analysis_failed. Última copia del log 20:37:31 Madrid; permanece el informe
de las 19:51:52, referencia abreviada 9dd17c72e247. No se recibieron ID completo,
recibo o bytes completos del log. La autorización queda consumida; no repetir.

Logs de Groq muestra varias filas 413 para 120b/20b entre 20:38 y 20:39 Madrid.
El detalle visible de 20b indica Request too large, type=tokens,
code=rate_limit_exceeded, TPM Limit 8000 y Requested 8103. Esos números no se
atribuyen a cada fila; los ceros de consumo no acreditan coste cero o un recibo
completo. El [413 de tamaño](https://console.groq.com/docs/errors) se distingue
del [429 temporal y Retry-After](https://console.groq.com/docs/rate-limits).
Los límites exactos dependen de la organización. Reenviar el mismo mensaje no
resuelve ese exceso. No se atribuye Requested 8103 al límite de salida 8192:
no se ha capturado ni tokenizado la petición real en el servidor.

## Corrección local

- Prompt structured-prototype-9: una fila con evidence_id/line_number/raw por
  evidencia seleccionada, en JSON compacto. Conserva cada línea cruda completa,
  orden, referencias, digest y metadatos de selección; evita repetir sus campos
  parseados. El EvidenceBundle y la publicación mantienen todos sus campos.
  Selección, guardas, umbral y límites de salida/timeout no cambian.
- Los estados HTTP explícitos de hasta ocho excepciones/causas prevalecen sobre
  nombres/texto al decidir reintentos. Se controlan ciclos y propiedades; un
  estado diferente de 429 no se trata como límite temporal.
- LiteLLM convierte el 413 simulado en RateLimitError/status 429 y conserva
  debajo OpenAIError/MaskedHTTPStatusError/HTTPStatusError con 413. CrewAI
  BaseLLM instala otra envoltura de tres intentos. Corregir solo el clasificador
  propio dejó tres peticiones en el primer pase de regresión.
- Se normaliza el 413 de la cadena a ProviderRequestTooLargeError, HTTP 413 y
  mensaje fijo. Se lanza fuera de except, sin contexto implícito: CrewAI recorre
  ese contexto incluso con from None. Así se detienen repetición y fallback por
  tamaño. El diagnóstico conserva tipo permitido y estado, sin mensaje/cuerpo/
  URL del proveedor. No se parchean SDK o estado global para conseguirlo.

La política existente ante 429 permanece. La compactación no garantiza admisión
de cualquier log ni saldo TPM disponible entre etapas/clientes. Una petición
todavía demasiado grande debe terminar; no se elimina evidencia en silencio.
No se cambia clave, modelo, plan, paquetes o .env.

## Verificación offline

339 casos Python: Windows 338 aprobados y uno Linux omitido; tres comprobaciones
JS. Cuatro casos nuevos comprueban prioridad HTTP/errores envueltos/ciclos, 413
SDK/CrewAI real y prompt/publicación compactos. El 413 simulado con el código
rate_limit_exceeded termina en una sola petición, sin fallback y con los archivos
del informe previo idénticos; se verifica diagnóstico HTTP 413.

Fixture sintética de 46 líneas/30 seleccionadas: tres respuestas HTTP escritas
a mano publican XSS y fuerza bruta con las ocho referencias 39–46. La entrada
retiene todas las líneas crudas seleccionadas y la evidencia publicada coincide
con la original. Estimación local cl100k_base de la primera petición: al menos
20 % menor que reinsertando el formato anterior y menos de 7000 tokens. No es
conteo de Groq, reproducción de bytes VM ni prueba semántica del proveedor.

27 escenarios SDK, 92 archivos de sintaxis y matriz A-05 de 13 casos/siete
controles aprobados; recibo 20261015T185242433279Z. Primer pase conservado:
tres HTTP por envoltura y comparación tuple/list de fixture; se corrigieron
normalización terminal y comparación JSON, sin relajar guardas o pruebas.

Recibos ignorados `.local-state/groq-413-20261015/`; pases iniciales en
`.local-state/dvwa-post-20261015/baseline-413*.log`. Sin proveedor real, trabajo
operativo nuevo, Docker, envío o servicios operativos Windows; sin lectura de
bytes .env ni nuevo inventario operativo Windows. Pendientes publicación/CI/VM;
código CI vigente 4c2e032. Cobertura real de fuerza bruta, A-05 y confirmación
de acceso exitoso siguen abiertos.

## Publicación y actualización prevista

Se publicó `33d987bf86e10b272adc79e57013bd504e958c0f` en origin/main V2.
Fetch previo sin divergencia; revisión de 248 candidatos/655 blobs alcanzables/
64 commits para exclusiones y formatos concretos de credenciales sin hallazgos,
sin auditoría global. Índice de diez archivos coincide con la revisión y hashes
vendor íntegros. Incluye las actas de aceptación del enlace y la preparación
offline facilitadas por el usuario después de la publicación anterior.

La [CI 38790268742](https://github.com/EnriqueForte/web-defense-ai-v2/actions/runs/38790268742)
se inició para ese código; el resultado final se consigna tras revisar estados,
pasos, logs y artefactos. No se atribuye un resultado real de Groq a la CI.

Después de recibir la confirmación de CI, detener las tres terminales de la VM
con Ctrl+C, esperar el prompt y actualizar como usuario normal:

```bash
cd "$HOME/Proyectos/web-defense-ai-v2"
git pull --ff-only
git rev-parse --short HEAD
.p2/bin/python -B -c 'from agents.structured_prototype import PROMPT_VERSION; print(PROMPT_VERSION)'
```

La versión debe ser structured-prototype-9. No hay cambios de dependencias o
frontend que requieran reinstalación o build por esta corrección. Para revisar
el informe existente con la consola de lectura:

```bash
source "$HOME/.nvm/nvm.sh"
nvm use 24
python3 webdefense.py start --mode structured
```

El log capturado con la ráfaga puede reutilizarse como evidencia; no se necesita
generar más intentos. Otro análisis real requiere un nuevo alcance expresamente
autorizado: la solicitud del trabajo 50f0fcc91e82 ya terminó. No se inicia un
trabajo ni se reenvía la petición al actualizar o abrir la consola de lectura.

## Cierre de publicación/CI

Código `33d987bf86e10b272adc79e57013bd504e958c0f`, run 38790268742/attempt 1,
Windows-latest/Ubuntu 24.04 completed/success. Estados/pasos/logs finales
revisados y cuatro pruebas nuevas identificadas en cada sistema. Instalación
nueva, pip check/contrato 172/0/build normal; Ubuntu 339 Python, Windows 338
aprobados y uno Linux omitido; 3 JS/92 sintaxis/HTTP/27 SDK/13 A-05+7 controles/
lint/tipos/17 UI aprobados. Nueve E2E de Configuración por OS (Windows 47,2 s,
Ubuntu 7,6 s), salida 0/cierre libre y smoke API directa/proxy 200, ejecutor
offline/cierre con puertos libres en ambos. No es una llamada real a Groq.

Inventarios completos descargados y verificados: 11999428216 Windows
Python 3.11.9 y 11999582390 Ubuntu Python 3.11.17, 172 paquetes/0 deriva/
0 extras. Paquetes contra contrato, metadatos y hash de freeze verificados;
hashes idénticos a los anteriores:

- Windows: `4444efe4144b1000fc66679788ca32dbd9d4685da2fd1161f7eb726fbd93553d`.
- Ubuntu: `2a89e0601de6126ec0449a723bcb0cf67f9b00af092e9abc60264439aa9127fa`.

Resúmenes A-05 12000212656 Windows/11999932578 Ubuntu: métricas/checks/hashes
de publicaciones coinciden con la matriz local 20261015T185242433279Z salvo
UUID de generación. No incluyen bytes de informes remotos ni prueban semántica
del proveedor. Recibos en .local-state/groq-413-20261015, ignorados.

El siguiente commit solo actualiza actas [skip ci]; el código probado sigue
siendo 33d987b. El informe real anterior no se ha recalculado ni se ha repetido
el ensayo. Sin llamadas LLM/Docker/envíos/servicios operativos Windows nuevos,
lectura de bytes .env o nuevo inventario operativo. Pendiente actualización
Parrot y nuevo alcance expresamente autorizado para otro trabajo real.

## Recepción comprobada en Parrot

La nueva captura del usuario muestra fast-forward 5c567d1..88e7b8a y HEAD
88e7b8a. El import de PROMPT_VERSION devuelve structured-prototype-9; nvm
activa Node 24.21.0 y `python3 webdefense.py start --mode structured` informa
Consola lista en 127.0.0.1:3000. Quedan acreditados recepción y arranque de
lectura; no hay nuevo análisis, inventario de paquetes o hashes completos de VM.
La corrección sigue pendiente de validación real con Groq.

Se propone un nuevo trabajo manual único sobre la copia existente de 46 líneas
con ocho POST, Groq 120b/alternativa 20b ante 429 y reintentos internos existentes,
timeout del motor 900 s, sin ciclos/notificaciones/repetición automática. Es
una autorización independiente del trabajo fallido 50f0fcc91e82 y todavía está
pendiente; aportar la captura de actualización no autoriza otra llamada.

El usuario autoriza después expresamente «sí» al alcance anterior: un único
análisis manual nuevo de la captura existente, 46 líneas/ocho POST, Groq
120b/alternativa 20b ante 429, reintentos internos existentes y timeout del
motor 900 s, sin ciclos/notificaciones/repetición automática. Es independiente
del trabajo fallido 50f0fcc91e82. No se generan nuevas peticiones DVWA.

Se guía la parada de la consola unificada de lectura y el arranque de Flask
manual primero, worker manual-only en la terminal con captura Docker correcta
y Next/Node24 aparte. Cuando la interfaz muestre ejecutor online y solicitudes
manuales habilitadas, el usuario solicitará una sola vez. El agente no dispone
de acceso directo a Parrot ni ha encolado un trabajo. Pendientes activación,
solicitud, resultado, diagnóstico y revisión de cobertura/referencias.

## Resultado recibido del ensayo autorizado

El usuario confirma que el informe se elaboró correctamente. Las capturas
muestran job prefijo 4ca7c97703a4, manual/succeeded/finished, publicación
15/10/2026 22:31:59 Europe/Madrid y referencia abreviada 275469b7e38b. Resumen:
dos grupos, una alta/una media, una IP y 19 coincidencias del log. Esto acredita
ejecución/publicación visible posterior a la corrección en esta VM; no es una
garantía general de admisión TPM o calidad del proveedor. No se recibieron ID
completo, recibo, consumos, bytes/hashes del informe o filas de tipos/referencias.

El usuario observa que Actividad conserva los ocho POST de 18:29:46–18:30:31
UTC. Son las solicitudes de la captura que se acordó reutilizar; 18:30:31 UTC
es 20:30:31 Madrid, coherente con la última petición visible en la consola.
La fecha del informe 22:31:59 es otra magnitud. El código de pipeline primero
sincroniza el origen y luego analiza; la captura copia los registros conservando
su texto y el dashboard muestra las últimas ocho líneas de la copia. Leer o
analizar no genera tráfico DVWA ni reemplaza las fechas de esos eventos.

No hay evidencia aportada de peticiones posteriores que se hayan perdido ni
se ha cambiado código de ingesta por esta observación. Queda pedir la fila de
Fuerza Bruta y sus referencias para comprobar cobertura de las líneas 39–46;
las dos tarjetas por sí solas no acreditan tipos ni todas las referencias.
La autorización de este trabajo está consumida; no se repite ni se generan
peticiones desde este equipo. Sin nuevos servicios operativos Windows, LLM,
Docker o envíos del agente. A-05/general y éxito de autenticación siguen abiertos.

### Referencias del informe comprobadas

La siguiente captura de la tabla AMENAZAS DETECTADAS confirma:

| Patrón | Referencias | Fecha UTC | Severidad/estado |
| --- | --- | --- | --- |
| XSS | 31 | 2026-10-15T16:20:17Z | MEDIA / Requiere investigación |
| Fuerza Bruta | 39,40,41,42,43,44,45,46 | 2026-10-15T18:29:46Z a 2026-10-15T18:30:31Z | ALTA / Requiere investigación |

Ambos grupos muestran IP observada 172.18.0.1. La ráfaga representa las ocho
referencias seleccionadas offline, con el mismo intervalo de 45 s, y conserva
el XSS de la línea 31. Los dos grupos/una alta/una media concuerdan con las
tarjetas anteriores. Queda validada la cobertura de esta muestra y su recorrido
guiado captura/preparación/análisis/publicación/lectura en Parrot.

La tabla marca investigación: no prueba acceso exitoso, credenciales halladas
o explotación XSS. No se han recibido ni revisado bytes/hashes completos de la
publicación, recibo de consumo, modelo efectivo o reintentos de este trabajo.
Esta aceptación no cierra calidad semántica general A-05 ni los otros bloques
del proyecto. No se repite el ensayo ni se solicita tráfico adicional. Solo se
actualizan actas locales; no se inicia otra llamada, job o servicio del agente.
