<?php

declare(strict_types=1);

function solo_supplement_brand(): array
{
    return [
        'name' => 'Northstar Well',
        'eyebrow' => 'Clean routine supplements',
        'tagline' => 'A lean WordPress starter for a compliance-first supplement storefront.',
        'promise' => 'Built for small catalogs, clear product education, trust surfaces, and a page model students can understand quickly.',
        'support_email' => 'support@northstarwell.example',
        'return_policy' => '30-day refund window on unopened product.',
        'shipping_policy' => 'Orders ship in 1-2 business days within the continental US.',
    ];
}

function solo_supplement_products(): array
{
    return [
        'magnesium-glycinate-200mg' => [
            'slug' => 'magnesium-glycinate-200mg',
            'name' => 'Magnesium Glycinate 200mg',
            'category' => 'Magnesium',
            'collection' => 'magnesium',
            'tagline' => 'A gentle daily mineral option for calm, steady routines.',
            'short_benefit' => 'Modeled after a common glycinate format: clear dose, simple usage, and straightforward routine support positioning.',
            'price' => '$29.99',
            'cadence' => '120 caplets · 60 servings',
            'description' => 'This sample PDP uses a magnesium glycinate example similar to the category and product structure used by major supplement retailers: clear serving count, direct format naming, and a simple benefit frame without aggressive claims.',
            'ingredients' => [
                'Magnesium glycinate',
                'Caplet delivery format',
                'Supportive inactive ingredients listed transparently on the label',
            ],
            'usage' => [
                'Take the labeled serving with water.',
                'Keep the routine simple and consistent.',
                'Review fit with a qualified professional if you are unsure about use alongside medication or a medical condition.',
            ],
            'warnings' => [
                'Do not use if the seal is broken.',
                'Keep out of reach of children.',
                'Consult a healthcare professional if pregnant, nursing, taking medication, or managing a medical condition.',
            ],
            'audience' => [
                'Customers shopping a straightforward mineral support product',
                'People who want a calm, low-hype supplement page',
                'Brands starting with a practical wellness catalog',
            ],
            'faqs' => [
                [
                    'question' => 'Why start with a magnesium example?',
                    'answer' => 'Magnesium glycinate is a realistic low-complexity category for a first supplement storefront because it supports a simple PDP structure and does not require a broad product matrix.',
                ],
                [
                    'question' => 'How does checkout work here?',
                    'answer' => 'The CTA routes into an internal checkout page inside the same WordPress template.',
                ],
            ],
            'cta_label' => 'Buy Magnesium',
            'checkout_path' => 'magnesium-glycinate-200mg',
            'disclaimer' => 'These statements have not been evaluated by the Food and Drug Administration. This product is not intended to diagnose, treat, cure, or prevent any disease.',
        ],
        'mega-men-50-plus' => [
            'slug' => 'mega-men-50-plus',
            'name' => 'Mega Men 50 Plus Multivitamin',
            'category' => "Men's multivitamins",
            'collection' => 'multivitamins',
            'tagline' => 'A broad daily multivitamin example for men over 50.',
            'short_benefit' => 'Structured as a category-leading multivitamin example with direct naming, serving count visibility, and broad nutrient-support positioning.',
            'price' => '$47.99',
            'cadence' => '120 caplets · 60 servings',
            'description' => 'This sample product uses the same kind of merchandising pattern seen on large supplement sites: a specific demographic target, a familiar format name, and a broad daily-support frame rather than a narrow disease claim.',
            'ingredients' => [
                'Broad-spectrum vitamin and mineral blend',
                'Two-caplet daily serving format',
                'Additional support ingredients displayed in a full label context',
            ],
            'usage' => [
                'Take the labeled serving size daily.',
                'Keep usage tied to a routine rather than one-off symptom shopping.',
                'Review the supplement facts panel and ingredient list before use.',
            ],
            'warnings' => [
                'Use only as directed on the label.',
                'Keep out of reach of children.',
                'Consult a healthcare professional before use if taking medication or managing a medical condition.',
            ],
            'audience' => [
                'Men shopping for a broad daily multivitamin format',
                'Brands that want a realistic category example with stronger comparison behavior',
                'A storefront that needs one anchor SKU and one mineral SKU',
            ],
            'faqs' => [
                [
                    'question' => 'Why include a multivitamin example?',
                    'answer' => 'Multivitamins are a strong category example because shoppers expect a comparison-style collection page and more overt demographic segmentation.',
                ],
            ],
            'cta_label' => 'Buy Mega Men 50 Plus',
            'checkout_path' => 'mega-men-50-plus',
            'disclaimer' => 'These statements have not been evaluated by the Food and Drug Administration. This product is not intended to diagnose, treat, cure, or prevent any disease.',
        ],
        'womens-50-plus-multivitamin' => [
            'slug' => 'womens-50-plus-multivitamin',
            'name' => "Women's 50 Plus Multivitamin",
            'category' => "Women's multivitamins",
            'collection' => 'multivitamins',
            'tagline' => 'A daily multivitamin example with age-targeted positioning.',
            'short_benefit' => 'Designed as a practical category companion to the men\'s product so the storefront can show a realistic multivitamin collection structure.',
            'price' => '$47.99',
            'cadence' => '120 caplets · 60 servings',
            'description' => 'This sample shows how a second multivitamin SKU can live in the same storefront without forcing a large catalog. It supports collection-page comparison while keeping the early site manageable.',
            'ingredients' => [
                'Broad-spectrum vitamin and mineral blend',
                'Timed-release style positioning where applicable',
                'Clear dietary information presented near the top of the page',
            ],
            'usage' => [
                'Take the labeled serving daily.',
                'Pair usage guidance with support and FAQ surfaces on the site.',
                'Review suitability with a qualified professional if you have questions about use.',
            ],
            'warnings' => [
                'Use only as directed on the label.',
                'Keep out of reach of children.',
                'Consult a healthcare professional before use if pregnant, nursing, taking medication, or managing a medical condition.',
            ],
            'audience' => [
                'Customers shopping an age-targeted daily multivitamin',
                'A starter storefront that needs a realistic category pair',
                'Brands testing whether category clarity matters before larger catalog expansion',
            ],
            'faqs' => [
                [
                    'question' => 'Why include both men\'s and women\'s multivitamin examples?',
                    'answer' => 'It gives the starter a realistic collection-page use case without forcing dozens of SKUs into the first site version.',
                ],
            ],
            'cta_label' => "Buy Women's 50 Plus",
            'checkout_path' => 'womens-50-plus-multivitamin',
            'disclaimer' => 'These statements have not been evaluated by the Food and Drug Administration. This product is not intended to diagnose, treat, cure, or prevent any disease.',
        ],
    ];
}

function solo_supplement_collections(): array
{
    return [
        'multivitamins' => [
            'slug' => 'multivitamins',
            'title' => 'Multivitamins',
            'intro' => 'Modeled after the kind of large retail category shoppers already understand: a demographic split, visible serving counts, and easy product comparison.',
            'product_slugs' => ['mega-men-50-plus', 'womens-50-plus-multivitamin'],
        ],
        'magnesium' => [
            'slug' => 'magnesium',
            'title' => 'Magnesium',
            'intro' => 'A smaller, focused mineral category that works well for an early supplement storefront because it is easier to explain and maintain.',
            'product_slugs' => ['magnesium-glycinate-200mg'],
        ],
    ];
}

function solo_supplement_home_faqs(): array
{
    return [
        [
            'question' => 'Why start with a magnesium product plus multivitamins?',
            'answer' => 'That combination gives the storefront a realistic category mix without creating a huge early catalog. It also creates a more believable collection-page pattern than a single isolated SKU.',
        ],
        [
            'question' => 'Why not use aggressive direct-response patterns?',
            'answer' => 'This starter assumes a compliance-first brand posture. It favors trust, clarity, and operational realism over fake urgency or exaggerated health language.',
        ],
        [
            'question' => 'How do students learn from this template?',
            'answer' => 'The theme shows a simple, maintainable page structure that can be extended in WordPress without hiding the product, policy, and disclaimer logic.',
        ],
    ];
}

function solo_supplement_policies(): array
{
    return [
        'privacy' => [
            'title' => 'Privacy',
            'summary' => 'Explain what customer data is collected, how it is used, and how support inquiries are handled.',
        ],
        'terms' => [
            'title' => 'Terms',
            'summary' => 'Set simple expectations for product information, ordering, support, and acceptable site use.',
        ],
        'disclaimer' => [
            'title' => 'Supplement Disclaimer',
            'summary' => 'State the required FDA disclaimer and explain that site content is educational and not medical advice.',
        ],
    ];
}

function solo_supplement_get_product(string $slug): ?array
{
    $products = solo_supplement_products();
    return $products[$slug] ?? null;
}

function solo_supplement_get_collection(string $slug): ?array
{
    $collections = solo_supplement_collections();
    return $collections[$slug] ?? null;
}

function solo_supplement_checkout_url(string $checkout_path): string
{
    return esc_url(home_url('/checkout/?product=' . rawurlencode($checkout_path)));
}
