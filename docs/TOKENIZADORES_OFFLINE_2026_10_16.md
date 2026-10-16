# Caché de tokenizadores empaquetados — 16/10/2026

Estado: corrección publicada como `a6ac079`; primera CI Ubuntu aprobada y
Windows fallida por cuatro aserciones de rutas de prueba, en corrección local.
Los apartados de comprobaciones locales conservan la evidencia anterior a
la publicación. El resultado remoto se registra en el apartado final.

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
La validación remota Windows/Ubuntu y la publicación de este cambio siguen
pendientes; no se atribuye a la CI anterior la cobertura del nuevo código.

Para revertir el código, se retira la preparación añadida al adaptador junto con
el módulo y sus pruebas. La caché generada es prescindible y no contiene logs,
informes ni credenciales; no hace falta borrarla para revertir. Tras reiniciar
el proceso se recupera la selección previa del SDK y también su limitación
original de empaquetado Windows. No se modifica un proceso operativo en marcha.

## Publicación

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
