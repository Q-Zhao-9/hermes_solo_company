import { clearSessionCookie } from "../../../../lib/auth";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function POST(): Promise<Response> {
  await clearSessionCookie();
  return Response.json({ ok: true });
}
