import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Sitelet",
  description: "Preview and operate websites through a client-rendered proxy.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
