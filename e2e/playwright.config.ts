import { defineConfig, devices } from "@playwright/test";

/**
 * HoneyAegis E2E Test Configuration
 *
 * Runs against the full Docker Compose stack.
 * Usage:
 *   docker compose up -d
 *   npx playwright test
 */
export default defineConfig({
  testDir: "./e2e",
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: process.env.CI ? "github" : "html",
  timeout: 30_000,

  use: {
    baseURL: process.env.E2E_BASE_URL || "http://localhost:3000",
    trace: "on-first-retry",
    screenshot: "only-on-failure",
  },

  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
    {
      name: "mobile",
      use: { ...devices["Pixel 5"] },
    },
  ],

  /* Start the full stack before running tests (local dev only) */
  ...(process.env.CI
    ? {}
    : {
        webServer: {
          command: "docker compose up -d && sleep 5",
          url: "http://localhost:3000",
          reuseExistingServer: true,
          timeout: 120_000,
        },
      }),
});
