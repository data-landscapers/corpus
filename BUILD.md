---
type: runbook
title: Job 1 — build outputs/ from OSINT — instruction for Claude Code
last_reviewed: 2026-08-28
---

# Job 1 — build the outputs — runbook for Claude Code

*(Job 1 turns OSINT's evidence into Corpus-owned `outputs/`. Job 2 (`RENDER.md`) renders `outputs/` into the site; `CYCLE.md` orders the two and changes nothing in either. `documentation/report-layer.md` is the record layer stage 4 works to. OSINT is read-only throughout; reading is unrestricted. The workroot junctions `raw/`, `wiki/` and `lookups/` — only what a stage reads — and `index/` is not among them: Corpus builds its own. The boundary is the write, and it is absolute.)*

## Running unattended — a run never stops to ask

**BUILD puts no question mid-stream.** It runs back to back with RENDER with nobody watching. A run ends exactly two ways: it **finishes**, or it **fails** — an error the run cannot get past, never a decision it would rather Bill made.

**Where this runbook says a human rules, BUILD rules.** Every such point is named below with the path to take. **Where BUILD wants Bill's attention, it finishes the job and leaves a message** in `logs/messages-for-bill.md`: what would have been asked, what the run did instead, what his options are. A run that needed nothing writes nothing there, which is the normal outcome.

**No check stops a finished run.** Every check in Job 1 is a work list, not a gate. A failing check is BUILD's work to do, and where it cannot be done the true statement is ***Not held*** with a `gaps.csv` line — a completed outcome, not a blocked one.

**An interrupted run is resumable.** Stage 4 reads a set difference over slugs, so a dead run leaves every finished unit marked and the next run picks up exactly there. The danger is the interruption going unnoticed — a half-moved build typesets cleanly and passes every check — which is what stage 0's sentinel is for.

## The two kinds of work in Job 1

The **compiles** (vocab, catalogue, finance, budgets) are pure functions of OSINT's `raw/` and `lookups/`: `scripts/rebuild.py`, and they just run. The **report update** is a model stage: `report-scan.py` says *which* sources are new; a model reads them and decides what moves.

**BUILD authors this content; it does not transcribe it.** BUILD holds editorial control over everything in `outputs/`. The scan is a convenience that stops the build re-reading what it has read — not a work order BUILD is confined to. Where a document can be made better, BUILD makes it better. Questions about what is published and what it costs are Bill's.

## Prerequisites

- The OSINT mirror readable at `C:\OSINT` (`CORPUS_OSINT_MIRROR` overrides; `rebuild.py` also honours `OSINT_PATH`). It is a **mirror**, synced as `SWEEP-CYCLE`'s last act — stage 0's freshness check reports how old this copy is.
- Run from the repo root. Commit after each coherent stage.
- **The index is Corpus's own**: built into the gitignored `scripts/.workroot/index/` from `raw/` and `wiki/`, rebuilt whenever either moves (~5 seconds). Stages 4 and 5 run **from `scripts/.workroot/`**, where `raw/` and `wiki/` resolve; `vault_lib.ForeignIndex` or `EmptyIndex` means the run started from the wrong root.

## Stage 0 — declare the run

```bash
python -c "import datetime,io; io.open('logs/.build-in-progress','w',encoding='utf-8').write('started {:%Y-%m-%d %H:%M}\n'.format(datetime.datetime.now()))"
python scripts/log-line.py --start build
python scripts/lint-osint-freshness.py    # 0 fresh · 1 stale or regressed · 2 nothing readable
```

**The freshness lint says how old the evidence is, and does not stop the run.** It reads three clocks off the mirror — last ingest, the rotation table's newest `End`, the mirror's `HEAD` commit date — and reports the newest. It also catches a mirror gone *backwards*, against the `done` watermark in `logs/.osint-cycle-seen`: a rollback is fresh by every clock and wrong by every record. A `STALE` or `UNREADABLE` line (ceiling `--max-age-hours`, default 72) goes in the run's message to Bill and the build continues — a cycle is run by hand, so a quiet stretch is OSINT's schedule, and the repair (FreeFileSync on OSINT's machine) is not Corpus's to run.

**`--start build` stamps the clock** into the gitignored `logs/.run-start-build`; the closing call reads it back and clears it. A run that skips it logs `unclocked`. A resumed run re-stamps, so its duration is that sitting — say in the log line that it resumed, and use `--since` on the closing call where the whole-job figure is the one worth having.

**The sentinel `logs/.build-in-progress` exists for exactly as long as a run is unaccounted for.** Written here, removed in the ending sequence — on a clean finish *and* on a logged error, because both reported themselves. What it survives is a session that dies without saying so. `RENDER.md` Step 0 refuses to render while it is present. It is gitignored: a statement about this machine at this moment, not history.

## Stages 1–3 — the compiles (scripted)

```bash
python scripts/rebuild.py --all        # vocab snapshot + catalogue + finance/budgets + the scan work order
```

Writes `outputs/catalogue/`, `outputs/non-state-finance/`, `outputs/budgets/`, refreshes `outputs/vocab/`, and prints the stage-4 work order. Commit `outputs/` and `outputs/vocab/`.

**Stage 2 is a precondition of stages 4 and 5.** The report layer resolves every citation through `outputs/catalogue/raw-catalogue.csv`; `report-render.py` refuses a catalogue older than `raw/` (`vault_lib.StaleCatalogue`), and the repair is to run this stage first. `--all` satisfies it in the right order.

### Stage 2a — the scope lint

**The remit is Africa, and non-African material is admissible in exactly two cases**: a **sovereignty** issue filing under a closed `geopol.*` slug, and material treating the **global south generally** (`XGL`). A single non-African country's domestic story is out however good it is.

**Applying the rule is OSINT's job; Corpus cannot do it.** `scripts/lint-scope.py` **notices rather than enforces**, sorting every catalogue record three ways: **in** (African place, or a `geopol.*` tag), **XGL unverified** (placed `XGL`, no `geopol.*` tag — admissible if it earns the code, a reading of the body a lint cannot do), and **unaccounted** (none of the above). **The unaccounted bucket is a review list, not a delete list**: it holds African stories with an empty `places` field alongside genuinely out-of-remit records, and the answer per record — delete, place, or code `XGL` — is OSINT's call.

**It reports and never gates.** Carry the counts in the run's log line; where the arrivals are new, write a note for OSINT.

**Clearing a deletion means checking every layer Corpus writes *and* every layer it reads**: `outputs/reports/*/ledger.csv`, the status baselines, and OSINT's `wiki/`. Say which layers were searched rather than reporting a bare *nothing found*.

```bash
python scripts/lint-scope.py --since {last build's date}   # what the last sweep sent
python scripts/lint-scope.py                               # the whole backlog
```

`--since` reads `ingested`, not `published` — a 2019 paper ingested last night is a new arrival.

## Stage 4 — report update (the ledgers' move; model authoring)

`documentation/report-layer.md` is the spec. This stage reads only the sources the ledger has **not** yet considered — a set difference over slugs — so an interrupted run resumes cleanly. The work order (from `--all`, or `python scripts/rebuild.py --scan`) lists each initialised unit and its unconsidered count. For **each** unit:

1. **List the new slugs.** `python scripts/report-scan.py --slugs {ISO3}` (from `scripts/.workroot/`). Read each slug's `hub_line`, facets, and body only where the line is not enough.
2. **Decide per source, against `outputs/reports/{ISO3}/ledger.csv`** (`report-layer.md` §1 for the row test, §3 for the vocabularies) — four outcomes:
   - *moves a row* — set `movement`, put the slug **first** in `sources` (the renderer links the claim cell to the first source that resolves, so appending would link the reader to the old evidence for the new position), and set `published` to the record's publication date — the date at the front of its slug — since `published` is what ages the row out of a report;
   - *mints a row* — a named system or instrument the ledger lacks, passing the row test;
   - *settles a **Not held** row* — strike it from `gaps.csv`, give it a status;
   - *default: nothing moves* — most sources report activity, not movement. Do **not** attach a slug to a row that did not move.
3. **Ask the same source the baseline question** — see *Maintaining the status baseline* below. Asked of the record already open, independent of step 2.
4. **Mark every slug read**, moved or not: `python scripts/report-scan.py --mark {ISO3} <slugs>`. (Sources on `origin_status: hold` are dropped by the script — pass them in regardless.)
5. **Rebuild the unit's documents**: `--doc all`. The renderer decides which documents the unit issues — a region issues the progress report only; a unit whose status report carries `built_by: STATUS-INIT` does not issue a rendered status report — so this line is the same on every unit. A build that changes nothing prints `unchanged`.

   **No fact is added without a source.** The citation goes on the sentence carrying the fact — a linked opening sentence does not source the three that follow. Three kinds of sentence rightly carry no link: a statement of what the base does **not** hold; a qualification of a fact already cited in the same sentence; and the single connecting sentence the register allows. A summary block is where this goes wrong most easily.

   **A source being in scope does not make every fact in it in scope.** The window selects *rows*, by the publication date of the newest record they cite; it does not select *facts*. A July source restating a 2023 measurement puts its row in the monthly, and the 2023 measurement still belongs in the status report, not in a report of what moved this month. Where the standing position is all a row offers, leave it out of the prose and let the ledger carry it.

   **Moving a window on is an editing job.** The renderer carries every narrative block across; BUILD removes what has aged out and writes in what has arrived. A carried sentence describing a period that has moved on passes every check; finding it is the point of the revision.
6. **Verify before moving on**: `python scripts/report-render.py --unit {ISO3} --check` — G (every link resolves through the catalogue), I (vocabulary), J (no document compiled before the ledger moved), L (no unwritten narrative block), M (every stated position cites a source that resolves) — then `python scripts/report-register-check.py --unit {ISO3}`.

   **A failing check is work, and BUILD does it in the same pass.** G, I, J and M are mechanical: each has one repair and BUILD makes it. L is authoring work: write the sentence or remove the section (*Narrative integrity* below). Where a check cannot be cleared, the fallback is a finished outcome: an unsourceable position is ***Not held*** with a `gaps.csv` line; a link resolving to nothing is struck along with the claim standing on it. The residue goes in the run's log line as counts.

   **The register check reports and BUILD rules.** A hit inside quoted source text stands; a hit in BUILD's own prose is rewritten. Message Bill only if clearing a hit would drop a fact the report needs.

   Check J skips the status report on an initialised unit: the baseline is not rendered from the ledger — its sources are largely ones the wiki does not hold — so currency is step 3's question, answered by revising the section, not re-rendering the file.

## Maintaining the status baseline

**On an initialised unit the status report is BUILD's to keep current, and BUILD never re-renders it.** The baseline is authored, drawing on sources the wiki does not hold; a rebuild from the ledger would not update it but destroy it, while reporting a normal successful build. `report-render.py` therefore narrows the document set on an initialised unit and `--doc all` no longer includes status.

**It is one more question asked of a record already open, not a stage**: does this source change what a sub-section can say — not whether it is relevant to one. Most sources are relevant and change nothing; that is the normal outcome. The baseline changes in two cases: the position it states is no longer the position the source establishes, or the baseline says nothing can be established and now something can.

**Where it changes, revise that one sub-section in place**, edited as prose:

- **The superseded fact comes out.** A revision replaces; it does not append — a baseline that accumulates is an archive, which is the decay the baseline exists to prevent.
- **A borderline source changes nothing.** `STATUS-INIT.md` → *When the evidence is borderline* governs; the baseline is what BUILD reads every subsequent source against, so an error written into it corrupts the judgement that decides what enters next. Where two accounts of equal tier conflict, the section stands.
- **The first sentence may have to change.** `STATUS-INIT.md` → *Writing* is in force: the opening sentence carries the best-evidenced news, so a revision that changes what is newest changes the opening line.
- **No apparatus.** A maintained section is indistinguishable from an initialised one; every time-varying figure dated; no changelog.
- **The citation resolves by construction** — the source arrived through the daily flow, so it is in `raw/` and the catalogue.
- **No acquire line is ever written here.** The exchange feed reports material the daily sweep should have caught and did not; a source reaching BUILD has by definition been caught.

**Frontmatter.** Move `compiled:` to the date of the edit, only when the document changed. Update `sources_cited`. Leave `built_by`, `hub_last_reviewed` and `intersections_read` alone: they date the initialisation and stay true of it.

**Verification.** `python scripts/status-check.py --unit {ISO3}` (`STATUS-INIT.md` → *Verification*, A to I), re-run **after the edit pass** — check A is set membership, and a URL synthesised from a remembered pattern is invisible until something tests it. `report-render.py --check` covers the other two documents and applies check G to the baseline too; run both.

**A revision that cannot pass does not stand.** Commit the unit's other work before the baseline edit pass, so the last good baseline is at `HEAD`. A failing A, B or G is repaired first; if it still fails, revert the file, re-run `status-check.py`, and write the message saying which source prompted the edit and why it could not pass — an unverifiable link left standing is a fabricated citation in a document a reader can download. C to F, H and I are repaired in place and never trigger a revert.

**Every piece of evidence has a source.** Absolute, and not a property of the checks — they only find where it has been broken. A position that cannot be sourced is ***Not held*** with a `gaps.csv` line, never a bare status standing on nothing. `report-layer.md` §6 has the rule and the single exemption.

Commit the moved ledgers, `considered.txt`, `gaps.csv` and re-rendered docs.

**The Corpus register governs the narrative** (`report-layer.md` §10): light touch, evidence-led, the lens carried mostly by selection, at most one plain connecting sentence per section, and no figure a reader cannot get to a source for — which is not the same as no figure beyond the ledger. Event detail that is deliberately not a ledger position belongs in the prose with its citation attached; the ledger is one route to a source, not the definition of one.

## Narrative integrity — BUILD owns what is fit to publish

**No document may leave BUILD carrying an unwritten narrative block.** Where a block has no prose, BUILD does one of two things, never a third: **remove the section**, or **write the sentence that explains why there is no suitable narrative** — the ledger holds no movement this period, the evidence is too thin to connect. Stating the absence is evidence-led reporting, the same discipline as publishing a *Not held* count.

The renderer mints no placeholder and clears nothing — it carries block bodies across verbatim, because deleting an author's content is not a script's decision. `report-render.py --check` counts empty blocks (check L) so BUILD can see the work; the count is a tally, not a gate on someone else's behalf.

**Empty sections do not arise here.** The renderer prints no heading for a section or sub-section with nothing in it (monthly, progress); only the status report states an absence, in a sentence it writes itself.

**RENDER does not check this and must not.** Integrity is maintained where the prose is written, not where it is typeset.

## Stage 5 — re-render (mechanical, always run)

```bash
python scripts/rebuild.py --reports all      # rebuild every report's tables from its ledger, carry narrative across
```

**Run it every time.** Whether something changed underneath the documents is exactly what an unattended run cannot be sure of. It is idempotent and cheap: an agreeing unit prints `unchanged` and is not touched. Safe over every unit — it goes through `report-render.py --doc all`, which does not issue a rendered status report for an initialised unit, so a format change reaches the monthlies and progress reports and leaves the baselines untouched.

## Stage 6 — topic reports (derived from the place documents)

```bash
python scripts/topic-render.py            # 38 slugs, two documents each -> outputs/topics/
python scripts/topic-render.py --check    # check G over what it wrote
```

Each Level-2 taxonomy slug issues `outputs/topics/{slug}/{slug}-monthly.md` and `{slug}-progress.md`, whose sections are places in alphabetical order, carrying that place's own material for that subject. Design note: `documentation/topic-reports.md`.

**Precondition: stages 4 and 5 first, in the same run.** A topic document derived from a place document stage 4 has not moved is stale in a way nothing downstream can detect. The ordering *is* the integrity mechanism.

**Nothing is authored here.** The monthly carries every `{section}--{subject}` narrative block a place holds; the progress report carries the subject's movement table and no prose. The one thing the script writes is the standing provenance line under each H1. It is a script, not a model stage: idempotent, and it never edits a place document. **Check G and nothing else** — the ledger checks belong to the place documents; there is no topic ledger and there is not meant to be one.

Commit the topic tree.

## Stage 7 — the bulletin (window select; model authoring)

One document over a two-day window: `outputs/bulletins/corpus-bulletin.md`, published at `/bulletin/`. Design note: `documentation/bulletin.md`. **This stage also runs on its own at midday** — `BULLETIN-TOPUP.md` is that run: this stage, one render, no sentinel, and the cycle trigger deliberately does not fire on it.

```bash
python scripts/bulletin.py --scan          # the window, and which items still need a summary
```

For **each** item in the work order, read it — `raw/{year}/{slug}.md` from `scripts/.workroot/`, `hub_line` first, body only where the line is not enough — and write one to three sentences:

```bash
python scripts/bulletin.py --write {slug} --text "…"
python scripts/bulletin.py --assemble      # then commit outputs/bulletins/
```

- **The window is publication, not acquisition**: an item is in when its `published` date is today or yesterday. **An empty window is a finished bulletin** — `--assemble` writes the document saying the window was empty and why, because an absent bulletin is indistinguishable from a build that did not run.
- **A summary is written once and kept** in `outputs/bulletins/summaries.json`; `--scan` asks only for what is not in it; entries age out 30 days after publication. The model stage costs one day's news per run, not two.
- **`--assemble` stops rather than publishing a gap**: an item in the window with no summary fails the command and names the slugs. Same rule as *Narrative integrity*, and mechanical.
- **Everything in a summary is sourced by construction** — each entry opens with the item's title linked to the publisher's record. That does not license a fact the item does not carry, and a verbatim sentence lifted from the body is a register failure caught here, at writing time.
- **Detail sits in one place.** An item carrying five topics is summarised once and cross-referenced from the other four; `bulletin.py` lands the summary where the item first appears in the document — the earliest of its topics in taxonomy order, so cross-references point backwards.
- **The sections are `lookups/taxonomy.csv`'s order and labels**, Level-1 groups with Level-2 sections, and a nav bar built from the sections that exist.
- **A sweep that published nothing into the window has still updated the bulletin.** The *Last updated* stamp — OSINT's last ingest, read from the mirror via `scripts/osint_lib.py` — moves whenever the material was looked at; the run reports `checked` rather than `written`. `render.py`'s digest is the body, which the stamp is not in, so a moved clock refreshes the page without minting an edition, and the dated PDF keeps the stamp it was cut with. `--assemble` writes nothing when nothing at all has moved, the clock included — the comparison is the whole file.
- **It is its own stage, not a question inside stage 4**: stage 4 iterates by unit over a set difference, so an item already considered is never reopened and an item with no place is in no unit's scope — a bulletin riding inside it would drop exactly the items a two-day window is most likely to hold. Its only precondition is stage 2.

## Deferred stages — not yet in this build

- **Report initialisation from the wiki** — for a place with no ledger. `report-country-init.py` is the shell; the authoring is a session's model work. The current ledgers are the accepted baseline, so initialisation is not run now.
- **Monthly narratives** — some monthly issues carry empty per-subject blocks; authoring them is tracked.

## Source bodies — the rule outlives its gate

`outputs/` carries metadata and compiled prose only, never a verbatim source body (`documentation/design.md` §8). The leak-check gate is retired — every file in `outputs/` is written by a compiler in this repo — so the rule is the drafter's, at the moment of writing; *Narrative integrity* and the register are where a lifted sentence is caught.

## Ending the run — message, log, commit, stand down

**1. Message Bill, if anything is owed him** — one block under the marker in `logs/messages-for-bill.md`. Nothing owed, nothing written: the normal outcome.

**2. Log one terse line:**

```bash
python scripts/log-line.py build "catalogue N, finance N places, scan N units, K ledgers updated — ok"
```

The duration writes itself from the stage-0 stamp, then clears it. Where the stamp was never taken, state the truth: `--since "…"` or `--took 3h02m`, never a hand-written figure. The script inserts at the top under the marker (the log reads newest first) and exits 1 if the marker is missing.

**3. Commit everything:**

```bash
git add -A && git diff --cached --quiet || git commit -m "Build run: outputs, log and messages"
```

**4. Stand down** — remove the sentinel, and only now, after the commit has landed; removing it earlier opens a window in which RENDER sees a finished build whose work is uncommitted.

```bash
rm -f logs/.build-in-progress
```

**On failure, the word is `errored`.** Log the stage and error in place of the completion line — `… errored at stage 3: <message>` — commit whatever is committable, remove the sentinel, and stop. A logged failure has reported itself; the sentinel is for the run that never got to say anything. `RENDER.md` Step 0 matches the word `errored`, so a failure line phrased around it reads downstream as a success. A failure writes a message only where it left something Bill has to undo; otherwise the log line is the whole report.

## Boundary

Nothing in Job 1 writes to OSINT. The only Corpus→OSINT channel is the exchange folder (`C:\corpus-osint-xfer\`): acquisition rows in `africa-acquire.csv`, numbered notes in `notes-for-osint.md` — files OSINT reads on Bill's schedule, never a write into OSINT itself.
