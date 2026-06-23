import type { Metadata } from "next";
import { SITE } from "@/lib/config";
import { SiteHeader } from "@/components/SiteHeader";
import { SiteFooter } from "@/components/SiteFooter";
import "./globals.css";

export const metadata: Metadata = {
  title: `${SITE.domain} — ${SITE.tagline}`,
  description: SITE.description,
  metadataBase: new URL("https://robark.io"),
  openGraph: {
    title: `${SITE.domain} — ${SITE.tagline}`,
    description: SITE.description,
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: `${SITE.domain} — ${SITE.tagline}`,
    description: SITE.description,
  },
  icons: { icon: "/favicon.svg" },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="" />
        <link
          rel="stylesheet"
          href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&family=Press+Start+2P&family=Space+Grotesk:wght@500;600;700&display=swap"
        />
      </head>
      <body className="min-h-screen font-sans">
        <div className="relative flex min-h-screen flex-col">
          <SiteHeader />
          <main className="flex-1">{children}</main>
          <SiteFooter />
        </div>
      </body>
    </html>
  );
}
