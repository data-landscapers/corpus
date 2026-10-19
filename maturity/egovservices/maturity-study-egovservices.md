---
type: task
reader: cc
title: maturity-study-egovservices.md — government services people can use online, in four questions
last_reviewed: 2026-10-16
status: first pass run 2026-10-16; staged, written and on the soft-launch map; waits for Bill's acceptance
---

# Maturity study: egovservices

*(Commissioned by Bill on 2026-10-16 as `dpi.govtech--e-government-services`, a first pass under `maturity/documentation/first-pass-batch.md`, in one batch with agrisatellite, metsatellite, digitalsovereignty, healthmis, educationmis, egovservices and ruralelectrification: the chapter the last seven indicators.)*

## 1. What is assessed

**Government services people can use online**: services that a citizen or business can apply for, pay for or receive through a government portal or app, and the gateway that brings them together. What lets people complete a government transaction online counts, whatever it is called.

The study redraws `dpi.govtech--e-government-services`, which as at 2026-08-31 puts 18 countries at stage 3, 19 at 2 and 17 unplaced. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| Government services online | e-government services: government services online | `dpi.govtech--e-government-services` |

Anything else the evidence names is `other`, noted and never staged: a website that only gives information, a tax or customs system used only by that agency, a payments platform with no government service named, a private company's app, a consultation or complaints channel.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Are government services going online? | A source from the last three years says the government launched a services portal or app, or piloted a service that can be applied for or paid online |
| 2 | Are ten or more services online? | A source from the last three years says ten or more government services can be completed online, or gives a count of ten or more on a government portal |
| 3 | Is there a single gateway with the national ID? | A source from the last three years says one national portal or app carries services of several ministries, with sign-in by the national ID or one shared account |
| 4 | Is its use published? | A source from the last three years gives a number of users, applications or transactions through the national portal |

## 3. The ladders

**Government services online**

| Stage | Answers |
|---|---|
| 1 Absent | A source from the past three years says no government service is available online. |
| 2 Going online | Yes to 1 |
| 3 Ten or more | Yes to 2 |
| 4 Single gateway | Yes to 3 |
| 5 Use published | Yes to 4 |

A later yes answers the earlier ones (method §3.3). `study.json` holds this as three aspects: `services` (`inservice`, `underway`, `none`) for stage 1 and questions 1 and 2, `gateway` (`single`) for 3 and `usage` (`published`) for 4.

## 4. The norm

The Digital Transformation Strategy asks for a single digital gateway carrying government services to citizens, businesses and government; the AU Public Service Charter asks for modern technologies in service delivery. This study asks the four questions above; it does not measure a country against the norm.

## 5. What the run reads

- **Carried**: nothing; no earlier study holds facts on these questions.
- **Read**: **249 story readings about the subject**, published since October 2023, in at most 20 stories a country: 3 in the batch's shared calls (8 calls over 36 stories), read once for every study that lists them, and 246 in 72 calls of its own. A story published before the three-year window can set no stage, and the twenty are each country's best ranked across the batch (`study-calls.py --batch … --cap 20`).
- **Not read**: the rest of the 3,884 documents this study lists, instruments, long reports, passing mentions and the documents the row's current cells cite. A question nothing answers is printed as *Not held*.

## 6. Token ceiling

**12 million** for this study; **75 million** for the batch, checked with `study-tokens.py` after every fan-out.

## 7. Tasks, in order

- [x] **D0. Prepared**: this file, `study.json` and the reading lists, 2026-10-16.
- [x] **D1. Read**, 2026-10-16: Sonnet drafters, self-contained calls; corrections in `corrections.csv`.
- [x] **D2. Staged** as at 2026-09-30: 2 at 5, 4 at 4, 11 at 3, 16 at 2; unplaced 3, no evidence 18. Every cell is a first pass; no second drafter.
- [x] **D3. Written, rendered and linted**; on the soft-launch map. Reported to Bill.

**Decided in the run**: Removed at the top-stage check: BEN-006, requests to the land agency's own service, not the national portal; MOZ-006, a portal not yet launched.

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
