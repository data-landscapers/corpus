---
type: task
reader: cc
title: maturity-study-aistrategy.md — the sixteenth maturity study: the national AI strategy, in four questions
last_reviewed: 2026-10-12
status: run on Bill's word of 2026-10-12; staged, written and on the soft-launch map as at 2026-09-30; awaiting Bill's acceptance
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
- [x] **D1. Bill's word**: run on it, 2026-10-12.
- [x] **D2. Read**: the 411 `about` stories, in 108 calls, which used 38 of the 60 million; then, for the ten countries those left with nothing, the cited news and one call of the newest held news each. The other countries' cited news and the strategies' texts were not read. 287 facts.
- [x] **D3. Staged**: one at stage 5, seven at 4, eight at 3, 24 at 2, two at 1, 12 with no evidence, as at 2026-09-30; 35 corrections by the parent; agreement 20 of 20.
- [x] **D4. Written, rendered and linted**; on the soft-launch map. **D5. Reported to Bill**, 2026-10-12.

**Decided in the run**:

- **Money announced at a launch and not yet released is not allocated** (Ghana's US$20 million). Nor is a strategy's own costing (Kenya) or a statement that programme budgets pay for it (Egypt, Mauritius).
- **A grant scheme a public regulator runs as an action in the strategy, with its amount named, is a yes to question 4** (Zimbabwe, the one stage 5).
- **An office the strategy says will be set up is not a body named** (Ghana, Mauritius's council). **A ministry created with the strategy among its duties is the ministry responsible in general** (Benin).
- **Commissions set up to monitor the strategy's axes are a body** (Algeria), as is a cabinet committee (Kenya) or an existing institute the policy names (Ethiopia, Zambia).
- **A strategy that sources cite as existing, with no approval or launch stated, answers question 1 only** (Nigeria, Togo, Lesotho's policy of 2025).
- **A strategy validated at a workshop is a draft** (Burundi, DR Congo), and so is a draft withdrawn (South Africa).
- **A source saying a strategy is needed, planned or recommended does not say there is none** (Mali, Madagascar, Eswatini, Chad, Togo): five stage 1 claims removed.
- **A body created for a strategy still in draft lifts nothing** (Mozambique).
- **A list of countries "still developing" a strategy is a yes to question 1** (Guinea) **unless a later source contradicts it** (Mali).
- **The summaries were written by the parent, not by writers**.

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
