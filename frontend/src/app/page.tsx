export default function DashboardPage() {
  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">Dashboard</h2>

      {/* Stats cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatsCard title="Total Sessions" value="--" subtitle="Awaiting data" />
        <StatsCard
          title="Unique IPs"
          value="--"
          subtitle="Awaiting data"
        />
        <StatsCard
          title="Auth Attempts"
          value="--"
          subtitle="Awaiting data"
        />
        <StatsCard title="Active Sensors" value="1" subtitle="Cowrie online" />
      </div>

      {/* Placeholder panels */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
          <h3 className="text-lg font-semibold mb-4">Recent Sessions</h3>
          <p className="text-gray-500 text-sm">
            Session data will appear here once Cowrie captures connections.
          </p>
        </div>
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
          <h3 className="text-lg font-semibold mb-4">Attack Map</h3>
          <p className="text-gray-500 text-sm">
            Live attack map with GeoIP visualization coming in Iteration 1.
          </p>
        </div>
      </div>
    </div>
  );
}

function StatsCard({
  title,
  value,
  subtitle,
}: {
  title: string;
  value: string;
  subtitle: string;
}) {
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
      <p className="text-sm text-gray-400">{title}</p>
      <p className="text-3xl font-bold mt-1">{value}</p>
      <p className="text-xs text-gray-500 mt-1">{subtitle}</p>
    </div>
  );
}
