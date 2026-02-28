"use client";

export function LoadingSpinner({ size = "md" }: { size?: "sm" | "md" | "lg" }) {
  const sizeClass = size === "sm" ? "w-4 h-4" : size === "lg" ? "w-8 h-8" : "w-6 h-6";
  return (
    <div className={`${sizeClass} border-2 border-gray-700 border-t-honeyaegis-400 rounded-full animate-spin`} />
  );
}

export function CardSkeleton({ count = 4 }: { count?: number }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="bg-gray-900 border border-gray-800 rounded-xl p-5 animate-pulse">
          <div className="h-3 bg-gray-800 rounded w-20 mb-3" />
          <div className="h-8 bg-gray-800 rounded w-16 mb-2" />
          <div className="h-2 bg-gray-800 rounded w-24" />
        </div>
      ))}
    </div>
  );
}

export function TableSkeleton({ rows = 5 }: { rows?: number }) {
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 animate-pulse space-y-3">
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="flex items-center justify-between p-3 bg-gray-800/50 rounded-lg">
          <div className="flex items-center gap-3">
            <div className="w-2 h-2 rounded-full bg-gray-700" />
            <div>
              <div className="h-3 bg-gray-700 rounded w-28 mb-1.5" />
              <div className="h-2 bg-gray-800 rounded w-40" />
            </div>
          </div>
          <div className="text-right">
            <div className="h-2 bg-gray-700 rounded w-16 mb-1.5" />
            <div className="h-2 bg-gray-800 rounded w-20" />
          </div>
        </div>
      ))}
    </div>
  );
}

export function FullPageLoader() {
  return (
    <div className="flex items-center justify-center h-64">
      <div className="text-center">
        <LoadingSpinner size="lg" />
        <p className="text-sm text-gray-500 mt-3">Loading...</p>
      </div>
    </div>
  );
}
