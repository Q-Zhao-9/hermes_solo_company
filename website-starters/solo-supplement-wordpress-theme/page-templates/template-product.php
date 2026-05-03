<?php
/*
Template Name: Product Template
*/

get_header();

$slug = solo_supplement_get_current_slug();
$product = solo_supplement_get_product($slug);
?>
<main class="page-wrap">
  <div class="container stack">
    <?php if (!$product) : ?>
      <div class="page-shell">
        <h1>Product not found</h1>
        <p>Create a page with a slug matching one of the sample product keys.</p>
      </div>
    <?php else : ?>
      <div class="product-layout">
        <section class="product-tile">
          <span class="hero__product-badge"><?php echo esc_html($product['category']); ?></span>
          <h1><?php echo esc_html($product['name']); ?></h1>
          <p><?php echo esc_html($product['tagline']); ?></p>
          <div class="product-price">
            <strong><?php echo esc_html($product['price']); ?></strong>
            <span><?php echo esc_html($product['cadence']); ?></span>
          </div>
          <div class="hero__actions">
            <a class="cta-link cta-link--primary" href="<?php echo solo_supplement_checkout_url($product['checkout_path']); ?>"><?php echo esc_html($product['cta_label']); ?></a>
          </div>
          <div class="pill-row">
            <span class="pill">Usage guidance visible</span>
            <span class="pill">Warnings visible</span>
            <span class="pill">Disclaimer included</span>
          </div>
        </section>

        <section class="page-shell">
          <h2>What it is</h2>
          <p><?php echo esc_html($product['description']); ?></p>
          <div class="notice-strip">
            <strong><?php echo esc_html($product['short_benefit']); ?></strong>
          </div>

          <h3>Who it is for</h3>
          <ul>
            <?php foreach ($product['audience'] as $item) : ?>
              <li><?php echo esc_html($item); ?></li>
            <?php endforeach; ?>
          </ul>
        </section>
      </div>

      <div class="card-grid">
        <article class="card">
          <h3>Ingredients</h3>
          <ul>
            <?php foreach ($product['ingredients'] as $item) : ?>
              <li><?php echo esc_html($item); ?></li>
            <?php endforeach; ?>
          </ul>
        </article>
        <article class="card">
          <h3>How to use</h3>
          <ul>
            <?php foreach ($product['usage'] as $item) : ?>
              <li><?php echo esc_html($item); ?></li>
            <?php endforeach; ?>
          </ul>
        </article>
        <article class="card">
          <h3>Warnings</h3>
          <ul>
            <?php foreach ($product['warnings'] as $item) : ?>
              <li><?php echo esc_html($item); ?></li>
            <?php endforeach; ?>
          </ul>
        </article>
      </div>

      <section class="page-shell">
        <h2>Product FAQ</h2>
        <div class="faq-list">
          <?php foreach ($product['faqs'] as $faq) : ?>
            <details>
              <summary><?php echo esc_html($faq['question']); ?></summary>
              <p><?php echo esc_html($faq['answer']); ?></p>
            </details>
          <?php endforeach; ?>
        </div>
      </section>

      <section class="disclaimer-block">
        <strong>Required disclaimer</strong>
        <p><?php echo esc_html($product['disclaimer']); ?></p>
      </section>
    <?php endif; ?>
  </div>
</main>
<?php
get_footer();
