import { AuthError, createApiToken, listApiTokens, requireSessionUser } from "../../../lib/auth";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET(): Promise<Response> {
  try {
    const user = await requireSessionUser();
    const tokens = await listApiTokens(user.id);
    return Response.json({ ok: true, tokens });
  } catch (error) {
    return errorResponse(error, "Could not list tokens.");
  }
}

export async function POST(request: Request): Promise<Response> {
  try {
    const user = await requireSessionUser();
    const body = await request.json();
    const result = await createApiToken(user.id, String(body.name || "Hermes Agent"));
    return Response.json({ ok: true, token: result.token, record: result.record });
  } catch (error) {
    return errorResponse(error, "Could not create token.");
  }
}

function errorResponse(error: unknown, fallback: string): Response {
  const message = error instanceof Error ? error.message : fallback;
  const status = error instanceof AuthError ? error.status : 400;
  return Response.json({ ok: false, error: message }, { status });
}
