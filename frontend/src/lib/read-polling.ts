/** Completion-based polling; visibility/manual triggers share the same in-flight read. */
export function startReadPolling(read: (signal: AbortSignal) => Promise<void>, interval: number, enabled = () => true) {
  const controller = new AbortController();
  let timer: ReturnType<typeof setTimeout> | undefined;
  let running = false;
  function schedule() {
    if (!controller.signal.aborted) timer = setTimeout(() => void request(), interval);
  }
  async function request() {
    if (controller.signal.aborted || running) return;
    clearTimeout(timer);
    if (!enabled()) { schedule(); return; }
    running = true;
    try { await read(controller.signal); }
    catch { /* The read callback owns its error state; keep polling after failure. */ }
    finally { running = false; schedule(); }
  }
  queueMicrotask(() => void request());
  return { request, stop: () => { controller.abort(); clearTimeout(timer); } };
}
