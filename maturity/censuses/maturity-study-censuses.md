---
type: task
reader: cc
title: maturity-study-censuses.md — the population census and household surveys, in four questions
last_reviewed: 2026-10-15
status: run 2026-10-15; staged, written and on the soft-launch map; waits for Bill's acceptance
---

# Maturity study: censuses

*(Commissioned by Bill on 2026-10-15 as `data.statistics--censuses-and-surveys`, under `maturity/documentation/maturity-study-method.md`.)*

## 1. What is assessed

**The country's count of its people, and the household surveys that measure them between counts**: a population and housing census (RGPH, *recensement général*, *recenseamento geral*), and a nationally representative household survey run by the statistics office, alone or with a partner (DHS, MICS, a living-standards, household budget or labour force survey, EHCVM).

The study redraws `data.statistics--censuses-and-surveys`, which as at 2026-08-31 puts 38 countries at stage 3 and 12 at stage 2, none at 1, 4 or 5, and leaves four unplaced (Algeria, Senegal, South Sudan, Tunisia). It touches no other row: the statistics law and the statistics strategy stay with their own studies.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| Censuses and surveys | Censuses and surveys: censuses and surveys | `data.statistics--censuses-and-surveys-censuses-and-surveys` |

Anything else the evidence names is `other`, noted and never staged: an agricultural, economic or business census, a school or health facility census, a survey of firms, a survey by a ministry or an NGO alone, an opinion poll (Afrobarometer), voter registration, population projections, a census of one region.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Is a census being prepared, or has one been taken? | A source from the last three years states mapping, a pilot census, funding or a date set for the next census, or a source states a census was counted in the last ten years. A census only promised is not a yes |
| 2 | Has a census been counted in the last ten years? | Enumeration completed since 1 October 2016 |
| 3 | Have its final results been published? | Final or definitive results of that census, not preliminary ones |
| 4 | Has a household survey published results in the last three years? | Results of a national household survey, as above, published since 1 October 2023 |

## 3. The ladders

**Censuses and surveys**

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
- **Not read**: census reports and survey reports themselves beyond those the cells cite, and passing mentions. A question nothing answers is printed as *Not held*.

## 6. Token ceiling

**50 million**: the statistics strategy read 97 calls for 36.4 million; this plans 127.

## 7. Tasks, in order

- [x] **D0. Prepare**: this file, `study.json` and the reading lists, 2026-10-15.
- [x] **D1. Bill's word**, 2026-10-15, the questions as prepared.
- [x] **D2. Read**: 127 drafters, ten regional stories read once; 237 facts, two removed by the parent (`corrections.csv`). The merge first refused survey facts, the sub-indicator assessing one class: `study-profile.py` now takes `also_assessed`, and `study.json` names `survey` there.
- [x] **D3. Staged** as at 2026-09-30: stage 5 Morocco, Uganda, Zambia; 4 Angola, Burkina Faso, Djibouti, Liberia, Mauritania, Namibia, Sierra Leone, Seychelles, Togo; 3 twenty-four; 2 DR Congo, Egypt, Equatorial Guinea, Niger, Nigeria; none at 1; unplaced eight; no evidence Algeria, Eritrea, Ghana, Kenya, Libya. The second drafter agreed on 20 of 20.
- [x] **D4. Written, rendered and linted**, by `study-censuses-write.py`; on the soft-launch map. **D5. Reported to Bill.** Tokens 41.8M of 50M, step 1's thread counted.

**Decided in the run**:

- **Togo's survey is removed**: the EHCVM 2021 cited by a 2026 article on literacy took the article's date. **Mauritania's is removed**: preliminary EPCV results presented to cabinet are not results published. Both stand at stage 4.
- **Morocco's decree fixing the legal population from the 2024 census counts as final results.** Djibouti's definitive-results report is taken at the date its listing gives.
- **Final results are dated by their first release**, not a later regional one (Angola: November 2025, not the Luanda report of 2026).
- **Kenya, Ghana and Zimbabwe hold no news on their 2019, 2021 and 2022 censuses**: what was read named only bills, voter models and survey launches. Kenya and Ghana are *No evidence*, Zimbabwe unplaced on its 2012 census. These are the rotation's searches (method §5), not this study's.
- **Unplaced eight hold only a census older than ten years or nothing dated**: Benin, Cabo Verde, Ethiopia, the Gambia, Sudan, Somalia, South Sudan, Zimbabwe.
- **The summaries were written by the script**; a country with five facts or fewer says so, and an empty survey paragraph lists the surveys the reading named without dated results.

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
