---
type: brief
reader: cc
title: note-for-cc-2026-10-09.md — the Maturity Assessment's presentation, built and design-locked; what CC inherits before the metadata work
date: 2026-10-09
status: handover; delete once CC has reviewed the build and the metadata work is under way
---

# Maturity presentation: handover from Cowork, 2026-10-09

*(Written at Bill's request after a design session. `output-spec-v2.md` carries the rules and Bill's rulings; this note says what exists, what was decided outside the spec, and what is open.)*

## What is built

Three outputs, all from `scripts/maturity-site.py` (RENDER Step 6c, after `methodology.py`, before `sitemap.py`; writes no edition):

- **`/maturity/`**: the map. d3 (vendored, `site/assets/js/d3-7.9.0.min.js`), `site/assets/js/maturity-map.js`, `site/assets/css/maturity.css`. It reads `site/maturity/data/maturity.json` and `africa.json` (from `lookups/africa.geojson`, africa-dpi's copy) and holds no content of its own.
- **`/maturity/countries/{iso3}/`**: one report per country, a section per studied indicator at `#{indicator_id}`, assembled from `outputs/maturity/{id}/{ISO3}.md`.
- **`/methodology/maturity/`**: the scale, then each indicator's norm and ladder at `#{indicator_id}`, from `outputs/maturity/{id}/{indicator_id}.md`.

The only data so far is the health study's draft (HMIS and EMR, as at 2026-09-30).

## Design is locked *(Bill, 2026-10-09)*

Do not restyle without asking him. The points most easily undone:

- **Colours**: `#b2182b #e66a2c #f2c12e #67a9cf #2166ac`, grey `#d4d4d4`. Chosen for even weight; every pair is distinct under simulated deuteranopia, protanopia and tritanopia.
- **Labels** 2 and 3 are *Preparing* and *Establishing*; all five are still under Bill's review. `relabel()` rewrites the studies' printed ladders at build, so the study outputs are untouched.
- **The map box takes the continent's height** (fitted to a frame excluding Prince Edward and Rodrigues; island circles at fixed coordinates). The sidebar matches the map column's height.
- **Soft launch**: noindex on every page and nothing links to them. The map says *Under construction* in its title; the reports and the methodology page carry the band (`SHOW_BAND`). `LAUNCHED = True` undoes all of it and enables downloads.

## Decided outside the spec

- `maturity/health/study.json` gained `redraws`: the frame rows the sub-indicators stand in for until acceptance. The dropdown shows the sub-indicators in the first row's place.
- **Downloads only at launch**: the buttons are disabled; undated copies go to `maturity/preview-downloads/` for Bill to check, outside `site/`.
- No `content/changelog.md` entry until launch.

## Open, and where the metadata work starts

- **The Methodology button** goes to `/methodology/maturity/#{indicator_id}` (Bill's ruling, spec §9). The v1 spec called this button *metadata*. If the metadata work means a field dictionary for the two CSVs, the site's pattern is `datasets.py` → `/datasets/metadata/` with a `-metadata.csv` per dataset; the maturity CSVs have none yet.
- **Stage history**: none exists, so every cell reads *First assessment* and the changes box is empty until `maturity-history.csv` is written from a second snapshot.
- **Legend definitions** paraphrase the archived §3 table; they change if the stage labels do.

## CC's review, 2026-10-09

- **Downloads at launch are now built.** `publish_downloads()` cuts the dated editions beside the map and the buttons become links; before, `LAUNCHED` only enabled two buttons that did nothing. At launch the script's RENDER line moves ahead of `r2-sync.py`.
- **The build stops instead of blanking the map.** `problems()` runs before anything is written; exit 1 leaves `site/` as it was.
- **`maturity.json` carries no build date**; it rewrote the file daily.
- **`africa.json` is thinned** from 917 KB to 211 KB (`GEO_TOLERANCE`); 15 pixels differ at 1440 px.
- **`lookups/africa.geojson` has its marker**, `AFRICA-GEOJSON-FROM`; `lint-shared-assets.py` compares it with africa-dpi's.
- **Preview CSVs are written LF**, only when their content moves.

## Verified

`scripts/test_maturity_site.py` covers the check, the geography and the launch path. The map was compared before and after in headless Chrome at 1440 px and 390 px. Not checked: launched pages on the live site, where editions come from R2.
