# Fijación de imágenes del laboratorio — 19/10/2026

Estado local: MariaDB y DVWA fijados a los digests del inventario auditado del
18/10, disponibilidad e identidad linux/amd64 verificadas directamente en los
registros públicos. Regresión local aprobada; publicación, CI y escaneo de las
referencias fijadas pendientes. La VM y sus volúmenes no se han modificado.

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

La reversión de referencias a etiquetas no recupera datos de un volumen alterado.
El alcance cerrado será la fijación y validación remota del repositorio; la
aplicación a la VM, riesgos de infraestructura/dependencias, procedencia del CSRF
histórico, A-05 general y entrega final permanecen separados.
