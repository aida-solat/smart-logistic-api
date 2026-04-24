import type { Metadata } from "next";
import { Archivo, Inter, Space_Mono } from "next/font/google";
import "./globals.css";

const body = Inter({
  subsets: ["latin"],
  variable: "--font-sans",
  display: "swap",
});
const heading = Archivo({
  subsets: ["latin"],
  variable: "--font-display",
  display: "swap",
  weight: ["700", "800", "900"],
});
const mono = Space_Mono({
  subsets: ["latin"],
  variable: "--font-mono",
  display: "swap",
  weight: ["400", "700"],
});

export const metadata: Metadata = {
  title: "Smart Logistics — Causal Decision Copilot",
  description:
    "A prescriptive, causal, risk-aware decision engine for logistics. Not another ETA predictor.",
  metadataBase: new URL("https://smart-logistics.dev"),
  openGraph: {
    title: "Smart Logistics — Causal Decision Copilot",
    description: "Prescriptive causal optimization under tail risk.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html
      lang="en"
      className={`${body.variable} ${heading.variable} ${mono.variable}`}
    >
      <body className="font-sans antialiased" suppressHydrationWarning>
        {children}
      </body>
    </html>
  );
}
