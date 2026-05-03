<?php
$brand = solo_supplement_brand();
$policies = solo_supplement_policies();
?>
  <footer class="site-footer">
    <div class="container">
      <div class="site-footer__panel">
        <div class="site-footer__grid">
          <div>
            <strong><?php echo esc_html($brand['name']); ?></strong>
            <p><?php echo esc_html($brand['tagline']); ?></p>
            <p><?php echo esc_html($brand['shipping_policy']); ?></p>
          </div>
          <div>
            <strong>Support</strong>
            <p><a href="<?php echo esc_url(home_url('/contact/')); ?>"><?php echo esc_html($brand['support_email']); ?></a></p>
            <p><a href="<?php echo esc_url(home_url('/shipping-returns/')); ?>">Shipping &amp; Returns</a></p>
          </div>
          <div>
            <strong>Policies</strong>
            <?php foreach ($policies as $slug => $policy) : ?>
              <p><a href="<?php echo esc_url(home_url('/policies/' . $slug . '/')); ?>"><?php echo esc_html($policy['title']); ?></a></p>
            <?php endforeach; ?>
          </div>
        </div>
      </div>
    </div>
  </footer>
</div>
<?php wp_footer(); ?>
</body>
</html>
