---
type: proposal
title: Migrating and re-founding the output layer in Corpus
last_reviewed: 2026-08-13
status: agreed; editorial register v0.3 (light touch), in force
---

# Migrating the output layer from OSINT to Corpus — and giving it a voice

*(Revised 2026-08-13 after Bill's steer. Two things changed from the first draft: the scope is now **all of `outputs/`**, not just the reports; and the reports acquire a **declared editorial position** rather than staying register-neutral. Written to Corpus conventions: one line per paragraph.)*

## The boundary, restated

**OSINT collects and classifies. Corpus compiles, reports, and analyses.**

That is the clean line, and everything follows from it.
OSINT owns the evidence: `raw/` (sources with their structured frontmatter — finance records, budget lines, facets), `index/`, `lookups/`, and the internal `wiki/` synthesis (hubs, entities, concepts). It runs the sweeps, `INGEST`, `UPDATE-WIKI`, `HUB-COMPILE`, `LINT`.
Corpus owns everything derived for a reader: the catalogue, the non-state-finance CSVs, the budget CSVs, and the report-and-analysis layer. It reads OSINT's `raw/` and `lookups/` read-only — the access it already has — and writes nothing back.

This is confirmed feasible in the code. Every output derives from read-only inputs: `build-catalogue.py` reads `raw/`; `build-finance-page.py` reads finance and budget records out of `raw/` plus two `lookups/` tables; the report scripts read `raw/`, `index/`, `lookups/`. Nothing that produces an output needs to write into OSINT.

## What Corpus now owns

- **The catalogue** — `build-catalogue.py`, `raw/` → `outputs/catalogue/`.
- **Non-state finance** — `build-finance-page.py`, `raw/` → `outputs/non-state-finance/`.
- **Budget CSVs** — the same script, `raw/` budget records → `outputs/budgets/`. The **compile** is Corpus's; the suspended **extraction** of new budget data from PDFs (`BUDGET-EXTRACT`, `new-budget/`) is collection work and stays with OSINT.
- **The report-and-analysis layer** — `REPORT-UPDATE`, the report checks, and the ledgers/gaps/issued documents, relocated into Corpus and authored here.

## What stays with OSINT

- Collection and classification — all sweeps, `INGEST`, `UPDATE-WIKI` — the nightly load the colleague keeps.
- The internal wiki compiles — `HUB-COMPILE`, and the hub-`## Financing` prose. **The hubs are private wiki navigation the site never publishes**, so they and the checks that verify them (`REPORT-LINT` B, C, E, F) stay OSINT-side. Corpus takes the checks that verify *its* outputs: **A** (finance CSVs rebuild from records), **D** (financier display names), and **G–K** (the reports).
- `LINT` and vault hygiene.

## The hub coupling — the one seam to name

`FINANCE-COMPILE` does two jobs from one aggregation: it writes the CSVs (now Corpus's) and it rewrites each hub's `## Financing` prose (OSINT-internal wiki).
After the split, OSINT's hub compile needs the finance numbers, which Corpus now produces.
Recommended resolution: OSINT's hub compile re-derives its numbers from `raw/` directly (it can — the aggregation is a pure function of `raw/`), so neither repo depends on the other's build order. Corpus reads `raw/` for the CSVs; OSINT reads `raw/` for the hub prose; the shared truth is `raw/`, not either output. This is worth confirming with the colleague and recording as a standing constraint.

## What we agreed

- **Run manually for now**, schedule once bedded down.
- **Port the scripts** into Corpus `build/` and maintain them there.
- **Go straight to Phase 2** — Corpus becomes the single, authoritative home of the output layer; no parallel-run gate.
- **Rewrite the in-flight monthlies** rather than ageing them out — in line with the editorial reframing below.
- **Note 6 is moot** — Corpus builds its own ledgers clean, so the old count discrepancy does not carry over.
- **Nothing in `outputs/` was ever public** — it was all build-phase. So the immutability and never-reissue-a-slug constraints do not bind retroactively; Corpus is free to re-cut the whole layer. They begin to bind at public launch, not before.
- **Sunday target (assumed): a full outputs rebuild.** OSINT is frozen until Sunday and credits are expensive, so the milestone is that Corpus can regenerate *all* of `outputs/` — catalogue, finance, budgets, report ledgers — from the frozen `raw/` snapshot, proving it no longer needs OSINT to write. Say if you meant something narrower.

## The reframing: reports with a declared position

You've said the reports should **analyse, not only report** — that Corpus carries a noticeable editorial position, the sovereignty-and-colonialism lens as the leading example, developed dialectically.
This overturns the one thing the OSINT report layer was most careful about. Its §10 register bans first person, verdicts, argumentative headings, and taking any party's framing into the report's voice — on the principle that *"a reader who cannot tell where the evidence stops and the writing starts discounts the evidence too."*
That principle does not disappear because Corpus takes a position. It has to be **satisfied by other means**, because the evidence is exactly what earns Corpus the right to an opinion. The re-founding below is how.

### Corpus editorial register — v0.3, light touch

**One principle: the evidence speaks; the lens decides what gets noticed and connected, and then gets out of the way.**

*(Revised after Bill's steer, 2026-08-13: the position is light-touch and explicitly not polemical. The lens is a way of seeing, not a verdict laid over the facts. Most sentences in a report should be indistinguishable from the OSINT register — dated, cited, plain. The editorial hand shows in selection and in the occasional connecting sentence, rarely in an adjective and never in a charge.)*

- **The spine stays as disciplined as OSINT's.** The ledger, the tables, every dated figure, the published *Not held* count — script-emitted, cited, honest about gaps, exactly as now. Its neutrality is what makes any reading credible. A reader must always be able to **take the facts and refuse the reading**; that is the test the whole thing has to pass.
- **The prose stays factual first.** §10's discipline mostly holds: dated, attributed, no flash verbs, no staged reveals, no arguing a heading. What changes is narrow — a report may *connect* facts the lens brings together, and may name a pattern the evidence already shows, in a sentence a reader can check against the rows above it. It states the connection; it does not press it.
- **The lens is a quiet set of questions, asked by what gets included.** Who owns the infrastructure, who holds the data and under whose jurisdiction, what dependency a financing arrangement creates, who is vendor and who is regulator. These shape which facts a section foregrounds. They rarely need to be spoken; the selection carries them.
- **Where a reading is offered, it is visibly a reading and rests on the dated facts beside it** — one sentence, not a paragraph, and never a flourish. If the point is real, the facts above it have usually already made it, and the sentence only names it.

Worked contrast, on the same facts §10 uses as its model:

> **§10 (evidence, then stop):** the circular of 24 July sets no implementation deadline, scope or compliance mechanism; the estimates published the next day carry no budget line for the agency named to implement it.
>
> **Corpus, light touch:** the same two dated facts — then, at most, one plain connecting sentence: the mandate names an implementing agency the same week's estimates do not fund. *(No charge, no thesis. It states the gap between two dated documents and leaves the reader to weigh it. The polemical version — "a document rather than a programme" — is exactly what this register rules out, as §10 already did.)*

**Consequences to handle.** This supersedes §10 for Corpus only — OSINT's internal reports keep it as written. `report-register-check.py`'s tic-scanner still runs, but reports rather than gates; a connecting sentence is not a defect. Checks G–K (links held, prose agrees with the ledger, vocabulary, as-of honesty) bind unchanged — a position, however light, raises the cost of an unchecked figure, it does not lower it.

**This section is v0.3, the light-touch register now in force** — settled with Bill after the South Africa test case. The earlier intent to keep developing the voice dialectically is closed; the register is evidence-led and non-polemical, the lens carried mostly by selection.

## The gaps loop still crosses the boundary

Unchanged from the first draft, and still the one hard coupling. A *Not held* row becomes a research brief; OSINT's sweeps are what chase it; Corpus can't write to OSINT.
Mechanism: Corpus writes a machine-readable **request feed** (`logs/requests-for-osint.csv`) that OSINT reads on its own schedule; OSINT fetches and ingests into `raw/`; Corpus's next scan sees the new source arrive and settles the gap itself, stamping `probe_at` — which moves to Corpus with the ledger. `raw/` is the return channel it already is. Nothing in Corpus blocks on OSINT having acted.

## Standing constraints to agree with the colleague

The mirror of the constraints already atop `logs/notes-for-osint.md`, now that Corpus depends on OSINT's evidence:

- `raw/`, `index/` and `lookups/` stay git-tracked and committed — Corpus reads committed `HEAD`.
- Slugs in `raw/` stay stable — a re-slugged source reads as new to Corpus.
- The hub compile re-derives from `raw/`, not from Corpus's CSVs — no cross-repo build-order dependency.
- The request feed is honoured on some cadence, or the gaps loop stops draining.

## Revised phasing — straight to Phase 2, against the frozen snapshot

**Phase 2a — port and rebuild (before Sunday).** Port the output scripts into `build/`, pointed at OSINT's frozen `raw/`/`index/`/`lookups/` read-only. Rebuild all of `outputs/` into a Corpus-owned tree from the snapshot. This is the proof of independence and the Sunday milestone.

**Phase 2b — re-found the report layer with the new register.** Rebuild the ledgers clean (Note 6 moot), and draft one real report under the v0.3 editorial register — a live test of the voice, the thing we iterate on together. Rewrite the in-flight monthlies to match once the register settles.

**Phase 2c — cut the site over.** Render the site from Corpus-owned state; retire the report/finance/catalogue halves of `scripts/pull.py`. Add the final verification: a full render + A, D, G–K over every unit before anything is called authoritative.

**Phase 3 — close the loop (after Sunday, needs OSINT).** Stand up the request feed, move `probe_at` into Corpus, confirm a gap minted in Corpus reaches OSINT's sweeps and returns as a source.

## What this buys

OSINT's night sheds not just the report writing but the whole compile-for-reading half, which is the token relief you're after.
Corpus stops being a mirror of state written in a repo it may not touch, and becomes what it should be: the place the evidence is compiled, read, and given a position — owning its outputs and authoring its voice.
The deepest change is the last one. A derived view with no opinion was always a slightly false shape for this project; the published work at data-landscapers.com already has a position, and the reports that feed it can now share it — openly, and resting on evidence disciplined enough to carry the weight.
