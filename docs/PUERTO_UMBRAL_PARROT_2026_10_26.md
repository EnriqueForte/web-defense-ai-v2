# Puerto Umbral y V2 — preparación de actualización y revisión manual en Parrot

Fecha: 26/10/2026. El propietario autoriza compilación, commit/push del proyecto
y revisión manual posterior desde la VM. Se mantiene la restricción de no
ejecutar suites de escenarios o análisis LLM automáticamente.

## Qué cambia al actualizar

La distribución portable en [labs/puerto_umbral](../labs/puerto_umbral/README.md)
permite obtener las dos aplicaciones con un único `git pull`. El Site privado
F1 sigue separado y conserva su publicación. No se crea otro repositorio ni se
copian al código credenciales, historial Git, imágenes, entornos o datos locales.

El nuevo comando explícito es:

```bash
python3 webdefense.py start --mode structured --with-puerto-umbral
```

Arranca Flask, Next, el panel de Puerto Umbral y sus servicios Docker propios,
con los cinco puertos solo en loopback. Prepara y comprueba disponibilidad; no
inicia escenarios, corpus, worker, análisis del modelo, avisos o monitorización
periódica. El arranque anterior sin esa opción conserva su alcance de V2/pilot.

El laboratorio admite el Compose realmente instalado: `docker compose` cuando
está disponible o el ejecutable `docker-compose` usado anteriormente en Parrot.
No instala otro cliente ni cambia el contexto de Docker por sí solo.
La preparación construye las imágenes con `docker build` y reserva Compose para
configuración y arranque con `--no-build`; no invoca `compose build`.

Ctrl+C debe cerrar los procesos iniciados por la terminal y solicitar la parada
de los servicios propios Puerto Umbral. Se conservan sus evidencias y volúmenes.
No se ejecuta `down --volumes` ni se detienen servicios DVWA/Mailpit existentes.
Una sesión Puerto Umbral previa debe cerrarse antes de asumir una nueva.

## Compilación de preparación

El frontend se compiló localmente en Windows con Webpack y terminó la comprobación
de tipos TypeScript. Turbopack falló al iniciar su proceso PostCSS incluso fuera
del sandbox; ese intento no se cuenta como compilación correcta. No se cambiaron
dependencias para resolverlo. La compilación local no acredita compilación ni
arranque en Parrot. El lanzador conjunto y el backend siguen pendientes de esa
revisión manual en la VM.
La sintaxis de los 16 archivos Python nuevos/modificados se compiló en memoria
con el intérprete de `.p2`, sin importar ni ejecutar los módulos de aplicación;
los dos JSON del bloque se leyeron correctamente. No se ejecutaron suites ni escenarios.

## Pasos en la VM: no ejecutados por el agente

Desde el clon V2 en Parrot, primero cerrar sus consolas/worker propios si quedan
abiertos y comprobar que `git status --short` no muestre cambios que puedan
perderse. Si aparecen cambios, conservarlos antes de actualizar; no usar reset.

Antes del `pull`, crear una copia nueva de los datos operativos con el intérprete
de la instalación existente:

```bash
.p2/bin/python -B scripts/backup_operational.py --profile all
```

Conservar la ruta devuelta y confirmar `verified: true`. Es un respaldo de la
aplicación y su recuperación aislada; no copia el volumen DB ni correo de DVWA.
El laboratorio existente no se recrea como parte de este procedimiento.

Después de que el commit autorizado esté publicado y la copia esté verificada:

```bash
git pull --ff-only
python3 webdefense.py install
python3 webdefense.py start --mode structured --with-puerto-umbral
```

El instalador conserva un `.env` existente. No es necesario mostrar su contenido,
copiar claves al chat ni abrir el analizador para comprobar las pantallas.

Si la compilación del frontend en ese equipo presenta el mismo fallo de
Turbopack, conservar el diagnóstico y compilar solo la interfaz con la alternativa
que se usó en Windows, desde `frontend`:

```bash
node node_modules/next/dist/bin/next build --webpack
```

No se presupone que vaya a fallar en Linux. Un error de instalación previo a la
compilación requiere revisar su causa antes de continuar.

## Revisión manual de las páginas

Abrir estas direcciones en el navegador **dentro de Parrot**:

| Dirección | Revisión |
| --- | --- |
| `http://127.0.0.1:3000` | Consola V2 y vista Actividad |
| `http://127.0.0.1:4381` | Panel local de Puerto Umbral |
| `http://127.0.0.1:4380` | Portal del modo vulnerable |
| `http://127.0.0.1:4382` | Portal del modo corregido |

Primero revisar navegación normal y estado de los servicios. Cambiar una
selección no inicia un escenario. La captura solo se solicita desde el botón de
Actividad; esa acción no llama al modelo. Los escenarios se revisarán después
mediante acciones manuales explícitas del propietario, conservando cada recibo.

La primera revisión debe confirmar puertos y pantallas antes de extraer
conclusiones sobre efectos de escenarios o detección. Los resultados iniciales
42/45 y los pendientes F2/F3 se conservan en
[su registro](PUERTO_UMBRAL_F2_F3_2026_10_26.md).

No marcar Parrot actualizado ni los servicios arrancados hasta recibir su salida
real. La accesibilidad desde otro equipo no se habilita por este procedimiento.

## Evidencia a recoger al terminar

- Commit efectivo mostrado por `git rev-parse --short HEAD` en la VM.
- Resultado de instalación/compilación y mensajes de consola lista.
- Confirmación de acceso a V2 y al panel Puerto Umbral en el navegador de la VM.
- Estado de fuente y, solo si se solicita, recibo de captura manual.
- Salida de cierre con Ctrl+C y cualquier aviso de parada no confirmada.

No se atribuyen a esta publicación pruebas de CI, cierre de F2/F3 ni seguridad
general. El commit de desarrollo se prepara con exclusión de CI para respetar
la revisión manual acordada. El estado final de publicación se informará tras
comprobar el push; esta guía no lo presume.

## Diagnóstico de la primera preparación en Parrot

La captura del propietario acredita `existing_preserved` e instalación completada.
El arranque conjunto se detuvo durante la construcción con el error
`compose build requires buildx 0.17.0 or later`. La carpeta del laboratorio sí
está presente: el traceback ejecuta `labs/puerto_umbral/labctl.py` y su controlador.
No se atribuye el fallo a una actualización incompleta ni se acredita el arranque
de Flask, Next o del laboratorio por esa salida.

Se sustituye la compilación mediante Compose por dos invocaciones secuenciales
de Docker, una por imagen compartida. Se conservan Dockerfiles, digests, puertos,
restricciones y `up --no-build`. No se instala ni actualiza Buildx automáticamente,
ni se fuerza un constructor alternativo por variables de entorno. La operación
real sigue pendiente de repetir el arranque manual en Parrot.

Los resultados completos de cada construcción quedan en
`labs/puerto_umbral/.local-state/f2/setup-history/build-*.json`, separados del
código versionado. El log del lanzador indica su ruta si la construcción falla.
El identificador del primer log se localizó por búsqueda, evitando volver a
transcribirlo desde una captura. No hace falta repetir el instalador para aplicar
esta corrección Python: tras el `pull`, volver a ejecutar solo el arranque conjunto.
