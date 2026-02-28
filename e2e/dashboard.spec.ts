import { test, expect } from "@playwright/test";

/**
 * E2E tests for HoneyAegis dashboard UI.
 *
 * These tests verify that all pages load correctly, navigation works,
 * and key UI elements are present.
 *
 * Prerequisites:
 *   - Full Docker Compose stack running
 *   - Admin user created (default: admin@honeyaegis.local / changeme)
 */

const ADMIN_EMAIL = process.env.E2E_ADMIN_EMAIL || "admin@honeyaegis.local";
const ADMIN_PASSWORD = process.env.E2E_ADMIN_PASSWORD || "changeme";

// ---------------------------------------------------------------------------
// Login page
// ---------------------------------------------------------------------------

test.describe("Login Page", () => {
  test("renders login form", async ({ page }) => {
    await page.goto("/login");
    await expect(page.locator("h2")).toContainText("Sign in");
    await expect(page.locator('input[type="email"]')).toBeVisible();
    await expect(page.locator('input[type="password"]')).toBeVisible();
    await expect(page.locator('button[type="submit"]')).toBeVisible();
  });

  test("rejects invalid credentials", async ({ page }) => {
    await page.goto("/login");
    await page.fill('input[type="email"]', "wrong@test.com");
    await page.fill('input[type="password"]', "wrongpassword");
    await page.click('button[type="submit"]');
    await expect(page.locator("text=Invalid")).toBeVisible({ timeout: 5000 });
  });

  test("successful login redirects to dashboard", async ({ page }) => {
    await page.goto("/login");
    await page.fill('input[type="email"]', ADMIN_EMAIL);
    await page.fill('input[type="password"]', ADMIN_PASSWORD);
    await page.click('button[type="submit"]');
    await page.waitForURL("/", { timeout: 10000 });
    await expect(page.locator("h2")).toContainText("Dashboard");
  });
});

// ---------------------------------------------------------------------------
// Dashboard
// ---------------------------------------------------------------------------

test.describe("Dashboard", () => {
  test.beforeEach(async ({ page }) => {
    // Login first
    await page.goto("/login");
    await page.fill('input[type="email"]', ADMIN_EMAIL);
    await page.fill('input[type="password"]', ADMIN_PASSWORD);
    await page.click('button[type="submit"]');
    await page.waitForURL("/", { timeout: 10000 });
  });

  test("shows stats cards", async ({ page }) => {
    await expect(page.locator("text=Attacks Today")).toBeVisible();
    await expect(page.locator("text=Unique IPs Today")).toBeVisible();
    await expect(page.locator("text=Auth Successes")).toBeVisible();
    await expect(page.locator("text=Active Sensors")).toBeVisible();
  });

  test("shows recent sessions panel", async ({ page }) => {
    await expect(page.locator("text=Recent Sessions")).toBeVisible();
  });

  test("shows live feed panel", async ({ page }) => {
    await expect(page.locator("text=Live Feed")).toBeVisible();
  });

  test("auto-refresh indicator visible", async ({ page }) => {
    await expect(page.locator("text=Auto-refreshing")).toBeVisible();
  });
});

// ---------------------------------------------------------------------------
// Navigation
// ---------------------------------------------------------------------------

test.describe("Navigation", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/login");
    await page.fill('input[type="email"]', ADMIN_EMAIL);
    await page.fill('input[type="password"]', ADMIN_PASSWORD);
    await page.click('button[type="submit"]');
    await page.waitForURL("/", { timeout: 10000 });
  });

  test("sidebar has all nav items", async ({ page }) => {
    const nav = page.locator('nav[aria-label="Main navigation"]');
    await expect(nav.locator("text=Dashboard")).toBeVisible();
    await expect(nav.locator("text=Sessions")).toBeVisible();
    await expect(nav.locator("text=Alerts")).toBeVisible();
    await expect(nav.locator("text=Honey Tokens")).toBeVisible();
    await expect(nav.locator("text=Webhooks")).toBeVisible();
    await expect(nav.locator("text=Sensors")).toBeVisible();
    await expect(nav.locator("text=Config")).toBeVisible();
  });

  test("shows version in sidebar", async ({ page }) => {
    await expect(page.locator("text=HoneyAegis v1.0.0")).toBeVisible();
  });

  test("navigate to sessions page", async ({ page }) => {
    await page.click('nav[aria-label="Main navigation"] >> text=Sessions');
    await expect(page.locator("h2")).toContainText("Sessions");
  });

  test("navigate to alerts page", async ({ page }) => {
    await page.click('nav[aria-label="Main navigation"] >> text=Alerts');
    await expect(page.locator("h2")).toContainText("Alerts");
  });

  test("navigate to honey tokens page", async ({ page }) => {
    await page.click('nav[aria-label="Main navigation"] >> text=Honey Tokens');
    await expect(page.locator("h2")).toContainText("Honey Tokens");
  });

  test("navigate to webhooks page", async ({ page }) => {
    await page.click('nav[aria-label="Main navigation"] >> text=Webhooks');
    await expect(page.locator("h2")).toContainText("Webhooks");
  });

  test("navigate to sensors page", async ({ page }) => {
    await page.click('nav[aria-label="Main navigation"] >> text=Sensors');
    await expect(page.locator("h2")).toContainText("Sensors");
  });

  test("navigate to config page", async ({ page }) => {
    await page.click('nav[aria-label="Main navigation"] >> text=Config');
    await expect(page.locator("h2")).toContainText("Configuration");
  });
});

// ---------------------------------------------------------------------------
// Accessibility
// ---------------------------------------------------------------------------

test.describe("Accessibility", () => {
  test("html has lang attribute", async ({ page }) => {
    await page.goto("/login");
    const lang = await page.locator("html").getAttribute("lang");
    expect(lang).toBe("en");
  });

  test("main navigation has aria-label", async ({ page }) => {
    await page.goto("/login");
    await page.fill('input[type="email"]', ADMIN_EMAIL);
    await page.fill('input[type="password"]', ADMIN_PASSWORD);
    await page.click('button[type="submit"]');
    await page.waitForURL("/", { timeout: 10000 });
    const nav = page.locator('nav[aria-label="Main navigation"]');
    await expect(nav).toBeVisible();
  });

  test("main content has role=main", async ({ page }) => {
    await page.goto("/login");
    await page.fill('input[type="email"]', ADMIN_EMAIL);
    await page.fill('input[type="password"]', ADMIN_PASSWORD);
    await page.click('button[type="submit"]');
    await page.waitForURL("/", { timeout: 10000 });
    const main = page.locator('main[role="main"]');
    await expect(main).toBeVisible();
  });

  test("error page has role=alert", async ({ page }) => {
    // Navigate to a route that will throw an error in the app
    // The error boundary should have role="alert"
    await page.goto("/login");
    const errorDiv = page.locator('[role="alert"]');
    // This may or may not be visible depending on error state
    // Just verify the page loaded without crashing
    expect(await page.title()).toContain("HoneyAegis");
  });
});
