---
type: task
reader: cc
title: maturity-study-landadmin.md — land administration run on an information system, in four questions
last_reviewed: 2026-10-16
status: first pass run 2026-10-16; staged, written and on the soft-launch map; waits for Bill's acceptance
---

# Maturity study: landadmin

*(Commissioned by Bill on 2026-10-16 as `dpi.mis--land`, a first pass under `maturity/documentation/first-pass-batch.md`, in one batch with socialprotection, justice, taxadmin, customs and landadmin: the topic Sectoral management information systems.)*

## 1. What is assessed

**The information system land administration runs on**: transfers, mortgages and other land transactions processed electronically, joined to survey maps, valuation and tax. What processes land transactions electronically counts, whatever it is called.

The study redraws `dpi.mis--land`, which as at 2026-08-31 puts 21 countries at stage 3, 23 at 2 and nine unplaced. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| Land | Land: land | `dpi.mis--land` |

Anything else the evidence names is `other`, noted and never staged: a land law or policy with no system, a mapping or titling drive with no system named, a private property portal, a land dispute with no system named.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Is a land information system under way? | A source from the last three years says a land information or land administration system is procured, piloted in some regions or being built |
| 2 | Are land transactions processed electronically? | A source from the last three years says transfers, registrations or mortgages are processed in a land information system in service, in some areas at least |
| 3 | Does it join records to survey maps or valuation? | A source from the last three years says the system joins land records with the cadastre's survey maps or with property valuation |
| 4 | Is it linked to tax? | A source from the last three years says land or property tax, stamp duty or rates are assessed or paid through, or from, the land system |

## 3. The ladders

**Land**

| Stage | Answers |
|---|---|
| 1 Paper | A source from the past three years says land transactions, valuation and planning are run on paper. |
| 2 Under way | Yes to 1 |
| 3 In service | Yes to 2 |
| 4 Maps or valuation | Yes to 3 |
| 5 Linked to tax | Yes to 4 |

A later yes answers the earlier ones (method §3.3). `study.json` holds this as three aspects: `system` (`inservice`, `underway`, `none`) for stage 1 and questions 1 and 2, `joined` (`joined`) for 3 and `tax` (`linked`) for 4.

## 4. The norm

The AU Framework and Guidelines on Land Policy asks for a computerised land information system through which rights are registered and tracked across the administration's functions. This study asks the four questions above; it does not measure a country against the norm.

## 5. What the run reads

- **Carried**: nothing; no earlier study holds facts on these questions.
- **Read**: **42 story readings about the subject**, published since October 2023, in at most 20 stories a country: 0 in the batch's three shared calls (13 stories), read once for every study that lists them, and 42 in 21 calls of its own. A story published before the three-year window can set no stage, and the twenty are each country's best ranked across the batch (`study-calls.py --batch … --cap 20`).
- **Not read**: the rest of the 360 documents this study lists, instruments, long reports, passing mentions and the documents the row's current cells cite. A question nothing answers is printed as *Not held*.

## 6. Token ceiling

**8 million** for this study; **40 million** for the batch, checked with `study-tokens.py` after every fan-out.

## 7. Tasks, in order

- [x] **D0. Prepared**: this file, `study.json` and the reading lists, 2026-10-16.
- [x] **D1. Read**, 2026-10-16: the batch's shared calls and this study's own, Sonnet drafters; 46 facts after the parent's corrections (`corrections.csv`).
- [x] **D2. Staged** as at 2026-09-30: 5 at 5, 3 at 3, 9 at 2; unplaced 0, no evidence 37. Every cell is a first pass; no second drafter.
- [x] **D3. Written, rendered and linted**, by `study-first-write.py`; on the soft-launch map. Reported to Bill.

**Decided in the run**: Removed: what Malawi's land system is designed to do read as in service.

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
