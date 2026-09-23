---
type: runbook
title: Job 1 — build outputs/ from OSINT — instruction for Claude Code
last_reviewed: 2026-09-20
---

# Job 1 — build the outputs — runbook for Claude Code

*(Job 1 turns OSINT's evidence into Corpus-owned `outputs/`. Job 2 (`RENDER.md`) renders it into the site; `CYCLE.md` orders the two and changes nothing in either. **`documentation/build.md` is why each stage is where it is and what each check catches**; this file is what to run. `documentation/report-layer.md` is the record layer stage 4 works to. OSINT is read-only throughout; reading is unrestricted. The workroot junctions `raw/`, `wiki/` and `lookups/` — only what a stage reads — and `index/` is not among them: Corpus builds its own. The boundary is the write, and it is absolute.)*

## Running unattended — a run never stops to ask

**BUILD puts no question mid-stream.** It runs back to back with RENDER with nobody watching, and ends exactly two ways: it **finishes**, or it **fails** — an error it cannot get past, never a decision it would rather Bill made.

**Where this runbook says a human rules, BUILD rules**, and every such point is named below with the path to take. **Where BUILD wants Bill's attention, it finishes the job and leaves a message** in `logs/messages-for-bill.md`: what would have been asked, what the run did instead, what his options are. A run that needed nothing writes nothing there.

**No check stops a finished run.** Every check in Job 1 is a work list, not a gate. A failing check is BUILD's work to do, and where it cannot be done the true statement is ***Not held*** with a `gaps.csv` line — a completed outcome, not a blocked one.

**An interrupted run is resumable**: stage 4 reads a set difference over slugs, so the next run picks up where a dead one stopped. Stage 0's sentinel catches the interruption nobody noticed.

## The two kinds of work in Job 1

The **compiles** (vocab, catalogue, finance, budgets) are pure functions of OSINT's `raw/` and `lookups/` — and, for budgets since 2026-09-20, of Corpus's own `budgets/{ISO3}/{FY}.csv` as well *(R54; `BUDGET-EXTRACT.md` writes those, and a country-year in that folder replaces OSINT's rows for the year)*: `scripts/rebuild.py`, and they just run. The **report update** is a model stage: `report-scan.py` says *which* sources are new; a model reads them and decides what moves.

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

`documentation/report-layer.md` is the spec. This stage reads only the sources the ledger has **not** yet considered — a set difference over slugs, so **an item already considered is never reopened** (`scripts/reopen-considered.py` is the only thing that can undo a mark). The work order (from `--all`, or `rebuild.py --scan`) lists each initialised unit and its unconsidered count. For **each** unit:

1. **List the new slugs.** `python scripts/report-scan.py --slugs {ISO3}` (from `scripts/.workroot/`). Read each slug's `hub_line`, facets, and body only where the line is not enough.

2. **Decide per source, against `outputs/reports/{ISO3}/ledger.csv`** (`report-layer.md` §1 for the row test, §3 for the vocabularies) — four outcomes:
   - *moves a row* — set `movement`, put the slug **first** in `sources`, and set `published` to the record's publication date, the date at the front of its slug;
   - *mints a row* — a named system or instrument the ledger lacks, passing the row test;
   - *settles a **Not held** row* — strike it from `gaps.csv`, give it a status;
   - *default: nothing moves* — most sources report activity, not movement. Do **not** attach a slug to a row that did not move.

   **"Nothing moves" is about a position the ledger already holds, not about the source** *(corrected 2026-09-10)*. Where the ledger holds **no** position on the thing a source names, the outcome is *mints a row* with `movement: Baseline not held`. **The test is the row test of `report-layer.md` §1 and nothing else** — could a reader name the thing, and could its position be different next quarter — never "did this change in the window".

   **A row that moves or is minted is then mapped** in `outputs/reports/{ISO3}/indicators.csv`, because the progress report renders from the indicator frame and not from the ledger. `documentation/indicator-mapping-conventions.md` is the procedure; the file is maintained like the ledger, never rebuilt.

3. **Ask the same source the baseline question** — see *Maintaining the status baseline*. Asked of the record already open, independent of step 2.

4. **Mark every slug read**, moved or not: `python scripts/report-scan.py --mark {ISO3} <slugs>`. (Sources on `origin_status: hold` are dropped by the script — pass them in regardless.)

5. **Rebuild the unit's documents**: `--doc all`. The renderer decides which documents a unit issues, so this line is the same on every unit; a build that changes nothing prints `unchanged`. Three rules govern what is written:
   - **No fact without a source, on the sentence carrying the fact.** Only three kinds of sentence rightly carry no link: a statement of what the base does **not** hold, a qualification of a fact cited in the same sentence, and the single connecting sentence the register allows. **In published prose the collection is *the repository*, never *the base*** *(Bill, 2026-09-11)*.
   - **A source in scope does not make every fact in it in scope.** The window selects *rows*, not facts; where the standing position is all a row offers, leave it out of the prose and let the ledger carry it.
   - **Moving a window on is an editing job.** The renderer carries every narrative block across; BUILD removes what has aged out and writes in what has arrived.

6. **Verify before moving on**:

   ```bash
   python scripts/report-render.py --unit {ISO3} --check
   python scripts/report-register-check.py --unit {ISO3}
   ```

   G (every link resolves through the catalogue), I (vocabulary), J (no document compiled before the ledger moved), L (no unwritten narrative block), M (every stated position cites a source that resolves).

   **A failing check is work, and BUILD does it in the same pass.** G, I, J and M are mechanical, each with one repair; L is authoring work — write the sentence or remove the section (*Narrative integrity*). Where a check cannot be cleared the fallback is a finished outcome: an unsourceable position is ***Not held*** with a `gaps.csv` line, and a link resolving to nothing is struck along with the claim standing on it.

   **Residue is outcomes converted, never work deferred**, and **there is no "note it and move along"**: a finding that needs more than a run goes in `logs/messages-for-bill.md`. **A finding is not scoped out because the run did not create it** — the check runs over the unit, not over the diff.

   **The register check reports and BUILD rules.** A hit inside quoted source text stands; a hit in BUILD's own prose is rewritten. Message Bill only if clearing a hit would drop a fact the report needs.

## Maintaining the status baseline

**On an initialised unit the status report is BUILD's to keep current, and BUILD never re-renders it** — `report-render.py` narrows the document set, so `--doc all` does not include status.

**It is one more question asked of a record already open, not a stage**: does this source change what a sub-section can *say*, not whether it is relevant to one. The baseline changes in two cases: the position it states is no longer the position the source establishes, or it says nothing can be established and now something can.

**Where it changes, revise that one sub-section in place**, edited as prose:

- **The superseded fact comes out.** A revision replaces; it does not append.
- **A borderline source changes nothing** (`STATUS-INIT.md` → *When the evidence is borderline*). Where two accounts of equal tier conflict, the section stands.
- **The first sentence may have to change**: the opening sentence carries the best-evidenced news (`STATUS-INIT.md` → *Writing*).
- **No apparatus.** Every time-varying figure dated, no changelog.
- **No acquire line is ever written here.**
- **Frontmatter.** Move `compiled:` to the date of the edit, only when the document changed, and update `sources_cited`. Leave `built_by`, `hub_last_reviewed` and `intersections_read` alone.

**Verification**, re-run **after** the edit pass:

```bash
python scripts/status-check.py --unit {ISO3}      # STATUS-INIT.md → Verification, A to I
python scripts/report-render.py --unit {ISO3} --check
```

**A revision that cannot pass does not stand.** Commit the unit's other work before the baseline edit pass, so the last good baseline is at `HEAD`. A failing A, B or G is repaired first; if it still fails, revert the file, re-run `status-check.py`, and write the message saying which source prompted the edit and why it could not pass. C to F, H and I are repaired in place and never trigger a revert.

**Every piece of evidence has a source.** A position that cannot be sourced is ***Not held*** with a `gaps.csv` line, never a bare status standing on nothing (`report-layer.md` §6).

Commit the moved ledgers, `considered.txt`, `gaps.csv` and re-rendered docs. **The Corpus register governs the narrative** (`report-layer.md` §10).

## Stage 4b — datasets (model authoring)

**The same set difference as stage 4, over a dataset instead of a ledger** (`documentation/datasets.md`, T7). A raw record is a candidate for Data Centres if it carries `infra.store` or its title or `hub_line` names a data centre; it stays unconsidered until its slug is in `outputs/datasets/data-centres/considered.txt`. From `scripts/.workroot/`:

```bash
python scripts/dataset-scan.py                                   # the work order, by place
python scripts/dataset-scan.py --packet data-centres {PLACE}     # --parts N past ~30 records
```

1. **Read the packet** — each record beside the current rows of every country it names — and **write `prep/dc-evidence/t7/{PLACE}/decisions.json`**: an outcome for every slug under `considered`, and under `rows` the edits, new facilities and sources they rest on, each with a plain-English `summary` for the page's Recent changes. The format and the rules are in `scripts/dataset-scan.py`'s docstring; the reading rules are T6's (`scripts/dataset-evidence.py`).
2. **Decide per record** — *modifies a row* (something newer or more specific than the row holds), *adds a facility* (one the dataset lacks, checked against every row, not only the country's), or *nothing* (the default: most records restate what a row already says). A record that confirms a row joins it through `add_slugs`, so the row cites the catalogue.
3. **Apply**: `python scripts/dataset-scan.py --apply data-centres {PLACE} --dry-run` until clean, then without `--dry-run`. It writes the master, logs each change at the top of `logs/dataset-updates.csv` with its sources, and marks every accounted slug considered.

**A night's arrivals are one packet**: `--packet data-centres ALL`, applied as `--apply data-centres ALL`. The backlog was read place by place. Commit the master, `considered.txt`, `url-audit.csv`, `claims-to-source.csv` and the log. RENDER mints the dated edition.

## Narrative integrity — BUILD owns what is fit to publish

**No document may leave BUILD carrying an unwritten narrative block.** Where a block has no prose, BUILD does one of two things, never a third: **remove the section**, or **write the sentence that explains why there is no suitable narrative**. Stating the absence is evidence-led reporting, the same discipline as publishing a *Not held* count.

The renderer mints no placeholder and clears nothing; `report-render.py --check` counts empty blocks (check L) so BUILD can see the work. **RENDER does not check this and must not.**

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

One document over the newest day or two of publication: `outputs/bulletins/corpus-bulletin.md`, published at `/bulletin/`. Design note: `documentation/bulletin.md`. **This stage can also run on its own at midday** — `BULLETIN-TOPUP.md` is that run. Its only precondition is stage 2.

```bash
python scripts/bulletin.py --scan          # the window, and which items still need a summary
```

For **each** item in the work order, read it — `raw/{year}/{slug}.md` from `scripts/.workroot/`, `hub_line` first, body only where the line is not enough — and write one to three sentences:

```bash
python scripts/bulletin.py --write {slug} --text "…"
python scripts/bulletin.py --assemble      # then commit outputs/bulletins/
```

- **The window is publication, not acquisition**: an item is in when its `published` date is today or yesterday — **today alone from 18:00**. **An empty window is a finished bulletin**; `--assemble` writes the document saying the window was empty and why.
- **A summary is written once and kept** in `summaries.json`; `--scan` asks only for what is not in it.
- **`--assemble` stops rather than publishing a gap**: an item in the window with no summary fails the command and names the slugs.
- **Everything in a summary is sourced by construction** — each entry opens with the item's title linked to the publisher's record. That does not license a fact the item does not carry, and **a verbatim sentence lifted from the body is a register failure**.
- **Detail sits in one place**: an item carrying five topics is summarised once and cross-referenced from the other four.
- **The sections are `lookups/taxonomy.csv`'s order and labels**, Level-1 groups with Level-2 sections.
- **A sweep that published nothing into the window has still updated the bulletin**; the run reports `checked` rather than `written`.

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

**2. Message Bill, if anything is owed him** — one block under the marker in `logs/messages-for-bill.md`, at most 80 words. Nothing owed, nothing written. After writing one:

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
