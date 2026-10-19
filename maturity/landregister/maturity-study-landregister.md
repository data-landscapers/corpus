---
type: task
reader: cc
title: maturity-study-landregister.md — land titles and parcels held digitally, in four questions
last_reviewed: 2026-10-16
status: first pass run 2026-10-16; staged, written and on the soft-launch map; waits for Bill's acceptance
---

# Maturity study: landregister

*(Commissioned by Bill on 2026-10-16 as `dpi.registry--land-register`, a first pass under `maturity/documentation/first-pass-batch.md`, in one batch with populationregister, civilregister, addressregister, businessregister, socialregistry, electoralregister, taxregister and landregister: the topic Registries.)*

## 1. What is assessed

**The register of land rights and parcels held digitally**: a digital title register, cadastre or land information system run by government. What records land rights digitally counts, whatever it is called.

The study redraws `dpi.registry--land-register`, which as at 2026-08-31 puts 23 countries at stage 3, 22 at 2 and nine unplaced. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| Land register | Land register: land register | `dpi.registry--land-register` |

Anything else the evidence names is `other`, noted and never staged: a land law or policy with no system, a mapping project with no register, a private property portal, a land dispute with no register named.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Is digital land registration under way? | A source from the last three years says titles are being digitised or a digital cadastre or land information system is under way in some areas |
| 2 | Is a digital land register in service? | A source from the last three years says a digital title register, cadastre or land information system is in service for part of the country |
| 3 | Does it cover the whole country? | A source from the last three years says the digital land register is in service nationally or in all land offices |
| 4 | Can people search or register land online? | A source from the last three years says land searches, title applications or transfers can be made online |

## 3. The ladders

**Land register**

| Stage | Answers |
|---|---|
| 1 Paper | A source from the past three years says land rights are recorded on paper or not recorded. |
| 2 Under way | Yes to 1 |
| 3 In service | Yes to 2 |
| 4 Nationwide | Yes to 3 |
| 5 Online | Yes to 4 |

A later yes answers the earlier ones (method §3.3). `study.json` holds this as three aspects: `register` (`inservice`, `underway`, `none`) for stage 1 and questions 1 and 2, `national` (`nationwide`) for 3 and `online` (`online`) for 4.

## 4. The norm

The AU Framework and Guidelines on Land Policy asks for land rights, customary tenure included, to be registered and tracked in a computerised land information system with public access. This study asks the four questions above; it does not measure a country against the norm.

## 5. What the run reads

- **Carried**: nothing; no earlier study holds facts on these questions.
- **Read**: **190 story readings about the subject**, published since October 2023, in at most 20 stories a country: 43 in the batch's 15 shared calls (75 stories), read once for every study that lists them, and 147 in 56 calls of its own. A story published before the three-year window can set no stage, and the twenty are each country's best ranked across the batch (`study-calls.py --batch … --cap 20`).
- **Not read**: the rest of the 1,778 documents this study lists, instruments, long reports, passing mentions and the documents the row's current cells cite. A question nothing answers is printed as *Not held*.

## 6. Token ceiling

**13 million** for this study; **105 million** for the batch, checked with `study-tokens.py` after every fan-out.

## 7. Tasks, in order

- [x] **D0. Prepared**: this file, `study.json` and the reading lists, 2026-10-16.
- [x] **D1. Read**, 2026-10-16: the batch's shared calls and this study's own, Sonnet drafters; 115 facts after the parent's corrections (`corrections.csv`).
- [x] **D2. Staged** as at 2026-09-30: 9 at 5, 1 at 4, 7 at 3, 16 at 2; unplaced 2, no evidence 19. Every cell is a first pass; no second drafter.
- [x] **D3. Written, rendered and linted**, by `study-first-write.py`; on the soft-launch map. Reported to Bill.

**Decided in the run**: Nothing removed at the top-stage check.

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
