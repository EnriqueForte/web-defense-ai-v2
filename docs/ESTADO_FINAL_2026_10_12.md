# Estado para la entrega final — 12/10/2026

Este es el resumen vigente. Las actas fechadas anteriores conservan sus pruebas
y límites históricos; sus pendientes pueden haberse cerrado después.
Última revisión del estado: 20/10/2026. El [análisis de cierre](ANALISIS_CIERRE_2026_10_20.md)
separa los pendientes actuales de las actas históricas y propone su orden finito.

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
- [Revisión de dependencias y secretos del 18/10](REVISION_DEPENDENCIAS_SECRETOS_2026_10_18.md):
  conflicto MCP corregido/CrewAI reproducido sin instalar; revisión de constructores
  legacy/structured sin llamadas; escaneo con Gitleaks y triage individual.
  El fixture DVWA sustituye un valor CSRF opaco por datos explícitamente sintéticos.
  Conserva el hallazgo histórico de procedencia no acreditada; código `31c8a29`,
  CI39122621402 Windows/Ubuntu aprobada y logs/inventarios/A-05 verificados.
- [Fijación del laboratorio por digest](FIJACION_IMAGENES_LAB_2026_10_19.md):
  MariaDB/DVWA fijados y Mailpit conservado; el escáner rechaza otro digest.
  Código `2d2f197`, CI39229681306 y escaneo39229681189 aprobados y artefactos
  verificados el 19/10. Cierra reproducibilidad del repositorio, con avisos
  conservados; no acredita actualización de Parrot o migración de su volumen.
- Documentación consolidada localmente el 20/10: README y guías con estado
  comprobado, instalación/lectura/análisis separados y backlog A-01–A-04
  actualizado. Cronologías conservadas en archivos históricos enlazados.
  La [matriz de aceptación A-05](MATRIZ_ACEPTACION_A05_2026_10_20.md) reúne las
  muestras y límites en 12 criterios y cuatro decisiones. C1 queda consolidada;
  su publicación quedó incluida después en el código de entrega C4.
- A-05/C2 aceptada por el usuario el 20/10 para la primera versión local de
  apoyo a la revisión de indicadores, con límites explícitos y comparación
  legacy diferida. [Revisión y decisión](REVISION_ACEPTACION_A05_2026_10_20.md):
  doce recibos/once publicaciones sintéticas, 56 archivos preservados y tres
  narrativas/Markdown E2 iguales a la política actual. No se realizaron llamadas
  nuevas. No se certifica calidad general, resistencia LLM o superioridad frente
  a legacy; `quality=semantic_evaluation_pending` permanece en los resultados.
- C3 cerrado el 20/10 por aceptación expresa del [tratamiento de riesgos](TRATAMIENTO_RIESGOS_C3_2026_10_20.md)
  para uso personal local aislado. Se conservan los avisos residuales y sus
  límites. El parche aiohttp/yarl pasó las comprobaciones locales y posteriormente
  CI nueva Windows/Ubuntu, según C4. La aceptación C3 no
  certifica seguridad global ni autoriza una release o cambios en la VM.
- [Entrega C4 v0.1.0](ENTREGA_LOCAL_C4_2026_10_20.md): código `0d73ec2`,
  CI39466610699 intento 1 aprobada en Windows/Ubuntu. Logs finales, dos inventarios
  172/0/0 y 25 publicaciones sintéticas completas/101 archivos por OS verificados;
  376 casos Python por OS (Windows: 375 aprobados y uno Linux omitido), tres JS,
  101 sintaxis, 27 SDK, 17 UI, nueve E2E y arranque/proxy/cierre correctos.
  Notas e identidad de distribución vinculadas al código probado; solo actas
  posteriores, sin nueva CI atribuida a esos commits documentales.

Referencias: [inicio rápido](INICIO_RAPIDO.md), [contrato Linux](CONTRATO_LINUX_2026_10_12.md),
[validación Parrot](VALIDACION_PARROT_2026_10_12.md) y [corrección de puertos](CORRECCION_PUERTOS_2026_10_12.md).

## Pendientes de cierre

| Bloque | Trabajo restante | Evidencia de cierre |
| --- | --- | --- |
| V1, si se incluye actualizar Parrot | Actualizar y acreditar conservación/recuperación de los datos de la VM con los pines actuales | Respaldo DB verificado y exportación de correo necesaria antes de recrear; prueba de recuperación separada. No es una actualización ya realizada por la entrega C4 |

La auditoría de archivos/historial aparece en seguridad y entrega, pero es una
misma tarea de cierre. La revisión acotada previa al push no fue exhaustiva.
No se presenta el clon de lectura como prueba del análisis real o laboratorio.

La [validación global del ejecutor](CONFIGURACION_GLOBAL_2026_10_13.md) reemplaza
las conversiones directas de `config/settings.py`: errores por variable y rechazo
antes de crear estado, con regresión offline aprobada. R-15 dispone ahora del
E2E del formulario en Chromium con Flask/proxy reales y persistencia sintética;
se cierra en ese alcance, sin acreditar uso con un proveedor real. A-05 tiene
aceptación local según la matriz enlazada, sin certificar el proveedor. La corrección de
[formato manual](CORRECCION_FORMATO_MANUAL_A05_2026_10_11.md) conserva su
historia; las muestras posteriores del 14/15 acreditan sus recorridos concretos.

El 13/10 se añadió una [revisión A-05 offline reproducible](EVALUACION_OFFLINE_A05_2026_10_13.md):
13 casos con respuestas sintéticas y siete controles de rechazo/conservación de
publicación. La evaluación incorpora cobertura por pares de patrón–línea además
de familias, separando omisiones de selección y de respuesta. Esto verifica el
evaluador y las guardas; por sí sola no acredita calidad del proveedor ni fue
el cierre de A-05, aceptado posteriormente para el alcance local descrito arriba.
La [ampliación de contexto del 19/10](EVALUACION_CONTEXTO_A05_2026_10_19.md)
añade nueve escenarios y un control de referencias entre IP: 22 casos/ocho
controles aprobados en Windows/Ubuntu CI39233803582, código `a46e21c`, conservando
las nueve entradas y los resultados de los 13 casos previos. Se descargaron las
23 publicaciones completas de cada OS (93 archivos), verificando manifiestos,
bytes JSON/Markdown iguales a la revisión local y métricas recomputadas. Esta
evidencia sintética no cierra la evaluación semántica del proveedor.
La revisión original del 13/10 se publicó como `c7df36a`, con
[CI 38411563805](https://github.com/EnriqueForte/web-defense-ai-v2/actions/runs/38411563805)
Windows/Ubuntu success; logs y artefactos A-05/inventarios revisados.
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
Parrot para la muestra XSS/fuerza bruta descrita arriba. La aceptación local
se cerró después el 20/10 sin extrapolar a calidad semántica general.

La [evaluación de grupos del 19/10](EVALUACION_GRUPOS_A05_2026_10_19.md) corrige
una carencia de medición: dividir una ráfaga podía conservar todos los pares
pero aumentar el contador de hallazgos. Añade métricas de partición exacta según
etiquetas de fixture y un CLI para revisar publicaciones existentes sin proveedor.
24 casos/ocho controles aprobados y publicados como `ca2f6af`, CI39239742802
Windows/Ubuntu aprobada y verificada el 20/10. Se revisaron las 25 publicaciones
completas por OS (101 archivos), hashes, bytes JSON/Markdown iguales a la matriz
local y métricas recomputadas. Ubuntu: 374 Python; Windows: 373 aprobadas y una
exclusiva Linux omitida; tres JS, 100 sintaxis, 27 SDK, 17 UI y nueve E2E por OS.
No cambia las reglas del motor ni demuestra calidad semántica general.

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

## Seguridad: tratamiento aceptado y avisos conservados

La [revisión del 20/10](TRATAMIENTO_RIESGOS_C3_2026_10_20.md) actualiza el estado:
la auditoría de los freezes CI anteriores añade tres avisos de aiohttp (nueve
entradas por OS). El parche local aiohttp3.14.4/yarl1.25.1 deja seis entradas
en el inventario Windows probado y en la proyección Linux, que no es ejecución
Linux. El usuario aceptó expresamente el tratamiento residual para uso local
aislado el 20/10; C3 queda cerrado en ese alcance, con los avisos conservados.
La CI nueva se verificó posteriormente en C4, sobre código `0d73ec2`. Los párrafos
siguientes conservan las revisiones anteriores y sus fechas.

La [fijación de MariaDB/DVWA por digest](FIJACION_IMAGENES_LAB_2026_10_19.md) está
publicada y verificada el 19/10, con paridad Compose/inventario y rechazo de otro
digest. El escaneo conserva los avisos. DVWA, con el mismo ImageID del 18/10,
presenta 347 entradas Debian UNKNOWN adicionales (total 4011); no se atribuyen
a un cambio de contenido ni son correcciones aplicadas. La aplicación a la VM
y la migración de su volumen no se han ejecutado ni acreditado.

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

La [consulta del 18/10](REVISION_DEPENDENCIAS_SECRETOS_2026_10_18.md) repite esos
audits con los inventarios CI39120143671: mismos resultados y sin cambios de
paquetes. El resolutor confirma que CrewAI publicado aún impide MCP corregido.
Gitleaks amplía la búsqueda por patrones y conserva los hallazgos: hashes públicos
y una muestra CSRF histórica de procedencia no acreditada, anonimizada en el
fixture actual. No se declaran eliminados los avisos ni seguridad global cerrada.

La CSP completa de scripts Next, retención automatizada, soporte de otras
arquitecturas/macOS y funcionamiento como servicio de sistema son mejoras
adicionales condicionadas al alcance; no se añaden como requisitos para terminar
la versión local actualmente acordada.
