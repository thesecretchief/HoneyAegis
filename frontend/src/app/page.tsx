"use client";

import { useEffect, useState } from "react";
import dynamic from "next/dynamic";
import {
  getSessionStats,
  getSessions,
  connectWebSocket,
  getToken,
  type SessionStats,
  type Session,
  type WSEvent,
} from "@/lib/api";

const AttackMap = dynamic(() => import("@/components/AttackMap"), {
  ssr: false,
  loading: () => (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 h-[460px] flex items-center justify-center text-gray-500">
      Loading map...
    </div>
  ),
});

export default function DashboardPage() {
  const [stats, setStats] = useState<SessionStats | null>(null);
  const [recentSessions, setRecentSessions] = useState<Session[]>([]);
  const [liveEvents, setLiveEvents] = useState<WSEvent[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!getToken()) {
      window.location.href = "/login";
      return;
    }

    async function fetchData() {
      try {
        const [statsData, sessionsData] = await Promise.all([
          getSessionStats(),
          getSessions({ limit: 10 }),
        ]);
        setStats(statsData);
        setRecentSessions(sessionsData.sessions);
      } catch (err) {
        setError("Failed to load dashboard data");
      }
    }

    fetchData();
    const interval = setInterval(fetchData, 15000);

    // WebSocket for live events
    const ws = connectWebSocket((event: WSEvent) => {
      setLiveEvents((prev) => [event, ...prev].slice(0, 50));
    });

    return () => {
      clearInterval(interval);
      ws.close();
    };
  }, []);

  if (error) {
    return (
      <div className="p-8">
        <p className="text-red-400">{error}</p>
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold">Dashboard</h2>
        <span className="text-xs text-gray-500">
          Auto-refreshing every 15s
        </span>
      </div>

      {/* Stats cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatsCard
          title="Attacks Today"
          value={stats?.sessions_today?.toString() || "0"}
          subtitle={`${stats?.total_sessions || 0} total`}
          color="text-red-400"
        />
        <StatsCard
          title="Unique IPs Today"
          value={stats?.unique_ips_today?.toString() || "0"}
          subtitle={`${stats?.unique_source_ips || 0} total`}
          color="text-blue-400"
        />
        <StatsCard
          title="Auth Successes"
          value={stats?.successful_auths?.toString() || "0"}
          subtitle="Logins accepted by honeypot"
          color="text-yellow-400"
        />
        <StatsCard
          title="Active Sensors"
          value="1"
          subtitle="Cowrie SSH/Telnet"
          color="text-green-400"
        />
      </div>

      {/* Main panels */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Recent Sessions */}
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">Recent Sessions</h3>
            <a
              href="/sessions"
              className="text-xs text-honeyaegis-400 hover:text-honeyaegis-300"
            >
              View all
            </a>
          </div>
          {recentSessions.length === 0 ? (
            <p className="text-gray-500 text-sm">
              No sessions captured yet. Waiting for connections...
            </p>
          ) : (
            <div className="space-y-2">
              {recentSessions.map((session) => (
                <a
                  key={session.id}
                  href={`/sessions/${session.id}`}
                  className="flex items-center justify-between p-3 rounded-lg bg-gray-800/50 hover:bg-gray-800 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <span
                      className={`w-2 h-2 rounded-full ${session.ended_at ? "bg-gray-500" : "bg-green-400 animate-pulse"}`}
                    />
                    <div>
                      <p className="text-sm font-mono">{session.src_ip}</p>
                      <p className="text-xs text-gray-500">
                        {session.country_name || "Unknown"}{" "}
                        {session.username ? `- ${session.username}` : ""}
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-xs text-gray-400">
                      {session.protocol.toUpperCase()} :{session.dst_port}
                    </p>
                    <p className="text-xs text-gray-500">
                      {new Date(session.started_at).toLocaleTimeString()}
                    </p>
                  </div>
                </a>
              ))}
            </div>
          )}
        </div>

        {/* Live Events Feed */}
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">Live Feed</h3>
            <span className="flex items-center gap-1.5 text-xs text-green-400">
              <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
              Connected
            </span>
          </div>
          {liveEvents.length === 0 ? (
            <p className="text-gray-500 text-sm">
              Listening for events via WebSocket...
            </p>
          ) : (
            <div className="space-y-1.5 max-h-80 overflow-y-auto">
              {liveEvents.map((event, i) => (
                <div
                  key={i}
                  className="p-2 rounded bg-gray-800/50 text-xs font-mono"
                >
                  <span className="text-gray-500">
                    {new Date(event.timestamp).toLocaleTimeString()}
                  </span>{" "}
                  <span className="text-honeyaegis-400">{event.type}</span>{" "}
                  <span className="text-gray-300">{event.src_ip}</span>
                  {(event as Record<string, unknown>).command && (
                    <span className="text-red-400">
                      {" "}
                      $ {String((event as Record<string, unknown>).command)}
                    </span>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Attack Map */}
      <div className="mb-6">
        <AttackMap />
      </div>

      {/* Bottom panels */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Top Countries */}
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
          <h3 className="text-lg font-semibold mb-4">Top Countries</h3>
          {stats?.top_countries && stats.top_countries.length > 0 ? (
            <div className="space-y-2">
              {stats.top_countries.slice(0, 8).map((c, i) => (
                <div
                  key={i}
                  className="flex items-center justify-between text-sm"
                >
                  <span className="text-gray-300">
                    {c.country_code} {c.country_name}
                  </span>
                  <span className="text-gray-500 font-mono">{c.count}</span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-sm">No data yet</p>
          )}
        </div>

        {/* Top Ports */}
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
          <h3 className="text-lg font-semibold mb-4">Top Ports</h3>
          {stats?.top_ports && stats.top_ports.length > 0 ? (
            <div className="space-y-2">
              {stats.top_ports.slice(0, 8).map((p, i) => (
                <div
                  key={i}
                  className="flex items-center justify-between text-sm"
                >
                  <span className="text-gray-300 font-mono">
                    :{p.port}
                  </span>
                  <span className="text-gray-500 font-mono">{p.count}</span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-sm">No data yet</p>
          )}
        </div>

        {/* Top Usernames */}
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
          <h3 className="text-lg font-semibold mb-4">Top Usernames</h3>
          {stats?.top_usernames && stats.top_usernames.length > 0 ? (
            <div className="space-y-2">
              {stats.top_usernames.slice(0, 8).map((u, i) => (
                <div
                  key={i}
                  className="flex items-center justify-between text-sm"
                >
                  <span className="text-gray-300 font-mono">
                    {u.username}
                  </span>
                  <span className="text-gray-500 font-mono">{u.count}</span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-sm">No data yet</p>
          )}
        </div>
      </div>
    </div>
  );
}

function StatsCard({
  title,
  value,
  subtitle,
  color = "text-gray-100",
}: {
  title: string;
  value: string;
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
