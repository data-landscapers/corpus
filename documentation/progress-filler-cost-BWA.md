# Progress filler — throughput record, BWA, 2026-08-28

*(The thirteenth run of `PROGRESS-FILLER.md`, the largest frame yet (69 gaps) and the first
at six concurrent slices. No prior BWA run, so §0's skip found nothing to carry forward.
Batch label `progress-filler-BWA-2026-08-28`. Run CSV: `logs/progress-filler/BWA-2026-08-28.csv`,
with the selected register beside it — the unselected register is a header-only stub this run;
see below.)*

## The headline

**69 of 69 gaps had evidence to find. Zero nils** — the second run running to close a
60+-gap frame with none (after TZA). 68 indicators got a baseline; one
(`dpi.mis--education`) closed at 0 baseline + 1 progress because `gov.bw` was unreachable
throughout the slice's run, blocking every candidate that would have served as its baseline
(confirmed dead across the DoH check, per `capture-rule.md`, not just the system resolver).
177 selections over 118 distinct files, 2.57 per gap — lower density than the last several
runs, consistent with the frame's unusually wide topic spread (six slices, several
single-indicator chapters) rather than a coverage problem.

## Stage 1 — the sweep (complete)

| | |
|---|---|
| Gaps worked | 69 of 69 (no skips — no prior BWA run) |
| `agent_run` calls | 138 — 2 per gap, `effort: medium` |
| Candidates returned | 459 |
| Fetched | 182 |
| Dropped | 43 |
| Held back by the cap | 108 (count only — see the data-loss note below; the register itself did not survive this run) |
| **Staged after the cap** | **177 selections — 68 baseline + 107 progress — over 118 distinct files**, filed as 53 in `BWA/baseline/` and 65 in `BWA/progress/` |
| Batch size on disk | ~1.1 MB |
| Sessions | one |

## A defect in this run's own tooling — the unselected register was lost, not just miscounted

**The parent's merge script deleted six batch CSVs before the merge that needed them had
actually completed.** The Python merge routine crashed partway through reading the six
unselected-register batch files (a malformed row — likely an unquoted comma in a `why_not`
field, the same class of defect NGA's batch B produced earlier in this series) before it ever
opened its output file. The next shell command in the same block was an unconditional
`rm -f` cleanup of all three CSV kinds (run, selected, unselected) across all six batches,
which ran regardless of the merge's exit status. The run-CSV and selected-register merges had
already completed and their batch files were correctly cleaned up; the unselected merge had
not, and its six source files were deleted anyway.

**What this actually costs**: nothing evidentiary. Every staged source file, every selection,
the full cap audit and cross-slice dedup all completed and were verified independently before
this happened — 177 selections resolve to exactly 118 files on disk, zero missing, zero
orphans, zero cap violations, zero duplicate URLs. The `not_selected` counts survive in the
run CSV (108 candidates were cap-excluded across the run) because those were written per-batch
before the crash. What is gone is the *detail* — the 108 rows of URL/title/publisher naming
which specific candidates lost to the cap, which `PROGRESS-FILLER.md` §4a keeps precisely so a
later cap-widening decision costs no new `agent_run` calls. That saving is gone for BWA only:
widening the cap on any BWA indicator later means re-searching, not re-reading a register.
`BWA-2026-08-28-unselected.csv` is committed as a header-only file, honestly documenting the
loss rather than a plausible-looking empty register.

**Fix applied for future runs**: never chain a cleanup command after a multi-step Python merge
in the same shell block without checking the merge's exit status first. The three merges
should run as three independent, individually-verified steps, each confirmed against its
expected row count before its source files are removed — exactly the discipline already
applied to the run-CSV and selected-register merges in every prior run of this series, which
is why only the unselected merge was exposed to this failure mode.

## Six slices, and the merge-additively instruction working under real load

**Grouped in ~11-13-indicator chunks**: gov.policy+gov.legislate (13),
gov.protect/regional/standards/discourse+finance+infra (13), DPI exchange/ID/payments (12),
DPI registries/MIS (12), digitalisation+technology (10), inclusion/data/geopolitics (9). Every
slice carried the explicit merge-additively instruction and the TZA precedent (both prior
overwrites in that run were self-corrected by the affected sub-agent).

**This run pushed the instruction hardest yet, and it held.** Six concurrent slices searching
Botswana's comparatively small, tightly-drafted 2025 Digital Services Act and a handful of
2026 Committee-of-Supply budget speeches produced an unusually high rate of independent
re-discovery of the same handful of foundational documents — the Digital Services Act alone
was independently staged by **five separate slices** before consolidation, and the 2026 Budget
Speech, the Digital Delta data-centre launch article, and three separate ministries'
Committee-of-Supply speeches were each independently staged two to three times. **Every one of
these was caught and merged additively by the sub-agents themselves, mid-run, before the
parent's audit ever saw them** — batches A, B, C, D and E all report doing this consolidation
work on their own initiative, going beyond "merge when you notice a collision" to actively
grep-checking the shared queue after every write and repairing collisions they found. The
result is **21 files that legitimately answer between two and twelve indicators each** — the
Digital Services Act alone now answers twelve — which is the densest multi-indicator sharing
this series has produced by a wide margin, and none of it required parent intervention.

**The parent audit still found real work**: 5 selected-register rows named files that had been
renamed during a sub-agent's own consolidation without the row being repointed (a bookkeeping
lag behind a correct content-level merge, not a content defect), and one further true
duplicate (a World Bank HEPRR project press release, staged twice under different titles by
two different slices) had not been caught by anyone. All six fixed at the parent audit;
`scripts/lint-staged-queue.py` reports clean over both folders (118 files, save for one
already-verified false positive — see below) after the merge.

**One `lint-staged-queue.py` CROSSED finding, independently verified false**: a Botswana
Administration of Justice court-reforms page (`2022-08-05-aoj-reforms-and-developments.md`)
scored a structural title-token match against an unrelated ministerial speech purely because
both titles are generic ("Reforms and Developments" / a Committee-of-Supply speech). Two
sub-agents and the parent all independently read the file's actual body against its own
`url:`/`title:` and confirmed it is exactly what it claims to be — Botswana's Court Records
Management System and Judicial Case Management reform, correctly staged as
`dpi.mis--justice`'s baseline.

## Two origin-screen adjudications — `[ACT]`

`botswanayouth.com` (generated-content site, no primary cited) and `tenderimpulse.com`
(third-party tender-notice aggregator) both adjudicated `drop`, surfacing as the sole route to
a training workshop report and a procurement notice respectively; neither staged from. Two
rows appended to `progress-filler-drop-list.csv` — 12 rows now, across seven countries. This
run's `notes-for-osint.md` entry is `[ACT]`.

## Capture quality, declared

- **73 of 118 are `body_completeness: full`, 42 `excerpt`, 3 `paywalled`** — flagged, not
  retried, per `capture-rule.md`.
- **113 of 118 carry `date_source: source`, 4 `proxy`.** Precision is `day` on 94, `month` on
  15, `year` on 9.
- **The three largest files**: the Data Protection Act 2024 (117 KB), the Digital Services Act
  2025 (41 KB, now answering twelve indicators), and the Ministry of Health Committee of
  Supply speech (35 KB).
- No mojibake (`�`) found in a scan of all 118 staged bodies.

## Stages 2–4 — not yet run

- **Stage 2 — the stage 4 read.** Pending Bill's hand-carry of `new-queue/BWA/` into
  `OSINT\new\`, `update wiki`, and the mirror refresh.
- **Stage 3 — the mapping.** `outputs/reports/BWA/indicators.csv` rewritten by hand against
  `documentation/indicator-mapping-conventions.md`.
- **Stage 4 — the render.**

**Yield is stated when stage 3 lands**, as gaps closed against the 69 probed and against
sessions spent.
