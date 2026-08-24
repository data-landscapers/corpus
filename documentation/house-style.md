# House style — guidelines for new pages

One style, two sites. data-landscapers.io is the origin; every Corpus page is an application of it, never a variation on it. These rules govern any new page or page type in either repo. The one-time analysis behind them is `house-style-review-2026-08-24.md`.

**Status, 2026-08-24: this describes the target, not the tree.** None of the review's §4 changes has been made. `corpus.css` does not exist yet, `main.css` still carries the Corpus block inline, the lint still checks only the datatable, the type and rhythm values below are the proposed ones rather than the shipped ones, and the main-site nav does not yet link to Corpus. Build a new page to these rules; do not read them as a description of what a page currently does. This paragraph comes out when §4 lands.

## Where style lives

All identity — palette, faces, type scale, chrome, boundaries — comes from `main.css`, canonical in `data-landscapers/assets/css/`, vendored byte-identical into Corpus with `MAIN-CSS-FROM` naming the commit. Corpus-wide additions live in `corpus.css`; a page type may add one stylesheet of its own (`report.css`, `country.css`, `home.css`) for **its own components** — grids, column widths, table geometry, and the sizes those components need. What it may not do is restate identity: every colour comes from a `:root` token, no new face, no new radius, no override of the type scale below for ordinary headings or body text. (The literal reading — no sizes at all — is not the rule, and never was: `report.css` alone sets 26 font sizes for report apparatus, all of them legitimate. The two hex colours outside the tokens are `.country-box:hover #2a6b3a` and the print-only greys in the `@media print` block, which sit outside the screen palette by design.) A change to anything shared is made upstream first, copied down, marker updated. `lint-shared-assets.py` reports drift.

Never: an inline `<style>` block defining identity; a new colour outside the `:root` tokens; a px type scale; a border radius off the house pair — 2px on controls, 3px on containers; a new font face. The catalogue page did four of these five (every one but the font face) and became a different site. That is the failure these rules exist to prevent.

## Type

Root 18px. Body: Lato 400, line-height 1.6, paragraph margin 0.9rem. The scale, complete:

| Role | Face | Size |
|---|---|---|
| h1 — page title, one per page | Trebuchet (display) 700 | clamp(1.6rem, 3vw, 2rem) |
| h2 — section | display 700 | 1.45rem, margins 1.75rem / 0.5rem |
| h3 — subsection | Lato 600 | 1.05rem, margin-top 1.4rem |
| Subtitle / standfirst | Lato 400 italic | 1.05rem, `--ink-light` |
| Kicker, labels, table headers | JetBrains Mono 500 uppercase | 0.67–0.72rem, letter-spaced |
| Byline | JetBrains Mono 400 | 0.8rem, `--ink-faint` |

The subtitle is pinned explicitly — never left to inheritance, never weight 300 (the 300-italic web face fails intermittently and browsers synthesise a fake oblique).

## Chrome and navigation

Header 60px, logo 44px. Main site: header sticky, one nav row. Corpus: header scrolls away; the mono `corpus-nav` row is the only sticky element (`top:0`, ~36px). Corpus chrome comes from `chrome_lib.py` only — no page builds its own header, and the nav lists only pages that exist. The main-site nav includes Corpus; every corpus page carries the main-site row above its own.

In-page jump navigation (category bars, report section lists, article TOCs) is one idiom — the bulletin's terracotta small caps: mono 0.72rem uppercase letter-spaced links in `--accent` (hover `--accent-dk`), separated by middots, closed below by a single 1px rule. Not dashes, not grey, not a second style of bar. The distinction from site chrome holds: the corpus-nav is the same voice but grey (`--ink-light`), taking the accent only on hover/active — terracotta all the time marks the page's own contents, grey marks the site's.

## Boundaries

Three devices, and no others. A 1px `--rule` separates items and closes headers. A 2px `--ink` top rule with a display h2 (`.section-heading`) opens a major page section. A 3px `--accent` left border marks quoted or apparatus matter (blockquote, standfirst, callout). Fills: `--paper-warm` for apparatus only, never behind content. Radius 2px on controls (buttons, inputs, badges), 3px on containers (table wraps, cards, code blocks) — the house sets both, and neither is a licence for a third.

## Whitespace

Dense but not cramped. Two hard rules and no enumerated scale: **no vertical margin or padding inside a page exceeds 1.75rem**, and adjacent blocks get one gap, not two stacked margins. Prefer 0.25rem steps where a component allows it; the coordinated values are not all on that grid (paragraph margin 0.9rem, `.stat-bar` and `.report-key` 1.5rem, `.report-row` 0.8rem, `corpus-nav` padding 0.45rem) and a false scale that the site's own targets break is worse than none. Floors that keep it readable: prose line-height ≥ 1.45, list-item padding ≥ 0.75rem, table cell padding ≥ 0.28rem 0.45rem.

**The fold budget, checked before a new page type ships:** at 1366×768, the first line of body content sits within 260px of the viewport top; a landing reader sees at least five entries of an index or five paragraphs of an article. If a header block breaks the budget, the header block shrinks — the budget doesn't.

## Print

The screen page and the PDF are one document; `report.css`'s `@page` / `@media print` blocks own print geometry and are not touched by screen-density changes. Fonts on a report page are the vendored woff2 files — `report.css`'s `@font-face` block is global rather than print-scoped, so screen and PDF draw on the same files and two builds of one edition stay byte-comparable. Trebuchet cannot be embedded; headings fall to Lato 700 in print, and that is the only deliberate divergence.

## Checklist for a new page

1. Loads `main.css` first, `corpus.css` on Corpus, then at most one page-type stylesheet, for that page type's own components only.
2. Chrome from `chrome_lib` (Corpus) or the Jekyll layouts (main site); nothing hand-rolled.
3. Every heading, label and boundary maps to a row of the tables above.
4. Jump nav, if any, in the mono-middot idiom.
5. Fold budget met at 1366×768.
6. No new colours, faces, radii, or inline identity styles.
7. If it touched a shared asset: changed upstream, copied down, marker updated, lint run.
