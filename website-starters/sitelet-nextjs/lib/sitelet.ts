const REWRITABLE_ATTRS = ["href", "src", "action", "poster"] as const;

export function normalizeTargetUrl(value: string | null): URL {
  if (!value) {
    throw new Error("Missing required url parameter.");
  }

  const url = new URL(value);
  if (!["http:", "https:"].includes(url.protocol)) {
    throw new Error("Only http and https URLs can be previewed.");
  }
  return url;
}

export function rewriteHtml(html: string, targetUrl: URL, requestUrl: URL): string {
  let rewritten = html;

  rewritten = removeFrameBlockingMeta(rewritten);
  rewritten = rewriteBaseTag(rewritten, targetUrl);

  for (const attr of REWRITABLE_ATTRS) {
    rewritten = rewriteAttribute(rewritten, attr, targetUrl, requestUrl);
  }

  rewritten = rewriteSrcset(rewritten, targetUrl, requestUrl);
  rewritten = rewriteInlineUrls(rewritten, targetUrl, requestUrl);
  rewritten = injectToolbar(rewritten, targetUrl);
  return rewritten;
}

export function proxyUrlFor(target: URL, requestUrl: URL): string {
  const proxied = new URL("/sitelet", requestUrl.origin);
  proxied.searchParams.set("url", target.toString());
  return proxied.pathname + proxied.search;
}

export function upstreamHeaders(request: Request, targetUrl: URL): Headers {
  const headers = new Headers();
  const allowed = [
    "accept",
    "accept-language",
    "content-type",
    "cookie",
    "user-agent",
  ];

  for (const key of allowed) {
    const value = request.headers.get(key);
    if (value) {
      headers.set(key, value);
    }
  }

  return headers;
}

export function responseHeaders(upstream: Response, contentType: string): Headers {
  const headers = new Headers();
  const passthrough = [
    "cache-control",
    "content-language",
    "content-type",
    "expires",
    "last-modified",
  ];

  for (const key of passthrough) {
    const value = upstream.headers.get(key);
    if (value) {
      headers.set(key, value);
    }
  }

  headers.set("content-type", contentType);
  headers.set("x-sitelet-proxy", "1");
  headers.delete("content-security-policy");
  headers.delete("x-frame-options");
  return headers;
}

function rewriteAttribute(html: string, attr: string, targetUrl: URL, requestUrl: URL): string {
  const pattern = new RegExp(`\\s${attr}=([\"'])(.*?)\\1`, "gi");
  return html.replace(pattern, (match, quote: string, rawValue: string) => {
    const rewritten = rewriteUrlValue(rawValue, targetUrl, requestUrl);
    return ` ${attr}=${quote}${escapeAttribute(rewritten)}${quote}`;
  });
}

function rewriteSrcset(html: string, targetUrl: URL, requestUrl: URL): string {
  return html.replace(/\ssrcset=(["'])(.*?)\1/gi, (_match, quote: string, rawValue: string) => {
    const rewritten = rawValue
      .split(",")
      .map((part) => {
        const trimmed = part.trim();
        if (!trimmed) {
          return trimmed;
        }
        const [urlPart, ...descriptor] = trimmed.split(/\s+/);
        return [rewriteUrlValue(urlPart, targetUrl, requestUrl), ...descriptor].join(" ");
      })
      .join(", ");
    return ` srcset=${quote}${escapeAttribute(rewritten)}${quote}`;
  });
}

function rewriteInlineUrls(html: string, targetUrl: URL, requestUrl: URL): string {
  return html.replace(/url\((["']?)(.*?)\1\)/gi, (_match, quote: string, rawValue: string) => {
    return `url(${quote}${rewriteUrlValue(rawValue, targetUrl, requestUrl)}${quote})`;
  });
}

function rewriteUrlValue(rawValue: string, targetUrl: URL, requestUrl: URL): string {
  const value = rawValue.trim();
  if (
    value === "" ||
    value.startsWith("#") ||
    value.startsWith("mailto:") ||
    value.startsWith("tel:") ||
    value.startsWith("data:") ||
    value.startsWith("javascript:")
  ) {
    return rawValue;
  }

  try {
    const absolute = new URL(value, targetUrl);
    if (!["http:", "https:"].includes(absolute.protocol)) {
      return rawValue;
    }
    return proxyUrlFor(absolute, requestUrl);
  } catch {
    return rawValue;
  }
}

function rewriteBaseTag(html: string, targetUrl: URL): string {
  const baseTag = `<base href="${escapeAttribute(targetUrl.origin + "/")}">`;
  if (/<base\s/i.test(html)) {
    return html.replace(/<base\b[^>]*>/i, baseTag);
  }
  return html.replace(/<head(\s[^>]*)?>/i, (match) => `${match}\n${baseTag}`);
}

function removeFrameBlockingMeta(html: string): string {
  return html.replace(
    /<meta[^>]+http-equiv=(["'])content-security-policy\1[^>]*>/gi,
    "",
  );
}

function injectToolbar(html: string, targetUrl: URL): string {
  const toolbar = `
<div style="position:fixed;left:12px;bottom:12px;z-index:2147483647;background:#10211f;color:#fff;border:1px solid rgba(255,255,255,.18);border-radius:8px;padding:9px 11px;font:12px Arial,sans-serif;box-shadow:0 12px 34px rgba(0,0,0,.22);max-width:min(520px,calc(100vw - 24px));">
  <strong style="display:inline-block;margin-right:6px;">Sitelet</strong>
  <span style="opacity:.78;overflow-wrap:anywhere;">${escapeHtml(targetUrl.toString())}</span>
</div>`;

  if (/<body(\s[^>]*)?>/i.test(html)) {
    return html.replace(/<body(\s[^>]*)?>/i, (match) => `${match}\n${toolbar}`);
  }
  return `${toolbar}\n${html}`;
}

function escapeAttribute(value: string): string {
  return value.replace(/&/g, "&amp;").replace(/"/g, "&quot;");
}

function escapeHtml(value: string): string {
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}
