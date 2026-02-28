"use client";

import { useEffect, useRef, useState } from "react";
import { getMapData, type GeoPoint } from "@/lib/api";

/**
 * Attack Map component using Leaflet.
 * Dynamically imports leaflet to avoid SSR issues.
 */
export default function AttackMap() {
  const mapRef = useRef<HTMLDivElement>(null);
  const [points, setPoints] = useState<GeoPoint[]>([]);
  const [mapInstance, setMapInstance] = useState<unknown>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const data = await getMapData(24);
        setPoints(data);
      } catch {
        // will show empty map
      } finally {
        setLoading(false);
      }
    }
    loadData();
    const interval = setInterval(loadData, 30000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (!mapRef.current || typeof window === "undefined") return;

    // Dynamic import of Leaflet
    import("leaflet").then((L) => {
      // Fix default marker icon
      delete (L.Icon.Default.prototype as Record<string, unknown>)._getIconUrl;
      L.Icon.Default.mergeOptions({
        iconRetinaUrl:
          "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png",
        iconUrl:
          "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png",
        shadowUrl:
          "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png",
      });

      if (mapInstance) return;

      const map = L.map(mapRef.current!, {
        center: [20, 0],
        zoom: 2,
        minZoom: 2,
        maxZoom: 12,
        zoomControl: true,
        attributionControl: true,
      });

      // Dark tile layer
      L.tileLayer(
        "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
        {
          attribution:
            '&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a> &copy; <a href="https://carto.com/">CARTO</a>',
          subdomains: "abcd",
          maxZoom: 19,
        },
      ).addTo(map);

      setMapInstance(map);

      // Add markers for existing points
      for (const point of points) {
        if (point.latitude === 0 && point.longitude === 0) continue;

        const radius = Math.min(Math.max(point.session_count * 3, 5), 30);

        L.circleMarker([point.latitude, point.longitude], {
          radius,
          fillColor: "#ef4444",
          color: "#fbbf24",
          weight: 1,
          opacity: 0.8,
          fillOpacity: 0.5,
        })
          .bindPopup(
            `<div style="color: #000;">
              <strong>${point.src_ip}</strong><br/>
              ${point.city ? point.city + ", " : ""}${point.country_name}<br/>
              Sessions: ${point.session_count}<br/>
              ${point.last_seen ? "Last seen: " + new Date(point.last_seen).toLocaleString() : ""}
            </div>`,
          )
          .addTo(map);
      }
    });
  }, [points]);

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden">
      <div className="flex items-center justify-between px-4 py-3 border-b border-gray-800">
        <h3 className="text-lg font-semibold">Attack Map</h3>
        <span className="text-xs text-gray-500">
          {loading ? "Loading..." : `${points.length} sources (24h)`}
        </span>
      </div>
      <div ref={mapRef} style={{ height: "400px", width: "100%" }} />
    </div>
  );
}
