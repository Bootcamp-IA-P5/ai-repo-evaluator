import { NextRequest, NextResponse } from 'next/server';

/**
 * Proxy all /api/v1/* requests to the FastAPI backend.
 *
 * Using a Route Handler (app/api/v1/[...path]/route.ts) instead of
 * next.config.ts rewrites because Turbopack doesn't honour rewrites reliably
 * in dev mode, and rewrite-based proxying leaks the Docker-internal hostname
 * (http://backend:8000) to the browser via Location headers.
 *
 * This handler runs server-side so the browser only ever talks to
 * localhost:3000.
 */

// Server-side only env var — never exposed to the browser bundle.
// Override in frontend/.env (or docker-compose env_file) for non-Docker setups.
const BACKEND_URL = process.env.BACKEND_URL ?? 'http://backend:8000';

// Hop-by-hop headers that must not be forwarded to the upstream service.
const HOP_BY_HOP = new Set([
  'connection', 'keep-alive', 'proxy-authenticate', 'proxy-authorization',
  'te', 'trailers', 'transfer-encoding', 'upgrade',
  // 'host' must be omitted so the backend sees its own hostname, not localhost:3000
  'host',
]);

async function handler(req: NextRequest): Promise<NextResponse> {
  const pathname = req.nextUrl.pathname;
  const search = req.nextUrl.search; // e.g. ?limit=10
  const initialTarget = `${BACKEND_URL}${pathname}${search}`;

  // Only POST / PUT / PATCH carry a request body.
  // DELETE / GET / HEAD / OPTIONS must NOT have a body in the options object —
  // Node 18 (undici) throws TypeError when body is present on bodyless methods.
  const hasBody = ['POST', 'PUT', 'PATCH'].includes(req.method);

  // Read body once into a Node.js Buffer (immune to ArrayBuffer detachment).
  // We use Buffer.from() to clone it before each fetch call, because undici
  // internally detaches the underlying ArrayBuffer after the first use.
  // This allows us to safely follow 307 redirects by re-sending the same body.
  const bodyBytes = hasBody ? Buffer.from(await req.arrayBuffer()) : undefined;

  // Forward all original request headers except hop-by-hop ones.
  const forwardHeaders: Record<string, string> = {};
  req.headers.forEach((value, key) => {
    if (!HOP_BY_HOP.has(key.toLowerCase())) {
      forwardHeaders[key] = value;
    }
  });

  // Perform fetch with redirect:'manual' so we can follow 307/308 ourselves,
  // re-attaching a fresh copy of the body buffer on each redirect hop.
  // This avoids the "detached ArrayBuffer" crash that occurs when undici tries
  // to re-read an already-consumed buffer while following redirects internally.
  const doFetch = (url: string): Promise<Response> =>
    fetch(url, {
      method: req.method,
      headers: forwardHeaders,
      redirect: 'manual',
      ...(bodyBytes ? { body: Buffer.from(bodyBytes) } : {}),
    });

  let upstream: Response;
  let currentUrl = initialTarget;

  try {
    // Follow up to 5 redirect hops manually.
    for (let hop = 0; hop < 5; hop++) {
      upstream = await doFetch(currentUrl);
      const isRedirect = upstream.status === 301 || upstream.status === 302 ||
                         upstream.status === 307 || upstream.status === 308;
      if (!isRedirect) break;

      const location = upstream.headers.get('location');
      if (!location) break;

      // Location may be relative (e.g. "/api/v1/rubrics/") or absolute.
      currentUrl = location.startsWith('http') ? location : `${BACKEND_URL}${location}`;
    }
  } catch (err) {
    // Network-level failure (DNS, TCP, etc.) — backend unreachable
    console.error('[proxy] upstream fetch failed:', currentUrl, err);
    return new NextResponse(
      JSON.stringify({ success: false, errors: ['Backend unreachable'], message: 'Proxy error' }),
      { status: 502, headers: { 'Content-Type': 'application/json' } }
    );
  }

  const contentType = upstream!.headers.get('content-type') ?? '';
  const body = await upstream!.text();

  return new NextResponse(body, {
    status: upstream!.status,
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
