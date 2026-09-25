---
type: doc
title: Budget documents — how to use the archetype table
reader: cc
last_reviewed: 2026-09-25
---

# Budget documents — the archetype table

*(The table is data: [`lookups/budget-archetypes.csv`](../lookups/budget-archetypes.csv), one row per structural archetype. It moved there from this file on 2026-09-25, strategic review 5 R85, because it grew a row with every document read. The full reasoning behind each row is in OSINT's `budget-extraction-strategies.md`, published in [data-landscapers/osint-process](https://github.com/data-landscapers/osint-process).)*

**This table gets the figures off the page; [`budget-extract.md`](budget-extract.md) decides what they mean.** Scope, the origin gate, the stages, the record shape, cross-footing, scale per table and when an absence counts as a finding are all there.

## The table

| Column | What it holds |
|---|---|
| `id` | The key: the letter for a base archetype (`A`, `AN`), and letter/ISO3 for a variant or companion (`M/TGO`). A second variant from the same country takes a digit (`M/CAF2`). |
| `archetype`, `kind` | The letter, and `variant` or `companion` where the row modifies a base shape. |
| `name`, `seen_as`, `iso3` | The shape in words, the document it was first seen in, and that document's country. |
| `shape` | What the pages look like: axes, columns, grain, where the money tables are. |
| `how_to_read` | The extraction method and the trap. |
| `worked_example` | The cross-foot that proved a parse. It is the check to repeat. |

**Every new document either matches a row or earns one.** Match on shape, not country: a Congo finance law and a Gabon one can share a row, and three Mozambique documents need two. A match is noted in the sitting's commit and adds nothing here. A document that matches no row gets a new row in the same sitting, with the next free letter, or letter/ISO3 if it varies an existing shape. The row keeps the same four substantive columns and fits on one CSV line; its argument goes in the commit body.

## The toolchain, in order

1. `pdfinfo` for pages and producer (the producer hints at the archetype), then `pdftotext -enc UTF-8 <f> - | wc -c` over the **whole** document. A low count on the first pages means a graphical cover, not a scan.
2. `pdftotext -enc UTF-8 -layout` into `grep -n` to find tables by their captions before extracting anything.
3. **`pdftotext -table` as soon as `-layout` misaligns a wide table.** `-layout` keeps horizontal position, not columns. Its digit groups come back separated by spaces, so collapse runs of three or more spaces into a delimiter and read columns rather than matching numbers.
4. `pdfplumber` where both fail. Group `extract_words()` by `top`, or group `page.chars` where glyphs go missing. Assign amounts by **right edge**, because money columns are right-aligned.
5. OCR only where `pdftotext` returns almost no characters across the whole document. **OCR of dense, wide numeric tables on a low-DPI scan returns wrong figures that look plausible.** Where the figure matters, render the page and read it.

**Put `-enc UTF-8` on every invocation.** The default is Latin-1, and every accented term then silently fails to match.

## Not worth extracting

- **Treasury cash-flow and monthly statements.** They are aggregates, with no vote or programme detail.
- **End-of-year statistical annexes at economic-nature grain.** They have no ministry and no programme.
- **MTEF outer years.** They are indicative plans, not appropriations.

The full estimates volume is worth extracting even where a sector extract duplicates one chapter, because the other chapters are where much of the spending lives.
