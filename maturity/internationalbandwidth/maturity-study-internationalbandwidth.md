---
type: task
reader: cc
title: maturity-study-internationalbandwidth.md — the forty-second maturity study: fibre routes to the rest of the world, in four questions
last_reviewed: 2026-10-14
status: prepared 2026-10-14; waits for Bill's word on the questions
---

# Maturity study: internationalbandwidth

*(Commissioned by Bill on 2026-10-14 as `infra.connect--international-internet-bandwidth`, under `maturity/documentation/maturity-study-method.md`.)*

## 1. What is assessed

**Fibre that carries the country's internet traffic abroad**, whoever owns it and whatever it is called: a submarine cable landing in the country, or for any country a fibre link to a neighbour's network that its international traffic runs over.

The study redraws `infra.connect--international-internet-bandwidth`, which as at 2026-08-31 puts seven countries at stage 4, eight at stage 3, three at stage 2 and Eritrea at stage 1, none at stage 5, leaves Angola, the Gambia, Seychelles and Uganda unplaced and 31 countries without evidence. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| Fibre routes to the rest of the world | International internet bandwidth: fibre routes to the rest of the world | `infra.connect--international-internet-bandwidth-fibre-routes-to-the-rest-of-the-world` |

Anything else the evidence names is `other`, noted and never staged: satellite and microwave links; a cable that passes the country without landing; a cable announced, financed or being laid but not in service; the national backbone inland, which `fibrebackbone` assesses; data centres and exchange points; bandwidth in gigabits, which is reported in the long summary and sets nothing.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Is the country joined to the rest of the world by fibre? | A source states that a submarine cable lands in the country and is in service, or that the country's international traffic runs over fibre to a neighbour |
| 2 | Does it have two or more such routes? | Two routes, each stated in service, on one source or two |
| 3 | Are two of them independent of each other? | Two routes stated landing at different stations, or for a country without a coast, running through two different neighbours |
| 4 | Is capacity on them sold to other operators? | A source states that operators other than the owner buy capacity at the landing station or on the cable, or that it runs on open-access or regulated wholesale terms |

## 3. The ladder

**Fibre routes to the rest of the world**

| Stage | Answers |
|---|---|
| 1 Absent | A source from the past three years says the country has no international fibre route: satellite or microwave only |
| 2 Preparing | Yes to 1: one route |
| 3 Establishing | Yes to 2: two or more routes, sharing one landing station or one neighbour |
| 4 Operating | Yes to 3: two independent routes, the minimum the African Union sets |
| 5 Leading | Yes to 4: two independent routes, and capacity sold to other operators |

- **No question has a window.** A route in service stays in service until a later source says it is cut or closed; a cut that is repaired is still in service.
- **A route counts for the country it lands in, or whose traffic a source says it carries.** A cable that passes offshore does not count.
- **Question 4 needs question 3.** Open access on routes that are not independent is noted and leaves the country at stage 3.
- **Stages 1 to 4 are the row as it stands.** Stage 5 asked for bandwidth per internet user in Africa's top fifth; Corpus holds that figure for no country, so no country could reach it. Capacity sold to other operators replaces it: the African Union asks for infrastructure to be shared, and a story states it.

`study.json` holds this as two aspects: `routes` (`independent`, `two`, `one`, `none`) for questions 1 to 3, and `access` (`open`, `none`) for question 4.

## 4. The norm

The African Union's Digital Transformation Strategy 2020–2030 asks every member state for at least two international connections, and asks operators to share infrastructure. This study asks whether a country has a fibre route abroad, has two, has two that do not share a point of failure, and sells their capacity to other operators; it does not measure bandwidth or price.

## 5. What the run reads

- **Read**: **847 news readings**, in all 54 countries: 778 about the routes, which are 361 stories, a regional cable story being read once for each country it names, and 69 more that the current cells cite for this row. 127 of the 778 were read by `fibrebackbone` or `regionalinfrastructure` for their own questions, and are read again for these.
- **Not read**: long texts, reports and passing mentions. **No web search and no handover to OSINT.**

## 6. Token ceiling

**70 million.** The fibre backbone study read 388 stories and came to 40 million with its summaries written by a script; this one reads 847. The run checks after every fan-out and stops at it.

## 7. Tasks, in order

- [x] **D0. Prepare**: this file, `study.json` and the reading lists, 2026-10-14.
- [ ] **D1. Bill's word** on the questions.
- [ ] **D2. Read**: one fan-out of drafters over the 847 readings.
- [ ] **D3. Stage** as at 2026-09-30, the parent reading every fact that sets stage 4 or 5; agreement on 20 cells.
- [ ] **D4. Write, render and lint**; the soft-launch map. **D5. Report to Bill.**

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
