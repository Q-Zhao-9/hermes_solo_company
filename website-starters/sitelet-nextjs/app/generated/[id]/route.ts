import { readGeneratedPage } from "../../../lib/generated-store";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET(
  _request: Request,
  context: { params: Promise<{ id: string }> },
): Promise<Response> {
  try {
    const { id } = await context.params;
    const record = await readGeneratedPage(id);
    return new Response(record.html, {
      headers: {
        "content-type": "text/html; charset=utf-8",
        "cache-control": "no-store",
        "x-sitelet-generated": record.id,
      },
    });
  } catch (error) {
    const message = error instanceof Error ? error.message : "Generated page not found.";
    return new Response(renderNotFound(message), {
      status: 404,
      headers: { "content-type": "text/html; charset=utf-8" },
    });
  }
}

function renderNotFound(message: string): string {
  return `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Generated page not found</title>
  <style>
    body { margin: 0; min-height: 100vh; display: grid; place-items: center; font: 16px Arial, sans-serif; color: #172033; background: #f6f8fb; }
    main { width: min(640px, calc(100vw - 32px)); padding: 28px; border: 1px solid #d9e0ea; border-radius: 8px; background: #fff; }
    code { display: block; padding: 12px; border-radius: 8px; background: #f2f5f8; overflow-wrap: anywhere; }
  </style>
</head>
<body>
  <main>
    <h1>Generated page not found</h1>
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
