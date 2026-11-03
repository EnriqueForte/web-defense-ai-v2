# Puerto Umbral F7 — matriz de cierre educativo

Revisión documental finalizada el **03/11/2026**, Europe/Madrid, por instrucción
del propietario, sin ejecutar pruebas. Acta de origen: 31/10/2026.
**Matriz educativa F7 aceptada expresamente por el propietario el 03/11.**
La ronda representativa previa conserva once recorridos observados; no se
añaden ejecuciones ni se acredita detección completa de categorías por V2.

La aceptación se limita al mapa, evidencias y límites de esta matriz. F6
conserva su cierre expreso anterior; F4/F5 quedan también cerradas por decisión
expresa sin sus pruebas restantes, con omisiones no verificadas. El
[registro de decisiones](CIERRE_V2_PUERTO_UMBRAL_2026_11_03.md) detalla el
alcance; no se infiere validación completa de categorías o aceptación global
del conjunto de entrega.

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
| A01 — Control de acceso | Autorizar recursos/operaciones según identidad: traversal, Cargas, Preferencias y Baliza | HTTP, estado de aplicación, formulario entre orígenes y señuelo acotado; se conserva la evidencia parcial F2/F6 y el cierre expreso F6 con verificaciones omitidas, sin certificar toda la categoría |
| A02 — Configuración | Reducir detalle de diagnóstico: Configuración | Revisión ficticia HTTP; normal e intento corregidos observados |
| A03 — Suministro | Comparar el artefacto recibido con referencia confiable fija: Suministro | Revisión ficticia de digests; aceptación normal y rechazo de modificación observados |
| A04 — Criptografía | Distinguir codificación reversible de derivación con sal: Criptografía | `scrypt` observado en normal; comparación con base64 en código, sin ejecución del modo vulnerable |
| A05 — Inyección | Separar datos de consultas, comandos y marcado: módulos F2 y Bitácora F6 | HTTP, respuesta funcional e iframe cuando procede; histórico 42/45 y corrección representativa posterior de comandos conservados; Bitácora vulnerable omitida por cierre expreso F6, sin aceptación global |
| A06 — Diseño inseguro | Exigir aprobación y uso único del permiso: Atraque | Eventos de negocio y estados; controles corregidos observados y consumo vulnerable de permiso pendiente recibido el 03/11, con observación/copia V2; F6 cerrada con límites, sin certificar todo flujo de negocio |
| A07 — Autenticación | Observar intentos repetidos y resultado de acceso: módulo base de autenticación | HTTP local, ráfaga y resultado del acceso del corpus F2; evaluación del detector F5 sin realizar, sin auditoría adicional o nueva validación en esta ronda F7 |
| A08 — Integridad | Verificar integridad del manifiesto antes de aceptarlo: Integridad | Revisión ficticia HMAC; aceptación normal y rechazo de modificación observados |
| A09 — Registro y alertas | Reconocer huecos y distinguir lectura reciente de continuidad: Registro y seguimiento F4 | Secuencia ficticia completa/incompleta observada; por separado, veinte muestras API y fallo/recuperación con snapshot conservado recibidos en F4. Rotación/continuidad completa y entrega de avisos no acreditadas; el ejercicio no las sustituye |
| A10 — Condiciones excepcionales | Responder de forma acotada ante datos inválidos: Excepciones | Revisión ficticia HTTP; respuesta normal y error controlado observados, recuperación general no demostrada |

## Revisión de los criterios F7

El dictamen siguiente es documental y se limita a las fuentes leídas. La
aceptación del propietario se registra por separado de esta revisión.

| Criterio del PRD | Revisión del alcance actual | Dictamen documental del 03/11 |
| --- | --- | --- |
| F7-AC1: objetivo educativo y tipo de evidencia por categoría | Mapa con diez filas, objetivos, módulos y tipos de evidencia explícitos, cotejado con el catálogo base y el de ampliaciones; estados observados y omisiones visibles | Revisión documental completada: correspondencia y alcance explícitos para las diez categorías. No equivale a validar operativamente cada categoría |
| F7-AC2: revisiones/simulaciones no se presentan como explotación real | El target declara `fictional_artifact_review` y `production_security_claim: false`; el panel identifica la revisión ficticia y la matriz limita cada conclusión | Conforme en el código, actas y textos revisados. Los once recorridos se describen como revisiones HTTP de fixtures, sin presentarlos como explotación o seguridad de producción |
| F7-AC3: no declarar detección sin regla, evidencia y evaluación propias | V2 separa reglas F6 del informe LLM y advierte que ausencia de coincidencias no evalúa F7; el catálogo conserva `full_category_detection_verified: false` | Conforme en el alcance documental revisado: ninguna categoría se declara detectada completamente. No existe evaluación propia de detección F7 y se mantiene explícita |

## Trazabilidad de la revisión documental del 03/11

Se realiza únicamente lectura y cotejo, sin importar o ejecutar los módulos:

- **Requisitos:** F7-AC1/2/3 cotejados con el PRD. Sus criterios no fijan una
  cuota de 54 ejecuciones ni requieren que todas las categorías sean detectadas.
- **Catálogo:** diez categorías locales, cinco escenarios F2, cinco F6 y seis
  revisiones F7. Las seis revisiones, tres variantes y tres entradas por variante
  explican las 54 entradas F7; no se genera o modifica el corpus para contarlas.
- **Evidencia recibida:** los once identificadores de la tabla se localizan en
  el acta F6/F7, con sus recepciones. Son seis normales y cinco adversos corregidos,
  todos variante 1. Se cotejan registros documentales, sin abrir la VM, leer
  originales operativos, recalcular hashes o repetir copias.
- **Criptografía:** la lectura de `review()` confirma que en modo corregido
  normal e intento eligen `scrypt`. El intento no ejecutado permanece sin
  resultado observado; la equivalencia por código no se transforma en un pass.
- **Presentación:** el panel denomina la acción «Revisar artefacto ficticio»;
  el componente de auditoría V2 distingue ausencia de reglas y evaluación F7.
  El observador no tiene una rama de detección de artefactos F7; guardar sus
  eventos no se describe como clasificación o evaluación del contenido.

Además del catálogo y el target enlazados arriba, se leen el
[catálogo base](../labs/puerto_umbral/lab/catalog.py), el
[panel del laboratorio](../labs/puerto_umbral/lab/control.js), el
[observador de auditoría](../dashboard/services/application_audit.py) y su
[componente V2](../frontend/src/components/application-audit-panel.tsx).
Se incorpora la recepción Atraque del [registro de cierre F6](PUERTO_UMBRAL_CIERRE_MINIMO_2026_11_03.md)
y la [medición/recuperación F4](PUERTO_UMBRAL_MEDICION_F4_2026_11_02.md), sin
atribuir esas comprobaciones al ejercicio ficticio de Registro.

## Dictamen de cierre documental y alcance de entrega

**Bloque de revisión documental F7 completado y matriz aceptada por el propietario.**
El expediente aceptado incluye mapa de diez categorías,
once recorridos identificados, evidencias y límites por ejercicio, y dictamen
documental de sus tres criterios. No se identifica trabajo documental adicional
imprescindible para esta matriz dentro del alcance revisado.

La formulación respaldada para la entrega es: «Puerto Umbral incluye un mapa
educativo de diez categorías y seis tipos de revisión de artefactos ficticios;
se documentan once recorridos representativos en modo corregido, variante 1,
con lectura y conservación de auditoría V2 informadas por el propietario».
No se anuncia 54/54, detección completa de diez categorías, garantía de
seguridad de producción ni ejecución del intento de Criptografía.

El propietario acepta expresamente esta matriz el 03/11; F7 queda aceptada
en ese alcance educativo, sin pruebas adicionales. F6 conserva su cierre
previo y F4/F5 quedan cerradas por decisión expresa con sus omisiones. En el
[plan de cierre](CIERRE_V2_PUERTO_UMBRAL_2026_11_03.md) queda la consolidación/
aceptación final de la entrega, con límites de cobertura F2/F3 registrados.

No se solicita otra ejecución para la ronda F7 ni se añaden pruebas bajo la
instrucción vigente. No hay cambios de runtime, JSON históricos, servicios,
modelo, copias, hashes, Git o release. La [auditoría de cierre](PUERTO_UMBRAL_AUDITORIA_CIERRE_2026_10_31.md)
conserva las decisiones separadas de los resultados observados.
