import hashlib

from django import template
from django.core.cache import cache

from ..utils.image_optimizer import (
    VARIANTS, MOBILE_VARIANTS, DESKTOP_VARIANTS, variant_name,
)

register = template.Library()

CACHE_SECONDS = 60 * 60 * 24
FALLBACK_WIDTH = 1920


def _original_width(field_file):
    try:
        return field_file.width
    except Exception:
        return FALLBACK_WIDTH


def _build(field_file, widths, include_original):
    if not field_file or not getattr(field_file, "name", None):
        return ""

    tag = f"{min(widths)}-{max(widths)}-{int(include_original)}"
    key = "srcset:" + tag + hashlib.md5(field_file.name.encode()).hexdigest()
    cached = cache.get(key)
    if cached is not None:
        return cached

    storage = field_file.storage
    original_w = _original_width(field_file)

    parts = []
    for width in sorted(widths):
        if width >= original_w:
            continue
        name = variant_name(field_file.name, width)
        if storage.exists(name):
            parts.append(f"{storage.url(name)} {width}w")

    if include_original or not parts:
        parts.append(f"{field_file.url} {original_w}w")

    result = ", ".join(parts)
    if len(parts) > 1:
        cache.set(key, result, CACHE_SECONDS)
    return result


@register.filter
def srcset(field_file):
    return _build(field_file, VARIANTS, True)


@register.filter
def mobile_srcset(field_file):
    return _build(field_file, MOBILE_VARIANTS, False)


@register.filter
def desktop_srcset(field_file):
    return _build(field_file, DESKTOP_VARIANTS, True)
