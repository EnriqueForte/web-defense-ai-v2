# Puerto Umbral — desarrollo F2/F3 y revisión manual

Fecha: 26/10/2026. Continuación del [PRD](PRD_PUERTO_UMBRAL_2026_10_26.md)
y de la [entrega visual F1](PUERTO_UMBRAL_F1_2026_10_26.md).

El propietario confirma el carácter educativo, solicita detener las pruebas
automáticas y continuar el desarrollo para revisar después la web. Esa
restricción sigue vigente: no se ejecutan suites, nuevos escenarios, capturas,
análisis LLM ni recorridos automatizados como parte de esta continuación.

## Estado real

| Bloque | Desarrollo | Validación |
| --- | --- | --- |
| F1 | Prototipo privado publicado en Sites | Comprobaciones visuales previas conservadas; sin nuevo despliegue |
| F2 | Portal, panel y cinco escenarios en ambos modos implementados | Primer corpus: 42/45 conformes; tres fallos retenidos; validación incompleta |
| Corrección F2 | Ajustado el límite de procesos para evitar interferencia entre UID de contenedores | Fuente corregida, sin nueva construcción ni repetición del corpus |
| F3 | Capturador, perfil, APIs, vista Actividad y vínculo trabajo/snapshot desarrollados | Sin ejecución ni compilación; revisión manual y recorrido completo pendientes |
| F4/F5 | Seguimiento y aceptación de la entrega | No iniciados |

F2 no se marca cerrada y F3 no se presenta como integración verificada. Continuar
el código de F3 no acredita resultados que el usuario ha pedido aplazar.

## Conservación de F2

La fuente local independiente se encuentra en el checkout indicado en el
registro F1; incluye `lab/README.md` con operación y límites. Se construyeron y
arrancaron doce contenedores propios en Docker Desktop para Linux en Windows.
Se verificó su configuración y se corrigió la publicación efectiva en loopback
de las pasarelas, conservando los escenarios sin red IP.

El primer corpus HTTP fijo quedó en 42/45: tres variantes del escenario de
comandos no produjeron el efecto esperado por un límite de procesos por UID.
La corrección de fuente conserva el techo de procesos por contenedor. No se ha
reconstruido esa versión ni repetido sus casos. La observación XSS por HTTP no
demuestra ejecución en navegador: esa comprobación y las verificaciones negativas
de límites/aislamiento siguen pendientes.

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
No se abrió ningún servicio de V2 durante esta continuación. Las rutas creadas
son código pendiente de revisión; no evidencia de APIs ya ejecutadas.

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

## Recorrido manual preparado, todavía no ejecutado

Estos pasos quedan para cuando el propietario quiera revisar la web. Se usarán
Puerto Umbral y V2 en el mismo equipo/contexto Docker. No describen una ejecución
en Parrot ya realizada.

1. Preparar y abrir el panel F2 siguiendo su `lab/README.md`. No ejecutar comandos
   `check-*`. La preparación de servicios no recorre el corpus de pruebas.
2. En V2, iniciar únicamente Flask con el perfil de lectura nuevo, desde la raíz:

   ```powershell
   .\.p2\Scripts\python.exe -B scripts/local_runtime_profile.py --profile puerto-umbral --mode structured --lab-mode vulnerable --component flask --start
   ```

3. En otra terminal, preparar el frontend cuando proceda y abrirlo. Los cambios
   nuevos aún no se han compilado:

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

La captura CLI también queda preparada en el nuevo módulo, pero no se ha
ejecutado. El botón de la web es el recorrido de revisión preferido acordado.

## Pendientes de aceptación

- Construir y revisar manualmente la corrección de F2, junto con las observaciones
  de navegador pendientes. No sustituir los resultados históricos 42/45.
- Compilar el frontend y comprobar la interacción real del panel de fuente.
- Revisar captura válida, fallo conservando anterior, modo cambiado y copia antigua.
- Cuando se autorice expresamente, comprobar un trabajo real con su snapshot y
  publicación. No atribuir por adelantado validación a proveedor, modelo o detector.
- Revisar regresión de perfiles anteriores y recuperación del nuevo perfil.
- Registrar resultados manuales antes de considerar cumplidos F3-AC1–AC4.

Los cambios permanecen locales, sin commit/push, CI, release ni modificación del
Site alojado. No se han ejecutado nuevas pruebas automáticas tras la restricción
del propietario, ni se han leído claves del `.env` operativo.
