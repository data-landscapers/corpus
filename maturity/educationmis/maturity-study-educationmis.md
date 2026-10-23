---
type: task
reader: cc
title: maturity-study-educationmis.md — the national education information system, in four questions
last_reviewed: 2026-10-23
status: first pass run 2026-10-16; staged, written and on the soft-launch map; waits for Bill's acceptance
---

# Maturity study: educationmis

*(Commissioned by Bill on 2026-10-16 as `dpi.mis--education`, a first pass under `maturity/documentation/first-pass-batch.md`, in one batch with agrisatellite, metsatellite, digitalsovereignty, healthmis, educationmis, egovservices and ruralelectrification: the chapter the last seven indicators.)*

## 1. What is assessed

**The national education management information system (EMIS)**: the system in which the education ministry holds its school census and, at its fuller stage, a record for each learner, teacher and school. What holds the ministry's national education statistics and records digitally counts, whatever it is called; one school's or district's records do not.

The study redraws `dpi.mis--education`, which as at 2026-08-31 puts one country at stage 3, five at 2 and 48 unplaced. The `schools` study claimed the row until 2026-10-16 but staged only rural primary schools; this study asks about the national system *(Bill)*. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| Education information system | Education: education information system | `dpi.mis--education` |

Anything else the evidence names is `other`, noted and never staged: records kept by one school or district on its own, a learning platform or e-learning content, an exam board's results portal on its own, a school's own software, a university admissions system, a donor's survey with no ministry system on record.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Is an education information system under way? | A source from the last three years says the education ministry procured, piloted or is building an education management information system |
| 2 | Is the school census run through it? | A source from the last three years says the ministry collected or published an annual school census or education statistics through its education information system |
| 3 | Does it hold a record for each learner? | A source from the last three years says the system holds individual learner records with a unique learner number, in service for schools across the country |
| 4 | Is it linked to the national ID? | A source from the last three years says learner records are linked to the national ID or birth registration number, or exchange data with another government system |

## 3. The ladders

**Education information system**

| Stage | Answers |
|---|---|
| 1 Absent | A source from the past three years says there is no education management information system. |
| 2 Under way | Yes to 1 |
| 3 School census | Yes to 2 |
| 4 Learner records | Yes to 3 |
| 5 Linked | Yes to 4 |

A later yes answers the earlier ones (method §3.3). `study.json` holds this as three aspects: `system` (`inservice`, `underway`, `none`) for stage 1 and questions 1 and 2, `learners` (`individual`) for 3 and `linked` (`linked`) for 4.

**Question 3, learner records in service for schools across the country, is shown by its own evidence** *(Bill, 2026-10-23; `study.json` → `"must_show": [3]`)*: a later yes no longer answers it, and answers the other questions still. No cell moved.

## 4. The norm

The AU Digital Education Strategy asks for education management information systems to move from aggregate school returns to records for each learner, teacher and school. This study asks the four questions above; it does not measure a country against the norm.

## 5. What the run reads

- **Carried**: nothing; no earlier study holds facts on these questions.
- **Read**: **135 story readings about the subject**, published since October 2023, in at most 20 stories a country: 21 in the batch's shared calls (8 calls over 36 stories), read once for every study that lists them, and 114 in 45 calls of its own. A story published before the three-year window can set no stage, and the twenty are each country's best ranked across the batch (`study-calls.py --batch … --cap 20`).
- **Not read**: the rest of the 1,022 documents this study lists, instruments, long reports, passing mentions and the documents the row's current cells cite. A question nothing answers is printed as *Not held*.

## 6. Token ceiling

**12 million** for this study; **75 million** for the batch, checked with `study-tokens.py` after every fan-out.

## 7. Tasks, in order

- [x] **D0. Prepared**: this file, `study.json` and the reading lists, 2026-10-16.
- [x] **D1. Read**, 2026-10-16: Sonnet drafters, self-contained calls; corrections in `corrections.csv`.
- [x] **D2. Staged** as at 2026-09-30: 2 at 5, 4 at 4, 14 at 3, 18 at 2; unplaced 1, no evidence 15. Every cell is a first pass; no second drafter.
- [x] **D3. Written, rendered and linted**; on the soft-launch map. Reported to Bill.

**Decided in the run**: Removed at the top-stage check: GMB-005, an MoU signed, not a link in service; KEN-004, identity details required for a future integration, not a link in service; SLE-005, a pilot in four districts yet to start, not a national link.

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
