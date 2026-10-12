# Revisión de seguridad e imágenes — 12/10/2026

## Auditorías de paquetes actuales

Se auditó el contrato completo de158paquetes Windows y el freeze158Linux,
incluyendo pip/setuptools y uvloop Linux, con pip-audit2.10.1/PyPI. Uso de
`--no-deps --disable-pip` solo para auditar inventarios ya fijados; no se instaló
con esos flags ni se suprimieron IDs. Se guardaron todos los avisos recibidos.

Ambos inventarios mantienen36entradas en cuatro paquetes,22IDs principales
distintos. Incluyen duplicados/aliases y no equivalen a36explotaciones probadas.
Los dos audits devuelven1 por avisos; un primer intento Windows falló al leer
caché global y se repitió con caché propia del proyecto hasta obtener JSON válido.

Frontend con pnpm11.19.0: producción0avisos, completo1alto de desarrollo.
Chart.js4.4.1/marked9.1.6, auditados mediante manifiesto/lockfile aislados,0avisos.
No se modificaron las dependencias del producto ni sus recursos.

| Paquete retenido | Entradas/IDs | Situación |
| --- | --- | --- |
| chromadb1.1.1 | 5/4 | Base sin versión corregida; revisar condiciones de servidor y caminos usados por CrewAI |
| json-repair0.25.3 | 1/1 | Corrección0.60.1; CrewAIactual exige~=0.25.2 |
| litellm1.83.0 | 24/14 | Correcciones en varios parches/ramas; parte supera el rango~=1.83.0 de CrewAIactual |
| mcp1.26.0 | 6/3 | Correcciones1.27.2/1.28.1; CrewAIactual exige~=1.26.0 |

Las restricciones se comprobaron en metadatos de CrewAI1.14.3 instalado. No
es correcto forzar esas versiones ignorando las restricciones. La revisión
individual de condiciones y una migración del conjunto compatible siguen abiertas.
La app usa LiteLLM cliente y no despliega servidores Chroma/LiteLLM/MCP; esa
inspección limita los caminos observados, no demuestra ausencia global de riesgo.

[Braces](https://github.com/advisories/GHSA-vfj7-8cjw-p6xm) sigue sin parche en la
ficha; el registro npm confirmólatest3.0.3 y ausencia de3.0.4. El aviso no se
oculta ni se añade un override a una versión inexistente.

Fuentes de paquetes: [pip-audit/PyPI](https://github.com/pypa/pip-audit),
[JSON Repair](https://github.com/advisories/GHSA-xf7x-x43h-rpqh),
[LiteLLM](https://github.com/BerriAI/litellm/security/advisories/GHSA-3cv6-jpf6-8222),
[MCP](https://github.com/modelcontextprotocol/python-sdk/security/advisories/GHSA-jpw9-pfvf-9f58)
y [Chroma](https://github.com/advisories/GHSA-f4j7-r4q5-qw2c).
Recibos de auditoría en `.local-state/security-20261012/`; no sobrescriben el acta10/10.

## Escaneo remoto de imágenes preparado

Trivy0.75.0Linux-64bit, releaseoficial y checksumSHA256 comprobados:
`c6e65abddb348e25f10549df887045629cf28cc72453cd1c63acb717316b3f3f`.
Se prepara workflowUbuntu con comprobación de ese checksum antes de ejecutarlo.
Windows no vuelve a ejecutar el binario bloqueado ni desactiva controles.

Referencias recomendadas: mariadb:10.11,ghcr.io/digininja/dvwa:b496a5d,
axllent/mailpit:v1.31.1. Referencias legacy: mysql:8.0,vulnerables/web-dvwa:latest,
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
Tres regresiones offline del resumen/fallos y82archivossintaxis aprobados.
Escaneo real y revisión de resultados pendientes de la ejecución CI.

## Alcance

No se hicieron llamadas al proveedor, trabajos de análisis, envíos o reinicios
operativos; `.env` no leído. Scanner y herramientas aislados de los entornos de
la aplicación. Los avisos retenidos y el escaneo todavía pendiente mantienen
abierto el cierre de seguridad; no se declara una versión libre de vulnerabilidades.
