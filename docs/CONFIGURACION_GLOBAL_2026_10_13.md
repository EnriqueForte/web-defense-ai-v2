# Validación de configuración global — 13/10/2026

## Comportamiento

El ejecutor podía fallar al importar `config/settings.py` con una conversión
numérica poco comprensible. Ahora valida conjuntamente sus cuatro parámetros
numéricos y muestra los nombres que deben corregirse antes de cargar el resto
del ejecutor. No imprime los valores introducidos ni el traceback en la CLI.
Por ejemplo, `INTERVALO_MINUTOS=abc` termina con código 2 y explica que debe ser
un entero positivo; no crea la base de trabajos, el heartbeat o archivos de datos.

| Variable | Valores admitidos | Predeterminado si falta |
| --- | --- | --- |
| `INTERVALO_MINUTOS` | Entero >=1, con segundos representables como número finito | 3 |
| `MAX_LINEAS_LOG` | Entero entre 1 y 1000 | 100 |
| `UMBRAL_FUERZA_BRUTA` | Entero entre 1 y 100 | 5 |
| `LLM_TEMPERATURE` | Número finito entre 0 y 2 | 0.1 |

Una variable presente pero vacía, no numérica o fuera de rango se rechaza;
no se sustituye silenciosamente por el predeterminado. Los límites de líneas
e intentos coinciden con los ya exigidos por la preparación structured.
Se mantienen el comportamiento de rutas, la precedencia de dotenv existente y
los predeterminados de configuración global. No se cambia el resolver LLM,
sus reintentos ni el preprocesamiento legacy. Esta validación corresponde al
ejecutor que importa `config.settings`, no certifica todas las entradas del motor
iniciado directamente ni el formulario de Configuración.

## Comprobación

Cinco pruebas nuevas cubren predeterminados/límites, valores vacíos y tipos
incorrectos, NaN/infinito/desbordamiento, varios errores simultáneos y carga real
del módulo. Un intérprete separado ejecuta la CLI del worker con configuración
sintética inválida: salida 2, mensaje sin valor privado/traceback y directorio
temporal sin archivos creados. Dotenv operativo deshabilitado para esta prueba.

Se usa `.p4` como entorno de pruebas aislado del contrato de 172 paquetes;
no se activa como entorno operativo. La línea base completa pasó 303 casos
Python (302 aprobados y uno exclusivo de Linux omitido en Windows) y tres JS.
El primer ensayo dentro del sandbox fue bloqueado por permisos de reemplazo
de archivos temporales y sockets locales; el ensayo autorizado fuera del sandbox
pasó. La comprobación de sintaxis cubre 84 archivos.

Recibos ignorados: `.local-state/config-validation-20261013/`. No se modifica
el `.env` operativo ni se inicia el worker operativo, Docker, análisis real,
proveedor o notificaciones. El E2E de guardar/recargar/desmontar Configuración
(R-15), A-05, laboratorio Parrot y seguridad residual conservan sus pendientes.
La validación CI de esta entrega se registrará después de revisar sus resultados.
