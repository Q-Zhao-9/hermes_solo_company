import Link from "next/link";

import { brand } from "../lib/storefront-data";

export function SiteHeader() {
  return (
    <header className="site-header">
      <div className="container site-header__inner">
        <Link className="brand-mark" href="/">
          <span className="brand-mark__glyph">✦</span>
          <span>
            <span className="brand-mark__eyebrow">{brand.eyebrow}</span>
            <span className="brand-mark__name">{brand.name}</span>
          </span>
        </Link>

        <nav className="site-nav" aria-label="Primary">
          <Link href="/">Home</Link>
          <Link href="/collections/multivitamins">Multivitamins</Link>
          <Link href="/collections/magnesium">Magnesium</Link>
          <Link href="/faq">FAQ</Link>
          <Link href="/about">About</Link>
          <Link href="/shipping-returns">Shipping</Link>
          <Link href="/contact">Support</Link>
        </nav>
      </div>
    </header>
  );
}
