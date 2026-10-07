# Endurecimiento local y alcance de distribución GitHub

El 07/10/2026 el usuario aclaró el objetivo: publicar el código de V2 en GitHub
para que otras personas lo clonen y ejecuten en sus instalaciones. El cierre
se orienta a distribución autoalojada, no a crear un dashboard central público.
La licencia MIT existente se conserva. No se publicaron commits, no se cambió
visibilidad/remotos ni se modificó el repositorio original.

## Cambios de este bloque

R-21, protección local de Flask:

- TRUSTED_HOSTS admite localhost, 127.0.0.1 y [::1]; conserva puertos/proxy Next.
  Se mantiene además la restricción de conexiones loopback y la política Origin.
- MAX_CONTENT_LENGTH de 16 KiB limita la lectura del cuerpo de configuración;
  un exceso devuelve 413 con código request_too_large sin invocar su escritor.
- Errores HTTP de /api/ mantienen formato JSON. Errores internos generan 500
  constante sin mensajes, traceback o contenido de excepción en respuesta/log.
  Los errores internos HTML devuelven texto plano. Esto no sustituye el
  diagnóstico seguro por etapas pendiente del motor operativo.
- X-Content-Type-Options=nosniff y Referrer-Policy=same-origin. El contrato de
  caché API y X-Request-ID se conservan.

Preparación para distribución:

- `.gitignore` excluye todo dato generado bajo logs/ y reports/, incluidos los
  JSON/generaciones que no cubría la exclusión anterior; conserva .gitkeep.
  `.env`, `.local-state`, backups y entornos siguen excluidos. No elimina archivos.
- `.env.example` deja NOTIFICATION_DESTINATIONS vacío para nuevas instalaciones.
  La configuración existente del usuario no se cambia; manual y motor legacy
  conservan sus defaults hasta la decisión final de activación/distribución.
- docker-compose.yml se identifica como legacy, con su diferencia de exposición
  de puertos. Se recomienda compose.lab.yaml sin modificar contenedores/volúmenes.
- README enlaza [instalación propia](INSTALACION_AUTOALOJADA.md), distingue código
  compartido de servicio accesible y reconoce Windows/Python 3.11 como entorno
  comprobado. La guía es preparatoria: no afirma una clonación limpia final ni
  validación Linux/macOS que no se han realizado.

## Validación y operación

232 pruebas Python aprobadas en `.p2` y `.venv`, tres diagnósticos JS por ejecución.
Fixtures sintéticas prueban hosts locales y ajenos, IPv6, cuerpo excesivo sin
escritura, excepciones con secreto ficticio sin filtración y cabeceras/caché.
El comportamiento TRUSTED_HOSTS se comprobó en el código instalado de Flask
3.1.3/Werkzeug, sin añadir una implementación propia de parsing de Host.

Flask propio se recargó con el perfil piloto existente. Lanzador vigente PID
33740; worker 37076 y Next 10616 se conservaron. Verificar identidad antes de
operar esos PID. La API real admite hosts locales, rechaza untrusted.example
con 400, conserva salud ok/executor online, devuelve las nuevas cabeceras y
responde 413 al cuerpo inválido excesivo de prueba. El proxy Next devuelve 200.
La sonda no introdujo una configuración válida ni guardó .env.
Recibo: `.local-state/a05-activation/self-hosted-20261007/hardening.json`.

`git check-ignore` confirmó exclusión de JSON actuales/generaciones, log .txt,
.env y estado local. Los archivos actualmente registrados bajo logs/reports
son únicamente sus .gitkeep; no se inspeccionaron ni publicaron datos privados.
Esto no certifica que toda la historia Git carezca de secretos: la revisión
previa a publicar sigue pendiente. No se ejecutaron jobs, LLM, Docker,
notificaciones o instalaciones de dependencias en esta entrega.

## Pendientes y reversión

Quedan diagnóstico operativo, aceptación/observación A-05, instrucciones
definitivas para análisis estructurado, instalación limpia del contenido final,
build/auditorías, política de datos y revisión del paquete/historial antes de
publicar V2. La recuperación de aplicación/SQLite está implementada; cobertura
de volúmenes/buzón debe decidirse. La autonomía offline del retorno Flask, que
aún utiliza recursos CDN, queda separada de estas protecciones HTTP.

Los cambios HTTP son reversibles por configuración/código y recarga de Flask;
no requieren restaurar SQLite o informes. Los defaults y exclusiones solo
afectan nuevas configuraciones/adiciones Git. No retirar protecciones locales
para convertirlo en servicio compartido sin definir otro alcance de acceso.
