---
type: tasks
title: Design consistency — tasks for Claude Code
date: 2026-09-11
source: documentation/design-consistency-review-2026-09-11.md (finding codes A1–C7 refer to it)
status: 1–12 done 2026-09-11 (CC, on Bill's instruction to set the freeze aside); 13 is Bill's
---

# Design consistency — tasks for CC

## Where this stands (CC, 2026-09-11)

**Tasks 1–12 are done; 13 is Bill's.** Bill set the freeze aside for this work. Every change was measured before and after, in Chrome at 390×844 and 1366×768, with `design-review-audit.js` run under Playwright. Main-site figures are from the live site after deploy. Upstream commits are `14b0b6a`, `fd78524` and `d1f46fe`; Corpus's shared copies are marked at `fd78524`.

- **1 (A1):** `chrome_lib.chrome()` now carries the website's hamburger markup. Below 900px the `corpus-nav` is one row that scrolls sideways. At 390px, header plus nav is 105px, down from 198px, and the hamburger opens the four main-site items. Nothing moved at 1366px.
- **11 (C4):** the pivot and both progress tables sit in `.table-scroll` (`corpus.css`), which scrolls at 720px and below only. At wider widths the progress table's sticky header keeps working. The colophon `dd` is `overflow-wrap: anywhere` in a `minmax(0, 1fr)` column. The review missed one page: the report colophon on `/bulletin/` ran to 512px because the edition picker is sized by its longest option. It has a screen-only fix in `report.css`, so no PDF reflows. `scrollWidth` now equals the viewport width on all 13 pages measured.
- **9 (A3):** a script at the foot of data-landscapers `_layouts/default.html` (commit `14b0b6a`). Run against the live `/portfolio/`, links opening in place fell from 14 of 17 to 0, and no internal link gained a target.

- **2 (A4):** the task ran the wrong way. On 2026-09-09 Bill took `Bill Anderson /` and the link row off Corpus's footer, so the stale one was the main site's. Bill chose Corpus's wording, and the main site's layout now carries it word for word. The CC BY link's inline style became `.site-footer__copy a` in `main.css`.
- **3 (A5):** buttons are `.btn` (0.82rem) and a new `.btn--sm` (0.7rem) for the data-table toolbar and the catalogue's download box. `datatable.js` puts `btn--sm` on the buttons it creates. The article and report PDF buttons lost their inline 0.8rem. The audit now reports only 14.76px and 12.6px.
- **4 (A2, C1–C3, C7):** **`.article-header` became the page head; there is no new `.page-head`.** It was already the head for the essay, every report, progress and methodology, and the print CSS and `test_editions.py` key on it, so a rename would have touched all of those for no gain. It gained `__crumb`, `__meta` (`__byline` left, `__actions` right) and a `--norule` modifier. `.country-head`, `.crumb` and the bare `h1` are retired; `.cathead` survives only as the catalogue's grid hook. Every page has one `h1` except the two home pages.
  - The head starts at the same point everywhere. The `h1` sits at 89px on the main site's index pages and at 127px on Corpus pages with nothing above the title. It drops one row, to 155–157px, where a crumb or a report's kicker comes first, and to 182px on Countries & Regions, which keeps its stat bar above the head. Before, the offsets were 109, 127, 131, 139 and 157px.
  - **Crumbs** go on pages below a nav index: place pages, their finance tables and topic pages. Documents keep their kicker instead of gaining a crumb row. The review's suggestion put crumbs on reports too, but that costs a line against a fold budget they already miss.
  - `.report-row__meta` and the `/finance/` stat line carry `.byline`, the one byline style. `region.py` was missing from the task's builder list and is covered.
- **5 (A6):** the byline and the PDF button were already on one row. The standfirst lost its tinted box. The Kenya monthly's first body line moved from 531px to 504px; the status report is unchanged at 462px, the bulletin is at 488px and methodology at 311px. **300px is not reachable** without taking the standfirst or the contents bar off the first screen, and both were placed there by decision. So `house-style.md` records the measured figure instead of a target the reports cannot meet.
- **6 (B1, B4, B5, A8):** inline `style` attributes are at 0 on `/`, `/writing/`, `/portfolio/` and `/about/` (they were 48, 94, 282 and 15). `/portfolio/` has no `<style>` block left. All three lists are built on the `.article-list` classes, and the category chip is `.badge--grey`. The sidebar label colour, the first section's missing rule and the aside padding (now 1.75rem) moved into CSS, as did the article footer (`.article-footer`) and the about page (`.about-row`). `/writing/`, `/portfolio/` and `/about/` each have an `h1`.
- **7 (B2):** `.filter-select` joins the `.data-table-controls select` rule; on `/writing/` it measures Lato, 14.4px, 2px radius, `--rule` border. The bulletin's filter, whose own comment calls it the same control, now matches it, and the edition picker takes the control radius of 2px.
- **8 (B3):** `.lab-notice` now uses the amber badge tints and the 3px callout border, and sits below the page head. The working paper's first line moved from 485px to 471px. It is still over 300px because of the kicker and a two-line title.
- **10 (A7):** the table's badges use the house tints, the scrollbar thumb has a 3px radius, and the head is closed by a 1px `--rule`. The breakout width is stated once as `--dt-max: 1800px`, unchanged; **Bill to confirm the figure.** The article layout's asset stamp went from `v=3` to `v=4`: a fixed stamp is a cache key, and the live table went on serving the old files until the stamp was bumped. On the live working paper the table draws 306 rows, sorts, and wears the new styles.
- **12 (C5):** `home.css` now holds the hero alone and loads only on the home page; everything else in it moved to `corpus.css`. Every other page loads `main.css`, `corpus.css`, at most one page-type sheet, and `datatable.css` where it has a table.

Each Corpus change reached the served pages through `render.py --repage` and the page builders; no edition, CSV or PDF was minted. `lint-external-links.py` and `lint-shared-assets.py` are clean.

At 390px the live main site shows the hamburger and nothing overflows on the six pages audited: home, writing, portfolio, about, an essay and a working paper.

**Found in passing:** `scripts/test_render_gate.py` fails one case, "a deleted PDF is re-cut under its own name". It fails the same way at `0fa288f`, before any of this work, and has not been investigated.

**Task 13 (C6):** Bill chose to scale the headings. `corpus.css`'s screen block now sets h2–h4 and `.section-heading` to 0.94 of the house sizes, the same step as the body prose. The `h1` and print are not scaled.

**Bill's follow-ups, the same day:** he confirmed the 1800px table width. The main site's category chip is the green badge. The Corpus home hero and the Portfolio intro are body size — the hero went from 1.05rem to the prose size, and Portfolio's intro is a plain paragraph below the page head rather than its italic subtitle.

Ground rules for every task here, from `documentation/house-style.md`: anything shared changes **upstream in data-landscapers first**, is copied down, and the marker (`MAIN-CSS-FROM` / `DATATABLE-FROM`) is updated; `scripts/lint-shared-assets.py` must pass afterwards. No new colours, faces or radii. Corpus presentation changes are applied with `render.py --repage`, not `--force`. Re-run `documentation/design-review-audit.js` (paste into the console on a page, or run it under Playwright) before and after to confirm the numbers below moved.

Tasks are in the order the review recommends. Each states where the change goes, what done looks like, and what must not change.

## 1. Give Corpus a mobile navigation (A1) — small, do first

Where: `scripts/chrome_lib.py` → `header()`; `corpus.css`.

Do: emit the same `<button class="nav-toggle" aria-label="Toggle navigation">` with its three `<span>`s and the same `onclick` toggle that `_layouts/default.html` uses, between `.site-logo` and `.site-nav`. Give `.site-nav` the `id="site-nav"` the toggle targets. In `corpus.css`, below 900px make `.corpus-nav__inner` a single horizontally scrollable row (`flex-wrap: nowrap; overflow-x: auto; justify-content: flex-start`) so the bar stays one line (~38px) instead of wrapping to four; keep it sticky.

Done when: at 390px every Corpus page shows the hamburger, opening it lists Corpus / Work in progress / Portfolio / About, and header + corpus-nav together measure ≤ 110px. Nothing changes at ≥ 900px.

## 2. One footer for both sites (A4) — small

Where: `_layouts/default.html` (canonical) and `chrome_lib.py` → footer.

Do: decide the wording once (the main site's, with "Bill Anderson / Data Landscapers Ltd" and the LinkedIn + GitHub links, is the fuller of the two) and make `chrome_lib` emit the identical markup and text. Move the inline `style="color:inherit;border-bottom:none"` on the CC BY link into `main.css` as `.site-footer__copy a`.

Done when: the footer's rendered text and links are byte-identical on `data-landscapers.io/` and `corpus.data-landscapers.io/countries/KEN/`.

## 3. Two button sizes, both classes (A5) — small

Where: `main.css` (upstream); then `_layouts/article.html`, `report-render.py` / `render.py` report header, `assets/shared/datatable.css`, `catalogue.css`.

Do: keep `.btn` at 0.82rem; add `.btn--sm` at 0.7rem (the size the data table and catalogue already use). Replace the inline `font-size: 0.8rem` on the article PDF button and the report PDF button with plain `.btn` (0.82rem) — one step, not three. Make the data table's and catalogue's download buttons `.btn .btn--sm` and delete their own size rules.

Done when: the audit's `btn` field reports only 14.76px and 12.6px across all pages.

## 4. A shared page-head component, used by both sites (A2, C1, C2, C3, C7) — the big one

Where: `main.css` (upstream, since both sites use it); `chrome_lib.py` (a `page_head()` helper) and the six Corpus page builders (`home.py`, `country.py`, `finance.py`, `topic-page.py`, `progress.py`, `methodology.py`, `catalogue.py`, `bulletin.py`, `report-render.py`); the main site's `index.md`, `writing/index.md`, `portfolio/index.md`, `about/index.md`, `_layouts/article.html`.

Do: define one `.page-head` in `main.css` with optional slots in a fixed order — `.page-head__crumb` (mono 0.68rem, `--ink-faint`), `.page-head__kicker` (the existing kicker style), `h1.page-head__title`, `.page-head__standfirst` (the existing pinned subtitle style), `.page-head__byline` (mono 0.8rem `--ink-faint`; absorbs `.country-head__meta`, `.article-header__byline`, the report `__meta`), `.page-head__actions` (right-hand slot for the PDF/CSV buttons and the feedback ask, so they stop floating into the title), and a single bottom `--rule`. Fixed top padding (the essay's current 1rem) and bottom margin (0.75rem) so the `h1` is at the same offset on every page. Then:

- Corpus: retire `.country-head`, `.cathead` and the bare-`h1` variant; `.article-header` keeps its name only if it becomes an alias. `/countries/` gets an `h1` ("Countries & Regions") and the stat bar stays. Breadcrumb: decide once — the suggestion is *every* page under `/countries/{ISO3}/` including the three reports, none elsewhere — and emit it from the helper so it cannot be on one page only.
- Main site: `/writing/`, `/portfolio/` and `/about/` get an `h1` via the same component (the portfolio's inline `<header>` becomes it); the home page keeps "Latest work in progress" as its first `.section-heading` and gets no `h1` unless Bill wants one.
- `.report-row__meta` (Lato 0.75rem) becomes the label style (mono 0.72rem) or the byline style — pick from the type table; do not keep a third.

Done when: the audit's `h1` field reports the same top offset (± 2px) on `/progress/`, `/topics/`, `/finance/`, `/countries/KEN/`, `/catalogue/`, `/reports/KEN/KEN-status.html` and the main site's essay; `h1n` is 1 on every page except the two home pages; `kk`/`by` report one kicker class and one byline class; the `crumb` appears on all or none of the country tree.

Must not change: the essay's first-line offset (259px at 1366×768) — the component's padding is the essay header's current padding, so this holds if nothing is added above it.

## 5. Bring the report header inside the fold budget (A6)

Where: `report-render.py` header emission; `report.css`.

Do: with task 4's `.page-head`, put the edition/compiled-by byline and the PDF button on one row (`__byline` left, `__actions` right), drop the standfirst box on the monthly update to a one-line `__standfirst` (the 3px accent left-border callout is fine, but not as a second boxed block above the TOC), and let the jump nav follow immediately. Then measure.

Done when: first body line on `/reports/KEN/KEN-status.html` and `KEN-monthly.html` at 1366×768 is ≤ 300px (260 is the house budget; the reports carry a jump nav the essay does not, so 300 is the realistic target — record whichever number is agreed in `house-style.md`). `/methodology/` (311 now) and `/bulletin/` (488 now, same header shape) should meet the same figure.

## 6. Main-site index pages: use the classes, delete the inline styles (B1, B4, B5, A8)

Where: `index.md`, `writing/index.md`, `portfolio/index.md`, `about/index.md`, `_layouts/article.html`; `main.css` for the two or three classes that are missing.

Do: rebuild the three article lists on `.article-list__item` / `__meta` / `__title` / `__excerpt` with no `style` attributes, adding `.article-list__subtitle` (italic, 0.9rem, `--ink-faint`) since the writing list has one. Portfolio adopts the writing list's values (summary 0.9rem, `--ink-faint`; date as "Month YYYY" is fine but set it in the same `__meta` row). Replace `.wip-item-card__status--active` as the category chip with `.badge .badge--grey` (or add `.article-list__cat` in mono grey) on all three lists — the green chip is a status, not a category. Move the sidebar label colour, the first-section `border-top: none`, and the aside padding into CSS (and bring the aside's 2.5rem down to the 1.75rem ceiling). Move `article.html`'s footer styles to `.article-footer`, and `/about/`'s inline ruled boxes to a small `.about-row` class.

Done when: `[style]` counts from the audit are 0 on `/writing/`, `/portfolio/`, `/about/` and ≤ 5 on the home page; `/portfolio/` has no `<style>` block; the three lists render the same summary size and colour.

## 7. Style the category filter as a house control (B2)

Where: `main.css` (a `.select` or `.filter select` rule, matching `.data-table-controls select`); `writing/index.md`, `portfolio/index.md`.

Do: Lato 0.8rem, `1px solid var(--rule)`, 2px radius, white background, `--ink` text; remove the inline `#ccc / #333 / 3px` attributes. Put the filter inside the new page head or immediately under it, never as the first thing on the page.

Done when: the audit's `sel` field on `/writing/` matches its field on `/countries/KEN/finance.html`.

## 8. Move the *Working analysis* notice into CSS on tokens (B3)

Where: `_layouts/article.html`; `main.css`.

Do: `.lab-notice { background: #fdf6e0; border-left: 3px solid var(--accent); color: #7a5000; … }` — the amber badge tints already in `main.css`, the house 3px callout border — and delete the inline block. Consider placing it *below* the page head rather than above it, which returns the working paper's first line from 485px to within budget.

Done when: no `#fdf3e3`, `#7a4010` or `4px solid` anywhere in the layouts; the working paper's first-line offset ≤ 300px.

## 9. External links open in a new tab on the main site too (A3)

Where: `_layouts/default.html`.

Do: GitHub Pages cannot run a custom Jekyll plugin, so add a ten-line script before `</body>` that sets `target="_blank" rel="noopener"` on every `a[href^="http"]` whose host is not `data-landscapers.io` or `corpus.data-landscapers.io` and that has no `target` already. Mirror `chrome_lib.INTERNAL_HOSTS` — same two hosts, no `noreferrer`, anchors with an explicit `target` left alone.

Done when: the audit's `extNB` is 0 on the essay and on `/portfolio/`, and the logo / nav / footer links (internal) still open in place.

## 10. Shared data table: house badges, house radius, stated width (A7)

Where: `assets/shared/datatable.css` in data-landscapers (upstream), then copied to Corpus with `DATATABLE-FROM` updated.

Do: replace the four Bootstrap badge colour sets with the `main.css` tints (`.dt-badge--green` = `.badge--green` values, and so on — or simply make the JS emit `.badge .badge--green` and delete the `.dt-badge` rules); change the scrollbar thumb's 7px radius to 3px; change the head's `2px solid var(--accent)` to `1px solid var(--rule)` unless Bill wants the accent kept as the table's one flourish; and put the breakout width in one token (`--col-table`, e.g. `1500px`) referenced by the widget, so the ~1500px is a decision rather than a side effect. Leave the width itself for Bill to confirm.

Done when: no hex literal in `datatable.css` other than those in `main.css`'s badge set; `lint-shared-assets.py` clean; the finance tables still scroll and sort.

## 11. Stop tables and the colophon overflowing on phones (C4)

Where: `country.css` (`table.pivot`), `progress.css` (`table.progress-table`), `home.css`/`corpus.css` (`.colophon`).

Do: wrap the two tables in a `<div class="table-scroll">` (`overflow-x: auto`) from the builders, or set it on a wrapper they already have; give `.colophon dd` `overflow-wrap: anywhere` and let `<code>` inside it wrap.

Done when: at 390px the audit's `sw` equals `vw` on `/`, `/topics/`, `/countries/KEN/` and `/progress/`.

## 12. `home.css` back to home-only; the rest into `corpus.css` (C5)

Where: `home.css`, `corpus.css`, `chrome_lib.styles()`.

Do: move `.boxes`, `.box`, `.topic-group`, `.tsub__inner`, `.sbox`, `.colophon`, `.section-intro`, `.caveat` and the `.section-heading` margin override into `corpus.css` (they are used on countries, topics, KEN, finance and methodology); leave `.hero` in `home.css` and load it on the home page only. Then check which pages still need `country.css` (finance.html and the country page do; `/finance/` probably does).

Done when: every Corpus page loads `main.css`, `corpus.css`, and at most one page-type sheet (plus `datatable.css` where there is a table); nothing visibly moves.

## 13. Decision needed from Bill before any CSS: heading scale on Corpus (C6)

Not a task yet. Since 10 September the Corpus body is 0.94rem but `h2`/`h3`/`h4` are still sized from root, so headings are a step larger relative to prose than on the main site (h3:body 1.12 vs 1.05). Options: (a) accept and write it into `house-style.md`; (b) in the same `@media screen` block in `corpus.css`, scale `h2`–`h4` by 0.94 too. CC should not choose.

## Verification pass (after all of the above)

Run `documentation/design-review-audit.js` on the twelve pages listed in the review at 1366×768 and 390×844, and check: `h1n` = 1 everywhere except the two homes; one `h1` offset; `extNB` = 0; `sw` = `vw` at 390; `[style]` counts as in task 6; `lint-shared-assets.py` clean; `render.py --repage` used, no new dated editions minted; `test_external_links.py` and the catalogue/bulletin tests green. Then write a short note for Cowork saying what was changed and what was pushed back, per the working arrangement.
