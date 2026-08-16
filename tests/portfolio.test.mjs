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
    assert.equal(result.columns, 3, 'three columns at 1440px');
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
    assert.equal(await page.$$eval('.card[data-in]', (c) => c.length), 36);
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
