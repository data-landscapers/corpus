# Country pages

The blurbs and empty states on `site/countries/{ISO3}/index.html`, read by `scripts/country.py`.

These render 54 times each, so they carry the weight of the whole Countries section. The report blurbs in particular are what a reader uses to decide which of four documents to open, and they are the shortest text on the site with the most work to do.

Blocks that carry `{placeholders}` are still in `scripts/country.py` and have not moved here yet.

`budget-intro` is what a place with no budget lines shows. The other `budget-*` blocks are the section on a country that has them: `budget-summary` above the topic-by-year table, `budget-table-note` under it, and `budget-table-intro` on `budgets.html`.

## report-status

A summary of the status of all known systems and instruments

## report-status-baseline

Where the country stands across 37 questions, with a source for every claim

## report-monthly

A summary of sources published since the beginning of last month.

## report-hosting

Where the state's websites and email are hosted: US cloud, shields, telecoms, government or foreign hosts

## no-reports

No reports are yet published for this place.

## catalogue-intro

The repository holds {sources} documents for {name}. The catalogue only contains the metadata — title, publisher, date, facets and the publisher’s own link. Every piece of evidence in the reports above resolves to one of these records.

## budget-intro

Work is ongoing to compile information on national budgets, expenditures and audits. See [National budgets](../../finance/budgets/).

## budget-summary

What {name} budgets for digital from its own money, read from its own budget documents. Figures are in millions of US Dollars, converted at the IMF annual average rate for the year the fiscal year starts in. Each line counts at the latest stage held: audited, else spent, released, revised, enacted or proposed. A line that is only partly digital, or whose scope is unclear, counts at 50% of its value, because its digital part cannot be separated; the full table gives every line's scope and its full figures in the local currency.

## budget-table-note

US$m, by topic and the year the fiscal year starts in. Partly digital and unclear lines are in at 50%. An empty cell is a year with no line read, not a zero.

## budget-none-counted

No line read so far has a US dollar figure, so no totals are shown. The lines are in the full table.

## budget-table-intro

Every digital line read from {name}'s own budget documents: what was proposed, enacted, revised and spent. Figures are in the budget's own currency; `budget_usd` gives the latest one in US dollars. Only the state's own money is here. Some lines are only partly digital: a ministry's IT directorate, for example, whose budget also pays for other work. For a few, the document does not say enough to tell. The digital part cannot be separated, so `budget_usd` counts 50% of a line whose scope is partial or unclear. The figures in the local currency are never adjusted: they are the full amounts as the document prints them. Open a row to see them beside the line's scope, or filter on scope to list the lines counted at half. Click any row to see more. Where each figure is printed, and our notes on it, are in the CSV download.

## dataset-description

Every document the Data Landscapers Corpus holds on {name}, as a single table: title, publisher, author, publication date and its precision, the countries and regions covered, the subjects from the Corpus taxonomy, the organisations and people tagged, the date the document entered the repository, and the publisher's own link. The subjects are digital transformation, digital public infrastructure and data governance. It is a catalogue of metadata and links — it does not contain the text of the documents themselves, each of which stays with its publisher at the URL given. This is the {name} cut of the full Corpus catalogue, and every claim in the {name} reports on this site rests on a record in it.

## report-finance

What the state budgets for digital, what others commit to it, and the two added together

## finance-all-intro

{name}'s digital finance from both sides: what the state budgets from its own money, and what development financiers, foundations, vendors and operators commit. Figures are in millions of US Dollars. The two are added together as they are counted below them.

## finance-all-note

US$m, by topic and year: budget lines by the year the fiscal year starts in, commitments by the year they were made. A budget is one year's money and a commitment may span several, so a year's total is a sum of both, not a measure of spending. ‘-{cutoff}’ aggregates every year before {cutoff}. An empty cell is a year with nothing recorded, not a zero.

## finance-all-none

No budget line or non-state commitment is yet held for {name}.

## all-finance-intro

Every row the finance report's All finance table adds up for {name}: the state's digital budget lines and the commitments of other financiers, in the columns the two have in common. Figures are in millions of US Dollars as counted there: a budget line at its latest stage, a commitment at its counted amount, and either at 50% where it is only partly digital or its scope is unclear. Each row's other fields are in its own table, found by its `deal_id`. Click any row to see more.

## all-finance-dataset

Every digital budget line and non-state finance commitment counted for {name} by Data Landscapers, in one table: side, year, topic, US dollar amount, payer, recipient, stage and scope.
