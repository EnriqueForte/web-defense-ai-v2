# DVWA: envíos POST y reporte actual en Resumen — 15/10/2026

Seguimiento: corrección publicada como 4c2e032 y CI Windows/Ubuntu aprobada;
véase el cierre al final. Actualización y aceptación en Parrot pendientes.
Los apartados iniciales conservan el estado local previo a publicar.

## Evidencia recibida de Parrot

El usuario actualizó el clon a 3947554 y autorizó un trabajo manual nuevo,
independiente del ensayo HTTP 400 anterior. Las capturas posteriores muestran
`6356df80e4994602ba3004fd2841e6a8` succeeded/finished y el reporte actual con
referencia abreviada `9dd17c72e247`, publicado el 15/10/2026 a las 19:51:52
Europe/Madrid. Reportes permite seleccionar y leer report.md (1450 bytes).
Por tanto, la afirmación inicial de informe no generado se precisó como
ausencia de su entrada en la tarjeta Reportes recientes de Resumen.

El texto visible del informe clasifica un grupo XSS de severidad baja,
requiere investigación, referido a la línea 31, con 30 líneas seleccionadas de
36 y seis omitidas. El Resumen muestra un grupo, cero críticas/altas, una IP y
nueve coincidencias de patrones en el log. No se han leído los archivos de la
VM, hashes completos, recibo del segundo trabajo, consumo ni transportes.
Estas capturas acreditan publicación y lectura, no calidad semántica general.

El usuario identifica sus pruebas como XSS y fuerza bruta. El fragmento final
del access.log muestra tres POST a `/vulnerabilities/brute/`, a las 16:20:27,
16:20:35 y 16:20:43 UTC desde la misma IP, seguidos de un GET de
`/hackable/users/admin.jpg` a las 16:20:43. La petición de imagen con HTTP 200
es una pista contextual, no un registro de autenticación exitosa: el access.log
no contiene aquí cuerpo de formulario ni resultado de autenticación. No se
infiere una intrusión confirmada ni que este fragmento sea el log completo.

## Causas y cambios locales

1. Resumen consumía solamente el historial, que excluye la copia idéntica del
   reporte actual. Un primer reporte podía existir en Reportes mientras la
   tarjeta del Resumen anunciaba que no había históricos. Ahora muestra el
   reporte actual disponible, fecha de publicación, grupos y botón Abrir
   reporte. El botón selecciona la referencia de esa captura en Reportes y
   vuelve a la primera página del catálogo. El historial sigue diferenciado.
   No se cambia el contrato de la API ni se duplica el archivo publicado.
2. La preparación estructurada reconocía el formulario DVWA únicamente si la
   URL contenía username y password, incluso en POST. Ahora un POST a la ruta
   exacta del formulario cuenta como envío sin exigir un cuerpo que Apache
   no registra. GET sigue requiriendo ambos parámetros; visitar el módulo no
   constituye un intento. La regla queda versionada como observed-access-4.

Se mantienen umbral, ventana temporal, separación por IP, selección equilibrada,
guardas y clasificación. Los valores predeterminados son cinco envíos en 60
segundos; no se ha leído ni modificado el valor configurado en la VM. Los tres
POST visibles no alcanzan ese valor predeterminado ni después del arreglo.
La coincidencia amplia del gráfico también puede contar visitas y referentes;
sus nueve coincidencias no equivalen a nueve grupos del informe.

Confirmar éxito de autenticación requiere evidencia adicional de aplicación o
una instrumentación del laboratorio diseñada para ello. No se añade esa fuente
en esta corrección ni se registran contraseñas, cuerpos POST o cookies.

## Validación y límites

- Regresión completa: 335 casos Python, 334 aprobados y uno Linux omitido en
  Windows; tres comprobaciones JavaScript aprobadas. Cuatro pruebas nuevas:
  umbral POST DVWA, negativos de rutas/GET/referentes, límites de IP/tiempo y
  publicación sintética XSS más cinco POST con dos grupos y referencias válidas.
- Lint, TypeScript y 17 grupos de regresión UI aprobados; 92 archivos Python
  sin errores de sintaxis y git diff --check sin errores.
- Build Webpack aprobado y build normal Turbopack aprobado. El primer intento
  en sandbox bloqueó el subproceso de prueba y falló al generar el endpoint
  CSS; Turbopack volvió a fallar fuera del sandbox con la salida generada
  existente. Se conservó `.next` dentro de los recibos ignorados, se construyó
  sin esa caché y el build normal terminó correctamente. Solo se detuvo el
  proceso de regresión propio tras verificar ejecutable, argumentos, parentesco
  y fecha. No se cambió configuración de Next, paquetes ni políticas del SO.
- Los ensayos son sintéticos, sin llamada real al proveedor. La publicación
  de dos grupos usa respuestas de clasificación explícitas de prueba: no
  acredita que el modelo real detecte siempre todas las familias.

Recibos locales en `.local-state/parrot-http-20261015/`, ignorados. No se ha
iniciado otro trabajo, servicio operativo Windows, Docker ni envío. No se
leyeron bytes de .env ni se volvió a inventariar el estado operativo Windows.

Cambios locales pendientes de publicación, CI y actualización de Parrot. El
código con CI remota comprobada sigue siendo 646aaf2. No se ha probado el enlace
nuevo mediante navegador/E2E ni en la VM. El informe existente se conserva y no
se recalcula. Las autorizaciones de f217a6210aa3 y 6356df80e499 están consumidas;
no se repetirá una llamada real automáticamente. A-05 y aceptación general
siguen abiertos.

## Publicación autorizada y actualización de Parrot

El usuario pidió continuar con la publicación y verificación antes de actualizar
su VM. Se publicó el código `4c2e032308066e6afbc1030887c6d55580f1fe51`
en origin/main de EnriqueForte/web-defense-ai-v2. Fetch previo sin divergencia,
247 candidatos/644 blobs alcanzables/62 commits revisados para exclusiones y
formatos concretos de credenciales, sin hallazgos; hashes vendor y los siete
archivos del índice coinciden con la revisión. No constituye una auditoría
exhaustiva. El repositorio original conserva el remoto de push deshabilitado.
La matriz offline del código actual volvió a pasar 13 casos y siete controles
con cero llamadas; recibo local 20261015T180748646529Z.

La [CI 38783207354](https://github.com/EnriqueForte/web-defense-ai-v2/actions/runs/38783207354)
se inició para ese código. El cierre y los artefactos se consignan después de
comprobar el resultado final; no se declara CI aprobada durante la espera.

Tras recibir la confirmación de CI, actualizar en Parrot como el usuario normal,
cuando no haya un análisis en curso:

1. Detener con Ctrl+C las tres terminales de Flask, worker y Next.
2. Ejecutar cada línea por separado y detenerse si alguna falla:

```bash
cd "$HOME/Proyectos/web-defense-ai-v2"
git pull --ff-only
git rev-parse --short HEAD
source "$HOME/.nvm/nvm.sh"
nvm use 24
cd frontend
pnpm run build
cd ..
python3 webdefense.py start --mode structured
```

3. Esperar «Consola lista», abrir http://127.0.0.1:3000 y comprobar en Resumen
   la entrada Reporte actual y su botón Abrir reporte, que debe llevar al informe
   existente. Comparar con la sección Reportes y su referencia/fecha.

Este arranque es de lectura: no inicia worker ni análisis manual o periódico.
La corrección de preparación se aplicará a futuros análisis, no reescribe la
publicación existente. Para retomar una prueba real será necesario definir su
alcance; no se reutiliza la autorización de los dos trabajos anteriores.

## Cierre de publicación y CI

La CI 38783207354/attempt 1 del código
`4c2e032308066e6afbc1030887c6d55580f1fe51` terminó completed/success en
Windows-latest y Ubuntu 24.04. Se revisaron los estados y pasos finales, los
logs descargados y los cuatro nombres de pruebas nuevas en ambos sistemas.

| Verificación | Resultado |
| --- | --- |
| Instalación nueva/contrato/pip check/build normal | Aprobados en ambos sistemas, 172 pines/0 diferencias |
| Regresión Python | Ubuntu 335; Windows 334 aprobados y una prueba Linux omitida |
| JavaScript/sintaxis/HTTP/SDK offline | 3 comprobaciones, 92 archivos, HTTP sintético y 27 escenarios SDK aprobados |
| Matriz A-05/guardas | 13 casos y siete controles aprobados por OS, cero llamadas al proveedor |
| Frontend | Lint, TypeScript y 17 grupos UI aprobados por OS |
| E2E Configuración | Nueve por OS, Windows 27,3 s/Ubuntu 8,4 s; salida 0 y cierre con puertos libres |
| Lanzador | API directa/proxy 200, ejecutor offline y cierre con puertos libres en ambos sistemas |

Inventarios descargados y verificados completos: artefacto 11996213722 Windows
Python 3.11.9 y 11996029339 Ubuntu Python 3.11.17, 172 paquetes/0 deriva/0 extras.
Paquetes contra contrato, metadatos y hash de freeze comprobados. Sus hashes
coinciden con los inventarios del código anterior:

- Windows: `4444efe4144b1000fc66679788ca32dbd9d4685da2fd1161f7eb726fbd93553d`.
- Ubuntu: `2a89e0601de6126ec0449a723bcb0cf67f9b00af092e9abc60264439aa9127fa`.

Resúmenes A-05: artefactos 11997490073 Windows y 11995344892 Ubuntu. Todos los
checks/métricas/hashes de publicaciones coinciden con la matriz local actual
20261015T180748646529Z al excluir únicamente el UUID de generación. Estos
resúmenes no incluyen los bytes de los informes remotos ni evalúan semántica
del proveedor real.

El commit siguiente actualiza solo las actas con [skip ci]; el código probado
es 4c2e032, no se le atribuye una ejecución nueva al acta. Los recibos están en
`.local-state/dvwa-post-20261015/`. No se realizó otra llamada LLM, trabajo
operativo, Docker o envío; no se iniciaron servicios operativos Windows ni se
releyó su inventario operativo/.env. El recorrido de actualización de arriba
queda pendiente de ejecución y confirmación del usuario en Parrot. Las E2E de
Configuración no verifican el nuevo enlace del Resumen. A-05 y la confirmación
de autenticación exitosa siguen abiertas.
