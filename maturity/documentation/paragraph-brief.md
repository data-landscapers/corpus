---
reader: cc
type: brief
title: paragraph-brief.md — the maturity paragraph, one an indicator
opened: 2026-11-26
status: in force from R162 (strategic review 8); edited once on Bill's R155 line
---

# The maturity paragraph

Bill ruled the shape on 26 November 2026 (R153). **He raised the length to 60 to 130 words the same day, when R162 ran.** `calibration-zaf-governance.md` beside this file holds 29 paragraphs written to the shape by hand. The labelled evidence, written under `writer-brief.md`, sits in a fold below it. Read the prose sheet, `X:\documentation\prose-style.md`, last.

## What you are given

`scripts/maturity-paragraph.py packet` gives one JSON file per study. Each cell carries the country, the indicator, the stage, the next stage's test, the moves of the last twelve months, `gaps`, and `section`. The section is the cell's evidence page, with every fact and link you may use. Write `{ "ISO3|indicator_id": "paragraph", ... }` for every cell to `{study}.out.json` beside it. `maturity-paragraph.py apply` keeps what passes.

## The shape

The paragraph is one block of 60 to 130 words with no line breaks. It has three parts, in this order.

1. **What exists, dated and linked.** Open on the instrument, body or system, with its date and a link. Name it in full the first time. Say who did what, and when.
2. **What changed in the last twelve months.** Give each change with its date and link. A change states the dated position it changed from, under the sheet's no-history rule. Where nothing changed, write *No change has been found in the last twelve months.* A source in the window that only cites the instrument is not a change: write *it was cited and not changed*. The words *twelve months* appear in every paragraph.
3. **What has not been found, said as what the next stage would need.** Name what was looked for and not found. End on one sentence of the form *{Next stage} would need {the test in `next`, in plain words}*, naming the next stage.

At stage 5 there is no next stage. End on the open question in `gaps`, or on the latest dated fact. An unplaced cell opens on *No stage is set.* It ends on what the lowest stage in `next` that the facts come nearest to would need.

## Where the facts come from

Use only the section's facts and links, copied exactly as `[words](<url>)`. Add no fact and no link that is not there, and nothing you know of the country. Leave a fact out rather than say more than the section does. `changes` tells you which moves fall in the window; its notes are the ledger's, so do not quote them.

Choose the instrument or body, its date, the strongest fact the stage rests on, and the window's changes. Leave the rest to the fold.

## What stays out

- The labels, such as *Standing* or *Text*, and the *Also on file* list. They stay in the fold.
- The ledger. Do not write *the cell moved*, *re-placed* or *rescored*. Write about the country.
- Verdicts, mood words and set-up contrasts. Could a reader check the sentence against the link?

## Words

- Use the stage names Absent, Preparing, Establishing, Operating and Mature.
- Write *has been found* for an absence. Write *has been published* only where a source shows publication.
- Aim for sentences of about 16 words. Keep the mean under 20, and no sentence over 40.

## What `apply` refuses

It refuses a paragraph outside 60 to 130 words, or one that fails `lint-prose.py`'s numbers or words. It also refuses one with a link the section does not carry, one without *twelve months*, and one whose last sentence does not name the next stage with *would need*.
