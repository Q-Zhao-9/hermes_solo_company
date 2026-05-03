<?php
/*
Template Name: Policy Template
*/

get_header();

$slug = solo_supplement_get_current_slug();
$policies = solo_supplement_policies();
$policy = $policies[$slug] ?? null;
$products = solo_supplement_products();
$sample_product = reset($products);
?>
<main class="page-wrap">
  <div class="container policy-grid">
    <?php if (!$policy) : ?>
      <section class="policy-card">
        <h1>Policy not found</h1>
        <p>Create a page with a slug like <code>privacy</code>, <code>terms</code>, or <code>disclaimer</code>.</p>
      </section>
    <?php else : ?>
      <section class="policy-card">
        <h1><?php echo esc_html($policy['title']); ?></h1>
        <p><?php echo esc_html($policy['summary']); ?></p>
      </section>

      <section class="policy-card">
        <h2>Starter guidance</h2>
        <p>Replace this placeholder text with the exact policy language your business, counsel, and fulfillment flow require.</p>
        <?php if ('disclaimer' === $slug && $sample_product) : ?>
          <div class="disclaimer-block">
            <strong>Current disclaimer block</strong>
            <p><?php echo esc_html($sample_product['disclaimer']); ?></p>
          </div>
        <?php endif; ?>
      </section>
    <?php endif; ?>
  </div>
</main>
<?php
get_footer();
