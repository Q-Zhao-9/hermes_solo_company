import { homeFaqs, products } from "../../lib/storefront-data";

export default function FaqPage() {
  const product = products[0];

  return (
    <main className="page-intro">
      <div className="container stack">
        <div className="page-shell">
          <h1>FAQ</h1>
          <p>
            This page combines site-level questions with product-level questions so a
            small team can reduce repetitive support work before adding more SKUs.
          </p>
        </div>

        <div className="faq-list">
          {homeFaqs.concat(product.faqs).map((item) => (
            <details key={item.question}>
              <summary>{item.question}</summary>
              <p>{item.answer}</p>
            </details>
          ))}
        </div>
      </div>
    </main>
  );
}
