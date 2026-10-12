# Validación guiada en Parrot — 12/10/2026

El usuario clonó `EnriqueForte/web-defense-ai-v2` en el disco local de su VM
y ejecutó las instrucciones desde una terminal de Parrot. Evidencia: capturas
aportadas en la conversación y confirmación explícita de navegación correcta.
No se dispuso de acceso remoto a la VM ni se obtuvieron logs completos.
El commit comprobado en el ensayo inicial fue `df40ad8`, con `main` y `origin/main`
coincidentes. El ensayo posterior del lanzador unificado se recoge al final;
su SHA no aparece en las nuevas capturas.

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
Las terminales Flask y Next quedaron abiertas al terminar el ensayo inicial.
La comprobación posterior del cierre corresponde al lanzador unificado descrito abajo.

## Alcance y siguiente entrega

Quedan acreditados instalación, pruebas offline, build, arranque y lectura en
esta VM Parrot. No se acredita Docker/DVWA, ingesta ni análisis real en Parrot,
otras distribuciones/versiones/arquitecturas o calidad semántica A-05.
El [seguimiento del contrato Linux](CONTRATO_LINUX_2026_10_12.md) capturó el
inventario completo Ubuntu y fijó `uvloop==0.23.0`. La comprobación posterior
del inventario en esta VM también pasó, según el apartado final.

La batería de pruebas pertenece a la validación de desarrollo. Para usuarios,
el instalador unificado posterior automatiza dependencias y build, pero requiere
Python 3.11, Node 24 y pnpm 11.19.0 previamente disponibles.

## Ensayo posterior: instalación y arranque unificados

Tras indicar actualización a `f8318d6`, el usuario aportó estas evidencias.
No se recibió una captura del SHA actualizado; no se certifica ese SHA en la VM.

- Instalación finalizada: pip check correcto, 157 paquetes fijados sin diferencias,
  pnpm 11.19.0, build Next 16.3.8 y `existing_preserved` para configuración existente.
- `python3 webdefense.py start` confirmó «Consola lista» en 127.0.0.1:3000.
  El usuario confirmó que la web funciona y que cambió entre vistas.
- Tras indicar Ctrl+C, dejó de cargar la web. Tres comprobaciones `check`
  mostraron puerto 3000 ocupado: el reinicio inmediato no quedó validado.
- Más tarde `ss -ltnp` y `ss -tan state time-wait`, filtrados por 3000/5000,
  mostraron únicamente cabeceras. `python3 webdefense.py check` terminó preparado.
  Queda confirmado el cierre con puertos libres después de la espera.

La duración de la espera no se midió. No se capturó el estado de sockets durante
el fallo; TIME_WAIT es una explicación compatible, no una causa probada de ese
episodio. La [corrección del comprobador](CORRECCION_PUERTOS_2026_10_12.md)
se publicó como `2a73ff0` y pasó Windows/Ubuntu CI, incluida la regresión real
de sockets residuales en Ubuntu. Su ensayo posterior en la VM se recoge a continuación.
No se solicitaron motor, proveedor, Docker ni notificaciones para este recorrido.

## Confirmación posterior del ajuste de puertos

Tras indicar `git pull --ff-only` hasta `e1f7383` (documentación; código probado
`2a73ff0`) y el recorrido de cierre/comprobación/arranque inmediato, el usuario
confirmó «perfecto ya funciona correctamente». La captura muestra:

1. `python3 webdefense.py check`: «Preparado».
2. `python3 webdefense.py start`: «Consola lista» en 127.0.0.1:3000.
3. Ctrl+C: «Consola detenida».
4. `python3 webdefense.py check`: «Preparado», sin aviso de puerto ocupado.

Entre comandos aparecen dos intentos de ejecutar una ruta Windows en zsh,
rechazados como comando inexistente; las órdenes de la herramienta terminan
correctamente. No se midió la demora entre comandos, ni se recibió la salida
Git del SHA actualizado. El segundo arranque después del último check no aparece
en la captura. La aceptación explícita del usuario completa la validación guiada
del ajuste en esta VM, con esos límites de evidencia. El último estado visible
es consola detenida y preflight preparado; no se afirma servicio activo.

La instalación, lectura entre vistas, arranque y cierre del flujo unificado quedan
aceptados en esta VM. Docker/ingesta/análisis real siguen fuera de esta validación;
el inventario Linux se comprobó posteriormente.

## Contrato completo e inventario de dependencias

Nueva captura del usuario: commit `86c21b5`, con main/originmain/originHEAD
coincidentes. `.p2/bin/python -m pip check` termina sin requisitos rotos;
`check_environment.py --strict` informa158pines/0diferencias/0adicionalessinfixar;
`snapshot_environment.py` informa instantánea158/0diferencias/0adicionales.

El contrato Linux completo y la exportación del inventario quedan comprobados en
esta VM, incluyendo uvloop0.23.0 por la validación estricta. No se recibieron
los archivos exportados ni su hash desde la VM: la evidencia recibida es la
captura de ejecución satisfactoria. El freeze Ubuntu conservado sigue siendo
evidencia independiente. No fue necesario reinstalar paquetes para esta prueba.
