import { redirect } from "next/navigation";
import { headers } from "next/headers";
import { requireSessionUser } from "../../lib/auth";
import { DashboardClient } from "../components/DashboardClient";
import { resolvePublicOriginFromHeaders } from "../../lib/public-url";

export const dynamic = "force-dynamic";

export default async function DashboardPage() {
  try {
    const user = await requireSessionUser();
    const requestHeaders = await headers();
    return (
      <DashboardClient
        email={user.email}
        siteletBaseUrl={resolvePublicOriginFromHeaders(requestHeaders)}
        configuredApiToken={process.env.SITELET_API_TOKEN?.trim() || ""}
      />
    );
  } catch {
    redirect("/login");
  }
}
