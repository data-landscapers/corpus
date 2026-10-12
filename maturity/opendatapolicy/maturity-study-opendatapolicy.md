---
type: task
reader: cc
title: maturity-study-opendatapolicy.md — the nineteenth maturity study: the open data policy, in four questions
last_reviewed: 2026-10-12
status: prepared 2026-10-12; nothing run; waits for Bill's word on the four questions
---

# Maturity study: opendatapolicy

*(Commissioned by Bill on 2026-10-12 as `gov.policy--open-data-policy`, under `maturity/documentation/maturity-study-method.md`.)*

## 1. What is assessed

**The government's own policy that public bodies publish the data they hold for anyone to use and reuse**, whatever it is called: an open data policy, strategy, charter, decree or law, an open government data policy, or the open data part of a larger policy or law where a source says that part sets out that rule.

The study redraws `gov.policy--open-data-policy`, which as at 2026-08-31 puts 33 countries at stage 2, nine at stage 3 and five at stage 1, none at 4 or 5, and leaves seven unplaced. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| Open data policy | Open data policy: national open data policy | `gov.policy--open-data-policy-national-open-data-policy` |

Anything else the evidence names is `other`, noted and never staged: a portal with no policy behind it, a statistics office's data portal, a portal run by a donor or a development bank, an access to information law, a national data policy, one ministry's, one sector's or one city's open data policy, an open data licence, a hackathon, a commitment in an Open Government Partnership plan.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Is there an open data policy, or one being written? | A policy, strategy, decree or law on publishing government data openly: being drafted, out for consultation, or adopted. A consultant hired or a team appointed to write it counts. A stated intention with no drafting begun is not a yes |
| 2 | Has the government adopted it, and has it not run out? | Approved by cabinet, or launched or issued by the head of state, the minister or the agency responsible, and not ended, replaced or withdrawn. A policy with no end date counts |
| 3 | Is a government open data portal running under it? | A national portal the government runs, opened or reported at work, that a source ties to the policy or that the body responsible for the policy runs |
| 4 | Have public bodies published data under it? | In the last three years: a dated source naming a ministry or agency that has released data on the portal or under the policy, or counting the datasets or the bodies publishing |

## 3. The ladders

**Open data policy**

| Stage | Answers |
|---|---|
| 1 Absent | A dated source says the country has no open data policy and none is being written |
| 2 Preparing | Yes to 1: a policy being written, or one that has run out with no successor adopted |
| 3 Establishing | Yes to 1 and 2: a policy adopted and still running |
| 4 Operating | Yes to 1, 2 and 3: a government portal is running under it |
| 5 Leading | Yes to all four: public bodies have published data under it in the last three years |

- **Questions 1 to 3 have no time limit**: an adopted policy stands, with its year, until its end date passes or a dated source says it has been replaced or withdrawn.
- **A statement that there is no policy counts for three years.**
- **A draft validated at a workshop, or handed to the minister, is still a draft.**
- **A portal with no policy behind it places nothing.** This is one change from the row as it stands, whose stage 2 counts a portal or a pilot on its own. The portal is noted, and `data.open--use-of-open-data` is the row that reads what is published.
- **A statistics office's data portal is not the portal**, nor is one a development bank or a donor runs for the country, unless a source ties it to the policy.
- **The top stage is data published under the policy, not a law requiring it.** This is the other change from the row as it stands, whose stage 4 asks for a licence, a portal, a duty to publish and a custodian together, and whose stage 5 is agreement with the African Commission's declaration.
- **An access to information law is not an open data policy.** A right to ask for information is noted; a law or decree that a source says requires public bodies to publish their data openly counts.
- **A commitment in an Open Government Partnership plan to write a policy is a stated intention**, and a yes to question 1 only once drafting is reported.
- **Signing the International Open Data Charter places nothing.**
- **A policy for one ministry, one sector or one city does not count.**
- **The open data part of a national data policy or a digital strategy counts** where a source says that part sets the rule; it is named in the summary by that instrument's name, and the data governance and digital strategy rows are not changed by it.
- **A policy adopted but not yet in effect is a yes to question 2**, and the summary gives the date it starts.
- **How good the policy is, how open the licence is and how many datasets there are, are not judged.** A count is given where a source gives one.

`study.json` holds this as two aspects: `standing` (`adopted`, `ended`, `draft`, `none`) for questions 1 and 2, and `use` (`published`, `portal`, `none`) for 3 and 4.

## 4. The norm

The African Commission on Human and Peoples' Rights' Declaration of Principles on Freedom of Expression and Access to Information in Africa, adopted in November 2019, asks public bodies to publish information of public interest without being asked, including by digital means (Principle 29). The African Union's Data Policy Framework, of 2022, asks states to open government data. This study asks whether a policy exists, is adopted, has a portal and has data published under it; it does not measure the policy against either.

## 5. What the run reads

- **Read first**: **49 news stories about an open data policy or portal**, across 33 countries. None has been read for this subject; 22 were opened by an earlier study for another.
- **Then, for every country those leave short of an answer**: the news stories its current cell cites, 108 across 47 countries.
- **Then, only for a country still short of an answer to question 1 or 2**: the newest held news that names such a policy or portal, one call a country, from at most 137 stories across 38 countries.
- **Not read**: the texts of the policies and long reports, 581 of them. A policy's text is opened only for a country with nothing else.
- **No web search and no handover to OSINT.** A question nothing answers is printed as *Not held*.

## 6. Token ceiling

**50 million.** The run checks after every fan-out and again after the writing step, and stops and reports if it reaches it. The reading is smaller than the data governance study's, which spent 43.2 million against 50; the third read is one call a country and the parent writes the summaries. Earlier studies hold the names of open data policies and portals but no fact that answers these questions, so nothing is carried.

## 7. Tasks, in order

- [x] **D0. Prepare**: this file and `study.json`, 2026-10-12.
- [ ] **D1. Bill's word** on the four questions.
- [ ] **D2. Read**, in the order of §5.
- [ ] **D3. Stage**: as at 2026-09-30; the parent reads every fact that would set stage 4 or 5; two drafters compared on 20 cells.
- [ ] **D4. Write, render and lint**; the soft-launch map. **D5. Report to Bill.**

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
