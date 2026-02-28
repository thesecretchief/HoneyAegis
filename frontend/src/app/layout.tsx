import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "HoneyAegis Dashboard",
  description: "Professional-grade honeypot platform dashboard",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-gray-950 text-gray-100">
        <div className="flex min-h-screen">
          <nav className="w-64 bg-gray-900 border-r border-gray-800 p-4">
            <div className="mb-8">
              <h1 className="text-xl font-bold text-honeyaegis-400">
                HoneyAegis
              </h1>
              <p className="text-xs text-gray-500 mt-1">Deception Platform</p>
            </div>
            <ul className="space-y-2">
              <li>
                <a
                  href="/"
                  className="block px-3 py-2 rounded-lg bg-gray-800 text-gray-100"
                >
                  Dashboard
                </a>
              </li>
              <li>
                <a
                  href="/sessions"
                  className="block px-3 py-2 rounded-lg text-gray-400 hover:text-gray-100 hover:bg-gray-800"
                >
                  Sessions
                </a>
              </li>
              <li>
                <a
                  href="/alerts"
                  className="block px-3 py-2 rounded-lg text-gray-400 hover:text-gray-100 hover:bg-gray-800"
                >
                  Alerts
                </a>
              </li>
              <li>
                <a
                  href="/sensors"
                  className="block px-3 py-2 rounded-lg text-gray-400 hover:text-gray-100 hover:bg-gray-800"
                >
                  Sensors
                </a>
              </li>
            </ul>
          </nav>
          <main className="flex-1 p-8">{children}</main>
        </div>
      </body>
    </html>
  );
}
