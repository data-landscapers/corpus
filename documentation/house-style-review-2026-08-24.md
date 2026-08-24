# House style review — audit, proposal, and per-page changes (2026-08-24)

Requested by Bill: the six representative pages are applying different variations on the supposedly common house style. Goal: coordinate headings, text, internal navigation, internal boundaries and whitespace, largely on the main site's model; minimise whitespace without becoming cramped, so a reader landing on a page sees as much content as possible before scrolling. Companion file: `house-style.md` — the standing guidelines for new pages. This file is the one-time analysis and change list.

Pages examined: `/writing/` and the sovereignty-dividing-line article (main site); `/bulletin/`, `/catalogue/`, `/countries/AGO/` and `/reports/AGO/AGO-status.html` (Corpus). Source examined in both repos, including git history and the served CSS.

## 1 · The subtitle font (the NB)

Nothing server-side has changed recently. The served `main.css` on data-landscapers.io is byte-identical to the repo; `.article-header__subtitle` has not been touched by any commit since `d50a9d0` *Design update 1* on 1 May 2026; `--serif` changed site-wide from `'Source Serif 4', Georgia` to `'Lato', Calibri, Arial` in `8d13eb4` on **11 May** (subject "Update main.css", not one of the three Design Updates, which are all 1 May); and `main.css` has not been touched at all since `82a6bc8` on 20 May. That is the only font change the subtitle has ever had, and all three dates precede the article's publication (16 June). Two candidate explanations for a recent visible shift, neither in our code: a browser cache finally refreshing past the pre-May stylesheet, or Google Fonts failing to serve Lato's 300-italic face on some loads, in which case the browser synthesises an oblique from the regular — which looks like a different font. The fix in §3 pins the subtitle to Lato 400 italic (the 300-italic face is the flakiest in the set and the weight difference at 1.05rem is negligible), which removes the failure mode either way.

## 2 · What the audit found

**The shared base is healthy.** Corpus's `main.css` is upstream's plus a 23-line Corpus-only block (`.corpus-nav`, `.stat-bar`, `.section-heading`) — inserted at line 155, between the mobile-nav media query and `.btn`, not appended at the foot, so `diff` shows exactly one hunk; the datatable copies match upstream exactly and the lint confirms it. But that block means `main.css` can never be byte-compared — which is why `lint-shared-assets.py` checks only the datatable — so the one asset the lint was invented for is the one it cannot see. §3 fixes this structurally.

**Four different navigation chromes are live.** The main site has one row (Writing…Search — with no link to Corpus at all). Corpus pages built through `chrome_lib.py` (home, country, catalogue, finance, method) have two rows: the main-site row plus the right-aligned mono `corpus-nav`. Corpus pages built through `render.py` (bulletin, status/monthly/progress reports) have a third variant: a single row of corpus items styled as the main nav, whose logo links to the corpus home instead of the main site, whose item set disagrees with `chrome_lib` ("Data" instead of "Finance", `/countries/` instead of `/#countries`) — and whose "Data", "Regions" **and "Countries"** links all point at pages that do not exist (`site/data/` and `site/regions/` are absent; `site/countries/` holds the per-country directories but no `index.html`, so it 404s too). Three dead links, live now on every bulletin and report. And `topic-page.py` carries a fourth: its own hard-coded `CHROME` string with yet another item set (Home/Bulletin/Countries/Topics/Catalogue/Finance — no Regions, no Method, no main-site row) and its own footer text. `chrome_lib.py`'s header note predicted exactly this: a copy nothing compares against does not announce that it has fallen behind.

**The catalogue is a separate identity.** Its page carries a ~100-line inline `<style>` defining its own palette (`--accent:#7a1f2b` against the house `#c84b2f`, its own ink/paper/line hexes), a px type scale, an 8px border radius against the site's 2–3px, and an 1180px column against the site's 980px. It is exactly the "separate identity" that report.css's own header note says the design record forbids.

**Two section-boundary idioms with near-identical names.** The main site's `.section-header` is a tiny mono uppercase label over a 1px rule; Corpus's `.section-heading` is 1.45rem display bold over a 2px ink top rule. Both are fine devices; nothing says which does what, and the catalogue uses neither.

**Heading sizes disagree.** h1 is 2.4rem on the main site, 3rem on country pages, 26px (≈1.44rem) in the catalogue's own scale, `clamp(1.8–2.6rem)` on articles and reports.

**Whitespace — the substance of the complaint.** The above-the-fold cost of an article page today: sticky header 88px (an 80px logo), then `.article-header` at 3rem top padding + 2rem bottom + 2.5rem margin — roughly 430px of chrome and header before the first line of body text, on a body set 18px/1.75 with 1.25rem paragraph gaps and 2.5rem above every h2. On a 1366×768 laptop a reader sees the title block and about two paragraphs. Corpus pages stack a second sticky row (~40px) on top, so ~128px of every scroll position is chrome. The writing index spends 1.75rem of padding per entry: about three entries visible. The country page opens with a 3rem h1 and a stat-bar carrying 2.5rem of bottom margin before "Reports".

## 3 · Proposal — one style, set for density

Direction, per the brief: the main site's identity (palette, faces, rules-not-boxes) is the house style; the changes below tighten its vertical rhythm and make every Corpus page an application of it. All values are the coordinated targets; the per-file routing is §4.

**Chrome.** Header height 88px → 60px, logo 80px → 44px. On the main site the header stays sticky (60px is a tolerable tax). On Corpus pages the header scrolls away and only the corpus-nav sticks, at `top:0` (~36px) — long reports keep a persistent nav, and the persistent cost drops from ~128px to ~36px. `corpus-nav` padding 0.65rem → 0.45rem.

**Page-title block.** `.article-header` padding `3rem 0 2rem` → `1.25rem 0 1rem`, margin-bottom 2.5rem → 1.25rem. h1 unified at `clamp(1.6rem, 3vw, 2rem)` everywhere a page has one title — articles, reports, bulletin, catalogue, and the country page's 3rem comes down to it. Kicker and byline unchanged. Subtitle pinned: `font: italic 400 1.05rem var(--serif); color: var(--ink-light);` (see §1).

**Text.** Body line-height 1.75 → 1.6; paragraph margin 1.25rem → 0.9rem. h2 margins `2.5rem 0 0.75rem` → `1.75rem 0 0.5rem`; h3 `2rem` top → `1.4rem`. Root stays 18px — density comes from rhythm, not from shrinking the type. These two lines are the single biggest win on every prose page.

**Headings, one scale.** h1 as above, display 700, one per page. h2 1.45rem display 700 (the article-body value becomes the value). h3 1.05rem Lato 600 — a new value, between today's global 1.2rem and the article-body 1.1rem, chosen so h3 sits clearly under h2 at the tighter rhythm. Labels (colophon, sidebar, table headers) mono 0.7rem uppercase letter-spaced. Nothing else.

**Boundaries, three devices with defined jobs.** (1) A 1px `--rule` separates items in a list and closes a header. (2) A 2px `--ink` top rule + display h2 (`.section-heading`) opens a major page section — Reports/Sources/Finance on a country page, Countries/Regions/Topics on the home page; the main site's `.section-header` mono label is retired into it. (3) A 3px `--accent` left border marks quoted or apparatus matter (blockquote, standfirst, callout). Radius as the house already sets it — 2px on controls (buttons, inputs, badges), 3px on containers (table wraps, cards, code blocks); the catalogue's 8px goes. `--paper-warm` fill for apparatus, never for content. No other boundary devices.

**Internal navigation, one idiom.** In-page jump navs — the bulletin's category bar, a report's section list, an article's table of contents — take the bulletin's existing treatment, promoted to the pattern: mono 0.72rem uppercase letter-spaced links in the terracotta accent (`--accent`, hover `--accent-dk` — Bill, 2026-08-21 and reconfirmed 2026-08-24), separated by middots, closed below by a single 1px rule. The sovereignty article's hand-written dash-separated TOC converts to it. The corpus-nav item set is `chrome_lib`'s and lists only pages that exist.

**Density budget, measurable.** At 1366×768, the first line of body content sits within 260px of the viewport top; a landing reader sees ≥ 5 entries on an index page and ≥ 5 paragraphs of an article. Any new page type is checked against this before it ships.

**Whitespace floor.** Minimum tap/read separations stay: list-item padding never below 0.75rem, table cell padding never below 0.28rem/0.45rem (the print values), line-height never below 1.45 on prose. That is the "without becoming cramped" line.

Estimated effect on the article page: first paragraph starts ~240px from the top instead of ~430px; with the tighter rhythm roughly twice the words above the fold. Writing index: five to six entries visible instead of three.

## 4 · Per-page / per-file changes

Shared assets change upstream first (global rule): edit in `data-landscapers`, copy down, update the marker.

**data-landscapers (upstream):**

1. `assets/css/main.css` — the §3 values: header 60px/logo 44px (and the mobile menu's `top: 88px` follows it), body 1.6/0.9rem, h2/h3 margins, `.article-header` trim, h1 clamp, subtitle pinned to 400 italic, `.article-list__item` padding 1.75rem → 1rem, `.site-footer` padding 2.5rem → 1.5rem, `.section-header` retired in favour of `.section-heading` (which moves up from the Corpus block into main.css proper, so both sites own it).
2. `_layouts/default.html` — add **Corpus** to the site nav (the corpus pages already link back; the main site never links forward).
3. `_posts/2026-06-16-sovereignty-dividing-line.md` (and the article/lab layouts for future posts) — TOC line onto the mono-middot idiom, e.g. a `.article-toc` class styled in main.css.
4. Affects `/writing/` and every article/Lab page in one move; no per-page edits beyond the TOC markup.

**Corpus:**

5. Copy `main.css` down; update `MAIN-CSS-FROM`. Move the appended Corpus-only block into a new `site/assets/css/corpus.css` loaded after main.css on every corpus page, so the vendored file is byte-identical again — then extend `lint-shared-assets.py` with a `("site/assets/css/MAIN-CSS-FROM", "site/assets/css/main.css", "assets/css/main.css")` row, which the appended block currently makes impossible.
6. `scripts/render.py` (bulletin + status/monthly/progress reports) and `scripts/topic-page.py` — drop their private chromes and take `chrome_lib.chrome()/foot()`. This alone removes two of the four nav variants, restores the main-site row to the bulletin, reports and topic pages, repoints the logo, and kills the `/data/` and `/regions/` 404s.
7. `scripts/chrome_lib.py` — corpus-nav becomes the sticky row at `top:0` (header un-sticks on corpus pages); item set audited against pages that exist.
8. `scripts/catalogue.py` — rebuild the page on main.css: delete the `.cat` palette and inline `<style>` block's identity rules, keep only genuine layout (the cathead grid, the downloads box) restated in house tokens; column 980px; radius 3px; h1 on the house scale. The biggest single job in the list.
9. `scripts/country.py` / `country.css` — h1 3rem → house h1; `.stat-bar` margin 2.5rem → 1.5rem; `.report-row` padding 1.1rem → 0.8rem; `.section-heading` margin 3rem → 1.75rem (in the shared rule).
10. `report.css` — `.report-standfirst` padding 1rem → 0.75rem and margin 1.75rem → 1.25rem; `.report-key` margin 2.25rem → 1.5rem; `.report-colophon` margin-top 3rem → 1.75rem (2rem would breach the rhythm ceiling in `house-style.md`); print block untouched (page geometry is a different economy).
11. Editions rule respected: nothing already published under a dated URL is rebuilt; the style arrives with each page's next build, and old PDFs stay as they were (RENDER.md §9).

Nothing here changes content, URLs (beyond removing dead links), or the PDF pipeline's geometry.
