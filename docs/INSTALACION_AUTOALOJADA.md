# Instalación propia desde GitHub — guía preparatoria

Objetivo: clonar web-defense-ai V2 y usarlo en el entorno de cada persona.
El destino es EnriqueForte/web-defense-ai-v2; la publicación final y el ensayo
desde una clonación limpia siguen pendientes. No se cambió la visibilidad del
repositorio en esta entrega. Se conserva la licencia MIT de LICENSE.

## Entorno comprobado

Windows, PowerShell, Python 3.11, Node.js 24 o posterior y pnpm 11.19.0 según
frontend/package.json. Docker Desktop con contenedores Linux es necesario
solo para el laboratorio DVWA, no para pruebas aisladas o lectura de la consola.
Los pines Python completos están validados en Windows/Python 3.11; no se afirma
compatibilidad probada con otras plataformas ni otras versiones de Python.

## Preparar una instalación nueva

Después de que la versión esté publicada/accesible, desde PowerShell:

```powershell
git clone https://github.com/EnriqueForte/web-defense-ai-v2.git
Set-Location web-defense-ai-v2
py -3.11 -m venv .p2
.p2/Scripts/python.exe -m pip install -r requirements.txt -c constraints-windows-py311-delivery2.txt
.p2/Scripts/python.exe -B scripts/check_environment.py
```

Usar una ruta corta para el entorno ayuda con los recursos de LiteLLM en Windows.
`.p2` es un entorno que cada clonación crea; no se distribuye el del mantenedor.
No copiar entornos virtuales, `.env`, bases SQLite, logs o reportes de otra persona.

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
Antes de la versión final queda preparar/verificar el arranque habitual del
análisis desde una clonación limpia, con defaults y rutas coherentes.

## Cierre de distribución pendiente

- Ensayo de clonación/instalación limpia del contenido final, build final y auditorías.
- Cierre de calidad/observación A-05 y diagnóstico del motor operativo.
- Procedimiento definitivo de arranque/análisis, conservación y recuperación.
- Revisión de archivos e historial a publicar para excluir secretos/datos locales.
- Documentación final, versión y publicación solo al destino V2.

La guía no declara ya completadas esas verificaciones ni solicita acceso a
credenciales de quien clone el proyecto.
