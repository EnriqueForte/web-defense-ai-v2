import { test, expect, type Page, type Route } from "@playwright/test";

const api = process.env.WEB_DEFENSE_E2E_API!;
const key = "synthetic-e2e-openrouter-key";
const settingsPath = "**/api/v1/configuracion/llm";
const pageErrors = new WeakMap<Page, string[]>();

declare global {
  interface Window {
    settingsEvents: { get: number; put: number; abortedGet: number; abortedPut: number };
  }
}

function deferred() {
  let resolve!: () => void;
  const promise = new Promise<void>((done) => { resolve = done; });
  return { promise, resolve };
}

async function openSettings(page: Page) {
  await page.goto("/");
  await page.getByRole("button", { name: "Configuración", exact: true }).click();
  await expect(page.getByLabel("Proveedor", { exact: true })).toBeVisible();
}

async function selectOpenRouter(page: Page) {
  await page.getByLabel("Proveedor", { exact: true }).selectOption("openrouter");
  await page.getByLabel("Clave API de OpenRouter", { exact: true }).fill(key);
}

test.beforeEach(async ({ page, request }) => {
  const errors: string[] = [];
  pageErrors.set(page, errors);
  page.on("pageerror", (error) => errors.push(error.message));
  await request.post(api + "/__e2e__/control", { data: { reset: true } });
  await page.addInitScript(() => {
    window.settingsEvents = { get: 0, put: 0, abortedGet: 0, abortedPut: 0 };
    const nativeFetch = window.fetch;
    window.fetch = (input, init) => {
      const path = typeof input === "string" ? input : input instanceof URL ? input.href : input.url;
      if (new URL(path, location.href).pathname === "/api/v1/configuracion/llm") {
        const put = init?.method === "PUT";
        window.settingsEvents[put ? "put" : "get"]++;
        init?.signal?.addEventListener("abort", () => {
          window.settingsEvents[put ? "abortedPut" : "abortedGet"]++;
        }, { once: true });
      }
      return nativeFetch.call(window, input, init);
    };
  });
  // Browser traffic is restricted to the isolated frontend. No provider request.
  await page.route("**/*", async (route) => {
    const url = new URL(route.request().url());
    if (url.origin !== process.env.WEB_DEFENSE_E2E_URL) {
      throw new Error("Unexpected browser destination");
    }
    await route.continue();
  });
});

test.afterEach(async ({ page }) => {
  expect(pageErrors.get(page)).toEqual([]);
});

test("real save, blank-key retention and reload preserve settings without returning keys", async ({ page, request }) => {
  await openSettings(page);
  await expect(page.getByLabel("Proveedor", { exact: true })).toHaveValue("groq");
  await selectOpenRouter(page);
  const response = page.waitForResponse((value) => value.url().endsWith("/configuracion/llm") && value.request().method() === "PUT");
  await page.getByRole("button", { name: "Guardar configuración", exact: true }).click();
  expect((await response).status()).toBe(200);
  expect(await (await response).text()).not.toContain(key);
  await expect(page.getByText("Configuración guardada. Se usará en el próximo análisis.", { exact: true })).toBeVisible();
  await expect(page.getByLabel("Clave API de OpenRouter", { exact: true })).toHaveValue("");
  await page.getByRole("button", { name: "Guardar configuración", exact: true }).click();
  await expect(page.getByRole("button", { name: "Guardar configuración", exact: true })).toBeEnabled();
  await page.reload();
  await expect(page.getByLabel("Proveedor", { exact: true })).toHaveValue("openrouter");
  await expect(page.getByLabel("Modelo", { exact: true })).toHaveValue("openrouter/openrouter/free");
  await expect(page.getByLabel("Clave API de OpenRouter", { exact: true })).toHaveValue("");
  const receipt = await (await request.get(api + "/__e2e__/receipt")).json();
  expect(receipt).toMatchObject({ provider: "openrouter", unrelated: "synthetic-kept",
    openrouter_key_retained: true, managed_blocks: 1, jobs_db_exists: false });
  await page.getByRole("button", { name: "Resumen", exact: true }).click();
  await expect(page.getByText("LLM configurado: openrouter", { exact: true })).toBeVisible();
  await expect(page.getByRole("button", { name: "Iniciar análisis", exact: true })).toBeDisabled();
});

test("provider and pricing changes clear stale input and persist a custom model", async ({ page, request }) => {
  await openSettings(page);
  await page.getByLabel("Clave API de Groq", { exact: true }).fill("synthetic-e2e-groq-key");
  await page.getByLabel("Proveedor", { exact: true }).selectOption("openrouter");
  await expect(page.getByLabel("Clave API de OpenRouter", { exact: true })).toHaveValue("");
  await page.getByLabel("Selección del modelo", { exact: true }).selectOption("paid");
  await expect(page.getByLabel("Identificador del modelo", { exact: true })).toHaveValue("");
  await page.getByLabel("Identificador del modelo", { exact: true }).fill("openrouter/synthetic/custom");
  await page.getByLabel("Clave API de OpenRouter", { exact: true }).fill(key);
  await page.getByRole("button", { name: "Guardar configuración", exact: true }).click();
  await expect(page.getByText("Configuración guardada. Se usará en el próximo análisis.", { exact: true })).toBeVisible();
  await page.reload();
  await expect(page.getByLabel("Selección del modelo", { exact: true })).toHaveValue("paid");
  await expect(page.getByLabel("Identificador del modelo", { exact: true })).toHaveValue("openrouter/synthetic/custom");
  expect(await (await request.get(api + "/__e2e__/receipt")).json()).toMatchObject({
    mode: "paid", model: "openrouter/synthetic/custom", groq_key_retained: false });
});

test("backend validation error preserves stored configuration and allows correction", async ({ page, request }) => {
  await openSettings(page);
  await selectOpenRouter(page);
  await page.getByLabel("Selección del modelo", { exact: true }).selectOption("paid");
  await page.getByLabel("Identificador del modelo", { exact: true }).fill("groq/wrong-provider");
  await page.getByRole("button", { name: "Guardar configuración", exact: true }).click();
  await expect(page.getByRole("alert").filter({ hasText: "debe comenzar por openrouter/" })).toBeVisible();
  expect(await (await request.get(api + "/__e2e__/receipt")).json()).toMatchObject({ provider: null, managed_blocks: 0 });
  await page.getByLabel("Identificador del modelo", { exact: true }).fill("openrouter/synthetic/custom");
  await page.getByRole("button", { name: "Guardar configuración", exact: true }).click();
  await expect(page.getByText("Configuración guardada. Se usará en el próximo análisis.", { exact: true })).toBeVisible();
});

test("real lock conflict and simulated disk failure do not change configuration", async ({ page, request }) => {
  await openSettings(page);
  await selectOpenRouter(page);
  for (const mode of ["locked", "write_error"]) {
    await request.post(api + "/__e2e__/control", { data: { mode } });
    const response = page.waitForResponse((value) => value.url().endsWith("/configuracion/llm") && value.request().method() === "PUT");
    await page.getByRole("button", { name: "Guardar configuración", exact: true }).click();
    expect((await response).status()).toBe(mode === "locked" ? 409 : 500);
    await expect(page.locator(".llm-settings-panel [role=alert]")).toBeVisible();
    await expect(page.getByRole("button", { name: "Guardar configuración", exact: true })).toBeEnabled();
    expect(await (await request.get(api + "/__e2e__/receipt")).json()).toMatchObject({ provider: null, managed_blocks: 0 });
  }
  await request.post(api + "/__e2e__/control", { data: { mode: "normal" } });
  await page.getByRole("button", { name: "Guardar configuración", exact: true }).click();
  await expect(page.getByText("Configuración guardada. Se usará en el próximo análisis.", { exact: true })).toBeVisible();
});

test("malformed save response shows an error and a reload reads the committed settings", async ({ page }) => {
  await openSettings(page);
  await selectOpenRouter(page);
  await page.route(settingsPath, async (route) => {
    if (route.request().method() !== "PUT") return route.continue();
    await route.fetch(); // The real backend commits before the response is corrupted.
    await route.fulfill({ status: 200, contentType: "application/json", body: '{"data":null}' });
  });
  await page.getByRole("button", { name: "Guardar configuración", exact: true }).click();
  await expect(page.getByRole("alert").filter({ hasText: "no tiene el formato esperado" })).toBeVisible();
  expect(await page.evaluate(() => window.settingsEvents.put)).toBe(1);
  await page.reload();
  await expect(page.getByLabel("Proveedor", { exact: true })).toHaveValue("openrouter");
  await expect(page.getByLabel("Clave API de OpenRouter", { exact: true })).toHaveValue("");
});

test("leaving the view cancels the pending initial read and remount loads fresh settings", async ({ page }) => {
  await page.goto("/");
  const pending = deferred(), release = deferred();
  let first = true;
  await page.route(settingsPath, async (route) => {
    if (!first) return route.continue();
    first = false;
    pending.resolve();
    await release.promise;
    await route.abort();
  });
  await page.getByRole("button", { name: "Configuración", exact: true }).click();
  await pending.promise;
  await page.getByRole("button", { name: "Resumen", exact: true }).click();
  expect(await page.evaluate(() => window.settingsEvents.abortedGet)).toBe(1);
  release.resolve();
  await page.getByRole("button", { name: "Configuración", exact: true }).click();
  await expect(page.getByLabel("Proveedor", { exact: true })).toHaveValue("groq");
});

test("leaving during a committed save aborts the wait without repeating or undoing the write", async ({ page, request }) => {
  await openSettings(page);
  await selectOpenRouter(page);
  const committed = deferred(), release = deferred();
  await page.route(settingsPath, async (route) => {
    if (route.request().method() !== "PUT") return route.continue();
    await route.fetch();
    committed.resolve();
    await release.promise;
    await route.abort();
  });
  await page.getByRole("button", { name: "Guardar configuración", exact: true }).click();
  await committed.promise;
  await expect(page.getByRole("button", { name: "Guardando…", exact: true })).toBeDisabled();
  await page.getByRole("button", { name: "Resumen", exact: true }).click();
  expect(await page.evaluate(() => window.settingsEvents.abortedPut)).toBe(1);
  release.resolve();
  await page.getByRole("button", { name: "Configuración", exact: true }).click();
  await expect(page.getByLabel("Proveedor", { exact: true })).toHaveValue("openrouter");
  await expect(page.getByText("Configuración guardada. Se usará en el próximo análisis.", { exact: true })).not.toBeVisible();
  expect(await page.evaluate(() => window.settingsEvents.put)).toBe(1);
  expect(await (await request.get(api + "/__e2e__/receipt")).json()).toMatchObject({ openrouter_key_retained: true });
});

test("read timeout releases loading and remount can recover", async ({ page }) => {
  await page.goto("/");
  await page.clock.install();
  const pending = deferred(), release = deferred();
  let first = true;
  await page.route(settingsPath, async (route) => {
    if (!first) return route.continue();
    first = false; pending.resolve();
    await release.promise;
    await route.abort();
  });
  await page.getByRole("button", { name: "Configuración", exact: true }).click();
  await pending.promise;
  await page.clock.fastForward(10001);
  await expect(page.getByRole("alert").filter({ hasText: "La lectura superó el límite" })).toBeVisible();
  release.resolve();
  await page.getByRole("button", { name: "Resumen", exact: true }).click();
  await page.getByRole("button", { name: "Configuración", exact: true }).click();
  await expect(page.getByLabel("Proveedor", { exact: true })).toHaveValue("groq");
});

test("save timeout restores controls and requires rereading instead of automatic retry", async ({ page, request }) => {
  await openSettings(page);
  await selectOpenRouter(page);
  await page.clock.install();
  const committed = deferred(), release = deferred();
  await page.route(settingsPath, async (route: Route) => {
    if (route.request().method() !== "PUT") return route.continue();
    await route.fetch(); committed.resolve();
    await release.promise;
    await route.abort();
  });
  await page.getByRole("button", { name: "Guardar configuración", exact: true }).click();
  await committed.promise;
  await page.clock.fastForward(10001);
  await expect(page.getByRole("alert").filter({ hasText: "Vuelve a consultar la configuración antes de reintentar" })).toBeVisible();
  await expect(page.getByRole("button", { name: "Guardar configuración", exact: true })).toBeEnabled();
  expect(await page.evaluate(() => window.settingsEvents.put)).toBe(1);
  release.resolve();
  expect(await (await request.get(api + "/__e2e__/receipt")).json()).toMatchObject({ openrouter_key_retained: true });
  await page.reload();
  await expect(page.getByLabel("Proveedor", { exact: true })).toHaveValue("openrouter");
});
