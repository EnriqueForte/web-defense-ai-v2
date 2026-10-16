# Revisión de seguridad e imágenes — 12/10/2026

Seguimiento vigente de seguridad: [revisión residual del 16/10](SEGURIDAD_RESIDUAL_2026_10_16.md).
Auditorías nuevas de los 172 pines conservan seis entradas por OS: Chroma y un
aviso MCP incorporado después; braces de desarrollo sigue retenido. Este acta
mantiene los resultados y límites históricos del 12/10.

Seguimiento posterior: la [migración CrewAI](MIGRACION_CREWAI_2026_10_12.md)
actualiza el contrato de 158 a 172 pines y pasó instalación limpia/SDK/lanzador en
Windows/Ubuntu CI. La auditoría completa posterior mantiene cinco entradas/cuatro IDs
solo en Chroma1.5.9. Las 36 entradas y restricciones de CrewAI1.14.3 descritas
en esta acta corresponden al inventario previo; avisos de imágenes/braces y
alcance de seguridad permanecen independientes.

## Auditorías de paquetes actuales

Se auditó el contrato completo de 158 paquetes Windows y el freeze de 158 Linux,
incluyendo pip/setuptools y uvloop Linux, con pip-audit 2.10.1/PyPI. Uso de
`--no-deps --disable-pip` solo para auditar inventarios ya fijados; no se instaló
con esos flags ni se suprimieron IDs. Se guardaron todos los avisos recibidos.

Ambos inventarios mantienen 36 entradas en cuatro paquetes y 22 IDs principales
distintos. Incluyen duplicados/aliases y no equivalen a 36 explotaciones probadas.
Los dos audits devuelven 1 por avisos; un primer intento Windows falló al leer
caché global y se repitió con caché propia del proyecto hasta obtener JSON válido.

Frontend con pnpm 11.19.0: producción cero avisos, completo un alto de desarrollo.
Chart.js 4.4.1/marked 9.1.6, auditados mediante manifiesto/lockfile aislados, cero avisos.
No se modificaron las dependencias del producto ni sus recursos.

| Paquete retenido | Entradas/IDs | Situación |
| --- | --- | --- |
| chromadb 1.1.1 | 5/4 | Base sin versión corregida; condiciones de servidor revisadas |
| json-repair 0.25.3 | 1/1 | Corrección 0.60.1; CrewAI actual exige ~=0.25.2 |
| litellm 1.83.0 | 24/14 | Correcciones en varios parches/ramas; parte supera ~=1.83.0 de CrewAI actual |
| mcp 1.26.0 | 6/3 | Correcciones 1.27.2/1.28.1; CrewAI actual exige ~=1.26.0 |

Las restricciones se comprobaron en metadatos de CrewAI 1.14.3 instalado. No
es correcto forzar esas versiones ignorando las restricciones. La revisión
individual de las 22 fichas oficiales se completó; la migración del conjunto
compatible sigue abierta. El [recibo JSON](SEGURIDAD_AUDIT_2026_10_12.json)
conserva cada ID, aliases, versiones corregidas de PyPI, rango/parche de la ficha
primaria y condición revisada, sin suprimir avisos.
La app usa LiteLLM cliente y no despliega servidores Chroma/LiteLLM/MCP; esa
inspección limita los caminos observados, no demuestra ausencia global de riesgo.
Las 14 fichas LiteLLM describen caminos de proxy/administración/MCP/Skills que no
se observaron en el proyecto. Los tres avisos MCP requieren transportes/tareas de
servidor. Los cuatro Chroma se refieren a servidor/configuración/aislamiento de
tenants; no se despliega dicho servidor. JSON Repair describe SchemaRepairer y
loads(schema=...), que no aparecen en 0.25.3 instalado. No se certifica benignidad
ni se acepta automáticamente el riesgo por esta inspección.

Hay discrepancias entre bases: por ejemplo, el parche PyPI del aviso de guardrail
es 1.83.10 mientras el texto primario indica 1.83.11. Se conservan ambos y no se
elige un umbral de actualización solo a partir del primer dato.

[Braces](https://github.com/advisories/GHSA-vfj7-8cjw-p6xm) sigue sin parche en la
ficha; el registro npm confirmó latest 3.0.3 y ausencia de 3.0.4. El aviso no se
oculta ni se añade un override a una versión inexistente.

Fuentes de paquetes: [pip-audit/PyPI](https://github.com/pypa/pip-audit),
[JSON Repair](https://github.com/advisories/GHSA-xf7x-x43h-rpqh),
[LiteLLM](https://github.com/BerriAI/litellm/security/advisories/GHSA-3cv6-jpf6-8222),
[MCP](https://github.com/modelcontextprotocol/python-sdk/security/advisories/GHSA-jpw9-pfvf-9f58)
y [Chroma](https://github.com/advisories/GHSA-f4j7-r4q5-qw2c).
Recibos de auditoría en `.local-state/security-20261012/`; no sobrescriben el acta10/10.

## Escaneo remoto de imágenes completado

Trivy 0.75.0 Linux-64bit, release oficial y checksum SHA-256 comprobados:
`c6e65abddb348e25f10549df887045629cf28cc72453cd1c63acb717316b3f3f`.
El workflow Ubuntu comprobó ese checksum antes de ejecutarlo.
Windows no vuelve a ejecutar el binario bloqueado ni desactiva controles.

Referencias recomendadas: mariadb:10.11, ghcr.io/digininja/dvwa:b496a5d y
axllent/mailpit:v1.31.1. Referencias legacy: mysql:8.0, vulnerables/web-dvwa:latest y
python:3.11-slim. `scan_lab_images.py` consulta el registro remoto para linux/amd64,
guarda digests, versión/base del scanner y todos los avisos por paquete/severidad.
No arranca contenedores ni utiliza el Docker local. Un fallo se marca scan_failed
y nunca se convierte en cero vulnerabilidades; se intentan las seis referencias.

El éxito del workflow acredita la ejecución del scanner, no ausencia de riesgos.
DVWA es deliberadamente vulnerable; su aplicación y su infraestructura se deben
revisar por separado. Las etiquetas remotas pueden apuntar a otros digests que
las imágenes instaladas en el laboratorio del usuario; estas últimas no se han
inspeccionado ni reemplazado en esta entrega.

Fuentes: [release Trivy](https://github.com/aquasecurity/trivy/releases/tag/v0.75.0)
y [scanner remoto](https://trivy.dev/docs/latest/target/container_image/).
Tres regresiones offline del resumen/fallos y 82 archivos de sintaxis aprobados.

Código final `3ea20a95214f32c1f748986f4f84dbec5a498395`:
[run 38242912010](https://github.com/EnriqueForte/web-defense-ai-v2/actions/runs/38242912010),
attempt 1, completado/success. Artefacto 11744271076 descargado y verificado:
las seis referencias, digests y conteos del resumen coinciden con los informes.
Trivy 0.75.0, DB versión 2, actualizada 12/10/2026 09:47:21 UTC y descargada
11:29:12 UTC; captura 11:29:39 UTC. El ajuste de caché en el código final conserva
la fecha de la misma base utilizada por el scanner.

| Referencia | Entradas por paquete | Críticas | Altas | IDs distintos | Entradas con versión corregida |
| --- | --- | --- | --- | --- | --- |
| mariadb:10.11 | 98 | 1 | 25 | 86 | 68 |
| DVWA b496a5d | 3571 | 15 | 257 | 2660 | 1442 |
| mailpit:v1.31.1 | 20 | 0 | 4 | 15 | 19 |
| mysql:8.0 legacy | 255 | 1 | 100 | 204 | 254 |
| vulnerables/web-dvwa:latest legacy | 1575 | 254 | 551 | 439 | 1380 |
| python:3.11-slim legacy | 175 | 0 | 46 | 82 | 11 |

El JSON conserva también medias/bajas/desconocidas, todos los digests y SHA-256
de cada informe. Estos conteos no son incidentes ni explotaciones probadas.
La ausencia de críticas en Mailpit/Python no equivale a ausencia de riesgo.

La crítica de MariaDB corresponde a la biblioteca estándar Go de un binario de
la imagen, no se atribuye automáticamente al servidor SQL. Las críticas DVWA
incluyen Perl, libxml2, headers y cliente SSH de la base; no son todas fallos
intencionados de la aplicación. Mailpit tiene avisos altos de Go/x/net con
versiones corregidas. El DVWA legacy usa Debian 9.5 marcado EOSL. Esto requiere
actualización/revisión de infraestructura y compatibilidad de laboratorio; no se
sustituyen tags o volúmenes sin ese ensayo ni se acepta el riesgo automáticamente.

Recibos `.local-state/security-20261012/images-38242912010/`, ZIP incluido.
El primer run 38242250320 completó los seis scans pero omitía la fecha de la DB
en el resumen de versión por consultar otra caché; sus registros se conservan
como evidencia previa. El resultado final anterior incorpora esa corrección.

## Compatibilidad y trabajos siguientes

[CI 38242912062](https://github.com/EnriqueForte/web-defense-ai-v2/actions/runs/38242912062),
mismo SHA final, Windows/Ubuntu success. Logs revisados: instalación nueva,
contrato estricto 158/0, freeze completo, build, 82 sintaxis, tres JS, HTTP
sintético, 25 SDK, lint/tipos/15 UI y smoke API/proxy200/ejecutoroffline/cierrelibre.
Ubuntu aprobó 298 Python; Windows 297 y omitió un caso específico Linux.

Las auditorías actualizadas y el escaneo efectivo de las seis referencias quedan
completados. Seguridad sigue abierta por migración compatible CrewAI/dependencias,
paquete braces sin parche, revisión/actualización de infraestructura y revisión
final del historial. El siguiente trabajo concreto es evaluar un conjunto de
CrewAI y dependencias corregidas en un entorno aislado, con resolución compatible,
auditoría y pruebas antes de cambiar el contrato del producto.

## Alcance

No se hicieron llamadas al proveedor, trabajos de análisis, envíos o reinicios
operativos; `.env` no leído. Scanner y herramientas aislados de los entornos de
la aplicación. Los avisos retenidos y las actualizaciones todavía pendientes mantienen
abierto el cierre de seguridad; no se declara una versión libre de vulnerabilidades.
