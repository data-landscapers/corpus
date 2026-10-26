---
type: task
reader: cc
title: maturity-study-itcapacity.md — the fifty-second maturity study: whether government's own staff build and run its computer systems, in four questions
last_reviewed: 2026-10-26
status: run 2026-10-14; on the soft-launch map; waits for Bill to accept
---

# Maturity study: itcapacity

*(Commissioned by Bill on 2026-10-14 as `infra.capacity--local-capacity-to-maintain-manage-and-develop-government-systems`, under `maturity/documentation/maturity-study-method.md`.)*

## 1. What is assessed

**Government's own technical staff building, running and maintaining its computer systems, rather than suppliers doing it for them.**

Who counts is whoever does the job on the state's payroll, whatever they are called: a ministry's IT directorate, a national IT agency, or a state company that builds and runs systems for government (Gabon's ANINF, Cabo Verde's NOSi, South Africa's SITA).

The study redraws `infra.capacity--local-capacity-to-maintain-manage-and-develop-government-systems`, which as at 2026-08-31 puts 15 countries at stage 3 and 28 at stage 2 and leaves 11 unplaced. It touches no other row: whether the core systems are in use stays with `infra.capacity--robustness-of-government-hardware-and-software`, the government data centre with `infra.store--local-data-centre-capacity-national-providers`, and the cyber response team with `infra.cybersec--national-cybersecurity-readiness`.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| In-house capacity | Local capacity to maintain, manage and develop government systems: in-house capacity | `infra.capacity--local-capacity-to-maintain-manage-and-develop-government-systems` |

Anything else the evidence names is `other`, noted and never staged: a training course, workshop or digital-skills school; skills for citizens or young people; a recruitment advertisement with no appointment; a donor project unit or consultants; a system built by a contractor; a regulator; a capacity programme announced but not running.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Do government staff run or maintain any of its computer systems? | A source from 2023 or later states a government body's own technical staff run, maintain or support a named system |
| 2 | Does a government technology body build or run systems for the rest of government? | A source from 2023 or later states a government agency or state company builds, hosts or runs systems for ministries |
| 3 | Has a government team built a system that went live in the last three years? | A source states a system built by government staff, not a contractor, went live in October 2023 or later |
| 4 | Do government staff wholly run three or more of its systems? | Sources from the last three years name three or more systems that government staff run, maintain or built, with no contractor named doing the work |

## 3. The ladders

**In-house capacity**

| Stage | Answers |
|---|---|
| 1 Absent | A source from 2023 or later says the government's systems are run by outside suppliers, or that its bodies need outside technical help to run them |
| 2 Preparing | Yes to 1: government staff run a system |
| 3 Establishing | Yes to 2: a government technology body serves the rest of government |
| 4 Operating | Yes to 3: a system built in-house went live in the last three years |
| 5 Leading | Yes to 4: three or more systems run wholly by government staff |

- **Stage 2 changes.** The row put a training exercise, a programme announced or a body needing technical help at stage 2. Training says nothing of who runs the systems, so it is `other`; a body needing help is stage 1.
- **Stage 3 changes.** The row's "in-house teams on some systems" becomes question 1. Its place is taken by a body whose job is the rest of government's systems, which is what separates one team from a capacity.
- **Stage 4 keeps the row's "systems built in-house"** as one fact a story states: a launch built by government staff. The row's cadre moves up.
- **Stage 5 is three or more systems run wholly by government staff** *(Bill, 2026-10-26, message 31)*: the cadre went, as a career structure says nothing of who runs the systems. A system counts where a source says government staff or a state technology body built it, or run and maintain it, and names no contractor doing the work; donor funding is not a contractor. A network, a data centre, a hosting service or a security team is not a system.
- **Window**: three years for every question.

`study.json` holds this as four aspects, which head the long summary's paragraphs: `inhouse` (`yes`, `outsourced`) for question 1, `agency` (`operating`) for question 2, `built` (`live`) for question 3 and `own` (`entire`) for question 4, one row per system, its name in `system`. **For the drafter**: `outsourced` needs a statement that a body's systems are run by suppliers or that it needs outside help to run them; a system's name goes in `country_label`, and who built it, where the story says, in the fact.

**Rung 5 rewritten** *(Bill, 2026-10-26)*: the 36 `own` rows were added from facts already held (`corrections.csv`); Gambia's cadre row went, and Gambia with it to no evidence.

## 4. The norm

The African Charter on the Values and Principles of Public Service and Administration, Art. 21, asks for systematic capacity development across the public service; the Digital Transformation Strategy asks for digital skills built in state institutions. Neither names a stage. The World Bank's GovTech Enablers Index is not read.

## 5. What the run reads

- **Read**: **544 stories** in all 54 countries: 363 about government's own technical capacity or its technology bodies that no study has read, in 36 countries, and 181 more that the frame's cells for the row cite, in 52. Eight of the 363 are regional, read once each.
- **No earlier study is carried**: none holds facts on who builds or runs the systems.
- **Not read**: the long texts, reports and passing mentions the listing also holds.

## 6. Token ceiling

**50 million**: coresystems read 357 stories in 120 drafters and 39.4 million; this plans 150 drafters.

## 7. Tasks, in order

- [x] **D0. Prepare**: this file, `study.json` and the reading lists, 2026-10-14.
- [x] **D1. Bill's word**, 2026-10-14, the questions as prepared.
- [x] **D2. Read**: 150 drafters over 544 readings, seven regional stories read once; 197 facts after five rows removed and one added by the parent (`corrections.csv`): two pilots, a Nigeria row that does not say who built the portal, and Equatorial Guinea's telecom operator out; Zambia's SMART Office, built in-house and in use at the Ministry of Health from June 2025, in as a go-live. Mauritius's "ICTA" is its telecom regulator, so the term brought regulator news; Kenya's and Rwanda's stories name their agencies without saying what they run. All three are *No evidence*, for the update's search.
- [x] **D3. Staged** as at 2026-09-30: stage 4 seven, 3 fourteen, 2 four, 1 two, unplaced five, no evidence 22; none at 5, no source held stating an IT cadre. The second drafter agreed on 20 of 20 after the Zambia row.
- [x] **D4. Written, rendered and linted**, by `study-itcapacity-write.py`; on the soft-launch map. **D5. Reported to Bill.** Tokens 51.2M of 50M, step 1's thread counted.

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
