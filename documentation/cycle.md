---
type: doc
reader: cc
title: cycle.md — why the cycle is ordered as it is
last_reviewed: 2026-10-03
---

# The cycle — why each rule in `CYCLE.md` is there

`CYCLE.md` is what to run. This file is why: the reasoning behind each of its rules, moved out on 2026-10-03 so the runbook holds the steps and nothing else. A rule changed there is changed here in the same commit.

## Why the cycle is a driver and not a third runbook

A combined file that restated `BUILD.md` or `RENDER.md` would drift from its original silently, leaving an unattended run two instructions on one step and no way to rule between them. So nothing bridges the halves: no state is passed but the committed tree, and there is no work at the seam but the unit review, which has its own runbook. The cycle drives four jobs rather than two — the notes drain and the unit review are jobs whose *placement* the cycle fixes, and whose own rules stay where they already live.

Each runbook stands alone exactly as written; nothing in either was changed to make the cycle possible beyond a pointer to it. That is the test of the seam: if the combined form had needed either half altered, the halves were not separable.

## Why running the halves together is better than running them apart

- **The bulletin.** BUILD stage 7 writes it over a two-day publication window; a render a day later publishes a window the site is no longer in — well-formed, and invisible downstream.
- **`BUILT-FROM` gets tighter for free**: in a cycle, the stamped HEAD is the build's own final commit.
- **One mirror covers both halves.** RENDER's *Mirror* captures the build's `outputs/` and the render's `site/` in one pass; a build never followed by a render is not backed up until one is.

## Why the notes drain runs first

Every open note names in its `Affects:` line the artefact it bears on — usually something the cycle is about to rebuild. Drained first, the fix is in tonight's build; drained after, or not at all, it waits for the next close, and a note that waits a cycle is indistinguishable from one nobody read. The drain used to happen when Bill said so, which meant it happened when he remembered; a close is the one event that reliably recurs.

A note left open by a drain is a note still queued, which is where it started — which is why a note too large for the run, or one that fails, does not hold the cycle.

## Why a cycle ignores what OSINT sends after it has started

OSINT works in its own session on its own drive and mirrors after every commit, so a daytime cycle runs beside a tree that is moving. It used to lose that race: `report-render.py` compared a count and a high-water mtime over `raw/` and stopped the run on *any* movement, so one record landing during the fifty minutes a cycle takes ended it — a record that could not have affected anything.

The three ways `raw/` can move are not one thing. A record deleted leaves the catalogue resolving a slug the base no longer holds. A record changed may leave the catalogue's URL for it wrong, and a stale table does not fail, it answers wrongly. A record added is not in the catalogue, so nothing resolves through it, and nothing in `outputs/` can cite a source that did not exist when the prose was written.

`report-render._assert_catalogue_current` counts the records at or below the stamp's own high-water mark, which answers that exactly: a deletion or an edit moves a record out of that population, an addition never enters it. There is no pin file and no second clock — the pin cannot drift from the thing it pins because it *is* that thing. `scripts/test_catalogue_pin.py` holds it down, including the case that makes the shape necessary: one record deleted and one arrived leaves `raw/` holding the same number of files it held at the build, which a plain count would pass.

This does not freeze the tree at step 1. A record arriving between the drain and stage 2 is built like any other; the cycle is consistent from stage 2 onward, which is what the render half needs.

## Why the seam has no repair

BUILD's ending sequence leaves the tree in exactly the state `RENDER.md` Step 0 tests for — everything committed, a non-error build line, no sentinel. The cycle does not weld the halves; it runs the second at the point where the first has finished saying so. A retry inside the same run is a job looping on the fault that stopped it, so a seam stop ends the cycle. The build's work is committed and logged, and a plain `RENDER.md` run finishes it later.

A build with no render is a stale site, not a broken one — the previous render is still served.

## Why the log and the sentinel are left alone

There is no `· **CYCLE** ·` job name because `lint-mirror-freshness.py` finds the newest render line, Step 0 greps for the build line, and per-half durations stay comparable. A cycle is indistinguishable in the log from two runs an hour apart, which is correct.

The two message blocks are written by the half that owes each, when it owes it: held back and merged, the build half's message dies with a seam stop.

There is no cycle sentinel. A cycle that dies during the render half has already stood down its build; the repair is a render — or another whole cycle, whose build half finds nothing unconsidered and costs almost nothing. The render is idempotent, so re-running it is never the wrong move.

## Why the trigger reads the closed row

`SWEEP-CYCLE` writes the row's `End` into `cycle-manifest.json` as `rotation.newest_close.end` and commits *before* it mirrors, so that stamp advances on a close and nothing else, and reading a new one from the mirror is itself the proof the mirror carried it.

- **Every close fires, with no minimum interval**, because each close is a night's evidence landed in `raw/`.
- **The poll is started against a cycle, not left running.** Bill starts `/loop` when he initiates `SWEEP-CYCLE`, so the only OSINT commits inside the poll's life are that cycle's own. A poll left running across a housekeeping morning could start a build over a tree that moves under it. The mechanical half is guarded regardless — `report-render.py` raises `vault_lib.StaleCatalogue` rather than rendering against a moved base — so a slip costs a stopped run naming its own repair, not a bad publish.
- **`--skip` loses nothing** because BUILD works off a set difference: the next close covers a skipped one whole.
- **The quiet answer says how far the base has moved** because *nothing owed* and *nothing wanted* are different questions. It fires only on the close row: a base-movement trigger would fire mid-session repeatedly, and a size threshold only delays that. What it cannot tell apart — *OSINT has not run* from *the mirror has not carried what it ran* — `scripts/lint-osint-freshness.py` measures at BUILD stage 0.
- **A hand-run cycle need not call `--done`**: the cost is one redundant cycle, cheaper than a trigger inferring what a hand-run did from log lines.
- **A claim that never reported done stops the loop**, because a loop that re-fired on its own failure would be a job looping on the fault that stopped it.

## Why the seam is the place to hand over

BUILD stage 4 is model authoring across forty-odd units; the render half deserves a session with room to read its own output. There is nothing to hand over but the instruction — a fresh session running `RENDER.md` from Step 0 is in exactly the position the cycle would have been in. Anywhere else an interruption costs something: inside stage 4 it is survivable but invisible; inside the render half it leaves `site/` part-written and undeployed.
