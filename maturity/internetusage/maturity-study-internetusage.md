---
type: task
reader: cc
title: maturity-study-internetusage.md — the thirty-ninth maturity study: people who use the internet, in four questions
last_reviewed: 2026-10-13
status: run 2026-10-13 on Bill's word; staged as at 2026-09-30, written, rendered and on the soft-launch map; waits for Bill to accept
---

# Maturity study: internetusage

*(Commissioned by Bill on 2026-10-13 as `infra.connect--internet-usage`, under `maturity/documentation/maturity-study-method.md`.)*

## 1. What is assessed

**How many of a country's people use the internet: a quarter, half, four in five, or nearly everyone.**

**The figure** is the share of the whole population who used the internet in the last three months, as the International Telecommunication Union publishes it for each country, or as a national household survey or census gives it. **A government press statement that gives the share of people who use the internet counts as a survey** *(Bill, 2026-10-13)*.

The study redraws `infra.connect--internet-usage`, which as at 2026-08-31 puts 15 countries at stage 1, 19 at stage 2, 17 at stage 3 and three at stage 4, with none at stage 5 and none unplaced. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| People who use the internet | Internet usage: people who use the internet | `infra.connect--internet-usage-people-who-use-the-internet` |

Anything else the evidence names is `other`, noted and never staged: internet or mobile-data subscriptions, which count a person once for every line; an operator's or the regulator's count of "internet users" or its "penetration rate", which are counts of subscriptions; DataReportal's yearly country figures; a figure for adults only; households with internet; mobile internet users; social media users; network coverage; the price of data.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Does at least a quarter of the population use the internet? | The latest figure held, for 2024 or later, is 25 per cent or more |
| 2 | Does at least half? | That figure is 50 per cent or more |
| 3 | Do at least four in five? | That figure is 80 per cent or more |
| 4 | Does nearly everyone? | That figure is 95 per cent or more |

## 3. The ladders

**People who use the internet**

| Stage | Answers |
|---|---|
| 1 Absent | The latest figure, for 2024 or later, is below 25 per cent: fewer than a quarter use the internet |
| 2 Preparing | Yes to 1: at least a quarter |
| 3 Establishing | Yes to 1 and 2: at least half |
| 4 Operating | Yes to 1, 2 and 3: at least four in five |
| 5 Leading | Yes to all four: nearly everyone |

- **The figures Corpus already holds answer all four questions for 51 countries before anything is read**: stage 1 for 11, stage 2 for 21, stage 3 for 16, and stage 4 for Libya, Morocco and Seychelles. None reaches stage 5.
- **Three countries have no figure in the window**: Eritrea's latest is for 2020, South Sudan's for 2019 and Sudan's for 2017. They are *No evidence* unless a story read in the run gives one.
- **The two lower lines are a quarter and a half, where the row as it stands uses 27 and 53 per cent**, thirds of the way to 80. On the held figures that moves Sierra Leone (25.1) and Lesotho (51.8) up a stage and no other country.
- **An estimate by the International Telecommunication Union counts.** It is the latest figure for 45 of the 51; the summary says where a figure is an estimate and not a survey.
- **A national survey or census figure for 2024 or later, where one is held, is used in place of an estimate**, and the newest survey in place of an older one. A government press statement's figure is a survey figure where it is a share of people; one that counts subscriptions or lines is not.
- **A fall is a fall**: the latest figure sets the stage, whatever an earlier one said.
- **A regulator's or operator's count, DataReportal's figure, and a figure for adults only are noted and never used**, even for a country with nothing else. South Sudan's current cell rests on the regulator's count.

`study.json` holds this as one aspect, `users`, each fact carrying `survey:` or `estimate:`, its per cent and its year; the ladder counts the lines the latest figure clears.

## 4. The norm

The African Union's second ten-year plan for Agenda 2063 asks that 80 per cent of the population be reached by broadband of at least 6 megabits a second by 2033, and its Digital Transformation Strategy 2020–2030 asks for everyone by 2030. The International Telecommunication Union's 2030 target for universal connectivity is that everyone aged 15 and over uses the internet. Stage 4 here, 80 per cent, is read from the first and stage 5, 95 per cent, from the other two; the lower lines are Corpus's own.

## 5. What the run reads

- **Carried, nothing opened**: the International Telecommunication Union's internet-use figures in `reference/measures.csv`, for all four questions, by a carry script written in the run on the pattern of `scripts/study-mobile-carry.py`.
- **Read**: **130 news stories about internet use that no study has read**, in 50 countries, Eritrea, South Sudan and Sudan among them. They include the national survey reports the current cells cite for Angola and Lesotho.
- **Not read**: 37 DataReportal country pages, whose figures are never used; the other stories the current cells cite, which are about networks and operators; long texts, reports and passing mentions. **No web search and no handover to OSINT.**

## 6. Token ceiling

**30 million.** The mobile-phone study, built the same way, read 28 stories and came to 12.5 million; this one reads 130, at five to a drafter, and its summaries are again written by script from the figures. The run checks after every fan-out and stops at it.

## 7. Tasks, in order

- [x] **D0. Prepare**: this file and `study.json`, 2026-10-13.
- [x] **D1. Bill's word**: run on it, 2026-10-13, with his ruling that a government press statement giving a share of people counts as a survey.
- [x] **D2. Carried and read**: 204 figures for all 54 countries from the held series; 62 drafters in one fan-out over the 130 stories. 232 facts after the parent's reading, 28 of them from stories.
- [x] **D3. Staged** as at 2026-09-30: 4: 3, 3: 17, 2: 20, 1: 11, three unplaced, none at 5; agreement 20 of 20.
- [x] **D4. Written, rendered and linted**; on the soft-launch map. **D5. Reported to Bill**, 2026-10-13.

**Decided in the run**:

- **The stories moved one country: Angola, from stage 2 to stage 3.** Its regulator gave the share of individuals who use the internet as 55.5 per cent for 2024, at an International Telecommunication Union workshop; the Union's estimate is 40.7. It is used under Bill's ruling on government statements.
- **Removed by the parent, six rows** (`corrections.csv`). Tunisia's regulator gave 85.9 per cent "of the sample" in its 2026 survey, in four records, with no sampling frame or age range: it would have put Tunisia at stage 4, and Tunisia is stage 3 on the estimate of 70. Eritrea's 26.59 per cent names no year and is for 2023 or earlier. Rwanda's 38 per cent "as of mid-2025" is not in the Union's series; Rwanda is stage 2 either way.
- **Eritrea, South Sudan and Sudan are unplaced, not *No evidence***: their figures for 2020, 2019 and 2017 are carried and set nothing. No story gave a later one.
- **Sierra Leone is stage 2 on an estimate of 25.1 and Lesotho stage 3 on 51.8.** Lesotho's regulator's survey found 58.4 per cent in 2023, a year outside the window.
- **Mauritius is stage 3 on a survey figure of 73.3 for 2024**, down from an estimate of 79.5 for 2023: a fall is a fall.
- **A regulator's "penetration rate" with no stated basis was noted and not used**, in Benin, Burundi, the Central African Republic, the Comoros and others. The Central African Republic's ministers said about 30 per cent, where the estimate is 13.8.
- **The two figures the series marks suspect, Ghana's for 2020 and 2021, were not carried.** Both are outside the window.
- **The 37 DataReportal pages were not opened**; where a story quoted DataReportal, the figure is noted.
- **The series is cited as data**, under `ref:itu-sdg-17-8-1-internet-use@2026-06-30`. **A script wrote the summaries**, `scripts/study-internet-write.py`; no writer was called.
- **Tokens: 21.0 million at the map**, ceiling 30 million, step 1 excluded: it ran in an earlier session.

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
