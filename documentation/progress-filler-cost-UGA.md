# Progress filler — throughput record, UGA, 2026-08-29

*(Run against Uganda — no prior UGA run, so §0's skip found nothing to carry forward. Batch
label `progress-filler-UGA-2026-08-29`. Run CSV: `logs/progress-filler/UGA-2026-08-29.csv`,
with the selected and unselected registers beside it.)*

## The headline

**60 of 60 gaps had evidence to find. Zero nils.** The first fully clean run in this series —
no data loss, no self-forking, no mid-run API failure — under the mature design that NAM, ZWE
and ZMB each forced a change into: isolated per-slice staging, a standing bar on sub-agents
spawning sub-agents, and a `note:` field on every staged file complete enough to reconstruct
the run from disk alone if a slice failed.

## Stage 1 — the sweep (complete)

| | |
|---|---|
| Gaps worked | 60 of 60 (no skips — no prior UGA run) |
| `agent_run` calls | 120 — 2 per gap across six clean-reporting slices |
| Candidates returned | 562 |
| Fetched | 179 |
| Dropped | 15 — `already-seen` 11, `fetch-blocked` 1, `url-dead` 1 (3 unaccounted against the 15 total, see below) |
| Held back by the cap | 100, recorded with URLs in the unselected register |
| **Staged after the cap** | **177 selections — 60 baseline + 117 progress**, over **166 distinct files** before merge, filed as 59 in `UGA/baseline/` and 107 in `UGA/progress/` |
| Sessions | one (six parallel sub-agents, one parent merge) |

*(The drop-code tally above sums to 13 against a `dropped` total of 15; the remaining 2 are
duplicate-in-run drops recorded without a code string in two slices' `run.csv` rows — a
cosmetic gap in this run's own bookkeeping, not a loss of any file or selection. Left as
observed rather than corrected after the fact, per the standing rule against rewriting a run's
own record post-hoc.)*

## Slicing and cross-slice dedup

**Six slices, by Level-1 topic**: Governance A (policy/discourse), Governance B
(legislate/protect/regional/standards) plus Infrastructure, DPI A (identity/exchange), DPI B
(registries/payments), Digital + Capacity + Technology + Inclusion, Data + Geopolitics. All six
completed cleanly with zero indicators skipped or reassigned — the first run in the series with
no batch requiring a remediation slice.

**Twelve cross-slice URL duplicates, 14 loser files retired at merge (166 → 152 files)**, found
using host-normalized URL comparison (stripping `www.` and scheme), standing practice since
MWI/ZMB. Ten pairs and two three-way groups. Resolution followed §5 in order: two groups
resolved on raw selection count where one capture served three or four indicator-selections
against the other's one (the UNESCO AI-readiness validation article, the NITA-U FY2025–26 to
FY2029–30 strategic plan); the rest tied on selection count and were resolved to the fuller
verbatim capture, five of them 3-way or baseline-vs-progress splits merging every named
indicator's topic onto the survivor.

**One group carries a genuine date conflict, left unresolved for ingest**: two captures of
NITA-U's 2022 National IT Survey PDF (`demo.nita.go.ug`) disagree on `published` — one states
2022-01-01 (the survey's own stated year), the other 2024-09-01 (apparently the file's hosting/
re-upload date on the demo subdomain). The fuller capture (150,003 chars vs 3,264, both
`excerpt`) survived and carries a note stating the conflict rather than picking a date.

**Two consolidation-stage filename collisions, safely renamed rather than overwritten**
(`mglsd-launch-national-single-registry`, `newvision-govt-rolls-out-new-emis-rules`, each
suffixed with the losing batch's tag) — one later turned out to be a genuine duplicate URL and
was merged away at dedup; the other's collision partner carried a materially different URL
(a different `NV_...` article-ID suffix) and was correctly left as a distinct file.

**`scripts/lint-staged-queue.py` reports clean after eight false-positive findings were
investigated and cleared**: one `CROSSED` flag between a ministerial op-ed and an unrelated
policy-vision PDF sharing only generic vocabulary; four `SUSPECT` flags on ordinary news
articles whose lede doesn't restate the headline verbatim; three `DATE` flags (filename vs.
`published:` off by one to eighteen days) fixed by renaming the file to the frontmatter's own
established date, never the reverse, with `selected.csv` updated to match. The merge's own
newline-loss bug (documented in every prior country's record) hit 8 of the 12 survivor files
this run — the standard post-merge fix was applied and re-verified by full YAML round-trip
across all 152 remaining files.

## Capture quality, declared

- **105 of 152 are `body_completeness: full`, 47 `excerpt`** — flagged, not retried, per
  `capture-rule.md`.
- **132 of 152 carry `date_source: source`, 20 `proxy`.** Precision is `day` on 125, `month`
  on 18, `year` on 9.

## Origin adjudications — none

**Zero `inadmissible-origin` drops** across all six slices — every drop this run was
`already-seen`, `fetch-blocked`, or `url-dead`. This run's `notes-for-osint.md` entry is a
plain `[FYI]`.

## Stages 2–4 — not yet run

- **Stage 2 — the stage 4 read.** Pending Bill's hand-carry of `new-queue/UGA/` into
  `OSINT\new\`, `update wiki`, and the mirror refresh.
- **Stage 3 — the mapping.** `outputs/reports/UGA/indicators.csv` rewritten by hand against
  `documentation/indicator-mapping-conventions.md`.
- **Stage 4 — the render.**

**Yield is stated when stage 3 lands**, as gaps closed against the 60 probed and against
sessions spent.
