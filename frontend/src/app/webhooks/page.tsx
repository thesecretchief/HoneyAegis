"use client";

import { useEffect, useState } from "react";
import {
  getWebhooks,
  createWebhook,
  deleteWebhook,
  testWebhook,
  getToken,
  type WebhookData,
} from "@/lib/api";

export default function WebhooksPage() {
  const [webhooks, setWebhooks] = useState<WebhookData[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [formName, setFormName] = useState("");
  const [formUrl, setFormUrl] = useState("");
  const [formTrigger, setFormTrigger] = useState("alert");
  const [formSeverity, setFormSeverity] = useState("");
  const [testing, setTesting] = useState<string | null>(null);

  useEffect(() => {
    if (!getToken()) {
      window.location.href = "/login";
      return;
    }
    fetchWebhooks();
  }, []);

  async function fetchWebhooks() {
    try {
      const data = await getWebhooks();
      setWebhooks(data.webhooks);
    } catch {
      // handled
    } finally {
      setLoading(false);
    }
  }

  async function handleCreate() {
    if (!formName || !formUrl) return;
    try {
      await createWebhook({
        name: formName,
        url: formUrl,
        trigger_on: formTrigger,
        severity_filter: formSeverity || undefined,
      });
      setFormName("");
      setFormUrl("");
      setFormTrigger("alert");
      setFormSeverity("");
      setShowCreate(false);
      await fetchWebhooks();
    } catch {
      // handled
    }
  }

  async function handleTest(webhookId: string) {
    setTesting(webhookId);
    try {
      await testWebhook(webhookId);
    } catch {
      // handled
    } finally {
      setTesting(null);
      await fetchWebhooks();
    }
  }

  async function handleDelete(webhookId: string) {
    try {
      await deleteWebhook(webhookId);
      await fetchWebhooks();
    } catch {
      // handled
    }
  }

  if (loading) {
    return <div className="p-8 text-gray-500">Loading webhooks...</div>;
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold">Auto-Response Hooks</h2>
          <p className="text-sm text-gray-500 mt-1">
            Trigger webhooks on alerts, honey tokens, and sessions
          </p>
        </div>
        <button
          onClick={() => setShowCreate(!showCreate)}
          className="px-4 py-2 bg-honeyaegis-500 hover:bg-honeyaegis-400 text-black rounded-lg text-sm font-semibold transition-colors"
        >
          {showCreate ? "Cancel" : "Add Webhook"}
        </button>
      </div>

      {/* Create Form */}
      {showCreate && (
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 mb-6">
          <h3 className="text-sm font-semibold text-gray-300 mb-4">New Webhook</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs text-gray-500 mb-1">Name</label>
              <input
                value={formName}
                onChange={(e) => setFormName(e.target.value)}
                className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm"
                placeholder="e.g., Slack Alert"
              />
            </div>
            <div>
              <label className="block text-xs text-gray-500 mb-1">URL</label>
              <input
                value={formUrl}
                onChange={(e) => setFormUrl(e.target.value)}
                className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm"
                placeholder="https://hooks.slack.com/..."
              />
            </div>
            <div>
              <label className="block text-xs text-gray-500 mb-1">Trigger On</label>
              <select
                value={formTrigger}
                onChange={(e) => setFormTrigger(e.target.value)}
                className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm"
              >
                <option value="alert">Alert</option>
                <option value="honey_token">Honey Token</option>
                <option value="session">Session Connect</option>
                <option value="malware">Malware Capture</option>
              </select>
            </div>
            <div>
              <label className="block text-xs text-gray-500 mb-1">Severity Filter (optional)</label>
              <select
                value={formSeverity}
                onChange={(e) => setFormSeverity(e.target.value)}
                className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm"
              >
                <option value="">All severities</option>
                <option value="critical">Critical only</option>
                <option value="high">High+</option>
                <option value="medium">Medium+</option>
              </select>
            </div>
          </div>
          <button
            onClick={handleCreate}
            className="mt-4 px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded-lg text-sm font-semibold text-white transition-colors"
          >
            Create Webhook
          </button>
        </div>
      )}

      {/* Webhook List */}
      {webhooks.length === 0 ? (
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-8 text-center">
          <p className="text-gray-500">No webhooks configured.</p>
          <p className="text-gray-600 text-sm mt-1">
            Add webhooks to automatically respond to security events.
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {webhooks.map((hook) => (
            <div
              key={hook.id}
              className="bg-gray-900 border border-gray-800 rounded-xl p-5"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className={`w-3 h-3 rounded-full ${hook.is_active ? "bg-green-400" : "bg-gray-600"}`} />
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-semibold">{hook.name}</span>
                      <span className="px-2 py-0.5 bg-gray-800 rounded text-xs text-gray-400">
                        {hook.trigger_on}
                      </span>
                      {hook.severity_filter && (
                        <span className="px-2 py-0.5 bg-gray-800 rounded text-xs text-orange-400">
                          {hook.severity_filter}+
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-gray-500 font-mono mt-1 truncate max-w-md">
                      {hook.http_method} {hook.url}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-gray-500">
                    {hook.execution_count} call{hook.execution_count !== 1 ? "s" : ""}
                    {hook.last_status_code && (
                      <span className={hook.last_status_code < 300 ? " text-green-400" : " text-red-400"}>
                        {" "}({hook.last_status_code})
                      </span>
                    )}
                  </span>
                  <button
                    onClick={() => handleTest(hook.id)}
                    disabled={testing === hook.id}
                    className="px-3 py-1 text-xs bg-gray-800 hover:bg-gray-700 rounded transition-colors disabled:opacity-50"
                  >
                    {testing === hook.id ? "Testing..." : "Test"}
                  </button>
                  <button
                    onClick={() => handleDelete(hook.id)}
                    className="px-3 py-1 text-xs text-red-400 hover:bg-red-900/30 rounded transition-colors"
                  >
                    Delete
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
