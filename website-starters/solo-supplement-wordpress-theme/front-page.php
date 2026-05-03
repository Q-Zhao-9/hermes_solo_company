<?php
get_header();

$brand = solo_supplement_brand();
$products = array_values(solo_supplement_products());
$featured_product = $products[0];
$faqs = solo_supplement_home_faqs();
?>
<main>
  <section class="hero">
    <div class="container hero__grid">
      <div class="hero__panel">
        <span class="hero__eyebrow">WordPress storefront starter</span>
        <h1>Quietly credible supplement storefronts.</h1>
        <p><?php echo esc_html($brand['promise']); ?></p>

        <div class="hero__actions">
          <a class="cta-link cta-link--primary" href="<?php echo esc_url(home_url('/' . $featured_product['slug'] . '/')); ?>">View Sample PDP</a>
          <a class="cta-link cta-link--secondary" href="<?php echo esc_url(home_url('/multivitamins/')); ?>">Browse Categories</a>
        </div>

        <div class="hero__metrics">
          <div class="hero__metric">
            <strong>2</strong>
            <span>starter categories with realistic supplement structure</span>
          </div>
          <div class="hero__metric">
            <strong>0</strong>
            <span>fake urgency widgets or medical hype patterns</span>
          </div>
          <div class="hero__metric">
            <strong>100%</strong>
            <span>visible support, usage, and disclaimer surfaces</span>
          </div>
        </div>
      </div>

      <div class="glass-panel hero__panel">
        <div class="hero__product">
          <span class="hero__product-badge"><?php echo esc_html($featured_product['category']); ?></span>
          <h2><?php echo esc_html($featured_product['name']); ?></h2>
          <p><?php echo esc_html($featured_product['short_benefit']); ?></p>
          <div class="product-price">
            <strong><?php echo esc_html($featured_product['price']); ?></strong>
            <span><?php echo esc_html($featured_product['cadence']); ?></span>
          </div>
          <div class="pill-row">
            <span class="pill">WordPress theme</span>
            <span class="pill">Student-ready</span>
            <span class="pill">Internal checkout shell</span>
          </div>
        </div>
      </div>
    </div>
  </section>

  <section class="section">
    <div class="container">
      <div class="section-heading">
        <h2>Start with realistic supplement structure</h2>
        <p>Use a magnesium product plus a multivitamin collection so students can learn category pages, product pages, trust surfaces, and checkout shell structure in one template.</p>
      </div>

      <div class="card-grid">
        <?php foreach ($products as $product) : ?>
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
    </div>
  </section>

  <section class="section">
    <div class="container">
      <div class="section-heading">
        <h2>Early questions the site should answer</h2>
        <p>A lean storefront reduces support burden when common questions are resolved by page structure instead of one-off email replies.</p>
      </div>

      <div class="faq-list">
        <?php foreach ($faqs as $faq) : ?>
          <details>
            <summary><?php echo esc_html($faq['question']); ?></summary>
            <p><?php echo esc_html($faq['answer']); ?></p>
          </details>
        <?php endforeach; ?>
      </div>
    </div>
  </section>
</main>
<?php
get_footer();
