# Validación guiada en Parrot — 12/10/2026

El usuario clonó `EnriqueForte/web-defense-ai-v2` en el disco local de su VM
y ejecutó las instrucciones desde una terminal de Parrot. Evidencia: capturas
aportadas en la conversación y confirmación explícita de navegación correcta.
No se dispuso de acceso remoto a la VM ni se obtuvieron logs completos.
El commit comprobado fue `df40ad8`, con `main` y `origin/main` coincidentes.

## Entorno y preparación

- VMware Workstation Pro 26H1, versión 26.0.1 según captura.
- Parrot Security 7.3 (echo), x86_64; `/etc/os-release` informa Debian 13.5.
- Memoria total 15 GiB y 37 GiB de disco disponibles en la comprobación inicial.
- Git 2.47.3. Inicialmente Python 3.13.5 y Node 20.19.2; pnpm y Python 3.11 ausentes.
- Se guio instalación de Python 3.11 con uv y Node 24 con nvm en el usuario.
  Las capturas finales confirman Python 3.11.17, Node 24.21.0, npm 11.19.0 y
  pnpm 11.19.0. No se solicitó reemplazar el Python de Parrot.
- Instalador común con `--install --frontend --init-env`: entorno `.p2`,
  dependencias frontend y plantilla local `.env`; salida final `created`.

## Resultados observados

| Comprobación | Evidencia recibida |
| --- | --- |
| Python del entorno | 3.11.17 |
| `pip check` | No broken requirements found |
| Contrato Linux | 157 paquetes fijados, cero diferencias |
| Baseline | 269 Python aprobadas y tres comprobaciones JS aprobadas |
| HTTP sintético | Flask, CSP, informe y recursos/hash verificados |
| CrewAI/LiteLLM offline | 25 escenarios aprobados, sin proveedor |
| Frontend | lint/tipos sin errores visibles, 15 grupos UI y build Next 16.3.8 completados |
| Arranque | Perfil pilot/legacy, Flask en 127.0.0.1:5000 y Next producción en 127.0.0.1:3000 |
| API directa/proxy | Salud HTTP 200 en ambos puertos |
| Navegación | Captura de Resumen; usuario confirma Amenazas, Reportes, Actividad y Configuración sin errores |

Se indicó ejecutar `check_syntax.py`, pero su resumen no aparece en las capturas;
no se atribuye una comprobación visual independiente de sus 71 archivos en esta VM.

La primera lectura de Next devolvía 500 y el acceso directo a 5000 rechazaba
la conexión. Después de arrancar Flask, la API directa y el proxy dieron 200.
La navegación inicial a 5000 mostraba la interfaz Flask conservada; 3000 muestra
la nueva interfaz. No fue necesario cambiar código para resolver la incidencia.

El estado final «Fuentes incompletas» corresponde a la ausencia de logs e informes
en este clon. No hay datos del mantenedor copiados. Manual deshabilitado y worker
sin arrancar; no se solicitaron llamadas reales al proveedor, Docker o envíos.
Las terminales Flask y Next quedaron abiertas según las instrucciones; no se
ha comprobado su continuidad ni su parada después de la confirmación del usuario.

## Alcance y siguiente entrega

Quedan acreditados instalación, pruebas offline, build, arranque y lectura en
esta VM Parrot. No se acredita Docker/DVWA, ingesta ni análisis real en Parrot,
otras distribuciones/versiones/arquitecturas o calidad semántica A-05.
Falta capturar un inventario completo Linux y fijar dependencias adicionales;
`uvloop==0.23.0` se observó en Ubuntu CI, no se ha verificado su versión en esta VM.

La batería de pruebas pertenece a la validación de desarrollo. Para usuarios,
el instalador actual automatiza las dependencias del proyecto, pero requiere
Python 3.11, Node 24 y pnpm 11.19.0 previamente disponibles. El build y el arranque
de Flask/Next siguen siendo pasos separados. Simplificar requisitos, preparación,
build, arranque y diagnóstico inicial mediante un asistente sigue pendiente;
no se presenta como una función implementada en esta entrega documental.
