---
type: task
reader: cc
title: maturity-study-censuses.md — the population census and household surveys, in four questions
last_reviewed: 2026-10-15
status: prepared 2026-10-15; waits for Bill's word on the questions
---

# Maturity study: censuses

*(Commissioned by Bill on 2026-10-15 as `data.statistics--censuses-and-surveys`, under `maturity/documentation/maturity-study-method.md`.)*

## 1. What is assessed

**The country's count of its people, and the household surveys that measure them between counts**: a population and housing census (RGPH, *recensement général*, *recenseamento geral*), and a nationally representative household survey run by the statistics office, alone or with a partner (DHS, MICS, a living-standards, household budget or labour force survey, EHCVM).

The study redraws `data.statistics--censuses-and-surveys`, which as at 2026-08-31 puts 38 countries at stage 3 and 12 at stage 2, none at 1, 4 or 5, and leaves four unplaced (Algeria, Senegal, South Sudan, Tunisia). It touches no other row: the statistics law and the statistics strategy stay with their own studies.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| Censuses and surveys | Censuses and surveys: population census and household surveys | `data.statistics--censuses-and-surveys-censuses-and-surveys` |

Anything else the evidence names is `other`, noted and never staged: an agricultural, economic or business census, a school or health facility census, a survey of firms, a survey by a ministry or an NGO alone, an opinion poll (Afrobarometer), voter registration, population projections, a census of one region.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Is a census being prepared, or has one been taken? | A source from the last three years states mapping, a pilot census, funding or a date set for the next census, or a source states a census was counted in the last ten years. A census only promised is not a yes |
| 2 | Has a census been counted in the last ten years? | Enumeration completed since 1 October 2016 |
| 3 | Have its final results been published? | Final or definitive results of that census, not preliminary ones |
| 4 | Has a household survey published results in the last three years? | Results of a national household survey, as above, published since 1 October 2023 |

## 3. The ladder

| Stage | Answers |
|---|---|
| 1 Absent | A source from the last three years says no census has been counted in ten years and none is being prepared |
| 2 Preparing | Yes to 1 only: a census in preparation |
| 3 Counted | Yes to 2: a census counted, results preliminary or not yet out |
| 4 Published | Yes to 3: its final results published |
| 5 Surveyed | Yes to 4: a household survey published as well |

- **A later yes answers the earlier ones**: final results show a census was counted. **A survey answers question 4 only**: on its own it is noted, and it counts only above a published census.
- **The ten-year window is the UN's rule** of a census at least once a decade. A census counted before October 2016 with a successor in preparation is stage 2.
- **No census in ten years and none in preparation is not stage 1** unless a source says so; the cell is unplaced and the summary gives the year of the last count.
- **Changes from the row as it stands.** Stage 3 also took a survey programme with irregular rounds, stage 4 asked for disaggregation, a portal or microdata and a regular survey programme together, and stage 5 for every round met under the Charter's principles. Disaggregation and access need the results themselves read, and "under the Charter's principles" is alignment, so they go; the census is the ladder and one recent survey its top.

`study.json` holds this as three aspects: `census` (`taken`, `preparing`, `none`) for questions 1 and 2, `results` (`final`) for 3 and `survey` (`published`) for 4. **For the drafter**: the census or survey and its year go in `country_label` (e.g. *RGPH-5 2023*, *DHS 2022*), and the enumeration dates in the fact.

## 4. The norm

The African Charter on Statistics (2009) and SHaSA 2 ask each country to produce its core statistics from censuses and surveys. ECOSOC resolution E/RES/2025/13 sets the 2030 round of population and housing censuses, 2025 to 2034, and asks for one at least every ten years.

## 5. What the run reads

- **Read**: **286 news stories about a census or household survey that no study has read**, in 52 countries (none for Algeria or Mauritius), two calls of them regional and read once; then the 60 news stories and 33 documents that the row's current cells cite, in 40 countries. 127 drafters.
- **No earlier study is carried**: the statistics law and strategy studies noted censuses as `other` and hold no answer to these questions.
- **Not read**: census reports and survey reports themselves beyond those the cells cite, and passing mentions. **No web search and no handover to OSINT.** A question nothing answers is printed as *Not held*.

## 6. Token ceiling

**50 million**: the statistics strategy read 97 calls for 36.4 million; this plans 127.

## 7. Tasks, in order

- [x] **D0. Prepare**: this file, `study.json` and the reading lists, 2026-10-15.
- [ ] **D1. Bill's word** on the questions.
- [ ] **D2. Read**: the 127 calls, one workflow; merged and profiled.
- [ ] **D3. Stage** as at 2026-09-30 with `study-ladder-censuses.py`; the parent reads every stage 4 and 5 fact; second drafter on 20 cells.
- [ ] **D4. Write, render and lint**; soft-launch map. **D5. Report to Bill.**

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
