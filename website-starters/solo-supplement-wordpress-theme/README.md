# Solo Supplement WordPress Theme Starter

WordPress theme starter that mirrors the supplement storefront structure used in the Next.js starter.

## What it includes

- home page template
- collection page template
- product page template
- FAQ template
- shipping and returns template
- contact/support template
- internal checkout shell template
- sample supplement data in `inc/storefront-data.php`

## Install

Copy this folder into your WordPress install:

```bash
wp-content/themes/solo-supplement-wordpress-theme
```

Then activate the theme in WordPress.

## Export a student zip

From the repo root:

```bash
bash scripts/export_solo_supplement_wordpress_theme.sh
```

This produces:

```bash
website-starters/dist/solo-supplement-wordpress-theme.zip
```

## Recommended Pages

Create these pages and assign templates:

- `Home` using the default front page
- `multivitamins` using `Collection Template`
- `magnesium` using `Collection Template`
- `magnesium-glycinate-200mg` using `Product Template`
- `mega-men-50-plus` using `Product Template`
- `womens-50-plus-multivitamin` using `Product Template`
- `faq` using `FAQ Template`
- `shipping-returns` using `Shipping & Returns Template`
- `contact` using `Contact Template`
- `checkout` using `Checkout Template`

Set the `Home` page as the static front page in WordPress settings.

## Internal checkout flow

Product CTAs point to:

```bash
/checkout/?product=<product-slug>
```

This is only a structural checkout shell. It does not include live payment or backend order processing.
