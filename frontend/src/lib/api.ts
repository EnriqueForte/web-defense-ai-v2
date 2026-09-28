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

export function validState(value: StateResponse): boolean {
  return value.meta.api_version === "1" && typeof value.meta.snapshot_id === "string" &&
    typeof value.data.stats?.total === "number" && Array.isArray(value.data.threats) &&
    Array.isArray(value.data.recent_log) && Array.isArray(value.data.timeline?.periods);
}
