---
type: note
title: The 206 unwritten narrative blocks are four chapters, not forty-seven units
last_reviewed: 2026-08-27
status: live — a work list for successive BUILD runs, not a defect to repair
---

# The check-L backlog is four chapters wide

*(Written 2026-08-26 by the sweep cycle's day-1 build, which cleared 39 blocks across ten units and then measured what was left rather than guessing at it.)*

## What the number actually is

`report-render.py --check` fails L on **206 narrative blocks across 47 of the 57 units**. Read unit by unit that looks like a backlog spread everywhere and owned by nobody. It is not. Broken down it is almost entirely **four chapter keys**:

| key | blocks |
|---|---|
| `capacity` | 60 |
| `data` | 56 |
| `geopolitics` | 48 |
| `digitalisation` | 42 |

and by document, **150 in progress reports and 56 in status reports** — none in a monthly, because a monthly's blocks are per-subject and are minted only when a row in that subject moves, so a run that mints a row writes the block in the same pass.

Nothing else is failing. G, I, J and M are at **0** across all 57 units.

## The cause is the section change of 2026-08-25

`documentation/report-layer.md` §5 records Bill's ruling of that date: **a country report's sections are the taxonomy's ten Level-1 chapters, in `lookups/taxonomy.csv`'s order**, replacing the older grouping. Four of those ten chapters had no counterpart under the previous layout, so every progress report and every ledger-rendered status report in the tree gained four headings at once — each with an empty block under it and no prose that could be carried across, because there was none to carry.

That is why the same four keys appear on unit after unit and why the count is so nearly `4 × 47`. It is one change with 206 consequences, not 206 independent oversights.

**The 56 status-report blocks are the units `STATUS-INIT` has not reached.** An initialised unit's status report is an authored baseline that the renderer no longer rebuilds, so it carries prose and does not appear here; a unit still on the ledger render gained the four headings like everything else. The backlog therefore shrinks from two directions — a run that writes the prose, and initialisation reaching another unit.

## What a run should do about it

**`BUILD.md` → stage 4 step 6 already governs this and does not ask for it to be cleared in one pass**: *"A failing check is work, and BUILD does it in the same pass … What is left after the repair pass goes in the run's log line as a count."* L is authoring work, and the two outcomes under *Narrative integrity* are to write the sentence or remove the section. **Removing the section is not available here** — the chapters are the taxonomy's own and a unit with rows under them has something to say — so every one of the 206 is a paragraph somebody has to write.

The cheap ordering, learned from clearing 39 of them:

1. **Write the progress blocks for a unit while its ledger is open.** The tables above each block carry the resolved links, the two window positions and the movement stem, so the paragraph is a reading of material already on screen. Doing it later means re-opening the unit for nothing else.
2. **A block with one row in it still gets a sentence**, and the truthful sentence is usually about the record rather than the country — *the base carries one row here and no position for it a year ago, so the chapter records a level rather than a movement*. That is evidence-led reporting, not filler.
3. **Watch the word budget.** `report-register-check.py` puts a progress report at 900–1,250 words; four new chapters of prose push a large unit over it. On CIV the blocks were cut twice and the document still finished 229 over, which is the right trade — L is a gate on what is published, the budget is a report on it.

## The count on 2026-08-27: 138, and the second way it shrinks

The build of 2026-08-27 re-measured it and found **138 blocks across 34 of 58 units** — `capacity` 40,
`data` 35, `geopolitics` 33, `digitalisation` 30; **82 in progress reports and 56 in status reports**.

**Sixty-eight of the sixty-eight cleared were cleared by the indicator mapping pass, not by authoring.**
A unit whose `indicators.csv` exists renders its progress report as the indicator frame, which has no
Level-1 chapter headings in it at all, so the four empty blocks stop existing the moment the mapping
pass reaches that unit. That is the third direction the backlog shrinks from and it is much the
cheapest of the three: 26 units mapped so far have taken 104 progress blocks off this list as a side
effect of work being done for another reason. The remaining 82 progress blocks belong to the 28
unmapped units, and the mapping pass will take them the same way.

**Which leaves the 56 status-report blocks as the real authoring debt.** Those are the units
`STATUS-INIT` has not reached, unchanged from the 2026-08-26 measurement because nothing this month
has initialised a unit. A run looking for the cheapest hundred words should not spend them on a
progress block in an unmapped unit — the mapping pass is going to delete that block.

## Why this is a note and not a message to Bill

It is reversible, it is BUILD's own work, and it carries its own solution — the housekeeping bar in `CLAUDE.md` makes that a task rather than a message. What is worth having written down is the *shape*: a future run that sees 206 and reads it as forty-seven separate problems will cost itself a re-derivation, and a run that clears four chapters on one unit has done about 2% of it.
