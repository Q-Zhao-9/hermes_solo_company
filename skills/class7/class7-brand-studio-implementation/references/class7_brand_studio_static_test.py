#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

SITE_ROOT = Path(__file__).resolve().parent
DOCS_ROOT = SITE_ROOT / 'docs' / 'class7'


def assert_student_workspace_markers() -> None:
    html = (SITE_ROOT / 'student-workspace.html').read_text(encoding='utf-8')
    for token in [
        'data-student-panel-target="brand-studio"',
        'data-student-panel="brand-studio"',
        'data-student-brand-studio-panel',
        'data-class7-brand-form',
        'data-class7-demo-load',
        'data-class7-generate-directions',
        'data-class7-generate-prompt-pack',
        'data-class7-generate-design-system',
        'data-class7-generate-website-workflow',
        'data-class7-website-workflow-output',
        'data-class7-direction-output',
        'data-class7-prompt-pack-output',
        'data-class7-design-system-output',
        'data-class7-website-workflow-output',
        'data-class7-generate-website-workflow',
        'Class 7 / AI Brand &amp; Visual System',
        'creative direction, not final approved branding',
        '需要先选定一个品牌方向',
        'docs/class7/demo-inputs.md',
        'docs/class7/brand-brief-template.md',
    ]:
        assert token in html, f'{token} missing from student-workspace.html'


def assert_admin_console_markers() -> None:
    html = (SITE_ROOT / 'admin.html').read_text(encoding='utf-8')
    for token in [
        'data-admin-panel-target="brand-studio"',
        'data-admin-panel="brand-studio"',
        'data-admin-brand-studio-panel',
        'data-admin-brand-doc-list',
        'data-admin-brand-phase-plan',
        'Brand Studio',
        'docs/plans/2026-06-15-class7-brand-studio-implementation-plan.md',
        'docs/class7/brand-visual-system/SKILL.md',
        'docs/class7/website-brand-integration-checklist.md',
        'docs/design-system.md',
        'data-class7-website-workflow-output',
    ]:
        assert token in html, f'{token} missing from admin.html'


def assert_site_auth_markers() -> None:
    js = (SITE_ROOT / 'site-auth.js').read_text(encoding='utf-8')
    for token in [
        'initClass7BrandStudio',
        'loadClass7BrandDemo',
        'buildClass7BrandDirections',
        'buildClass7PromptPack',
        'buildClass7DesignSystem',
        'buildClass7WebsiteWorkflow',
        'renderClass7BrandOutput',
        'data-class7-brand-form',
        'data-class7-demo-load',
        'data-class7-generate-directions',
        'data-class7-generate-prompt-pack',
        'data-class7-generate-design-system',
        'data-class7-generate-website-workflow',
        'data-class7-website-workflow-output',
        'creative direction, not final approved branding',
        'docs/class7/demo-inputs.md',
    ]:
        assert token in js, f'{token} missing from site-auth.js'


def assert_prompt_image_generation_cleanup() -> None:
    student_js = (SITE_ROOT / 'student-workspace-page.js').read_text(encoding='utf-8')
    admin_js = (SITE_ROOT / 'admin-console-page.js').read_text(encoding='utf-8')
    student_html = (SITE_ROOT / 'student-workspace.html').read_text(encoding='utf-8')
    admin_html = (SITE_ROOT / 'admin.html').read_text(encoding='utf-8')
    gateway_js = (SITE_ROOT / 'modules' / 'website_chatbot' / 'backend' / 'site_gateway.py').read_text(encoding='utf-8')
    for content, label in [
        (student_js, 'student-workspace-page.js'),
        (admin_js, 'admin-console-page.js'),
    ]:
        for token in [
            'data-class7-generate-asset-image',
            'Generate 4 variants',
            'Upload image',
            'data-class7-select-asset',
            '/api/class7/assets/generate',
            '/api/class7/assets/upload',
            '/api/class7/assets/select',
        ]:
            assert token in content, f'{token} missing from {label}'
    for content, label in [
        (student_html, 'student-workspace.html'),
        (admin_html, 'admin.html'),
    ]:
        assert 'Copy website build handoff' in content, f'Copy website build handoff missing from {label}'
    for token in [
        '/api/class7/assets/generate',
        '/api/class7/assets/upload',
        '/api/class7/assets/select',
        'class7/brand-visual-system',
    ]:
        assert token in gateway_js, f'{token} missing from site_gateway.py'


def assert_styles_markers() -> None:
    css = (SITE_ROOT / 'styles.css').read_text(encoding='utf-8')
    for token in [
        '.brand-studio-hero',
        '.brand-studio-grid',
        '.brand-direction-card',
        '.brand-prompt-pack',
        '.brand-design-system-card',
        '.brand-chip-list',
        '.brand-website-workflow-card',
        '.brand-studio-hero-metrics',
    ]:
        assert token in css, f'{token} missing from styles.css'


def assert_docs() -> None:
    design_system = SITE_ROOT / 'docs' / 'design-system.md'
    assert design_system.exists(), f'{design_system} should exist'
    design_system_text = design_system.read_text(encoding='utf-8')
    for token in ['# Design System', '## Brand Direction', '## Color Palette', '## Implementation Notes']:
        assert token in design_system_text, f'{token} missing from {design_system}'

    files_and_tokens = {
        DOCS_ROOT / 'brand-brief-template.md': ['# Class 7 Brand Brief Template', 'Target audience', 'Visual direction'],
        DOCS_ROOT / 'brand-brief-template-zh.md': ['# 第 7 课品牌 brief 模板', '目标用户', '视觉方向'],
        DOCS_ROOT / 'demo-inputs.md': ['# Class 7 Demo Inputs', 'brand brief', 'hero image'],
        DOCS_ROOT / 'demo-inputs-zh.md': ['# 第 7 课演示输入', '品牌 brief', '首屏图'],
        DOCS_ROOT / 'demo-output-example.md': ['# Class 7 Demo Output Example', 'Direction A', 'Prompt pack'],
        DOCS_ROOT / 'demo-output-example-zh.md': ['# 第 7 课演示输出示例', '方向 A', 'Prompt pack'],
        DOCS_ROOT / 'design-system-example.md': ['# Class 7 Design System Example', 'Color palette', 'Typography'],
        DOCS_ROOT / 'design-system-example-zh.md': ['# 第 7 课设计系统示例', '颜色方案', '字体'],
        DOCS_ROOT / 'website-brand-integration-checklist.md': ['# Website Brand Integration Checklist', 'homepage hero', 'CTA'],
        DOCS_ROOT / 'website-brand-integration-checklist-zh.md': ['# 网站品牌接入检查清单', '首页首屏', 'CTA'],
        DOCS_ROOT / 'test-checklist.md': ['# Class 7 Test Checklist', 'brand direction', 'design system'],
        DOCS_ROOT / 'test-checklist-zh.md': ['# 第 7 课测试清单', '品牌方向', '设计系统'],
        DOCS_ROOT / 'brand-visual-system' / 'SKILL.md': ['# Class 7 Brand Visual System Skill', 'Trigger', 'Outputs'],
    }
    for path, tokens in files_and_tokens.items():
        assert path.exists(), f'{path} should exist'
        content = path.read_text(encoding='utf-8')
        for token in tokens:
            assert token in content, f'{token} missing from {path}'


def main() -> None:
    assert_student_workspace_markers()
    assert_admin_console_markers()
    assert_site_auth_markers()
    assert_prompt_image_generation_cleanup()
    assert_styles_markers()
    assert_docs()
    print('class7_brand_studio_static_test: PASS')


if __name__ == '__main__':
    main()
