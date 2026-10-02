export type Threat = {
  id: string;
  number: string;
  severity: string;
  type: string;
  status: string;
  source_ip: string | null;
  event_time: string | null;
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
    source_ips: string[];
    timeline: { source: string; meaning: string; periods: { period: string; count: number; matches: Record<string, number> }[] };
    recent_reports: { nombre: string; fecha: string; amenazas: number }[];
  };
};

export type PageResponse<T> = {
  meta: { api_version: string; total: number; page: number; per_page: number; snapshot_id?: string; report_id?: string | null };
  data: T[];
};

export type ReportDetail = { meta: { report_id: string }; data: { report: Report; markdown: string } };

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
    if (typeof body?.data?.id !== "string") throw new ApiError("Respuesta de trabajo inválida.", 502);
    return { job: body.data as AnalysisJob, busy: response.status === 409 };
  }
  throw new ApiError(typeof body?.error?.message === "string" ? body.error.message :
    `No se pudo solicitar el análisis (${response.status}).`, response.status);
}

export class ApiError extends Error {
  constructor(message: string, public status: number) { super(message); }
}

export async function getApi<T>(path: string, signal?: AbortSignal): Promise<T> {
  const response = await fetch(`/api/v1/${path}`, { cache: "no-store", signal, headers: { Accept: "application/json" } });
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    const message = body?.error?.message;
    throw new ApiError(typeof message === "string" ? message : `La lectura falló (${response.status}).`, response.status);
  }
  const body: unknown = await response.json();
  if (!body || typeof body !== "object" || !("meta" in body) || !("data" in body)) {
    throw new ApiError("La respuesta de la API no tiene el formato esperado.", 502);
  }
  return body as T;
}

export async function putApi<T>(path: string, value: unknown): Promise<T> {
  const response = await fetch(`/api/v1/${path}`, {
    method: "PUT", cache: "no-store",
    headers: { Accept: "application/json", "Content-Type": "application/json" },
    body: JSON.stringify(value),
  });
  const body = await response.json().catch(() => null);
  if (!response.ok) {
    const message = body?.error?.message;
    throw new ApiError(typeof message === "string" ? message : `No se pudo guardar (${response.status}).`, response.status);
  }
  if (!body || typeof body !== "object" || !("meta" in body) || !("data" in body)) {
    throw new ApiError("La respuesta de la API no tiene el formato esperado.", 502);
  }
  return body as T;
}

export function validState(value: StateResponse): boolean {
  return value.meta.api_version === "1" && typeof value.meta.snapshot_id === "string" &&
    typeof value.data.stats?.total === "number" && Array.isArray(value.data.threats) &&
    Array.isArray(value.data.recent_log) && Array.isArray(value.data.recent_events) &&
    Array.isArray(value.data.timeline?.periods);
}
