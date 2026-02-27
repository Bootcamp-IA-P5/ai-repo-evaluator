import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "AI Repository Evaluator",
  description: "AI-powered tool for evaluating student repositories using custom rubrics",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      {/*
       * suppressHydrationWarning is required on <body> to prevent false hydration
       * mismatch errors caused by browser extensions (e.g. password managers,
       * ColorZilla) that inject attributes like `cz-shortcut-listen` into the DOM
       * before React hydrates. This does NOT suppress real hydration errors in
       * child components.
       */}
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
        suppressHydrationWarning
      >
        {children}
      </body>
    </html>
  );
}
