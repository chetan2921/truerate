import type { Metadata } from "next";
import { Urbanist } from "next/font/google";
import "./globals.css";

// Solo uses Gilroy, a paid font; Urbanist is the closest free geometric match (DESIGN.md).
const urbanist = Urbanist({
  variable: "--font-urbanist",
  subsets: ["latin"],
  weight: ["400", "600", "700"],
});

export const metadata: Metadata = {
  title: "TrueRate",
  description: "What one reel is worth, and whether WLDD should book the creator.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="en" className={`${urbanist.variable} h-full antialiased`}>
      <body className="min-h-full font-sans">{children}</body>
    </html>
  );
}
