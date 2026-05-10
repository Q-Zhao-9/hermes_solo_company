import { requireSessionUser } from "../../../../lib/auth";
import { listGeneratedPages } from "../../../../lib/generated-store";
import { resolvePublicOriginFromRequest } from "../../../../lib/public-url";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET(request: Request): Promise<Response> {
  try {
    const user = await requireSessionUser();
    const publicOrigin = resolvePublicOriginFromRequest(request);
    const records = await listGeneratedPages(user.id);

    return Response.json({
      ok: true,
      pages: records.map((record) => {
        const generatedUrl = new URL(`/generated/${record.id}`, publicOrigin);
        const siteletUrl = new URL("/sitelet", publicOrigin);
        siteletUrl.searchParams.set("url", generatedUrl.toString());
        return {
          id: record.id,
          title: record.title,
          source: record.source,
          createdAt: record.createdAt,
          generatedUrl: generatedUrl.toString(),
          siteletUrl: siteletUrl.toString(),
          storageFile: record.storageFile,
          htmlBytes: record.htmlBytes,
        };
      }),
    });
  } catch (error) {
    const message = error instanceof Error ? error.message : "Could not load generated page history.";
    return Response.json({ ok: false, error: message }, { status: 401 });
  }
}
