# Progress filler — throughput record, NAM, 2026-08-29

*(Run against Namibia — no prior NAM run, so §0's skip found nothing to carry forward. Batch
label `progress-filler-NAM-2026-08-29`. Run CSV: `logs/progress-filler/NAM-2026-08-29.csv`,
with the selected and unselected registers beside it.)*

## The headline

**59 of 59 gaps had evidence to find. Zero nils.** But this run carries a real incident, not
just a clean throughput number — see below.

## Incident: mid-run loss of four of six slices' staged work, and how it was recovered

**After all six parallel sub-agents reported completion, the parent's own audit — cross-checking
every batch's `selected.csv` against what actually existed on disk — found that batches 1, 2, 3
and nearly all of batch 4 (39 of 59 indicators' worth of fetched, staged bodies) had vanished
from `new-queue\NAM\`.** Only batches 5 and 6 (20 indicators, 49 files) survived, and their
survival was confirmed by content (every surviving file's `topics:` matched only those two
slices' subjects).

**Cause: not established with certainty.** The shared staging folders (`new-queue\NAM\baseline\`
and `\progress\`) are written concurrently by every parallel sub-agent, and the procedure
depends on each one only ever *creating* new files there, never deleting or bulk-rewriting.
Batch 6's own report flagged, mid-run, that its files had briefly been replaced by an unrelated
set before it "recovered" by rewriting from its own context — in hindsight this was an early
symptom of the same event, not a false alarm. No git history exists for `new-queue\` (it is
untracked, hand-carry-only staging, per the share's own design) and no Recycle Bin or sync
backup held a copy, so the four slices' original captures are **unrecoverable**. The bookkeeping
CSVs in `C:\CORPUS\logs\progress-filler\` — a separate directory from the wiped one — were
untouched throughout and remained the only surviving record of what each lost slice had done.

**Remediation**: batches 1–4 were re-run from scratch as fresh sub-agents, each briefed on the
incident and instructed never to run any delete, move, or bulk-rewrite command against the
shared folders — only ever create their own new files, one at a time. Each rerun verified its
own output was present on disk before reporting done. The parent then independently
cross-checked **every** batch's `selected.csv` against the filesystem a second time before
proceeding — this is now standing practice for every future run, not just a one-off check.
**The recovered run is clean**: 169/169 selections resolve to real files, zero missing, zero
cap violations, zero orphans.

**Cost of the incident**: roughly 40 extra `agent_run` calls and their associated fetch/staging
work — the four reruns' full throughput below is genuinely double-spent against the original
(lost) attempt. This is the number that should inform any future decision about the format of
this staging step (e.g., per-slice subfolders instead of one shared pair of folders, which
would make one slice's failure unable to touch another's files at all).

## Stage 1 — the sweep (complete, post-recovery figures)

| | |
|---|---|
| Gaps worked | 59 of 59 (no skips — no prior NAM run) |
| `agent_run` calls | 118 — 2 per gap, `effort: medium` (excludes the ~40 calls spent on the lost first attempt at batches 1-4) |
| Candidates returned | 538 |
| Fetched | 156 |
| Dropped | 9 — `already-seen` 5, `duplicate-raw` 2, `DUP-EXACT` 1 |
| Held back by the cap | 196, recorded with URLs in the unselected register |
| **Staged after the cap** | **169 selections — 59 baseline + 110 progress**, over **132 distinct files**, filed as 43 in `NAM/baseline/` and 89 in `NAM/progress/` |
| Sessions | one (six parallel sub-agents, a mid-run recovery of four, one parent merge) |

## Slicing and cross-slice dedup

**Six slices, grouped by Level-1 with Governance and DPI each split into two**: Governance A
(policy/legislate, 10), Governance B + Finance + Capacity (10), ICT Infrastructure +
Digitalisation (9), DPI Data Exchange/Identity/Payments + local-government (10), DPI
Registries + Sectoral MIS (11), Rural + Technology + Inclusion + Data (9).

**Seven cross-slice URL duplicates, 7 loser files retired at merge** — smaller than either
Lesotho's or Eswatini's equivalent counts, helped by the reruns' distinctive-filename
instruction. Baseline kept over progress per §5 in the one folder-crossing case (the UNESCO AI
Readiness Assessment report); same-folder duplicates resolved to the fuller capture. One
compilation-gazette case recorded rather than silently merged: Government Gazette No. 8949
carries multiple distinct legal notices under one URL, and the note says so rather than
implying the two sub-agents' different framings were simply redundant.

**`scripts/lint-staged-queue.py` reports five open `SUSPECT` findings, all investigated and
cleared** — ordinary news articles whose body prose doesn't restate the headline verbatim, the
same false-positive shape seen in every run this series. No `CROSSED` or `MISFILED` finding.
One malformed CSV row (unescaped commas across 30-odd `why_not` values in one batch's register,
from long multi-clause rejection reasons) was caught and repaired programmatically before it
could reach the final registers.

## Capture quality, declared

- **83 of 132 are `body_completeness: full`, 39 `excerpt`, 10 `paywalled`** — flagged, not
  retried, per `capture-rule.md`.
- **109 of 132 carry `date_source: source`, 23 `proxy`.** Precision is `day` on 110, `month`
  on 11, `year` on 11.

## Origin adjudications — none

**Zero new watch/drop rows** across all ten sub-agent runs (six original plus four reruns).
`progress-filler-drop-list.csv` is unchanged by this run. This run's `notes-for-osint.md` entry
is a plain `[FYI]`, and names the incident.

## Stages 2–4 — not yet run

- **Stage 2 — the stage 4 read.** Pending Bill's hand-carry of `new-queue/NAM/` into
  `OSINT\new\`, `update wiki`, and the mirror refresh.
- **Stage 3 — the mapping.** `outputs/reports/NAM/indicators.csv` rewritten by hand against
  `documentation/indicator-mapping-conventions.md`.
- **Stage 4 — the render.**

**Yield is stated when stage 3 lands**, as gaps closed against the 59 probed and against
sessions spent — the incident's extra cost included.
