---
type: task
reader: cc
title: maturity-study-ruralelectrification.md — the fiftieth maturity study: how many rural people have electricity, in four questions
last_reviewed: 2026-10-14
status: prepared 2026-10-14; waits for Bill's word on the questions
---

# Maturity study: ruralelectrification

*(Commissioned by Bill on 2026-10-14 as `infra.energy--rural-electrification`, under `maturity/documentation/maturity-study-method.md`.)*

## 1. What is assessed

**How many people in the countryside have electricity: under a quarter, a quarter, half, 80% or 95% and more.**

**The figure** is the share of the rural population with electricity, from the grid or off it, as the World Bank counts it (SDG 7.1.1, rural), or a later rural figure published by the country's statistics office, ministry, regulator or electrification agency.

The study redraws `infra.energy--rural-electrification`, which as at 2026-08-31 puts 18 countries at stage 1, 16 at stage 2, seven at stage 3, four at stage 4 and seven at stage 5, and leaves Libya and Mauritania unplaced. It touches no other row; how often the power goes off stays with `infra.energy--grid-reliability`, and data centres' supply with `infra.energy--sufficient-energy-and-water-for-data-centres`.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| Rural people with electricity | Rural electrification: share of rural people with electricity | `infra.energy--rural-electrification-rural-people-with-electricity` |

Anything else the evidence names is `other`, noted and never staged: a national or urban access figure; a count of connections or of households connected; a target or a programme's plan; a figure for one region or district; generation capacity; a Mission 300 compact's commitments.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Do at least a quarter of rural people have electricity? | The latest figure held, for 2023 or later, is 25% or more |
| 2 | At least half? | That figure is 50% or more |
| 3 | At least 80%? | That figure is 80% or more |
| 4 | At least 95%? | That figure is 95% or more |

## 3. The ladders

**Rural people with electricity**

| Stage | Answers |
|---|---|
| 1 Absent | The latest figure, for 2023 or later, is under 25% |
| 2 Preparing | Yes to 1: a quarter or more |
| 3 Establishing | Yes to 2: half or more |
| 4 Operating | Yes to 3: 80% or more, the African Union's target |
| 5 Leading | Yes to 4: 95% or more, near universal |

- **The figures Corpus already holds answer all four questions for 52 countries before anything is read**: stage 1 for 17, stage 2 for 17, stage 3 for seven, stage 4 for Comoros, Eswatini, Ghana and South Africa, and stage 5 for Algeria, Cabo Verde, Egypt, Mauritius, Morocco, Seychelles and Tunisia.
- **Libya and Mauritania have no figure since 2012.** They are *No evidence* unless a story read in the run gives one.
- **The lines become round: a quarter and a half in place of the rubric's 27% and 53%.** Plain lines say the same thing in words. Only Madagascar moves, up to stage 2 at 26.5%.
- **Chad's 2024 figure of 100% is set aside as an error**: the series reads 0.4% for 2023 and never above 7.7% before. The 2023 figure stands, as it does in the row.
- **A national figure replaces the World Bank's only when it is for a later year and is for rural people or rural households.** A national rate, a target or a connections count is `other`.
- **A fall is a fall**: the latest figure sets the stage, whatever an earlier one said.

`study.json` holds this as one aspect, `access`, whose value is the figure: `wdi:45.0` for the World Bank's, `national:52.3` for a national rural figure, dated by the year the figure is for. The ladder counts the lines the latest figure clears. **For the drafter**: `national:` takes a rural access rate, of people or households, published by a statistics office, ministry, regulator or electrification agency, to one decimal, the fact naming the publisher and the year the figure is for. Class `access`, system the publisher's name for the figure. A national or urban rate, a count of connections or a target is not a fact: record it under `systems`, class `other`, with the figure in `country_label`.

## 4. The norm

The African Union's Agenda 2063 first ten-year plan asks for 80% of households to have electricity, which sets stage 4; the SDG 7.1 goal of universal access sets stage 5. Mission 300 aims to connect 300 million Africans by 2030 and sets no rural figure. The lines at a quarter and a half are Corpus's own.

## 5. What the run reads

- **Carried, nothing opened**: the World Bank's rural access figures in `reference/measures.csv`, 2010 to 2024 for 54 countries, by a carry script written at the run's start on the pattern of `study-gridreliability-carry.py`.
- **Read**: **136 stories** about electricity access, listed 178 times across 49 countries; a regional story is read once. None is listed for Algeria, Equatorial Guinea, Guinea-Bissau, Libya or Mauritius, so Libya stays *No evidence*.
- **Not read**: the long texts, reports and passing mentions the listing also holds. **No web search and no handover to OSINT.**

## 6. Token ceiling

**30 million**: gridreliability read 92 documents in 25.8 million; this reads 136 stories, all of them short.

## 7. Tasks, in order

- [x] **D0. Prepare**: this file, `study.json` and the reading lists, 2026-10-14.
- [ ] **D1. Bill's word.**
- [ ] **D2. Carried and read.**
- [ ] **D3. Staged** as at 2026-09-30.
- [ ] **D4. Written, rendered and linted**; on the soft-launch map. **D5. Reported to Bill.**

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
