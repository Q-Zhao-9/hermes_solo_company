import { redirect } from "next/navigation";
import { requireSessionUser } from "../../lib/auth";
import { DashboardClient } from "../components/DashboardClient";

export const dynamic = "force-dynamic";

export default async function DashboardPage() {
  try {
    const user = await requireSessionUser();
    return <DashboardClient email={user.email} />;
  } catch {
    redirect("/login");
  }
}
