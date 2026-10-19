---
type: task
reader: cc
title: maturity-study-retailpayments.md — mobile money and other everyday digital payments, in four questions
last_reviewed: 2026-10-16
status: first pass run 2026-10-16; staged, written and on the soft-launch map; waits for Bill's acceptance
---

# Maturity study: retailpayments

*(Commissioned by Bill on 2026-10-16 as `dpi.pay--p2p-p2g-and-p2b-functionality`, a first pass under `maturity/documentation/first-pass-batch.md`, in one batch with centralbank, g2ppayments, revenuecollection, businesspayments, retailpayments, paymentsuptake, crossborderpayments and consumerprotection: the topic Digital Payments and Fintech.)*

## 1. What is assessed

**Everyday digital payments by people**: mobile money, e-money wallets and instant payments between people, to shops and to government. What lets people pay each other digitally counts, whoever provides it.

The study redraws `dpi.pay--p2p-p2g-and-p2b-functionality`, which as at 2026-08-31 puts 50 countries at stage 3, two at 2 and two unplaced. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| P2P, P2G and P2B functionality | P2P, P2G and P2B functionality: p2p, p2g and p2b functionality | `dpi.pay--p2p-p2g-and-p2b-functionality` |

Anything else the evidence names is `other`, noted and never staged: a card scheme for banks alone, a payment from government to people, a crypto-asset exchange, a bank's internal system.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Is a mobile money service starting? | A source from the last three years says a mobile money or e-money service is licensed or piloted, with none yet in service |
| 2 | Are people paying by mobile money or e-money? | A source from the last three years says a mobile money or e-money service is in service |
| 3 | Can money move between providers? | A source from the last three years says payments between different mobile money providers, or between wallets and banks, are in service |
| 4 | Is there one national switch for wallets and banks? | A source from the last three years says a national switch connects mobile money wallets and bank accounts, in service |

## 3. The ladders

**P2P, P2G and P2B functionality**

| Stage | Answers |
|---|---|
| 1 None licensed | A source from the past three years says no mobile money or retail digital payment service is licensed. |
| 2 Starting | Yes to 1 |
| 3 In service | Yes to 2 |
| 4 Interoperable | Yes to 3 |
| 5 National switch | Yes to 4 |

A later yes answers the earlier ones (method §3.3). `study.json` holds this as three aspects: `service` (`inservice`, `underway`, `none`) for stage 1 and questions 1 and 2, `interop` (`interop`) for 3 and `switch` (`national`) for 4.

## 4. The norm

The African Union's Digital Transformation Strategy asks for interoperable e-money and digital financial services, with low-cost channels and agents reaching underserved areas. This study asks the four questions above; it does not measure a country against the norm.

## 5. What the run reads

- **Carried**: nothing; no earlier study holds facts on these questions.
- **Read**: **883 story readings about the subject**, published since October 2023, in at most 20 stories a country: 875 in the batch's 160 shared calls (800 stories), read once for every study that lists them, and 8 in 8 calls of its own. A story published before the three-year window can set no stage, and the twenty are each country's best ranked across the batch (`study-calls.py --batch … --cap 20`).
- **Not read**: the rest of the about 3,400 stories a study lists, instruments, long reports, passing mentions and the documents the row's current cells cite. A question nothing answers is printed as *Not held*.

## 6. Token ceiling

**12 million** for this study; **95 million** for the batch, checked with `study-tokens.py` after every fan-out.

## 7. Tasks, in order

- [x] **D0. Prepared**: this file, `study.json` and the reading lists, 2026-10-16.
- [x] **D1. Read**, 2026-10-16: the batch's shared calls and this study's own, Sonnet drafters; 635 facts after the parent's corrections (`corrections.csv`).
- [x] **D2. Staged** as at 2026-09-30: 23 at 5, 20 at 4, 7 at 3, 1 at 2; unplaced 0, no evidence 3. Every cell is a first pass; no second drafter.
- [x] **D3. Written, rendered and linted**, by `study-first-write.py`; on the soft-launch map. Reported to Bill.

**Decided in the run**: Zimbabwe's ZimSwitch read as providers interoperating, not a switch joining wallets and banks; Libya's bank QR instruction removed.

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
