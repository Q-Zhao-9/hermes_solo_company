export function resolvePublicOriginFromRequest(request: Request): string {
  const configured = process.env.SITELET_PUBLIC_URL?.trim();
  if (configured) {
    return configured.replace(/\/+$/, "");
  }

  const requestUrl = new URL(request.url);
  const forwardedHost = request.headers.get("x-forwarded-host");
  const forwardedProto = request.headers.get("x-forwarded-proto");
  if (forwardedHost) {
    const proto = (forwardedProto || requestUrl.protocol.replace(":", "")).split(",")[0].trim();
    const host = forwardedHost.split(",")[0].trim();
    return `${proto}://${host}`;
  }

  return requestUrl.origin;
}

export function resolvePublicOriginFromHeaders(requestHeaders: Headers): string {
  const configured = process.env.SITELET_PUBLIC_URL?.trim();
  if (configured) {
    return configured.replace(/\/+$/, "");
  }

  const host = requestHeaders.get("x-forwarded-host") || requestHeaders.get("host");
  if (!host) {
    return "https://your-sitelet-domain.example";
  }

  const proto = (requestHeaders.get("x-forwarded-proto") || "http").split(",")[0].trim();
  return `${proto}://${host.split(",")[0].trim()}`;
}
