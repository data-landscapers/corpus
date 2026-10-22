## Introduction
What each column in the downloadable datasets means. Each table can be downloaded as a CSV, and the same file is what the dataset's own page links to.

<!-- A "table:" comment names a CSV and, optionally, the columns to show; scripts/datasets.py draws it at build time with methodology.py's lookup_tables. Edit the file, not a copy here. -->

## Data centres
<!-- table: site/metadata/data-centres-metadata.csv | column, label, values, definition -->

## Institution hosting
<!-- table: site/metadata/institution-hosting-metadata.csv | column, label, values, definition -->

## Non-state finance

One row per commitment to digital transformation from a financier other than the state. Each is tagged to one country or region only, so totals by place sum without double-counting. Figures are commitments, not disbursements, in millions of US dollars at a rate dated to the year of announcement; a multi-year commitment sits wholly in its start year. A commitment that is only partly digital, or whose scope is unclear, counts at 50% in `commitment_usd_m`, because its digital part cannot be separated: double it for the amount announced, and `scope_basis` says why it was judged so. A commitment where digital is incidental to another purpose is left out.

<!-- table: site/metadata/non-state-finance-metadata.csv -->

## National budgets

One row per digital line read from a state's own budget documents, the state's own money only. Local-currency figures are the full amounts as printed and are never adjusted. `budget_usd` is the latest stage held (audited, else spent, released, revised, enacted or proposed) at the IMF annual average rate for the year the fiscal year starts in, and counts 50% of a line that is only partly digital or whose scope is unclear. Fourteen functions of a digital state are looked for in every country's documents; one with no line of its own is not necessarily unfunded, as the money may sit inside a larger line or outside the general budget.

<!-- table: site/metadata/budgets-metadata.csv | column, label, values, definition -->

## All finance

Both sides in the columns they share: budget lines at their latest stage by the year the fiscal year starts in, commitments at their counted amount by the year they were made, either at 50% where only partly digital or unclear. A budget is one year's money and a commitment may span several, so a year's total is a sum of both, not a measure of spending. A row's other fields are in its own table, found by its `deal_id`. In a summary by year, an empty cell is a year with nothing recorded, not a zero.

<!-- table: site/metadata/all-finance-metadata.csv | column, label, values, definition -->

## Catalogue
<!-- table: site/metadata/catalogue-metadata.csv -->
