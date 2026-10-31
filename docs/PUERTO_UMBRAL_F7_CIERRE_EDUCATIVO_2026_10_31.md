# Puerto Umbral F7 — matriz de cierre educativo

Fecha: 31/10/2026, Europe/Madrid. Estado: **ronda manual representativa
terminada; matriz revisada documentalmente y propuesta de aceptación de este
alcance educativo preparada; aceptación global F6/F7/proyecto pendiente**.

## Alcance y fuentes

Se revisan los criterios F7-AC1/2/3 del
[PRD](PRD_PUERTO_UMBRAL_2026_10_26.md), el
[catálogo de ampliaciones](../labs/puerto_umbral/lab/advanced_catalog.py), las
[revisiones de artefactos](../labs/puerto_umbral/lab/advanced_target.py) y las
capturas aportadas por el propietario, registradas en el
[acta F6/F7](PUERTO_UMBRAL_F6_F7_2026_10_29.md). No se ejecutan nuevos casos,
suites o llamadas al modelo para elaborar esta matriz.

Las once ejecuciones observadas son del modo corregido, variante 1. Son
revisiones de artefactos ficticios servidos por HTTP local. Cada una muestra
3 peticiones del ejecutor, 3 líneas Apache correlacionadas, 2 eventos de
aplicación y 2 referencias HTTP; la lectura posterior en V2 presenta el mismo
identificador y conteo, con mensaje de copia conservada sin análisis. Es
evidencia de pantalla del propietario, sin acceso independiente del agente a
los bytes de la VM. Después se observa la lectura del recibo local de la última
copia de Excepciones, registrada en la
[auditoría de cierre](PUERTO_UMBRAL_AUDITORIA_CIERRE_2026_10_31.md). Confirma
metadatos y una captura posterior de `sha256sum` acredita que los bytes del
`events.json` de esa copia coinciden con su recibo. No se extrapola a los otros
snapshots. Después se observa respaldo actualizado del perfil con verificación
interna, 113 archivos, `verified: true`, `missing: []`; la restauración
independiente adicional sigue aplazada. Esto no reabre los once recorridos.

## Recorridos observados y límites

| Ejercicio | Control normal observado | Condición adversa corregida observada | Límite educativo |
| --- | --- | --- | --- |
| Configuración | 200, depuración desactivada y configuración mínima | 200, conserva configuración mínima sin `debug_trace` | No audita Apache o configuración real del despliegue |
| Suministro | 200, hashes iguales y `accepted: true` | 422, hashes distintos y `accepted: false` | Referencia local fija; no prueba procedencia de paquetes o firma de proveedor |
| Criptografía | 200, `scrypt`, sal y derivación presentes | No ejecutada; lectura del código muestra la misma rama `scrypt` en modo corregido | Equivalencia por código propuesta, sin puntuar el caso como superado; no audita criptografía de producción |
| Integridad | 200, manifiesto aceptado con `hmac_sha256` | 422, manifiesto modificado rechazado con `hmac_sha256` | Manifiesto ficticio y clave interna del ejercicio; no valida una cadena real de publicación |
| Registro | 200, `[1,2,3,4,5]`, sin huecos o advertencia | 200, `[1,2,4,5]`, hueco `[3]` y `warning_recorded: true` | Secuencia ficticia; no prueba continuidad de Apache, rotación o entrega de avisos |
| Excepciones | 200, `controlled_response`, `error: null` | 400, `controlled_response`, error solo `code: invalid_fixture`, sin `fictional_trace` en la respuesta mostrada | No comprueba recuperación general del sistema ni ausencia universal de filtraciones |

## Identidad de las evidencias

Todos los recorridos de esta tabla tienen lectura y conservación informadas
en V2 según capturas. Los SHA mostrados y los detalles se conservan en el acta.

| Ejercicio | Ejecución normal | Ejecución adversa corregida |
| --- | --- | --- |
| Configuración | `608700e1fe2c6d7d91f4f275a770a56a` | `9370f0028216a9926d2ca38ef0c2b1ee` |
| Suministro | `d34aba7e1dfae17f750c1ac7c8722be1` | `3708b145de707ced3497dbb37883f07d` |
| Criptografía | `8fa4ffafefc52573988c36dd75fbcbb5` | No ejecutada |
| Integridad | `38d690cd4161439e73f4d38df256e0d1` | `cc7cdd171465527bc6cd31497755c38a` |
| Registro | `2c26ab55cda7b3e95eccfbf5080580b2` | `6a0648c2fed5d6b50f5d08e1a7db6db1` |
| Excepciones | `b4ca524b483be65d9549d6b132f25fe7` | `a8a228ff56fc61649041b9740731cc86` |

El catálogo declara 54 entradas F7: 11 distintas observadas y 43 sin resultado
observado. No es un porcentaje de detección ni 54/54. El PRD no fija 54
ejecuciones como cuota de salida F7. Las variantes restantes y el modo vulnerable
siguen sin validación operativa F7; el corpus y sus expectativas no se cambian.

## Mapa educativo de diez categorías

La correspondencia usa el catálogo local OWASP 2025. Un módulo ilustra aspectos
de una categoría; no certifica toda la categoría o su detección por V2.

| Categoría | Objetivo educativo y módulo | Tipo de evidencia y estado del alcance |
| --- | --- | --- |
| A01 — Control de acceso | Autorizar recursos/operaciones según identidad: traversal, Cargas, Preferencias y Baliza | HTTP, estado de aplicación, formulario entre orígenes y señuelo acotado; observaciones parciales F2/F6 en el acta, aceptación ampliada pendiente |
| A02 — Configuración | Reducir detalle de diagnóstico: Configuración | Revisión ficticia HTTP; normal e intento corregidos observados |
| A03 — Suministro | Comparar el artefacto recibido con referencia confiable fija: Suministro | Revisión ficticia de digests; aceptación normal y rechazo de modificación observados |
| A04 — Criptografía | Distinguir codificación reversible de derivación con sal: Criptografía | `scrypt` observado en normal; comparación con base64 en código, sin ejecución del modo vulnerable |
| A05 — Inyección | Separar datos de consultas, comandos y marcado: módulos F2 y Bitácora F6 | HTTP, respuesta funcional e iframe cuando procede; evidencia parcial e histórico 42/45 conservados, no aceptación global |
| A06 — Diseño inseguro | Exigir aprobación y uso único del permiso: Atraque | Eventos de negocio y estados; aprobación normal, rechazo sin aprobación y reutilización corregida observados, cobertura ampliada pendiente |
| A07 — Autenticación | Observar intentos repetidos y resultado de acceso: módulo base de autenticación | HTTP y auditoría de autenticación prevista; remisión al corpus/evaluación F5, sin nueva validación en esta ronda F7 |
| A08 — Integridad | Verificar integridad del manifiesto antes de aceptarlo: Integridad | Revisión ficticia HMAC; aceptación normal y rechazo de modificación observados |
| A09 — Registro y alertas | Reconocer huecos y distinguir lectura reciente de continuidad: Registro y seguimiento F4 | Secuencia ficticia completa/incompleta observada; seguimiento básico previo separado; rotación, continuidad real y entrega de avisos siguen pendientes |
| A10 — Condiciones excepcionales | Responder de forma acotada ante datos inválidos: Excepciones | Revisión ficticia HTTP; respuesta normal y error controlado observados, recuperación general no demostrada |

## Revisión de los criterios F7

| Criterio del PRD | Revisión del alcance actual | Decisión de alcance |
| --- | --- | --- |
| F7-AC1: objetivo educativo y tipo de evidencia por categoría | El mapa anterior explicita objetivos, módulos, evidencia y alcance observado/no observado para las diez categorías | Matriz documental preparada para revisión del propietario; no equivale a validar operativamente todas las categorías |
| F7-AC2: revisiones/simulaciones no se presentan como explotación real | Panel y respuestas observadas identifican artefactos ficticios; `production_security_claim: false`; documentación declara límites | Conforme en los recorridos y textos revisados; sin generalizar a todo el producto |
| F7-AC3: no declarar detección sin regla, evidencia y evaluación propias | La vista V2 separa reglas F6 del informe LLM y advierte que ausencia de coincidencias no evalúa el artefacto F7; el catálogo conserva `full_category_detection_verified: false` | Mantener sin afirmar detección completa de ninguna categoría F7; no hay evaluación propia de detección F7 |

## Propuesta de cierre y siguiente trabajo

Se propone dar por terminada la **validación manual educativa representativa
F7 en modo corregido, variante 1**, con esta matriz y las limitaciones visibles.
Los cuatro comportamientos nuevos propuestos (Suministro, Integridad, Registro
y Excepciones) ya están observados. No se proponen más ejecuciones para esa
ronda ni se repiten los once recorridos completados.

La aceptación de esta propuesta de alcance y de la fase global sigue pendiente.
La dependencia F6 y las validaciones abiertas del MVP no se eliminan. El
[plan de cierre](CIERRE_V2_PUERTO_UMBRAL_2026_11_03.md) debe revisar después
F6-AC1/2/3/4/5, regresión/aislamiento, operación y recuperación, evaluación o
decisión expresa de alcance F5 y revisión final de documentación V2.

No se autoriza por esta matriz otra suite, llamada al modelo, servicio, caso o
publicación Git. El único análisis Groq anterior sigue consumido. La revisión
puede continuar con evidencias existentes y una lista concreta de bloqueadores,
evitando convertir cobertura no observada en requisitos nuevos del PRD.

La [auditoría de pendientes F6/MVP](PUERTO_UMBRAL_AUDITORIA_CIERRE_2026_10_31.md)
prepara después esa lista y sincroniza las guías vigentes. Distingue los cinco
grupos de cierre de un número de pruebas y conserva los recorridos completados,
las dependencias y las decisiones de alcance pendientes.
