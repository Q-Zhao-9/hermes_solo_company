import Link from "next/link";

import { SectionHeading } from "../components/section-heading";
import {
  brand,
  featuredSignals,
  getCheckoutUrl,
  homeFaqs,
  products,
  trustBullets,
} from "../lib/storefront-data";

export default function HomePage() {
  const product = products[0];
  const checkoutUrl = getCheckoutUrl(product);

  return (
    <main>
      <section className="hero">
        <div className="container hero__grid">
          <div className="hero__panel stagger">
            <span className="hero__eyebrow">Static storefront starter</span>
            <h1>Quietly credible supplement storefronts.</h1>
            <p>{brand.promise}</p>

            <div className="hero__actions">
              {checkoutUrl ? (
                <a className="cta-link cta-link--primary" href={checkoutUrl}>
                  {product.ctaLabel}
                </a>
              ) : (
                <Link className="cta-link cta-link--primary" href={`/products/${product.slug}`}>
                  View Sample PDP
                </Link>
              )}
              <Link className="cta-link cta-link--secondary" href="/about">
                Review Site Structure
              </Link>
            </div>

            <div className="hero__metrics">
              <div className="hero__metric">
                <strong>1-3</strong>
                <span>starter products before catalog sprawl</span>
              </div>
              <div className="hero__metric">
                <strong>0</strong>
                <span>fake urgency widgets or medical hype patterns</span>
              </div>
              <div className="hero__metric">
                <strong>100%</strong>
                <span>visible support, usage, and disclaimer surfaces</span>
              </div>
            </div>
          </div>

          <div className="hero__card glass-panel stagger">
            <div className="hero__product">
              <span className="hero__product-badge">{product.category}</span>
              <h2>{product.name}</h2>
              <p>{product.shortBenefit}</p>
              <div className="product-price">
                <strong>{product.price}</strong>
                <span>{product.cadence}</span>
              </div>
              <ul>
                {trustBullets.map((bullet) => (
                  <li key={bullet}>{bullet}</li>
                ))}
              </ul>
            </div>

            <div className="hero__notes">
              <div className="hero__note">
                <strong>Trust-first architecture</strong>
                <p>
                  Home, collection, product, FAQ, shipping, support, and policy pages
                  are ready before deeper content expansion.
                </p>
              </div>
              <div className="hero__note">
                <strong>Checkout stays separate</strong>
                <p>
                  This starter is marketing-first. CTAs can point into your external
                  checkout flow now and evolve into Shopify or a deeper commerce stack later.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="section">
        <div className="container">
          <SectionHeading
            title="Built for a small, disciplined launch"
            body="The point of the first storefront is not to look gigantic. It is to explain the product clearly, reduce hesitation, and stay maintainable for a solo operator."
          />

          <div className="card-grid">
            {featuredSignals.map((signal) => (
              <article className="card stagger" key={signal.title}>
                <span className="pill">{signal.title}</span>
                <h3>{signal.title}</h3>
                <p>{signal.body}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="section">
        <div className="container">
          <SectionHeading
            title="Start with one product page that does its job"
            body="The PDP is where most trust work happens in early-stage supplement brands. This starter now uses a realistic magnesium example plus multivitamin category structure, while still treating the PDP as an education and decision page."
          />

          <div className="page-shell">
            <div className="stack">
              <div className="notice-strip">
                Includes ingredient sections, how-to-use guidance, warnings, FAQ, support path,
                and a required disclaimer block.
              </div>
              <div className="pill-row">
                <span className="pill">App Router</span>
                <span className="pill">Static export</span>
                <span className="pill">Data-driven pages</span>
                <span className="pill">Compliance-first layout</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="section">
        <div className="container">
          <SectionHeading
            title="Early questions the site should answer"
            body="A lean storefront reduces support burden when common questions are resolved by structure instead of email."
          />

          <div className="faq-list">
            {homeFaqs.map((item) => (
              <details key={item.question} className="stagger">
                <summary>{item.question}</summary>
                <p>{item.answer}</p>
              </details>
            ))}
          </div>
        </div>
      </section>
    </main>
  );
}
