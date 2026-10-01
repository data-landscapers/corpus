---
type: design-note
reader: cc
title: nonstate-scope.md — how much of a non-state deal counts
last_reviewed: 2026-10-01
---

# Non-state scope

**Every non-state deal carries a scope, as every budget line does** *(Bill's ruling, 2026-10-01)*. OSINT admits a deal in or out; it never said how much of the money is digital, so the tables counted a cash-transfer programme with a beneficiary registry at its full amount. `lookups/deal-scope.csv` is Corpus's judgement, one row per `deal_id`:

| `scope` | Meaning | In the tables |
|---|---|---|
| `whole` | The deal's stated purpose is a digital activity. | Full amount. |
| `partial` | Digital is a named part beside something else, and the text does not split the money. | Half. |
| `unclear` | The text does not say enough to tell. | Half. |
| `out` | Digital is incidental to another purpose. | Left out. |

`scope_basis` is one sentence, in our words, saying why. It is published.

**Partial or out.** A deal is `partial` where digital is in its title or is one of two or three named components: broadband with electrification, a financial and digital inclusion operation, a land project built round its information system. It is `out` where the money's purpose is something else and digital serves it: cash transfers with a registry, general scholarships, youth employment across sectors, budget support with one digital condition, a solar company's pay-as-you-go metering, a fund investing across sectors.

**Where it bites.** `scripts/build-finance-page.py` → `in_scope` drops `out` deals and tags the rest; `_ns_row` halves `commitment_usd_m` and writes `scope` and `scope_basis`. Everything downstream reads those CSVs. OSINT keeps every record: this is the dataset's rule, as the 2015 window is.

**A new deal.** The lookup does not hold it, so it publishes with a blank scope at its full amount, and the finance build prints `NOT YET ASSESSED` with the ids. Read each deal's title and description, add its row, rebuild. A run that leaves the line standing has not finished the finance stage.

**The first assessment** judged all 1,402 deals on 2026-10-01; `documentation/nonstate-scope-assessment.csv` is that reading, before the incidental class was split from the mixed one. It took US$83.3bn over 1,402 deals to US$68.9bn over 1,312.

**Reports are not the tables.** A report's prose quotes commitments as announced, from the wiki. A figure there can be twice the table's, or name a deal the table leaves out.
