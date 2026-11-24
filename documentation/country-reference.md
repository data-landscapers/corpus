---
type: runbook
reader: cc
title: The country reference table — the quarterly check
last_reviewed: 2026-11-24
---

# The country reference table — the quarterly check

`lookups/country-reference.csv` is one row per African country; `lookups/country-reference-metadata.csv` defines each column, names its authoritative origin (`url`), the year its data describes (`year`), when it was last checked (`checked`) and whether a script can refresh it (`update`). Every column is checked at least every 90 days *(Bill, 2026-11-24)*.

## In the cycle

`CYCLE.md` step 7a runs `python scripts/country-reference.py --quarterly`. Inside 90 days of every column's last check it prints `not due` and the step is over. Otherwise it refreshes the `auto` columns itself and prints three kinds of line:

- a changed cell — nothing to do; it is in the diff;
- `CHECK` — a currency or FTS code that no longer matches its registry. Correct the cell from the registry;
- `DUE` — a `manual` column overdue, oldest first.

## A `DUE` column

Fetch its `url` — the depositary, the publisher's own list, the latest edition — and compare every country. **Every value comes from a fetched source, never from memory**: an unverifiable cell is left blank rather than guessed. Correct the cells, then set the metadata row's `year` to the source's edition or as-at year and `checked` to today. A column whose origin has moved gets its new `url`; one with no origin left is retired from both files in the same commit.

Work as many `DUE` columns as the cycle's time allows, oldest first; what is left is due on the next cycle, which is not a message. Columns that need reading across 54 sources — the law years, the memberships — can go to one subagent apiece, with this rule in its brief.

## Afterwards

Commit both files as `Country reference: quarterly check, N cells` and log `python scripts/log-line.py reference "<that line>"`. A change a reader could notice is not involved: the table is a lookup, not a page.
