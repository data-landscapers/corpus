---
type: task
reader: cc
title: maturity-study-schoolinternet.md — internet in secondary schools and digital skills in the curriculum, from the held figure
last_reviewed: 2026-10-16
status: first pass run 2026-10-16; staged, written and on the soft-launch map; waits for Bill's acceptance
---

# Maturity study: schoolinternet

*(Commissioned by Bill on 2026-10-16 as `capacity.training--dt-related-training-in-secondary-education`, a first pass under `maturity/documentation/first-pass-batch.md`, in one batch with civilserviceskills, digitalskills, policyresearch, schoolinternet, stemgraduates and ictjobs: the chapter Capacity. A measure, staged from the held series as `ictproduction` was, by `study_figure.py`.)*

## 1. What is assessed

**How many secondary schools have internet for teaching, and whether digital skills are a compulsory subject.** The figure is UNESCO's SDG 4.a.1 share of secondary schools with internet for pedagogical purposes (`uis-4a1-secondary-internet` in `reference/measures.csv`), the frame row's own value.

The study redraws `capacity.training--dt-related-training-in-secondary-education`, which as at 2026-08-31 puts two countries at stage 5, ten at 4, three at 3, seven at 2, 11 at 1 and 21 unplaced. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| Internet in secondary schools | DT-related training in secondary education: internet in secondary schools | `capacity.training--dt-related-training-in-secondary-education-internet-in-secondary-schools` |

Anything else the evidence names is `other`, noted and never staged: a connectivity or device programme, an optional or pilot course, a coding club, primary or university teaching.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Is the figure at least 17? | The latest figure held, for 2023 or later, is 17 per cent of secondary schools or more |
| 2 | At least 33? | That figure is 33 or more |
| 3 | At least 50? | That figure is 50 or more |
| 4 | Is digital literacy or computing compulsory in the secondary curriculum? | A source from the last three years says digital literacy, ICT or computing is a compulsory subject in the national secondary curriculum |

## 3. The ladders

**Internet in secondary schools**

| Stage | Answers |
|---|---|
| 1 Absent | The latest figure, for 2023 or later, is below 17 |
| 2 Nascent | Yes to 1 |
| 3 Established | Yes to 2 |
| 4 Operating | Yes to 3 |
| 5 Leading | Yes to 3 and 4 |

- **The lines are the frame's own cuts** (`lookups/maturity-measures.csv`), fixed and not redrawn, so a country moves only when its own figure crosses one.
- **Question 4 counts only beside a figure at the top line**: it is the frame's stage-5 condition, not a step beyond the figure, so method §3.3 does not apply to it.
- **A fall is a fall**: the latest figure sets the stage. No figure for 2023 or later is *unplaced*; none at all is *No evidence*.

`study.json` holds this as two aspects: `internet`, whose value is the figure (`official:…`), and `curriculum` (`compulsory`).

## 4. The norm

The AU Digital Education Strategy asks for half of institutions connected by 2027 and a digital literacy and coding framework for all students. The lines are the frame's; this study does not measure a country against the norm.

## 5. What the run reads

- **Carried**: the series for 34 countries, 70 figures since 2021, by `study-figure.py schoolinternet carry`; no document opened.
- **Read**: **60 story readings**, in 18 Sonnet calls, for the 10 countries whose latest figure is at 50 or more (DJI, DZA, MAR, MUS, NAM, RWA, SEN, SYC, TUN, ZMB), at most ten stories a country: nowhere else can question 4 move a stage.
- **Not read**: the rest of the 5,173 documents this study lists.

## 6. Token ceiling

**3 million** for this study; **70 million** for the batch.

## 7. Tasks, in order

- [x] **D0. Prepared**: this file, `study.json`, the reading lists and the carried figures, 2026-10-16.
- [x] **D1. Read**, 2026-10-16: Sonnet drafters, self-contained calls; corrections in `corrections.csv`.
- [x] **D2. Staged** as at 2026-09-30: 1 at 5, 9 at 4, 3 at 3, 6 at 2, 5 at 1; unplaced 10, no evidence 20. Every cell is a first pass; no second drafter.
- [x] **D3. Written, rendered and linted**; on the soft-launch map. Reported to Bill.

**Decided in the run**: Nothing removed.

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
