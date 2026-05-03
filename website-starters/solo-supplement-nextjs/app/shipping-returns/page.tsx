import { brand } from "../../lib/storefront-data";

export default function ShippingReturnsPage() {
  return (
    <main className="page-intro">
      <div className="container support-grid">
        <section className="support-card">
          <h1>Shipping</h1>
          <p>{brand.shippingPolicy}</p>
          <p>
            Use this page to explain where the product ships, how delays are handled, and
            where customers should reach out if tracking looks wrong.
          </p>
        </section>

        <section className="support-card">
          <h1>Returns</h1>
          <p>{brand.returnPolicy}</p>
          <p>
            A small supplement company should make the return process plain enough that
            support replies do not have to reinterpret policy on every ticket.
          </p>
        </section>
      </div>
    </main>
  );
}
