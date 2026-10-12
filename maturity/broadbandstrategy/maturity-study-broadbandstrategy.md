---
type: task
reader: cc
title: maturity-study-broadbandstrategy.md — the thirteenth maturity study: the national broadband plan, in four questions
last_reviewed: 2026-10-12
status: run on Bill's word of 2026-10-12; staged, written and on the soft-launch map as at 2026-09-30; awaiting Bill's acceptance
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

## 3. The ladders

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
- **A published review does not answer question 3**: it does not show that money was committed, so a country with a review and no money on record stays at stage 3.
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
- [x] **D1. Bill's word**: run on it, 2026-10-12.
- [x] **D2. Read**: the 14 `about` stories; then the cited news of 48 countries; then the newest held news for 19 still short of questions 1 and 2; then the cited plan texts of 12 with nothing else. 68 facts.
- [x] **D3. Staged**: one at stage 4, 20 at 3, eight at 2, one at 1, none at 5, one unplaced and 23 with no evidence, as at 2026-09-30; ten corrections by the parent; agreement 19 of 20.
- [x] **D4. Written, rendered and linted**; on the soft-launch map. **D5. Reported to Bill**, 2026-10-12.

**Decided in the run**:

- **A published review with no money on record stays at stage 3** (Algeria, Uganda): the second drafter read the ladder that way, and it is the lower reading.
- **A minister's figure given in an interview is not a published report** (Kenya).
- **A universal service fund's own strategy counts as the plan**, and is a draft until the government or the minister adopts it (DR Congo, Guinea-Bissau).
- **A programme launched while its strategy is still a proposal is a plan being written** (Mozambique): the one cell the second drafter read differently.
- **A 5G strategy with a national internet target counts as the plan** (Cabo Verde).
- **Nigeria is at stage 2**: its 2020 to 2025 plan has ended and no successor is adopted.

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
