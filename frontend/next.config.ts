import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",

  // Prevent Next.js from stripping trailing slashes — avoids 307 redirect
  // from backend exposing internal Docker hostname (backend:8000) to the browser.
  skipTrailingSlashRedirect: true,

  async redirects() {
    return [
      {
        source: "/",
        destination: "/dashboard",
        permanent: false,
      },
    ];
  },

  // NOTE: /api/v1/* proxying is handled by the Route Handler at
  // app/api/v1/[...path]/route.ts — no rewrites needed.
};

export default nextConfig;
