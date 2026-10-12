# Primera instalación y arranque

Instala en el disco local de Windows o Linux. Cada instalación conserva sus
propios datos y configuración. Los comandos siguientes parten de la carpeta
del repositorio clonado.

## Requisitos iniciales

- Git para clonar el repositorio.
- Python 3.11 con `venv` y `ensurepip`.
- Node.js 24 o posterior.
- pnpm 11.19.0: con Node disponible, `npm install --global pnpm@11.19.0`.

El instalador comprueba versiones antes de preparar el proyecto. Por ahora las
herramientas anteriores se instalan por separado; no modifica el Python del
sistema ni instala gestores globales automáticamente. En Parrot se comprobó
Python 3.11 mediante [uv](https://docs.astral.sh/uv/guides/install-python/) y
Node 24 mediante [nvm](https://github.com/nvm-sh/nvm#installing-and-updating).
En Windows puede utilizarse el [instalador de Python](https://www.python.org/downloads/windows/)
y el [de Node.js](https://nodejs.org/en/download).

## Instalar una vez

```bash
git clone https://github.com/EnriqueForte/web-defense-ai-v2.git
cd web-defense-ai-v2
python3 webdefense.py install
```

En Windows usa `py webdefense.py install`. La entrada busca Python 3.11 aunque
el comando inicial utilice otra versión reciente de Python. En Linux, si lo
instalaste en tu usuario, asegúrate de que `python3.11` esté en el PATH.
Si el repositorio solicita autenticación, utiliza tu acceso de GitHub.

La instalación crea o reutiliza `.p2`, instala los paquetes del contrato,
comprueba sus versiones y dependencias, instala el frontend con lockfile y
compila Next. Crea `.env` desde la plantilla cuando falta y conserva uno existente.
Ejecuta sin sudo; detén las instancias anteriores antes de instalar o actualizar.
Los puertos ocupados, bloqueos de operación y trabajos activos impiden la
instalación simplificada. Un error detiene el recorrido; no elimina instalaciones
ni datos para intentar recuperarse. Consulta la última etapa fallida.

## Iniciar habitualmente

```bash
python3 webdefense.py start
```

En Windows: `py webdefense.py start`. No necesitas activar el entorno virtual,
recompilar cada vez ni abrir una segunda terminal. El comando usa `.p2` y arranca
Flask y Next en modo producción. Cuando aparece «Consola lista», abre:

**http://127.0.0.1:3000**

En VMware abre esa dirección desde el navegador de la VM. Mantén la terminal
abierta. **Ctrl+C detiene los dos servicios creados por este comando.**
El puerto 5000 conserva la interfaz Flask; la interfaz nueva está en 3000.

El arranque comprueba contrato Python, build, proxy, puertos y bloqueos. No adopta
ni detiene una instancia anterior. Si uno de sus servicios termina, cierra el otro
y devuelve un error. Los logs están en `.local-state/launcher/<ejecución>/`;
consúltalos localmente si el inicio no llega a confirmar la conexión.

Comprobación sin arrancar servicios:

```bash
python3 webdefense.py check
```

Es una comprobación previa al inicio: un puerto ocupado por una consola que ya
está abierta se indicará como impedimento para iniciar otra instancia.

## Configuración y análisis

La primera lectura puede mostrar «Fuentes incompletas»: el clon no incluye logs
ni informes del mantenedor. Configura tu proveedor en Configuración y prepara tu
fuente de logs siguiendo la [guía completa](INSTALACION_AUTOALOJADA.md).
Docker solo es requisito adicional para el laboratorio DVWA de esa guía.

Este lanzador inicia la consola de lectura con perfil pilot, solicitudes manuales
deshabilitadas y destinos de notificación vacíos; no arranca el worker. El arranque
operativo del análisis sigue el procedimiento explícito de la guía completa.
El modo de informes predeterminado es legacy; para leer publicaciones structured:
`python3 webdefense.py start --mode structured`. Esto no habilita análisis.

Las pruebas completas Python/SDK/UI son verificaciones de desarrollo y CI;
no forman parte de cada arranque del usuario.

Si necesitas verificar también que no hay paquetes adicionales en `.p2`,
en Linux ejecuta `.p2/bin/python -B scripts/check_environment.py --strict`.
En Windows utiliza `.p2/Scripts/python.exe`. La [guía del contrato Linux](CONTRATO_LINUX_2026_10_12.md)
explica cómo guardar el inventario completo para diagnosticar una instalación.

## Alcance comprobado

El nuevo instalador y lanzador se ensayaron en una copia aislada de Windows,
incluido build, API directa/proxy y cierre con puertos libres. Después pasó el
mismo recorrido desde una instalación nueva en [Windows y Ubuntu CI](https://github.com/EnriqueForte/web-defense-ai-v2/actions/runs/38234970879),
para el commit `c82441c`, ya publicado. Después, el usuario confirmó instalación,
arranque unificado y navegación en [Parrot](VALIDACION_PARROT_2026_10_12.md).
El cierre dejó los puertos libres tras una espera; el comprobador indicó ocupado
antes de ella. El [ajuste posterior de puertos](CORRECCION_PUERTOS_2026_10_12.md)
del commit `2a73ff0` pasó después en [Windows y Ubuntu CI](https://github.com/EnriqueForte/web-defense-ai-v2/actions/runs/38237671713),
incluida la regresión de conexiones residuales y reinicio inmediato en Linux.
El usuario confirmó después el recorrido guiado en Parrot: comprobación preparada,
arranque listo, cierre por Ctrl+C y nueva comprobación preparada sin aviso de puerto.
El registro Parrot conserva los límites de las capturas y de la confirmación.
