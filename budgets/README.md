# `budgets/` — Corpus's own budget extractions

**One file per country: `budgets/budgets-{ISO3}.csv`, every fiscal year in it** *(Bill, 2026-09-30)*. A new year's rows are added to the same file, and a row's fiscal year is its own `fy_start`. Each row is one budget line of one state's own budget document, read by hand against `documentation/budget-extract.md` and citing the held document it is printed in.

**These are source files, not outputs.** Everything else Corpus publishes is derived from OSINT's `raw/` and is overwritten by the next build. These files are not: nothing regenerates their rows, they are tracked, and they are the record. `build-finance-page.py` merges them into `outputs/budgets/{ISO3}-budget.csv`, and **a country-year present here replaces OSINT's rows for that year rather than adding to them**.

**Two things here are derived, and both are refreshed after any change.** One is the `budget_usd` column of each country file: the latest stage held (audited back to proposed) in whole US dollars, at the finance build's rate. The other is `budgets-all-countries.csv`, every country file in one. `python scripts/budget_source.py --update` writes both, and the finance build runs it. The check fails when either falls behind. Leave `budget_usd` blank when adding rows, and never edit the all-countries file by hand.

**Two kinds of row, and `origin_record` is which.** A row that a `BUDGET-EXTRACT.md` sitting read against the spec carries the full schema and leaves `origin_record` empty. A row **migrated** from an OSINT domestic-state record names that record there. All 488 were migrated on 2026-09-20 under R56a, and they carry what the record held, which for most is less than the schema asks. Nothing was invented to fill the difference: `python scripts/budget_source.py` counts, per country, how many rows are short, and that count is the work order R58 reads. A country-year is finished when a sitting has replaced its rows and none of them carries an `origin_record`.

Three pointers, and no copy of what they say:

- **`BUDGET-EXTRACT.md`** (repo root) — the runbook that writes the rows: where the document comes from, the order of the work, the checks, and how it publishes.
- **`documentation/budget-extract.md`** — what a figure means: scope, the origin gate, the stages, the record shape. **`lookups/budget-archetypes.csv`** — how to get a table off a particular shape of page, one row per archetype; its method note is `documentation/budget-archetypes.md`.
- **`scripts/budget_source.py`** — the columns and every rule they are held to. `python scripts/budget_source.py --columns` prints the header; `python scripts/budget_source.py {ISO3}` checks a country, and the compile refuses to build from a file that does not pass.

`budgets/.documents/` is gitignored working space for a fetched document. Nothing in it is ever committed.
