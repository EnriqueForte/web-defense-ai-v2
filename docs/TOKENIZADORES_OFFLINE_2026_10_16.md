# Caché de tokenizadores empaquetados — 16/10/2026

Estado: corrección local; publicación y CI Windows/Ubuntu pendientes. La versión
publicada sigue siendo `88e7b8a`, con código verificado en CI `33d987b`.

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

Ocho pruebas específicas verifican copias, conservación del paquete, reutilización,
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
La validación remota Windows/Ubuntu y la publicación de este cambio siguen
pendientes; no se atribuye a la CI anterior la cobertura del nuevo código.

Para revertir el código, se retira la preparación añadida al adaptador junto con
el módulo y sus pruebas. La caché generada es prescindible y no contiene logs,
informes ni credenciales; no hace falta borrarla para revertir. Tras reiniciar
el proceso se recupera la selección previa del SDK y también su limitación
original de empaquetado Windows. No se modifica un proceso operativo en marcha.
