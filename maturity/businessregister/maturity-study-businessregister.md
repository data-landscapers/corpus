---
type: task
reader: cc
title: maturity-study-businessregister.md — firms registered online, in four questions
last_reviewed: 2026-10-16
status: first pass run 2026-10-16; staged, written and on the soft-launch map; waits for Bill's acceptance
---

# Maturity study: businessregister

*(Commissioned by Bill on 2026-10-16 as `dpi.registry--business-register`, a first pass under `maturity/documentation/first-pass-batch.md`, in one batch with populationregister, civilregister, addressregister, businessregister, socialregistry, electoralregister, taxregister and landregister: the topic Registries.)*

## 1. What is assessed

**The government register of companies and businesses, held digitally**: registration of a firm, its number and its record. What registers firms counts, whatever the registry is called.

The study redraws `dpi.registry--business-register`, which as at 2026-08-31 puts 19 countries at stage 3, 25 at 2, one at 1 and nine unplaced. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| Business register | Business register: business register | `dpi.registry--business-register` |

Anything else the evidence names is `other`, noted and never staged: a chamber of commerce membership list, a tax register alone, a licence for one sector, a private directory.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Is a digital business register under way? | A source from the last three years says a digital business register is procured, its records are being digitised, or a one-stop registration counter has opened |
| 2 | Can firms register online? | A source from the last three years says online business registration is in service |
| 3 | Does the firm's number serve tax or social security too? | A source from the last three years says registration gives a firm one number shared with the tax authority or social security |
| 4 | Are beneficial owners recorded? | A source from the last three years says the register collects the firms' beneficial owners, in service |

## 3. The ladders

**Business register**

| Stage | Answers |
|---|---|
| 1 Paper | A source from the past three years says business registration is on paper and held locally. |
| 2 Under way | Yes to 1 |
| 3 Online | Yes to 2 |
| 4 Shared number | Yes to 3 |
| 5 Beneficial owners | Yes to 4 |

A later yes answers the earlier ones (method §3.3). `study.json` holds this as three aspects: `registration` (`inservice`, `underway`, `none`) for stage 1 and questions 1 and 2, `shared` (`shared`) for 3 and `owners` (`recorded`) for 4.

## 4. The norm

The African Union's Digital Transformation Strategy asks for an electronic business register, and the AfCFTA Digital Trade Protocol for the identity of firms to be recognised across borders. This study asks the four questions above; it does not measure a country against the norm.

## 5. What the run reads

- **Carried**: nothing; no earlier study holds facts on these questions.
- **Read**: **123 story readings about the subject**, published since October 2023, in at most 20 stories a country: 33 in the batch's 15 shared calls (75 stories), read once for every study that lists them, and 90 in 43 calls of its own. A story published before the three-year window can set no stage, and the twenty are each country's best ranked across the batch (`study-calls.py --batch … --cap 20`).
- **Not read**: the rest of the 1,976 documents this study lists, instruments, long reports, passing mentions and the documents the row's current cells cite. A question nothing answers is printed as *Not held*.

## 6. Token ceiling

**13 million** for this study; **105 million** for the batch, checked with `study-tokens.py` after every fan-out.

## 7. Tasks, in order

- [x] **D0. Prepared**: this file, `study.json` and the reading lists, 2026-10-16.
- [x] **D1. Read**, 2026-10-16: the batch's shared calls and this study's own, Sonnet drafters; 49 facts after the parent's corrections (`corrections.csv`).
- [x] **D2. Staged** as at 2026-09-30: 3 at 5, 1 at 4, 9 at 3, 11 at 2, 1 at 1; unplaced 4, no evidence 25. Every cell is a first pass; no second drafter.
- [x] **D3. Written, rendered and linted**, by `study-first-write.py`; on the soft-launch map. Reported to Bill.

**Decided in the run**: Removed: a law's requirement read as a beneficial-owner register in service (Zambia).

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
