/**
 * Behavioural tests for the portfolio gallery.
 *
 *   npm test
 *
 * Serves the repo root, then drives a real browser: layout packing, filtering,
 * sorting, deep-linkable state, the viewer, and the no-JavaScript fallback.
 */
import { after, before, describe, it } from 'node:test';
import assert from 'node:assert/strict';
import { createServer } from 'node:http';
import { readFile, readdir } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import { extname, join, normalize } from 'node:path';
import { fileURLToPath } from 'node:url';
import { chromium } from 'playwright';

const ROOT = fileURLToPath(new URL('..', import.meta.url));
const TYPES = {
  '.html': 'text/html', '.css': 'text/css', '.js': 'text/javascript',
  '.webp': 'image/webp', '.png': 'image/png', '.jpg': 'image/jpeg',
  '.webm': 'video/webm', '.svg': 'image/svg+xml',
};

let server, browser, origin;

before(async () => {
  server = createServer(async (req, res) => {
    const path = normalize(decodeURIComponent(req.url.split('?')[0])).replace(/^(\.\.[/\\])+/, '');
    try {
      const body = await readFile(join(ROOT, path));
      res.writeHead(200, { 'content-type': TYPES[extname(path)] ?? 'application/octet-stream' });
      res.end(body);
    } catch {
      res.writeHead(404).end();
    }
  });
  await new Promise((done) => server.listen(0, '127.0.0.1', done));
  origin = `http://127.0.0.1:${server.address().port}`;

  browser = await launchChromium();
});

/**
 * Launch Playwright's own Chromium, falling back to a browser already present in
 * PLAYWRIGHT_BROWSERS_PATH when the installed build does not match.
 */
async function launchChromium() {
  const explicit = process.env.CHROMIUM_PATH;
  if (explicit) return chromium.launch({ executablePath: explicit });
  try {
    return await chromium.launch();
  } catch (error) {
    const pool = process.env.PLAYWRIGHT_BROWSERS_PATH;
    if (!pool) throw error;
    const [found] = (await readdir(pool))
      .filter((entry) => entry.startsWith('chromium-'))
      .map((entry) => join(pool, entry, 'chrome-linux', 'chrome'))
      .filter(existsSync);
    if (!found) throw error;
    return chromium.launch({ executablePath: found });
  }
}

after(async () => {
  await browser?.close();
  server?.close();
});

/** Open the portfolio, wait for the grid to settle, and hand back the page. */
async function open(query = '', options = {}) {
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 }, ...options });
  const page = await context.newPage();
  const failures = [];
  page.on('pageerror', (e) => failures.push(e.message));
  await page.goto(`${origin}/portfolio.html${query}`, { waitUntil: 'domcontentloaded' });
  await page.waitForFunction(() => document.querySelector('#gallery')?.classList.contains('is-live'));
  page.failures = failures;
  return page;
}

const shown = (page) =>
  page.$$eval('.card:not([data-out])', (cards) => cards.map((c) => c.dataset.title));

describe('portfolio gallery', () => {
  it('lays every work out without overlap or horizontal overflow', async () => {
    const page = await open();
    const result = await page.evaluate(() => {
      const rects = [...document.querySelectorAll('.card:not([data-out])')].map((c) => c.getBoundingClientRect());
      let overlaps = 0;
      for (let i = 0; i < rects.length; i++) {
        for (let j = i + 1; j < rects.length; j++) {
          const a = rects[i], b = rects[j];
          if (a.left < b.right - 1 && b.left < a.right - 1 && a.top < b.bottom - 1 && b.top < a.bottom - 1) overlaps++;
        }
      }
      return {
        cards: rects.length,
        overlaps,
        columns: new Set(rects.map((r) => Math.round(r.left))).size,
        overflowX: document.documentElement.scrollWidth - document.documentElement.clientWidth,
        galleryHeight: Math.round(document.querySelector('#gallery').getBoundingClientRect().height),
      };
    });

    assert.equal(result.cards, 36);
    assert.equal(result.overlaps, 0);
    assert.equal(result.columns, 3, 'never more than three canvases across');
    assert.equal(result.overflowX, 0);
    assert.ok(result.galleryHeight > 1000, 'gallery is given an explicit height');
    assert.deepEqual(page.failures, []);
  });

  it('filters by medium and reports the count', async () => {
    const page = await open();
    await page.click('.chip[data-value="Acrylic"]');
    await page.waitForFunction(() => document.querySelectorAll('.card:not([data-out])').length === 2);

    assert.deepEqual((await shown(page)).sort(), ['Deep Blue', 'In Shades of Pink']);
    assert.equal(await page.textContent('[data-count]'), '2 works');
    assert.equal(new URL(page.url()).search, '?medium=Acrylic');
  });

  it('hides collected works behind the availability toggle', async () => {
    const page = await open();
    await page.click('.chip[data-value="available"]');
    await page.waitForFunction(() => document.querySelector('[data-count]').textContent === '25 works');

    const sold = await page.$$eval('.card:not([data-out])', (c) => c.filter((x) => x.dataset.status === 'sold').length);
    assert.equal(sold, 0);
  });

  it('sorts alphabetically and in both chronological directions', async () => {
    const page = await open();

    await page.selectOption('#sort-select', 'title');
    await page.waitForFunction(() => document.querySelector('.card:not([data-out])').dataset.title === 'Blue Bubble');
    const alpha = await shown(page);
    assert.deepEqual(alpha, [...alpha].sort((a, b) => a.localeCompare(b, 'en')));

    await page.selectOption('#sort-select', 'oldest');
    await page.waitForFunction(() => document.querySelector('.card:not([data-out])').dataset.year === '2009');

    await page.selectOption('#sort-select', 'recent');
    await page.waitForFunction(() => document.querySelector('.card:not([data-out])').dataset.year === '2025');
  });

  it('keeps DOM order in step with visual order', async () => {
    const page = await open();
    await page.selectOption('#sort-select', 'title');
    await page.waitForFunction(() => document.querySelector('.card:not([data-out])').dataset.title === 'Blue Bubble');

    const inOrder = await page.evaluate(() => {
      const cards = [...document.querySelectorAll('.card:not([data-out])')];
      return cards.every((c, i) => i === 0 || !(cards[i - 1].compareDocumentPosition(c) & Node.DOCUMENT_POSITION_PRECEDING));
    });
    assert.ok(inOrder, 'tab order follows the sorted order');
  });

  it('restores state from the URL', async () => {
    const page = await open('?medium=Oil&year=2022&sort=title');

    assert.equal(await page.inputValue('#year-select'), '2022');
    assert.equal(await page.inputValue('#sort-select'), 'title');
    assert.equal(await page.getAttribute('.chip[data-value="Oil"]', 'aria-pressed'), 'true');
    assert.deepEqual(await shown(page), [
      'Blue White', 'Intensity', 'Rise Like a Sun', 'Summer',
      'The 7 Hearts', 'The Curve', 'The Wall', 'Waves',
    ]);
  });

  it('offers a way out of an empty result', async () => {
    const page = await open('?medium=Acrylic&year=2009');
    await page.waitForFunction(() => !document.querySelector('[data-empty]').hidden);
    assert.equal(await page.textContent('[data-count]'), '0 works');

    await page.click('[data-reset]');
    await page.waitForFunction(() => document.querySelector('[data-count]').textContent === '36 works');
    assert.equal(new URL(page.url()).search, '');
  });

  it('opens the viewer from the keyboard and gives focus back on close', async () => {
    const page = await open();
    await page.evaluate(() => document.querySelector('.card .card__zoom').focus());
    await page.keyboard.press('Enter');
    await page.waitForFunction(() => document.querySelector('#viewer').open);

    assert.equal(await page.textContent('[data-viewer-title]'), 'Summer');
    assert.equal(await page.textContent('[data-viewer-index]'), '1 / 36');
    assert.ok(await page.evaluate(() => document.querySelector('#viewer').contains(document.activeElement)));

    await page.keyboard.press('ArrowRight');
    await page.waitForFunction(() => document.querySelector('[data-viewer-title]').textContent === 'The Red');

    await page.keyboard.press('Escape');
    await page.waitForFunction(() => !document.querySelector('#viewer').open);
    assert.ok(await page.evaluate(() => document.activeElement.classList.contains('card__zoom')));
  });

  it('fits the plate inside the viewer without covering the caption', async () => {
    const page = await open();
    await page.evaluate(() => document.querySelector('.card .card__zoom').click());
    await page.waitForFunction(() => document.querySelector('[data-viewer-plate]'));

    const { plateBottom, barTop } = await page.evaluate(() => ({
      plateBottom: document.querySelector('[data-viewer-plate]').getBoundingClientRect().bottom,
      barTop: document.querySelector('.viewer__bar').getBoundingClientRect().top,
    }));
    assert.ok(plateBottom <= barTop, `plate overruns the caption bar by ${plateBottom - barTop}px`);
  });

  it('walks only the works currently on show', async () => {
    const page = await open('?medium=Acrylic');
    await page.waitForFunction(() => document.querySelectorAll('.card:not([data-out])').length === 2);
    await page.evaluate(() => document.querySelector('.card:not([data-out]) .card__zoom').click());
    await page.waitForFunction(() => document.querySelector('#viewer').open);

    assert.equal(await page.textContent('[data-viewer-index]'), '1 / 2');
    await page.keyboard.press('ArrowRight');
    await page.waitForFunction(() => document.querySelector('[data-viewer-index]').textContent === '2 / 2');
    await page.keyboard.press('ArrowRight');
    await page.waitForFunction(() => document.querySelector('[data-viewer-index]').textContent === '1 / 2');
  });

  it('reflows to one column on a phone', async () => {
    const page = await open('', { viewport: { width: 390, height: 844 } });
    const { columns, overflowX } = await page.evaluate(() => {
      const rects = [...document.querySelectorAll('.card:not([data-out])')].map((c) => c.getBoundingClientRect());
      return {
        columns: new Set(rects.map((r) => Math.round(r.left))).size,
        overflowX: document.documentElement.scrollWidth - document.documentElement.clientWidth,
      };
    });
    assert.equal(columns, 1);
    assert.equal(overflowX, 0);
  });

  it('reveals every work up front when motion is not welcome', async () => {
    const page = await open('', { reducedMotion: 'reduce' });
    assert.equal(await page.$$eval('.card .reveal[data-in]', (c) => c.length), 36);
  });

  it('holds to three columns on a wide desktop too', async () => {
    const page = await open('', { viewport: { width: 1920, height: 1080 } });
    const columns = await page.evaluate(() =>
      new Set([...document.querySelectorAll('.card:not([data-out])')]
        .map((c) => Math.round(c.getBoundingClientRect().left))).size);
    assert.equal(columns, 3);
  });

  it('renders the artworks with JavaScript disabled', async () => {
    const context = await browser.newContext({ viewport: { width: 1280, height: 900 }, javaScriptEnabled: false });
    const page = await context.newPage();
    await page.goto(`${origin}/portfolio.html`, { waitUntil: 'load' });

    const state = await page.evaluate(() => ({
      cards: document.querySelectorAll('.card').length,
      opaque: [...document.querySelectorAll('.card img')].every((i) => getComputedStyle(i).opacity === '1'),
      columns: getComputedStyle(document.querySelector('.gallery')).columnCount,
    }));
    assert.equal(state.cards, 36);
    assert.ok(state.opaque, 'images must not depend on a JS class to become visible');
    assert.notEqual(state.columns, '1', 'the no-JS fallback still uses a multi-column layout');
    await context.close();
  });

  it('links every card to an artwork page that exists', async () => {
    const page = await open();
    const hrefs = await page.$$eval('.card__link', (links) => links.map((l) => new URL(l.href).pathname));
    const codes = await Promise.all(hrefs.map(async (p) => (await fetch(origin + p)).status));
    assert.deepEqual([...new Set(codes)], [200]);
  });

  it('ships every image rendition it advertises', async () => {
    const page = await open();
    const sources = await page.$$eval('.card img', (imgs) =>
      imgs.flatMap((i) => i.srcset.split(',').map((s) => s.trim().split(' ')[0])));
    const codes = await Promise.all(sources.map(async (s) => (await fetch(`${origin}/${s}`)).status));
    assert.deepEqual([...new Set(codes)], [200], 'a srcset entry is missing from images/gallery');
  });
});

describe('the home carousel', () => {
  /** Open the home page and wait for the carousel to take over. */
  async function home(options = {}, lang = 'en') {
    const context = await browser.newContext({ viewport: { width: 1440, height: 950 }, ...options });
    const page = await context.newPage();
    const failures = [];
    page.on('pageerror', (e) => failures.push(e.message));
    await page.goto(`${origin}/${lang === 'fr' ? 'fr/' : ''}index.html`, { waitUntil: 'domcontentloaded' });
    await page.waitForFunction(() => document.querySelector('[data-slide-status]')?.textContent);
    page.failures = failures;
    return page;
  }

  const at = (page) => page.textContent('[data-slide-status]');
  const COUNT = 2;
  const SLIDE = { en: (n) => `Slide ${n} of ${COUNT}`, fr: (n) => `Diapositive ${n} sur ${COUNT}` };

  it('opens on the artist beside the black and white canvas', async () => {
    const page = await home();
    const slides = await page.$$eval('[data-slide] img', (imgs) =>
      imgs.map((i) => ({ src: i.getAttribute('src').split('/').pop(), alt: i.alt })));

    assert.equal(slides.length, COUNT);
    assert.match(slides[0].src, /^slide-monochrome-/);
    assert.match(slides[0].alt, /black and white/);
    assert.match(slides[1].src, /^slide-studio-/);
    assert.deepEqual(page.failures, []);
  });

  it('has every slide in hand before anyone clicks', async () => {
    const page = await home();
    // A slide waiting off-screen must not download on the click that reveals it.
    await page.waitForFunction(
      () => [...document.querySelectorAll('[data-slide] img')].every((i) => i.complete && i.naturalWidth),
      null, { timeout: 15000 });
  });

  it('steps forward, back, and wraps around', async () => {
    const page = await home();
    const lands = (n) => page.waitForFunction(
      (want) => document.querySelector('[data-slide-status]').textContent === want, n);

    assert.equal(await at(page), SLIDE.en(1));

    for (let i = 2; i <= COUNT; i++) {
      await page.click('[data-slide-next]');
      await lands(SLIDE.en(i));
    }
    await page.click('[data-slide-next]');
    await lands(SLIDE.en(1));

    await page.click('[data-slide-prev]');
    await lands(SLIDE.en(COUNT));
  });

  it('jumps from the dots and marks the current one', async () => {
    const page = await home();
    const last = COUNT - 1;
    assert.equal(await page.$$eval('[data-slide-to]', (d) => d.length), COUNT, 'one dot per slide');

    await page.click(`[data-slide-to="${last}"]`);
    await page.waitForFunction(
      (want) => document.querySelector('[data-slide-status]').textContent === want,
      SLIDE.en(COUNT));

    const current = await page.$$eval('[data-slide-to]', (d) =>
      d.findIndex((x) => x.hasAttribute('aria-current')));
    assert.equal(current, last);

    const hidden = await page.$$eval('[data-slide]', (s) => s.map((x) => x.hasAttribute('aria-hidden')));
    assert.deepEqual(hidden, hidden.map((_, i) => i !== last), 'only the visible slide is exposed');
  });

  it('keeps rotating, not just once', async () => {
    // It used to advance a single time and stop: the timer called show()
    // instead of go(), so it never re-armed itself.
    const page = await home();
    await page.mouse.move(5, 5); // away from the carousel, so hover does not pause it

    for (const round of [2, 1, 2]) {
      await page.waitForFunction(
        (want) => document.querySelector('[data-slide-status]').textContent === want,
        SLIDE.en(round), { timeout: 9000 });
    }
  });

  it('advances briskly — a slide should not outstay its welcome', async () => {
    const page = await home();
    await page.mouse.move(5, 5);
    const first = await at(page);

    const started = Date.now();
    await page.waitForFunction(
      (was) => document.querySelector('[data-slide-status]').textContent !== was,
      first, { timeout: 9000 });
    const dwell = Date.now() - started;

    assert.ok(dwell < 5000, `a slide held for ${dwell}ms — too slow`);
    assert.ok(dwell > 1200, `a slide held for only ${dwell}ms — too fast to read`);
  });

  it('stops when told to', async () => {
    const page = await home();
    await page.mouse.move(5, 5);

    await page.waitForFunction(
      (want) => document.querySelector('[data-slide-status]').textContent === want,
      SLIDE.en(2), { timeout: 9000 });

    await page.click('[data-slide-toggle]');
    assert.equal(await page.textContent('[data-slide-toggle-label]'), 'Play');
    const held = await at(page);
    await page.waitForTimeout(8000);
    assert.equal(await at(page), held, 'a paused carousel must stay put');
  });

  it('holds still for anyone who asked for stillness', async () => {
    const page = await home({ reducedMotion: 'reduce' });
    assert.equal(await page.textContent('[data-slide-toggle-label]'), 'Play');
    const first = await at(page);
    await page.waitForTimeout(8000);
    assert.equal(await at(page), first, 'no autoplay under prefers-reduced-motion');

    await page.click('[data-slide-next]');
    await page.waitForFunction(
      (want) => document.querySelector('[data-slide-status]').textContent === want,
      SLIDE.en(2));
  });

  it('speaks French on the French home page', async () => {
    const page = await home({}, 'fr');
    assert.equal(await at(page), SLIDE.fr(1));
    assert.equal(await page.textContent('[data-slide-toggle-label]'), 'Pause');

    await page.click('[data-slide-next]');
    await page.waitForFunction(
      (want) => document.querySelector('[data-slide-status]').textContent === want, SLIDE.fr(2));
    assert.deepEqual(page.failures, []);
  });

  it('fits a phone without spilling sideways', async () => {
    const page = await home({ viewport: { width: 390, height: 844 } });
    assert.equal(await page.evaluate(
      () => document.documentElement.scrollWidth - document.documentElement.clientWidth), 0);
  });
});

describe('both languages', () => {
  const NAMES = ['index.html', 'about-me.html', 'portfolio.html', 'events.html',
    'art-exhibition.html', 'the-temptation.html', 'summer-2025.html'];

  async function visit(path, options = {}) {
    const context = await browser.newContext({ viewport: { width: 1280, height: 900 }, ...options });
    const page = await context.newPage();
    await page.goto(`${origin}/${path}`, { waitUntil: 'domcontentloaded' });
    return page;
  }

  it('serves a French twin of every page', async () => {
    for (const name of NAMES) {
      const page = await visit(`fr/${name}`);
      assert.equal(await page.evaluate(() => document.documentElement.lang), 'fr', name);
      assert.ok(await page.$('.masthead'), name);
      await page.context().close();
    }
  });

  it('declares each page as the alternate of the other', async () => {
    for (const [path, self] of [['portfolio.html', ''], ['fr/portfolio.html', 'fr/']]) {
      const page = await visit(path);
      const links = await page.$$eval('link[rel="alternate"]', (l) =>
        l.map((x) => `${x.hreflang} ${new URL(x.href).pathname}`));
      assert.ok(links.includes('en /portfolio.html'), `${path}: ${links}`);
      assert.ok(links.includes('fr /fr/portfolio.html'), `${path}: ${links}`);
      assert.ok(links.includes('x-default /portfolio.html'), `${path}: ${links}`);

      const canonical = await page.$eval('link[rel="canonical"]', (l) => new URL(l.href).pathname);
      assert.equal(canonical, `/${self}portfolio.html`);
      await page.context().close();
    }
  });

  it('switches language on the same page, and back', async () => {
    const page = await visit('portfolio.html');
    assert.equal(await page.textContent('.masthead__lang'), 'Français');

    await page.click('.masthead__lang');
    await page.waitForURL(/\/fr\/portfolio\.html$/);
    assert.equal(await page.textContent('.masthead__lang'), 'English');

    await page.click('.masthead__lang');
    await page.waitForURL(/\/portfolio\.html$/);
    assert.equal(await page.evaluate(() => document.documentElement.lang), 'en');
    await page.context().close();
  });

  it('translates the furniture but never a painting', async () => {
    const page = await visit('fr/portfolio.html');
    await page.waitForFunction(() => document.querySelector('#gallery')?.classList.contains('is-live'));

    assert.equal(await page.textContent('h1'), 'Portfolio');
    assert.equal(await page.textContent('[data-count]'), '36 œuvres');
    assert.deepEqual(await page.$$eval('.chip[data-filter]', (c) => c.map((x) => x.textContent.trim())),
      ['Toutes', 'Huile', 'Acrylique', 'Disponibles seulement']);

    // The works keep their names — a gallery label does not rename a canvas.
    const titles = await page.$$eval('.card__title', (h) => h.map((x) => x.textContent.trim()));
    assert.ok(titles.includes('Serenity of Motion'), titles.slice(0, 5).join(', '));
    assert.ok(titles.includes('The Red'));

    await page.click('.chip[data-value="Acrylic"]');
    await page.waitForFunction(() => document.querySelector('[data-count]').textContent === '2 œuvres');
    await page.context().close();
  });

  it('says Vendu on a French artwork page', async () => {
    const page = await visit('fr/the-red.html');
    const rows = await page.$$eval('.work__facts div', (r) =>
      r.map((x) => x.textContent.replace(/\s+/g, ' ').trim()));
    assert.ok(rows.includes('Statut Vendu'), rows.join(' | '));
    assert.ok(rows.some((r) => r.startsWith('Technique Huile')), rows.join(' | '));
    assert.equal(await page.textContent('h1'), 'The Red', 'the title of the work is not translated');
    await page.context().close();
  });

  it('keeps the French pages pointing at real assets', async () => {
    for (const name of ['fr/index.html', 'fr/portfolio.html', 'fr/summer-2025.html']) {
      const missing = [];
      const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
      const page = await context.newPage();
      page.on('response', (r) => { if (r.status() === 404) missing.push(`${name}: ${r.url()}`); });
      await page.goto(`${origin}/${name}`, { waitUntil: 'networkidle' });
      assert.deepEqual(missing, []);
      await context.close();
    }
  });

  it('navigates within its own language', async () => {
    const page = await visit('fr/index.html');
    await page.click('.masthead__nav a[href="portfolio.html"]');
    await page.waitForURL(/\/fr\/portfolio\.html$/);
    assert.equal(await page.evaluate(() => document.documentElement.lang), 'fr');
    await page.context().close();
  });
});

describe('the site around it', () => {
  const NAMES = ['index.html', 'about-me.html', 'portfolio.html', 'events.html',
    'art-exhibition.html', 'the-temptation.html', 'summer-2025.html', 'winter.html'];
  const PAGES = [...NAMES, ...NAMES.map((n) => `fr/${n}`)];

  it('serves every page with the shared shell', async () => {
    for (const name of PAGES) {
      const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
      const page = await context.newPage();
      const failures = [];
      page.on('pageerror', (e) => failures.push(`${name}: ${e.message}`));
      const response = await page.goto(`${origin}/${name}`, { waitUntil: 'domcontentloaded' });

      assert.equal(response.status(), 200, name);
      assert.deepEqual(failures, [], name);
      assert.ok(await page.$('.masthead'), `${name} has the header`);
      assert.ok(await page.$('.footer'), `${name} has the footer`);
      assert.ok(await page.$('a.skip-link'), `${name} has a skip link`);
      assert.equal(await page.$$eval('h1', (h) => h.length), 1, `${name} has exactly one h1`);
      await context.close();
    }
  });

  it('paints on white, everywhere', async () => {
    for (const name of ['index.html', 'portfolio.html', 'summer-2025.html']) {
      const context = await browser.newContext();
      const page = await context.newPage();
      await page.goto(`${origin}/${name}`, { waitUntil: 'domcontentloaded' });
      assert.equal(await page.evaluate(() => getComputedStyle(document.body).backgroundColor),
        'rgb(255, 255, 255)', name);
      await context.close();
    }
  });

  it('never asks the browser to fetch a missing image', async () => {
    for (const name of PAGES) {
      const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
      const page = await context.newPage();
      const missing = [];
      page.on('response', (r) => { if (r.status() === 404) missing.push(`${name}: ${r.url()}`); });
      await page.goto(`${origin}/${name}`, { waitUntil: 'networkidle' });
      assert.deepEqual(missing, []);
      await context.close();
    }
  });

  it('walks the whole catalogue with prev / next', async () => {
    const context = await browser.newContext();
    const page = await context.newPage();
    await page.goto(`${origin}/summer-2025.html`, { waitUntil: 'domcontentloaded' });

    const links = await page.$$eval('.pager a', (a) => a.map((x) => new URL(x.href).pathname.slice(1)));
    assert.equal(links.length, 2);
    assert.equal(links[0], 'winter.html', 'the first work wraps back to the last');
    assert.equal(links[1], 'the-red.html');
    await context.close();
  });

  it('opens an artwork plate in the viewer', async () => {
    const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
    const page = await context.newPage();
    await page.goto(`${origin}/serenity-of-motion.html`, { waitUntil: 'networkidle' });

    await page.click('.work__canvas [data-viewer-open]');
    await page.waitForFunction(() => document.querySelector('#viewer').open);
    assert.equal(await page.textContent('[data-viewer-title]'), 'Serenity of Motion');
    assert.match(await page.textContent('[data-viewer-spec]'), /Oil · 2025/);

    await page.keyboard.press('Escape');
    await page.waitForFunction(() => !document.querySelector('#viewer').open);
    await context.close();
  });

  it('says Sold, never Collected', async () => {
    for (const name of ['portfolio.html', 'the-red.html', 'index.html']) {
      const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
      const page = await context.newPage();
      await page.goto(`${origin}/${name}`, { waitUntil: 'domcontentloaded' });
      const text = await page.evaluate(() => document.body.innerText);
      assert.ok(!/Collected/.test(text), `${name} still says Collected`);
      await context.close();
    }

    const context = await browser.newContext();
    const page = await context.newPage();
    await page.goto(`${origin}/the-red.html`, { waitUntil: 'domcontentloaded' });
    const status = await page.$$eval('.work__facts div', (rows) =>
      rows.map((r) => r.textContent.replace(/\s+/g, ' ').trim()));
    assert.ok(status.includes('Status Sold'), status.join(' | '));
    await context.close();
  });

  it('names both studios on the home page', async () => {
    const context = await browser.newContext();
    const page = await context.newPage();
    await page.goto(`${origin}/index.html`, { waitUntil: 'domcontentloaded' });
    assert.match(await page.textContent('.opening .eyebrow'), /Paris\s*&\s*Mauritius/);
    await context.close();
  });

  it('defers the heavy films until someone presses play', async () => {
    const context = await browser.newContext();
    const page = await context.newPage();
    await page.goto(`${origin}/the-temptation.html`, { waitUntil: 'domcontentloaded' });
    const video = await page.$eval('video', (v) => ({ preload: v.preload, poster: !!v.poster }));
    assert.equal(video.preload, 'none', 'a 90 MB film must not download on load');
    assert.ok(video.poster, 'and it needs a poster to stand in for it');
    await context.close();
  });
});
