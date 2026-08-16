#!/usr/bin/env python3
"""Render portfolio.html from the gallery manifest and the page shell."""
from __future__ import annotations

import html
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SIZES = "(max-width:559px) 92vw, (max-width:899px) 46vw, (max-width:1399px) 31vw, 23vw"
EAGER = 3  # cards likely to be in view on a short viewport
AURA = ("the-red", "flow-of-energy", "the-blue", "whispers-of-pink", "mystic-flames")

ZOOM_ICON = (
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" '
    'stroke-linecap="round" aria-hidden="true"><path d="M4 9V4h5M20 15v5h-5M15 4h5v5M9 20H4v-5"/></svg>'
)


def card_markup(art: dict, index: int) -> str:
    e = html.escape
    srcset = ", ".join(f"{s['src'].replace(' ', '%20')} {s['w']}w" for s in art["srcset"])
    default = next((s for s in art["srcset"] if s["w"] >= 640), art["srcset"][-1])
    status = "sold" if art["sold"] else "available"
    tag = "Collected" if art["sold"] else (art["price"] or "On request")
    loading = "eager" if index < EAGER else "lazy"
    alt = f'{art["title"]} — {art["medium"].lower()} painting, {art["year"]}'

    return f"""        <article class="card" role="listitem" data-order="{index}" data-title="{e(art['title'])}"
          data-medium="{art['medium']}" data-year="{art['year']}" data-status="{status}">
          <div class="card__inner">
            <a class="card__link" href="{e(art['page'])}">
              <div class="card__frame" style="aspect-ratio:{art['w']}/{art['h']};background-image:url({art['lqip']})">
                <img src="{default['src'].replace(' ', '%20')}" srcset="{srcset}" sizes="{SIZES}"
                  width="{art['w']}" height="{art['h']}" alt="{e(alt)}" loading="{loading}" decoding="async">
              </div>
              <div class="card__body">
                <div>
                  <h3 class="card__title">{e(art['title'])}</h3>
                  <p class="card__spec"><span>{art['medium']}</span><span>{art['year']}</span><span>{e(art['size'])}</span></p>
                </div>
                <p class="card__tag"{' data-sold' if art['sold'] else ''}>{e(tag)}</p>
              </div>
            </a>
            <button class="card__zoom" type="button" data-zoom
              aria-label="View {e(art['title'])} full size">{ZOOM_ICON}</button>
          </div>
        </article>"""


def main() -> None:
    works = json.load(open(os.path.join(HERE, "gallery.json"), encoding="utf-8"))
    shell = open(os.path.join(HERE, "portfolio.template.html"), encoding="utf-8").read()

    years = sorted({w["year"] for w in works}, reverse=True)
    by_slug = {w["slug"]: w for w in works}

    replacements = {
        "{{CARDS}}": "\n".join(card_markup(w, i) for i, w in enumerate(works)),
        "{{COUNT}}": str(len(works)),
        "{{AVAILABLE}}": str(sum(not w["sold"] for w in works)),
        "{{YEAR_MIN}}": str(min(years)),
        "{{YEAR_MAX}}": str(max(years)),
        "{{YEAR_OPTIONS}}": "".join(f'\n          <option value="{y}">{y}</option>' for y in years),
        "{{TITLE_LETTERS}}": "".join(
            f'<span style="--i:{i}">{c}</span>' for i, c in enumerate("Portfolio")
        ),
        "{{AURA}}": "".join(
            f'<span style="--i:{i};background-image:url({by_slug[slug]["lqip"]})"></span>'
            for i, slug in enumerate(AURA)
        ),
        "{{OG_SLUG}}": works[0]["slug"],
    }

    page = shell
    for token, value in replacements.items():
        page = page.replace(token, value)

    assert "{{" not in page, "unresolved template token"

    out = os.path.join(ROOT, "portfolio.html")
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(page)
    print(f"wrote {out} — {len(page) / 1024:.1f} KB, {len(works)} works")


if __name__ == "__main__":
    main()
