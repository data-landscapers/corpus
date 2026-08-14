---
type: doc
title: OSINT migration — what CORPUS took over, and what OSINT now retires
last_reviewed: 2026-08-13
audience: OSINT (Bill, or a colleague's session run *in* OSINT)
status: written in Corpus — to be actioned in an OSINT session (logs/notes-for-osint.md)
---

# OSINT migration — the retirement list

*(Written from CORPUS, for OSINT. It briefs an OSINT session on what CORPUS has taken over and lists, as tasks, what OSINT should now retire. Action this **before** `notes-for-osint.md`, which assumes the boundary below is already in force. One line per paragraph, OSINT house style.)*

## What CORPUS is

CORPUS (`C:\CORPUS`, its own git repo) is the public-site layer for **corpus.data-landscapers.com**: country and regional reports, a source catalogue, and non-state-finance and budget data, served over the private research base that OSINT maintains.

Until 2026-08-13 CORPUS was a **mirror**: it pulled OSINT's `outputs/` and rendered it. That is no longer true. CORPUS now **authors** the output layer itself. The current architecture is CORPUS's `documentation/migration-report-layer.md`; this file is its OSINT-facing half.

## The relationship now — two repos, one direction

**OSINT collects and classifies. CORPUS compiles, reports, and analyses.**

CORPUS reads OSINT **read-only** — `raw/`, `lookups/` and the internal `wiki/`, and *not* `index/`, which it builds for itself — and writes only into its own tree. It never writes to OSINT, in any form. OSINT does not read CORPUS, and gains no publication step in its night, with one exception (the request feed, task R9).

CORPUS runs as two jobs on Bill's machine: **BUILD** (OSINT evidence → CORPUS `outputs/`) and **RENDER** (`outputs/` → the site). BUILD's compiles are pure functions of `raw/`; its report-update stage is a model pass; RENDER produces the site and backs both repos up (`mirror.bat`, which reads OSINT read-only).

**What OSINT must keep stable, because CORPUS reads it:** `raw/`, `lookups/`, `wiki/` — git-tracked, committed, and with stable slugs. **`index/` is not one of them and owes CORPUS nothing** *(2026-08-14)*: CORPUS builds its own index from `raw/` and `wiki/` rather than reading OSINT's, so OSINT's index is OSINT's business entirely. These are the standing constraints; they live in `notes-for-osint.md`, not here.

## The retirement list — tasks for OSINT

Each is *retire X, because CORPUS now owns it, keeping Y*. Do them once CORPUS is confirmed authoritative for the output layer (it is, as of the 2026-08-13 render).

**R1 — Retire the report layer.** Remove `REPORT-UPDATE`, `REPORT-COUNTRY`, `REPORT-REGION`, `REPORT-MONTHLY` as processes and drop the `REPORT-UPDATE` step from `SWEEP-CYCLE`'s nightly run (the line after `UPDATE-WIKI`). CORPUS authors ledgers and reports now. The ledgers, `considered.txt`, `gaps.csv` and issued documents under `outputs/reports/` are CORPUS-owned going forward; OSINT's copies become dead once R6 runs.

**R2 — Retire the nightly output refresh.** Remove the `run the output refresh` step (`outputs\ except budgets\, catalogue + capped narrative drain`) from `SWEEP-CYCLE`. CORPUS builds the catalogue (`build-catalogue.py`) and authors report narrative itself.

**R3 — Retire the report half of REPORT-LINT.** *(Corrected 2026-08-14 — an earlier draft of this task told OSINT to drop A and D. It should not. Bill's ruling of 2026-08-13: "REPORT-LINT splits along a seam already inside it — checks A–F stay in OSINT next to what they verify; G–K travel to Corpus.")*

**Checks A–F all stay in OSINT.** They verify the finance and hub compiles against `raw/`, and `raw/` is OSINT's — a check belongs next to the records it reconciles, not next to the CSV it happens to have produced. **Checks G–K travel to CORPUS** (link-held, prose-vs-ledger, vocabulary, as-of, register), because they verify the report layer, which is CORPUS's. Retire `REPORT-LINT` as a report-layer pass; fold A–F into `LINT` or `FINANCE-COMPILE`. Nothing here asks OSINT to give up a check.

**R4 — Retire the finance/budget CSV export.** `build-finance-page.py` (via `FINANCE-COMPILE` / `FINANCE-PAGES`) writes `outputs/non-state-finance/` and `outputs/budgets/`; CORPUS builds these now. **Keep all finance and budget COLLECTION** — `DOMESTIC-FINANCE-SWEEP`, `BUDGET-EXTRACT`, `COUNTRY-BUDGET-BATCH`, `SWEEP-COUNTRY-BUDGET`, `SWEEP-FINANCIERS`, `SWEEP-IATI` — because those write the finance and budget *records* into `raw/`, which is exactly what CORPUS reads. Only the CSV compile moves.

**R5 — Decide the hub `## Financing` prose (the one real coupling).** `compile-hub-financing.py` rewrites a hub's Financing sentences from `outputs/non-state-finance/{ISO3}-nonstate.csv` — a file OSINT will stop producing at R4. The hub is internal OSINT navigation, so it stays; pick one: **(a) re-derive** those sentences straight from `raw/` (recommended — keeps hubs self-contained and reading only OSINT's own evidence); **(b) freeze** the Financing prose as-is; or **(c) read** CORPUS's committed `outputs/`. Do not leave it reading a file that no longer gets written.

**R6 — Retire OSINT's `outputs/`.** Once R1–R4 stop producing it, `outputs/` (reports, catalogue, non-state-finance, budgets) is no longer read by anything — CORPUS reads `raw/`/`lookups/`/`wiki/`, never OSINT's `outputs/`. Remove it from git to reclaim space and end the two-authorities risk. Confirm CORPUS has a clean build first; keep one tagged commit as a fallback.

**R7 — Retire the report-layer specs and scripts.** `wiki/report-layer.md`, `wiki/report-country-skeleton.md`, `wiki/report-region-skeleton.md`, and `scripts/report-*.py` (`report-render`, `report-scan`, `report-register-check`, `report-country-init`, `report-region-init`) — CORPUS holds its own copies: the scripts in `scripts/`, and the three specs in `documentation/` as of 2026-08-14, adapted rather than mirrored (the register now points at CORPUS's own, and the gaps loop at the request feed). Nothing in CORPUS reads these three files from OSINT any more, so their removal breaks nothing here. Remove from OSINT unless something else in the vault imports them; grep first.

**R8 — Retire OSINT's own mirror.** CORPUS's `mirror.bat` now backs up **both** repos: OSINT and CORPUS working trees + `git bundle` to Dropbox, plus one FreeFileSync pass (`repos-to-flash.ffs_batch`) copying both repos to `D:`. Remove the `run mirror.bat` close step from `SWEEP-CYCLE` and retire OSINT's `mirror.bat` + `Repo-mirrors.ffs_batch`, unless you want an independent OSINT-only backup — in which case keep it and note the duplication.

**R9 — Wire the request feed (the only OSINT-ward channel).** CORPUS writes a machine-readable `logs/requests-for-osint.csv` — gaps and named documents a report needs, that OSINT's sweeps should chase. Give `ACQUIRE` (and the deep/country sweeps) a step that reads it and takes each request as a brief; what they fetch lands in `raw/` the ordinary way, and CORPUS's next scan settles the gap. This replaces the CORPUS-side half of the old report→gaps→acquire loop.

**R10 — Update the vault's own docs.** Prune `SWEEP-CYCLE`, `STATUS.md`, `wiki/index.md` and `CLAUDE.md` of references to the retired passes, and state the boundary plainly: OSINT collects and classifies; CORPUS compiles, reports and analyses over a read-only view. Keep `wiki/index.md`'s Processes directory current, per OSINT's own rule.

## What OSINT keeps — the guardrail against over-retiring

Do **not** retire any of these; CORPUS depends on them or they are OSINT's core:

- **Collection & classification:** every `SWEEP-*`, `INGEST`, `UPDATE-WIKI`, `ENTITY-PASS`.
- **Quality & gaps loops:** `ACQUIRE`, `RECONCILE`, `PRUNE`.
- **Finance/budget record collection:** the sweeps and extractors named in R4.
- **The wiki:** `HUB-COMPILE` (hub prose), entities, concepts, intersections, place hubs — CORPUS reads the place hubs and `wiki/intersections/` when it initialises a new report.
- **`LINT`** — vault hygiene, unchanged.
- **`raw/`, `lookups/`, `wiki/`** — committed and stable; these are the evidence CORPUS reads, from the working tree through its workroot junctions. **`index/`** it does not read at all: it builds its own.

## Sequencing

R1–R3 and R6 are the report layer and can go together. R4–R5 are the finance seam; do R5 in the same change as R4 so the hub prose never reads a dead file. R8 needs Bill's call on independent backup. R9 is the one that keeps the gaps loop alive across the boundary and should not be skipped. R10 last, once the shape is settled.
