# Laboratorio DVWA aislado para la Fase 6

Este Compose prepara una instancia local para el piloto de web-defense-ai V2.
No ejecuta Flask, Next.js, CrewAI, el pipeline ni las notificaciones. Las
imágenes solo se descargan al iniciar explícitamente el laboratorio.

## Límites del entorno

- DVWA y Mailpit solo publican puertos en `127.0.0.1`: DVWA en `4280`, la
  bandeja de correo en `8025` y SMTP de prueba en `1025`.
- DVWA y MySQL comparten una red Docker interna; MySQL no publica ningún
  puerto. DVWA y Mailpit se conectan además a una red puente para publicar los
  puertos de loopback; la traducción de salida a Internet está desactivada en
  esa red.
- Solo la base tiene un volumen persistente propio. Apache escribe accesos a
  la salida del contenedor, que Docker rota; no se monta el repositorio ni se
  conecta con el Compose heredado.
- La publicación de puertos necesita una red puente adicional: Docker Engine
  29 puede aceptar `ports` en una red exclusivamente interna sin crear el
  mapeo efectivo del puerto. La red puente conserva la publicación local y
  desactiva masquerade para evitar la salida NAT habitual.
- El correo se captura en Mailpit; no se entrega. Telegram debe permanecer sin
  configurar durante estas pruebas.
- DVWA es intencionalmente vulnerable. Úsala solo desde el mismo equipo y con
  tráfico de demostración autorizado.
- Las credenciales de la base son conocidas y solo sirven dentro de la red
  aislada; no reutilizarlas fuera del laboratorio.

## Inicio y detención

Desde PowerShell, en la raíz del proyecto:

```powershell
.\scripts\start_dvwa_lab.ps1
```

Si aparece un error sobre `dockerDesktopLinuxEngine` o una tubería `npipe`,
Docker Desktop está cerrado o su motor Linux aún no está listo. Abre Docker
Desktop, espera el estado **Engine running** y comprueba en una terminal nueva
con `docker info`. Si el menú ofrece **Switch to Linux containers**, selecciónalo
y espera a que el motor arranque; el laboratorio usa contenedores Linux.

Abre DVWA en `http://127.0.0.1:4280` y Mailpit en `http://127.0.0.1:8025`.
La configuración inicial de DVWA permite crear o reinicializar su base desde
la propia página de configuración de DVWA.

Para detener los contenedores conservando la base y los logs aún retenidos por
Docker:

```powershell
.\scripts\stop_dvwa_lab.ps1
```

Para eliminar los contenedores, la base y los logs aún retenidos por Docker,
ejecuta desde la raíz, revisa el nombre del volumen y confirma la acción:

```powershell
docker compose --file compose.lab.yaml down --volumes
```

Esto elimina los datos de prueba guardados por este Compose. No borra la captura
local en `.local-state/dvwa-lab/`, los logs operativos, reportes ni históricos
de la aplicación en el host.

## Copiar un log de prueba

Después de generar solicitudes en DVWA:

```powershell
.\scripts\sync_dvwa_lab_logs.ps1
```

La utilidad filtra las líneas de acceso Apache desde la salida retenida de
Docker y el archivo se guarda en `.local-state/dvwa-lab/access.log`, excluido
de Git y separado de `logs/access.log`. La salida del contenedor rota con un
límite total aproximado de 30 MB, así que la captura contiene lo que Docker aún
conserva. Para apuntar Flask a esa captura, configura
localmente `LOG_PATH=./.local-state/dvwa-lab/access.log` y reinicia Flask. En
VSCode puedes iniciar la tarea **web-defense-ai V2: laboratorio DVWA (Flask +
Next.js)**: usa esa ruta y mantiene `ANALYSIS_MANUAL_ENABLED=0`. Detén primero
cualquier Flask que ya ocupe el puerto 5000. Sincroniza de nuevo después de
cada tanda de solicitudes para actualizar la captura. No copies datos reales ni
secretos al laboratorio.

Mailpit solo captura correo que se configure expresamente. No actives el
ejecutor ni `ANALYSIS_MANUAL_ENABLED` hasta completar las revisiones de fase 6
y comprobar que Telegram está desactivado. Para una futura prueba controlada
con Mailpit, el SMTP debe apuntar a `127.0.0.1:1025`; la opción
`EMAIL_SMTP_STARTTLS=0` se usa solo para este sink local, sin reenvío. STARTTLS
sigue activo por defecto y no puede desactivarse para servidores que no sean de
loopback. Usa remitente, destinatario y contraseña ficticios.

## Un ciclo integrado de prueba

Cuando DVWA y Mailpit estén activos y la clave del proveedor LLM ya esté
configurada localmente, ejecuta desde PowerShell:

```powershell
.\scripts\run_phase6_cycle.ps1
```

El comando solicita un único análisis al proveedor configurado y puede consumir
cuota. El modelo preferido se define en `LLM_MODEL` y los modelos alternativos,
separados por comas, en `LLM_FALLBACK_MODELS`; `.env.example` propone los IDs
Groq vigentes al preparar esta fase. Los modelos anteriores ya retirados se
reemplazan por el predeterminado vigente. El proceso sobrescribe únicamente
`.local-state/phase6-pilot/`: el log
se vuelve a capturar desde DVWA, los reportes y SQLite quedan aislados, Telegram
se omite y cualquier email se entrega solo a Mailpit con datos ficticios. No
lee ni muestra el valor de las claves. Si el reporte no contiene alertas altas
o críticas, no se genera correo. `ANALYSIS_MANUAL_ENABLED` y la entrada Next.js
principal permanecen desactivadas.

Este ciclo no completa el piloto: aún se requieren diez ciclos, medición con
carga representativa, observación de 24–48 horas y un ensayo de reversión.

## Verificación y reversión

La estructura se valida sin iniciar contenedores con:

```powershell
docker compose --file compose.lab.yaml config --quiet
```

Verificación local realizada el 28/09/2026: las imágenes arrancaron, DVWA y
Mailpit respondieron en sus puertos de loopback, la sincronización produjo una
captura con solicitudes SQLi y Flask/Next.js mostraron esas solicitudes. Esto
no acredita integración con CrewAI, entrega SMTP, carga representativa ni una
ventana de piloto sostenido. Un ciclo integrado completó análisis y publicó el
reporte; la alerta SMTP alcanzó Mailpit. La tarea de VSCode para iniciar ambos dashboards
también se comprobó correctamente. Para volver al entorno anterior, detén este
Compose y continúa usando Flask con sus datos locales; el Compose heredado y sus
datos no forman parte de la pila nueva.
