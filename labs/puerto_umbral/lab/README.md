# Puerto Umbral — laboratorio local F2

Aplicación educativa independiente del prototipo alojado en Sites. El código del
laboratorio solo se sirve localmente. No se despliega como backend vulnerable en
el Site y no contiene credenciales de V2.

La [evaluación F5](../../../docs/PUERTO_UMBRAL_F5_2026_10_27.md) y el
[manual de operación](../../../docs/PUERTO_UMBRAL_OPERACION_LOCAL.md) recogen el
estado posterior. Parrot cuenta con compilación y ronda básica F4 observadas;
una variante XSS vulnerable confirmó ejecución en navegador. El corpus completo
y los fallos históricos conservan sus límites. Las secciones siguientes
describen la preparación inicial; no solicitan repetir pruebas ahora.

## Estado inicial al 26/10/2026 (histórico)

Implementados el portal Apache, el panel local, cinco escenarios por dos modos,
datos ficticios, recibos funcionales y límites del servidor. Diez contenedores de
escenario no tienen red IP; dos pasarelas exponen solo loopback y acceden a sus
sockets Unix mediante volúmenes propios. No hay montajes de directorios del host
en los escenarios. El panel usa un tercer origen local separado.

La primera ejecución del corpus fijo produjo 42/45 resultados funcionales
conformes. Se conservan los tres casos de comandos no conformes y sus recibos.
Su causa fue un límite de procesos por UID compartido entre contenedores. El
código pasa a utilizar el límite por contenedor ya existente (pids_limit=32),
conservando límites de CPU, memoria, salida y tiempo. Esta corrección **no se ha
reconstruido ni probado**, por petición posterior de continuar sin pruebas
automáticas. También siguen pendientes XSS en navegador y comprobaciones
negativas de aislamiento y límites. F2 no se declara validada ni cerrada.

Los doce contenedores usados anteriormente quedaron detenidos. Se conservaron
volúmenes, logs, imágenes y recibos. El sitio privado F1 sigue siendo un prototipo.

## Operación directa del laboratorio (referencia histórica)

El recorrido actual preferido es el arranque conjunto desde la raíz de V2,
documentado en el manual enlazado arriba. La preparación independiente inicial
utilizaba, desde la raíz de esta fuente:

```powershell
py -B labctl.py prepare
py -B labctl.py serve
```

En Linux se utiliza `python3` en lugar de `py`. `prepare` construye y prepara
servicios propios, comprueba su configuración y disponibilidad; no recorre el
corpus ni ejecuta análisis del modelo. En aquella preparación el funcionamiento
en Parrot aún no estaba comprobado; la revisión posterior está en el acta F4.

Abrir el panel en `http://127.0.0.1:4381`. El portal vulnerable usa 4380 y el
corregido 4382. Las acciones de escenario solo se inician desde un botón explícito
o mediante una petición manual del operador al portal. Cambiar la selección no
envía pruebas. Cada ejecución restablece solo su escenario/modo y conserva los
recibos anteriores. El formulario de autenticación usa exclusivamente datos
ficticios y las contraseñas no se incorporan a URLs ni recibos.

El panel distingue reflexión HTTP de ejecución XSS confirmada en un iframe
sandbox. La revisión visual del resultado y del marcador estaba pendiente en el
primer corpus. La observación posterior de una variante se registra por separado;
no se presume ejecución a partir de HTTP 200.

Para finalizar, Ctrl+C en la terminal del panel y después:

```powershell
py -B labctl.py stop
```

Esto detiene únicamente los servicios de este proyecto, sin eliminar volúmenes
ni archivos de evidencia. Los comandos `check-*` están desactivados por defecto
y requieren un parámetro adicional de autorización explícita; no forman parte
del recorrido manual acordado.

## Evidencia y fuente

El corpus se fija en `corpus.json` y `catalog.py` antes de ejecutarlo. Sus
expectativas no se han ajustado para ocultar los fallos. Los resultados previos
se conservan en `.local-state/f2/suite.json` y las ejecuciones en `runs/`, fuera de
Git. Los snapshots Apache conservan sus líneas y hashes; el registro de efectos
funcionales se mantiene aparte de cualquier futura entrada del detector V2.

La F3 se desarrolla en el repositorio V2 como conector local. Su capturador solo
lee los logs de la pasarela del modo seleccionado; no inicia escenarios, no
reconstruye contenedores y no consulta al modelo.
