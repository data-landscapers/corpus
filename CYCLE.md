---
type: runbook
reader: cc
title: The cycle — BUILD then RENDER in one run — instruction for Claude Code
last_reviewed: 2026-10-03
---

# The cycle — BUILD then RENDER in one run — runbook for Claude Code

*(Run when the whole pipeline goes end to end: Job 1 builds `outputs/` from OSINT, Job 2 renders it into the site and deploys. OSINT is read-only throughout. **`documentation/cycle.md` is why each rule here is as it is**; this file is what to run.)*

## This file is a driver, not a third runbook

**`BUILD.md` and `RENDER.md` remain the procedures, unedited and unabridged.** This file names the order, the one seam between them and what changes there; everything else it delegates. The notes drain and the unit review are jobs whose *placement* this file fixes, and whose own rules stay where they live. An instruction here that is not about *ordering* is an instruction in the wrong file.

## The notes drain runs first

**A cycle opens by clearing what OSINT has asked for** in `C:\corpus-osint-xfer\notes-for-corpus.md`, so the fix is in tonight's build.

**Its rules are not restated here**: `CLAUDE.md` → *The exchange* and the share's `README.md` → *Conventions*. This file says only when it runs.

**An empty queue is the normal outcome and writes nothing** — no log line, no message, no commit. Where the drain did work it writes its own `· **NOTES** ·` line before the build's, naming the numbers closed.

**A note too large for the run does not hold the cycle, and neither does one that fails.** Take the conservative option and state it, never stop to ask: annotate the note with what was established, leave it open at its number, put a line in the build half's message to Bill, and go on to the build. **Never start the build over a half-written share**: commit and push before stage 0, or leave the share untouched.

## A cycle ignores what OSINT sends after it has started

**The base is pinned at stage 2, and the catalogue is the pin** *(Bill, 2026-09-08)*. `report-render._assert_catalogue_current` enforces it:

- a record **deleted** from `raw/` — stop.
- a record **changed** — stop.
- a record **added** — ignored, and said out loud on the run that ignored it.

A record arriving between the drain and stage 2 is built like any other. The sources that arrive after stage 2 are the next cycle's.

## The unit review runs at the seam, on unattended cycles only

**Two countries or regions a cycle have all their reports reviewed whole** *(Bill, 2026-09-17)*: `UNIT-REVIEW.md` is the procedure and `scripts/unit-review.py` picks the units and says whether a review is owed — only on a cycle started by the poll or between 21:00 and 05:00, so a daytime hand-run cycle skips it. **It runs after the build and before the render** so the render publishes what it repaired; it skips itself if the build half did not finish, and a review that fails restores the unit to `HEAD` and never holds the render.

## The seam is a job boundary, not a joint

**The seam check is `RENDER.md` Step 0, run exactly as written.** In a cycle each of its three checks names a defect in *this* run: sentinel still present — BUILD never finished; newest build line missing or `errored` — the build half failed; `outputs/` uncommitted — BUILD's ending sequence did not complete.

**In a cycle there is no repair at the seam.** The cycle stops, does not render, and **does not re-attempt the build**. Log the render half as not run, write the message, stand down. The cycle is finished later by a plain `RENDER.md` run.

## The run

1. **Drain `notes-for-corpus.md`**, as above. Nothing open, nothing to do — go straight to 2.
1a. **Run `python scripts/traffic.py pull`**, then commit `logs/site-analytics.xlsx` alone if it changed, subject `Analytics: <newest day>`. A failure is a log line, never a hold.
2. **Read the sentinel.** If `logs/.build-in-progress` is present, an earlier build died unaccounted. **In a cycle this is a note, not a stop**: the run about to start is the repair — stage 4 resumes on a set difference. Say in the build line that it resumed.
3. **Run `BUILD.md`, whole, stage 0 to the end of its ending sequence** — including the ending sequence, which is what puts the tree into the state the seam reads.
3a. **Finance upkeep** *(Bill, 2026-10-01; the share's `documentation/finance-upkeep.md` is the rule and is not restated here)*. `python scripts/budget-watch.py poll`, every live library. Then budget readings: `logs/budget-followups.md` and any reading a drained note asked for, oldest first, each by `BUDGET-EXTRACT.md`, **until two hours by the clock are used or nothing is waiting — never stopping early on judgement** *(Bill, 2026-10-02)*. Then judge any deal the finance build printed as `NOT YET ASSESSED` into `lookups/deal-scope.csv`. Rebuild finance if anything moved, commit, and put the number of readings still waiting in the build line.
4. **Run `UNIT-REVIEW.md`** if `python scripts/unit-review.py next` (with `--poll` from the loop) names units, for each in turn. Exit 1 — go straight to 5. **A maturity study whose handover note has closed** (`lint-prepared.py` names it) **is named in the cycle's closing report and not completed here**: step 5 opens in a fresh session (method §0). **Then `MATURITY-UPDATE.md` → *The rebuild***, three indicators, on `study-update.py next` the same way.
5. **Run `RENDER.md` Step 0**, unchanged. A stop here ends the cycle.
6. **Run `RENDER.md` Steps 1 to 7**, then its *Log* and its *Mirror*. Unchanged, in order.
7. **Run `python scripts/r2-sync.py --mirror-down --weekly`** — the second copy of the editions; it does nothing inside a week of its last clean pull. When it pulls, log its line: `python scripts/log-line.py copy "<the R2 copy line>"`. Exit 1 is a message to Bill.
8. **Rebuild Research's search index, last and alone** *(Bill, 2026-10-29)* — under the poll, after housekeeping. `C:\Research\handovers\index-build-for-corpus.md` is the procedure; log it as `log-line.py index`. Failure: a line to Bill, never a hold.

The cycle has no stage of its own; steps 1, 4 and 8 are jobs run where they count.

## What does not change

- **`· **BUILD** ·`, `· **REVIEW** ·` and `· **RENDER** ·`, exactly as each job writes them — no `· **CYCLE** ·` job name.** A `· **NOTES** ·` line sits ahead of them on the cycles where there was something to drain.
- **Two message blocks, each written by the half that owes it, when it owes it.**
- **The `.build-in-progress` sentinel stays, and there is no cycle sentinel.** A cycle that dies during the render half is repaired by a render, or by another whole cycle.
- **Commit discipline is unchanged**: one commit per coherent stage in both halves; the cycle adds none.

## Running unattended — a cycle ends three ways

Both halves forbid stopping to ask; the cycle and **every agent it briefs** inherit that. A cycle **finishes**; or **fails in the build half** (the render is not attempted — the seam declines it); or **fails in the render half** (the build's work is committed, logged and safe). The drain sits ahead of all three and ends none of them. Only the third leaves a cycle half-done, and `RENDER.md` on its own completes it.

## What starts a cycle — `scripts/osint-cycle-ready.py`

**A cycle is owed when a sweep cycle has closed and Corpus has not built since.** The discriminator is the **closed row** in `cycle-manifest.json`, not the mirror copy. `osint-cycle-ready.py` is that judgement: exit **0** ready, **1** not ready, **2** needs a human.

**`scripts/poll-loop.py` runs it** *(Bill, 2026-10-29)*: half-hourly, 22:00 to 06:00, in the `CORPUS-POLL` tab.

- **Under the poll, only a critical error stops a cycle** *(Bill, 2026-10-23)*: exit 2, a message, a push notification, the loop stopped. Uncommitted work is committed first, an open OSINT day is left to the catalogue pin, a dead claim or sentinel is resumed. The trigger's head says what counts as critical.
- **`logs/.hold-cycle` is Bill's switch, the one hold left.** It defers a close without consuming it, and `scripts/corpus-status.py` reports it as a gate.
- **A tick that does not fire prints one line**, with any gate `corpus-status.py --gates` reports.
- **Every close fires; there is no minimum interval.**
- **`--skip` passes a close over and loses nothing**: for a night not worth a cycle, or one a cycle starting now supersedes.
- **`--claim` before, `--done` after**; a hand-run cycle need not call `--done`, at the cost of one redundant cycle. `--release` clears a claim by hand.

## Handing over at the seam

**The seam is the right place to stop for context, and the only one** — after the unit review, if one ran; a review is not split across sessions. A fresh session running `RENDER.md` from Step 0 is in exactly the position the cycle would have been in. **Stopping at the seam is a completed build, not an abandoned cycle.** Anywhere else, do not stop deliberately.

## Running the halves separately, and the boundary

Each runbook stands alone exactly as written. Nothing in either half, or here, writes to OSINT — `CLAUDE.md` has the rule.
