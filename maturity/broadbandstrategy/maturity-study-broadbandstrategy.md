---
type: task
reader: cc
title: maturity-study-broadbandstrategy.md — the thirteenth maturity study: the national broadband plan, in four questions
last_reviewed: 2026-10-12
status: prepared 2026-10-12; nothing run; waits for Bill's word on the questions
---

# Maturity study: broadbandstrategy

*(Commissioned by Bill on 2026-10-12 as `gov.policy--broadband-strategy`, under `maturity/documentation/maturity-study-method.md`.)*

## 1. What is assessed

**The government's plan for getting broadband to the whole country, with targets for coverage, speed or price**, whatever it is called: a broadband plan, policy or strategy of its own, or the broadband part of a larger digital strategy, ICT policy or development plan where a source states its broadband targets.

The study redraws `gov.policy--broadband-strategy`, which as at 2026-08-31 puts 14 countries at stage 3, 14 at stage 2, three at stage 1 and one at stage 4, none at 5, and leaves 22 unplaced. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| National broadband plan | Broadband strategy: national plan | `gov.policy--broadband-strategy-national-plan` |

Anything else the evidence names is `other`, noted and never staged: a single fibre or tower project, an operator's rollout, a regulator's licence or pricing decision, a universal service fund with no plan behind it.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Is there a national broadband plan, or one being written? | A plan with broadband targets for the country: being drafted, out for consultation, or adopted |
| 2 | Has the government adopted it, and is it still running? | Adopted by the government or the minister responsible, and its stated period has not ended. A plan with no end date counts |
| 3 | Is money committed to it? | In the last three years: a budget line, a universal service fund allocation or a financed programme that the source ties to the plan |
| 4 | Does the government publish progress against the plan's targets? | In the last three years: a published review or report giving figures against the plan's own targets |

## 3. The ladder

**National broadband plan**

| Stage | Answers |
|---|---|
| 1 Absent | A dated source says the country has no national broadband plan and none is being written |
| 2 Preparing | Yes to 1: a plan being written, or one whose period has ended with no successor adopted |
| 3 Establishing | Yes to 1 and 2: a plan adopted and still running |
| 4 Operating | Yes to 1, 2 and 3: money is committed to the plan |
| 5 Leading | Yes to all four: the plan is funded and progress against its targets is published |

- **Questions 1 and 2 have no time limit**: an adopted plan stands, with its year, until its period ends or a dated source says it is replaced or withdrawn.
- **A statement that there is no plan counts for three years.**
- **Money counts only where the source ties it to the plan.** A financed fibre project in a country with no plan is noted and places nothing.
- **Whether the targets are met is not judged.** A published review saying the plan missed its targets is a yes to question 4, and the summary says what it found.
- **A regulator's yearly market figures are not a yes to question 4** unless they are set against the plan's targets.
- **The African Union's 2030 target is noted and does not change the stage.**
- **A plan that is part of a larger strategy** is named in the summary by the strategy's name; the digital strategy and ICT policy rows are not changed by it.

`study.json` holds this as two aspects: `standing` (`adopted`, `ended`, `draft`, `none`) for questions 1 and 2, and `delivery` (`reported`, `funded`, `none`) for 3 and 4.

## 4. The norm

The Broadband Commission's first target is a funded national broadband plan in every country by 2025, which gives questions 1 to 3. The African Union's Digital Transformation Strategy sets the 2030 outcome: universal access at 6 Mb/s or more, at no more than one US cent a megabyte. This study asks whether the plan exists, is adopted, is funded and is reported on; it does not measure the outcome.

## 5. What the run reads

- **Read first**: **14 news stories about a national broadband plan**, across 12 countries. No study has read them.
- **Then, for every country those leave short of an answer**: the news stories its current cell cites, 174 across 49 countries.
- **Then, only for a country still short of an answer to question 1 or 2**: the newest held news that names a broadband plan, at most 183 stories across 30 countries.
- **Not read**: the texts of the plans and long reports, 291 of them. A plan's text is opened only for a country with nothing else.
- **No web search and no handover to OSINT.** A question nothing answers is printed as *Not held*.

## 6. Token ceiling

**40 million.** The run stops and reports if it reaches it. No earlier study holds facts on broadband plans, so nothing is carried.

## 7. Tasks, in order

- [x] **D0. Prepare**: this file and `study.json`, 2026-10-12.
- [ ] **D1. Bill's word** on the four questions.
- [ ] **D2. Read**: `study-select.py`, then the drafters, in the order of §5.
- [ ] **D3. Stage**: `study-ladder-broadbandstrategy.py`, the parent's reading of every fact that sets stage 4 or 5, and the agreement check.
- [ ] **D4. Write, render and lint**; the soft-launch map. **D5. Report to Bill.**

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
