# Configuración local del proveedor LLM

Estado: implementado el 02/10/2026 para una instalación autoalojada.

## Alcance

Cada instalación de web-defense-ai V2 configura su propio proveedor desde la
pestaña **Configuración** del dashboard. Groq es el proveedor predeterminado;
OpenRouter también está disponible. Esta versión no tiene cuentas ni almacena
credenciales separadas por identidad. Si varias personas comparten una misma
instalación, comparten su proveedor y clave. No publicar ese dashboard en una
red compartida sin añadir autenticación y aislamiento por usuario.

La interfaz ofrece los modelos incluidos en el catálogo como opciones
gratuitas y permite introducir el identificador de otro modelo compatible con
CrewAI/LiteLLM. Un modelo personalizado puede tener coste. La selección no
consulta precios, saldo ni plan del proveedor, y la disponibilidad gratuita
puede cambiar en cualquier momento.

## Guardado y uso

- El navegador envía la clave una sola vez al backend local; las respuestas
  solo indican si existe una clave y nunca incluyen su valor.
- Flask valida el proveedor y el prefijo del modelo contra un catálogo fijo.
  No acepta una URL de API arbitraria.
- El backend guarda proveedor, modelo y clave en una sección administrada del
  `.env` local mediante escritura atómica. El archivo permanece fuera de Git.
- El guardado usa los mismos bloqueos que el ciclo y el motor de análisis. Si
  hay un análisis activo, responde `409` y no cambia la configuración.
- No se hace una llamada de validación al proveedor al guardar. La clave se
  usa cuando se inicia el siguiente análisis; el proveedor puede rechazarla o
  facturar según su cuenta y modelo.
- Las opciones actuales son Groq con `gpt-oss-120b` y `gpt-oss-20b`, y el
  enrutador gratuito de OpenRouter. El fallback de Groq queda limitado a sus
  modelos gratuitos configurados; los modelos personalizados no tienen
  fallback automático a otro modelo o proveedor.

## Corrección del análisis con OpenRouter

El 02/10/2026, dos intentos manuales fallaron porque CrewAI construyó su
cliente nativo para OpenRouter y envió `max_retries` como parámetro de la
solicitud de completado. Ese parámetro pertenece al cliente, y el SDK lo
rechazó antes de realizar la llamada. El motor ahora fuerza la ruta LiteLLM
para OpenRouter, que mantiene el adaptador de reintentos y los candidatos
configurados en `main.py`. Groq conserva su ruta anterior. La corrección no
valida por adelantado la clave, el acceso a modelos ni la disponibilidad de
OpenRouter. Después de la corrección, el usuario completó dos análisis manuales
con OpenRouter el 02/10/2026; el segundo generó un reporte tras 10 min 57 s.

## Protección de credenciales

`.env` es texto sin cifrar. La aplicación no lo sirve ni envía claves al
frontend en respuestas, logs de diagnóstico o SQLite; aun así, el sistema de
archivos y la cuenta local protegen ese archivo. Mantén el dashboard limitado
a localhost, no lo compartas y no publiques `.env`. La escritura de
configuración requiere un origen localhost permitido además de la conexión
local. Cada usuario de una publicación autoalojada debe aportar su propia
clave; el repositorio no contiene claves de proveedor.

## Ampliar el catálogo o volver a Groq

Los proveedores, claves de entorno, modelos permitidos y base URL fija se
declaran en `config/model_config.py`. Para añadir un proveedor, agrega su clave
de entorno, prefijo/modelos admitidos y URL fija en ese catálogo; actualiza el
selector y el esquema de `/api/v1/configuracion/llm`. No permitas que el
navegador establezca una URL libre ni imprimas el valor de una clave.

Para volver a la opción predeterminada, selecciona Groq y uno de sus modelos
del catálogo en **Configuración**. Cambiar el código atrás no elimina por sí
solo la sección administrada que ya se haya escrito en el `.env` local; revisa
ese archivo localmente y conserva las claves que quieras seguir usando.
