---
type: task
reader: cc
title: maturity-study-mobileaffordability.md — the fortieth maturity study: what a month of mobile data costs against income, in four questions
last_reviewed: 2026-10-13
status: prepared 2026-10-13; waits for Bill's word on the questions
---

# Maturity study: mobileaffordability

*(Commissioned by Bill on 2026-10-13 as `infra.connect--mobile-affordability`, under `maturity/documentation/maturity-study-method.md`.)*

## 1. What is assessed

**How much of an average month's income a month of mobile data costs: a tenth, a twentieth, 2 per cent, or 1 per cent.**

**The figure** is the price of the cheapest 30-day plan of at least 5 GB from the country's largest operator, as a share of average monthly income (gross national income per person, divided by 12), as the International Telecommunication Union publishes it for each country each year.

The study redraws `infra.connect--mobile-affordability`, which as at 2026-08-31 puts 23 countries at stage 1, ten at stage 2, eight at stage 3 and 12 at stage 4, with none at stage 5 and one unplaced. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| The price of mobile data against income | Mobile affordability: the price of mobile data against income | `infra.connect--mobile-affordability-the-price-of-mobile-data-against-income` |

Anything else the evidence names is `other`, noted and never staged: a price per gigabyte, in any currency; an operator's tariff, price cut or price rise; a price floor or cap set by the regulator; the Union's older 2 GB basket, which is a different basket; another body's ranking or price comparison; the price of a handset; taxes on data, airtime or phones; zero-rated sites; what people say they spend.

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

- **The figures Corpus already holds answer all four questions for 51 countries before anything is read**, each on a figure for 2025: stage 1 for nine, stage 2 for 16, stage 3 for 14, stage 4 for nine, and stage 5 for Algeria, Libya and Mauritius.
- **Three countries have no figure in the window**: Eritrea has none at all, Equatorial Guinea's latest is for 2022 and Zimbabwe's for 2023. They are unplaced unless a story read in the run gives one.
- **The two lower lines are 10 and 5 per cent, where the row as it stands uses 6 and 4.** On the held figures that moves 12 countries from stage 1 to stage 2 and six from stage 2 to stage 3. Kept at 6 and 4, the count would be 21, ten, eight, nine and three.
- **The two upper lines are unchanged**: 2 per cent is the international target, and 1 per cent is half of it.
- **Stage 5 no longer asks for a second test.** The row as it stands also asks that a gigabyte cost no more than USD 10; that is dropped, so one figure sets the stage.
- **A figure the Union did not publish is used only where a government or regulator states it for the same plan**: at least 5 GB, 30 days, as a share of income per person, with its year. Nothing is worked out from a tariff by Corpus.
- **A rise is a rise**: the latest figure sets the stage, whatever an earlier one said.
- **A price per gigabyte, a tariff change and a price floor are noted and never used**, even for a country with nothing else.

`study.json` holds this as one aspect, `share`, each fact carrying `basket:` for the Union's figure or `statement:` for a government's, its per cent and its year; the ladder counts the lines the latest figure is at or under.

## 4. The norm

The African Union's Digital Transformation Strategy 2020–2030 asks that access cost no more than one US cent a megabyte by 2030. It sets no share of income. The Broadband Commission's target, carried into the International Telecommunication Union's 2030 targets for universal connectivity, is that entry-level broadband cost less than 2 per cent of monthly income per person. Stage 4 here is that target; stage 5 and the lower lines are Corpus's own.

## 5. What the run reads

- **Carried, nothing opened**: the International Telecommunication Union's price figures in `reference/measures.csv`, for all four questions, by a carry script written in the run on the pattern of `scripts/study-internet-carry.py`.
- **Read**: **54 news stories about the price of data that no study has read**, in 30 countries, Eritrea and Zimbabwe among them. None covers Equatorial Guinea.
- **Not read**: long texts, reports and passing mentions. **No web search and no handover to OSINT.**

## 6. Token ceiling

**25 million.** The mobile-phone study read 28 stories and came to 12.5 million, the internet-use study 130 and 21.0 million; this one reads 54, and its summaries are again written by script from the figures. The run checks after every fan-out and stops at it.

## 7. Tasks, in order

- [x] **D0. Prepare**: this file, `study.json` and the reading lists, 2026-10-13.
- [ ] **D1. Bill's word** on the questions.
- [ ] **D2. Carry and read**: the held series, then one fan-out of drafters over the 54 stories.
- [ ] **D3. Stage** as at 2026-09-30, the parent reading every fact that sets stage 4 or 5; agreement on 20 cells.
- [ ] **D4. Write, render and lint**; the soft-launch map. **D5. Report to Bill.**

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
