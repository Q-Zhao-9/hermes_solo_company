<?php
$brand = solo_supplement_brand();
?>
<!DOCTYPE html>
<html <?php language_attributes(); ?>>
<head>
  <meta charset="<?php bloginfo('charset'); ?>">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <?php wp_head(); ?>
</head>
<body <?php body_class(); ?>>
<?php wp_body_open(); ?>
<div class="site-shell">
  <header class="site-header">
    <div class="container site-header__inner">
      <a class="site-brand" href="<?php echo esc_url(home_url('/')); ?>">
        <span class="site-brand__glyph">✦</span>
        <span>
          <span class="site-brand__eyebrow"><?php echo esc_html($brand['eyebrow']); ?></span>
          <span class="site-brand__name"><?php echo esc_html($brand['name']); ?></span>
        </span>
      </a>

      <nav class="site-nav" aria-label="Primary">
        <a href="<?php echo esc_url(home_url('/')); ?>">Home</a>
        <a href="<?php echo esc_url(home_url('/multivitamins/')); ?>">Multivitamins</a>
        <a href="<?php echo esc_url(home_url('/magnesium/')); ?>">Magnesium</a>
        <a href="<?php echo esc_url(home_url('/faq/')); ?>">FAQ</a>
        <a href="<?php echo esc_url(home_url('/shipping-returns/')); ?>">Shipping</a>
        <a href="<?php echo esc_url(home_url('/contact/')); ?>">Support</a>
      </nav>
    </div>
  </header>
