# Fijación de imágenes del laboratorio — 19/10/2026

Estado: publicado como `2d2f197`, CI Windows/Ubuntu y escaneo remoto verificados.
MariaDB y DVWA quedan fijados a los digests del inventario auditado del 18/10,
con identidad linux/amd64 contrastada en los registros públicos y el escaneo
del 19/10. La VM y sus volúmenes no se han modificado.

## Problema y cambio

MariaDB seguía declarada como `mariadb:10.11` y DVWA como
`ghcr.io/digininja/dvwa:b496a5d`. Una etiqueta puede resolver a otra imagen;
el inventario del 18/10 ya acreditó un cambio de digest de MariaDB respecto al
16/10. Mailpit estaba fijado por digest. Ahora los tres servicios del Compose
y el inventario del escáner usan referencias fijadas.

| Servicio | Referencia fijada |
| --- | --- |
| MariaDB | `mariadb:10.11@sha256:0d0945c57f75b3a3b9ebe71aedaaad005fa5305054e8fca3d2e42a8c92b43b5e` |
| DVWA | `ghcr.io/digininja/dvwa:b496a5d@sha256:ed35515e9111801e6e386a6fbb11165508cc7f72e0cb8da4dbb3df70182986c6` |
| Mailpit, conservado | `axllent/mailpit:v1.31.6@sha256:23fe39e81bde596a918000b3135c0f85dc8bb4c9ea6be274b051143f3e300387` |

No se escoge una versión nueva de MariaDB o DVWA. Se conserva la identidad de
las imágenes revisadas en el [inventario del 18/10](SEGURIDAD_RESIDUAL_2026_10_16.md),
run39120143668/artifact12133887424. La fijación aporta reproducibilidad; no
corrige por sí misma los avisos de esos paquetes ni acredita su ausencia.

El escáner exigía un digest resuelto válido, pero no lo comparaba con el digest
solicitado en una referencia fijada. Se reprodujo con una prueba sintética:
ArtifactName correcto y RepoDigests distinto pasaban. Ahora ese caso se rechaza;
el resumen conserva `scan_failed`, sin inventar cero vulnerabilidades.
`requested_digest_verified` vale true solo cuando se verificó un pin; en las
referencias históricas por etiqueta queda null, sin atribuirles esa propiedad.

## Verificación de registros e identidad

Se consultan Docker Hub y GHCR sin Docker ni credenciales privadas. Los tokens
anónimos de lectura de los registros se resuelven internamente y no se guardan
en el recibo. Se verifica SHA-256 de los bytes del manifiesto raíz, la selección
linux/amd64 y el digest de configuración contra los ImageID del escaneo del 18/10.

MariaDB conserva ImageID `sha256:4e667183d5236dbbecf88167a0f1f49dc0c116aa46990309e920e663e2fdc348`;
DVWA, `sha256:7c65cc0145a5c4d3e8fcd226b37c46df6d041d76eaa9f83e7eb067beb5f89e40`.
Ambas etiquetas todavía apuntaban a esos mismos digests al consultar el 19/10;
se registra esa observación temporal sin convertir la etiqueta en inmutable.
Los digests raíz pueden identificar índices de varias plataformas; solo se
verifica linux/amd64, sin ampliar soporte a otras arquitecturas.
Se conservan también los bytes originales de los cuatro manifiestos raíz/amd64;
sus hashes se volvieron a comprobar desde los recibos locales, sin depender del
formato de una copia JSON reindentada.

Los upstream mantienen las imágenes y configuración de laboratorio en
[DVWA Compose](https://github.com/digininja/DVWA/blob/master/compose.yml) y
[manifiesto oficial MariaDB](https://github.com/docker-library/official-images/blob/master/library/mariadb).
La elección concreta de este cambio procede del inventario auditado del proyecto,
no de asumir que una etiqueta más reciente elimina los hallazgos.

## Validación local

- Regresión reproducida antes del arreglo: el nuevo rechazo de digest incorrecto
  fallaba porque el escáner lo aceptaba.
- Nueve pruebas del escáner aprobadas, incluidas cuatro nuevas: paridad de los
  tres pins, rechazo de otro digest, conservación de fallo sin métricas falsas y
  separación entre etiqueta histórica y pin verificado.
- 358 casos Python: 357 aprobados y un caso Linux omitido en Windows `.p4`.
- Tres contratos JavaScript y 96 archivos sin errores de sintaxis aprobados.
- No cambian las seis entradas del inventario remoto ni la comparación histórica
  Mailpit; las referencias legacy conservan su alcance de observación por etiqueta.

El [registro JSON](FIJACION_IMAGENES_LAB_2026_10_19.json) conserva los digests,
manifiestos seleccionados, evidencia de procedencia y resultados locales.
Recibos y manifiestos completos en `.local-state/image-pins-20261019/`, ignorado.

## Publicación y verificación remota

Código `2d2f197663da43c25fd94cc7315bc63388f04ae9`,
[CI 39229681306/attempt1](https://github.com/EnriqueForte/web-defense-ai-v2/actions/runs/39229681306)
Windows/Ubuntu completed/success. Se revisaron estados, pasos y logs finales,
con las cuatro pruebas nuevas aprobadas en ambos sistemas:

- Ubuntu 358 pruebas Python; Windows 357 aprobadas y una Linux omitida.
- Tres contratos JavaScript, 96 archivos sin errores de sintaxis, HTTP sintético
  y 27 escenarios SDK offline; lint, tipos y 17 grupos de regresión UI aprobados.
- Nueve E2E por OS: Windows 9,3 s y Ubuntu 10,7 s.
- API directa/proxy 200, ejecutor offline y puertos libres al cerrar.
- Inventarios completos 12176378240 Windows y 12176875612 Ubuntu: 172 paquetes,
  cero diferencias/adicionales y versiones/metadatos/hashes de freeze iguales
  a los recibos anteriores. No se atribuyen esos hashes a la VM.
- Resúmenes A-05 12175908253 Windows y 12176202901 Ubuntu: 13 casos y siete
  controles; métricas/checks/hashes de publicación iguales al recibo local
  `20261015T185242433279Z`, salvo UUID de generación. Estos resúmenes no incluyen
  los bytes completos de informes remotos ni acreditan calidad semántica del LLM.

[Escaneo 39229681189/attempt1](https://github.com/EnriqueForte/web-defense-ai-v2/actions/runs/39229681189)
completed/success; artefacto 12175678051 descargado y contrastado con los seis
informes completos. Trivy 0.75.0, DB v2 UpdatedAt 19/10/2026 07:19:54 UTC,
descargada 09:23:39 y captura 09:24:06 UTC. Los tres pins se verifican y sus
ImageID coinciden con los auditados; las tres referencias legacy conservan null.

| Referencia | Entradas | Críticas | Altas | Desconocidas |
| --- | ---: | ---: | ---: | ---: |
| MariaDB fijado | 102 | 1 | 24 | 1 |
| DVWA fijado | 4011 | 16 | 276 | 357 |
| Mailpit fijado | 1 | 0 | 0 | 1 |
| MySQL legacy | 266 | 1 | 102 | 1 |
| DVWA legacy | 1575 | 254 | 551 | 12 |
| Python legacy | 175 | 0 | 46 | 3 |

Con el mismo ImageID DVWA del 18/10, el informe del 19/10 añade 347 entradas
Debian UNKNOWN/347 IDs nuevos, sin retirar IDs anteriores: total 3664 -> 4011.
El escáner informa versión corregida para 302 de esas entradas. Se conserva
todo el detalle; son hallazgos de paquetes, no ataques confirmados o correcciones
aplicadas. La diferencia refleja nueva información del escáner sobre los mismos
bytes y no se presenta como un cambio del contenido provocado por la fijación.

Queda verificada la fijación del repositorio y el rechazo de digest incorrecto.
El commit posterior solo publica estas actas con `[skip ci]`; el código validado
permanece en `2d2f197`. Las revisiones de publicación conservan los hallazgos de
hashes públicos y el CSRF histórico de procedencia no acreditada; no se suprimen.

## Aplicación y límites

Esta entrega no ejecuta Docker, análisis LLM ni notificaciones y no lee `.env`.
No consulta imágenes instaladas en Parrot ni sustituye contenedores o volúmenes.
La equivalencia con un inventario de registro no demuestra que el contenedor
actual de la VM tenga esos bytes ni que su base existente pueda migrarse sin
comprobación. El escaneo remoto posterior conservará todos sus avisos.

Antes de aplicar el Compose en una instalación existente, conservar una copia
verificada de la base y un plan de recuperación. El respaldo de aplicación no
incluye ese volumen Docker. No usar `down --volumes` para actualizar referencias,
activar `MARIADB_AUTO_UPGRADE` o ejecutar un reset de DVWA como parte de este cambio.
La [documentación MariaDB](https://mariadb.com/docs/server/server-management/automated-mariadb-deployment-and-administration/docker-and-mariadb/mariadb-server-docker-official-image-environment-variables)
distingue la inicialización de una base nueva del tratamiento de un directorio
ya existente; no se acredita aquí una migración viva.

Las futuras correcciones de imagen requieren revisar otro digest y actualizar
el pin de forma expresa: una etiqueta que cambie no actualizará estas referencias.
La reversión de referencias a etiquetas no recupera datos de un volumen alterado.
El alcance cerrado es la fijación y validación remota del repositorio; la
aplicación a la VM, riesgos de infraestructura/dependencias, procedencia del CSRF
histórico, A-05 general y entrega final permanecen separados.
