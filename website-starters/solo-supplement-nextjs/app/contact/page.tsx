import { brand } from "../../lib/storefront-data";

export default function ContactPage() {
  return (
    <main className="page-intro">
      <div className="container stack">
        <div className="page-shell">
          <h1>Contact &amp; Support</h1>
          <p>
            This page exists to lower friction, not to hide support behind forms and
            aggressive self-service flows.
          </p>
        </div>

        <div className="support-grid">
          <section className="support-card">
            <h2>Email</h2>
            <p>{brand.supportEmail}</p>
            <p>
              Replace this with the support path your solo-company workflow can actually
              maintain consistently.
            </p>
          </section>

          <section className="support-card">
            <h2>Before you write in</h2>
            <ul>
              <li>Check shipping and returns for timing and policy expectations.</li>
              <li>Use FAQ to resolve common usage and ordering questions.</li>
              <li>Keep product-effect questions within approved educational boundaries.</li>
            </ul>
          </section>
        </div>
      </div>
    </main>
  );
}
