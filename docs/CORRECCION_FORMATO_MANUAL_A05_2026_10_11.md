# A-05 — Formato y conversión de clasificación, 11/10/2026

Después del ensayo de instalación limpia Windows solicitado por el usuario,
se corrigió offline el recorrido de clasificación inválida identificado en
`331efe77ad3c40fb8eb876f8b84bf260`. **La corrección está implementada y probada con
respuestas simuladas; no se repitió el análisis con proveedor.** A-05 continúa
abierta por verificación real del recorrido y por la causa desconocida del
primer `ingestion_failed`.

## Cambio

`structured-prototype-8` conserva tres tareas, contratos, salida Pydantic,
guardas y un reintento por etapa. Las tareas usan `StrictJsonTask`: la exportación
parsea el JSON original completo y valida su esquema localmente. Si no es válido,
devuelve salida tipada ausente y permite que la guarda registre el motivo y use
su único reintento. No extrae JSON de texto libre, repara contenido, convierte
errores en cero hallazgos ni hace llamadas adicionales de conversión.

Esto evita que `_export_output → convert_to_model → handle_partial_json`
interrumpa el segundo intento con `ValidationError` antes de pasar por la guarda.
Un reintento válido puede terminar; dos salidas inválidas siguen produciendo un
fallo controlado, sin narrativa ni publicación. La corrección **no significa
aceptar cualquier salida del proveedor como éxito**.

En la ruta LiteLLM de OpenRouter, el adaptador estructurado añade por llamada
`response_format={"type":"json_object"}` y
`extra_body.provider.require_parameters=true`. Mantiene credencial, URL,
candidatos, límites y preferencias existentes; restaura los parámetros del
delegado incluso si la llamada falla. No modifica `.env`, modelos elegidos por
el usuario, presupuestos, fallbacks de precio, modo legacy o proveedores distintos.

OpenRouter documenta el parámetro de [formato de respuesta](https://openrouter.ai/docs/client-sdks/python/api-reference/chat)
y el filtrado por parámetros en [salidas estructuradas](https://openrouter.ai/docs/guides/features/structured-outputs).
El [router gratuito](https://openrouter.ai/openrouter/free) selecciona modelos
según las funciones solicitadas. Pedir JSON permite comunicar ese requisito
al transporte; no acredita por sí solo esquema, semántica o disponibilidad.
Si no hay endpoint compatible, puede fallar: no se elimina el requisito como
fallback silencioso. Las guardas Python siguen siendo obligatorias.

## Verificación offline

- 268 pruebas Python y tres comprobaciones JavaScript en `.p3`, aprobadas.
- 71 archivos de sintaxis, cero errores.
- **25 escenarios CrewAI/LiteLLM**, aprobados en `.p3`, `.p2`, `.venv` y el
  entorno recién instalado `.i1/.p2`, con conexiones a proveedor bloqueadas.
- El recorrido positivo conserva tres llamadas. Una clasificación inválida y
  un reintento válido terminan con cuatro llamadas y publicación validada.
- Dos clasificaciones inválidas (texto con JSON parcial, o JSON completo de
  esquema incorrecto) registran ambas guardas, usan tres llamadas contando la
  detección, no llegan a narrativa y conservan el informe previo. Se bloqueó
  explícitamente el conversor genérico para demostrar que no interviene.
- La llamada LiteLLM simulada recibe JSON mode, require_parameters, clave/URL
  sintéticas y preferencias originales. Los parámetros del delegado se restauran
  tanto tras éxito como tras fallo de transporte.
- Los recibos no contienen el texto privado sintético utilizado en el fallo.

Las pruebas ejercitan los hooks de CrewAI fijados en los entornos disponibles.
Una actualización futura de CrewAI debe volver a comprobar este comportamiento;
no se declara compatibilidad con versiones no ensayadas.

La instalación limpia se comprobó primero sobre el snapshot de 197 archivos.
Después se actualizaron en `.i1` únicamente `agents/structured_prototype.py`
y `scripts/check_structured_prototype.py` para verificar esta corrección sobre
sus dependencias nuevas. El manifiesto original se conserva como evidencia
del ensayo previo; no se presenta como hash del candidato posterior modificado.

## Estado operativo y límites

Lectura posterior: 28 trabajos, 17 succeeded/11 failed, cero queued/running,
entregas históricas 11 sent/3 unknown y cero entregas de los dos fallidos.
Generación actual del 10/10, hashes report/result y hash de la copia de 151
líneas preservados. No se restauran los datos generados por el usuario.

No se reiniciaron Flask, worker o Next, ni se enviaron notificaciones o solicitudes
Docker/proveedor. Manual permanece habilitado por la aceptación previa y worker
manual-only. **Un futuro hijo `main.py` cargará prototype-8**; no se afirma que
los procesos activos hayan recargado código o que el siguiente proveedor vaya
a responder correctamente. Esta tarea no publica la vista narrativa aceptada
ni cambia el informe existente.

La causa concreta del primer fallo de ingesta sigue desconocida por la escasa
información del registro previo. Esta entrega no incorpora diagnósticos nuevos
de captura ni declara reparada una condición Docker que no se verificó.
Linux/Parrot, CI/clonación remota y avisos residuales siguen pendientes
independientes. No hubo llamada real nueva, commit o push.

Recibos locales: `.local-state/a05-incident-20261011/` (`baseline-correction.log`,
`sdk-correction.log`, `sdk-correction-p2.log`, `sdk-correction-venv.log`,
`sdk-correction-clean.log`, `state-readonly.json`). Para revertir este cambio,
retirar solo JSON mode y `StrictJsonTask`, volver a Task y prototype-7,
conservando las correcciones anteriores de omisión/narrativa y el resto de
cambios del usuario; no usar una restauración Git general del archivo.
