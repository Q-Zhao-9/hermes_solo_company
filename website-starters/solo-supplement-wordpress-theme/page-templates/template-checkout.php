<?php
/*
Template Name: Checkout Template
*/

get_header();

$slug = isset($_GET['product']) ? sanitize_text_field(wp_unslash($_GET['product'])) : 'magnesium-glycinate-200mg';
$product = solo_supplement_get_product($slug);
?>
<main class="page-wrap">
  <div class="container stack">
    <div class="page-shell">
      <h1>Checkout</h1>
      <p>This is a V1 internal checkout shell inside the same WordPress theme. It keeps the purchase flow local while students learn the structure before live payment is added.</p>
    </div>

    <?php if (!$product) : ?>
      <div class="page-shell">
        <p>Select a valid product.</p>
      </div>
    <?php else : ?>
      <div class="checkout-layout">
        <section class="page-shell">
          <h2>Customer information</h2>
          <form class="checkout-form">
            <label>
              Full name
              <input type="text" name="name" placeholder="Jane Doe">
            </label>
            <label>
              Email
              <input type="email" name="email" placeholder="jane@example.com">
            </label>
            <label>
              Address line 1
              <input type="text" name="address1" placeholder="123 Main St">
            </label>
            <label>
              Address line 2
              <input type="text" name="address2" placeholder="Apt, suite, etc.">
            </label>
            <div class="checkout-form__row">
              <label>
                City
                <input type="text" name="city" placeholder="Los Angeles">
              </label>
              <label>
                State
                <input type="text" name="state" placeholder="CA">
              </label>
            </div>
            <div class="checkout-form__row">
              <label>
                ZIP
                <input type="text" name="zip" placeholder="90001">
              </label>
              <label>
                Quantity
                <input type="number" name="quantity" min="1" value="1">
              </label>
            </div>
            <label>
              Notes
              <textarea name="notes" rows="4" placeholder="Optional delivery or order notes"></textarea>
            </label>

            <div class="notice-strip">
              <strong>No live payment is connected yet.</strong>
              <p>This template is a structural starter only. Replace the action with Stripe, WooCommerce, Shopify handoff, or your own order backend when ready.</p>
            </div>

            <button class="cta-link cta-link--primary" type="button">Continue to Payment Setup</button>
          </form>
        </section>

        <aside class="page-shell">
          <h2>Order summary</h2>
          <div class="checkout-summary">
            <div>
              <strong><?php echo esc_html($product['name']); ?></strong>
              <p><?php echo esc_html($product['short_benefit']); ?></p>
            </div>
            <div class="product-price">
              <strong><?php echo esc_html($product['price']); ?></strong>
              <span><?php echo esc_html($product['cadence']); ?></span>
            </div>
          </div>

          <div class="notice-strip">
            <strong>Shipping policy</strong>
            <p>Orders ship in 1-2 business days within the continental US.</p>
          </div>

          <div class="notice-strip">
            <strong>Return policy</strong>
            <p>30-day refund window on unopened product.</p>
          </div>

          <div class="disclaimer-block">
            <strong>Required disclaimer</strong>
            <p><?php echo esc_html($product['disclaimer']); ?></p>
          </div>
        </aside>
      </div>
    <?php endif; ?>
  </div>
</main>
<?php
get_footer();
