---
type: task
reader: cc
title: maturity-study-aistrategy.md — the sixteenth maturity study: the national AI strategy, in four questions
last_reviewed: 2026-10-12
status: prepared 2026-10-12; nothing run; waits for Bill's word on the questions
---

# Maturity study: aistrategy

*(Commissioned by Bill on 2026-10-12 as `gov.policy--ai-strategy`, under `maturity/documentation/maturity-study-method.md`.)*

## 1. What is assessed

**The government's own plan for artificial intelligence in the country**, whatever it is called: a national AI strategy, an AI policy, an AI roadmap or action plan, or the AI part of a larger strategy where a source says that part sets out the government's aims and actions for AI.

The study redraws `gov.policy--ai-strategy`, which as at 2026-08-31 puts 26 countries at stage 2, 14 at stage 3 and six at stage 1, none at 4 or 5, and leaves eight unplaced. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| National AI strategy | AI strategy: national AI strategy | `gov.policy--ai-strategy-national-ai-strategy` |

Anything else the evidence names is `other`, noted and never staged: an AI law or regulation, an AI research centre, hub or lab, an AI readiness assessment, a company's or donor's AI project, a digital strategy that names AI as a priority.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Is there a national AI strategy, or one being written? | A strategy, policy or roadmap for AI: being drafted, out for consultation, or adopted. A task force appointed to write it counts. A stated intention with no drafting begun is not a yes |
| 2 | Has the government adopted it, and has it not run out? | Approved by cabinet, or launched or issued by the head of state, the minister or the agency responsible, and not ended, replaced or withdrawn. A strategy with no end date counts |
| 3 | Has the government named a body to carry it out? | A council, office, agency, committee or ministry unit set up or named to carry out the strategy, by an instrument or reported at work |
| 4 | Has the government put money into carrying it out? | In the last three years: a dated source naming public money allocated to the strategy, or an action in the strategy started with funding named |

## 3. The ladders

**National AI strategy**

| Stage | Answers |
|---|---|
| 1 Absent | A dated source says the country has no national AI strategy and none is being written |
| 2 Preparing | Yes to 1: a strategy being written, or one that has run out with no successor adopted |
| 3 Establishing | Yes to 1 and 2: a strategy adopted and still running |
| 4 Operating | Yes to 1, 2 and 3: a body is named to carry it out |
| 5 Leading | Yes to all four: public money has gone into carrying it out |

- **Questions 1 to 3 have no time limit**: an adopted strategy stands, with its year, until its end date passes or a dated source says it has been replaced or withdrawn.
- **A statement that there is no strategy counts for three years.**
- **AI named as a priority in a digital strategy places nothing.** The source must say the strategy's AI part sets out the government's aims and actions for AI, or that an AI strategy is being written. This is the one change from the row as it stands, whose stage 2 counts AI as a section of a digital strategy.
- **A draft validated at a workshop, or handed to the minister, is still a draft.** Question 2 needs approval or a launch by the government.
- **The ministry that wrote the strategy being responsible for it in general is not a yes to question 3.** The source must name the body or unit given the job.
- **A body counts for question 3, and money for question 4, only where the source ties it to the strategy.** An AI centre, hub or fund with no strategy behind it is noted. A donor's or company's AI project is noted.
- **A body set up to write the strategy answers question 1, not question 3.**
- **A strategy adopted but not yet in effect is a yes to question 2**, and the summary gives the date it starts.
- **How good the strategy is, is not judged.** The African Union's Continental AI Strategy, and whether a country's strategy says it follows it, is noted and does not change the stage. So is a UNESCO readiness assessment.
- **A strategy that is part of a larger strategy or law** is named in the summary by that instrument's name; the digital strategy and ICT policy rows are not changed by it.

`study.json` holds this as two aspects: `standing` (`adopted`, `ended`, `draft`, `none`) for questions 1 and 2, and `use` (`funded`, `body`, `none`) for 3 and 4.

## 4. The norm

The African Union's Continental AI Strategy, adopted in 2024, says member states must develop national AI strategies, with strategies and governance structures in its first phase to 2026. This study asks whether a strategy exists, is adopted, has a body to carry it out and has money behind it; it does not measure the strategy's content or its ethics rules.

## 5. What the run reads

- **Read first**: **411 news stories about a national AI strategy**, across 51 countries. No study has read them. Comoros, Guinea-Bissau and Niger have none.
- **Then, for every country those leave short of an answer**: the news stories its current cell cites, 132 across 48 countries.
- **Then, only for a country still short of an answer to question 1 or 2**: the newest held news that names an AI strategy, one call a country, from at most 948 stories across 54 countries.
- **Not read**: the texts of the strategies and long reports, 855 of them. A strategy's text is opened only for a country with nothing else.
- **No web search and no handover to OSINT.** A question nothing answers is printed as *Not held*.

## 6. Token ceiling

**60 million.** The run checks after every fan-out and again after the writing step, and stops and reports if it reaches it. The interoperability study, with 73 stories to read first and 143 cited, spent 45.3 million against 50. This one reads five times as many first, so the cited stories are read only for a country the first read leaves short, the third read is one call a country, and the summaries are written by the parent. No earlier study holds facts on an AI strategy, so nothing is carried.

## 7. Tasks, in order

- [x] **D0. Prepare**: this file and `study.json`, 2026-10-12.
- [ ] **D1. Bill's word** on the four questions.
- [ ] **D2. Read**: the 411 `about` stories; then the cited news; then the newest held news for a country still short of questions 1 and 2.
- [ ] **D3. Stage**: as at 2026-09-30; the parent reads every fact that sets stage 4 or 5; a second drafter restages 20 cells.
- [ ] **D4. Write, render and lint**; the soft-launch map. **D5. Report to Bill.**

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
