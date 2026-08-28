# Progress filler — throughput record, RWA, 2026-08-28

*(The ninth run of `PROGRESS-FILLER.md`, the largest frame yet (52 gaps) and the first at
five concurrent slices. No prior RWA run, so §0's skip found nothing to carry forward. Batch
label `progress-filler-RWA-2026-08-28`. Run CSV: `logs/progress-filler/RWA-2026-08-28.csv`,
with the selected and unselected registers beside it.)*

## The headline

**51 of 52 gaps had evidence to find. One nil**: `dpi.registry--address-register` — genuinely
not evidenced as a standalone Rwandan register, distinct from the domicile fields carried
inside the population/SDID system. 136 selections over 101 distinct files, 2.62 per gap —
lower than KEN's 2.96, mostly because this run's five-slice split produced far heavier
cross-slice overlap (Rwanda's NIDA/RISA/RRA digital-government ecosystem is unusually
interconnected — see below) and one genuine 0-baseline outcome
(`tech.ai--use-of-ai-in-government-administration`, whose baseline candidate was already held
in `raw/` unmapped, correctly left unstaged per the dedup rule rather than restaged).

## Stage 1 — the sweep (complete)

| | |
|---|---|
| Gaps worked | 52 of 52 (no skips — no prior RWA run) |
| `agent_run` calls | 104 — 2 per gap, `effort: medium` |
| Candidates returned | 400 |
| Fetched | 149 |
| Dropped | 2 — `already-seen` 1, `headline-only-stub` 1 |
| Held back by the cap | 90, recorded with URLs in the unselected register |
| **Staged after the cap** | **136 selections — 50 baseline + 86 progress — over 101 distinct files**, filed as 39 in `RWA/baseline/` and 62 in `RWA/progress/` |
| Batch size on disk | ~3.6 MB |
| Sessions | one |

**Distribution**: 38 indicators at the full 1+2, 8 at 1+1, 4 at 1+0, 1 at 0+2 (see above), 1
nil.

## Five slices — the largest split this series has run, and it shows

**Grouped by Level-1 with small chapters merged**: Governance (11), ICT
Infrastructure+Digitalisation+Technology (11), DPI data-exchange/ID/payments (12), DPI
registries/sectoral-MIS (10), Inclusion+Data (8).

**Five cross-slice URL duplicates, all caught and resolved at merge** — the highest count of
the series, concentrated exactly where the frame said to expect it: Rwanda's DPI/governance
layer is tightly cross-referenced, so several strategy documents and one ministerial order
were independently found and staged by two (in one case three) different slices before the
merge could catch them:

- The Governance and Decentralisation Sector Strategic Plan 2024–2029 — staged **three times**
  under three filenames by three different slices (`digital.localgov`'s baseline,
  `gov.discourse`'s baseline, `include.access--citizen-participation-in-policy`'s baseline).
  Kept the one `full` capture (270 KB) over the two `excerpt` captures (255 KB and 7 KB), and
  merged `topics:`/`note:` to carry all three indicators' rationale.
- The Education Sector Strategic Plan (ESSP) 2024–2029 — staged twice (`dpi.exchange`'s
  baseline at 154 KB `excerpt`, `dpi.mis--education`'s baseline at 5 KB `excerpt`). Kept the
  fuller capture.
- The VAT Ministerial Order (29 April 2026) — staged twice under different filenames
  (`gov.legislate--e-commerce-legislation`'s progress pick, and a document already merged
  across three DPI indicators by the sub-agent that found it first). Kept the fuller,
  already-multiply-annotated capture and repointed the fourth indicator onto it.
- The e-Title electronic land registration launch — staged twice, both `full`
  (`digital.localgov`'s progress pick at 6.6 KB, `dpi.mis--land`'s progress pick at 3.2 KB).
  Kept the larger.
- RISA's national PKI procurement RFP — staged twice, both `excerpt`
  (`dpi.id--authentication`'s progress pick at 154 KB, `infra.capacity`'s progress pick at
  103 KB). Kept the larger.

**Fifteen further files legitimately serve two or more indicators each** (not duplicates —
one document, several indicators, staged once) — the densest multi-indicator sharing this
series has produced, led by a single RISA shared-government-data-hub market-engagement notice
answering six indicators across governance and DPI, and Law 029/2023 on population
registration (SDID) answering five DPI identity indicators.

**One transient false alarm, self-resolved.** Batch B's mid-run lint pass flagged what looked
like a crossed body on `2012-03-12-rwanda-ict-procurement-ministerial-instructions-2012.md`
(a sibling slice's file, mid-write at the moment batch B happened to check it). By the time
every slice had finished, the file's frontmatter and body matched correctly — a race-condition
read, not a defect, and the final `lint-staged-queue.py` pass over the merged queue confirms
clean.

**One accounting defect, caught and fixed at merge.** The DPI data-exchange/ID/payments slice
recorded `not_selected: 0` in its own run-CSV row for all 12 of its indicators despite writing
89 real rows to its own unselected register — a summary-column miscount, not a missing
register. Corrected against the register (the authoritative source) before merging; the run
CSV's `not_selected` total moved from 64 to 90 to match.

**One procedural deviation, left as-is.** The infra/digitalisation slice committed and pushed
its own 26-file sub-slice to the xfer share mid-run (`ed1066d`), ahead of the parent's merge
audit — PROGRESS-FILLER.md §6/§8 reserve the commit to the parent. No harm resulted; the
parent's final commit completed the batch and folded in the merge fixes, two of which touched
files already in that early commit.

**`scripts/lint-staged-queue.py` reports clean** over both folders (101 files) after the
merge. 136 selections resolve to exactly 101 files on disk, verified programmatically: zero
rows pointing at a missing file, zero orphan files, zero cap violations, zero duplicate URLs
remaining.

## Capture quality, declared

- **77 of 101 are `body_completeness: full`, 24 `excerpt`** — flagged, not retried, per
  `capture-rule.md`.
- **89 of 101 carry `date_source: source`, 12 `proxy`.** Precision is `day` on 80, `month` on
  16, `year` on 5.
- **The three largest files**: Law No. 011/2026 on Competition and Consumer Protection
  (273 KB), the merged Governance and Decentralisation Sector Strategic Plan (264 KB), and the
  draft law governing the National Bank of Rwanda (219 KB).
- No mojibake (`�`) found in a scan of all 101 staged bodies.

## Origin adjudications — none

**Zero new watch/drop rows.** All five slices reported every candidate domain as either
already-known or novel-and-informational; `progress-filler-drop-list.csv` is unchanged — still
8 rows across five earlier countries. This run's `notes-for-osint.md` entry is a plain
`[FYI]`.

## Stages 2–4 — not yet run

- **Stage 2 — the stage 4 read.** Pending Bill's hand-carry of `new-queue/RWA/` into
  `OSINT\new\`, `update wiki`, and the mirror refresh.
- **Stage 3 — the mapping.** `outputs/reports/RWA/indicators.csv` rewritten by hand against
  `documentation/indicator-mapping-conventions.md`.
- **Stage 4 — the render.**

**Yield is stated when stage 3 lands**, as gaps closed against the 52 probed and against
sessions spent.

## What this says about scheduling

**A 50+-gap frame is worth splitting five ways, but the split needs subject-clustering
awareness, not just Level-1 grouping.** Every one of this run's five duplicate clusters sits
inside Rwanda's own tightly integrated DPI/governance layer (RISA, NIDA, SDID, RRA) — exactly
the risk BFA's cost record flagged and recommended addressing by telling concurrent slices
which other subjects are running alongside them. This run's slice prompts did carry that
warning for the two DPI slices (C and D) but not for the governance/infra/inclusion slices (A,
B, E), where four of the five duplicates actually originated. The lesson holds across runs:
warn every slice, not just the ones an L1 grouping makes look obviously adjacent.
