---
type: runbook
reader: cc
title: The report update — BUILD stage 4 — instruction for Claude Code
last_reviewed: 2026-10-03
---

# The report update — BUILD stage 4 — runbook for Claude Code

*(Stage 4 of `BUILD.md`, which runs it for each unit in the work order; moved here word for word on 2026-10-03 so that file fits its cap. `BUILD.md` → *Running unattended* governs here as there: no check stops a finished run. `documentation/build.md` is why.)*

## The update, per unit

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

   **Then ask whether the pile is due a whole re-read** (countries only): `python scripts/report-scan.py --sections {ISO3}`. If it names sub-sections, re-read each whole against the ledger and the unit's held sources, as `UNIT-REVIEW.md` step 3 reads a status sub-section, and revise under *Maintaining the status baseline*. Then run `python scripts/report-scan.py --sections-read {ISO3}` and count the sub-sections revised in the run's log line. `report-layer.md` §2 holds the rule.

5. **Rebuild the unit's documents**: `python scripts/report-render.py --unit {ISO3} --doc all --render`. The renderer decides which documents a unit issues, so this line is the same on every unit; a build that changes nothing prints `unchanged`. Three rules govern what is written:
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

   **Residue is outcomes converted, never work deferred**, and **there is no "note it and move along"**: a finding that needs more than a run goes in `C:\corpus-osint-xfer\messages-for-bill.md`. **A finding is not scoped out because the run did not create it** — the check runs over the unit, not over the diff.

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

Commit the moved ledgers, `considered.txt`, `sections-read.txt`, `gaps.csv` and re-rendered docs. **The Corpus register governs the narrative** (`report-layer.md` §10).

## Narrative integrity — BUILD owns what is fit to publish

**No document may leave BUILD carrying an unwritten narrative block.** Where a block has no prose, BUILD does one of two things, never a third: **remove the section**, or **write the sentence that explains why there is no suitable narrative**. Stating the absence is evidence-led reporting, the same discipline as publishing a *Not held* count.

The renderer mints no placeholder and clears nothing; `report-render.py --check` counts empty blocks (check L) so BUILD can see the work. **RENDER does not check this and must not.**
