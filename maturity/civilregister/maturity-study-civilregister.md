---
type: task
reader: cc
title: maturity-study-civilregister.md — births and deaths registered digitally, in four questions
last_reviewed: 2026-10-25
status: first pass run 2026-10-16; staged, written and on the soft-launch map; waits for Bill's acceptance
---

# Maturity study: civilregister

*(Commissioned by Bill on 2026-10-16 as `dpi.registry--civil-register`, a first pass under `maturity/documentation/first-pass-batch.md`, in one batch with populationregister, civilregister, addressregister, businessregister, socialregistry, electoralregister, taxregister and landregister: the topic Registries.)*

## 1. What is assessed

**Civil registration of births and deaths in a digital system**: the register that records vital events, held electronically. What records births and deaths digitally counts, whoever runs it.

The study redraws `dpi.registry--civil-register`, which as at 2026-08-31 puts 18 countries at stage 3, 23 at 2 and 13 unplaced. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| Civil register | Civil register: civil register | `dpi.registry--civil-register` |

Anything else the evidence names is `other`, noted and never staged: a health facility's own records, a national ID enrolment, a census, a paper register with no digital system named.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Is digital civil registration under way? | A source from the last three years says a digital civil registration system is procured, piloted or rolled out to some offices |
| 2 | Are births registered digitally across the country? | A source from the last three years says births are registered in a digital system in service nationally |
| 3 | Are deaths registered digitally too? | A source from the last three years says deaths are registered in the digital system, in service |
| 4 | Are 90% or more of births registered? | A source from the last three years puts the share of births registered in the digital system at 90% or more. A national rate that may include paper registration is not a yes *(Bill, 2026-10-25)* |

## 3. The ladders

**Civil register**

| Stage | Answers |
|---|---|
| 1 Paper | A source from the past three years says civil registration is on paper with no digital register. |
| 2 Under way | Yes to 1 |
| 3 Births digital | Yes to 2 |
| 4 Deaths digital | Yes to 3 |
| 5 Births at 90% | Yes to 4 |

A later yes answers the earlier ones (method §3.3). `study.json` holds this as three aspects: `births` (`inservice`, `underway`, `none`) for stage 1 and questions 1 and 2, `deaths` (`digital`) for 3 and `coverage` (`target`, `general`) for 4, where `general` is a national rate not tied to the digital system and is not a yes.

**Question 2, births registered digitally across the country, is shown by its own evidence** *(Bill, 2026-10-23; `study.json` → `"must_show": [2]`)*: a later yes no longer answers it, and answers the other questions still. Seven cells fell to stage 2: Burkina Faso, Ethiopia, Guinea-Bissau, Somalia and Zambia from 4, Botswana and Cabo Verde from 5.

## 4. The norm

The African Union's Digital Transformation Strategy and the Africa Programme on Accelerated Improvement of CRVS ask for digital civil registration; the SDG target is every birth and 80% of deaths registered. This study asks the four questions above; it does not measure a country against the norm.

## 5. What the run reads

- **Carried**: nothing; no earlier study holds facts on these questions.
- **Read**: **409 story readings about the subject**, published since October 2023, in at most 20 stories a country: 58 in the batch's 15 shared calls (75 stories), read once for every study that lists them, and 351 in 106 calls of its own. A story published before the three-year window can set no stage, and the twenty are each country's best ranked across the batch (`study-calls.py --batch … --cap 20`).
- **Not read**: the rest of the 3,370 documents this study lists, instruments, long reports, passing mentions and the documents the row's current cells cite. A question nothing answers is printed as *Not held*.

## 6. Token ceiling

**13 million** for this study; **105 million** for the batch, checked with `study-tokens.py` after every fan-out.

## 7. Tasks, in order

- [x] **D0. Prepared**: this file, `study.json` and the reading lists, 2026-10-16.
- [x] **D1. Read**, 2026-10-16: the batch's shared calls and this study's own, Sonnet drafters; 184 facts after the parent's corrections (`corrections.csv`).
- [x] **D2. Staged** as at 2026-09-30: 4 at 5, 9 at 4, 2 at 3, 29 at 2, 1 at 1; unplaced 1, no evidence 8. Every cell is a first pass; no second drafter.
- [x] **D3. Written, rendered and linted**, by `study-first-write.py`; on the soft-launch map. Reported to Bill.

**Decided in the run**: Removed: two Namibia rows whose source has no link; the population register's death update read as death registration (Benin); computerised municipal certificates (Eritrea); 90% birth registration in Ghana, which the same source says fell to 73% by end-2025; a share of people holding a birth certificate (São Tomé and Príncipe). Djibouti (city only) and Somalia (a pilot) revalued to under way.

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
