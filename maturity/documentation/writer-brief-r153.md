---
reader: cc
type: brief
title: writer-brief-r153.md — the maturity paragraph, one an indicator
opened: 2026-11-26
status: draft; R162 makes it `writer-brief.md` in the commit that switches the writers, and edits it once on Bill's R155 line
---

# The maturity paragraph

This brief sets how a maturity cell is written for a country. Bill ruled the shape on 26 November 2026 (R153). `calibration-zaf-governance.md` beside it holds 29 paragraphs written to it by hand. Read the prose sheet, `X:\documentation\prose-style.md`, last, just before drafting.

## The shape

Each indicator gets one paragraph of 60 to 110 words under its stage. It has three parts, in this order.

1. **What exists, dated and linked.** Open on the instrument, body or system, with its date and a link. Name it in full the first time. Say who did what, and when.
2. **What changed in the last twelve months.** Give each change with its date and link. A change states the dated position it changed from, under the sheet's no-history rule. Where nothing changed, write *No change has been found in the last twelve months.* A source in the window that only cites the instrument is not a change. Write *it was cited and not changed*, and link the citation.
3. **What has not been found, said as what the next stage would need.** Name what was looked for and not found. Close on one sentence in the form *{Next stage} would need {the next rung's test, in plain words}*.

At stage 5 there is no next stage. Close on the open question from `gaps`, if there is one, or on the latest dated fact. A cell with no stage opens on *No stage is set.* Its close says what the second rung would need.

## Where the facts come from

Take every fact and every link from the cell's current page, `outputs/maturity/{study}/{ISO3}.md`. Take the stage and `gaps` from `assessment.csv`, the changes from `history.csv`, and the next rung from the indicator's ladder. Add no fact that is not on file. Leave a fact out rather than rewording it beyond what its source says.

Choose facts in this order: the instrument or body, its date of force or issue, the strongest fact the current stage rests on, and the changes in the window. Leave the rest to the fold.

## What leaves the paragraph

- **The labels.** *Standing*, *Text*, *Period* and the rest stay in the CSV and in the evidence fold.
- ***Also on file***. It moves into the fold.
- **Repeated facts.** Each fact goes in once. An instrument that serves two indicators is named in both, each time with its own date.
- **The ledger.** Do not write *the cell moved*, *re-placed* or *rescored*. Write about the country.

## Words

- Use the site's stage names: Absent, Preparing, Establishing, Operating, Mature.
- Write *has been found* for an absence. Write *has been published* only where a source shows publication.
- Do not use a verdict, a mood word or a set-up contrast. The test is the sheet's: could a reader check the sentence against the link?
- Aim for sentences of about 16 words. None may run over 40.

## The check

`lint-prose.py --file` passes the chapter. Each paragraph is 60 to 110 words. Every sentence that states a fact carries a link, or follows a linked sentence about the same source. The closing sentence names the next stage.
