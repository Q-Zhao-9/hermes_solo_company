import Link from "next/link";
import { AuthForm } from "../components/AuthForm";
import { getSessionUser } from "../../lib/auth";
import { redirect } from "next/navigation";

export const dynamic = "force-dynamic";

export default async function RegisterPage() {
  const user = await getSessionUser();
  if (user) {
    redirect("/dashboard");
  }

  return (
    <main className="auth-page">
      <section className="auth-panel">
        <p className="eyebrow">Sitelet Cloud</p>
        <h1>Create account</h1>
        <p className="lede">
          Create an account, generate a Hermes token, and deploy this Sitelet
          server anywhere that can run Next.js.
        </p>
        <AuthForm mode="register" />
        <p className="auth-switch">
          Already have an account? <Link href="/login">Sign in</Link>
        </p>
      </section>
    </main>
  );
}
