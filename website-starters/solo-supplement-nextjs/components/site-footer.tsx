import Link from "next/link";

import { brand, policies } from "../lib/storefront-data";

export function SiteFooter() {
  return (
    <footer className="site-footer">
      <div className="container">
        <div className="site-footer__panel">
          <div className="site-footer__grid">
            <div>
              <strong>{brand.name}</strong>
              <p>{brand.tagline}</p>
              <p>{brand.shippingPolicy}</p>
            </div>
            <div>
              <strong>Support</strong>
              <p>
                <Link href="/contact">{brand.supportEmail}</Link>
              </p>
              <p>
                <Link href="/shipping-returns">Shipping &amp; Returns</Link>
              </p>
            </div>
            <div>
              <strong>Policies</strong>
              {policies.map((policy) => (
                <p key={policy.slug}>
                  <Link href={`/policies/${policy.slug}`}>{policy.title}</Link>
                </p>
              ))}
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}
