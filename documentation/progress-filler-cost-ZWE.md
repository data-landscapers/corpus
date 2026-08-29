# Progress filler — throughput record, ZWE, 2026-08-29

*(Run against Zimbabwe — no prior ZWE run, so §0's skip found nothing to carry forward. Batch
label `progress-filler-ZWE-2026-08-29`. Run CSV: `logs/progress-filler/ZWE-2026-08-29.csv`,
with the selected and unselected registers beside it.)*

## The headline

**57 of 57 gaps had evidence to find. Zero nils.**

## Staging-architecture change, and how it performed

**This run switched from a shared staging folder to per-slice isolation**, following the prior
NAM run's incident (four of six slices' captures lost from a shared `new-queue\NAM\` when
several parallel writers touched it at once, cause never conclusively identified). Each of this
run's sub-agents wrote into its own private `new-queue\ZWE\_staging\batchN\{baseline,progress}\`
that no sibling could reach; the parent consolidated into the canonical two-folder shape only
after every slice finished.

**Five of six original slices ran clean with no incident whatsoever** — the isolation held.

**One slice (`batch5_tech_capacity_incl`) spawned an internal fork by mistake, and the fork
independently duplicated fetch/staging work into the same private folder** (private per-slice,
not per-agent — the design didn't anticipate a slice spawning a child of itself). The slice's
own agent detected the anomaly mid-run by directly checking the filesystem rather than trusting
its own memory of what it had written, stopped rather than compound the confusion, and reported
precisely which files were its own (verified against its own `selected.csv`) versus unclaimed.
**No data was lost and nothing needed re-fetching**: the slice's own bookkeeping was internally
consistent for the 2 of 10 indicators it had completed, so the 5 unclaimed orphan files (the
fork's redundant captures of the same real-world events, under near-duplicate filenames) were
simply excluded from consolidation. A second, fresh sub-agent — explicitly barred from spawning
any child agent — completed the remaining 8 indicators cleanly as `batch5b_remainder`.

**Lesson for next time, recorded rather than acted on**: an isolated staging folder per slice
prevents cross-slice collisions, but not a slice's own accidental self-duplication via a spawned
child. The fix that actually worked here was the sub-agent's own discipline — verifying its
claimed files against its own CSV rather than trusting the folder listing at face value — not
the isolation design itself. Future slice prompts should explicitly bar spawning any child
agent, as this run's remedial `batch5b_remainder` prompt did.

## Stage 1 — the sweep (complete)

| | |
|---|---|
| Gaps worked | 57 of 57 (no skips — no prior ZWE run) |
| `agent_run` calls | 114 — 2 per gap, `effort: medium` |
| Candidates returned | 481 |
| Fetched | 183 |
| Dropped | 28 — `already-seen` 16, `url-dead` 3, `fetch-blocked` 2, `off-topic` 2, `inadmissible-origin` 1 |
| Held back by the cap | 117, recorded with URLs in the unselected register |
| **Staged after the cap** | **160 selections — 57 baseline + 103 progress**, over **140 distinct files**, filed as 50 in `ZWE/baseline/` and 90 in `ZWE/progress/` |
| Sessions | one (six parallel sub-agents plus one targeted remediation sub-agent, one parent merge) |

## Slicing and cross-slice dedup

**Six slices, grouped by Level-1 with Governance and DPI each split into two**: Governance A
(policy/legislate, 10), Governance B + ICT Infrastructure (11), DPI Exchange/Identity/Payments +
Digitalisation (10), DPI Registries + Sectoral MIS (11), Technology + Capacity + Inclusion (10,
split 2+8 across the fork incident), Data + Geopolitics (5).

**Twelve cross-slice URL duplicates, 15 loser files retired at merge.** Baseline kept over
progress per §5 in the folder-crossing cases; same-folder ties broken on fuller capture. **Three
date conflicts recorded rather than silently resolved**, per §6: the Cyber and Data Protection
Act (2021 vs 2022 captures of the identical URL), the National Statistics Development Strategy
III (one capture read the plan's nominal 2021 period, the other the PDF's own filename-embedded
finalisation date of 25 January 2024 — the more likely correct one, but not asserted as such),
and the National Registration Act (1976 original enactment vs a 2016 consolidated-chapter
reprint of the identical zimlii.org URL, both true of the instrument at different points).

**`scripts/lint-staged-queue.py` reports clean on both folders after three date-precision
corrections**: three files' filenames disagreed with their own `published:` field (a Census and
Statistics Act misdated by 13 years, and two off-by-days-or-months cases) — renamed to match
the frontmatter's own stated date, which is the value actually established from the fetched
page per `capture-rule.md`.

## Capture quality, declared

- **111 of 140 are `body_completeness: full`, 28 `excerpt`, 1 `paywalled`** — flagged, not
  retried, per `capture-rule.md`.
- **125 of 140 carry `date_source: source`, 15 `proxy`.** Precision is `day` on 116, `month`
  on 13, `year` on 11.

## Origin adjudications — none

**Zero new watch/drop rows** across all seven sub-agent runs (six original slices plus the
remediation slice). `progress-filler-drop-list.csv` is unchanged. This run's `notes-for-osint.md`
entry is a plain `[FYI]`.

## Stages 2–4 — not yet run

- **Stage 2 — the stage 4 read.** Pending Bill's hand-carry of `new-queue/ZWE/` into
  `OSINT\new\`, `update wiki`, and the mirror refresh.
- **Stage 3 — the mapping.** `outputs/reports/ZWE/indicators.csv` rewritten by hand against
  `documentation/indicator-mapping-conventions.md`.
- **Stage 4 — the render.**

**Yield is stated when stage 3 lands**, as gaps closed against the 57 probed and against
sessions spent.
