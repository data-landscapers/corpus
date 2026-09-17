---
type: runbook
title: UNIT-REVIEW — one place's reports reviewed whole, once a night — instruction for Claude Code
opened: 2026-09-17
last_reviewed: 2026-09-17
---

# UNIT-REVIEW — one country or region a cycle, every report it issues

*(Commissioned by Bill on 2026-09-17. Run by `CYCLE.md`, between the build and the render, when `scripts/unit-review.py next` names a unit. OSINT is read-only throughout.)*

**The one-line brief.** *BUILD reads only what is new to a unit, so nothing ever re-reads a unit's reports as a whole; this does, one place a cycle in rotation, and repairs what it finds before the render publishes it.*

## Why

**Stage 4 works a set difference, and a set difference never looks back.** A sentence carried across a window that has moved on, an indicator cell the ledger has overtaken, a baseline section a later source quietly contradicted, a finance row counted twice: each passes every check, because the checks test the documents' consistency, not whether they are still right. `CITE-REREAD.md` found 3,774 such claims in one sweep of the baselines. A rotation finds the same class a unit at a time, before it accumulates, at a cost a nightly cycle can carry.

## When — the script decides

```bash
python scripts/unit-review.py next --poll    # from the /poll loop
python scripts/unit-review.py next           # any other cycle
```

**Exit 0 prints the unit; exit 1 means none is owed now** — a cycle not started by `/poll` and outside 21:00–05:00 — and the review is skipped with no log line and no message. Exit 2 is a malformed `logs/unit-review.csv`: write one message block quoting it and go on to the render. The script's docstring holds the rotation order and the time rule; do not re-derive either.

**Skip it too if the build half did not finish** — `logs/.build-in-progress` present, or the newest `· build ·` line `errored`. The seam will stop the cycle, and a review over a half-built unit reviews the wrong thing.

## What a unit issues

| | status | progress | monthly | non-state finance |
|---|---|---|---|---|
| **country** | `outputs/reports/{U}/{U}-status.md` | `{U}-progress.md` + `indicators.csv` | `{U}-monthly.md` | `outputs/non-state-finance/{U}-nonstate.csv`, `-summary.csv` |
| **region** | never | where `outputs/reports/{U}/` exists | where it exists | where the CSV exists |

`XGL` and `XSS` issue finance tables and no reports. A document a unit does not issue is not reviewed and not created.

## The run

Commands run from `scripts/.workroot/`, where `raw/` and `wiki/` resolve; the rotation commands run from the Corpus root.

1. **Stamp the clock**: `python scripts/log-line.py --start review`.
2. **Read the unit whole** — every document in the table, plus `ledger.csv` and `gaps.csv`. Then run the checks, so the mechanical findings are on the table before the judgement starts:

   ```bash
   python scripts/report-render.py --unit {U} --check
   python scripts/report-register-check.py --unit {U}
   python scripts/status-check.py --unit {U} --openings     # countries only
   ```

3. **Review each document against the question the checks cannot ask — is it still right?**
   - **Status** (countries). Does each sub-section state the position the ledger and the newest held sources now establish? Superseded facts, figures whose *as of* has been overtaken, an opening sentence no longer carrying the best-evidenced news, a claim its link does not make. Revise under `BUILD.md` → *Maintaining the status baseline*, whose rules apply whole — including its revert rule and *a borderline source changes nothing*.
   - **Progress.** Does `indicators.csv` answer from the ledger as it stands — every moved or minted row mapped, each Developments cell current, each Progress judgement supported by what it cites? A *No evidence* over a ledger that holds the answer is the `considered-not-carried.md` defect and is repaired here. `documentation/indicator-mapping-conventions.md` is the procedure.
   - **Monthly.** Does every narrative block describe what is in the window? Sentences about a period that has moved on come out; a standing fact that belongs in the status report comes out of the monthly (`BUILD.md` stage 4 step 5).
   - **Non-state finance.** The table is derived and **never hand-edited**. Read the rows for a deal counted twice, a recipient that is not this place, an amount whose basis or quality the description contradicts, a financier name that did not resolve, a row that is state finance, a total in `-summary.csv` the rows do not support. **Repair where the defect lives.** A fault in how Corpus compiles the rows — `scripts/build-finance-page.py` or `scripts/finance_lib.py` — is fixed here, then `python scripts/build-finance-page.py --all`. A fault in the record, or in the financier-name and deal maps the compile reads through the `lookups` junction, is OSINT's: an `[ACT]` note in `C:\corpus-osint-xfer\notes-for-osint.md` with `Affects: outputs/non-state-finance/{U}-nonstate.csv` (`CLAUDE.md` → *The exchange*), committed and pushed in the share.

   `BUILD.md` stage 4 is in force throughout: no fact without a source on its own sentence, the register of `report-layer.md` §10, *the repository* never *the base* in published prose, and **no finding noted and left** — a finding is repaired in this run, converted to a finished outcome (*Not held* with a `gaps.csv` line, a claim struck), or, if it needs more than a run, a block in `logs/messages-for-bill.md`.

4. **Re-render and re-check**: `python scripts/report-render.py --unit {U} --doc all`, then the three checks in step 2 again. They pass, or the failing edit is repaired or reverted.
5. **Record and commit** — from the Corpus root, one commit for the unit, explicit paths, pushed straight away:

   ```bash
   python scripts/unit-review.py done {U}
   git add outputs/reports/{U} outputs/non-state-finance outputs/budgets scripts logs/unit-review.csv   # only what the run touched
   git commit -F - <<'EOF'
   Review {U}: <what changed, in counts>
   EOF
   git push
   ```

   A review that changed nothing still stamps and commits the rotation file — *reviewed and right* is a result.
6. **Log it**:

   ```bash
   python scripts/log-line.py review "{U}: status <n> sections revised, progress <n> cells, monthly <n> blocks, finance <n> rows; <n> notes for OSINT — ok"
   ```

   Counts of zero are written, not omitted, so a line says what was looked at.

## When it fails

**A review never holds the render.** It runs unattended under the cycle's rules: never stop to ask, take the conservative option and say so. If the run cannot finish — context, a check that will not clear, anything — restore the unit's files to `HEAD` (the last good state; nothing of this run's is committed until step 5), **do not stamp the rotation**, so the unit stays first in line, and log `python scripts/log-line.py review "{U}: <what stopped it> — errored"`. The cycle goes on to `RENDER.md` Step 0, whose check 3 needs `outputs/` clean.

**A unit whose previous review line also `errored` is stamped anyway**, with a message block saying what stopped it twice — otherwise one unit a run cannot finish holds the head of the rotation for ever.

## Boundary

Nothing here writes to `C:\OSINT`. A defect in a record is a note in the share, never an edit — `CLAUDE.md` has the rule.
