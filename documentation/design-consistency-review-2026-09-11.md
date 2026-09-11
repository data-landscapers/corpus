---
type: review
title: Design consistency review — data-landscapers.io and corpus.data-landscapers.io
date: 2026-09-11
author: Cowork (Claude), for Bill; tasks for Claude Code in design-consistency-tasks-2026-09-11.md
status: draft for review
---

# Design consistency review — both sites

## What was reviewed and how

Both live sites were read on 11 September 2026 in Chrome at 1366–1600px wide: on data-landscapers.io the home page, `/writing/`, `/portfolio/`, `/about/`, one essay and one working paper with a data table; on Corpus the home page and `/progress/`, `/bulletin/`, `/countries/`, `/countries/KEN/`, `/countries/KEN/finance.html`, `/topics/`, `/finance/`, `/catalogue/`, `/methodology/`, and the Kenya status and monthly reports. A script (`documentation/design-review-audit.js`, kept so the checks can be re-run) read the computed styles on each page — font faces and sizes in use, colours in use, radii, the position of the `h1` and of the first line of body text, external links without `target="_blank"`, and any element wider than the viewport. The built Corpus tree in `site/` was also rendered locally at 1366×768 and 390×844 to check the phone layout, and the stylesheets, `_layouts/`, the index pages and `chrome_lib.py` were read directly.

The standard measured against is the one the two repos already state: `documentation/house-style.md` (one style, two sites; identity only from `main.css` tokens; one h1 per page; the fold budget; the three boundary devices; the mono-middot jump nav; external links in a new tab), and `design.md` §1 ("look and feel matches data-landscapers.com — same family, not a separate identity").

## The short version

The identity itself is in good shape. Both sites load the same byte-identical `main.css`, the palette is held to the tokens almost everywhere, the three faces are the three faces, the two radii are the two radii, and the header, wordmark, tagline and nav row are literally the same on every page of both sites. The 24 August rewrite did its job: nothing on either site any longer reads as a different site.

What has drifted is one level up from identity — the *patterns* built from it. Three of these are worth fixing first because a reader meets them on every visit:

First, **Corpus has no mobile navigation.** `chrome_lib.py` writes the header without the `.nav-toggle` button that `_layouts/default.html` has, and `main.css` hides `.site-nav` below 900px on the assumption the button is there. On a phone every Corpus page loses the main-site row entirely (no way back to the website except the logo), while the `.corpus-nav` wraps to four ragged right-aligned lines, sticks, and together with the header takes 198px of a 390px-wide screen at every scroll position.

Second, **there is no single "top of page" pattern.** The main site's four index pages have no `h1` at all (`/writing/` opens on a bare `<select>`); Corpus uses four different wrappers for its `h1` (`.article-header`, `.country-head`, `.cathead`, and a bare `h1`), each with its own top offset (109, 127, 139 or 157px from the viewport top), its own meta line, and its own idea of where the feedback ask, the PDF button, the standfirst and the jump nav go. The reader experiences this as every page starting differently.

Third, **the main site is built from inline styles rather than the classes `main.css` defines.** `/portfolio/` carries 282 `style=""` attributes and a `<style>` block; `/writing/` 94; the home page 48; the article layout's *Working analysis* notice is three off-token colours inline. The list that the home page, `/writing/` and `/portfolio/` all draw is written three times with three sets of values (summary at 0.9rem / 0.9rem / 0.85rem; the title in Trebuchet by class, by class, and by a literal font stack). `house-style.md` forbids exactly this ("Never: an inline `<style>` block defining identity; a new colour outside the `:root` tokens; a border radius off the house pair") and the catalogue was rewritten for it; the main site's own index pages were never brought in line.

Everything else is smaller and listed below. Nothing found is a new colour system or a new face; it is duplication and small divergence, which is the cheap kind of drift to remove.

## Findings

Each finding carries a code that the task list uses. Severity is about how many readers meet it and how visibly, not how hard it is to fix.

### A. Across the two sites

**A1 — Corpus header has no hamburger (high).** `chrome_lib.header()` emits `.site-header` → `.site-logo` + `.site-nav`, and nothing else; `default.html` on the main site emits the same plus `<button class="nav-toggle">`. `main.css` at `max-width: 900px` sets `.site-nav { display: none }` and `.nav-toggle { display: flex }`. On Corpus the first fires and the second has nothing to fire on. Measured at 390px: main nav absent on all eight Corpus pages checked; `.corpus-nav` 127px tall (four rows) and sticky under a 71px header. The main site at the same width shows the hamburger and a 71px header.

**A2 — No shared page-head pattern; the main site's index pages have no `h1` (high).** Counted `h1` elements: home 0, `/writing/` 0, `/portfolio/` 0, `/about/` 0 on the main site; Corpus home 0, `/countries/` 0 ("Countries" is an `h2.section-heading`). Where an `h1` exists it sits in one of four wrappers, at four heights. The house-style type table says "h1 — page title, one per page". The consequence for the fold budget is in A6.

**A3 — External links open in the same tab on the main site, a new tab on Corpus (medium).** The rule in `house-style.md` → Links is stated for "every page" of both hosts, and Corpus applies it with `chrome_lib.external_links()`. The Jekyll site has no equivalent: on one essay 24 of 27 outbound links lack `target="_blank"`, on `/portfolio/` 14 of 17. A reader following a citation from an essay loses the essay; from a Corpus report they do not.

**A4 — Two footers (medium).** Main site: "CC BY 4.0 2026 Bill Anderson / Data Landscapers Ltd · Registered in the UK · Co. No. 16040544" plus LinkedIn and GitHub links. Corpus: "CC BY 4.0 2026 Data Landscapers Ltd · Registered in the UK · Co. No. 16040544", no name, no links. One of these is the footer; the other is a copy that stopped being updated.

**A5 — Three sizes of the same button (medium).** `.btn` is 0.82rem in `main.css` (renders 14.76px: the subscribe button, the country page's *Read* and *↓ PDF*). The article layout and the report header set `font-size: 0.8rem` inline on the PDF button (14.4px). The shared data table and the catalogue set 0.7rem on *↓ CSV* / *↓ Metadata* / *↓ JSON* (12.6px). Same device, three sizes, none of them a class.

**A6 — Fold budget (260px to the first body line at 1366×768) is met on the essay and missed on the pages with the most apparatus (medium).** Measured first-body-line offsets: essay 259 (as documented); working paper with the *Working analysis* notice 485; Corpus home 227; `/countries/` 218; `/topics/` 161; `/finance/` 195; `/countries/KEN/finance.html` 246; `/progress/` 262; `/methodology/` 311; Kenya status report 463; Kenya monthly update 532 (kicker, two-line title, byline row with PDF button, standfirst box, two-row jump nav, `h2`, `h3`); `/bulletin/` 488. (The Corpus figures for the built tree were taken at 1366px; the live-page figures at 1600px, where the `h1` clamp is at its 2rem ceiling either way, so the two sets are comparable to within a line.) The report header is where the budget goes: it stacks six rows before a word of the report. Corpus already pays 107px of sticky chrome, so the report header has less room than the essay header, not more.

**A7 — The shared data table carries its own badge palette and its own geometry (medium; upstream).** `assets/shared/datatable.css` (canonical in data-landscapers, copied to Corpus) defines `.dt-badge--green/blue/amber/red` with Bootstrap's alert colours (`#155724/#d4edda`, `#004085/#cce5ff`, `#856404/#fff3cd`, `#721c24/#f8d7da`) while `main.css` already defines `.badge--green/blue/amber/red` with the house tints (`#2a6b3a/#edf7ef` etc.). The scrollbar thumb has a 7px radius, off the house pair. The table header is closed by a 2px accent rule where the house rule for a table header is 1px `--rule`. And the whole widget breaks out of the 980px column to ~1500px on both sites. If the breakout is intended (it may well be: the finance tables are wide) it should be a stated width, not a side effect.

**A8 — Category chip on the main site borrows the Lab's *active* status chip (low).** Home, `/writing/` and `/portfolio/` show each entry's category in `.wip-item-card__status--active` — the green chip that meant "this Lab project is active". It reads as a status, and green means the same thing as the badge set's green (a positive state) everywhere else. A category is a label, not a state: `.badge--grey` or a dedicated `.article-list__cat` in mono grey is the honest chip.

**A9 — Contact details point at two domains (low; not design, noted in passing).** `/about/` writes `bill-anderson@data-landscapers.com` and `_config.yml` carries the same; Corpus's feedback link uses `info@data-landscapers.io`. The memory of the domain move says `.com` is stale.

### B. Within data-landscapers.io

**B1 — Index pages are built inline, three ways (high).** The article list exists as classes in `main.css` (`.article-list__item`, `__meta`, `__title`, `__excerpt`, `__tags`) and the comment in `main.css` says the inline overrides "are gone and the value lives here, once". They are not gone: `index.md`, `writing/index.md` and `portfolio/index.md` each rebuild the list with inline `style` on the meta row, the title, the subtitle and the summary. Portfolio differs from writing in summary size (0.85 vs 0.9rem), line-height (1.45 vs inherited 1.6), colour (`--ink-light` vs `--ink-faint`), date format ("September 2024" vs "16 June 2026"), and title markup (a literal `'Trebuchet MS', 'Gill Sans', Calibri` stack instead of `.article-list__title`). Portfolio summaries also contain links, so blue appears in a list where writing shows none.

**B2 — The category `<select>` is an unstyled control with off-token values (medium).** Both filters: `font-family: var(--mono); font-size: 0.8em; border: 1px solid #ccc; border-radius: 3px; background: #fff; color: #333`. `#ccc` and `#333` are not tokens; 3px is the container radius, not the control radius; `main.css` already styles a select (`.data-table-controls select`: Lato 0.8rem, `--rule` border, 2px). `/writing/` opens on this control with nothing above it.

**B3 — The *Working analysis* notice is inline identity in the layout (medium).** `_layouts/article.html` writes `.lab-notice` with `background:#fdf3e3; border-left:4px solid #c84b2f; color:#7a4010` inline — three literals, one of them a fourth border width (the house callout is 3px accent). The badge-amber tints in `main.css` (`#fdf6e0`, `#7a5000`) are the same idea already in the tokens' orbit. It also sits above the article header, which is what pushes the working paper's first line to 485px (A6).

**B4 — Home page overrides its own components inline (low).** `.sidebar-block__label` is `--ink-faint` in CSS and forced to `--accent` by inline style on all four blocks; the first `.section-heading` has `border-top: none` inline (the `:first-of-type` rule already removes the top *margin*, so the remaining rule is the only accent rule on the page — decide whether the home page's first section has one, and put the answer in CSS); the aside has `padding-top: 2.5rem` inline, which is above the 1.75rem ceiling.

**B5 — Article footer and about page carry their layout inline (low).** `article.html`'s footer (border, padding, flex) is inline; `/about/` uses `.cv-section__label` as a generic section label with inline margins and two inline-styled ruled boxes. All are candidates for the same small set of classes the page-head work (A2) will produce.

### C. Within corpus.data-landscapers.io

**C1 — Sibling index pages open five different ways (high; the Corpus half of A2).** `/progress/` and `/methodology/`: `.article-header` + `h1` + `.article-toc`. `/countries/`: `.stat-bar` + `h2.section-heading` (no `h1`). `/topics/`: bare `h1` + paragraph. `/finance/` and `/countries/KEN/`: `.country-head` + `h1` + mono meta line. `/catalogue/`: `.cathead` + `h1` beside a download box. `/bulletin/`: `.article-header` + `h1` + byline + PDF button + jump nav. The stat bar appears on two pages only. These are all reasonable in isolation; together they mean the top 150px of a Corpus page never looks the same twice.

**C2 — Breadcrumb on one page only (medium).** `.crumb` ("COUNTRIES & REGIONS / KENYA / NON-STATE FINANCE") exists on `finance.html` and nowhere else — not on the country page it sits under, not on the reports, which are the deepest pages. Either every page under `/countries/` gets one or none does.

**C3 — Four small-print styles for what the type table calls two (medium).** `.country-head__meta` mono 0.72rem `--ink-faint`; `.report-row__meta` Lato 0.75rem `--ink-faint`; `.article-header__byline` mono 0.8rem `--ink-faint`; `.article-header__meta` on reports at body size in `--ink`; the `/finance/` section headings carry a mono stat line of their own. The house table has a byline (mono 0.8rem) and a label (mono 0.67–0.72rem). Two roles, one class each.

**C4 — Tables and the colophon overflow on phones (medium).** At 390px: `table.pivot` on the country page runs to 458px, `table.progress-table` on `/progress/` to 680px, and the colophon's `dd.mono` / `<code>` cells on the home and topics pages to 438–445px, so those pages scroll sideways. The shared data table handles this (it has its own scroll frame); the site's own tables and the colophon do not. Each needs an `overflow-x: auto` wrapper, or the colophon's `dd` needs `overflow-wrap: anywhere`.

**C5 — `home.css` is loaded on every page and has become a second `corpus.css` (medium).** `/progress/`, `/countries/`, `/countries/KEN/`, `/topics/`, `/finance/` and `/methodology/` all load `home.css`; `finance.html` loads five sheets (`main`, `corpus`, `home`, `country`, `datatable`). `home.css` holds the box grids, the topic matrix, the colophon, the `.section-heading` margin override and the hero — most of it used off the home page. The house checklist says "at most one page-type stylesheet". Move what every page uses into `corpus.css` and leave `home.css` for the hero.

**C6 — Heading-to-body ratio changed on 10 September and only the body moved (low; a decision, not a defect).** Body prose is now 0.94rem of root (16.92px) while `h2` (1.45rem → 26.1px) and `h3` (1.05rem → 18.9px) are still sized from root. The house ratio of h3 to body was 1.05:1; on Corpus it is now 1.12:1, and h2 to body 1.54:1 against 1.45:1. The report header's Lato 700 `h3` sub-headings visibly outweigh their paragraphs. Either accept it (the headings are the reference apparatus and may deserve the extra step) or scale `h2`–`h4` by the same `--prose` factor on screen.

**C7 — The feedback ask sits at a different height on each page-head variant (low).** It is a float, as the CSS comment explains, and it works; but because the four wrappers give the `h1` different top offsets, the ask lands at 70, 80, 100 or 118px from the viewport top. It will settle itself once C1 is done.

## What is consistent and should stay so

Worth writing down so the task list does not undo it: the header row and wordmark (identical markup, 71px, on every page); the tagline in green; the terracotta mono-middot jump nav wherever it appears (essay TOC, methodology, bulletin categories, report sections) — this is the single most consistent device on the two sites; the `.section-heading` 1px accent rule (home, countries, KEN, finance); the link colour and the hover rule; the 2px/3px radius pair everywhere except the scrollbar thumb; the `.btn` outline style, which reads as one family even at three sizes; the paper background with `--paper-warm` reserved for apparatus (nav bar, stat bar, table heads, colophon, callout); the badge tints (main.css badges, catalogue tags, bulletin country chips all share one set); and the catalogue after its rewrite, which now sits inside the house.

## Recommended order

Fix A1 first; it is a one-line markup change with a visible effect on every phone visit to Corpus. Then A4 and A5 (footer, button sizes), which are small and shared. Then the page-head work (A2/C1/C2/C3/C7 together — one component, used by both sites, replacing four wrappers and the four index pages that have none), which is the largest item and the one that most changes how the sites feel. Then the main site's inline-style clean-up (B1–B5), which is mechanical once the classes exist. A3, A7, C4 and C5 are independent and can go in any gap. C6 is Bill's call before any CSS is written.

Two things are deliberately not on the task list. The 0.94rem Corpus body size is a recorded decision and is respected here. And whether the shared data table should break out to ~1500px is a design question for Bill rather than a task for CC; the task list only asks for the width to be stated once.
