import type { Report } from "./api";

/** Follow a new current publication; keep explicitly selected historical reports. */
export function refreshedReportSelection(selected: string, previous: Report[], next: Report[]): string {
  if (!previous.some((report) => report.id === selected && report.current)) return selected;
  return next.find((report) => report.current)?.id ?? selected;
}
