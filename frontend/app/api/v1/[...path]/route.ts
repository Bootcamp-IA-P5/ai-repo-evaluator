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
  // Forward the path as-is — redirect:'follow' handles any 307 the backend emits.
  const pathname = req.nextUrl.pathname;
  const search = req.nextUrl.search; // e.g. ?limit=10
  const target = `${BACKEND_URL}${pathname}${search}`;

  // Only POST / PUT / PATCH carry a request body.
  // DELETE / GET / HEAD / OPTIONS must NOT have a body in the options object —
  // Node 18 (undici) throws TypeError when body is present on bodyless methods.
  const hasBody = ['POST', 'PUT', 'PATCH'].includes(req.method);

  // Pass the raw ReadableStream directly — this avoids the "detached ArrayBuffer"
  // error that occurs when req.arrayBuffer() is read and then passed to fetch(),
  // because Node's undici may detach the buffer during the transfer. Streaming
  // the body also preserves binary payloads (multipart/form-data) without copying.
  const bodyBuffer = hasBody ? req.body : undefined;

  // Forward all original request headers except hop-by-hop ones.
  const forwardHeaders: Record<string, string> = {};
  req.headers.forEach((value, key) => {
    if (!HOP_BY_HOP.has(key.toLowerCase())) {
      forwardHeaders[key] = value;
    }
  });

  const fetchOptions: RequestInit = {
    method: req.method,
    headers: forwardHeaders,
    redirect: 'follow',
    ...(hasBody ? { body: bodyBuffer } : {}),
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
