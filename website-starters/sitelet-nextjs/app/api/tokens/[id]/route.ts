import { AuthError, requireSessionUser, revokeApiToken } from "../../../../lib/auth";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function DELETE(
  _request: Request,
  context: { params: Promise<{ id: string }> },
): Promise<Response> {
  try {
    const user = await requireSessionUser();
    const { id } = await context.params;
    await revokeApiToken(user.id, id);
    return Response.json({ ok: true });
  } catch (error) {
    const message = error instanceof Error ? error.message : "Could not revoke token.";
    const status = error instanceof AuthError ? error.status : 400;
    return Response.json({ ok: false, error: message }, { status });
  }
}
