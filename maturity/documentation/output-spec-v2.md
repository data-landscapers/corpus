---
type: spec
reader: cc
title: output-spec-v2.md — the maturity map, the country report and the methodology anchors that present the Maturity Assessment
last_reviewed: 2026-10-09
status: Bill's answers of 2026-10-09 to the v1 review; replaces output-spec-v1.md (archived); built 2026-10-09 by scripts/maturity-site.py, soft launch
---

# Presenting the Maturity Assessment

*(v1 was Bill's twelve-point outline. This version holds his rulings of 2026-10-09 on the sixteen questions raised against it. Model: https://bill-anderson.github.io/africa-dpi/ — its d3 map, control row, legend and tooltip are the starting point.)*

## 1. What is built, and where

Three things, all on the Corpus site:

| Output | Address | New? |
|---|---|---|
| The map | `corpus.data-landscapers.io/maturity/` | new |
| The country report, one per country, all indicators | `/maturity/countries/{iso3}/`, one bookmark per indicator: `#{indicator_id}` | new *(Bill: no per-country-per-indicator report; only the one country report)* |
| The methodology, one page, one bookmark per indicator | `/methodology/maturity/#{indicator_id}` | new section of the existing methodology |

**Soft launch** *(Bill)*. The pages are built and served now but not linked: nothing is added to `site_menu.yml` or to any page's navigation. Each page carries `<meta name="robots" content="noindex">` and an **Under construction** band at the top. It does not matter if they are found. The band comes off, the noindex goes, and the menu entry is added at launch, once data collection is complete.

**Drafts are shown** *(Bill)*. The map and the country reports show draft stages as they are produced; the Under construction band is the only signal and there is no separate draft banner. This is a ruling against `maturity-study-method.md` §8's *nothing is published to `site/` until Bill accepts the study*, for these pages only; the frame, `adding-an-indicator.md` minting and the baseline edition still wait for acceptance.

## 2. Page layout

From top to bottom:

1. The Under construction band.
2. **Control row**: the *Topic* dropdown, the *Indicator* dropdown, then the buttons *Methodology*, *Download this indicator (CSV)* and *Download all (CSV)*.
3. **The body**: the map on the left, as large as the space allows, and on the right a wide sidebar split horizontally into two halves (§6).
4. **The legend** directly under the map (§4).
5. **The changes box** in the whitespace beside the map; the Atlantic, west of the bulge, is the natural place (§7).

At phone width the sidebar stacks below the map and the changes box below the sidebar.

## 3. The map

- **All 54 countries, as large as possible.** The geojson is `africa-dpi/africa.geojson`, copied into the site.
- **Island states get clickable circles** *(Bill)*: Cabo Verde, Comoros, Mauritius, Seychelles and São Tomé and Príncipe each get a circle about 16 px across beside their outline, filled with the stage colour and answering hover, click and double-click exactly as a mainland country does.
- **Western Sahara is greyed out** *(Bill)*: drawn in the no-evidence grey with no tooltip and no click; it is not one of the 54.
- **One map per sub-indicator** *(Bill)*: HMIS and EMR are separate options in the Indicator dropdown, each with its own map.

## 4. Colours and the legend

**One grey for everything not staged** *(Bill)*: *No evidence* and *unplaced* share it, and the tooltip says which.

**Five stages, bad to good, readable without red–green discrimination** *(Bill left the choice to Cowork)*. A diverging red–yellow–blue scale (ColorBrewer RdYlBu), which colour-blind readers can tell apart and which still reads as bad to good:

| Stage | Label | Fill |
|---|---|---|
| 1 | Absent | `#d73027` |
| 2 | Nascent | `#fc8d59` |
| 3 | Established | `#fee090` |
| 4 | Operating | `#91bfdb` |
| 5 | Leading | `#4575b4` |
| — | No evidence | `#d4d4d4` |

The labels are the five from `documentation/archived/maturity-assessment.md` §3. Colour never carries the stage alone: the tooltip and the sidebar print the stage number and label.

**The legend gives the generic description of each stage** *(Bill)*, one line apiece, from the same §3 table, plus the grey.

## 5. Interactions

| Action | Desktop | Phone |
|---|---|---|
| Hover | Tooltip: country, stage number and label, the **short summary** (one sentence, ≤ 25 words, method §8) | — |
| Click / tap | Selects the country and fills the bottom half of the sidebar | same |
| Double-click | Opens the country report at `#{indicator_id}` | replaced by a **View in country report** button in the sidebar *(Bill)* |

The sidebar button is on desktop too, so double-click is a shortcut, not the only route. A single click is delayed by the double-click interval only if testing shows the sidebar flickering before navigation; otherwise both fire.

## 6. The sidebar

**Top half: the indicator.** The scale criteria for the selected indicator, being its ladder (the rung-by-aspect table, condensed to one line per stage), and a button to the indicator's bookmark on the methodology page.

**Bottom half: the selected country** *(Bill)*. A summary of the indicator's section in that country's report, as long as the space allows, headed by:

- the stage, number and label;
- **Last assessed**: the date the stage was last set or confirmed (`assessed_on`);
- **Stage last moved**: the month the stage last changed on evidence. A change from a re-read or a rubric correction (`reassessed = 1`) does not count as a move; it is shown here as *Reassessed {month}* when it is the latest change *(Bill: reassessments are handled here, not in the changes box)*;
- then the short summary, then as much of the long summary as fits, ending in **View in country report**.

Before a click it says *Select a country.*

## 7. The changes box

**Stage changes on evidence in the past six months, for the selected indicator.** One line per change: *Country: stage 2 → 3 (Aug 2026)*, newest first. The initial baseline is excluded *(Bill)*, and so are reassessed cells *(Bill: see §6)*. With nothing to show it says *No stage changes in the past six months.*, which is what it will say until the first post-baseline snapshot.

## 8. The dropdowns

**Topic** lists the topics of `lookups/indicators.csv` (`Topic`, in `Topic Sort` order). **Indicator** lists only the selected topic's indicators, in `Indicator Sort` order, with sub-indicators as their own entries. **Unstudied indicators are shown greyed out** and cannot be chosen *(Bill)*; a topic with no studied indicator is greyed out the same way. The page opens on the first studied indicator.

## 9. Methodology and downloads

**Methodology** goes to `/methodology/maturity/#{indicator_id}` *(Bill)*: one page holding the general method (the scale, the null, the as-at rule, the two phases) and then one section per indicator with its norm, typology, aspects and ladder, built from each study's `study.json` and study file.

**Downloads are dated editions, offered only at launch** *(Bill, 2026-10-09)*. *This indicator* is that indicator's `assessment.csv`; *all* is every studied indicator's rows in one file; both served from R2 under `design.md` §9, where a dated file once downloaded is kept for ever. Until launch the buttons show disabled with *Downloads available at launch*, and the same files are written undated to `maturity/preview-downloads/`, outside `site/`, for Bill to check.

## 10. The country report

**One page per country covering every studied indicator** *(Bill)*, grouped by topic in frame order, one section per indicator or sub-indicator with the anchor `#{indicator_id}`. Each section: stage and label, Last assessed, Stage last moved, the short summary, then the long summary (one paragraph per aspect, every claim linked, method §8), then *Noted, not assessed* and *Not held*. Unstudied indicators are listed by name only, marked *Not yet studied*. The page is assembled at render from the per-study `outputs/maturity/{id}/{ISO3}.md` files; nothing is written by hand.

## 11. What the page reads

One JSON built at render, `site/maturity/data/maturity.json`: per indicator, its topic, label, studied flag, ladder lines and methodology anchor; per country per indicator, stage, label, `assessed_on`, last move, reassessed flag, short summary, sidebar summary text and report anchor; and the six-month changes list. Source: every `outputs/maturity/{id}/assessment.csv`, the history file, `lookups/indicators.csv` and the §3 stage table. The map holds no content of its own.

## 12. Build and launch

`scripts/maturity-site.py` builds all three outputs (RENDER Step 6c). The geography is `lookups/africa.geojson`, copied from africa-dpi; d3 is vendored at `site/assets/js/d3-7.9.0.min.js`. A study's `study.json` → `redraws` names the frame rows its sub-indicators stand in for until acceptance.

**At launch**: `LAUNCHED = True` in the script (drops the band and the noindex, enables downloads), the menu entry in data-landscapers `_data/site_menu.yml`, and a `content/changelog.md` entry. None is made before.

## 13. Still open

- **Legend lines.** The five one-line descriptions paraphrase the archived §3 table's *instruments and systems* column; if that table changes for the new method, they change with it.
- **Stage history.** No snapshot history exists yet, so every cell reads *First assessment* and the changes box is empty; both read `maturity-history.csv` once the second snapshot is cut.
