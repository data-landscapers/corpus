# The Datasets pages

Read by `scripts/datasets.py`. `/datasets/` is the index, and each dataset has a page of its own below it. **No counts belong in this file**: the page prints its own from the run that built it.

The Data Centres blocks have to make three things clear without a lecture: what counts as a row (a facility, whether operational, under construction or planned); that `control_category` is our judgement from the ownership chain and is not a legal finding; and that the table is maintained, so it changes, and every change is logged with its sources.

`data-centres-status` is the notice at the top of both pages while the dataset is being finalised (documentation/datasets.md, T1–T10). **Empty the block once the last task closes**, and the notice disappears; delete the key and the build stops.

The Institution Hosting blocks have to make two things clear: a row is an institution and its figures are shares of its working addresses on the scan date; and the scan sees the public edge only (websites, mail, name servers), not where databases or core systems run.

`dataset-data-centres` and `dataset-institution-hosting` are not shown on the page. It is the description in the `Dataset` block in the head, which is what a dataset search shows before anyone clicks. It has to stand on its own, and it must stay between 50 and 5,000 characters.

## index-intro

These datasets are constructed solely from the data in the Corpus repository and are updated nightly whenever new evidence arrives. Constructing tables automatically from news reports is not without its dangers, but this is outweighed, in our view, by the freshness of the evidence.

## index-finance

It is currently impossible to calculate total investments into digital transformation. There are three main reasons for this. Firstly no one has integrated non-state finance data with national budgets, expenditure and audits. Secondly no one has attempted to align the full spectrum of cross-border and domestic, public and private investment. Thirdly, with the exception of the World Bank, no investors have attempted to adopt a common modern taxonomy that classifies investments in categories compatible with digital transformation. Over the next year we aim to fill this vacuum.

## index-data-centres

The location, ownership and (where available) capacity of the growing number of data centres across Africa.

## index-institution-hosting

Where ministries, regulators, security services, banks and payment systems host their websites, email and name servers: US cloud, US online services, behind a shield, African data centres, telecoms networks or their own systems.

## index-catalogue

A searchable index of all sources stored in the repository. While the full text of these sources cannot be shared for copyright reasons, they can all be accessed using the links provided.

## index-metadata

Column definitions for each of the datasets.

## data-centres-intro

One row per facility, whether operational, under construction or planned. For each one the table records the operator, the ownership chain up to the ultimate parent, and who controls the facility: African, US, other foreign, or joint. **Control is our reading of the ownership chain, not a legal finding.** The table is maintained automatically. When new evidence arrives, the affected rows are corrected or added, and each change is [listed below](#changes) with its sources.

## data-centres-status

## data-centres-table-note

Click a row to see the full record. Sort on any column, shift-click another to sort within it, filter with the dropdowns, and search across every field.

## dataset-data-centres

Data centres in Africa: one record per facility, whether operational, under construction or planned. Each record gives the facility's location, status, type and capacity; its operator, ownership chain and ultimate parent; and who controls it (African, US, other foreign or joint), with a confidence rating. It also records relationships with hyperscalers (AWS, Microsoft, Google), Chinese involvement, DFI finance, connectivity (subsea cable, IXP, carrier neutrality) and certifications. Every record lists its sources. The table is maintained rather than rebuilt: corrections and additions are logged with their sources, and each published file is a dated edition that is never revised.

## institution-hosting-intro

One row per institution: the presidency, ministries, regulators, security services, the largest banks and the payment systems, in 54 countries. For each one the table shows where its public internet services are hosted: on US cloud (Amazon, Microsoft, Google, Oracle), on US online services such as Microsoft 365, behind a shield such as Cloudflare that hides the real host, on government or the institution's own systems, on African data centres, on telecoms networks, or with other foreign hosts. **Figures are shares of the institution's working addresses on the scan date, and together they add up to 100.** The scan sees websites, mail and name servers only. It does not see where databases, payroll or core banking systems run.

## institution-hosting-table-note

Click a row to see the full record. Sort on any column, shift-click another to sort within it, filter with the dropdowns, and search across every field. Shares are percentages.

## dataset-institution-hosting

Where strategic institutions in 54 African countries host their public internet services: one record per institution, covering the presidency, ministries, regulators, security services, the largest banks and the payment systems. Each record gives the domains scanned, the number of working addresses found, and the share of them on US cloud (Amazon, Microsoft, Google, Oracle), on those companies' African data centres, on US online services, behind a shield such as Cloudflare, on government or the institution's own systems, on African data centres and IT firms, on telecoms networks, on other foreign hosts and on Chinese cloud. It also records the email provider and any mail filter. Figures come from passive DNS lookups on the scan date and describe websites, mail and name servers, not internal systems. Each published file is a dated edition that is never revised.
