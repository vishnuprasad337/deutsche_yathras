import os
from PIL import Image, ImageOps

# width -> WebP quality
MOBILE_VARIANTS = {480: 72, 768: 75}
DESKTOP_VARIANTS = {1024: 78, 1440: 80, 1920: 82}
VARIANTS = {**MOBILE_VARIANTS, **DESKTOP_VARIANTS}

MAX_ORIGINAL_WIDTH = 2200


def variant_name(name, width):
    base, _ = os.path.splitext(name)
    return f"{base}-{width}w.webp"


def variant_path(path, width):
    base, _ = os.path.splitext(path)
    return f"{base}-{width}w.webp"


def _prepare(img):
    img = ImageOps.exif_transpose(img)
    if img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGBA" if "transparency" in img.info else "RGB")
    return img


def optimize_image(path):
    if not os.path.exists(path):
        return

    with Image.open(path) as src:
        fmt = (src.format or "JPEG").upper()
        img = _prepare(src)

        original = img
        if img.width > MAX_ORIGINAL_WIDTH:
            h = round(img.height * MAX_ORIGINAL_WIDTH / img.width)
            original = img.resize((MAX_ORIGINAL_WIDTH, h), Image.LANCZOS)

        if fmt in ("JPEG", "JPG"):
            original.convert("RGB").save(path, "JPEG", quality=82, optimize=True, progressive=True)
        elif fmt == "PNG":
            original.save(path, "PNG", optimize=True)
        elif fmt == "WEBP":
            original.save(path, "WEBP", quality=82, method=6)
        else:
            original.save(path, fmt)

        for width, quality in VARIANTS.items():
            if width >= original.width:
                continue
            h = round(original.height * width / original.width)
            resized = original.resize((width, h), Image.LANCZOS)
            resized.save(variant_path(path, width), "WEBP", quality=quality, method=6)


def delete_variants(path):
    for width in VARIANTS:
        p = variant_path(path, width)
        if os.path.exists(p):
            os.remove(p)
