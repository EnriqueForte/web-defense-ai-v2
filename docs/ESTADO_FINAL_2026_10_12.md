# Estado para la entrega final — 12/10/2026

Este es el resumen vigente. Las actas fechadas anteriores conservan sus pruebas
y límites históricos; sus pendientes pueden haberse cerrado después.
Última revisión del estado: 18/10/2026.

## Completado

- Migración de interfaz y rediseño SOC; Flask conservado como retorno local.
- Instalación y build con una orden, arranque Flask/Next con otra y cierre por Ctrl+C.
- Clon/instalación limpia y CI Windows/Ubuntu; validación guiada Parrot7.3/VMware.
- Corrección de comprobación de puertos y aceptación del recorrido en Parrot.
- Contrato inicial de 158 pines/inventario completo y uvloop Linux aprobados en Parrot.
  La [migración posterior CrewAI](MIGRACION_CREWAI_2026_10_12.md) pasó Windows/Ubuntu
  desde instalación nueva con 172 pines. El 13/10 el usuario acreditó actualización,
  inventario 172/0/0, arranque/cierre y navegación correcta en su VM Parrot.
- Código y evidencias publicados en el repositorio V2; original independiente.
- Validación numérica del ejecutor y [recorrido E2E de Configuración](CONFIGURACION_E2E_2026_10_13.md):
  nueve casos Chromium en Windows/Ubuntu CI, con guardado sintético, recarga,
  desmontaje/cancelación, errores y cierre de puertos comprobados el 13/10.
- [Operación/recuperación de aplicación](OPERACION_RECUPERACION_2026_10_14.md):
  guía, copia de 76 archivos/12 diagnósticos y restauración aislada con datos
  Windows, filas/entregas/publicación preservadas y CI Windows/Ubuntu propia.
  Volúmenes DVWA/buzón Mailpit y promoción en vivo tienen alcance separado.
- Recorrido guiado en Parrot de captura DVWA, análisis y lectura del informe,
  aceptado el 15/10 para la muestra XSS/fuerza bruta. El trabajo `4ca7c97703a4`
  publicó XSS en la línea 31 y fuerza bruta con las ocho referencias 39–46,
  coherentes con Resumen y Reportes. Véanse [evidencia y límites](INCIDENCIA_GROQ_413_2026_10_15.md):
  ambas entradas requieren investigación; no acreditan explotación exitosa ni
  calidad general del modelo. La autorización del ensayo está consumida.
- [Caché de tokenizadores empaquetados](TOKENIZADORES_OFFLINE_2026_10_16.md):
  carga BPE en frío corregida y verificada con backend Python real en CI
  Windows/Ubuntu, código `976af10`/run38886025823. Conserva cl100k/p50k/o200k;
  nueve pruebas nuevas y contratos/inventarios 172/0/0 comprobados. El primer
  fallo de CI por rutas de fixtures está registrado junto con su corrección.
- [Actualización de Mailpit](SEGURIDAD_RESIDUAL_2026_10_16.md): versión 1.31.6
  fijada al digest escaneado y probado mediante SMTP/API sintéticos en Ubuntu.
  Comparación del 16/10: 20 hallazgos pasan a uno UNKNOWN, que se conserva.
  Código `dfcd97a`, CI Windows/Ubuntu 39120143671 y escaneo 39120143668 verificados
  el 18/10, incluidos inventarios 172/0/0. La VM y su buzón no se han actualizado.

Referencias: [inicio rápido](INICIO_RAPIDO.md), [contrato Linux](CONTRATO_LINUX_2026_10_12.md),
[validación Parrot](VALIDACION_PARROT_2026_10_12.md) y [corrección de puertos](CORRECCION_PUERTOS_2026_10_12.md).

## Pendientes de cierre

| Bloque | Trabajo restante | Evidencia de cierre |
| --- | --- | --- |
| Seguridad | [Seguimiento 16–18/10](SEGURIDAD_RESIDUAL_2026_10_16.md): seis entradas por OS en Chroma/MCP auditadas el 16/10, braces retenido; Mailpit actualizado con un aviso UNKNOWN; otras imágenes conservan avisos | Migración compatible de MCP, revisión de riesgos Chroma/braces/Mailpit y demás infraestructura, aplicación separada en Parrot y auditoría final del historial |
| Calidad A-05 | Matriz offline/CI y muestras mixed/normal/same_family verificadas; recorrido XSS/fuerza bruta aceptado en Parrot para esa muestra | Sigue pendiente la evaluación semántica general; la aceptación de las muestras no equivale a cobertura general |
| Entrega final | Consolidar documentación, revisar archivos/historial y preparar versión final GitHub | Resumen vigente, auditoría de cierre, CI final y versión/release en V2; el pendiente de caché BPE ya está publicado y verificado en su alcance |

La auditoría de archivos/historial aparece en seguridad y entrega, pero es una
misma tarea de cierre. La revisión acotada previa al push no fue exhaustiva.
No se presenta el clon de lectura como prueba del análisis real o laboratorio.

La [validación global del ejecutor](CONFIGURACION_GLOBAL_2026_10_13.md) reemplaza
las conversiones directas de `config/settings.py`: errores por variable y rechazo
antes de crear estado, con regresión offline aprobada. R-15 dispone ahora del
E2E del formulario en Chromium con Flask/proxy reales y persistencia sintética;
se cierra en ese alcance, sin acreditar uso con un proveedor real. A-05 mantiene la evaluación
semántica pendiente y la revisión del recorrido manual según
[formato manual](CORRECCION_FORMATO_MANUAL_A05_2026_10_11.md).

El 13/10 se añadió una [revisión A-05 offline reproducible](EVALUACION_OFFLINE_A05_2026_10_13.md):
13 casos con respuestas sintéticas y siete controles de rechazo/conservación de
publicación. La evaluación incorpora cobertura por pares de patrón–línea además
de familias, separando omisiones de selección y de respuesta. Esto verifica el
evaluador y las guardas; no acredita calidad del proveedor ni cierra A-05.
Código `c7df36a` publicado y [CI 38411563805](https://github.com/EnriqueForte/web-defense-ai-v2/actions/runs/38411563805)
Windows/Ubuntu completada con success; logs y artefactos A-05/inventarios revisados.
El [ensayo real autorizado del 14/10](ENSAYO_REAL_A05_2026_10_14.md) consumió
seis intentos lógicos: mixed y normal publicaron resultados verificados,
same_family falló con dos JSON inválidos. Se corrigió offline un envoltorio del
evaluador que ocultaba el formato JSON antes de los otros dos casos; no se repitió
el fallido. Corrección publicada como `6f0e549`, con
[CI 38545831374](https://github.com/EnriqueForte/web-defense-ai-v2/actions/runs/38545831374)
Windows/Ubuntu success y logs/artefactos revisados, incluidos 27 SDK offline.
Un nuevo ensayo único same_family autorizado el mismo día pasó con tres llamadas,
dos referencias SQLi cubiertas y solicitud normal sin hallazgo. Se revisaron
informe/guardas/métricas/hashes y conservación operativa. El fallo inicial sigue
registrado; los dos presupuestos se mantienen separados y sus saldos no se
reutilizan. El 15/10 se aceptó además el recorrido de ingesta y análisis en
Parrot para la muestra XSS/fuerza bruta descrita arriba; la evaluación semántica
general sigue pendiente y no se cierra A-05.

[Operación y recuperación del 14/10](OPERACION_RECUPERACION_2026_10_14.md)
añade `restore_operational.py --backup <carpeta>` para un destino nuevo aislado,
sin sustituir datos o reproducir entregas. Recibos de diagnóstico conocidos
entran ahora en la cobertura del respaldo. Parrot acredita por capturas Docker
respondiendo y Compose independiente validando el archivo (salida 0), desde
`e5af1a6` en la evidencia del 14/10. El recorrido posterior del 15/10 acredita
laboratorio/ingesta/análisis para la muestra guiada; la restauración en esa VM
no se ha acreditado.
Código `4cb1707`, [CI 38552056806](https://github.com/EnriqueForte/web-defense-ai-v2/actions/runs/38552056806)
Windows/Ubuntu success; logs y artefactos/inventarios revisados. La VM recibió
después `88e7b8a` y completó el ensayo guiado. Otro análisis real necesitaría
un alcance nuevo; no se reutiliza la autorización consumida.

## Seguridad en curso

Las [auditorías del 16/10](SEGURIDAD_RESIDUAL_2026_10_16.md) sobre los 172 pines
completos mantienen seis entradas/cinco IDs por OS en Chroma/MCP; producción
frontend sin avisos y braces de desarrollo con uno alto. MCP necesita una
migración compatible con CrewAI; la ausencia de caminos de servidor observados
no suprime los avisos. Mailpit se actualizó en el repositorio al digest probado,
con un UNKNOWN residual confirmado en el escaneo del 18/10. Las seis referencias
de imágenes conservan hallazgos. MariaDB cambió de digest entre ambos escaneos;
la diferencia de conteos no se atribuye solo a la DB. No se declara cierre global
de seguridad ni actualización operativa de la VM. Los resultados del 12/10 se
conservan como historia en el [acta inicial](SEGURIDAD_2026_10_12.md).

La CSP completa de scripts Next, retención automatizada, soporte de otras
arquitecturas/macOS y funcionamiento como servicio de sistema son mejoras
adicionales condicionadas al alcance; no se añaden como requisitos para terminar
la versión local actualmente acordada.
