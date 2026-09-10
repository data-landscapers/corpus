---
type: documentation
title: Considered and not carried — 467 false No-evidence rows
opened: 2026-09-10
---

# Considered and not carried

**467 of the 698 ***No evidence*** rows in the country progress reports are false.** The
base holds a document on the indicator, in the window, correctly tagged; stage 4 read it
and marked it considered; it left no trace in the ledger, the indicator frame or the
status baseline; and the report then states that the base holds nothing on that indicator
at all.

Found 2026-09-10 from Bill's read of `/progress/`, published that morning, which put the
six progress counts on one page for the first time. Benin's 50 *No evidence* against
Togo's 0 is what showed it.

## The worked example

`digital.localgov--ict-infrastructure-for-local-government` reads ***No evidence*** in
`BEN-progress.md`. The base holds
`raw/2025/2025-10-02-numerique-gouv-bj-e-communes-lancement.md`:

    published: 2025-10-02          # inside the window, 2025-09-01 to 2026-09-09
    places: [BEN]
    topics: [digital.localgov]     # the indicator's own subject
    ingested: 2026-09-03
    sweep_batch: progress-filler-BEN-2026-08-28
    note: '…Benin's e-Communes platform is operationally live, providing the ICT
           backbone for online municipal services piloted in three communes ahead
           of a planned national rollout across all 77 communes.'

Its slug is in `outputs/reports/BEN/considered.txt`. It is cited by no row of
`ledger.csv`, mapped in no row of `indicators.csv`, and named nowhere in `BEN-status.md`.
It was read and it left no trace anywhere.

## The cause — corrected 2026-09-10

**The first account written here said a run had marked a batch and died before minting the
rows. That is wrong and the correction matters, because it changes the repair.**

The run is identifiable: `96110c3`, 2026-09-04, *"BEN: 128 sources read, the statutory
base minted and the India gap settled"*. It did not die. It read 128 sources, minted
twelve ledger rows (114 → 126), mapped thirteen indicators (59 → 70), revised two
baseline sub-sections, and marked the remaining 106 slugs considered — **which is exactly
what `BUILD.md` stage 4 step 2 tells it to do**:

> *default: nothing moves* — most sources report activity, not movement. Do **not** attach
> a slug to a row that did not move.

So the marks are not the residue of a crash. They are the correct output of the rule, and
the rule is wrong for this cohort.

**The filler documents are not news and stage 4 read them as news.** They were selected
*because* an indicator had no evidence, and the filler's own manifest classifies each one
`baseline` or `progress` in its `brief` column. Stage 4 has no baseline outcome that mints
a row: its four outcomes are *moves a row*, *mints a row* (a named system or instrument
the ledger lacks), *settles a Not-held row*, and *nothing moves*. A document establishing
that a system exists and is live, where the base held no position at all, is not a
movement — so it falls to the default and disappears. For Benin:

| | selected | considered | cited by a ledger row |
|---|---|---|---|
| `brief: baseline` | 63 | 37 | 22 |
| `brief: progress` | 111 | 84 | 4 |

**And the mark is what makes it permanent.** Stage 4 reads "only the sources the ledger has
not yet considered — a set difference over slugs", and `BUILD.md` step 200 states the
consequence: *"an item already considered is never reopened."* `report-scan.py --json`
reports **zero unconsidered sources across all 54 units**: as far as the build is
concerned there is nothing left to read, and there never will be.

**Nothing downstream can see it.** Checks G, I, J, L and M test the frame against the
ledger, and `report-render.py`'s check I asserts *No evidence* iff no row maps to the
indicator — true here, which is why it passes. The frame is consistent with a ledger that
is missing the evidence, and consistency with the ledger is the only property anything
tests.

## Two smaller losses found alongside it

Both are Benin's numbers; neither has been measured estate-wide.

- **25 of the 174 documents the filler staged for Benin are not in `raw/` at all.** They
  were staged and never ingested. That is upstream of everything here.
- **28 are in `raw/` and in no unit's considered list**, while `report-scan` reports
  nothing unconsidered — so the unit's scope does not see them. Most likely their
  `places:` does not carry `BEN`.

## The scale

| | |
|---|---|
| *No evidence* rows in the 54 country reports | 698 |
| of those, a document exists, was considered, was never carried | **467** |
| documents involved | 860 |
| countries affected | 22 |
| countries carrying 84% of it | COG, CPV, BEN, BFA, ERI, GIN, GAB, COD, CMR |

Reproduce from `lookups/indicators.csv`, each unit's `{ISO}-progress.md`,
`considered.txt` and `ledger.csv`, and `logs/progress-filler/*-selected.csv`. For each
unit: take the indicators the report calls *No evidence*; take the filler-selected
documents naming those indicators; keep the ones whose slug is in `considered.txt` and in
no ledger row's `sources`. The manifests carry two header shapes — `staged_file` on three
units, `file` on the rest.

## What the repair is

**Un-marking alone is not enough.** Putting the 860 slugs back into stage 4's set
difference sends them through the same rule that discarded them the first time, and it
will discard them again. The repair has two halves and the second is the one that matters:

1. **The rule.** Stage 4 needs a fifth outcome, or an explicit widening of *mints a row*:
   **a source that establishes a standing position where the ledger holds none mints a
   row, with `movement: Baseline not held`.** That vocabulary value already exists and
   already means exactly this. The row test in `report-layer.md` §1 is the text to change,
   and `BUILD.md` stage 4 step 2 the procedure.
2. **The re-read.** Un-mark the affected slugs and run stage 4 over them under the
   corrected rule. 860 sources over 22 units, each needing a decision and a mapping row
   where it mints.

Both are reversible; the marks are a Corpus-owned file and the documents are untouched in
`raw/`.

## What would have caught it

Nothing existing, and the check is one query needing no model: **a slug marked considered,
whose indicator the report calls *No evidence*, and which is cited by no ledger row.**
Today it returns 467. Run at the end of stage 4 per unit, it would have refused
`96110c3` and every run like it. It is worth more than the nightly per-country review
under discussion, because it makes this class of failure impossible rather than findable
eight weeks later.
