<?php
/*
Template Name: Shipping & Returns Template
*/

get_header();
$brand = solo_supplement_brand();
?>
<main class="page-wrap">
  <div class="container support-grid">
    <section class="support-card">
      <h1>Shipping</h1>
      <p><?php echo esc_html($brand['shipping_policy']); ?></p>
      <p>Use this page to explain where product ships, how delays are handled, and what customers should do when tracking looks wrong.</p>
    </section>

    <section class="support-card">
      <h1>Returns</h1>
      <p><?php echo esc_html($brand['return_policy']); ?></p>
      <p>A small supplement company should make the return process plain enough that support replies do not have to reinterpret policy on every ticket.</p>
    </section>
  </div>
</main>
<?php
get_footer();
