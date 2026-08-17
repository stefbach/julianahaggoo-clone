#!/usr/bin/env python3
"""Render every page of the site, in every language, from the catalogue.

    python3 tools/build-images.py     # first: renditions + tools/site.json
    python3 tools/build-site.py       # then:  the pages

English sits at the repository root so the live URLs never moved; French sits
under fr/ with the same file names, so switching language is a path swap and
nothing else. Every page shares css/atelier.css and js/atelier.js.
"""
from __future__ import annotations

import html
import json
import os
import sys
from urllib.parse import quote

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from artworks import ARTWORKS, HOME_SLIDES, STUDIO  # noqa: E402
from i18n import HOME, LOCALES, TIMELINE, UP, medium, t, tag  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

FONTS = ("https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;"
         "1,300;1,400&family=Italiana&display=swap")

# How long a carousel slide holds before the next one arrives.
SLIDE_DWELL_MS = 3500

SIZES = {
    "card": "(max-width:559px) 92vw, (max-width:979px) 46vw, 30vw",
    "third": "(max-width:60em) 92vw, 30vw",
    "half": "(max-width:58em) 92vw, 46vw",
    "canvas": "(max-width:62em) 92vw, 62vw",
    "wide": "(max-width:60em) 92vw, 68vw",
    "photo": "(max-width:40em) 92vw, (max-width:70em) 46vw, 23vw",
    "slide": "100vw",
}

ZOOM_ICON = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" '
             'stroke-linecap="round" aria-hidden="true">'
             '<path d="M4 9V4h5M20 15v5h-5M15 4h5v5M9 20H4v-5"/></svg>')

e = html.escape


# ------------------------------------------------------------------ helpers

def url(path: str) -> str:
    return quote(path, safe="/:?=&#%")


def nav_items(lang: str) -> list[tuple[str, str]]:
    return [
        ("index.html", t(lang, "nav_home")),
        ("about-me.html", t(lang, "nav_about")),
        ("portfolio.html", t(lang, "nav_portfolio")),
        ("events.html", t(lang, "nav_events")),
        (f"mailto:{STUDIO['email']}", t(lang, "nav_contact")),
    ]


def asset(lang: str, path: str) -> str:
    """An asset path as seen from a page in this locale's folder."""
    return url(UP[lang] + path)


def other(lang: str) -> str:
    return "fr" if lang == "en" else "en"


def switch_href(lang: str, name: str) -> str:
    """The same page in the other language."""
    return url(f"fr/{name}" if lang == "en" else f"../{name}")


def img(lang: str, entry: dict, sizes: str, alt: str, *, loading: str = "lazy",
        target: int = 900, extra: str = "") -> str:
    """An <img> with the full ladder, intrinsic size and a lazy default."""
    srcset = ", ".join(f'{asset(lang, s["src"])} {s["w"]}w' for s in entry["srcset"])
    default = next((s for s in entry["srcset"] if s["w"] >= target), entry["srcset"][-1])
    priority = ' fetchpriority="high"' if loading == "eager" else ""
    return (f'<img src="{asset(lang, default["src"])}" srcset="{srcset}" sizes="{sizes}" '
            f'width="{entry["w"]}" height="{entry["h"]}" alt="{e(alt)}" '
            f'loading="{loading}" decoding="async"{priority}{extra}>')


def plate(lang: str, entry: dict, sizes: str, alt: str, *, loading: str = "lazy",
          target: int = 900) -> str:
    """A framed canvas: blur-up placeholder, exact ratio, no layout shift."""
    return (f'<div class="plate" style="aspect-ratio:{entry["w"]}/{entry["h"]};'
            f'background-image:url({entry["lqip"]})">'
            f'{img(lang, entry, sizes, alt, loading=loading, target=target)}</div>')


def head(lang: str, name: str, title: str, description: str, og: dict | None = None) -> str:
    og_image = f'{STUDIO["site"]}/{url(og["srcset"][-1]["src"])}' if og else ""
    alternates = "\n  ".join(
        f'<link rel="alternate" hreflang="{code}" '
        f'href="{STUDIO["site"]}/{HOME[code]}{url(name)}">' for code in LOCALES)

    return f"""<!DOCTYPE html>
<html lang="{t(lang, 'html_lang')}" class="no-js">

<head>
  <meta charset="utf-8">
  <title>{e(title)}</title>
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <meta name="description" content="{e(description)}">
  <meta name="theme-color" content="#ffffff">
  <meta name="format-detection" content="telephone=no">
  <meta property="og:type" content="website">
  <meta property="og:locale" content="{'en_GB' if lang == 'en' else 'fr_FR'}">
  <meta property="og:title" content="{e(title)}">
  <meta property="og:description" content="{e(description)}">
  <meta property="og:url" content="{STUDIO['site']}/{HOME[lang]}{url(name)}">
  {f'<meta property="og:image" content="{og_image}">' if og_image else ''}
  <meta name="twitter:card" content="summary_large_image">
  <link rel="icon" href="{asset(lang, 'images/favicon.svg')}" type="image/svg+xml">
  <link rel="canonical" href="{STUDIO['site']}/{HOME[lang]}{url(name)}">
  {alternates}
  <link rel="alternate" hreflang="x-default" href="{STUDIO['site']}/{url(name)}">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="{FONTS}">
  <link rel="stylesheet" href="{asset(lang, 'css/atelier.css')}">
</head>

<body>
  <a class="skip-link" href="#main">{t(lang, 'skip')}</a>
  <div data-sentinel aria-hidden="true" style="position:absolute;top:0;width:1px;height:1px"></div>
"""


def nav_link(href: str, label: str, active: str) -> str:
    current = ' aria-current="page"' if href == active else ""
    return f'<a href="{href}"{current}>{label}</a>'


def masthead(lang: str, name: str, active: str) -> str:
    links = "\n      ".join(nav_link(href, label, active) for href, label in nav_items(lang))
    drawer_links = "\n      ".join(
        nav_link(href, label, active)
        for href, label in [*nav_items(lang)[:4],
                            ("the-temptation.html", t(lang, "nav_temptation"))])
    switch = (f'<a class="masthead__lang" href="{switch_href(lang, name)}" '
              f'lang="{other(lang)}" hreflang="{other(lang)}" '
              f'aria-label="{t(lang, "language_switch_label")}">{t(lang, "language_switch")}</a>')

    return f"""
  <header class="masthead">
    <a class="masthead__brand" href="index.html" aria-label="{STUDIO['name']} — {t(lang, 'brand_label')}">
      <img src="{asset(lang, 'images/brand.png')}" width="984" height="91" alt="{STUDIO['name']}">
    </a>
    <nav class="masthead__nav" aria-label="{t(lang, 'nav_primary')}">
      {links}
      {switch}
    </nav>
    <button class="menu-toggle" type="button" data-menu-open
      aria-label="{t(lang, 'menu_open')}"><span></span></button>
  </header>

  <dialog class="drawer" id="drawer" aria-label="Menu">
    <button class="drawer__close" type="button" data-menu-close
      aria-label="{t(lang, 'menu_close')}">&times;</button>
    <nav aria-label="{t(lang, 'nav_primary_mobile')}">
      {drawer_links}
    </nav>
    <div class="drawer__contact">
      <a href="{STUDIO['phone_href']}">{STUDIO['phone']}</a>
      <a href="mailto:{STUDIO['email']}">{STUDIO['email']}</a>
      <a href="{STUDIO['instagram']}" rel="noopener">Instagram</a>
      {switch}
    </div>
  </dialog>
"""


def footer(lang: str) -> str:
    return f"""
  <footer class="footer">
    <div class="footer__grid">
      <p class="footer__cta">{t(lang, 'footer_cta')}
        <a href="mailto:{STUDIO['email']}">{t(lang, 'footer_cta_link')}</a></p>
      <div class="footer__col">
        <span class="eyebrow">{t(lang, 'footer_studio')}</span>
        <a href="{STUDIO['phone_href']}">{STUDIO['phone']}</a>
        <a href="mailto:{STUDIO['email']}">{STUDIO['email']}</a>
        <a href="{STUDIO['instagram']}" rel="noopener">Instagram</a>
      </div>
      <div class="footer__col">
        <span class="eyebrow">{t(lang, 'footer_explore')}</span>
        <a href="index.html">{t(lang, 'nav_home')}</a>
        <a href="about-me.html">{t(lang, 'nav_about_long')}</a>
        <a href="portfolio.html">{t(lang, 'nav_portfolio')}</a>
        <a href="events.html">{t(lang, 'nav_events')}</a>
      </div>
    </div>
    <div class="footer__base">
      <span>{STUDIO['name']} — {t(lang, 'role')} &copy; <span data-copyright-year></span></span>
      <span>{t(lang, 'footer_rights')}</span>
    </div>
  </footer>
"""


def viewer(lang: str) -> str:
    return f"""
  <dialog class="viewer" id="viewer" aria-label="{t(lang, 'viewer_label')}">
    <div class="viewer__stage">
      <div class="viewer__canvas">
        <p class="viewer__index" data-viewer-index></p>
        <button class="viewer__close" type="button" data-viewer-close
          aria-label="{t(lang, 'viewer_close')}">&times;</button>
        <button class="viewer__nav viewer__nav--prev" type="button" data-viewer-prev
          aria-label="{t(lang, 'viewer_prev')}">
          <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor"
            stroke-width="1.4" aria-hidden="true"><path d="M15 4 7 12l8 8" /></svg>
        </button>
        <button class="viewer__nav viewer__nav--next" type="button" data-viewer-next
          aria-label="{t(lang, 'viewer_next')}">
          <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor"
            stroke-width="1.4" aria-hidden="true"><path d="m9 4 8 8-8 8" /></svg>
        </button>
      </div>
      <div class="viewer__bar">
        <div>
          <h2 class="viewer__title" data-viewer-title></h2>
          <p class="cartel viewer__spec" data-viewer-spec></p>
        </div>
        <div class="viewer__actions">
          <span class="cartel" data-viewer-tag></span>
          <a class="link-quiet" data-viewer-link href="#">{t(lang, 'viewer_open')}</a>
        </div>
      </div>
    </div>
  </dialog>
"""


def tail(lang: str) -> str:
    return f'\n  <script src="{asset(lang, "js/atelier.js")}" defer></script>\n</body>\n\n</html>\n'


def write(lang: str, name: str, markup: str) -> None:
    path = os.path.join(ROOT, HOME[lang], name)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(markup)


def spec(lang: str, work: dict) -> str:
    return (f'<span>{medium(lang, work["medium"])}</span><span>{work["year"]}</span>'
            f'<span>{e(work["size"])}</span>')


def spec_text(lang: str, work: dict) -> str:
    return f'{medium(lang, work["medium"])} · {work["year"]} · {work["size"]}'


def work_alt(lang: str, work: dict) -> str:
    return t(lang, "work_alt", title=work["title"],
             medium=medium(lang, work["medium"]).lower(), year=work["year"])


# -------------------------------------------------------------------- cards

def card(lang: str, work: dict, index: int, *, eager: bool = False) -> str:
    """A portfolio card: a link to the work, plus a button that enlarges it."""
    sold = " data-sold" if work["sold"] else ""
    label = tag(lang, work)
    return f"""        <article class="card" role="listitem" data-order="{index}" data-title="{e(work['title'])}"
          data-medium="{work['medium']}" data-year="{work['year']}" data-status="{work['status']}"
          data-viewer-item data-spec="{e(spec_text(lang, work))}"
          data-tag="{e(label)}" data-href="{url(work['page'])}">
          <div class="card__inner reveal">
            <a class="card__link" href="{url(work['page'])}">
              <div class="card__frame">{plate(lang, work['canvas'], SIZES['card'], work_alt(lang, work),
                                              loading='eager' if eager else 'lazy', target=640)}</div>
              <div class="card__body">
                <div>
                  <h3 class="card__title">{e(work['title'])}</h3>
                  <p class="cartel card__spec">{spec(lang, work)}</p>
                </div>
                <p class="card__tag"{sold}>{e(label)}</p>
              </div>
            </a>
            <button class="card__zoom" type="button" data-viewer-open
              aria-label="{t(lang, 'work_enlarge', title=e(work['title']))}">{ZOOM_ICON}</button>
          </div>
        </article>"""


def teaser(lang: str, work: dict) -> str:
    """A quieter card for the home page and the artwork pages."""
    return f"""        <a class="card__link reveal" href="{url(work['page'])}">
          {plate(lang, work['canvas'], SIZES['third'], work_alt(lang, work), target=640)}
          <div class="card__body">
            <div>
              <h3 class="card__title">{e(work['title'])}</h3>
              <p class="cartel card__spec">{spec(lang, work)}</p>
            </div>
            <p class="card__tag">{e(tag(lang, work))}</p>
          </div>
        </a>"""


# -------------------------------------------------------------------- pages

def carousel(lang: str, page: dict) -> str:
    """The artist beside her own canvases — the plates the old site opened on."""
    slides = "\n".join(f"""          <li class="slider__slide" data-slide{' aria-hidden="true"' if i else ''}>
            {img(lang, page[s['key']], SIZES['slide'], t(lang, f"{s['key'].replace('-', '_')}_alt"),
                 loading='eager' if i == 0 else 'lazy', target=1400,
                 extra=f' style="object-position:{s["focus"]}"')}
            <p class="slider__caption"><span>{t(lang, f"{s['key'].replace('-', '_')}_caption")}</span></p>
          </li>""" for i, s in enumerate(HOME_SLIDES))

    def dot(i: int) -> str:
        current = ' aria-current="true"' if i == 0 else ""
        return (f'            <button type="button" data-slide-to="{i}" '
                f'aria-label="{t(lang, "slider_goto", n=i + 1)}"{current}></button>')

    dots = "\n".join(dot(i) for i in range(len(HOME_SLIDES)))

    return f"""
    <section class="slider" data-slider aria-roledescription="carousel"
      aria-label="{t(lang, 'slider_label')}" data-dwell="{SLIDE_DWELL_MS}"
      data-status-template="{t(lang, 'slider_status', n='{n}', total='{total}')}"
      data-label-pause="{t(lang, 'slider_pause')}" data-label-play="{t(lang, 'slider_play')}"
      data-aria-pause="{t(lang, 'slider_pause_label')}" data-aria-play="{t(lang, 'slider_play_label')}">
      <div class="slider__viewport">
        <ul class="slider__track" data-track>
{slides}
        </ul>
      </div>

      <button class="slider__arrow slider__arrow--prev" type="button" data-slide-prev
        aria-label="{t(lang, 'slider_prev')}">
        <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor"
          stroke-width="1.4" aria-hidden="true"><path d="M15 4 7 12l8 8" /></svg>
      </button>
      <button class="slider__arrow slider__arrow--next" type="button" data-slide-next
        aria-label="{t(lang, 'slider_next')}">
        <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor"
          stroke-width="1.4" aria-hidden="true"><path d="m9 4 8 8-8 8" /></svg>
      </button>

      <div class="slider__controls">
        <div class="slider__dots" role="group" aria-label="{t(lang, 'slider_dots')}">
{dots}
        </div>
        <button class="slider__play" type="button" data-slide-toggle
          aria-label="{t(lang, 'slider_pause_label')}">
          <span data-slide-toggle-label>{t(lang, 'slider_pause')}</span>
        </button>
      </div>
      <p class="visually-hidden" role="status" data-slide-status></p>
    </section>
"""


def build_home(lang: str, works: list[dict], page: dict) -> str:
    hero = works[0]
    cards = "\n".join(teaser(lang, w) for w in works[1:7])

    return (head(lang, "index.html", t(lang, "home_title"), t(lang, "home_description"),
                 og=hero["canvas"])
            + masthead(lang, "index.html", "index.html") + f"""
  <main id="main">
    <section class="shell opening">
      <div>
        <p class="eyebrow">{t(lang, 'role')} — {t(lang, 'based')}</p>
        <h1 class="opening__name">{STUDIO['name']}</h1>
      </div>
      <div class="opening__meta">
        <p class="lede" style="max-width:32rem">{t(lang, 'home_quote')}</p>
        <a class="link-quiet" href="portfolio.html">{t(lang, 'home_see_works', n=len(works))}</a>
      </div>
    </section>

{carousel(lang, page)}
    <section class="shell section--tight">
      <div class="feature">
        <a href="{url(hero['page'])}" aria-label="{e(hero['title'])}">
          {plate(lang, hero['canvas'], SIZES['wide'], work_alt(lang, hero), target=1400)}
        </a>
        <div class="feature__caption">
          <p class="eyebrow">{t(lang, 'home_latest')}</p>
          <h2 class="feature__title">{e(hero['title'])}</h2>
          <p class="cartel">{spec(lang, hero)}</p>
          <p><a class="link-quiet" href="{url(hero['page'])}">{t(lang, 'home_open_work')}</a></p>
        </div>
      </div>
    </section>

    <section class="shell section" data-viewer-group>
      <div class="section-head">
        <h2 class="section-title">{t(lang, 'home_selected')}</h2>
        <a class="link-quiet more" href="portfolio.html">{t(lang, 'home_all_works')}</a>
      </div>
      <div class="grid-3">
{cards}
      </div>
    </section>

    <section class="shell section">
      <div class="about">
        <div class="about__portrait reveal">
          {plate(lang, page['portrait'], SIZES['half'], t(lang, 'home_studio_alt'), target=900)}
        </div>
        <div class="reveal">
          <p class="eyebrow">{t(lang, 'home_the_artist')}</p>
          <h2 class="section-title" style="margin-top:.75rem">{t(lang, 'home_about_heading')}</h2>
          <div class="prose" style="margin-top:1.5rem;max-width:var(--measure)">
            <p>{t(lang, 'home_about_1')}</p>
            <p>{t(lang, 'home_about_2')}</p>
          </div>
          <p style="margin-top:2rem"><a class="button" href="about-me.html">{t(lang, 'home_about_button')}</a></p>
        </div>
      </div>
    </section>
  </main>
""" + footer(lang) + viewer(lang) + tail(lang))


def build_about(lang: str, page: dict) -> str:
    timeline = "\n".join(
        f'          <li class="reveal"><b>{when}</b>\n            <p>{text}</p>\n          </li>'
        for when, text in TIMELINE[lang])

    return (head(lang, "about-me.html", t(lang, "about_title"), t(lang, "about_description"),
                 og=page["portrait"])
            + masthead(lang, "about-me.html", "about-me.html") + f"""
  <main id="main">
    <section class="shell section--tight">
      <ul class="breadcrumb">
        <li><a href="index.html">{t(lang, 'nav_home')}</a></li>
        <li>{t(lang, 'about_heading')}</li>
      </ul>
      <h1 class="page-title">{t(lang, 'about_heading')}</h1>
    </section>

    <section class="shell section--tight section--after-title">
      <div class="about">
        <div class="about__portrait">
          {plate(lang, page['portrait'], SIZES['half'], t(lang, 'about_portrait_alt'),
                 loading='eager', target=900)}
        </div>
        <div>
          <p class="lede">{t(lang, 'about_quote')}</p>
          <ol class="timeline">
{timeline}
          </ol>
          <p style="margin-top:2.5rem"><a class="button" href="portfolio.html">{t(lang, 'about_button')}</a></p>
        </div>
      </div>
    </section>
  </main>
""" + footer(lang) + tail(lang))


def build_portfolio(lang: str, works: list[dict]) -> str:
    years = sorted({w["year"] for w in works}, reverse=True)
    options = "".join(f'\n            <option value="{y}">{y}</option>' for y in years)
    cards = "\n".join(card(lang, w, i, eager=i < 3) for i, w in enumerate(works))
    available = sum(not w["sold"] for w in works)

    return (head(lang, "portfolio.html", t(lang, "portfolio_title"),
                 t(lang, "portfolio_description", n=len(works), first=min(years), last=max(years)),
                 og=works[0]["canvas"])
            + masthead(lang, "portfolio.html", "portfolio.html") + f"""
  <main id="main">
    <section class="shell section--tight">
      <ul class="breadcrumb">
        <li><a href="index.html">{t(lang, 'nav_home')}</a></li>
        <li>{t(lang, 'portfolio_heading')}</li>
      </ul>
      <h1 class="page-title">{t(lang, 'portfolio_heading')}</h1>
      <div class="opening__meta" style="margin-top:clamp(1.5rem,3vw,2.5rem)">
        <p class="lede" style="max-width:30rem">{t(lang, 'portfolio_lede', first=min(years), last=max(years))}</p>
        <p class="cartel"><span>{t(lang, 'portfolio_count', n=len(works))}</span><span>{t(lang, 'portfolio_available', n=available)}</span></p>
      </div>
    </section>

    <div class="controls" data-count-template="{t(lang, 'portfolio_count', n='{n}')}"
      data-count-one="{t(lang, 'portfolio_count_one', n='{n}')}">
      <fieldset class="chips">
        <legend class="visually-hidden">{t(lang, 'filter_medium')}</legend>
        <button class="chip" type="button" data-filter="medium" data-value="all"
          aria-pressed="true">{t(lang, 'filter_all')}</button>
        <button class="chip" type="button" data-filter="medium" data-value="Oil"
          aria-pressed="false">{medium(lang, 'Oil')}</button>
        <button class="chip" type="button" data-filter="medium" data-value="Acrylic"
          aria-pressed="false">{medium(lang, 'Acrylic')}</button>
      </fieldset>

      <fieldset class="chips">
        <legend class="visually-hidden">{t(lang, 'filter_availability')}</legend>
        <button class="chip" type="button" data-filter="status" data-value="available"
          aria-pressed="false">{t(lang, 'filter_available')}</button>
      </fieldset>

      <p class="field"><label for="year-select">{t(lang, 'filter_year')}</label>
        <select id="year-select" data-filter="year">
          <option value="all">{t(lang, 'filter_all_years')}</option>{options}
        </select>
      </p>

      <p class="field"><label for="sort-select">{t(lang, 'filter_order')}</label>
        <select id="sort-select" data-sort>
          <option value="recent">{t(lang, 'order_recent')}</option>
          <option value="oldest">{t(lang, 'order_oldest')}</option>
          <option value="title">{t(lang, 'order_title')}</option>
        </select>
      </p>

      <p class="controls__count" role="status" data-count>{t(lang, 'portfolio_count', n=len(works))}</p>
    </div>

    <div class="shell section--tight section--after-title">
      <div class="gallery" id="gallery" role="list" data-viewer-group>
{cards}
      </div>
      <div class="gallery-empty" hidden data-empty>
        <p>{t(lang, 'empty')}</p>
        <button class="chip" type="button" data-reset>{t(lang, 'empty_reset')}</button>
      </div>
    </div>
  </main>
""" + footer(lang) + viewer(lang) + tail(lang))


def build_events(lang: str, page: dict) -> str:
    events = [
        ("art-exhibition.html", page["event-exhibition"], t(lang, "event_exhibition"),
         t(lang, "event_exhibition_venue"), t(lang, "event_exhibition_date")),
        ("the-temptation.html", page["event-temptation"], t(lang, "event_temptation"),
         t(lang, "event_temptation_kind"), ""),
    ]
    cards = "\n".join(f"""        <a class="event reveal" href="{href}">
          <div class="event__frame">{img(lang, cover, SIZES['half'], title.replace('&amp;', '&'), target=900)}</div>
          <div>
            <h2 class="event__title">{title}</h2>
            <p class="cartel" style="margin-top:.4rem"><span>{venue}</span>{f'<span>{when}</span>' if when else ''}</p>
          </div>
        </a>""" for href, cover, title, venue, when in events)

    return (head(lang, "events.html", t(lang, "events_title"), t(lang, "events_description"),
                 og=page["event-exhibition"])
            + masthead(lang, "events.html", "events.html") + f"""
  <main id="main">
    <section class="shell section--tight">
      <ul class="breadcrumb">
        <li><a href="index.html">{t(lang, 'nav_home')}</a></li>
        <li>{t(lang, 'events_heading')}</li>
      </ul>
      <h1 class="page-title">{t(lang, 'events_heading')}</h1>
    </section>

    <section class="shell section--tight section--after-title">
      <div class="grid-2">
{cards}
      </div>
    </section>
  </main>
""" + footer(lang) + tail(lang))


def build_exhibition(lang: str, photos: list[dict], page: dict) -> str:
    poster = next(s for s in page["event-exhibition"]["srcset"] if s["w"] >= 900)
    tiles = "\n".join(f"""        <span data-viewer-item data-title="{t(lang, 'event_exhibition_venue')}"
          data-spec="{t(lang, 'event_exhibition')} · {t(lang, 'event_exhibition_date')}">
          <button type="button" data-viewer-open aria-label="{t(lang, 'exhibition_enlarge', n=i)}">
            {img(lang, photo, SIZES['photo'], t(lang, 'exhibition_photo_alt', n=i),
                 loading='eager' if i <= 4 else 'lazy', target=800)}
          </button>
        </span>""" for i, photo in enumerate(photos, 1))

    return (head(lang, "art-exhibition.html", t(lang, "exhibition_title"),
                 t(lang, "exhibition_description"), og=page["event-exhibition"])
            + masthead(lang, "art-exhibition.html", "events.html") + f"""
  <main id="main">
    <section class="shell section--tight">
      <ul class="breadcrumb">
        <li><a href="index.html">{t(lang, 'nav_home')}</a></li>
        <li><a href="events.html">{t(lang, 'events_heading')}</a></li>
        <li>{t(lang, 'event_exhibition')}</li>
      </ul>
      <h1 class="page-title">{t(lang, 'event_exhibition')}</h1>
      <p class="cartel" style="margin-top:1.25rem"><span>{t(lang, 'event_exhibition_venue')}</span>
        <span>{t(lang, 'event_exhibition_date')}</span></p>
    </section>

    <section class="shell section--tight section--after-title">
      <div class="film">
        <video controls preload="none" playsinline poster="{asset(lang, poster['src'])}"
          width="1920" height="1080">
          <source src="{asset(lang, 'images/Art-Exhibition-video.mp4')}" type="video/mp4">
        </video>
      </div>
      <p class="film__note">{t(lang, 'exhibition_film_note')}</p>
    </section>

    <section class="shell section--tight" data-viewer-group>
      <div class="section-head">
        <h2 class="section-title">{t(lang, 'exhibition_evening')}</h2>
        <p class="cartel more">{t(lang, 'exhibition_photographs', n=len(photos))}</p>
      </div>
      <div class="photos">
{tiles}
      </div>
    </section>
  </main>
""" + footer(lang) + viewer(lang) + tail(lang))


def build_temptation(lang: str, page: dict) -> str:
    poster = next(s for s in page["event-temptation"]["srcset"] if s["w"] >= 900)
    return (head(lang, "the-temptation.html", t(lang, "temptation_title"),
                 t(lang, "temptation_description"), og=page["event-temptation"])
            + masthead(lang, "the-temptation.html", "events.html") + f"""
  <main id="main">
    <section class="shell section--tight">
      <ul class="breadcrumb">
        <li><a href="index.html">{t(lang, 'nav_home')}</a></li>
        <li><a href="events.html">{t(lang, 'events_heading')}</a></li>
        <li>The Temptation</li>
      </ul>
      <h1 class="page-title">{t(lang, 'temptation_heading')}</h1>
    </section>

    <section class="shell section--tight section--after-title">
      <div class="film">
        <video controls preload="none" playsinline poster="{asset(lang, poster['src'])}"
          width="1080" height="1080">
          <source src="{asset(lang, 'images/the-temptation.mp4')}" type="video/mp4">
        </video>
      </div>
      <p class="film__note">{t(lang, 'temptation_note')}</p>
      <p style="margin-top:2.5rem"><a class="button button--ghost" href="events.html">{t(lang, 'temptation_back')}</a></p>
    </section>
  </main>
""" + footer(lang) + tail(lang))


def build_work(lang: str, work: dict, previous: dict, following: dict,
               related: list[dict]) -> str:
    subject = quote(t(lang, "work_enquiry_subject", title=work["title"], year=work["year"]))

    views = ""
    if work["views"]:
        tiles = "\n".join(f"""        <span data-viewer-item data-title="{e(work['title'])}"
          data-spec="{e(spec_text(lang, work))}">
          <button type="button" data-viewer-open
            aria-label="{t(lang, 'work_enlarge_view', n=i, title=e(work['title']))}">
            {img(lang, view, SIZES['third'], t(lang, 'work_view_alt', title=work['title'], n=i), target=900)}
          </button>
        </span>""" for i, view in enumerate(work["views"], 1))
        views = f"""
    <section class="shell section--tight" data-viewer-group>
      <div class="section-head">
        <h2 class="section-title">{t(lang, 'work_in_situ')}</h2>
      </div>
      <div class="views">
{tiles}
      </div>
    </section>
"""

    cards = "\n".join(teaser(lang, w) for w in related)
    facts = [(t(lang, "work_medium"), t(lang, "work_on_canvas", medium=medium(lang, work["medium"]))),
             (t(lang, "work_year"), str(work["year"])),
             (t(lang, "work_dimensions"), work["size"]),
             (t(lang, "work_status"), tag(lang, work))]
    fact_rows = "\n".join(
        f'          <div><dt>{label}</dt>\n            <dd>{e(value)}</dd>\n          </div>'
        for label, value in facts)

    enquire = ("" if work["sold"] else
               f'          <p><a class="button" href="mailto:{STUDIO["email"]}?subject={subject}">'
               f'{t(lang, "work_enquire")}</a></p>\n')

    return (head(lang, work["page"], f'{work["title"]} — {STUDIO["name"]}',
                 t(lang, "work_description", title=work["title"],
                   medium=medium(lang, work["medium"]).lower(), year=work["year"], size=work["size"]),
                 og=work["canvas"])
            + masthead(lang, work["page"], "portfolio.html") + f"""
  <main id="main">
    <section class="shell section--tight">
      <ul class="breadcrumb">
        <li><a href="index.html">{t(lang, 'nav_home')}</a></li>
        <li><a href="portfolio.html">{t(lang, 'nav_portfolio')}</a></li>
        <li>{e(work['title'])}</li>
      </ul>
      <h1 class="page-title">{e(work['title'])}</h1>
    </section>

    <section class="shell section--tight section--after-title" data-viewer-group>
      <div class="work">
        <div class="work__canvas" data-viewer-item data-title="{e(work['title'])}"
          data-spec="{e(spec_text(lang, work))}" data-tag="{e(tag(lang, work))}">
          <button type="button" data-viewer-open style="display:block;width:100%;padding:0"
            aria-label="{t(lang, 'work_enlarge', title=e(work['title']))}">
            {plate(lang, work['canvas'], SIZES['canvas'], work_alt(lang, work),
                   loading='eager', target=1400)}
          </button>
        </div>
        <div class="work__side">
          <dl class="work__facts">
{fact_rows}
          </dl>
{enquire}          <p><a class="link-quiet" href="portfolio.html">{t(lang, 'work_back')}</a></p>
        </div>
      </div>
    </section>
{views}
    <section class="shell section--tight" data-viewer-group>
      <div class="section-head">
        <h2 class="section-title">{t(lang, 'work_more')}</h2>
        <a class="link-quiet more" href="portfolio.html">{t(lang, 'home_all_works')}</a>
      </div>
      <div class="grid-3">
{cards}
      </div>
    </section>

    <nav class="shell pager" aria-label="{t(lang, 'work_nav')}">
      <a href="{url(previous['page'])}">
        <span class="eyebrow">{t(lang, 'work_previous')}</span>
        <strong>{e(previous['title'])}</strong>
      </a>
      <a href="{url(following['page'])}">
        <span class="eyebrow">{t(lang, 'work_next')}</span>
        <strong>{e(following['title'])}</strong>
      </a>
    </nav>
  </main>
""" + footer(lang) + viewer(lang) + tail(lang))


# ---------------------------------------------------------------------- main

def main() -> None:
    manifest = json.load(open(os.path.join(HERE, "site.json"), encoding="utf-8"))
    works, photos, page = manifest["works"], manifest["exhibition"], manifest["page"]
    assert len(works) == len(ARTWORKS), "manifest is stale — run build-images.py first"

    total = len(works)
    for lang in LOCALES:
        write(lang, "index.html", build_home(lang, works, page))
        write(lang, "about-me.html", build_about(lang, page))
        write(lang, "portfolio.html", build_portfolio(lang, works))
        write(lang, "events.html", build_events(lang, page))
        write(lang, "art-exhibition.html", build_exhibition(lang, photos, page))
        write(lang, "the-temptation.html", build_temptation(lang, page))

        for i, work in enumerate(works):
            related = [works[(i + n) % total] for n in (1, 2, 3)]
            write(lang, work["page"],
                  build_work(lang, work, works[(i - 1) % total], works[(i + 1) % total], related))

    per_locale = 6 + total
    print(f"rendered {per_locale * len(LOCALES)} pages "
          f"({per_locale} per locale × {len(LOCALES)}: {', '.join(LOCALES)})")


if __name__ == "__main__":
    main()
