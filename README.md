# julianahaggoo-clone

Static mirror of [julianahaggoo.art](https://julianahaggoo.art/), the official portfolio website of artist **Juliana Haggoo**.

## Credits

- **Artist & copyright holder:** Juliana Haggoo — [julianahaggoo.art](https://julianahaggoo.art/)
- All artworks, photographs, written content, and the original site design are the property of Juliana Haggoo.
- This mirror is published with the artist's permission.
- Contact: jh@julianahaggoo.art

## Contents

- 42 pages: home, about, portfolio, events, the Barcelona exhibition, the Temptation film, and one page per painting
- `css/atelier.css` — the whole design system, one file for every page
- `js/atelier.js` — the whole behaviour: menu, reveal, lightbox, portfolio grid
- `images/` — the artist's masters, untouched
- `images/{gallery,plates,exhibition,page}/` — responsive WebP renditions the pages actually link to (generated)
- `tools/` — the build
- `tests/` — browser tests

## The build

Every page is **generated**. Do not edit the `.html` files: they are overwritten.
Edit one of these instead, then rebuild.

| To change | Edit |
| --- | --- |
| a painting, its price, its plates | `tools/artworks.py` |
| the look of anything | `css/atelier.css` |
| behaviour | `js/atelier.js` |
| a page's structure or copy | `tools/build-site.py` |

```sh
python3 tools/build-images.py   # re-encode the WebP renditions → tools/site.json
python3 tools/build-site.py     # render the 42 pages
# or both:
npm run build
```

`build-images.py` needs Pillow (`pip install Pillow`). For each painting it picks the
truest, highest-resolution rendition in the repository — separating the canvas from the
photographs of it hanging by comparing luminance fingerprints — and emits a WebP ladder
plus an inline blur-up placeholder. The originals are never modified.

The catalogue in `tools/artworks.py` is the single source of truth: the works, their order,
their prices, and the plates each one shows.

## Design

White wall, hairline rules, and no colour of its own — every colour on the site comes from
a painting. Italiana for display, Cormorant Garamond for titles and prose, the system sans
for labels. The portfolio never shows more than three canvases across, so each one has room.

## Run locally

```sh
npm run dev     # python3 -m http.server 8000
```

## Test

```sh
npm install
npx playwright install chromium
npm test
```

Drives a real browser over layout, filtering, sorting, deep links, the lightbox, mobile
reflow, reduced motion, the no-JavaScript fallback, and the existence of every linked page
and image rendition.

## License

Code structure of this repository: see repo settings.
**All artistic content (images, video, written text) remains © Juliana Haggoo and is not relicensed.** Do not redistribute the artwork without the artist's permission.
