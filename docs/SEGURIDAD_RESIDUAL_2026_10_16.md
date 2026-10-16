# Seguridad residual y candidato Mailpit — 16/10/2026

Estado: auditorías actualizadas; revisión de imágenes y compatibilidad en
preparación local. No se declara cierre global de seguridad.

## Auditorías y versiones publicadas

Se auditaron los freeze completos de Windows/Ubuntu de CI38886025823: 172
paquetes por OS, incluidos los instaladores, con pip-audit 2.10.1/PyPI.
Los archivos de entrada coinciden por SHA-256 con los inventarios verificados;
`--no-deps --disable-pip` se usa únicamente para auditar esos inventarios,
sin instalar paquetes ni ignorar IDs. Los avisos completos se conservan.

Resultado por OS: seis entradas/cinco IDs, en Chroma 1.5.9 y MCP 1.28.1.
Chroma conserva cinco entradas/cuatro IDs, incluido un duplicado de la base.
El aviso MCP no figuraba en la auditoría anterior. pnpm 11.19.0/npm: cero avisos
en producción y un alto de desarrollo en braces 3.0.3. Se conserva el detalle en
[el recibo JSON](SEGURIDAD_RESIDUAL_2026_10_16.json).

| Dependencia | Resultado revisado | Decisión |
| --- | --- | --- |
| Chroma 1.5.9 | Las cuatro fichas siguen sin versión corregida; PyPI mantiene 1.5.9 | Conservar avisos y límite de uso local; no se acredita ausencia general de riesgo |
| MCP 1.28.1 | GHSA-84m7-p3x7-pcfv; corregido en 1.30.0/2.2.0 | Requiere migración compatible; CrewAI instalado 1.15.27 y último revisado 1.15.28 exigen ~=1.28.1 |
| braces 3.0.3 | GHSA-vfj7-8cjw-p6xm; npm latest 3.0.3, sin 3.0.4 publicada | Retenido; no se fuerza una versión inexistente |

La inspección del proyecto no observa un servidor Chroma ni MCP Streamable HTTP
con estado. El nuevo aviso MCP describe retención ilimitada de sesiones y sus
parámetros iniciales en ese modo. La ficha del mantenedor indica severidad alta;
el registro GitHub consultado indica media. Se conservan ambos datos. No se
cambia el rango MCP ignorando las restricciones de CrewAI.

braces entra por `@next/eslint-plugin-next -> fast-glob -> micromatch` en las
herramientas de desarrollo. No se observa que los logs o peticiones del usuario
se usen como patrones de glob. Estas observaciones limitan los caminos revisados;
no suprimen hallazgos ni constituyen aceptación automática del riesgo.

Fuentes primarias consultadas:
[Chroma pre-auth](https://github.com/advisories/GHSA-f4j7-r4q5-qw2c),
[Chroma tenants](https://github.com/advisories/GHSA-2wm9-hf6c-p5cr),
[Chroma actualización](https://github.com/advisories/GHSA-36p7-vc44-83pf),
[Chroma RBAC](https://github.com/advisories/GHSA-xph7-9rjv-w5fr),
[MCP](https://github.com/modelcontextprotocol/python-sdk/security/advisories/GHSA-84m7-p3x7-pcfv),
[braces](https://github.com/advisories/GHSA-vfj7-8cjw-p6xm),
[metadatos CrewAI](https://pypi.org/pypi/crewai/json) y
[registro braces](https://registry.npmjs.org/braces).

## Evaluación de Mailpit

La versión del laboratorio sigue siendo `axllent/mailpit:v1.31.1`. Se selecciona
como candidato [v1.31.6](https://github.com/axllent/mailpit/releases/tag/v1.31.6),
publicada el 15/10. Ser posterior no demuestra que corrija los avisos del escaneo;
la decisión exige comparar ambas imágenes con la misma base del scanner.

`scan_lab_images.py --image-set mailpit-review` separa actual/candidata, conserva
digest, ImageID y todas las severidades. El inventario predeterminado de seis
referencias se conserva. El workflow permite solicitar la revisión mediante
`workflow_dispatch`; en ese perfil se añade una prueba Docker aislada en el
runner Ubuntu de CI, con dos instancias efímeras y ninguna configuración operativa.

La prueba exige igualdad entre ImageID ejecutado y escaneado. Usa redes bridge
propias sin masquerading (como host-loopback de Compose), puertos efímeros solo
en 127.0.0.1, filesystem de solo lectura con tmpfs
para SQLite y ausencia de relay externo. Invoca `enviar_email` real con dotenv
desactivado, direcciones example.invalid y SMTP loopback; comprueba versión,
lectura API, asunto/cuerpo UTF-8, una sola recepción y exportación raw. Verifica
las etiquetas de propiedad antes de eliminar sus contenedores/redes. El registro
distingue fallos de escaneo, de compatibilidad y de limpieza.

`check_mailpit_compat.py` sin `--run` solo muestra el plan: no consulta Docker,
no arranca contenedores y no conecta a SMTP/HTTP. La regresión normal cubre ese
límite, el rechazo de interfaces abiertas/referencias ajenas y la separación de
imágenes. No se ha sustituido la imagen de Parrot ni se ha tocado su buzón.

Criterio de promoción: escaneo real válido con comparación de avisos, igualdad
de imagen con la prueba y SMTP/API/limpieza aprobados. Aun si se promociona, el
inventario histórico y los avisos restantes siguen visibles. La instalación VM
y la conservación de su buzón requieren un paso de operación separado; actualizar
el repositorio no equivale a recrear el contenedor.

## Evidencia local y pendientes

352 casos Python (351 aprobados/uno Linux omitido), tres JS y 96 archivos sin
errores de sintaxis. Cuatro pruebas nuevas; no invocan Docker ni SMTP. Los
resultados reales de imagen/compatibilidad y la publicación/CI están pendientes.
No se han leído bytes `.env`, consumido API LLM o enviado notificaciones reales.

Recibos de auditoría/fuentes en `.local-state/security-20261016/`, excluidos de
Git. Los del 12/10 se preservan. Siguen pendientes Chroma, MCP, braces, resto de
infraestructura y auditoría final del historial; no se declara software sin avisos.

## Primera publicación y evidencia remota

Publicado `c96f0cf72c47c092580d32ca58414e48199c8af2`. Inventario remoto
38889958310 completado/success; CI de compatibilidad 38889958508 en observación.
La revisión Mailpit 38890039641/attempt1 terminó failure en compatibilidad, con
escaneos válidos de las dos referencias y misma DB del 16/10 (UpdatedAt 01:13:54 UTC).
Artefacto 12041267004 descargado: las filas coinciden con sus informes completos.

| Imagen | Críticas/altas/medias/bajas/desconocidas | Total |
| --- | --- | --- |
| Mailpit 1.31.1 | 0/4/13/1/2 | 20 |
| Mailpit 1.31.6 | 0/0/0/0/1 | 1 |

La candidata conserva `GO-2026-5932` en golang.org/x/crypto v0.58.0, sin versión
corregida y severidad UNKNOWN del scanner. La [ficha Go](https://pkg.go.dev/vuln/GO-2026-5932)
describe OpenPGP sin mantenimiento; no se suprime ni se concluye alcanzabilidad
solo por presencia del módulo. La mejora de conteos no acredita software sin riesgo.

Ambas instancias arrancaron y coincidían con el ImageID escaneado. Las dos se
detuvieron en `fixture_port_not_loopback`, antes de SMTP/API, y sus recursos
propios fueron eliminados. Los logs muestran servicios escuchando dentro del
contenedor. El comportamiento coincide con la [limitación de publicación de
puertos en redes solo internas](https://github.com/moby/moby/discussions/53256).

Se corrige la fixture para reproducir la red host-loopback del laboratorio:
bridge no interna con `enable_ip_masquerade=false`, configuración verificada
por inspect, y la misma exigencia de publicación únicamente en 127.0.0.1. Se
añaden al recibo la versión de Docker y los bindings observados. Una prueba
offline rechaza redes host, internas sin publicación y bridge con NAT habilitado.
La aprobación remota de la corrección sigue pendiente; Compose conserva 1.31.1.

Regresión local del ajuste de red: 353 casos Python (352 aprobados/uno Linux
omitido), tres JS y 96 archivos sin errores de sintaxis. No se han relajado
las comprobaciones de loopback ni de igualdad con la imagen escaneada.
