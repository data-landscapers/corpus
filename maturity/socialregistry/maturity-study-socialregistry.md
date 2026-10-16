---
type: task
reader: cc
title: maturity-study-socialregistry.md — a social registry of households, in four questions
last_reviewed: 2026-10-16
status: first pass run 2026-10-16; staged, written and on the soft-launch map; waits for Bill's acceptance
---

# Maturity study: socialregistry

*(Commissioned by Bill on 2026-10-16 as `dpi.registry--social-protection-register`, a first pass under `maturity/documentation/first-pass-batch.md`, in one batch with populationregister, civilregister, addressregister, businessregister, socialregistry, electoralregister, taxregister and landregister: the topic Registries.)*

## 1. What is assessed

**A social registry**: one government register of households or people, with their circumstances, that social programmes draw on to choose who receives support. What does that job counts, whatever it is called.

The study redraws `dpi.registry--social-protection-register`, which as at 2026-08-31 puts 34 countries at stage 3, 13 at 2 and seven unplaced. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| Social protection register | Social protection register: social protection register | `dpi.registry--social-protection-register-social-protection-register` |

Anything else the evidence names is `other`, noted and never staged: one programme's own beneficiary list, a humanitarian agency's registration, a payment system, a census.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Is a social registry under way? | A source from the last three years says a social registry is procured, piloted or being populated in some districts |
| 2 | Is a social registry in service? | A source from the last three years says a social registry is in service |
| 3 | Do two or more programmes use it? | A source from the last three years says two or more social programmes choose who receives support from the social registry |
| 4 | Is it linked to the national ID? | A source from the last three years says the social registry is linked to or checked against the national ID |

## 3. The ladders

**Social protection register**

| Stage | Answers |
|---|---|
| 1 None | A source from the past three years says no social registry exists and programmes hold their own lists. |
| 2 Under way | Yes to 1 |
| 3 In service | Yes to 2 |
| 4 Several programmes | Yes to 3 |
| 5 Linked to ID | Yes to 4 |

A later yes answers the earlier ones (method §3.3). `study.json` holds this as three aspects: `registry` (`inservice`, `underway`, `none`) for stage 1 and questions 1 and 2, `programmes` (`several`) for 3 and `linked` (`linked`) for 4.

## 4. The norm

The African Union's Protocol on Social Protection asks states for a social registry and integrated beneficiary registry, interoperable with civil registration and payments. This study asks the four questions above; it does not measure a country against the norm.

## 5. What the run reads

- **Carried**: nothing; no earlier study holds facts on these questions.
- **Read**: **155 story readings about the subject**, published since October 2023, in at most 20 stories a country: 45 in the batch's 15 shared calls (75 stories), read once for every study that lists them, and 110 in 48 calls of its own. A story published before the three-year window can set no stage, and the twenty are each country's best ranked across the batch (`study-calls.py --batch … --cap 20`).
- **Not read**: the rest of the 1,387 documents this study lists, instruments, long reports, passing mentions and the documents the row's current cells cite. No web search and no handover to OSINT. A question nothing answers is printed as *Not held*.

## 6. Token ceiling

**13 million** for this study; **105 million** for the batch, checked with `study-tokens.py` after every fan-out.

## 7. Tasks, in order

- [x] **D0. Prepared**: this file, `study.json` and the reading lists, 2026-10-16.
- [x] **D1. Read**, 2026-10-16: the batch's shared calls and this study's own, Sonnet drafters; 124 facts after the parent's corrections (`corrections.csv`).
- [x] **D2. Staged** as at 2026-09-30: 3 at 5, 11 at 4, 14 at 3, 15 at 2; unplaced 0, no evidence 11. Every cell is a first pass; no second drafter.
- [x] **D3. Written, rendered and linted**, by `study-first-write.py`; on the soft-launch map. Reported to Bill.

**Decided in the run**: Removed: future use (Angola) and an aim of interoperability (Burkina Faso) read as use and a link.

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
