---
type: design-note
title: progress-report-redesign.md — the indicator-framed country progress report
last_reviewed: 2026-08-26
status: agreed with Bill 2026-08-26 (Cowork session); CC's operational review (progress-report-redesign-review.md) accepted same day — table baked not datatable-drawn, regions out of frame, PDF kept. CC implements from this note.
---

# The indicator-framed country progress report

*(Design agreed between Bill and Cowork, 2026-08-26. This note is the decision record; CC reviews it operationally and owns the implementation. It supersedes the open question in `documentation/progress-report-scope.md` — the diagnosis there stands, but the answer chosen is none of its three options in the form stated: see §2.)*

## 1. What changes and why

The country progress report stops being an inventory of whatever ledger rows the base happened to accumulate, and becomes a fixed frame of **indicators** — one row per indicator, the same set for every country, defined in the wireframe (`prep/progress-report-wireframe-v2.csv`, 121 indicators over all 38 taxonomy Level-2 subjects).

**The frame covers the 54 countries only** *(CC review item 2, accepted 2026-08-26)*. XAF, XSA and XWA keep the current progress renderer: a region's sections deliberately run from its institutions outward rather than through the taxonomy, and the indicator list was not drawn for that document. Extending the frame to regions is possible later but is not part of this change.

This fixes both of Bill's complaints at once. The "random systems and instruments" problem goes by construction: the report's rows are chosen by design, not by arrival. And the baseline problem goes with it, because the question each row answers is no longer a diff of two dated positions (one of which the base often never held) but *what happened on this indicator in the twelve-month window* — with **No evidence** as an honest, cheap answer where the base holds nothing.

The document shape: **one table per Level-1 chapter**, in taxonomy order, with columns **Topic L2 · Indicator · Developments · Progress**. **No per-L1 narrative blocks.** The Developments cell does the narrative's job at the indicator level.

## 2. The ledger stays the record layer; indicators are a view over it

`ledger.csv` is unchanged as the evidence layer — rows, sources, checks G and M, all as `report-layer.md` states. What is added is a **mapping from ledger rows to indicators**: an `indicator` column on the ledger (or a per-unit mapping file — CC's call, see §8), keyed to a stable indicator id minted from the wireframe.

A row that maps to no indicator simply does not appear in the progress report. This settles `progress-report-scope.md`'s question more cleanly than any of its three options: no reclassification pass over 6,194 rows, no admission test to argue about, and the filter (its option 3) becomes principled rather than ad hoc — the frame defines what progress is asked about, and the Teraco expansions and rights-commission inquiries of this world remain on the ledger, feeding the status inventory and the monthly, where an inventory of everything held is defensible.

Every hyperlink in a Developments cell resolves through a ledger row's `sources` — slugs, resolved to URLs at render time as now — so the evidence rule — checks G and M, two halves of *every piece of evidence has a source* — carries over without modification.

The ledger's `movement` column stays exactly as it is, serving the monthly, and **is not read by the indicator layer** *(CC review item 8)*. The indicator Progress vocabulary (§3) is a separate closed set that happens to share four words; neither derives from the other, and merging them would be a defect, not a tidy-up.

## 3. The Progress vocabulary

**Advanced** · **Stalled** · **Regressed** · **Mixed** · **No change** · **No evidence**.

- *Advanced* — a system entered service, a stage completed, an instrument was made.
- *Stalled* — a stated target passed without delivery. Retained from the current vocabulary deliberately: it is distinct from No change and is often the most newsworthy state an indicator can be in.
- *Regressed* — an instrument withdrawn or neutralised, or a reported position worsened.
- *Mixed* — the indicator's instruments moved in different directions in the window. **The qualifying clause is mandatory** and names which moved which way: *Mixed — act enacted, regulations stalled*. Chosen over repeating the indicator row, which was considered and rejected: a second row per indicator breaks the one-row frame and reinstates the per-instrument view the redesign exists to retire.
- *No change* — the base holds a standing position and nothing in the window touched it. The standing position is cited, so the cell still carries a link.
- *No evidence* — the base holds nothing on this indicator at all. Never linked; there is nothing behind it.

**What is testable is narrower than the vocabulary** *(CC review item 7)*: *No evidence ⟺ zero mapped rows* (both directions, plus Developments empty and no link); *Progress ≠ No evidence ⇒ Developments non-empty* (§5's check); *Mixed ⇒ qualifying clause present*. Everything else is vocabulary closure only — Advanced, Stalled, Regressed, Mixed and No change are drafter's judgements throughout, since a row published inside the window can merely restate a standing position. Stems and qualifiers work as in `report-layer.md` §3; the stem is what the check tests.

Where several rows map to one indicator and one direction clearly dominates, the judgement is the drafter's (a model call, not a script), recorded in the qualifier where the plain stem would mislead — the same mechanism the current vocabularies use.

## 4. No evidence is presented, not counted

**Every indicator row prints, including No evidence rows.** The fixed frame is precisely what makes the gaps visible, and that visibility is the feature — ZAF, one of the largest ledgers in the base, currently has zero rows in 17 of 38 Level-2 subjects. **At least a third of a median country's indicators are No evidence before any mapping is done** — 42 of 121, on the most generous assumption available (every ledger row landing on a distinct indicator inside its own subject), and the real figure will run well above that floor because rows cluster on the same indicator *(CC, 2026-08-26)*. That is a finding about the base and sometimes about the country.

**There is no published no-evidence count.** An **explanatory paragraph at the top of the report** does the work instead: what the frame is, what No evidence means (the base holds nothing — which is not a claim that nothing exists), and that the content speaks for itself *(Bill, 2026-08-26 — consistent with his removal of the bare Not held counts from the other reports, which read as a number without an explanation)*. The paragraph is renderer-emitted boilerplate, identical across countries, not per-unit prose.

## 5. The Developments cell: terse in the table, full in the expander

The cell shows a **terse summary** — a clause or two, hyperlinked on the claim. The **full text** — dated developments, each cited on the claim it supports — sits behind a **`<details>` expander per row, in a table baked into the page** *(CC review item 1, accepted 2026-08-26, replacing the datatable proposed in the first draft of this note)*. The shared datatable component is not used: it escapes every cell, so prose cannot carry inline links through it, and its case is arithmetic that does not transfer — it earns its keep on finance's 1,257×20, while sorting and filtering across 121 fixed rows read in taxonomy order is a thin prize for an upstream change to a shared asset. A written table keeps inline citations exactly as the reports carry them now, works with JavaScript off, and keeps the PDF (§7).

Both texts are drafted prose and get the narrative-block treatment from `report-layer.md`, transposed to the indicator: they live in a **maintained per-unit file** (§8), are carried across on re-render so a rebuild costs a render and not a redraft, and are subject to a check-L equivalent — **an indicator whose Progress is anything but No evidence and whose Developments is empty fails the check**. A No evidence row carries no prose; the value is the statement.

## 6. Measures are stories of direction, not calculated levels

The measure-type indicators — mobile penetration, affordability, grid reliability, digital literacy and their kind — report *what the base says moved*: a story that a figure rose or fell, dated and cited. **No absolute level is computed or asserted as current state** *(Bill, 2026-08-26)*. This keeps the redesign inside the currency rules: reference studies are cited, not absorbed, and a global index's release is a dated story about a measure, not a promotion of its figure into the country's current position. These indicators will move slowly — annually at best, on index cycles — and No evidence or No change is their normal state.

## 7. Publication shape

The page stays inside the existing pipeline: a baked HTML table, and **the PDF edition continues** under the editions rule (`RENDER.md` §9) — `country.py`'s report cards glob for it, and a page with no PDF would silently drop progress from the country page *(CC review item 3, dissolved by the baked table)*. The PDF prints each row's detail text **expanded**, since a PDF has no expander and the full text is the document, not an extra. The status report and the monthly are **unchanged** by this redesign.

## 8. Open items — CC's, on review

- **The wireframe is final** *(Bill, 2026-08-26)*: `prep/progress-report-wireframe-v2.csv` — 121 indicators over all 38 L2 subjects, columns `Topic Sort, Indicator Sort, Topic L1, Topic, Topic L2, Progress indicator`. The two sort columns are **display order only**. Bill accepted the three proposed additions and kept both citizen-participation indicators (gov.discourse and include.access) deliberately.
- **Indicator ids.** Mint stable ids as `{subject-slug}--{slug-of-full-indicator-text}`, mechanically, no hand-shortening *(CC review item 9 — an id nobody composes by hand cannot be composed inconsistently)*; never reissued, never renamed — same discipline as `row_id`. Do **not** use `Indicator Sort` as the id: it is an ordering, and an id that renumbers when a row is inserted is not an id. `lookups/indicators.csv` (wireframe plus an `indicator_id` column) becomes the canonical list once minted, and **`prep/progress-report-wireframe-v2.csv` is then retired, not kept** — two copies of one list with nothing comparing them is the drift pattern the shared-assets lint exists to catch, and there would be no lint here. An indicator is added by editing the lookup.
- **Where the mapping and prose live.** One file is simplest: `outputs/reports/{unit}/indicators.csv` — indicator id, mapped `row_id`s, summary, developments, progress, sources — maintained like the ledger, never rebuilt. An `indicator` column on the ledger instead would put the mapping beside the evidence but leaves the prose needing a home anyway. CC's call.
- **The mapping pass emits the coverage summary as a standing byproduct.** A cross-country report — per indicator, which countries hold evidence and which are **No evidence** (long form: `indicator_id, country, rows_mapped`) — written to `outputs/reports/indicator-coverage.csv` and refreshed whenever ledgers or mappings move. Its purpose is **sweep targeting**: the empty cells are the best possible input to an OSINT sweep brief, framed subject×country (Bill, 2026-08-26). Delivery to OSINT stays as it is — via the exchange folder on Bill's call, never a Corpus path. Until the pass runs, `prep/indicator-coverage-summary.md` and its two CSVs are the subject-level proxy (Cowork, 2026-08-26): over the 54 countries in the frame, 309 of 2,052 country×subject cells are empty, so ≥635 of 6,534 country×indicator slots are guaranteed No evidence; emptiest subjects are digital.rural, finance.mou and the geopol.* cluster. *(CC measured 361 of 2,166 over all 57 units; the difference is the three regions, now out of frame per §1.)*
- **Renderer.** `render_progress()` is a rewrite, not an edit; the vocabulary change lands in `STATUSES`/`MOVEMENTS`'s sibling and in check I. The shape check (§7 of report-layer.md) retires for this document — the frame replaces the period comparison it guarded — and **check J follows** *(CC review item 6)*: `check_asof()` asserts the shape-check string and parses `period:`, and both halves need reworking for a document that carries neither.
- **Migration.** Mapping existing ledger rows to indicators is a model pass over the 54 country ledgers, run once at re-initialisation of the progress layer. Rows mapping to nothing stay on the ledger untouched. Before the first re-render, the 469 written narrative blocks (~636k characters) are archived per unit and fed to the indicator drafting pass as source material — CC's call, recorded in its review item 4. The register check is extended to read the indicator file's prose columns (review item 5), so the redesign does not trade a checked document for an unchecked one.
