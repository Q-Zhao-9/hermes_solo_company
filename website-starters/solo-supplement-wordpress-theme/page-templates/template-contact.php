<?php
/*
Template Name: Contact Template
*/

get_header();
$brand = solo_supplement_brand();
?>
<main class="page-wrap">
  <div class="container stack">
    <div class="page-shell">
      <h1>Contact &amp; Support</h1>
      <p>This page exists to lower friction, not to hide support behind forms and aggressive self-service flows.</p>
    </div>

    <div class="support-grid">
      <section class="support-card">
        <h2>Email</h2>
        <p><?php echo esc_html($brand['support_email']); ?></p>
        <p>Replace this with the support path your actual workflow can maintain consistently.</p>
      </section>

      <section class="support-card">
        <h2>Before you write in</h2>
        <ul>
          <li>Check shipping and returns for timing and policy expectations.</li>
          <li>Use FAQ to resolve common usage and ordering questions.</li>
          <li>Keep product-effect questions within approved educational boundaries.</li>
        </ul>
      </section>
    </div>
  </div>
</main>
<?php
get_footer();
