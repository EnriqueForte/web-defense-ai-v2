# Puerto Umbral — distribución local portable

Este directorio incluye la fuente educativa local de Puerto Umbral para que un
solo checkout de Web Defense AI V2 contenga ambas aplicaciones. Los contenedores
siguen separados de V2 y de DVWA; el prototipo privado de Sites no se modifica.

## Arranque conjunto desde la raíz de V2

```bash
python3 webdefense.py start --mode structured --with-puerto-umbral
```

Necesita la instalación `.p2` de V2, su frontend compilado, Docker y un cliente
Compose disponible. Se admite `docker compose` o `docker-compose`, sin instalar
plugins ni cambiar el contexto Docker automáticamente.
Las dos imágenes compartidas se construyen una vez con `docker build`; Compose
valida la configuración y arranca con `up --no-build`. Así no se invoca el
constructor de Compose, que en la VM solicitó Buildx 0.17 o posterior. La CLI
Docker usa el constructor configurado en ese equipo, sin cambiar sus opciones.

La terminal supervisa Flask, Next y el panel local de Puerto Umbral, y prepara
sus doce contenedores. Solo hace comprobaciones de disponibilidad de servicios;
no ejecuta el corpus, escenarios, análisis del modelo ni notificaciones.

- V2: `http://127.0.0.1:3000`.
- Panel de Puerto Umbral: `http://127.0.0.1:4381`.
- Portal vulnerable: `http://127.0.0.1:4380`.
- Portal corregido: `http://127.0.0.1:4382`.

Ctrl+C cierra los procesos propios y solicita detener únicamente los servicios
de este laboratorio. No borra volúmenes ni evidencias, ni detiene DVWA/Mailpit.
Si ya existe una sesión de Puerto Umbral arrancada, el lanzador pide cerrarla en
lugar de asumir el control de sus procesos. Los errores de parada quedan en los logs.

Para leer los logs del modo corregido, añadir `--lab-mode corrected`. Seleccionar
el modo de captura no ejecuta un escenario ni modifica el portal.

## Origen y separación

La fuente deriva del trabajo F2 posterior al prototipo Sites F1 identificado en
las actas del proyecto. Se incluyen solo código, fixtures ficticios y dos assets
de interfaz propios. No se copian `.git`, `.openai`, credenciales, entornos,
imágenes Docker ni `.local-state` del checkout de trabajo original.

`lab/README.md` conserva el estado de validación F2: primer corpus 42/45,
corrección de fuente pendiente de comprobación manual y observación XSS en
navegador pendiente. Publicar o compilar no cambia esa valoración.

La decisión inicial de un repositorio independiente se adapta a una distribución
portable dentro de V2 por la necesidad del propietario de actualizar y arrancar
ambas aplicaciones desde Parrot con un único checkout.

Los datos del laboratorio quedan en `.local-state/f2` dentro de este directorio,
ignorados por Git. La copia de captura y las publicaciones V2 usan el perfil
separado `.local-state/puerto-umbral` en la raíz del proyecto.
