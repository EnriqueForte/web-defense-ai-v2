# Instalación propia desde GitHub — Windows y Linux

Para usuarios nuevos, consulta [Inicio rápido](INICIO_RAPIDO.md): instalación
con `webdefense.py install` y arranque en una terminal con `webdefense.py start`.
Esta guía conserva las órdenes separadas y el procedimiento operativo avanzado.

Ensayo limpio local Windows del 11/10/2026 aprobado sobre una copia del código
actual sin entornos ni datos del mantenedor: [evidencia y límites](INSTALACION_LIMPIA_WINDOWS_2026_10_11.md).
Checkout e instalación nueva en Windows y Ubuntu 24.04 aprobados en GitHub
Actions el 12/10/2026: [evidencia CI y límites](VALIDACION_CI_2026_10_12.md).
Parrot 7.3 x86_64 en VMware pasó instalación, pruebas offline, build y lectura
con API directa/proxy HTTP200: [ensayo guiado del 12/10](VALIDACION_PARROT_2026_10_12.md).

Contrato actualizado el 10/10/2026: [Paso 1 Dependencias](DEPENDENCIAS_2026_10_10.md).
El instalador prepara pip/setuptools desde `requirements-bootstrap.txt` antes
de instalar `requirements.txt` con `constraints-py311.txt`. Validación Windows
aislada en `.p3`, 158 pines; `.p2/.venv` del mantenedor conservan el contrato
anterior y no deben actualizarse mientras sus servicios estén activos. `.p3`
no se activa automáticamente. Persisten avisos documentados y falta el escaneo
de imágenes; no se declara cierre de seguridad. La instalación Linux acreditada
en CI se limita a Ubuntu 24.04 x86_64.

Objetivo: clonar web-defense-ai V2 y usarlo en el entorno de cada persona.
El destino es EnriqueForte/web-defense-ai-v2; el código está publicado y el
checkout limpio pasó en CI. La versión final sigue pendiente; el ensayo guiado
Parrot acreditó instalación y lectura. No se cambió la visibilidad del
repositorio en esta entrega. Se conserva la licencia MIT de LICENSE.

## Entorno comprobado

Windows, PowerShell, Python 3.11, Node.js 24 o posterior y pnpm 11.19.0 según
frontend/package.json. Docker Desktop con contenedores Linux es necesario
solo para el laboratorio DVWA, no para pruebas aisladas o lectura de la consola.
El soporte Linux contempla Parrot OS x86_64 en VMware como caso de uso del usuario
y Ubuntu 24.04 x86_64 como entorno inicial de CI, con Python 3.11 y Docker Engine
con Compose v2 para el laboratorio. La instalación y pruebas offline pasaron en
Ubuntu CI y Parrot 7.3 en la VM del usuario; allí también pasó arranque/proxy Next.
El laboratorio Docker, ingesta y análisis real en esa VM siguen pendientes.
No se afirma soporte de todas las distribuciones Linux, ARM o macOS.
Ambos sistemas utilizan `constraints-py311.txt`; las instantáneas con nombre
Windows se mantienen como evidencia histórica. Los marcadores excluyen pywin32
en Linux; el resolutor puede añadir dependencias propias de esa plataforma.
En el runner Ubuntu se observó `uvloop==0.23.0` adicional; capturar el freeze
Linux y fijar esa dependencia sigue pendiente para reproducibilidad completa.

## Preparar una instalación nueva

### Parrot OS dentro de VMware y otras distribuciones

El instalador selecciona Linux por sistema operativo, sin exigir Ubuntu ni
usar apt, dnf o pacman. La disponibilidad de Python 3.11/venv, Node 24 y pnpm
11.19.0 depende de la distribución y versión. También importan arquitectura y
compatibilidad de las dependencias binarias. No se garantiza cualquier Linux
por compartir los mismos comandos. Ubuntu en CI no acredita Parrot, Debian,
Kali, Fedora, Arch o Alpine.

Parrot documenta su instalación en
[VMware](https://www.parrotsec.org/docs/virtualization/parrot-on-vmware/).
Para este proyecto instala y ejecuta Python, Next y, si usas DVWA, Docker Engine
con Compose v2 dentro de la VM. Usa el navegador de Parrot para abrir
http://127.0.0.1:3000: localhost corresponde a la VM, no al equipo anfitrión.
Los puertos siguen enlazados a loopback; no necesitan abrirse a la red para
este uso. Acceder desde el navegador del anfitrión requeriría un procedimiento
separado de acceso, que no se configura en esta entrega.

Clona en el disco local de la VM, por ejemplo dentro de tu directorio personal,
y crea allí sus entornos. Evita ejecutar la instalación sobre una carpeta
compartida de VMware: no se han validado allí bloqueos, permisos o sustituciones
atómicas. No copies .p2/node_modules de Windows ni cambies el Python del sistema.

Antes de instalar, anota la versión/arquitectura reales y comprueba herramientas:

```bash
cat /etc/os-release
uname -m
python3.11 --version
python3.11 -m venv --help
node --version
pnpm --version
```

Si falta una herramienta, prepararla según esa versión de Parrot; no asumir
que su `python3` predeterminado es 3.11 ni añadir repositorios Ubuntu a Parrot.
Después utiliza los comandos Linux de esta guía. La aceptación realizada en
Parrot 7.3/VMware incluye instalación nueva, pip check/pines, pruebas offline,
HTTP sintético, build Next y lectura desde el navegador de esa VM.
El laboratorio Docker se comprueba aparte, sin llamadas LLM rutinarias.

Después de que la versión esté publicada/accesible, desde PowerShell:

```powershell
git clone https://github.com/EnriqueForte/web-defense-ai-v2.git
Set-Location web-defense-ai-v2
py -3.11 -B scripts/setup_installation.py --frontend
py -3.11 -B scripts/setup_installation.py --install --frontend --init-env
.p2/Scripts/python.exe -B scripts/check_environment.py
```

Usar una ruta corta para el entorno ayuda con los recursos de LiteLLM en Windows.
`.p2` es un entorno que cada clonación crea; no se distribuye el del mantenedor.
No copiar entornos virtuales, `.env`, bases SQLite, logs o reportes de otra persona.
El primer comando solo presenta el plan. `--install` crea/reutiliza `.p2` e
instala dependencias; nunca borra un entorno existente. `--init-env` crea la
plantilla si falta y conserva un `.env` existente sin leerlo. No usar sudo para
este instalador. Se necesitan Python 3.11 con venv/pip, Node 24 y pnpm 11.19.0
disponibles previamente; no instala herramientas globales ni cambia el sistema.

Desde una terminal Bash Linux, después de disponer de esas herramientas:

```bash
git clone https://github.com/EnriqueForte/web-defense-ai-v2.git
cd web-defense-ai-v2
python3.11 -B scripts/setup_installation.py --frontend
python3.11 -B scripts/setup_installation.py --install --frontend --init-env
.p2/bin/python -B scripts/check_environment.py
.p2/bin/python -B scripts/check_baseline.py
.p2/bin/python -B scripts/check_local_http.py
```

No reutilizar `.p2` o `frontend/node_modules` entre Windows y Linux. El clon y
entorno Linux deben residir en su propio directorio local. Si faltan Python 3.11
o su módulo venv, instalarlos por el procedimiento de tu distribución antes de
continuar; `python3` no garantiza ser Python 3.11.

Con pnpm 11.19.0 disponible:

```powershell
Set-Location frontend
pnpm install --frozen-lockfile
pnpm run lint
pnpm run test:ui
Set-Location ..
.p2/Scripts/python.exe -B scripts/check_baseline.py
```

Estas comprobaciones no ejecutan el motor ni requieren una clave API. La
construcción del adaptador puede verificarse offline con
`scripts/check_llm_adapter.py`. Docker y llamadas LLM no son pruebas rutinarias.

## Configuración y primera lectura

```powershell
if (-not (Test-Path -LiteralPath .env)) {
    Copy-Item -LiteralPath .env.example -Destination .env
}
.p2/Scripts/python.exe -B scripts/local_runtime_profile.py --profile pilot --mode legacy
```

La plantilla mantiene modo legacy y análisis manual apagados; las notificaciones
quedan vacías por defecto. Cada persona configura su propio proveedor/clave en
la pantalla Configuración o en su `.env`, que no se publica. El análisis puede
enviar la muestra del log al proveedor seleccionado: usar datos propios o
anonimizados cuya transmisión esté autorizada. No hay cuentas centrales.

El comando anterior comprueba el perfil sin arrancar procesos. Si indica ready,
se puede iniciar únicamente la lectura de Flask:

```powershell
.p2/Scripts/python.exe -B scripts/local_runtime_profile.py --profile pilot --mode legacy --component flask --start
```

En otra terminal, desde frontend:

```powershell
pnpm run dev
```

Abrir http://127.0.0.1:3000. Una clonación nueva no contiene el piloto, logs,
informes o SQLite del mantenedor. Sin esas fuentes, la consola debe mostrar
su ausencia, no un informe inventado. Las rutas del perfil piloto se crean
localmente cuando se capture el laboratorio o se ejecute un trabajo.
No arrancar Flask o Next dos veces en el mismo puerto.

Flask admite localhost, 127.0.0.1 e IPv6 loopback. El proxy de Next en estos
puertos se conserva. Esta configuración no expone un dashboard a otros equipos.
El puerto API predeterminado es 5000; Next usa 3000.

## Laboratorio y análisis

Usar [el laboratorio aislado](LABORATORIO_DVWA_FASE_6.md), compose.lab.yaml y
scripts/start_dvwa_lab.ps1. docker-compose.yml es histórico: no es el arranque
recomendado para la clonación. Sus datos se conservan; no ejecutar limpiezas
o borrados de volúmenes como parte de la instalación.

Después de generar peticiones de laboratorio se puede capturar el log con
`.p2/Scripts/python.exe -B -m dashboard.services.dvwa_lab_capture`.
Actualizar la consola relee esa copia; no vuelve a capturar Docker por sí solo.

Un análisis real necesita proveedor configurado y consume su presupuesto.
La activación del flujo estructurado y la admisión manual son decisiones
separadas de la primera lectura; véanse [activación](ACTIVACION_LOCAL_A05.md)
y [coordinación](FASE_5_ANALISIS_COORDINADO.md). Los recibos de la instalación
del mantenedor no se incluyen ni constituyen pruebas del equipo del usuario.
El procedimiento de arranque habitual está preparado debajo; antes de la versión
final queda comprobarlo desde una clonación limpia del contenido final.

## Arranque habitual en ambos sistemas

Los comandos siguientes parten de la raíz del proyecto. En Windows utiliza
`.p2/Scripts/python.exe`; en Linux utiliza `.p2/bin/python`. No es necesario
activar el entorno virtual ni usar los scripts PowerShell del laboratorio.

En Linux, primera terminal para lectura:

```bash
.p2/bin/python -B scripts/local_runtime_profile.py --profile pilot --mode legacy --component flask
.p2/bin/python -B scripts/local_runtime_profile.py --profile pilot --mode legacy --component flask --start
```

En una segunda terminal, en ambos sistemas:

```text
cd frontend
pnpm run build
pnpm run start
```

La interfaz queda en http://127.0.0.1:3000 y Flask en http://127.0.0.1:5000.
`pnpm run dev` se conserva como alternativa de desarrollo. Cada comando se
mantiene en primer plano y se detiene con Ctrl+C; no se instala un servicio
systemd ni una tarea programada. El preflight bloquea puertos ocupados, trabajos
pendientes, entornos diferentes o bloqueos activos. No elude esas condiciones
matando otros procesos. Usa el mismo perfil y modo en Flask y worker.

Para utilizar el laboratorio en cualquiera de los sistemas:

```text
docker compose --file compose.lab.yaml up --detach
```

Linux usa Docker Engine/Compose v2; Windows puede usar Docker Desktop con
contenedores Linux. Después de generar tráfico autorizado, captura desde la
raíz usando el intérprete de tu sistema:

```bash
.p2/bin/python -B -m dashboard.services.dvwa_lab_capture
```

El perfil `pilot` lee esa copia en `.local-state/dvwa-lab/access.log`, escribe
informes en `.local-state/phase6-pilot/reports` y usa su SQLite separada. El nombre
se conserva por compatibilidad; estas rutas se crean en cada instalación.
El perfil `legacy` usa las rutas históricas y su origen Docker anterior.

Para admitir análisis manuales estructurados cuando decidas consumir tu proveedor,
detén primero la lectura Flask anterior con Ctrl+C y arranca estas dos terminales
(en Windows sustituye el intérprete como se indicó):

```bash
.p2/bin/python -B scripts/local_runtime_profile.py --profile pilot --mode structured --component flask --enable-manual --start
```

```bash
.p2/bin/python -B scripts/local_runtime_profile.py --profile pilot --mode structured --component worker --enable-manual --start
```

La opción admite solicitudes; no solicita un análisis por sí sola. El worker es
`--manual-only`, sin ciclos periódicos. Sin un primer informe válido se muestra
fuente ausente. Configura tu proveedor, captura datos y solicita el análisis en
la interfaz cuando aceptes la transmisión y coste. Las notificaciones siguen
desactivadas por el lanzador. Volver a lectura: detener ambos componentes con
Ctrl+C e iniciar Flask sin `--enable-manual`. Cambiar a legacy requiere que
ambos componentes utilicen `--mode legacy`; conserva los informes originales.

Para detener el laboratorio conservando sus volúmenes:

```text
docker compose --file compose.lab.yaml stop
```

## Verificación continua de plataformas

`.github/workflows/compatibility.yml` prepara instalación desde checkout,
pip check, comparación de pines, tests Python/JS, HTTP sintético, SDK offline y
build Next en Windows y Ubuntu 24.04. Se ejecuta al publicar cambios, en PR
o manualmente en GitHub. La [ejecución 38224024703](https://github.com/EnriqueForte/web-defense-ai-v2/actions/runs/38224024703)
del commit `96d190c` pasó en ambos sistemas. No contiene claves de proveedor,
llamadas reales o arranque Docker. Acredita instalación y pruebas en esos
runners; no acredita Parrot ni arranque/proxy Next en Linux.

## Cierre de distribución pendiente

- Freeze/pines Linux adicionales y auditorías; Windows/Ubuntu CI y el ensayo
  guiado de instalación/lectura Parrot aprobados dentro de sus respectivos alcances.
- Verificar en Parrot la nueva entrada simplificada, ya aprobada en Windows/
  Ubuntu CI; la preparación de requisitos globales sigue siendo un paso previo.
- Laboratorio Docker, ingesta y análisis real en la VM Parrot.
- Cierre de calidad/observación A-05 y diagnóstico del motor operativo.
- Procedimiento definitivo de arranque/análisis, conservación y recuperación.
- Completar auditoría de archivos/historial; la revisión acotada previa al push
  conserva su alcance documentado.
- Documentación final, versión y publicación solo al destino V2.

Los pendientes de esta lista no se presentan como completados por CI. Cada
persona configura sus credenciales dentro de su propia instalación.
