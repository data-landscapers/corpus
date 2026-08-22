---
type: runbook
title: The cycle — BUILD then RENDER in one run — instruction for Claude Code
last_reviewed: 2026-08-17
---

# The cycle — BUILD then RENDER in one run — runbook for Claude Code

*(Hand this to Claude Code in the Corpus repo when the whole pipeline is to run end to end: Job 1 builds `outputs/` from OSINT, Job 2 renders `outputs/` into the site and deploys it. **Bill, 2026-08-17**: run the two together, while still allowing separate runs. OSINT is read-only throughout — nothing here writes to it.)*

## This file is a driver, not a third runbook

**`BUILD.md` and `RENDER.md` remain the procedures, unedited and unabridged.** This file names the order, the one seam between them and what changes there; everything else it delegates. Read it alongside them, not instead of them.

**A combined file that restated either half would be the worst of the three** *(2026-08-17)*. The two halves are long, they are revised often — nine dated amendments between them in the last four days — and a copy drifts from its original silently, because both read correctly on their own. An unattended run that met the drift would have two instructions on the same step and no way to rule between them, which is exactly the fault `RENDER.md` → *Mirror* documents in its own history: a paragraph contradicting the section above it, on the single destructive step in the job. So there is no second copy here of anything either runbook says.

**Nothing bridges the halves.** There is no work the cycle does that neither half does alone, no state passed between them beyond the committed tree, and no step that exists only in the combined form. That is what makes combining them safe, and it is worth checking against if this file ever grows: an instruction here that is not about *ordering* is an instruction in the wrong file.

## Why running them together is better than running them apart

**The bulletin is the reason** *(2026-08-17)*. `BUILD.md` stage 7 writes a bulletin over a **two-day publication window**, rendered at `RENDER.md` Step 2 and linked from the home page at Step 3. A build whose render comes a day later publishes a bulletin whose window has already moved — well-formed, correctly dated, and describing a window the site is no longer in. Nothing downstream can see that, which is the same shape as every other fault these two runbooks are built around.

**`BUILT-FROM` gets tighter, for free.** Step 1 stamps `git rev-parse HEAD`, and in a cycle that HEAD is the build's own final commit. Run apart, HEAD may have moved under an unrelated commit between the two jobs, and the site's provenance stamp then names a tree that is not the one it was cut from.

**One mirror covers both halves.** `RENDER.md` → *Mirror* is the last step of the last job, and in a cycle it captures the build's `outputs/` and the render's `site/` in a single pass. Run apart, a build that is never followed by a render is not backed up until one is — which `lint-mirror-freshness.py` check 3 eventually catches, seventy-two hours later.

## The seam is a job boundary, not a joint

**BUILD's ending sequence already leaves the tree in exactly the state `RENDER.md` Step 0 tests for.** Everything committed, one line in `logs/log.md` that is not an error line, no sentinel outstanding. That is not a coincidence to be tidied away — it is the whole reason the two jobs can be joined without inventing anything. The cycle does not weld them; it runs the second one at the point where the first one has finished saying so.

**So the seam check is `RENDER.md` Step 0, run exactly as written, and it is not a formality.** In a separate render it is a gate on a predecessor nobody watched. In a cycle it is a self-test on the half that just ran, and each of its three checks now names a specific defect in *this* run:

- **the sentinel is still there** — BUILD did not reach step 5 of its ending sequence, so it did not finish;
- **the newest build line is missing or says `errored`** — the build half failed and said so;
- **`outputs/` has uncommitted changes** — BUILD did not reach step 4 of its ending sequence.

**What differs is the repair, and in a cycle there is none.** `RENDER.md` Step 0 says the repair is to run BUILD; that is advice to a render standing on its own. Here the build half has already had its run. **The cycle stops at the seam, does not render, and does not re-attempt the build** — a retry inside the same run is how a job starts looping on the fault that stopped it. Log the render half as not run, write the message, stand down. The build's own work is committed and logged, so the cycle is finished later by a plain `RENDER.md` run and nothing is lost or repeated.

## The run

1. **Read the sentinel before anything else.** If `logs/.build-in-progress` is present, an earlier build died without accounting for itself. **In a cycle this is a note, not a stop**: the run about to start is the repair, since `BUILD.md` stage 4 resumes on a set difference over slugs and every unit the dead run finished is already marked. Say so in the build line — a resumed build is worth being able to see in the log.
2. **Run `BUILD.md`, whole, from stage 0 to the end of its ending sequence.** Every stage, both gates, its log line, its commit, its stand-down. Do not skip its ending sequence on the grounds that the render is about to run: it is what puts the tree into the state the seam reads.
3. **Run `RENDER.md` Step 0**, unchanged — the `--start render` stamp, the three checks, then the sweep-up commit. Under *The seam* above, a stop here ends the cycle.
4. **Run `RENDER.md` Steps 1 to 7**, then its *Log* and its *Mirror*. Unchanged, in order.

That is the whole of it. The cycle has no stage of its own.

## What does not change, and why each one is worth saying

**Two log lines, `· build ·` and `· render ·`, exactly as each half writes them.** There is no `· cycle ·` job name and there must not be: `RUN_RE` in `scripts/lint-mirror-freshness.py` finds the newest `· render ·` line and would stop seeing one, `RENDER.md` Step 0 greps for `· build ·` and a separate render would stop finding one, and the durations — measured per half, from the two stamps — stay comparable against every line already in the log. A cycle is therefore indistinguishable in `logs/log.md` from two runs an hour apart, which is correct, because nothing reads the log to find out which it was.

**Two message blocks, each written by the half that owes it, at the moment it owes it.** Do not hold BUILD's block back to merge it with RENDER's: a cycle that dies at the seam would then lose the build half's message along with the render, and the message is the thing that survives a run precisely so that it can be read after one.

**The `logs/.build-in-progress` sentinel stays, and there is no cycle sentinel.** It is what makes step 1 above meaningful and what lets a later separate `BUILD.md` run resume an interrupted cycle. A second sentinel for the cycle would guard nothing: a cycle that dies during the render half has already committed and stood down its build, and the repair is to run the render — or another whole cycle, whose build half finds nothing unconsidered, prints `unchanged` across the tree and costs almost nothing. The render is idempotent by construction, so re-running it is never the wrong move.

**The leak gate runs twice, over `outputs` in BUILD's ending sequence and over `site outputs` at Step 7.** The second is not redundant: it is the gate on the public boundary, it covers `site/`, which did not exist when the first one ran, and `RENDER.md` names it as the only STOP in that half. Both stand.

**Commit discipline is unchanged.** One commit per coherent stage in both halves, per `CLAUDE.md`. The cycle adds no commit of its own and defers none.

## Running unattended — a cycle ends three ways

**Both halves already forbid stopping to ask, and the cycle inherits that whole** *(Bill, 2026-08-16, in both runbooks)*. Where the run wants Bill's attention it finishes what it can and leaves a block in `logs/messages-for-bill.md`.

A cycle **finishes**; or it **fails in the build half**, in which case the render is not attempted and the seam check is what declines it; or it **fails in the render half**, in which case the build's work is committed, logged and safe.

**Only the third of those leaves a cycle genuinely half-done, and it is not repaired by hand.** `RENDER.md` on its own completes it, and its Step 0 will pass, because the build half accounted for itself. A build with no render is a stale site, not a broken one — the previous render is still being served.

## What starts a cycle — `scripts/osint-cycle-ready.py`

**A cycle is owed when a sweep cycle has closed and Corpus has not built since** *(Bill, 2026-08-20)*. `SWEEP-CYCLE.md` → *Mirror* makes FreeFileSync the night's last act, so a completed cycle refreshes the whole of `C:\OSINT` — but so does a manual FFS run in the middle of an afternoon's work, and the two look identical in every mtime on the disk. **The discriminator is the closed row**, not the copy: the cycle writes `End` into `logs/sweep-cycle_log.md` and commits *before* it mirrors, so `max(End)` advances on a close and on nothing else, and reading a new `End` from the mirror is itself the proof the mirror carried it. `osint-cycle-ready.py` is that judgement and its reasoning; exit **0** ready, **1** not ready, **2** needs a human. **Nothing changed on the OSINT side to make this work** — the signal was already written and already crosses, which is the only version of it that respects the read-only rule instead of routing round it.

**Poll it from a session left open:**

```
/loop 25m Run `python scripts/osint-cycle-ready.py --claim`. On exit 0, run CYCLE.md end to
end and finish with `python scripts/osint-cycle-ready.py --done`. On exit 1, stop and say
nothing. On exit 2, write one block in logs/messages-for-bill.md and stop — do not re-run.
```

**Every close fires, and there is no minimum interval** *(Bill, 2026-08-20: "until everything is automated i may well be running sweep-cycle twice a day. If I do it is my responsibility to ensure that i don't interfere with your protocol.")*. Each close is a night's evidence genuinely landed in `raw/`, so each earns a build.

**The poll is started against a cycle, not left running** *(Bill, 2026-08-22)*. He starts `/loop` when he initiates `SWEEP-CYCLE`, so the only OSINT commits inside the poll's life are that cycle's own — and the trigger does not fire until its close, by which point OSINT is finished. That matters now in a way it did not before: **OSINT mirrors after every commit as of 2026-08-22**, so `C:\OSINT` is refreshed throughout its working day rather than once at the end of a night, and a poll left running across a housekeeping morning could start a build over a tree that then moves under it. The discipline is what keeps the two apart, and it costs nothing because a cycle is the only thing a poll is waiting for anyway.

**The mechanical half is guarded regardless**, which is why this is a discipline rather than a lock. `report-render.py` recomputes the catalogue's stamp — records and newest mtime — and raises `vault_lib.StaleCatalogue` rather than rendering the report layer against a base that has moved since stage 2. So a slip costs a stopped run naming its own repair, not a bad publish. `wiki/` has no equivalent check, but that path is model authoring and the next cycle covers it.

**`logs/.hold-cycle` is the switch to flip before sitting down to work.** While it exists the trigger holds — as it does for `logs/.build-in-progress` and for uncommitted tracked changes — and **it does not advance the watermark**, so the close it held over runs when the file comes out rather than being skipped.

**`--skip` passes a close over without building it, and loses nothing.** `BUILD.md` works off a set difference over slugs rather than a window, so the next close covers a skipped one whole — the only cost is the delay. It is what to run when a night's catch does not earn a cycle, and when a close is superseded by a cycle starting now, where firing would put a build and OSINT's writes over `raw/` at the same moment.

**The trigger answers *is a cycle owed*, and since 2026-08-21 its quiet answer also says how far the base has moved.** On that afternoon it printed `nothing new — newest close 00:14 (day 1) already built` while OSINT's housekeeping had moved 205 files under it: 38 duplicate records retired, an OCR layer put on every image-only PDF in `raw/`, `pdftotext` re-run under UTF-8. All 38 were cited in Corpus's published layer and `report-render.py`'s check M was already failing on three, so the cycle Bill asked for by hand had real work to do. The trigger was right that nothing was owed and unhelpful about whether one was wanted, and answering that took a hand-written diff against `git log`. It now appends the file counts and the commit range to that line.

**It reports; it does not fire on them, and that is not a gap to close later.** A second condition on base movement was considered and rejected: OSINT commits to `raw/` all through its own working day, so a movement trigger would fire mid-session repeatedly — the exact failure the closed-row discriminator was chosen to avoid, and a size threshold only delays it. The close row stays the only thing that starts a cycle, the exit codes are untouched, and a `/loop` still stops silently on exit 1. What changed is that a person asking the question gets the answer from the same command.

**A cycle run by hand need not call `--done`, and the cost of not doing so is one redundant cycle.** That is deliberate rather than tolerated: *Running unattended* above already establishes that a second whole cycle finds nothing unconsidered, prints `unchanged` across the tree and costs almost nothing, and that the render is idempotent by construction. Paying that occasionally is cheaper than a trigger that infers what a hand-run did from log lines it cannot date precisely against the close.

**`--claim` before, `--done` after, and a claim that never reported done stops the loop.** A cycle that dies leaves the claim outstanding and the next poll exits 2 — `--release` clears it once someone has looked. A poll loop that re-fired on its own failure every twenty-five minutes would be *a job looping on the fault that stopped it*, which *The seam* refuses for the same reason.

## Handing over at the seam

**The seam is the right place to stop for context, and the only one** *(2026-08-17)*. BUILD stage 4 is model authoring across forty-odd units and the log shows it running from twenty minutes to three hours; a session that has just done that has spent a great deal of what it has, and the render half is nine steps of scripted work that deserves a session with room to read its own output.

There is nothing to hand over but the instruction. The build has committed everything, written its line and removed its sentinel, so a fresh session running `RENDER.md` from Step 0 is in exactly the position the cycle would have been in — that is what *the seam is a job boundary* means in practice. **Stopping at the seam is a completed build, not an abandoned cycle**, and it is a better outcome than a render half-run out of context at Step 5.

Anywhere else, do not stop deliberately. Inside stage 4 an interruption is survivable but invisible, which is what the sentinel exists to make visible; inside the render half it leaves `site/` part-written and undeployed.

## Running the halves separately

**Unchanged, and this file is not involved.** `BUILD.md` and `RENDER.md` each stand alone exactly as they did: hand over either one on its own and run it as written, with no reference to the cycle. A separate `RENDER.md` run reads its Step 0 the way that step describes — a gate on a build somebody else ran, whose repair is to run BUILD.

**Nothing in either runbook was changed to make the cycle possible**, beyond a pointer at the top of each saying this file exists. That is the test of whether combining them was a real simplification or a rearrangement: if the combined form had needed either half altered, the halves were not separable and the seam was not where this file claims it is.

## Boundary

Nothing in either half writes to OSINT, and neither does this. `C:\OSINT` is read-only from Corpus without exception — `CLAUDE.md` has the rule and the reasoning.
