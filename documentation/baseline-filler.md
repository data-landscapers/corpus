---
type: task
title: Baseline filler — find the missing start positions in the region progress reports
last_reviewed: 2026-09-11
---

# Baseline filler — find the missing start positions in the region progress reports

**Run for all six regions on 2026-09-11** (see *Runs*); a re-run regenerates the list first. Written 2026-09-11 at Bill's request. Trigger: "**run the baseline filler**", optionally naming a region (`XAF`, `XWA`…). Until he says so, nothing here fetches.

## What

Every region-ledger row whose Progress prints ***Baseline not held*** — the base holds where the thing stood at the end of the period and nothing on where it stood at the start (2025-09-01). **119 of 408 rows**, over a quarter of what the six region reports compare, currently state no direction at all. A baseline found turns each into *Movement*, *No change*, *Stalled* or *Regressed*, which is the finding the report exists to make.

The list is `logs/baseline-not-held-rows.csv` (unit, row_id, section, subject, name, status, published, both positions, sources). **It is a snapshot of 2026-09-11 — regenerate it at run time**, because the ledgers move every cycle. The selection is `report-render.py`'s own: a row is on it when its `position_start` is empty or one of `NO_BASELINE`'s phrasings, or its `movement` is *Baseline not held* with any start other than "Did not exist". Rows whose status is ***Not held*** are excluded: they hold no position at either end and belong to `gaps.csv`.

| Region | Rows | Of |
|---|---|---|
| XAF | 58 | 171 |
| XWA | 25 | 86 |
| XEA | 13 | 51 |
| XCA | 11 | 43 |
| XSA | 10 | 44 |
| XNA | 2 | 13 |

Order: that table, top down — the most unanswered rows first.

## How

**The machinery is PROGRESS-FILLER's** (`documentation/archived/PROGRESS-FILLER.md`); read §0, §3–§6 and §8 before running and apply them unchanged except as follows.

- **Object: a ledger row, not an indicator.** One Exa brief per row, Brief 1 only: *"{name} ({region name}): what was its position on or before 2025-09-01?"*, with `position_end` and the row's `sources` given as context so the search looks for an earlier state of the same thing rather than for the thing again. No progress brief — the end position is already held.
- **Cap: one baseline document per row.** A nil is a finding and is recorded, never padded.
- **Staging: `C:\corpus-osint-xfer\new-queue\{XUNIT}\baseline\`**, §5's shape, then `python scripts/lint-staged-queue.py`. The batch is undelivered until Bill hand-carries it — say so.
- **Run record: `logs/progress-filler/{XUNIT}-YYYY-MM-DD.csv`** as §8, keyed on `row_id` in place of `indicator_id`.
- **Authorisation.** §0 authorised the progress pass alone. Bill's trigger is this pass's authorisation, on the same boundary: nothing written to `C:\OSINT`, nothing entering a ledger directly.
- **The loop closes through BUILD, not here.** Once OSINT ingests a batch, the report update sets `position_start` on the row from the new source and the next render moves its Progress. A staged file that never comes back through ingest changes nothing.

## Runs

**XAF, 2026-09-11.** 58 rows: **36 staged** (34 files in `new-queue\XAF\baseline\`, two each answering two rows), **10 held**, **12 nil**. Records: `logs/progress-filler/XAF-2026-09-11{,-selected,-unselected}.csv`. Three picks were withdrawn at merge as not stating their row's pre-window position (the reasons are in the unselected register), which is why those rows are nil.

- **The 10 `held` rows need no ingest.** The base already holds a document stating their start position — the selected register names each `raw/` file — so the next report update can set `position_start` from it directly. Until it does, those rows keep printing ***Baseline not held***.
- **The 36 staged rows wait on Bill's hand-carry and OSINT's ingest** (`notes-for-osint` 136), then the report update.
- **Dedup is by exact URL against `lookups/raw-url-index.csv`**, run through a helper that also flags a same-path match on another host. It misses a held document filed under a different URL; the slices caught three that way by title. A later run should search `raw/` titles as well.

**XWA, XEA, XCA, XSA, XNA, 2026-09-11.** 61 rows, list regenerated at run time and matching the snapshot: **31 staged** (29 files, one answering two XSA rows, and one XWA row answered by a file already in the XAF batch), **25 held**, **5 nil**. By region, staged/held/nil: XWA 15/8/2, XEA 6/6/1, XCA 2/8/1, XSA 7/2/1, XNA 1/1/0. Records: `logs/progress-filler/{XWA,XEA,XCA,XSA,XNA}-2026-09-11{,-selected,-unselected}.csv`.

- **One folder, not five.** At Bill's request the batch is staged flat in `new-queue\regions-baseline\`, not `new-queue\{XUNIT}\baseline\`; each file's `sweep_batch` still names its own region.
- **Most held rows are held on their own source.** Where a row's only source predates 2025-09-01 (an enacting act, a 2018 study), that source is its start position, following the XAF precedent. The report update sets `position_start` from it.
- **For the report update:** `XWA-finance.new-janngo-startup-fund` carries `published` 2026-08-09, but its staged baseline dates the fund's first close to 2022 and the EUR10.5m approval appears to be from December 2021, so check the row's date against its source. `XSA-tech.ai-sadc-ai-position`'s better lead (the SADC Parliamentary Forum's 57th plenary communiqué) would not fetch; it sits in the unselected register.
- **Taxonomy check against `wiki/topics-index.md`**: `wiki/taxonomy.md`, which PROGRESS-FILLER §5a names, is not in the mirror.

**Cost.** 119 briefs, against the ~121-gap country passes costed in `documentation/archived/progress-filler-cost-{ZAF,AGO,GNB}.md` — roughly one country pass of the week, less the progress briefs.
