---
type: task
reader: cc
title: maturity-study-gridreliability.md — the forty-ninth maturity study: how often the power goes off, in four questions
last_reviewed: 2026-10-14
status: run 2026-10-14 on Bill's word; staged as at 2026-09-30, written, rendered and on the soft-launch map; waits for Bill to accept
---

# Maturity study: gridreliability

*(Commissioned by Bill on 2026-10-14 as `infra.energy--grid-reliability`, under `maturity/documentation/maturity-study-method.md`.)*

## 1. What is assessed

**How often the power goes off: more than ten times a month, up to ten, up to five, up to two, or once or less.**

**The figure** is power outages in a month: the regulator's or the utility's published interruption frequency (SAIFI) divided by 12, or else the number of outages firms report in a typical month in the World Bank's Enterprise Surveys.

The study redraws `infra.energy--grid-reliability`, which as at 2026-08-31 puts ten countries at each of stages 1, 2 and 3, 20 at stage 4 and none at stage 5, and leaves four unplaced. It touches no other row; who has power at all stays with `infra.energy--rural-electrification`, and data centres' supply with `infra.energy--sufficient-energy-and-water-for-data-centres`.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| Power outages a month | Grid reliability: power outages a month | `infra.energy--grid-reliability-power-outages-a-month` |

Anything else the evidence names is `other`, noted and never staged: how long outages last (SAIDI); hours of load shedding or a load-shedding schedule; a national grid collapse; a power station's availability or breakdowns; a figure for one city, region or customer class; generation capacity or a supply shortfall; a blackout story with no count.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Does the power go off ten times a month or fewer? | The latest figure held, for 2023 or later, is 10 or fewer outages a month |
| 2 | Five times or fewer? | That figure is 5 or fewer |
| 3 | Twice or fewer? | That figure is 2 or fewer |
| 4 | Once or less? | That figure is 1 or fewer |

## 3. The ladders

**Power outages a month**

| Stage | Answers |
|---|---|
| 1 Absent | The latest figure, for 2023 or later, is more than 10 outages a month |
| 2 Preparing | Yes to 1: ten or fewer |
| 3 Establishing | Yes to 2: five or fewer |
| 4 Operating | Yes to 3: two or fewer |
| 5 Leading | Yes to 4: one or fewer |

- **The figures Corpus already holds answer all four questions for 48 countries before anything is read**: stage 1 for nine, stage 2 for ten, stage 3 for 13, stage 4 for ten, and stage 5 for Cabo Verde, Morocco, Senegal, Seychelles, Tanzania and Tunisia.
- **Six countries have no figure in the window**: Algeria, Eritrea and Libya have none at all; Madagascar's is for 2022, South Africa's for 2020 and Sudan's for 2014. They are *No evidence* unless a story read in the run gives one.
- **The power-pool condition goes.** The row reaches stage 5 only with a best-fifth figure and the grid trading through its regional power pool, which no cell holds, and which is about trade, not whether the lights stay on. Stage 5 is a figure: once a month or less.
- **The lines are fixed, not drawn from where other countries stand.** The row divides the continent into fifths, so a country can move because its neighbours did; here it moves only when its own figure crosses a line. The row's provisional cuts of 10, 5 and 2 become the lines.
- **A regulator's or utility's SAIFI for 2023 or later is used in place of the survey**, as the row does: Guinea's and Senegal's are held.
- **A fall is a fall**: the latest figure sets the stage, whatever an earlier one said.
- **The survey counts outages firms report, not how many people the grid reaches**: South Sudan and Somalia reach stage 4 on it. The short summary says where a figure is the survey.

`study.json` holds this as one aspect, `outages`, whose value is the figure: `utility:0.76` for a regulator's or utility's SAIFI divided by 12, `survey:2.37` for the Enterprise Surveys, dated by the year the figure is for. The ladder counts the lines the latest figure clears. A fact is recorded only for interruptions across the whole country's grid; everything in §1's `other` list is a `systems` entry of class `other`, with the figure in `country_label`. **For the drafter**: `utility:` takes a regulator's or utility's interruption frequency for the whole grid (SAIFI, or interruptions per customer a year) divided by 12, to two decimals, the fact giving the published yearly figure and who publishes it; a figure already given per month is used as it stands. `survey:` takes an Enterprise Survey's outages in a typical month. Date it by the year the figure is for. Class `grid`, system the publisher's name for the figure. A count of grid collapses, an hours-a-day load-shedding figure or a SAIDI is not a fact: record it under `systems`, class `other`, with the figure in `country_label`.

## 4. The norm

The African Union's single electricity market and Continental Power System Master Plan ask for secure, reliable and affordable electricity across the continent. They set no outage figure. The lines here are Corpus's own.

## 5. What the run reads

- **Carried, nothing opened**: the Enterprise Surveys' outage figures in `reference/measures.csv`, 92 of them for 51 countries, by `scripts/study-gridreliability-carry.py`.
- **Read**: **92 documents** in 44 countries: the 49 stories about power outages that no study had read, and 43 the frame's cells cite that name the subject, among them the regulators' and utilities' annual reports where an interruption frequency is published.
- **Not read**: 87 documents the frame's cells cite that never name the subject, about who has power rather than how often it goes off; long texts, reports and passing mentions. **No web search and no handover to OSINT.**

## 6. Token ceiling

**25 million**, the mobilepenetration study's, which read 28 stories in 12.5 million.

## 7. Tasks, in order

- [x] **D0. Prepare**: this file, `study.json` and the reading lists, 2026-10-14.
- [x] **D1. Bill's word**: run on it, 2026-10-14.
- [x] **D2. Carried and read**: 92 survey figures for 51 countries; 62 drafters over 92 documents; ten facts, nine of them a utility's or regulator's figure.
- [x] **D3. Staged** as at 2026-09-30: 5: 6, 4: 11, 3: 12, 2: 10, 1: 9, six without evidence; two rows corrected; agreement 20 of 20.
- [x] **D4. Written, rendered and linted**; on the soft-launch map. **D5. Reported to Bill**, 2026-10-14. Tokens 25.8M of 25M: step 1 ran in the same session and its thread is counted.

**Decided in the run**:

- **Togo and Guinea move up to stage 4 on their own figures**: the regulator ARSE gives Togo a SAIFI of 23 for 2024 and EDG gives Guinea 23 for 2025, each 1.92 a month, in place of surveys at 2.74 and 3.24.
- **Senegal is at stage 5 on the regulator's figure**: CRSE gives Senelec a SAIFI of 9.12 for 2024, 0.76 a month.
- **The Gambia stays at stage 2 on its utility's own word**: NAWEC said two to six blackouts a month in June 2026; the top of the range is taken, not its midpoint (`corrections.csv`).
- **Equatorial Guinea stays at stage 4**: the survey's printed profile rounds the 2024 figure to 0.9, the held series gives 1.02; the series stands.
- **Niger's utility figure, 24 a month, is for 2019** and sets nothing; South Africa's Eskom reports load-shedding days and plant availability, not a count of outages, and are noted.
- **The summaries are written by script from the figures**, as mobilepenetration's were; no writer was called.

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
