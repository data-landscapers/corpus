# The Finance page

Three pages built by `scripts/finance.py` under one toc bar: `site/finance/index.html`, non-state finance, and `site/finance/budgets/index.html`, every budget line Corpus has read *(Bill, 2026-09-22 and 2026-09-30)*, joined by `site/finance/all/index.html` *(Bill, 2026-10-01)*. **Their explanation is the ⓘ by the title, from `content/info.md` → Finance**: the intros that stood above each table came off on 2026-10-21 (Bill), so nothing here is printed above a table.

`non-state-scope` is the paragraph on how partly digital commitments are counted (Bill's ruling, 2026-10-01); `country.py` and `region.py` print it on every place's full table.

`budgets-absences` opens the table under it of functions looked for and not found, which `finance.py` prints from `logs/budget-functions.csv`.

The `dataset-*` blocks are not shown on the page: they are the descriptions in the `Dataset` structured data `finance.py` and `country.py` write into the head, which is what a reader meets in a dataset search before they have clicked anything. They live here because they are prose a reader reads. Each has to carry on its own the caveat that these are **commitments**, not disbursements, and a total of them is not a market size, because whoever sees one has not seen the page. Keep them between 50 and 5,000 characters, which is what a dataset search will take.

## non-state-scope

Some commitments are only partly digital: a rural project that pairs broadband with electrification, for example. The digital part cannot be separated, so `commitment_usd_m` counts 50% of a commitment whose scope is partial or unclear. Double it for the amount as announced; `original_amount` gives that amount where it was made in another currency. `scope_basis` says why each commitment was judged as it was. Open a row to see both, or filter on scope to list the commitments counted at half. A commitment where digital is incidental to another purpose, such as a cash-transfer programme with a beneficiary registry, is left out.

## budgets-absences

Fourteen functions of a digital state are looked for in every country's budget documents, from the statistics office to the revenue service. A function listed here has no budget line of its own in the documents read. That is not the same as unfunded: the money may sit inside a larger line, or outside the general budget.

## dataset-all

Every non-state financial commitment to Africa's digital sector held by Data Landscapers, as a single table: the recipient country, the financier, the year the finance was approved and the year the activity ends, the sector and instrument, the committed amount in millions of US dollars with its basis and a quality assessment, the status, the recipient organisation, the original currency amount, the financier's own project identifier and IATI activity identifier where published, and the public source each row rests on. The amounts are commitments rather than disbursements, because disbursement data is largely unavailable, so a total of them is what was promised and not what was spent — it is not a measure of market size. A commitment that is only partly digital counts at half its amount, and its scope and the reason are given. The subjects covered are digital transformation, digital public infrastructure and data governance. Domestic budget appropriations are not in this table.

## dataset-budgets

Every digital line Data Landscapers has read from African states' own budget documents, as a single table: the country, the fiscal year, what the money is for, the ministry, spending body, programme and line, and the figure at each stage of the budget cycle held, from the bill tabled in parliament through the enacted law and in-year revisions to the outturn and audited accounts. Each line gives its currency, a US dollar figure for its latest stage, and the document, table and page the figure is printed on. Only the state's own money is included: lines financed by donors or lenders are in the non-state finance table. A line is included when its stated purpose is digital, so the totals are what budgets say about digital transformation, digital public infrastructure and data governance, not the whole of a state's ICT spending.

## dataset-place

Every non-state financial commitment to the digital sector in {name} held by Data Landscapers, as a single table: the financier, the year the finance was approved and the year the activity ends, the sector and instrument, the committed amount in millions of US dollars with its basis and a quality assessment, the status, the recipient organisation, the original currency amount, the financier's own project identifier and IATI activity identifier where published, and the public source each row rests on. The amounts are commitments rather than disbursements, because disbursement data is largely unavailable, so a total of them is what was promised to {name} and not what was spent there — it is not a measure of market size. A commitment that is only partly digital counts at half its amount, and its scope and the reason are given. The subjects covered are digital transformation, digital public infrastructure and data governance. Domestic budget appropriations are not in this table. This is the {name} cut of the full Data Landscapers non-state finance table.

## dataset-budgets-place

Every digital line Data Landscapers has read from the budget documents of {name}, as a single table: the fiscal year, what the money is for, the ministry, spending body, programme and line, and the figure at each stage of the budget cycle held, from the bill tabled in parliament through the enacted law and in-year revisions to the outturn and audited accounts. Each line gives its currency, a US dollar figure for its latest stage, and the document, table and page the figure is printed on. Only the state's own money is included: lines financed by donors or lenders are in the non-state finance table. A line is included when its stated purpose is digital, so the totals are what the budget says about digital transformation, digital public infrastructure and data governance, not the whole of the state's ICT spending. This is the {name} cut of the full Data Landscapers national budgets table.

## dataset-all-finance

Every non-state financial commitment to Africa's digital sector made since 2024 and every digital line read from African states' own budget documents, joined in one table by Data Landscapers: the country or region, the year, what the money is for, whether the row is aid, other finance from an African or a non-African financier, or a state budget line, the financier, the recipient, a title and description, the amount in US dollars and a key to the full record. Non-state rows are commitments, not disbursements, and sit in the year they were made; budget rows are one fiscal year's figure at the latest stage held. A row that is only partly digital counts at half its amount, and its scope and the reason are given. The subjects covered are digital transformation, digital public infrastructure and data governance.
