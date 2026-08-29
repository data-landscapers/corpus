# Progress filler — throughput record, LSO, 2026-08-29

*(Run against Lesotho — no prior LSO run, so §0's skip found nothing to carry forward. Batch
label `progress-filler-LSO-2026-08-29`. Run CSV: `logs/progress-filler/LSO-2026-08-29.csv`,
with the selected and unselected registers beside it.)*

## The headline

**60 of 60 gaps had evidence to find. Zero nils.** The largest frame worked so far in this
series (LSO's held report carried only 61 of 121 indicators before this run).

**Every one of the 60 indicators closed at the full 1 baseline + 2 progress**, except three
that closed at 1 baseline + 1 progress where a genuine second candidate did not survive
screening (`infra.capacity--robustness-of-government-hardware-and-software`,
`digital.rural--digitalisation-of-rural-health-clinics`,
`dpi.exchange--interoperability-of-education-systems`,
`tech.ai--development-of-national-regional-ai-systems`,
`include.access--inclusion-of-refugees-and-idps`) — none padded. 174 selections resolve to
127 distinct files, a cross-slice sharing rate the highest of the series so far: parallel
sub-agents independently converged on the same broad government documents (the MICSTI–UNICEF
digital-ID work plan alone was independently selected across **11 different indicators** by
five of the six slices).

## Stage 1 — the sweep (complete)

| | |
|---|---|
| Gaps worked | 60 of 60 (no skips — no prior LSO run) |
| `agent_run` calls | 120 — 2 per gap, `effort: medium` |
| Candidates returned | 517 |
| Fetched | 181 |
| Dropped | 27 — `already-seen` 10, `duplicate-raw` 6 (mirror `DUP-EXACT` via `raw-url-index.py`), `headline-only-stub` 1, `inadmissible-origin` 1, remainder substituted inline before reaching the drop tally |
| Held back by the cap | 110, recorded with URLs in the unselected register |
| **Staged after the cap** | **174 selections — 60 baseline + 114 progress**, over **127 distinct files**, filed as 49 in `LSO/baseline/` and 78 in `LSO/progress/` |
| Sessions | one (six parallel sub-agents, one parent merge) |

## Slicing and cross-slice dedup

**Six slices, grouped by Level-1 with small chapters merged to fill a batch**: Governance (11),
ICT Infrastructure + Digitalisation (11), DPI Data Exchange + Digital Identity + Payments (10),
DPI Registries + Sectoral MIS (10), Technology + Capacity + Inclusion/Access (11), and
Inclusion/Divides + Data + Geopolitics (7).

**Twelve cross-slice URL duplicates, 15 loser files retired at merge** — by far the largest
consolidation this series has needed, a direct consequence of Lesotho's evidence base
concentrating on a small number of broad cross-cutting documents (a national strategy, a
ministry work plan) that answer many indicators at once:

- The **MICSTI–UNICEF digital-ID work plan** was staged three times under three filenames by
  five sibling slices, spanning eleven indicators from `gov.standards` to `data.statistics`.
  One survivor kept (`progress/2026-02-26-lesotho-micsti-unicef-digital-id-work-plan.md`),
  `topics:` merged to eight Topic L2 slugs, `note:` carries every indicator it now serves.
- The **Financial Sector Development Strategy II** was staged as both a `dpi.id` baseline and
  a `gov.legislate` progress pick under the identical filename in both folders — baseline wins
  per §5, progress copy retired.
- The **LCA Strategic Plan 2026–2029** — same pattern, baseline (`include.divides`) over
  progress (`infra.connect`).
- The **National Home Affairs digital-ID modernisation** article was staged three times
  (`gov.legislate`, `dpi.registry`, `dpi.id`) under three filenames — one survivor, three
  indicators merged.
- Seven further two-way duplicates (WHO Lesotho 2025 Annual Report — with a genuine
  `published` date conflict recorded in the survivor's `note:` rather than resolved, per §6;
  the UN Global Dialogue AI-governance statement; the Moorosi meaningful-connectivity article;
  the Payment System Bill coverage; the LENA DPI-framework workshop; the RSL–Standard Lesotho
  Bank integration; the STATAFRIC/NSS peer-review report; the UNDP Lehokela launch) — each
  resolved to the fuller capture, topics and notes merged.

**One bookkeeping duplicate caught and removed**: a single sub-agent's own `selected.csv`
carried the same file/brief/rank row twice under `dpi.mis--land` (a CSV-writing slip, not a
second real selection) — dropped at merge, bringing that indicator back to its correct 1+2.

**`scripts/lint-staged-queue.py` reports one open finding, investigated and cleared**: a
`CROSSED` flag between the WHO Lesotho 2025 Annual Report and the National Digital Policy
2024–2035 (both long PDF extracts scoring high on the title-token heuristic). Both bodies were
read in full and correctly match their own frontmatter — a false positive from two
similarly-structured government documents, not a real crossing. No other file in the batch was
flagged.

**A parent-side write bug, caught and fixed before commit**: the frontmatter-merge pass that
consolidated the twelve duplicate groups' `topics:`/`note:` fields initially dropped the
newline separating the merged `note:` line from the closing `---` delimiter (a greedy `\s*$` in
the merge regex), breaking YAML parsing on exactly the twelve touched files.
`lint-staged-queue.py` caught all twelve as `no frontmatter block`; repaired programmatically
by re-inserting the missing newline, then re-linted clean.

## Capture quality, declared

- **92 of 127 are `body_completeness: full`, 35 `excerpt`** — flagged, not retried, per
  `capture-rule.md`. Excerpts are concentrated in long Acts, gazette scans and donor PDFs
  truncated at fetch-length limits.
- **116 of 127 carry `date_source: source`, 11 `proxy`.** Precision is `day` on 113, `month`
  on 8, `year` on 6.
- One filename/date-prefix correction made at merge: a WMO regional report's filename said
  `2011-07-01` against its own `published: 2011-07-19` — renamed to match.
- One recorded, unresolved `published` date conflict: the WHO Lesotho 2025 Annual Report
  (two captures of the identical URL recorded 2026-04-01 and 2026-04-09) — left in the
  survivor's `note:` for ingest to settle with the document in hand, per §6.

## Origin adjudications — none

**Zero new watch/drop rows.** All six slices reported every candidate domain as either
already-known or novel-and-informational; `progress-filler-drop-list.csv` is unchanged by this
run. This run's `notes-for-osint.md` entry is a plain `[FYI]`.

## Stages 2–4 — not yet run

- **Stage 2 — the stage 4 read.** Pending Bill's hand-carry of `new-queue/LSO/` into
  `OSINT\new\`, `update wiki`, and the mirror refresh.
- **Stage 3 — the mapping.** `outputs/reports/LSO/indicators.csv` rewritten by hand against
  `documentation/indicator-mapping-conventions.md`.
- **Stage 4 — the render.**

**Yield is stated when stage 3 lands**, as gaps closed against the 60 probed and against
sessions spent.
