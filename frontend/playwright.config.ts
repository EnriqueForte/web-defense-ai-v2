import { defineConfig } from "@playwright/test";

// Only the isolated Python supervisor supplies these URLs and output paths.
const baseURL = process.env.WEB_DEFENSE_E2E_URL;
const apiURL = process.env.WEB_DEFENSE_E2E_API;
if (!baseURL || !apiURL || !process.env.WEB_DEFENSE_E2E_RESULTS ||
    ![baseURL, apiURL].every((url) => /^http:\/\/127\.0\.0\.1:\d+$/.test(url) &&
      !["3000", "5000"].includes(new URL(url).port))) {
  throw new Error("Usa scripts/check_settings_e2e.py con un entorno Python de pruebas.");
}

export default defineConfig({
  testDir: "./e2e",
  fullyParallel: false,
  workers: 1,
  retries: 0,
  timeout: 45000,
  expect: { timeout: 7000 },
  outputDir: process.env.WEB_DEFENSE_E2E_RESULTS,
  reporter: [["list"]],
  use: { baseURL, browserName: "chromium", viewport: { width: 1440, height: 1000 },
    trace: "retain-on-failure", screenshot: "only-on-failure" },
});
