---
type: procedure
reader: cc
title: adding-an-indicator.md — how an indicator is added to, or retired from, the frame
last_reviewed: 2026-09-22
status: in force from the maturity assessment build; first used for indicator-digital-sovereignty.md and indicator-financial-sustainability.md
---

# Adding an indicator to the frame

*(The frame is `lookups/indicators.csv`; `archived/maturity-assessment.md` is what reads it. This is the generic procedure — everything that has to be true of a new indicator before the assessment can carry it; a specific addition answers each numbered section for one indicator, §11.)*

## 0. Whether to add it at all

**The test: does it change what the assessment can say?** An indicator earns a row if it asks a question no existing row asks, if the base holds or can plausibly collect evidence for more than a handful of countries, and if a norm — continental for preference — exists to assess it against. A question the status report answers better in prose is not an indicator. A relationship (a partnership, an agreement, a donor) is not a position and is not an indicator.

**Prefer a measure where one can be defined**: an instrument or system indicator that could have been a measure with a figure of record is the weaker choice.

**One indicator, one question.** An indicator that would need two ladders is two indicators. Where the answer is a composite (readiness, sovereignty, sustainability), the rubric says which part decides the stage, and the specific document shows that a single ladder holds.

## 1. The subject

**An indicator hangs off a taxonomy Level-2 subject, and the subject must exist.** `indicators_lib.frame()` joins `Topic L2` to `lookups/taxonomy.csv`; an unknown subject breaks the render. The vocabulary is **OSINT's** (`lookups/taxonomy.md`, what sources are tagged against). `lookups/taxonomy.csv` is Corpus's display copy — order, Level-1 group, label — and gains the row only once the mirror shows the subject.

So a new indicator either sits under an existing subject — preferred, a Corpus-only change — or needs a new subject, an OSINT change: `scripts/osint-patch.py prepare`, add the slug to `lookups/taxonomy.md` (and to `lookups/report-region-sections.csv`) in the clone, `cut`, deliver to `prepared/` on the share, and write the `[ACT]` note asking OSINT to apply it; the note names the slug's concept page as OSINT's to mint, since a patch may not carry wiki prose. **Nothing in the frame is minted until the mirror shows the subject.** Tagging sources with it is a sweep brief on Bill's call, never a Corpus-side write.

## 2. The id

**`{subject-slug}--{slug-of-full-indicator-text}`, minted mechanically, never composed by hand, never reissued, never renamed** (`progress-report-redesign.md` §2, carried into the assessment). The slug is the indicator's full text lower-cased with every run of non-alphanumerics collapsed to one hyphen, leading and trailing hyphens dropped: *P2P, P2G and P2B functionality* → `p2p-p2g-and-p2b-functionality`. A sort number is never part of an id. Check `indicators_lib.ids()` for a collision before writing the row; on a collision the text changes, not the id rule.

## 3. The frame row

One row in `lookups/indicators.csv`, hand-edited, with every column the file already has — `indicator_id, Topic Sort, Indicator Sort, Topic L1, Topic, Topic L2, Progress indicator` — plus the two the assessment adds: `kind` (`instrument | system | measure`) and `assessed` (`1`, or `0` for a row kept for its id and its mapped rows but not staged). `Topic Sort` is the subject's taxonomy sort order and `Indicator Sort` its position within the subject — display order only, so an insertion renumbers only what follows it within the subject. `Progress indicator` is the display text, named so because the scripts read it.

**The frame count must not be hard-coded in logic.** After any frame change, `grep -rn` scripts for the old count and fix every docstring, description and comment stating it; `scripts/test_indicators.py` and `lint-indicators-draft.py` read the file, not the number.

## 4. The norm

One row in `lookups/maturity-norms.csv` (and, until that is cut, one row in `archived/maturity-assessment-norms.md` §3 with a note under the table): the anchoring instrument found by the register's rule — AU organ instrument → continental agency or alliance → REC → global → Corpus-defined — with the adopting body, date, status, the provision that bears on the indicator, what it fixes (top · rungs · target), the reference that carries a number the anchor lacks, and the URL checked on the day. **A Corpus-defined row says what was searched.** A norm's vintage is frozen at the instrument as adopted.

## 5. The rubric

Five rows in `lookups/maturity-rubric.csv`, one per stage, each an *anchor* — what evidence satisfies that stage for this indicator — and each marked `interpolated` where the norm does not itself state the rung. The generic scale is `archived/maturity-assessment.md` §3; the family is set by `kind` (§4 there). For a measure the rubric also states the value's definition and unit, the reference dataset and year, the target where the norm has one, and otherwise the Africa-only quintile cut and the year it was cut; and it restates the precedence rule — Corpus's own cited figure over the global dataset's (`archived/maturity-assessment-norms.md` §7).

## 6. The status outline

`documentation/status-outline.md` carries, per subject, the question the section answers and the DPI variable ids that answer it, with `[PROPOSED]` marking an indicator not yet collected. A new indicator gets a bullet under its subject naming any DPI variables that bear on it, or the statement that none does and the section is answered from the wiki — so the status report and the assessment ask the same question, as the soft agreement check in `archived/maturity-assessment.md` §9 relies on.

## 7. The mapping pass

**Fifty-four ledgers, one new question.** The mapping conventions (`indicator-mapping-conventions.md`) hold unchanged: the indicator a row belongs to is chosen by what the row is; one row may map to several indicators where it answers several, with different prose in each; placeholder *Not held* rows with no source are not mapped. Most new indicators find their first evidence in rows already mapped elsewhere, so the pass re-reads mapped rows against the new rubric before reading anything new. A country with nothing mappable is *No evidence*, and the coverage byproduct (`outputs/reports/indicator-coverage.csv`) then shows the gap for sweep targeting.

**Watch `considered.txt`** (`considered-not-carried.md`): a source marked considered and mapped nowhere may become mappable under a new indicator, so the pass re-reads the considered list for the subject, not only the ledger.

## 8. Snapshots

**A new indicator enters the history at the baseline, not at the month it was added.** It is assessed retrospectively for every month-end the history already holds — as at each date, from rows dated on or before it — so the country grid has no ragged edge and the first stage is a position, not a movement. The retrospective rows go into the existing editions' successors, never into an edition already cut: an indicator added in November has July–October rows in the history file (flagged `added`) and appears in the November edition onward. The flag is `added`, not `reassessed`, so the movement note never reports an addition as a change.

## 9. Checks, methodology, changelog

The frame checks in `archived/maturity-assessment.md` §11 must pass: a norms row and five rubric rows for the new id, `kind` set, the published counts (Corpus-defined norms, interpolated rungs, indicators assessed) updated on the methodology page. **A reader can notice a new indicator, so the addition gets a `content/changelog.md` entry** in the same commit — what was added and what it means for the reader — under the day's heading.

## 10. Retiring an indicator

**An id is never deleted and never reused.** Retirement is `assessed = 0` in the frame row and a `retired` date in a column added for the purpose; the row stays, its mapped rows stay, its history rows stay, and the renderers stop staging it from the retirement date. The reason goes in the commit body and, if readers could notice, the changelog. The mapped rows are kept for any indicator that replaces it.

## 11. The specific document

A specific addition answers §§0–10 for one indicator in `documentation/indicator-{slug}.md`: the question, the subject and whether it exists, the id, the frame row, the norm row, the five rubric anchors, the status-outline bullet, the evidence and how much the base holds, and the build steps in order with who does each. It makes the addition a task CC can pick up without a conversation.
