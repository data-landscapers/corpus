---
type: task
reader: cc
title: maturity-study-ictjobs.md — employment in information and communication and youth unemployment, from the held figure
last_reviewed: 2026-10-16
status: first pass run 2026-10-16; staged, written and on the soft-launch map; waits for Bill's acceptance
---

# Maturity study: ictjobs

*(Commissioned by Bill on 2026-10-16 as `capacity.training--graduates-entering-dt-ecosystem`, a first pass under `maturity/documentation/first-pass-batch.md`, in one batch with civilserviceskills, digitalskills, policyresearch, schoolinternet, stemgraduates and ictjobs: the chapter Capacity. A measure, staged from the held series as `ictproduction` was, by `study_figure.py`.)*

## 1. What is assessed

**How much of the workforce is employed in information and communication, and whether youth unemployment is low.** The figure is ILOSTAT's employment in ISIC section J as a share of all employment (`ilostat-isic-j-employment` in `reference/measures.csv`), the frame row's own value; the frame reads absorption into the sector, since the STEM share is the university row's.

The study redraws `capacity.training--graduates-entering-dt-ecosystem`, which as at 2026-08-31 puts 18 countries at stage 4, nine each at 3, 2 and 1, and nine unplaced. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| ICT employment | Graduates entering DT ecosystem: ICT employment | `capacity.training--graduates-entering-dt-ecosystem-ict-employment` |

Anything else the evidence names is `other`, noted and never staged: a jobs or skills programme, an overall unemployment rate with no youth figure, an estimate with no survey named.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Is the figure at least 0.3? | The latest figure held, for 2023 or later, is 0.3 per cent of employment or more |
| 2 | At least 0.6? | That figure is 0.6 or more |
| 3 | At least 1? | That figure is 1 or more |
| 4 | Is youth unemployment 14 per cent or below? | A source from the last three years gives youth unemployment of 14 per cent or less from the national labour force survey |

## 3. The ladders

**ICT employment**

| Stage | Answers |
|---|---|
| 1 Absent | The latest figure, for 2023 or later, is below 0.3 |
| 2 Nascent | Yes to 1 |
| 3 Established | Yes to 2 |
| 4 Operating | Yes to 3 |
| 5 Leading | Yes to 3 and 4 |

- **The lines are the frame's own cuts** (`lookups/maturity-measures.csv`), fixed and not redrawn, so a country moves only when its own figure crosses one.
- **Question 4 counts only beside a figure at the top line**: it is the frame's stage-5 condition, not a step beyond the figure, so method §3.3 does not apply to it.
- **A fall is a fall**: the latest figure sets the stage. No figure for 2023 or later is *unplaced*; none at all is *No evidence*.

`study.json` holds this as two aspects: `jobs`, whose value is the figure (`official:…`), and `youth` (`low`).

## 4. The norm

Agenda 2063's second ten-year plan asks for 40 per cent of graduates in STEM and youth unemployment down to 14 per cent by 2033; the Continental TVET Strategy asks for wider technical training. The lines are the frame's; this study does not measure a country against the norm.

## 5. What the run reads

- **Carried**: the series for 46 countries, 78 figures since 2021, by `study-figure.py ictjobs carry`; no document opened.
- **Read**: **7 story readings**, in 4 Sonnet calls, for the 8 countries whose latest figure is at 1 or more (DJI, GAB, GNQ, MUS, NAM, SWZ, SYC, TUN), at most ten stories a country: nowhere else can question 4 move a stage.
- **Not read**: the rest of the 663 documents this study lists.

## 6. Token ceiling

**3 million** for this study; **70 million** for the batch.

## 7. Tasks, in order

- [x] **D0. Prepared**: this file, `study.json`, the reading lists and the carried figures, 2026-10-16.
- [x] **D1. Read**, 2026-10-16: Sonnet drafters, self-contained calls; corrections in `corrections.csv`.
- [x] **D2. Staged** as at 2026-09-30: 8 at 4, 2 at 3, 5 at 2, 8 at 1; unplaced 23, no evidence 8. Every cell is a first pass; no second drafter.
- [x] **D3. Written, rendered and linted**; on the soft-launch map. Reported to Bill.

**Decided in the run**: Nothing removed; no drafter found a youth unemployment figure of 14 per cent or less in the eight countries read.

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
