#!/usr/bin/env python3
"""Build responsive, weight-optimised gallery derivatives for the portfolio page.

For every artwork we pick the highest-resolution master available in the repo
(the thumbnail itself, or a larger plate referenced by the artwork's own detail
page, alpha-trimmed to the canvas), then emit a WebP ladder plus a base64 LQIP
used for the blur-up placeholder.
"""
from __future__ import annotations

import base64
import io
import json
import os
import re
from dataclasses import dataclass, field

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "images", "gallery")
WIDTHS = (400, 640, 900, 1400, 1800)
# Thumbnails below this width are template crops from the old build, not real
# sources: for those we fall back to the artwork plate on the detail page.
GOOD_THUMB_WIDTH = 900
AR_TOLERANCE = 0.06
# Plates on a detail page also include room mock-ups and photos of the canvas
# outdoors. Same-canvas renditions score < 0.6 here, foreign shots score > 1.0.
LIKENESS_LIMIT = 0.7
SKIP_PLATE = ("environment", "gallery", "mock")


@dataclass
class Art:
    slug: str
    title: str
    page: str
    thumb: str
    medium: str
    year: int
    size: str
    price: str = ""
    sold: bool = False
    ladder: list = field(default_factory=list)


ARTWORKS = [
    Art("summer-2025", "Summer", "summer-2025.html", "images/summer.png", "Oil", 2025, "120 × 120 × 3 cm", "€2900"),
    Art("the-red", "The Red", "the-red.html", "images/THE RED 1.png", "Oil", 2025, "130 × 130 cm", sold=True),
    Art("breath-of-light", "Breath of Light", "Breath-of-Light.html", "images/Breath-of-Light.png", "Oil", 2025, "100 × 100 cm", sold=True),
    Art("the-blue", "The Blue", "the-blue.html", "images/the_blue.png", "Oil", 2025, "120 × 120 cm", sold=True),
    Art("earth-vision", "Earth Vision", "Earth-vision.html", "images/Les-deux-tableaux-portfolio.png", "Oil", 2025, "65 × 100 × 3 cm", "€2600"),
    Art("serenity-of-motion", "Serenity of Motion", "serenity-of-motion.html", "images/serenity-of-motion-imageneavant.png", "Oil", 2025, "130 × 130 × 3 cm", "€3800"),
    Art("flow-of-energy", "Flow of Energy", "flow-of-energy.html", "images/FLOW-OF-ENERGY.png", "Oil", 2024, "100 × 100 × 3 cm", "€2300"),
    Art("whispers-of-pink", "Whispers of Pink", "whispers-of-pink.html", "images/WHISPERS-OF-PINK.png", "Oil", 2024, "100 × 100 × 3 cm", "€2200"),
    Art("blue-shadows", "Blue Shadows", "blue-shadows.html", "images/BLUE-SHADOWS.png", "Oil", 2024, "100 × 100 × 3 cm", "€2400"),
    Art("passion-palette", "Passion Palette", "passion-palette.html", "images/image-04-442x332.png", "Oil", 2023, "150 × 200 × 5 cm", "€6700"),
    Art("midnight-whispers", "Midnight Whispers", "midnight-whispers.html", "images/image-11.png", "Oil", 2023, "150 × 100 × 3 cm", sold=True),
    Art("sensuality", "Sensuality", "sensuality.html", "images/sensuality-07.webp", "Oil", 2023, "150 × 150 × 5 cm", "€5400"),
    Art("feeling-flow", "Feeling Flow", "feeling-flow.html", "images/image-18.webp", "Oil", 2023, "100 × 100 × 3 cm", "€2200"),
    Art("blue-bubble", "Blue Bubble", "blue-bubble.html", "images/image-23.webp", "Oil", 2023, "100 × 100 × 3 cm", "€2300"),
    Art("sunset-silhouettes", "Sunset Silhouettes", "sunset-silhouettes.html", "images/image-24.webp", "Oil", 2023, "100 × 100 × 3 cm", "€2300"),
    Art("deep-blue-lagoon", "Deep Blue Lagoon", "deep-blue-lagoon.html", "images/image-25.webp", "Oil", 2023, "100 × 100 × 3 cm", sold=True),
    Art("the-dark-and-light", "The Dark and Light", "the-dark-and-light.html", "images/image-29.webp", "Oil", 2023, "100 × 120 × 3 cm", "€2400"),
    Art("harmony", "Harmony", "harmony.html", "images/harmony-2.png", "Oil", 2023, "60 × 80 × 2 cm", sold=True),
    Art("rise-like-a-sun", "Rise Like a Sun", "rise-like-a-sun.html", "images/image-09-442x332.webp", "Oil", 2022, "100 × 100 × 4 cm", sold=True),
    Art("the-curve", "The Curve", "the-curve.html", "images/image-08-442x442.webp", "Oil", 2022, "100 × 100 × 4 cm", "€2300"),
    Art("in-shades-of-pink", "In Shades of Pink", "in-shades-of-pink.html", "images/image-2-442x332.webp", "Acrylic", 2022, "100 × 120 × 3 cm", "€2000"),
    Art("blue-white", "Blue White", "blue-white.html", "images/image-21-442x332.webp", "Oil", 2022, "100 × 100 × 4 cm", sold=True),
    Art("waves", "Waves", "waves.html", "images/image-21.webp", "Oil", 2022, "100 × 120 × 2 cm", "€2400"),
    Art("deep-blue", "Deep Blue", "deep-blue.html", "images/image-27.webp", "Acrylic", 2022, "100 × 120 × 3 cm", "€1900"),
    Art("the-wall", "The Wall", "the-wall.html", "images/image-28.webp", "Oil", 2022, "100 × 100 × 2 cm", "€2200"),
    Art("summer-2022", "Summer", "summer.html", "images/image-30.webp", "Oil", 2022, "80 × 60 × 4 cm", sold=True),
    Art("intensity", "Intensity", "intensity.html", "images/image-31.webp", "Oil", 2022, "60 × 80 × 4 cm", "€1500"),
    Art("the-7-hearts", "The 7 Hearts", "the-7-hearts.html", "images/image-32.webp", "Oil", 2022, "100 × 120 × 4 cm", "€2300"),
    Art("nightfall", "Nightfall", "nightfall.html", "images/image-05.webp", "Oil", 2021, "80 × 80 × 4 cm", "€1600"),
    Art("the-white-cross", "The White Cross", "the-white-cross.html", "images/image-3-442x332.webp", "Oil", 2020, "80 × 100 × 2 cm", "€1700"),
    Art("the-red-wall", "The Red Wall", "the-red-wall.html", "images/image-22.webp", "Oil", 2019, "97 × 130 × 2 cm", "€2500"),
    Art("freedom-and-love", "Freedom and Love", "freedom-and-love.html", "images/image-06.webp", "Oil", 2013, "100 × 100 × 4 cm", sold=True),
    Art("fly-like-a-bird", "Fly Like a Bird", "fly-like-a-bird.html", "images/image-07.webp", "Oil", 2012, "100 × 100 × 4 cm", sold=True),
    Art("the-circle", "The Circle", "the-circle.html", "images/image-16.webp", "Oil", 2012, "100 × 100 × 4 cm", "€2100"),
    Art("mystic-flames", "Mystic Flames", "mystic-flames.html", "images/image-14.webp", "Oil", 2010, "100 × 100 × 2 cm", "€2200"),
    Art("winter", "Winter", "winter.html", "images/image-12.webp", "Oil", 2009, "54 × 65 × 2 cm", "€1500"),
]


def load_trimmed(path: str) -> Image.Image | None:
    """Open an image and trim the transparent margin the plates are mounted on."""
    if not os.path.exists(path):
        return None
    im = Image.open(path)
    if im.mode in ("RGBA", "LA"):
        bbox = im.getchannel("A").getbbox()
        if bbox:
            im = im.crop(bbox)
    return im.convert("RGB")


def detail_plates(page: str) -> list[str]:
    """Hi-res plates referenced by an artwork's own detail page, in slide order."""
    path = os.path.join(ROOT, page)
    if not os.path.exists(path):
        return []
    html = open(path, encoding="utf-8", errors="ignore").read()
    return [m.replace("&#32;", " ") for m in re.findall(r'data-slide-bg="(images/[^"]+)"', html)]


def signature(im: Image.Image) -> list[float]:
    """Contrast-normalised 32×32 luminance fingerprint, scale and colour agnostic."""
    px = list(im.convert("L").resize((32, 32), Image.LANCZOS).get_flattened_data())
    mean = sum(px) / len(px)
    sd = (sum((p - mean) ** 2 for p in px) / len(px)) ** 0.5 or 1.0
    return [(p - mean) / sd for p in px]


def likeness(a: list[float], b: list[float]) -> float:
    return (sum((x - y) ** 2 for x, y in zip(a, b)) / len(a)) ** 0.5


def pick_master(art: Art) -> Image.Image:
    """The truest, highest-resolution rendition of a canvas available in the repo."""
    base = load_trimmed(os.path.join(ROOT, art.thumb))
    assert base is not None, f"missing thumbnail for {art.slug}"

    base_sig = signature(base)
    plates = [
        img
        for plate in detail_plates(art.page)
        if not any(tag in plate.lower() for tag in SKIP_PLATE)
        for img in [load_trimmed(os.path.join(ROOT, plate))]
        if img is not None and likeness(base_sig, signature(img)) <= LIKENESS_LIMIT
    ]

    # A 442px thumbnail is a letterbox crop from the old build, so the canvas on
    # the artwork's own page defines the true framing. A large thumbnail is a
    # genuine source and defines it itself.
    if base.width >= GOOD_THUMB_WIDTH or not plates:
        ref_ar = base.width / base.height
    else:
        ref_ar = plates[0].width / plates[0].height

    candidates = [im for im in [base, *plates] if abs(im.width / im.height - ref_ar) / ref_ar <= AR_TOLERANCE]
    return max(candidates or [base], key=lambda im: im.width)


def lqip(im: Image.Image) -> str:
    tiny = im.resize((20, max(1, round(20 * im.height / im.width))), Image.LANCZOS)
    buf = io.BytesIO()
    tiny.save(buf, "WEBP", quality=45, method=6)
    return "data:image/webp;base64," + base64.b64encode(buf.getvalue()).decode()


def main() -> None:
    os.makedirs(OUT_DIR, exist_ok=True)
    manifest, saved, before = [], 0, 0

    for art in ARTWORKS:
        master = pick_master(art)
        before += os.path.getsize(os.path.join(ROOT, art.thumb))
        # Never upscale; 1800px is ample for the lightbox on any display. The
        # master's own width joins the ladder so odd-sized plates aren't wasted.
        widths = sorted({*(w for w in WIDTHS if w <= master.width), min(master.width, WIDTHS[-1])})

        ladder = []
        for w in widths:
            h = max(1, round(w * master.height / master.width))
            out = os.path.join(OUT_DIR, f"{art.slug}-{w}.webp")
            master.resize((w, h), Image.LANCZOS).save(out, "WEBP", quality=82, method=6)
            ladder.append({"w": w, "src": f"images/gallery/{art.slug}-{w}.webp"})
            saved += os.path.getsize(out)

        manifest.append({
            "slug": art.slug,
            "title": art.title,
            "page": art.page,
            "medium": art.medium,
            "year": art.year,
            "size": art.size,
            "price": art.price,
            "sold": art.sold,
            "w": master.width,
            "h": master.height,
            "lqip": lqip(master),
            "srcset": ladder,
        })
        print(f"{art.slug:22} master {master.width}×{master.height}  →  {len(ladder)} renditions")

    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "gallery.json"), "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=1)

    print(f"\nthumbnail payload before: {before/1e6:.1f} MB")
    print(f"full webp ladder after:   {saved/1e6:.1f} MB (all sizes combined)")


if __name__ == "__main__":
    main()
