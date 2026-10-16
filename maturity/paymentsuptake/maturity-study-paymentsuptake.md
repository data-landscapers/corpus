---
type: task
reader: cc
title: maturity-study-paymentsuptake.md — how many adults hold an account and pay digitally, in four questions
last_reviewed: 2026-10-16
status: first pass run 2026-10-16; staged, written and on the soft-launch map; waits for Bill's acceptance
---

# Maturity study: paymentsuptake

*(Commissioned by Bill on 2026-10-16 as `dpi.pay--population-uptake`, a first pass under `maturity/documentation/first-pass-batch.md`, in one batch with centralbank, g2ppayments, revenuecollection, businesspayments, retailpayments, paymentsuptake, crossborderpayments and consumerprotection: the topic Digital Payments and Fintech.)*

## 1. What is assessed

**The share of adults with an account at a bank or mobile money provider**, from a survey of people: Global Findex, FinScope or the central bank's own survey. A count of accounts is not a count of people.

The study redraws `dpi.pay--population-uptake`, which as at 2026-08-31 puts five countries at stage 4, 16 at 3, 18 at 2, five at 1 and ten unplaced. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| Population uptake | Population uptake: population uptake | `dpi.pay--population-uptake-population-uptake` |

Anything else the evidence names is `other`, noted and never staged: a count of mobile money or bank accounts, registered or active, a provider's customer count, a SIM count.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Does a quarter of adults hold an account? | A survey from the last three years puts adults with a bank or mobile money account at 26% or more |
| 2 | Do over half hold one? | A survey from the last three years puts adults with an account at 53% or more |
| 3 | Do four in five hold one? | A survey from the last three years puts adults with an account at 79% or more |
| 4 | Do four in five pay digitally? | A survey from the last three years puts adults who made or received a digital payment in the past year at 79% or more |

## 3. The ladders

**Population uptake**

| Stage | Answers |
|---|---|
| 1 Under a quarter | A survey from the past three years puts adults with a bank or mobile money account below 26%. |
| 2 A quarter | Yes to 1 |
| 3 Over half | Yes to 2 |
| 4 Four in five | Yes to 3 |
| 5 Four in five paying | Yes to 4 |

A later yes answers the earlier ones (method §3.3). `study.json` holds this as three aspects: `share` (`half`, `quarter`, `below`) for stage 1 and questions 1 and 2, `target` (`target`) for 3 and `payments` (`payments`) for 4.

## 4. The norm

The World Bank's Global Findex 2025 puts account ownership at 79% of adults worldwide; the frame takes that as the target. This study asks the four questions above; it does not measure a country against the norm.

## 5. What the run reads

- **Carried**: nothing; no earlier study holds facts on these questions.
- **Read**: **882 story readings about the subject**, published since October 2023, in at most 20 stories a country: 874 in the batch's 160 shared calls (800 stories), read once for every study that lists them, and 8 in 8 calls of its own. A story published before the three-year window can set no stage, and the twenty are each country's best ranked across the batch (`study-calls.py --batch … --cap 20`).
- **Not read**: the rest of the about 3,400 stories a study lists, instruments, long reports, passing mentions and the documents the row's current cells cite. No web search and no handover to OSINT. A question nothing answers is printed as *Not held*.

## 6. Token ceiling

**12 million** for this study; **95 million** for the batch, checked with `study-tokens.py` after every fan-out.

## 7. Tasks, in order

- [x] **D0. Prepared**: this file, `study.json` and the reading lists, 2026-10-16.
- [x] **D1. Read**, 2026-10-16: the batch's shared calls and this study's own, Sonnet drafters; 29 facts after the parent's corrections (`corrections.csv`).
- [x] **D2. Staged** as at 2026-09-30: 1 at 4, 8 at 3, 3 at 2; unplaced 1, no evidence 41. Every cell is a first pass; no second drafter.
- [x] **D3. Written, rendered and linted**, by `study-first-write.py`; on the soft-launch map. Reported to Bill.

**Decided in the run**: Nothing removed.

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
