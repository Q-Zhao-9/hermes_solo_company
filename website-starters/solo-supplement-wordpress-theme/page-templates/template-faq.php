<?php
/*
Template Name: FAQ Template
*/

get_header();
$faqs = solo_supplement_home_faqs();
?>
<main class="page-wrap">
  <div class="container stack">
    <div class="page-shell">
      <h1>FAQ</h1>
      <p>This page combines storefront-level questions with structure students can expand later.</p>
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
</main>
<?php
get_footer();
