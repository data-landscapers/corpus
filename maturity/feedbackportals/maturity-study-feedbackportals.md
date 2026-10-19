---
type: task
reader: cc
title: maturity-study-feedbackportals.md — digital channels for complaints about public services, in four questions
last_reviewed: 2026-10-16
status: first pass run 2026-10-16; staged, written and on the soft-launch map; waits for Bill's acceptance
---

# Maturity study: feedbackportals

*(Commissioned by Bill on 2026-10-16 as `include.access--citizen-feedback-portals`, a first pass under `maturity/documentation/first-pass-batch.md`, in one batch with feedbackportals, eparticipation, gendergap, disabilityaccess, refugees and digitaldivides: the chapter Inclusion.)*

## 1. What is assessed

**A digital channel for complaints and feedback on public services**: a government web portal, app, SMS or messaging service through which people report problems with, complain about or rate public services. What takes citizens' feedback on public services digitally counts, whatever it is called.

The study redraws `include.access--citizen-feedback-portals`, which as at 2026-08-31 puts one country at stage 4, five at 3, 35 at 2, one at 1 and 12 unplaced. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| Citizen feedback channel | Citizen feedback portals: citizen feedback channel | `include.access--citizen-feedback-portals` |

Anything else the evidence names is `other`, noted and never staged: a portal that only gives information, a company's customer-service line, an ombudsman or anti-corruption office with no digital channel on record, a line for reporting crimes, a consultation on a draft law or policy.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Is a digital feedback channel under way? | A source from the last three years says a government body has launched, piloted or is preparing a web portal, app or messaging service through which people report problems with or complain about public services |
| 2 | Is one in service with cases on record? | A source from the last three years says such a channel is in service and gives a number of complaints, reports or cases it has received or handled |
| 3 | Does it reach across government? | A source from the last three years says a national channel takes complaints about the services of most ministries or of local governments, or routes them to the bodies responsible across government |
| 4 | Are its results published? | A source from the last three years gives the share of complaints resolved, response times, or a published report of the cases and what was done about them |

## 3. The ladders

**Citizen feedback channel**

| Stage | Answers |
|---|---|
| 1 Absent | A source from the past three years says people have no digital channel to complain about or comment on public services. |
| 2 Under way | Yes to 1 |
| 3 In service | Yes to 2 |
| 4 Across government | Yes to 3 |
| 5 Results published | Yes to 4 |

A later yes answers the earlier ones (method §3.3). `study.json` holds this as three aspects: `channel` (`inservice`, `underway`, `none`) for stage 1 and questions 1 and 2, `reach` (`wide`) for 3 and `results` (`published`) for 4.

## 4. The norm

The AU Charter on Decentralisation asks that ICT be used so residents can give feedback to their representatives; the UN E-Participation Index ranks e-information, e-consultation and e-decision-making. This study asks the four questions above; it does not measure a country against the norm.

## 5. What the run reads

- **Carried**: nothing; no earlier study holds facts on these questions.
- **Read**: **31 story readings about the subject**, published since October 2023, in at most 20 stories a country: 0 in the batch's shared calls (4 calls over 17 stories), read once for every study that lists them, and 31 in 19 calls of its own. A story published before the three-year window can set no stage, and the twenty are each country's best ranked across the batch (`study-calls.py --batch … --cap 20`).
- **Not read**: the rest of the 882 documents this study lists, instruments, long reports, passing mentions and the documents the row's current cells cite. A question nothing answers is printed as *Not held*.

## 6. Token ceiling

**15 million** for this study; **90 million** for the batch, checked with `study-tokens.py` after every fan-out.

## 7. Tasks, in order

- [x] **D0. Prepared**: this file, `study.json` and the reading lists, 2026-10-16.
- [x] **D1. Read**, 2026-10-16: Sonnet drafters, self-contained calls; corrections in `corrections.csv`.
- [x] **D2. Staged** as at 2026-09-30: 1 at 5, 1 at 4, 7 at 2; unplaced 0, no evidence 45. Every cell is a first pass; no second drafter.
- [x] **D3. Written, rendered and linted**; on the soft-launch map. Reported to Bill.

**Decided in the run**: Nothing removed.

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
