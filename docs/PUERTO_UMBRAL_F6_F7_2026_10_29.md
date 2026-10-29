# Puerto Umbral — preparación de código F6/F7

Fecha: 29/10/2026, Europe/Madrid. Estado: **implementación revisada en código;
sin ejecutar escenarios, servicios o suites y sin aceptación de fases**.
El propietario solicita cerrar F0–F7 antes del martes 03/11 y elige expresamente
continuar por ahora solo con desarrollo y revisión de código. La planificación
y los criterios que siguen abiertos están en el
[plan de cierre de V2 y Puerto Umbral](CIERRE_V2_PUERTO_UMBRAL_2026_11_03.md).

## Alcance y separación del histórico

El corpus original de F2 permanece en 45 entradas y conserva su resultado
histórico 42/45. No se ha repetido, renombrado o ajustado para incorporar estas
ampliaciones. F6 y F7 tienen catálogo y semilla propios en
[advanced_catalog.py](../labs/puerto_umbral/lab/advanced_catalog.py) y un
[manifiesto separado](../labs/puerto_umbral/lab/extensions-corpus.json):
99 entradas declaradas, 45 para F6 y 54 para F7. Cada módulo define tres
variantes, seis intentos entre dos modos y tres controles normales corregidos.
Son expectativas fijadas antes de ejecutar, no resultados de una evaluación.

Las once ampliaciones comparten un target avanzado por modo y se restablecen
antes de cada ejecución individual. Se conservan los diez targets base y las
dos pasarelas: la topología preparada pasa de 12 a 14 contenedores. Los dos
targets nuevos utilizan usuario 10001, raíz de solo lectura, límites de recursos,
sin privilegios o montajes del host, y `network_mode: none`. Las pasarelas montan
solo el socket del módulo de su modo. El código de inspección contempla esta
topología; todavía no se ha construido o comprobado en Docker.

El mismo comando de arranque construirá las imágenes al distribuir esta fuente,
pero **no se solicita arrancarlo o actualizar la VM para probarla en este bloque**.
No cambian los digests base, dependencias Python/Node, `.env` o el Site privado.

## F6: escenarios con estado e identidad

| Módulo | Comparación preparada | Evidencia y límite |
| --- | --- | --- |
| XSS almacenado | Guarda un aviso y lo vuelve a presentar; salida sin codificar frente a codificación HTML | POST/GET, auditoría de almacenamiento/lectura e iframe. Solo el marcador del iframe y nonce acreditan ejecución; renderizar no basta |
| IDOR | Sesión de estibador, objeto de su propiedad y objeto de supervisor; autorización por propietario | Actor/rol, recurso, propietario, decisión y respuesta. Identidades y datos ficticios |
| CSRF | Preferencias de cuenta; control de origen y token ligado a sesión | Prueba HTTP separada de formulario real entre 4381 y el portal. Confirmación requiere cookie y evento de origen cruzado que no proceda del ejecutor HTTP |
| SSRF acotada | URL lógica del señuelo, recurso público frente a interno | HTTP real sobre socket Unix privado a un pequeño servidor dentro del target. Destinos enumerados, sin IP, DNS, redirecciones o URL arbitraria |
| Permisos de atraque | Ejecutar sin aprobación y reutilizar un permiso consumido, frente a aprobación de supervisor y uso único | Estado anterior/posterior y actor. La autorización corregida requiere estado aprobado y consume el permiso |

Los tokens de sesión/CSRF se conservan en memoria durante la secuencia y se
omiten del texto de respuesta guardado por el controlador. El recibo distingue
hash de respuesta original y hash del texto redactado. No guarda cabeceras
Authorization, contraseñas del formulario o cookies. Las sesiones son
exclusivamente ficticias y se pierden al restablecer el módulo.
Las cookies tienen nombres separados por modo. Cada target avanzado queda
ligado al primer identificador de ejecución recibido después del reset y
rechaza otro identificador; una referencia anterior no se incorpora al lote
de la ejecución siguiente. Los identificadores de recurso desconocidos se
normalizan y no copian entradas arbitrarias a la auditoría.

El ejercicio CSRF de navegador es una página estática del origen de control,
sin scripts ni token del panel. El operador crea la sesión ficticia en el
portal y envía un formulario desde el otro origen. La comprobación posterior
consulta la auditoría capturada; la prueba HTTP inicial no se presenta como
prueba de navegador. Ambos pasos quedan pendientes de ejecución autorizada.
El ejecutor conserva su límite de 30 segundos. Solo el target avanzado dispone
de una ventana máxima de cinco minutos desde su primera petición para completar
los pasos manuales, sin ampliar las 20 solicitudes ni la frecuencia máxima de
dos por segundo. La fecha límite queda en el recibo y se muestra en el panel;
un reset o agotar la cuota puede invalidar antes esa ventana. Los targets base
mantienen sus 30 segundos. Las confirmaciones usan el mismo bloqueo que el
ejecutor y el reset, y conservan los fallos de captura sin marcar una
confirmación exitosa antes de obtener la evidencia correspondiente.

Las páginas del target avanzado permiten conservar su origen para los
formularios normales. El iframe XSS del panel mantiene `sandbox="allow-scripts"`
sin `allow-same-origin`; la confirmación sigue validando `event.source`, origen
opaco y nonce. El CSP del target limita conexiones y formularios; el formulario
CSRF del controlador tiene una excepción de CSP solo para los dos portales
loopback. No se amplía el acceso del portal a la API de control.

## F7: revisiones de artefactos ficticios

| Categoría OWASP 2025 | Ejercicio preparado | Qué no acredita |
| --- | --- | --- |
| A02 — Configuración | Réplica de diagnóstico con detalle ficticio frente a respuesta mínima | Una auditoría de configuración de Apache o de producción |
| A03 — Suministro | Artefacto local modificado frente a un digest de referencia fijo | Un análisis de dependencias reales, firma de proveedor o instalación de malware |
| A04 — Criptografía | Codificación base64 reversible frente a derivación scrypt con sal | Certificación criptográfica o parámetros recomendados para cualquier despliegue |
| A08 — Integridad | Manifiesto ficticio modificado frente a comprobación HMAC | Firma de todos los datos o de toda la cadena de publicación |
| A09 — Registro y alertas | Secuencia ficticia con un hueco y advertencia local | Continuidad de Apache, entrega de notificaciones o validación ampliada F4 |
| A10 — Excepciones | Detalle de error ficticio frente a respuesta controlada | Recuperación exhaustiva ante fallos del sistema real |

El panel muestra `fixture_review` como revisión de artefactos y ofrece un mapa
de las diez categorías. Las restantes se relacionan con los escenarios de
F2/F6. Todas las categorías conservan aceptación pendiente. Un catálogo
educativo completo no implica detección completa por V2 o explotación real.

## Auditoría y observador de V2

El [contrato de eventos](../labs/puerto_umbral/lab/audit_contract.py) fija una
lista cerrada de campos: secuencia, UTC, ejecución/petición, componente/modo,
actor/rol, acción/recurso/propietario, decisión/resultado/HTTP, origen, mecanismo
de sesión y estados observados. Rechaza campos adicionales, truncado y valores
fuera de formato. No admite etiquetas esperadas del corpus, credenciales,
tokens o cuerpos arbitrarios. La auditoría se obtiene por HTTP local, se
valida y guarda fuera del target con hash y correlación de peticiones.
Los componentes se denominan por su función de negocio (carga, preferencias,
baliza, etc.), sin nombres de vulnerabilidad, categoría OWASP o caso esperado.

El [lector de V2](../dashboard/services/application_audit.py) valida el recibo
del controlador, versión, ruta y digest antes de procesar el lote. Sus reglas
describen acceso a recursos de otro propietario, aprobación ausente, lectura
del señuelo interno, control de origen y contenido almacenado sin codificar.
No consultan resultados esperados del corpus ni el veredicto funcional del
ejecutor. Un evento de renderizado no se transforma en ejecución XSS.

La auditoría procede de la aplicación observada: no equivale a una afirmación
independiente de compromiso. La nueva vista en Actividad muestra esas
observaciones por reglas separadas del informe LLM. No modifica los cuatro
grupos ya publicados ni produce métricas del detector.

Rutas preparadas:

- `GET /api/v1/fuentes/auditoria`: solo lectura de la última auditoría disponible
  del modo seleccionado. No usa Docker ni llama al modelo.
- `POST /api/v1/fuentes/auditoria/capturar`: acción explícita local para conservar
  un lote validado en el perfil V2. Fija `run_id` y `sha256`, requiere perfil
  Puerto Umbral y captura manual habilitada; rechaza una auditoría cuyo hash
  cambió y respeta bloqueos de ciclo/motor y operaciones activas.

La copia conservada usa `.local-state/puerto-umbral/application-audit/` con
`current.json` y snapshots inmutables `events.json`/`receipt.json`. La lista del
backup y del restaurador reconoce exclusivamente esos nombres y UUID. Los
recibos originales bajo `labs/` siguen requiriendo conservación separada.
Los 66 archivos recuperados anteriormente no acreditan esta cobertura nueva.
Repetir la conservación del mismo modo, ejecución y hash reutiliza la copia
íntegra identificada por esos datos; no genera otra generación ni sobrescribe
una copia incompleta o distinta. El recibo conserva el estado de la ejecución
en el momento de la copia. La interfaz advierte si el lote es parcial y bloquea
la conservación durante lectura, errores, seguimiento o captura manual
deshabilitada. Un plazo de red agotado se presenta como resultado sin confirmar,
porque la escritura del servidor puede haber terminado.

## Revisión de código solicitada, paso 1 — 29/10/2026

Recorrido de lectura manual de target, controlador, contrato, lector de V2,
rutas Flask, panel React, JavaScript del laboratorio, configuración declarada
y lista compartida de respaldo/restauración. Se aplicaron estas correcciones
locales; su comportamiento todavía debe comprobarse cuando se autorice ejecutar:

| Punto encontrado | Corrección en código |
| --- | --- |
| Confirmación podía coincidir con otra ejecución/reset | Bloqueo compartido para confirmaciones, UI bloqueada durante la operación y vínculo de target a ejecución |
| Ventana de 30 segundos poco práctica para pasos humanos | Ventana avanzada de cinco minutos; ejecutor/base, frecuencia y cuota conservan sus límites |
| Captura de navegador podía fallar después de marcar confirmación | Capturar/persistir antes de confirmar; errores y nuevas evidencias quedan registrados incluso si no aparece el evento esperado |
| Lectura previa comprobaba tamaño, pero después cargaba el archivo sin límite | Lectura acotada antes de decodificar, UTF-8 estricto y comparación de identidad/tamaño/fechas tras la lectura |
| Valores libres en campos semánticos del contrato | Enumeraciones para decisión, origen, control CSRF, alcance del señuelo, renderizado y mecanismo de sesión |
| Una recaptura fallida podía dejar seleccionable el lote anterior | Estado de fuente inválida cuando el último intento registrado falla; conteo, esquema y modo comprobados |
| La interfaz podía conservar datos antiguos tras una actualización fallida | Error visible, conservación deshabilitada y validación de identificadores, hashes, conteos y filas; cancelación al salir de la vista |
| Repetir una solicitud podía crear copias duplicadas | Identificador estable por modo/ejecución/hash y reutilización solo tras verificar contenido y recibo completos |

La revisión estática del paso 1 queda completada con estas correcciones. No
equivale a revisión exhaustiva, ausencia de defectos, validación funcional o
aceptación F6/F7. Permanecen pendientes navegador real, compatibilidad de la
topología Docker, permisos efectivos de volúmenes, límites de tiempo/cuota,
cancelación, concurrencia, regresión y recuperación de estas copias nuevas.
No se ejecutó ninguna de esas comprobaciones operativas.

## Estado de aceptación y revisión pendiente

| Criterio | Preparación actual | Pendiente para cerrarlo |
| --- | --- | --- |
| F6-AC1 | Identidades, objetos, propietarios y flujo de permisos implementados | Observar positivos y controles normales de cada variante |
| F6-AC2 | Señuelo Unix HTTP y destinos enumerados, targets sin red IP | Construcción e inspección real de la topología y caso SSRF |
| F6-AC3 | Página entre orígenes y confirmación por auditoría de cookie/origen | Revisión real de navegador en ambos modos |
| F6-AC4 | Lector por esquema/hash; sin lectura de etiquetas esperadas | Verificación operativa y evaluación independiente de la nueva fuente |
| F6-AC5 | Corpus de ampliación separado y corpus base intacto | Positivos, normales y regresión autorizados |
| F7-AC1 | Mapa de diez categorías y tipo de evidencia por módulo | Revisar artefactos y correspondencia con el propietario |
| F7-AC2 | Revisiones ficticias y límites visibles en panel/recibos/docs | Comprobar esas pantallas en el producto actual |
| F7-AC3 | No se declaran categorías completas detectadas | Evaluación propia antes de cualquier afirmación de detección |

Las comprobaciones estáticas no acreditan comportamiento en navegador,
compatibilidad de Docker, efectos funcionales, regresión o calidad de detección.
No hay un resultado nuevo 99/99 ni cierre de F6/F7. El siguiente bloque de
ejecución se decidirá con el propietario; la restricción actual es solo código.

Revisión estática completada en este bloque: sintaxis/compilación en memoria de
ocho archivos Python sin importarlos; sintaxis JavaScript sin ejecutarlo;
TypeScript sin emisión; JSON OpenAPI y manifiesto de ampliación legibles; YAML
de 14 servicios con las propiedades de aislamiento declaradas; referencias
entre IDs HTML y selectores JS coherentes; 184 enlaces locales comprobados sin
ausencias en la preparación inicial; la comprobación posterior del paso 1
abarca 180 enlaces locales actuales sin ausencias y `git diff --check` correcto.
El corpus base se comparó con HEAD y
permanece sin cambios. No se ha realizado build Docker, preview, compilación
Next.js completa o pruebas funcionales. El primer recorrido de validación
está pendiente de autorización posterior.

## Distribución autorizada del código revisado

El 29/10 el propietario solicita expresamente commit/push de este paquete antes
de continuar. Se prepara una publicación de 34 archivos sobre `main`, con base
`c8abcaf` comprobada frente a `origin/main` y mensaje `[skip ci]`. Incluye la
fuente F6/F7, su integración en V2, documentación y las actas pendientes de la
recuperación previamente observada. La identidad de entrega es el commit que
incorpora esta nota; el resultado del push y su coincidencia remota se verifican
al terminar la operación Git. No se crea una release o etiqueta nueva.

Publicar la fuente no construye o activa la topología nueva, actualiza Parrot,
ejecuta suites o consume la autorización de otro análisis. El corpus base y los
JSON históricos F5 se mantienen sin cambios. Esta entrega conserva la revisión
funcional, las métricas del detector y la aceptación de F6/F7 como pendientes.

## Referencias de diseño

- [OWASP Top 10:2025](https://top10.owasp.org/2025/): categorías del mapa educativo.
- [Prevención de IDOR](https://cheatsheetseries.owasp.org/cheatsheets/Insecure_Direct_Object_Reference_Prevention_Cheat_Sheet.html): autorización por objeto y usuario.
- [Prevención de CSRF](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html): token y comprobación de origen.
- [Prevención de SSRF](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html): destinos permitidos y límites de conectividad.

Consultadas el 29/10/2026. Son referencias de diseño; no certifican esta
implementación. La guía de Sites se aplica en modalidad local, preservando el
Site privado F1 y sin desplegar allí el backend del laboratorio.
