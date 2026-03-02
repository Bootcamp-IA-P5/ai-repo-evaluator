import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: 'standalone',
  async redirects() {
    return [
      {
        source: '/',
        destination: '/new-evaluation',
        permanent: false,
      },
    ];
  },

  /**
   * Proxy all /api/v1/* requests through the Next.js server to avoid
   * CORS issues in the browser. The destination uses the Docker Compose
   * service name "backend" which is only reachable server-side.
   */
  async rewrites() {
    return [
      {
        source: '/api/v1/:path*',
        destination: 'http://backend:8000/api/v1/:path*',
      },
    ];
  },
};

export default nextConfig;