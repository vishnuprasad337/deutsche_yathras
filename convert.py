from PIL import Image
import os

B = "static/frontend/"
jobs = [
    # (source, output, max width or None, quality)
    ("hero.webp", "hero-768.webp", 768, 75),
    ("assets/images/about/image-2.jpg", "assets/images/about/image-2.webp", 900, 78),
    ("assets/images/home/airplane.png", "assets/images/home/airplane.webp", 600, 80),
    ("map.png", "map.webp", 920, 80),
    ("tr.png", "tr.webp", 1000, 80),
    ("re.png", "re.webp", 1400, 80),
]

for src, out, w, q in jobs:
    p = B + src
    if not os.path.exists(p):
        print("MISSING", p)
        continue
    im = Image.open(p)
    if im.mode not in ("RGB", "RGBA"):
        im = im.convert("RGBA")
    if w and im.width > w:
        im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
    im.save(B + out, "WEBP", quality=q, method=6)
    print("OK", out, im.size, os.path.getsize(p) // 1024, "KB ->", os.path.getsize(B + out) // 1024, "KB")
