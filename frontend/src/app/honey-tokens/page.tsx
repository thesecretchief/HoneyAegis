"use client";

import { useEffect, useState } from "react";
import {
  getHoneyTokens,
  createHoneyToken,
  deleteHoneyToken,
  getToken,
  type HoneyTokenData,
} from "@/lib/api";

export default function HoneyTokensPage() {
  const [tokens, setTokens] = useState<HoneyTokenData[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [formName, setFormName] = useState("");
  const [formUsername, setFormUsername] = useState("");
  const [formPassword, setFormPassword] = useState("");
  const [formType, setFormType] = useState("credential");

  useEffect(() => {
    if (!getToken()) {
      window.location.href = "/login";
      return;
    }
    fetchTokens();
  }, []);

  async function fetchTokens() {
    try {
      const data = await getHoneyTokens();
      setTokens(data.tokens);
    } catch {
      // handled
    } finally {
      setLoading(false);
    }
  }

  async function handleCreate() {
    if (!formName) return;
    try {
      await createHoneyToken({
        name: formName,
        token_type: formType,
        username: formUsername || undefined,
        password: formPassword || undefined,
        alert_severity: "critical",
      });
      setFormName("");
      setFormUsername("");
      setFormPassword("");
      setShowCreate(false);
      await fetchTokens();
    } catch {
      // handled
    }
  }

  async function handleDelete(tokenId: string) {
    try {
      await deleteHoneyToken(tokenId);
      await fetchTokens();
    } catch {
      // handled
    }
  }

  if (loading) {
    return <div className="p-8 text-gray-500">Loading honey tokens...</div>;
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold">Honey Tokens</h2>
          <p className="text-sm text-gray-500 mt-1">
            Deploy decoy credentials that trigger critical alerts when used
          </p>
        </div>
        <button
          onClick={() => setShowCreate(!showCreate)}
          className="px-4 py-2 bg-honeyaegis-500 hover:bg-honeyaegis-400 text-black rounded-lg text-sm font-semibold transition-colors"
        >
          {showCreate ? "Cancel" : "Create Token"}
        </button>
      </div>

      {/* Create Form */}
      {showCreate && (
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 mb-6">
          <h3 className="text-sm font-semibold text-gray-300 mb-4">New Honey Token</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs text-gray-500 mb-1">Name</label>
              <input
                value={formName}
                onChange={(e) => setFormName(e.target.value)}
                className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm"
                placeholder="e.g., Fake Admin Creds"
              />
            </div>
            <div>
              <label className="block text-xs text-gray-500 mb-1">Type</label>
              <select
                value={formType}
                onChange={(e) => setFormType(e.target.value)}
                className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm"
              >
                <option value="credential">Credential</option>
                <option value="file">File</option>
                <option value="api_key">API Key</option>
              </select>
            </div>
            {formType === "credential" && (
              <>
                <div>
                  <label className="block text-xs text-gray-500 mb-1">Username</label>
                  <input
                    value={formUsername}
                    onChange={(e) => setFormUsername(e.target.value)}
                    className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm"
                    placeholder="e.g., admin"
                  />
                </div>
                <div>
                  <label className="block text-xs text-gray-500 mb-1">Password</label>
                  <input
                    value={formPassword}
                    onChange={(e) => setFormPassword(e.target.value)}
                    className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm"
                    placeholder="e.g., P@ssw0rd123"
                  />
                </div>
              </>
            )}
          </div>
          <button
            onClick={handleCreate}
            className="mt-4 px-4 py-2 bg-red-600 hover:bg-red-500 rounded-lg text-sm font-semibold text-white transition-colors"
          >
            Deploy Token
          </button>
        </div>
      )}

      {/* Token List */}
      {tokens.length === 0 ? (
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-8 text-center">
          <p className="text-gray-500">No honey tokens deployed yet.</p>
          <p className="text-gray-600 text-sm mt-1">
            Create decoy credentials to detect lateral movement and targeted attacks.
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {tokens.map((token) => (
            <div
              key={token.id}
              className="bg-gray-900 border border-gray-800 rounded-xl p-5 flex items-center justify-between"
            >
              <div className="flex items-center gap-4">
                <div className={`w-3 h-3 rounded-full ${token.is_active ? "bg-green-400" : "bg-gray-600"}`} />
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-semibold">{token.name}</span>
                    <span className="px-2 py-0.5 bg-gray-800 rounded text-xs text-gray-400">
                      {token.token_type}
                    </span>
                    {token.trigger_count > 0 && (
                      <span className="px-2 py-0.5 bg-red-900/60 text-red-400 rounded-full text-xs font-bold">
                        {token.trigger_count} trigger{token.trigger_count !== 1 ? "s" : ""}
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-gray-500 mt-1">
                    {token.username && <span className="font-mono">{token.username}</span>}
                    {token.username && token.password && <span> / </span>}
                    {token.password && <span className="font-mono">{token.password}</span>}
                    {token.filename && <span className="font-mono">{token.filename}</span>}
                    {!token.username && !token.filename && "No credentials set"}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <span className={`text-xs ${
                  token.alert_severity === "critical" ? "text-red-400" :
                  token.alert_severity === "high" ? "text-orange-400" : "text-yellow-400"
                }`}>
                  {token.alert_severity}
                </span>
                <button
                  onClick={() => handleDelete(token.id)}
                  className="px-3 py-1 text-xs text-red-400 hover:bg-red-900/30 rounded transition-colors"
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
