---
type: runbook
title: Job 1 — build outputs/ from OSINT — instruction for Claude Code
last_reviewed: 2026-08-13
---

# Job 1 — build the outputs — runbook for Claude Code

*(Hand this to Claude Code in the Corpus repo. Job 1 turns OSINT's evidence into Corpus-owned `outputs/`. Job 2 (`RENDER.md`) then renders `outputs/` into the site. Read `documentation/migration-report-layer.md` for the architecture and `documentation/report-layer.md` for the record layer stage 4 works to. OSINT is read-only throughout — never write to it. **Reading is unrestricted** (`CLAUDE.md`; Bill, 2026-08-14): the workroot junctions `raw/`, `wiki/` and `lookups/`, and adding another is a line in `setup_workroot()` rather than a boundary decision. It junctions **only what a stage reads**, because each one is a directory of OSINT's exposed to a process that can write — and `index/` is not among them at all: Corpus builds its own. The boundary is the write, and it is absolute.)*

## The two kinds of work in Job 1

Job 1 has scripted stages and one model-authoring stage, and they are run differently.

The **compiles** (vocab, catalogue, finance, budgets) are pure functions of OSINT's `raw/` and `lookups/`. They are `scripts/rebuild.py` and they just run.
The **report update** — moving the ledgers forward as new sources arrive — is a model stage. A script (`report-scan.py`) says *which* sources are new; a model reads them and decides what moves. It cannot be a plain script, and it belongs here, in the build, run every time Job 1 runs.

**BUILD authors this content; it does not transcribe it** *(Bill, 2026-08-14)*. BUILD holds editorial control over everything in `outputs/` and its job is to produce the best output it can, full stop. The scan is a convenience that stops the build re-reading what it has read — it is not a work order BUILD is confined to, and a unit the scan did not nominate is still BUILD's to improve. Where a document can be made better, BUILD makes it better. Questions about what is published, what is still being tested and what any of it costs are Bill's, and are not BUILD's to weigh.
Three further stages are deferred and named at the end: report initialisation from the wiki (for a brand-new place), the monthly narratives, and topics.

## Prerequisites

- OSINT checked out and readable (`OSINT_PATH`, default `C:\OSINT`). On this machine `raw/` is local, so the scan and renders are fast.
- Run from the repo root. Commit after each coherent stage.
- **The index is Corpus's own and needs nothing from OSINT** *(Bill, 2026-08-14)*. It is built into the gitignored workroot at `scripts/.workroot/index/` from `raw/` and `wiki/`, rebuilds itself whenever either moves, and takes about 5 seconds over 12,588 files. Nothing here waits on an OSINT maintenance step, and OSINT's own `index/` is not read at all. If a run ever raises `vault_lib.ForeignIndex` or `EmptyIndex`, it was started from the wrong root — stage 4 and 5 run **from `scripts/.workroot/`**, where `raw/` and `wiki/` resolve; from the repo root there is no base to index and the guard says so rather than writing an empty index.

## Stages 1–3 — the compiles (scripted)

```bash
python scripts/rebuild.py --all        # vocab snapshot + catalogue + finance/budgets + the scan work order
```

This writes `outputs/catalogue/`, `outputs/non-state-finance/`, `outputs/budgets/`, refreshes `outputs/vocab/`, and prints the report-update work order (stage 4 below). Commit `outputs/` and `outputs/vocab/`.

## Stage 4 — report update (the ledgers' move; model authoring)

This is the report update. `documentation/report-layer.md` is the spec — Corpus-owned, and the only one; the register below governs the prose. It reads only the sources the ledger has **not** yet considered — a set difference over slugs, not a date window — so an interrupted run resumes cleanly and nothing is re-read.

The work order (from `--all` above, or `python scripts/rebuild.py --scan`) lists each initialised unit and how many unconsidered sources it holds. For **each** such unit:

1. **List the new slugs.** `python scripts/report-scan.py --slugs {ISO3}` (run from `scripts/.workroot/`, which `rebuild.py` sets up). Read each slug's `hub_line`, facets, and body from `raw/` only where the line is not enough.
2. **Decide per source, against that unit's `outputs/reports/{ISO3}/ledger.csv`** — the four outcomes (`documentation/report-layer.md` §1 for the row test and columns, §3 for the two closed vocabularies):
   - *moves a row* — a status, milestone, position or figure changed: set `movement`, append the slug to `sources`, and set `published` to that record's publication date, which is the date at the front of its slug. **`published` is what ages the row out of a report**, so a move that does not update it leaves the row in a window it has left;
   - *mints a row* — a named system or instrument the ledger lacks, passing the row test (a named object whose position can move — not a topic the news covered);
   - *settles a **Not held** row* — strike it from `gaps.csv`, give it a status;
   - *default: nothing moves* — most sources report activity, not movement. Do **not** attach a slug to a row that did not move.
3. **Mark every slug read**, moved or not: `python scripts/report-scan.py --mark {ISO3} <slugs>`. (Sources on `origin_status: hold` are dropped by the script, not marked — pass them in regardless.)
4. **Rebuild all three documents**, not just the live one: `--doc all` (regions: `--doc progress`). Each unit has one status report, one monthly and one progress report — living documents, not dated editions — and a moved row can show in any of them. A build that changes nothing leaves a file untouched and prints `unchanged`.

   **No fact is added without a source** *(Bill, 2026-08-14)*. The citation goes on the sentence carrying the fact, not somewhere else in the block: a paragraph whose opening sentence is linked does not thereby source the three that follow it. Check H asks only that a block carries a citation at all, which is the cheap half — the rule is the drafter's. Three kinds of sentence carry no link and are right not to: a statement of what the base does **not** hold, which is a claim about the record rather than about the world; a qualification of a fact already cited in the same sentence (*the figures are the operator's own*); and the single connecting sentence the register allows, which asserts nothing. Everything else needs its link, and a summary block is where this goes wrong most easily, because it restates facts drafted elsewhere and their citations are easy to leave behind.

   **A source being in scope does not make every fact in it in scope** *(Bill, 2026-08-14)*. The window selects *rows*, by the publication date of the newest record they cite. It does not select *facts*. A July source that restates a 2023 measurement puts its row in the monthly, and the 2023 measurement still has no business in a report of what moved this month — it belongs in the status report, where the current position lives. The same goes for a stock figure a year old carried forward by a fresh article. **The monthly reports developments; selection is the drafter's, not the scan's.** Where the standing position is the only thing a row offers, the honest outcome is to leave that row out of the prose and let the ledger carry it.

   **Moving a window on is an editing job.** The renderer carries every narrative block across; deciding what still belongs is BUILD's. Both windows overlap their previous position heavily — the monthly always spans a month boundary, the progress report keeps eleven of its twelve months — so **BUILD removes what has aged out and writes in what has arrived**. A carried sentence describing a period that has moved on is well-formed prose and passes every check; finding it is the point of the revision.
5. **Verify** before moving on: `python scripts/report-render.py --unit {ISO3} --check` — checks G (every link held in `index/`), I (vocabulary), **J (no document compiled before the ledger moved)**, **L (no unwritten narrative block)** and **M (every row that states a position cites a source that resolves)** must all pass; then the register check `python scripts/report-register-check.py --unit {ISO3}` reports, a human rules.

**Every piece of evidence has a source** *(Bill, 2026-08-14)*. This is absolute and it is not a property of the checks — the checks only find where it has been broken. Nothing BUILD publishes states a position the base cannot show a reader the origin of. A row whose position cannot be sourced is ***Not held*** with a `gaps.csv` line, which is the true statement and the one the layer is built to make; it is never a bare status standing on nothing. `documentation/report-layer.md` §6 has the rule and the single exemption.

A re-render that changes nothing now leaves the file untouched and prints `unchanged` — `compiled:` is the date the document last changed, not the date the build last ran (`documentation/report-layer.md` §2). A unit that reports `unchanged` for all its documents did no work, which is the normal outcome and not a failure.

Commit the moved ledgers, `considered.txt`, `gaps.csv` and re-rendered docs.

**The Corpus register governs the narrative**: light touch, evidence-led, the lens carried mostly by selection, at most one plain connecting sentence per section, and **no figure a reader cannot get to a source for** — which is not the same as no figure beyond the ledger *(2026-08-14)*. A monthly reports developments, and §2 forbids the build becoming a chronology, so event detail that is deliberately not a ledger position belongs in the prose with its citation attached. The ledger is one route to a source, not the definition of one; check H asks only that a source exists. Full statement in `documentation/migration-report-layer.md` → *Corpus editorial register*. The evidential spine — tables, dated figures, the *Not held* count — stays exactly as disciplined as OSINT's.

## Narrative integrity — BUILD owns what is fit to publish

**No document may leave BUILD carrying an unwritten narrative block** *(Bill, 2026-08-13; tightened 2026-08-14)*. Where a narrative block has no prose, BUILD does one of two things, never a third:

- **remove the section**, if there is nothing to say about it; or
- **write the sentence that explains why there is no suitable narrative** — the ledger holds no movement this period, the evidence is too thin to connect, the place has no rows under this heading. Stating the absence is itself evidence-led reporting, and it is the same discipline as publishing a *Not held* count rather than a silence.

Leaving the block unwritten is the third thing, and it is not available. The renderer no longer mints `_(narrative not yet written)_` — a placeholder is a note-to-self that has escaped into a document a reader may download — and the empty block that replaced it says the same thing with the evidence removed. **The renderer does not clear either one**: it carries block bodies across verbatim, because deleting an author's content is not a script's decision. Clearing them is BUILD's, as the whole document is. `report-render.py --check` counts them (check L) so BUILD can see the work; the count is a tally, not a gate on someone else's behalf.

**Empty sections do not arise here at all.** The renderer prints no heading for a section or sub-section with nothing in it, in the monthly and the progress report, so there is no empty box to fill. Only the status report states an absence, and it writes that sentence itself.

**RENDER does not check this and must not.** It renders whatever BUILD produced, because a downstream guard is a second copy of a judgement that belongs here — and one that, when it existed, stopped every render instead of improving a single document. Integrity is maintained where the prose is written, not where it is typeset.

## Stage 5 — re-render (optional, mechanical)

```bash
python scripts/rebuild.py --reports all      # rebuild every report's tables from its ledger, carry narrative across
```

Needed only after a format change or to refresh tables outside a unit you already re-rendered in stage 4.

## Deferred stages — not yet in this build

- **Report initialisation from the wiki** — for a place with no ledger. Reads the compiled wiki (`wiki/places/{ISO}.md`, `wiki/intersections/`) to distil a new ledger and write the first reports. `report-country-init.py` is the shell; the authoring is a session's model work. Bill's decision (2026-08-13): the current ledgers are the accepted baseline, so initialisation is not run now.
- **Monthly narratives** — some monthly issues carry empty per-subject blocks; authoring them is tracked.
- **Topics** — the topic-report layer is not built; awaiting Bill's instruction.

## Leak gate — before any commit of outputs/

`outputs/` must carry metadata and compiled prose only, never a verbatim source body. Before **any** commit that includes `outputs/` — the compile commits above and the final one below — run the gate:

```bash
python scripts/leak-check.py outputs      # exit 0 = clean; exit 1 = a body leaked
```

If it exits non-zero, **do not commit** — a compiler is wrong; stop and fix it. A leak into public history is permanent (`documentation/design.md` §8), so this is the one check that fails the build rather than warning.

## Log

On completion or error, append **one terse line** to `logs/log.md`, in the form `YYYY-MM-DD HH:MM · build · what happened`:

```bash
printf '%s · build · %s\n' "$(date '+%Y-%m-%d %H:%M')" \
  "catalogue N, finance N places, scan N units, K ledgers updated — ok" >> logs/log.md
```

On failure, log the stage and the error instead (`… errored at stage 3: <message>`) and stop. One line per run — the detail is in git.

Then run the leak gate and commit everything, so the build ends clean with nothing outstanding:

```bash
python scripts/leak-check.py outputs || exit 1
git add -A && git diff --cached --quiet || git commit -m "Build run: outputs and log"
```

## Boundary

Nothing in Job 1 writes to OSINT. The only Corpus→OSINT channel is the gaps request-feed (a *Not held* row asking OSINT's sweeps to fetch a named document) — a file OSINT reads, never a write.
