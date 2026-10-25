---
type: task
reader: cc
title: maturity-study-centralbank.md — the central bank's oversight of digital payments, in four questions
last_reviewed: 2026-10-25
status: first pass run 2026-10-16; staged, written and on the soft-launch map; waits for Bill's acceptance
---

# Maturity study: centralbank

*(Commissioned by Bill on 2026-10-16 as `dpi.pay--governance-role-of-central-bank`, a first pass under `maturity/documentation/first-pass-batch.md`, in one batch with centralbank, g2ppayments, revenuecollection, businesspayments, retailpayments, paymentsuptake, crossborderpayments and consumerprotection: the topic Digital Payments and Fintech.)*

## 1. What is assessed

**The central bank's role over payment systems and e-money**: its mandate, its licensing of payment providers, its oversight of the national switch and its links to regional systems. What the central bank does counts, whatever the law that gives it the power.

The study redraws `dpi.pay--governance-role-of-central-bank`, which as at 2026-08-31 puts two countries at stage 4, 40 at 3, one at 2 and 11 unplaced. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| Governance role of central bank | Governance role of central bank: governance role of central bank | `dpi.pay--governance-role-of-central-bank` |

Anything else the evidence names is `other`, noted and never staged: a commercial bank's own service, a telecoms regulator's rules, a finance ministry policy with no central bank role, a law not yet adopted described only as text.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Is a payments mandate being set up? | A source from the last three years says the central bank's payments mandate or e-money rules are being drafted, or it oversees payments by circular only |
| 2 | Does the central bank license payment providers? | A source from the last three years says the central bank licenses or authorises mobile money, e-money or payment service providers |
| 3 | Does it run or oversee a national switch? | A source from the last three years says the central bank runs or oversees a national payment switch or interoperability arrangement in service |
| 4 | Is the country live on PAPSS? | A source from the last three years says the country's banks or payment providers send and receive payments through PAPSS. Joining PAPSS, or a regional payment system, is not a yes |

## 3. The ladders

**Governance role of central bank**

| Stage | Answers |
|---|---|
| 1 No mandate | A source from the past three years says the central bank has no mandate over payment systems or e-money. |
| 2 Mandate in drafting | Yes to 1 |
| 3 Licensing providers | Yes to 2 |
| 4 Overseeing a switch | Yes to 3 |
| 5 Live on PAPSS | Yes to 4 |

A later yes answers the earlier ones (method §3.3). `study.json` holds this as three aspects: `mandate` (`licensing`, `drafting`, `none`) for stage 1 and questions 1 and 2, `switch` (`overseen`) for 3 and `regional` (`live`, `joined`, `regional`) for 4, where only `live` is a yes.

**Rung 5 rewritten** *(Bill, 2026-10-25)*: PAPSS fully operational only; a regional payment system (PI-SPI, GIMACPAY, SADC-RTGS, REPSS, EAPS) no longer answers it, and joining PAPSS does not. The 94 `linked` facts were revalued (`corrections.csv`). Nineteen cells fell from 5 to 4, and Uganda, whose only fact was the East African Payment System, to unplaced. Djibouti, the Gambia, Ghana, Liberia, Nigeria, Sierra Leone and Zimbabwe hold 5 on live PAPSS participation.

## 4. The norm

The AfCFTA Digital Trade Protocol's annex on digital payments asks central banks to oversee payment systems, make them interoperate at home and across borders, and join the continent's Pan-African Payment and Settlement System. This study asks the four questions above; it does not measure a country against the norm.

## 5. What the run reads

- **Carried**: nothing; no earlier study holds facts on these questions.
- **Read**: **894 story readings about the subject**, published since October 2023, in at most 20 stories a country: 879 in the batch's 160 shared calls (800 stories), read once for every study that lists them, and 15 in 10 calls of its own. A story published before the three-year window can set no stage, and the twenty are each country's best ranked across the batch (`study-calls.py --batch … --cap 20`).
- **Not read**: the rest of the about 3,400 stories a study lists, instruments, long reports, passing mentions and the documents the row's current cells cite. A question nothing answers is printed as *Not held*.

## 6. Token ceiling

**12 million** for this study; **95 million** for the batch, checked with `study-tokens.py` after every fan-out.

## 7. Tasks, in order

- [x] **D0. Prepared**: this file, `study.json` and the reading lists, 2026-10-16.
- [x] **D1. Read**, 2026-10-16: the batch's shared calls and this study's own, Sonnet drafters; 266 facts after the parent's corrections (`corrections.csv`).
- [x] **D2. Staged** as at 2026-09-30: 26 at 5, 15 at 4, 7 at 3, 2 at 2; unplaced 0, no evidence 4. Every cell is a first pass; no second drafter.
- [x] **D3. Written, rendered and linted**, by `study-first-write.py`; on the soft-launch map. Reported to Bill.

**Decided in the run**: Removed: PAPSS joined or signed with no live participation reported (DRC, Algeria, Egypt, Kenya, Morocco, Tunisia, Zimbabwe); RTGS and cheque clearing taken for a national switch (Mauritania, South Sudan).

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
