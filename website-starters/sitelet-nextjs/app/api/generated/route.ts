import { saveGeneratedPage } from "../../../lib/generated-store";
import { AuthError, getSessionUser, requireBearerUser } from "../../../lib/auth";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function POST(request: Request): Promise<Response> {
  try {
    const user = await authenticateUpload(request);
    const body = await request.json();
    const record = await saveGeneratedPage({
      title: typeof body.title === "string" ? body.title : undefined,
      html: typeof body.html === "string" ? body.html : "",
      source: typeof body.source === "string" ? body.source : "api",
      userId: user?.id,
    });

    const requestUrl = new URL(request.url);
    const generatedUrl = new URL(`/generated/${record.id}`, requestUrl.origin);
    const siteletUrl = new URL("/sitelet", requestUrl.origin);
    siteletUrl.searchParams.set("url", generatedUrl.toString());

    return Response.json({
      ok: true,
      id: record.id,
      title: record.title,
      generatedUrl: generatedUrl.toString(),
      siteletUrl: siteletUrl.toString(),
      createdAt: record.createdAt,
    });
  } catch (error) {
    const message = error instanceof Error ? error.message : "Could not save generated page.";
    const status = error instanceof AuthError ? error.status : 400;
    return Response.json({ ok: false, error: message }, { status });
  }
}

async function authenticateUpload(request: Request) {
  if (request.headers.get("authorization")) {
    return requireBearerUser(request);
  }

  const sessionUser = await getSessionUser();
  if (sessionUser) {
    return sessionUser;
  }

  if (process.env.SITELET_ALLOW_ANONYMOUS_UPLOADS === "true") {
    return null;
  }

  throw new AuthError("Login or bearer token required.", 401);
}
