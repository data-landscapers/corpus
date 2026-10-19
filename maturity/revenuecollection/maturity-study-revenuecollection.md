---
type: task
reader: cc
title: maturity-study-revenuecollection.md — taxes, duties and fees paid electronically, in four questions
last_reviewed: 2026-10-16
status: first pass run 2026-10-16; staged, written and on the soft-launch map; waits for Bill's acceptance
---

# Maturity study: revenuecollection

*(Commissioned by Bill on 2026-10-16 as `dpi.pay--revenue-collection`, a first pass under `maturity/documentation/first-pass-batch.md`, in one batch with centralbank, g2ppayments, revenuecollection, businesspayments, retailpayments, paymentsuptake, crossborderpayments and consumerprotection: the topic Digital Payments and Fintech.)*

## 1. What is assessed

**Taxes, customs duties and government fees paid electronically**: online filing and payment, mobile money or bank transfer to the revenue authority or treasury. What lets people and firms pay the state electronically counts.

The study redraws `dpi.pay--revenue-collection`, which as at 2026-08-31 puts 41 countries at stage 3, ten at 2 and three unplaced. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| Revenue collection | Revenue collection: revenue collection | `dpi.pay--revenue-collection-revenue-collection` |

Anything else the evidence names is `other`, noted and never staged: a payment from government to people, a revenue authority's internal system with no payment, a municipal parking app with no state revenue role.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Is electronic payment of taxes or fees under way? | A source from the last three years says electronic payment of a tax or fee is piloted or contracted, or e-filing is announced |
| 2 | Can some taxes or fees be paid electronically? | A source from the last three years says electronic payment is in service for some taxes or fees |
| 3 | Are the main taxes and customs duties paid electronically? | A source from the last three years says electronic filing and payment are in service for the main taxes and for customs duties |
| 4 | Is the electronic share reported? | A source from the last three years gives a figure for revenue paid electronically: a share or an amount |

## 3. The ladders

**Revenue collection**

| Stage | Answers |
|---|---|
| 1 Cash only | A source from the past three years says taxes, duties or fees are paid in cash or on paper only. |
| 2 Under way | Yes to 1 |
| 3 Some taxes | Yes to 2 |
| 4 Main taxes and duties | Yes to 3 |
| 5 Share reported | Yes to 4 |

A later yes answers the earlier ones (method §3.3). `study.json` holds this as three aspects: `payment` (`inservice`, `underway`, `none`) for stage 1 and questions 1 and 2, `main` (`main`) for 3 and `reported` (`reported`) for 4.

## 4. The norm

The AfCFTA Digital Trade Protocol asks states to accept electronic payment and electronic documents for trade and dues. This study asks the four questions above; it does not measure a country against the norm.

## 5. What the run reads

- **Carried**: nothing; no earlier study holds facts on these questions.
- **Read**: **942 story readings about the subject**, published since October 2023, in at most 20 stories a country: 876 in the batch's 160 shared calls (800 stories), read once for every study that lists them, and 66 in 43 calls of its own. A story published before the three-year window can set no stage, and the twenty are each country's best ranked across the batch (`study-calls.py --batch … --cap 20`).
- **Not read**: the rest of the about 3,400 stories a study lists, instruments, long reports, passing mentions and the documents the row's current cells cite. A question nothing answers is printed as *Not held*.

## 6. Token ceiling

**12 million** for this study; **95 million** for the batch, checked with `study-tokens.py` after every fan-out.

## 7. Tasks, in order

- [x] **D0. Prepared**: this file, `study.json` and the reading lists, 2026-10-16.
- [x] **D1. Read**, 2026-10-16: the batch's shared calls and this study's own, Sonnet drafters; 143 facts after the parent's corrections (`corrections.csv`).
- [x] **D2. Staged** as at 2026-09-30: 4 at 5, 1 at 4, 27 at 3, 7 at 2; unplaced 1, no evidence 14. Every cell is a first pass; no second drafter.
- [x] **D3. Written, rendered and linted**, by `study-first-write.py`; on the soft-launch map. Reported to Bill.

**Decided in the run**: Congo's FOUTA arrêté read as some payment in service, not every tax and duty.

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
