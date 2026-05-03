import { notFound } from "next/navigation";
import Link from "next/link";

import {
  getCheckoutUrl,
  getCollection,
  getProduct,
  collections,
} from "../../../lib/storefront-data";

type CollectionPageProps = {
  params: Promise<{ slug: string }>;
};

export async function generateStaticParams() {
  return collections.map((collection) => ({ slug: collection.slug }));
}

export default async function CollectionPage({ params }: CollectionPageProps) {
  const { slug } = await params;
  const collection = getCollection(slug);

  if (!collection) {
    notFound();
  }

  const collectionProducts = collection.productSlugs
    .map((productSlug) => getProduct(productSlug))
    .filter(Boolean);

  return (
    <main className="page-intro">
      <div className="container stack">
        <div className="page-shell">
          <h1>{collection.title}</h1>
          <p>{collection.intro}</p>
        </div>

        <div className="card-grid">
          {collectionProducts.map((product) => (
            <article className="card" key={product!.slug}>
              <span className="pill">{product!.category}</span>
              <h3>{product!.name}</h3>
              <p>{product!.shortBenefit}</p>
              <div className="product-price">
                <strong>{product!.price}</strong>
                <span>{product!.cadence}</span>
              </div>
              <div className="hero__actions">
                <Link className="cta-link cta-link--primary" href={`/products/${product!.slug}`}>
                  View Product
                </Link>
                {getCheckoutUrl(product!) ? (
                  <a className="cta-link cta-link--secondary" href={getCheckoutUrl(product!)}>
                    {product!.ctaLabel}
                  </a>
                ) : null}
              </div>
            </article>
          ))}
        </div>
      </div>
    </main>
  );
}
