# Puerto Umbral — desarrollo F2/F3 y revisión manual

Fecha: 26/10/2026. Continuación del [PRD](PRD_PUERTO_UMBRAL_2026_10_26.md)
y de la [entrega visual F1](PUERTO_UMBRAL_F1_2026_10_26.md).

El propietario confirma el carácter educativo, solicita detener las pruebas
automáticas y continuar el desarrollo para revisar después la web. Esa
restricción sigue vigente: no se ejecutan suites, nuevos escenarios, capturas,
análisis LLM ni recorridos automatizados como parte de esta continuación.

**Actualización posterior:** se realizó una revisión manual parcial por el
propietario en Parrot, documentada en la [guía de operación](PUERTO_UMBRAL_PARROT_2026_10_26.md).
La ronda se da ahora por finalizada, sin solicitar más casos. El [estado
consolidado](PUERTO_UMBRAL_ESTADO_ACTUAL_2026_10_26.md) distingue esas observaciones
de las verificaciones aplazadas y prepara el alcance de desarrollo F4.
La [implementación F4 del 27/10](PUERTO_UMBRAL_F4_2026_10_27.md) añade seguimiento
explícito sin ejecutar ciclos o reabrir la ronda de pruebas.

## Estado real

| Bloque | Desarrollo | Validación |
| --- | --- | --- |
| F1 | Prototipo privado publicado en Sites | Comprobaciones visuales previas conservadas; sin nuevo despliegue |
| F2 | Portal, panel y cinco escenarios en ambos modos implementados y distribuidos dentro de V2 | Corpus histórico 42/45 conservado; variante 1 de SQL/XSS/traversal comparada manualmente en Parrot; comandos corregido observado; validación incompleta |
| Corrección F2 | Ajustado el límite de procesos para evitar interferencia entre UID de contenedores | Corrección incluida en la fuente distribuida; comportamiento vulnerable de comandos no revisado de nuevo |
| F3 | Capturador, perfil, APIs, vista Actividad y vínculo trabajo/snapshot desarrollados; arranque conjunto incluido | Frontend compilado con Webpack en Windows; captura y lectura manual observadas en Parrot, en ambos modos; recorrido hasta informe pendiente |
| F4 | Seguimiento local, API, controles UI y checkpoint implementados el 27/10; publicación autorizada | Compilación y revisión estática correctas; revisión operativa guiada autorizada, aún pendiente |
| F5 | Evidencia parcial consolidada | Evaluación completa y aceptación pendientes |

F2 y F3 no se marcan cerradas. Se acredita parcialmente la captura/lectura de F3,
sin presentar como verificado su recorrido completo ni los resultados aplazados.

## Conservación de F2

La fuente local independiente inicial se encuentra en el checkout indicado en el
registro F1. Posteriormente se distribuyó una copia portable en
[labs/puerto_umbral](../labs/puerto_umbral/README.md), junto con V2, para actualizar
Parrot con un único repositorio. Se construyeron y
arrancaron doce contenedores propios en Docker Desktop para Linux en Windows.
Se verificó su configuración y se corrigió la publicación efectiva en loopback
de las pasarelas, conservando los escenarios sin red IP.

El primer corpus HTTP fijo quedó en 42/45: tres variantes del escenario de
comandos no produjeron el efecto esperado por un límite de procesos por UID.
La corrección de fuente conserva el techo de procesos por contenedor. No se ha
repetido ese corpus ni verificado de nuevo el caso vulnerable de comandos.
En la ronda manual posterior, una variante XSS vulnerable sí confirmó ejecución
en navegador y su comparación corregida mostró codificación y texto literal.
Esa observación no sustituye al resto de variantes ni a las verificaciones
negativas de límites/aislamiento pendientes.

Tras la petición de parar las pruebas se detuvieron únicamente los doce servicios
Puerto Umbral. La orden devolvió `evidence_preserved=true` y
`volumes_removed=false`. No se alteraron servicios DVWA ni datos de la VM.

## Cambios de F3

- [Capturador local](../dashboard/services/puerto_umbral_capture.py): modo explícito,
  identidad de pasarela comprobada al capturar, formato Apache validado, ventana
  acotada y generaciones con SHA-256. Solo usa Docker inspect/logs; no ejecuta
  peticiones contra el portal ni arranca contenedores.
- [Perfil](../scripts/local_runtime_profile.py) `puerto-umbral`: rutas propias de
  log, informes y SQLite; requiere modo `structured`; análisis manual y avisos
  desactivados por defecto. `--lab-mode` elige qué pasarela leer, sin cambiarla.
- [Coordinador](../pipeline.py): el futuro trabajo consume el snapshot concreto
  devuelto por su ingesta y comprueba el hash; un registro separado vincula
  `analysis_id`, snapshot y digest. No depende de que la copia visible permanezca
  sin cambios durante el análisis.
- [API](../dashboard/openapi-v1.json): lectura de metadatos y captura manual
  explícita. Se conservan restricciones de origen local y exclusión entre operaciones.
- [Vista de fuente](../frontend/src/components/log-source-panel.tsx) en Actividad:
  fecha, modo, líneas, snapshot, hash y captura sin iniciar análisis.
- Respaldo/restauración: el nuevo perfil incluye los archivos de captura admitidos,
  sus generaciones y referencias por trabajo. La opción CLI `all` abarca ahora
  también este perfil; las rutas de legacy y pilot conservan sus valores.

No se modificó el detector ni se añadieron categorías nuevas de vulnerabilidad.
Durante el desarrollo inicial de F3 no se abrieron servicios de V2. Más tarde,
el propietario confirmó el arranque en Parrot y aportó imágenes de la captura
manual, metadatos y Actividad. Se conserva esa distinción entre implementación,
observación manual y recorrido de análisis todavía pendiente.

## Contrato de captura

Rutas propuestas por la implementación:

```text
.local-state/puerto-umbral/
  access.log
  current.json
  last-attempt.json
  snapshots/<snapshot_id>/access.log
  snapshots/<snapshot_id>/receipt.json
  analysis-inputs/<analysis_id>.json
  reports/
  analysis.sqlite3
```

El capturador conserva generaciones anteriores y publica mediante escrituras
atómicas por archivo. El puntero y la copia visible son archivos distintos: si
una interrupción los deja desparejados, la lectura debe indicar el desajuste,
sin prometer una transacción entre archivos. Un fallo no destruye los snapshots
anteriores. El vínculo del análisis registra el snapshot inmutable elegido.

Se solicitan las últimas 1.000 líneas retenidas de una sola pasarela; la entrada
publicada se limita a 1 MiB y declara las líneas omitidas de esa ventana. No se
afirma cobertura completa del historial ni retención de Docker. Los metadatos
del evaluador F2 no se mezclan con el log que recibirá V2.

`GET /api/v1/fuentes/log` solo lee archivos locales. Distingue ausencia, captura
antigua, desajuste, cambio de modo y error. La fecha de captura no equivale a la
fecha de la última petición ni confirma que el contenedor siga arrancado.

`POST /api/v1/fuentes/log/capturar` requiere el perfil habilitado y el ejecutor
detenido. No llama al modelo, no encola análisis y no envía avisos. Si más adelante
se autoriza un análisis manual, será una operación separada con su alcance y
presupuesto; no se ha habilitado en esta entrega.

## Recorrido de preparación inicial (histórico)

Estos pasos documentan la preparación anterior al arranque conjunto. No deben
interpretarse como una nueva solicitud de ejecución tras finalizar la ronda.
La guía de Parrot y el estado consolidado enlazados al inicio recogen la
distribución posterior y las observaciones efectivamente aportadas.

1. Preparar y abrir el panel F2 siguiendo su `lab/README.md`. No ejecutar comandos
   `check-*`. La preparación de servicios no recorre el corpus de pruebas.
2. En V2, iniciar únicamente Flask con el perfil de lectura nuevo, desde la raíz:

   ```powershell
   .\.p2\Scripts\python.exe -B scripts/local_runtime_profile.py --profile puerto-umbral --mode structured --lab-mode vulnerable --component flask --start
   ```

3. En otra terminal, preparar el frontend cuando proceda y abrirlo. En el momento
   de esta preparación los cambios aún no se habían compilado:

   ```powershell
   cd frontend
   pnpm run build
   pnpm run start
   ```

4. Abrir V2 en `http://127.0.0.1:3000`, entrar en Actividad y leer el estado de
   la fuente. Abrir el portal F2 por separado y generar primero navegación normal
   manual. No hay escenario automático al cambiar una selección o abrir una página.
5. Pulsar «Capturar log de Puerto Umbral» y después «Actualizar» para releer la
   actividad. Revisar modo, fecha, líneas y referencia del snapshot. No iniciar
   worker ni usar habilitación de análisis en este recorrido.
6. Para leer la pasarela corregida, detener Flask y reiniciar el mismo perfil con
   `--lab-mode corrected`. La interfaz debe señalar una captura del modo anterior
   hasta realizar una captura de la selección nueva.
7. Al terminar, Ctrl+C en los procesos propios y la orden `labctl.py stop` indicada
   en la guía del laboratorio. Conservar recibos, snapshots y datos anteriores.

La captura CLI también quedó preparada en el nuevo módulo, sin ejecución
acreditada. El botón de la web fue el recorrido utilizado en la ronda posterior.

## Pendientes de aceptación

- Completar las verificaciones funcionales de F2 aplazadas, incluida la corrección
  del caso vulnerable de comandos. No sustituir el resultado histórico 42/45.
- Conservar la compilación Webpack de Windows y la interacción del panel de fuente
  observada en Parrot como evidencias parciales, sin atribuirles una nueva CI.
- Completar la revisión de errores, conservación de la captura anterior, cambios
  de modo y copia antigua; la captura válida ya se ha observado en ambos modos.
- Cuando se autorice expresamente, comprobar un trabajo real con su snapshot y
  publicación. No atribuir por adelantado validación a proveedor, modelo o detector.
- Revisar regresión de perfiles anteriores y recuperación del nuevo perfil.
- Registrar resultados manuales antes de considerar cumplidos F3-AC1–AC4.

La fuente y el arranque conjunto se publicaron en `fdffd08`, con corrección de
construcción Docker en `abab01d`. El propietario autoriza posteriormente publicar
las nuevas actas manuales y F4 para la revisión operativa guiada. No se atribuyen
nueva CI, release o modificación del Site alojado. No se han ejecutado nuevas
pruebas automáticas tras la restricción del
propietario, ni se han leído claves del `.env` operativo. Los pendientes no
constituyen una solicitud de reabrir pruebas: quedan aplazados por la decisión
actual y no se dan por cumplidos.
