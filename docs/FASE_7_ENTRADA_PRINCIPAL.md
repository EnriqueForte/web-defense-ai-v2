# Fase 7 — Preparación de la entrada principal

Estado: conmutador reversible implementado, pero apagado. El cambio habitual
a Next.js no se activa hasta aceptar las condiciones del piloto de fase 6.

## Comportamiento

- `NEXT_PRIMARY_ENABLED=0` mantiene Flask como página de entrada en
  `http://127.0.0.1:5000/` y no sondea Next.js.
- Con `NEXT_PRIMARY_ENABLED=1`, Flask comprueba `http://127.0.0.1:3000/` en
  loopback. Si recibe HTTP 200, responde con redirección temporal a Next.js.
- Si Next.js no está disponible o no devuelve HTTP 200, Flask renderiza su
  dashboard anterior en la misma solicitud. No se hace un sondeo externo ni se
  siguen redirecciones durante la comprobación.
- El cliente conserva la entrada Flask como ruta manual de retorno. El
  conmutador no cambia API, ejecutor, almacenamiento, históricos ni el
  comportamiento de `/api/v1`.

## Activación posterior

No activar hasta completar el piloto de fase 6: recorridos aceptados, carga
representativa, diez ciclos, 24–48 horas de estabilidad, reinicio y retorno
ensayado. En el entorno local, manteniendo ambos procesos ligados a loopback:

1. Establecer `NEXT_PRIMARY_ENABLED=1` en la configuración local y reiniciar
   Flask.
2. Iniciar Next.js y abrir la dirección estable de Flask,
   `http://127.0.0.1:5000/`. Verificar la redirección y los recorridos.
3. Detener Next.js durante una prueba controlada. Una nueva visita a Flask debe
   mostrar el dashboard anterior; registrar el resultado y el tiempo de retorno.
4. Mantener la entrada habitual apagada hasta documentar la aceptación del
   periodo de observación de siete días previsto en el plan.

## Retorno

Poner `NEXT_PRIMARY_ENABLED=0` y reiniciar Flask. Abrir
`http://127.0.0.1:5000/`; Flask servirá el dashboard anterior sin depender de
Next.js. Para el retorno rápido ante caída de Next, acceder directamente a esa
misma dirección. La acción manual continúa controlada por separado mediante
`ANALYSIS_MANUAL_ENABLED`.

## Validación local y límites

La suite automatizada comprueba el modo apagado, redirección con Next disponible
y render Flask cuando Next no responde. La verificación de disponibilidad está
aislada en pruebas y no requiere iniciar Next.js. Esta preparación no sustituye
el piloto real de fase 6 ni autoriza el cambio de entrada habitual. No hay
despliegue público, autenticación compartida ni telemetría centralizada.

La revisión visual local también comprobó navegación, persistencia de filtros,
lectura de históricos con HTML tratado como texto y actividad con la fixture de
fase 4. En móviles el panel lateral cerrado se excluye de la navegación por
teclado; tras elegir una sección, el foco vuelve al control de menú. El ancho del
documento no superó el viewport en 390, 768, 1280 y 1440 píxeles.

La comprobación puntual de contraste corrigió la etiqueta de navegación, el
nombre del espacio de trabajo, los encabezados de tabla y el pie de página. Los
pares medidos quedan entre 5.38:1 y 6.03:1, y el foco por teclado muestra un
borde visible de 2 píxeles. Es una revisión parcial de componentes visibles,
no una certificación WCAG ni una auditoría automatizada completa.
