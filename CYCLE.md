---
type: runbook
title: The cycle — BUILD then RENDER in one run — instruction for Claude Code
last_reviewed: 2026-08-28
---

# The cycle — BUILD then RENDER in one run — runbook for Claude Code

*(Run when the whole pipeline goes end to end: Job 1 builds `outputs/` from OSINT, Job 2 renders it into the site and deploys. OSINT is read-only throughout.)*

## This file is a driver, not a third runbook

**`BUILD.md` and `RENDER.md` remain the procedures, unedited and unabridged.** This file names the order, the one seam between them and what changes there; everything else it delegates. A combined file that restated either half would drift from its original silently, leaving an unattended run two instructions on one step and no way to rule between them. **Nothing bridges the halves**: no work the cycle does that neither half does alone, no state passed beyond the committed tree. An instruction here that is not about *ordering* is an instruction in the wrong file.

## Why running them together is better than running them apart

- **The bulletin.** BUILD stage 7 writes it over a two-day publication window; a render a day later publishes a window the site is no longer in — well-formed, and invisible downstream.
- **`BUILT-FROM` gets tighter for free**: in a cycle, the stamped HEAD is the build's own final commit.
- **One mirror covers both halves.** RENDER's *Mirror* captures the build's `outputs/` and the render's `site/` in one pass; a build never followed by a render is not backed up until one is.

## The seam is a job boundary, not a joint

**BUILD's ending sequence leaves the tree in exactly the state `RENDER.md` Step 0 tests for** — everything committed, a non-error build line, no sentinel. The cycle does not weld the halves; it runs the second at the point where the first has finished saying so.

**The seam check is `RENDER.md` Step 0, run exactly as written.** In a cycle each of its three checks names a defect in *this* run: sentinel still present — BUILD never finished; newest build line missing or `errored` — the build half failed; `outputs/` uncommitted — BUILD's ending sequence did not complete.

**In a cycle there is no repair at the seam.** The cycle stops, does not render, and **does not re-attempt the build** — a retry inside the same run is a job looping on the fault that stopped it. Log the render half as not run, write the message, stand down. The build's work is committed and logged, so the cycle is finished later by a plain `RENDER.md` run.

## The run

1. **Read the sentinel before anything else.** If `logs/.build-in-progress` is present, an earlier build died unaccounted. **In a cycle this is a note, not a stop**: the run about to start is the repair — stage 4 resumes on a set difference. Say in the build line that it resumed.
2. **Run `BUILD.md`, whole, stage 0 to the end of its ending sequence** — including the ending sequence, which is what puts the tree into the state the seam reads.
3. **Run `RENDER.md` Step 0**, unchanged. A stop here ends the cycle.
4. **Run `RENDER.md` Steps 1 to 7**, then its *Log* and its *Mirror*. Unchanged, in order.

The cycle has no stage of its own.

## What does not change

- **Two log lines, `· build ·` and `· render ·`, exactly as each half writes them — no `· cycle ·` job name**: `lint-mirror-freshness.py` finds the newest `· render ·` line, Step 0 greps for `· build ·`, and per-half durations stay comparable. A cycle is indistinguishable in the log from two runs an hour apart, which is correct.
- **Two message blocks, each written by the half that owes it, when it owes it** — held back and merged, the build half's message dies with a seam stop.
- **The `.build-in-progress` sentinel stays, and there is no cycle sentinel.** A cycle that dies during the render half has already stood down its build; the repair is a render — or another whole cycle, whose build half finds nothing unconsidered and costs almost nothing. The render is idempotent, so re-running it is never the wrong move.
- **Commit discipline is unchanged**: one commit per coherent stage in both halves; the cycle adds none.

## Running unattended — a cycle ends three ways

Both halves forbid stopping to ask, and the cycle inherits that whole. A cycle **finishes**; or **fails in the build half** (the render is not attempted — the seam declines it); or **fails in the render half** (the build's work is committed, logged and safe). Only the third leaves a cycle half-done, and `RENDER.md` on its own completes it. A build with no render is a stale site, not a broken one — the previous render is still served.

## What starts a cycle — `scripts/osint-cycle-ready.py`

**A cycle is owed when a sweep cycle has closed and Corpus has not built since.** The discriminator is the **closed row**, not the mirror copy: `SWEEP-CYCLE` writes `End` into `logs/sweep-cycle_log.md` and commits *before* it mirrors, so `max(End)` advances on a close and nothing else, and reading a new `End` from the mirror is itself the proof the mirror carried it. `osint-cycle-ready.py` is that judgement: exit **0** ready, **1** not ready, **2** needs a human.

**Poll it from a session left open:**

```
/loop 25m Run `python scripts/osint-cycle-ready.py --claim`. On exit 0, run CYCLE.md end to
end and finish with `python scripts/osint-cycle-ready.py --done`. On exit 1, stop and say
nothing. On exit 2, write one block in logs/messages-for-bill.md and stop — do not re-run.
```

- **Every close fires; there is no minimum interval.** Each close is a night's evidence landed in `raw/`, so each earns a build.
- **The poll is started against a cycle, not left running.** Bill starts `/loop` when he initiates `SWEEP-CYCLE`, so the only OSINT commits inside the poll's life are that cycle's own. OSINT mirrors after every commit, so a poll left running across a housekeeping morning could start a build over a tree that moves under it. The mechanical half is guarded regardless — `report-render.py` raises `vault_lib.StaleCatalogue` rather than rendering against a moved base — so a slip costs a stopped run naming its own repair, not a bad publish.
- **`logs/.hold-cycle` is the switch to flip before sitting down to work.** While it exists the trigger holds (as for `.build-in-progress` and uncommitted tracked changes), and it does not advance the watermark — the held close runs when the file comes out.
- **`--skip` passes a close over without building it, and loses nothing** — the next close covers a skipped one whole, since BUILD works off a set difference. Use it when a night's catch does not earn a cycle, or when a close is superseded by a cycle starting now.
- **The quiet answer also says how far the base has moved** — file counts and commit range appended to `nothing new` — because *nothing owed* and *nothing wanted* are different questions and a person asking gets both from one command. It fires only on the close row: a base-movement trigger would fire mid-session repeatedly, and a size threshold only delays that. What the quiet answer cannot tell apart — *OSINT has not run* from *the mirror has not carried what it ran* — `scripts/lint-osint-freshness.py` measures at BUILD stage 0.
- **A hand-run cycle need not call `--done`; the cost is one redundant cycle**, which finds nothing unconsidered and costs almost nothing — cheaper than a trigger inferring what a hand-run did from log lines.
- **`--claim` before, `--done` after; a claim that never reported done stops the loop** — the next poll exits 2, and `--release` clears it once someone has looked. A loop that re-fired on its own failure would be a job looping on the fault that stopped it.

## Handing over at the seam

**The seam is the right place to stop for context, and the only one.** BUILD stage 4 is model authoring across forty-odd units; the render half deserves a session with room to read its own output. There is nothing to hand over but the instruction — a fresh session running `RENDER.md` from Step 0 is in exactly the position the cycle would have been in. **Stopping at the seam is a completed build, not an abandoned cycle.** Anywhere else, do not stop deliberately: inside stage 4 an interruption is survivable but invisible; inside the render half it leaves `site/` part-written and undeployed.

## Running the halves separately

**Unchanged, and this file is not involved.** Each runbook stands alone exactly as written; nothing in either was changed to make the cycle possible beyond a pointer to this file. That is the test of the seam: if the combined form had needed either half altered, the halves were not separable.

## Boundary

Nothing in either half writes to OSINT, and neither does this. `C:\OSINT` is read-only from Corpus without exception — `CLAUDE.md` has the rule.
