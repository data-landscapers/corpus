---
type: task
reader: cc
title: maturity-study-cloudstrategy.md — the fourteenth maturity study: the government's hosting and cloud policy, in four questions
last_reviewed: 2026-10-12
status: run on Bill's word of 2026-10-12; staged, written and on the soft-launch map as at 2026-09-30; awaiting Bill's acceptance
---

# Maturity study: cloudstrategy

*(Commissioned by Bill on 2026-10-12 as `gov.policy--data-storage-cloud-strategy`, under `maturity/documentation/maturity-study-method.md`.)*

## 1. What is assessed

**The government's rule on where the state's own data and systems are hosted, and on how public bodies may use cloud services**, whatever it is called: a cloud-first policy, a cloud strategy, hosting rules, a prime minister's circular, a hosting standard, or the hosting part of a larger strategy or law where a source states its rule.

The study redraws `gov.policy--data-storage-cloud-strategy`, which as at 2026-08-31 puts 35 countries at stage 2, 12 at stage 3 and two at stage 1, none at 4 or 5, and leaves five unplaced. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| Government hosting and cloud policy | Data storage / cloud strategy: hosting policy | `gov.policy--data-storage-cloud-strategy-hosting-policy` |

Anything else the evidence names is `other`, noted and never staged: a data centre or sovereign cloud built or planned with no policy behind it, an operator's commercial cloud, a rule on where private companies keep data, a data protection law.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Is there a government hosting or cloud policy, or one being written? | A policy on where state data is hosted or on public bodies' use of cloud: being drafted, out for consultation, or adopted. A stated intention with no drafting begun is not a yes |
| 2 | Has the government adopted it, and is it still in force? | Adopted or issued by the government, the minister or the regulator responsible, and not ended, replaced or withdrawn. A policy with no end date counts |
| 3 | Has the government named where public bodies must host? | A government cloud or data centre in service that the policy tells public bodies to use, or a published list of approved or accredited providers |
| 4 | Have public bodies moved onto it? | In the last three years: a dated source naming or counting ministries or agencies whose systems have moved to the named hosting under the policy |

## 3. The ladders

**Government hosting and cloud policy**

| Stage | Answers |
|---|---|
| 1 Absent | A dated source says the government has no hosting or cloud policy and none is being written |
| 2 Preparing | Yes to 1: a policy being written, or one that has ended with no successor adopted |
| 3 Establishing | Yes to 1 and 2: a policy adopted and in force |
| 4 Operating | Yes to 1, 2 and 3: the government has named where public bodies must host |
| 5 Leading | Yes to all four: public bodies have moved onto the named hosting |

- **Questions 1 to 3 have no time limit**: an adopted policy stands, with its year, until a dated source says it has ended, been replaced or withdrawn.
- **A statement that there is no policy counts for three years.**
- **A data centre or cloud alone places nothing.** A national data centre built, or a sovereign cloud announced, in a country with no policy on record is noted. This is the change from the row as it stands, whose stage 2 counts a data centre under construction.
- **A government cloud counts for question 3 only where the source ties it to the policy**, or says public bodies are required to use it.
- **A move counts for question 4 only onto the named hosting.** Agencies using a cloud service of their own choosing is noted.
- **A policy adopted but not yet in effect is a yes to question 2**, and the summary gives the date it starts.
- **How good the policy is, and whether it keeps data in the country, is not judged.** The African Union's Data Policy Framework is noted and does not change the stage.
- **A policy that is part of a larger strategy or law** is named in the summary by that instrument's name; the digital strategy, ICT policy and data protection rows are not changed by it.

`study.json` holds this as two aspects: `standing` (`adopted`, `ended`, `draft`, `none`) for questions 1 and 2, and `use` (`moved`, `named`, `none`) for 3 and 4.

## 4. The norm

The African Union's Data Policy Framework asks each state to set rules for hosting its own data, by category, and to build national or regional cloud capacity; the Digital Transformation Strategy sets a target for hosting the continent's content on the continent. This study asks whether the policy exists, is adopted, names where to host and is being followed; it does not measure the capacity or the localisation.

## 5. What the run reads

- **Read first**: **29 news stories about a government hosting or cloud policy**, across 10 countries. No study has read them.
- **Then, for every country those leave short of an answer**: the news stories its current cell cites, 199 across 44 countries.
- **Then, only for a country still short of an answer to question 1 or 2**: the newest held news that names a hosting or cloud policy, at most 322 stories across 44 countries.
- **Not read**: the texts of the policies and long reports, 381 of them. A policy's text is opened only for a country with nothing else.
- **No web search and no handover to OSINT.** A question nothing answers is printed as *Not held*.

## 6. Token ceiling

**50 million.** The run checks after every fan-out and again after the writing step, and stops and reports if it reaches it. The broadband study, a little smaller, spent 46.9 million against 40. No earlier study holds facts on hosting or cloud policy, so nothing is carried.

## 7. Tasks, in order

- [x] **D0. Prepare**: this file and `study.json`, 2026-10-12.
- [x] **D1. Bill's word**: run on it, 2026-10-12.
- [x] **D2. Read**: the 29 `about` stories; then the cited news of 44 countries; then the newest held news for 31 still short of questions 1 and 2. The policy texts were not opened, South Africa's excepted. 81 facts.
- [x] **D3. Staged**: four at stage 4, eight at 3, four at 2, one at 1, none at 5, two unplaced and 35 with no evidence, as at 2026-09-30; eleven corrections by the parent; agreement 16 of 17.
- [x] **D4. Written, rendered and linted**; on the soft-launch map. **D5. Reported to Bill**, 2026-10-12.

**Decided in the run**:

- **A head of government's instruction to host at a named place is a policy adopted** (Senegal, 2021; Burkina Faso's circular): it does the job, whatever its form.
- **A regulation that licenses commercial cloud providers is not the government's hosting policy** (Sudan, Mozambique).
- **Naming the agency that buys cloud services is not naming where to host** (South Africa, Nigeria): the one cell the second drafter read differently, and the lower reading stands.
- **A sovereign cloud provided for in another strategy, or listed in a roadmap, is not a policy** (Zimbabwe, Botswana).
- **An order to connect systems through a data centre, or a target for its use, is not a hosting rule** (Algeria, Uganda).
- **A regulator's rule on public bodies' use of foreign cloud counts** (Mauritania).
- **A source held with no web address gives no fact** (Nigeria's policy text): news of it carries the same.
- **The summaries were written by the parent, not by writers**, to stay inside the ceiling.

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
