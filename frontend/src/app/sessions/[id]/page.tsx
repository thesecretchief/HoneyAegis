"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import {
  getSession,
  getSessionCommands,
  getSessionReplay,
  getVideoExportUrl,
  getToken,
  type Session,
  type SessionCommand,
  type ReplayData,
} from "@/lib/api";

export default function SessionDetailPage() {
  const params = useParams();
  const sessionId = params.id as string;
  const [session, setSession] = useState<Session | null>(null);
  const [commands, setCommands] = useState<SessionCommand[]>([]);
  const [replay, setReplay] = useState<ReplayData | null>(null);
  const [replayPlaying, setReplayPlaying] = useState(false);
  const [replayOutput, setReplayOutput] = useState("");
  const [replayProgress, setReplayProgress] = useState(0);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<"commands" | "replay">(
    "commands",
  );

  useEffect(() => {
    if (!getToken()) {
      window.location.href = "/login";
      return;
    }

    async function fetchData() {
      try {
        const [sessionData, commandsData] = await Promise.all([
          getSession(sessionId),
          getSessionCommands(sessionId).catch(() => []),
        ]);
        setSession(sessionData);
        setCommands(commandsData);

        // Try loading replay data
        try {
          const replayData = await getSessionReplay(sessionId);
          setReplay(replayData);
        } catch {
          // replay not available
        }
      } catch {
        // handled by API client
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, [sessionId]);

  async function playReplay() {
    if (!replay) return;

    setReplayPlaying(true);
    setReplayOutput("");
    setReplayProgress(0);

    const lines = replay.asciicast.split("\n");
    const events = lines.slice(1).map((line) => {
      try {
        return JSON.parse(line);
      } catch {
        return null;
      }
    }).filter(Boolean);

    const duration = replay.header.duration || 1;
    let output = "";

    for (const event of events) {
      const [time, , text] = event;
      setReplayProgress((time / duration) * 100);
      output += text;
      setReplayOutput(output);
      // Delay proportional to time gap (max 500ms between frames)
      const nextIdx = events.indexOf(event) + 1;
      if (nextIdx < events.length) {
        const gap = Math.min(events[nextIdx][0] - time, 0.5);
        if (gap > 0) {
          await new Promise((r) => setTimeout(r, gap * 1000));
        }
      }
    }

    setReplayProgress(100);
    setReplayPlaying(false);
  }

  if (loading) {
    return (
      <div className="p-8 text-gray-500">Loading session details...</div>
    );
  }

  if (!session) {
    return <div className="p-8 text-red-400">Session not found</div>;
  }

  return (
    <div>
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <a
            href="/sessions"
            className="text-sm text-gray-500 hover:text-gray-300"
          >
            Sessions /
          </a>
          <h2 className="text-2xl font-bold mt-1">
            {session.src_ip}
            <span className="text-gray-500 text-lg ml-2">
              {session.session_id}
            </span>
          </h2>
        </div>
        <div className="flex gap-2">
          {replay && (
            <>
              <a
                href={getVideoExportUrl(sessionId, "mp4")}
                className="px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg text-sm transition-colors"
                target="_blank"
              >
                Export MP4
              </a>
              <a
                href={getVideoExportUrl(sessionId, "gif")}
                className="px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg text-sm transition-colors"
                target="_blank"
              >
                Export GIF
              </a>
            </>
          )}
        </div>
      </div>

      {/* Session metadata */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <InfoCard label="Protocol" value={`${session.protocol.toUpperCase()} :${session.dst_port}`} />
        <InfoCard label="Source" value={`${session.src_ip}:${session.src_port || "?"}`} />
        <InfoCard
          label="Location"
          value={
            session.country_name && session.country_name !== "Unknown"
              ? `${session.city || ""} ${session.country_name} (${session.country_code})`
              : "Unknown"
          }
        />
        <InfoCard
          label="Duration"
          value={
            session.duration_seconds
              ? `${Math.round(session.duration_seconds)}s`
              : "Active"
          }
        />
        <InfoCard
          label="Username"
          value={session.username || "N/A"}
        />
        <InfoCard
          label="Auth Success"
          value={session.auth_success ? "Yes" : "No"}
          color={session.auth_success ? "text-green-400" : "text-gray-400"}
        />
        <InfoCard
          label="Commands"
          value={session.commands_count.toString()}
        />
        <InfoCard
          label="Started"
          value={new Date(session.started_at).toLocaleString()}
        />
      </div>

      {/* Tabs */}
      <div className="flex gap-1 mb-4">
        <button
          onClick={() => setActiveTab("commands")}
          className={`px-4 py-2 rounded-lg text-sm transition-colors ${
            activeTab === "commands"
              ? "bg-gray-800 text-gray-100"
              : "text-gray-500 hover:text-gray-300"
          }`}
        >
          Commands ({commands.length})
        </button>
        <button
          onClick={() => setActiveTab("replay")}
          className={`px-4 py-2 rounded-lg text-sm transition-colors ${
            activeTab === "replay"
              ? "bg-gray-800 text-gray-100"
              : "text-gray-500 hover:text-gray-300"
          }`}
        >
          Session Replay
        </button>
      </div>

      {/* Commands Tab */}
      {activeTab === "commands" && (
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
          {commands.length === 0 ? (
            <p className="text-gray-500 text-sm">
              No commands captured in this session.
            </p>
          ) : (
            <div className="space-y-2">
              {commands.map((cmd, i) => (
                <div key={i} className="font-mono text-sm">
                  <div className="flex items-start gap-2">
                    <span className="text-green-400 select-none">$</span>
                    <span className="text-gray-200">{cmd.command}</span>
                    <span className="text-gray-600 text-xs ml-auto">
                      {cmd.timestamp
                        ? new Date(cmd.timestamp).toLocaleTimeString()
                        : ""}
                    </span>
                  </div>
                  {cmd.output && (
                    <pre className="text-gray-400 text-xs ml-4 mt-1 whitespace-pre-wrap">
                      {cmd.output}
                    </pre>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Replay Tab */}
      {activeTab === "replay" && (
        <div className="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden">
          {/* Terminal header */}
          <div className="flex items-center justify-between px-4 py-2 bg-gray-800 border-b border-gray-700">
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-red-500" />
              <span className="w-3 h-3 rounded-full bg-yellow-500" />
              <span className="w-3 h-3 rounded-full bg-green-500" />
              <span className="text-xs text-gray-500 ml-2">
                {session.session_id} - {session.src_ip}
              </span>
            </div>
            {replay ? (
              <button
                onClick={playReplay}
                disabled={replayPlaying}
                className="px-3 py-1 bg-green-600 hover:bg-green-500 rounded text-xs font-semibold text-white disabled:opacity-50 transition-colors"
              >
                {replayPlaying ? "Playing..." : "Play"}
              </button>
            ) : (
              <span className="text-xs text-gray-500">
                No recording available
              </span>
            )}
          </div>

          {/* Progress bar */}
          {replayPlaying && (
            <div className="h-0.5 bg-gray-800">
              <div
                className="h-full bg-green-400 transition-all duration-200"
                style={{ width: `${replayProgress}%` }}
              />
            </div>
          )}

          {/* Terminal output */}
          <pre className="p-4 font-mono text-sm text-green-400 bg-black min-h-[300px] max-h-[600px] overflow-auto whitespace-pre-wrap">
            {replayOutput || (replay
              ? "Press Play to start session replay..."
              : "No tty recording found for this session.\nCommands are available in the Commands tab.")}
          </pre>

          {/* Stats */}
          {replay && (
            <div className="px-4 py-2 bg-gray-800 border-t border-gray-700 flex items-center justify-between text-xs text-gray-500">
              <span>
                {replay.event_count} events | Duration:{" "}
                {Math.round(replay.header.duration)}s
              </span>
              <span>
                {replay.header.width}x{replay.header.height}
              </span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function InfoCard({
  label,
  value,
  color = "text-gray-200",
}: {
  label: string;
  value: string;
  color?: string;
}) {
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-4">
      <p className="text-xs text-gray-500">{label}</p>
      <p className={`text-sm font-semibold mt-1 ${color}`}>{value}</p>
    </div>
  );
}
