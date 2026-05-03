import { notFound } from "next/navigation";
import Link from "next/link";

import { getCheckoutUrl, getProduct, products } from "../../../lib/storefront-data";

type ProductPageProps = {
  params: Promise<{ slug: string }>;
};

export async function generateStaticParams() {
  return products.map((product) => ({ slug: product.slug }));
}

export default async function ProductPage({ params }: ProductPageProps) {
  const { slug } = await params;
  const product = getProduct(slug);

  if (!product) {
    notFound();
  }

  const checkoutUrl = getCheckoutUrl(product);

  return (
    <main className="page-intro">
      <div className="container stack">
        <div className="product-layout">
          <section className="product-tile">
            <span className="hero__product-badge">{product.category}</span>
            <h1>{product.name}</h1>
            <p>{product.tagline}</p>
            <div className="product-price">
              <strong>{product.price}</strong>
              <span>{product.cadence}</span>
            </div>
            <div className="hero__actions">
              {checkoutUrl ? (
                <a className="cta-link cta-link--primary" href={checkoutUrl}>
                  {product.ctaLabel}
                </a>
              ) : (
                <Link className="cta-link cta-link--primary" href="/contact">
                  Add Checkout URL
                </Link>
              )}
            </div>
            <div className="pill-row">
              <span className="pill">Usage guidance visible</span>
              <span className="pill">Warnings visible</span>
              <span className="pill">Disclaimer included</span>
            </div>
          </section>

          <section className="product-info">
            <article className="page-shell">
              <h2>What it is</h2>
              <p>{product.description}</p>
              <div className="notice-strip">
                <strong>{product.shortBenefit}</strong>
              </div>
            </article>

            <article className="page-shell">
              <h2>Who it is for</h2>
              <ul>
                {product.audience.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </article>
          </section>
        </div>

        <div className="card-grid">
          <article className="card">
            <h3>Ingredients</h3>
            <ul>
              {product.ingredients.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </article>
          <article className="card">
            <h3>How to use</h3>
            <ul>
              {product.usage.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </article>
          <article className="card">
            <h3>Warnings</h3>
            <ul>
              {product.warnings.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </article>
        </div>

        <section className="page-shell stack">
          <h2>Product FAQ</h2>
          <div className="faq-list">
            {product.faqs.map((item) => (
              <details key={item.question}>
                <summary>{item.question}</summary>
                <p>{item.answer}</p>
              </details>
            ))}
          </div>
        </section>

        <section className="disclaimer-block">
          <strong>Required disclaimer</strong>
          <p>{product.disclaimer}</p>
        </section>
      </div>
    </main>
  );
}
