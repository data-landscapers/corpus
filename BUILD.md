---
type: runbook
title: Job 1 — build outputs/ from OSINT — instruction for Claude Code
last_reviewed: 2026-08-13
---

# Job 1 — build the outputs — runbook for Claude Code

*(Hand this to Claude Code in the Corpus repo. Job 1 turns OSINT's evidence into Corpus-owned `outputs/`. Job 2 (`RENDER.md`) then renders `outputs/` into the site. Read `documentation/migration-report-layer.md` first. OSINT is read-only throughout — never write to it.)*

## The two kinds of work in Job 1

Job 1 has scripted stages and one model-authoring stage, and they are run differently.

The **compiles** (vocab, catalogue, finance, budgets) are pure functions of OSINT's `raw/` and `lookups/`. They are `scripts/rebuild.py` and they just run.
The **report update** — moving the ledgers forward as new sources arrive — is a model stage. A script (`report-scan.py`) says *which* sources are new; a model reads them and decides what moves. It cannot be a plain script, and it belongs here, in the build, run every time Job 1 runs.
Three further stages are deferred and named at the end: report initialisation from the wiki (for a brand-new place), the monthly narratives, and topics.

## Prerequisites

- OSINT checked out and readable (`OSINT_PATH`, default `C:\OSINT`). On this machine `raw/` is local, so the scan and renders are fast.
- Run from the repo root. Commit after each coherent stage.

## Stages 1–3 — the compiles (scripted)

```bash
python scripts/rebuild.py --all        # vocab snapshot + catalogue + finance/budgets + the scan work order
```

This writes `outputs/catalogue/`, `outputs/non-state-finance/`, `outputs/budgets/`, refreshes `outputs/vocab/`, and prints the report-update work order (stage 4 below). Commit `outputs/` and `outputs/vocab/`.

## Stage 4 — report update (the ledgers' move; model authoring)

This is REPORT-UPDATE (`wiki/report-layer.md` in OSINT is the spec; the Corpus register below governs the prose). It reads only the sources the ledger has **not** yet considered — a set difference over slugs, not a date window — so an interrupted run resumes cleanly and nothing is re-read.

The work order (from `--all` above, or `python scripts/rebuild.py --scan`) lists each initialised unit and how many unconsidered sources it holds. For **each** such unit:

1. **List the new slugs.** `python scripts/report-scan.py --slugs {ISO3}` (run from `scripts/.workroot/`, which `rebuild.py` sets up). Read each slug's `hub_line`, facets, and body from `raw/` only where the line is not enough.
2. **Decide per source, against that unit's `outputs/reports/{ISO3}/ledger.csv`** — the four outcomes of `report-layer.md` §1/§3:
   - *moves a row* — a status, milestone, `as_at`, position or figure changed: move the old position into `prior_*`, set `movement`, append the slug to `sources`;
   - *mints a row* — a named system or instrument the ledger lacks, passing the row test (a named object whose position can move — not a topic the news covered);
   - *settles a **Not held** row* — strike it from `gaps.csv`, give it a status;
   - *default: nothing moves* — most sources report activity, not movement. Do **not** attach a slug to a row that did not move.
3. **Mark every slug read**, moved or not: `python scripts/report-scan.py --mark {ISO3} <slugs>`. (Sources on `origin_status: hold` are dropped by the script, not marked — pass them in regardless.)
4. **Re-render** the unit's live document: `python scripts/report-render.py --unit {ISO3} --doc status --render` (regions: `--doc progress`).
5. **Verify** before moving on: `python scripts/report-render.py --unit {ISO3} --check` — check G (every link held in `index/`) must pass; then the register check `python scripts/report-register-check.py --unit {ISO3}` reports, a human rules.

Commit the moved ledgers, `considered.txt`, `gaps.csv` and re-rendered docs.

**The Corpus register governs the narrative** (not OSINT's §10): light touch, evidence-led, the lens carried mostly by selection, at most one plain connecting sentence per section, no new figures beyond the ledger. Full statement in `documentation/migration-report-layer.md` → *Corpus editorial register*. The evidential spine — tables, dated figures, the *Not held* count — stays exactly as disciplined as OSINT's.

## Stage 5 — re-render (optional, mechanical)

```bash
python scripts/rebuild.py --reports all      # rebuild every report's tables from its ledger, carry narrative across
```

Needed only after a format change or to refresh tables outside a unit you already re-rendered in stage 4.

## Deferred stages — not yet in this build

- **Report initialisation from the wiki** — for a place with no ledger. Reads the compiled wiki (`wiki/places/{ISO}.md`, `wiki/intersections/`) to distil a new ledger and write the first reports. `report-country-init.py` is the shell; the authoring is a session's model work. Bill's decision (2026-08-13): the current ledgers are the accepted baseline, so initialisation is not run now.
- **Monthly narratives** — some monthly issues carry empty per-subject blocks; authoring them is tracked.
- **Topics** — the topic-report layer is not built; awaiting Bill's instruction.

## Log

On completion or error, append **one terse line** to `logs/log.md`, in the form `YYYY-MM-DD HH:MM · build · what happened`:

```bash
printf '%s · build · %s\n' "$(date '+%Y-%m-%d %H:%M')" \
  "catalogue N, finance N places, scan N units, K ledgers updated — ok" >> logs/log.md
```

On failure, log the stage and the error instead (`… errored at stage 3: <message>`) and stop. One line per run — the detail is in git.

Then commit everything, so the build ends with nothing outstanding:

```bash
git add -A && git diff --cached --quiet || git commit -m "Build run: outputs and log"
```

## Boundary

Nothing in Job 1 writes to OSINT. The only Corpus→OSINT channel is the gaps request-feed (a *Not held* row asking OSINT's sweeps to fetch a named document) — a file OSINT reads, never a write.
