#!/usr/bin/env python3
"""Encode every image the site serves into responsive WebP, and write a manifest.

The repository holds the artist's masters: multi-megabyte PNGs and 4000px
photographs. Nothing here is thrown away — the originals stay untouched and this
script derives the renditions the pages actually link to.

    python3 tools/build-images.py     # → images/{gallery,plates,exhibition,page}/
                                      # → tools/site.json

Requires Pillow.
"""
from __future__ import annotations

import base64
import io
import json
import os
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from artworks import ARTWORKS, EXHIBITION_PHOTOS, PAGE_IMAGES, PLATES, Art  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

LADDERS = {
    "gallery": (400, 640, 900, 1400, 1800),   # portfolio cards + lightbox
    "plates": (500, 900, 1300),               # in-situ views on an artwork page
    "exhibition": (450, 800, 1300),           # exhibition photographs
    "page": (800, 1400, 1800),                # portraits and page headers
}
# The canvases carry the work and deserve the bit budget; the photographs
# around them are context and compress harder without anyone noticing.
QUALITY = {"gallery": 82, "plates": 76, "exhibition": 76, "page": 80}

# A thumbnail this wide is a genuine master; anything smaller is a letterbox
# crop from the old template build and the artwork page holds a better plate.
GOOD_THUMB_WIDTH = 900
AR_TOLERANCE = 0.06
# Same-canvas renditions score below this; room mock-ups and outdoor photos of
# the canvas score above 1.0, which is also what makes them worth showing.
LIKENESS_LIMIT = 0.7


# --------------------------------------------------------------------- images

def load(path: str) -> Image.Image | None:
    """Open an image, trimming the transparent sheet a plate is mounted on."""
    full = os.path.join(ROOT, path)
    if not os.path.exists(full):
        return None
    im = Image.open(full)
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA")
        bbox = im.getchannel("A").getbbox()
        if bbox:
            im = im.crop(bbox)
        # Composite onto the wall rather than dropping alpha: a cut-out keeps
        # clean edges instead of inheriting whatever sat under the transparency.
        wall = Image.new("RGB", im.size, (255, 255, 255))
        wall.paste(im, mask=im.getchannel("A"))
        return wall
    return im.convert("RGB")


def signature(im: Image.Image) -> list[float]:
    """Contrast-normalised 32×32 luminance fingerprint: scale and colour blind."""
    px = list(im.convert("L").resize((32, 32), Image.LANCZOS).get_flattened_data())
    mean = sum(px) / len(px)
    sd = (sum((p - mean) ** 2 for p in px) / len(px)) ** 0.5 or 1.0
    return [(p - mean) / sd for p in px]


def likeness(a: list[float], b: list[float]) -> float:
    return (sum((x - y) ** 2 for x, y in zip(a, b)) / len(a)) ** 0.5


def lqip(im: Image.Image) -> str:
    """A 20px inline placeholder — the blur the card shows before the paint."""
    tiny = im.resize((20, max(1, round(20 * im.height / im.width))), Image.LANCZOS)
    buf = io.BytesIO()
    tiny.save(buf, "WEBP", quality=45, method=6)
    return "data:image/webp;base64," + base64.b64encode(buf.getvalue()).decode()


def encode(im: Image.Image, folder: str, stem: str, ladder: str) -> dict:
    """Write the WebP ladder for one image and describe it for the manifest."""
    out_dir = os.path.join(ROOT, "images", folder)
    os.makedirs(out_dir, exist_ok=True)
    steps = LADDERS[ladder]
    widths = sorted({*(w for w in steps if w <= im.width), min(im.width, steps[-1])})

    srcset = []
    for width in widths:
        height = max(1, round(width * im.height / im.width))
        name = f"{stem}-{width}.webp"
        im.resize((width, height), Image.LANCZOS).save(
            os.path.join(out_dir, name), "WEBP", quality=QUALITY[ladder], method=6)
        srcset.append({"w": width, "src": f"images/{folder}/{name}"})

    return {"w": im.width, "h": im.height, "lqip": lqip(im), "srcset": srcset}


# ---------------------------------------------------------------- the sources

def resolve(art: Art) -> tuple[Image.Image, list[Image.Image]]:
    """Split an artwork's sources into the canvas itself and its other views."""
    base = load(art.thumb)
    assert base is not None, f"missing source for {art.slug}"
    base_sig = signature(base)

    # From the catalogue, never from the pages: this build regenerates them.
    candidates = [im for plate in PLATES.get(art.slug, [])
                  for im in [load(plate)] if im is not None]

    same, other = [], []
    for im in candidates:
        (same if likeness(base_sig, signature(im)) <= LIKENESS_LIMIT else other).append(im)

    # The old 442px thumbnails crop into the canvas; the plate shows all of it.
    reference = base if (base.width >= GOOD_THUMB_WIDTH or not same) else same[0]
    ratio = reference.width / reference.height
    canvases = [im for im in [base, *same] if abs(im.width / im.height - ratio) / ratio <= AR_TOLERANCE]

    return max(canvases or [base], key=lambda im: im.width), other


# ---------------------------------------------------------------------- build

def main() -> None:
    manifest = {"works": [], "exhibition": [], "page": {}}
    source_bytes = 0

    for art in ARTWORKS:
        canvas, views = resolve(art)
        source_bytes += os.path.getsize(os.path.join(ROOT, art.thumb))

        entry = {
            "slug": art.slug, "title": art.title, "page": art.page,
            "medium": art.medium, "year": art.year, "size": art.size,
            "price": art.price, "sold": art.sold, "status": art.status, "tag": art.tag,
            "canvas": encode(canvas, "gallery", art.slug, "gallery"),
            "views": [encode(v, "plates", f"{art.slug}-view-{i + 1}", "plates")
                      for i, v in enumerate(views)],
        }
        manifest["works"].append(entry)
        print(f"  {art.slug:22} canvas {canvas.width}×{canvas.height}  + {len(views)} view(s)")

    for i, photo in enumerate(EXHIBITION_PHOTOS, 1):
        im = load(photo)
        if im is None:
            print(f"  ! missing exhibition photo {photo}")
            continue
        manifest["exhibition"].append(encode(im, "exhibition", f"noho-{i:02d}", "exhibition"))
    print(f"  exhibition             {len(manifest['exhibition'])} photographs")

    for key, path in PAGE_IMAGES.items():
        im = load(path)
        assert im is not None, f"missing page image {path}"
        manifest["page"][key] = encode(im, "page", key, "page")
    print(f"  page images            {len(manifest['page'])}")

    with open(os.path.join(HERE, "site.json"), "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=1)

    derived = sum(
        os.path.getsize(os.path.join(dirpath, name))
        for folder in LADDERS
        for dirpath, _, names in os.walk(os.path.join(ROOT, "images", folder))
        for name in names
    )
    print(f"\nsources for the works: {source_bytes / 1e6:.1f} MB")
    print(f"derived renditions:    {derived / 1e6:.1f} MB across every size")


if __name__ == "__main__":
    main()
