# V2 y Puerto Umbral — revisión de producto

Estado consolidado al 02/11/2026, Europe/Madrid. **Revisión básica de ambas
interfaces completada dentro del recorrido observado y confirmado por el
propietario.** Esta versión sustituye las instrucciones intermedias que aún
pedían pantallas recibidas después. No solicita repetirlas.

El [resumen de entrega](PUERTO_UMBRAL_ENTREGA_2026_11_02.md) concentra los
pendientes vigentes. La [cronología de cierre](CIERRE_V2_PUERTO_UMBRAL_2026_11_03.md)
conserva las recepciones y acuerdos anteriores. La revisión usa las capturas y
confirmaciones del propietario en Parrot; el agente no controla la VM.

## Distribución de escritorio

La entrega `cd6b34d1e87b6382cfd24856a19afce2f485dcd5` redistribuyó el Resumen
de V2 para aprovechar el ancho disponible. Desde 1600 px, gráficas y reportes
comparten fila, con amenazas y terminal debajo; desde 1000 px se distribuyen
en dos columnas por bloques y en tamaños menores se apilan. Las vistas de
detalle mantienen su ancho de lectura.

Las vistas previas muestran hasta cuatro amenazas, seis últimas líneas de la
ventana de log y dos reportes históricos, con cantidades y enlaces al detalle.
No se recorta el archivo original. Se conserva la tipografía base y el
desplazamiento natural, sin imponer una altura global fija.

La compilación de producción webpack, TypeScript, generación de rutas y
ESLint de la página pasaron antes de publicar ese cambio. Después, la captura
del propietario a zoom 60 % mostró la nueva distribución en Parrot. Informó
que a 100 % seguía necesitando desplazamiento y priorizó la legibilidad.

**Se mantiene el diseño actual y se recomienda zoom 100 % con desplazamiento
vertical natural.** No se acredita encaje completo sin scroll a 100 % ni se
propone reducir más los textos para conseguirlo.

## Vista estrecha y navegación recibidas el 01/11

Firefox Responsive permitió revisar un viewport de 390 × 844 px, DPR 1,
sin cambiar la configuración de ventanas de Parrot. Es una vista adaptable
del navegador, no una comprobación en un teléfono físico. Las capturas
posteriores conservan ese contexto, aunque no todas muestran sus dimensiones.

| Aplicación / recorrido | Evidencia recibida | Resultado y límite |
| --- | --- | --- |
| V2: menú | Menú abierto con marca, cinco vistas, selección activa y panel de fuentes | Disposición legible; propietario confirma foco con Tab/Mayús+Tab y cierre con Escape con devolución al botón de menú |
| V2: cinco vistas | Resumen, Amenazas, Reportes, Actividad y Configuración | Navegación básica observada; no evaluación de todos los controles |
| V2: informe | `report.md` anterior abierto con texto ajustado dentro del panel | Lectura visible; conserva publicación de 27/10 y alcance de 17 líneas, sin análisis nuevo |
| V2: fuente y configuración | Amenazas identifica Puerto Umbral; Actividad muestra captura antigua, modo y fechas; Configuración presenta Groq y catálogo | Estados visibles en las zonas mostradas; no se guardan formularios ni se verifica la clave contra el proveedor |
| Puerto Umbral: presentación | Marca, navegación horizontal, autoría, cabecera y formulario | Bloques mostrados legibles; su navegación estrecha usa tira horizontal, no el menú de V2 |
| Puerto Umbral: historial | Lista Ejecuciones y evidencia, con columnas visibles de ejecución, escenario y modo | Lectura básica observada; no acredita recorrido de todas las columnas ni resultados funcionales de sus filas |
| Puerto Umbral: foco | Propietario indica «Paso 3 sí se distingue» tras solicitar observar el control seleccionado | Se interpreta como confirmación del foco visible en ese recorrido; no prueba general de accesibilidad |

El historial incluye Baliza vulnerable con prefijo `525a2076b8ae`. La fila
acredita su presencia, sin aportar HTTP, efecto o recibo para evaluarlo. Su
resultado funcional sigue sin recibirse; no se cuenta como caso aprobado ni
se concluye que nunca se ejecutó. No se solicita abrirlo o repetirlo por esta
revisión visual.

## Alcance completado y cobertura adicional

La revisión básica de navegación, presentación estrecha y foco termina en el
alcance anterior. No se detecta en las capturas aportadas una incidencia nueva
que justifique otro cambio de frontend. Esto no certifica accesibilidad global.

Quedan **sin observar**, como cobertura adicional del plan de producto:

- Zoom 200 %, dispositivo físico y recorrido exhaustivo de controles/columnas.
- Exportación de una evidencia existente y consulta móvil de recibos individuales.
- Apertura manual de todos los enlaces externos de autoría.

El PRD requiere revisión del propietario, incluido móvil y teclado; no fija
estas comprobaciones adicionales como una nueva cuota de salida. Se mantienen
visibles, sin presentarlas como superadas ni imponerlas automáticamente como
bloqueadores nuevos. Si la revisión final exige alguna por una incidencia
concreta, se define su alcance antes de realizarla.

Consultar ciertos recibos de Puerto Umbral monta un iframe y puede generar
peticiones o ejecución del contenido del laboratorio. Esa acción queda fuera
del recorrido visual realizado. Exportar crea un archivo local. Ninguna se
considera ejecutada por haber observado sus botones o enlaces.

## Uso actual y documentación

El lanzador conjunto vigente es `python3 webdefensev2.py`, con fuente V2
corregida por defecto. `--enable-manual` habilita el ejecutor que espera
solicitudes; el arranque no solicita un análisis. Ambos modos y el retorno a
lectura se observaron por separado según el
[manual local](PUERTO_UMBRAL_OPERACION_LOCAL.md). No requieren repetir las
pantallas para esta consolidación.

Esta revisión contribuye a C-05/UX-01. Los criterios funcionales, operativos,
de evaluación y la decisión final del propietario se revisan en la
[auditoría de cierre](PUERTO_UMBRAL_AUDITORIA_CIERRE_2026_10_31.md).
La recepción de pantallas no acepta por sí sola F0–F7 ni autoriza una release.
