---
type: task
title: Baseline filler — find the missing start positions in the region progress reports
last_reviewed: 2026-09-11
---

# Baseline filler — find the missing start positions in the region progress reports

**Queued, not run.** Written 2026-09-11 at Bill's request. Trigger: "**run the baseline filler**", optionally naming a region (`XAF`, `XWA`…). Until he says so, nothing here fetches.

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

**Cost.** 119 briefs, against the ~121-gap country passes costed in `documentation/archived/progress-filler-cost-{ZAF,AGO,GNB}.md` — roughly one country pass of the week, less the progress briefs.
