---
type: task
reader: cc
title: maturity-study-birthidlink.md — the civil register and the ID system exchanging records, in four questions
last_reviewed: 2026-10-23
status: first pass run 2026-10-16; staged, written and on the soft-launch map; waits for Bill's acceptance
---

# Maturity study: birthidlink

*(Commissioned by Bill on 2026-10-16 as `dpi.id--interoperability-of-birth-registration-and-digital-id`, a first pass under `maturity/documentation/first-pass-batch.md`, in one batch with idrobustness, idcoverage, idmaintenance, authentication, idfrombirth, birthidlink and idregisters: the topic Digital Identity and CRVS.)*

## 1. What is assessed

**Records passing between the civil register (births, deaths, marriages) and the national ID system**: births feeding the ID register, deaths retiring ID numbers, changes of name or status carried across. What links the two registers counts, whatever it is called.

The study redraws `dpi.id--interoperability-of-birth-registration-and-digital-id`, which as at 2026-08-31 puts 15 countries at stage 3, 21 at 2 and 17 unplaced. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| Interoperability of birth registration and digital id | Interoperability of birth registration and digital id: interoperability of birth registration and digital id | `dpi.id--interoperability-of-birth-registration-and-digital-id` |

Anything else the evidence names is `other`, noted and never staged: a civil register or ID system on its own, a statistics office's use of civil records, a birth registration campaign with no link to the ID, a plan with no link.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Is a link under way? | A source from the last three years says a link between the civil register and the ID system is planned, contracted or piloted, or one body is made responsible for both |
| 2 | Is one link in service? | A source from the last three years says records pass one way or for one event (births feed the ID, or deaths retire ID numbers), or one body holds both registers |
| 3 | Do records pass both ways, across events? | A source from the last three years says births enrol people in the ID system and deaths retire their numbers, or more |
| 4 | Is the exchange reported? | A source from the last three years gives a figure for records exchanged, numbers retired on death or records reconciled between the two. **An audit is not system exchange** *(Bill, 2026-10-23)*: a figure from an anti-fraud or other audit comparing the two does not answer it, only one for the systems' own exchange |

## 3. The ladders

**Interoperability of birth registration and digital id**

| Stage | Answers |
|---|---|
| 1 Separate | A source from the past three years says the civil register and the ID system do not exchange records. |
| 2 Under way | Yes to 1 |
| 3 One link | Yes to 2 |
| 4 Both ways | Yes to 3 |
| 5 Reported | Yes to 4 |

**A later yes no longer answers the earlier ones** *(Bill, 2026-10-23; method §3.3 switched off here, `study.json` → `"later_yes": false`)*: a stage needs every lower rung shown by its own evidence, and a cell whose evidence stops short takes the rung it reaches. Question 2 still answers question 1: a link in service was under way first, and the two are one aspect. `study.json` holds this as three aspects: `link` (`inservice`, `underway`, `none`) for stage 1 and questions 1 and 2, `events` (`both`) for 3 and `reported` (`reported`) for 4.

## 4. The norm

The African Union's interoperability framework and the African ministers responsible for civil registration ask that civil registration, vital statistics and the ID system work as one, each event updating the others. This study asks the four questions above; it does not measure a country against the norm.

## 5. What the run reads

- **Carried**: nothing; no earlier study holds facts on these questions.
- **Read**: **730 news stories about the subject**, published since October 2023, in at most 15 a country: 725 in the batch's 149 shared calls, read once for every study that lists them, and 5 in 5 calls of its own. A story published before the three-year window can set no stage, and the fifteen are each country's best ranked across the batch (`study-calls.py --batch … --cap 15`).
- **Not read**: the rest of the 2,421 stories in the window, instruments, long reports, passing mentions and the documents the row's current cells cite. A question nothing answers is printed as *Not held*.

## 6. Token ceiling

**10 million** for this study; **70 million** for the batch, checked with `study-tokens.py` after every fan-out.

## 7. Tasks, in order

- [x] **D0. Prepared**: this file, `study.json` and the reading lists, 2026-10-16.
- [x] **D1. Read**, 2026-10-16: the batch's shared calls and this study's own, Sonnet drafters; 109 facts after the parent's corrections (`corrections.csv`).
- [x] **D2. Staged** as at 2026-09-30: 23 at 3, 17 at 2; unplaced 4, no evidence 10. Every cell is a first pass; no second drafter.
- [x] **D3. Written, rendered and linted**, by `study-first-write.py`; on the soft-launch map. Reported to Bill.

**Decided in the run**: Nothing removed.

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
