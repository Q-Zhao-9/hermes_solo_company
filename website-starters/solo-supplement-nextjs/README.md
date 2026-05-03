# Solo Supplement Next.js Starter

Static storefront starter for the solo-supplement-commerce skill family.

## What it includes

- App Router Next.js starter
- static export configuration
- sample home, collection, product, FAQ, support, shipping, and policy pages
- structured product data in `lib/storefront-data.ts`
- visible disclaimer and trust surfaces

## Run it

```bash
bash scripts/run_solo_supplement_storefront.sh
```

Or on a custom port:

```bash
PORT=3001 bash scripts/run_solo_supplement_storefront.sh
```

The launcher syncs the app into:

```bash
/tmp/solo-supplement-nextjs-runtime
```

before installing dependencies and starting Next.js. This avoids npm/Next.js issues on the mounted repo filesystem.

## Internal checkout flow

Product CTAs now point to internal routes like:

```bash
/checkout/magnesium-glycinate-200mg
```

This V1 checkout is a structural shell only. It includes customer fields and an order
summary, but no live payment integration yet.

## Build static output

```bash
cd website-starters/solo-supplement-nextjs
npm install
npm run build
```

This starter is intentionally marketing-first. It includes a local checkout shell, but it does not include live payment, subscriptions, or backend order processing.
