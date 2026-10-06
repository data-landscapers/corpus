---
type: brief
reader: cc
title: h4-ladder-test.md — what testing the health ladders on the Phase 1 profiles found, and what was rewritten
date: 2026-10-06
status: the record of task H4; the ladders it left are in maturity-study-health.md §4
---

# H4: the health ladders, tested

*(Task H4 of `maturity-study-health.md`. `scripts/study-ladder-health.py` reruns both counts, `--as-written` for the first; `ladder-test.csv` holds the second, country by country, with what stopped each. The count reads profile values only, the strictest reading a rung can have. Phase 2 stages from the evidence rows.)*

**What H4 changed, and why.** Read strictly from the profiles, the ladders as first written put one country at stage 4 on HMIS, none on EMR and none at 5. Three wordings did it, none a threshold:

- **Stages 4 and 5 asked for all of T1 to T4.** Sources name the tier they are about, so 27 cells stopped there. The test is now the primary tier.
- **HMIS stage 3 asked that every district report**, which no value carries; 17 countries keyed at district stopped at 2. A system keyed at district or below now meets it.
- **EMR stage 4's shared record had no value.** `shared` is added, and four rows restated to it (`evidence/reclassified.csv`).

Also settled: *paper* means no digital entry at any level, and stands only where no source states a system; **a share of all health facilities is read as the share of primary clinics**, which are most of them, and the short summary says which it is.

As rewritten: HMIS 5 at stage 4, 29 at 3, 7 at 2, 1 at 1, 12 unplaced or *No evidence*; EMR 1, 19, 15, 4 and 15. **Nothing reaches stage 5, and the rung stands**: four HMIS shares pass 90 per cent and are older than two years, which is a search for H5 and not a fault in the ladder. Mali's 98 per cent, for one, is DHIS2 *deployed* in community health centres in 2019. `scripts/study-ladder-health.py` reruns both counts.
