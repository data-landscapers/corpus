---
type: task
reader: cc
title: maturity-study-ictproduction.md — ICT service exports and ICT equipment made at home, in four questions
last_reviewed: 2026-10-16
status: first pass run 2026-10-16; staged, written and on the soft-launch map; waits for Bill's acceptance
---

# Maturity study: ictproduction

*(Commissioned by Bill on 2026-10-16 as `tech.industry--national-capacity-in-dt-related-production`, a first pass under `maturity/documentation/first-pass-batch.md`, run beside the Technology batch: aigovernment, aisectoral, aisystems, aiabuse, techhubs and startups. The row is a measure, so it is staged from the held figures and not read with the batch.)*

## 1. What is assessed

**How much a country earns selling computer and telecommunications services abroad, as a share of GDP, and whether ICT equipment is assembled or made there.** The figure is the World Bank's ICT service exports over GDP (`wdi-ict-service-exports-gdp` in `reference/measures.csv`), the frame row's own value.

The study redraws `tech.industry--national-capacity-in-dt-related-production`, which as at 2026-08-31 puts 19 countries at stage 4 and nine each at 3, 2 and 1, by Africa quintiles. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| ICT exports and production | National capacity in DT-related production: ICT exports and production | `tech.industry--national-capacity-in-dt-related-production` |

Anything else the evidence names is `other`, noted and never staged: a plant announced or being built, an importer or retailer, a software company, a data centre, a chip ambition with no production.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Are ICT service exports at least 0.05 per cent of GDP? | The latest figure held, for 2023 or later, is 0.05 per cent or more |
| 2 | At least 0.2 per cent? | That figure is 0.2 per cent or more |
| 3 | At least 0.5 per cent? | That figure is 0.5 per cent or more |
| 4 | Is ICT equipment assembled or made in the country? | A source from the last three years says a plant assembling or making phones, computers or other ICT equipment is in production |

## 3. The ladders

**ICT exports and production**

| Stage | Answers |
|---|---|
| 1 Absent | The latest figure, for 2023 or later, is below 0.05 per cent of GDP |
| 2 Nascent | Yes to 1: 0.05 per cent or more |
| 3 Established | Yes to 2: 0.2 per cent or more |
| 4 Operating | Yes to 3: 0.5 per cent or more |
| 5 Leading | Yes to 3 and 4: 0.5 per cent or more, and ICT equipment made in the country |

- **The lines are the frame's own provisional cuts**, fixed and not redrawn as quintiles, so a country moves only when its own figure crosses one.
- **A plant counts only beside a figure of 0.5 per cent or more**: it is the frame's stage-5 condition, not a step beyond the figure, so method §3.3 does not apply to question 4.
- **A fall is a fall**: the latest figure sets the stage.

`study.json` holds this as two aspects: `exports`, whose value is the figure (`official:0.7088`), and `plant` (`production`).

## 4. The norm

The Digital Transformation Strategy's digital industry pillar asks for ICT assembling and manufacturing plants and growing ICT exports; STISA-2034 asks for technology-based production. Neither sets a figure; the lines are Corpus's.

## 5. What the run reads

- **Carried**: the World Bank series for 48 countries, 184 figures since 2021, by `study-ictproduction-carry.py`; no document opened.
- **Read**: **8 story readings**, in three Sonnet calls, for Kenya, Egypt and Morocco: the only countries at 0.5 per cent or more with a story about ICT manufacturing since October 2023. Nowhere else can question 4 move a stage.
- **Not read**: the rest of the 528 documents this study lists.

## 6. Token ceiling

**4 million**. Spent: about 0.2 million.

## 7. Tasks, in order

- [x] **D0. Prepared**: this file, `study.json`, the reading lists and the carry, 2026-10-16.
- [x] **D1. Read**, 2026-10-16: three Sonnet calls; five plant facts.
- [x] **D2. Staged** as at 2026-09-30: 1 at 5, 10 at 4, 8 at 3, 13 at 2, 11 at 1; unplaced 5, no evidence 6. Every cell is a first pass; no second drafter.
- [x] **D3. Written, rendered and linted**, by `study-ictproduction-write.py`; on the soft-launch map. Reported to Bill.

**Decided in the run**: Morocco's plant fact (STMicroelectronics near Casablanca) is in a story dated after the as-at, so Morocco stays at 4 until the next as-at. Unplaced: the five countries whose latest figure is before 2023. No evidence: the six the series does not cover.

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
