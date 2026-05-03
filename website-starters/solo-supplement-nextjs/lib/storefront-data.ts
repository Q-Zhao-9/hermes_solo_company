export type Product = {
  slug: string;
  name: string;
  category: string;
  collection: string;
  tagline: string;
  shortBenefit: string;
  price: string;
  cadence: string;
  description: string;
  ingredients: string[];
  usage: string[];
  warnings: string[];
  audience: string[];
  faqs: Array<{ question: string; answer: string }>;
  ctaLabel: string;
  checkoutPath: string;
  disclaimer: string;
};

export const brand = {
  name: "Northstar Well",
  eyebrow: "Clean routine supplements",
  tagline: "A lean static storefront starter for a compliance-first supplement brand.",
  promise:
    "Built for small catalogs, clear product education, and trust surfaces that a solo operator can maintain.",
  supportEmail: "support@northstarwell.example",
  returnPolicy: "30-day refund window on unopened product.",
  shippingPolicy: "Orders ship in 1-2 business days within the continental US.",
};

export const products: Product[] = [
  {
    slug: "magnesium-glycinate-200mg",
    name: "Magnesium Glycinate 200mg",
    category: "Magnesium",
    collection: "magnesium",
    tagline: "A gentle daily mineral option for calm, steady routines.",
    shortBenefit:
      "Modeled after a common glycinate format: clear dose, simple usage, and straightforward routine support positioning.",
    price: "$29.99",
    cadence: "120 caplets · 60 servings",
    description:
      "This sample PDP uses a magnesium glycinate example similar to the category and product structure used by major supplement retailers: clear serving count, direct format naming, and a simple benefit frame without aggressive claims.",
    ingredients: [
      "Magnesium glycinate",
      "Caplet delivery format",
      "Supportive inactive ingredients listed transparently on the label",
    ],
    usage: [
      "Take the labeled serving with water.",
      "Keep the routine simple and consistent.",
      "Review fit with a qualified professional if you are unsure about use alongside medication or a medical condition.",
    ],
    warnings: [
      "Do not use if the seal is broken.",
      "Keep out of reach of children.",
      "Consult a healthcare professional if pregnant, nursing, taking medication, or managing a medical condition.",
    ],
    audience: [
      "Customers shopping a straightforward mineral support product",
      "People who want a calm, low-hype supplement page",
      "Brands starting with a practical wellness catalog",
    ],
    faqs: [
      {
        question: "Why start with a magnesium example?",
        answer:
          "Magnesium glycinate is a realistic low-complexity category for a first supplement storefront because it supports a simple PDP structure and does not require a broad product matrix.",
      },
      {
        question: "Why keep the copy conservative?",
        answer:
          "This starter is designed around compliance-first supplement merchandising, so the product page emphasizes routine fit, usage clarity, and warning visibility instead of exaggerated outcomes.",
      },
      {
        question: "How does checkout work here?",
        answer:
          "The CTA now routes into an internal checkout page in this same Next.js starter, so the storefront can keep the purchase flow in one codebase.",
      },
    ],
    ctaLabel: "Buy Magnesium",
    checkoutPath: "magnesium-glycinate-200mg",
    disclaimer:
      "These statements have not been evaluated by the Food and Drug Administration. This product is not intended to diagnose, treat, cure, or prevent any disease.",
  },
  {
    slug: "mega-men-50-plus",
    name: "Mega Men 50 Plus Multivitamin",
    category: "Men's multivitamins",
    collection: "multivitamins",
    tagline: "A broad daily multivitamin example for men over 50.",
    shortBenefit:
      "Structured as a category-leading multivitamin example with direct naming, serving count visibility, and broad nutrient-support positioning.",
    price: "$47.99",
    cadence: "120 caplets · 60 servings",
    description:
      "This sample product uses the same kind of merchandising pattern seen on large supplement sites: a specific demographic target, a familiar format name, and a broad daily-support frame rather than a narrow disease claim.",
    ingredients: [
      "Broad-spectrum vitamin and mineral blend",
      "Two-caplet daily serving format",
      "Additional support ingredients displayed in a full label context",
    ],
    usage: [
      "Take the labeled serving size daily.",
      "Keep usage tied to a routine rather than one-off symptom shopping.",
      "Review the supplement facts panel and ingredient list before use.",
    ],
    warnings: [
      "Use only as directed on the label.",
      "Keep out of reach of children.",
      "Consult a healthcare professional before use if taking medication or managing a medical condition.",
    ],
    audience: [
      "Men shopping for a broad daily multivitamin format",
      "Brands that want a realistic category example with stronger comparison behavior",
      "A storefront that needs one anchor SKU and one mineral SKU",
    ],
    faqs: [
      {
        question: "Why include a multivitamin example?",
        answer:
          "Multivitamins are a strong category example because shoppers expect a comparison-style collection page and more overt demographic segmentation.",
      },
      {
        question: "Why not copy retailer claims exactly?",
        answer:
          "The goal here is to borrow category and PDP structure, not duplicate copyrighted marketing copy or overstate product effects.",
      },
    ],
    ctaLabel: "Buy Mega Men 50 Plus",
    checkoutPath: "mega-men-50-plus",
    disclaimer:
      "These statements have not been evaluated by the Food and Drug Administration. This product is not intended to diagnose, treat, cure, or prevent any disease.",
  },
  {
    slug: "womens-50-plus-multivitamin",
    name: "Women's 50 Plus Multivitamin",
    category: "Women's multivitamins",
    collection: "multivitamins",
    tagline: "A daily multivitamin example with age-targeted positioning.",
    shortBenefit:
      "Designed as a practical category companion to the men's product so the storefront can show a realistic multivitamin collection structure.",
    price: "$47.99",
    cadence: "120 caplets · 60 servings",
    description:
      "This sample shows how a second multivitamin SKU can live in the same storefront without forcing a large catalog. It supports collection-page comparison while keeping the early site manageable.",
    ingredients: [
      "Broad-spectrum vitamin and mineral blend",
      "Timed-release style positioning where applicable",
      "Clear dietary information presented near the top of the page",
    ],
    usage: [
      "Take the labeled serving daily.",
      "Pair usage guidance with support and FAQ surfaces on the site.",
      "Review suitability with a qualified professional if you have questions about use.",
    ],
    warnings: [
      "Use only as directed on the label.",
      "Keep out of reach of children.",
      "Consult a healthcare professional before use if pregnant, nursing, taking medication, or managing a medical condition.",
    ],
    audience: [
      "Customers shopping an age-targeted daily multivitamin",
      "A starter storefront that needs a realistic category pair",
      "Brands testing whether category clarity matters before larger catalog expansion",
    ],
    faqs: [
      {
        question: "Why include both men's and women's multivitamin examples?",
        answer:
          "It gives the starter a realistic collection-page use case without forcing dozens of SKUs into the first site version.",
      },
      {
        question: "Can these be replaced with your own formulas later?",
        answer:
          "Yes. The page structure is data-driven so products can be swapped without changing the overall storefront architecture.",
      },
    ],
    ctaLabel: "Buy Women's 50 Plus",
    checkoutPath: "womens-50-plus-multivitamin",
    disclaimer:
      "These statements have not been evaluated by the Food and Drug Administration. This product is not intended to diagnose, treat, cure, or prevent any disease.",
  },
];

export const featuredSignals = [
  {
    title: "GNC-style category realism",
    body: "The starter now uses a realistic mix of one mineral category and one multivitamin category so the site behaves more like an actual supplement storefront.",
  },
  {
    title: "Static by default",
    body: "A solo operator can ship a trustworthy site faster when the first version avoids unnecessary backend complexity.",
  },
  {
    title: "Checkout-ready CTA wiring",
    body: "Product CTAs now point into an internal checkout route so the storefront can grow into a full in-repo commerce flow later.",
  },
];

export const trustBullets = [
  "Plain-language ingredient and usage sections",
  "Support and policy pages linked from every major view",
  "Required disclaimer block included on product pages",
];

export const homeFaqs = [
  {
    question: "Why start with a magnesium product plus multivitamins?",
    answer:
      "That combination gives the storefront a realistic category mix without creating a huge early catalog. It also creates a more believable collection-page pattern than a single isolated SKU.",
  },
  {
    question: "Why not use aggressive direct-response patterns?",
    answer:
      "This starter assumes a compliance-first brand posture. It favors trust, clarity, and operational realism over fake urgency or exaggerated health language.",
  },
  {
    question: "How do I connect the CTA to my actual checkout?",
    answer:
      "The starter now uses an internal checkout route. If you later move to an external checkout provider, you can swap those links out without changing the storefront structure.",
  },
];

export const policies = [
  {
    slug: "privacy",
    title: "Privacy",
    summary:
      "Explain what customer data is collected, how it is used, and how support inquiries are handled.",
  },
  {
    slug: "terms",
    title: "Terms",
    summary:
      "Set simple expectations for product information, ordering, support, and acceptable site use.",
  },
  {
    slug: "disclaimer",
    title: "Supplement Disclaimer",
    summary:
      "State the required FDA disclaimer and explain that site content is educational and not medical advice.",
  },
];

export const collections = [
  {
    slug: "multivitamins",
    title: "Multivitamins",
    intro:
      "Modeled after the kind of large retail category shoppers already understand: a demographic split, visible serving counts, and easy product comparison.",
    productSlugs: ["mega-men-50-plus", "womens-50-plus-multivitamin"],
  },
  {
    slug: "magnesium",
    title: "Magnesium",
    intro:
      "A smaller, focused mineral category that works well for an early supplement storefront because it is easier to explain and maintain.",
    productSlugs: ["magnesium-glycinate-200mg"],
  },
];

export function getProduct(slug: string) {
  return products.find((product) => product.slug === slug);
}

export function getCollection(slug: string) {
  return collections.find((collection) => collection.slug === slug);
}

export function getCheckoutUrl(product: Product) {
  const checkoutPath = product.checkoutPath.replace(/^\/+/, "");
  return `/checkout/${checkoutPath}`;
}
