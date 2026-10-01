---
type: log
title: Messages for Bill
last_reviewed: 2026-08-28
---

# Messages for Bill

*(Things an unattended run needed Bill for and could not ask. An empty file is the normal outcome. What earns a block, the caps and who strikes one: `CLAUDE.md` → *Be decisive*; `python scripts/lint-messages.py` counts them after every write.)*

*(**Form.** `## YYYY-MM-DD HH:MM · job`, then one bullet per item: what happened, what the run did, what Bill's options are. Insert directly under the marker, newest first.)*

<!-- newest first: a new block goes directly below this line -->

## 2026-10-01 12:28 · non-state scope

- Reports still quote non-state commitments at full value, from the wiki; the finance tables now halve 181 deals and leave 90 out. A report's figure can be twice its country table's, or name a deal the table omits. MDG's status report says two broad operations are "counted whole"; both are now out. Each report corrects at its next unit review. Say "align the reports" for one pass over all 54.

## 2026-10-01 12:02 · runbook caps

- `lint-docs.py` fails on five root runbooks over the 1,500-word cap: STATUS-INIT 4,064, BUILD 3,074, CYCLE 2,489, CITE-REREAD 2,042, BUDGET-EXTRACT 1,768. About 5,900 words must move to `documentation/`, as R92 did for the rest. Not done in the budgets session: it rewrites the procedures the cycle runs on and wants a session of its own. Say "trim the runbooks" to start it.

## 2026-09-29 16:05 · hyperscaler reports

- 13 names in 9 countries point at deleted cloud names anyone can re-register and publish under: Absa, Standard Bank and SARS (ZAF); Safaricom; the Central Bank and health ministry (NGA); ECG (Ghana); Stanbic Uganda; First Capital Bank Malawi; Zambia immigration; Libya's electoral commission. Each is in its country's `run.json` → `findings`; the reports do not name them. Disclosure is your call.

## 2026-09-28 · hyperscaler scan ZAF

- `cdn.eskom.co.za` points at `eskom.ensight-cdn.com`, now on a domain-parking host: whoever registers `ensight-cdn.com` can serve content under an Eskom name. It is public and it is Eskom's problem. Tell Eskom or leave it; nothing of ours depends on it.
- `dalrrd.gov.za` returns SERVFAIL; the seed note records gambling content earlier today. The seed wants the successor department's domain.
