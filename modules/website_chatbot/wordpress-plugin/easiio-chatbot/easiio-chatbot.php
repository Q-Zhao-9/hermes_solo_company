<?php
/**
 * Plugin Name: Easiio Chatbot
 * Plugin URI: https://www.easiio.com/
 * Description: Adds the Easiio chatbot popup widget to WordPress with safe admin settings for chatbot, RAG, and Solo CRM lead capture through the Easiio backend.
 * Version: 0.2.0
 * Author: Easiio
 * License: GPL-2.0-or-later
 * Text Domain: easiio-chatbot
 */

if (!defined('ABSPATH')) {
    exit;
}

const EASIIO_CHATBOT_OPTION = 'easiio_chatbot_options';
const EASIIO_CHATBOT_SETTINGS_GROUP = 'easiio_chatbot_settings_group';

/**
 * Safe defaults for the public widget.
 *
 * Keep credentials, LLM keys, CRM tokens, webhook URLs, SMTP/Brevo secrets,
 * and MCP/database details out of this plugin. Those belong on the protected
 * chatbot backend only.
 */
function easiio_chatbot_default_options() {
    return array(
        'api_base' => 'https://chat.easiio.com',
        'widget_url' => 'https://chat.easiio.com/widget.js',
        'site_id' => 'easiio-main',
        'organization_name' => 'Easiio',
        'website_name' => get_bloginfo('name') ?: 'Easiio Website',
        'track_page_views' => 'true',
        'position' => 'bottom-right',
        'title' => 'Easiio Assistant',
        'primary_color' => '#2563eb',
        'launcher_style' => 'bubble',
        'launcher_size' => 'small',
        'auto_open' => 'false',
        'rag_admin' => 'false',
        'lead_forms_enabled' => 'false',
        'voice_enabled' => 'false',
        'voice_label' => 'Listen',
        'voice_input_enabled' => 'false',
        'voice_input_label' => 'Speak',
        'voice_input_language' => 'auto',
        'voice_call_enabled' => 'false',
        'voice_call_label' => 'Call AI Assistant',
        'voice_call_api_base' => '',
        'voice_call_consent_text' => 'This AI assistant may transcribe your voice to answer your question and follow up if you share contact details.',
        'greeting' => 'Hi, I can help answer questions or book a demo.',
        'email' => '',
        'exclude_paths' => '/wp-admin,/wp-login.php,/cart,/checkout,/my-account',
        'consent_text' => 'By chatting, you agree that this website may use your message to follow up.'
    );
}

function easiio_chatbot_bool_value($value) {
    return in_array((string) $value, array('1', 'true', 'yes', 'on'), true) ? 'true' : 'false';
}

function easiio_chatbot_sanitize_path_list($value) {
    $paths = explode(',', (string) $value);
    $clean = array();
    foreach ($paths as $path) {
        $path = trim(sanitize_text_field($path));
        if ($path === '') {
            continue;
        }
        if ($path[0] !== '/') {
            $path = '/' . $path;
        }
        $clean[] = $path;
    }
    $clean = array_values(array_unique($clean));
    return implode(',', $clean);
}

function easiio_chatbot_sanitize_options($input) {
    $defaults = easiio_chatbot_default_options();
    $input = is_array($input) ? $input : array();

    $options = array();
    $options['api_base'] = !empty($input['api_base']) ? esc_url_raw($input['api_base']) : $defaults['api_base'];
    $options['widget_url'] = !empty($input['widget_url']) ? esc_url_raw($input['widget_url']) : $defaults['widget_url'];
    $options['site_id'] = !empty($input['site_id']) ? sanitize_key($input['site_id']) : $defaults['site_id'];
    $options['organization_name'] = !empty($input['organization_name']) ? sanitize_text_field($input['organization_name']) : $defaults['organization_name'];
    $options['website_name'] = !empty($input['website_name']) ? sanitize_text_field($input['website_name']) : $defaults['website_name'];
    $options['track_page_views'] = easiio_chatbot_bool_value($input['track_page_views'] ?? $defaults['track_page_views']);
    $options['position'] = sanitize_text_field($input['position'] ?? $defaults['position']);
    $options['title'] = !empty($input['title']) ? sanitize_text_field($input['title']) : $defaults['title'];
    $options['primary_color'] = sanitize_hex_color($input['primary_color'] ?? $defaults['primary_color']);
    $options['primary_color'] = $options['primary_color'] ?: $defaults['primary_color'];
    $options['launcher_style'] = sanitize_text_field($input['launcher_style'] ?? $defaults['launcher_style']);
    $options['launcher_size'] = sanitize_text_field($input['launcher_size'] ?? $defaults['launcher_size']);
    $options['auto_open'] = easiio_chatbot_bool_value($input['auto_open'] ?? $defaults['auto_open']);
    $options['rag_admin'] = easiio_chatbot_bool_value($input['rag_admin'] ?? $defaults['rag_admin']);
    $options['lead_forms_enabled'] = easiio_chatbot_bool_value($input['lead_forms_enabled'] ?? $defaults['lead_forms_enabled']);
    $options['voice_enabled'] = easiio_chatbot_bool_value($input['voice_enabled'] ?? $defaults['voice_enabled']);
    $options['voice_label'] = !empty($input['voice_label']) ? sanitize_text_field($input['voice_label']) : $defaults['voice_label'];
    $options['voice_input_enabled'] = easiio_chatbot_bool_value($input['voice_input_enabled'] ?? $defaults['voice_input_enabled']);
    $options['voice_input_label'] = !empty($input['voice_input_label']) ? sanitize_text_field($input['voice_input_label']) : $defaults['voice_input_label'];
    $options['voice_input_language'] = !empty($input['voice_input_language']) ? sanitize_text_field($input['voice_input_language']) : $defaults['voice_input_language'];
    $options['voice_call_enabled'] = easiio_chatbot_bool_value($input['voice_call_enabled'] ?? $defaults['voice_call_enabled']);
    $options['voice_call_label'] = !empty($input['voice_call_label']) ? sanitize_text_field($input['voice_call_label']) : $defaults['voice_call_label'];
    $options['voice_call_api_base'] = !empty($input['voice_call_api_base']) ? esc_url_raw($input['voice_call_api_base']) : $defaults['voice_call_api_base'];
    $options['voice_call_consent_text'] = !empty($input['voice_call_consent_text']) ? sanitize_textarea_field($input['voice_call_consent_text']) : $defaults['voice_call_consent_text'];
    $options['greeting'] = !empty($input['greeting']) ? sanitize_text_field($input['greeting']) : $defaults['greeting'];
    $options['email'] = !empty($input['email']) ? sanitize_email($input['email']) : $defaults['email'];
    $options['exclude_paths'] = easiio_chatbot_sanitize_path_list($input['exclude_paths'] ?? $defaults['exclude_paths']);
    $options['consent_text'] = !empty($input['consent_text']) ? sanitize_textarea_field($input['consent_text']) : $defaults['consent_text'];

    $allowed_positions = array('bottom-right', 'bottom-left', 'top-right', 'top-left');
    if (!in_array($options['position'], $allowed_positions, true)) {
        $options['position'] = $defaults['position'];
    }

    $allowed_launcher_styles = array('bubble', 'pill');
    if (!in_array($options['launcher_style'], $allowed_launcher_styles, true)) {
        $options['launcher_style'] = $defaults['launcher_style'];
    }

    $allowed_launcher_sizes = array('small', 'medium', 'large');
    if (!in_array($options['launcher_size'], $allowed_launcher_sizes, true)) {
        $options['launcher_size'] = $defaults['launcher_size'];
    }

    return wp_parse_args($options, $defaults);
}

function easiio_chatbot_get_options() {
    $saved = get_option(EASIIO_CHATBOT_OPTION, array());
    if (!is_array($saved)) {
        $saved = array();
    }
    return wp_parse_args($saved, easiio_chatbot_default_options());
}

function easiio_chatbot_register_settings() {
    register_setting(
        EASIIO_CHATBOT_SETTINGS_GROUP,
        EASIIO_CHATBOT_OPTION,
        array(
            'type' => 'array',
            'sanitize_callback' => 'easiio_chatbot_sanitize_options',
            'default' => easiio_chatbot_default_options(),
        )
    );
}
add_action('admin_init', 'easiio_chatbot_register_settings');

function easiio_chatbot_register_settings_page() {
    add_options_page(
        __('Easiio Chatbot', 'easiio-chatbot'),
        __('Easiio Chatbot', 'easiio-chatbot'),
        'manage_options',
        'easiio-chatbot',
        'easiio_chatbot_render_settings_page'
    );
}
add_action('admin_menu', 'easiio_chatbot_register_settings_page');

function easiio_chatbot_field($options, $key, $label, $type = 'text', $help = '') {
    $name = EASIIO_CHATBOT_OPTION . '[' . $key . ']';
    $value = $options[$key] ?? '';
    ?>
    <tr>
        <th scope="row"><label for="easiio-chatbot-<?php echo esc_attr($key); ?>"><?php echo esc_html($label); ?></label></th>
        <td>
            <?php if ($type === 'textarea') : ?>
                <textarea class="large-text" rows="3" id="easiio-chatbot-<?php echo esc_attr($key); ?>" name="<?php echo esc_attr($name); ?>"><?php echo esc_textarea($value); ?></textarea>
            <?php else : ?>
                <input class="regular-text" type="<?php echo esc_attr($type); ?>" id="easiio-chatbot-<?php echo esc_attr($key); ?>" name="<?php echo esc_attr($name); ?>" value="<?php echo esc_attr($value); ?>" />
            <?php endif; ?>
            <?php if ($help) : ?>
                <p class="description"><?php echo esc_html($help); ?></p>
            <?php endif; ?>
        </td>
    </tr>
    <?php
}

function easiio_chatbot_select_field($options, $key, $label, $choices, $help = '') {
    $name = EASIIO_CHATBOT_OPTION . '[' . $key . ']';
    $value = $options[$key] ?? '';
    ?>
    <tr>
        <th scope="row"><label for="easiio-chatbot-<?php echo esc_attr($key); ?>"><?php echo esc_html($label); ?></label></th>
        <td>
            <select id="easiio-chatbot-<?php echo esc_attr($key); ?>" name="<?php echo esc_attr($name); ?>">
                <?php foreach ($choices as $choice_value => $choice_label) : ?>
                    <option value="<?php echo esc_attr($choice_value); ?>" <?php selected($value, $choice_value); ?>><?php echo esc_html($choice_label); ?></option>
                <?php endforeach; ?>
            </select>
            <?php if ($help) : ?>
                <p class="description"><?php echo esc_html($help); ?></p>
            <?php endif; ?>
        </td>
    </tr>
    <?php
}

function easiio_chatbot_render_settings_page() {
    if (!current_user_can('manage_options')) {
        return;
    }

    $options = easiio_chatbot_get_options();
    $nonce = wp_create_nonce('easiio_chatbot_health_check');
    ?>
    <div class="wrap">
        <h1><?php esc_html_e('Easiio Chatbot', 'easiio-chatbot'); ?></h1>
        <p><?php esc_html_e('Configure the public Easiio chatbot widget for this WordPress site. RAG, CRM, LLM, email, and connector secrets must stay on the protected backend server.', 'easiio-chatbot'); ?></p>

        <form method="post" action="options.php">
            <?php settings_fields(EASIIO_CHATBOT_SETTINGS_GROUP); ?>
            <h2><?php esc_html_e('Backend and Site Identity', 'easiio-chatbot'); ?></h2>
            <table class="form-table" role="presentation">
                <?php
                easiio_chatbot_field($options, 'api_base', 'API base URL', 'url', 'Example: https://chat.easiio.com or same-origin gateway URL.');
                easiio_chatbot_field($options, 'widget_url', 'Widget script URL', 'url', 'Example: https://chat.easiio.com/widget.js');
                easiio_chatbot_field($options, 'site_id', 'Site ID', 'text', 'Stable ID used to separate this site in RAG and Solo CRM.');
                easiio_chatbot_field($options, 'organization_name', 'Organization name');
                easiio_chatbot_field($options, 'website_name', 'Website name');
                ?>
            </table>

            <h2><?php esc_html_e('Widget Appearance and Behavior', 'easiio-chatbot'); ?></h2>
            <table class="form-table" role="presentation">
                <?php
                easiio_chatbot_field($options, 'title', 'Chat title');
                easiio_chatbot_field($options, 'greeting', 'Greeting');
                easiio_chatbot_field($options, 'primary_color', 'Primary color', 'text', 'Hex color such as #2563eb.');
                easiio_chatbot_select_field($options, 'position', 'Position', array(
                    'bottom-right' => 'Bottom right',
                    'bottom-left' => 'Bottom left',
                    'top-right' => 'Top right',
                    'top-left' => 'Top left',
                ));
                easiio_chatbot_select_field($options, 'launcher_style', 'Launcher style', array('bubble' => 'Bubble', 'pill' => 'Pill'));
                easiio_chatbot_select_field($options, 'launcher_size', 'Launcher size', array('small' => 'Small', 'medium' => 'Medium', 'large' => 'Large'));
                easiio_chatbot_select_field($options, 'auto_open', 'Auto open', array('false' => 'No', 'true' => 'Yes'), 'Recommended: No.');
                easiio_chatbot_select_field($options, 'track_page_views', 'Track page views', array('true' => 'Yes', 'false' => 'No'));
                easiio_chatbot_select_field($options, 'lead_forms_enabled', 'Enable automatic lead forms', array('false' => 'No', 'true' => 'Yes'), 'Recommended: No for normal factual Q&A.');
                easiio_chatbot_select_field($options, 'rag_admin', 'Enable RAG admin on public pages', array('false' => 'No', 'true' => 'Yes'), 'Only enable on protected/admin-only pages.');
                easiio_chatbot_select_field($options, 'voice_enabled', 'Enable voice playback', array('false' => 'No', 'true' => 'Yes'), 'Optional. Requires the backend /api/chat/voice endpoint and server-side TTS provider.');
                easiio_chatbot_field($options, 'voice_label', 'Voice button label', 'text', 'Example: Listen');
                easiio_chatbot_select_field($options, 'voice_input_enabled', 'Enable voice input', array('false' => 'No', 'true' => 'Yes'), 'Optional. Uses browser SpeechRecognition when supported; no server-side speech key is stored in WordPress.');
                easiio_chatbot_field($options, 'voice_input_label', 'Voice input button label', 'text', 'Example: Speak');
                easiio_chatbot_field($options, 'voice_input_language', 'Voice input language', 'text', 'Examples: auto, en-US, zh-CN');
                easiio_chatbot_select_field($options, 'voice_call_enabled', 'Enable browser AI voice call', array('false' => 'No', 'true' => 'Yes'), 'Optional. Requires the separate voice_call_bot backend; keep disabled until reviewed.');
                easiio_chatbot_field($options, 'voice_call_label', 'Voice call button label', 'text', 'Example: Call AI Assistant');
                easiio_chatbot_field($options, 'voice_call_api_base', 'Voice-call API base URL', 'url', 'Example: https://voice.example.com or same-origin gateway URL. No provider keys are stored here.');
                easiio_chatbot_field($options, 'voice_call_consent_text', 'Voice call consent text', 'textarea');
                easiio_chatbot_field($options, 'email', 'Public contact email', 'email');
                easiio_chatbot_field($options, 'exclude_paths', 'Excluded paths', 'text', 'Comma-separated paths where chatbot should not render.');
                easiio_chatbot_field($options, 'consent_text', 'Consent text', 'textarea');
                ?>
            </table>

            <?php submit_button(); ?>
        </form>

        <hr />
        <h2><?php esc_html_e('Health check', 'easiio-chatbot'); ?></h2>
        <p><?php esc_html_e('Checks the backend /health endpoint server-side and returns sanitized status only.', 'easiio-chatbot'); ?></p>
        <button type="button" class="button" id="easiio-chatbot-health-check"><?php esc_html_e('Check backend health', 'easiio-chatbot'); ?></button>
        <span id="easiio-chatbot-health-result" style="margin-left: 8px;"></span>
        <script>
        (function() {
            var button = document.getElementById('easiio-chatbot-health-check');
            var result = document.getElementById('easiio-chatbot-health-result');
            if (!button || !result) return;
            button.addEventListener('click', function() {
                result.textContent = 'Checking...';
                var body = new URLSearchParams();
                body.append('action', 'easiio_chatbot_health_check');
                body.append('_ajax_nonce', '<?php echo esc_js($nonce); ?>');
                fetch(ajaxurl, {
                    method: 'POST',
                    credentials: 'same-origin',
                    headers: {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'},
                    body: body.toString()
                }).then(function(response) {
                    return response.json();
                }).then(function(data) {
                    if (data && data.success) {
                        result.textContent = 'Backend reachable: HTTP ' + data.data.status;
                    } else {
                        result.textContent = 'Backend check failed: ' + ((data && data.data && data.data.message) || 'unknown error');
                    }
                }).catch(function() {
                    result.textContent = 'Backend check failed.';
                });
            });
        })();
        </script>

        <h2><?php esc_html_e('Security reminder', 'easiio-chatbot'); ?></h2>
        <p><?php esc_html_e('Do not put LLM keys, CRM tokens, HubSpot tokens, Google Sheets webhook URLs, email provider keys, MCP details, or database paths in this plugin. Configure those server-side only.', 'easiio-chatbot'); ?></p>
    </div>
    <?php
}

function easiio_chatbot_health_check() {
    if (!current_user_can('manage_options')) {
        wp_send_json_error(array('message' => 'forbidden'), 403);
    }

    check_ajax_referer('easiio_chatbot_health_check');

    $options = easiio_chatbot_get_options();
    $api_base = rtrim($options['api_base'], '/');
    $health_url = $api_base . '/health';
    $response = wp_remote_get($health_url, array('timeout' => 8));

    if (is_wp_error($response)) {
        wp_send_json_error(array('message' => sanitize_text_field($response->get_error_message())));
    }

    $status = (int) wp_remote_retrieve_response_code($response);
    if ($status >= 200 && $status < 300) {
        wp_send_json_success(array('status' => $status));
    }

    wp_send_json_error(array('message' => 'HTTP ' . $status, 'status' => $status));
}
add_action('wp_ajax_easiio_chatbot_health_check', 'easiio_chatbot_health_check');

function easiio_chatbot_is_excluded_path($exclude_paths) {
    $request_uri = isset($_SERVER['REQUEST_URI']) ? sanitize_text_field(wp_unslash($_SERVER['REQUEST_URI'])) : '';
    $request_path = parse_url($request_uri, PHP_URL_PATH);
    if (!$request_path) {
        return false;
    }

    foreach (explode(',', (string) $exclude_paths) as $path) {
        $path = trim($path);
        if ($path !== '' && strpos($request_path, $path) === 0) {
            return true;
        }
    }
    return false;
}

/**
 * Render the Easiio chatbot script in the footer.
 */
function easiio_chatbot_footer_script() {
    $options = easiio_chatbot_get_options();

    if (easiio_chatbot_is_excluded_path($options['exclude_paths'])) {
        return;
    }
    ?>
    <script
        async
        src="<?php echo esc_url($options['widget_url']); ?>"
        data-easiio-chatbot
        data-site-id="<?php echo esc_attr($options['site_id']); ?>"
        data-organization-name="<?php echo esc_attr($options['organization_name']); ?>"
        data-website-name="<?php echo esc_attr($options['website_name']); ?>"
        data-track-page-views="<?php echo esc_attr($options['track_page_views']); ?>"
        data-api-base="<?php echo esc_url($options['api_base']); ?>"
        data-position="<?php echo esc_attr($options['position']); ?>"
        data-title="<?php echo esc_attr($options['title']); ?>"
        data-primary-color="<?php echo esc_attr($options['primary_color']); ?>"
        data-launcher-style="<?php echo esc_attr($options['launcher_style']); ?>"
        data-launcher-size="<?php echo esc_attr($options['launcher_size']); ?>"
        data-auto-open="<?php echo esc_attr($options['auto_open']); ?>"
        data-rag-admin="<?php echo esc_attr($options['rag_admin']); ?>"
        data-lead-forms-enabled="<?php echo esc_attr($options['lead_forms_enabled']); ?>"
        data-voice-enabled="<?php echo esc_attr($options['voice_enabled']); ?>"
        data-voice-label="<?php echo esc_attr($options['voice_label']); ?>"
        data-voice-input-enabled="<?php echo esc_attr($options['voice_input_enabled']); ?>"
        data-voice-input-label="<?php echo esc_attr($options['voice_input_label']); ?>"
        data-voice-input-language="<?php echo esc_attr($options['voice_input_language']); ?>"
        data-voice-call-enabled="<?php echo esc_attr($options['voice_call_enabled']); ?>"
        data-voice-call-label="<?php echo esc_attr($options['voice_call_label']); ?>"
        data-voice-call-api-base="<?php echo esc_url($options['voice_call_api_base']); ?>"
        data-voice-call-consent-text="<?php echo esc_attr($options['voice_call_consent_text']); ?>"
        data-email="<?php echo esc_attr($options['email']); ?>"
        data-exclude-paths="<?php echo esc_attr($options['exclude_paths']); ?>"
        data-consent-text="<?php echo esc_attr($options['consent_text']); ?>"
        data-greeting="<?php echo esc_attr($options['greeting']); ?>">
    </script>
    <?php
}
add_action('wp_footer', 'easiio_chatbot_footer_script', 100);
