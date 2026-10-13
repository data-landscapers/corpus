---
type: task
reader: cc
title: maturity-study-regionalinfrastructure.md — the twenty-ninth maturity study: digital links and facilities shared with other African countries, in four questions
last_reviewed: 2026-10-13
status: prepared 2026-10-13; waits for Bill to confirm the questions
---

# Maturity study: regionalinfrastructure

*(Commissioned by Bill on 2026-10-13 as `gov.regional--shared-regional-infrastructure`, under `maturity/documentation/maturity-study-method.md`.)*

## 1. What is assessed

**A link or facility that carries or holds digital traffic for the country and at least one other African country**, whoever owns it and whatever it is called: a fibre link across a border, a submarine cable that joins two African countries or that a landlocked country reaches through a neighbour, an internet exchange point or data centre that serves more than one country, a satellite owned or used by more than one.

The study redraws `gov.regional--shared-regional-infrastructure`, which as at 2026-08-31 puts 22 countries at stage 3, 22 at stage 2 and one at stage 1, none at 4 or 5, and leaves nine unplaced. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| Digital links and facilities shared with other African countries | Shared regional infrastructure: digital links and facilities shared with other African countries | `gov.regional--shared-regional-infrastructure-digital-links-and-facilities-shared-with-other-african-countries` |

Anything else the evidence names is `other`, noted and never staged: a roaming cut, a frequency agreement or a joint body, which the regional policy row holds; a regional payment switch or settlement system, which the cross-border payments row holds; an identity card or a police or customs system shared across borders; a link to a country outside Africa; a submarine cable landing with no other African country named; a national backbone, exchange point or data centre that no other country is reported using.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Has the country agreed in the last three years to build or join a shared link or facility with another African country? | A dated agreement, memorandum or financing agreement that names the link or facility and the other country or the regional body. Talks, a study, a bid to host or a commitment reaffirmed is not a yes |
| 2 | Has building started in the last three years? | A dated source saying a contract was awarded, works began or cable was being laid. A tender opened or money promised is not a yes |
| 3 | Is it in service? | A dated source saying the link was lit, commissioned or opened to traffic, or the facility opened to users from another country. A launch ceremony for works, or a test, is not a yes |
| 4 | Is it reported carrying another country's traffic in the last three years? | Published figures of capacity sold or traffic carried across the border; a named operator or government of the other country reported buying or using it; or a fault on it reported cutting the other country's service. An opening or a statement of capacity available is not a yes |

## 3. The ladders

**Digital links and facilities shared with other African countries**

| Stage | Answers |
|---|---|
| 1 Absent | A dated source says the country has no digital link with a neighbour, or stands outside the shared links of its region, with none on record |
| 2 Preparing | Yes to 1: agreed, and nothing more on record |
| 3 Establishing | Yes to 1 and 2: being built |
| 4 Operating | Yes to 1, 2 and 3: in service |
| 5 Leading | Yes to all four: reported carrying another country's traffic in the last three years |

- **A yes to a later question answers the earlier ones**: a link in service was agreed and built.
- **Question 3 has no time limit**; a link in service stands, with its year, until a dated source says it is cut or closed. Questions 1, 2 and 4 count for three years.
- **A statement that the country has no shared link counts for three years**, and gives way to a dated source naming one.
- **A link counts for each country a source names at its ends.** A country only named as on the route does not take the stage.
- **A landlocked country's route to a sea cable through a neighbour is a link in service** for both, where a dated source says traffic runs over it.
- **A submarine cable counts where a source says it joins the country to another African country.** A landing alone does not.
- **A company's link counts as a government's does.** What is asked is what the link does.
- **A regional programme's financing signed by the country is a yes to question 1** where the source names the cross-border link or shared facility it pays for.
- **An agreement a later dated source says is suspended or cancelled is no longer a yes.**
- **A national facility described as serving the region is not a yes to question 3** until a source names another country using it.
- **The best-placed link sets the stage**; the others are named in the summary.
- **What a link joins and what it carries is taken from what a source says of it.** How good or how dear it is, is not judged.

`study.json` holds this as two aspects: `built` (`building`, `agreed`, `none`) for questions 1 and 2, and `service` (`in-use`, `in-service`, `none`) for 3 and 4.

## 4. The norm

The African Union's Programme for Infrastructure Development in Africa and its Digital Transformation Strategy for Africa (2020 to 2030) ask member states to join their networks across borders, to give landlocked countries a route to the sea cables and to share exchange points and data centres. This study asks whether a country has agreed a shared link or facility, started building it, put it in service and has it carrying another country's traffic; it does not measure capacity or price.

## 5. What the run reads

- **Read first**: **183 news stories about cross-border links and shared facilities filed to a country**, covering 45 countries: 80 distinct stories. No study has read them.
- **Then, for every country those leave short of an answer**: the news stories its current cell cites, 180 across 53 countries. Cabo Verde has no cell.
- **Not read**: project documents, tenders, long reports and the general run of submarine cable news. **No web search and no handover to OSINT.** A question nothing answers is printed as *Not held*.

## 6. Token ceiling

**40 million.** The run checks after every fan-out and stops at it.

## 7. Tasks, in order

- [x] **D0. Prepare**: this file and `study.json`, 2026-10-13.
- [ ] **D1. Bill's word.**
- [ ] **D2. Read.**
- [ ] **D3. Stage**, as at 2026-09-30.
- [ ] **D4. Write, render and lint**; the soft-launch map. **D5. Report to Bill.**

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
