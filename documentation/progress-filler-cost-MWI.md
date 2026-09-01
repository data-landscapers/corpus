# Progress filler — throughput record, MWI, 2026-08-29

*(Run against Malawi — no prior MWI run, so §0's skip found nothing to carry forward. Batch
label `progress-filler-MWI-2026-08-29`. Run CSV: `logs/progress-filler/MWI-2026-08-29.csv`,
with the selected and unselected registers beside it.)*

## The headline

**56 of 56 gaps had evidence to find. Zero nils.** The cleanest run in the per-slice-isolation
era of this series: all six slices reported no incident, no self-forking, no cross-agent
interference of any kind.

## Stage 1 — the sweep (complete)

| | |
|---|---|
| Gaps worked | 56 of 56 (no skips — no prior MWI run) |
| `agent_run` calls | 112 — 2 per gap, `effort: medium` |
| Candidates returned | 516 |
| Fetched | 157 |
| Dropped | 25 — `already-seen` 9, `duplicate-raw` 6, `inadmissible-origin` 3, `off-topic` 2 |
| Held back by the cap | 133, recorded with URLs in the unselected register |
| **Staged after the cap** | **160 selections — 56 baseline + 104 progress**, over **117 distinct files**, filed as 39 in `MWI/baseline/` and 78 in `MWI/progress/` |
| Sessions | one (six parallel sub-agents, each in its own isolated staging folder; one parent merge) |

## Slicing and cross-slice dedup

**Six slices, grouped by Level-1**: Governance A (policy/legislate, 10), Governance B + ICT
Infrastructure (11), DPI Data Exchange/Identity/Payments (10), DPI Registries/Sectoral MIS +
Digitalisation-rural (9), Capacity + Inclusion + Technology (9), Data + Geopolitics (7).

**Nineteen cross-slice URL duplicates, 20 loser files retired at merge** — the largest count
this series has seen, reflecting Malawi's evidence base being both dense and heavily
cross-cutting (the DMAP — Digital Malawi Acceleration Project — implementation-status
documents alone answer indicators across four different slices). Baseline kept over progress
per §5 in every folder-crossing case; same-folder ties resolved to the fuller verbatim capture.
One three-way duplicate (the UNDP IDT4M Annual Report 2025, independently captured by three
different slices under three filenames) consolidated onto the copy already carrying the most
selections.

**Four filename collisions at consolidation**, all safely renamed rather than overwritten
(the Malawi Data Protection Act 2024, the Digital Readiness Assessment, the OGP National
Action Plan, and the NSO strategic-plan article were each independently staged by two slices
under the identical auto-generated filename) — the per-slice isolation design converts what
would have been silent data loss in the old shared-folder design into a visible, safely-handled
rename.

**One duplicate the first merge pass missed, caught in a post-commit re-check**: the parent's
URL-dedup script compared exact URL strings and missed a pair that differed only by a `www.`
host prefix (`finance.gov.mw` vs `www.finance.gov.mw`) for the identical 2026-27 Budget Policy
Statement PDF. Found by re-running the dedup with host normalization after the batch was
already committed, merged in a follow-up commit before hand-carry. Worth carrying the
normalization forward into future runs' first pass.
rename.

**`scripts/lint-staged-queue.py` reports clean after one genuine fix**: an ASCII-transliterated
title (`Aide Memoire`) was restored to the source's own accented spelling (`Aide Mémoire`) from
a line in the document's own body. Three further findings — a `CROSSED` flag between two
long-PDF-extraction files with unrelated content, a `MISFILED` flag on a court judgment whose
frontmatter `url:` (the HTML page) legitimately differs from its body's own embedded PDF
download URL, and a `SUSPECT` flag on an ordinary news article — were investigated and
confirmed as false positives; no file needed changing.

## Capture quality, declared

- **87 of 118 are `body_completeness: full`, 31 `excerpt`** — flagged, not retried, per
  `capture-rule.md`.
- **107 of 118 carry `date_source: source`, 11 `proxy`.** Precision is `day` on 94, `month`
  on 23, `year` on 1.

## Origin adjudications — none

**Zero new watch/drop rows** across all six sub-agent runs. `progress-filler-drop-list.csv` is
unchanged. This run's `notes-for-osint.md` entry is a plain `[FYI]`.

## Stages 2–4 — not yet run

- **Stage 2 — the stage 4 read.** Pending Bill's hand-carry of `new-queue/MWI/` into
  `OSINT\new\`, `update wiki`, and the mirror refresh.
- **Stage 3 — the mapping.** `outputs/reports/MWI/indicators.csv` rewritten by hand against
  `documentation/indicator-mapping-conventions.md`.
- **Stage 4 — the render.**

**Yield is stated when stage 3 lands**, as gaps closed against the 56 probed and against
sessions spent.

## Stages 2 to 4 — the read, the mapping and the render (complete)

**One sitting, 2026-09-01, roughly 55 minutes of wall time, no sub-agents**, run as a `CYCLE.md`
run straight after the COM cycle: BUILD stages 0 to 7 in 25 minutes, RENDER behind it.

| | |
|---|---|
| Sources reaching stage 4 | 111 of the 160 staged selections, after ingest dedup and re-slugging |
| Gaps closed | 51 of 51 still open at stage 4 — **Malawi answers all 121 frame indicators**, up from 70 |
| Still *No evidence* | none |
| Ledger | 198 rows to **246**; 48 rows minted, 28 moved, 14 *Not held* rows settled |
| *Not held* rows | 53 to **39** |
| Baseline statements corrected | 4 — the 2016 cyber security Act was listed as unadopted while its own text is now held; the baseline recorded no national open data portal against one launched September 2025; it recorded no government use of earth-observation data against two documented uses; and the Gulf and India sections said no engagement existed against five memoranda and a payments demonstration |
| Documents rewritten | monthly (five empty blocks written, trimmed into band) and the authored status baseline, revised in fourteen passages |
| Sessions | one, unbroken from stage 2 to deployment |

## Yield against the four stages

**51 gaps closed for one sweep session and one mapping session, and the frame closes completely.**
Malawi is the second country in the series to answer every indicator. The mapping half was again
where the editorial risk sat: all four corrections above were found there, three of them in the
authored status baseline, which is the document a reader is most likely to take at face value and
the one no check can test for truth.

**The base did most of the work.** MWI arrived at stage 4 with 198 ledger rows against COM's 120,
so more than a third of the new mappings resolved onto rows that already existed — five indicators
already held were revised rather than written, and fourteen *Not held* rows were settled from
their own texts rather than from new evidence. A thick ledger makes a filler cheaper to land,
which is the opposite of the intuition that a thin country is the easy one.

**One defect the pass found and fixed in passing**: the Digital Readiness Assessment is held twice,
as the print and web editions of one report, and the mapping pass would have double-cited it
across four indicators. Corpus now cites the full capture throughout; note 94 records it.
