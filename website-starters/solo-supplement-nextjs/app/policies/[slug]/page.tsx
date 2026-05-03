import { notFound } from "next/navigation";

import { policies, products } from "../../../lib/storefront-data";

type PolicyPageProps = {
  params: Promise<{ slug: string }>;
};

export async function generateStaticParams() {
  return policies.map((policy) => ({ slug: policy.slug }));
}

export default async function PolicyPage({ params }: PolicyPageProps) {
  const { slug } = await params;
  const policy = policies.find((item) => item.slug === slug);

  if (!policy) {
    notFound();
  }

  const disclaimer = products[0].disclaimer;

  return (
    <main className="page-intro">
      <div className="container policy-grid">
        <section className="policy-card">
          <h1>{policy.title}</h1>
          <p>{policy.summary}</p>
        </section>
        <section className="policy-card">
          <h2>Starter guidance</h2>
          <p>
            Replace this placeholder text with the exact policy language your business,
            counsel, and fulfillment flow require. The important part is that the page
            exists clearly in navigation from the beginning.
          </p>
          {slug === "disclaimer" ? (
            <div className="disclaimer-block">
              <strong>Current disclaimer block</strong>
              <p>{disclaimer}</p>
            </div>
          ) : null}
        </section>
      </div>
    </main>
  );
}
