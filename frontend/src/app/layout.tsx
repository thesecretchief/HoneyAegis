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
      <head>
        <link
          rel="stylesheet"
          href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css"
          integrity="sha512-h9FcoyWjHcOcmEVkxOfTLnmZFWIH0iZhZT1H2TbOq55xssQGEJHEaIm+PgoUaZhRvQTNTluNOEfb1ZRy6D3bA=="
          crossOrigin="anonymous"
        />
      </head>
      <body className="min-h-screen bg-gray-950 text-gray-100">
        <div className="flex min-h-screen">
          <nav className="w-64 bg-gray-900 border-r border-gray-800 p-4 flex flex-col">
            <div className="mb-8">
              <h1 className="text-xl font-bold text-honeyaegis-400">
                HoneyAegis
              </h1>
              <p className="text-xs text-gray-500 mt-1">Deception Platform</p>
            </div>
            <ul className="space-y-1 flex-1">
              <NavItem href="/" label="Dashboard" />
              <NavItem href="/sessions" label="Sessions" />
              <NavItem href="/alerts" label="Alerts" />
              <NavItem href="/sensors" label="Sensors" />
            </ul>
            <div className="mt-auto pt-4 border-t border-gray-800">
              <p className="text-xs text-gray-600">HoneyAegis v0.2.0</p>
            </div>
          </nav>
          <main className="flex-1 p-8 overflow-auto">{children}</main>
        </div>
      </body>
    </html>
  );
}

function NavItem({ href, label }: { href: string; label: string }) {
  return (
    <li>
      <a
        href={href}
        className="block px-3 py-2 rounded-lg text-gray-400 hover:text-gray-100 hover:bg-gray-800 transition-colors"
      >
        {label}
      </a>
    </li>
  );
}
