---
type: task
reader: cc
title: maturity-study-businesspayments.md — government buying and paying firms electronically, in four questions
last_reviewed: 2026-10-16
status: first pass run 2026-10-16; staged, written and on the soft-launch map; waits for Bill's acceptance
---

# Maturity study: businesspayments

*(Commissioned by Bill on 2026-10-16 as `dpi.pay--b2b-and-b2g-functionality`, a first pass under `maturity/documentation/first-pass-batch.md`, in one batch with centralbank, g2ppayments, revenuecollection, businesspayments, retailpayments, paymentsuptake, crossborderpayments and consumerprotection: the topic Digital Payments and Fintech.)*

## 1. What is assessed

**Government buying from firms electronically**: an e-procurement system that runs tenders and pays suppliers online. What runs public purchasing online counts, whatever it is called.

The study redraws `dpi.pay--b2b-and-b2g-functionality`, which as at 2026-08-31 puts 29 countries at stage 3, eight at 2, one at 1 and 16 unplaced. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| B2B and B2G functionality | B2B and B2G functionality: b2b and b2g functionality | `dpi.pay--b2b-and-b2g-functionality-b2b-and-b2g-functionality` |

Anything else the evidence names is `other`, noted and never staged: a private marketplace, a bank's corporate banking service, a tax system, a procurement law with no system.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Is e-procurement under way? | A source from the last three years says an e-procurement system is procured, being built or piloted |
| 2 | Is an e-procurement system in service? | A source from the last three years says government tenders are published or bid online through a system in service |
| 3 | Does it run end to end across government? | A source from the last three years says e-procurement runs from tender to award or payment, or is required of all public bodies |
| 4 | Is its use reported with figures? | A source from the last three years gives a figure for e-procurement: tenders, value or share of purchasing through it |

## 3. The ladders

**B2B and B2G functionality**

| Stage | Answers |
|---|---|
| 1 Paper | A source from the past three years says public procurement runs on paper. |
| 2 Under way | Yes to 1 |
| 3 In service | Yes to 2 |
| 4 End to end | Yes to 3 |
| 5 Use reported | Yes to 4 |

A later yes answers the earlier ones (method §3.3). `study.json` holds this as three aspects: `system` (`inservice`, `underway`, `none`) for stage 1 and questions 1 and 2, `endtoend` (`endtoend`) for 3 and `reported` (`reported`) for 4.

## 4. The norm

The AfCFTA Digital Trade Protocol asks states to enable electronic transactions, electronic invoicing and interoperable payments between businesses and with government. This study asks the four questions above; it does not measure a country against the norm.

## 5. What the run reads

- **Carried**: nothing; no earlier study holds facts on these questions.
- **Read**: **890 story readings about the subject**, published since October 2023, in at most 20 stories a country: 875 in the batch's 160 shared calls (800 stories), read once for every study that lists them, and 15 in 13 calls of its own. A story published before the three-year window can set no stage, and the twenty are each country's best ranked across the batch (`study-calls.py --batch … --cap 20`).
- **Not read**: the rest of the about 3,400 stories a study lists, instruments, long reports, passing mentions and the documents the row's current cells cite. A question nothing answers is printed as *Not held*.

## 6. Token ceiling

**12 million** for this study; **95 million** for the batch, checked with `study-tokens.py` after every fan-out.

## 7. Tasks, in order

- [x] **D0. Prepared**: this file, `study.json` and the reading lists, 2026-10-16.
- [x] **D1. Read**, 2026-10-16: the batch's shared calls and this study's own, Sonnet drafters; 14 facts after the parent's corrections (`corrections.csv`).
- [x] **D2. Staged** as at 2026-09-30: 1 at 5, 1 at 3, 5 at 2; unplaced 1, no evidence 46. Every cell is a first pass; no second drafter.
- [x] **D3. Written, rendered and linted**, by `study-first-write.py`; on the soft-launch map. Reported to Bill.

**Decided in the run**: Nothing removed.

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
