---
type: design-note
title: progress-report-redesign.md — the indicator-framed country progress report
last_reviewed: 2026-08-28
status: in force — implemented; every country unit carries indicators.csv
---

# The indicator-framed country progress report

## 1. What it is

The country progress report is a fixed frame of **indicators** — one row per indicator, the same set for every country: `lookups/indicators.csv`, 121 indicators over all 38 taxonomy Level-2 subjects. **The frame covers the 54 countries only**: XAF, XSA and XWA keep the region progress renderer, whose sections deliberately run from institutions outward rather than through the taxonomy.

This fixes two problems by construction. The "random systems and instruments" problem goes because the report's rows are chosen by design, not by arrival. The baseline problem goes because the question each row answers is no longer a diff of two dated positions (one of which the base often never held) but *what happened on this indicator in the twelve-month window* — with **No evidence** as an honest, cheap answer where the base holds nothing.

The document shape: **one table per Level-1 chapter**, in taxonomy order, columns **Topic L2 · Indicator · Developments · Progress**. No per-L1 narrative blocks — the Developments cell does the narrative's job at the indicator level.

## 2. The ledger stays the record layer; indicators are a view over it

`ledger.csv` is unchanged as the evidence layer. `outputs/reports/{unit}/indicators.csv` — indicator id, mapped `row_id`s, summary, developments, progress, sources — is maintained like the ledger, never rebuilt. A row that maps to no indicator simply does not appear in the progress report: the frame defines what progress is asked about, and everything else stays on the ledger, feeding the status inventory and the monthly, where an inventory of everything held is defensible.

Every hyperlink in a Developments cell resolves through a ledger row's `sources`, so checks G and M carry over without modification. The ledger's `movement` column serves the monthly and **is not read by the indicator layer** — the Progress vocabulary is a separate closed set that happens to share four words; neither derives from the other, and merging them would be a defect.

**Indicator ids are `{subject-slug}--{slug-of-full-indicator-text}`**, minted mechanically — an id nobody composes by hand cannot be composed inconsistently — never reissued, never renamed, the same discipline as `row_id`. Never a sort number: an id that renumbers when a row is inserted is not an id. `lookups/indicators.csv` is the canonical list; an indicator is added by editing it. (The originating wireframe in `prep/` is retired — two copies of one list with nothing comparing them is the drift pattern the shared-assets lint exists to catch, and there would be no lint here.)

## 3. The Progress vocabulary

**Advanced** · **Stalled** · **Regressed** · **Mixed** · **No change** · **No evidence**.

- *Advanced* — a system entered service, a stage completed, an instrument was made.
- *Stalled* — a stated target passed without delivery. Distinct from No change, and often the most newsworthy state an indicator can be in.
- *Regressed* — an instrument withdrawn or neutralised, or a reported position worsened.
- *Mixed* — the indicator's instruments moved in different directions. **The qualifying clause is mandatory** and names which moved which way: *Mixed — act enacted, regulations stalled*. (A second row per indicator was considered and rejected: it breaks the one-row frame and reinstates the per-instrument view the redesign retires.)
- *No change* — the base holds a standing position and nothing in the window touched it. The standing position is cited, so the cell still carries a link.
- *No evidence* — the base holds nothing on this indicator. Never linked; there is nothing behind it.

**What is testable is narrower than the vocabulary**: *No evidence ⟺ zero mapped rows* (both directions, plus empty Developments and no link); *Progress ≠ No evidence ⇒ Developments non-empty*; *Mixed ⇒ qualifying clause present*. Everything else is vocabulary closure only — the five substantive stems are drafter's judgements, since a row published inside the window can merely restate a standing position. Stems and qualifiers work as in `report-layer.md` §3; the stem is what the check tests. Where several rows map to one indicator, the dominant direction is the drafter's call, recorded in the qualifier where the plain stem would mislead.

## 4. No evidence is presented, not counted

**Every indicator row prints, including No evidence rows.** The fixed frame is precisely what makes the gaps visible, and that visibility is the feature — a finding about the base and sometimes about the country. **There is no published no-evidence count**: an explanatory paragraph at the top of the report does the work — what the frame is, what No evidence means (the base holds nothing, which is not a claim that nothing exists) — renderer-emitted boilerplate, identical across countries.

## 5. The Developments cell: terse in the table, full in the expander

The cell shows a **terse summary** — a clause or two, hyperlinked on the claim. The **full text** — dated developments, each cited on the claim it supports — sits behind a **`<details>` expander per row, in a table baked into the page**. The shared datatable component is not used: it escapes every cell, so prose cannot carry inline links through it, and its case is arithmetic that does not transfer — it earns its keep on finance's 1,257×20, not on 121 fixed rows read in taxonomy order. A baked table keeps inline citations, works with JavaScript off, and keeps the PDF.

Both texts are drafted prose with the narrative-block treatment transposed to the indicator: they live in `indicators.csv`, carry across on re-render, and are subject to the check-L equivalent — **an indicator whose Progress is anything but No evidence and whose Developments is empty fails the check**. A No evidence row carries no prose; the value is the statement. The register check reads the indicator file's prose columns, so the redesign does not trade a checked document for an unchecked one. Word bands are in `report-country-skeleton.md` → *Word budget*.

## 6. Measures are stories of direction, not calculated levels

The measure-type indicators — penetration, affordability, grid reliability, literacy — report *what the base says moved*: a story that a figure rose or fell, dated and cited. **No absolute level is computed or asserted as current state.** Reference studies are cited, not absorbed; a global index's release is a dated story about a measure, not a promotion of its figure into the country's current position. These indicators move slowly, and No evidence or No change is their normal state.

## 7. Publication shape

A baked HTML table inside the existing pipeline, and **the PDF edition continues** under the editions rule — the PDF prints each row's detail text **expanded**, since a PDF has no expander and the full text is the document. The status report and the monthly are unchanged. The shape check (`report-layer.md` §7) and check J's period parsing retire for this document — the frame replaces the period comparison they guarded.

## 8. The coverage byproduct — not yet built

The mapping pass should emit a standing cross-country summary — per indicator, which countries hold evidence and which are No evidence (`indicator_id, country, rows_mapped`) — to `outputs/reports/indicator-coverage.csv`, refreshed whenever ledgers or mappings move. Its purpose is **sweep targeting**: the empty cells are the best possible input to an OSINT sweep brief, framed subject×country. Delivery to OSINT stays via the exchange folder on Bill's call, never a Corpus path.
