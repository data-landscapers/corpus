---
type: task
reader: cc
title: maturity-study-statisticsstrategy.md — the national strategy for the development of statistics, in four questions
last_reviewed: 2026-10-15
status: prepared 2026-10-15; waits for Bill's word on the questions
---

# Maturity study: statisticsstrategy

*(Commissioned by Bill on 2026-10-15 as `data.statistics--national-strategy-for-development-of-statistics`, under `maturity/documentation/maturity-study-method.md`.)*

## 1. What is assessed

**The country's plan for its whole statistical system over several years**, whatever it is called: a national strategy for the development of statistics (NSDS, SNDS, ENDE), a statistical master plan, a plan for national statistical development, a *schéma directeur de la statistique*.

The study redraws `data.statistics--national-strategy-for-development-of-statistics`, which as at 2026-08-31 puts one country at stage 4, 27 at stage 3, 15 at stage 2 and four at stage 1, and leaves seven unplaced. It touches no other row: the statistics law stays with `gov.legislate--statistics-legislation` and its study.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| Statistics strategy | National strategy for development of statistics: statistics strategy | `data.statistics--national-strategy-for-development-of-statistics-statistics-strategy` |

Anything else the evidence names is `other`, noted and never staged: the statistics office's own corporate plan where it does not cover the whole system, a strategy for one sector's statistics (agriculture, health, education), the statistics law, a census or survey, a donor project, the regional strategy (SHaSA) and the African Charter on Statistics.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Is a national statistics strategy being prepared, or has one been adopted? | A source from the last three years states a strategy is being designed, drafted, validated or put to cabinet, or that one was adopted or launched. A strategy only promised is not a yes |
| 2 | Is an adopted strategy current? | A strategy adopted or launched whose stated period includes the as-at date |
| 3 | Has progress on it been reviewed in the last three years? | A dated annual review, progress report, or meeting of its steering body on how it is being carried out |
| 4 | Has it been evaluated? | A mid-term or final evaluation of the current strategy, completed, in the last three years |

## 3. The ladders

**Statistics strategy**

| Stage | Answers |
|---|---|
| 1 Absent | A source from the last three years says the country has no current strategy and none in preparation |
| 2 Preparing | Yes to 1 only: a strategy in preparation |
| 3 Adopted | Yes to 2: a current strategy |
| 4 Reviewed | Yes to 3: its progress reviewed |
| 5 Evaluated | Yes to 4: an evaluation completed |

- **A later yes answers the earlier ones**: a review of a strategy shows it was adopted.
- **A strategy counts for its stated period.** One with no stated period counts for five years from adoption. A successor in preparation after one expires is stage 2.
- **An expired strategy with nothing after it is not stage 1** unless a source says so; the cell is unplaced and the summary gives the year it ended. That moves DR Congo, Ethiopia, Libya and Mauritius off stage 1 unless a source states the absence.
- **The final evaluation of the strategy just ended counts for its successor** only where the successor is current; otherwise it is noted.
- **Changes from the row as it stands.** Stage 4 asked for a costed plan, funding and a monitoring report together, and stage 5 for alignment with SHaSA and the Charter ratified. Costing needs the strategy's text read, and alignment is a statement of intent, so both go; the review and the evaluation are the two facts a notice states. Tanzania's stage 4 rests on a steering committee review and holds.

`study.json` holds this as three aspects: `standing` (`adopted`, `preparing`, `none`) for questions 1 and 2, `review` (`reviewed`) for 3 and `evaluation` (`evaluated`) for 4. **For the drafter**: the strategy's period goes in `country_label` (e.g. *SNDS 2021-2025*).

## 4. The norm

The African Charter on Statistics (2009) and the Strategy for the Harmonisation of Statistics in Africa (SHaSA 2) ask each country to design, carry out and evaluate a national strategy for the development of statistics. PARIS21's yearly NSDS status table, where held, is read like any other dated source.

## 5. What the run reads

- **Read**: **65 news stories about a national statistics strategy that no study has read**, in 34 countries, one of them regional and read once; then the 80 news stories and 52 documents that the row's current cells cite, in 51 countries. 97 drafters.
- **No earlier study is carried**: the statistics law study noted strategies as `other` and holds no answer to these questions.
- **Not read**: the strategies' own texts beyond those the cells cite, reports and passing mentions. **No web search and no handover to OSINT.** A question nothing answers is printed as *Not held*.

## 6. Token ceiling

**35 million**: statistics law read through 80 calls for 37 million; this plans 97, mostly short news.

## 7. Tasks, in order

- [x] **D0. Prepare**: this file, `study.json` and the reading lists, 2026-10-15.
- [ ] **D1. Bill's word** on the questions.
- [ ] **D2. Read**: the 97 calls, one workflow; carried, merged and profiled.
- [ ] **D3. Stage** as at 2026-09-30 with `study-ladder-statisticsstrategy.py`; the parent reads every stage 4 and 5 fact; second drafter on 20 cells.
- [ ] **D4. Write, render and lint**; soft-launch map. **D5. Report to Bill.**

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
