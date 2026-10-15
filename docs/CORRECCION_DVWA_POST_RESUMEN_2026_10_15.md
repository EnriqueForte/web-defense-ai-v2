# DVWA: envíos POST y reporte actual en Resumen — 15/10/2026

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
