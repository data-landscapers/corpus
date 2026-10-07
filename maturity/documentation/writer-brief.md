---
type: brief
reader: cc
title: writer-brief.md — what one writer does with one country of a maturity study
last_reviewed: 2026-10-07
status: first used for maturity study health, task H7
---

# Writer brief: write a country's summaries

*(Method §8 as instructions.)*

## What you are given

A study id `{id}` and a country `{ISO3}`, under `C:\CORPUS`.

1. Read `documentation/AI-speak.md` and `documentation/house-style.md`. They govern every sentence.
2. Read `maturity/{id}/study.json` and the study file it names: the typology, the aspects and the ladders.
3. Read, in `maturity/{id}/evidence/{ISO3}/`: `stage.json`, the staging you write up; `evidence.csv`, the facts; `systems.csv`, the systems named; `readlist.csv`, which gives the `url` of every `slug`.

**Read no source document and use nothing you know of the country.** You do not restage.

## The two rules that outrank the rest

**Every stated fact carries an inline link, on the claim, to the `url` of the evidence row that states it. No link, no claim.** Write every link as `[words](<url>)`, the URL copied exactly from `evidence.csv` or `readlist.csv` inside the angle brackets. A row from a source the study excludes is never cited.

**A borderline fact is stated at a coarser grain the evidence supports, or dropped.** No hedge, no caveat and no word about the evidence goes on the page, except in the *Not held* line. Where two rows disagree and recency does not separate them, state what they agree on. Figures are dated. A country's own name for a system is attributed to it.

## The long summary

**One file**: `outputs/maturity/{id}/{ISO3}.md`. A `# ` heading with the country's name, then one `## ` section per sub-indicator, headed with its label from `study.json`, in the study's order.

**A staged cell takes exactly five paragraphs, one per aspect, in the study's order**, each a single line, each opening with the aspect's `name` from `study.json` in bold followed by a full stop, as `**Tiers in use.**`. Each paragraph carries at least one link. **The five together run 120 to 250 words.** An aspect with nothing held still gets its paragraph: it says what the nearest held fact states, linked, and stops.

- Write what the country has, on that aspect, as the evidence states it. The stage's reasoning is in `stage.json`; use its `gaps` and `note` to choose what matters, and do not quote them.
- A share of all health facilities is given as that, with its year and who says so.
- Do not name the stage, the ladder or the cap in the prose.

**Then two closing paragraphs, each a single line**:

- `***Noted, not assessed***` followed by a full stop and the country's systems of the noted classes, from `systems.csv`: trackers, single-function, community and enabling systems, each named once and linked to its source's URL. Where there are none: *None held.*
- `***Not held***` followed by a full stop and what the evidence does not establish, from `gaps`, in one or two plain sentences. No link is needed here.

**A cell with no stage** (`unplaced` or `no evidence`) takes only the two closing paragraphs under its heading.

## The short summaries

**One file**: `maturity/{id}/evidence/{ISO3}/short.json`, as `{"<sub-indicator key>": "<short>", ...}`, one entry per sub-indicator.

**One line, 25 words at most, no link.** The fact that sets the stage, with its year, then what is not established. Where the stage rests on a share of all health facilities, say so. A cell with no stage says in the same space what is held and why it sets no rung.

## What you may write

**Those two files, with the Write tool. Create no other file, edit none, delete none, and start no agent of your own.**

## When you finish

Reply in two lines: each long summary's word count, and anything the parent must know.
