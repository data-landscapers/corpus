---
type: task
reader: cc
title: maturity-study-digitaldivides.md — closing the gap between rural and urban internet use, in four questions
last_reviewed: 2026-10-16
status: first pass run 2026-10-16; staged, written and on the soft-launch map; waits for Bill's acceptance
---

# Maturity study: digitaldivides

*(Commissioned by Bill on 2026-10-16 as `include.divides--bridging-of-digital-divides`, a first pass under `maturity/documentation/first-pass-batch.md`, in one batch with feedbackportals, eparticipation, gendergap, disabilityaccess, refugees and digitaldivides: the chapter Inclusion.)*

## 1. What is assessed

**Closing the gap between rural and urban internet use**: a government or universal service fund programme that brings internet access to rural or underserved areas, and survey figures for internet use in rural and urban areas. What brings internet to rural people, or measures how far rural use lags urban, counts, whatever it is called.

The study redraws `include.divides--bridging-of-digital-divides`, which as at 2026-08-31 puts every country unplaced. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| Rural internet gap | Bridging of digital divides: rural internet gap | `include.divides--bridging-of-digital-divides` |

Anything else the evidence names is `other`, noted and never staged: a programme for schools or hospitals only, an operator's commercial roll-out with no government part, electricity with no internet, a national internet use figure with no rural and urban split, a figure for phone ownership or network coverage only.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Is a programme to connect rural areas under way? | A source from the last three years says the government or its universal service fund has launched, funded or is preparing a programme to bring internet access to rural or underserved areas |
| 2 | Is one delivering, with sites counted? | A source from the last three years says such a programme has connected a stated number of rural sites, towers, localities or people |
| 3 | Is rural and urban internet use measured? | A source from the last three years gives the share of people using the internet in rural areas and in urban areas, from a household survey or the statistics office |
| 4 | Is rural use at least four-fifths of urban? | A source from the last three years gives rural internet use of 80 per cent or more of the urban rate, from a household survey |

## 3. The ladders

**Rural internet gap**

| Stage | Answers |
|---|---|
| 1 Absent | A source from the past three years says no programme brings internet access to rural areas. |
| 2 Under way | Yes to 1 |
| 3 Delivering | Yes to 2 |
| 4 Measured | Yes to 3 |
| 5 Gap narrow | Yes to 4 |

**Every rung is met in order** *(Bill, 2026-10-30, message 49)*: a later yes does not answer an earlier one, so a country with the gap measured but no programme shown delivering stays at 2 (`study.json` → `later_yes: false`). Every question looks back three years. `study.json` holds this as three aspects: `programme` (`delivering`, `underway`, `none`) for stage 1 and questions 1 and 2, `measured` (`measured`) for 3 and `narrow` (`narrow`) for 4.

**Kenya stays at 2** *(Bill, 2026-10-31, message 59)*: what lifts a country past 2 is evidence that a named programme is delivering; a survey of the gap, however recent, does not. The three-year window runs from the survey year, as staged.

## 4. The norm

The Digital Transformation Strategy asks for universal, equitable and affordable access for all people wherever they live; the ITU's 2030 targets ask for universal internet use. This study asks the four questions above; it does not measure a country against the norm.

## 5. What the run reads

- **Carried**: nothing; no earlier study holds facts on these questions.
- **Read**: **246 story readings about the subject**, published since October 2023, in at most 20 stories a country: 14 in the batch's shared calls (4 calls over 17 stories), read once for every study that lists them, and 232 in 69 calls of its own. A story published before the three-year window can set no stage, and the twenty are each country's best ranked across the batch (`study-calls.py --batch … --cap 20`).
- **Not read**: the rest of the 4,070 documents this study lists, instruments, long reports, passing mentions and the documents the row's current cells cite. A question nothing answers is printed as *Not held*.

## 6. Token ceiling

**15 million** for this study; **90 million** for the batch, checked with `study-tokens.py` after every fan-out.

## 7. Tasks, in order

- [x] **D0. Prepared**: this file, `study.json` and the reading lists, 2026-10-16.
- [x] **D1. Read**, 2026-10-16: Sonnet drafters, self-contained calls; corrections in `corrections.csv`.
- [x] **D2. Staged** as at 2026-09-30: 3 at 4, 11 at 3, 19 at 2; unplaced 0, no evidence 21. Every cell is a first pass; no second drafter.
- [x] **D3. Written, rendered and linted**; on the soft-launch map. Reported to Bill.

**Decided in the run**: Nothing removed; Burkina Faso's rural and urban figures were shown at a justice forum, with no survey named.

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
