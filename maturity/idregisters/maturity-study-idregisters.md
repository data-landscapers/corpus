---
type: task
reader: cc
title: maturity-study-idregisters.md — public registers that use the national ID number, in four questions
last_reviewed: 2026-10-16
status: first pass run 2026-10-16; staged, written and on the soft-launch map; waits for Bill's acceptance
---

# Maturity study: idregisters

*(Commissioned by Bill on 2026-10-16 as `dpi.id--use-by-other-systems`, a first pass under `maturity/documentation/first-pass-batch.md`, in one batch with idrobustness, idcoverage, idmaintenance, authentication, idfrombirth, birthidlink and idregisters: the topic Digital Identity and CRVS.)*

## 1. What is assessed

**A public register keyed on the national ID number**: the electoral roll drawn from the ID register, a tax register, civil service payroll, a social protection registry or the business register using the national number as its identifier. What makes the ID number the register's key counts.

The study redraws `dpi.id--use-by-other-systems`, which as at 2026-08-31 puts 13 countries at stage 3, 14 at 2, one at 1 and 25 unplaced. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| Use by other systems | Use by other systems: use by other systems | `dpi.id--use-by-other-systems-use-by-other-systems` |

Anything else the evidence names is `other`, noted and never staged: a private service checking customers against the ID (the idverification study holds those), SIM registration, a register with its own numbering and no link, a plan with no register.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Is another register's use of the ID number under way? | A source from the last three years says a public register's adoption of the national ID number is planned or piloted |
| 2 | Is one public register keyed on it? | A source from the last three years says a public register uses the national ID number: the electoral roll drawn from it, the tax register, payroll or a social registry |
| 3 | Are three or more main registers keyed on it? | Sources from the last three years show three or more of the electoral, tax, social protection, civil service payroll and business registers using the number |
| 4 | Is matching between registers reported? | A source from the last three years gives a figure from checking a register against the ID: ghost workers removed, duplicates found, records reconciled |

## 3. The ladders

**Use by other systems**

| Stage | Answers |
|---|---|
| 1 Not used | A source from the past three years says public registers do not use the national ID number. |
| 2 Under way | Yes to 1 |
| 3 One register | Yes to 2 |
| 4 Main registers | Yes to 3 |
| 5 Matching reported | Yes to 4 |

A later yes answers the earlier ones (method §3.3). `study.json` holds this as three aspects: `register` (`inservice`, `underway`, `none`) for stage 1 and questions 1 and 2, `several` (`several`) for 3 and `matching` (`reported`) for 4.

## 4. The norm

The African Union's interoperability framework and Data Policy Framework ask that the national ID be the single source of truth for identity across public registers. This study asks the four questions above; it does not measure a country against the norm.

## 5. What the run reads

- **Carried**: nothing; no earlier study holds facts on these questions.
- **Read**: **566 news stories about the subject**, published since October 2023, in at most 15 a country: 556 in the batch's 149 shared calls, read once for every study that lists them, and 10 in 10 calls of its own. A story published before the three-year window can set no stage, and the fifteen are each country's best ranked across the batch (`study-calls.py --batch … --cap 15`).
- **Not read**: the rest of the 2,421 stories in the window, instruments, long reports, passing mentions and the documents the row's current cells cite. No web search and no handover to OSINT. A question nothing answers is printed as *Not held*.

## 6. Token ceiling

**10 million** for this study; **70 million** for the batch, checked with `study-tokens.py` after every fan-out.

## 7. Tasks, in order

- [x] **D0. Prepared**: this file, `study.json` and the reading lists, 2026-10-16.
- [x] **D1. Read**, 2026-10-16: the batch's shared calls and this study's own, Sonnet drafters; 43 facts after the parent's corrections (`corrections.csv`).
- [x] **D2. Staged** as at 2026-09-30: 1 at 5, 1 at 4, 10 at 3, 7 at 2; unplaced 2, no evidence 33. Every cell is a first pass; no second drafter.
- [x] **D3. Written, rendered and linted**, by `study-first-write.py`; on the soft-launch map. Reported to Bill.

**Decided in the run**: Nothing removed.

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
