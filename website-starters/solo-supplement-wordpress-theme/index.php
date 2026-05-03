<?php
get_header();
?>
<main class="page-wrap">
  <div class="container page-shell">
    <?php if (have_posts()) : while (have_posts()) : the_post(); ?>
      <h1><?php the_title(); ?></h1>
      <div><?php the_content(); ?></div>
    <?php endwhile; else : ?>
      <h1>Content</h1>
      <p>This theme starter expects you to create pages using the included templates.</p>
    <?php endif; ?>
  </div>
</main>
<?php
get_footer();
