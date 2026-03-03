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
  // For all other methods (GET, DELETE, HEAD, OPTIONS) we must NOT set `body`
  // or `duplex` — Node 18 fetch throws TypeError when `duplex: 'half'` is
  // present without a real body stream.
  const hasBody = ['POST', 'PUT', 'PATCH'].includes(req.method);

  // Build fetch options conditionally so DELETE never gets body/duplex.
  // We also do NOT use redirect:'follow' because Node fetch re-sends the original
  // request (including any problematic options) on 307/308 — instead we handle
  // the redirect manually so we control the options on the second hop.
  const fetchOptions: RequestInit & { duplex?: string } = {
    method: req.method,
    headers: {
      'Content-Type': req.headers.get('content-type') ?? 'application/json',
    },
    redirect: 'manual', // capture 3xx ourselves
  };
  if (hasBody) {
    fetchOptions.body = req.body as BodyInit;
    fetchOptions.duplex = 'half'; // required for streaming body in Node 18+
  }

  let upstream = await fetch(target, fetchOptions);

  // Handle 307 / 308 redirects manually so we keep full control of options.
  // FastAPI may 307 if the ASGI server applies its own trailing-slash redirect.
  if (upstream.status === 307 || upstream.status === 308) {
    const location = upstream.headers.get('location');
    if (location) {
      // Resolve relative Location headers against the backend base URL
      const redirectTarget = location.startsWith('http')
        ? location
        : `${BACKEND_URL}${location}`;
      upstream = await fetch(redirectTarget, fetchOptions);
    }
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
