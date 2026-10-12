---
type: task
reader: cc
title: maturity-study-datagovernance.md — the eighteenth maturity study: the national data policy, in four questions
last_reviewed: 2026-10-12
status: prepared 2026-10-12; nothing run; awaiting Bill's word on the questions
---

# Maturity study: datagovernance

*(Commissioned by Bill on 2026-10-12 as `gov.policy--data-governance-policy`, under `maturity/documentation/maturity-study-method.md`.)*

## 1. What is assessed

**The government's own policy for how data is managed, shared and used across the government or the country**, whatever it is called: a national data policy, a national data strategy, a data governance policy, strategy or framework, a data management or data sharing policy for the whole government, or the data part of a larger strategy or law where a source says that part sets out those rules.

The study redraws `gov.policy--data-governance-policy`, which as at 2026-08-31 puts 22 countries at stage 2 and 11 at stage 3, none at 1, 4 or 5, and leaves the other 21 unplaced. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| National data policy | Data governance policy: national data policy | `gov.policy--data-governance-policy-national-data-policy` |

Anything else the evidence names is `other`, noted and never staged: a data protection law, an open data policy, a rule on keeping data in the country, an interoperability framework, a cloud policy, an AI strategy, a national strategy for statistics, one ministry's or one sector's data policy, a data exchange platform.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Is there a national data policy, or one being written? | A policy, strategy or framework for data: being drafted, out for consultation, or adopted. A consultant hired or a team appointed to write it counts. A stated intention with no drafting begun is not a yes |
| 2 | Has the government adopted it, and has it not run out? | Approved by cabinet, or launched or issued by the head of state, the minister or the agency responsible, and not ended, replaced or withdrawn. A policy with no end date counts |
| 3 | Has the government named a body to carry it out? | A council, office, agency, committee, chief data officer or ministry unit set up or named to carry out the policy, by an instrument or reported at work |
| 4 | Has the government issued a rule or standard the policy called for? | In the last three years: a dated source naming a law, regulation, standard or guideline issued under the policy, such as one on classifying data, on sharing data between public bodies or on publishing data |

## 3. The ladders

**National data policy**

| Stage | Answers |
|---|---|
| 1 Absent | A dated source says the country has no national data policy and none is being written |
| 2 Preparing | Yes to 1: a policy being written, or one that has run out with no successor adopted |
| 3 Establishing | Yes to 1 and 2: a policy adopted and still running |
| 4 Operating | Yes to 1, 2 and 3: a body is named to carry it out |
| 5 Leading | Yes to all four: a rule or standard the policy called for has been issued |

- **Questions 1 to 3 have no time limit**: an adopted policy stands, with its year, until its end date passes or a dated source says it has been replaced or withdrawn.
- **A statement that there is no policy counts for three years.**
- **A draft validated at a workshop, or handed to the minister, is still a draft.** Question 2 needs approval or a launch by the government. Most of what is held is a validation, so most countries will sit at stage 2.
- **A policy on sharing or managing data across the whole government counts** (Rwanda's data sharing policy, Lesotho's data management policy), as it does in the row as it stands. The summary says what it covers.
- **A policy on one matter with a row of its own does not count**: data protection, open data, keeping data in the country, cloud, interoperability, AI. Nor does a strategy for official statistics.
- **A country saying it will follow the African Union's Data Policy Framework, with no policy of its own being written, places nothing.** This is one change from the row as it stands, whose stage 2 counts it.
- **A body counts for question 3, and a rule for question 4, only where the source ties it to the policy.** A data protection authority is not the body unless a source says the policy is its job.
- **The ministry that wrote the policy being responsible for it in general is not a yes to question 3.** A body the policy says will be set up is not yet named.
- **A body set up to write the policy answers question 1, not question 3.**
- **The top stage is one rule issued, not a set.** This is the other change from the row as it stands, whose stage 4 asks for rules in two named areas and whose stage 5 is agreement with the African Union's framework.
- **A policy adopted but not yet in effect is a yes to question 2**, and the summary gives the date it starts.
- **How good the policy is, is not judged**, nor whether it follows the African Union's framework; a source saying it does is noted.
- **A policy that is part of a larger strategy or law** is named in the summary by that instrument's name; the digital strategy, cloud and data protection rows are not changed by it.

`study.json` holds this as two aspects: `standing` (`adopted`, `ended`, `draft`, `none`) for questions 1 and 2, and `use` (`issued`, `body`, `none`) for 3 and 4.

## 4. The norm

The African Union's Data Policy Framework, endorsed by the Executive Council in February 2022, asks each member state to write a national data policy, put it into its own rules and institutions, and monitor it. This study asks whether a policy exists, is adopted, has a body to carry it out and has produced a rule; it does not measure the policy's content against the framework.

## 5. What the run reads

- **Read first**: **102 news stories about a national data policy**, across 42 countries. No study has read them. 27 are one roundup read once for each country it names.
- **Then, for every country those leave short of an answer**: the news stories its current cell cites, 169 across 42 countries.
- **Then, only for a country still short of an answer to question 1 or 2**: the newest held news that names such a policy, one call a country, from at most 430 stories across 54 countries.
- **Not read**: the texts of the policies and long reports, 527 of them. A policy's text is opened only for a country with nothing else.
- **No web search and no handover to OSINT.** A question nothing answers is printed as *Not held*.

## 6. Token ceiling

**50 million.** The run checks after every fan-out and again after the writing step, and stops and reports if it reaches it. The data localisation study, with 60 stories to read first and 159 cited, spent 42.3 million against 50. This one reads 102 first, so the cited stories are read only for a country the first read leaves short, the third read is one call a country, and the parent writes the summaries. No earlier study holds facts on a national data policy, so nothing is carried.

## 7. Tasks, in order

- [x] **D0. Prepare**: this file and `study.json`, 2026-10-12.
- [ ] **D1. Bill's word** on the four questions.
- [ ] **D2. Read**, as §5.
- [ ] **D3. Stage**, as at 2026-09-30; the parent reads every fact that would set stage 4 or 5; two drafters compared on 20 countries.
- [ ] **D4. Write, render and lint**; the soft-launch map. **D5. Report to Bill**, with the tokens spent.

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
