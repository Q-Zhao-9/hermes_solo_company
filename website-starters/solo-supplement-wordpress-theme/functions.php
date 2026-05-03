<?php

declare(strict_types=1);

require_once get_template_directory() . '/inc/storefront-data.php';

function solo_supplement_theme_setup(): void
{
    add_theme_support('title-tag');
    add_theme_support('post-thumbnails');
    add_theme_support('menus');

    register_nav_menus([
        'primary' => __('Primary Menu', 'solo-supplement-wordpress-theme'),
    ]);
}
add_action('after_setup_theme', 'solo_supplement_theme_setup');

function solo_supplement_enqueue_assets(): void
{
    wp_enqueue_style(
        'solo-supplement-style',
        get_stylesheet_uri(),
        [],
        wp_get_theme()->get('Version')
    );
}
add_action('wp_enqueue_scripts', 'solo_supplement_enqueue_assets');

function solo_supplement_get_current_slug(): string
{
    global $post;

    if ($post instanceof WP_Post) {
        return $post->post_name;
    }

    return '';
}
