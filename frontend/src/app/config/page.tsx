"use client";

import { useEffect, useState } from "react";
import {
  getPlatformConfig,
  updateAlertRules,
  getAIStatus,
  getToken,
  type PlatformConfig,
  type AIStatus,
} from "@/lib/api";

export default function ConfigPage() {
  const [config, setConfig] = useState<PlatformConfig | null>(null);
  const [aiStatus, setAiStatus] = useState<AIStatus | null>(null);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [loading, setLoading] = useState(true);

  // Local alert form state
  const [alertNewSession, setAlertNewSession] = useState(true);
  const [alertMalware, setAlertMalware] = useState(true);
  const [cooldown, setCooldown] = useState(5);

  useEffect(() => {
    if (!getToken()) {
      window.location.href = "/login";
      return;
    }

    async function fetchData() {
      try {
        const [configData, statusData] = await Promise.all([
          getPlatformConfig(),
          getAIStatus().catch(() => null),
        ]);
        setConfig(configData);
        setAiStatus(statusData);
        setAlertNewSession(configData.alert_rules.alert_on_new_session);
        setAlertMalware(configData.alert_rules.alert_on_malware_capture);
        setCooldown(configData.alert_rules.cooldown_minutes);
      } catch {
        // handled by API client
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, []);

  async function saveAlertRules() {
    setSaving(true);
    try {
      await updateAlertRules({
        alert_on_new_session: alertNewSession,
        alert_on_malware_capture: alertMalware,
        cooldown_minutes: cooldown,
      });
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } catch {
      // error handled by client
    } finally {
      setSaving(false);
    }
  }

  if (loading) {
    return (
      <div className="p-8">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-800 rounded w-48" />
          <div className="h-64 bg-gray-800 rounded" />
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold">Configuration</h2>
      </div>

      {/* Honeypots Section */}
      <section className="mb-8">
        <h3 className="text-lg font-semibold mb-4">Honeypot Services</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {config?.honeypots.map((hp) => (
            <div
              key={hp.name}
              className="bg-gray-900 border border-gray-800 rounded-xl p-5"
            >
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-semibold">{hp.name}</h4>
                <span
                  className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                    hp.enabled
                      ? "bg-green-900/50 text-green-400"
                      : "bg-gray-800 text-gray-500"
                  }`}
                >
                  {hp.enabled ? "Active" : "Disabled"}
                </span>
              </div>
              <p className="text-sm text-gray-500 mb-3">{hp.description}</p>
              <div className="flex items-center gap-2">
                <span className="text-xs text-gray-500">Ports:</span>
                {hp.ports.map((port) => (
                  <span
                    key={port}
                    className="px-2 py-0.5 bg-gray-800 rounded text-xs font-mono text-gray-400"
                  >
                    {port}
                  </span>
                ))}
              </div>
              {!hp.enabled && (
                <p className="text-xs text-gray-600 mt-3">
                  Enable in docker-compose.yml with --profile full
                </p>
              )}
            </div>
          ))}
        </div>
      </section>

      {/* Alert Rules */}
      <section className="mb-8">
        <h3 className="text-lg font-semibold mb-4">Alert Rules</h3>
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 space-y-5">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium">Alert on new session</p>
              <p className="text-xs text-gray-500">
                Send notification when a new attacker connects
              </p>
            </div>
            <button
              onClick={() => setAlertNewSession(!alertNewSession)}
              className={`w-12 h-6 rounded-full transition-colors relative ${
                alertNewSession ? "bg-green-600" : "bg-gray-700"
              }`}
            >
              <span
                className={`absolute top-0.5 w-5 h-5 rounded-full bg-white transition-transform ${
                  alertNewSession ? "translate-x-6" : "translate-x-0.5"
                }`}
              />
            </button>
          </div>

          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium">Alert on malware capture</p>
              <p className="text-xs text-gray-500">
                Send notification when malware/files are downloaded
              </p>
            </div>
            <button
              onClick={() => setAlertMalware(!alertMalware)}
              className={`w-12 h-6 rounded-full transition-colors relative ${
                alertMalware ? "bg-green-600" : "bg-gray-700"
              }`}
            >
              <span
                className={`absolute top-0.5 w-5 h-5 rounded-full bg-white transition-transform ${
                  alertMalware ? "translate-x-6" : "translate-x-0.5"
                }`}
              />
            </button>
          </div>

          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium">Cooldown (minutes)</p>
              <p className="text-xs text-gray-500">
                Minimum time between duplicate alerts
              </p>
            </div>
            <input
              type="number"
              value={cooldown}
              onChange={(e) => setCooldown(parseInt(e.target.value) || 1)}
              min={1}
              max={1440}
              className="w-20 px-3 py-1.5 bg-gray-800 border border-gray-700 rounded-lg text-sm text-gray-200 focus:outline-none focus:ring-1 focus:ring-honeyaegis-400"
            />
          </div>

          {config?.alert_rules.apprise_urls &&
            config.alert_rules.apprise_urls.length > 0 && (
              <div>
                <p className="text-sm font-medium mb-2">
                  Notification Channels
                </p>
                <div className="space-y-1">
                  {config.alert_rules.apprise_urls.map((url, i) => (
                    <div
                      key={i}
                      className="px-3 py-1.5 bg-gray-800 rounded text-xs font-mono text-gray-400"
                    >
                      {url.replace(/:\/\/.*@/, "://***@")}
                    </div>
                  ))}
                </div>
              </div>
            )}

          <div className="flex items-center gap-3 pt-2">
            <button
              onClick={saveAlertRules}
              disabled={saving}
              className="px-4 py-2 bg-honeyaegis-600 hover:bg-honeyaegis-500 rounded-lg text-sm font-semibold text-white disabled:opacity-50 transition-colors"
            >
              {saving ? "Saving..." : "Save Alert Rules"}
            </button>
            {saved && (
              <span className="text-sm text-green-400">Saved!</span>
            )}
          </div>
        </div>
      </section>

      {/* AI Settings */}
      <section className="mb-8">
        <h3 className="text-lg font-semibold mb-4">AI Analysis</h3>
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <p className="text-sm font-medium">Local AI (Ollama)</p>
              <p className="text-xs text-gray-500">
                AI-powered threat summaries with MITRE ATT&CK mapping
              </p>
            </div>
            <span
              className={`px-3 py-1 rounded-full text-xs font-medium ${
                aiStatus?.available
                  ? "bg-green-900/50 text-green-400"
                  : config?.ai_enabled
                    ? "bg-yellow-900/50 text-yellow-400"
                    : "bg-gray-800 text-gray-500"
              }`}
            >
              {aiStatus?.available
                ? "Connected"
                : config?.ai_enabled
                  ? "Enabled (not connected)"
                  : "Disabled"}
            </span>
          </div>

          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-gray-500">Model:</span>{" "}
              <span className="text-gray-300 font-mono">
                {config?.ai_model || "phi3:mini"}
              </span>
            </div>
            <div>
              <span className="text-gray-500">Status:</span>{" "}
              <span className="text-gray-300">
                {aiStatus?.available ? "Ready" : "Unavailable"}
              </span>
            </div>
          </div>

          {!config?.ai_enabled && (
            <div className="mt-4 p-3 border border-dashed border-gray-700 rounded-lg">
              <p className="text-xs text-gray-500">
                Enable AI with:{" "}
                <code className="text-gray-400">
                  OLLAMA_ENABLED=true docker compose --profile full up -d
                </code>
              </p>
            </div>
          )}
        </div>
      </section>

      {/* Fleet Mode */}
      <section>
        <h3 className="text-lg font-semibold mb-4">Fleet Mode</h3>
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium">Deployment Mode</p>
              <p className="text-xs text-gray-500">
                Standalone sensor or hub-and-spoke fleet
              </p>
            </div>
            <span className="px-3 py-1 bg-gray-800 rounded-full text-xs font-medium text-gray-400">
              {config?.fleet_mode || "standalone"}
            </span>
          </div>
          <p className="text-xs text-gray-600 mt-3">
            Configure fleet mode via FLEET_MODE env var (standalone | hub |
            sensor)
          </p>
        </div>
      </section>
    </div>
  );
}
