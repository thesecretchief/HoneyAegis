"use client";

import { useEffect, useState } from "react";
import {
  getAlerts,
  acknowledgeAlert,
  acknowledgeAllAlerts,
  getToken,
  type Alert,
} from "@/lib/api";

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(0);
  const [filter, setFilter] = useState<string>("");
  const [showAcknowledged, setShowAcknowledged] = useState(false);
  const [loading, setLoading] = useState(true);
  const limit = 25;

  useEffect(() => {
    if (!getToken()) {
      window.location.href = "/login";
      return;
    }
    fetchAlerts();
  }, [page, filter, showAcknowledged]);

  async function fetchAlerts() {
    setLoading(true);
    try {
      const data = await getAlerts({
        limit,
        offset: page * limit,
        severity: filter || undefined,
        acknowledged: showAcknowledged ? undefined : false,
      });
      setAlerts(data.alerts);
      setTotal(data.total);
    } catch {
      // handled by API client
    } finally {
      setLoading(false);
    }
  }

  async function handleAcknowledge(alertId: string) {
    try {
      await acknowledgeAlert(alertId);
      setAlerts((prev) =>
        prev.map((a) =>
          a.id === alertId ? { ...a, acknowledged: true } : a,
        ),
      );
    } catch {
      // error handling
    }
  }

  async function handleAcknowledgeAll() {
    try {
      await acknowledgeAllAlerts();
      fetchAlerts();
    } catch {
      // error handling
    }
  }

  function severityBadge(severity: string) {
    const colors: Record<string, string> = {
      critical: "text-red-400 bg-red-400/10",
      high: "text-orange-400 bg-orange-400/10",
      medium: "text-yellow-400 bg-yellow-400/10",
      low: "text-green-400 bg-green-400/10",
      info: "text-blue-400 bg-blue-400/10",
    };
    return colors[severity] || colors.medium;
  }

  const totalPages = Math.ceil(total / limit);
  const unacknowledgedCount = alerts.filter((a) => !a.acknowledged).length;

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold">Alerts</h2>
        <div className="flex items-center gap-3">
          <select
            value={filter}
            onChange={(e) => {
              setFilter(e.target.value);
              setPage(0);
            }}
            className="px-3 py-1.5 bg-gray-800 border border-gray-700 rounded-lg text-sm text-gray-300"
          >
            <option value="">All Severities</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
          <label className="flex items-center gap-2 text-sm text-gray-400">
            <input
              type="checkbox"
              checked={showAcknowledged}
              onChange={(e) => setShowAcknowledged(e.target.checked)}
              className="rounded"
            />
            Show acknowledged
          </label>
          {unacknowledgedCount > 0 && (
            <button
              onClick={handleAcknowledgeAll}
              className="px-3 py-1.5 bg-gray-800 hover:bg-gray-700 rounded-lg text-sm text-gray-300 transition-colors"
            >
              Acknowledge All
            </button>
          )}
        </div>
      </div>

      <div className="space-y-2">
        {loading ? (
          <div className="bg-gray-900 border border-gray-800 rounded-xl p-8 text-center text-gray-500">
            Loading...
          </div>
        ) : alerts.length === 0 ? (
          <div className="bg-gray-900 border border-gray-800 rounded-xl p-8 text-center text-gray-500">
            No alerts found.
            {!showAcknowledged &&
              " Try enabling 'Show acknowledged' to see past alerts."}
          </div>
        ) : (
          alerts.map((alert) => (
            <div
              key={alert.id}
              className={`bg-gray-900 border rounded-xl p-4 flex items-start justify-between gap-4 ${
                alert.acknowledged
                  ? "border-gray-800 opacity-60"
                  : "border-gray-700"
              }`}
            >
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <span
                    className={`px-2 py-0.5 rounded text-xs font-semibold ${severityBadge(alert.severity)}`}
                  >
                    {alert.severity.toUpperCase()}
                  </span>
                  <span className="text-xs text-gray-500">
                    {alert.alert_type}
                  </span>
                  <span className="text-xs text-gray-600">
                    {new Date(alert.created_at).toLocaleString()}
                  </span>
                </div>
                <p className="text-sm text-gray-200 font-medium">
                  {alert.title}
                </p>
                {alert.description && (
                  <p className="text-xs text-gray-400 mt-1 whitespace-pre-wrap">
                    {alert.description}
                  </p>
                )}
                {alert.session_id && (
                  <a
                    href={`/sessions/${alert.session_id}`}
                    className="text-xs text-honeyaegis-400 hover:text-honeyaegis-300 mt-1 inline-block"
                  >
                    View Session
                  </a>
                )}
              </div>
              {!alert.acknowledged && (
                <button
                  onClick={() => handleAcknowledge(alert.id)}
                  className="px-3 py-1 bg-gray-800 hover:bg-gray-700 rounded text-xs text-gray-400 transition-colors whitespace-nowrap"
                >
                  Acknowledge
                </button>
              )}
            </div>
          ))
        )}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between mt-4">
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
  );
}
