---
type: task
reader: cc
title: maturity-study-dataexchange.md — a platform through which government systems exchange data, in four questions
last_reviewed: 2026-10-16
status: first pass run 2026-10-16; staged, written and on the soft-launch map; waits for Bill's acceptance
---

# Maturity study: dataexchange

*(Commissioned by Bill on 2026-10-16 as `dpi.exchange--national-data-exchange-system`, a first pass under `maturity/documentation/first-pass-batch.md`, in one batch with dataexchange, idverification, healthexchange, educationexchange and socialexchange.)*

## 1. What is assessed

**A platform through which government systems exchange data with each other**: a national data exchange or interoperability platform, a government service bus, an X-Road deployment, an information mediator. What carries data between two or more public bodies' systems counts, under whatever name and inside whatever programme.

The study redraws `dpi.exchange--national-data-exchange-system`, which as at 2026-08-31 puts one country at stage 4, 12 at 3, 23 at 2, three at 1 and 15 unplaced. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| National data exchange system | National data exchange system: national data exchange system | `dpi.exchange--national-data-exchange-system` |

Anything else the evidence names is `other`, noted and never staged: a framework, standard or law with no platform running (the interoperability studies hold those), a portal or e-services site for citizens, a data centre or cloud, a single ministry's internal integration, a regional platform between states, a payments switch.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Is a government data exchange platform under way? | A source from the last three years says one is procured, being built or piloted between a few systems |
| 2 | Is it in service? | A source from the last three years says the platform is live and carries data between two or more public bodies' systems |
| 3 | Does it connect many systems? | A source from the last three years counts ten or more institutions, systems or services connected to it |
| 4 | Is its use reported? | A source from the last three years gives a figure for the exchanges or transactions through it |

## 3. The ladders

**National data exchange system**

| Stage | Answers |
|---|---|
| 1 Absent | A source from the last three years says it is absent |
| 2 Under way | Yes to 1 |
| 3 In service | Yes to 2 |
| 4 Wide | Yes to 3 |
| 5 Use reported | Yes to 4 |

A later yes answers the earlier ones (method §3.3). `study.json` holds this as three aspects: `platform` (`inservice`, `underway`, `none`) for questions 1 and 2, `reach` (`wide`) for 3 and `usage` (`reported`) for 4. **For the drafter**: the system's name goes in `system`, the bodies or systems it links in the fact.

## 4. The norm

The African Union's Digital Transformation Strategy and its interoperability framework ask for a secure exchange layer through which government systems reuse each other's data and registers. This study asks the four questions above; it does not measure a country against the norm.

## 5. What the run reads

- **Carried**: nothing; no earlier study holds facts on these questions.
- **Read**: **125 news stories about the subject that no study has read**, in 41 countries; then the 176 documents the row's current cells cite, in 53 countries. 100 calls of its own, besides the batch's 19 shared calls over 84 stories read once for two studies or more.
- **Not read**: instruments, long reports and passing mentions. A question nothing answers is printed as *Not held*.

## 6. Token ceiling

**40 million** for this study; **200 million** for the batch, checked with `study-tokens.py` after every fan-out.

## 7. Tasks, in order

- [x] **D0. Prepared**: this file, `study.json` and the reading lists, 2026-10-16.
- [x] **D1. Read**, 2026-10-16: the batch's 19 shared calls and this study's own, Sonnet drafters; 165 facts after the parent's corrections (`corrections.csv`).
- [x] **D2. Staged** as at 2026-09-30: 1 at 5, 3 at 4, 11 at 3, 18 at 2, 3 at 1; unplaced 5, no evidence 13. Every cell is a first pass; no second drafter.
- [x] **D3. Written, rendered and linted**, by `study-first-write.py`; on the soft-launch map. Reported to Bill. Batch tokens 203M of 200M, the reading of all five studies.

**Decided in the run**: Zambia's revenue figures for its Government Services Bus are removed as use reported: revenue is not a count of exchanges. Benin stands at 5 on its exchange platform's published request counts.

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
