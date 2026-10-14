# Operación, conservación y recuperación local — 14/10/2026

La aplicación dispone ahora de un comando de recuperación comprobable desde un
respaldo existente. Restaura los datos en **un directorio nuevo aislado**, revisa
hashes/integridad/publicación y conserva los estados de trabajos y entregas.
No cambia las rutas operativas, ejecuta análisis o reenvía notificaciones.
El ensayo Windows con datos existentes pasó; CI de estos cambios aún pendiente.

## Operación habitual y ventana de conservación

Instalar/actualizar y abrir la consola sigue [inicio rápido](INICIO_RAPIDO.md):
servicios anteriores detenidos, `git pull --ff-only`, `python3 webdefense.py install`
y `python3 webdefense.py start --mode structured`. En Windows usar `py` como
entrada. El lanzador inicia la consola de lectura; no inicia worker ni admite
análisis. Ctrl+C cierra los dos procesos propios.

La operación de análisis requiere delimitar fuentes, proveedor, llamadas y
notificaciones antes de activar Flask con `--enable-manual` y el worker
`--manual-only` mediante `scripts/local_runtime_profile.py`. Sus comandos de
plan/preflight sin `--start` permiten revisar las rutas y los bloqueos. No
habilitar una segunda instancia ni reutilizar PID históricos. Un resultado
fallido no autoriza otra llamada al proveedor o el reenvío de una entrega.

Antes de copiar o recuperar, utilizar una ventana sin queued/running. Para
actualizar o sustituir almacenamiento, detener admisión/worker/servicios propios
mediante sus consolas y comprobar identidades/estado; no borrar locks para forzar
el acceso. El respaldo usa locks cooperativos cycle/engine/publicación,
captura estable y la API SQLite backup; escritores externos que ignoren esos
locks no forman una transacción global. Se recomienda la ventana sin escritores.

## Cobertura explícita del respaldo

| Perfil | Fuentes |
| --- | --- |
| `legacy` | `logs/access.log`, Markdown en `reports`, `.local-state/analysis.sqlite3` cuando existe |
| `pilot` | `.local-state/dvwa-lab/access.log`, Markdown en `.local-state/phase6-pilot/reports`, SQLite del piloto |
| Ambos | `structured/current.json`, generaciones con `manifest.json`/`result.json` y Markdown; tres JSON de diagnóstico conocidos por directorio análisis–UUID |

Los tres JSON añadidos son `checkpoint.json`, `receipt.json` y `process.json`
bajo `analysis-diagnostics/<32hex>-<32hex>/`. Otros JSON no se seleccionan.
La copia mantiene datos e históricos, incluso entregas `unknown`; no transforma
esos estados en `sent` ni recupera correos que hayan desaparecido del buzón.
Los commits presentes en WAL se incluyen mediante snapshot SQLite, sin copiar
locks/WAL/SHM vivos. Las fuentes ausentes se registran, sin crearlas.

No incluye `.env`, claves, paquetes/build, Git, volúmenes/imágenes/redes Docker,
buzón Mailpit, todos los recibos de `.local-state` o rutas personalizadas fuera
de los perfiles. Revisar el listado antes de afirmar cobertura. Los logs e
informes sí pueden contener información sensible: copias/restauraciones se
guardan en carpetas ignoradas, sin exportación a servicios externos.

Desde la raíz, Linux/Parrot:

```bash
.p2/bin/python -B scripts/backup_operational.py --profile all --list
.p2/bin/python -B scripts/backup_operational.py --profile all
```

Windows utiliza `.p2/Scripts/python.exe` en lugar de `.p2/bin/python`. El entorno
`.p4` solo se utilizó en el ensayo local de desarrollo, sin activarlo como piloto.
La salida identifica una carpeta nueva `.local-backups/operational-<fecha>/` y
`verified=true` únicamente tras comprobar su ZIP y una restauración auxiliar.
Un error conserva los artefactos parciales y las fuentes. No usar una copia con
`verified=false`. Mantener las copias existentes; la limpieza es una operación
separada y no se automatiza en esta entrega.

## Recuperar una copia existente

Elegir la carpeta devuelta por el respaldo, que contiene `manifest.json` y
`operational.zip`. Ejemplo del ensayo realizado, disponible solo en este Windows:

```powershell
.p4/Scripts/python.exe -B scripts/restore_operational.py --backup '.local-backups/operational-20261014T103331825812Z'
```

En la instalación del usuario utilizar su intérprete `.p2` y la carpeta de su
propia copia. El comando **no acepta un destino operativo**: crea
`.local-state/recovery/restore-<fecha>/` y solo devuelve `verified=true` después
de comprobar todos los archivos, las bases, ausencia de trabajos activos y las
publicaciones actuales. `recovery-review.json` registra perfiles, fuentes
ausentes, conteos y el hash de los bytes del manifiesto revisado, sin credenciales
o filas crudas de SQLite. No instala paquetes ni arranca servicios.

Se rechazan manifiestos no verificados/esquema ajeno/claves duplicadas,
rutas ajenas al perfil, traversal/alias Windows/nombres reservados, enlaces
y puntos de reanálisis, miembros ZIP inesperados/enlazados/cifrados, tamaños o
hashes inconsistentes, SQLite inválido/activo y publicaciones corruptas.
Límites del comando: manifiesto 4 MiB, 10.000 archivos, 64 MiB por archivo y
1 GiB total descomprimido. Si una copia excede el alcance, conservarla y revisar
un procedimiento apropiado; no omitir validaciones. SHA-256 verifica consistencia
con el manifiesto, no autentica criptográficamente su procedencia: usar una copia
de origen conocido.

Si falla tras extraer parte del ZIP, la carpeta parcial permanece para diagnóstico
sin un nuevo `recovery-review.json` verificado. No modificar las fuentes o
reintentar dentro de esa misma carpeta. Una nueva invocación usa un destino nuevo.

La recuperación aislada es el resultado prometido. Promover esos datos a una
instalación operativa es una actuación posterior concreta: conservar también el
estado más reciente, comparar generaciones/trabajos/entregas, detener todos los
escritores y decidir el cambio de rutas/datos. No copiar automáticamente sobre
la base viva, iniciar un worker en el directorio recuperado ni reconciliar/recrear
trabajos para reconstruir una entrega. No se ha hecho una sustitución en vivo.

## Laboratorio: datos con ciclo de vida separado

Esto se deriva del `compose.lab.yaml` vigente; no demuestra el estado de la VM:

| Dato | Conservación definida |
| --- | --- |
| Base DVWA | Volumen nombrado `web-defense-ai-v2-lab-dvwa-db`, montado en `/var/lib/mysql`; no incluido en el ZIP de aplicación |
| Accesos Apache | Salida del contenedor DVWA, driver `json-file`, rotación 10m/3; eliminar/recrear el contenedor o rotar puede perder accesos todavía no capturados |
| Captura de la aplicación | `.local-state/dvwa-lab/access.log`; el perfil pilot sí la copia cuando existe; no reconstruye todo el historial Docker |
| Mailpit | Sin volumen configurado, máximo 500 mensajes; buzón efímero, no archivo de entregas; recrear el contenedor puede perderlo |
| `.env` | Conservación separada a cargo del usuario; no viaja con estos respaldos |

Detener con `docker-compose --file compose.lab.yaml stop` en Parrot (o
`docker compose ... stop` donde exista el plugin) conserva contenedores/volumen.
Antes de recrear/eliminar contenedores, capturar los accesos que se necesiten
y acordar conservación del buzón/base. `down --volumes`, la reinicialización de
la base DVWA y la purga de buzón son destructivos; no forman parte del cierre o
la recuperación habitual. No se promete respaldo/restauración de esos componentes
ni se les aplica el ZIP de la aplicación. No se modifica Compose o imágenes.

## Ensayo local verificado

Se crearon y conservaron una primera copia de 64 archivos del alcance anterior
y una copia final de **76 archivos, incluidos 12 JSON de diagnóstico**. Copia
final: `.local-backups/operational-20261014T103331825812Z`. Restauración final del
CLI: `.local-state/recovery/restore-20261014T103821142161Z`. Ambos perfiles se
incluyen; la SQLite legacy ausente quedó registrada, sin inventar su contenido.

Se compararon hashes de todos los archivos seleccionados y **todas las columnas**
de trabajos/entregas entre fuentes e instancia recuperada: piloto 29 trabajos
(18 succeeded/11 failed), 14 entregas (11 sent/3 unknown), cero activos y misma
generación. Las fuentes operativas y metadatos de `.env` coinciden antes/después.
No se leyeron bytes de `.env`, hicieron análisis, proveedor, Docker, envíos o
arranques operativos. Los datos recuperados no se publican ni sustituyen el piloto.

Validación local final `.p4`: 322 pruebas Python, 321 aprobadas y una exclusiva
Linux omitida; tres JS; 91 archivos de sintaxis/diff. Ocho pruebas nuevas cubren
filas completas/unknown/publicación/diagnósticos, manifiestos/caminos/tamaños,
alteraciones, enlaces ZIP/destino, SQLite activo y errores sin contenido privado.
El primer ensayo dentro del sandbox falló en reemplazos/renombrados temporales;
la repetición autorizada pasó, sin relajar el producto. Recibos y hashes de filas
se guardan en `.local-state/recovery-20261014/`, ignorados. CI/publicación pendientes.

## Evidencia preliminar Parrot y pendientes

Capturas del usuario el 14/10: motor consultado Docker26.1.5+dfsg1, Linux/x86_64;
`docker compose` no disponible; binario `docker-compose` v5.1.0. En clon
`e5af1a6`, `docker-compose --file compose.lab.yaml config --quiet` terminó con 0.
Ese archivo coincide con el actual. Esto acredita consulta de motor y validación
de configuración; no contenedores iniciados, redes/puertos efectivos, ingesta,
informe o restauración en Parrot. Laboratorio no existente según el usuario.

Quedan actualizar la VM tras la publicación/CI de esta entrega y efectuar el
recorrido guiado con datos/llamadas concretos. Las imágenes tienen hallazgos de
seguridad pendientes de revisión independiente; la comprobación de configuración
no los elimina ni cambia sus digests. A-05 necesita aceptación y ensayo manual
de ingesta. La recuperación probada aquí es aislada y no acredita una promoción
en vivo o recuperación completa de Docker/Mailpit.
