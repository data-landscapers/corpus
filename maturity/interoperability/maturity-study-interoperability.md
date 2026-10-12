---
type: task
reader: cc
title: maturity-study-interoperability.md — the fifteenth maturity study: the government's interoperability framework, in four questions
last_reviewed: 2026-10-12
status: run on Bill's word of 2026-10-12; staged, written and on the soft-launch map as at 2026-09-30; awaiting Bill's acceptance
---

# Maturity study: interoperability

*(Commissioned by Bill on 2026-10-12 as `gov.policy--data-interoperability-framework-roadmap`, under `maturity/documentation/maturity-study-method.md`.)*

## 1. What is assessed

**The government's common rule for how its own systems exchange data with each other**, whatever it is called: an interoperability framework, an e-GIF, a *référentiel général d'interopérabilité*, a government enterprise architecture that sets exchange standards, an interoperability decree or regulation, or a roadmap that sets the rule out.

The study redraws `gov.policy--data-interoperability-framework-roadmap`, which as at 2026-08-31 puts 31 countries at stage 2, 13 at stage 3 and one at stage 1, none at 4 or 5, and leaves nine unplaced. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| Government interoperability framework | Data interoperability framework / roadmap: government interoperability framework | `gov.policy--data-interoperability-framework-roadmap-government-interoperability-framework` |

Anything else the evidence names is `other`, noted and never staged: a data exchange platform built or planned with no framework behind it, an agreement between two agencies to share data, a framework for one sector only (health, land, spatial data), a digital strategy that names interoperability as an aim.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Is there a government interoperability framework, or one being written? | A framework, standard, regulation or roadmap for how government systems exchange data: being drafted, out for consultation, or adopted. A stated intention with no drafting begun is not a yes |
| 2 | Has the government adopted and published it? | Adopted or issued by the government, the minister or the agency responsible, and not ended, replaced or withdrawn. A framework with no end date counts |
| 3 | Are public bodies required to follow it? | A decree, law, regulation or circular that makes the framework compulsory for public bodies and names the body that enforces it |
| 4 | Are public bodies following it? | In the last three years: a dated source naming or counting ministries, agencies or systems that exchange data under the framework, or that have been certified as meeting it |

## 3. The ladders

**Government interoperability framework**

| Stage | Answers |
|---|---|
| 1 Absent | A dated source says the government has no interoperability framework and none is being written |
| 2 Preparing | Yes to 1: a framework being written, or one that has ended with no successor adopted |
| 3 Establishing | Yes to 1 and 2: a framework adopted and published |
| 4 Operating | Yes to 1, 2 and 3: public bodies are required to follow it |
| 5 Leading | Yes to all four: public bodies are following it |

- **Questions 1 to 3 have no time limit**: an adopted framework stands, with its year, until a dated source says it has ended, been replaced or withdrawn.
- **A statement that there is no framework counts for three years.**
- **An exchange platform alone places nothing.** A data exchange layer built, funded or piloted in a country with no framework on record is noted. This is one change from the row as it stands, whose stage 2 counts a platform being funded.
- **Interoperability named as an aim in a digital strategy places nothing.** The strategy must say a framework is being written, or contain the rule itself. This is the other change: the row's stage 2 counts the aim.
- **A framework adopted by decree is a yes to questions 2 and 3 together** where the source says public bodies must follow it and names the enforcing body.
- **An exchange platform counts for question 4 only where the source ties it to the framework**: bodies connected to a platform the framework governs. Agencies sharing data under an agreement of their own is noted.
- **A framework adopted but not yet in effect is a yes to question 2**, and the summary gives the date it starts.
- **How good the framework is, and whether it uses open standards, is not judged.** The African Union's interoperability framework is noted and does not change the stage.
- **A framework that is part of a larger strategy or law** is named in the summary by that instrument's name; the digital strategy and ICT policy rows are not changed by it.

`study.json` holds this as two aspects: `standing` (`adopted`, `ended`, `draft`, `none`) for questions 1 and 2, and `use` (`followed`, `required`, `none`) for 3 and 4.

## 4. The norm

The African Union's Digital Transformation Strategy asks for a framework, with implementing acts, for interoperability and levels of assurance; its Data Policy Framework asks for open data standards, and its interoperability framework for open standards with no dependence on one supplier. This study asks whether a framework exists, is adopted, is compulsory and is being followed; it does not measure the standards.

## 5. What the run reads

- **Read first**: **73 news stories about a government interoperability framework**, across 38 countries. No study has read them.
- **Then, for every country those leave short of an answer**: the news stories its current cell cites, 143 across 43 countries.
- **Then, only for a country still short of an answer to question 1 or 2**: the newest held news that names an interoperability framework, at most 500 stories across 54 countries.
- **Not read**: the texts of the frameworks and long reports, 858 of them. A framework's text is opened only for a country with nothing else.
- **No web search and no handover to OSINT.** A question nothing answers is printed as *Not held*.

## 6. Token ceiling

**50 million.** The run checks after every fan-out and again after the writing step, and stops and reports if it reaches it. The cloud study, with 29 stories to read first and 199 cited, spent 42.1 million against 50; this one starts with more unread stories and fewer cited. No earlier study holds facts on an interoperability framework, so nothing is carried.

## 7. Tasks, in order

- [x] **D0. Prepare**: this file and `study.json`, 2026-10-12.
- [x] **D1. Bill's word**: run on it, 2026-10-12.
- [x] **D2. Read**: the 73 `about` stories; then the cited news of 43 countries; then the newest held news, one call each, for the 35 countries still short of questions 1 and 2. The framework texts were opened for Cote d'Ivoire, Libya, Somalia and Gabon, which had nothing else, and for Kenya. 89 facts.
- [x] **D3. Staged**: two at stage 4, 15 at 3, 16 at 2, two at 1, none at 5, four unplaced and 15 with no evidence, as at 2026-09-30; 19 corrections by the parent; agreement 19 of 20.
- [x] **D4. Written, rendered and linted**; on the soft-launch map. **D5. Reported to Bill**, 2026-10-12.

**Decided in the run**:

- **A mandate to write a framework is not a framework being written** (Liberia's executive order, Cape Verde's minister): question 1 needs drafting begun.
- **A text that says of itself that it is compulsory is not an instrument making it so** (Zambia's standard).
- **A decree that binds public bodies but names no enforcing body is not a yes to question 3** (Cote d'Ivoire).
- **A version 0.1, or an edition with its approval left blank, is a draft** (Sao Tome and Principe, Kenya). Kenya is the one cell the second drafter read differently, and the lower reading stands.
- **An enterprise architecture handed to officials, with nothing saying it is published or sets exchange rules, is a draft** (Zimbabwe, The Gambia).
- **An exchange platform called a framework states no rule** (Namibia).
- **A source saying a framework is needed, or proposing one, does not say there is none** (Eswatini, South Africa, Libya).
- **A data sharing policy for public institutions does the job** (Rwanda), as does a government enterprise architecture in use for data exchange (Nigeria).
- **A source dated by year only as 2026 falls after the as-at and sets nothing** (Guinea's rules at version 0.2.2).
- **The third read was one call a country, not the whole listing, and the summaries were written by the parent**, to stay inside the ceiling.

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
