---
type: task
reader: cc
title: maturity-study-civilserviceskills.md — digital-skills training for civil servants, in four questions
last_reviewed: 2026-10-16
status: first pass run 2026-10-16; staged, written and on the soft-launch map; waits for Bill's acceptance
---

# Maturity study: civilserviceskills

*(Commissioned by Bill on 2026-10-16 as `capacity.literacy--digital-literacy-civil-service`, a first pass under `maturity/documentation/first-pass-batch.md`, in one batch with civilserviceskills, digitalskills, policyresearch, schoolinternet, stemgraduates and ictjobs: the chapter Capacity.)*

## 1. What is assessed

**Digital-skills training for civil servants**: a government programme, academy, platform or certification that trains public servants in digital skills, from basic computer use to e-government and data. What trains civil servants in digital skills counts, whatever it is called.

The study redraws `capacity.literacy--digital-literacy-civil-service`, which as at 2026-08-31 puts every country unplaced. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| Civil service digital skills | Digital literacy (civil service): civil service digital skills | `capacity.literacy--digital-literacy-civil-service` |

Anything else the evidence names is `other`, noted and never staged: training for the public, students or companies, a course for a ministry's own IT staff only, a strategy or law that only promises training, a study tour abroad.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Is digital-skills training for civil servants under way? | A source from the last three years says a government body has launched, piloted or is preparing a digital-skills programme for civil servants, or has held digital-skills courses for officials |
| 2 | Is a standing programme in service? | A source from the last three years says a government digital-skills programme, academy or learning platform for civil servants is in service and has trained a stated number of public servants |
| 3 | Does it reach across government? | A source from the last three years says the programme is open to or required of civil servants in all ministries, or has trained staff across most of government |
| 4 | Is the share trained published? | A source from the last three years gives the share of the civil service that has completed digital-skills training, or the number trained beside the civil-service headcount |

## 3. The ladders

**Civil service digital skills**

| Stage | Answers |
|---|---|
| 1 Absent | A source from the past three years says civil servants receive no digital-skills training. |
| 2 Under way | Yes to 1 |
| 3 Programme | Yes to 2 |
| 4 Across government | Yes to 3 |
| 5 Share published | Yes to 4 |

A later yes answers the earlier ones (method §3.3). **Two rulings** *(Bill, 2026-10-26)*: a programme open to all civil servants reaches across government with no number trained (message 32: Tunisia and Cameroon stay at 4), and so does a government commitment to train at that scale (message 33: Ghana's 200,000, and Zimbabwe's mandatory training for all, to 4). `study.json` holds this as three aspects: `training` (`inservice`, `underway`, `none`) for stage 1 and questions 1 and 2, `reach` (`wide`) for 3 and `share` (`published`) for 4.

## 4. The norm

The AU Charter on the Principles of Public Service and Administration asks for systematic capacity development of public servants; the Digital Transformation Strategy asks for digital and data skills in state institutions. This study asks the four questions above; it does not measure a country against the norm.

## 5. What the run reads

- **Carried**: nothing; no earlier study holds facts on these questions.
- **Read**: **385 story readings about the subject**, published since October 2023, in at most 20 stories a country: 268 in the batch's shared calls (49 calls over 243 stories), read once for every study that lists them, and 117 in 67 calls of its own. A story published before the three-year window can set no stage, and the twenty are each country's best ranked across the batch (`study-calls.py --batch … --cap 20`).
- **Not read**: the rest of the 4,820 documents this study lists, instruments, long reports, passing mentions and the documents the row's current cells cite. A question nothing answers is printed as *Not held*.

## 6. Token ceiling

**20 million** for this study; **70 million** for the batch, checked with `study-tokens.py` after every fan-out.

## 7. Tasks, in order

- [x] **D0. Prepared**: this file, `study.json` and the reading lists, 2026-10-16.
- [x] **D1. Read**, 2026-10-16: Sonnet drafters, self-contained calls; corrections in `corrections.csv`.
- [x] **D2. Staged** as at 2026-09-30: 3 at 4, 2 at 3, 27 at 2; unplaced 3, no evidence 19. Every cell is a first pass; no second drafter.
- [x] **D3. Written, rendered and linted**; on the soft-launch map. Reported to Bill.

**Decided in the run**: TGO and ZWE lose `reach: wide` (27 data specialists; a certification only planned).

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
