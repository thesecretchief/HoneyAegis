import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Client Portal - HoneyAegis",
  description: "View-only client portal for honeypot monitoring",
};

export default function ClientPortalLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}
