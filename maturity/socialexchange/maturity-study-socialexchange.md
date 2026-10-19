---
type: task
reader: cc
title: maturity-study-socialexchange.md — social protection systems exchanging data, in four questions
last_reviewed: 2026-10-16
status: first pass run 2026-10-16; staged, written and on the soft-launch map; waits for Bill's acceptance
---

# Maturity study: socialexchange

*(Commissioned by Bill on 2026-10-16 as `dpi.exchange--interoperability-of-social-protection-systems`, a first pass under `maturity/documentation/first-pass-batch.md`, in one batch with dataexchange, idverification, healthexchange, educationexchange and socialexchange.)*

## 1. What is assessed

**Data passing between social protection systems, or between them and others**: a social registry or programme MIS linked to the national ID, to a payment provider or to another programme; a registry several programmes draw on. What moves beneficiary data between systems counts, whatever it is called.

The study redraws `dpi.exchange--interoperability-of-social-protection-systems`, which as at 2026-08-31 puts 16 countries at stage 3, 28 at 2 and ten unplaced. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| Interoperability of social protection systems | Interoperability of social protection systems: interoperability of social protection systems | `dpi.exchange--interoperability-of-social-protection-systems` |

Anything else the evidence names is `other`, noted and never staged: a beneficiary list kept for one programme with no link, a survey or targeting exercise, a payment made in cash with no system link, a plan or policy with no link in service.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Is a link between social protection systems under way? | A source from the last three years says a registry or programme link to the ID, a payment provider or another programme is contracted, being built or piloted |
| 2 | Is one exchange in service? | A source from the last three years says a registry or programme MIS exchanges data with the national ID, a payment provider or another programme in use |
| 3 | Do two or more programmes share one registry? | A source from the last three years says two or more programmes draw beneficiaries from a shared social registry |
| 4 | Is the registry linked to the ID and another sector? | A source from the last three years says the registry is linked to the national ID and to civil registration, health, education or tax |

## 3. The ladders

**Interoperability of social protection systems**

| Stage | Answers |
|---|---|
| 1 Absent | A source from the last three years says it is absent |
| 2 Under way | Yes to 1 |
| 3 In service | Yes to 2 |
| 4 Shared registry | Yes to 3 |
| 5 Linked beyond | Yes to 4 |

A later yes answers the earlier ones (method §3.3). `study.json` holds this as three aspects: `exchange` (`inservice`, `underway`, `none`) for questions 1 and 2, `registry` (`shared`) for 3 and `linked` (`linked`) for 4. **For the drafter**: the system's name goes in `system`, the bodies or systems it links in the fact.

## 4. The norm

The African Union's Protocol on Social Protection asks for a social protection information system that works with the ID, civil registration, payments and other sectors, so benefits follow the person. This study asks the four questions above; it does not measure a country against the norm.

## 5. What the run reads

- **Carried**: nothing; no earlier study holds facts on these questions.
- **Read**: **150 news stories about the subject that no study has read**, in 42 countries; then the 143 documents the row's current cells cite, in 46 countries. 101 calls of its own, besides the batch's 19 shared calls over 84 stories read once for two studies or more.
- **Not read**: instruments, long reports and passing mentions. A question nothing answers is printed as *Not held*.

## 6. Token ceiling

**40 million** for this study; **200 million** for the batch, checked with `study-tokens.py` after every fan-out.

## 7. Tasks, in order

- [x] **D0. Prepared**: this file, `study.json` and the reading lists, 2026-10-16.
- [x] **D1. Read**, 2026-10-16: the batch's 19 shared calls and this study's own, Sonnet drafters; 158 facts after the parent's corrections (`corrections.csv`).
- [x] **D2. Staged** as at 2026-09-30: 1 at 5, 16 at 4, 7 at 3, 17 at 2; unplaced 1, no evidence 12. Every cell is a first pass; no second drafter.
- [x] **D3. Written, rendered and linted**, by `study-first-write.py`; on the soft-launch map. Reported to Bill. Batch tokens 203M of 200M, the reading of all five studies.

**Decided in the run**: The DRC's two decrees creating the Registre Social Unique are removed as a shared registry: they create it, and no programme is said to draw on it yet.

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
