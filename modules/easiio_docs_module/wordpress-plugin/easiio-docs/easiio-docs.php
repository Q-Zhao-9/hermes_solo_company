<?php
/**
 * Plugin Name: Easiio Docs
 * Plugin URI: https://www.easiio.com/
 * Description: Embeds the reusable Easiio Docs Module with the [easiio_docs] shortcode.
 * Version: 0.1.0
 * Author: Easiio
 * License: GPL-2.0-or-later
 * Text Domain: easiio-docs
 */

if (!defined('ABSPATH')) {
    exit;
}

function easiio_docs_bool_attr($value) {
    return in_array(strtolower((string) $value), array('1', 'true', 'yes', 'on'), true) ? 'true' : 'false';
}

function easiio_docs_shortcode($atts) {
    $atts = shortcode_atts(array(
        'api_base' => 'https://chat.easiio.com',
        'site_id' => 'easiio-main',
        'mode' => 'public',
        'title' => 'Documentation',
        'subtitle' => 'Guides, manuals, and knowledge base articles.',
        'target_filter' => 'wordpress-shortcode',
        'status' => 'published',
        'visibility' => 'public',
        'require_login' => 'false',
        'credential_mode' => 'same-origin',
        'auth_token' => '',
    ), $atts, 'easiio_docs');

    $api_base = rtrim(esc_url_raw($atts['api_base']), '/');
    $site_id = sanitize_key($atts['site_id']);
    $mode = $atts['mode'] === 'admin' ? 'admin' : 'public';
    $require_login = easiio_docs_bool_attr($atts['require_login']) === 'true';
    if ($require_login && !is_user_logged_in()) {
        return '<div class="easiio-docs-login-required">Please log in to view this documentation.</div>';
    }
    $current_user = $require_login ? wp_get_current_user() : null;
    $credential_mode = in_array($atts['credential_mode'], array('omit', 'same-origin', 'include'), true) ? $atts['credential_mode'] : 'same-origin';
    $root_id = 'easiio-docs-root-' . wp_rand(1000, 999999);
    $widget_url = $api_base . '/docs/docs.js';
    $css_url = $api_base . '/docs/docs.css';
    $auth_token = sanitize_text_field($atts['auth_token']);

    ob_start();
    ?>
    <link rel="stylesheet" href="<?php echo esc_url($css_url); ?>" />
    <div id="<?php echo esc_attr($root_id); ?>"></div>
    <script
        async
        src="<?php echo esc_url($widget_url); ?>"
        data-easiio-docs
        data-api-base="<?php echo esc_url($api_base); ?>"
        data-site-id="<?php echo esc_attr($site_id); ?>"
        data-mode="<?php echo esc_attr($mode); ?>"
        data-root-selector="#<?php echo esc_attr($root_id); ?>"
        data-title="<?php echo esc_attr($atts['title']); ?>"
        data-subtitle="<?php echo esc_attr($atts['subtitle']); ?>"
        data-target-filter="<?php echo esc_attr(sanitize_text_field($atts['target_filter'])); ?>"
        data-status="<?php echo esc_attr(sanitize_text_field($atts['status'])); ?>"
        data-visibility="<?php echo esc_attr(sanitize_text_field($atts['visibility'])); ?>"
        data-login-required="<?php echo esc_attr($require_login ? 'true' : 'false'); ?>"
        data-credential-mode="<?php echo esc_attr($credential_mode); ?>"
        data-auth-token="<?php echo esc_attr($auth_token); ?>"
        data-wp-user="<?php echo esc_attr($current_user ? $current_user->user_login : ''); ?>">
    </script>
    <?php
    return ob_get_clean();
}
add_shortcode('easiio_docs', 'easiio_docs_shortcode');
