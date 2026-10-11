---
type: task
reader: cc
title: maturity-study-dataprotectionreadiness.md — the eleventh maturity study: national data protection readiness, the ability to act
last_reviewed: 2026-10-11
status: run on Bill's word of 2026-10-11; staged, written and on the soft-launch map as at 2026-09-30; awaiting Bill's acceptance
---

# Maturity study: dataprotectionreadiness

*(Commissioned by Bill on 2026-10-11, under `maturity/documentation/maturity-study-method.md`.)*

## 1. What is assessed

**Whether the country is able to act on data protection** *(Bill, 2026-10-11)*: a law in force, a commitment or a body behind it, and then evidence that the law is being implemented and the authority is acting. Ratifying the Malabo Convention counts at stage 3 and is never needed for stage 4 or 5.

The study redraws `gov.protect--national-data-protection-readiness`, which as at 2026-08-31 puts 25 countries at stage 3, one at 4, two at 2, one at 1, and leaves 25 unplaced. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| Data protection system | National data protection readiness: data protection system | `gov.protect--national-data-protection-readiness-data-protection-system` |

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Is a data protection law in force? | A law in force, including one whose compliance period is still running. A bill, or a law passed and not yet commenced, is not a yes |
| 2 | Has the country ratified the Malabo Convention, or appointed an authority? | Either: the African Union's list shows it has ratified or acceded, signing alone not counting; or the authority's head or members are appointed, or an existing body given the job is doing it |
| 3 | Is the law being implemented, in the last three years? | A dated source shows the authority registering organisations, taking breach reports, issuing guidance or inspecting |
| 4 | Is the authority acting, in the last three years? | A dated decision, fine or order of the authority against a named organisation, or the authority's own published count of them for a recent period. A court's judgment is not a yes |

## 3. The ladders

**Data protection system**

| Stage | Answers |
|---|---|
| 1 Absent | A dated source shows no data protection law is in force: there is none, or it is still a bill or not yet commenced |
| 2 Preparing | A law is in force |
| 3 Establishing | A law is in force, and the country has ratified the Malabo Convention or appointed an authority |
| 4 Operating | The law is being implemented: the authority registers organisations, takes breach reports, issues guidance or inspects |
| 5 Leading | The authority is acting: it has ruled against a named organisation, or publishes a count of its rulings |

- **A yes to a later question answers the earlier ones**: an authority at work shows a law in force and a body appointed.
- **Ratification alone, with no law in force, is stage 1**, and the summary says the country has ratified.
- **Questions 1 and 2 have no time limit**; a yes stands, with its year, until a dated source reverses it.
- **Questions 1, 2 and 4 take the answers the law study and the authority study reached**, so the three rows cannot disagree.

`study.json` holds this as four aspects: `law`, `treaty`, `authority` and `practice`.

## 4. The norm

The African Union's Data Policy Framework, endorsed by the Executive Council in February 2022, asks each member state for a law, an independent authority and working practice, and asks it to ratify the Malabo Convention. It sets the parts and no measure of them. This study puts the ability to act above ratification.

## 5. What the run reads

- **Carried, no document opened**: the law study's facts on whether the law is in force and on the authority's activity, and the authority study's facts on appointment and rulings.
- **Read**: **45 documents that neither study has read.** Two of them, the African Union's list of ratifications of 2 February 2026 and a report of 19 September 2026, settle ratification for every country and are read once, not once per country.
- **No web search and no handover to OSINT.** A question nothing answers is printed as *Not held*.

## 6. Token ceiling

**25 million.** The run stops and reports if it reaches it. The authority study took 35 million, including building the scripts this one reuses.

## 7. Tasks, in order

- [x] **D0. Prepare**: this file and `study.json`, 2026-10-11.
- [x] **D1. Bill's word**: the ladder redrawn on the ability to act and run on his word, 2026-10-11.
- [x] **D2. Carried and read**: 810 facts carried from the two studies, the ratification list read once for all 54, 72 further listings read in 41 calls.
- [x] **D3. Staged**: 13 at stage 5, 15 at 4, 8 at 3, 4 at 2, 13 at 1, one with no evidence, as at 2026-09-30; one correction; agreement 18 of 20, the two splits on whether a published count is a ruling, which question 4 now states.
- [x] **D4. Written, rendered and linted**; on the soft-launch map. **D5. Reported to Bill**, 2026-10-11.

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
