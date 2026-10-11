---
type: task
reader: cc
title: maturity-study-dataprotectionreadiness.md — the eleventh maturity study: national data protection readiness, in four questions
last_reviewed: 2026-10-11
status: prepared; awaiting Bill's word on the four questions (method step 2); not run
---

# Maturity study: dataprotectionreadiness

*(Commissioned by Bill on 2026-10-11, under `maturity/documentation/maturity-study-method.md`.)*

## 1. What is assessed

**Whether the country's data protection system is in place and in use**: the law, the authority, the authority's day-to-day work with organisations, and the African Union convention.

The study redraws `gov.protect--national-data-protection-readiness`, which as at 2026-08-31 puts 25 countries at stage 3, one at 4, two at 2, one at 1, and leaves 25 unplaced. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| Data protection system | National data protection readiness: data protection system | `gov.protect--national-data-protection-readiness-data-protection-system` |

**This row sits beside the law row and the authority row and repeats neither.** Those ask how far the law is applied and whether the authority rules and reports. This asks whether the four parts exist together.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Is a data protection law in force? | A law in force, including one whose compliance period is still running. A bill, or a law passed and not yet commenced, is not a yes |
| 2 | Has an authority been appointed? | Its head or members are appointed, or an existing body given the job is doing it. An acting head counts |
| 3 | Is the authority working with organisations, in the last three years? | A dated source shows it registering organisations, taking breach reports, issuing guidance, inspecting or ruling |
| 4 | Has the country ratified the Malabo Convention? | The African Union's list, or a dated report of it, shows the country has ratified or acceded. Signing is not a yes |

## 3. The ladders

**Data protection system**

| Stage | Answers |
|---|---|
| 1 Absent | A dated source shows no data protection law is in force: there is none, or it is still a bill or not yet commenced |
| 2 Preparing | Yes to 1 |
| 3 Establishing | Yes to 1 and 2 |
| 4 Operating | Yes to 1, 2 and 3 |
| 5 Leading | Yes to all four |

- **A yes to question 3 answers 1 and 2**: an authority at work shows a law in force and a body appointed.
- **A yes to question 4 answers nothing else.** A country that has ratified and has no law in force is stage 1, and the summary says it has ratified.
- **Questions 1, 2 and 4 have no time limit**; a yes stands, with its year, until a dated source reverses it.
- **Questions 1 and 2 take the answers the law study and the authority study reached**, so the three rows cannot disagree.

`study.json` holds this as four aspects: `law`, `authority`, `practice` and `treaty`.

## 4. The norm

The African Union's Data Policy Framework, endorsed by the Executive Council in February 2022, asks each member state for a law, an independent authority and working practice, and asks it to ratify the Malabo Convention. It sets the parts and no measure of them. This study asks only whether each part is in place.

## 5. What the run reads

- **Carried, no document opened**: the law study's facts on whether the law is in force and on the authority's activity, and the authority study's facts on appointment.
- **Read**: **45 documents that neither study has read.** Two of them, the African Union's list of ratifications of 2 February 2026 and a report of 19 September 2026, settle question 4 for every country and are read once, not once per country.
- **No web search and no handover to OSINT.** A question nothing answers is printed as *Not held*.

## 6. Token ceiling

**25 million.** The run stops and reports if it reaches it. The authority study took 35 million, including building the scripts this one reuses.

## 7. Tasks, in order

- [x] **D0. Prepare**: this file and `study.json`, 2026-10-11.
- [ ] **D1. Bill's word on the four questions.**
- [ ] **D2. Carry from both studies** (`study-carry.py` must merge two studies' facts on one source), **read the ratification list once for all 54, then the remaining stories**, method §4.
- [ ] **D3. Stage all 54 countries and check agreement**, method §7.
- [ ] **D4. Write, render and lint**, method §8. **D5. Report to Bill.**

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
