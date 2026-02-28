"use client";

import { useEffect, useState } from "react";
import { getToken } from "@/lib/api";

interface Plugin {
  id: string;
  name: string;
  description: string;
  version: string;
  author: string;
  category: string;
  downloads: number;
  rating: number;
  installed: boolean;
  tags: string[];
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function fetchPlugins(
  category?: string,
  search?: string,
): Promise<Plugin[]> {
  const params = new URLSearchParams();
  if (category && category !== "all") params.set("category", category);
  if (search) params.set("search", search);

  const token = getToken();
  const res = await fetch(
    `${API_BASE}/api/v1/marketplace/plugins?${params.toString()}`,
    {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    },
  );
  if (!res.ok) return [];
  const data = await res.json();
  return data.plugins || [];
}

async function installPlugin(pluginId: string): Promise<boolean> {
  const token = getToken();
  if (!token) return false;
  const res = await fetch(
    `${API_BASE}/api/v1/marketplace/plugins/${pluginId}/install`,
    {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
    },
  );
  return res.ok;
}

const CATEGORIES = [
  { value: "all", label: "All Plugins" },
  { value: "enrichment", label: "Enrichment" },
  { value: "response", label: "Response" },
  { value: "notification", label: "Notification" },
  { value: "emulator", label: "Emulator" },
];

export default function MarketplacePage() {
  const [plugins, setPlugins] = useState<Plugin[]>([]);
  const [loading, setLoading] = useState(true);
  const [category, setCategory] = useState("all");
  const [search, setSearch] = useState("");
  const [installing, setInstalling] = useState<string | null>(null);

  useEffect(() => {
    if (!getToken()) {
      window.location.href = "/login";
      return;
    }
    loadPlugins();
  }, [category]);

  async function loadPlugins() {
    setLoading(true);
    try {
      const data = await fetchPlugins(category, search);
      setPlugins(data);
    } finally {
      setLoading(false);
    }
  }

  async function handleSearch(e: React.FormEvent) {
    e.preventDefault();
    await loadPlugins();
  }

  async function handleInstall(pluginId: string) {
    setInstalling(pluginId);
    try {
      const ok = await installPlugin(pluginId);
      if (ok) {
        setPlugins((prev) =>
          prev.map((p) => (p.id === pluginId ? { ...p, installed: true } : p)),
        );
      }
    } finally {
      setInstalling(null);
    }
  }

  function getCategoryColor(cat: string): string {
    switch (cat) {
      case "enrichment":
        return "bg-blue-900/30 text-blue-400";
      case "response":
        return "bg-red-900/30 text-red-400";
      case "notification":
        return "bg-purple-900/30 text-purple-400";
      case "emulator":
        return "bg-green-900/30 text-green-400";
      default:
        return "bg-gray-900/30 text-gray-400";
    }
  }

  if (loading) {
    return (
      <div className="p-8">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-800 rounded w-64" />
          <div className="h-12 bg-gray-800 rounded" />
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <div key={i} className="h-48 bg-gray-800 rounded-xl" />
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold">Plugin Marketplace</h2>
          <p className="text-sm text-gray-500 mt-1">
            Extend HoneyAegis with community plugins
          </p>
        </div>
        <span className="text-xs text-gray-500">
          {plugins.length} plugin{plugins.length !== 1 ? "s" : ""} available
        </span>
      </div>

      {/* Search and filters */}
      <div className="flex flex-col md:flex-row gap-4 mb-6">
        <form onSubmit={handleSearch} className="flex-1">
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search plugins..."
            className="w-full px-4 py-2 bg-gray-900 border border-gray-800 rounded-lg text-sm text-gray-200 focus:outline-none focus:ring-1 focus:ring-honeyaegis-400"
          />
        </form>
        <div className="flex gap-2">
          {CATEGORIES.map((cat) => (
            <button
              key={cat.value}
              onClick={() => setCategory(cat.value)}
              className={`px-3 py-2 rounded-lg text-xs font-medium transition-colors ${
                category === cat.value
                  ? "bg-honeyaegis-600 text-white"
                  : "bg-gray-900 text-gray-400 hover:bg-gray-800"
              }`}
            >
              {cat.label}
            </button>
          ))}
        </div>
      </div>

      {/* Plugin grid */}
      {plugins.length === 0 ? (
        <div className="text-center py-16 bg-gray-900 border border-gray-800 rounded-xl">
          <p className="text-gray-500 text-sm">No plugins found.</p>
          <p className="text-gray-600 text-xs mt-1">
            Try a different search or category.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {plugins.map((plugin) => (
            <div
              key={plugin.id}
              className="bg-gray-900 border border-gray-800 rounded-xl p-5 hover:border-gray-700 transition-colors"
            >
              <div className="flex items-start justify-between mb-3">
                <div>
                  <h3 className="text-sm font-semibold text-gray-100">
                    {plugin.name}
                  </h3>
                  <p className="text-xs text-gray-500">
                    by {plugin.author} &middot; v{plugin.version}
                  </p>
                </div>
                <span
                  className={`px-2 py-0.5 rounded text-xs ${getCategoryColor(plugin.category)}`}
                >
                  {plugin.category}
                </span>
              </div>

              <p className="text-xs text-gray-400 mb-4 line-clamp-2">
                {plugin.description}
              </p>

              <div className="flex flex-wrap gap-1 mb-4">
                {plugin.tags.map((tag) => (
                  <span
                    key={tag}
                    className="px-2 py-0.5 bg-gray-800 rounded text-xs text-gray-500"
                  >
                    {tag}
                  </span>
                ))}
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3 text-xs text-gray-500">
                  <span>{plugin.downloads.toLocaleString()} installs</span>
                  <span>{"*".repeat(Math.round(plugin.rating))}</span>
                </div>
                {plugin.installed ? (
                  <span className="px-3 py-1.5 bg-green-900/30 text-green-400 rounded-lg text-xs font-medium">
                    Installed
                  </span>
                ) : (
                  <button
                    onClick={() => handleInstall(plugin.id)}
                    disabled={installing === plugin.id}
                    className="px-3 py-1.5 bg-honeyaegis-600 hover:bg-honeyaegis-500 rounded-lg text-xs font-semibold text-white disabled:opacity-50 transition-colors"
                  >
                    {installing === plugin.id ? "Installing..." : "Install"}
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
