---
type: runbook
reader: cc
title: BUDGET-EXTRACT — one country-year of a national budget, read and published
opened: 2026-09-20
---

# BUDGET-EXTRACT — one country-year, read out of the state's own budget document

*(Bill, 2026-09-20, R54. The spec is `documentation/budget-extract.md`; the archetype table `lookups/budget-archetypes.csv`, its method note `documentation/budget-archetypes.md`; the schema and its checker `scripts/budget_source.py`; the log `logs/budget-extract.csv`.)*

**The one-line brief for a fresh session.** *Take one country-year, read the digital lines out of that state's own budget document, add them to `budgets/budgets-{ISO3}.csv` with a citation on every row, and publish — the build merges the file into the Finance page and a country-year in the file replaces whatever OSINT's records said about that year.*

## What a sitting is

**The output is a tracked CSV, not a wiki record.** Corpus owns the file, nothing regenerates it, and `build-finance-page.py` merges it with what OSINT's records still yield.

**One country-year per sitting.** Not one country: a state's fiscal years are different documents, often different archetypes.

## Before you start

1. **Pick the country-year and check what is already there.** `logs/budget-followups.md` lists the sittings already owed; take from it first. `logs/budget-extract.csv` is the record of what has been *read*. A row carrying `origin_record` was **migrated** from OSINT's records, not read: a year of migrated rows is a placeholder — **replace it whole**, do not amend it. `python scripts/budget_source.py` prints how many rows are short of the full schema, per country: that is the queue. A year with no migrated rows is finished work and is re-read only to correct it.
2. **Find the document OSINT holds for it.** `outputs/catalogue/catalogue-internal.csv` carries the slug, title and URL of every held document — filter on the country and look for the budget volume, the appropriation act, the gazette or the execution report. A budget document is usually a **companion source page** (`…-companion`), which is the page the line-item records cite; it names the instrument, the scope, the currency and the scale in its body.
3. **Get the bytes.** OSINT's copy lives in the mirror's `budget-archive/`, and **Corpus reads it there**. `lookups/artefact-md5-index.csv` maps each record to its artefact path, md5 and size. Where OSINT does not hold the document, fetch the publisher's copy from the companion's `url:` into `budgets/.documents/` (gitignored) and say so in `notes`. **Where neither exists, stop.** Ask for the document in a `notes-for-osint` `[ACT]` note and take the next one. Do not extract from a summary of a document.
4. **Read the spec.** `documentation/budget-extract.md` end to end. Then read `documentation/budget-archetypes.md` (the toolchain and how the table works) and find the document's row in `lookups/budget-archetypes.csv`. **A document matching no row earns a row in the CSV**, written in the same sitting; a match is noted in the commit and adds nothing.

## The sitting

**1. Reconcile before extracting.** One reconciliation for the country-year, before anything else: a programme sum against its printed section total, or an estimates figure against the same figure in the execution annex. It fixes the scale, confirms which annex is which, and catches a wrong join before it becomes a row. A document that will not reconcile is not extracted from.

**2. Establish the scale, per table.** `amount_scale` goes in every row as printed — full units, thousands, millions — and the amounts are stored **normalised to units**. Scale is a property of the table, not of the document.

**3. Scan across every vote, not the digital ministry's.** The largest single line is repeatedly in interior, finance, justice or the head of government's vote. The scan **locates and does not identify**: read the vote block and pair label to amount by position before recording anything.

**3a. Record every vote, and look for the fourteen functions** *(budget data review, 2026-10-02)*. Write each vote in the document's summary table to `budgets/votes-read.csv` as `lines taken`, `read, none digital` or `not read`; **a vote is read only when its cost centres or sub-heads have been read**. Then `python scripts/budget-functions.py {ISO3}` lists the functions not yet found: look for each in the votes read, and enter one that is not there with `--absent`, naming the year, the document and the page.

**4. Run the origin gate on every line** before building it. An externally financed line is a non-state deal and builds no row here or in any file of its own — its magnitude goes in the log note; a line naming no funder beyond *external*, *Dons* or *Externo* builds nothing anywhere and its magnitude is a dated finding in the log. Own-source levy and fee income is domestic-state, and is often legislated in the finance law's articles rather than appropriated in a vote — read the articles and the special accounts.

**5. Write the rows.** Add them to the country's one file, `budgets/budgets-{ISO3}.csv` *(Bill, 2026-09-30)*: every fiscal year sits in it, and a new year is new rows, never a new file. A first country starts the file with the header exactly as `python scripts/budget_source.py --columns` prints it, UTF-8 with BOM. `origin_record` is empty on every row. The topic goes in `primary_topic_id` as a taxonomy key and the country's ISO-3 in `country`. Leave `report_year`, `primary_topic` and `budget_usd` blank; all three are derived. A row's fiscal year is its `fy_start`, and `fiscal_year_label` carries the state's own form verbatim. Replacing a year means deleting its old rows from the file, not keeping them beside the new ones. One row per budget line per fiscal year, at the **finest grain the document prints for that line** — and never a programme alongside its own sub-programmes, which would sum.

**Every row names its admin head and its programme** *(Bill, 2026-09-22)*. `admin_head_basis` and `programme_basis` say `printed` for the document's own name; `programme_level` says what grain `programme` holds, and a budget with no programmes gives the next level it prints — `project`, `activity`, `action`, `chapter`, `line` — or `vote`/`body` for a whole appropriation.

**6. Cite every row.** `source_slug` is the held document's catalogue slug; `doc_locator` is where in it the figure is printed, as printed — volume, table, entity, line, column. Both are the row's whole provenance, and `doc_locator` is what publishes.

**7. Write `purpose`, `scope_basis` and `notes` in Corpus's own words.** This folder is tracked in a public repository and `design.md` → *Source bodies* forbids a verbatim source body reaching one. The line's **name** as the document prints it is a label and goes in `line_name`, `programme` and `sub_programme`; anything longer is written, not lifted. `notes` is where the cross-foot lands, and any qualifier an execution rate has to carry.

**8. Cross-foot, and record that you did.** A line that does not cross-foot is not written.

## Checks, then publish

```
python scripts/budget_source.py --update         # the derived columns and budgets-all-countries.csv, after any change
python scripts/budget_source.py {ISO3}          # the schema, from the repo root
python scripts/budget-votes.py {ISO3}           # the votes read, and that a vote with lines holds rows
python scripts/budget-functions.py              # the function and name logs, after rows change
cd scripts/.workroot
python scripts/build-finance-page.py {ISO3}     # merges; prints the swap it made
```

The build's line says what happened: `[budgets/budgets-GHA.csv: FY2024 12->15]` — twelve OSINT records for that year dropped, fifteen Corpus rows in their place. **Read that number.** A year the source file covers publishes entirely from the source file, so a count that fell means lines were lost, not that the file is smaller.

Then, from the repo root:

1. `python scripts/rebuild.py --all` if more than one country moved, else the single-place build above is enough.
2. Commit the source file and the rebuilt `outputs/` together — they are one change: `BUDGET-EXTRACT {ISO3} FY{year}: N lines from {document}`.
3. **A change-log entry, in the same commit.** Two terse sentences under today's date in `content/changelog.md`: what was read, and what it means for a reader — which years, which stages, and whether it replaced a thinner reading.
4. Run a cycle's *Render* and *Mirror* so the Finance page and its dated CSV carry it.
5. One line in `logs/log.md` via `python scripts/log-line.py budget-extract "…"`, and one row in `logs/budget-extract.csv`.

## The log

`logs/budget-extract.csv`: `date,iso3,fy,slug,archetype,lines,scope_whole,scope_partial,stages,absences,cost,note`. **`absences`** counts the dated findings this sitting produced and did not write as rows — a body appropriated nothing, a line whose funder is named only as external, a nil return earned by walking the library end to end. **`cost`** is the sitting's share of the week.

## What is never written here

An envelope — a ministry total, a thematic total, a body whose mandate is mixed. An MTEF or plan-period figure. A procurement plan or a signed contract. A tax expenditure. State revenue. A commitment plan. A percentage of a mixed line — no apportionment, ever; a line that demonstrably contains digital spend that cannot be separated is `partial`, not estimated. A row for a line the document does not carry a figure for.

**And nothing is written into `C:\OSINT`.** Not the OCR sidecar, not a corrected record, not a note. Where a sitting OCRs a volume at real cost, offer the sidecar to OSINT through the share's `prepared/`; where it finds a defect in a record, that is an `[ACT]` note in `notes-for-osint.md` with an `Affects:` line, written after the extraction is committed.

## Done

A country-year is done when every step under *Checks, then publish* has run and `logs/budget-extract.csv` carries the row, absences included. A sitting that found nothing to record is done the same way: no file, and a log row saying what was searched and why the nil return is earned.
