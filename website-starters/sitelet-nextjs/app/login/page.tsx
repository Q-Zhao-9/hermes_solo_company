import Link from "next/link";
import { AuthForm } from "../components/AuthForm";
import { getSessionUser } from "../../lib/auth";
import { redirect } from "next/navigation";

export const dynamic = "force-dynamic";

export default async function LoginPage() {
  const user = await getSessionUser();
  if (user) {
    redirect("/dashboard");
  }

  return (
    <main className="auth-page">
      <section className="auth-panel">
        <p className="eyebrow">Sitelet Cloud</p>
        <h1>Sign in</h1>
        <p className="lede">
          Manage the API token Hermes uses to upload generated pages and return
          preview URLs to Discord or another chat gateway.
        </p>
        <AuthForm mode="login" />
        <p className="auth-switch">
          Need an account? <Link href="/register">Create one</Link>
        </p>
      </section>
    </main>
  );
}
