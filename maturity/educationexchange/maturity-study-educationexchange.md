---
type: task
reader: cc
title: maturity-study-educationexchange.md — education systems exchanging data, in four questions
last_reviewed: 2026-10-16
status: first pass run 2026-10-16; staged, written and on the soft-launch map; waits for Bill's acceptance
---

# Maturity study: educationexchange

*(Commissioned by Bill on 2026-10-16 as `dpi.exchange--interoperability-of-education-systems`, a first pass under `maturity/documentation/first-pass-batch.md`, in one batch with dataexchange, idverification, healthexchange, educationexchange and socialexchange.)*

## 1. What is assessed

**Data passing between education systems**: the EMIS with the examinations body, teacher payroll, learner registration or the national ID; a learner identifier shared by them. What moves education data between systems counts, whatever the product.

The study redraws `dpi.exchange--interoperability-of-education-systems`, which as at 2026-08-31 puts five countries at stage 3, 22 at 2 and 27 unplaced. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| Interoperability of education systems | Interoperability of education systems: interoperability of education systems | `dpi.exchange--interoperability-of-education-systems-interoperability-of-education-systems` |

Anything else the evidence names is `other`, noted and never staged: a school census or EMIS on its own (the schools study holds those), a learning platform, a plan or standard with no link in service, a single school's software, a donor's reporting tool.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Is a link between education systems under way? | A source from the last three years says one is contracted, being built or piloted |
| 2 | Do two education systems exchange data in service? | A source from the last three years says the EMIS exchanges data with the examinations body, teacher payroll, learner registration or another system in use |
| 3 | Is one learner identifier used across education systems? | A source from the last three years says learners carry a unique identifier used by two or more education systems |
| 4 | Are learner records linked to the national ID or another sector? | A source from the last three years says learner records are linked to the national ID, civil registration, health or social protection |

## 3. The ladders

**Interoperability of education systems**

| Stage | Answers |
|---|---|
| 1 Absent | A source from the last three years says it is absent |
| 2 Under way | Yes to 1 |
| 3 In service | Yes to 2 |
| 4 One learner ID | Yes to 3 |
| 5 Linked beyond | Yes to 4 |

A later yes answers the earlier ones (method §3.3). `study.json` holds this as three aspects: `exchange` (`inservice`, `underway`, `none`) for questions 1 and 2, `learnerid` (`shared`) for 3 and `linked` (`linked`) for 4. **For the drafter**: the system's name goes in `system`, the bodies or systems it links in the fact.

## 4. The norm

The African Union's Digital Education Strategy asks for an individual, identifier-based education management information system linked to the national ID and other sectors. This study asks the four questions above; it does not measure a country against the norm.

## 5. What the run reads

- **Carried**: nothing; no earlier study holds facts on these questions.
- **Read**: **154 news stories about the subject that no study has read**, in 43 countries; then the 158 documents the row's current cells cite, in 49 countries. 112 calls of its own, besides the batch's 19 shared calls over 84 stories read once for two studies or more.
- **Not read**: instruments, long reports and passing mentions. No web search and no handover to OSINT. A question nothing answers is printed as *Not held*.

## 6. Token ceiling

**40 million** for this study; **200 million** for the batch, checked with `study-tokens.py` after every fan-out.

## 7. Tasks, in order

- [x] **D0. Prepared**: this file, `study.json` and the reading lists, 2026-10-16.
- [x] **D1. Read**, 2026-10-16: the batch's 19 shared calls and this study's own, Sonnet drafters; 63 facts after the parent's corrections (`corrections.csv`).
- [x] **D2. Staged** as at 2026-09-30: 5 at 5, 2 at 4, 6 at 3, 11 at 2, 2 at 1; unplaced 3, no evidence 25. Every cell is a first pass; no second drafter.
- [x] **D3. Written, rendered and linted**, by `study-first-write.py`; on the soft-launch map. Reported to Bill. Batch tokens 203M of 200M, the reading of all five studies.

**Decided in the run**: Kenya's circular saying the learner identifier is needed for integration with the national ID is removed as linked: it states a need, not a link.

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
