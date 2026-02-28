"use client";

import { useEffect } from "react";
import { getToken } from "@/lib/api";

export default function SensorsPage() {
  useEffect(() => {
    if (!getToken()) {
      window.location.href = "/login";
    }
  }, []);

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">Sensors</h2>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">Active Sensors</h3>
          <span className="text-xs text-gray-500">1 sensor online</span>
        </div>

        <div className="space-y-3">
          <div className="flex items-center justify-between p-4 rounded-lg bg-gray-800/50">
            <div className="flex items-center gap-3">
              <span className="w-3 h-3 rounded-full bg-green-400 animate-pulse" />
              <div>
                <p className="text-sm font-semibold">Primary Sensor</p>
                <p className="text-xs text-gray-500">
                  sensor-01 | Cowrie SSH/Telnet
                </p>
              </div>
            </div>
            <div className="text-right">
              <p className="text-xs text-gray-400">Ports: 2222, 2223</p>
              <p className="text-xs text-gray-500">Status: Active</p>
            </div>
          </div>
        </div>

        <div className="mt-6 p-4 border border-dashed border-gray-700 rounded-lg text-center">
          <p className="text-sm text-gray-500">
            Multi-sensor fleet management coming in Iteration 2.
          </p>
          <p className="text-xs text-gray-600 mt-1">
            Register remote sensors, RPi nodes, and VPS instances from this
            console.
          </p>
        </div>
      </div>
    </div>
  );
}
