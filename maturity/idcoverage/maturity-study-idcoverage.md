---
type: task
reader: cc
title: maturity-study-idcoverage.md — how much of the population holds a national ID, in four questions
last_reviewed: 2026-10-16
status: first pass run 2026-10-16; staged, written and on the soft-launch map; waits for Bill's acceptance
---

# Maturity study: idcoverage

*(Commissioned by Bill on 2026-10-16 as `dpi.id--registration-of-entire-population`, a first pass under `maturity/documentation/first-pass-batch.md`, in one batch with idrobustness, idcoverage, idmaintenance, authentication, idfrombirth, birthidlink and idregisters: the topic Digital Identity and CRVS.)*

## 1. What is assessed

**The share of the whole population, of all ages, holding a unique national identity number or credential**: people enrolled in the national ID system, counted once each, over the population. Cards printed are not people enrolled.

The study redraws `dpi.id--registration-of-entire-population`, which as at 2026-08-31 puts two countries at stage 3, one at 2, one at 1 and 50 unplaced. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| Registration of entire population | Registration of entire population: registration of entire population | `dpi.id--registration-of-entire-population` |

Anything else the evidence names is `other`, noted and never staged: a voter register, SIM registrations, a sectoral ID, an adults-only survey share (Findex), a count of cards produced or distributed.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Does a third of the population hold a national ID? | A source from the last three years gives a count or share of people enrolled that is a third of the population or more |
| 2 | Do two-thirds hold one? | A source from the last three years gives a count or share that is two-thirds of the population or more |
| 3 | Does everyone hold one? | A source from the last three years gives a count or share of 99.9% of the population or more |
| 4 | Are births and deaths registered at the target? | A source from the last three years puts birth registration at all births and death registration at 80% or more |

## 3. The ladders

**Registration of entire population**

| Stage | Answers |
|---|---|
| 1 Under a third | A source from the past three years counts fewer than a third of the population holding a national ID. |
| 2 A third | Yes to 1 |
| 3 Two-thirds | Yes to 2 |
| 4 Everyone | Yes to 3 |
| 5 Births and deaths registered | Yes to 4 |

A later yes answers the earlier ones (method §3.3). `study.json` holds this as three aspects: `share` (`twothirds`, `third`, `below`) for stage 1 and questions 1 and 2, `everyone` (`all`) for 3 and `births` (`target`) for 4.

## 4. The norm

The African Union's Digital Transformation Strategy sets a target of 99.9% of people in Africa holding a digital legal identity by 2030, from birth. This study asks the four questions above; it does not measure a country against the norm.

## 5. What the run reads

- **Carried**: nothing; no earlier study holds facts on these questions.
- **Read**: **589 news stories about the subject**, published since October 2023, in at most 15 a country: 573 in the batch's 149 shared calls, read once for every study that lists them, and 16 in 15 calls of its own. A story published before the three-year window can set no stage, and the fifteen are each country's best ranked across the batch (`study-calls.py --batch … --cap 15`).
- **Not read**: the rest of the 2,421 stories in the window, instruments, long reports, passing mentions and the documents the row's current cells cite. A question nothing answers is printed as *Not held*.

## 6. Token ceiling

**10 million** for this study; **70 million** for the batch, checked with `study-tokens.py` after every fan-out.

## 7. Tasks, in order

- [x] **D0. Prepared**: this file, `study.json` and the reading lists, 2026-10-16.
- [x] **D1. Read**, 2026-10-16: the batch's shared calls and this study's own, Sonnet drafters; 94 facts after the parent's corrections (`corrections.csv`).
- [x] **D2. Staged** as at 2026-09-30: 6 at 3, 8 at 2, 7 at 1; unplaced 2, no evidence 31. Every cell is a first pass; no second drafter.
- [x] **D3. Written, rendered and linted**, by `study-first-write.py`; on the soft-launch map. Reported to Bill.

**Decided in the run**: Population shares were taken from the drafters, who divided a stated count by the population held where the source gave no share; none was rechecked.

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
