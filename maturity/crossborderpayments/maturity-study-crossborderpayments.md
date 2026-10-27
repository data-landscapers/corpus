---
type: task
reader: cc
title: maturity-study-crossborderpayments.md — digital payments across borders, in four questions
last_reviewed: 2026-10-16
status: first pass run 2026-10-16; staged, written and on the soft-launch map; waits for Bill's acceptance
---

# Maturity study: crossborderpayments

*(Commissioned by Bill on 2026-10-16 as `dpi.pay--cross-border-functionality`, a first pass under `maturity/documentation/first-pass-batch.md`, in one batch with centralbank, g2ppayments, revenuecollection, businesspayments, retailpayments, paymentsuptake, crossborderpayments and consumerprotection: the topic Digital Payments and Fintech.)*

## 1. What is assessed

**Regulated digital payments across the country's borders**: cross-border mobile money, remittance corridors and links to regional payment systems. What moves money across the border digitally counts.

The study redraws `dpi.pay--cross-border-functionality`, which as at 2026-08-31 puts three countries at stage 4, 13 at 3, 30 at 2, one at 1 and seven unplaced. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| Cross-border functionality | Cross-border functionality: cross-border functionality | `dpi.pay--cross-border-functionality` |

Anything else the evidence names is `other`, noted and never staged: a cash remittance agent with no digital channel, a card network used abroad with no named corridor, a remittance figure with no channel named.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Is a cross-border corridor under way? | A source from the last three years says a cross-border digital payment corridor is piloted or licensed, or rules for it are being drafted |
| 2 | Is a corridor in service? | A source from the last three years says cross-border mobile money or digital remittances through a named corridor are in service |
| 3 | Is the country in a regional payment system? | A source from the last three years says the country takes part in PAPSS or a regional payment system in service |
| 4 | Are cross-border volumes or costs reported? | A source from the last three years gives a figure for cross-border digital payments through the country's corridors or regional link: volume, value or cost |

**A cost is a measured cost, not a posted fee** *(Bill, 2026-10-27)*: a provider's published transfer fee is a price list, not evidence of payments made, and does not answer question 4.

## 3. The ladders

**Cross-border functionality**

| Stage | Answers |
|---|---|
| 1 None | A source from the past three years says no regulated cross-border digital payment channel exists. |
| 2 Under way | Yes to 1 |
| 3 Corridor in service | Yes to 2 |
| 4 Regional system | Yes to 3 |
| 5 Volumes reported | Yes to 4 |

A later yes answers the earlier ones (method §3.3). `study.json` holds this as three aspects: `corridor` (`inservice`, `underway`, `none`) for stage 1 and questions 1 and 2, `regional` (`regional`) for 3 and `reported` (`reported`) for 4.

## 4. The norm

The African Union's Digital Transformation Strategy and the Pan-African Payment and Settlement System aim at a single African payments area, with cross-border mobile money regulated and costs brought down. This study asks the four questions above; it does not measure a country against the norm.

## 5. What the run reads

- **Carried**: nothing; no earlier study holds facts on these questions.
- **Read**: **900 story readings about the subject**, published since October 2023, in at most 20 stories a country: 876 in the batch's 160 shared calls (800 stories), read once for every study that lists them, and 24 in 16 calls of its own. A story published before the three-year window can set no stage, and the twenty are each country's best ranked across the batch (`study-calls.py --batch … --cap 20`).
- **Not read**: the rest of the about 3,400 stories a study lists, instruments, long reports, passing mentions and the documents the row's current cells cite. A question nothing answers is printed as *Not held*.

## 6. Token ceiling

**12 million** for this study; **95 million** for the batch, checked with `study-tokens.py` after every fan-out.

## 7. Tasks, in order

- [x] **D0. Prepared**: this file, `study.json` and the reading lists, 2026-10-16.
- [x] **D1. Read**, 2026-10-16: the batch's shared calls and this study's own, Sonnet drafters; 219 facts after the parent's corrections (`corrections.csv`).
- [x] **D2. Staged** as at 2026-09-30: 7 at 5, 23 at 4, 5 at 3, 9 at 2; unplaced 1, no evidence 9. Every cell is a first pass; no second drafter.
- [x] **D3. Written, rendered and linted**, by `study-first-write.py`; on the soft-launch map. Reported to Bill.

**Decided in the run**: GIMACPAY's CEMAC-wide figures read as regional participation, not the country's volumes; PAPSS joined or signed with no live participation removed (DRC, Algeria, Morocco, Tunisia, Zimbabwe); PAPSS's continent-wide saving removed for Algeria.

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
