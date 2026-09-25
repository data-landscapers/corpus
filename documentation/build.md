---
type: doc
reader: cc
title: The build — why each stage is where it is
last_reviewed: 2026-09-20
---

# The build — why each stage is where it is

*(Spec for `BUILD.md`. The runbook says what to run and what rule to obey while running it; this says why, and what each check exists to catch. Split out 2026-09-20, strategic review 4 R60, on the pattern of `documentation/render.md`. **Where another file already owns an argument this points at it** rather than repeating it: `report-layer.md` for the record layer, `considered-not-carried.md` for the defect that corrected stage 4, `STATUS-INIT.md` for how a baseline section is written, `bulletin.md` and `topic-reports.md` for those two stages' designs, `design.md` for the source-body rule and its retired gate.)*

## Why nothing here is a gate

Job 1 runs unattended, back to back with Job 2. A procedure that stops to ask is a procedure that stops, and a build that stops has left `outputs/` half-moved with nothing downstream able to see it.

So **every check is a work list**. A check that blocked would have to be cleared by somebody, and there is nobody; it would convert a finished-but-imperfect build into an unfinished one, which is strictly worse, because the imperfection is *stated* and the unfinished build is not. The fallback is always a completed outcome: ***Not held*** with a `gaps.csv` line says the true thing about a position that cannot be sourced, and a reader can act on it.

**The same reasoning makes BUILD the editor rather than the transcriber.** `report-scan.py` exists so a build does not re-read what it has read; it is not a work order. What is *published* and what it *costs* are Bill's questions — not what a sentence should say.

## Stage 0 — the lints, and the sentinel

**The freshness lint does not gate** because the sweep cycle is run by hand: a quiet stretch is OSINT's schedule, and the repair runs on OSINT's machine. Its own header describes the three clocks it reads; the part worth stating here is the fourth test, against the `done` watermark in `logs/.osint-cycle-seen` — **a mirror gone backwards is fresh by every clock and wrong by every record**, which no age test can see.

**The interface lint reads Corpus's own source and nothing of OSINT's**, so it costs nothing and can run before the evidence is touched. **The notes lint checks the open queue, not the run**: a note is written *between* builds, and nothing else would look at it before the next one.

**`--start build` stamps the clock** into the gitignored `logs/.run-start-build`; the closing call reads it back and clears it, and a run that skipped it logs `unclocked`.

**The sentinel is a statement about this machine at this moment, not history** — hence gitignored. Written at stage 0, removed in the ending sequence on a clean finish *and* on a logged error, because both reported themselves. What it survives is the one thing nothing else detects: a session that died without saying so. `documentation/render.md` → *Step 0* has the other half.

## Stages 1–3 — why stage 2 is a precondition, and also the pin

The report layer resolves every citation through `outputs/catalogue/catalogue-internal.csv` — the download's rows with the slug still on them, which is what a citation resolves *by* and is deliberately not a published column. A report therefore cannot be rendered against a catalogue older than the evidence, and `report-render.py` refuses one.

**"Older" means a record deleted or edited since the catalogue was built — not one added since.** A record that arrived afterwards is not listed and nothing can cite it, so it cannot make a document wrong; it can only make it incomplete, which the next run fixes. That asymmetry is what lets a build run while OSINT works beside it (`CYCLE.md` → *A cycle ignores what OSINT sends after it has started*).

## Stage 2a — why the scope lint notices rather than enforces

The remit rule is a reading of a body, and a lint cannot read. So `lint-scope.py` sorts rather than judges, and its three buckets are three different questions: **in** needs nothing; **XGL unverified** is admissible *if it earns the code*, which is exactly the reading a lint cannot do; and **unaccounted** is a **review list, not a delete list**, because it holds African stories with an empty `places` field alongside genuinely out-of-remit records.

**Clearing a deletion is the expensive half**, which is why the runbook asks for the layers to be named: a deleted record can be cited from a ledger, from a status baseline, and from OSINT's own `wiki/`, and a bare *nothing found* does not say which were looked at.

## Stage 4 — the correction that matters most

**The default outcome was read for two years as though it were about the source, and it is about the ledger.** *Nothing moves* means *this does not move a position the ledger already holds*. Where the ledger holds no position on the thing a source names, the source is not reporting activity on a row — it is the first record of a row.

The cost of the other reading was **467 false *No evidence* rows across 22 units**, and it is silent: a source read and defaulted leaves no trace anywhere — no row, no mapping, no baseline sentence — and step 4 then marks it so nothing ever reads it again. `considered-not-carried.md` is the defect in full and `REREAD.md` the repair loop.

**Mapping is part of the move, not a separate job.** The progress report renders from `indicators.csv`, so a ledger the build moves and an `indicators.csv` it does not leaves that document stating a position the base no longer holds. Checks I and L test the frame's own consistency, not whether the mapping was done.

**The three authoring rules in step 5 are stated where the writing happens**, because each fails invisibly. A citation on a summary block's opening sentence does not source the three that follow. The window selects rows by the publication date of the newest record they cite, so a July source restating a 2023 measurement puts its row in the monthly while the measurement belongs in the status report. And a carried narrative sentence describing a period that has moved on **passes every check** — finding it is the point of the revision.

**"Residue" is outcomes converted, never work deferred.** The counts in a log line are *Not held* rows written and claims struck — things the pass finished by stating them. A finding the pass could have cleared and did not is neither a finished outcome nor residue; it is unfinished work, and a run has no way to hand it on.

**Check J skips the status report on an initialised unit**, because the baseline is not rendered from the ledger: its sources are largely ones the wiki does not hold, so currency is step 3's question, answered by revising the section rather than re-rendering the file.

## The status baseline — why it is never re-rendered

The baseline is **authored**, from sources the wiki does not hold. A rebuild from the ledger would not update it but **destroy it, while reporting a normal successful build** — which is why `report-render.py` narrows the document set rather than leaving the choice to whoever types the command. `STATUS-INIT.md` owns how a section is written; three things are the maintenance's own:

- **Most sources are relevant and change nothing**, and that is the normal outcome. The question is whether a source changes what a sub-section can *say*, not whether it bears on one.
- **A borderline source changes nothing** because the baseline is what BUILD reads every subsequent source against: an error written into it corrupts the judgement that decides what enters next.
- **A failing revision is reverted, not repaired.** Check A is set membership, and a URL synthesised from a remembered pattern is invisible until something tests it — **an unverifiable link left standing is a fabricated citation in a document a reader can download**. The last good baseline at `HEAD` is the safe state. C to F, H and I describe the prose rather than the evidence, so they are repaired in place.

**The register allows more than the ledger holds** (`report-layer.md` §10). Event detail that is deliberately not a ledger position belongs in the prose with its citation attached: the ledger is one route to a source, not the definition of one.

## Narrative integrity — why it is BUILD's and not RENDER's

**The renderer mints no placeholder and clears nothing.** It carries block bodies across verbatim, because deleting an author's content is not a script's decision, and check L's count is a tally for the author rather than a gate on someone else's behalf.

Integrity is maintained where the prose is written. A check in RENDER would be a second, weaker copy of a judgement already made, applied by a job with no way to write the missing sentence. **Empty sections do not arise**: the renderer prints no heading for a section with nothing in it, and only the status report states an absence, in a sentence it writes itself.

## Stages 5 and 6

**Stage 5 always runs** because whether something changed underneath the documents is exactly what an unattended run cannot be sure of. It costs nothing — an agreeing unit prints `unchanged` — and it issues no rendered status report for an initialised unit, so a format change reaches the monthlies and progress reports and leaves the baselines alone.

**Stage 6's ordering is its integrity mechanism.** A topic document derived from a place document stage 4 has not moved is stale in a way nothing downstream can detect, so stages 4 and 5 are a precondition in the same run and there is no check for it beyond the ordering. Check G and nothing else: the ledger checks belong to the place documents, and there is no topic ledger. Design note: `topic-reports.md`.

## Stage 7 — why the bulletin is its own stage

**Stage 4 iterates by unit over a set difference**, so an item already considered is never reopened and an item with no place is in no unit's scope. A bulletin riding inside stage 4 would drop exactly the items a two-day window is most likely to hold. Its only precondition is stage 2. `bulletin.md` owns the window, the summary store and the rest of the design.

**A sweep that published nothing into the window has still updated the bulletin.** The *Last updated* stamp is OSINT's stated close of collection, read from the mirror's cycle manifest; `render.py`'s digest is the body, which the stamp is not in, so a moved clock refreshes the page without minting an edition and the dated PDF keeps the stamp it was cut with. `--assemble` compares the whole file, so it writes nothing when nothing at all has moved, the clock included.

## The ending sequence — why the estate-wide run is at the end

**Every other check in Job 1 runs per unit, on the units the pass worked** — so a finding in a unit nobody touched is reported to nobody, and accumulates. The first time the estate-wide run was made it found **203 register hits over 54 files**, two progress reports outside their word band and one indicator cell, none of it in any log line or message.

`lint-considered.py` runs here for the same reason *(2026-09-17, R13)*: it is the one query that would have caught the 467 rows — a source marked considered, over an indicator the report says the base holds nothing on, cited by no ledger row. The repair is done and it reads clean; it runs estate-wide from here **so that it goes on being read after everyone has forgotten what it was for**. It is a disclosure the run computes rather than one the operator has to remember, and it is not a gate.

**The sentinel comes off after the commit, never before.** Removing it earlier opens a window in which RENDER sees a finished build whose work is uncommitted. **On failure the word is `errored`**, because `RENDER.md` Step 0 matches that word: a failure line phrased any other way reads downstream as a success.

## Source bodies, and the deferred stages

`design.md` §8 carries the rule and the argument for retiring its gate. What follows for BUILD is that the rule is the drafter's, at the moment of writing, and that *Narrative integrity* and the register are where a lifted sentence is caught.

**Report initialisation from the wiki** is deferred: `report-country-init.py` is the shell, the authoring is a session's model work, and the current ledgers are the accepted baseline. **Monthly narratives** — some monthly issues carry empty per-subject blocks, and authoring them is tracked.
