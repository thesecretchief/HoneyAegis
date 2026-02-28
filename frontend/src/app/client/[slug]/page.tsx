"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface Branding {
  name: string;
  primary_color: string;
  logo_url: string | null;
}

interface PortalStats {
  total_sessions: number;
  unique_source_ips: number;
  successful_auths: number;
  sessions_today: number;
  unique_ips_today: number;
}

interface PortalSession {
  id: string;
  session_id: string;
  protocol: string;
  src_ip: string;
  dst_port: number | null;
  username: string | null;
  auth_success: boolean;
  duration_seconds: number | null;
  commands_count: number;
  started_at: string;
  ended_at: string | null;
  country_name: string | null;
  country_code: string | null;
}

async function portalFetch<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`);
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export default function ClientPortalPage() {
  const params = useParams();
  const slug = params.slug as string;

  const [branding, setBranding] = useState<Branding | null>(null);
  const [stats, setStats] = useState<PortalStats | null>(null);
  const [sessions, setSessions] = useState<PortalSession[]>([]);
  const [alertCount, setAlertCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [activeTab, setActiveTab] = useState<"overview" | "sessions">("overview");

  useEffect(() => {
    async function fetchData() {
      try {
        const [brandingData, statsData, sessionsData, alertData] = await Promise.all([
          portalFetch<Branding>(`/api/v1/client/${slug}/branding`),
          portalFetch<PortalStats>(`/api/v1/client/${slug}/stats`),
          portalFetch<{ sessions: PortalSession[]; total: number }>(`/api/v1/client/${slug}/sessions?limit=50`),
          portalFetch<{ unacknowledged_alerts: number }>(`/api/v1/client/${slug}/alerts/count`),
        ]);
        setBranding(brandingData);
        setStats(statsData);
        setSessions(sessionsData.sessions);
        setAlertCount(alertData.unacknowledged_alerts);
      } catch {
        setError("Portal not found or unavailable.");
      } finally {
        setLoading(false);
      }
    }

    fetchData();
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, [slug]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-950 flex items-center justify-center">
        <div className="text-gray-500">Loading portal...</div>
      </div>
    );
  }

  if (error || !branding) {
    return (
      <div className="min-h-screen bg-gray-950 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-300 mb-2">Portal Not Found</h1>
          <p className="text-gray-500">{error || "This client portal does not exist."}</p>
        </div>
      </div>
    );
  }

  const primaryColor = branding.primary_color || "#f59e0b";

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100">
      {/* Header */}
      <header className="border-b border-gray-800 bg-gray-900">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            {branding.logo_url && (
              <img src={branding.logo_url} alt={branding.name} className="h-8 w-8 rounded" />
            )}
            <div>
              <h1 className="text-lg font-bold" style={{ color: primaryColor }}>
                {branding.name}
              </h1>
              <p className="text-xs text-gray-500">Security Monitoring Portal</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            {alertCount > 0 && (
              <span className="px-2 py-1 bg-red-900/60 text-red-400 rounded-full text-xs font-bold">
                {alertCount} alert{alertCount !== 1 ? "s" : ""}
              </span>
            )}
            <span className="text-xs text-gray-500">View-only access</span>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 py-6">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <StatCard title="Attacks Today" value={stats?.sessions_today ?? 0} subtitle={`${stats?.total_sessions ?? 0} total`} color="text-red-400" />
          <StatCard title="Unique IPs Today" value={stats?.unique_ips_today ?? 0} subtitle={`${stats?.unique_source_ips ?? 0} total`} color="text-blue-400" />
          <StatCard title="Auth Successes" value={stats?.successful_auths ?? 0} subtitle="Accepted by honeypot" color="text-yellow-400" />
          <StatCard title="Active Alerts" value={alertCount} subtitle="Unacknowledged" color="text-orange-400" />
        </div>

        {/* Tabs */}
        <div className="flex gap-1 mb-4 border-b border-gray-800">
          <button
            onClick={() => setActiveTab("overview")}
            className={`px-4 py-2 text-sm transition-colors border-b-2 ${
              activeTab === "overview"
                ? "border-current text-gray-100"
                : "border-transparent text-gray-500 hover:text-gray-300"
            }`}
            style={activeTab === "overview" ? { borderColor: primaryColor } : {}}
          >
            Overview
          </button>
          <button
            onClick={() => setActiveTab("sessions")}
            className={`px-4 py-2 text-sm transition-colors border-b-2 ${
              activeTab === "sessions"
                ? "border-current text-gray-100"
                : "border-transparent text-gray-500 hover:text-gray-300"
            }`}
            style={activeTab === "sessions" ? { borderColor: primaryColor } : {}}
          >
            Sessions ({sessions.length})
          </button>
        </div>

        {/* Overview Tab */}
        {activeTab === "overview" && (
          <div className="space-y-6">
            <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
              <h3 className="text-lg font-semibold mb-4">Recent Attacks</h3>
              {sessions.length === 0 ? (
                <p className="text-gray-500 text-sm">No sessions recorded yet.</p>
              ) : (
                <div className="space-y-2">
                  {sessions.slice(0, 10).map((session) => (
                    <div
                      key={session.id}
                      className="flex items-center justify-between p-3 rounded-lg bg-gray-800/50"
                    >
                      <div className="flex items-center gap-3">
                        <span className={`w-2 h-2 rounded-full ${session.ended_at ? "bg-gray-500" : "bg-green-400 animate-pulse"}`} />
                        <div>
                          <p className="text-sm font-mono">{session.src_ip}</p>
                          <p className="text-xs text-gray-500">
                            {session.country_name || "Unknown"} {session.username ? `- ${session.username}` : ""}
                          </p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="text-xs text-gray-400">
                          {session.protocol.toUpperCase()} :{session.dst_port}
                        </p>
                        <p className="text-xs text-gray-500">
                          {new Date(session.started_at).toLocaleString()}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Export Section */}
            <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
              <h3 className="text-lg font-semibold mb-4">Export Reports</h3>
              <p className="text-sm text-gray-400 mb-4">
                Download forensic reports for your records.
              </p>
              <div className="flex gap-3">
                <a
                  href={`${API_BASE}/api/v1/client/${slug}/stats`}
                  target="_blank"
                  className="px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg text-sm transition-colors"
                >
                  Export JSON
                </a>
              </div>
            </div>
          </div>
        )}

        {/* Sessions Tab */}
        {activeTab === "sessions" && (
          <div className="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-gray-800">
                <tr>
                  <th className="text-left p-3 text-gray-400 font-medium">Source IP</th>
                  <th className="text-left p-3 text-gray-400 font-medium">Protocol</th>
                  <th className="text-left p-3 text-gray-400 font-medium">Username</th>
                  <th className="text-left p-3 text-gray-400 font-medium">Location</th>
                  <th className="text-left p-3 text-gray-400 font-medium">Duration</th>
                  <th className="text-left p-3 text-gray-400 font-medium">Commands</th>
                  <th className="text-left p-3 text-gray-400 font-medium">Time</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800">
                {sessions.map((session) => (
                  <tr key={session.id} className="hover:bg-gray-800/50">
                    <td className="p-3 font-mono">{session.src_ip}</td>
                    <td className="p-3">
                      <span className="px-2 py-0.5 bg-gray-800 rounded text-xs">
                        {session.protocol.toUpperCase()} :{session.dst_port}
                      </span>
                    </td>
                    <td className="p-3 text-gray-400">{session.username || "-"}</td>
                    <td className="p-3 text-gray-400">
                      {session.country_code ? `${session.country_code} ${session.country_name || ""}` : "-"}
                    </td>
                    <td className="p-3 text-gray-400">
                      {session.duration_seconds ? `${Math.round(session.duration_seconds)}s` : "Active"}
                    </td>
                    <td className="p-3 text-gray-400">{session.commands_count}</td>
                    <td className="p-3 text-gray-500 text-xs">
                      {new Date(session.started_at).toLocaleString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Footer */}
        <div className="mt-8 text-center text-xs text-gray-600">
          Powered by HoneyAegis - Auto-refreshing every 30s
        </div>
      </div>
    </div>
  );
}

function StatCard({
  title,
  value,
  subtitle,
  color = "text-gray-100",
}: {
  title: string;
  value: number;
  subtitle: string;
  color?: string;
}) {
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
      <p className="text-sm text-gray-400">{title}</p>
      <p className={`text-3xl font-bold mt-1 ${color}`}>{value}</p>
      <p className="text-xs text-gray-500 mt-1">{subtitle}</p>
    </div>
  );
}
