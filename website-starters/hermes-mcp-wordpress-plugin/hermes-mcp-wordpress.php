<?php
/**
 * Plugin Name: Hermes MCP for WordPress
 * Description: Exposes a controlled MCP-style endpoint so Hermes Agent can manage WordPress content through approved tools.
 * Version: 0.1.0
 * Author: Hermes Agent
 * License: MIT
 * Requires at least: 6.2
 * Requires PHP: 8.0
 */

if (!defined('ABSPATH')) {
    exit;
}

final class Hermes_MCP_WordPress {
    private const OPTION = 'hermes_mcp_settings';
    private const AUDIT_OPTION = 'hermes_mcp_audit_log';
    private const REST_NAMESPACE = 'hermes-mcp/v1';
    private const REST_ROUTE = '/mcp';
    private const MAX_AUDIT_ROWS = 200;

    private static ?Hermes_MCP_WordPress $instance = null;

    private array $default_tools = [
        'list_posts' => true,
        'get_post' => true,
        'create_draft_post' => true,
        'update_post' => true,
        'list_pages' => true,
        'get_page' => true,
        'update_page' => true,
        'upload_media_from_url' => true,
        'list_comments' => true,
        'update_comment_status' => true,
    ];

    public static function instance(): self {
        if (self::$instance === null) {
            self::$instance = new self();
        }
        return self::$instance;
    }

    private function __construct() {
        add_action('rest_api_init', [$this, 'register_routes']);
        add_action('admin_menu', [$this, 'register_admin_page']);
        add_action('network_admin_menu', [$this, 'register_network_admin_page']);
        add_action('admin_init', [$this, 'handle_settings_post']);
        add_filter('plugin_action_links_' . plugin_basename(__FILE__), [$this, 'plugin_action_links']);
    }

    public static function activate(): void {
        $settings = get_option(self::OPTION);
        if (!is_array($settings)) {
            add_option(self::OPTION, self::default_settings());
        }
    }

    private static function default_settings(): array {
        return [
            'enabled' => false,
            'api_key_hash' => '',
            'api_key_hint' => '',
            'api_user_id' => 0,
            'tools' => [
                'list_posts' => true,
                'get_post' => true,
                'create_draft_post' => true,
                'update_post' => true,
                'list_pages' => true,
                'get_page' => true,
                'update_page' => true,
                'upload_media_from_url' => true,
                'list_comments' => true,
                'update_comment_status' => true,
            ],
            'default_post_status' => 'draft',
            'audit_enabled' => true,
        ];
    }

    private function get_settings(): array {
        $settings = get_option(self::OPTION, []);
        if (!is_array($settings)) {
            $settings = [];
        }
        return array_replace_recursive(self::default_settings(), $settings);
    }

    public function plugin_action_links(array $links): array {
        $url = admin_url('options-general.php?page=hermes-mcp-wordpress');
        array_unshift($links, '<a href="' . esc_url($url) . '">' . esc_html__('Settings', 'hermes-mcp') . '</a>');
        return $links;
    }

    public function register_routes(): void {
        register_rest_route(self::REST_NAMESPACE, self::REST_ROUTE, [
            'methods' => WP_REST_Server::CREATABLE,
            'callback' => [$this, 'handle_mcp_request'],
            'permission_callback' => [$this, 'authorize_request'],
        ]);

        register_rest_route(self::REST_NAMESPACE, '/health', [
            'methods' => WP_REST_Server::READABLE,
            'callback' => [$this, 'handle_health_request'],
            'permission_callback' => '__return_true',
        ]);
    }

    public function authorize_request(WP_REST_Request $request): bool|WP_Error {
        $settings = $this->get_settings();
        if (empty($settings['enabled'])) {
            return new WP_Error('hermes_mcp_disabled', 'Hermes MCP endpoint is disabled.', ['status' => 403]);
        }
        if (empty($settings['api_key_hash'])) {
            return new WP_Error('hermes_mcp_no_key', 'Hermes MCP API key has not been generated.', ['status' => 403]);
        }

        $header = $request->get_header('authorization');
        if (!preg_match('/^Bearer\s+(.+)$/i', $header, $matches)) {
            return new WP_Error('hermes_mcp_missing_bearer', 'Missing bearer token.', ['status' => 401]);
        }

        if (!wp_check_password(trim($matches[1]), $settings['api_key_hash'])) {
            $this->audit('auth_failed', 'unknown', ['ip' => $this->client_ip()]);
            return new WP_Error('hermes_mcp_bad_token', 'Invalid bearer token.', ['status' => 401]);
        }

        return true;
    }

    public function handle_health_request(): WP_REST_Response {
        $settings = $this->get_settings();
        return new WP_REST_Response([
            'ok' => true,
            'enabled' => (bool) $settings['enabled'],
            'site_url' => home_url('/'),
            'mcp_url' => esc_url_raw(rest_url(self::REST_NAMESPACE . self::REST_ROUTE)),
        ]);
    }

    public function handle_mcp_request(WP_REST_Request $request): WP_REST_Response {
        $payload = $request->get_json_params();
        if (!is_array($payload)) {
            return $this->json_rpc_error(null, -32700, 'Invalid JSON payload.');
        }

        if ($this->is_list_array($payload)) {
            $responses = [];
            foreach ($payload as $message) {
                if (!is_array($message)) {
                    $responses[] = $this->json_rpc_error_payload(null, -32600, 'Invalid JSON-RPC message.');
                    continue;
                }
                $response = $this->handle_json_rpc_message($message);
                if ($response !== null) {
                    $responses[] = $response;
                }
            }
            return new WP_REST_Response($responses);
        }

        $response = $this->handle_json_rpc_message($payload);
        if ($response === null) {
            return new WP_REST_Response(null, 202);
        }
        $rest_response = new WP_REST_Response($response);
        if (($payload['method'] ?? '') === 'initialize') {
            $rest_response->header('Mcp-Session-Id', wp_generate_uuid4());
        }
        return $rest_response;
    }

    private function handle_json_rpc_message(array $payload): ?array {
        $id = $payload['id'] ?? null;
        $method = isset($payload['method']) ? sanitize_text_field((string) $payload['method']) : '';
        $params = isset($payload['params']) && is_array($payload['params']) ? $payload['params'] : [];

        try {
            if ($id === null && str_starts_with($method, 'notifications/')) {
                return null;
            }

            if ($method === 'initialize') {
                return $this->json_rpc_result_payload($id, [
                    'protocolVersion' => '2025-03-26',
                    'serverInfo' => [
                        'name' => 'hermes-mcp-wordpress',
                        'version' => '0.1.0',
                    ],
                    'capabilities' => [
                        'tools' => new stdClass(),
                    ],
                ]);
            }

            if ($method === 'tools/list') {
                return $this->json_rpc_result_payload($id, [
                    'tools' => array_values($this->tool_definitions()),
                ]);
            }

            if ($method === 'tools/call') {
                $tool_name = isset($params['name']) ? sanitize_key((string) $params['name']) : '';
                $arguments = isset($params['arguments']) && is_array($params['arguments']) ? $params['arguments'] : [];
                return $this->json_rpc_result_payload($id, $this->call_tool($tool_name, $arguments));
            }

            return $this->json_rpc_error_payload($id, -32601, 'Unknown MCP method.');
        } catch (Throwable $error) {
            $this->audit('tool_error', $method ?: 'unknown', ['message' => $error->getMessage()]);
            return $this->json_rpc_error_payload($id, -32000, $error->getMessage());
        }
    }

    private function json_rpc_result(mixed $id, mixed $result): WP_REST_Response {
        return new WP_REST_Response($this->json_rpc_result_payload($id, $result));
    }

    private function is_list_array(array $value): bool {
        if ($value === []) {
            return true;
        }
        return array_keys($value) === range(0, count($value) - 1);
    }

    private function json_rpc_result_payload(mixed $id, mixed $result): array {
        return [
            'jsonrpc' => '2.0',
            'id' => $id,
            'result' => $result,
        ];
    }

    private function json_rpc_error(mixed $id, int $code, string $message): WP_REST_Response {
        $status = $code === -32601 ? 404 : 400;
        return new WP_REST_Response($this->json_rpc_error_payload($id, $code, $message), $status);
    }

    private function json_rpc_error_payload(mixed $id, int $code, string $message): array {
        return [
            'jsonrpc' => '2.0',
            'id' => $id,
            'error' => [
                'code' => $code,
                'message' => $message,
            ],
        ];
    }

    private function tool_definitions(): array {
        $settings = $this->get_settings();
        $enabled_tools = is_array($settings['tools']) ? $settings['tools'] : [];
        $definitions = [
            'list_posts' => [
                'name' => 'list_posts',
                'description' => 'List recent WordPress posts with IDs, titles, statuses, dates, and links.',
                'inputSchema' => [
                    'type' => 'object',
                    'properties' => [
                        'status' => ['type' => 'string', 'description' => 'Post status filter. Defaults to any.'],
                        'search' => ['type' => 'string', 'description' => 'Optional search query.'],
                        'limit' => ['type' => 'integer', 'description' => 'Maximum posts to return, up to 50.'],
                    ],
                ],
            ],
            'get_post' => [
                'name' => 'get_post',
                'description' => 'Read one WordPress post by ID, including rendered and raw content.',
                'inputSchema' => [
                    'type' => 'object',
                    'required' => ['id'],
                    'properties' => ['id' => ['type' => 'integer']],
                ],
            ],
            'create_draft_post' => [
                'name' => 'create_draft_post',
                'description' => 'Create a draft WordPress post. Publishing should be a separate human-reviewed action.',
                'inputSchema' => [
                    'type' => 'object',
                    'required' => ['title'],
                    'properties' => [
                        'title' => ['type' => 'string'],
                        'content' => ['type' => 'string'],
                        'excerpt' => ['type' => 'string'],
                        'slug' => ['type' => 'string'],
                    ],
                ],
            ],
            'update_post' => [
                'name' => 'update_post',
                'description' => 'Update a WordPress post by ID. Only supplied fields are changed.',
                'inputSchema' => [
                    'type' => 'object',
                    'required' => ['id'],
                    'properties' => [
                        'id' => ['type' => 'integer'],
                        'title' => ['type' => 'string'],
                        'content' => ['type' => 'string'],
                        'excerpt' => ['type' => 'string'],
                        'slug' => ['type' => 'string'],
                        'status' => ['type' => 'string', 'description' => 'draft, pending, private, or publish if the API user can publish posts.'],
                    ],
                ],
            ],
            'list_pages' => [
                'name' => 'list_pages',
                'description' => 'List WordPress pages with IDs, titles, statuses, parents, and links.',
                'inputSchema' => [
                    'type' => 'object',
                    'properties' => [
                        'status' => ['type' => 'string'],
                        'search' => ['type' => 'string'],
                        'limit' => ['type' => 'integer'],
                    ],
                ],
            ],
            'get_page' => [
                'name' => 'get_page',
                'description' => 'Read one WordPress page by ID, including rendered and raw content.',
                'inputSchema' => [
                    'type' => 'object',
                    'required' => ['id'],
                    'properties' => ['id' => ['type' => 'integer']],
                ],
            ],
            'update_page' => [
                'name' => 'update_page',
                'description' => 'Update a WordPress page by ID. Only supplied fields are changed.',
                'inputSchema' => [
                    'type' => 'object',
                    'required' => ['id'],
                    'properties' => [
                        'id' => ['type' => 'integer'],
                        'title' => ['type' => 'string'],
                        'content' => ['type' => 'string'],
                        'excerpt' => ['type' => 'string'],
                        'slug' => ['type' => 'string'],
                        'status' => ['type' => 'string'],
                    ],
                ],
            ],
            'upload_media_from_url' => [
                'name' => 'upload_media_from_url',
                'description' => 'Upload an image or file to the WordPress media library from a URL.',
                'inputSchema' => [
                    'type' => 'object',
                    'required' => ['url'],
                    'properties' => [
                        'url' => ['type' => 'string'],
                        'title' => ['type' => 'string'],
                        'alt_text' => ['type' => 'string'],
                    ],
                ],
            ],
            'list_comments' => [
                'name' => 'list_comments',
                'description' => 'List recent WordPress comments.',
                'inputSchema' => [
                    'type' => 'object',
                    'properties' => [
                        'status' => ['type' => 'string', 'description' => 'approve, hold, spam, trash, or all.'],
                        'post_id' => ['type' => 'integer'],
                        'limit' => ['type' => 'integer'],
                    ],
                ],
            ],
            'update_comment_status' => [
                'name' => 'update_comment_status',
                'description' => 'Approve, hold, spam, or trash a WordPress comment.',
                'inputSchema' => [
                    'type' => 'object',
                    'required' => ['id', 'status'],
                    'properties' => [
                        'id' => ['type' => 'integer'],
                        'status' => ['type' => 'string', 'description' => 'approve, hold, spam, or trash.'],
                    ],
                ],
            ],
        ];

        return array_filter($definitions, static function (array $definition) use ($enabled_tools): bool {
            return !empty($enabled_tools[$definition['name']]);
        });
    }

    private function call_tool(string $name, array $arguments): array {
        $settings = $this->get_settings();
        if (empty($settings['tools'][$name])) {
            throw new RuntimeException('Tool is disabled or does not exist: ' . $name);
        }

        $result = match ($name) {
            'list_posts' => $this->list_content('post', $arguments),
            'get_post' => $this->get_content('post', $arguments),
            'create_draft_post' => $this->create_draft_post($arguments),
            'update_post' => $this->update_content('post', $arguments),
            'list_pages' => $this->list_content('page', $arguments),
            'get_page' => $this->get_content('page', $arguments),
            'update_page' => $this->update_content('page', $arguments),
            'upload_media_from_url' => $this->upload_media_from_url($arguments),
            'list_comments' => $this->list_comments($arguments),
            'update_comment_status' => $this->update_comment_status($arguments),
            default => throw new RuntimeException('Unknown tool: ' . $name),
        };

        $this->audit('tool_call', $name, [
            'arguments' => $this->redact_large_values($arguments),
            'result' => $this->redact_large_values($result),
        ]);

        return [
            'content' => [
                [
                    'type' => 'text',
                    'text' => wp_json_encode($result, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES),
                ],
            ],
        ];
    }

    private function list_content(string $post_type, array $arguments): array {
        $this->require_capability($post_type === 'page' ? 'edit_pages' : 'edit_posts');
        $limit = min(max(absint($arguments['limit'] ?? 20), 1), 50);
        $status = isset($arguments['status']) ? sanitize_key((string) $arguments['status']) : 'any';
        $search = isset($arguments['search']) ? sanitize_text_field((string) $arguments['search']) : '';

        $query = new WP_Query([
            'post_type' => $post_type,
            'post_status' => $status ?: 'any',
            's' => $search,
            'posts_per_page' => $limit,
            'orderby' => 'modified',
            'order' => 'DESC',
            'no_found_rows' => true,
        ]);

        $items = [];
        foreach ($query->posts as $post) {
            $items[] = $this->summarize_post($post);
        }

        return [
            'items' => $items,
            'count' => count($items),
        ];
    }

    private function get_content(string $post_type, array $arguments): array {
        $id = absint($arguments['id'] ?? 0);
        if (!$id) {
            throw new InvalidArgumentException('A valid id is required.');
        }

        $post = get_post($id);
        if (!$post || $post->post_type !== $post_type) {
            throw new RuntimeException('Content not found.');
        }

        $this->require_capability('edit_post', $id);

        return [
            'id' => $post->ID,
            'type' => $post->post_type,
            'status' => $post->post_status,
            'title' => get_the_title($post),
            'slug' => $post->post_name,
            'excerpt' => $post->post_excerpt,
            'content_raw' => $post->post_content,
            'content_rendered' => apply_filters('the_content', $post->post_content),
            'modified_gmt' => $post->post_modified_gmt,
            'link' => get_permalink($post),
        ];
    }

    private function create_draft_post(array $arguments): array {
        $this->require_capability('edit_posts');
        $title = isset($arguments['title']) ? sanitize_text_field((string) $arguments['title']) : '';
        if ($title === '') {
            throw new InvalidArgumentException('title is required.');
        }

        $post_id = wp_insert_post([
            'post_type' => 'post',
            'post_status' => 'draft',
            'post_title' => $title,
            'post_content' => wp_kses_post((string) ($arguments['content'] ?? '')),
            'post_excerpt' => sanitize_textarea_field((string) ($arguments['excerpt'] ?? '')),
            'post_name' => isset($arguments['slug']) ? sanitize_title((string) $arguments['slug']) : '',
        ], true);

        if (is_wp_error($post_id)) {
            throw new RuntimeException($post_id->get_error_message());
        }

        return [
            'id' => $post_id,
            'status' => get_post_status($post_id),
            'edit_link' => get_edit_post_link($post_id, 'raw'),
            'link' => get_permalink($post_id),
        ];
    }

    private function update_content(string $post_type, array $arguments): array {
        $id = absint($arguments['id'] ?? 0);
        if (!$id) {
            throw new InvalidArgumentException('A valid id is required.');
        }

        $post = get_post($id);
        if (!$post || $post->post_type !== $post_type) {
            throw new RuntimeException('Content not found.');
        }

        $this->require_capability('edit_post', $id);

        $data = [
            'ID' => $id,
        ];
        if (array_key_exists('title', $arguments)) {
            $data['post_title'] = sanitize_text_field((string) $arguments['title']);
        }
        if (array_key_exists('content', $arguments)) {
            $data['post_content'] = wp_kses_post((string) $arguments['content']);
        }
        if (array_key_exists('excerpt', $arguments)) {
            $data['post_excerpt'] = sanitize_textarea_field((string) $arguments['excerpt']);
        }
        if (array_key_exists('slug', $arguments)) {
            $data['post_name'] = sanitize_title((string) $arguments['slug']);
        }
        if (array_key_exists('status', $arguments)) {
            $status = sanitize_key((string) $arguments['status']);
            $allowed = ['draft', 'pending', 'private', 'publish'];
            if (!in_array($status, $allowed, true)) {
                throw new InvalidArgumentException('Unsupported status.');
            }
            if ($status === 'publish' && !current_user_can($post_type === 'page' ? 'publish_pages' : 'publish_posts')) {
                throw new RuntimeException('Current API user cannot publish this content type.');
            }
            $data['post_status'] = $status;
        }

        $updated_id = wp_update_post($data, true);
        if (is_wp_error($updated_id)) {
            throw new RuntimeException($updated_id->get_error_message());
        }

        return [
            'id' => $updated_id,
            'status' => get_post_status($updated_id),
            'modified_gmt' => get_post($updated_id)->post_modified_gmt,
            'edit_link' => get_edit_post_link($updated_id, 'raw'),
            'link' => get_permalink($updated_id),
        ];
    }

    private function upload_media_from_url(array $arguments): array {
        $this->require_capability('upload_files');
        $url = esc_url_raw((string) ($arguments['url'] ?? ''));
        if ($url === '') {
            throw new InvalidArgumentException('url is required.');
        }

        require_once ABSPATH . 'wp-admin/includes/file.php';
        require_once ABSPATH . 'wp-admin/includes/media.php';
        require_once ABSPATH . 'wp-admin/includes/image.php';

        $tmp = download_url($url, 30);
        if (is_wp_error($tmp)) {
            throw new RuntimeException($tmp->get_error_message());
        }

        $filename = basename(parse_url($url, PHP_URL_PATH) ?: 'hermes-upload');
        $file = [
            'name' => sanitize_file_name($filename),
            'tmp_name' => $tmp,
        ];

        $attachment_id = media_handle_sideload($file, 0, sanitize_text_field((string) ($arguments['title'] ?? '')));
        if (is_wp_error($attachment_id)) {
            @unlink($tmp);
            throw new RuntimeException($attachment_id->get_error_message());
        }

        if (!empty($arguments['alt_text'])) {
            update_post_meta($attachment_id, '_wp_attachment_image_alt', sanitize_text_field((string) $arguments['alt_text']));
        }

        return [
            'id' => $attachment_id,
            'url' => wp_get_attachment_url($attachment_id),
            'edit_link' => get_edit_post_link($attachment_id, 'raw'),
        ];
    }

    private function list_comments(array $arguments): array {
        $this->require_capability('moderate_comments');
        $limit = min(max(absint($arguments['limit'] ?? 20), 1), 50);
        $status = isset($arguments['status']) ? sanitize_key((string) $arguments['status']) : 'all';
        $args = [
            'number' => $limit,
            'status' => $status ?: 'all',
            'orderby' => 'comment_date_gmt',
            'order' => 'DESC',
        ];
        if (!empty($arguments['post_id'])) {
            $args['post_id'] = absint($arguments['post_id']);
        }

        $comments = get_comments($args);
        $items = array_map(static function (WP_Comment $comment): array {
            return [
                'id' => $comment->comment_ID,
                'post_id' => $comment->comment_post_ID,
                'author' => $comment->comment_author,
                'author_email' => $comment->comment_author_email,
                'status' => wp_get_comment_status($comment),
                'date_gmt' => $comment->comment_date_gmt,
                'content' => $comment->comment_content,
            ];
        }, $comments);

        return [
            'items' => $items,
            'count' => count($items),
        ];
    }

    private function update_comment_status(array $arguments): array {
        $this->require_capability('moderate_comments');
        $id = absint($arguments['id'] ?? 0);
        $status = sanitize_key((string) ($arguments['status'] ?? ''));
        if (!$id || !in_array($status, ['approve', 'hold', 'spam', 'trash'], true)) {
            throw new InvalidArgumentException('A valid id and status are required.');
        }

        $ok = wp_set_comment_status($id, $status);
        if (!$ok) {
            throw new RuntimeException('Could not update comment status.');
        }

        return [
            'id' => $id,
            'status' => wp_get_comment_status($id),
        ];
    }

    private function summarize_post(WP_Post $post): array {
        return [
            'id' => $post->ID,
            'type' => $post->post_type,
            'status' => $post->post_status,
            'title' => get_the_title($post),
            'slug' => $post->post_name,
            'modified_gmt' => $post->post_modified_gmt,
            'parent' => $post->post_parent,
            'link' => get_permalink($post),
        ];
    }

    private function require_capability(string $capability, int $object_id = 0): void {
        $user_id = $this->api_user_id();
        if ($user_id <= 0) {
            throw new RuntimeException('No API user is available for capability checks.');
        }

        wp_set_current_user($user_id);
        $allowed = $object_id > 0 ? current_user_can($capability, $object_id) : current_user_can($capability);
        if (!$allowed) {
            throw new RuntimeException('API user lacks required capability: ' . $capability);
        }
    }

    private function api_user_id(): int {
        $settings = $this->get_settings();
        return absint($settings['api_user_id'] ?? 0);
    }

    public function register_admin_page(): void {
        add_options_page(
            'Hermes MCP',
            'Hermes MCP',
            'manage_options',
            'hermes-mcp-wordpress',
            [$this, 'render_settings_page']
        );
    }

    public function register_network_admin_page(): void {
        if (!is_multisite()) {
            return;
        }

        add_submenu_page(
            'settings.php',
            'Hermes MCP Sites',
            'Hermes MCP',
            'manage_network_options',
            'hermes-mcp-wordpress-network',
            [$this, 'render_network_page']
        );
    }

    public function handle_settings_post(): void {
        if (!isset($_POST['hermes_mcp_action'])) {
            return;
        }
        if (!current_user_can('manage_options')) {
            wp_die(esc_html__('You do not have permission to manage Hermes MCP settings.', 'hermes-mcp'));
        }
        check_admin_referer('hermes_mcp_save_settings');

        $settings = $this->get_settings();
        $action = sanitize_key((string) $_POST['hermes_mcp_action']);

        if ($action === 'save') {
            $settings['enabled'] = !empty($_POST['enabled']);
            $settings['audit_enabled'] = !empty($_POST['audit_enabled']);
            $settings['api_user_id'] = absint($_POST['api_user_id'] ?? 0);
            $settings['tools'] = [];
            foreach ($this->default_tools as $tool => $default_enabled) {
                $settings['tools'][$tool] = !empty($_POST['tools'][$tool]);
            }
            update_option(self::OPTION, $settings, false);
            $this->redirect_with_notice('saved');
        }

        if ($action === 'generate_key') {
            $key = 'hmcp_' . wp_generate_password(48, false, false);
            $settings['api_key_hash'] = wp_hash_password($key);
            $settings['api_key_hint'] = substr($key, 0, 10) . '...' . substr($key, -6);
            update_option(self::OPTION, $settings, false);
            set_transient('hermes_mcp_new_key_' . get_current_user_id(), $key, 120);
            $this->redirect_with_notice('key_generated');
        }

        if ($action === 'clear_audit') {
            delete_option(self::AUDIT_OPTION);
            $this->redirect_with_notice('audit_cleared');
        }
    }

    private function redirect_with_notice(string $notice): void {
        wp_safe_redirect(add_query_arg([
            'page' => 'hermes-mcp-wordpress',
            'hermes_mcp_notice' => $notice,
        ], admin_url('options-general.php')));
        exit;
    }

    public function render_settings_page(): void {
        if (!current_user_can('manage_options')) {
            return;
        }

        $settings = $this->get_settings();
        $new_key = get_transient('hermes_mcp_new_key_' . get_current_user_id());
        if ($new_key) {
            delete_transient('hermes_mcp_new_key_' . get_current_user_id());
        }
        $audit = get_option(self::AUDIT_OPTION, []);
        if (!is_array($audit)) {
            $audit = [];
        }
        $users = get_users([
            'orderby' => 'display_name',
            'order' => 'ASC',
            'fields' => ['ID', 'display_name', 'user_login'],
        ]);

        ?>
        <div class="wrap">
            <h1>Hermes MCP for WordPress</h1>
            <p>Expose a controlled MCP endpoint for Hermes Agent. Configure each site separately when this plugin is network activated.</p>

            <?php if ($new_key): ?>
                <div class="notice notice-success">
                    <p><strong>New API key generated.</strong> Copy it now; it will not be shown again.</p>
                    <p><code style="font-size: 14px;"><?php echo esc_html($new_key); ?></code></p>
                </div>
            <?php endif; ?>

            <table class="widefat striped" style="max-width: 960px;">
                <tbody>
                    <tr>
                        <th scope="row">MCP endpoint</th>
                        <td><code><?php echo esc_html(rest_url(self::REST_NAMESPACE . self::REST_ROUTE)); ?></code></td>
                    </tr>
                    <tr>
                        <th scope="row">Health endpoint</th>
                        <td><code><?php echo esc_html(rest_url(self::REST_NAMESPACE . '/health')); ?></code></td>
                    </tr>
                    <tr>
                        <th scope="row">API key</th>
                        <td><?php echo $settings['api_key_hint'] ? esc_html($settings['api_key_hint']) : 'Not generated'; ?></td>
                    </tr>
                </tbody>
            </table>

            <form method="post" style="margin-top: 24px;">
                <?php wp_nonce_field('hermes_mcp_save_settings'); ?>
                <input type="hidden" name="hermes_mcp_action" value="save">

                <h2>Site Settings</h2>
                <p>
                    <label>
                        <input type="checkbox" name="enabled" value="1" <?php checked(!empty($settings['enabled'])); ?>>
                        Enable MCP endpoint for this site
                    </label>
                </p>
                <p>
                    <label>
                        <input type="checkbox" name="audit_enabled" value="1" <?php checked(!empty($settings['audit_enabled'])); ?>>
                        Keep audit log
                    </label>
                </p>
                <p>
                    <label for="hermes-mcp-api-user"><strong>API user for capability checks</strong></label><br>
                    <select id="hermes-mcp-api-user" name="api_user_id">
                        <option value="0">Select a WordPress user</option>
                        <?php foreach ($users as $user): ?>
                            <option value="<?php echo esc_attr((string) $user->ID); ?>" <?php selected(absint($settings['api_user_id']), absint($user->ID)); ?>>
                                <?php echo esc_html($user->display_name . ' (' . $user->user_login . ', #' . $user->ID . ')'); ?>
                            </option>
                        <?php endforeach; ?>
                    </select>
                </p>
                <p class="description">Hermes can only perform actions this WordPress user is allowed to perform. Use a dedicated Editor account for content workflows.</p>

                <h2>Enabled Tools</h2>
                <table class="widefat striped" style="max-width: 960px;">
                    <thead>
                        <tr>
                            <th>Enabled</th>
                            <th>Tool</th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php foreach ($this->default_tools as $tool => $default_enabled): ?>
                            <tr>
                                <td>
                                    <input type="checkbox" name="tools[<?php echo esc_attr($tool); ?>]" value="1" <?php checked(!empty($settings['tools'][$tool])); ?>>
                                </td>
                                <td><code><?php echo esc_html($tool); ?></code></td>
                            </tr>
                        <?php endforeach; ?>
                    </tbody>
                </table>

                <?php submit_button('Save Settings'); ?>
            </form>

            <form method="post" style="display:inline-block;">
                <?php wp_nonce_field('hermes_mcp_save_settings'); ?>
                <input type="hidden" name="hermes_mcp_action" value="generate_key">
                <?php submit_button('Generate New API Key', 'secondary', 'submit', false); ?>
            </form>

            <form method="post" style="display:inline-block; margin-left: 8px;">
                <?php wp_nonce_field('hermes_mcp_save_settings'); ?>
                <input type="hidden" name="hermes_mcp_action" value="clear_audit">
                <?php submit_button('Clear Audit Log', 'secondary', 'submit', false); ?>
            </form>

            <h2>Hermes Config Example</h2>
            <pre style="max-width: 960px; padding: 12px; background: #f6f7f7; overflow:auto;">mcp_servers:
  wordpress_<?php echo esc_html((string) get_current_blog_id()); ?>:
    url: "<?php echo esc_html(rest_url(self::REST_NAMESPACE . self::REST_ROUTE)); ?>"
    headers:
      Authorization: "Bearer YOUR_API_KEY"</pre>

            <h2>Recent Audit Log</h2>
            <table class="widefat striped" style="max-width: 960px;">
                <thead>
                    <tr>
                        <th>Time</th>
                        <th>Event</th>
                        <th>Tool</th>
                        <th>IP</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach (array_slice(array_reverse($audit), 0, 25) as $row): ?>
                        <tr>
                            <td><?php echo esc_html($row['time'] ?? ''); ?></td>
                            <td><?php echo esc_html($row['event'] ?? ''); ?></td>
                            <td><code><?php echo esc_html($row['tool'] ?? ''); ?></code></td>
                            <td><?php echo esc_html($row['ip'] ?? ''); ?></td>
                        </tr>
                    <?php endforeach; ?>
                    <?php if (!$audit): ?>
                        <tr><td colspan="4">No audit entries yet.</td></tr>
                    <?php endif; ?>
                </tbody>
            </table>
        </div>
        <?php
    }

    public function render_network_page(): void {
        if (!current_user_can('manage_network_options')) {
            return;
        }

        $sites = get_sites(['number' => 200]);
        ?>
        <div class="wrap">
            <h1>Hermes MCP Sites</h1>
            <p>Each site has independent Hermes MCP settings and API keys. Open a site dashboard to configure its endpoint.</p>
            <table class="widefat striped">
                <thead>
                    <tr>
                        <th>Site</th>
                        <th>Endpoint</th>
                        <th>Configure</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($sites as $site): ?>
                        <?php
                        switch_to_blog((int) $site->blog_id);
                        $url = rest_url(self::REST_NAMESPACE . self::REST_ROUTE);
                        $settings_url = admin_url('options-general.php?page=hermes-mcp-wordpress');
                        $name = get_bloginfo('name');
                        restore_current_blog();
                        ?>
                        <tr>
                            <td><?php echo esc_html($name); ?> <code>#<?php echo esc_html((string) $site->blog_id); ?></code></td>
                            <td><code><?php echo esc_html($url); ?></code></td>
                            <td><a href="<?php echo esc_url($settings_url); ?>">Open site settings</a></td>
                        </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        </div>
        <?php
    }

    private function audit(string $event, string $tool, array $data = []): void {
        $settings = $this->get_settings();
        if (empty($settings['audit_enabled'])) {
            return;
        }

        $rows = get_option(self::AUDIT_OPTION, []);
        if (!is_array($rows)) {
            $rows = [];
        }

        $rows[] = [
            'time' => gmdate('c'),
            'event' => $event,
            'tool' => $tool,
            'ip' => $this->client_ip(),
            'data' => $data,
        ];

        if (count($rows) > self::MAX_AUDIT_ROWS) {
            $rows = array_slice($rows, -self::MAX_AUDIT_ROWS);
        }

        update_option(self::AUDIT_OPTION, $rows, false);
    }

    private function client_ip(): string {
        $ip = $_SERVER['REMOTE_ADDR'] ?? '';
        return sanitize_text_field((string) $ip);
    }

    private function redact_large_values(array $value): array {
        $redacted = [];
        foreach ($value as $key => $item) {
            if (is_string($item) && strlen($item) > 500) {
                $redacted[$key] = substr($item, 0, 500) . '...';
            } elseif (is_array($item)) {
                $redacted[$key] = $this->redact_large_values($item);
            } else {
                $redacted[$key] = $item;
            }
        }
        return $redacted;
    }
}

register_activation_hook(__FILE__, ['Hermes_MCP_WordPress', 'activate']);
Hermes_MCP_WordPress::instance();
