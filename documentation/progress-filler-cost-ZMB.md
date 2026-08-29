# Progress filler — throughput record, ZMB, 2026-08-29

*(Run against Zambia — no prior ZMB run, so §0's skip found nothing to carry forward. Batch
label `progress-filler-ZMB-2026-08-29`. Run CSV: `logs/progress-filler/ZMB-2026-08-29.csv`,
with the selected and unselected registers beside it.)*

## The headline

**65 of 65 gaps had evidence to find. Zero nils.** The largest frame this series has run.

## Incident: one slice's context overflow, recovered without re-fetching

**`batch6_dpi_c_capacity_tech` (9 indicators) failed mid-run** — the harness reported "Prompt
is too long" (an infrastructure-side context-window overflow, not a defect in the work itself)
after the sub-agent had completed 7 of its 9 indicators (all six `dpi.registry` indicators plus
`tech.ai--use-of-ai-in-sectoral-management-information-systems`) and started an eighth. Unlike
the NAM incident, **no files were lost** — the per-slice isolated staging folder held all 18
already-written files intact.

**Recovery was mechanical, not a re-run**: every one of the 18 staged files carried its own
complete `note:` field stating exactly which indicator, brief and rank it had been selected
for (per the standing template), so the parent reconstructed `selected.csv` for those 7
indicators directly from the files' own frontmatter — no guessing, no re-fetching. Throughput
counters (`candidates_returned`, `fetched`, `not_selected`, `dropped`) for those 7 rows are
left blank in the run CSV rather than invented, since they were never durably recorded before
the failure; `selected.csv` — the file the merge audit actually checks — is complete and
accurate. A fresh sub-agent (`batch6b_capacity_remainder`) then finished the remaining 2
`capacity.training` indicators cleanly in a separate isolated folder.

**Lesson recorded**: a slice's own `note:` field carrying its full selection rationale is a
cheap insurance policy against exactly this failure mode — worth keeping as standing practice
regardless of slice size.

## Stage 1 — the sweep (complete)

| | |
|---|---|
| Gaps worked | 65 of 65 (no skips — no prior ZMB run) |
| `agent_run` calls | 130 recorded — 2 per gap for the six clean-reporting slices; batch6's 7 reconstructed rows carry no call count of their own |
| Candidates returned | 572 (recorded rows only) |
| Fetched | 173 (recorded rows only) |
| Dropped | 13 — `already-seen` 5, `DUP-EXACT` 3, `inadmissible-origin` 2, `url-dead` 1 (recorded rows only) |
| Held back by the cap | 102, recorded with URLs in the unselected register (recorded rows only) |
| **Staged after the cap** | **184 selections — 65 baseline + 119 progress**, over **146 distinct files**, filed as 54 in `ZMB/baseline/` and 92 in `ZMB/progress/` |
| Sessions | one (seven parallel sub-agents plus one targeted remediation sub-agent for the interrupted slice, one parent merge) |

## Slicing and cross-slice dedup

**Seven slices, grouped by Level-1 with Governance and DPI each split, plus a remediation
eighth**: Governance A (policy/discourse, 9), Governance B (legislate/protect/regional/
standards, 9), ICT Infrastructure + Digitalisation (11), DPI Data Exchange/Identity (9), DPI
Payments/Sectoral MIS (7), DPI Registries + Technology + Capacity (9, split 7+2 across the
incident), Inclusion + Data + Geopolitics (11).

**Twelve cross-slice URL duplicates, 15 loser files retired at merge**, found using
host-normalized URL comparison (stripping `www.` and scheme) from the start this time, a
practice adopted after MWI's post-commit correction. Baseline kept over progress per §5 in
every folder-crossing case; same-folder ties resolved to the fuller verbatim capture. One
six-way consolidation (a Zambia National Spatial Data Infrastructure policy/geoportal launch
article, independently captured under three filenames by three different slices, together
answering six indicators) landed on the copy already carrying the most selections. Two
filename collisions at consolidation (the Electronic Government Act 2021, the National
Registration Act 1964 — both legitimately cited by two different slices) were safely renamed
rather than overwritten.

**`scripts/lint-staged-queue.py` reports clean after four false-positive findings were
investigated and cleared** — one `CROSSED` flag between two long-PDF-extraction files with
unrelated content, and three `SUSPECT` flags on ordinary news/government-notice articles whose
body prose doesn't restate the headline verbatim. No file needed changing.

## Capture quality, declared

- **106 of 146 are `body_completeness: full`, 40 `excerpt`** — flagged, not retried, per
  `capture-rule.md`.
- **127 of 146 carry `date_source: source`, 19 `proxy`.** Precision is `day` on 128, `month`
  on 11, `year` on 7.

## Origin adjudications — none

**Zero new watch/drop rows** across all eight sub-agent runs (seven original slices plus the
remediation slice). `progress-filler-drop-list.csv` is unchanged. This run's `notes-for-osint.md`
entry is a plain `[FYI]`, and names the incident.

## Stages 2–4 — not yet run

- **Stage 2 — the stage 4 read.** Pending Bill's hand-carry of `new-queue/ZMB/` into
  `OSINT\new\`, `update wiki`, and the mirror refresh.
- **Stage 3 — the mapping.** `outputs/reports/ZMB/indicators.csv` rewritten by hand against
  `documentation/indicator-mapping-conventions.md`.
- **Stage 4 — the render.**

**Yield is stated when stage 3 lands**, as gaps closed against the 65 probed and against
sessions spent.
