# Progress filler — throughput record, SWZ, 2026-08-29

*(Run against Eswatini (formerly Swaziland) — no prior SWZ run, so §0's skip found nothing to
carry forward. Batch label `progress-filler-SWZ-2026-08-29`. Run CSV:
`logs/progress-filler/SWZ-2026-08-29.csv`, with the selected and unselected registers beside
it.)*

## The headline

**78 of 78 gaps had evidence to find. Zero nils.** The largest frame this series has run,
comfortably ahead of LSO's 60 the same day — Eswatini's held report carried only 43 of 121
indicators before this run.

**77 of 78 indicators closed with a baseline; the sole exception**
(`gov.policy--data-storage-cloud-strategy`) closed at 0 baseline + 2 progress because its
strongest baseline candidate was already held in OSINT's `raw/` (a `DUP-EXACT` skip) — a
correct nil-baseline, not a gap in the sweep. 217 selections resolve to 159 distinct files, a
cross-slice sharing rate even denser than LSO's: seven parallel sub-agents drawing on a small,
overlapping national evidence base (the 2026 Budget Speech alone answers eight indicators
across five slices) produced 21 URL-duplicate groups needing consolidation at merge, against
LSO's twelve.

## Stage 1 — the sweep (complete)

| | |
|---|---|
| Gaps worked | 78 of 78 (no skips — no prior SWZ run) |
| `agent_run` calls | 157 — ~2 per gap, `effort: medium` |
| Candidates returned | 773 |
| Fetched | 223 |
| Dropped | 30 — `already-seen` 12, `inadmissible-origin` 3, `out-of-window` 3, `duplicate-raw` 2, `off-topic` 2, `no-development` 1, `fetch-blocked` 1 |
| Held back by the cap | 118, recorded with URLs in the unselected register |
| **Staged after the cap** | **217 selections — 77 baseline + 140 progress**, over **159 distinct files**, filed as 63 in `SWZ/baseline/` and 96 in `SWZ/progress/` |
| Sessions | one (seven parallel sub-agents, one parent merge) |

## Slicing and cross-slice dedup

**Seven slices, grouped by Level-1 with Governance and DPI each split into two** (both chapters
ran to 20 and 25 gaps respectively, too large for one slice): Governance A (policy/regional/
discourse, 11), Governance B (legislate/standards/finance, 11), ICT Infrastructure +
Digitalisation (11), DPI Data Exchange + Digital Identity (10), DPI Payments/Sectoral MIS +
Capacity (11), DPI Registries + Technology + Capacity training (11), Inclusion + Data +
Geopolitics (13).

**Twenty-one cross-slice URL duplicates, 27 loser files retired at merge** — the densest
consolidation this series has needed:

- The **2026 Budget Speech** split across **two genuinely different URLs** (Parliament's own
  copy and the Ministry of Finance's `gov.sz` mirror) — each treated as its own duplicate group
  rather than collapsed into one, since a different host is a different capture, not a
  dedupable pair. The Parliament copy answers five indicators across three slices; the
  Ministry mirror answers three across three slices.
- The **MICT/DPMO Annual Performance Reports**, the **National FinTech Strategy 2025–2030**
  (staged four times under four filenames, spanning five indicators), the **Digital Eswatini
  World Bank appraisal documents** (three filenames), and the **UNDP Digital Readiness
  Assessment 2024** (three filenames) were each independently captured by multiple slices.
- **One in-flight accidental overwrite, self-reported and recovered.** A sub-agent issued a
  placeholder `Write` that landed on an existing sibling's file
  (`progress/2026-07-22-eswatini-mchumanisi-data-governance-policy-validation.md`), destroying
  its `note:` field's rank/why text. The sub-agent re-fetched the source and flagged the
  incident as `CRITICAL` in its report rather than concealing it. **No data was actually lost**:
  the original selecting batch's own `selected.csv` still held the correct indicator/rank/why
  rows independent of the file's corrupted `note:`, so the merge recovered them from the CSV
  and consolidated this document (2 filenames, 1 URL) into the intact sibling capture
  (`mchumanisi-data-exchange-platform.md`), now serving six indicators across four slices.
- Baseline kept over progress in every folder-crossing case, per §5; same-folder duplicates
  resolved to the fuller verbatim capture, topics and notes merged onto the survivor.
- **One date conflict recorded rather than resolved**: the MICT Annual Performance Report
  (`baseline/2024-01-01-eswatini-mict-annual-performance-report-2024-25.md`, the fullest of
  three captures at 50KB) carries `published: 2024-01-01` against two sibling captures of the
  identical URL recording `2025-01-01` — left in the survivor's `note:` for ingest to settle
  with the document in hand, per §6.

**`scripts/lint-staged-queue.py` reports seven open `SUSPECT` findings, all investigated and
cleared.** Every flagged file is an ordinary news or UN article whose body does not literally
restate its own headline — the heuristic's known false-positive shape — confirmed by reading
each body against its own frontmatter. No `CROSSED` or `MISFILED` finding in the batch. One
malformed CSV row (an unescaped comma in a title field) was caught and repaired during the
merge's own CSV build, before it could corrupt the final registers.

## Capture quality, declared

- **113 of 159 are `body_completeness: full`, 46 `excerpt`** — flagged, not retried, per
  `capture-rule.md`. Excerpts cluster in long government PDFs (Annual Performance Reports,
  Acts, the Budget Speech, the FinTech Strategy) truncated at fetch-length limits.
- **142 of 159 carry `date_source: source`, 17 `proxy`.** Precision is `day` on 124, `month`
  on 19, `year` on 16.
- No filename/date-prefix corrections needed beyond the one recorded conflict above.

## Origin adjudications — none

**Zero new watch/drop rows.** All seven slices reported every candidate domain as either
already-known, novel-and-informational, or an existing drop-list entry (`africa-press.net`,
`vatupdate.com`) re-encountered rather than newly adjudicated. `progress-filler-drop-list.csv`
is unchanged by this run. This run's `notes-for-osint.md` entry is a plain `[FYI]`.

## Stages 2–4 — not yet run

- **Stage 2 — the stage 4 read.** Pending Bill's hand-carry of `new-queue/SWZ/` into
  `OSINT\new\`, `update wiki`, and the mirror refresh.
- **Stage 3 — the mapping.** `outputs/reports/SWZ/indicators.csv` rewritten by hand against
  `documentation/indicator-mapping-conventions.md`.
- **Stage 4 — the render.**

**Yield is stated when stage 3 lands**, as gaps closed against the 78 probed and against
sessions spent.
