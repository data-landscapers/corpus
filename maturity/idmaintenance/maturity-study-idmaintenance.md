---
type: task
reader: cc
title: maturity-study-idmaintenance.md — who runs and maintains the national ID system, in four questions
last_reviewed: 2026-10-16
status: first pass run 2026-10-16; staged, written and on the soft-launch map; waits for Bill's acceptance
---

# Maturity study: idmaintenance

*(Commissioned by Bill on 2026-10-16 as `dpi.id--national-maintenance-of-id-and-credentials-systems`, a first pass under `maturity/documentation/first-pass-batch.md`, in one batch with idrobustness, idcoverage, idmaintenance, authentication, idfrombirth, birthidlink and idregisters: the topic Digital Identity and CRVS.)*

## 1. What is assessed

**Who operates, maintains and owns the national ID system**: the national authority and its staff, or a foreign supplier. The ID card, number and the systems that issue them count, whoever built them.

The study redraws `dpi.id--national-maintenance-of-id-and-credentials-systems`, which as at 2026-08-31 puts 22 countries at stage 3, four at 2 and 28 unplaced. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| National maintenance of id and credentials systems | National maintenance of id and credentials systems: national maintenance of id and credentials systems | `dpi.id--national-maintenance-of-id-and-credentials-systems-national-maintenance-of-id-and-credentials-systems` |

Anything else the evidence names is `other`, noted and never staged: a passport or voter-card contract, a supplier's sale of equipment with no operating role, a law with no system.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Is national operation under way? | A source from the last three years says national operation is a stated goal, or a transfer of skills or a local team is announced, while a supplier still runs the system |
| 2 | Does a national authority run it day to day? | A source from the last three years says the national authority operates the system day to day, even on a platform built abroad |
| 3 | Do national staff maintain it? | A source from the last three years says the authority's own staff or a national company maintain and upgrade it, or the foreign contract has ended |
| 4 | Does the state own the platform it runs on? | A source from the last three years says the system in service runs on code the state owns: built in-house, on open source such as MOSIP, or with the code handed over |

## 3. The ladders

**National maintenance of id and credentials systems**

| Stage | Answers |
|---|---|
| 1 Run by a supplier | A source from the past three years says a foreign supplier builds, hosts and runs the national ID system, with no national capacity. |
| 2 Transfer under way | Yes to 1 |
| 3 Run nationally | Yes to 2 |
| 4 Maintained nationally | Yes to 3 |
| 5 Owned | Yes to 4 |

A later yes answers the earlier ones (method §3.3). `study.json` holds this as three aspects: `operation` (`national`, `transfer`, `supplier`) for stage 1 and questions 1 and 2, `maintenance` (`national`) for 3 and `ownership` (`owned`) for 4.

## 4. The norm

The African Union's interoperability framework asks that countries own and operate their identity systems on open standards, with no vendor lock-in and sustainable finance. This study asks the four questions above; it does not measure a country against the norm.

## 5. What the run reads

- **Carried**: nothing; no earlier study holds facts on these questions.
- **Read**: **575 news stories about the subject**, published since October 2023, in at most 15 a country: 562 in the batch's 149 shared calls, read once for every study that lists them, and 13 in 13 calls of its own. A story published before the three-year window can set no stage, and the fifteen are each country's best ranked across the batch (`study-calls.py --batch … --cap 15`).
- **Not read**: the rest of the 2,421 stories in the window, instruments, long reports, passing mentions and the documents the row's current cells cite. A question nothing answers is printed as *Not held*.

## 6. Token ceiling

**10 million** for this study; **70 million** for the batch, checked with `study-tokens.py` after every fan-out.

## 7. Tasks, in order

- [x] **D0. Prepared**: this file, `study.json` and the reading lists, 2026-10-16.
- [x] **D1. Read**, 2026-10-16: the batch's shared calls and this study's own, Sonnet drafters; 117 facts after the parent's corrections (`corrections.csv`).
- [x] **D2. Staged** as at 2026-09-30: 7 at 5, 4 at 4, 27 at 3, 2 at 2; unplaced 1, no evidence 13. Every cell is a first pass; no second drafter.
- [x] **D3. Written, rendered and linted**, by `study-first-write.py`; on the soft-launch map. Reported to Bill.

**Decided in the run**: Removed as the state owning the platform: Lesotho's MOSIP still being deployed, Morocco named the first to implement MOSIP with no word that its ID runs on it, Uganda's OpenCRVS module, which is the civil register.

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
