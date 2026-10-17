# Country pages

The text on the finance table pages under `site/countries/{ISO3}/` and on the country finance report, read by `scripts/country.py` and `scripts/finance-report.py`. The country page itself is retired (2026-10-17) and forwards to the country's news page.

`budget-intro` is what a place with no budget lines shows. The other `budget-*` blocks are the section on a country that has them: `budget-summary` above the topic-by-year table, `budget-table-note` under it, and `budget-table-intro` on `budgets.html`.

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
