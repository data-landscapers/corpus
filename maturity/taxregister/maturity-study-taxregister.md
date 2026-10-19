---
type: task
reader: cc
title: maturity-study-taxregister.md — a computerised register of taxpayers, in four questions
last_reviewed: 2026-10-16
status: first pass run 2026-10-16; staged, written and on the soft-launch map; waits for Bill's acceptance
---

# Maturity study: taxregister

*(Commissioned by Bill on 2026-10-16 as `dpi.registry--tax-register`, a first pass under `maturity/documentation/first-pass-batch.md`, in one batch with populationregister, civilregister, addressregister, businessregister, socialregistry, electoralregister, taxregister and landregister: the topic Registries.)*

## 1. What is assessed

**The tax authority's register of taxpayers, held on computer**, and the taxpayer number it issues. What registers taxpayers counts, whatever the number is called.

The study redraws `dpi.registry--tax-register`, which as at 2026-08-31 puts one country at stage 4, six at 3, 29 at 2 and 18 unplaced. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| Tax register | Tax register: tax register | `dpi.registry--tax-register-tax-register` |

Anything else the evidence names is `other`, noted and never staged: tax payment or filing with no register named, a business register alone, customs declarations, a tax law with no register.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Is a computerised taxpayer register under way? | A source from the last three years says a computerised taxpayer register or new taxpayer number is being built, migrated or rolled out |
| 2 | Are taxpayers registered on computer? | A source from the last three years says taxpayer numbers are issued from a computerised register in service, online or at offices |
| 3 | Is the taxpayer number shared with business registration or customs? | A source from the last three years says the taxpayer number is issued at business registration or used by customs, one number for both |
| 4 | Is the taxpayer number tied to the national ID? | A source from the last three years says the taxpayer number is the national ID number or is checked against the national ID |

## 3. The ladders

**Tax register**

| Stage | Answers |
|---|---|
| 1 Paper | A source from the past three years says taxpayers are registered on paper or not registered. |
| 2 Under way | Yes to 1 |
| 3 Computerised | Yes to 2 |
| 4 Shared with firms or customs | Yes to 3 |
| 5 Tied to ID | Yes to 4 |

A later yes answers the earlier ones (method §3.3). `study.json` holds this as three aspects: `register` (`inservice`, `underway`, `none`) for stage 1 and questions 1 and 2, `shared` (`shared`) for 3 and `nationalid` (`linked`) for 4.

## 4. The norm

The TADAT framework asks for every taxpayer to hold one unique identifier in one central database, shared with other registers. This study asks the four questions above; it does not measure a country against the norm.

## 5. What the run reads

- **Carried**: nothing; no earlier study holds facts on these questions.
- **Read**: **87 story readings about the subject**, published since October 2023, in at most 20 stories a country: 33 in the batch's 15 shared calls (75 stories), read once for every study that lists them, and 54 in 32 calls of its own. A story published before the three-year window can set no stage, and the twenty are each country's best ranked across the batch (`study-calls.py --batch … --cap 20`).
- **Not read**: the rest of the 1,252 documents this study lists, instruments, long reports, passing mentions and the documents the row's current cells cite. A question nothing answers is printed as *Not held*.

## 6. Token ceiling

**13 million** for this study; **105 million** for the batch, checked with `study-tokens.py` after every fan-out.

## 7. Tasks, in order

- [x] **D0. Prepared**: this file, `study.json` and the reading lists, 2026-10-16.
- [x] **D1. Read**, 2026-10-16: the batch's shared calls and this study's own, Sonnet drafters; 50 facts after the parent's corrections (`corrections.csv`).
- [x] **D2. Staged** as at 2026-09-30: 3 at 5, 8 at 4, 9 at 3, 1 at 2; unplaced 1, no evidence 32. Every cell is a first pass; no second drafter.
- [x] **D3. Written, rendered and linted**, by `study-first-write.py`; on the soft-launch map. Reported to Bill.

**Decided in the run**: Removed: an ID number checked against the attached copy (Cameroon); future use of the NIN (Uganda, which stays at 5 on another fact).

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
