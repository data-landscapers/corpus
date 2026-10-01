# The Finance page

Three pages built by `scripts/finance.py` under one toc bar: `site/finance/all/index.html` joins the other two *(Bill, 2026-10-01)* and carries `all-intro`. The first two *(Bill, 2026-09-22)*: `site/finance/index.html`, non-state finance, and `site/finance/budgets/index.html`, which carries `budgets-intro` and the table of every budget line Corpus has read (Bill, 2026-09-30). The budget tables first published on 2026-09-20 (R53) came off the site on 2026-09-22; this one replaced them.

`non-state-scope` is the paragraph on how partly digital commitments are counted (Bill's ruling, 2026-10-01); `finance.py` prints it after `non-state-intro`, and `country.py` on every place's full table.

`non-state-intro` is what a reader meets before the commitments table, and it has to say three things: what a row is, what the money figures do and do not mean, and why the totals cannot be read as a market size. **No count of rows is written into this file** — the page prints its own from the run that built it, and a number here drifts the moment the base moves.

`budgets-intro` is what a reader meets before the budget table. Like `non-state-intro`, it carries no count: the page prints its own.

The `dataset-*` blocks are not shown on the page: they are the descriptions in the `Dataset` structured data `finance.py` and `country.py` write into the head, which is what a reader meets in a dataset search before they have clicked anything. They live here because they are prose a reader reads. Each has to carry on its own the caveat the page spends a paragraph on — these are **commitments**, not disbursements, and a total of them is not a market size — because whoever sees one has not seen the page. Keep them between 50 and 5,000 characters, which is what a dataset search will take.

## non-state-intro

This table documents funds committed to digital transformation by financiers other than the state: bilateral and multilateral donors, development finance institutions, foundations, private investors, vendors and operators. See [this introduction](https://data-landscapers.io/2026/09/27/non-state-finance/) to its contents and processes.

We parse the text accompanying each commitment to arrive at a primary topic categorisation based on [our taxonomy](https://corpus.data-landscapers.io/methodology/lookups/#topics). This is our assessment, not the financier's.

## non-state-scope

Some commitments are only partly digital: a rural project that pairs broadband with electrification, for example. The digital part cannot be separated, so `commitment_usd_m` counts 50% of a commitment whose scope is partial or unclear. Double it for the amount as announced; `original_amount` gives that amount where it was made in another currency. `scope_basis` says why each commitment was judged as it was. Open a row to see both, or filter on scope to list the commitments counted at half. A commitment where digital is incidental to another purpose, such as a cash-transfer programme with a beneficiary registry, is left out.

## non-state-table-note

Click any row to open the full record. Sort on any column heading, filter with the dropdowns, and search across every field whether or not it is shown. Regions are recipients in their own right, not aggregates of the countries beside them.

## budgets-intro

This table monitors national budgets since 2024. Where available every budget line is traced from proposed through appropriated and revised to actual and audited expenditure. These values are recorded in the local currency. The most recent of the values is converted to US dollars for cross-country comparison.

Some lines are only partly digital: a ministry's IT directorate, for example, whose budget also pays for other work. For a few, the document does not say enough to tell. The digital part cannot be separated, so `budget_usd` counts 50% of a line whose scope is partial or unclear. The figures in the local currency are never adjusted: they are the full amounts as the document prints them. Open a row to see them beside the line's scope, or filter on scope to list the lines counted at half.

We parse each line's programme and sub-programme text to arrive at a primary topic categorisation based on [our taxonomy](https://corpus.data-landscapers.io/methodology/lookups/#topics). This is our assessment, not the government's.

Click any row to see more. Where each figure is printed, and our notes on it, are in the CSV download. The table is updated automatically when new documents are discovered.

## all-intro

This table joins the two finance tables from 2024 onwards: every non-state commitment and every national budget line, in one set of columns. It shows the money for a country, a year or a topic from every source together.

`type` says what a row is: aid (a grant, concessional loan or technical assistance), other finance (every other non-state commitment) or budget (the state's own money). Each row's full record is in [non-state finance](../) or [national budgets](../budgets/), under the same `deal_id`.

Read totals with care. A non-state row is a commitment and sits wholly in the year it was made; a budget row is one fiscal year's figure. Commitments made before 2024 are in the non-state table only. Some rows are only partly digital and the digital part cannot be separated, so `value_usd` counts 50% of a row whose scope is partial or unclear. Double it for the full amount; `scope_basis` says why the row was judged as it was. Filter on scope to list the rows counted at half. Some non-state rows are for a region, not a country.

## dataset-all

Every non-state financial commitment to Africa's digital sector held by Data Landscapers, as a single table: the recipient country, the financier, the year the finance was approved and the year the activity ends, the sector and instrument, the committed amount in millions of US dollars with its basis and a quality assessment, the status, the recipient organisation, the original currency amount, the financier's own project identifier and IATI activity identifier where published, and the public source each row rests on. The amounts are commitments rather than disbursements, because disbursement data is largely unavailable, so a total of them is what was promised and not what was spent — it is not a measure of market size. A commitment that is only partly digital counts at half its amount, and its scope and the reason are given. The subjects covered are digital transformation, digital public infrastructure and data governance. Domestic budget appropriations are not in this table.

## dataset-budgets

Every digital line Data Landscapers has read from African states' own budget documents, as a single table: the country, the fiscal year, what the money is for, the ministry, spending body, programme and line, and the figure at each stage of the budget cycle held, from the bill tabled in parliament through the enacted law and in-year revisions to the outturn and audited accounts. Each line gives its currency, a US dollar figure for its latest stage, and the document, table and page the figure is printed on. Only the state's own money is included: lines financed by donors or lenders are in the non-state finance table. A line is included when its stated purpose is digital, so the totals are what budgets say about digital transformation, digital public infrastructure and data governance, not the whole of a state's ICT spending.

## dataset-place

Every non-state financial commitment to the digital sector in {name} held by Data Landscapers, as a single table: the financier, the year the finance was approved and the year the activity ends, the sector and instrument, the committed amount in millions of US dollars with its basis and a quality assessment, the status, the recipient organisation, the original currency amount, the financier's own project identifier and IATI activity identifier where published, and the public source each row rests on. The amounts are commitments rather than disbursements, because disbursement data is largely unavailable, so a total of them is what was promised to {name} and not what was spent there — it is not a measure of market size. A commitment that is only partly digital counts at half its amount, and its scope and the reason are given. The subjects covered are digital transformation, digital public infrastructure and data governance. Domestic budget appropriations are not in this table. This is the {name} cut of the full Data Landscapers non-state finance table.

## dataset-budgets-place

Every digital line Data Landscapers has read from the budget documents of {name}, as a single table: the fiscal year, what the money is for, the ministry, spending body, programme and line, and the figure at each stage of the budget cycle held, from the bill tabled in parliament through the enacted law and in-year revisions to the outturn and audited accounts. Each line gives its currency, a US dollar figure for its latest stage, and the document, table and page the figure is printed on. Only the state's own money is included: lines financed by donors or lenders are in the non-state finance table. A line is included when its stated purpose is digital, so the totals are what the budget says about digital transformation, digital public infrastructure and data governance, not the whole of the state's ICT spending. This is the {name} cut of the full Data Landscapers national budgets table.

## dataset-all-finance

Every non-state financial commitment to Africa's digital sector made since 2024 and every digital line read from African states' own budget documents, joined in one table by Data Landscapers: the country or region, the year, what the money is for, whether the row is aid, other non-state finance or a state budget line, the financier, the recipient, a title and description, the amount in US dollars and a key to the full record. Non-state rows are commitments, not disbursements, and sit in the year they were made; budget rows are one fiscal year's figure at the latest stage held. A row that is only partly digital counts at half its amount, and its scope and the reason are given. The subjects covered are digital transformation, digital public infrastructure and data governance.
