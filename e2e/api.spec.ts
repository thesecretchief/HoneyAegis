import { test, expect, type Page } from "@playwright/test";

const API_BASE = process.env.E2E_API_URL || "http://localhost:8000";
const ADMIN_EMAIL = process.env.E2E_ADMIN_EMAIL || "admin@honeyaegis.local";
const ADMIN_PASSWORD = process.env.E2E_ADMIN_PASSWORD || "changeme";

/**
 * Helper: Login and store JWT token.
 */
async function login(page: Page): Promise<string> {
  const res = await page.request.post(`${API_BASE}/api/v1/auth/login`, {
    form: {
      username: ADMIN_EMAIL,
      password: ADMIN_PASSWORD,
    },
  });
  expect(res.ok()).toBeTruthy();
  const data = await res.json();
  expect(data.access_token).toBeTruthy();
  return data.access_token;
}

// ---------------------------------------------------------------------------
// API Health & Auth Tests
// ---------------------------------------------------------------------------

test.describe("API Health", () => {
  test("GET /health returns healthy", async ({ request }) => {
    const res = await request.get(`${API_BASE}/health`);
    expect(res.ok()).toBeTruthy();
    const data = await res.json();
    expect(data.status).toBe("healthy");
    expect(data.version).toBe("1.0.0");
  });

  test("GET /metrics returns Prometheus metrics", async ({ request }) => {
    const res = await request.get(`${API_BASE}/metrics`);
    expect(res.ok()).toBeTruthy();
    const text = await res.text();
    expect(text).toContain("honeyaegis");
  });
});

test.describe("Authentication", () => {
  test("POST /api/v1/auth/login with valid credentials", async ({ request }) => {
    const res = await request.post(`${API_BASE}/api/v1/auth/login`, {
      form: {
        username: ADMIN_EMAIL,
        password: ADMIN_PASSWORD,
      },
    });
    expect(res.ok()).toBeTruthy();
    const data = await res.json();
    expect(data.access_token).toBeTruthy();
    expect(data.token_type).toBe("bearer");
  });

  test("POST /api/v1/auth/login with invalid credentials returns 401", async ({ request }) => {
    const res = await request.post(`${API_BASE}/api/v1/auth/login`, {
      form: {
        username: "wrong@example.com",
        password: "wrongpassword",
      },
    });
    expect(res.status()).toBe(401);
  });

  test("GET /api/v1/sessions without token returns 401", async ({ request }) => {
    const res = await request.get(`${API_BASE}/api/v1/sessions/`);
    expect(res.status()).toBe(401);
  });
});

// ---------------------------------------------------------------------------
// Authenticated API Tests
// ---------------------------------------------------------------------------

test.describe("Sessions API", () => {
  let token: string;

  test.beforeAll(async ({ browser }) => {
    const page = await browser.newPage();
    token = await login(page);
    await page.close();
  });

  test("GET /api/v1/sessions/ returns session list", async ({ request }) => {
    const res = await request.get(`${API_BASE}/api/v1/sessions/`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    expect(res.ok()).toBeTruthy();
    const data = await res.json();
    expect(data).toHaveProperty("sessions");
    expect(data).toHaveProperty("total");
    expect(Array.isArray(data.sessions)).toBeTruthy();
  });

  test("GET /api/v1/sessions/stats returns stats", async ({ request }) => {
    const res = await request.get(`${API_BASE}/api/v1/sessions/stats`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    expect(res.ok()).toBeTruthy();
    const data = await res.json();
    expect(data).toHaveProperty("total_sessions");
    expect(data).toHaveProperty("unique_source_ips");
    expect(data).toHaveProperty("sessions_today");
  });
});

test.describe("Alerts API", () => {
  let token: string;

  test.beforeAll(async ({ browser }) => {
    const page = await browser.newPage();
    token = await login(page);
    await page.close();
  });

  test("GET /api/v1/alerts/ returns alert list", async ({ request }) => {
    const res = await request.get(`${API_BASE}/api/v1/alerts/`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    expect(res.ok()).toBeTruthy();
    const data = await res.json();
    expect(data).toHaveProperty("alerts");
    expect(data).toHaveProperty("total");
  });
});

test.describe("Honey Tokens API", () => {
  let token: string;

  test.beforeAll(async ({ browser }) => {
    const page = await browser.newPage();
    token = await login(page);
    await page.close();
  });

  test("GET /api/v1/honey-tokens/ returns token list", async ({ request }) => {
    const res = await request.get(`${API_BASE}/api/v1/honey-tokens/`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    expect(res.ok()).toBeTruthy();
    const data = await res.json();
    expect(data).toHaveProperty("tokens");
    expect(data).toHaveProperty("total");
  });

  test("POST + DELETE honey token lifecycle", async ({ request }) => {
    // Create
    const createRes = await request.post(`${API_BASE}/api/v1/honey-tokens/`, {
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      data: {
        name: "e2e-test-token",
        token_type: "credential",
        username: "e2e_admin",
        password: "e2e_password_123",
        alert_severity: "high",
      },
    });
    expect(createRes.ok()).toBeTruthy();
    const created = await createRes.json();
    expect(created.id).toBeTruthy();

    // Delete
    const deleteRes = await request.delete(
      `${API_BASE}/api/v1/honey-tokens/${created.id}`,
      { headers: { Authorization: `Bearer ${token}` } },
    );
    expect(deleteRes.ok()).toBeTruthy();
  });
});

test.describe("Webhooks API", () => {
  let token: string;

  test.beforeAll(async ({ browser }) => {
    const page = await browser.newPage();
    token = await login(page);
    await page.close();
  });

  test("GET /api/v1/webhooks/ returns webhook list", async ({ request }) => {
    const res = await request.get(`${API_BASE}/api/v1/webhooks/`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    expect(res.ok()).toBeTruthy();
    const data = await res.json();
    expect(data).toHaveProperty("webhooks");
    expect(data).toHaveProperty("total");
  });
});

test.describe("Console API", () => {
  let token: string;

  test.beforeAll(async ({ browser }) => {
    const page = await browser.newPage();
    token = await login(page);
    await page.close();
  });

  test("GET /api/v1/console/stats returns aggregated stats", async ({ request }) => {
    const res = await request.get(`${API_BASE}/api/v1/console/stats`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    expect(res.ok()).toBeTruthy();
    const data = await res.json();
    expect(data).toHaveProperty("total_deployments");
    expect(data).toHaveProperty("total_sensors");
  });

  test("GET /api/v1/console/license returns community tier", async ({ request }) => {
    const res = await request.get(`${API_BASE}/api/v1/console/license`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    expect(res.ok()).toBeTruthy();
    const data = await res.json();
    expect(data.tier).toBe("community");
    expect(data.max_sensors).toBe(999);
  });
});

test.describe("SIEM Export API", () => {
  let token: string;

  test.beforeAll(async ({ browser }) => {
    const page = await browser.newPage();
    token = await login(page);
    await page.close();
  });

  test("GET /api/v1/export/json returns structured events", async ({ request }) => {
    const res = await request.get(`${API_BASE}/api/v1/export/json?limit=10`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    expect(res.ok()).toBeTruthy();
    const data = await res.json();
    expect(data.format).toBe("honeyaegis-json");
    expect(data).toHaveProperty("events");
    expect(data).toHaveProperty("count");
  });

  test("GET /api/v1/export/cef returns CEF lines", async ({ request }) => {
    const res = await request.get(`${API_BASE}/api/v1/export/cef?limit=10`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    expect(res.ok()).toBeTruthy();
    const data = await res.json();
    expect(data.format).toBe("cef");
  });

  test("GET /api/v1/export/syslog returns syslog lines", async ({ request }) => {
    const res = await request.get(`${API_BASE}/api/v1/export/syslog?limit=10`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    expect(res.ok()).toBeTruthy();
    const data = await res.json();
    expect(data.format).toBe("syslog");
  });
});
