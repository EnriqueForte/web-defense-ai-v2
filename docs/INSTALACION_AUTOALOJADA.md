# Instalación propia desde GitHub — Windows y Linux

Para usuarios nuevos, consulta [Inicio rápido](INICIO_RAPIDO.md): instalación
con `webdefense.py install` y arranque en una terminal con `webdefense.py start`.
Esta guía conserva las órdenes separadas y el procedimiento operativo avanzado.

Revisión vigente: **20/10/2026**. El [resumen de estado](ESTADO_FINAL_2026_10_12.md)
reúne pruebas y pendientes; las actas fechadas conservan su alcance histórico.
El código está publicado en EnriqueForte/web-defense-ai-v2 con licencia MIT.
La formalización de la versión final sigue pendiente.

El instalador actual crea o reutiliza `.p2`, prepara pip/setuptools desde
`requirements-bootstrap.txt` y aplica `requirements.txt` con `constraints-py311.txt`:
contrato de 172 paquetes por plataforma. Las rutas `.p3/.p4/.venv` de actas
anteriores identifican entornos de pruebas del mantenedor, no requisitos para
una instalación nueva.

| Entorno | Evidencia disponible |
| --- | --- |
| Windows y Ubuntu 24.04 x86_64 | Instalación nueva, build, API/proxy, regresión y cierre aprobados en CI39239742802, código `ca2f6af`. [Acta y artefactos completos](EVALUACION_GRUPOS_A05_2026_10_19.md). |
| Parrot 7.3 x86_64/VMware | Instalación/lectura guiadas, inventario 172/0/0 y arranque/cierre comprobados; muestra DVWA XSS/fuerza bruta aceptada el 15/10. [Instalación](VALIDACION_PARROT_2026_10_12.md) y [análisis guiado](INCIDENCIA_GROQ_413_2026_10_15.md). |
| VM con pins posteriores | Actualización y recuperación del volumen Docker todavía no acreditadas; requieren preparación separada. |

Las [auditorías de paquetes del 18/10](REVISION_DEPENDENCIAS_SECRETOS_2026_10_18.md)
y el [escaneo de imágenes del 19/10](FIJACION_IMAGENES_LAB_2026_10_19.md) sí se
realizaron y conservan riesgos. No se declara cierre global de seguridad ni
aceptación semántica general del motor; véase la [matriz A-05](MATRIZ_ACEPTACION_A05_2026_10_20.md).

La [revisión C3 del20/10](TRATAMIENTO_RIESGOS_C3_2026_10_20.md) añade un parche
local aiohttp3.14.4/yarl1.25.1, probado en Windows `.p4`. La CI del contrato
nuevo está pendiente; no se atribuye a los runners o a Parrot una actualización
que no se ha ejecutado allí.

## Entorno comprobado

Windows, PowerShell, Python 3.11, Node.js 24 o posterior y pnpm 11.19.0 según
frontend/package.json. Docker Desktop con contenedores Linux es necesario
solo para el laboratorio DVWA, no para pruebas aisladas o lectura de la consola.
El soporte Linux contempla Parrot OS x86_64 en VMware como caso de uso del usuario
y Ubuntu 24.04 x86_64 como entorno inicial de CI, con Python 3.11 y Docker Engine
con Compose v2 para el laboratorio. La instalación y pruebas offline pasaron en
Ubuntu CI y Parrot 7.3 en la VM del usuario; allí también pasó arranque/proxy Next.
El recorrido Docker/ingesta/análisis pasó en esa VM para la muestra guiada del
15/10; eso no acredita aplicar después los nuevos pins o restaurar su volumen.
No se afirma soporte de todas las distribuciones Linux, ARM o macOS.
Ambos sistemas utilizan `constraints-py311.txt`; las instantáneas con nombre
Windows se mantienen como evidencia histórica. Los marcadores excluyen pywin32
en Linux; `uvloop==0.23.0` queda fijado solo para Linux desde el 12/10.
La instalación comprueba también paquetes adicionales con `--strict`.
El [contrato Linux](CONTRATO_LINUX_2026_10_12.md) conserva la etapa inicial de 158
distribuciones. La [migración posterior](MIGRACION_CREWAI_2026_10_12.md) y la CI
actual verifican 172/0/0 en ambos OS. El inventario de Parrot se acreditó por
capturas; no se recibieron sus freezes ni hashes. Los bytes de CI son evidencia
separada y no se atribuyen a esa VM.

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

### Instalación manual alternativa

Para el recorrido habitual usa `webdefense.py install`, como indica el inicio
rápido. Las siguientes órdenes permiten inspeccionar por separado la instalación.
Con acceso al repositorio, desde PowerShell:

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

### Comprobaciones opcionales de desarrollo

Con pnpm 11.19.0 disponible, estas pruebas pueden ejecutarse por separado.
No son pasos necesarios en cada arranque; la instalación ya prepara el frontend:

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

El recorrido habitual es `python3 webdefense.py start` (Windows: `py`), que
mantiene Flask y Next juntos. Para leer informes structured añade `--mode structured`.
No arranques además los componentes manuales siguientes mientras ese lanzador
esté activo.

Para separar componentes, después de detener el lanzador con Ctrl+C, desde
PowerShell en la raíz:

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

En otra terminal, desde frontend, con el build preparado por la instalación:

```powershell
pnpm run start
```

`pnpm run dev` es una alternativa de desarrollo. Para los comandos Python de
esta sección en Linux sustituye `.p2/Scripts/python.exe` por `.p2/bin/python`.

Abrir http://127.0.0.1:3000. Una clonación nueva no contiene el piloto, logs,
informes o SQLite del mantenedor. Sin esas fuentes, la consola debe mostrar
su ausencia, no un informe inventado. Las rutas del perfil piloto se crean
localmente cuando se capture el laboratorio o se ejecute un trabajo.
No arrancar Flask o Next dos veces en el mismo puerto.

Flask admite localhost, 127.0.0.1 e IPv6 loopback. El proxy de Next en estos
puertos se conserva. Esta configuración no expone un dashboard a otros equipos.
El puerto API predeterminado es 5000; Next usa 3000.

## Laboratorio y análisis

Usar [el laboratorio aislado](LABORATORIO_DVWA_FASE_6.md) y `compose.lab.yaml`.
`scripts/start_dvwa_lab.ps1` es la utilidad PowerShell; más abajo figura la orden
Compose para ambos sistemas. `docker-compose.yml` es legacy, con exposición
diferente, y no es el arranque recomendado.

Antes de iniciar un laboratorio existente con el Compose actualizado, conservar
una copia verificada de su base y un plan de recuperación. Los pins nuevos
pueden recrear DVWA/MariaDB. Mailpit no tiene buzón persistente: exportar los
mensajes necesarios antes de recrearlo. El respaldo de aplicación no cubre esos
datos. No usar `down --volumes`, reset o actualización automática para aplicar cambios.

Después de generar peticiones de laboratorio se puede capturar el log con
`.p2/Scripts/python.exe -B -m dashboard.services.dvwa_lab_capture`.
Actualizar la consola relee esa copia; no vuelve a capturar Docker por sí solo.

Un análisis real necesita proveedor configurado y consume su presupuesto.
La activación del flujo estructurado y la admisión manual son decisiones
separadas de la primera lectura; véanse [activación](ACTIVACION_LOCAL_A05.md)
y [coordinación](FASE_5_ANALISIS_COORDINADO.md). Los recibos de la instalación
del mantenedor no se incluyen ni constituyen pruebas del equipo del usuario.
El arranque de lectura y los contratos están comprobados en CI para el código
enlazado al principio. Las llamadas reales y el recorrido de una VM concreta
tienen evidencia separada; no se atribuyen a las pruebas offline.

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

### Pasar de lectura a análisis manual

Configura el proveedor y confirma que la copia de log contiene los datos que
quieres analizar. Usa el mismo usuario y permisos de captura Docker; no arranques
el motor como root para resolver permisos. Si Node se instaló con nvm, carga
su entorno en cada terminal que vaya a iniciar Next.

Espera a que termine cualquier análisis activo antes de cambiar perfiles.
Detén la lectura anterior con Ctrl+C. Si usabas `webdefense.py start`, ese cierre
detiene tanto Flask como Next, por lo que necesitarás las tres terminales de abajo.
Si Next ya se mantiene abierto por separado, conserva esa instancia y omite la tercera.

Primera terminal desde la raíz: Flask con solicitudes manuales habilitadas
(en Windows sustituye el intérprete como se indicó):

```bash
.p2/bin/python -B scripts/local_runtime_profile.py --profile pilot --mode structured --component flask --enable-manual --start
```

Segunda terminal desde la raíz: worker del mismo perfil y modo:

```bash
.p2/bin/python -B scripts/local_runtime_profile.py --profile pilot --mode structured --component worker --enable-manual --start
```

Tercera terminal, si Next no está activo, desde la raíz:

```text
cd frontend
pnpm run start
```

La opción admite solicitudes; no solicita un análisis por sí sola. El worker es
`--manual-only`, sin ciclos periódicos. Sin un primer informe válido se muestra
fuente ausente. Configura tu proveedor, captura datos y solicita el análisis en
la interfaz cuando aceptes la transmisión y coste. Las notificaciones siguen
desactivadas por el perfil. Un fallo debe revisarse en el trabajo y sus recibos
antes de solicitar otro; no se elimina el último informe válido.

Para volver al lanzador de lectura, espera al fin del trabajo activo y detén
worker, Flask y Next por separado con Ctrl+C. Desde la raíz ejecuta
`python3 webdefense.py start --mode structured` (Windows: `py`). Así se conserva
la lectura de esos informes y se deshabilita la admisión manual. Si mantienes
componentes separados, basta detener worker/Flask y reiniciar Flask sin
`--enable-manual`, conservando Next. Cambiar a legacy requiere usar ese modo en
los componentes implicados; conserva los informes originales.

Para detener el laboratorio conservando sus volúmenes:

```text
docker compose --file compose.lab.yaml stop
```

## Actualizar una instalación existente

1. Espera a que no haya trabajos activos, detén worker y consola y conserva
   datos según [operación y recuperación](OPERACION_RECUPERACION_2026_10_14.md).
   Si aplicarás cambios de laboratorio, prepara además su copia DB y exportación
   de correo; el respaldo de aplicación no las sustituye.
2. Revisa `git status` y conserva/resuelve cambios locales antes de actualizar.
   Comprueba que `origin` sea el repositorio V2. No uses reset o limpieza de datos
   para conseguir un árbol limpio.
3. Actualiza con `git pull --ff-only` y revisa las notas de los cambios recibidos.
4. Ejecuta `python3 webdefense.py install` (Windows: `py`) si cambió el código
   instalado: prepara el contrato y el build sin sustituir `.env` existente.
5. Inicia lectura con el modo correspondiente y comprueba las fuentes. Aplicar
   los cambios de Compose al laboratorio es un paso posterior y separado,
   sujeto al respaldo previo. Actualizar el repo no recrea contenedores por sí solo.

## Verificación continua de plataformas

`.github/workflows/compatibility.yml` prepara instalación desde checkout,
pip check, comparación de pines, tests Python/JS, HTTP sintético, SDK offline y
build Next en Windows y Ubuntu 24.04. Se ejecuta al publicar cambios, en PR
o manualmente en GitHub, salvo cambios documentales con CI omitida explícitamente.
La [ejecución 39239742802](https://github.com/EnriqueForte/web-defense-ai-v2/actions/runs/39239742802)
del código `ca2f6af` pasó en ambos OS, incluidos E2E Chromium y smoke API/proxy
en Linux y Windows. No contiene llamadas reales de proveedor o arranque Docker
operativo. Parrot conserva su evidencia guiada independiente. Solo cambiar
documentación no exige repetir la CI de ese código.

## Cierre de distribución pendiente

- Conservar los avisos y reevaluar ante cambios de exposición los riesgos de
  [dependencias/historial](TRATAMIENTO_RIESGOS_C3_2026_10_20.md) e
  [imágenes](FIJACION_IMAGENES_LAB_2026_10_19.md); no se declaran eliminados.
- C3 tiene tratamiento residual aceptado el20/10 para uso local aislado. Los
  riesgos siguen documentados; no se reabre su aceptación como condición
  indefinida, pero ampliar exposición/capacidades requiere revisión propia.
- Preparar notas, revisión del contenido final y versión en V2 vinculada a su
  código probado; el parche local de dependencias requiere CI Windows/Ubuntu
  nueva antes de entrega. La documentación actualizada no equivale a una release.
- Si se incluye la actualización de Parrot, acreditar por separado conservación
  y recuperación de su laboratorio con los pins actuales.

Instalación/lectura, muestra guiada XSS/fuerza bruta y restauración aislada de
aplicación ya tienen evidencia en sus alcances. A-05 se aceptó el 20/10 para la
primera versión local, con límites y comparación legacy expresamente diferida:
[decisión y evidencias](REVISION_ACEPTACION_A05_2026_10_20.md).
No vuelven a ser pendientes por
figurar en actas antiguas. El [análisis de cierre](ANALISIS_CIERRE_2026_10_20.md)
delimita lo que sigue abierto. Cada persona configura sus credenciales en su instalación.
