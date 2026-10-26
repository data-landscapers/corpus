---
type: task
reader: cc
title: maturity-study-consumerprotection.md — protection of people using digital financial services, in four questions
last_reviewed: 2026-10-25
status: first pass run 2026-10-16; staged, written and on the soft-launch map; waits for Bill's acceptance
---

# Maturity study: consumerprotection

*(Commissioned by Bill on 2026-10-16 as `dpi.pay--consumer-protection`, a first pass under `maturity/documentation/first-pass-batch.md`, in one batch with centralbank, g2ppayments, revenuecollection, businesspayments, retailpayments, paymentsuptake, crossborderpayments and consumerprotection: the topic Digital Payments and Fintech.)*

## 1. What is assessed

**Rules and redress protecting people who use digital financial services**: conduct rules for mobile money, digital lending and payments, and a body that takes complaints. What protects users counts, whichever regulator holds it.

The study redraws `dpi.pay--consumer-protection`, which as at 2026-08-31 puts ten countries at stage 3, 22 at 2 and 22 unplaced. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| Consumer protection | Consumer protection: consumer protection | `dpi.pay--consumer-protection` |

Anything else the evidence names is `other`, noted and never staged: a general consumer law with no financial services rule, a data protection law alone, a provider's own customer service.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Are consumer rules for digital finance being drafted? | A source from the last three years says consumer-protection rules for digital financial services are being drafted |
| 2 | Are such rules in force? | A source from the last three years says consumer-protection or conduct rules covering digital financial services or digital lending are in force |
| 3 | Does a body take complaints? | A source from the last three years says a financial ombudsman or a regulator's complaints unit takes complaints about digital financial services |
| 4 | Is enforcement reported? | A source from the last three years reports a fine, sanction, licence withdrawal or complaint figures under these rules, for digital financial services. Complaint figures across all financial services are not a yes *(Bill, 2026-10-25)* |

## 3. The ladders

**Consumer protection**

| Stage | Answers |
|---|---|
| 1 No rules | A source from the past three years says no consumer-protection rules apply to digital financial services. |
| 2 Drafting | Yes to 1 |
| 3 Rules in force | Yes to 2 |
| 4 Complaints handled | Yes to 3 |
| 5 Enforced | Yes to 4 |

A later yes answers the earlier ones (method §3.3). **Dated by the source** *(Bill, 2026-10-26, message 34)*: rules in force and a complaints body are standing states, so a source from the last three years answers questions 2 and 3 whenever the rule was adopted (`study.json` → `source_dated`); a fine or a year's complaint count keeps its own date. **A study's account is not a government action** (same message): Gambia's competition commission study is removed and Gambia stands at 2. `study.json` holds this as three aspects: `rules` (`inforce`, `draft`, `none`) for stage 1 and questions 1 and 2, `redress` (`redress`) for 3 and `enforced` (`enforced`) for 4.

## 4. The norm

The African Union's Digital Transformation Strategy asks for consumer protection in digital financial services across disclosure, responsible lending, data privacy and dispute resolution. This study asks the four questions above; it does not measure a country against the norm.

## 5. What the run reads

- **Carried**: nothing; no earlier study holds facts on these questions.
- **Read**: **908 story readings about the subject**, published since October 2023, in at most 20 stories a country: 877 in the batch's 160 shared calls (800 stories), read once for every study that lists them, and 31 in 26 calls of its own. A story published before the three-year window can set no stage, and the twenty are each country's best ranked across the batch (`study-calls.py --batch … --cap 20`).
- **Not read**: the rest of the about 3,400 stories a study lists, instruments, long reports, passing mentions and the documents the row's current cells cite. A question nothing answers is printed as *Not held*.

## 6. Token ceiling

**12 million** for this study; **95 million** for the batch, checked with `study-tokens.py` after every fan-out.

## 7. Tasks, in order

- [x] **D0. Prepared**: this file, `study.json` and the reading lists, 2026-10-16.
- [x] **D1. Read**, 2026-10-16: the batch's shared calls and this study's own, Sonnet drafters; 38 facts after the parent's corrections (`corrections.csv`).
- [x] **D2. Staged** as at 2026-09-30: 2 at 5, 5 at 4, 9 at 3, 1 at 2; unplaced 1, no evidence 36. Every cell is a first pass; no second drafter.
- [x] **D3. Written, rendered and linted**, by `study-first-write.py`; on the soft-launch map. Reported to Bill.

**Decided in the run**: Removed: Rwanda's fraud complaints in general; Zimbabwe's fuel stations without POS machines.

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
