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
