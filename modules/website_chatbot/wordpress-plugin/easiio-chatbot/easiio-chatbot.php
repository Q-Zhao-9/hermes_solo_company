<?php
/**
 * Plugin Name: Easiio Chatbot
 * Plugin URI: https://www.easiio.com/
 * Description: Adds the Easiio chatbot popup widget to the WordPress footer.
 * Version: 0.1.0
 * Author: Easiio
 * License: GPL-2.0-or-later
 * Text Domain: easiio-chatbot
 */

if (!defined('ABSPATH')) {
    exit;
}

/**
 * Render the Easiio chatbot script in the footer.
 *
 * This first version intentionally uses fixed reviewed defaults instead of an
 * admin settings page. That keeps the production surface small while the
 * widget/backend are reviewed. Update these values before activating on a live
 * domain if the chatbot backend is deployed somewhere else.
 */
function easiio_chatbot_footer_script() {
    $api_base = 'https://chat.easiio.com';
    $widget_url = $api_base . '/widget.js';
    // Site ID and organization are used by Hermes Bot CRM to separate multiple websites/tenants.
    $site_id = 'easiio-main';
    $organization_name = 'Easiio';
    $website_name = get_bloginfo('name') ?: 'Easiio Website';
    $track_page_views = 'true';
    $position = 'bottom-right';
    $title = 'Easiio Assistant';
    $primary_color = '#2563eb';
    $launcher_style = 'bubble';
    $launcher_size = 'small';
    $auto_open = 'false';
    $rag_admin = 'false';
    $greeting = 'Hi, I can help with AI automation or book a demo.';
    $email = 'hello@easiio.com';
    $exclude_paths = '/wp-admin,/wp-login.php,/cart,/checkout,/my-account';
    $consent_text = 'By chatting, you agree that Easiio may use your message to follow up about its services.';
    ?>
    <script
        async
        src="<?php echo esc_url($widget_url); ?>"
        data-easiio-chatbot
        data-site-id="<?php echo esc_attr($site_id); ?>"
        data-organization-name="<?php echo esc_attr($organization_name); ?>"
        data-website-name="<?php echo esc_attr($website_name); ?>"
        data-track-page-views="<?php echo esc_attr($track_page_views); ?>"
        data-api-base="<?php echo esc_url($api_base); ?>"
        data-position="<?php echo esc_attr($position); ?>"
        data-title="<?php echo esc_attr($title); ?>"
        data-primary-color="<?php echo esc_attr($primary_color); ?>"
        data-launcher-style="<?php echo esc_attr($launcher_style); ?>"
        data-launcher-size="<?php echo esc_attr($launcher_size); ?>"
        data-auto-open="<?php echo esc_attr($auto_open); ?>"
        data-rag-admin="<?php echo esc_attr($rag_admin); ?>"
        data-email="<?php echo esc_attr($email); ?>"
        data-exclude-paths="<?php echo esc_attr($exclude_paths); ?>"
        data-consent-text="<?php echo esc_attr($consent_text); ?>"
        data-greeting="<?php echo esc_attr($greeting); ?>">
    </script>
    <?php
}
add_action('wp_footer', 'easiio_chatbot_footer_script', 100);
