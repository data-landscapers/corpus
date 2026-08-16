---
type: doc
title: OSINT migration — what CORPUS took over, and what OSINT now retires
last_reviewed: 2026-08-16
audience: OSINT (Bill, or a colleague's session run *in* OSINT)
status: written in Corpus — to be actioned in an OSINT session (logs/notes-for-osint.md)
---

# OSINT migration — the retirement list

*(Written from CORPUS, for OSINT. It briefs an OSINT session on what CORPUS has taken over and lists, as tasks, what OSINT should now retire. Action this **before** `notes-for-osint.md`, which assumes the boundary below is already in force. One line per paragraph, OSINT house style.)*

*(**Read Sequencing first — the list is not in the order it should be done in, and two tasks carry rulings Bill has not made yet.** R3 and R5 each present options rather than an instruction; deleting anything before those are answered settles them by default. Verified against both trees on 2026-08-16, which is where the file counts and dates below come from.)*

## What CORPUS is

CORPUS (`C:\CORPUS`, its own git repo) is the public-site layer for **corpus.data-landscapers.com**: country and regional reports, a source catalogue, and non-state-finance and budget data, served over the private research base that OSINT maintains.

Until 2026-08-13 CORPUS was a **mirror**: it pulled OSINT's `outputs/` and rendered it. That is no longer true. CORPUS now **authors** the output layer itself. The current architecture is CORPUS's `documentation/migration-report-layer.md`; this file is its OSINT-facing half.

## The relationship now — two repos, one direction

**OSINT collects and classifies. CORPUS compiles, reports, and analyses.**

CORPUS reads OSINT **read-only** — `raw/`, `lookups/` and the internal `wiki/`, and *not* `index/`, which it builds for itself — and writes only into its own tree. It never writes to OSINT, in any form. OSINT does not read CORPUS, and gains no publication step in its night, with one exception (the request feed, task R9).

CORPUS runs as two jobs on Bill's machine: **BUILD** (OSINT evidence → CORPUS `outputs/`) and **RENDER** (`outputs/` → the site). BUILD's compiles are pure functions of `raw/`; its report-update stage is a model pass; RENDER produces the site and backs both repos up (`mirror.bat`, which reads OSINT read-only).

**What OSINT must keep stable, because CORPUS reads it:** `raw/`, `lookups/`, `wiki/` — git-tracked, committed, and with stable slugs. **`index/` is not one of them and owes CORPUS nothing** *(2026-08-14)*: CORPUS builds its own index from `raw/` and `wiki/` rather than reading OSINT's, so OSINT's index is OSINT's business entirely. These are the standing constraints; they live in `notes-for-osint.md`, not here.

## The retirement list — tasks for OSINT

Each is *retire X, because CORPUS now owns it, keeping Y*. Do them once CORPUS is confirmed authoritative for the output layer (it is, as of the 2026-08-13 render). R11 is the exception to the shape: OSINT initiates it, and it is listed here because CORPUS reads what it removes.

**R1 — Retire the report layer.** Remove `REPORT-UPDATE`, `REPORT-COUNTRY`, `REPORT-REGION`, `REPORT-MONTHLY` as processes and drop the `REPORT-UPDATE` step from `SWEEP-CYCLE`'s nightly run (the line after `UPDATE-WIKI`). CORPUS authors ledgers and reports now. The ledgers, `considered.txt`, `gaps.csv` and issued documents under `outputs/reports/` are CORPUS-owned going forward; OSINT's copies become dead once R6 runs.

**R2 — Retire the nightly output refresh.** Remove the `run the output refresh` step (`outputs\ except budgets\, catalogue + capped narrative drain`) from `SWEEP-CYCLE`, and the `## Output refresh` section that documents it. CORPUS builds the catalogue (`build-catalogue.py`) and authors report narrative itself. Two things fall with the phase and are easy to leave standing: `scripts/report-narrative-backlog.py`, which exists only to feed the capped narrative drain, and **`LINT` #26** (`scripts/lint-output-freshness.py`), which asserts the refresh regenerated `outputs\` and so fails every night once it no longer runs. Retire both in the same change.

**R3 — Retire the report half of REPORT-LINT.** *(Corrected 2026-08-14 — an earlier draft of this task told OSINT to drop A and D. It should not. Bill's ruling of 2026-08-13: "REPORT-LINT splits along a seam already inside it — checks A–F stay in OSINT next to what they verify; G–K travel to Corpus.")*

**Checks A–F all stay in OSINT.** They verify the finance and hub compiles against `raw/`, and `raw/` is OSINT's — a check belongs next to the records it reconciles, not next to the CSV it happens to have produced. **Checks G–K travel to CORPUS** (link-held, prose-vs-ledger, vocabulary, as-of, register), because they verify the report layer, which is CORPUS's. Retire `REPORT-LINT` as a report-layer pass; fold A–F into `LINT` or `FINANCE-COMPILE`. Nothing here asks OSINT to give up a check — `scripts/report-lint.py` stays, and is deliberately absent from R7's removal list.

**Five of them lose their subject at R4 and R6, though, unless something is decided first** *(2026-08-16)*. Checks A–E all read `outputs/non-state-finance/{ISO3}-nonstate.csv`: A rebuilds each place's deal rows from `raw/` and compares them *to that export*, D reads its `financier` column, and B and C run `compile-hub-financing.py`, which reads it. R4 stops producing that file and R6 deletes the folder, so only F — hub bullets against the sources — survives untouched. This is R5's problem one layer up, and it takes the same kind of ruling before R3, R4 or R6 is actioned. **(a) Carve the non-state CSV out of R4 and R6** and keep producing it as an internal OSINT artefact that nothing publishes: the smallest change, and all five checks stand as written. **(b) Rewrite A–E** to reconcile the hub prose against `raw/` directly, with no CSV in the middle: most faithful to *a check belongs next to the records it reconciles*, and much the most work. **(c) Let A–E go**, leaving nothing OSINT-side that verifies its own finance compiles — recorded for completeness, not recommended. Until this is settled the sentence above is an intention, not a fact.

**R4 — Retire the finance/budget CSV export.** `build-finance-page.py` (via `FINANCE-COMPILE` / `FINANCE-PAGES`) writes `outputs/non-state-finance/` and `outputs/budgets/`; CORPUS builds these now. **Keep all finance and budget COLLECTION** — `DOMESTIC-FINANCE-SWEEP`, `BUDGET-EXTRACT`, `COUNTRY-BUDGET-BATCH`, `SWEEP-COUNTRY-BUDGET`, `SWEEP-FINANCIERS`, `SWEEP-IATI` — because those write the finance and budget *records* into `raw/`, which is exactly what CORPUS reads. Only the CSV compile moves. One loose end in the prose: `COUNTRY-BUDGET-BATCH.md`'s *budget-line record* section specifies `FINANCE-COMPILE` building the per-country exports (`outputs/budgets/{ISO3}-budget.csv`) from the records. That is a spec sentence, not a live read — the domestic-state budget layer is suspended and the refresh already excludes `outputs\budgets\` — so nothing breaks, but the process stays and the sentence should not outlive the file it names.

**R5 — Decide the hub `## Financing` prose (the one real coupling).** `compile-hub-financing.py` rewrites a hub's Financing sentences from `outputs/non-state-finance/{ISO3}-nonstate.csv` — a file OSINT will stop producing at R4. The hub is internal OSINT navigation, so it stays; pick one: **(a) re-derive** those sentences straight from `raw/` (recommended — keeps hubs self-contained and reading only OSINT's own evidence); **(b) freeze** the Financing prose as-is; or **(c) read** CORPUS's committed `outputs/`. Do not leave it reading a file that no longer gets written. **(b) costs more than it looks**: CORPUS reads the place hubs directly when it initialises a country or region report and when it scopes a status baseline, so frozen Financing prose is not merely stale inside OSINT — it is a permanently stale finance narrative sitting in front of every CORPUS report that starts from a hub.

**R6 — Retire OSINT's `outputs/`.** Once R1–R4 stop producing it, `outputs/` (reports, catalogue, non-state-finance, budgets) is no longer read by anything — CORPUS reads `raw/`/`lookups/`/`wiki/`, never OSINT's `outputs/`. Remove it from git to reclaim space and end the two-authorities risk. Confirm CORPUS has a clean build first; keep one tagged commit as a fallback. **Settle R3's ruling before this runs** — five of the checks R3 keeps in OSINT read `outputs/non-state-finance/`, so deleting the folder answers that question by default and in the least considered direction. `LINT` #26 and `scripts/lint-output-freshness.py` go with the folder (R2).

**R7 — Retire the report-layer specs and scripts.** `wiki/report-layer.md`, `wiki/report-country-skeleton.md`, `wiki/report-region-skeleton.md`, and `scripts/report-*.py` (`report-render`, `report-scan`, `report-register-check`, `report-country-init`, `report-region-init`) — CORPUS holds its own copies: the scripts in `scripts/`, and the three specs in `documentation/` as of 2026-08-14, adapted rather than mirrored (the register now points at CORPUS's own, and the gaps loop at the request feed). Nothing in CORPUS reads these three files from OSINT any more, so their removal breaks nothing here. Remove from OSINT unless something else in the vault imports them; grep first, scoped to the process files, `scripts/` and `wiki/` — a whole-tree grep also returns a dozen `raw/` sources that merely mention a skeleton by name, and `reviews/acquisitions.md` and `reviews/housekeeping-jobs.md`, which are expected hits and R10's to prune. `scripts/report-lint.py` and `scripts/compile-hub-financing.py` are **not** on this list: R3 keeps checks A–F and R5 decides the second.

**R8 — Retire OSINT's own mirror.** CORPUS's `mirror.bat` now backs up **both** repos: OSINT and CORPUS working trees + `git bundle` to Dropbox, plus one FreeFileSync pass (`repos-to-flash.ffs_batch`) copying both repos to `D:`. Remove the `run mirror.bat` close step from `SWEEP-CYCLE`, and the `## Mirror` section that documents it, and retire OSINT's `mirror.bat` + `Repo-mirrors.ffs_batch`.

**Half of this has already happened, and the half that has not is live** *(checked 2026-08-16 — do this one ahead of the rest of the list)*. Both files are gone from OSINT's working tree but still tracked: `git status` shows them as unstaged deletions. `SWEEP-CYCLE` meanwhile still carries `run mirror.bat` as the last command of the night, so the cycle's close step points at a file that is not there. Commit the deletion and cut the step and the section together. **`LINT` #19 is already false-alarming on this**: it compares the newest line of `logs/mirror_log.md` against the newest `End` in the cycle log, and OSINT's mirror log stops at 2026-08-11 20:10 while CORPUS's mirror has been running the OSINT legs since — 2026-08-14 20:50 in CORPUS's own `logs/mirror_log.md`. So OSINT has been reporting an unmirrored vault, nightly, while the backup ran. Retire #19 with the mirror, or repoint it at CORPUS's log.

All of which is unless you want an independent OSINT-only backup — in which case restore both files, keep the step and #19, and note the duplication.

**R9 — Wire the request feed (the only OSINT-ward channel).** CORPUS writes a machine-readable `logs/requests-for-osint.csv` — gaps and named documents a report needs, that OSINT's sweeps should chase. Give `ACQUIRE` (and the deep/country sweeps) a step that reads it and takes each request as a brief; what they fetch lands in `raw/` the ordinary way, and CORPUS's next scan settles the gap. This replaces the CORPUS-side half of the old report→gaps→acquire loop.

**The contract, since OSINT has to code against it.** The file is `C:\CORPUS\logs\requests-for-osint.csv`, columns `raised,unit,row_id,name,subject,type,request,url,status`. **OSINT reads it and never writes it** — this is the single exception to *OSINT does not read CORPUS*, and it stays one-way, so a request is closed by CORPUS's next scan finding the record in `raw/` and not by OSINT marking the row. It holds a header and one empty record today, so land a real request in it before wiring `ACQUIRE` against it; otherwise there is nothing to test the step on.

**R10 — Update the vault's own docs — but the boundary statement goes first, not last.** This task splits in two, and only one half belongs at the end.

**The boundary into `CLAUDE.md` before anything else on this list.** OSINT's `CLAUDE.md`, `SWEEP-CYCLE.md` and `ACQUIRE.md` mention CORPUS nowhere at all today — the word does not appear in any of them. Until that sentence lands, every OSINT session opens under the pre-migration model with nothing to anchor this file against, including the sessions that action the tasks above. State it plainly: OSINT collects and classifies; CORPUS compiles, reports and analyses over a read-only view; OSINT writes nothing to CORPUS and reads only the R9 request feed.

**The pruning last, once the shape is settled.** `SWEEP-CYCLE`, `STATUS.md`, `wiki/index.md`, `CLAUDE.md`, `reviews/housekeeping-jobs.md` and `reviews/acquisitions.md` lose their references to the retired passes. `REPORT-LINT.md` needs its own pass: the file survives on checks A–F, so what goes is its cross-references to `wiki/report-layer.md` §6 and to checks G–K, both of which travel to CORPUS at R3. Keep `wiki/index.md`'s Processes directory current, per OSINT's own rule.

**R11 — Retire the entity *pages*; keep the entity *tags*.** *(Bill, 2026-08-16 — populating them costs time and tokens for a level of detail the work does not need. The first retirement OSINT initiates rather than CORPUS; it is listed here because CORPUS reads what it removes.)*

`ENTITY-PASS.md` opens by saying exactly what it is: the pass that turns entity *tags* into entity *pages*. `INGEST.md` step 4 deliberately does not mint pages — ingest tags, and the pass decides later with a count in hand — so the tags are written on the hot path and are already paid for, and the pages are the model work. **Retiring `ENTITY-PASS`, the 1,891 pages under `wiki/entities/` (9.4 MB) and the ten `entities-index*.md` files (2,206 lines) takes the whole saving.** The `entities:` field on sources stays: it costs nothing further, 9,174 of 9,407 sources carry one, and it is a published column in CORPUS's `raw-catalogue.csv` and a facet count in `raw-catalogue.json`.

**Precondition — lift the region map out first, or CORPUS's region reports silently narrow.** `report-region-init.py` scopes a region by both halves of a rule: sources carrying the place code, *and* sources that reach the region only through an institution. The second half is built from the entity pages' own frontmatter — `entity_type` in (`organisation`, `government-body`, `initiative`, `instrument`) plus a regional `places` list — so removing the pages removes half the scope, with no error to show for it and a shorter source list as the only symptom. **291 pages carry that membership** (XAF 162, XGL 121, XSS 52, XWA 29, XEA 14, XSA 12, XCA 11, XNA 1). A lookup of slug, `entity_type` and place codes carries all of it; write it to `lookups/` before the pages go and name the file here, so CORPUS can repoint. The other two CORPUS reads of the pages are cosmetic and can simply go — a financier's display-name fallback in `finance_lib.py`, and the reading list a region work order prints — though losing the first makes `lookups/financier-names.csv` coverage load-bearing and so raises the stakes on REPORT-LINT check D.

**`LINT` #4 will ask for the pages back.** It rewires or retires broken `[[links]]` per `wiki/reference.md` §9's referrer bands, and the top band reads **≥10 → create the wanted page**. With the pages gone and the tags kept, several hundred slugs sit above that bar and the check reads them as a backlog to mint — undoing R11 one lint at a time. So `CLAUDE.md` → *Entities*, `reference.md` §5 (the paging bar) and §9 (the bands), and `LINT` #4 all move in the same change, to say that a tag is now a terminal state rather than a page deferred. `ENTITY-PASS`'s backlog in `reviews/housekeeping-jobs.md` goes with them.

## What OSINT keeps — the guardrail against over-retiring

Do **not** retire any of these; CORPUS depends on them or they are OSINT's core:

- **Collection & classification:** every `SWEEP-*`, `INGEST`, `UPDATE-WIKI`. *(`ENTITY-PASS` was on this list until R11 retired it. The tagging survives it — that is `INGEST`'s, and it stays.)*
- **The `entities:` tag on sources** — kept explicitly by R11 when the pages go. CORPUS publishes it as a catalogue column and counts a region's institutions with it.
- **Quality & gaps loops:** `ACQUIRE`, `RECONCILE`, `PRUNE`.
- **Finance/budget record collection:** the sweeps and extractors named in R4.
- **The wiki:** `HUB-COMPILE` (hub prose), concepts, intersections, place hubs — CORPUS reads the place hubs and `wiki/intersections/` when it initialises a new report.
- **`LINT`** — vault hygiene, but **not unchanged**: #19 (mirror freshness) and #26 (output freshness) verify things this list retires and go with them, at R8 and R2, and #4's referrer bands are rewritten at R11. Everything else stands.
- **`raw/`, `lookups/`, `wiki/`** — committed and stable; these are the evidence CORPUS reads, from the working tree through its workroot junctions. **`index/`** it does not read at all: it builds its own.

## Sequencing

**Two things come before the numbered order.** R10's boundary sentence goes into `CLAUDE.md` first, because every session that actions the rest needs it. Then R8's live half — commit the mirror deletion and cut the dead close step — because until that is done the cycle's last command points at a file that is not there, and `LINT` #19 reports a failure that is not real.

**Then a ruling, before anything is deleted.** R3's A–E question has to be answered, because R4 and R6 decide it by default if they run first.

R1–R3 and R6 are the report layer and can go together once that ruling is in. R4–R5 are the finance seam; do R5 in the same change as R4 so the hub prose never reads a dead file. R8's remaining question is Bill's call on whether an independent OSINT-only backup is wanted. R9 is the one that keeps the gaps loop alive across the boundary and should not be skipped. R11 is independent of all of it and can go at any point, provided its own precondition — the 291-row region lookup — lands before the pages do. R10's pruning last, once the shape is settled.
