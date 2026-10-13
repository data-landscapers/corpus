---
type: task
reader: cc
title: maturity-study-mobilepenetration.md — the thirty-eighth maturity study: people who own a mobile phone, in four questions
last_reviewed: 2026-10-13
status: run 2026-10-13 on Bill's word; staged as at 2026-09-30, written, rendered and on the soft-launch map; waits for Bill to accept
---

# Maturity study: mobilepenetration

*(Commissioned by Bill on 2026-10-13 as `infra.connect--mobile-penetration`, under `maturity/documentation/maturity-study-method.md`.)*

## 1. What is assessed

**How many of a country's people own a mobile phone: half, two in three, four in five, or nearly everyone.**

**The figure** is the share of people aged 10 and over who own a mobile phone, as the International Telecommunication Union publishes it for each country, or as a national household survey or census gives it.

The study redraws `infra.connect--mobile-penetration`, which as at 2026-08-31 puts 11 countries at stage 1, ten at stage 2, ten at stage 3, 20 at stage 4 and one at stage 5, and leaves two unplaced. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| People who own a mobile phone | Mobile penetration: people who own a mobile phone | `infra.connect--mobile-penetration-people-who-own-a-mobile-phone` |

Anything else the evidence names is `other`, noted and never staged: SIM cards or subscriptions per 100 people, which count a person once for every SIM; an operator's or the regulator's subscriber count; unique subscribers; households with a phone; a figure for adults only; smartphone ownership; network coverage; the price of a handset.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Do at least half of the people own a mobile phone? | The latest figure held, for 2024 or later, is 50 per cent or more |
| 2 | Do at least two in three? | That figure is 65 per cent or more |
| 3 | Do at least four in five? | That figure is 80 per cent or more |
| 4 | Does nearly everyone? | That figure is 95 per cent or more |

## 3. The ladders

**People who own a mobile phone**

| Stage | Answers |
|---|---|
| 1 Absent | The latest figure, for 2024 or later, is below 50 per cent: fewer than half own a phone |
| 2 Preparing | Yes to 1: at least half |
| 3 Establishing | Yes to 1 and 2: at least two in three |
| 4 Operating | Yes to 1, 2 and 3: at least four in five |
| 5 Leading | Yes to all four: nearly everyone |

- **The figures Corpus already holds answer all four questions for 51 countries before anything is read**: stage 1 for eight, stage 2 for 12, stage 3 for 16, stage 4 for 12, and stage 5 for Egypt, Morocco and Seychelles.
- **Three countries have no figure in the window**: Eritrea and South Sudan have none at all, and Sudan's is for 2016. They are *No evidence* unless a story read in the run gives one.
- **The lines are fixed, not drawn from where other countries stand.** The row as it stands divides the continent into fifths, so a country can move because its neighbours did. Here it moves only when its own figure crosses a line.
- **An estimate by the International Telecommunication Union counts.** It is the latest figure for 39 of the 51; the summary says where a figure is an estimate and not a survey.
- **A national survey or census figure for 2024 or later, where one is held, is used in place of an estimate**, and the newest survey in place of an older one.
- **A fall is a fall**: the latest figure sets the stage, whatever an earlier one said.
- **A figure for adults only, and every count of SIM cards or subscribers, is noted and never used**, even for a country with nothing else.

`study.json` holds this as one aspect, `owners`, whose value is the figure itself: `survey:53.7` for a national survey or census, `estimate:59.7` for an estimate, dated by the year the figure is for. The ladder counts the lines the latest figure clears. A fact is recorded only for a share of people, of an age range that starts at 10 or younger or of the whole population, who own a mobile phone, across the whole country; everything in §1's `other` list is a `systems` entry of class `other`, with the figure in `country_label`.

## 4. The norm

The African Union's Digital Transformation Strategy 2020–2030 asks that every person be digitally empowered by 2030, with a device costing no more than USD 100. It sets no ownership figure. The International Telecommunication Union's 2030 target for universal connectivity is that everyone aged 15 and over owns a mobile phone. The top stage here, 95 per cent, is read from those; the lower lines are Corpus's own.

## 5. What the run reads

- **Carried, nothing opened**: the International Telecommunication Union's ownership figures in `reference/measures.csv`, for all four questions, by a carry script written in the run on the pattern of `scripts/study-nonstate-carry.py`.
- **Read**: **28 news stories about phone ownership that no study has read**, in 22 countries, Eritrea and Sudan among them.
- **Not read**: the stories the current cells cite, which are about masts and networks and give no ownership figure; long texts, reports and passing mentions. **No web search and no handover to OSINT.**

## 6. Token ceiling

**25 million.** The smallest studies so far, reading 80 to 150 stories, came to 28 to 35 million, most of it the writing of 54 countries; this one reads 28. The run checks after every fan-out and stops at it.

## 7. Tasks, in order

- [x] **D0. Prepare**: this file and `study.json`, 2026-10-13.
- [x] **D1. Bill's word**: run on it, 2026-10-13.
- [x] **D2. Carried and read**: 199 figures for 52 countries from the held series; 22 drafters in one fan-out over the 28 stories. 201 facts after the parent's reading.
- [x] **D3. Staged** as at 2026-09-30: 5: 3, 4: 12, 3: 16, 2: 12, 1: 8, one unplaced, two without evidence; agreement 20 of 20.
- [x] **D4. Written, rendered and linted**; on the soft-launch map. **D5. Reported to Bill**, 2026-10-13.

**Decided in the run**:

- **The 28 stories moved no country.** Two gave a countable figure: Kenya's housing survey, the same 53.7 per cent the series holds, and Lesotho's for 2016, outside the window.
- **Removed by the parent, one row** (`corrections.csv`): Mali's 88.1 per cent for 2025, which its source describes as households with a phone. It would have put Mali at stage 4; Mali is stage 3 on the estimate of 69.2.
- **Lesotho is stage 3 on an estimate of 75.2 per cent for 2024.** Its regulator's survey found 83.1 per cent of individuals in 2023, a year outside the window and with no age range given, so it is noted and not used.
- **Sudan is unplaced, not *No evidence***: its 2016 figure is carried and sets nothing.
- **Seychelles is stage 5 on an estimate of exactly 95, Benin stage 3 on exactly 65, and Mozambique stage 3 at 79.9.** A figure on the line clears it; none is rounded up.
- **The series is cited as data.** It is no record in `raw/`, so its facts are filed under `ref:itu-sdg-5b1-mobile-ownership-10plus@2026-06-30`, as the frame cites it, and `lint-study.py` now passes a reference series as held (`study_lib.reference_held`).
- **A script wrote the summaries**, `scripts/study-mobile-write.py`: each says one figure, its kind, the years before it and the distance to the next line, which is arithmetic. No writer was called.
- **Tokens: 12.5 million at the map**, ceiling 25 million, step 1 included.

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
