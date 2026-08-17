/* =============================================================================
   Juliana Haggoo — site behaviour.
   One file for every page. Each module bails out when its markup is absent, so
   an artwork page pays for the lightbox only, and the portfolio for the grid.
   ========================================================================== */
(() => {
  "use strict";

  const $ = (sel, ctx = document) => ctx.querySelector(sel);
  const $$ = (sel, ctx = document) => [...ctx.querySelectorAll(sel)];
  const calm = matchMedia("(prefers-reduced-motion: reduce)");

  document.documentElement.classList.remove("no-js");

  // Not [data-year] — every card carries that, and this would erase the first one.
  const year = $("[data-copyright-year]");
  if (year) year.textContent = new Date().getFullYear();

  /* -------------------------------------------------------------- masthead */
  const sentinel = $("[data-sentinel]");
  const masthead = $(".masthead");
  if (sentinel && masthead) {
    new IntersectionObserver(([entry]) =>
      masthead.toggleAttribute("data-stuck", !entry.isIntersecting)).observe(sentinel);
  }

  /* ---------------------------------------------------------------- drawer */
  const drawer = $("#drawer");
  if (drawer) {
    $("[data-menu-open]")?.addEventListener("click", () => drawer.showModal());
    $("[data-menu-close]")?.addEventListener("click", () => drawer.close());
    drawer.addEventListener("click", (e) => { if (e.target === drawer) drawer.close(); });
  }

  /* ------------------------------------------------- images, once they land */
  for (const img of $$(".plate img, .views img, .photos img, .event__frame img")) {
    if (img.complete) img.classList.add("is-loaded");
    else img.addEventListener("load", () => img.classList.add("is-loaded"), { once: true });
  }

  /* ----------------------------------------------------------- reveal */
  const pending = new Set();
  const revealer = new IntersectionObserver((entries, obs) => {
    let batch = 0;
    for (const entry of entries) {
      if (!entry.isIntersecting) continue;
      entry.target.style.setProperty("--reveal-delay", `${Math.min(batch++, 8) * 55}ms`);
      entry.target.setAttribute("data-in", "");
      pending.delete(entry.target);
      obs.unobserve(entry.target);
    }
  }, { rootMargin: "0px 0px -6% 0px", threshold: 0.03 });

  /** An element moved by a transform does not re-trigger the observer. */
  function rewatch() {
    for (const el of pending) {
      revealer.unobserve(el);
      revealer.observe(el);
    }
  }

  function watch(el) {
    if (el.hasAttribute("data-in")) return;
    pending.add(el);
    revealer.observe(el);
  }

  if (calm.matches) {
    for (const el of $$(".reveal")) el.setAttribute("data-in", "");
  } else {
    for (const el of $$(".reveal")) watch(el);
  }

  /* --------------------------------------------------------------- viewer */
  /* One dialog serves the portfolio, the artwork pages and the exhibition.
     A trigger names its group; the group decides what prev/next walk. */
  const viewer = $("#viewer");
  const plates = () => visibleGroup ?? group;
  let group = [];
  let visibleGroup = null;
  let cursor = 0;
  let opener = null;

  function paint(index) {
    const list = plates();
    cursor = (index + list.length) % list.length;
    const trigger = list[cursor];
    const source = $("img", trigger);
    const canvas = $(".viewer__canvas", viewer);

    $("[data-viewer-plate]", viewer)?.remove();
    const plate = new Image();
    plate.dataset.viewerPlate = "";
    plate.srcset = source.srcset;
    plate.sizes = "(max-width: 900px) 92vw, 78vw";
    plate.src = source.src;
    plate.width = source.getAttribute("width");
    plate.height = source.getAttribute("height");
    plate.alt = source.alt;
    canvas.appendChild(plate);

    const link = trigger.dataset.href ?? $("a", trigger)?.href ?? "";
    $("[data-viewer-title]", viewer).textContent = trigger.dataset.title ?? "";
    $("[data-viewer-spec]", viewer).textContent = trigger.dataset.spec ?? "";
    $("[data-viewer-tag]", viewer).textContent = trigger.dataset.tag ?? "";
    $("[data-viewer-index]", viewer).textContent = `${cursor + 1} / ${list.length}`;
    const open = $("[data-viewer-link]", viewer);
    open.hidden = !link;
    if (link) open.href = link;
  }

  function openViewer(trigger) {
    const scope = trigger.closest("[data-viewer-group]");
    group = $$("[data-viewer-item]", scope);
    visibleGroup = null;
    if (scope?.id === "gallery") visibleGroup = group.filter((el) => !el.closest(".card[data-out]"));
    const index = plates().indexOf(trigger);
    if (index < 0) return;
    opener = document.activeElement;
    paint(index);
    viewer.showModal();
  }

  if (viewer) {
    document.addEventListener("click", (event) => {
      const trigger = event.target.closest("[data-viewer-open]");
      if (!trigger) return;
      event.preventDefault();
      openViewer(trigger.closest("[data-viewer-item]") ?? trigger);
    });

    $("[data-viewer-close]", viewer).addEventListener("click", () => viewer.close());
    $("[data-viewer-prev]", viewer).addEventListener("click", () => paint(cursor - 1));
    $("[data-viewer-next]", viewer).addEventListener("click", () => paint(cursor + 1));
    viewer.addEventListener("close", () => opener?.focus());
    viewer.addEventListener("keydown", (event) => {
      if (event.key === "ArrowLeft") { event.preventDefault(); paint(cursor - 1); }
      if (event.key === "ArrowRight") { event.preventDefault(); paint(cursor + 1); }
    });

    let swipeFrom = null;
    const canvas = $(".viewer__canvas", viewer);
    canvas.addEventListener("pointerdown", (e) => { swipeFrom = e.clientX; });
    canvas.addEventListener("pointerup", (e) => {
      if (swipeFrom === null) return;
      const delta = e.clientX - swipeFrom;
      swipeFrom = null;
      if (Math.abs(delta) > 60) paint(cursor + (delta < 0 ? 1 : -1));
    });
  }

  /* ------------------------------------------------------------- carousel */
  const slider = $("[data-slider]");
  if (slider) {
    const track = $("[data-track]", slider);
    const slides = $$("[data-slide]", slider);
    const dots = $$("[data-slide-to]", slider);
    const status = $("[data-slide-status]", slider);
    const toggle = $("[data-slide-toggle]", slider);
    const toggleLabel = $("[data-slide-toggle-label]", slider);
    const say = slider.dataset;
    const DWELL = Number(say.dwell) || 3500;

    let index = 0;
    let timer = 0;
    // Anyone who asked for stillness gets a carousel that only moves on demand.
    let playing = !calm.matches;

    function show(next) {
      index = (next + slides.length) % slides.length;
      track.style.transform = `translate3d(${-index * 100}%, 0, 0)`;
      slides.forEach((slide, i) => slide.toggleAttribute("aria-hidden", i !== index));
      dots.forEach((dot, i) => dot.toggleAttribute("aria-current", i === index));
      status.textContent = say.statusTemplate
        .replace("{n}", index + 1).replace("{total}", slides.length);
    }

    function go(next) {
      show(next);
      schedule();
    }

    /* go(), not show(): advancing has to re-arm the timer or the carousel
       moves once and then sits there. */
    function schedule() {
      clearTimeout(timer);
      if (playing) timer = setTimeout(() => go(index + 1), DWELL);
    }

    function setPlaying(on) {
      playing = on;
      toggleLabel.textContent = on ? say.labelPause : say.labelPlay;
      toggle.setAttribute("aria-label", on ? say.ariaPause : say.ariaPlay);
      schedule();
    }

    $("[data-slide-prev]", slider).addEventListener("click", () => go(index - 1));
    $("[data-slide-next]", slider).addEventListener("click", () => go(index + 1));
    for (const dot of dots) {
      dot.addEventListener("click", () => go(Number(dot.dataset.slideTo)));
    }
    toggle.addEventListener("click", () => setPlaying(!playing));

    slider.addEventListener("keydown", (event) => {
      if (event.key === "ArrowLeft") { event.preventDefault(); go(index - 1); }
      if (event.key === "ArrowRight") { event.preventDefault(); go(index + 1); }
    });

    // Hovering, reading, or looking at another tab all suspend the rotation.
    for (const [event, on] of [["pointerenter", false], ["pointerleave", true],
                               ["focusin", false], ["focusout", true]]) {
      slider.addEventListener(event, () => {
        clearTimeout(timer);
        if (on) schedule();
      });
    }
    document.addEventListener("visibilitychange", () => {
      clearTimeout(timer);
      if (!document.hidden) schedule();
    });

    let swipeFrom = null;
    track.addEventListener("pointerdown", (e) => { swipeFrom = e.clientX; });
    track.addEventListener("pointerup", (e) => {
      if (swipeFrom === null) return;
      const delta = e.clientX - swipeFrom;
      swipeFrom = null;
      if (Math.abs(delta) > 50) go(index + (delta < 0 ? 1 : -1));
    });

    /* A slide parked off to the right is outside the viewport, so a lazy one
       only starts downloading on the click that reveals it — and the first
       transition lands on an empty frame. Warm them once the page is in. */
    function warm() {
      for (const img of $$("[data-slide] img", slider)) img.loading = "eager";
    }
    if (document.readyState === "complete") warm();
    else addEventListener("load", warm, { once: true });

    slider.classList.add("is-jumping");
    show(0);
    requestAnimationFrame(() => slider.classList.remove("is-jumping"));
    setPlaying(playing);
  }

  /* -------------------------------------------------------------- gallery */
  const gallery = $("#gallery");
  if (!gallery) return;

  const cards = $$(".card", gallery);
  const controls = $(".controls");
  const countEl = $("[data-count]");
  const emptyEl = $("[data-empty]");
  const state = { medium: "all", status: "all", year: "all", sort: "recent" };
  let visible = cards.slice();

  const gap = () => parseFloat(getComputedStyle(gallery).getPropertyValue("--gap")) ||
    parseFloat(getComputedStyle(document.body).getPropertyValue("--gap")) || 24;

  /* Never more than three across: a canvas needs room to be looked at. */
  const columnsFor = (width) => width < 560 ? 1 : width < 980 ? 2 : 3;

  function layout() {
    const width = gallery.clientWidth;
    if (!width) return;
    const space = gap();
    const cols = columnsFor(width);
    const colWidth = (width - space * (cols - 1)) / cols;

    for (const card of visible) card.style.width = `${colWidth}px`;
    const heights = visible.map((card) => card.offsetHeight); // one forced reflow
    const cursorY = new Array(cols).fill(0);

    visible.forEach((card, i) => {
      let col = 0;
      for (let c = 1; c < cols; c++) if (cursorY[c] < cursorY[col] - 0.5) col = c;
      card.style.transform =
        `translate3d(${Math.round(col * (colWidth + space))}px, ${Math.round(cursorY[col])}px, 0)`;
      cursorY[col] += heights[i] + space + 16;
    });

    gallery.style.height = `${Math.max(0, Math.max(...cursorY) - space - 16)}px`;
    rewatch();
  }

  const matches = (card) =>
    (state.medium === "all" || card.dataset.medium === state.medium) &&
    (state.year === "all" || card.dataset.year === state.year) &&
    (state.status === "all" || card.dataset.status === state.status);

  const comparators = {
    recent: (a, b) => a.dataset.order - b.dataset.order,
    oldest: (a, b) => b.dataset.order - a.dataset.order,
    title: (a, b) => a.dataset.title.localeCompare(b.dataset.title, "en"),
  };

  function apply({ animate = true } = {}) {
    const next = cards.filter(matches).sort(comparators[state.sort]);
    const keep = new Set(next);

    for (const card of cards) {
      const shown = keep.has(card);
      card.toggleAttribute("data-out", !shown);
      card.inert = !shown;
      card.setAttribute("aria-hidden", String(!shown));
    }

    // Visual order becomes DOM order, so tabbing follows what the eye reads.
    const frag = document.createDocumentFragment();
    for (const card of next) frag.appendChild(card);
    gallery.appendChild(frag);

    visible = next;
    if (!animate) gallery.classList.add("is-resizing");
    layout();
    if (!animate) requestAnimationFrame(() => gallery.classList.remove("is-resizing"));

    const template = next.length === 1
      ? controls.dataset.countOne
      : controls.dataset.countTemplate;
    countEl.textContent = template.replace("{n}", next.length);
    emptyEl.hidden = next.length > 0;
    if (!calm.matches) for (const card of next) watch($(".reveal", card) ?? card);
  }

  function syncUrl() {
    const params = new URLSearchParams();
    for (const [key, value] of Object.entries(state)) {
      if (value !== "all" && !(key === "sort" && value === "recent")) params.set(key, value);
    }
    const query = params.toString();
    history.replaceState(null, "", query ? `?${query}` : location.pathname);
  }

  function readUrl() {
    const params = new URLSearchParams(location.search);
    for (const key of Object.keys(state)) {
      const value = params.get(key);
      if (value) state[key] = value;
    }
    for (const chip of $$(".chip[data-filter]")) {
      chip.setAttribute("aria-pressed", String(state[chip.dataset.filter] === chip.dataset.value));
    }
    $("#year-select").value = state.year;
    $("#sort-select").value = state.sort;
  }

  for (const chip of $$(".chip[data-filter]")) {
    chip.addEventListener("click", () => {
      const { filter, value } = chip.dataset;
      if (filter === "status") {
        state.status = state.status === value ? "all" : value;
        chip.setAttribute("aria-pressed", String(state.status === value));
      } else {
        state[filter] = value;
        for (const sibling of $$(`.chip[data-filter="${filter}"]`)) {
          sibling.setAttribute("aria-pressed", String(sibling.dataset.value === value));
        }
      }
      apply();
      syncUrl();
    });
  }

  $("[data-reset]")?.addEventListener("click", () => {
    Object.assign(state, { medium: "all", status: "all", year: "all" });
    for (const chip of $$(".chip[data-filter]")) {
      chip.setAttribute("aria-pressed", String(chip.dataset.value === "all"));
    }
    $("#year-select").value = "all";
    apply();
    syncUrl();
  });

  for (const select of $$(".controls select")) {
    select.addEventListener("change", () => {
      state[select.dataset.sort !== undefined ? "sort" : select.dataset.filter] = select.value;
      apply();
      syncUrl();
    });
  }

  gallery.classList.add("is-live");
  readUrl();
  apply({ animate: false });

  let frame = 0;
  new ResizeObserver(() => {
    cancelAnimationFrame(frame);
    gallery.classList.add("is-resizing");
    frame = requestAnimationFrame(() => {
      layout();
      requestAnimationFrame(() => gallery.classList.remove("is-resizing"));
    });
  }).observe(gallery);

  document.fonts?.ready.then(layout);
  addEventListener("load", layout);
})();
