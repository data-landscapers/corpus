---
type: task
reader: cc
title: maturity-study-aisystems.md — AI models, datasets and computing built or hosted in the country, in four questions
last_reviewed: 2026-10-16
status: first pass run 2026-10-16; staged, written and on the soft-launch map; waits for Bill's acceptance
---

# Maturity study: aisystems

*(Commissioned by Bill on 2026-10-16 as `tech.ai--development-of-national-regional-ai-systems`, a first pass under `maturity/documentation/first-pass-batch.md`, in one batch with aigovernment, aisectoral, aisystems, aiabuse, techhubs and startups: the chapter Technology.)*

## 1. What is assessed

**AI capacity built in the country**: an AI model, a dataset made for AI, or computing for AI (GPUs, an AI supercomputer or an AI factory) developed or hosted in the country, by government, universities or companies. What builds or hosts AI in the country counts, whatever it is called.

The study redraws `tech.ai--development-of-national-regional-ai-systems`, which as at 2026-08-31 puts eight countries at stage 3, 31 at 2 and 15 unplaced. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| AI built at home | Development of national / regional AI systems: AI built at home | `tech.ai--development-of-national-regional-ai-systems` |

Anything else the evidence names is `other`, noted and never staged: a foreign AI product used with no local development, an AI strategy or law, a data centre with no AI computing named, a training course, hackathon or skills programme.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Is a national AI model, dataset or AI computing facility under way? | A source from the last three years says one is being built, piloted, or planned with a named builder, funder or site |
| 2 | Is one in service? | A source from the last three years says an AI model built in the country is released, a dataset made for AI is published, or AI computing is in service |
| 3 | Is AI computing in service in the country? | A source from the last three years says a facility with GPUs or other AI accelerators is in service in the country |
| 4 | Is it shared with users? | A source from the last three years says national AI computing, models or datasets are open to researchers, startups or other countries, with users named or counted |

## 3. The ladders

**AI built at home**

| Stage | Answers |
|---|---|
| 1 Absent | A source from the past three years says no AI model, dataset or AI computing is developed or hosted in the country. |
| 2 Under way | Yes to 1 |
| 3 Model or dataset | Yes to 2 |
| 4 AI computing | Yes to 3 |
| 5 Shared with users | Yes to 4 |

A later yes answers the earlier ones (method §3.3). `study.json` holds this as three aspects: `build` (`inservice`, `underway`, `none`) for stage 1 and questions 1 and 2, `compute` (`compute`) for 3 and `shared` (`shared`) for 4.

## 4. The norm

The Continental AI Strategy asks that a country can manage its own data and AI, Local First: sovereign or regional computing, open national datasets and talent, taking part in continental AI infrastructure. This study asks the four questions above; it does not measure a country against the norm.

## 5. What the run reads

- **Carried**: nothing; no earlier study holds facts on these questions.
- **Read**: **595 story readings about the subject**, published since October 2023, in at most 20 stories a country: 554 in the batch's shared calls (147 calls over 732 stories), read once for every study that lists them, and 41 in 27 calls of its own. A story published before the three-year window can set no stage, and the twenty are each country's best ranked across the batch (`study-calls.py --batch … --cap 20`).
- **Not read**: the rest of the 7,217 documents this study lists, instruments, long reports, passing mentions and the documents the row's current cells cite. A question nothing answers is printed as *Not held*.

## 6. Token ceiling

**14 million** for this study; **85 million** for the batch, checked with `study-tokens.py` after every fan-out.

## 7. Tasks, in order

- [x] **D0. Prepared**: this file, `study.json` and the reading lists, 2026-10-16.
- [x] **D1. Read**, 2026-10-16: the batch's shared calls and this study's own, Sonnet drafters; 104 facts after the parent's corrections (`corrections.csv`).
- [x] **D2. Staged** as at 2026-09-30: 8 at 4, 14 at 3, 14 at 2; unplaced 0, no evidence 18. Every cell is a first pass; no second drafter.
- [x] **D3. Written, rendered and linted**, by `study-first-write.py`; on the soft-launch map. Reported to Bill.

**Decided in the run**: Removed: funding for computing centres read as computing in service (Namibia, now 2).

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
