/**
 * HoneyAegis API client for the Next.js frontend.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const WS_BASE = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000/ws";

// -- Types ------------------------------------------------------------------

export interface Session {
  id: string;
  session_id: string;
  protocol: string;
  src_ip: string;
  src_port: number | null;
  dst_port: number | null;
  username: string | null;
  auth_success: boolean;
  duration_seconds: number | null;
  commands_count: number;
  started_at: string;
  ended_at: string | null;
  country_code: string | null;
  country_name: string | null;
  city: string | null;
  latitude: number | null;
  longitude: number | null;
}

export interface SessionStats {
  total_sessions: number;
  unique_source_ips: number;
  successful_auths: number;
  sessions_today: number;
  unique_ips_today: number;
  top_ports: { port: number; count: number }[];
  top_countries: { country_code: string; country_name: string; count: number }[];
  top_usernames: { username: string; count: number }[];
}

export interface GeoPoint {
  src_ip: string;
  latitude: number;
  longitude: number;
  country_code: string;
  country_name: string;
  city: string | null;
  session_count: number;
  last_seen: string | null;
}

export interface Alert {
  id: string;
  session_id: string | null;
  alert_type: string;
  severity: string;
  title: string;
  description: string | null;
  acknowledged: boolean;
  created_at: string;
}

export interface ReplayData {
  asciicast: string;
  header: {
    version: number;
    width: number;
    height: number;
    duration: number;
    title: string;
  };
  event_count: number;
}

export interface SessionCommand {
  command: string;
  output: string | null;
  timestamp: string | null;
}

export interface WSEvent {
  type: string;
  session_id: string;
  src_ip: string;
  timestamp: string;
  [key: string]: unknown;
}

// -- Auth -------------------------------------------------------------------

let _token: string | null = null;

export function setToken(token: string) {
  _token = token;
  if (typeof window !== "undefined") {
    localStorage.setItem("honeyaegis_token", token);
  }
}

export function getToken(): string | null {
  if (_token) return _token;
  if (typeof window !== "undefined") {
    _token = localStorage.getItem("honeyaegis_token");
  }
  return _token;
}

export function clearToken() {
  _token = null;
  if (typeof window !== "undefined") {
    localStorage.removeItem("honeyaegis_token");
  }
}

// -- Fetch ------------------------------------------------------------------

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options?.headers as Record<string, string> || {}),
  };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });
  if (res.status === 401) {
    clearToken();
    if (typeof window !== "undefined") {
      window.location.href = "/login";
    }
    throw new Error("Unauthorized");
  }
  if (!res.ok) {
    throw new Error(`API error: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

// -- Auth API ---------------------------------------------------------------

export async function login(email: string, password: string): Promise<string> {
  const formData = new URLSearchParams();
  formData.append("username", email);
  formData.append("password", password);

  const res = await fetch(`${API_BASE}/api/v1/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: formData.toString(),
  });

  if (!res.ok) {
    throw new Error("Invalid credentials");
  }

  const data = await res.json();
  setToken(data.access_token);
  return data.access_token;
}

// -- Sessions API -----------------------------------------------------------

export async function getSessionStats(): Promise<SessionStats> {
  return apiFetch<SessionStats>("/api/v1/sessions/stats");
}

export async function getSessions(
  params?: { limit?: number; offset?: number; protocol?: string; src_ip?: string }
): Promise<{ sessions: Session[]; total: number }> {
  const searchParams = new URLSearchParams();
  if (params?.limit) searchParams.set("limit", params.limit.toString());
  if (params?.offset) searchParams.set("offset", params.offset.toString());
  if (params?.protocol) searchParams.set("protocol", params.protocol);
  if (params?.src_ip) searchParams.set("src_ip", params.src_ip);
  const qs = searchParams.toString();
  return apiFetch(`/api/v1/sessions/${qs ? `?${qs}` : ""}`);
}

export async function getSession(id: string): Promise<Session> {
  return apiFetch<Session>(`/api/v1/sessions/${id}`);
}

export async function getMapData(hours?: number): Promise<GeoPoint[]> {
  const qs = hours ? `?hours=${hours}` : "";
  return apiFetch<GeoPoint[]>(`/api/v1/sessions/map${qs}`);
}

// -- Replay API -------------------------------------------------------------

export async function getSessionReplay(sessionId: string): Promise<ReplayData> {
  return apiFetch<ReplayData>(`/api/v1/sessions/${sessionId}/replay`);
}

export async function getSessionCommands(sessionId: string): Promise<SessionCommand[]> {
  return apiFetch<SessionCommand[]>(`/api/v1/sessions/${sessionId}/commands`);
}

export function getVideoExportUrl(sessionId: string, format: "mp4" | "gif" = "mp4"): string {
  return `${API_BASE}/api/v1/sessions/${sessionId}/video?format=${format}`;
}

// -- Alerts API -------------------------------------------------------------

export async function getAlerts(
  params?: { limit?: number; offset?: number; severity?: string; acknowledged?: boolean }
): Promise<{ alerts: Alert[]; total: number }> {
  const searchParams = new URLSearchParams();
  if (params?.limit) searchParams.set("limit", params.limit.toString());
  if (params?.offset) searchParams.set("offset", params.offset.toString());
  if (params?.severity) searchParams.set("severity", params.severity);
  if (params?.acknowledged !== undefined) searchParams.set("acknowledged", params.acknowledged.toString());
  const qs = searchParams.toString();
  return apiFetch(`/api/v1/alerts/${qs ? `?${qs}` : ""}`);
}

export async function acknowledgeAlert(alertId: string): Promise<void> {
  await apiFetch(`/api/v1/alerts/${alertId}/acknowledge`, { method: "POST" });
}

export async function acknowledgeAllAlerts(): Promise<void> {
  await apiFetch("/api/v1/alerts/acknowledge-all", { method: "POST" });
}

// -- AI Summary API ---------------------------------------------------------

export interface AISummary {
  id: string;
  session_id: string;
  summary: string;
  threat_level: string | null;
  mitre_ttps: string[];
  recommendations: string | null;
  model_used: string | null;
  created_at: string;
}

export interface AIStatus {
  enabled: boolean;
  available: boolean;
  model: string;
}

export async function getAIStatus(): Promise<AIStatus> {
  return apiFetch<AIStatus>("/api/v1/sessions/ai/status");
}

export async function getAISummary(sessionId: string): Promise<AISummary | null> {
  return apiFetch<AISummary | null>(`/api/v1/sessions/${sessionId}/ai-summary`);
}

export async function generateAISummary(sessionId: string): Promise<AISummary> {
  return apiFetch<AISummary>(`/api/v1/sessions/${sessionId}/ai-summary`, {
    method: "POST",
  });
}

// -- Sensors API ------------------------------------------------------------

export interface Sensor {
  id: string;
  sensor_id: string;
  name: string;
  hostname: string | null;
  ip_address: string | null;
  status: string;
  last_seen: string | null;
  config: Record<string, unknown>;
  session_count: number;
  created_at: string;
  updated_at: string;
}

export async function getSensors(): Promise<{ sensors: Sensor[]; total: number }> {
  return apiFetch("/api/v1/sensors/");
}

export async function registerSensor(data: {
  sensor_id: string;
  name: string;
  hostname?: string;
  ip_address?: string;
}): Promise<Sensor> {
  return apiFetch<Sensor>("/api/v1/sensors/register", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function deleteSensor(sensorId: string): Promise<void> {
  await apiFetch(`/api/v1/sensors/${sensorId}`, { method: "DELETE" });
}

// -- Config API -------------------------------------------------------------

export interface HoneypotConfig {
  name: string;
  enabled: boolean;
  ports: number[];
  description: string;
}

export interface AlertRuleConfig {
  alert_on_new_session: boolean;
  alert_on_malware_capture: boolean;
  cooldown_minutes: number;
  apprise_urls: string[];
}

export interface PlatformConfig {
  honeypots: HoneypotConfig[];
  alert_rules: AlertRuleConfig;
  silence_windows: unknown[];
  ai_enabled: boolean;
  ai_model: string;
  fleet_mode: string;
}

export async function getPlatformConfig(): Promise<PlatformConfig> {
  return apiFetch<PlatformConfig>("/api/v1/config/");
}

export async function updateAlertRules(data: {
  alert_on_new_session?: boolean;
  alert_on_malware_capture?: boolean;
  cooldown_minutes?: number;
}): Promise<void> {
  await apiFetch("/api/v1/config/alerts", {
    method: "PATCH",
    body: JSON.stringify(data),
  });
}

// -- Reports API ------------------------------------------------------------

export async function downloadReport(
  format: "json" | "pdf",
  sessionId?: string,
): Promise<void> {
  const qs = sessionId ? `?session_id=${sessionId}` : "";
  const path = `/api/v1/reports/${format}${qs}`;
  const token = getToken();
  const headers: Record<string, string> = {};
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE}${path}`, { headers });
  if (res.status === 401) {
    clearToken();
    if (typeof window !== "undefined") window.location.href = "/login";
    return;
  }
  if (!res.ok) throw new Error(`Report download failed: ${res.status}`);

  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  const ext = format === "pdf" ? "pdf" : "json";
  a.download = sessionId
    ? `honeyaegis-report-${sessionId.slice(0, 8)}.${ext}`
    : `honeyaegis-report.${ext}`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

// -- Tenants API ------------------------------------------------------------

export interface TenantBranding {
  id: string;
  slug: string;
  name: string;
  display_name: string | null;
  primary_color: string;
  logo_url: string | null;
}

export async function getTenantBranding(): Promise<TenantBranding> {
  return apiFetch<TenantBranding>("/api/v1/tenants/branding");
}

export async function updateTenantBranding(data: {
  display_name?: string;
  primary_color?: string;
  logo_url?: string;
}): Promise<TenantBranding> {
  // We need the tenant ID first
  const branding = await getTenantBranding();
  return apiFetch<TenantBranding>(`/api/v1/tenants/${branding.id}`, {
    method: "PATCH",
    body: JSON.stringify(data),
  });
}

// -- Honey Tokens API -------------------------------------------------------

export interface HoneyTokenData {
  id: string;
  token_type: string;
  name: string;
  description: string | null;
  username: string | null;
  password: string | null;
  filename: string | null;
  is_active: boolean;
  trigger_count: number;
  last_triggered_at: string | null;
  alert_severity: string;
  webhook_url: string | null;
  created_at: string;
}

export async function getHoneyTokens(): Promise<{ tokens: HoneyTokenData[]; total: number }> {
  return apiFetch("/api/v1/honey-tokens/");
}

export async function createHoneyToken(data: {
  name: string;
  token_type?: string;
  username?: string;
  password?: string;
  filename?: string;
  alert_severity?: string;
}): Promise<{ id: string }> {
  return apiFetch("/api/v1/honey-tokens/", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function deleteHoneyToken(tokenId: string): Promise<void> {
  await apiFetch(`/api/v1/honey-tokens/${tokenId}`, { method: "DELETE" });
}

// -- Webhooks API -----------------------------------------------------------

export interface WebhookData {
  id: string;
  name: string;
  url: string;
  description: string | null;
  trigger_on: string;
  severity_filter: string | null;
  http_method: string;
  is_active: boolean;
  execution_count: number;
  last_executed_at: string | null;
  last_status_code: number | null;
  created_at: string;
}

export async function getWebhooks(): Promise<{ webhooks: WebhookData[]; total: number }> {
  return apiFetch("/api/v1/webhooks/");
}

export async function createWebhook(data: {
  name: string;
  url: string;
  trigger_on?: string;
  severity_filter?: string;
}): Promise<{ id: string }> {
  return apiFetch("/api/v1/webhooks/", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function deleteWebhook(webhookId: string): Promise<void> {
  await apiFetch(`/api/v1/webhooks/${webhookId}`, { method: "DELETE" });
}

export async function testWebhook(webhookId: string): Promise<{ status: string; response_code: number }> {
  return apiFetch(`/api/v1/webhooks/${webhookId}/test`, { method: "POST" });
}

// -- Plugins API ------------------------------------------------------------

export interface PluginData {
  name: string;
  version: string;
  description: string;
  plugin_type: string;
  author: string;
  enabled: boolean;
}

export async function getPlugins(): Promise<{ plugins: PluginData[] }> {
  return apiFetch("/api/v1/plugins/");
}

// -- WebSocket --------------------------------------------------------------

export function connectWebSocket(
  onMessage: (event: WSEvent) => void,
  onError?: (err: Event) => void,
): WebSocket {
  const ws = new WebSocket(WS_BASE);

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      onMessage(data);
    } catch {
      // ignore non-JSON messages like "pong"
    }
  };

  ws.onerror = (err) => {
    if (onError) onError(err);
  };

  // Keep alive
  const pingInterval = setInterval(() => {
    if (ws.readyState === WebSocket.OPEN) {
      ws.send("ping");
    }
  }, 30000);

  ws.onclose = () => {
    clearInterval(pingInterval);
  };

  return ws;
}

// -- SIEM Export ---------------------------------------------------------------

export async function exportSIEM(format: "json" | "cef" | "syslog", limit = 100): Promise<any> {
  return apiFetch<any>(`/api/v1/export/${format}?limit=${limit}`);
}
