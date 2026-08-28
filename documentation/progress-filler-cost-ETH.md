# Progress filler — throughput record, ETH, 2026-08-28

*(The tenth run of `PROGRESS-FILLER.md`, the second at five concurrent slices. No prior ETH
run, so §0's skip found nothing to carry forward. Batch label
`progress-filler-ETH-2026-08-28`. Run CSV: `logs/progress-filler/ETH-2026-08-28.csv`, with
the selected and unselected registers beside it.)*

## The headline

**55 of 55 gaps had evidence to find. Zero nils — including the entire `dpi.registry`
chapter**, all eight of whose indicators entered this run at `subject_rows_at_probe = 0` (no
prior evidence in the ledger at all) and were flagged in the brief as a genuine risk of a thin
chapter. Every one closed with a baseline: Ethiopia's registries turn out to be documented, just
under a different framing than a named standalone register — mostly as modules of the
Digital Ethiopia 2030 programme, the Civil and Family Registration Proclamation, or
sector-specific systems (SSGI's address-registry pilots, the Addis Ababa land bureau's ILIMS).

**42 of 55 indicators closed at the full 1 baseline + 2 progress; 13 at 1+1.** No indicator
fell below 1+1 or lost its baseline. 152 selections over 121 distinct files, 2.76 per gap.

## Stage 1 — the sweep (complete)

| | |
|---|---|
| Gaps worked | 55 of 55 (no skips — no prior ETH run) |
| `agent_run` calls | 110 — 2 per gap, `effort: medium` |
| Candidates returned | 417 |
| Fetched | 160 |
| Dropped | 18 — `already-seen` (3 rows), `fetch-blocked` (5), `headline-only-stub` (2) |
| Held back by the cap | 93, recorded with URLs in the unselected register |
| **Staged after the cap** | **152 selections — 55 baseline + 97 progress — over 121 distinct files**, filed as 45 in `ETH/baseline/` and 76 in `ETH/progress/` |
| Batch size on disk | ~1.0 MB |
| Sessions | one |

## Five slices, and the cross-slice warning broadcast to every one this time

**RWA's cost record ended on a lesson**: warn every slice about cross-cutting subjects, not
just the ones an L1 grouping makes look obviously adjacent — four of RWA's five duplicates
originated in slices that weren't warned. This run's five slice briefings all carried the same
warning and the same instruction to check the shared queue by URL regardless of apparent
topic match, before fetching. **Grouped**: Governance+Finance+Infra (12), DPI registries +
Digitalisation (13), DPI exchange/ID/payments/MIS (12), Technology+Capacity+Inclusion (10),
Data+Geopolitics (8).

**Four cross-slice URL duplicates, all caught and resolved at merge** — lower than RWA's five
despite a comparable frame size, plausibly because every slice was warned this time:

- The REILA land-administration programme close-out report — staged twice by two different
  slices (`digital.rural--digitalisation-of-rural-registry-offices`'s baseline at 7.3 KB, and
  `dpi.mis--land`'s baseline at 4.3 KB). Kept the fuller capture, merged `topics:`/`note:`.
- A Government Communication Service article on the Addis Ababa civil-registration pilot —
  staged twice (`digital.localgov`'s baseline / `dpi.registry--population-register`'s progress
  pick at 2071 bytes, and `dpi.id--interoperability-of-birth-registration-and-digital-id`'s
  progress pick at 2088 bytes). Kept the baseline-designated file per §5's baseline-wins rule
  despite the tiny size difference, merged all three indicators' rationale onto it.
- The Ethiopia OpenAgriNet launch announcement — staged twice under different filenames by two
  slices, on top of already being legitimately cross-listed by a third
  (`tech.ai`'s baseline, `gov.policy--open-data-policy`'s progress pick, and
  `data.open--use-of-open-data`'s progress pick all converged on one URL). Kept the
  baseline-designated file, now carrying four indicators.
- A World Bank PSNP6 (Productive Safety Net Project 6) approval press release — staged twice
  (one copy already legitimately shared by two DPI indicators, one copy staged separately by
  the registries slice for `dpi.registry--social-protection-register`). Kept the larger, now
  carrying three indicators.

**Twenty further files legitimately serve two or more indicators each** — the densest
multi-indicator sharing this series has produced (ahead of RWA's fifteen), led by the Council
of Ministers' approval of the Digital Ethiopia 2030 strategy (four governance indicators) and
the MInT e-government service-provision assessment (three).

**One accounting defect, caught and fixed at merge — a genuinely missing file, not a
misdescription.** The registries/digitalisation slice's selected register named a progress
pick (`2026-04-09-worldbank-additional-financing-education-transformation-operation.md`) for
`digital.rural--digitalisation-of-rural-primary-schools` that was never actually written to
disk — no fetch or write error surfaced in the sub-agent's own report, so the cause is
unclear. Withdrawn at merge rather than fabricated or refetched blind:
`logs/progress-filler/ETH-2026-08-28-misfiled.csv` records it, the run CSV's `staged_progress`
for that indicator comes down from 2 to 1, and the indicator still stands searched (not nil) on
its remaining baseline + one progress pick.

**Four `lint-staged-queue.py` SUSPECT findings, all verified false positives** — short
articles or a constitution whose own heading wraps across lines or opens with a dateline
rather than restating the title, with host/URL/publisher all tracing correctly. Two sub-agents
independently verified these against their own files' provenance before the parent's merge
pass confirmed the same four persist unchanged.

**`scripts/lint-staged-queue.py` reports clean of any addressable finding** over both folders
(121 files) after the merge. 152 selections resolve to exactly 121 files on disk, verified
programmatically: zero rows pointing at a missing file, zero orphan files, zero cap
violations, zero duplicate URLs remaining.

## Capture quality, declared

- **82 of 121 are `body_completeness: full`, 39 `excerpt`** — flagged, not retried, per
  `capture-rule.md`.
- **113 of 121 carry `date_source: source`, 8 `proxy`.** Precision is `day` on 103, `month` on
  16, `year` on 2.
- **The three largest files**: the Digital Education Strategy 2023–2028 (152 KB), the Startup
  Proclamation No. 1396/2025 (133 KB), and the 1995 Constitution (87 KB).
- No mojibake (`�`) found in a scan of all 121 staged bodies.

## Origin adjudications — none

**Zero new watch/drop rows.** All five slices reported every candidate domain as either
already-known or novel-and-informational; `progress-filler-drop-list.csv` is unchanged — still
8 rows across five earlier countries. This run's `notes-for-osint.md` entry is a plain
`[FYI]`.

## Stages 2–4 — not yet run

- **Stage 2 — the stage 4 read.** Pending Bill's hand-carry of `new-queue/ETH/` into
  `OSINT\new\`, `update wiki`, and the mirror refresh.
- **Stage 3 — the mapping.** `outputs/reports/ETH/indicators.csv` rewritten by hand against
  `documentation/indicator-mapping-conventions.md`.
- **Stage 4 — the render.**

**Yield is stated when stage 3 lands**, as gaps closed against the 55 probed and against
sessions spent.

## What this says about scheduling

**Warning every slice about cross-cutting subjects, not just the adjacent ones, measurably
helped**: four duplicates against RWA's five on a comparable frame (55 gaps vs. 52), and the
registries chapter — flagged in advance as a possible thin spot — turned out fully evidenced
once slices were told to search past the literal indicator name. Both are cheap prompt-level
fixes worth keeping standing practice for every run above ~40 gaps.
