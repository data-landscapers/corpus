# Progress filler — throughput record, KEN, 2026-08-28

*(The eighth run of `PROGRESS-FILLER.md`, and the first against Kenya — no prior KEN
run, so §0's skip found nothing to carry forward. Batch label
`progress-filler-KEN-2026-08-28`. Run CSV: `logs/progress-filler/KEN-2026-08-28.csv`, with
the selected and unselected registers beside it.)*

## The headline

**28 of 28 gaps had evidence to find. Zero nils.** A smaller frame than NGA's 29, on a
comparably well-populated ledger — 285 rows before this run.

**27 of 28 indicators closed at the full 1 baseline + 2 progress; one closed at 1+1**
(`dpi.id--robustness-of-system`). 83 selections over 75 distinct files is 2.96 per gap, the
densest cap-fill of the series so far (ahead of NGA's 2.90 and BFA's 2.82).

## Stage 1 — the sweep (complete)

| | |
|---|---|
| Gaps worked | 28 of 28 (no skips — no prior KEN run) |
| `agent_run` calls | 56 — 2 per gap, `effort: medium` |
| Candidates returned | 206 |
| Fetched | 89 |
| Dropped | 2 — `already-seen` 1, `off-topic` 1 |
| Held back by the cap | 4, recorded with URLs in the unselected register |
| **Staged after the cap** | **83 selections — 28 baseline + 55 progress — over 75 distinct files**, filed as 25 in `KEN/baseline/` and 50 in `KEN/progress/` |
| Batch size on disk | ~1.55 MB |
| Sessions | one |

## Slicing and cross-slice dedup

**Three slices, grouped by Level-1 with small chapters merged to fill a batch**: Governance +
ICT Infrastructure (8 gaps), the whole DPI chapter (11 gaps), and
Digitalisation + Capacity + Data + Geopolitics (9 gaps).

**Four cross-slice URL duplicates, all caught and resolved at merge** — the highest count of
this series so far, in line with the densest cap-fill:

- The Births and Deaths Registration (Amendment) Rules 2024 — staged independently by the DPI
  slice (`dpi.id--interoperability-of-birth-registration-and-digital-id`'s baseline) and the
  Digitalisation slice (`digital.rural--digitalisation-of-rural-registry-offices`'s baseline),
  under the **same composed filename**, so the second write silently overwrote the first —
  caught by the sibling slice checking its own file post-write, flagged for the parent rather
  than resolved in place, exactly as the procedure asks. One survivor kept, `topics:` and
  `note:` merged to carry both indicators' rationale.
- The Statistics Act 2006 (Cap. 112) — staged twice under different filenames by the
  Governance/Infra slice (`gov.legislate--statistics-legislation`'s baseline, `full`, 42.5 KB)
  and the Data slice (`data.statistics--censuses-and-surveys`'s baseline, `excerpt`, 8 KB).
  Kept the fuller capture.
- The NSDM/ArdhiSasa countrywide land-registry rollout notice — staged twice under different
  filenames by the Digitalisation slice (`digital.rural`'s progress pick, `full`, 5.1 KB) and
  the DPI slice (`dpi.mis--land`'s progress pick, `full`, 4.9 KB) — both `full`; kept the
  larger and merged the notes, since each slice had read a different facet of the same notice
  (registry-office coverage vs. the stamp-duty module).
- The Statistics Bill 2026 — staged twice under different filenames by the Governance/Infra
  slice (`gov.legislate`'s progress pick, `full`, 2.4 KB) and the Data slice
  (`data.statistics--national-strategy-for-development-of-statistics`'s progress pick,
  `excerpt`, 2.0 KB). Kept the fuller capture.

**Four further files legitimately serve two indicators each** (not duplicates — one document,
two indicators, staged once): a national data-governance-policy validation notice
(`gov.policy`/`gov.legislate`), the Social Protection Act 2025
(`dpi.exchange`/`dpi.registry`), the NPDM (formerly IPRS) page
(`dpi.registry`/`dpi.id`), and a KNA article on ID-registration technology
(`dpi.id`/`dpi.registry`).

**`scripts/lint-staged-queue.py` reports clean** over both folders (75 files) after the merge.
83 selections resolve to exactly 75 files on disk, verified programmatically: zero rows
pointing at a missing file, zero orphan files, zero cap violations, zero duplicate URLs
remaining.

## Capture quality, declared

- **63 of 75 are `body_completeness: full`, 12 `excerpt`** — flagged, not retried, per
  `capture-rule.md`.
- **65 of 75 carry `date_source: source`, 10 `proxy`.** Precision is `day` on 62, `month` on
  11, `year` on 2.
- **The three largest files**: the Auditor-General's 2024/25 national government report
  (196 KB), the Energy Act 2019 (196 KB), and the East African Community Treaty of
  Establishment (179 KB) — the last a founding regional instrument rather than a Kenya-specific
  one, staged as `gov.regional--regional-policy-collaboration`'s baseline.
- No mojibake (`�`) found in a scan of all 75 staged bodies.

## Origin adjudications — none

**Zero new watch/drop rows.** All three slices reported every candidate domain as either
already-known or novel-and-informational; `progress-filler-drop-list.csv` is unchanged from
the GNB run — still 8 rows across five earlier countries. This run's `notes-for-osint.md`
entry is a plain `[FYI]`.

## Stages 2–4 — not yet run

- **Stage 2 — the stage 4 read.** Pending Bill's hand-carry of `new-queue/KEN/` into
  `OSINT\new\`, `update wiki`, and the mirror refresh.
- **Stage 3 — the mapping.** `outputs/reports/KEN/indicators.csv` rewritten by hand against
  `documentation/indicator-mapping-conventions.md`.
- **Stage 4 — the render.**

**Yield is stated when stage 3 lands**, as gaps closed against the 28 probed and against
sessions spent.
