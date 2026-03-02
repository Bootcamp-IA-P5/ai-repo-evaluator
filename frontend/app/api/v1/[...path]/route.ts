import { NextRequest, NextResponse } from 'next/server';

/**
 * Proxy all /api/v1/* requests to the FastAPI backend.
 *
 * Using a Route Handler instead of next.config.ts rewrites because:
 * - Turbopack (dev mode) does not respect skipTrailingSlashRedirect reliably.
 * - When rewrites follow a 307 from the backend, Next.js forwards the raw
 *   Location header (http://backend:8000/...) to the browser, which can't
 *   resolve the Docker-internal hostname → CORS/ERR_NAME_NOT_RESOLVED.
 *
 * This handler follows redirects server-side so the browser only ever
 * talks to localhost:3000.
 */

const BACKEND_URL = 'http://backend:8000';

async function handler(req: NextRequest): Promise<NextResponse> {
  // Build the target URL — always add trailing slash so FastAPI doesn't 307
  const pathname = req.nextUrl.pathname.replace(/\/?$/, '/'); // ensure trailing /
  const search = req.nextUrl.search;                          // e.g. ?limit=10
  const target = `${BACKEND_URL}${pathname}${search}`;

  // Forward request body for methods that allow it
  const hasBody = !['GET', 'HEAD'].includes(req.method);

  const upstream = await fetch(target, {
    method: req.method,
    headers: {
      'Content-Type': req.headers.get('content-type') ?? 'application/json',
    },
    body: hasBody ? req.body : undefined,
    // Follow redirects server-side so the browser never sees backend:8000
    redirect: 'follow',
    // Required for streaming body passthrough
    // @ts-expect-error — Node 18+ fetch supports duplex
    duplex: 'half',
  });

  const contentType = upstream.headers.get('content-type') ?? '';
  const body = await upstream.text();

  return new NextResponse(body, {
    status: upstream.status,
    headers: {
      'Content-Type': contentType,
    },
  });
}

export const GET    = handler;
export const POST   = handler;
export const PUT    = handler;
export const PATCH  = handler;
export const DELETE = handler;
export const OPTIONS = handler;
