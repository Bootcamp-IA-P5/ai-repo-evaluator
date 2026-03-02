import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: 'standalone',

  // Prevent Next.js from stripping trailing slashes before rewrites are applied.
  // Without this, POST /api/v1/rubrics/ becomes POST /api/v1/rubrics (no slash),
  // the backend returns 307, and the browser follows the redirect directly to
  // backend:8000 — bypassing the proxy and causing CORS errors.
  skipTrailingSlashRedirect: true,

  async redirects() {
    return [
      {
        source: '/',
        destination: '/new-evaluation',
        permanent: false,
      },
    ];
  },

  // NOTE: /api/v1/* proxying is handled by the Route Handler at
  // app/api/v1/[...path]/route.ts — no rewrites needed.
};

export default nextConfig;
