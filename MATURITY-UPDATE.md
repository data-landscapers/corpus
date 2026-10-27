---
type: runbook
reader: cc
title: The maturity update — BUILD stage 4c and the nightly rebuild — instruction for Claude Code
opened: 2026-10-09
last_reviewed: 2026-10-18
---

# The maturity update — keeping a finished study current

*(Commissioned by Bill on 2026-10-09. `maturity/documentation/maturity-study-method.md` makes a study; this keeps what it issued true. OSINT is read-only throughout.)*

**The one-line brief.** *A study stages an indicator once. Every night's arrivals are read for facts that bear on it, a fact that could move a cell has the cell reassessed, and each night three indicators are rebuilt whole, all 54 countries against the one ladder, and searched for what they do not hold.*

**Lifted** *(Bill, 2026-10-17)*: every indicator has had its first study, so stage 4c and the rebuild run. `study-update.py` → `HELD` is the switch.

`scripts/study-update.py` is the mechanical half and its docstring holds the files and the rebuild's rules; do not re-derive them. A country is worked under the three briefs in `maturity/documentation/`: `drafter-brief.md` for a fact, `stager-brief.md` for a stage, `writer-brief.md` for the summaries, and the share's `documentation/prose-style.md` last.

**The facts are in news, not in large documents** *(Bill, 2026-10-17)*. An instrument, a story from before the three-year window and a country's stories past 20 are closed unread; the rest is read once across every study that lists it, by Sonnet drafters (`scripts/study-arrivals.py`).

## Stage 4c — the night's arrivals

The same set difference as stages 4 and 4b, over a study's reading lists. From `scripts/.workroot/`:

```bash
python scripts/study-select.py ALL --new          # every study's arrivals, from what changed since its stamp
python scripts/study-arrivals.py triage            # instruments and pre-window stories closed unread
python scripts/study-arrivals.py plan --cap 20     # shared calls; exit 0 with 0 calls = none
python scripts/study-arrivals.py prompts {dir}     # one drafter file per call
```

Start one Sonnet drafter per call file, then `study-arrivals.py fan`: an arrival stating nothing closes `nothing`. Levels 1 and 2 below work the arrivals left open, a country's together; step 1's reading is the drafter's.

### Level 1 — add the fact

1. **Read the document** at the `path` its reading-list row gives, whole or in passages, as the row says.
2. **Does it state a dated fact on one of the study's aspects, for this country, that `evidence.csv` does not hold?** The term test admits by a word, so most arrivals are about something else: a court system, a police pilot, another sector. That is `nothing`, the commonest outcome.
3. **A fact goes into `evidence.csv`** by `python scripts/study-profile.py {id} --merge`: each facts file taken once, only the countries it reached written. A hand-read fact follows the drafter brief.
4. **A substantive fact updates the country's text the same night**: the paragraph of `outputs/maturity/{id}/{ISO3}.md` on that aspect, under the writer brief and sheet, linked to the new row's URL; and the *Noted, not assessed* or *Not held* line if the fact changes what they say.

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

## The rebuild — three indicators a night

**Three indicators a night are rebuilt whole** *(Bill, 2026-10-18)*: 54 cells reassessed against one ladder, then all 54 countries searched afresh. `logs/maturity-review.csv` is the control list: one row an indicator, its last rebuild, and what that rebuild cost. At three a night the 116 indicators turn over in about six weeks.

**The rebuild is the deep dive** *(Bill, 2026-10-16)*: most indicators were first studied in batches that skip the second drafter and stage hard cells low (`maturity/documentation/first-pass-batch.md`, `study.json` → `"pass": "first"`). For those the rebuild adds the second-drafter check of method §7.3 and a fresh reading of every cell whose `note` opens *First pass:*.

**Stage 4c never looks back**: a cell staged on a 2023 figure stays there until a document happens to arrive. The rebuild does.

```bash
python scripts/study-update.py next --poll    # from the /poll loop
python scripts/study-update.py next           # any other cycle
```

**Exit 0 names tonight's three indicators; exit 1 means none is owed.** It runs in `CYCLE.md` after the unit review and is skipped whenever that is. Work each indicator whole, steps 1 to 10, then the next.

**Measure each one** *(Bill, 2026-10-17: what a night's rebuilds cost is the first question)*. Before step 1 run `python scripts/log-line.py --start rebuild` and `python scripts/study-tokens.py --total`, and keep the figure; step 10 takes the difference.

### Reassess

1. **Read the indicator whole**: the study file's ladder and its rules, then every country's rows for this sub-indicator in `evidence.csv`, its cell in `stage.json` and its row of `assessment.csv`. Read the 54 cells as a table, sorted by stage, before judging any one.
2. **Ask of each cell whether the ladder, applied as to its neighbours, still puts it there**: the same evidence staged two ways in two countries, `stage_sources` that no longer support the rung, a cap or flag whose 36 or 12 months have run out.
3. **Age does not expire a stage, and it can lower one** *(Bill)*. A cell is not moved because a window has closed. But where the only evidence for a rung is old enough that it no longer shows the country is there now, the reassessment may lower the stage, as a judgement, and says so in the note. The short summary of any cell resting on a fact older than three years prints its year.
4. **Restage what fails** under the stager brief, and **log every cell reassessed, moved or not**, with `--kind review`. A cell read and left alone is not logged; the indicator's `done` covers it.
5. **Rewrite what the restaging made untrue**: the short summary, and the country's paragraphs.
6. **A rung read two ways is not rewritten here.** That is a change to the ladder and Bill's: write it as a block in `messages-for-bill.md` with the two readings and the countries each would move, and stage on the wording as it stands. When he rules, the restaging is logged `--kind ladder`.
7. **Fold and check**: step 9 of stage 4c.

### Search

*(Bill, 2026-10-11.)* **What is found reaches Corpus only through ingest**: OSINT pulls it in its next sweep cycle and stage 4c reads it the night after.

8. **Search every country on every question of the ladder, whatever is held** *(Bill, 2026-10-19)*, under the method's §5: one Sonnet searcher a country to `searcher-brief.md`, the brief naming tonight's sub-indicator, then `scripts/study-stage.py` to fetch and stage. If `maturity/{id}/search/` holds an earlier round, `git mv` it to `maturity/{id}/search-{that round's searched date}/` first, or `stage` hands the old selections over again. This is the one place the runbook starts agents. **A searcher is never waited on**: one out 20 minutes past its wave is stopped and staged as it stands.
9. **Deliver without a note**: `python scripts/lint-staged-queue.py {folder}` passes, then `python scripts/study-stage.py {id} ready --rebuild --lint "<its line>"`. `notes-for-osint` 237 is the standing announcement; OSINT's cycle pulls the folder on `READY`. Delete any `prepared\maturity-study-*` folder `lint-prepared.py` calls spent, and commit and push the share. Nothing selected stages nothing.

### Close

10. **Stamp and commit**: `study.json` → `searched` takes today, then

    ```bash
    python scripts/study-update.py done {id} {key} --minutes <n> --tokens <M> --staged <n>
    python scripts/log-line.py rebuild "{id} {key}: <n> cells reassessed, <n> moved; <n> searched, <n> staged; <M>M tokens — ok"
    ```

    Minutes from the stamp, tokens as `--total` now less `--total` before. Commit `maturity/{id}/`, `outputs/maturity/{id}/` and `logs/maturity-review.csv`, explicit paths, and push.

**A rebuild that cannot finish** restores its files to `HEAD`, is not stamped, logs `errored` and never holds the render.

## What the site shows

`outputs/maturity/{id}/history.csv` is the record and `scripts/maturity-site.py` reads it. A change logged `fact` is a **move**: *Stage last moved* and the changes box. A change logged `review` or `ladder` shows as *Reassessed {month}* and is not counted as movement. A reassessment that left the stage alone moves only *Last assessed*. The build stops if a cell's stage differs from the one its last logged reassessment left, which is how an unlogged restaging is caught.

## Boundary

Nothing here writes to `C:\OSINT`. A defect in a held record is an `[ACT]` note with its `Affects:` line; a document the indicator needs and the catalogue lacks is what the rebuild's search asks for.
