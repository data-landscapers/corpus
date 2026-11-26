---
type: decision
reader: cc
title: catalogue-recosting.md — the catalogue and finance pages at 60,000 and 100,000 records (R145, R193)
date: 2026-11-26
status: decided by CC; the query service is housekeeping job 92
---

# The catalogue at 60,000 and 100,000 records

R145 asked, by 2027-03-01, what the catalogue costs a reader at 60,000 and 100,000 records and whether the split of shown columns and detail holds. R193 brought it forward because `raw/` grew faster than forecast: 51,769 records on 26 November, 196 to 375 admitted a night. It is answered early, from measurement.

## What the reader downloads today

The catalogue page is 184 KB (46 KB compressed). It then loads `filter-index.json`, the shown columns of every record, in full; the detail rows come in 94 chunks of 500, fetched only when opened. The index is what grows:

| Commit | Records shown | Index | Compressed |
|---|---|---|---|
| 15 Oct | 28,462 | 3.0 MB | 0.92 MB |
| 6 Nov | 42,312 | 4.0 MB | 1.20 MB |
| 26 Nov | 46,699 | 4.7 MB | 1.41 MB |

The page shows about 90 % of `raw/`. The three weeks to 26 November added about 47 compressed bytes a record.

## Projection

| `raw/` | Shown | Index, compressed | At 200 a night |
|---|---|---|---|
| 60,000 | 54,000 | about 1.75 MB | early January 2027 |
| 69,000 | 62,000 | about 2.1 MB: past R110's 2 MB rule | late February 2027 |
| 100,000 | 90,000 | about 3.4 MB, 100,000-row rule near | July 2027 |

**The split holds to about 60,000 and not to 100,000.** Past 2 MB compressed the first load is the slow part of the page on a phone, and R110 named the answer: a query service, so the index never travels whole. **Decision:** build it in January, before late February: a Cloudflare Worker over D1 (the site already runs Workers for alerts and downloads) answering the catalogue's filters and returning one page of rows. Housekeeping job 92 holds it. Re-measure on 15 January 2027; a faster intake moves the date, not the decision.

## The finance pages

`finance/index.html` draws 2,930 elements against R110's 3,000. The count has sat between 2,890 and 2,970 since October because the table draws 100 rows whatever its length; it moves only when the page's own markup or filters grow, so a new filter value list is what would break it. Its data file is 1.48 MB compressed for 5,814 rows, growing about one row a day: the 2 MB rule is years off. `lint-page-weight.py` fails the build at either line, so neither can be crossed silently.
