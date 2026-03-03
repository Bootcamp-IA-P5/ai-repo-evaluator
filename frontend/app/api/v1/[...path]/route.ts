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

  // Only POST / PUT / PATCH carry a request body.
  // DELETE, GET, HEAD, OPTIONS must NOT have `body` or `duplex` in the options
  // object at all — Node 18 (undici) throws TypeError: fetch failed when
  // `duplex: 'half'` is present even if `body` is undefined.
  const hasBody = ['POST', 'PUT', 'PATCH'].includes(req.method);

  // Read the body eagerly as text so we never pass a partially-consumed
  // ReadableStream to the upstream fetch — that causes a TypeError in undici
  // even when duplex:'half' is set.
  const bodyText = hasBody ? await req.text() : undefined;

  type FetchOpts = RequestInit & { duplex?: string };

  const fetchOptions: FetchOpts = {
    method: req.method,
    headers: {
      'Content-Type': req.headers.get('content-type') ?? 'application/json',
    },
    redirect: 'follow',
    ...(hasBody ? { body: bodyText } : {}),
  };

  let upstream: Response;
  try {
    upstream = await fetch(target, fetchOptions);
  } catch (err) {
    // Network-level failure (DNS, TCP, etc.) — backend unreachable
    console.error('[proxy] upstream fetch failed:', target, err);
    return new NextResponse(
      JSON.stringify({ success: false, errors: ['Backend unreachable'], message: 'Proxy error' }),
      { status: 502, headers: { 'Content-Type': 'application/json' } }
    );
  }

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
