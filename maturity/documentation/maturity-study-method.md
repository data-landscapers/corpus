---
type: procedure
reader: cc
title: maturity-study-method.md — how one indicator is studied, staged and written up, in five steps around OSINT's ingest
last_reviewed: 2026-10-11
status: in use; Bill's rulings of 2026-10-06, 2026-10-10 and 2026-10-11
---

# A maturity study: one indicator, worked whole

*(Bill, 2026-10-06. The scale, the null and the as-at rule of `documentation/archived/maturity-assessment.md` §3 and §7 still hold.)*

## 0. What a study is

**One indicator, all 54 countries, in five steps** *(Bill, 2026-10-10)*:

1. **Corpus prepares the criteria**: the study file (§1 to §3, §9), and stops.
2. **Bill confirms.**
3. **Corpus works to the OSINT note without stopping**: review, ladder test, search, handover (§4, §5).
4. **OSINT ingests without stopping** and closes the note.
5. **Corpus completes without stopping**: a stage, a short summary and a long summary per country per sub-indicator and the soft-launch map (§6 to §8).

**Bill is asked once, at step 2.** "**prepare maturity study {id}**" starts step 1, "**run maturity study {id}**" step 3 and "**complete maturity study {id}**" step 5, **in a fresh session**; the cycle that finds the note closed says so (`CYCLE.md` step 4). A later doubt is settled conservatively and reported at the end.

**A study is sized by the quota it takes** *(Bill, 2026-10-11)*. Each fan-out runs as one workflow, so the parent wakes once a stage. Steps 3 and 5 each end with `python scripts/study-tokens.py` and its total in the log line.

**Where things live** *(Bill)*: anything generic in `maturity/documentation/`, a study's file and working files in `maturity/{id}/`, what it issues in `outputs/maturity/{id}/`.

## 1. Typology before anything is compared

**Settle what the thing is, then classify every system the evidence names.** The study file lists the classes: assessed, noted and not assessed, or out of scope. Where one label hides two things, the indicator splits into sub-indicators, each with its own ladder.

**Class by what the thing does, never by its form** *(Bill, 2026-10-11)*: what does the job counts, whatever it is called and whatever larger thing it sits in. **A class exists only where it changes a stage or a flag.** A system named with no description stays unclassified, a gap for §5.

Output: `systems.csv`, one row per named system per country.

## 2. Aspects

**Each sub-indicator is assessed on a fixed list of aspects, each with one role and a closed list of values.** A **coverage** aspect sets the stage; a **qualifier** can cap or flag it and never raises it.

## 3. How a stage is defined

1. **A rung is a coverage test.** The existence of a named system, a strategy or a launch places nothing above Nascent.
2. **Each rung states a value for every coverage aspect**, as a table of rung by aspect, and is met only when every aspect meets it. A drafter decides it from a dated source without interpretation.
3. **Between two rungs, take the lower** and name the missing fact in the short summary.
4. **Stage 1 needs a cited, dated absence.** Evidence that states no coverage aspect leaves the cell unplaced; nothing held is *No evidence*.
5. **Stage 5 is reachable.** A coverage level on a published figure, set from the norm's target where it has one; a statement of alignment is not a test.
6. **A threshold is a share of a stated denominator.** A count without a denominator is a floor and places by the lower rung.
7. **A qualifier carries at most one cap rule and a closed list of flags.**
8. **A coverage fact carries its year**; one older than three years at the as-at still places the country and prints its year in the short summary.
9. **The ladder is confirmed at step 2, tested on the review's evidence and fixed before the search.** A rung nothing reaches, or one drafters read two ways, is rewritten then and the study file says so; a later change restages every country.

## 4. Step 3: review what is held

**Read the cheapest source that settles the rung** *(Bill, 2026-10-11)*. Dated news and official notices settle existence, standing and period. An instrument's own text is opened only for a cell at a rung whose test needs it.

**Start from the assessment already held** *(Bill, 2026-10-11)*: the frame's cells for the row and its neighbours, with their sources, are carried into `evidence.csv` first. **A country is read, and searched, only where they leave a coverage aspect short of a rung test.**

`scripts/study-select.py {id}` writes `maturity/{id}/evidence/{ISO3}/readlist.csv`: every held document on the country that carries a study term or that its report cites on the subject, a long or thinly matching one as passages.

**A term names the subject, not its field**: a dry run listing more than could be about the subject means the terms are too broad. Size a study by what it will read.

**The list is ranked and read from the top, by `pass`**: news before instruments, then title-matched, then newest.

1. **`1`, about 15 documents, is read for every country with such a gap.**
2. **`2` is read a call at a time while `profile.csv` shows a coverage `gap`**, and stops when two calls running add no fact.
3. **`rung` is opened a document at a time**, for a cell placed below a rung that tests the text, and for that rung's aspects.

**A drafter is a fresh call on one `slice`, five documents at most, never a run of them.** Drafters work to `drafter-brief.md`, on Sonnet, read the document and not its ledger line, and write the facts `study-profile.py --merge` folds into `evidence.csv`, one row per stated fact.
`study-profile.py` then writes `profile.csv`: each aspect's best-evidenced value, its sources and a `gap` cell.

**The parent verifies files, not tallies**: slugs resolve in `raw/` and sampled facts match the body.

## 5. Step 3: search for what is missing

**A gap is a coverage aspect with no dated fact inside three years, or a qualifier aspect with nothing in its window.**

**One Exa brief per country per sub-indicator that has a gap.**

**Searchers work to `searcher-brief.md`, on Sonnet; `scripts/study-stage.py` fetches and stages.**

- **Relevance selects; there is no numeric cap** *(Bill)*. A fetched document is kept when its body states a dated fact, on an aspect with a gap, that nothing held states.
- **Delivery is a handover in `prepared\`, not a `new-queue\` batch** *(Bill)*. Candidates are written flat to `C:\corpus-osint-xfer\prepared\maturity-study-{id}\`.
- **OSINT's cycle pulls the folder once it carries `READY`, written last**; file names are unique against `raw/`. One `[ACT]` note in `notes-for-osint.md`, titled *Maturity study {id}: evidence to ingest*, with `Affects: outputs/maturity/{id}/`. `study-stage.py ready` writes the folder's `BRIEF.md`.
- **Records in `maturity/{id}/search/`**: `searched.csv`, `staged.csv` by file handed over, and `unselected.csv`. Candidate bodies are never committed.

Before the note, `python scripts/lint-staged-queue.py {folder}` passes; then the share is committed and pushed.

**A found document reaches the study only through ingest** *(Bill)*.

## 6. Step 4: OSINT's ingest

**Step 5 waits until the note has moved to `notes-for-osint-resolved.md`** and the mirror's `cycle-manifest.json` is later than the move. `scripts/study-returned.py {id}` then checks every row of `staged.csv` against the mirror's URL indexes. A document not admitted is not held, and its gap stands. The spent handover is deleted in the same commit.

## 7. Step 5: stage

1. **Re-read**: admitted documents are read whole, in calls as §4, into `evidence.csv` and the profiles refreshed.
2. **Fix the as-at**: the last day of the month before step 5 opens.
3. **Stage from the ladder**: the coverage aspects pick the rung, then the cap rule and the flags; `stage_sources` names the `row_id`s that set it, and `cap` the rung a capped cell had reached.
4. **Check that two drafters agree.** A second drafter, on Opus, restages 20 cells, drawn by `study-profile.py --draw`, blind from `evidence.csv`. Below 16 in agreement, the rung that split them is rewritten and every country restaged.

## 8. Step 5: write

**Short summary: one plain sentence, 25 words at most, no link** *(Bill, 2026-10-09)*: what happens in the country, with its year; `writer-brief.md` holds the wording.

**Long summary: one paragraph per aspect, in the study's order, each opening with the aspect's name in bold; 120 to 250 words.** A link on every claim, and two closing lines: ***Noted, not assessed*** and ***Not held***. `writer-brief.md` holds the rest.

Files, in `outputs/maturity/{id}/`:

| File | Holds |
|---|---|
| `assessment.csv` | One row per country per sub-indicator; `lint-study.py` holds the columns |
| `{ISO3}.md` | The long summaries |
| `{indicator_id}.md` | Cross-country page: norm, ladder, then each country |

`scripts/study-render.py` writes the pages from the CSVs. `scripts/lint-study.py` holds them.

**Step 5 ends on the soft-launch map and methodology page** *(Bill; `output-spec-v2.md`)*: write five `criteria` and `criteria_of` into `study.json`, run `scripts/maturity-site.py`, commit and push.

**The frame is not touched until Bill accepts the study.** On acceptance, rows are retired and minted under `adding-an-indicator.md` §2 and §10, and the study's CSV is the baseline edition.

## 9. The study file

`maturity/{id}/maturity-study-{id}.md` answers §1 to §5 for one indicator, names the frame rows it redraws, and says whether the norm measures what the sub-indicators measure. `study.json` beside it restates its lists as data for the scripts.

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
