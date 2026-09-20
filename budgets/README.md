# `budgets/` — Corpus's own budget extractions

**One file per country-year: `budgets/{ISO3}/{FY}.csv`, where `{FY}` is the bare start year of the fiscal year.** Each row is one budget line of one state's own budget document, read by hand against `documentation/budget-extract.md` and citing the held document it is printed in.

**This is a source folder, not an output.** Everything else Corpus publishes is derived from OSINT's `raw/` and is overwritten by the next build. These files are not: nothing regenerates them, they are tracked, and they are the record. `build-finance-page.py` merges them into `outputs/budgets/{ISO3}-budget.csv`, and **a country-year present here replaces OSINT's rows for that year rather than adding to them**.

Three pointers, and no copy of what they say:

- **`BUDGET-EXTRACT.md`** (repo root) — the runbook that writes a file: where the document comes from, the order of the work, the checks, and how it publishes.
- **`documentation/budget-extract.md`** — what a figure means: scope, the origin gate, the stages, the record shape. **`documentation/budget-archetypes.md`** — how to get a table off a particular shape of page.
- **`scripts/budget_source.py`** — the 46 columns and every rule they are held to. `python scripts/budget_source.py --columns` prints the header; `python scripts/budget_source.py {ISO3}` checks a country, and the compile refuses to build from a file that does not pass.

`budgets/.documents/` is gitignored working space for a fetched document. Nothing in it is ever committed.
