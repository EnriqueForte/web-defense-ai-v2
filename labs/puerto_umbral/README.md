# Puerto Umbral — distribución local portable

Este directorio incluye la fuente educativa local de Puerto Umbral para que un
solo checkout de Web Defense AI V2 contenga ambas aplicaciones. Los contenedores
siguen separados de V2 y de DVWA; el prototipo privado de Sites no se modifica.

Estado documental al 03/11/2026: disponibilidad y recorridos representativos
recibidos en Parrot; aceptación completa F0–F7 pendiente. El objetivo de cierre
del desarrollo es el jueves 5 de noviembre. Consulta el
[índice documental](../../docs/README.md) y la
[revisión vigente](../../docs/REVISION_INTEGRAL_2026_11_03.md).

Decisión posterior del 03/11: F4/F5 cerradas por alcance sin pruebas restantes,
F6 cerrada previamente y matriz F7 aceptada en su alcance educativo. Rotación
real y métricas del detector no verificadas/no medidas permanecen como límites;
los estados pendientes inferiores describen sus antecedentes. Registro actual:
[decisiones de cierre](../../docs/CIERRE_V2_PUERTO_UMBRAL_2026_11_03.md).

## Arranque conjunto desde la raíz de V2

```bash
python3 webdefensev2.py
```

Necesita la instalación `.p2` de V2, su frontend compilado, Docker y un cliente
Compose disponible. Se admite `docker compose` o `docker-compose`, sin instalar
plugins ni cambiar el contexto Docker automáticamente.
Las dos imágenes compartidas se construyen una vez con `docker build`; Compose
valida la configuración y arranca con `up --no-build`. Así no se invoca el
constructor de Compose, que en la VM solicitó Buildx 0.17 o posterior. La CLI
Docker usa el constructor configurado en ese equipo, sin cambiar sus opciones.

La terminal supervisa Flask, Next y el panel local de Puerto Umbral. La topología
F6/F7 incluye catorce contenedores, con disponibilidad e inspección agregada
recibidas del propietario en Parrot. Esto no acepta todos sus escenarios.
El arranque solo hace comprobaciones de disponibilidad de servicios;
no ejecuta el corpus, escenarios, análisis del modelo ni notificaciones.

- V2: `http://127.0.0.1:3000`.
- Panel de Puerto Umbral: `http://127.0.0.1:4381`.
- Portal vulnerable: `http://127.0.0.1:4380`.
- Portal corregido: `http://127.0.0.1:4382`.

Ctrl+C cierra los procesos propios y solicita detener únicamente los servicios
de este laboratorio. No borra volúmenes ni evidencias, ni detiene DVWA/Mailpit.
Si ya existe una sesión de Puerto Umbral arrancada, el lanzador pide cerrarla en
lugar de asumir el control de sus procesos. Los errores de parada quedan en los logs.

La entrada `webdefensev2.py` selecciona la fuente corregida por defecto;
`--lab-mode vulnerable` selecciona la otra fuente para V2. La entrada avanzada
`webdefense.py start --mode structured --with-puerto-umbral --lab-mode corrected`
sigue disponible; en esa entrada anterior conviene indicar el modo explícito,
pues su valor predeterminado es vulnerable.
Seleccionar el modo de captura no ejecuta un escenario ni modifica el portal.

## Ampliaciones F6/F7 y aceptación pendiente

El [registro de desarrollo](../../docs/PUERTO_UMBRAL_F6_F7_2026_10_29.md)
describe cinco escenarios de estado/identidad y seis revisiones de artefactos
ficticios. Su catálogo de 99 entradas es independiente del corpus base de 45;
no representa 99 casos superados. La auditoría de aplicación tiene
contrato propio, lectura por reglas en V2 y conservación explícita respaldable.
Se han recibido normales e intentos corregidos, comparaciones puntuales de
Cargas y Atraque vulnerables con sus rechazos corregidos y once recorridos
educativos F7, a los alcances de sus actas. El 03/11 el propietario cierra F6
sin más pruebas por el bloqueo de la conversación: Bitácora/Preferencias
vulnerables, resultado vulnerable de Baliza y regresión F6 restante quedan
omitidos/no verificados. Se conservan los resultados recibidos. No se ejecutan nuevos
casos o modelos por esta guía.

## Origen y separación

La fuente deriva del trabajo F2 posterior al prototipo Sites F1 identificado en
las actas del proyecto. Se incluyen solo código, fixtures ficticios y dos assets
de interfaz propios. No se copian `.git`, `.openai`, credenciales, entornos,
imágenes Docker ni `.local-state` del checkout de trabajo original.

`lab/README.md` conserva el estado inicial de F2. El primer corpus conserva
42/45 conformes HTTP y tres fallos históricos de comandos; después se verifica
la corrección de `Cannot fork` con normal corregido y vulnerable representativo
de variante 1, sin reescribir ese archivo a 45/45. La revisión posterior de
Parrot también observó una variante SQL, XSS y Path traversal
en ambos modos, incluido el marcador XSS vulnerable. La
[evaluación F5](../../docs/PUERTO_UMBRAL_F5_2026_10_27.md) separa esas observaciones
del archivo histórico y de las métricas del detector sin medir.

El [manual actual de operación](../../docs/PUERTO_UMBRAL_OPERACION_LOCAL.md)
documenta captura, seguimiento F4, cierre y conservación. La ronda básica F4,
la medición API con desviación acotada aceptada y el recorrido de fallo/
recuperación están completados a sus alcances. Rotación real y aceptación
ampliada y del MVP siguen pendientes. No se
solicitan escenarios nuevos para cerrar el bloque documental.

La decisión inicial de un repositorio independiente se adapta a una distribución
portable dentro de V2 por la necesidad del propietario de actualizar y arrancar
ambas aplicaciones desde Parrot con un único checkout.

Los datos del laboratorio quedan en `.local-state/f2` dentro de este directorio,
ignorados por Git. La copia de captura y las publicaciones V2 usan el perfil
separado `.local-state/puerto-umbral` en la raíz del proyecto.
