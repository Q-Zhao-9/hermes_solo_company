import {
  normalizeTargetUrl,
  responseHeaders,
  rewriteHtml,
  upstreamHeaders,
} from "../../lib/sitelet";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const BODY_METHODS = new Set(["POST", "PUT", "PATCH", "DELETE"]);

export async function GET(request: Request) {
  return proxyRequest(request);
}

export async function POST(request: Request) {
  return proxyRequest(request);
}

export async function PUT(request: Request) {
  return proxyRequest(request);
}

export async function PATCH(request: Request) {
  return proxyRequest(request);
}

export async function DELETE(request: Request) {
  return proxyRequest(request);
}

async function proxyRequest(request: Request): Promise<Response> {
  const requestUrl = new URL(request.url);

  try {
    const targetUrl = normalizeTargetUrl(requestUrl.searchParams.get("url"));
    const init: RequestInit = {
      method: request.method,
      headers: upstreamHeaders(request, targetUrl),
      redirect: "manual",
    };

    if (BODY_METHODS.has(request.method)) {
      init.body = await request.arrayBuffer();
    }

    const upstream = await fetch(targetUrl, init);
    const location = upstream.headers.get("location");
    if (location && upstream.status >= 300 && upstream.status < 400) {
      const redirected = new URL(location, targetUrl);
      const nextUrl = new URL("/sitelet", requestUrl.origin);
      nextUrl.searchParams.set("url", redirected.toString());
      return Response.redirect(nextUrl, upstream.status);
    }

    const contentType = upstream.headers.get("content-type") || "application/octet-stream";
    if (contentType.includes("text/html")) {
      const html = await upstream.text();
      return new Response(rewriteHtml(html, targetUrl, requestUrl), {
        status: upstream.status,
        headers: responseHeaders(upstream, "text/html; charset=utf-8"),
      });
    }

    return new Response(upstream.body, {
      status: upstream.status,
      headers: responseHeaders(upstream, contentType),
    });
  } catch (error) {
    const message = error instanceof Error ? error.message : "Unknown Sitelet error.";
    return new Response(renderError(message), {
      status: 400,
      headers: {
        "content-type": "text/html; charset=utf-8",
      },
    });
  }
}

function renderError(message: string): string {
  return `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Sitelet Error</title>
  <style>
    body { margin: 0; min-height: 100vh; display: grid; place-items: center; font: 16px Arial, sans-serif; color: #172033; background: #f6f8fb; }
    main { width: min(640px, calc(100vw - 32px)); padding: 28px; border: 1px solid #d9e0ea; border-radius: 8px; background: #fff; box-shadow: 0 20px 60px rgba(23, 32, 51, .12); }
    h1 { margin: 0 0 12px; }
    p { color: #5d6b82; line-height: 1.5; }
    code { display: block; padding: 12px; border-radius: 8px; background: #f2f5f8; overflow-wrap: anywhere; }
  </style>
</head>
<body>
  <main>
    <h1>Sitelet could not render this page</h1>
    <p>Check the target URL and try again.</p>
    <code>${escapeHtml(message)}</code>
  </main>
</body>
</html>`;
}

function escapeHtml(value: string): string {
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}
