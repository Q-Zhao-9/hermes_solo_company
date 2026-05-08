import { createUser, setSessionCookie } from "../../../../lib/auth";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function POST(request: Request): Promise<Response> {
  try {
    const body = await request.json();
    const user = await createUser(String(body.email || ""), String(body.password || ""));
    await setSessionCookie(user.id);
    return Response.json({ ok: true, user: { id: user.id, email: user.email } });
  } catch (error) {
    const message = error instanceof Error ? error.message : "Could not create account.";
    return Response.json({ ok: false, error: message }, { status: 400 });
  }
}
