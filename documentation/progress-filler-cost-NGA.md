# Progress filler — throughput record, NGA, 2026-08-28

*(The seventh run of `PROGRESS-FILLER.md`, and the first against Nigeria — no prior NGA
run, so §0's skip found nothing to carry forward. Batch label
`progress-filler-NGA-2026-08-28`. Run CSV: `logs/progress-filler/NGA-2026-08-28.csv`, with
the selected and unselected registers beside it.)*

## The headline

**29 of 29 gaps had evidence to find. Zero nils.** NGA is a smaller frame than the last four
runs (BFA 57, BEN 64, BDI 78, GNB 100) because Nigeria's ledger is already comparatively
well populated — 285 rows before this run, against 25 for GNB — so most of the 121-indicator
frame was already held and only 29 indicators reached this pass at all.

**26 of 29 indicators closed at the full 1 baseline + 2 progress; three closed at 1+1**
(`gov.policy--data-governance-policy`, `gov.policy--open-data-policy`,
`data.statistics--statistics-from-administrative-data`) — no indicator fell below 1+1. 84
selections over 77 distinct files is 2.90 per gap, the densest cap-fill of the series so far
(ahead of BFA's 2.82).

## Stage 1 — the sweep (complete)

| | |
|---|---|
| Gaps worked | 29 of 29 (no skips — no prior NGA run) |
| `agent_run` calls | 58 — 2 per gap, `effort: medium` |
| Candidates returned | 219 |
| Fetched | 94 |
| Dropped | 2 — `headline-only-stub` 1, `already-seen` 1 |
| Held back by the cap | 9, recorded with URLs in the unselected register |
| **Staged after the cap** | **84 selections — 29 baseline + 55 progress — over 77 distinct files**, filed as 28 in `NGA/baseline/` and 49 in `NGA/progress/` |
| Batch size on disk | ~0.72 MB |
| Wall clock | ~30 minutes, three sub-agents concurrent (longest: the 12-indicator digital/inclusion/data/geopolitics slice, ~29.4 min) |
| Sessions | one |

## Slicing and cross-slice dedup

**Three slices, grouped by Level-1 with small chapters merged to fill a batch**: Governance +
Finance + ICT Infrastructure (7 gaps), the whole DPI chapter (10 gaps), and
Digitalisation + Inclusion + Data + Geopolitics (12 gaps).

**One cross-slice URL duplicate, caught and resolved at merge.** The Federal Ministry of
Education's DNEMIS pre-launch announcement was independently staged twice — once by the
DPI slice as `dpi.exchange--interoperability-of-education-systems`'s baseline, and once by
the Digitalisation/Inclusion/Data slice as `data.open--use-of-open-data`'s progress pick —
both `body_completeness: full`, same URL, same `published` date. Resolved by keeping the baseline copy (baseline wins, per §5), merging
`topics:` and `note:` to carry both indicators' rationale, deleting the progress-folder
duplicate, and repointing `data.open--use-of-open-data`'s selected-register row onto the
survivor. Verified programmatically afterward: 84 selections resolve to exactly 77 files on
disk, zero rows pointing at a missing file, zero orphan files.

**Six further files legitimately serve two indicators each** (not duplicates — one document,
two indicators, staged once): the NIMC Act 2026 assent (baseline for
`dpi.id--digital-id-from-birth`, also `dpi.id--interoperability-of-birth-registration-and-digital-id`'s
progress pick, filed under `baseline/` per the same rule), the National Education Data
Repository (NERD) deployment, the OHOPRS humanitarian/poverty-response flag-off, the VitalReg
registration platform launch, and the unified G2P digital-payment workshop.

**`scripts/lint-staged-queue.py` reports clean** over both folders (77 files) after the merge.

## Capture quality, declared

- **63 of 77 are `body_completeness: full`, 14 `excerpt`** — flagged, not retried, per
  `capture-rule.md`.
- **73 of 77 carry `date_source: source`, 4 `proxy`.** Precision is `day` on 67, `month` on 9,
  `year` on 1.
- **The three largest files**: the National Cloud Policy 2025 (75 KB), the *HEDA v NNPCL*
  judgment (48 KB), and NERC's Q1 2026 quarterly report (40 KB).
- No mojibake (`�`) found in a scan of all 77 staged bodies.

## Origin adjudications — none

**Zero new watch/drop rows.** All three slices reported every candidate domain as either
already-known or novel-and-informational; `progress-filler-drop-list.csv` is unchanged from
the GNB run. This run's `notes-for-osint.md` entry is a plain `[FYI]`.

## Stages 2–4 — not yet run

- **Stage 2 — the stage 4 read.** Pending Bill's hand-carry of `new-queue/NGA/` into
  `OSINT\new\`, `update wiki`, and the mirror refresh.
- **Stage 3 — the mapping.** `outputs/reports/NGA/indicators.csv` rewritten by hand against
  `documentation/indicator-mapping-conventions.md`.
- **Stage 4 — the render.**

**Yield is stated when stage 3 lands**, as gaps closed against the 29 probed and against
sessions spent.
