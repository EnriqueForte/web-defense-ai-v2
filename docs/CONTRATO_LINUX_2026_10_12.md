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

Recibos locales `.local-state/linux-contract-20261012/`. Instalación Ubuntu con
el nuevo contrato, artefacto completo Linux y comprobación final Parrot pendientes.
No se han instalado paquetes ni arrancado servicios operativos Windows por esta
entrega. Sin proveedor, análisis real, Docker o notificaciones.

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
