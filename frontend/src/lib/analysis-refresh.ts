import type { AnalysisJob } from "./api";

/** Refresh source reads once when ingestion or a successful publication changes. */
export function analysisSourcesChanged(previous: AnalysisJob | null, next: AnalysisJob | null): boolean {
  if (!next) return false;
  const sameJob = previous?.id === next.id;
  const ingested = next.last_ingested_at !== null &&
    (!sameJob || previous?.last_ingested_at !== next.last_ingested_at);
  const published = next.status === "succeeded" && next.report_id !== null &&
    (!sameJob || previous?.status !== "succeeded" || previous?.report_id !== next.report_id);
  return ingested || published;
}
