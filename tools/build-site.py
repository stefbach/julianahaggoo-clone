#!/usr/bin/env python3
"""Render every page of the site from the catalogue and the image manifest.

    python3 tools/build-images.py     # first: renditions + tools/site.json
    python3 tools/build-site.py       # then:  the 42 pages

Every page shares css/atelier.css and js/atelier.js, so a visitor pays for the
design system once and each document stays a few kilobytes.
"""
from __future__ import annotations

import html
import json
import os
import sys
from urllib.parse import quote

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from artworks import ARTWORKS, HOME_SLIDES, STUDIO  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

FONTS = ("https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;"
         "1,300;1,400&family=Italiana&display=swap")

SIZES = {
    "card": "(max-width:559px) 92vw, (max-width:979px) 46vw, 30vw",
    "third": "(max-width:60em) 92vw, 30vw",
    "half": "(max-width:58em) 92vw, 46vw",
    "canvas": "(max-width:62em) 92vw, 62vw",
    "wide": "(max-width:60em) 92vw, 68vw",
    "photo": "(max-width:40em) 92vw, (max-width:70em) 46vw, 23vw",
    "slide": "100vw",
}

NAV = [
    ("index.html", "Home"),
    ("about-me.html", "About"),
    ("portfolio.html", "Portfolio"),
    ("events.html", "Events"),
    (f"mailto:{STUDIO['email']}", "Contact"),
]

ZOOM_ICON = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" '
             'stroke-linecap="round" aria-hidden="true">'
             '<path d="M4 9V4h5M20 15v5h-5M15 4h5v5M9 20H4v-5"/></svg>')

e = html.escape


# ------------------------------------------------------------------ helpers

def url(path: str) -> str:
    return quote(path, safe="/:?=&#%")


def img(entry: dict, sizes: str, alt: str, *, loading: str = "lazy",
        target: int = 900, extra: str = "") -> str:
    """An <img> with the full ladder, intrinsic size and a lazy default."""
    srcset = ", ".join(f'{url(s["src"])} {s["w"]}w' for s in entry["srcset"])
    default = next((s for s in entry["srcset"] if s["w"] >= target), entry["srcset"][-1])
    priority = ' fetchpriority="high"' if loading == "eager" else ""
    return (f'<img src="{url(default["src"])}" srcset="{srcset}" sizes="{sizes}" '
            f'width="{entry["w"]}" height="{entry["h"]}" alt="{e(alt)}" '
            f'loading="{loading}" decoding="async"{priority}{extra}>')


def plate(entry: dict, sizes: str, alt: str, *, loading: str = "lazy", target: int = 900) -> str:
    """A framed canvas: blur-up placeholder, exact ratio, no layout shift."""
    return (f'<div class="plate" style="aspect-ratio:{entry["w"]}/{entry["h"]};'
            f'background-image:url({entry["lqip"]})">'
            f'{img(entry, sizes, alt, loading=loading, target=target)}</div>')


def head(title: str, description: str, *, canonical: str, og: dict | None = None,
         page_class: str = "") -> str:
    og_image = (f'{STUDIO["site"]}/{url(og["srcset"][-1]["src"])}' if og else "")
    return f"""<!DOCTYPE html>
<html lang="en" class="no-js{(' ' + page_class) if page_class else ''}">

<head>
  <meta charset="utf-8">
  <title>{e(title)}</title>
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <meta name="description" content="{e(description)}">
  <meta name="theme-color" content="#ffffff">
  <meta name="format-detection" content="telephone=no">
  <meta property="og:type" content="website">
  <meta property="og:title" content="{e(title)}">
  <meta property="og:description" content="{e(description)}">
  <meta property="og:url" content="{STUDIO['site']}/{canonical}">
  {f'<meta property="og:image" content="{og_image}">' if og_image else ''}
  <meta name="twitter:card" content="summary_large_image">
  <link rel="icon" href="images/favicon.svg" type="image/svg+xml">
  <link rel="canonical" href="{STUDIO['site']}/{canonical}">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="{FONTS}">
  <link rel="stylesheet" href="css/atelier.css">
</head>

<body>
  <a class="skip-link" href="#main">Skip to content</a>
  <div data-sentinel aria-hidden="true" style="position:absolute;top:0;width:1px;height:1px"></div>
"""


def nav_link(href: str, label: str, active: str) -> str:
    current = ' aria-current="page"' if href == active else ""
    return f'<a href="{href}"{current}>{label}</a>'


def masthead(active: str) -> str:
    links = "\n      ".join(nav_link(href, label, active) for href, label in NAV)
    drawer_links = "\n      ".join(
        nav_link(href, label, active)
        for href, label in [*NAV[:4], ("the-temptation.html", "Dark &amp; Light: The Temptation")])
    return f"""
  <header class="masthead">
    <a class="masthead__brand" href="index.html" aria-label="{STUDIO['name']} — home">
      <img src="images/brand.png" width="984" height="91" alt="{STUDIO['name']}">
    </a>
    <nav class="masthead__nav" aria-label="Primary">
      {links}
    </nav>
    <button class="menu-toggle" type="button" data-menu-open aria-label="Open menu"><span></span></button>
  </header>

  <dialog class="drawer" id="drawer" aria-label="Menu">
    <button class="drawer__close" type="button" data-menu-close aria-label="Close menu">&times;</button>
    <nav aria-label="Primary, mobile">
      {drawer_links}
    </nav>
    <div class="drawer__contact">
      <a href="{STUDIO['phone_href']}">{STUDIO['phone']}</a>
      <a href="mailto:{STUDIO['email']}">{STUDIO['email']}</a>
      <a href="{STUDIO['instagram']}" rel="noopener">Instagram</a>
    </div>
  </dialog>
"""


def footer() -> str:
    return f"""
  <footer class="footer">
    <div class="footer__grid">
      <p class="footer__cta">Interested in a canvas?
        <a href="mailto:{STUDIO['email']}">Write to the studio.</a></p>
      <div class="footer__col">
        <span class="eyebrow">Studio</span>
        <a href="{STUDIO['phone_href']}">{STUDIO['phone']}</a>
        <a href="mailto:{STUDIO['email']}">{STUDIO['email']}</a>
        <a href="{STUDIO['instagram']}" rel="noopener">Instagram</a>
      </div>
      <div class="footer__col">
        <span class="eyebrow">Explore</span>
        <a href="index.html">Home</a>
        <a href="about-me.html">About Me</a>
        <a href="portfolio.html">Portfolio</a>
        <a href="events.html">Events</a>
      </div>
    </div>
    <div class="footer__base">
      <span>{STUDIO['name']} — {STUDIO['role']} &copy; <span data-copyright-year></span></span>
      <span>All works and images are the property of the artist.</span>
    </div>
  </footer>
"""


def viewer() -> str:
    return """
  <dialog class="viewer" id="viewer" aria-label="Image viewer">
    <div class="viewer__stage">
      <div class="viewer__canvas">
        <p class="viewer__index" data-viewer-index></p>
        <button class="viewer__close" type="button" data-viewer-close aria-label="Close viewer">&times;</button>
        <button class="viewer__nav viewer__nav--prev" type="button" data-viewer-prev aria-label="Previous image">
          <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.4"
            aria-hidden="true"><path d="M15 4 7 12l8 8" /></svg>
        </button>
        <button class="viewer__nav viewer__nav--next" type="button" data-viewer-next aria-label="Next image">
          <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.4"
            aria-hidden="true"><path d="m9 4 8 8-8 8" /></svg>
        </button>
      </div>
      <div class="viewer__bar">
        <div>
          <h2 class="viewer__title" data-viewer-title></h2>
          <p class="cartel viewer__spec" data-viewer-spec></p>
        </div>
        <div class="viewer__actions">
          <span class="cartel" data-viewer-tag></span>
          <a class="link-quiet" data-viewer-link href="#">Open the work</a>
        </div>
      </div>
    </div>
  </dialog>
"""


def tail() -> str:
    return '\n  <script src="js/atelier.js" defer></script>\n</body>\n\n</html>\n'


def write(name: str, markup: str) -> None:
    with open(os.path.join(ROOT, name), "w", encoding="utf-8") as fh:
        fh.write(markup)


def spec(work: dict) -> str:
    return (f'<span>{work["medium"]}</span><span>{work["year"]}</span>'
            f'<span>{e(work["size"])}</span>')


def spec_text(work: dict) -> str:
    return f'{work["medium"]} · {work["year"]} · {work["size"]}'


# -------------------------------------------------------------------- cards

def card(work: dict, index: int, *, eager: bool = False) -> str:
    """A portfolio card: a link to the work, plus a button that enlarges it."""
    alt = f'{work["title"]} — {work["medium"].lower()} painting, {work["year"]}'
    sold = " data-sold" if work["sold"] else ""
    return f"""        <article class="card" role="listitem" data-order="{index}" data-title="{e(work['title'])}"
          data-medium="{work['medium']}" data-year="{work['year']}" data-status="{work['status']}"
          data-viewer-item data-spec="{e(spec_text(work))}"
          data-tag="{e(work['tag'])}" data-href="{url(work['page'])}">
          <div class="card__inner reveal">
            <a class="card__link" href="{url(work['page'])}">
              <div class="card__frame">{plate(work['canvas'], SIZES['card'], alt,
                                              loading='eager' if eager else 'lazy', target=640)}</div>
              <div class="card__body">
                <div>
                  <h3 class="card__title">{e(work['title'])}</h3>
                  <p class="cartel card__spec">{spec(work)}</p>
                </div>
                <p class="card__tag"{sold}>{e(work['tag'])}</p>
              </div>
            </a>
            <button class="card__zoom" type="button" data-viewer-open
              aria-label="Enlarge {e(work['title'])}">{ZOOM_ICON}</button>
          </div>
        </article>"""


def teaser(work: dict, *, eager: bool = False) -> str:
    """A quieter card for the home page selections."""
    alt = f'{work["title"]} — {work["medium"].lower()} painting, {work["year"]}'
    return f"""        <a class="card__link reveal" href="{url(work['page'])}">
          {plate(work['canvas'], SIZES['third'], alt, loading='eager' if eager else 'lazy', target=640)}
          <div class="card__body">
            <div>
              <h3 class="card__title">{e(work['title'])}</h3>
              <p class="cartel card__spec">{spec(work)}</p>
            </div>
            <p class="card__tag">{e(work['tag'])}</p>
          </div>
        </a>"""


# -------------------------------------------------------------------- pages

def carousel(page: dict) -> str:
    """The artist beside her own canvases — the plates the old site opened on."""
    slides = "\n".join(f"""          <li class="slider__slide" data-slide{' aria-hidden="true"' if i else ''}>
            {img(page[s['key']], SIZES['slide'], s['alt'],
                 loading='eager' if i == 0 else 'lazy', target=1400,
                 extra=f' style="object-position:{s["focus"]}"')}
            <p class="slider__caption"><span>{e(s['caption'])}</span></p>
          </li>""" for i, s in enumerate(HOME_SLIDES))

    def dot(i: int) -> str:
        current = ' aria-current="true"' if i == 0 else ""
        return (f'            <button type="button" data-slide-to="{i}" '
                f'aria-label="Go to slide {i + 1}"{current}></button>')

    dots = "\n".join(dot(i) for i in range(len(HOME_SLIDES)))

    return f"""
    <section class="slider" data-slider aria-roledescription="carousel"
      aria-label="Juliana Haggoo and her work">
      <div class="slider__viewport">
        <ul class="slider__track" data-track>
{slides}
        </ul>
      </div>

      <button class="slider__arrow slider__arrow--prev" type="button" data-slide-prev
        aria-label="Previous slide">
        <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor"
          stroke-width="1.4" aria-hidden="true"><path d="M15 4 7 12l8 8" /></svg>
      </button>
      <button class="slider__arrow slider__arrow--next" type="button" data-slide-next
        aria-label="Next slide">
        <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor"
          stroke-width="1.4" aria-hidden="true"><path d="m9 4 8 8-8 8" /></svg>
      </button>

      <div class="slider__controls">
        <div class="slider__dots" role="group" aria-label="Choose a slide">
{dots}
        </div>
        <button class="slider__play" type="button" data-slide-toggle aria-label="Pause the carousel">
          <span data-slide-toggle-label>Pause</span>
        </button>
      </div>
      <p class="visually-hidden" role="status" data-slide-status></p>
    </section>
"""


def build_home(works: list[dict], page: dict) -> str:
    hero = works[0]
    selection = works[1:7]
    alt = f'{hero["title"]} — {hero["medium"].lower()} painting, {hero["year"]}'
    cards = "\n".join(teaser(w) for w in selection)

    return (head(f'{STUDIO["name"]} — {STUDIO["role"]}',
                 "Abstract oil and acrylic paintings by Juliana Haggoo. Colour built up in layers, "
                 "painted at night to music.",
                 canonical="index.html", og=hero["canvas"])
            + masthead("index.html") + f"""
  <main id="main">
    <section class="shell opening">
      <div>
        <p class="eyebrow">{STUDIO['role']} — Paris &amp; Mauritius</p>
        <h1 class="opening__name">{STUDIO['name']}</h1>
      </div>
      <div class="opening__meta">
        <p class="lede" style="max-width:32rem">“It is at night, with music, that my creativity fully
          blossoms.”</p>
        <a class="link-quiet" href="portfolio.html">See the {len(works)} works</a>
      </div>
    </section>

{carousel(page)}
    <section class="shell section--tight">
      <div class="feature">
        <a href="{url(hero['page'])}" aria-label="{e(hero['title'])}">
          {plate(hero['canvas'], SIZES['wide'], alt, target=1400)}
        </a>
        <div class="feature__caption">
          <p class="eyebrow">Latest work</p>
          <h2 class="feature__title">{e(hero['title'])}</h2>
          <p class="cartel">{spec(hero)}</p>
          <p><a class="link-quiet" href="{url(hero['page'])}">Open the work</a></p>
        </div>
      </div>
    </section>

    <section class="shell section" data-viewer-group>
      <div class="section-head">
        <h2 class="section-title">Selected works</h2>
        <a class="link-quiet more" href="portfolio.html">All works</a>
      </div>
      <div class="grid-3">
{cards}
      </div>
    </section>

    <section class="shell section">
      <div class="about">
        <div class="about__portrait reveal">
          {plate(page['portrait'], SIZES['half'], 'Juliana Haggoo in the studio', target=900)}
        </div>
        <div class="reveal">
          <p class="eyebrow">The artist</p>
          <h2 class="section-title" style="margin-top:.75rem">From the stage to the canvas</h2>
          <div class="prose" style="margin-top:1.5rem;max-width:var(--measure)">
            <p>My artistic journey began in 2005 when I joined a jazz band in Paris. Painting then became
              my outlet in 2007 — I immersed myself in abstract art, letting my emotions flow onto the
              canvas.</p>
            <p>Today, my journey fuses music, dance and painting. It exemplifies resilience and the
              liberating power of art.</p>
          </div>
          <p style="margin-top:2rem"><a class="button" href="about-me.html">About the artist</a></p>
        </div>
      </div>
    </section>
  </main>
""" + footer() + viewer() + tail())


def build_about(page: dict) -> str:
    steps = [
        ("2005", "My artistic journey began when I joined a jazz band in Paris. We shared our passion "
                 "through intimate concerts."),
        ("Then", "I explored a more personal approach, blending singing and dancing in Parisian "
                 "cabarets. However, this hectic pace exhausted me."),
        ("2007", "Painting became my outlet. I immersed myself in abstract art, letting my emotions "
                 "flow onto the canvas."),
        ("At night", "It is at night, with music, that my creativity fully blossoms. Classical music "
                     "and jazz fuel my artistic impulses."),
        ("Mentors", "I discovered contemporary art thanks to benevolent mentors. It allows me to "
                    "explore my emotions and structure them artistically."),
        ("Today", "My journey fuses music, dance and painting. It exemplifies resilience and the "
                  "liberating power of art."),
    ]
    timeline = "\n".join(
        f'          <li class="reveal"><b>{when}</b>\n            <p>{text}</p>\n          </li>'
        for when, text in steps)

    return (head(f'About Me — {STUDIO["name"]}',
                 "Juliana Haggoo on jazz, cabaret, and the night-time painting practice that "
                 "became her life's work.",
                 canonical="about-me.html", og=page["portrait"])
            + masthead("about-me.html") + f"""
  <main id="main">
    <section class="shell section--tight">
      <ul class="breadcrumb">
        <li><a href="index.html">Home</a></li>
        <li>About Me</li>
      </ul>
      <h1 class="page-title">About Me</h1>
    </section>

    <section class="shell section--tight section--after-title">
      <div class="about">
        <div class="about__portrait">
          {plate(page['portrait'], SIZES['half'], 'Portrait of Juliana Haggoo',
                 loading='eager', target=900)}
        </div>
        <div>
          <p class="lede">“I immersed myself in the world of the abstract, letting my emotions and
            stress dissolve into the colors and shapes on the canvas.”</p>
          <ol class="timeline">
{timeline}
          </ol>
          <p style="margin-top:2.5rem"><a class="button" href="portfolio.html">See the works</a></p>
        </div>
      </div>
    </section>
  </main>
""" + footer() + tail())


def build_portfolio(works: list[dict]) -> str:
    years = sorted({w["year"] for w in works}, reverse=True)
    options = "".join(f'\n            <option value="{y}">{y}</option>' for y in years)
    cards = "\n".join(card(w, i, eager=i < 3) for i, w in enumerate(works))
    available = sum(not w["sold"] for w in works)

    return (head(f'Portfolio — {STUDIO["name"]}',
                 f'The complete body of work of Juliana Haggoo — {len(works)} oil and acrylic '
                 f'paintings from {min(years)} to {max(years)}.',
                 canonical="portfolio.html", og=works[0]["canvas"])
            + masthead("portfolio.html") + f"""
  <main id="main">
    <section class="shell section--tight">
      <ul class="breadcrumb">
        <li><a href="index.html">Home</a></li>
        <li>Portfolio</li>
      </ul>
      <h1 class="page-title">Portfolio</h1>
      <div class="opening__meta" style="margin-top:clamp(1.5rem,3vw,2.5rem)">
        <p class="lede" style="max-width:30rem">Oil and acrylic on canvas, {min(years)}–{max(years)}.</p>
        <p class="cartel"><span>{len(works)} works</span><span>{available} available</span></p>
      </div>
    </section>

    <div class="controls">
      <fieldset class="chips">
        <legend class="visually-hidden">Filter by medium</legend>
        <button class="chip" type="button" data-filter="medium" data-value="all" aria-pressed="true">All</button>
        <button class="chip" type="button" data-filter="medium" data-value="Oil" aria-pressed="false">Oil</button>
        <button class="chip" type="button" data-filter="medium" data-value="Acrylic" aria-pressed="false">Acrylic</button>
      </fieldset>

      <fieldset class="chips">
        <legend class="visually-hidden">Filter by availability</legend>
        <button class="chip" type="button" data-filter="status" data-value="available"
          aria-pressed="false">Available only</button>
      </fieldset>

      <p class="field"><label for="year-select">Year</label>
        <select id="year-select" data-filter="year">
          <option value="all">All years</option>{options}
        </select>
      </p>

      <p class="field"><label for="sort-select">Order</label>
        <select id="sort-select" data-sort>
          <option value="recent">Most recent</option>
          <option value="oldest">Earliest first</option>
          <option value="title">A – Z</option>
        </select>
      </p>

      <p class="controls__count" role="status" data-count>{len(works)} works</p>
    </div>

    <div class="shell section--tight section--after-title">
      <div class="gallery" id="gallery" role="list" data-viewer-group>
{cards}
      </div>
      <div class="gallery-empty" hidden data-empty>
        <p>No work matches this selection.</p>
        <button class="chip" type="button" data-reset>Show every work</button>
      </div>
    </div>
  </main>
""" + footer() + viewer() + tail())


def build_events(page: dict) -> str:
    events = [
        ("art-exhibition.html", page["event-exhibition"], "Art Exhibition",
         "Noho House Gallery, Barcelona", "January 23, 2025"),
        ("the-temptation.html", page["event-temptation"], "Dark &amp; Light as the love: the Temptation",
         "A film", ""),
    ]
    cards = "\n".join(f"""        <a class="event reveal" href="{href}">
          <div class="event__frame">{img(cover, SIZES['half'], title.replace('&amp;', '&'), target=900)}</div>
          <div>
            <h2 class="event__title">{title}</h2>
            <p class="cartel" style="margin-top:.4rem"><span>{venue}</span>{f'<span>{when}</span>' if when else ''}</p>
          </div>
        </a>""" for href, cover, title, venue, when in events)

    return (head(f'Events — {STUDIO["name"]}',
                 "Exhibitions and films by Juliana Haggoo, including Noho House Gallery Barcelona, "
                 "January 2025.",
                 canonical="events.html", og=page["event-exhibition"])
            + masthead("events.html") + f"""
  <main id="main">
    <section class="shell section--tight">
      <ul class="breadcrumb">
        <li><a href="index.html">Home</a></li>
        <li>Events</li>
      </ul>
      <h1 class="page-title">Events</h1>
    </section>

    <section class="shell section--tight section--after-title">
      <div class="grid-2">
{cards}
      </div>
    </section>
  </main>
""" + footer() + tail())


def build_exhibition(photos: list[dict], page: dict) -> str:
    poster = next(s for s in page["event-exhibition"]["srcset"] if s["w"] >= 900)
    tiles = "\n".join(f"""        <span data-viewer-item data-title="Noho House Gallery, Barcelona"
          data-spec="Art Exhibition · January 23, 2025">
          <button type="button" data-viewer-open aria-label="Enlarge photograph {i}">
            {img(photo, SIZES['photo'], f'Art exhibition at Noho House Gallery, Barcelona — photograph {i}',
                 loading='eager' if i <= 4 else 'lazy', target=800)}
          </button>
        </span>""" for i, photo in enumerate(photos, 1))

    return (head(f'Art Exhibition, Barcelona — {STUDIO["name"]}',
                 "Art Exhibition — January 23, 2025, at Noho House Gallery, Barcelona.",
                 canonical="art-exhibition.html", og=page["event-exhibition"])
            + masthead("events.html") + f"""
  <main id="main">
    <section class="shell section--tight">
      <ul class="breadcrumb">
        <li><a href="index.html">Home</a></li>
        <li><a href="events.html">Events</a></li>
        <li>Art Exhibition</li>
      </ul>
      <h1 class="page-title">Art Exhibition</h1>
      <p class="cartel" style="margin-top:1.25rem"><span>Noho House Gallery, Barcelona</span>
        <span>January 23, 2025</span></p>
    </section>

    <section class="shell section--tight section--after-title">
      <div class="film">
        <video controls preload="none" playsinline poster="{url(poster['src'])}"
          width="1920" height="1080">
          <source src="images/Art-Exhibition-video.mp4" type="video/mp4">
          Your browser does not support the video tag.
        </video>
      </div>
      <p class="film__note">Film from the opening — press play to load it.</p>
    </section>

    <section class="shell section--tight" data-viewer-group>
      <div class="section-head">
        <h2 class="section-title">The evening</h2>
        <p class="cartel more">{len(photos)} photographs</p>
      </div>
      <div class="photos">
{tiles}
      </div>
    </section>
  </main>
""" + footer() + viewer() + tail())


def build_temptation(page: dict) -> str:
    poster = next(s for s in page["event-temptation"]["srcset"] if s["w"] >= 900)
    return (head(f'Dark & Light as the love: the Temptation — {STUDIO["name"]}',
                 "Dark & Light as the love: the Temptation — a film by Juliana Haggoo.",
                 canonical="the-temptation.html", og=page["event-temptation"])
            + masthead("events.html") + f"""
  <main id="main">
    <section class="shell section--tight">
      <ul class="breadcrumb">
        <li><a href="index.html">Home</a></li>
        <li><a href="events.html">Events</a></li>
        <li>The Temptation</li>
      </ul>
      <h1 class="page-title">Dark &amp; Light as the love:<br>the Temptation</h1>
    </section>

    <section class="shell section--tight section--after-title">
      <div class="film">
        <video controls preload="none" playsinline poster="{url(poster['src'])}"
          width="1080" height="1080">
          <source src="images/the-temptation.mp4" type="video/mp4">
          Your browser does not support the video tag.
        </video>
      </div>
      <p class="film__note">Press play to load the film.</p>
      <p style="margin-top:2.5rem"><a class="button button--ghost" href="events.html">Back to events</a></p>
    </section>
  </main>
""" + footer() + tail())


def build_work(work: dict, previous: dict, following: dict, related: list[dict]) -> str:
    alt = f'{work["title"]} — {work["medium"].lower()} painting, {work["year"]}'
    subject = quote(f'Enquiry — {work["title"]} ({work["year"]})')

    views = ""
    if work["views"]:
        tiles = "\n".join(f"""        <span data-viewer-item data-title="{e(work['title'])}"
          data-spec="{e(spec_text(work))}">
          <button type="button" data-viewer-open aria-label="Enlarge view {i} of {e(work['title'])}">
            {img(view, SIZES['third'], f'{work["title"]} — view {i}', target=900)}
          </button>
        </span>""" for i, view in enumerate(work["views"], 1))
        views = f"""
    <section class="shell section--tight" data-viewer-group>
      <div class="section-head">
        <h2 class="section-title">In situ</h2>
      </div>
      <div class="views">
{tiles}
      </div>
    </section>
"""

    cards = "\n".join(teaser(w) for w in related)
    facts = [("Medium", f'{work["medium"]} on canvas'), ("Year", str(work["year"])),
             ("Dimensions", work["size"]),
             ("Status", "Sold" if work["sold"] else (work["price"] or "On request"))]
    fact_rows = "\n".join(
        f'          <div><dt>{label}</dt>\n            <dd>{e(value)}</dd>\n          </div>'
        for label, value in facts)

    enquire = ("" if work["sold"] else
               f'          <p><a class="button" href="mailto:{STUDIO["email"]}?subject={subject}">'
               f'Enquire about this work</a></p>\n')

    return (head(f'{work["title"]} — {STUDIO["name"]}',
                 f'{work["title"]}, {work["medium"].lower()} on canvas, {work["year"]}, '
                 f'{work["size"]}. By Juliana Haggoo.',
                 canonical=url(work["page"]), og=work["canvas"])
            + masthead("portfolio.html") + f"""
  <main id="main">
    <section class="shell section--tight">
      <ul class="breadcrumb">
        <li><a href="index.html">Home</a></li>
        <li><a href="portfolio.html">Portfolio</a></li>
        <li>{e(work['title'])}</li>
      </ul>
      <h1 class="page-title">{e(work['title'])}</h1>
    </section>

    <section class="shell section--tight section--after-title" data-viewer-group>
      <div class="work">
        <div class="work__canvas" data-viewer-item data-title="{e(work['title'])}"
          data-spec="{e(spec_text(work))}" data-tag="{e(work['tag'])}">
          <button type="button" data-viewer-open style="display:block;width:100%;padding:0"
            aria-label="Enlarge {e(work['title'])}">
            {plate(work['canvas'], SIZES['canvas'], alt, loading='eager', target=1400)}
          </button>
        </div>
        <div class="work__side">
          <dl class="work__facts">
{fact_rows}
          </dl>
{enquire}          <p><a class="link-quiet" href="portfolio.html">Back to the portfolio</a></p>
        </div>
      </div>
    </section>
{views}
    <section class="shell section--tight" data-viewer-group>
      <div class="section-head">
        <h2 class="section-title">More works</h2>
        <a class="link-quiet more" href="portfolio.html">All works</a>
      </div>
      <div class="grid-3">
{cards}
      </div>
    </section>

    <nav class="shell pager" aria-label="Works">
      <a href="{url(previous['page'])}">
        <span class="eyebrow">Previous</span>
        <strong>{e(previous['title'])}</strong>
      </a>
      <a href="{url(following['page'])}">
        <span class="eyebrow">Next</span>
        <strong>{e(following['title'])}</strong>
      </a>
    </nav>
  </main>
""" + footer() + viewer() + tail())


# ---------------------------------------------------------------------- main

def main() -> None:
    manifest = json.load(open(os.path.join(HERE, "site.json"), encoding="utf-8"))
    works, photos, page = manifest["works"], manifest["exhibition"], manifest["page"]
    assert len(works) == len(ARTWORKS), "manifest is stale — run build-images.py first"

    write("index.html", build_home(works, page))
    write("about-me.html", build_about(page))
    write("portfolio.html", build_portfolio(works))
    write("events.html", build_events(page))
    write("art-exhibition.html", build_exhibition(photos, page))
    write("the-temptation.html", build_temptation(page))

    total = len(works)
    for i, work in enumerate(works):
        related = [works[(i + n) % total] for n in (1, 2, 3)]
        write(work["page"], build_work(work, works[(i - 1) % total], works[(i + 1) % total], related))

    pages = 6 + total
    weight = sum(os.path.getsize(os.path.join(ROOT, f))
                 for f in os.listdir(ROOT) if f.endswith(".html"))
    print(f"rendered {pages} pages — {weight / 1024:.0f} KB of HTML in total")


if __name__ == "__main__":
    main()
