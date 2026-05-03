import type { Metadata } from "next";

import "./globals.css";
import { SiteFooter } from "../components/site-footer";
import { SiteHeader } from "../components/site-header";
import { brand } from "../lib/storefront-data";

export const metadata: Metadata = {
  title: `${brand.name} · Static Storefront Starter`,
  description: brand.promise,
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <div className="site-shell">
          <SiteHeader />
          {children}
          <SiteFooter />
        </div>
      </body>
    </html>
  );
}
