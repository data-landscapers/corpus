---
type: documentation
title: Considered and not carried — 467 false No-evidence rows
opened: 2026-09-10
---

# Considered and not carried

**467 of the 698 ***No evidence*** rows in the country progress reports are false.** The
base holds a document on the indicator, in the window, correctly tagged; the document was
read by stage 4 and marked considered; no ledger row was minted; and the report then
states that the base holds nothing on that indicator at all.

Found 2026-09-10 from Bill's read of `/progress/`, which was published that morning and
puts the six progress counts on one page for the first time. Benin's 50 *No evidence*
against Togo's 0 is what showed it. Nothing before that page put the numbers where the
outlier was visible.

## What the reports say and what the base holds

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

The slug is in `outputs/reports/BEN/considered.txt`. It is in no row of
`outputs/reports/BEN/ledger.csv`. It is in no row of `indicators.csv`. The published
sentence for that indicator is the renderer's boilerplate for an empty frame row.

That is one of 105 such documents for Benin, covering 48 of its 50 empty indicators.

## The mechanism, and why nothing caught it

`BUILD.md` → *Stage 4* step 4 marks every slug read, **moved or not**, and stage 4 reads
"only the sources the ledger has not yet considered — a set difference over slugs". Step
200 of the same file states the consequence plainly: **"an item already considered is
never reopened."**

So a mark is irreversible in effect. A run that marks a batch and then stops before
minting the rows for it does not lose the documents from the base — it loses them from
every future report, permanently, because the next run computes the same set difference
and skips them. `BUILD.md` line 19 names the danger in its own words: *"The danger is the
interruption going unnoticed — a half-moved build typesets cleanly and passes every
check."*

**Every check in step 6 tests internal consistency and none tests this.** G tests that
links resolve, I the vocabulary, J that no document was compiled before its ledger moved,
L that no narrative block is unwritten, M that every stated position cites a resolving
source. `report-render.py`'s own check I asserts *No evidence* iff no row maps to the
indicator — which is true here, and is exactly why the check passes. **The frame is
consistent with a ledger that is missing the evidence.** Consistency with the ledger is
the only property anything downstream tests, and it is preserved by the failure.

## Why it is a stopped run and not a judgement

Bill's first guess on seeing Benin was that a build ran out of tokens mid-run, and that is
what the evidence supports.

- **It is not a per-indicator fault.** The most-affected indicator is empty in 19 of 54
  countries; no indicator is empty in more than 20. There is no broken question.
- **It is not spread evenly.** 22 countries are affected and nine carry 84% of it: COG 54,
  CPV 49, BEN 48, BFA 46, ERI 43, GIN 42, GAB 41, COD 36, CMR 33. Thirty-two countries
  have none. That is the shape of a few runs dying, not of a standing rule misapplied.
- **The gaps are scattered through the indicator frame, not clustered at its tail** — the
  test that first looked like a refutation and is not. Stage 4 iterates **by unit and by
  source slug**, never down the indicator frame, so a run that stops partway loses a
  scattered set of indicators. The tail test was measuring the wrong axis.
- **The yields recorded in `logs/indicator-mapping-progress.md` are pre-filler.** Benin's
  entry reads *"57 from BEN's 105"* on a ledger that now holds 134 rows and an
  `indicators.csv` that now holds 71. Work did continue after the filler ingest of
  2026-09-03; it did not finish, and the marks say it did.

## The scale

| | |
|---|---|
| *No evidence* rows in the 54 country reports | 698 |
| of those, a document exists, was considered, was never carried | **467** |
| documents involved | 860 |
| countries affected | 22 |
| countries carrying 84% of it | COG, CPV, BEN, BFA, ERI, GIN, GAB, COD, CMR |

Reproduce with `scripts/.workroot`-free inputs only — `lookups/indicators.csv`, each
unit's `{ISO}-progress.md`, `considered.txt` and `ledger.csv`, and the filler manifests in
`logs/progress-filler/*-selected.csv`. For each unit: take the indicators the report calls
*No evidence*; take the filler-selected documents naming those indicators; keep the ones
whose slug appears in `considered.txt` and in no row of `ledger.csv`. Note the manifests
carry two header shapes — `staged_file` on three units and `file` on the rest.

## What the fix is

**Un-marking is the whole of it, and it is reversible.** The documents are in `raw/`,
correctly tagged and ingested; the only thing standing between them and the reports is
their presence in `considered.txt`. Striking the 860 slugs from the 22 units' considered
lists puts them back in stage 4's set difference, and the next stage 4 pass over those
units reads them as new.

Two things follow that are not this file's to decide:

- **The pass itself is model authoring and it is not small** — 860 sources over 22 units,
  each needing the four-outcome decision of stage 4 step 2 and a mapping row where it
  moves or mints. That is a scope call.
- **The check that would have caught it does not exist**, and building it is a feature
  under the freeze rather than a defect fix. The shape is one query and it needs no model:
  *a slug marked considered, whose indicator the report calls ***No evidence***, and which
  appears in no ledger row.* Today it returns 467. A version that runs per unit at the end
  of stage 4 would have refused the run that created them.

Until both are settled, `/progress/` and the country progress reports overstate absence,
and the *No evidence* column is the one column on that page that should not be read as
settled.
