import Link from "next/link";

export default function NotFound() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] p-8">
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-8 max-w-md w-full text-center">
        <h2 className="text-6xl font-bold text-gray-700 mb-2">404</h2>
        <h3 className="text-xl font-semibold text-gray-300 mb-4">Page Not Found</h3>
        <p className="text-gray-500 mb-6 text-sm">
          The page you are looking for does not exist or has been moved.
        </p>
        <Link
          href="/"
          className="inline-block px-4 py-2 bg-honeyaegis-500 hover:bg-honeyaegis-600 text-white rounded-lg transition-colors"
        >
          Back to Dashboard
        </Link>
      </div>
    </div>
  );
}
