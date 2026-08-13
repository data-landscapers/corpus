---
type: proposal
title: Migrating the report layer from OSINT to Corpus
last_reviewed: 2026-08-13
status: draft for Bill's review
---

# Migrating the report layer — REPORT-UPDATE and REPORT-LINT — into Corpus

*(A proposal, not a change. Nothing here has been actioned. It reviews the current arrangement, states what should move and what must not, and sets out a phased way to do it. Written to Corpus conventions: one line per paragraph.)*

## The problem, stated plainly

`SWEEP-CYCLE` runs nightly in OSINT and is now managed by a colleague who holds sole write on that repo.
It is consuming too many tokens, and the ask is to spread the load by moving the report-writing half of the night out of OSINT and into Corpus.
The natural candidates are the two passes that *write prose*: `REPORT-UPDATE` (brings the country and region reports forward each night) and the report-layer half of `REPORT-LINT` (verifies what those reports publish).
Everything else in the night — collection and classification — stays where it is.

## Where the cost actually is

The expensive thing in the report layer is a **model reading sources and editing prose**, not the scripts around it.
`report-scan.py`, `report-render.py`, `report-lint.py` and `report-register-check.py` are cheap: the scan is a set-difference over slugs, the renderer rebuilds tables from a CSV, the linters read and compare.
`REPORT-UPDATE`'s tokens go on step 2 of its run — one sub-agent per unit reading the night's new sources against that unit's ledger and deciding, per source, whether a row moved.
That is the load to relocate. The scripts come with it because they are its scaffolding, but they are not what costs.

This matters because it tells us the migration is clean: we are moving a *reading-and-writing* job that already runs off a well-defined, file-based interface, not untangling logic knotted into the sweep.

## What the report layer reads and writes today

`REPORT-UPDATE` and report-layer `REPORT-LINT` touch six things, all inside OSINT:

- **reads** `raw/` — the night's ingested sources, the input the pass reads (private verbatim bodies; ~2.8 GB).
- **reads** `index/` — slug→URL resolution, needed to render links and to run check G.
- **reads** `lookups/` — `countries.csv`, `taxonomy.md`, `report-*-sections.csv`, `financier-names.csv`.
- **reads and writes** `outputs/reports/{unit}/ledger.csv` and `gaps.csv` — the record layer the whole thing maintains.
- **reads and writes** `outputs/reports/{unit}/considered.txt` — the pass's own memory of which slugs it has read (the set-difference state).
- **writes** `outputs/reports/{unit}/{unit}-status.md` and the dated `monthly`/`progress` issues — the published documents.

The site already consumes the last three: `build/pull.py` copies OSINT's committed `outputs/reports/` into Corpus's `upstream/`, and the renderers turn them into `site/`.

## The core move

**The report layer's own state — ledgers, gaps, considered, and the issued documents — moves out of OSINT and into Corpus, and Corpus authors it in place.**

Once it lives in Corpus, the round-trip disappears.
Today the report state sits in OSINT, is written by OSINT's nightly pass, is pulled into Corpus, and is rendered.
After the move, Corpus reads OSINT's `raw/`, `index/` and `lookups/` (read-only, which is exactly the access it already has), maintains the ledgers itself, and renders the site directly from state it owns.
OSINT stops carrying report state and stops spending a model on it.

This fits the set-difference design perfectly. The scan asks "which slugs in `raw/` are not yet in my ledger or my `considered.txt`?"
`raw/` stays in OSINT and is read-only to Corpus; the ledger and `considered.txt` move to Corpus and are written by Corpus.
The question is answerable across the boundary because the two halves it compares sit on the correct sides of it — the source of record stays put, the memory of what has been read moves with the reader.

## What moves, what stays

**Moves to Corpus:**

- `REPORT-UPDATE` — the nightly pass, as a Corpus procedure with its own trigger and cadence.
- The report-layer checks of `REPORT-LINT` — **G, H, I, J, K** — plus `report-register-check.py` (§10 register and word budget). These verify the reports, which Corpus now owns.
- The report state — `outputs/reports/**` — relocated to a Corpus-owned tree (proposed `reports/` in Corpus, rendered into `site/` as now).
- The scripts these passes call — `report-scan.py`, `report-render.py`, the G–K portion of `report-lint.py`, `report-register-check.py`, `report-country-init.py`, `report-region-init.py`, and their shared `vault_lib` — ported into `build/`.

**Stays in OSINT (the colleague's daily job):**

- `SWEEP-CYCLE`, all sweeps, `INGEST`, `UPDATE-WIKI` — collection and classification, unchanged. This is the load the colleague keeps.
- `HUB-COMPILE`, `FINANCE-COMPILE`, `LINT` — the compiles and vault hygiene.
- The **finance and hub checks of `REPORT-LINT` — A, B, C, D, E, F**. These verify OSINT's *own* compiles (non-state-finance exports, hub Financing and Recent-developments prose), and they already run as `FINANCE-COMPILE`'s last step. They should stay next to what they check. Only the report checks G–K travel.
- `outputs/budgets/`, `outputs/non-state-finance/`, `outputs/catalogue/` — Corpus keeps pulling these as it does today.

So `REPORT-LINT` splits along the seam that already exists inside it: A–F stay and verify OSINT's compiles; G–K move and verify Corpus's reports.

## The one hard problem: the gaps loop crosses the boundary

The report layer is not a dead end. It feeds a loop: a ***Not held*** row becomes a line in `gaps.csv`, which becomes a brief for `SWEEP-COUNTRY-DEEP` and an acquisition request for `ACQUIRE`; `ACQUIRE` fetches the document into `raw/` and stamps `probe_at`; the next report reads the new source and settles the gap.
Today that loop closes inside one repo. After the move, its two halves sit in different repos owned by different people, and Corpus cannot write to OSINT.

This is exactly what point 9 of your message anticipates, and the mechanism already half-exists.
`NOTES-FOR-OSINT.md` is Corpus's write-nothing channel into OSINT: Corpus records a finding, the colleague actions it in an OSINT session.
The gaps loop needs a dedicated, machine-readable version of the same idea — call it a **request feed** that Corpus writes and OSINT reads:

- When Corpus's report pass mints a ***Not held*** row that names a fetchable document, it appends a line to `reports/requests-for-osint.csv` (in Corpus) rather than to OSINT's `acquisitions.md`.
- The colleague's OSINT passes read that feed, fetch or sweep for the named documents, and ingest what they find into `raw/` in the ordinary way.
- Corpus's next nightly scan sees the new source arrive in `raw/` through its set-difference, settles the gap, and stamps `probe_at` **itself** — because it now owns the ledger.

That keeps write-ownership clean on both sides and uses `raw/` as the shared channel it already is.
`probe_at` stamping moves from `ACQUIRE` to Corpus, which is correct once Corpus owns the ledger the stamp lives in.
The feed is a contract, not a coupling: OSINT reads it or not on its own schedule, and nothing in Corpus blocks on OSINT having acted.

## What has to be agreed with the colleague as standing constraints

The migration adds Corpus dependencies on OSINT that OSINT must not break silently, the mirror image of the constraints already at the top of `NOTES-FOR-OSINT.md`:

- **`raw/`, `index/` and `lookups/` stay git-tracked and committed.** Corpus reads OSINT's committed `HEAD`; a pass that stops committing them stops the reports updating with no error.
- **Slugs in `raw/` remain stable identifiers** — a re-slugged source reads to Corpus as a new source and a vanished old one.
- **The request feed is honoured on some cadence**, or the gaps loop stops draining and the reports slowly fill with un-chased ***Not held*** rows.

These belong in `NOTES-FOR-OSINT.md` as new standing constraints, and in OSINT's own `CLAUDE.md` once the colleague accepts them.

## Open decisions for you to settle

I have made a recommendation on each; these are the points where I should not simply assume.

1. **Cadence and trigger.** `REPORT-UPDATE` no longer rides inside `SWEEP-CYCLE`, so it needs its own clock. Recommended: a Corpus scheduled task that runs after OSINT's nightly cycle has committed, keyed off a new OSINT commit touching `raw/`. Alternative: you run it by hand when you want the site current.
2. **Scripts — port or call.** Recommended: copy the report scripts into Corpus `build/` and maintain them there, since Corpus can't depend on OSINT's working tree and the two repos now have different owners. Cost: `vault_lib` and the section lookups get a second home that must be kept in step — mitigated by pulling the lookups into `upstream/` (this is already open note 9).
3. **Where finance checks A–F run.** Recommended: leave them in OSINT with `FINANCE-COMPILE`. Alternative: Corpus re-runs them read-only over what it pulls, as a gate before publishing. The second is belt-and-braces and costs little.
4. **Migrating in-flight `monthly` prose.** The 2026-08-10 marker-granularity change already left existing monthlies un-migrated (report-layer §5). Moving repos is a natural moment to decide whether to re-sort that prose or let it age out. Recommended: let it age out; migrate none.
5. **Note 6 (Kenya's ledger count disagrees across three files) blocks trusting the ledger.** It should be resolved *before* Corpus takes ownership, not after, so Corpus starts from a ledger it can trust.

## A phased way to do it

**Phase 0 — settle preconditions.** Resolve note 6 (ledger-count discrepancy). Agree the three standing constraints with the colleague. Decide the five open questions above.

**Phase 1 — Corpus reads, OSINT still writes.** Port the report scripts into `build/` and point them at OSINT's `raw/`/`index/`/`lookups/` read-only and at a *copy* of the report state. Run `REPORT-UPDATE` and G–K from Corpus in parallel with OSINT's, and diff the two outputs until they agree. Nothing is authoritative yet; this is the correctness gate.

**Phase 2 — hand over ownership.** OSINT drops `REPORT-UPDATE` and G–K from `SWEEP-CYCLE` (the token saving lands here). The report state relocates to Corpus as the single copy. Corpus renders the site from state it owns; the report half of `build/pull.py` retires, the finance/budget/catalogue half stays.

**Phase 3 — close the loop.** Stand up `reports/requests-for-osint.csv`, move `probe_at` stamping into Corpus, and confirm gaps minted in Corpus reach OSINT's sweeps and come back as sources. Add a final verification step: a full render + G–K pass over every unit, checked against the last OSINT-authored issues, before the first Corpus-authored issues are published.

## What this buys, and what it costs

The night in OSINT loses its most expensive model step, which is the point.
Corpus gains a writing job, but it runs on Corpus's budget and cadence, decoupled from the sweep — a heavy sweep night no longer drags the reports, and a slow report night no longer delays the catch.
The cost is a second home for the report scripts and a new cross-repo contract for the gaps loop, both manageable and both using channels (`raw/`, `NOTES-FOR-OSINT.md`) that already exist.
The deepest benefit is architectural: the site becomes a view of report state it *owns and authors*, rather than a mirror of state written in a repo it isn't allowed to touch — which is a more honest shape for a derived public surface than the current round-trip.
