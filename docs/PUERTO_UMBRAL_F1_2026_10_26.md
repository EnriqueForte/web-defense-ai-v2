# Puerto Umbral — primera versión navegable

Fecha: 26/10/2026. Desarrollo iniciado por solicitud del propietario tras revisar
el [PRD](PRD_PUERTO_UMBRAL_2026_10_26.md).

## Estado verificable

Prototipo F1 publicado con acceso privado en
[Puerto Umbral](https://puerto-umbral.aglowsage65.chatgpt.site).
Sites confirmó el despliegue `succeeded`. La revisión visual del propietario
sigue pendiente; esta entrega no acredita el backend o la integración defensiva.

| Elemento | Estado |
| --- | --- |
| Centro de operaciones y plano orbital SVG original | Implementados |
| Mercancías, comunicaciones, archivo, mantenimiento y tripulación | Navegables, con datos ficticios |
| Búsquedas, filtros, detalle y descarga de documentos ficticios | Comprobados en navegador |
| Cinco escenarios con dos modos | Diez demostraciones verificadas, sin tráfico de ataque |
| Historial local y exportación JSON | Comprobados; datos de QA exportados y retirados del navegador |
| Diseño adaptable | Revisado en tamaños 390, 768 y 1440; sin desbordamiento horizontal en las vistas comprobadas |
| Backend vulnerable, aislamiento y corpus real | Pendientes F2 y especificaciones previas |
| Capturador, perfil y conexión V2 | Pendientes F3 |
| Seguimiento y evaluación defensiva | Pendientes F4/F5 |

## Identidad y fuente

- Site: `appgprj_6adf33ac8bcc81918087f268061f003a`.
- Commit de la fuente Sites: `3b1e3970b4f7d0d335004cbba577ed78e67088e2`.
- Versión: `appgprj_6adf33ac8bcc81918087f268061f003a~appgver_3b896e2e8a548191b1fbece47e5b11bb`.
- Despliegue: `appgdep_6adf390f10448191a31d7f66c57e4bd6`.
- Fuente independiente, gestionada mediante el repositorio de Sites. No se añade
  código del prototipo al árbol de producto V2.
- Checkout de esta sesión:
  `C:\Users\elqui\.codex\visualizations\2026\10\26\01a17795-369b-75e1-9c7a-75e6f9088cc6\sites\puerto-umbral`.

La fuente incluye README, decisiones F0/F1 y registro de validación. La interfaz
usa HTML/CSS/JavaScript estáticos sin paquetes de ejecución. Los recibos demo se
identifican como `browser_demonstration`, con cero peticiones de ataque y sin
consulta a V2; no son evidencias operativas ni forman parte del corpus de 45 casos.

## Conservación y continuación

No se iniciaron análisis LLM, ataques, Docker, avisos o acciones sobre la VM.
No se modificaron el código/configuración de V2, los datos DVWA ni sus cierres
históricos. Este registro y el PRD permanecen locales en V2, sin commit/push.

La continuación debe reutilizar el Site indicado y su identidad en
`.openai/hosting.json`, conservar su audiencia privada y revisar el diseño con
el propietario antes de considerar satisfecho el criterio F1-AC3 del PRD.
