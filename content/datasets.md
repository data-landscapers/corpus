# The Datasets pages

Read by `scripts/datasets.py`. `/datasets/` is the index, and each dataset has a page of its own below it. **No counts belong in this file**: the page prints its own from the run that built it.

The Data Centres blocks have to make three things clear without a lecture: what counts as a row (a facility, whether operational, under construction or planned); that `control_category` is our judgement from the ownership chain and is not a legal finding; and that the table is maintained, so it changes, and every change is logged with its sources.

`data-centres-status` is the notice at the top of both pages while the dataset is being finalised (documentation/datasets.md, T1–T10). **Empty the block once the last task closes**, and the notice disappears; delete the key and the build stops.

`dataset-data-centres` is not shown on the page. It is the description in the `Dataset` block in the head, which is what a dataset search shows before anyone clicks. It has to stand on its own, and it must stay between 50 and 5,000 characters.

## index-intro

Tables you can search, filter and download. Each one is dated, and a published file is never revised.

## index-data-centres

Data centres across Africa: who runs each one, who ultimately controls it, and which hyperscalers and Chinese firms are involved.

## index-finance

Money committed to Africa's digital sector by donors, development finance institutions and private investors, and the budget lines states set aside themselves.

## index-catalogue

Every source in the repository, with its date, publisher, places and topics.

## index-metadata

What each column in each dataset means, with its allowed values.

## data-centres-intro

One row per facility, whether operational, under construction or planned. For each one the table records the operator, the ownership chain up to the ultimate parent, and who controls the facility: African, US, other foreign, or joint.

**Control is our reading of the ownership chain, not a legal finding.** The confidence column says how well the sources support it.

The table is maintained, not rebuilt. When new evidence arrives, the affected rows are corrected or added, and each change is [listed below](#changes) with its sources.

## data-centres-status

**This dataset is still being finalised.** Every record has been checked against its sources; claims no readable source supports are being sourced, and missing facilities added. Figures may change until this notice goes.

## data-centres-table-note

Click a row to see the full record. Sort on any column, filter with the dropdowns, and search across every field, including fields the table does not show.

## dataset-data-centres

Data centres in Africa: one record per facility, whether operational, under construction or planned. Each record gives the facility's location, status, type and capacity; its operator, ownership chain and ultimate parent; and who controls it (African, US, other foreign or joint), with a confidence rating. It also records relationships with hyperscalers (AWS, Microsoft, Google), Chinese involvement, DFI finance, connectivity (subsea cable, IXP, carrier neutrality) and certifications. Every record lists its sources. The table is maintained rather than rebuilt: corrections and additions are logged with their sources, and each published file is a dated edition that is never revised.
