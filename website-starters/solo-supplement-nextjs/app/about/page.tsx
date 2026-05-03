import { brand } from "../../lib/storefront-data";

export default function AboutPage() {
  return (
    <main className="page-intro">
      <div className="container page-shell stack">
        <h1>About the starter</h1>
        <p>
          {brand.name} is a sample brand used to show how a supplement storefront can
          launch with restraint: a small product set, visible support information, and
          page structures that map back to product and compliance artifacts.
        </p>
        <p>
          This page is deliberately simple. In a real build, the About page should explain
          why the brand exists, what product philosophy it follows, and how customers can
          reach support without burying those answers in conversion fluff.
        </p>
      </div>
    </main>
  );
}
