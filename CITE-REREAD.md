---
type: runbook
title: CITE-REREAD — the citation re-read of the authored status baselines
opened: 2026-09-15
---

# CITE-REREAD — does every baseline link say what it is cited for

*(Commissioned by Bill on 2026-09-15. Written so the job survives a cleared context: the state is `logs/cite-reread-progress.csv`, the tooling is `scripts/cite-reread.py`, and nothing below needs the session that opened it.)*

**The one-line brief for a fresh session.** *The authored status baselines carry claims their linked sources do not make; six units were repaired on 2026-09-15; the other 48 are re-read here, one agent per unit, against the held source bodies, and each repair is applied, checked and committed by the parent.*

## Why

The 2026-09-15 build read the status-acquire backfill for six units in full and found claims in all six baselines that the linked source does not support: figures misdated by years, institutions the source never names, detail the source does not contain, a sweep annotation read as the source speaking. About 70 were repaired (MAR 18, LBR 17, LBY 12, LSO 10, MDG 5, GNQ 3). The other 48 baselines were written by the same fan-out (`STATUS-INIT.md` → *The run*), and check A tests only that a link is **held**, never that it **says** the thing — so a misattributed claim passes every check there is. These documents are published and downloadable.

## Scope

- **In:** every inline link in the 48 `built_by: STATUS-INIT` baselines not yet `done` in the progress file — about 17,000 links to 7,800 distinct URLs.
- **Checked:** a link resolving to a held body in `raw/` (~6,000 of the URLs), or to a finance-table or AfDB dataset row (most of the rest) — the worksheet prints the row, and the claim is judged against it. On the first batch every link resolved to one of these, which is what check A requires.
- **Not checked, counted:** a link to nothing on this machine, if any turns up, and a *gateway* — a held landing page for a dataset whose country values the body does not print. Both are counted in the progress file so what remains unverified is stated, not implied away.
- **Out:** `<!-- derived -->` paragraphs (the report's own arithmetic), and the ledger and indicators except where they repeat a baseline error being repaired.

## The loop

**The parent** (one session, sole occupant of the tree — `logs/.hold-cycle` is set for the job's duration so no cycle starts beside it):

1. `python scripts/cite-reread.py worksheet {UNIT}` for the batch (from the Corpus root). Writes `logs/cite-reread/{UNIT}-worksheet.md`, gitignored.
2. Launch one read-only agent per unit, up to eight at a time, with the brief below.
3. When an agent reports, apply its patch: `python logs/cite-reread/{UNIT}-patch.py` from the Corpus root. Then `python scripts/status-check.py --unit {UNIT}` — **A, B, E, G and FM must pass**; a failure is repaired once, and if it still fails the unit is reverted (`git checkout -- outputs/reports/{UNIT}`) and left `owed` with the reason in the progress note. Then, from `scripts/.workroot/`: `python scripts/report-render.py --unit {UNIT} --render --doc all`, `--check`, and `report-register-check.py --unit {UNIT}`; a register hit or band breach the patch introduced is fixed before commit.
4. Update the unit's progress row (`state` done, `date`, the counts from the summary's `TOTALS:` line) and commit the unit alone: `CITE-REREAD {UNIT}: N claims repaired over M held links`.
5. At the end of each batch push. After the last unit, run `python scripts/status-check.py --unit all` and `python scripts/report-register-check.py`, remove `logs/.hold-cycle`, log one line (`python scripts/log-line.py cite-reread "…"`), and run a cycle's *Render* and *Mirror* so the repaired baselines are published.

## The agent brief

You are a **read-only citation checker** for one Corpus status baseline, `{UNIT}`. You judge whether each linked source says what the sentence citing it says, and you write a patch that repairs what it does not.

**Boundaries.** Write only `C:\CORPUS\logs\cite-reread\{UNIT}-patch.py` and `C:\CORPUS\logs\cite-reread\{UNIT}-summary.md`. Never write anything else under `C:\CORPUS`, never anything under `C:\OSINT`, no git commands, no scripts under `C:\CORPUS\scripts` except reading `status_lib.py`. Another agent is working on another unit at the same time; touch no other unit's files.

**Read first:** `C:\CORPUS\STATUS-INIT.md` → *The one hard rule*, *When the evidence is borderline, the fact does not go in*, *Sources and conflicts* (the paragraph on narrating disagreement) and *Writing*; this runbook's *Why*.

**Your input** is `C:\CORPUS\logs\cite-reread\{UNIT}-worksheet.md`: for each link, the sentence, the held source (slug and body path under `C:\CORPUS\scripts\.workroot\raw\`), the two best-matching passages, and any figure in the claim found nowhere in the body. The passages are a retrieval: where they do not settle a claim, open the body and search it. **Sweep notes** (a body section headed `**Sweep note`) are OSINT's annotation, not the source: a claim only a sweep note supports is unsupported.

**Per link, one verdict:**

- **supported** — the source establishes the claim as written, including its date and figure (a figure written another way — `1.35 GW` for `1,350 MW`, `€`/`EUR` — is supported). Most links should be this. Nothing to do.
- **coarsen** — the source supports a weaker or less precise statement: rewrite to what it does say (*When the evidence is borderline*, outcome 2). A wrong date in a parenthesis is a coarsen: the date comes from the source.
- **re-link** — the claim is right but this source does not carry it and another held source does: the URL must be in `C:\CORPUS\outputs\catalogue\catalogue-internal.csv` (column `url`) or already cited in the same baseline **for that fact**, and you must have read it there.
- **drop** — no held source supports it: remove the clause or sentence, keeping the paragraph grammatical and its other cited facts intact.
- **gateway** — the held body is a landing page, brief or index for a dataset, and the claim is a country value from that dataset which the body does not print (the GovTech Maturity Index brief, a data portal page). Not checkable here; leave it.
- **finance / dataset row** — judge the claim against the row the worksheet prints.
- **not held** — leave it; count it.

**Rules for every rewrite.** One hard rule stands: every stated fact keeps a link on the claim. No apparatus on the page — never *reportedly, according to, sources indicate, the base, the dataset, the wiki, conflicting, discrepancy, no source*. Do not narrate that a claim was corrected. Every time-varying figure stays dated. A sub-section's **first sentence** must still carry its best-evidenced news; if you drop or weaken it, rewrite the opening from what remains. No verbatim lifting from a source. One line per paragraph. Where the same error is repeated in `{UNIT}`'s `ledger.csv` or `indicators.csv` (search them for the slug), repair it there too; indicators cite by slug, never URL.

**Deliverable 1 — `{UNIT}-patch.py`**, a self-contained Python 3 script run from `C:\CORPUS`: exact old→new string replacements in `outputs\reports\{UNIT}\{UNIT}-status.md`, each old string asserted to occur exactly once, all assertions checked before anything is written; line endings preserved as found (read and write bytes); `compiled:` set to the date the patch is written, only where the document changes; `sources_cited:` recomputed as `len(status_lib.links(new_text))` (import `status_lib` from `C:\CORPUS\scripts`); CSV edits, if any, with the `csv` module preserving each file's row terminator and every untouched row. Print one line per operation. Test it on copies of the files before you finish.

**Deliverable 2 — `{UNIT}-summary.md`**: one line per link that is not *supported* (verdict, sub-section, the claim in five to ten words, what the source does say); then a count of each verdict; then anything the parent must know — a contradiction between two held sources you did not resolve, a ledger row you could not repair. The **last line** is exactly:

`TOTALS: links=N held_checked=N supported=N coarsened=N relinked=N dropped=N gateway=N not_held=N ledger_edits=N indicator_edits=N`

Your final message is the two paths and the TOTALS line. Nobody will answer a question: take the conservative outcome and state it.

## Done

A unit is `done` when its patch is applied and committed with A, B, E, G and FM passing — including a unit whose verdicts were all *supported*, which is a finding and gets a row like any other. The job is done when the progress file carries no `owed` row, the repaired baselines are rendered and deployed, and one log line and one commit say so.
