---
type: task
reader: cc
title: maturity-study-coresystems.md — the fifty-first maturity study: whether the state's core computer systems are in use and kept current, in four questions
last_reviewed: 2026-10-14
status: run 2026-10-14; on the soft-launch map; waits for Bill to accept
---

# Maturity study: coresystems

*(Commissioned by Bill on 2026-10-14 as `infra.capacity--robustness-of-government-hardware-and-software`, under `maturity/documentation/maturity-study-method.md`.)*

## 1. What is assessed

**The computer systems central government runs its money and its staff on: the one that budgets, accounts and pays; the one that collects tax; and the one that pays civil servants.**

Each counts by what it does, whatever it is called: an IFMIS, SIGFiP or e-SISTAFE for the money; the tax authority's own system for tax; an HRMIS, IPPIS or payroll system for staff. A system that does two of these counts for both.

The study redraws `infra.capacity--robustness-of-government-hardware-and-software`, which as at 2026-08-31 puts 24 countries at stage 2 and Angola and Cabo Verde at stage 3, leaves 26 unplaced, and holds no cell for Congo or Togo. It touches no other row: the government data centre stays with `infra.store--local-data-centre-capacity-national-providers`, back-up with `infra.store--off-site-backup-capacity`, and the people who run the systems with `infra.capacity--local-capacity-to-maintain-manage-and-develop-government-systems`.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| Core government systems | Robustness of government hardware and software: core government systems | `infra.capacity--robustness-of-government-hardware-and-software-core-government-systems` |

Anything else the evidence names is `other`, noted and never staged: a system bought, tendered or piloted but not in use; one ministry's or one region's system; customs (ASYCUDA and the like); a portal, a payment gateway or an ID system; a cyber attack that did not take a core system down.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Does government budget, account and pay through a computer system? | A source from 2023 or later states the financial management system is in use across central government |
| 2 | Are tax and the civil-service payroll run on computer systems too? | Sources from 2023 or later state both are in use |
| 3 | Has one of the three gone live on a new or upgraded system in the last three years? | A source states one went live, replacing or upgrading the old, in October 2023 or later |
| 4 | Has the government published a map of its systems? | A source states an enterprise architecture or an inventory of government systems was published or adopted |

## 3. The ladders

**Core government systems**

| Stage | Answers |
|---|---|
| 1 Absent | A source from 2023 or later says the government's finances are not run on a computer system |
| 2 Preparing | Yes to 1: the money runs on a computer system |
| 3 Establishing | Yes to 2: tax and the payroll do too |
| 4 Operating | Yes to 3: one of them renewed in the last three years |
| 5 Leading | Yes to 4: a published architecture or inventory |

- **A core system out of action for a week or more in the last twelve months is not in use** until a source says it is back. Eswatini's financial system, down in a government-wide outage from 18 September 2026, is the case at the as-at. Ghana's tax payment faults of August 2026 are not: filing was unaffected and a September source says the system is working.
- **Stage 2 changes.** The row put a country whose systems were being bought or replaced at stage 2. A purchase is not a system in use, so it is `other`; the study asks what runs.
- **Stage 3 drops the custodian and the supported platform.** Whether a platform is supported is a vendor's judgement no story states. The renewal question takes its place: a system renewed in the last three years is current.
- **Stage 4 drops the government network, the data centre and the incident report**, which other rows assess or which no story states for all three systems.
- **Stage 5 keeps the Charter's end state as a fact**: a published architecture or inventory. Shared platforms and performance reporting go, as no story states them as one fact.
- **Window**: questions 1 to 3 are three years; question 4 has none, since an architecture stands until replaced.

`study.json` holds this as five aspects, which head the long summary's paragraphs: `finance`, `revenue` and `payroll` (`inuse`, `down`, `none`) for questions 1 and 2, `renewed` (`live`) for question 3 and `architecture` (`published`) for question 4. **For the drafter**: `none` needs a statement that the job is done on paper or spreadsheets; `down` a dated report that the system has stopped. A tender, a contract or a pilot is `other`, with the system's name in `country_label`.

## 4. The norm

The African Charter on the Values and Principles of Public Service and Administration, Art. 8, asks that modern technologies support service delivery; the Digital Transformation Strategy asks for mission-critical systems hosted to a standard. Neither names a system. The World Bank's GovTech Maturity Index (2025) groups countries by the same core systems and is not read.

## 5. What the run reads

- **Read**: **329 stories** in 53 countries: 148 about these systems that no study has read, in 35 countries, and 181 more that the frame's cells for the row cite, in 50. Nothing is listed for São Tomé and Príncipe, which stays *No evidence* unless a regional story names it.
- **No earlier study is carried**: none holds facts on these systems.
- **Not read**: the long texts, reports and passing mentions the listing also holds. **No web search and no handover to OSINT.**

## 6. Token ceiling

**40 million**: satellite broadband read 820 stories in 62.4 million, nationaldatacentres 194 in 40.2 million; this reads 329.

## 7. Tasks, in order

- [x] **D0. Prepare**: this file, `study.json` and the reading lists, 2026-10-14.
- [x] **D1. Bill's word**, 2026-10-14, the questions as prepared.
- [x] **D2. Read**: 120 drafters over 357 readings, 97 facts after five rows removed (`corrections.csv`).
- [x] **D3. Staged** as at 2026-09-30: stage 5 four, 4 three, 3 two, 2 eleven, unplaced eight, no evidence 26; the second drafter agreed on 20 of 20.
- [x] **D4. Written, rendered and linted**, by `study-coresystems-write.py`; on the soft-launch map. **D5. Reported to Bill.**

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
