# Recorrido completo de Configuración — 13/10/2026

## Cambio

El formulario cancelaba su lectura inicial al salir de la vista, pero no el
guardado. Ahora el ciclo de vida cancela ambas solicitudes y evita aplicar
resultados después del desmontaje. Una referencia de solicitud activa impide
guardar dos veces simultáneamente. `putApi` acepta una señal y limita la espera
a 10 segundos, incluyendo la lectura del cuerpo de respuesta.

Un timeout de guardado libera los controles y pide volver a consultar la
configuración antes de reintentar. Cancelar la espera del navegador no revierte
un guardado que ya haya completado el servidor; no hay reenvío automático.
El proveedor, los modelos, las claves y el contrato de persistencia no cambian.

## Ensayo reproducible

Playwright 1.64.0 está fijado como dependencia de desarrollo, junto con su
lockfile; no se cambian versiones existentes. Se comprobó el lockfile con
pnpm 11.19.0. El ejecutable pnpm disponible inicialmente era 11.25.0 y añadió
la dependencia; la comprobación posterior con la versión requerida conservó
el mismo lockfile.

`scripts/check_settings_e2e.py` copia las fuentes frontend y archivos de build
permitidos a un directorio nuevo en `.local-state/settings-e2e/`, sin dotenv ni
datos operativos. Comparte los módulos instalados mediante un enlace y compila
una salida de producción independiente con webpack. No sustituye `.next` normal.
Usa el proxy Next real a Flask y dos puertos loopback efímeros distintos de
3000/5000. ProcessOwner supervisa build, Flask, Next y Playwright; el cierre
comprueba que ambos puertos queden libres.

Flask usa las rutas reales de configuración y un `.env` sintético nuevo. Su
entorno heredado se vacía, dotenv operativo se bloquea y la lectura del resolver
se dirige exclusivamente al archivo de prueba. Se bloquean conexiones salientes
desde Flask; el navegador solo permite destinos del frontend aislado. Los modos
de fallo y las rutas de control existen únicamente en esta fixture. El ensayo
no habilita manual, worker, notificaciones ni análisis.

Nueve casos en Chromium cubren:

1. Guardado real, clave vacía conservada, respuesta sin clave, recarga, texto
   ajeno preservado, bloque administrado único y actualización del estado LLM.
2. Cambio de proveedor/modo, limpieza de entrada anterior y modelo personalizado.
3. Validación real del backend y corrección posterior sin alterar el archivo.
4. Conflicto por lock real y fallo de disco simulado, con recuperación.
5. Respuesta de guardado corrupta después del commit y lectura posterior correcta.
6. Salida durante lectura inicial: señal abortada y nueva lectura al volver.
7. Salida durante guardado ya confirmado por Flask: abortar espera sin revertir
   ni repetir, nueva vista sin avisos de la anterior.
8. Timeout de lectura y recuperación al volver a entrar.
9. Timeout de guardado, controles disponibles y ausencia de reintento automático.

Los timers de timeout se avanzan con el reloj del navegador; no se acorta el
límite de producción. Se comprueba la ausencia de errores JavaScript no manejados.
Las claves presentes en trazas o capturas son cadenas sintéticas conocidas.

Para repetir desde un entorno Python instalado de pruebas:

```bash
# Desde frontend (Linux necesita también las dependencias de sistema del navegador).
pnpm exec playwright install chromium --only-shell --with-deps
# Desde la raíz; Windows: .p2/Scripts/python.exe.
.p2/bin/python -B scripts/check_settings_e2e.py
```

La configuración Playwright rechaza ejecutarse sin URLs y salida suministradas
por el supervisor; no usa la consola operativa por defecto.

## Validación local y pendiente remoto

Windows `.p4`: 303 Python (302 aprobados/uno Linux omitido), tres JS, lint/tipos,
17 grupos UI y 86 archivos de sintaxis aprobados. Dos grupos UI nuevos comprueban
cancelación del cuerpo de PUT y timeout aun cuando un doble de fetch ignore la
señal, además de rechazo anterior a la llamada si ya está abortada.

El build de producción webpack y arranque/cierre de los servidores aislados
pasaron localmente. Chromium descargado no pudo iniciarse (`spawn UNKNOWN`);
eventos Code Integrity 3077/3033 relativos a su ejecutable confirman bloqueo de
Windows. Ningún caso E2E llegó a ejecutarse allí. No se cambia esa política.
Recibo del ensayo: `.local-state/settings-e2e/0d751955ffc24b1a9a7e75cc5ecc1f09/`.

Primer código publicado `d0e61c799c9c51fd58f4e3ba30845598aceaf00d`,
[CI 38380953611](https://github.com/EnriqueForte/web-defense-ai-v2/actions/runs/38380953611):
los nueve casos E2E pasaron en ambos sistemas (Ubuntu 7.7s, Windows 9.4s).
Ubuntu completó el job; Windows falló después de las pruebas en el probe
inmediato de disponibilidad de un puerto tras cerrar los procesos propios.
No hay captura de estado TCP para atribuir la causa exacta.

El supervisor de pruebas conserva el probe estricto y ahora espera hasta 10s
por la disponibilidad verificable de sus dos puertos, únicamente después de
cerrar ProcessOwner. No reutiliza servidores previos ni mata procesos ajenos.
La admisión inicial sigue rechazando inmediatamente puertos ocupados. Tres
pruebas comprueban cierre transitorio, bloqueo persistente y error de permiso
desconocido (este último falla sin reintento). Nueva CI pendiente de publicación
y revisión; R-15 conserva abierto el cierre completo hasta comprobarla.
No se acredita análisis real,
calidad semántica A-05, laboratorio Parrot ni seguridad residual por este ensayo.

## Cierre comprobado

Código `f8763178605e976e37982350adc702b225d89fc5`,
[CI 38383079313](https://github.com/EnriqueForte/web-defense-ai-v2/actions/runs/38383079313),
attempt 1: Windows-latest y Ubuntu24.04 completaron con success. Se revisaron
estados y logs finales. Los nueve casos E2E pasaron en ambos (Windows 9.5s,
Ubuntu 8.7s), y el supervisor confirmó salida 0/cierre con puertos libres.
Estos tiempos corresponden a las pruebas del formulario, no al build completo.

Ambos completaron instalación nueva, build normal, pip check/172 pines estrictos,
87 archivos de sintaxis, tres JS, HTTP sintético, 25 escenarios SDK offline,
lint/tipos/17 UI y smoke normal con API directa/proxy HTTP200, ejecutor offline
y cierre libre. Ubuntu aprobó 306 Python; Windows 305 más uno exclusivo Linux
omitido. La regresión local final también aprobó 305 más uno omitido.
El build normal de CI conserva Turbopack; el ensayo del navegador compila webpack
en una carpeta separada. No se afirma que sus chunks sean idénticos.

R-15 queda cerrado en el alcance del recorrido sintético de Configuración y los
efectos descritos. No se inicia un análisis para comprobar la clave ni se prueba
la conexión real a un proveedor. Esta evidencia del navegador procede de CI;
el bloqueo de Chromium local se conserva y la VM Parrot no ha repetido este E2E.

El estado operativo local coincide con el recibo anterior: 29 trabajos, 14
entregas, cero activos, mismos hashes de log/publicación/informe/resultado y
metadatos de `.env`. Recibo final en
`.local-state/migration-20261012/invariants-settings-e2e-final-20261013.json`.
Logs y resúmenes CI en `.local-state/launcher-20261012/`. El commit documental
posterior usa `[skip ci]`; el código de la CI aprobada sigue siendo f876317.
