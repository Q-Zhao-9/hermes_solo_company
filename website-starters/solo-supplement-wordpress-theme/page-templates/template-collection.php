<?php
/*
Template Name: Collection Template
*/

get_header();

$slug = solo_supplement_get_current_slug();
$collection = solo_supplement_get_collection($slug);
?>
<main class="page-wrap">
  <div class="container stack">
    <?php if (!$collection) : ?>
      <div class="page-shell">
        <h1>Collection not found</h1>
        <p>Create a page with a slug matching one of the collection keys, such as <code>multivitamins</code> or <code>magnesium</code>.</p>
      </div>
    <?php else : ?>
      <div class="page-shell">
        <h1><?php echo esc_html($collection['title']); ?></h1>
        <p><?php echo esc_html($collection['intro']); ?></p>
      </div>

      <div class="card-grid">
        <?php foreach ($collection['product_slugs'] as $product_slug) :
            $product = solo_supplement_get_product($product_slug);
            if (!$product) {
                continue;
            }
        ?>
          <article class="card">
            <span class="pill"><?php echo esc_html($product['category']); ?></span>
            <h3><?php echo esc_html($product['name']); ?></h3>
            <p><?php echo esc_html($product['short_benefit']); ?></p>
            <div class="product-price">
              <strong><?php echo esc_html($product['price']); ?></strong>
              <span><?php echo esc_html($product['cadence']); ?></span>
            </div>
            <div class="hero__actions">
              <a class="cta-link cta-link--primary" href="<?php echo esc_url(home_url('/' . $product['slug'] . '/')); ?>">View Product</a>
              <a class="cta-link cta-link--secondary" href="<?php echo solo_supplement_checkout_url($product['checkout_path']); ?>"><?php echo esc_html($product['cta_label']); ?></a>
            </div>
          </article>
        <?php endforeach; ?>
      </div>
    <?php endif; ?>
  </div>
</main>
<?php
get_footer();
