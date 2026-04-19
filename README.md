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
