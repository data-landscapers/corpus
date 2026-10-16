---
type: task
reader: cc
title: maturity-study-stemgraduates.md — STEM graduates and a research and education network, from the held figure
last_reviewed: 2026-10-16
status: first pass run 2026-10-16; staged, written and on the soft-launch map; waits for Bill's acceptance
---

# Maturity study: stemgraduates

*(Commissioned by Bill on 2026-10-16 as `capacity.training--dt-related-university-facilities-and-qualifications`, a first pass under `maturity/documentation/first-pass-batch.md`, in one batch with civilserviceskills, digitalskills, policyresearch, schoolinternet, stemgraduates and ictjobs: the chapter Capacity. A measure, staged from the held series as `ictproduction` was, by `study_figure.py`.)*

## 1. What is assessed

**What share of tertiary graduates are in science, technology, engineering and mathematics, and whether a research and education network connects the public universities.** The figure is UNESCO's STEM share of tertiary graduates (`uis-stem-graduates` in `reference/measures.csv`), the frame row's own value.

The study redraws `capacity.training--dt-related-university-facilities-and-qualifications`, which as at 2026-08-31 puts seven countries at stage 3, 16 at 2, six at 1 and 25 unplaced. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| STEM graduates | DT-related university facilities and qualifications: STEM graduates | `capacity.training--dt-related-university-facilities-and-qualifications-stem-graduates` |

Anything else the evidence names is `other`, noted and never staged: a university's own campus network, a single university's lab or hub, a degree programme on its own.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Is the figure at least 13? | The latest figure held, for 2023 or later, is 13 per cent of tertiary graduates or more |
| 2 | At least 27? | That figure is 27 or more |
| 3 | At least 40? | That figure is 40 or more |
| 4 | Does a research and education network connect the public universities? | A source from the last three years says a national research and education network is in service connecting the public universities |

## 3. The ladders

**STEM graduates**

| Stage | Answers |
|---|---|
| 1 Absent | The latest figure, for 2023 or later, is below 13 |
| 2 Nascent | Yes to 1 |
| 3 Established | Yes to 2 |
| 4 Operating | Yes to 3 |
| 5 Leading | Yes to 3 and 4 |

- **The lines are the frame's own cuts** (`lookups/maturity-measures.csv`), fixed and not redrawn, so a country moves only when its own figure crosses one.
- **Question 4 counts only beside a figure at the top line**: it is the frame's stage-5 condition, not a step beyond the figure, so method §3.3 does not apply to it.
- **A fall is a fall**: the latest figure sets the stage. No figure for 2023 or later is *unplaced*; none at all is *No evidence*.

`study.json` holds this as two aspects: `stem`, whose value is the figure (`official:…`), and `nren` (`service`).

## 4. The norm

The AU Digital Education Strategy asks for a national research and education network in every country by 2027; Agenda 2063's second ten-year plan asks for 40 per cent of graduates in STEM by 2033. The lines are the frame's; this study does not measure a country against the norm.

## 5. What the run reads

- **Carried**: the series for 32 countries, 57 figures since 2021, by `study-figure.py stemgraduates carry`; no document opened.
- **Read**: **Nothing**: the one country whose latest figure is at 40 or more (BFA) has no story about the subject since October 2023, so question 4 is *Not held* there.
- **Not read**: the rest of the 984 documents this study lists. No web search and no handover to OSINT.

## 6. Token ceiling

**3 million** for this study; **70 million** for the batch.

## 7. Tasks, in order

- [x] **D0. Prepared**: this file, `study.json`, the reading lists and the carried figures, 2026-10-16.
- [x] **D1. Read**, 2026-10-16: Sonnet drafters, self-contained calls; corrections in `corrections.csv`.
- [x] **D2. Staged** as at 2026-09-30: 1 at 4, 5 at 3, 9 at 2, 3 at 1; unplaced 14, no evidence 22. Every cell is a first pass; no second drafter.
- [x] **D3. Written, rendered and linted**; on the soft-launch map. Reported to Bill.

**Decided in the run**: Nothing removed; Burkina Faso, the one country at 40 per cent, has no story on a research and education network.

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
