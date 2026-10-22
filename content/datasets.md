# The Datasets pages

Read by `scripts/datasets.py`. `/datasets/` is the index, and each dataset has a page of its own below it. **No counts belong in this file**: the page prints its own from the run that built it.

The Data Centres blocks have to make three things clear without a lecture: what counts as a row (a facility, whether operational, under construction or planned); that `control_category` is our judgement from the ownership chain and is not a legal finding; and that the table is maintained, so it changes, and every change is logged with its sources.

`data-centres-status` is the notice at the top of both pages while the dataset is being finalised (documentation/datasets.md, T1–T10). **Empty the block once the last task closes**, and the notice disappears; delete the key and the build stops.

The Institution Hosting blocks have to make two things clear: a row is an institution and its figures are shares of its working addresses on the scan date; and the scan sees the public edge only (websites, mail, name servers), not where databases or core systems run.

Every `dataset-*` block, and `all-finance-dataset`, is not shown on the page. It is the description in the `Dataset` block in the head, which is what a dataset search shows before anyone clicks. It has to stand on its own, and it must stay between 50 and 5,000 characters.

The finance pages' explanation is the ⓘ, from `info.md` → Finance (Bill, 2026-10-22). What stays here for them is their dataset descriptions and the lines a place with nothing held shows: `budget-intro`, `budget-none-counted` and `finance-all-none`.

## index-intro

These datasets are constructed solely from the data in the Corpus repository and are updated nightly whenever new evidence arrives. Constructing tables automatically from news reports is not without its dangers, but this is outweighed, in our view, by the freshness of the evidence.

## index-finance

[Non-state finance](../finance/) is the money committed to Africa's digital sector by donors, development finance institutions, foundations, private investors and others outside the state. [National budgets](../finance/budgets/) holds every digital line read from African states' own budget documents, from the bill tabled in parliament to the audited accounts. [All finance](../finance/all/) joins the two in one table.

## index-data-centres

The location, ownership and (where available) capacity of the growing number of data centres across Africa.

## index-institution-hosting

Where ministries, regulators, security services, banks and payment systems host their websites, email and name servers: US cloud, US online services, behind a shield, African data centres, telecoms networks or their own systems.

## index-catalogue

A searchable index of all sources stored in the repository. While the full text of these sources cannot be shared for copyright reasons, they can all be accessed using the links provided.

## data-centres-intro

One row per facility, whether operational, under construction or planned. For each one the table records the operator, the ownership chain up to the ultimate parent, and who controls the facility: African, US, other foreign, or joint. **Control is our reading of the ownership chain, not a legal finding.** The table is maintained automatically. When new evidence arrives, the affected rows are corrected or added, and each change is [listed below](#changes) with its sources.

## data-centres-status

## data-centres-table-note

Click a row to see the full record. Sort on any column, shift-click another to sort within it, filter with the dropdowns, and search across every field.

## dataset-data-centres

Data centres in Africa: one record per facility, whether operational, under construction or planned. Each record gives the facility's location, status, type and capacity; its operator, ownership chain and ultimate parent; and who controls it (African, US, other foreign or joint), with a confidence rating. It also records relationships with hyperscalers (AWS, Microsoft, Google), Chinese involvement, DFI finance, connectivity (subsea cable, IXP, carrier neutrality) and certifications. Every record lists its sources. The table is maintained rather than rebuilt: corrections and additions are logged with their sources, and each published file is a dated edition that is never revised.

## institution-hosting-intro

This dataset shows who hosts the public internet services of Africa's strategic institutions, and how much of that hosting is with US cloud companies. It covers the presidency, ministries, regulators, security services, the largest banks and the payment systems in 54 countries, one row per institution. Each row splits the institution's working addresses between US cloud (Amazon, Microsoft, Google, Oracle), US online services such as Microsoft 365, shields such as Cloudflare that hide the real host, government or the institution's own systems, African data centres, telecoms networks and other foreign hosts. **The shares add up to 100 and are as of the scan date.** The scan sees websites, mail and name servers only, not where databases, payroll or core banking systems run.

## institution-hosting-table-note

Click a row to see the full record. Sort on any column, shift-click another to sort within it, filter with the dropdowns, and search across every field. Shares are percentages.

## dataset-institution-hosting

Where strategic institutions in 54 African countries host their public internet services: one record per institution, covering the presidency, ministries, regulators, security services, the largest banks and the payment systems. Each record gives the domains scanned, the number of working addresses found, and the share of them on US cloud (Amazon, Microsoft, Google, Oracle), on those companies' African data centres, on US online services, behind a shield such as Cloudflare, on government or the institution's own systems, on African data centres and IT firms, on telecoms networks, on other foreign hosts and on Chinese cloud. It also records the email provider and any mail filter. Figures come from passive DNS lookups on the scan date and describe websites, mail and name servers, not internal systems. Each published file is a dated edition that is never revised.

## dataset-catalogue

Every document the Data Landscapers Corpus holds on digital transformation, digital public infrastructure and data governance across Africa, as a single table: title, publisher, author, publication date and its precision, the countries and regions covered, the subjects from the Corpus taxonomy, the organisations and people tagged, the date the document entered the repository, and the publisher's own link. It is a catalogue of metadata and links — it does not contain the text of the documents themselves, each of which stays with its publisher at the URL given. Every claim in the country, region and topic reports on this site rests on a record in it.

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

## all-finance-dataset

Every digital budget line and non-state finance commitment counted for {name} by Data Landscapers, in one table: side, year, topic, US dollar amount, payer, recipient, stage and scope.

## budget-intro

Work is ongoing to compile information on national budgets, expenditures and audits. See [National budgets](../../finance/budgets/).

## budget-none-counted

No line read so far has a US dollar figure, so no totals are shown. The lines are in the full table.

## finance-all-none

No budget line or non-state commitment is yet held for {name}.
