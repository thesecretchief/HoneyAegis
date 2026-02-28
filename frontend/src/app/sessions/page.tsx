"use client";

import { useEffect, useState } from "react";
import { getSessions, getToken, type Session } from "@/lib/api";

export default function SessionsPage() {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(0);
  const [protocol, setProtocol] = useState<string>("");
  const [loading, setLoading] = useState(true);
  const limit = 25;

  useEffect(() => {
    if (!getToken()) {
      window.location.href = "/login";
      return;
    }
    fetchSessions();
  }, [page, protocol]);

  async function fetchSessions() {
    setLoading(true);
    try {
      const data = await getSessions({
        limit,
        offset: page * limit,
        protocol: protocol || undefined,
      });
      setSessions(data.sessions);
      setTotal(data.total);
    } catch {
      // handled by API client
    } finally {
      setLoading(false);
    }
  }

  function formatDuration(seconds: number | null): string {
    if (!seconds) return "-";
    if (seconds < 60) return `${Math.round(seconds)}s`;
    if (seconds < 3600) return `${Math.round(seconds / 60)}m`;
    return `${Math.round(seconds / 3600)}h`;
  }

  function riskScore(session: Session): { label: string; color: string } {
    let score = 0;
    if (session.auth_success) score += 3;
    if (session.commands_count > 0) score += 2;
    if (session.commands_count > 5) score += 2;
    if (session.duration_seconds && session.duration_seconds > 60) score += 1;
    if (session.duration_seconds && session.duration_seconds > 300) score += 2;

    if (score >= 7) return { label: "Critical", color: "text-red-400 bg-red-400/10" };
    if (score >= 5) return { label: "High", color: "text-orange-400 bg-orange-400/10" };
    if (score >= 3) return { label: "Medium", color: "text-yellow-400 bg-yellow-400/10" };
    return { label: "Low", color: "text-green-400 bg-green-400/10" };
  }

  const totalPages = Math.ceil(total / limit);

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold">Sessions</h2>
        <div className="flex items-center gap-3">
          <select
            value={protocol}
            onChange={(e) => {
              setProtocol(e.target.value);
              setPage(0);
            }}
            className="px-3 py-1.5 bg-gray-800 border border-gray-700 rounded-lg text-sm text-gray-300"
          >
            <option value="">All Protocols</option>
            <option value="ssh">SSH</option>
            <option value="telnet">Telnet</option>
          </select>
          <span className="text-sm text-gray-500">
            {total} total
          </span>
        </div>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-800 text-gray-400 text-left">
              <th className="p-3">Status</th>
              <th className="p-3">Source IP</th>
              <th className="p-3">Location</th>
              <th className="p-3">Protocol</th>
              <th className="p-3">Username</th>
              <th className="p-3">Commands</th>
              <th className="p-3">Duration</th>
              <th className="p-3">Risk</th>
              <th className="p-3">Time</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={9} className="p-8 text-center text-gray-500">
                  Loading...
                </td>
              </tr>
            ) : sessions.length === 0 ? (
              <tr>
                <td colSpan={9} className="p-8 text-center text-gray-500">
                  No sessions found
                </td>
              </tr>
            ) : (
              sessions.map((session) => {
                const risk = riskScore(session);
                return (
                  <tr
                    key={session.id}
                    className="border-b border-gray-800/50 hover:bg-gray-800/50 cursor-pointer transition-colors"
                    onClick={() =>
                      (window.location.href = `/sessions/${session.id}`)
                    }
                  >
                    <td className="p-3">
                      <span
                        className={`w-2.5 h-2.5 rounded-full inline-block ${session.ended_at ? "bg-gray-500" : "bg-green-400 animate-pulse"}`}
                      />
                    </td>
                    <td className="p-3 font-mono text-gray-200">
                      {session.src_ip}
                    </td>
                    <td className="p-3 text-gray-400">
                      {session.country_code && session.country_code !== "XX"
                        ? `${session.country_code} ${session.city || session.country_name || ""}`
                        : "-"}
                    </td>
                    <td className="p-3">
                      <span className="px-2 py-0.5 rounded bg-gray-800 text-xs font-mono">
                        {session.protocol.toUpperCase()}:{session.dst_port}
                      </span>
                    </td>
                    <td className="p-3 font-mono text-gray-300">
                      {session.username || "-"}
                    </td>
                    <td className="p-3 text-gray-400">
                      {session.commands_count || 0}
                    </td>
                    <td className="p-3 text-gray-400">
                      {formatDuration(session.duration_seconds)}
                    </td>
                    <td className="p-3">
                      <span
                        className={`px-2 py-0.5 rounded text-xs font-semibold ${risk.color}`}
                      >
                        {risk.label}
                      </span>
                    </td>
                    <td className="p-3 text-gray-500 text-xs">
                      {new Date(session.started_at).toLocaleString()}
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex items-center justify-between p-3 border-t border-gray-800">
            <button
              onClick={() => setPage(Math.max(0, page - 1))}
              disabled={page === 0}
              className="px-3 py-1 text-sm text-gray-400 hover:text-gray-200 disabled:opacity-30"
            >
              Previous
            </button>
            <span className="text-sm text-gray-500">
              Page {page + 1} of {totalPages}
            </span>
            <button
              onClick={() => setPage(Math.min(totalPages - 1, page + 1))}
              disabled={page >= totalPages - 1}
              className="px-3 py-1 text-sm text-gray-400 hover:text-gray-200 disabled:opacity-30"
            >
              Next
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
