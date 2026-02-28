"use client";

import { useEffect, useState } from "react";
import {
  getSensors,
  registerSensor,
  deleteSensor,
  getToken,
  type Sensor,
} from "@/lib/api";

export default function SensorsPage() {
  const [sensors, setSensors] = useState<Sensor[]>([]);
  const [loading, setLoading] = useState(true);
  const [showRegister, setShowRegister] = useState(false);
  const [formId, setFormId] = useState("");
  const [formName, setFormName] = useState("");
  const [formHostname, setFormHostname] = useState("");
  const [formIp, setFormIp] = useState("");
  const [registering, setRegistering] = useState(false);

  useEffect(() => {
    if (!getToken()) {
      window.location.href = "/login";
      return;
    }
    fetchSensors();
  }, []);

  async function fetchSensors() {
    try {
      const data = await getSensors();
      setSensors(data.sensors);
    } catch {
      // handled by api client
    } finally {
      setLoading(false);
    }
  }

  async function handleRegister() {
    if (!formId || !formName) return;
    setRegistering(true);
    try {
      await registerSensor({
        sensor_id: formId,
        name: formName,
        hostname: formHostname || undefined,
        ip_address: formIp || undefined,
      });
      setShowRegister(false);
      setFormId("");
      setFormName("");
      setFormHostname("");
      setFormIp("");
      await fetchSensors();
    } catch {
      // error handled
    } finally {
      setRegistering(false);
    }
  }

  async function handleDelete(sensorId: string) {
    try {
      await deleteSensor(sensorId);
      await fetchSensors();
    } catch {
      // error handled
    }
  }

  function getStatusColor(status: string, lastSeen: string | null): string {
    if (status !== "active") return "bg-gray-500";
    if (!lastSeen) return "bg-yellow-400";
    const diff = Date.now() - new Date(lastSeen).getTime();
    if (diff < 120_000) return "bg-green-400 animate-pulse";
    if (diff < 600_000) return "bg-yellow-400";
    return "bg-red-400";
  }

  function getStatusLabel(status: string, lastSeen: string | null): string {
    if (status !== "active") return "Inactive";
    if (!lastSeen) return "Registered";
    const diff = Date.now() - new Date(lastSeen).getTime();
    if (diff < 120_000) return "Online";
    if (diff < 600_000) return "Stale";
    return "Offline";
  }

  if (loading) {
    return (
      <div className="p-8">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-800 rounded w-48" />
          <div className="h-32 bg-gray-800 rounded" />
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold">Fleet Management</h2>
        <div className="flex items-center gap-3">
          <span className="text-xs text-gray-500">
            {sensors.length} sensor{sensors.length !== 1 ? "s" : ""} registered
          </span>
          <button
            onClick={() => setShowRegister(!showRegister)}
            className="px-4 py-2 bg-honeyaegis-600 hover:bg-honeyaegis-500 rounded-lg text-sm font-semibold text-white transition-colors"
          >
            {showRegister ? "Cancel" : "Register Sensor"}
          </button>
        </div>
      </div>

      {/* Register form */}
      {showRegister && (
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 mb-6">
          <h3 className="text-lg font-semibold mb-4">Register New Sensor</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div>
              <label className="block text-xs text-gray-500 mb-1">
                Sensor ID *
              </label>
              <input
                type="text"
                value={formId}
                onChange={(e) => setFormId(e.target.value)}
                placeholder="sensor-02"
                className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm text-gray-200 focus:outline-none focus:ring-1 focus:ring-honeyaegis-400"
              />
            </div>
            <div>
              <label className="block text-xs text-gray-500 mb-1">
                Name *
              </label>
              <input
                type="text"
                value={formName}
                onChange={(e) => setFormName(e.target.value)}
                placeholder="Office RPi Sensor"
                className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm text-gray-200 focus:outline-none focus:ring-1 focus:ring-honeyaegis-400"
              />
            </div>
            <div>
              <label className="block text-xs text-gray-500 mb-1">
                Hostname
              </label>
              <input
                type="text"
                value={formHostname}
                onChange={(e) => setFormHostname(e.target.value)}
                placeholder="rpi-office-01"
                className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm text-gray-200 focus:outline-none focus:ring-1 focus:ring-honeyaegis-400"
              />
            </div>
            <div>
              <label className="block text-xs text-gray-500 mb-1">
                IP Address
              </label>
              <input
                type="text"
                value={formIp}
                onChange={(e) => setFormIp(e.target.value)}
                placeholder="192.168.1.50"
                className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm text-gray-200 focus:outline-none focus:ring-1 focus:ring-honeyaegis-400"
              />
            </div>
          </div>
          <button
            onClick={handleRegister}
            disabled={!formId || !formName || registering}
            className="px-4 py-2 bg-green-600 hover:bg-green-500 rounded-lg text-sm font-semibold text-white disabled:opacity-50 transition-colors"
          >
            {registering ? "Registering..." : "Register"}
          </button>
        </div>
      )}

      {/* Sensors list */}
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        {sensors.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-gray-500 text-sm">
              No sensors registered yet.
            </p>
            <p className="text-gray-600 text-xs mt-1">
              Register your first sensor to start fleet management.
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {sensors.map((sensor) => (
              <div
                key={sensor.id}
                className="flex items-center justify-between p-4 rounded-lg bg-gray-800/50 hover:bg-gray-800/80 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <span
                    className={`w-3 h-3 rounded-full ${getStatusColor(
                      sensor.status,
                      sensor.last_seen,
                    )}`}
                  />
                  <div>
                    <p className="text-sm font-semibold">{sensor.name}</p>
                    <p className="text-xs text-gray-500">
                      {sensor.sensor_id}
                      {sensor.hostname ? ` | ${sensor.hostname}` : ""}
                      {sensor.ip_address ? ` | ${sensor.ip_address}` : ""}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <div className="text-right">
                    <p className="text-xs text-gray-400">
                      {sensor.session_count} sessions
                    </p>
                    <p className="text-xs text-gray-500">
                      {getStatusLabel(sensor.status, sensor.last_seen)}
                      {sensor.last_seen && (
                        <span className="ml-1">
                          - {new Date(sensor.last_seen).toLocaleString()}
                        </span>
                      )}
                    </p>
                  </div>
                  <button
                    onClick={() => handleDelete(sensor.id)}
                    className="px-2 py-1 text-xs text-red-400 hover:text-red-300 hover:bg-red-900/20 rounded transition-colors"
                  >
                    Remove
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
