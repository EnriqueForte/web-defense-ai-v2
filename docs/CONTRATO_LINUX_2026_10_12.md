# Contrato e inventario Python Linux — 12/10/2026

## Problema y cambio

La instalación Ubuntu CI anterior resolvía `uvloop==0.23.0` además de los 157
pines del contrato derivado de Windows. El comprobador revisaba los pines
esperados, pero no detectaba distribuciones adicionales. El log de instalación
no era una instantánea completa del entorno.

Se añade `uvloop==0.23.0; sys_platform == "linux"` a requisitos y constraints.
Los [marcadores de dependencias](https://packaging.python.org/en/latest/specifications/dependency-specifiers/)
seleccionan la plataforma; el lector admite explícitamente Windows y Linux.
Los 158 pines Windows conservan sus versiones; Linux pasa a 158 incluyendo uvloop.
Las instantáneas Windows históricas se conservan.

La instalación ejecuta ahora `check_environment.py --strict`: compara versiones,
ausencias y paquetes adicionales. Un paquete fuera del contrato detiene la
instalación; no se elimina automáticamente. La comprobación de arranque mantiene
la comparación de versiones necesarias y no elimina distribuciones del usuario.

`snapshot_environment.py` compara todos los metadatos instalados, el contrato y
`pip freeze --all`. [pip documenta](https://pip.pypa.io/en/stable/cli/pip_freeze/)
que `--all` incluye herramientas de instalación; freeze informa lo instalado,
no calcula un lockfile. La captura rechaza URLs, paquetes duplicados y cualquier
divergencia antes de escribir archivos. Exporta solo nombres/versiones, plataforma,
versión Python, conteos y hash del freeze; no lee `.env` ni importa el motor.

Los archivos locales son `.local-state/environment/requirements-freeze.txt` y
`environment.json`. La CI los conserva como artefactos por sistema durante 30 días,
con rutas de archivo explícitas. No se suben logs, configuración o bases.
No es un lockfile de artefactos binarios con hashes ni acredita todas las arquitecturas.

## Verificación local y estado remoto

- Windows `.p3`: 158 instalados/fijados, cero diferencias y cero adicionales.
- Freeze completo coincide con metadatos y contrato; hash y archivos verificados.
- 295 casos Python: 294 aprobados y caso específico Linux omitido; tres JS aprobados.
- 80 archivos de sintaxis y diff check aprobados.
- Pruebas nuevas: marcadores por plataforma, paquetes adicionales, bootstrap completo,
  faltantes/deriva/duplicados, rechazo de URLs sin salida sensible y ruta de exportación.

Recibos locales `.local-state/linux-contract-20261012/`. La comprobación final
del inventario en la VM Parrot sigue pendiente; resultados remotos abajo.
No se han instalado paquetes ni arrancado servicios operativos Windows por esta
entrega. Sin proveedor, análisis real, Docker o notificaciones.

## Instalación limpia e inventarios CI verificados

Commit de código `8cd7310366af66066949ea0a8a03b4ae6505cef9`,
[run38239653979](https://github.com/EnriqueForte/web-defense-ai-v2/actions/runs/38239653979),
attempt1: Windows-latest y Ubuntu24.04 completaron con success. Estados, logs
finales y los dos artefactos completos fueron descargados y comprobados.

| Plataforma | Python | Distribuciones instaladas/fijadas | Diferencias/adicionales | Exclusiva |
| --- | --- | --- | --- | --- |
| Windows-latest | 3.11.9 | 158/158 | 0/0 | pywin32 311 |
| Ubuntu 24.04 | 3.11.17 | 158/158 | 0/0 | uvloop 0.23.0 |

Los freezes coinciden exactamente con metadatos JSON y contrato aplicable;
incluyen pip/setuptools. Los hashes SHA-256 se comprobaron sobre los bytes:

- Linux: `3a728a13fa2a7914c858081fbb0759aa96bbd995545b2e10d2038a37c6965ec6`.
- Windows: `269cc0f83b7ed3e4bf2687527cebcef82be4a31d07b89fb973c1ae9e92b2157c`.

La [instantánea Linux](../constraints-linux-py311-20261012.txt) conserva los
bytes del freeze verificado, con regla Git sin conversión de finales de línea.
Es evidencia Ubuntu, no sustituye al contrato común ni se aplica en Windows.
Artefactos11741866982Linux/11742906549Windows: copias en
`.local-state/linux-contract-20261012/artifacts-38239653979/`, junto con resumen
de verificación. Los artefactos remotos tienen retención de 30 días.

Ambos runners completaron instalación/build, pip check/contrato estricto,
snapshot, 80 archivos sintaxis, tres JS, HTTP sintético, 25 SDK offline,
lint/tipos/15 UI y smoke API directa/proxy200,ejecutoroffline,cierrepuertoslibres.
Ubuntu aprobó295Python; Windows294 y omitió el caso Linux específico. La captura
y pin adicional Linux quedan completados para Ubuntu; verificar el mismo
inventario en Parrot sigue pendiente. La actualización siguiente guarda recibos
y documentación con `[skip ci]`; no se atribuye otra CI a ese commit.

## Comprobación en Parrot después de publicar

Desde el clon y con la consola detenida:

```bash
git pull --ff-only
.p2/bin/python -m pip check
.p2/bin/python -B scripts/check_environment.py --strict
.p2/bin/python -B scripts/snapshot_environment.py
```

La comprobación esperada es 158 pines, cero diferencias y cero adicionales.
Si uvloop difiere o falta, revisar primero la salida antes de modificar el entorno.
El freeze obtenido de Ubuntu no se atribuye automáticamente a la VM del usuario.
