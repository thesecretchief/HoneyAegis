import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "HoneyAegis Dashboard",
  description: "Professional-grade honeypot platform dashboard — real-time attack monitoring, session replay, AI threat analysis",
  keywords: ["honeypot", "security", "deception", "monitoring", "threat-intelligence"],
  authors: [{ name: "HoneyAegis Community" }],
  robots: "noindex, nofollow",
  other: {
    "theme-color": "#f59e0b",
  },
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
          <nav aria-label="Main navigation" className="hidden md:flex w-64 bg-gray-900 border-r border-gray-800 p-4 flex-col shrink-0">
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
              <NavItem href="/honey-tokens" label="Honey Tokens" />
              <NavItem href="/webhooks" label="Webhooks" />
              <NavItem href="/sensors" label="Sensors" />
              <NavItem href="/config" label="Config" />
            </ul>
            <div className="mt-auto pt-4 border-t border-gray-800">
              <p className="text-xs text-gray-600">HoneyAegis v1.0.0</p>
            </div>
          </nav>
          {/* Mobile nav */}
          <nav aria-label="Mobile navigation" className="md:hidden fixed bottom-0 left-0 right-0 bg-gray-900 border-t border-gray-800 z-50">
            <div className="flex justify-around py-2">
              <MobileNavItem href="/" label="Home" />
              <MobileNavItem href="/sessions" label="Sessions" />
              <MobileNavItem href="/alerts" label="Alerts" />
              <MobileNavItem href="/honey-tokens" label="Tokens" />
              <MobileNavItem href="/webhooks" label="Hooks" />
              <MobileNavItem href="/config" label="Config" />
            </div>
          </nav>
          <main role="main" className="flex-1 p-4 md:p-8 overflow-auto pb-20 md:pb-8">{children}</main>
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

function MobileNavItem({ href, label }: { href: string; label: string }) {
  return (
    <a
      href={href}
      className="flex flex-col items-center px-2 py-1 text-gray-400 hover:text-gray-100 transition-colors"
    >
      <span className="text-xs">{label}</span>
    </a>
  );
}
