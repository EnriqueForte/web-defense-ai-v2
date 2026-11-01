# V2 y Puerto Umbral — revisión de producto

Fecha: 31/10/2026, Europe/Madrid. Estado: redistribución implementada, compilada
y publicada; nueva captura de escritorio en Parrot recibida a zoom 60 %.
Se revisan las pantallas y evidencias existentes, sin ejecutar
escenarios, capturar fuentes nuevas, iniciar seguimiento o llamar al modelo.

Actualización de uso del 01/11: se desarrolla la entrada conjunta
`python3 webdefensev2.py`, que usa fuente V2 `corrected` por defecto.
Para conservar la fuente vulnerable de la revisión anterior, utilizar
`python3 webdefensev2.py --lab-mode vulnerable`. La receta explícita posterior
sigue siendo compatible. La nueva entrada tiene sintaxis y ayuda revisadas;
su arranque en Parrot aún no se ha observado y requiere recibir antes el cambio
publicado. No se repite una revisión visual por añadir este acceso.

## Resultado visual posterior en Parrot

Entrega `cd6b34d1e87b6382cfd24856a19afce2f485dcd5`, publicada en `origin/main`
con HEAD remoto y árbol limpio verificados al finalizar la publicación.
El propietario aporta una captura de la nueva distribución a zoom 60 %:
se aprovecha el ancho lateral, las gráficas y reportes comparten fila y
amenazas/terminal aparecen debajo; también se ve la barra inferior de estado.

Informa que a zoom 100 % todavía necesita desplazamiento vertical y que no
quiere empeorar la visibilidad de los datos. La recepción acredita la nueva
distribución mostrada a 60 %, no el encaje completo a 100 % o una revisión de
teclado/móvil. No se solicita repetir la captura solo para documentar esto.

Se recomienda mantener el diseño actual y usar zoom 100 % con desplazamiento
natural. Aprovechar el ancho no garantiza que todos los bloques quepan en la
altura visible de cualquier ventana. No se reduce más la tipografía ni se
impone una altura fija u ocultación de contenido para forzar el encaje. No se
introducen nuevos cambios de interfaz por esta recepción; el objetivo de
eliminar todo desplazamiento a 100 % no queda acreditado. El resto de la
revisión de producto conserva sus pendientes y no bloquea registrar lo observado.

## Recepción visual y redistribución del Resumen

El propietario aporta tres capturas del Resumen anterior: escritorio amplio,
zona superior de indicadores/gráficas y zona inferior de tabla/terminal/reportes.
Se observa contenido central limitado con ancho libre a ambos lados y bloques
inferiores que requieren desplazamiento. No son capturas de un menú móvil ni
una comprobación de teclado. Solicita optimizar la distribución y autoriza
implementar la propuesta.

Cambios en `frontend/src/app/page.tsx` y `frontend/src/app/globals.css`:

- Solo Resumen aprovecha el ancho disponible; las vistas de detalle conservan
  su ancho de lectura.
- Desde 1600 px de ventana, gráficas y Reportes recientes comparten la primera
  fila; Amenazas recientes y Terminal comparten la segunda. Desde 1000 px se
  distribuyen en dos columnas por bloques; por debajo se apilan. Los indicadores
  conservan su adaptación de cuatro a dos y una columna.
- Cabecera, coordinación, tarjetas y gráficas tienen menor espaciado/altura;
  la tipografía base se mantiene.
- El Resumen muestra hasta cuatro amenazas, seis últimas líneas de la ventana
  de log disponible y dos reportes históricos, con cantidades visibles y acceso
  a Amenazas, Actividad y Reportes. Son vistas previas, no recortes del archivo.
- No se impone una altura fija a toda la página ni se bloquea su desplazamiento.
  El contenido adicional, el zoom o las ventanas pequeñas pueden requerirlo.

Validación local del agente: compilación de producción
`node node_modules/next/dist/bin/next build --webpack`, incluido TypeScript y
generación de rutas, exit 0; ESLint de `src/app/page.tsx`, exit 0. No se ejecutan
suites, servicios o escenarios. La compilación no acredita el resultado visual.
El propietario autoriza después commit/push y revisión en Parrot. La entrega
se identifica por el commit que incorpora esta revisión, con `[skip ci]`;
la publicación se comprobará contra el HEAD remoto al finalizar. El diseño
nuevo aún no se ha comprobado visualmente en Parrot. Este cambio del frontend
requiere compilar de nuevo allí y reiniciar la consola propia antes de recoger
la captura del nuevo Resumen.

## Recibir la entrega en Parrot

Detener primero la consola propia con `Ctrl+C` y esperar al prompt. Desde la
raíz del checkout, revisar `git status --short`: si aparecen cambios locales,
conservarlos y revisar la salida antes de continuar, sin forzar el árbol.
Actualizar con `git pull --ff-only` y comprobar `git log -1 --oneline` contra
el commit publicado en esta entrega. Desde `frontend`, ejecutar:

```bash
node node_modules/next/dist/bin/next build --webpack
```

Tras el resultado correcto, volver a la raíz e iniciar:

```bash
python3 webdefense.py start --mode structured --with-puerto-umbral --lab-mode vulnerable
```

Se mantiene vulnerable como última fuente seleccionada; revisar el diseño no
necesita cambiarla. Dejar la terminal abierta y abrir Resumen en el navegador
de Parrot. Recargar con `Ctrl+Shift+R`. Recoger primero la vista de escritorio
a zoom 100 %, indicando resolución aproximada si se conoce; después una
ventana estrecha con el menú móvil abierto. No repetir casos o análisis para
obtener contenido nuevo: se usan las evidencias existentes.

## Condiciones de la revisión

Usar el navegador de Parrot con la aplicación ya abierta. V2 está en
`http://127.0.0.1:3000` y el panel de Puerto Umbral en
`http://127.0.0.1:4381`. Si no están disponibles, detener el recorrido visual y
confirmar el estado de la terminal propia; esta guía no requiere reinstalar,
recompilar o modificar la red. El modo y las fechas de las evidencias guardadas
pueden diferir de la selección actual: revisar sus etiquetas, no regenerarlas.

## Comprobaciones manuales

| Recorrido | Resultado esperado | Estado actual |
| --- | --- | --- |
| V2 en escritorio | Cabecera y autoría legibles; menú y contenido sin superposición | Nueva distribución observada a zoom 60 %; propietario informa desplazamiento a 100 %; se prioriza legibilidad, sin forzar encaje total |
| Navegación V2 | Resumen, Amenazas, Reportes, Actividad y Configuración se abren, con vista activa identificable | Pendiente |
| Evidencias existentes | Log e informe mantienen fechas y origen; la auditoría identifica modo y ejecución; vacíos y errores se explican sin aparentar datos nuevos | Evidencias previas parciales; revisión conjunta pendiente |
| Panel Puerto Umbral | Autoría visible, navegación legible y recibos existentes consultables sin ejecutar ni restablecer casos | Cabecera observada previamente; revisión conjunta pendiente |
| Ventana estrecha | En ambas apps el menú y los controles siguen accesibles; las tablas o bloques de texto pueden desplazarse dentro de su contenedor | Pendiente |
| Teclado | Tab/Mayús+Tab muestran el foco; el menú móvil puede abrirse y cerrarse; V2 permite cerrar con Escape y devuelve el foco al botón | Pendiente |
| Zoom del navegador al 200 % | Encabezados, navegación y controles siguen utilizables; no quedan acciones tapadas | Pendiente |

Las capturas iniciales sugeridas son Resumen de V2 en escritorio y la misma
vista en una ventana estrecha, con el menú abierto. Después se continúa con el
panel de Puerto Umbral y teclado. No hace falta repetir las pantallas ya
aportadas para afirmar sus resultados anteriores.

La captura visual no demuestra por sí sola navegación por teclado. Para esa
parte se necesita la observación del propietario sobre foco, Escape y acceso a
los controles. No se enviarán formularios de configuración, ni se abrirán
credenciales. Los enlaces externos de autoría se pueden revisar primero en el
código; su apertura manual no se da por realizada.

## Registro de resultados

Para cada incidencia anotar aplicación, vista, tamaño aproximado de ventana,
acción y efecto observado. Conservar la captura y describir qué impide leer o
usar la pantalla. Si se corrige código, registrar el cambio y la comprobación
pertinente antes de marcar la incidencia como resuelta.

Exportar una evidencia existente es un recorrido separado que crea un archivo
local. Todavía no se ha realizado en esta revisión; tampoco requiere generar
un caso nuevo. Se conserva pendiente en UX-01.

## Alcance del cierre

Esta revisión contribuye al bloque de producto C-05/UX-01. No sustituye las
validaciones funcionales, operativas o de evaluación que figuran en la
[auditoría de cierre](PUERTO_UMBRAL_AUDITORIA_CIERRE_2026_10_31.md).
La base V2 y el laboratorio mantienen sus evidencias y límites por separado.
