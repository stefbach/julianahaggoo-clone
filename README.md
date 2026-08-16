# julianahaggoo-clone

Static mirror of [julianahaggoo.art](https://julianahaggoo.art/), the official portfolio website of artist **Juliana Haggoo**.

## Credits

- **Artist & copyright holder:** Juliana Haggoo — [julianahaggoo.art](https://julianahaggoo.art/)
- All artworks, photographs, written content, and the original site design are the property of Juliana Haggoo.
- This mirror is published with the artist's permission.
- Contact: jh@julianahaggoo.art

## Contents

- 42 HTML pages (home, about, portfolio, events, individual artwork pages, art exhibition gallery)
- `css/` — Bootstrap, custom styles, font definitions
- `js/` — site scripts (`core.min.js`, `script.js`)
- `fonts/` — FontAwesome, Material Design Icons, lightGallery icon font
- `images/` — artwork images, gallery photos, branding, video assets
- `images/gallery/` — responsive WebP renditions used by the portfolio page (generated)
- `tools/` — the portfolio build pipeline
- `tests/` — browser tests for the portfolio page

## Portfolio page

`portfolio.html` is a self-contained document: it carries its own CSS and JavaScript
and loads none of `css/` or `js/`. It is **generated** — edit
`tools/portfolio.template.html` (markup, styles, behaviour) or the `ARTWORKS`
table in `tools/build-gallery.py` (the works themselves), never the output.

```sh
npm run build:gallery    # re-encode the WebP ladder, then render the page
npm run build:portfolio  # render the page only (needs tools/gallery.json)
```

`tools/build-gallery.py` needs Pillow (`pip install Pillow`). For each work it
picks the highest-resolution rendition in the repo — guarding against the room
mock-ups that sit alongside the canvases on the artwork pages — and emits a
400/640/900/1400/1800px WebP ladder plus an inline blur-up placeholder into
`tools/gallery.json`.

## Test

```sh
npm install
npx playwright install chromium
npm test
```

## Run locally

The site is fully static. Serve the repo root with any static server:

```sh
python3 -m http.server 8000
# then open http://localhost:8000/
```

## Source

Captured from the live site with `wget --mirror --convert-links --adjust-extension --page-requisites`.

## License

Code structure of this repository: see repo settings.
**All artistic content (images, video, written text) remains © Juliana Haggoo and is not relicensed.** Do not redistribute the artwork without the artist's permission.
