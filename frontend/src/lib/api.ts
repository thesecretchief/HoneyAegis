/**
 * HoneyAegis API client for the Next.js frontend.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

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
}

export interface SessionStats {
  total_sessions: number;
  unique_source_ips: number;
  successful_auths: number;
}

async function apiFetch<T>(path: string, token?: string): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE}${path}`, { headers });
  if (!res.ok) {
    throw new Error(`API error: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

export async function getSessionStats(token: string): Promise<SessionStats> {
  return apiFetch<SessionStats>("/api/v1/sessions/stats", token);
}

export async function getSessions(token: string): Promise<{ sessions: Session[]; total: number }> {
  return apiFetch("/api/v1/sessions/", token);
}
