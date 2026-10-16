# Caché de tokenizadores empaquetados — 16/10/2026

Estado: corrección y ajuste de pruebas publicados como `976af10`, con CI
Windows/Ubuntu aprobada y logs/artefactos verificados. La primera ejecución
fallida y las comprobaciones locales se conservan como evidencia histórica.

## Problema y revisión

El fallo de Windows en frío registrado en
[la incidencia Groq](INCIDENCIA_GROQ_PARROT_2026_10_15.md) precedía a la petición
HTTP: el recurso cl100k del wheel usaba CRLF y tiktoken esperaba el hash de sus
bytes LF. La fixture temporal de las pruebas anteriores resolvía únicamente
su entorno de prueba.

Se descargó desde PyPI, sin instalar, el wheel fijado
`litellm-1.105.0-cp310-abi3-win_amd64.whl`. SHA-256:
`6ff237f1fe64a086d91b1453116347e0c1b2aed0fe8c8b9014d5a019c6a6b5d6`.
Su recurso cl100k tiene 1.781.382 bytes, 100.256 CRLF y coincide con su RECORD.
La conversión a LF produce los 1.681.126 bytes y el hash esperado por tiktoken.
También se verificaron RECORD y hash canónico de p50k (886.466 bytes CRLF,
836.186 LF) y o200k (3.813.920 bytes CRLF, 3.613.922 LF). El wheel original se
conserva en los recibos locales ignorados.

La primera propuesta local seleccionaba una caché que contenía solo cl100k.
La revisión reprodujo una regresión: o200k funcionaba con los recursos completos
y, tras seleccionar esa caché parcial, intentaba descargarse. Esa propuesta no
se publicó. La corrección conserva los tres recursos BPE del paquete fijado.

## Comportamiento implementado

`RateLimitResilientLLM.call` prepara la caché antes de invocar la ruta LiteLLM.
`config/tokenizer_cache.py` valida hashes exactos y prepara copias LF en
`.local-state/tokenizers/bundled-bpe-v1/`. No descarga recursos ni modifica los
archivos instalados. Los hashes son los esperados por las funciones de tiktoken:

| Recurso | Clave de caché | SHA-256 canónico |
| --- | --- | --- |
| cl100k_base | `9b5ad71b2ce5302211f9c61530b329a4922fc6a4` | `223921b76ee99bde995b7ff738513eef100fb51d18c93597a113bcffe865b2a7` |
| p50k_base | `ec7223a39ce59f226a68acc30dc1af2788490e15` | `94b5ca7dff4d00767bc256fdd1b27e5b17361d7b8a5f968547f9f23eb70d2069` |
| o200k_base | `fb374d419588a4632f3f557e76b4b70aebbca790` | `446a9538cb6c348e3516120d7c08b09f57c36495e2acfffe59a5bf8b0cfb1a2d` |

`p50k_edit` y `o200k_harmony` reutilizan esos archivos. El JSON de Anthropic se
lee por otra ruta del paquete, ajena a esta caché BPE. Esto no añade soporte
offline para recursos que el paquete fijado no incluye, como r50k o GPT-2.

Los recursos que falten o requieran reparación se validan todos antes de crear
estado. Cada archivo se publica mediante reemplazo atómico; una publicación
concurrente solo se acepta si sus bytes tienen el hash previsto. La ruta propia
rechaza enlaces y puntos de reanálisis. Se seleccionan ambas variables de caché
solo después de preparar el conjunto.

Si existe `CUSTOM_TIKTOKEN_CACHE_DIR` explícita, se conserva y se exige que
contenga los tres recursos canónicos. Una caché externa parcial o inválida se
rechaza antes de la llamada; no se rellena ni se repara. Un error de recurso o
permisos produce `TokenizerResourceError`, sin recurrir a descargas.

## Comprobaciones y límites

Las ocho pruebas específicas iniciales verifican copias, conservación del paquete, reutilización,
rechazo de recurso dañado, caché externa completa/incompleta, rechazo de enlaces,
fallo de reemplazo y publicación concurrente simulada.

La prueba en frío crea procesos nuevos con los bytes instalados originales,
LF, CRLF y recurso inválido. Usa
CrewAI/LiteLLM y tokenizadores reales, con backend Python forzado, dotenv
desactivado, sockets bloqueados y respuesta HTTP sintética. Comprueba la ruta
de conteo GPT-4o/o200k y codificación/decodificación de los cinco nombres de
tokenizador anteriores. El caso inválido exige cero peticiones al proveedor
simulado y ninguna caché seleccionada. La ubicación del recurso empaquetado se
sustituye por una copia temporal; esta prueba no equivale a instalar un wheel
nuevo completo ni certifica todos los backends nativos o modelos.

Las pruebas HTTP Groq existentes ahora preparan una fixture con los tres recursos
verificados. No se cambian sus respuestas ni las aserciones de HTTP 400, 413,
429, publicación o conservación de evidencias.

Resultados locales: 347 casos Python (346 aprobados y uno exclusivo Linux
omitido), tres comprobaciones JavaScript y 27 escenarios SDK aprobados.
La variante adicional con bytes instalados originales pasó en la ejecución
final de las ocho pruebas específicas (20,659 s). Sintaxis: 94 archivos/cero
errores; contrato: 172 paquetes/cero diferencias/cero adicionales.
`git diff --check` no encontró errores de whitespace. Las restricciones del
sandbox sobre subprocesos/reemplazos temporales requirieron ejecución fuera
del sandbox con aprobación, manteniendo el bloqueo de red en las pruebas.

Recibos ignorados: `.local-state/tokenizer-20261015/`. Conservan el wheel, sus
hashes, la reproducción de la regresión y los resultados de pruebas. No hubo
llamadas reales al proveedor, trabajos operativos, Docker o envíos, ni lectura
de bytes `.env`. La muestra Parrot anterior permanece aceptada con sus límites.

## Compatibilidad y reversión

No cambia el contrato de dependencias, los prompts ni el frontend. La aplicación
requiere permiso de escritura en su `.local-state` cuando deba preparar la caché.
La validación remota de este cambio se documenta al final; no se atribuye a la
CI anterior la cobertura del nuevo código.

Para revertir el código, se retira la preparación añadida al adaptador junto con
el módulo y sus pruebas. La caché generada es prescindible y no contiene logs,
informes ni credenciales; no hace falta borrarla para revertir. Tras reiniciar
el proceso se recupera la selección previa del SDK y también su limitación
original de empaquetado Windows. No se modifica un proceso operativo en marcha.

## Primera publicación y ajuste de pruebas

Publicado `a6ac079d407e911d6c98ebbf1e0bf41387e30adf` en origin/main de V2.
El remoto original mantiene el push bloqueado. Fetch previo confirmó ausencia
de divergencia; el índice coincidió con los 251 archivos revisados y los nueve
cambios esperados, incluidos los registros de aceptación Parrot aún locales.

La revisión acotada de 251 candidatos, 669 blobs/66 commits alcanzables no
encontró rutas privadas ni los formatos específicos de credenciales comprobados;
los hashes vendor coinciden. No sustituye la auditoría de seguridad pendiente.

[CI 38884794976/attempt1](https://github.com/EnriqueForte/web-defense-ai-v2/actions/runs/38884794976)
terminó Ubuntu success y Windows failure. Logs finales descargados: Windows
instaló y compiló, pero cuatro comprobaciones nuevas fallaron. Tres variantes
de tokenización llegaron hasta la aserción final de pertenencia a la carpeta
temporal y fallaron allí; el caso de recurso inválido pasó. La simulación de
enlace no reconoció la ruta esperada. No se presenta esta ejecución como aprobada.

El producto resuelve su raíz y las pruebas comparaban esa ruta con la forma
temporal sin resolver. Se corrige la raíz de las fixtures mediante `resolve()`
antes de las comparaciones y del doble de enlace. Una prueba adicional reproduce
una raíz equivalente escrita con `..` en ambos sistemas: confirma la ubicación
canónica y el rechazo del enlace simulado. El código productivo no cambia.
La aprobación remota del ajuste de pruebas sigue pendiente.

Regresión local después del ajuste: 348 casos Python (347 aprobados/uno Linux
omitido), tres JS y 94 archivos sin errores de sintaxis. La nueva prueba de
alias mantiene las comprobaciones de pertenencia canónica y rechazo de enlace;
no se omiten ni se relajan para conseguir una aprobación. No hubo llamadas reales.

## Publicación final y CI verificada

El ajuste de fixtures se publicó como
`976af10d469f10e1545ec77f30bb8e9f6584ca54`. El código productivo coincide con
`a6ac079`; solo cambiaron las pruebas de rutas y el registro documental.
Revisión acotada antes de este segundo push: 251 candidatos, 678 blobs/67
commits, sin hallazgos en las exclusiones/formatos comprobados; vendor íntegro.
El índice de 251 archivos coincidía con los tres cambios revisados.

[CI 38886025823/attempt1](https://github.com/EnriqueForte/web-defense-ai-v2/actions/runs/38886025823)
terminó completed/success en Windows y Ubuntu. Se descargaron y revisaron los
logs finales, los estados y los pasos requeridos:

- Instalación nueva, pip check, build de producción y contrato estricto.
- Ubuntu: 348 Python aprobados, 28,894 s. Windows: 347 aprobados/uno exclusivo
  Linux omitido, 348 casos en 53,666 s. Las nueve pruebas de este cambio aparecen
  ejecutadas, incluida la raíz equivalente y las cuatro variantes en procesos
  fríos con el tokenizador Python real y sockets bloqueados.
- Tres JS, 94 archivos sin errores de sintaxis, HTTP sintético, 27 escenarios
  SDK, lint/tipos y 17 grupos UI por OS.
- Matriz A-05 de 13 casos/siete controles sin proveedor; nueve E2E por OS
  (Windows 11,4 s, Ubuntu 7,3 s), API directa/proxy 200, ejecutor offline y
  cierre con puertos libres.

Inventarios completos descargados y verificados contra contrato/metadatos:
Windows artefacto 12039209776, Python 3.11.9/pywin32 311; Ubuntu artefacto
12039418942, Python 3.11.17/uvloop 0.23.0. Ambos 172 paquetes, cero diferencias
y cero adicionales. Freeze SHA-256 previos conservados:

- Windows: `4444efe4144b1000fc66679788ca32dbd9d4685da2fd1161f7eb726fbd93553d`.
- Ubuntu: `2a89e0601de6126ec0449a723bcb0cf67f9b00af092e9abc60264439aa9127fa`.

Resúmenes A-05: Windows 12038694855 y Ubuntu 12039184065. Checks, métricas y
hashes de publicaciones coinciden con el recibo local
`20261015T185242433279Z`, excluyendo solo el UUID de generación. Estos resúmenes
no incluyen los bytes completos de los informes remotos.

Queda cerrado este pendiente de carga BPE de la aplicación para la distribución
fijada y la ruta Python comprobada en Windows/Ubuntu. El wheel del proveedor
se conserva intacto; la aplicación utiliza sus copias verificadas. No se amplía
a backends nativos/modelos no probados ni a calidad semántica general A-05.
No se repitió el ensayo Parrot, ni se iniciaron llamadas reales, Docker, envíos
o servicios operativos. La VM sigue acreditada en su revisión anterior.

Los recibos de ambas CI, los inventarios y resúmenes quedan en
`.local-state/tokenizer-20261015/`, excluidos de Git. La actualización siguiente
contiene solo actas `[skip ci]`; el código de CI sigue siendo `976af10`.
