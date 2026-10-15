# Groq HTTP 413 en la prueba de fuerza bruta — 15/10/2026

## Evidencia y alcance

Tras comprobar observed-access-4 (ocho POST en 45 s, referencias 39–46
seleccionadas, umbral 5/60), el usuario solicitó el único trabajo manual previsto.
La captura muestra el prefijo `50f0fcc91e82`, manual, failed/finished/
analysis_failed. Última copia del log 20:37:31 Madrid; permanece el informe
de las 19:51:52, referencia abreviada 9dd17c72e247. No se recibieron ID completo,
recibo o bytes completos del log. La autorización queda consumida; no repetir.

Logs de Groq muestra varias filas 413 para 120b/20b entre 20:38 y 20:39 Madrid.
El detalle visible de 20b indica Request too large, type=tokens,
code=rate_limit_exceeded, TPM Limit 8000 y Requested 8103. Esos números no se
atribuyen a cada fila; los ceros de consumo no acreditan coste cero o un recibo
completo. El [413 de tamaño](https://console.groq.com/docs/errors) se distingue
del [429 temporal y Retry-After](https://console.groq.com/docs/rate-limits).
Los límites exactos dependen de la organización. Reenviar el mismo mensaje no
resuelve ese exceso. No se atribuye Requested 8103 al límite de salida 8192:
no se ha capturado ni tokenizado la petición real en el servidor.

## Corrección local

- Prompt structured-prototype-9: una fila con evidence_id/line_number/raw por
  evidencia seleccionada, en JSON compacto. Conserva cada línea cruda completa,
  orden, referencias, digest y metadatos de selección; evita repetir sus campos
  parseados. El EvidenceBundle y la publicación mantienen todos sus campos.
  Selección, guardas, umbral y límites de salida/timeout no cambian.
- Los estados HTTP explícitos de hasta ocho excepciones/causas prevalecen sobre
  nombres/texto al decidir reintentos. Se controlan ciclos y propiedades; un
  estado diferente de 429 no se trata como límite temporal.
- LiteLLM convierte el 413 simulado en RateLimitError/status 429 y conserva
  debajo OpenAIError/MaskedHTTPStatusError/HTTPStatusError con 413. CrewAI
  BaseLLM instala otra envoltura de tres intentos. Corregir solo el clasificador
  propio dejó tres peticiones en el primer pase de regresión.
- Se normaliza el 413 de la cadena a ProviderRequestTooLargeError, HTTP 413 y
  mensaje fijo. Se lanza fuera de except, sin contexto implícito: CrewAI recorre
  ese contexto incluso con from None. Así se detienen repetición y fallback por
  tamaño. El diagnóstico conserva tipo permitido y estado, sin mensaje/cuerpo/
  URL del proveedor. No se parchean SDK o estado global para conseguirlo.

La política existente ante 429 permanece. La compactación no garantiza admisión
de cualquier log ni saldo TPM disponible entre etapas/clientes. Una petición
todavía demasiado grande debe terminar; no se elimina evidencia en silencio.
No se cambia clave, modelo, plan, paquetes o .env.

## Verificación offline

339 casos Python: Windows 338 aprobados y uno Linux omitido; tres comprobaciones
JS. Cuatro casos nuevos comprueban prioridad HTTP/errores envueltos/ciclos, 413
SDK/CrewAI real y prompt/publicación compactos. El 413 simulado con el código
rate_limit_exceeded termina en una sola petición, sin fallback y con los archivos
del informe previo idénticos; se verifica diagnóstico HTTP 413.

Fixture sintética de 46 líneas/30 seleccionadas: tres respuestas HTTP escritas
a mano publican XSS y fuerza bruta con las ocho referencias 39–46. La entrada
retiene todas las líneas crudas seleccionadas y la evidencia publicada coincide
con la original. Estimación local cl100k_base de la primera petición: al menos
20 % menor que reinsertando el formato anterior y menos de 7000 tokens. No es
conteo de Groq, reproducción de bytes VM ni prueba semántica del proveedor.

27 escenarios SDK, 92 archivos de sintaxis y matriz A-05 de 13 casos/siete
controles aprobados; recibo 20261015T185242433279Z. Primer pase conservado:
tres HTTP por envoltura y comparación tuple/list de fixture; se corrigieron
normalización terminal y comparación JSON, sin relajar guardas o pruebas.

Recibos ignorados `.local-state/groq-413-20261015/`; pases iniciales en
`.local-state/dvwa-post-20261015/baseline-413*.log`. Sin proveedor real, trabajo
operativo nuevo, Docker, envío o servicios operativos Windows; sin lectura de
bytes .env ni nuevo inventario operativo Windows. Pendientes publicación/CI/VM;
código CI vigente 4c2e032. Cobertura real de fuerza bruta, A-05 y confirmación
de acceso exitoso siguen abiertos.
