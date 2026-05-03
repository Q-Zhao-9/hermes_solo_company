import { notFound } from "next/navigation";

import { getProduct, products } from "../../../lib/storefront-data";

type CheckoutPageProps = {
  params: Promise<{ slug: string }>;
};

export async function generateStaticParams() {
  return products.map((product) => ({ slug: product.checkoutPath }));
}

export default async function CheckoutPage({ params }: CheckoutPageProps) {
  const { slug } = await params;
  const product = products.find((item) => item.checkoutPath === slug) ?? getProduct(slug);

  if (!product) {
    notFound();
  }

  return (
    <main className="page-intro">
      <div className="container stack">
        <div className="page-shell">
          <h1>Checkout</h1>
          <p>
            This is a V1 internal checkout shell inside the same codebase. It keeps the
            purchase flow local to the starter while you decide on payment and order
            infrastructure.
          </p>
        </div>

        <div className="checkout-layout">
          <section className="page-shell stack">
            <h2>Customer information</h2>
            <form className="checkout-form">
              <label>
                Full name
                <input type="text" name="name" placeholder="Jane Doe" />
              </label>
              <label>
                Email
                <input type="email" name="email" placeholder="jane@example.com" />
              </label>
              <label>
                Address line 1
                <input type="text" name="address1" placeholder="123 Main St" />
              </label>
              <label>
                Address line 2
                <input type="text" name="address2" placeholder="Apt, suite, etc." />
              </label>
              <div className="checkout-form__row">
                <label>
                  City
                  <input type="text" name="city" placeholder="Los Angeles" />
                </label>
                <label>
                  State
                  <input type="text" name="state" placeholder="CA" />
                </label>
              </div>
              <div className="checkout-form__row">
                <label>
                  ZIP
                  <input type="text" name="zip" placeholder="90001" />
                </label>
                <label>
                  Quantity
                  <input type="number" name="quantity" min="1" defaultValue="1" />
                </label>
              </div>
              <label>
                Notes
                <textarea
                  name="notes"
                  rows={4}
                  placeholder="Optional delivery or order notes"
                />
              </label>

              <div className="notice-strip">
                <strong>No live payment is connected yet.</strong>
                <p>
                  This page is a structural starter only. Replace the submit action with
                  Stripe, Shopify, WooCommerce, or your own order backend when ready.
                </p>
              </div>

              <button className="cta-link cta-link--primary checkout-submit" type="button">
                Continue to Payment Setup
              </button>
            </form>
          </section>

          <aside className="page-shell stack">
            <h2>Order summary</h2>
            <div className="checkout-summary">
              <div>
                <strong>{product.name}</strong>
                <p>{product.shortBenefit}</p>
              </div>
              <div className="product-price">
                <strong>{product.price}</strong>
                <span>{product.cadence}</span>
              </div>
            </div>

            <div className="notice-strip">
              <strong>Shipping policy</strong>
              <p>Orders ship in 1-2 business days within the continental US.</p>
            </div>

            <div className="notice-strip">
              <strong>Return policy</strong>
              <p>30-day refund window on unopened product.</p>
            </div>

            <div className="disclaimer-block">
              <strong>Required disclaimer</strong>
              <p>{product.disclaimer}</p>
            </div>
          </aside>
        </div>
      </div>
    </main>
  );
}
