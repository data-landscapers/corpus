---
type: task
reader: cc
title: maturity-study-mobileaffordability.md — the fortieth maturity study: what a month of mobile data costs against income, in four questions
last_reviewed: 2026-10-13
status: run 2026-10-13 on Bill's word, with his ruling that any documented figure counts equally; staged as at 2026-09-30, written, rendered and on the soft-launch map; waits for Bill to accept
---

# Maturity study: mobileaffordability

*(Commissioned by Bill on 2026-10-13 as `infra.connect--mobile-affordability`, under `maturity/documentation/maturity-study-method.md`.)*

## 1. What is assessed

**How much of an average month's income a month of mobile data costs: a tenth, a twentieth, 2 per cent, or 1 per cent.**

**The figure** is the price of 5 GB of mobile data for a month, as a share of average monthly income (gross national income per person, divided by 12). **Any dated, documented figure counts, and none outranks another** *(Bill, 2026-10-13)*: a regulator's or government's, an operator's published tariff, a research body's, a news story's, the International Telecommunication Union's.

The study redraws `infra.connect--mobile-affordability`, which as at 2026-08-31 puts 23 countries at stage 1, ten at stage 2, eight at stage 3 and 12 at stage 4, with none at stage 5 and one unplaced. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| The price of mobile data against income | Mobile affordability: the price of mobile data against income | `infra.connect--mobile-affordability-the-price-of-mobile-data-against-income` |

Anything else the evidence names is `other`, noted and never staged: a price cut or rise that gives no price; a promotional, night-only, daily or weekly bundle; a price floor or cap set by the regulator; a ranking with no price; fixed broadband; the price of a handset; taxes on data, airtime or phones; zero-rated sites; what people say they spend.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Does a month of mobile data cost no more than 10 per cent of an average month's income? | The latest figure held, for 2024 or later, is 10 per cent or less |
| 2 | No more than 5 per cent? | That figure is 5 per cent or less |
| 3 | No more than 2 per cent? | That figure is 2 per cent or less |
| 4 | No more than 1 per cent? | That figure is 1 per cent or less |

## 3. The ladders

**The price of mobile data against income**

| Stage | Answers |
|---|---|
| 1 Absent | The latest figure, for 2024 or later, is above 10 per cent: a month of data costs more than a tenth of a month's income |
| 2 Preparing | Yes to 1: 10 per cent or less |
| 3 Establishing | Yes to 1 and 2: 5 per cent or less |
| 4 Operating | Yes to 1, 2 and 3: 2 per cent or less |
| 5 Leading | Yes to all four: 1 per cent or less |

- **A figure is either of two things**: a stated share of income for a month of mobile data, or a stated price that Corpus sets against income.
- **A price is brought to 5 GB for a month**: a 30-day plan of 5 GB or more as priced; a smaller 30-day plan, or a price per gigabyte, multiplied up to 5 GB.
- **Income is the World Bank's figure per person for the latest year held**, in the currency of the price. The run adds it to `reference/denominators.csv`.
- **The newest figure sets the stage, whatever its source.** A figure dated only to a year counts as mid-year. A rise is a rise.
- **Before anything is read, the Union's figures for 2025 place 51 countries**: stage 1 for nine, stage 2 for 16, stage 3 for 14, stage 4 for nine, and stage 5 for Algeria, Libya and Mauritius. A newer figure from a story replaces any of them.
- **Three countries start unplaced**: Eritrea holds no figure, Equatorial Guinea's latest is for 2022 and Zimbabwe's for 2023.
- **The two lower lines are 10 and 5 per cent, where the row as it stands uses 6 and 4.** On the Union's figures that moves 12 countries from stage 1 to stage 2 and six from stage 2 to stage 3.
- **The two upper lines are unchanged**: 2 per cent is the international target, and 1 per cent is half of it.
- **Stage 5 no longer asks for a second test.** The row as it stands also asks that a gigabyte cost no more than USD 10; that is dropped, so one figure sets the stage.

`study.json` holds this as one aspect, `cost`, each fact carrying its year and either `share:` and a per cent, or `price:` with its currency, amount and gigabytes, as `price:XOF:2500:5`. The ladder turns a price into a share and counts the lines the newest figure is at or under. The source is on the fact's row, not in its value.

## 4. The norm

The African Union's Digital Transformation Strategy 2020–2030 asks that access cost no more than one US cent a megabyte by 2030. It sets no share of income. The Broadband Commission's target, carried into the International Telecommunication Union's 2030 targets for universal connectivity, is that entry-level broadband cost less than 2 per cent of monthly income per person. Stage 4 here is that target; stage 5 and the lower lines are Corpus's own.

## 5. What the run reads

- **Carried, nothing opened**: the International Telecommunication Union's price figures in `reference/measures.csv`, by a carry script written in the run on the pattern of `scripts/study-internet-carry.py`.
- **Read**: **165 news stories that no study has read**, in 51 countries, all three unplaced ones among them: 54 about the price of data, and 111 more that the current cells cite for this row.
- **Not read**: long texts, reports and passing mentions. **No web search and no handover to OSINT.**

## 6. Token ceiling

**30 million.** The internet-use study read 130 stories and came to 21.0 million; this one reads 165, and its summaries are again written by script from the figures. The run checks after every fan-out and stops at it.

## 7. Tasks, in order

- [x] **D0. Prepare**: this file, `study.json` and the reading lists, 2026-10-13.
- [x] **D1. Bill's word**: run on it, 2026-10-13, with his ruling that any documented figure counts equally.
- [x] **D2. Carried and read**: income per person for 54 countries into `reference/denominators.csv`; 205 figures for 53 countries from the held series; 60 drafters in one fan-out over the 165 stories. 230 facts after the parent's reading, 25 of them from stories.
- [x] **D3. Staged** as at 2026-09-30: 5: 3, 4: 10, 3: 13, 2: 16, 1: 9, two unplaced, one without evidence; agreement 20 of 20.
- [x] **D4. Written, rendered and linted**; on the soft-launch map. **D5. Reported to Bill**, 2026-10-13.

**Decided in the run**:

- **The stories moved one country: Angola, from stage 3 to stage 4.** Africell's 7 GB 30-day plan at 5,000 kwanza, on its tariff page of October 2025, comes to 1.89 per cent; the Union's figure for 2025, from the largest operator, is 3.05.
- **A story's price sets the stage in five more countries and moves none**: Botswana (1.17, stage 4), Libya (0.68, stage 5), Sudan (5.97, stage 2), Tanzania (3.81, stage 3) and Uganda (7.5, stage 2).
- **Removed by the parent, nine rows** (`corrections.csv`), four of which would have moved a country: Morocco's 12 GB plan sold with 12 hours of calls (to stage 3); Mozambique's 2.67 per cent for March 2026, from a World Bank project report, for a smaller basket of unstated size (to stage 3); Somalia's 220 GB bundle, Somaliland's alone (to stage 1); Tanzania's pay-as-you-go rate, paid by 0.1 per cent of users (to stage 1). A plan sold with voice is not a data plan.
- **A stated share whose basket is not given cannot be brought to 5 GB and is not used**: Mozambique's and Eswatini's two. One for a named smaller basket is multiplied up: Burkina Faso's and Eswatini's, four rows revalued, none setting a stage.
- **Of two figures for one date the dearer stands.** It decides Burkina Faso, where a 1 GB figure of 0.2 per cent for 2025 would otherwise have set stage 5 against the Union's 8.8.
- **A price is set against income only in the country's own currency or US dollars, and only where income is held for 2023 or later.** South Sudan's USD 23.70 a gigabyte is printed and sets nothing: its latest income figure is for 2015.
- **Eritrea is *No evidence*; Equatorial Guinea and Zimbabwe are unplaced** on figures for 2022 and 2023. No story gave any of the three a price.
- **The series is cited as data**, under `ref:itu-price-basket-5gb-gni@2025-12-10`; the World Bank's income figures are named and not linked, being no held record. **A script wrote the summaries**, `scripts/study-affordability-write.py`; no writer was called.
- **Tokens: 22.5 million at the map**, ceiling 30 million, step 1 included.

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
