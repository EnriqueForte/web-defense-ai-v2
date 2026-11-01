# Puerto Umbral — medición operativa acotada F4

Preparado el 02/11/2026. **Observador desarrollado; cinco comprobaciones
aisladas ejecutadas con permiso y correctas; medición en Parrot no realizada.**
La sesión antigua está interrumpida e inactiva según la respuesta actual de V2.
No se modifican el servicio de seguimiento, la interfaz o los logs para medir.

## Entrega versionada

El propietario autoriza commit/push del observador, sus cinco pruebas y la
documentación acumulada: trece archivos, once Markdown y dos Python, con
`[skip ci]`. Base `91a101e` coincidente con `origin/main` tras fetch y staging
inicial vacío. La entrega se identifica por el commit que incorpora esta nota;
su publicación se verifica contra HEAD remoto al terminar Git, sin anticiparla.
No se crea una release ni se autoriza una sesión real por publicar la fuente.

En Parrot se conserva cualquier cambio local y se actualiza con
`git pull --ff-only`. Solo se añaden el observador/pruebas y actas; no requiere
recompilar frontend, reinstalar dependencias o reiniciar los servicios ya
abiertos. Antes de la medición se confirma que el archivo ya está recibido y
se acuerda la sesión manual acotada; las pruebas simuladas no la sustituyen.

## Acción preparada para revisar

El [observador](../scripts/observe_puerto_umbral_follow.py) recoge veinte ciclos
distintos de **una sesión nueva que inicia el propietario desde Actividad**:
intervalo de cinco segundos, duración de cinco minutos y modo corregido.
Debe iniciarse el observador antes del seguimiento para fijar la referencia.

Su ayuda y el inicio explícito son:

```bash
.p2/bin/python -B scripts/observe_puerto_umbral_follow.py --help
.p2/bin/python -B scripts/observe_puerto_umbral_follow.py --observe
```

Esta receta queda preparada; no solicita ejecutarla antes de recibir el archivo
en Parrot y acordar la sesión. Sin `--observe` solo muestra ayuda. No importa
Flask, el pipeline o la configuración del proveedor, ni carga `.env`.

| Límite | Comportamiento |
| --- | --- |
| Transporte | Solo GET a `http://127.0.0.1:3000/api/v1/fuentes/log`, sin proxy del sistema ni redirecciones; respuestas de hasta 64 KiB y timeout de dos segundos |
| Duración/cantidad | Espera hasta 180 segundos desde que anuncia estar preparado; como máximo 181 GET contando el inicial; objetivo de veinte ciclos distintos, no veinte sondeos repetidos |
| Control | No envía POST, no inicia/pausa/detiene seguimiento, no contacta Docker, portales, proveedores o notificaciones |
| Base de datos | SQLite `mode=ro`/`query_only`, transacción de lectura antes y después; cantidades y hashes de metadatos de trabajos/entregas, sin destinos o contenido de logs |
| Capturas | Cuenta directorios de snapshots antes/después; conserva los IDs/digests de los checkpoints observados; no escribe en ellos |
| Escritura | Un recibo nuevo con nombre aleatorio y apertura exclusiva en `.local-state/puerto-umbral/operational-review/`; no sobrescribe evidencias anteriores |
| Fallo/interrupción | Conserva muestras parciales, estado incompleto y causa acotada; no inventa veinte ciclos, reintenta sesiones o cambia fuentes automáticamente |

Al terminar o fallar, si inició la sesión, el propietario la detiene desde
Actividad y consulta el estado. La sesión tiene además su duración finita de
cinco minutos. El observador nunca altera el proceso para detenerla.

## Qué mide y cómo se interpreta

Cada muestra relaciona un ciclo con su inicio, fin, duración de lectura,
checkpoint y el momento en que se observa coherente por la API que usa V2.
Se registra la cota `observed_at - last_cycle_at`, que incluye el sondeo y
transporte local. Se rechaza reloj incoherente; se registran sistema/kernel,
arquitectura, CPU lógicas y carga disponible antes/después.

**Es disponibilidad observada por API, no tiempo de renderizado/pintado del
navegador.** RNF-09 exige captura visible en diez segundos con condiciones del
ensayo; no se cambia ese requisito ni se declara satisfecho automáticamente.
El recibo marca `browser_paint_measured: false` y requiere revisión del
propietario. La medición contribuye a F4-AC1; cualquier desviación debe quedar
expresamente revisada, como permite el PRD.

El resultado `observed_20_cycles` significa que se recogieron veinte muestras,
**no que toda F4 haya pasado**. Las banderas separan la cota de diez segundos,
igualdad de metadatos SQLite y estabilidad de checkpoint. Un cambio de base,
origen o condición se conserva en el resultado; no se oculta para aprobarlo.
El primer ciclo puede renovar la referencia del origen sin duplicación por
cambios de identidad/procedencia; los directorios nuevos se informan aparte.

No se generan solicitudes nuevas en los portales durante la medición. Esto
permite estudiar reutilización sin cambios, sin acreditar ingestión de tráfico
nuevo, rotación o continuidad completa del historial. La interrupción de
contenedores y modificación de logs quedan fuera de esta sesión propuesta.
El recibo nuevo tampoco amplía retroactivamente el respaldo de 113 archivos.

## Verificación del observador

Se preparan cinco pruebas en
[test_follow_observer.py](../tests/test_follow_observer.py):

- La ayuda predeterminada no inicia observación ni lee datos operativos.
- URL GET fija, redirecciones deshabilitadas y entrada excesiva rechazada.
- Lectura de SQLite temporal conserva bytes y omite campos privados.
- Veinte ciclos distintos con sondeos duplicados no inflan la muestra.
- Un fallo de lectura conserva el recibo parcial sin inventar éxito o exponer
  el detalle de una excepción.

Usan respuestas simuladas y archivos temporales, sin servicios o transporte
real. El propietario autoriza después expresamente estas cinco pruebas;
se ejecuta una vez en Windows con `.p2`, Python **3.11.9**:

```powershell
.p2/Scripts/python.exe -B -m unittest tests.test_follow_observer -v
```

Resultado **5/5 correctas, 0,085 s según unittest, exit 0**. Sintaxis de ambos
archivos revisada y ayuda ejecutada sin iniciar observación. No se amplía la
suite después de este resultado. La ejecución con datos y HTTP reales en
Parrot sigue pendiente; las pruebas simuladas no acreditan latencias de la VM,
consumo real del proveedor o aceptación F4. Publicación Git y sesión Parrot
no se presuponen por aprobar las cinco comprobaciones.
