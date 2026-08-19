---
type: doc
title: instrument, status, beneficiary_type — where the values come from
last_reviewed: 2026-08-19
---

# Where the non-state finance values are written, and where a vocabulary would go

*(Written 2026-08-19, answering Bill's question. Findings only — nothing was changed, and the OSINT side of this is a `[PROPOSE]`, which is his to rule on.)*

## The short answer

**Nobody writes these three values to a standard, because no standard exists.** They are authored by hand into the body table of each `raw/` record in OSINT, and they arrive in the CSV untouched — Corpus applies no mapping, no case fold, not even a trim beyond the table parser's. The result is 114 distinct `instrument` values across 1,257 rows, 24 `status`, 53 `beneficiary_type`. All three are driving filter dropdowns on the site.

## Where they are authored

The three are **body-table fields, not frontmatter**: `wiki/finance-record-spec.md:323-325` creates the rows and gives the permitted values as `…` for each.

Two drivers then say incompatible things.

- `wiki/finance-news-driver.md:69` — *"Everything is read from the source's own words; nothing is normalised."* Its field table at `:77-78` is the only stated enum anywhere: instrument *"only if stated (loan, grant, equity, guarantee, concessional facility)"*, status *"map to the enum (`Approved` / `Active` / `Closed` / `Pipeline`)"*.
- `wiki/finance-iati-driver.md:108-109` — a different vocabulary lifted from IATI codelists: status `1 pipeline, 2 implementation, 3 finalisation, 4 closed, 5 cancelled, 6 suspended`.

That is why `Implementation`, `Finalisation` and `Pipeline/identification` sit beside `Active` and `Closed` in the same column, and why `Standard grant (IATI finance-type 110)` sits beside `Grant`. **Two enums in one field is not drift; it is two specifications both being followed correctly.**

`beneficiary_type` has no instruction at all — no driver field-table, no procedure file, no lookup. A sweep QA note (`sweep/donor/iati/qa-2026-08-11.md:9`) records it being *"inferred … from the title, not stated as a field"*. It is invented per record.

There is **no controlled vocabulary** for any of the three. `lookups/taxonomy.md` is subject slugs; `lookups/countries.csv` is places; `wiki/reference.md:229-233` names those two and no others. The contrast worth noting is `wiki/finance-record-spec.md:345`, which *does* enumerate *Amount quality* — so the spec knows how to state a vocabulary and has not done so here.

## The path into the CSV

`raw/YYYY/*.md` body table → `finance_lib.deal_table()` (`scripts/finance_lib.py:81-87`, regex over `| Field | Value |`, `.strip()` the only transformation) → `build-finance-page.py:_ns_row()` (`:271-274`) → both `{ISO3}-nonstate.csv` and `all-nonstate.csv`.

**No normalisation is applied.** The neighbouring cells in the same function do get treatment — `recip_org()` strips suffixes and trailing `(ISO3)`, `amount_quality()` falls back frontmatter→body and lower-cases. These three get a bare `T.get("Instrument", "")`.

## What the mess actually looks like

Not one problem but six, and they do not all have the same fix.

1. **Two enums in one column** — news-driver vs IATI-driver, above.
2. **Base value plus parenthetical qualifier**, the dominant pattern. `Equity` has 13 variants (`Equity (fund)`, `Equity (seed)`, `Equity (Series A)`, `Equity acquisition (20%, taking stake 35%→55%)` …), `Grant` about 12, `Government` 9.
3. **Editorial annotation inside the data cell.** `Concessional loan *(source label, unverified — see Notes)*` is 58 rows and `Concessional loan` is 49 — the same value split in two by a provenance note. Ten more rows carry `*(corrected from the source's "Concessional loan"…)*`. **This is not a vocabulary problem at all**: a cell is carrying commentary that belongs in `## Notes`, and no mapping table should have to know about it.
4. **Sentences where a value should be.** `Not stated; project's own dates (2023-03-01 to 2024-04-30) have elapsed as of this capture`. Also `## Notes` material.
5. **Case and synonym variants** — `government`/`Government`, `signed`/`Signed`, `TA` (37) vs `Technical assistance / advisory`, `Private` (8) vs `Private sector` (298) vs `Private company` (3).
6. **Three different null idioms** — empty, `(not stated)`, and `Not stated — …`.

## Where a fix belongs

Three places, and the evidence points at using all three for different parts of it.

**A vocabulary has to be declared in OSINT**, because that is where `lookups/frontmatter-schema.json`'s `x-authority` and `wiki/reference.md` say vocabularies live, and because the news driver's instruction to normalise status to an enum is already a vocabulary — just an undeclared one. The precedent for the mechanism is `lookups/financier-names.csv`. Files: a new `lookups/` table, plus replacing the `…` at `wiki/finance-record-spec.md:323-325`. **`wiki/reference.md:375` marks controlled vocabularies `[PROPOSE]`, so this is Bill's ruling, not CC's.**

**The mapping should be applied in the Corpus compile**, at `build-finance-page.py:_ns_row()` — one function writes all three cells, and a map there reaches both the per-country and the all-Africa CSVs with no other change. `amount_quality()` two functions above is the house pattern for exactly this. The reason to normalise here rather than edit the records is `wiki/finance-news-driver.md:69` and `wiki/capture-rule.md:73`: **the record is meant to keep the source's own words**, and a derived view is the right place to impose a house vocabulary on them.

**`raw/` edits should be confined to what is not a vocabulary problem** — items 3 and 4 above, where a cell holds commentary or a sentence. Those cannot be mapped and should not be; they are miscaptured records.

One more file needs changing whatever is decided. `scripts/country.py` used to carry a `FIELDS` list asserting vocabularies for all three — *"Loan, grant, equity, guarantee or other"*, *"approved, launched, signed, completed"*, *"Government, private sector, civil society or other"* — each citing `FINANCE-COMPILE.md` as its authority, and `FINANCE-COMPILE.md` states none of them. `status`'s four examples matched neither driver's enum. That list was retired on 2026-08-19 when the single hand-maintained dictionary at `site/metadata/non-state-finance-metadata.csv` replaced it; **whatever that file says about these three fields is now the site's only claim about them, so it should not repeat the mistake of describing a vocabulary that upstream does not enforce.**

## One thing to fix regardless

`description` cells carry raw wiki link syntax into the published CSV — `[[2025-03-06-microsoft-zaf-azure-expansion-…]]` appears in ZAF's data. That is markup leaking into a citable artefact, and it is a compile-side defect rather than a vocabulary question.
