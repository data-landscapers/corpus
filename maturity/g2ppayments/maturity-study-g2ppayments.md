---
type: task
reader: cc
title: maturity-study-g2ppayments.md — government payments to people made digitally, in four questions
last_reviewed: 2026-10-16
status: first pass run 2026-10-16; staged, written and on the soft-launch map; waits for Bill's acceptance
---

# Maturity study: g2ppayments

*(Commissioned by Bill on 2026-10-16 as `dpi.pay--g2p-functionality`, a first pass under `maturity/documentation/first-pass-batch.md`, in one batch with centralbank, g2ppayments, revenuecollection, businesspayments, retailpayments, paymentsuptake, crossborderpayments and consumerprotection: the topic Digital Payments and Fintech.)*

## 1. What is assessed

**Government payments to people made digitally**: social transfers, civil service salaries and pensions paid into a bank account, mobile money wallet or card instead of cash. What pays people digitally counts, whoever runs it.

The study redraws `dpi.pay--g2p-functionality`, which as at 2026-08-31 puts 31 countries at stage 3, seven at 2 and 16 unplaced. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| G2P functionality | G2P functionality: g2p functionality | `dpi.pay--g2p-functionality` |

Anything else the evidence names is `other`, noted and never staged: a donor's or NGO's own cash programme with no government role, a payment from a person to government, payments to firms.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Is digital government payment under way? | A source from the last three years says a government programme is piloting or has contracted digital payment to people |
| 2 | Does one government programme pay people digitally? | A source from the last three years says a government social transfer, salary or pension is paid digitally, in service |
| 3 | Are two or more main streams paid digitally? | Sources from the last three years show two or more of social transfers, civil service salaries and pensions paid digitally |
| 4 | Are payments checked against the national ID or social registry? | A source from the last three years says government payments to people are checked against the national ID or a social registry |

## 3. The ladders

**G2P functionality**

| Stage | Answers |
|---|---|
| 1 Cash | A source from the past three years says government payments to people are made in cash. |
| 2 Under way | Yes to 1 |
| 3 One programme | Yes to 2 |
| 4 Main streams | Yes to 3 |
| 5 Linked to ID | Yes to 4 |

A later yes answers the earlier ones (method §3.3). `study.json` holds this as three aspects: `payment` (`inservice`, `underway`, `none`) for stage 1 and questions 1 and 2, `streams` (`several`) for 3 and `linked` (`linked`) for 4.

## 4. The norm

The African Union's Digital Transformation Strategy asks governments to digitise government-to-person payments. This study asks the four questions above; it does not measure a country against the norm.

## 5. What the run reads

- **Carried**: nothing; no earlier study holds facts on these questions.
- **Read**: **907 story readings about the subject**, published since October 2023, in at most 20 stories a country: 874 in the batch's 160 shared calls (800 stories), read once for every study that lists them, and 33 in 29 calls of its own. A story published before the three-year window can set no stage, and the twenty are each country's best ranked across the batch (`study-calls.py --batch … --cap 20`).
- **Not read**: the rest of the about 3,400 stories a study lists, instruments, long reports, passing mentions and the documents the row's current cells cite. A question nothing answers is printed as *Not held*.

## 6. Token ceiling

**12 million** for this study; **95 million** for the batch, checked with `study-tokens.py` after every fan-out.

## 7. Tasks, in order

- [x] **D0. Prepared**: this file, `study.json` and the reading lists, 2026-10-16.
- [x] **D1. Read**, 2026-10-16: the batch's shared calls and this study's own, Sonnet drafters; 74 facts after the parent's corrections (`corrections.csv`).
- [x] **D2. Staged** as at 2026-09-30: 4 at 5, 1 at 4, 22 at 3, 7 at 2; unplaced 1, no evidence 19. Every cell is a first pass; no second drafter.
- [x] **D3. Written, rendered and linted**, by `study-first-write.py`; on the soft-launch map. Reported to Bill.

**Decided in the run**: Removed: Seychelles' payments through the registry, still planned; Tunisia's unique identifier, still being introduced.

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
