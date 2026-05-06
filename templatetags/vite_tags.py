"""
Vite manifest loader for hashed assets.
Path: templatetags/vite_tags.py
"""

import json
from django import template
from django.conf import settings
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag
def vite_css():
    """Get Vite built CSS file path from manifest."""
    # Thử tìm manifest ở cả 2 vị trí (cũ và mới)
    manifest_path_v1 = settings.BASE_DIR / 'static/dist/manifest.json'
    manifest_path_v2 = settings.BASE_DIR / 'static/dist/.vite/manifest.json'
    
    manifest_path = None
    if manifest_path_v2.exists():
        manifest_path = manifest_path_v2
    elif manifest_path_v1.exists():
        manifest_path = manifest_path_v1
    
    if manifest_path and manifest_path.exists():
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
        
        # Thu thập tất cả file CSS từ manifest
        css_files = []
        for entry_name, entry_info in manifest.items():
            if 'css' in entry_info:
                for css_file in entry_info['css']:
                    css_files.append(css_file)
        
        # Tạo thẻ link
        links = []
        for css_file in css_files:
            links.append(f'<link rel="stylesheet" href="/static/dist/{css_file}">')
        
        if links:
            return mark_safe('\n'.join(links))
    
    return ''

@register.simple_tag
def vite_js(entry_name='main.js'):
    """Get Vite built JS file path from manifest."""
    # Thử tìm manifest ở cả 2 vị trí
    manifest_path_v1 = settings.BASE_DIR / 'static/dist/manifest.json'
    manifest_path_v2 = settings.BASE_DIR / 'static/dist/.vite/manifest.json'
    
    manifest_path = None
    if manifest_path_v2.exists():
        manifest_path = manifest_path_v2
    elif manifest_path_v1.exists():
        manifest_path = manifest_path_v1
    
    if manifest_path and manifest_path.exists():
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
        
        # Tìm entry point trong manifest
        for key, entry_info in manifest.items():
            # So sánh tên file (có thể là 'main.js' hoặc 'src/js/main.js')
            if key == entry_name or key.endswith(entry_name) or entry_name in key:
                if 'file' in entry_info:
                    return mark_safe(f'<script type="module" src="/static/dist/{entry_info["file"]}"></script>')
        
        # Fallback: lấy entry đầu tiên có file
        for entry_info in manifest.values():
            if 'file' in entry_info and entry_info['file'].endswith('.js'):
                return mark_safe(f'<script type="module" src="/static/dist/{entry_info["file"]}"></script>')
    
    return ''