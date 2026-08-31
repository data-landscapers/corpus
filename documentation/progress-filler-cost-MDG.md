# Progress filler — throughput record, MDG, 2026-08-31

*(Run against Madagascar — no prior MDG run, so §0's skip found nothing to carry forward.
Batch label `progress-filler-MDG-2026-08-31`. Run CSV: `logs/progress-filler/MDG-2026-08-31.csv`,
with the selected and unselected registers beside it.)*

## The headline

**77 of 77 gaps had evidence to find. Zero nils** — 76 fully staged, 1 partial (a baseline with
no distinct progress movement inside the window).

## Stage 1 — the sweep (complete)

| | |
|---|---|
| Gaps worked | 77 of 77 (no skips — no prior MDG run) |
| `agent_run` calls | 154 — 2 per gap, `effort: medium` |
| Candidates returned | 601 |
| Fetched | 243 |
| Dropped | 70 — `already-seen` the large majority (cross-batch and against-mirror duplicates), plus `off-topic`, `fetch-failed`, `duplicate-event`, one `inadmissible-origin` |
| Held back by the cap | 322, recorded with URLs in the unselected register |
| **Staged after the cap** | **213 selections — 77 baseline + 136 progress**, consolidating to **180 distinct files** (64 in `MDG/baseline/`, 116 in `MDG/progress/`) after cross-batch dedup |
| Sessions | one (seven parallel sub-agents, one parent merge — no remediation needed) |

## Slicing

**Seven slices, grouped by Level-1, merging adjacent small chapters to fill each batch**:
gov.policy + gov.legislate (13); gov.protect + gov.regional + gov.standards + gov.discourse +
finance.budget + finance.mou + infra.connect (11); infra.store + infra.energy + infra.capacity +
dpi.exchange (10); dpi.id + dpi.pay (9); dpi.registry + dpi.mis + dpi.govtech (10);
digital.localgov + digital.rural + tech.ai + tech.industry + tech.innovate + capacity.literacy +
capacity.training (11); include.access + data.statistics + data.satellite + geopol.* (13).

Following the ERI batch-fabrication incident and the ZWE staging-collision incident (both
recorded in this file's prior-run counterparts), each sub-agent staged into its **own private
folder** (`new-queue\MDG\_staging\batchN\{baseline,progress}\`) that no sibling could reach, was
explicitly barred from spawning any child agent, and was required to reconcile its own claimed
files against the actual filesystem before reporting. **All seven ran clean — no collision, no
fabrication, no anomaly requiring remediation.** The parent (this session) did not trust any
sub-agent's self-reported tally at face value regardless: every batch's file count was
independently recounted from disk before the merge proceeded.

## Cross-batch dedup — the actual finding

**Isolating each slice's fetches prevents collisions, but not seven slices independently
rediscovering the same real-world document.** Twenty URLs were staged more than once across
batches — the same law, decree, or news event surfacing as the answer to more than one
indicator, fetched fresh by each batch that found it rather than reused. **29 loser files
retired at merge**, kept the fuller/`full`-over-`excerpt` capture in each group, and — per §5 —
**baseline wins the folder** where a document served as baseline for one indicator and progress
for another: two groups (an HCC decision on Loi 2025-019, and a PRODIGY datacentre tender)
crossed this way, five selection rows were repointed onto a baseline-side survivor as a result,
and the per-indicator `staged_baseline`/`staged_progress` counts in the run CSV are unaffected
because they record what each indicator itself selected, never which folder the consolidated
file happens to live in. All 213 selections reconcile exactly against the run CSV's per-indicator
tallies after that repoint (verified programmatically, zero mismatches).

**One `brief` column normalisation was needed.** Sub-agents wrote the numeric brief index
(`1`/`2`) into the `brief` field rather than the `baseline`/`progress` label the schema elsewhere
uses (ZWE, DJI, COM). The parent normalised every merged row's `brief` from that row's own
original staging folder (its per-indicator classification, independent of where consolidation
ultimately filed the survivor) before the final CSV was written. Future batch prompts should
give an explicit example row to avoid this drift.

## Staging-queue lint

`scripts/lint-staged-queue.py` over the consolidated two folders found **11 real defects**,
all fixed:

- **2 YAML parse failures** — an unquoted `publisher:` value containing `": "` inside a
  parenthetical (`(mirror: africa-laws.org...)`, `(...underlying source: ITU...)`). Quoted, not
  refetched.
- **5 date-precision mismatches** — filename date disagreed with the frontmatter's own
  `published:` (the value actually established from the fetched page). Renamed to match
  `published:` in every case, per `capture-rule.md`.

**4 further `TITLE` findings were investigated and left unchanged** — each is the guard case
PROGRESS-FILLER.md §5 names explicitly (an all-caps PDF/CMS cover heading that is itself
unaccented in the source, or an English proper noun the linter's accent heuristic mismatched
against unrelated French prose elsewhere in the body): BIANCO's own `RAPPORT D'ACTIVITES 2024`
cover, UGD's own unaccented all-caps page heading, a stylised-bold-Unicode "Madagascar" in a
social post (not an accent difference), and "Indian Ocean AI Summit" — a genuine English event
name, flagged only because the body's unrelated French prose says "l'océan Indien" elsewhere.
Re-titling any of these would have replaced the source's own orthography with an invented one.

## Origin adjudications — one

**`globaltenders.com`** — subscription-gated tender aggregator, `drop`, surfaced as a route to
an RSU IT-equipment tender for `dpi.exchange--interoperability-of-social-protection-systems`;
not staged from. Appended to `progress-filler-drop-list.csv`; this run's `notes-for-osint.md`
entry is `[ACT]`, asking OSINT to promote the row into `logs/drop-list.csv`.

## Capture quality, declared

Completeness and date-source breakdowns are recorded per-file in the staged frontmatter; several
long official PDFs (multi-hundred-article laws, 40-120 page strategies and audits) were staged
as `body_completeness: excerpt` with a note on where the fetch's character cap cut off, per
`capture-rule.md`'s truncation rule — flagged, not retried.

## Stages 2–4 — not yet run

- **Stage 2 — the stage 4 read.** Pending Bill's hand-carry of `new-queue/MDG/` (64 baseline +
  116 progress files, undelivered) into `OSINT\new\`, `update wiki`, and the mirror refresh.
- **Stage 3 — the mapping.** `outputs/reports/MDG/indicators.csv` rewritten by hand against
  `documentation/indicator-mapping-conventions.md`.
- **Stage 4 — the render.**

**Yield is stated when stage 3 lands**, as gaps closed against the 77 probed and against
sessions spent.
