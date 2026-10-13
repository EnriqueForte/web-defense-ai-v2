import { validReadResponse } from "./api-contracts";

export type Threat = {
  id: string;
  number: string;
  severity: string;
  type: string;
  status: string;
  source_ip: string | null;
  event_time: string | null;
  event_time_start?: string | null;
  event_time_end?: string | null;
  event_time_missing_count?: number;
  source_report_id: string | null;
};

export type ObservedEvent = {
  id: string;
  observed_at: string;
  category: string;
  source_ip: string | null;
  method: string;
  path: string;
  http_status: number;
};

export type Report = {
  id: string;
  filename: string;
  modified_at: string;
  size_bytes: number;
  current: boolean;
};

export type StateResponse = {
  meta: {
    api_version: string;
    snapshot_id: string;
    captured_at: string;
    health: "ok" | "degraded" | "unavailable";
    report_id: string | null;
    sources: Record<string, { status: string; modified_at: string | null }>;
  };
  data: {
    stats: { total: number; criticas: number; altas: number; medias: number; bajas: number; desconocidas: number; ips: number };
    threats: Threat[];
    threats_total: number;
    threats_truncated: boolean;
    recent_events: ObservedEvent[];
    recent_log: string[];
    log_period?: { first_at: string | null; last_at: string | null; undated_lines: number };
    source_ips: string[];
    timeline: { source: string; meaning: string; periods: { period: string; count: number; matches: Record<string, number> }[] };
    recent_reports: { nombre: string; fecha: string; amenazas: number }[];
  };
};

export type PageResponse<T> = {
  meta: { api_version: string; total: number; page: number; per_page: number; snapshot_id?: string; report_id?: string | null };
  data: T[];
};

export type ReportDetail = { meta: { report_id: string }; data: { report: Report; markdown: string; display_markdown?: string } };

export type AnalysisJob = {
  id: string;
  kind: "manual" | "periodic";
  status: "queued" | "running" | "succeeded" | "failed" | "interrupted";
  phase: string;
  requested_at: string;
  started_at: string | null;
  finished_at: string | null;
  last_ingested_at: string | null;
  last_analyzed_at: string | null;
  report_id: string | null;
  error_code: string | null;
  executor: "online" | "offline" | "unavailable";
  deliveries: Record<string, "attempting" | "sent" | "failed" | "unknown">;
};

export type AnalysisCurrent = { meta: { api_version: string }; data: {
  manual_enabled: boolean;
  llm_ready: boolean;
  llm_provider: string;
  executor: "online" | "offline" | "unavailable";
  job: AnalysisJob | null;
} };

export type LLMProviderOption = {
  id: string;
  label: string;
  default_model: string;
  free_models: string[];
  api_key_configured: boolean;
};

export type LLMSettings = {
  provider: string;
  model: string;
  pricing_mode: "free" | "paid";
  api_key_configured: boolean;
  providers: LLMProviderOption[];
};

export type LLMSettingsResponse = { meta: { api_version: string }; data: LLMSettings };

export async function requestAnalysis(key: string): Promise<{ job: AnalysisJob; busy: boolean }> {
  const response = await fetch("/api/v1/analisis", {
    method: "POST", cache: "no-store",
    headers: { Accept: "application/json", "Idempotency-Key": key },
  });
  const body = await response.json().catch(() => null);
  if (response.status === 202 || response.status === 409) {
    if (!validReadResponse(`analisis/${body?.data?.id}`, body)) throw new ApiError("Respuesta de trabajo inválida.", 502);
    return { job: body.data as AnalysisJob, busy: response.status === 409 };
  }
  throw new ApiError(typeof body?.error?.message === "string" ? body.error.message :
    `No se pudo solicitar el análisis (${response.status}).`, response.status);
}

export class ApiError extends Error {
  constructor(message: string, public status: number) { super(message); }
}

export const READ_TIMEOUT_MS = 10000;

export async function getApi<T>(path: string, signal?: AbortSignal, timeoutMs = READ_TIMEOUT_MS): Promise<T> {
  signal?.throwIfAborted();
  const controller = new AbortController();
  const cancel = () => controller.abort(signal?.reason);
  signal?.addEventListener('abort', cancel, { once: true });
  let onAbort: () => void = () => {};
  const canceled = new Promise<never>((_, reject) => {
    onAbort = () => reject(controller.signal.reason);
    controller.signal.addEventListener('abort', onAbort, { once: true });
  });
  const timer = setTimeout(() => controller.abort(new ApiError("La lectura superó el límite de espera. Puedes actualizar para reintentar.", 408)), timeoutMs);
  async function read(): Promise<T> {
    const response = await fetch(`/api/v1/${path}`, { cache: "no-store", signal: controller.signal, headers: { Accept: "application/json" } });
    controller.signal.throwIfAborted();
    if (!response.ok) {
      const body = await response.json().catch(() => null);
      controller.signal.throwIfAborted();
      const message = body?.error?.message;
      throw new ApiError(typeof message === "string" ? message : `La lectura falló (${response.status}).`, response.status);
    }
    const body: unknown = await response.json().catch(() => { throw new ApiError("La respuesta de lectura no contiene JSON válido.", 502); });
    controller.signal.throwIfAborted();
    if (!validReadResponse(path, body)) {
      throw new ApiError("La respuesta de lectura no coincide con el contrato de la API.", 502);
    }
    return body as T;
  }
  try { return await Promise.race([read(), canceled]); }
  finally {
    clearTimeout(timer);
    signal?.removeEventListener('abort', cancel);
    controller.signal.removeEventListener('abort', onAbort);
  }
}

export async function putApi<T>(path: string, value: unknown, signal?: AbortSignal, timeoutMs = READ_TIMEOUT_MS): Promise<T> {
  signal?.throwIfAborted();
  const controller = new AbortController();
  const cancel = () => controller.abort(signal?.reason);
  signal?.addEventListener("abort", cancel, { once: true });
  let onAbort: () => void = () => {};
  const canceled = new Promise<never>((_, reject) => {
    onAbort = () => reject(controller.signal.reason);
    controller.signal.addEventListener("abort", onAbort, { once: true });
  });
  const timer = setTimeout(() => controller.abort(new ApiError(
    "El guardado superó el límite de espera. Vuelve a consultar la configuración antes de reintentar.", 408)), timeoutMs);
  async function write(): Promise<T> {
    const response = await fetch(`/api/v1/${path}`, {
      method: "PUT", cache: "no-store", signal: controller.signal,
      headers: { Accept: "application/json", "Content-Type": "application/json" },
      body: JSON.stringify(value),
    });
    controller.signal.throwIfAborted();
    const body = await response.json().catch(() => null);
    controller.signal.throwIfAborted();
    if (!response.ok) {
      const message = body?.error?.message;
      throw new ApiError(typeof message === "string" ? message : `No se pudo guardar (${response.status}).`, response.status);
    }
    if (!validReadResponse(path, body)) {
      throw new ApiError("La respuesta de la API no tiene el formato esperado.", 502);
    }
    return body as T;
  }
  try { return await Promise.race([write(), canceled]); }
  finally {
    clearTimeout(timer);
    signal?.removeEventListener("abort", cancel);
    controller.signal.removeEventListener("abort", onAbort);
  }
}

export function validState(value: unknown): boolean {
  return validReadResponse('estado', value);
}
