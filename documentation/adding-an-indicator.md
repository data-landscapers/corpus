---
type: procedure
title: adding-an-indicator.md — how an indicator is added to, or retired from, the frame
last_reviewed: 2026-09-22
status: in force from the maturity assessment build; first used for indicator-digital-sovereignty.md and indicator-financial-sustainability.md
---

# Adding an indicator to the frame

*(Written 2026-09-22 in Cowork at Bill's request, alongside the two additions it was written for. The frame is `lookups/indicators.csv`; `maturity-assessment.md` is what reads it. This is the generic procedure — everything that has to be true of a new indicator before the assessment can carry it — and a specific addition is a short document that answers each numbered section below for one indicator, then hands the list to CC.)*

## 0. Whether to add it at all

**The test is the wiki's own: does it change what the assessment can say?** An indicator earns a row if it asks a question no existing row asks, if the base holds or can plausibly collect evidence that answers it for more than a handful of countries, and if a norm exists — continental for preference — to assess it against. A question the status report answers better in prose is not an indicator. A relationship (a partnership, an agreement, a donor) is not a position and is not an indicator: that is why the five `geopol.*` rows and `finance.mou` left the assessment on 2026-09-22.

**Prefer a measure where one can be defined.** Measures are the assessment's distinguishing column; an instrument or system indicator that could have been a measure with a figure of record is the weaker choice.

**One indicator, one question.** An indicator that would need two ladders is two indicators. Where the answer is a composite (readiness, sovereignty, sustainability), the rubric has to say which of its parts decides the stage, and the specific document has to show that a single ladder holds.

## 1. The subject

**An indicator hangs off a taxonomy Level-2 subject, and the subject must exist.** `indicators_lib.frame()` joins `Topic L2` to `lookups/taxonomy.csv` for the chapter and the display order; an unknown subject breaks the render. The taxonomy is **OSINT's vocabulary**, not Corpus's: the compile-stage workroot junctions `lookups/` to OSINT's `lookups/`, and the file lives there.

So a new indicator either sits under an existing subject — preferred, because it is a Corpus-only change — or needs a new subject, which is an OSINT change: `scripts/osint-patch.py prepare`, add the row to `lookups/taxonomy.csv` in the clone (sort order, key, Level 1, Level 2 label), `cut`, deliver to `prepared/` on the share, and wait for OSINT to apply it. `lookups/` is inside the set a patch may carry. If the wiki's `taxonomy.md` is not in that set, a `[ACT]` note in `notes-for-osint.md` asks OSINT to add the slug there in the same job, with an `Affects:` line naming the indicator. **Nothing in the frame is minted until the mirror shows the subject.** Sources will need the new tag before the coverage byproduct can find anything for it; that is a sweep brief on Bill's call, never a Corpus-side write.

## 2. The id

**`{subject-slug}--{slug-of-full-indicator-text}`, minted mechanically, never composed by hand, never reissued, never renamed** (`progress-report-redesign.md` §2, carried into the assessment). The slug is the indicator's full text lower-cased with every run of non-alphanumerics collapsed to one hyphen, leading and trailing hyphens dropped: *Data storage / cloud strategy* → `data-storage-cloud-strategy`; *P2P, P2G and P2B functionality* → `p2p-p2g-and-p2b-functionality`; *DT-related training in secondary education* → `dt-related-training-in-secondary-education`. A sort number is never part of an id. Check `indicators_lib.ids()` for a collision before writing the row; a collision means the text is not distinct enough, and the text changes, not the id rule.

## 3. The frame row

One row in `lookups/indicators.csv`, hand-edited, with every column the file already has — `indicator_id, Topic Sort, Indicator Sort, Topic L1, Topic, Topic L2, Progress indicator` — plus the two the assessment adds: `kind` (`instrument | system | measure`) and `assessed` (`1`, or `0` for a row kept for its id and its mapped rows but not staged). `Topic Sort` is the subject's taxonomy sort order and `Indicator Sort` its position within the subject — display order only, so an insertion renumbers what follows it within the subject and nothing else. The `Progress indicator` column keeps its name for now because the scripts read it; it is the indicator's display text.

**The frame count is stated in prose in several scripts and must not be hard-coded in logic.** After any frame change: `grep -rn "121" scripts/` (or whatever the count was) and fix every docstring, description and comment that states it; `scripts/test_indicators.py` and `lint-indicators-draft.py` read the file rather than the number, and should stay that way.

## 4. The norm

One row in `lookups/maturity-norms.csv` (and, until that is cut, one row in `maturity-assessment-norms.md` §3 with a note under the table): the anchoring instrument found by the register's rule — AU organ instrument → continental agency or alliance → REC → global → Corpus-defined — with the adopting body, date, status, the provision that bears on the indicator, what it fixes (top · rungs · target), the reference that carries a number the anchor lacks, and the URL checked on the day. **A Corpus-defined row says what was searched.** A norm's vintage is frozen at the instrument as adopted.

## 5. The rubric

Five rows in `lookups/maturity-rubric.csv`, one per stage, each an *anchor* — what evidence satisfies that stage for this indicator — and each marked `interpolated` where the norm does not itself state the rung. The generic scale is `maturity-assessment.md` §3; the family is set by `kind` (§4 there). For a measure the rubric also states the value's definition and unit, the reference dataset and year, the target where the norm has one, and otherwise the Africa-only quintile cut and the year it was cut; and it restates the precedence rule — Corpus's own cited figure over the global dataset's (`maturity-assessment-norms.md` §7).

## 6. The status outline

`documentation/status-outline.md` carries, per subject, the question the section answers and the DPI variable ids that answer it, with `[PROPOSED]` marking an indicator not yet collected. A new indicator gets a bullet under its subject naming any DPI variables that bear on it, or the statement that none does and the section is answered from the wiki. This keeps the status report and the assessment asking the same question of the same subject, which is what the soft agreement check in `maturity-assessment.md` §9 relies on.

## 7. The mapping pass

**Fifty-four ledgers, one new question.** The mapping conventions (`indicator-mapping-conventions.md`) hold unchanged: the indicator a row belongs to is chosen by what the row is; one row may map to several indicators where it answers several, with different prose in each; placeholder *Not held* rows with no source are not mapped. Most new indicators find their first evidence in rows already mapped elsewhere — the sovereignty indicator's is the 260 `geopol.*` rows — so the pass is a re-read of mapped rows against the new rubric before it is a read of anything new. A country with nothing mappable is *No evidence*, which is the cheap and correct answer, and the coverage byproduct (`outputs/reports/indicator-coverage.csv`) then shows the gap for sweep targeting.

**Watch `considered.txt`.** `considered-not-carried.md` records the failure this pass can repeat: a source read and marked considered, mapped nowhere, and the report then stating the base holds nothing. A new indicator is exactly the case where a previously considered source becomes mappable; the pass re-reads the considered list for the subject, not only the ledger.

## 8. Snapshots

**A new indicator enters the history at the baseline, not at the month it was added.** It is assessed retrospectively for every month-end the history already holds — as at each date, from rows dated on or before it — so the country grid has no ragged edge and the first stage is a position, not a movement. The retrospective rows are written into the existing editions' successors, never into an edition already cut: the edition rule holds, so an indicator added in November has July–October rows in the history file (flagged `added`) and appears in the November edition onward. `reassessed` is not used for this; `added` is its own flag so that the movement note never reports an addition as a change.

## 9. Checks, methodology, changelog

The frame checks in `maturity-assessment.md` §11 must pass: a norms row and five rubric rows for the new id, `kind` set, the published counts (Corpus-defined norms, interpolated rungs, indicators assessed) updated on the methodology page. **A reader can notice a new indicator, so the addition gets a `content/changelog.md` entry** in the same commit — what was added and what it means for the reader — under the day's heading.

## 10. Retiring an indicator

**An id is never deleted and never reused.** Retirement is `assessed = 0` in the frame row and a `retired` date in a column added for the purpose; the row stays, its mapped rows stay, its history rows stay, and the renderers stop staging it from the retirement date. The reason goes in the commit body and, if a reader could notice, in the changelog. A retired indicator's mapped rows remain available to any indicator that replaces it, which is the whole reason the rows are kept.

## 11. The specific document

A specific addition answers §§0–10 for one indicator in a document named `indicator-{slug}.md` in `documentation/`: the question, the subject and whether it exists, the id, the frame row, the norm row, the five rubric anchors, the status-outline bullet, where the evidence will come from and how much of it the base already holds, and the build steps in order with who does each. It is short, because the procedure is here; its job is to make the addition a task CC can pick up without a conversation.
