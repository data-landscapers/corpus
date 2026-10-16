---
type: task
reader: cc
title: maturity-study-idfrombirth.md — a unique identity number given at birth registration, in four questions
last_reviewed: 2026-10-16
status: first pass run 2026-10-16; staged, written and on the soft-launch map; waits for Bill's acceptance
---

# Maturity study: idfrombirth

*(Commissioned by Bill on 2026-10-16 as `dpi.id--digital-id-from-birth`, a first pass under `maturity/documentation/first-pass-batch.md`, in one batch with idrobustness, idcoverage, idmaintenance, authentication, idfrombirth, birthidlink and idregisters: the topic Digital Identity and CRVS.)*

## 1. What is assessed

**A unique identity number given to a child when the birth is registered**, which the person keeps for life and the ID system uses. What gives a number at birth counts, whoever issues it.

The study redraws `dpi.id--digital-id-from-birth`, which as at 2026-08-31 puts two countries at stage 4, seven at 3, 12 at 2 and 33 unplaced. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| Digital id from birth | Digital id from birth: digital id from birth | `dpi.id--digital-id-from-birth-digital-id-from-birth` |

Anything else the evidence names is `other`, noted and never staged: a birth certificate with only a certificate serial number, an ID number given at 16 or 18, a health card number, a birth registration campaign with no number.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Is a number at birth provided for or piloted? | A source from the last three years says a law or programme provides for a unique ID number at birth, or it is piloted in some districts or facilities |
| 2 | Is a number given at birth in part of the country? | A source from the last three years says children receive a unique ID number when their birth is registered, at least in some places |
| 3 | Is it given nationally? | A source from the last three years says every birth registered in the country receives the number, the birth record creating the identity record |
| 4 | Are all births registered with it? | A source from the last three years puts birth registration at all births, each given the number, and death registration at 80% or more |

## 3. The ladders

**Digital id from birth**

| Stage | Answers |
|---|---|
| 1 No number at birth | A source from the past three years says a birth creates no identity record: registration and ID are separate, or registration is on paper only. |
| 2 Provided for | Yes to 1 |
| 3 In part | Yes to 2 |
| 4 Nationally | Yes to 3 |
| 5 All births | Yes to 4 |

A later yes answers the earlier ones (method §3.3). `study.json` holds this as three aspects: `number` (`inservice`, `underway`, `none`) for stage 1 and questions 1 and 2, `national` (`national`) for 3 and `complete` (`target`) for 4.

## 4. The norm

The African Union's Digital Transformation Strategy asks for a digital legal identity for every person from birth, through civil registration; the SDG target is all births and 80% of deaths registered. This study asks the four questions above; it does not measure a country against the norm.

## 5. What the run reads

- **Carried**: nothing; no earlier study holds facts on these questions.
- **Read**: **730 news stories about the subject**, published since October 2023, in at most 15 a country: 725 in the batch's 149 shared calls, read once for every study that lists them, and 5 in 5 calls of its own. A story published before the three-year window can set no stage, and the fifteen are each country's best ranked across the batch (`study-calls.py --batch … --cap 15`).
- **Not read**: the rest of the 2,421 stories in the window, instruments, long reports, passing mentions and the documents the row's current cells cite. No web search and no handover to OSINT. A question nothing answers is printed as *Not held*.

## 6. Token ceiling

**10 million** for this study; **70 million** for the batch, checked with `study-tokens.py` after every fan-out.

## 7. Tasks, in order

- [x] **D0. Prepared**: this file, `study.json` and the reading lists, 2026-10-16.
- [x] **D1. Read**, 2026-10-16: the batch's shared calls and this study's own, Sonnet drafters; 39 facts after the parent's corrections (`corrections.csv`).
- [x] **D2. Staged** as at 2026-09-30: 2 at 4, 5 at 3, 5 at 2, 2 at 1; unplaced 3, no evidence 37. Every cell is a first pass; no second drafter.
- [x] **D3. Written, rendered and linted**, by `study-first-write.py`; on the soft-launch map. Reported to Bill.

**Decided in the run**: Nothing removed.

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
