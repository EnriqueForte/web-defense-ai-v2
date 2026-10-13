"use client";

import { useEffect, useMemo, useRef, useState, type FormEvent } from "react";
import { getApi, putApi, type LLMSettingsResponse } from "@/lib/api";

export function LLMSettings() {
  const [settings, setSettings] = useState<LLMSettingsResponse["data"] | null>(null);
  const [providerId, setProviderId] = useState("groq");
  const [pricingMode, setPricingMode] = useState<"free" | "paid">("free");
  const [model, setModel] = useState("");
  const [apiKey, setApiKey] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const lifetime = useRef<AbortController | null>(null);
  const saveInFlight = useRef(false);

  useEffect(() => {
    const controller = new AbortController();
    lifetime.current = controller;
    getApi<LLMSettingsResponse>("configuracion/llm", controller.signal)
      .then((response) => {
        if (controller.signal.aborted) return;
        setSettings(response.data);
        setProviderId(response.data.provider);
        setPricingMode(response.data.pricing_mode);
        setModel(response.data.model);
      })
      .catch((reason: unknown) => {
        if (!controller.signal.aborted) setError(reason instanceof Error ? reason.message : "No se pudo leer la configuración.");
      })
      .finally(() => { if (!controller.signal.aborted) setLoading(false); });
    return () => { controller.abort(); lifetime.current = null; };
  }, []);

  const provider = useMemo(
    () => settings?.providers.find((item) => item.id === providerId) ?? null,
    [settings, providerId],
  );

  function changeProvider(nextId: string) {
    const nextProvider = settings?.providers.find((item) => item.id === nextId);
    if (!nextProvider) return;
    setProviderId(nextId);
    setPricingMode("free");
    setModel(nextProvider.free_models[0] ?? nextProvider.default_model);
    setApiKey("");
    setNotice("");
    setError("");
  }

  function changeMode(nextMode: "free" | "paid") {
    setPricingMode(nextMode);
    if (nextMode === "free") setModel(provider?.free_models[0] ?? "");
    else if (provider?.free_models.includes(model)) setModel("");
    setNotice("");
    setError("");
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const controller = lifetime.current;
    if (!controller || controller.signal.aborted || saveInFlight.current) return;
    saveInFlight.current = true;
    setSaving(true);
    setError("");
    setNotice("");
    try {
      const response = await putApi<LLMSettingsResponse>("configuracion/llm", {
        provider: providerId,
        model: model.trim(),
        pricing_mode: pricingMode,
        api_key: apiKey,
      }, controller.signal);
      if (controller.signal.aborted) return;
      setSettings(response.data);
      setProviderId(response.data.provider);
      setPricingMode(response.data.pricing_mode);
      setModel(response.data.model);
      setApiKey("");
      setNotice("Configuración guardada. Se usará en el próximo análisis.");
    } catch (reason) {
      if (!controller.signal.aborted) setError(reason instanceof Error ? reason.message : "No se pudo guardar la configuración.");
    } finally {
      if (!controller.signal.aborted) { saveInFlight.current = false; setSaving(false); }
    }
  }

  return <section className="settings-layout">
    <article className="panel llm-settings-panel">
      <div className="panel-header">
        <div><div className="panel-kicker">PROVEEDOR DE IA</div><h2>Proveedor y modelo</h2><p>Cada instalación configura sus propias credenciales y asume los límites y costes de su cuenta.</p></div>
      </div>
      {loading && <p className="status-copy" role="status">Leyendo la configuración local…</p>}
      {error && !loading && !settings && <p className="status-copy error-copy" role="alert">{error}</p>}
      {!loading && settings && <form className="llm-settings-form" onSubmit={(event) => void submit(event)}>
        <label htmlFor="llm-provider">Proveedor</label>
        <select id="llm-provider" value={providerId} onChange={(event) => changeProvider(event.target.value)} disabled={saving}>
          {settings.providers.map((item) => <option key={item.id} value={item.id}>{item.label}{item.id === "groq" ? " · predeterminado" : ""}</option>)}
        </select>
        <p className="field-help">Groq queda seleccionado por defecto en una instalación nueva. Puedes cambiarlo cuando quieras.</p>

        <label htmlFor="llm-pricing-mode">Selección del modelo</label>
        <select id="llm-pricing-mode" value={pricingMode} onChange={(event) => changeMode(event.target.value as "free" | "paid")} disabled={saving || !provider}>
          <option value="free">Opciones gratuitas del catálogo</option>
          <option value="paid">Modelo personalizado</option>
        </select>
        {pricingMode === "free" ? <>
          <label htmlFor="llm-model">Modelo</label>
          <select id="llm-model" value={model} onChange={(event) => setModel(event.target.value)} disabled={saving || !provider}>
            {provider?.free_models.map((item) => <option key={item} value={item}>{item}</option>)}
          </select>
          <p className="field-help">La disponibilidad y los límites gratuitos dependen del proveedor y pueden cambiar.</p>
        </> : <>
          <label htmlFor="llm-model">Identificador del modelo</label>
          <input id="llm-model" value={model} onChange={(event) => setModel(event.target.value)} placeholder={provider?.id === "openrouter" ? "openrouter/organizacion/modelo" : "groq/proveedor/modelo"} autoComplete="off" spellCheck={false} disabled={saving} required />
          <p className="field-help">Usa el identificador de modelo reconocido por CrewAI/LiteLLM y con prefijo <code>{provider?.id}/</code>. Un modelo personalizado puede generar cargos según tu cuenta.</p>
        </>}

        <label htmlFor="llm-api-key">Clave API de {provider?.label ?? "proveedor"}</label>
        <input id="llm-api-key" type="password" value={apiKey} onChange={(event) => setApiKey(event.target.value)} autoComplete="new-password" placeholder={provider?.api_key_configured ? "Guardada; déjalo vacío para conservarla" : "Pega aquí tu clave API"} disabled={saving} aria-describedby="llm-key-status" />
        <p className="field-help" id="llm-key-status">{provider?.api_key_configured ? "Hay una clave guardada; nunca se vuelve a mostrar." : "Aún no hay una clave configurada para este proveedor."}</p>

        <aside className="llm-local-warning"><strong>Almacenamiento local</strong><span>Al guardar, la clave se escribe en el archivo <code>.env</code> de esta instalación. Ese archivo contiene texto sin cifrar y está excluido de Git. Mantén este dashboard en localhost y no compartas la clave ni el archivo.</span></aside>
        {error && <p className="status-copy error-copy" role="alert">{error}</p>}
        {notice && <p className="status-copy success-copy" role="status">{notice}</p>}
        <div className="settings-actions"><button className="button-primary" type="submit" disabled={saving || !provider}>{saving ? "Guardando…" : "Guardar configuración"}</button><span>El guardado no contacta al proveedor ni valida la clave.</span></div>
      </form>}
    </article>
    <aside className="panel llm-settings-note"><div className="panel-kicker">USO POR INSTALACIÓN</div><h2>Tu cuenta, tu elección</h2><p>En una instalación propia, cada usuario configura su proveedor y su clave. La app no envía credenciales a un servicio central.</p><p>“Gratuito” identifica una opción del catálogo, no garantiza disponibilidad permanente ni ausencia de costes; revisa las condiciones actuales de tu proveedor.</p></aside>
  </section>;
}
