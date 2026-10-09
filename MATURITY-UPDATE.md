---
type: runbook
reader: cc
title: The maturity update — BUILD stage 4c and the indicator rotation — instruction for Claude Code
opened: 2026-10-09
last_reviewed: 2026-10-09
---

# The maturity update — keeping a finished study current

*(Commissioned by Bill on 2026-10-09. `maturity/documentation/maturity-study-method.md` makes a study; this keeps what it issued true. OSINT is read-only throughout.)*

**The one-line brief.** *A study stages an indicator once. Every night's arrivals are read for facts that bear on it, a fact that could move a cell has the cell reassessed, and in rotation each indicator is reassessed whole, all 54 countries against the one ladder.*

`scripts/study-update.py` is the mechanical half and its docstring holds the files and the rotation's rules; do not re-derive them. A country is worked under the three briefs in `maturity/documentation/`: `drafter-brief.md` for a fact, `stager-brief.md` for a stage, `writer-brief.md` for the summaries. **CC does the work itself, in the run; no agent is started.**

## Stage 4c — the night's arrivals

The same set difference as stages 4 and 4b, over a study's reading lists. From `scripts/.workroot/`, for each study `python scripts/study-update.py list` names:

```bash
python scripts/study-select.py {id} --new     # appends the arrivals to the reading lists
python scripts/study-update.py order          # the open arrivals, by study and country; exit 1 = none
```

Exit 1 from `order` ends the stage. Otherwise work each arrival in turn, a country's together.

### Level 1 — add the fact

1. **Read the document** at the `path` its reading-list row gives, whole or as passages as the row says.
2. **Does it state a dated fact on one of the study's aspects, for this country, that `evidence.csv` does not hold?** The term test admits by a word, so most arrivals are about something else: a court system, a police pilot, another sector. That is `nothing`, and the commonest outcome.
3. **A fact goes into `evidence.csv`** as a new row under the drafter brief: the next `row_id`, the aspect, a value from its closed list, `as_of` and its precision, the system and its class, the slug and the URL. A system the country did not hold goes into `systems.csv`.
4. **A substantive fact updates the country's text the same night**: the paragraph of `outputs/maturity/{id}/{ISO3}.md` on that aspect, under the writer brief, linked to the new row's URL; and the *Noted, not assessed* or *Not held* line if the fact changes what they say.

### Level 2 — does the fact call for a reassessment?

**It does when it bears on what set the stage**: a coverage aspect of a studied sub-indicator, the qualifier the cap rule reads, or a dated event inside the last twelve months. A fact that only adds a source to a position already held does not.

5. **Reassess the cell** under the stager brief, from every row the country now holds on that sub-indicator, not from the new row alone. Rewrite its entry in `evidence/{ISO3}/stage.json`: the stage, each aspect's value, `cap`, `flags`, `stage_sources`, `gaps` and `note`.
6. **Log it, whether or not the stage moved**:

   ```bash
   python scripts/study-update.py log {id} {ISO3} {key} --kind fact --note "what arrived and what it settled"
   ```

   Run it after `stage.json` is rewritten and before `study-assess.py`: it reads the published stage as `from`.
7. **Rewrite the short summary** in `short.json` where the stage, or the fact it rests on, changed.

### Close and publish

8. **Close every arrival**: `python scripts/study-update.py close {id} {ISO3} {slug} --outcome nothing|fact|reassessed`.
9. **Fold and check**, from the workroot, once for the night:

   ```bash
   python scripts/study-assess.py {id} --as-at {the study's as-at}   # a logged cell keeps its own
   python scripts/study-render.py {id}
   python scripts/lint-study.py {id}
   ```

   A lint failure is repaired before the commit; a cell that cannot be repaired is restored from git and its arrival left open.
10. **Commit** `maturity/{id}/evidence/`, `outputs/maturity/{id}/` and nothing else; RENDER builds the pages. The log line carries the counts: arrivals, facts, reassessments, stages moved.

## The rotation — one indicator, whole

**Stage 4c never looks back.** A cell staged on a 2023 figure stays there until a document happens to arrive; a rung read one way in Angola and another in Zambia passes every check. The rotation re-reads an indicator across all its countries at once.

```bash
python scripts/study-update.py next --poll    # from the /poll loop
python scripts/study-update.py next           # any other cycle
```

**Exit 0 names tonight's indicator; exit 1 means none is owed**: the cycle is attended, or every indicator has been reassessed inside the script's gap. It runs in `CYCLE.md` after the unit review, on the same test, and is skipped whenever the unit review is.

1. **Read the indicator whole**: the study file's ladder and its rules, then every country's rows for this sub-indicator in `evidence.csv`, its cell in `stage.json` and its row of `assessment.csv`. Read the 54 cells as a table, sorted by stage, before judging any one.
2. **Ask of each cell whether the ladder, applied as it is applied to its neighbours, still puts it there.** Look for the same evidence staged two ways in two countries; a cell whose `stage_sources` no longer support its rung; a cap or a flag whose 36 or 12 months have run out; an arrival's fact that level 2 let pass.
3. **Age does not expire a stage, and it can lower one** *(Bill)*. A cell is not moved because a window has closed. But where the only evidence for a rung is old enough that it no longer shows the country is there now, the reassessment may lower the stage, as a judgement, and says so in the note. The short summary of any cell resting on a fact older than three years prints its year.
4. **Restage what fails** under the stager brief, and **log every cell reassessed, moved or not**, with `--kind review`. A cell the pass read and left alone is not logged; the indicator's `done` covers it.
5. **Rewrite what the restaging made untrue**: the short summary, and the country's paragraphs.
6. **A rung that the pass shows is read two ways is not rewritten here.** That is a change to the ladder and Bill's: write it as a block in `messages-for-bill.md` with the two readings and the countries each would move, and stage on the wording as it stands. When he rules, the restaging is logged `--kind ladder`.
7. **Fold, check and stamp**: step 9 above, then `python scripts/study-update.py done {id} {key}`, and commit as step 10 with `logs/maturity-review.csv`.

## The standing search is yearly

`order` and `next` print `standing search due` for a study whose `study.json` → `searched` is over a year old. **The search is the method's §5, and it spends OSINT's quota**, so it is not started by a cycle: add one job to `C:\corpus-osint-xfer\corpus-housekeeping.md` naming the study, and Bill starts it. Between searches a study relies on the ordinary collection.

## What the site shows

`outputs/maturity/{id}/history.csv` is the record and `scripts/maturity-site.py` reads it. A change logged `fact` is a **move**: *Stage last moved* and the changes box. A change logged `review` or `ladder` shows as *Reassessed {month}* and is not counted as movement. A reassessment that left the stage alone moves only *Last assessed*. The build stops if a cell's stage differs from the one its last logged reassessment left, which is how an unlogged restaging is caught.

## Boundary

Nothing here writes to `C:\OSINT`. A defect in a held record is an `[ACT]` note with its `Affects:` line; a document the indicator needs and the catalogue lacks waits for the yearly search.
