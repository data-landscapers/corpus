---
type: runbook
reader: cc
title: Job 1 — build outputs/ from OSINT — instruction for Claude Code
last_reviewed: 2026-09-20
---

# Job 1 — build the outputs — runbook for Claude Code

*(Job 1 turns OSINT's evidence into Corpus-owned `outputs/`. Job 2 (`RENDER.md`) renders it into the site; `CYCLE.md` orders the two and changes nothing in either. **`documentation/build.md` is why each stage is where it is and what each check catches**; this file is what to run. Stages 4, 4b and 7 are runbooks of their own: `REPORT-UPDATE.md`, `DATASET-UPDATE.md` and `BULLETIN.md`. OSINT is read-only throughout; reading is unrestricted. The workroot junctions `raw/`, `wiki/` and `lookups/` — only what a stage reads — and `index/` is not among them: Corpus builds its own. The boundary is the write, and it is absolute.)*

## Running unattended — a run never stops to ask

**BUILD puts no question mid-stream.** It runs back to back with RENDER with nobody watching, and ends exactly two ways: it **finishes**, or it **fails** — an error it cannot get past, never a decision it would rather Bill made.

**Where this runbook says a human rules, BUILD rules**, and every such point is named below with the path to take. **Where BUILD wants Bill's attention, it finishes the job and leaves a message** in `C:\corpus-osint-xfer\messages-for-bill.md`: what would have been asked, what the run did instead, what his options are. A run that needed nothing writes nothing there.

**No check stops a finished run.** Every check in Job 1 is a work list, not a gate. A failing check is BUILD's work to do, and where it cannot be done the true statement is ***Not held*** with a `gaps.csv` line — a completed outcome, not a blocked one.

**An interrupted run is resumable**: stage 4 reads a set difference over slugs, so the next run picks up where a dead one stopped. Stage 0's sentinel catches the interruption nobody noticed.

## The two kinds of work in Job 1

The **compiles** (vocab, catalogue, finance, budgets) are pure functions of OSINT's `raw/` and `lookups/` — and, for budgets since 2026-09-20, of Corpus's own `budgets/budgets-{ISO3}.csv` as well *(R54; `BUDGET-EXTRACT.md` writes those, and a country-year in one replaces OSINT's rows for the year)*: `scripts/rebuild.py`, and they just run. The **report update** is a model stage: `report-scan.py` says *which* sources are new; a model reads them and decides what moves.

**BUILD authors this content; it does not transcribe it.** It holds editorial control over everything in `outputs/`, and where a document can be made better it makes it better. The scan is a convenience, not a work order. Questions about what is published and what it costs are Bill's.

## Prerequisites

- The OSINT mirror readable at `C:\OSINT` (`CORPUS_OSINT_MIRROR` overrides; `rebuild.py` also honours `OSINT_PATH`).
- Run from the repo root. Commit after each coherent stage.
- **The index is Corpus's own**, built into the gitignored `scripts/.workroot/index/` and rebuilt whenever `raw/` or `wiki/` moves (~5 seconds). **Stages 4 and 5 run from `scripts/.workroot/`**; `vault_lib.ForeignIndex` or `EmptyIndex` means the run started from the wrong root.

## Stage 0 — declare the run

```bash
python -c "import datetime,io; io.open('logs/.build-in-progress','w',encoding='utf-8').write('started {:%Y-%m-%d %H:%M}\n'.format(datetime.datetime.now()))"
python scripts/log-line.py --start build
python scripts/lint-osint-freshness.py    # 0 fresh · 1 stale or regressed · 2 nothing readable
python scripts/lint-interface.py          # 0 the interface holds · 1 a read outside it
python scripts/lint-notes.py              # 0 every open note names what it bears on
python scripts/lint-prepared.py           # 0 no spent handover is still in prepared/
```

- **The freshness lint reports and never stops the run.** A `STALE` or `UNREADABLE` line goes in the run's message to Bill and the build continues.
- **The interface lint stops a read outside `raw/`, `wiki/`, `lookups/` and the mirror's git metadata** (`CLAUDE.md` → *The OSINT repo is read-only*).
- **The prepared lint says what the share is holding that is already spent.** A handover leaves `prepared/` when the job it was cut for closes; the closure signal is in the share, so this can tell without opening anything of OSINT's. Prune what it names, in the commit that records the close.
- **The notes lint fails on `notes-for-osint.md`**, which Corpus writes, and reports on `notes-for-corpus.md`, which OSINT writes.
- **A resumed run re-stamps the clock**, so its duration is that sitting: say in the log line that it resumed, and use `--since` where the whole-job figure is the one worth having.
- **The sentinel exists for exactly as long as a run is unaccounted for.** `RENDER.md` Step 0 refuses to render while it is present. Never hand-remove it.

## Stages 1–3 — the compiles (scripted)

```bash
python scripts/rebuild.py --all        # vocab snapshot + catalogue + finance/budgets + the scan work order
```

Writes `outputs/catalogue/`, `outputs/non-state-finance/`, `outputs/budgets/`, refreshes `outputs/vocab/`, and prints the stage-4 work order. Commit `outputs/` and `outputs/vocab/`.

**Stage 2 is a precondition of stages 4 and 5.** `report-render.py` refuses a catalogue older than `raw/` (`vault_lib.StaleCatalogue`); `--all` satisfies it in the right order. It is also **the pin**: a record arriving after the catalogue was built is not listed and cannot be cited, so a build can run while OSINT works beside it. The run says how many arrived that it left out.

### Stage 2a — the scope lint

**The remit is Africa, and non-African material is admissible in exactly two cases**: a **sovereignty** issue filing under a closed `geopol.*` slug, and material treating the **global south generally** (`XGL`). A single non-African country's domestic story is out however good it is.

**Applying the rule is OSINT's job; Corpus cannot do it.** `lint-scope.py` sorts every catalogue record three ways — **in**, **XGL unverified**, **unaccounted** — and the unaccounted bucket is a **review list, not a delete list**.

```bash
python scripts/lint-scope.py --since {last build's date}   # what the last sweep sent
python scripts/lint-scope.py                               # the whole backlog
```

`--since` reads `ingested`, not `published`. **It reports and never gates**: carry the counts in the run's log line, and where the arrivals are new, write a note for OSINT. **Clearing a deletion means checking every layer Corpus writes *and* every layer it reads** — the ledgers, the status baselines, and OSINT's `wiki/` — and saying which were searched rather than reporting a bare *nothing found*.

## Stage 4 — report update (the ledgers' move; model authoring)

**`REPORT-UPDATE.md` is the procedure: run it for each initialised unit in the work order** (from `--all`, or `rebuild.py --scan`). It holds the six steps, *Maintaining the status baseline* and *Narrative integrity*; `documentation/report-layer.md` is the spec. Commit the moved ledgers, `considered.txt`, `sections-read.txt`, `gaps.csv` and re-rendered docs.

## Stage 4b — datasets (model authoring)

**`DATASET-UPDATE.md` is the procedure**: the same set difference as stage 4, over the Data Centres dataset instead of a ledger. A night's arrivals are one packet.

## Stage 5 — re-render (mechanical, always run)

```bash
python scripts/rebuild.py --reports all      # rebuild every report's tables from its ledger, carry narrative across
```

**Run it every time.** It is idempotent and cheap: an agreeing unit prints `unchanged` and is not touched, and it issues no rendered status report for an initialised unit.

## Stage 6 — topic reports (derived from the place documents)

```bash
python scripts/topic-render.py            # every slug, two documents each -> outputs/topics/
python scripts/topic-render.py --check    # check G over what it wrote
```

**Precondition: stages 4 and 5 first, in the same run** — the ordering *is* the integrity mechanism. **Nothing is authored here**: it is a script, idempotent, and it never edits a place document. **Check G and nothing else.** Design note: `documentation/topic-reports.md`. Commit the topic tree.

## Stage 7 — the bulletin (window select; model authoring)

**`BULLETIN.md` is the procedure**: one document over the newest day or two of publication, `outputs/bulletins/corpus-bulletin.md`. Its only precondition is stage 2. Commit `outputs/bulletins/`.

## Deferred stages — not yet in this build

**Report initialisation from the wiki**, for a place with no ledger, and **monthly narratives** for the issues carrying empty per-subject blocks. Neither is run now; `documentation/build.md` says why.

## Source bodies — the rule outlives its gate

`outputs/` carries metadata and compiled prose only, never a verbatim source body (`design.md` §8). The gate is retired, so the rule is the drafter's, at the moment of writing.

## Ending the run — message, log, commit, stand down

**1. Say what the run is leaving behind, across every unit — not only the ones it touched:**

```bash
python scripts/report-register-check.py     # no --unit: the default is all 60
python scripts/lint-considered.py           # every unit; the "No evidence" trap
```

**This is the step that stops a finding living in a console** — every other check runs per unit, on the units the pass worked. Its counts go in the log line at step 3, anything the run did not clear gets a block at step 2, and it is **not a gate**.

**2. Message Bill, if anything is owed him** — one block under the marker in `C:\corpus-osint-xfer\messages-for-bill.md`, at most 80 words. Nothing owed, nothing written. After writing one:

```bash
python scripts/lint-messages.py     # five open blocks, 80 words each
python scripts/lint-preambles.py    # the preamble is still a pointer
```

**3. Log one terse line:**

```bash
python scripts/log-line.py build "catalogue N, finance N places, scan N units, K ledgers updated — ok"
```

The duration writes itself from the stage-0 stamp, then clears it. Where the stamp was never taken, state the truth with `--since` or `--took`, never a hand-written figure.

**4. Commit everything:**

```bash
git add -A && git diff --cached --quiet || git commit -m "Build run: outputs, log and messages"
```

**5. Stand down** — remove the sentinel, and only now, after the commit has landed:

```bash
rm -f logs/.build-in-progress
```

**On failure, the word is `errored`.** Log the stage and error in place of the completion line — `… errored at stage 3: <message>` — commit whatever is committable, remove the sentinel, and stop. `RENDER.md` Step 0 matches the word `errored`, so a failure line must be phrased around it. A failure writes a message only where it left something Bill has to undo.

## Boundary

Nothing in Job 1 writes to OSINT. The only Corpus→OSINT channel is the exchange folder (`C:\corpus-osint-xfer\`) — files OSINT reads on Bill's schedule, never a write into OSINT itself.
