---
type: task
reader: cc
title: maturity-study-aisectoral.md — AI at work in a sector's public system, in four questions
last_reviewed: 2026-10-16
status: first pass run 2026-10-16; staged, written and on the soft-launch map; waits for Bill's acceptance
---

# Maturity study: aisectoral

*(Commissioned by Bill on 2026-10-16 as `tech.ai--use-of-ai-in-sectoral-management-information-systems`, a first pass under `maturity/documentation/first-pass-batch.md`, in one batch with aigovernment, aisectoral, aisystems, aiabuse, techhubs and startups: the chapter Technology.)*

## 1. What is assessed

**AI in a sector's public system**: an AI model or tool working inside a public health, education, agriculture, tax, customs, social protection, justice or climate system, giving a diagnosis, a risk score, a forecast or a decision. What uses AI in a sector's public system counts, whatever it is called.

The study redraws `tech.ai--use-of-ai-in-sectoral-management-information-systems`, which as at 2026-08-31 puts 13 countries at stage 3, 19 at 2, one at 1 and 21 unplaced. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| AI in sector systems | Use of AI in sectoral management information systems: AI in sector systems | `tech.ai--use-of-ai-in-sectoral-management-information-systems-ai-in-sector-systems` |

Anything else the evidence names is `other`, noted and never staged: an AI chatbot or document tool for general administration, an AI strategy or law, a company's product with no public body using it, a training course or hackathon.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Is a sectoral AI tool under way? | A source from the last three years says an AI tool for a public health, education, agriculture, tax, customs or other sector's system is piloted, tested or being built |
| 2 | Is one in service? | A source from the last three years says an AI tool is in service in a public sector's system and producing outputs, such as diagnoses, risk scores, forecasts or notices |
| 3 | Is AI in service in several sectors? | A source from the last three years says AI tools are in service in the public systems of two or more sectors |
| 4 | Are its results reported? | A source from the last three years reports measured results of a sectoral AI system in service, such as cases detected, revenue recovered or accuracy |

## 3. The ladders

**AI in sector systems**

| Stage | Answers |
|---|---|
| 1 Absent | A source from the past three years says no public sector's system uses AI. |
| 2 Under way | Yes to 1 |
| 3 In service | Yes to 2 |
| 4 Several sectors | Yes to 3 |
| 5 Results reported | Yes to 4 |

A later yes answers the earlier ones (method §3.3). `study.json` holds this as three aspects: `use` (`inservice`, `underway`, `none`) for stage 1 and questions 1 and 2, `sectors` (`several`) for 3 and `results` (`reported`) for 4.

## 4. The norm

The Continental AI Strategy asks for AI adopted in the core sectors, with national centres of excellence or datasets supporting it and outcomes reported. This study asks the four questions above; it does not measure a country against the norm.

## 5. What the run reads

- **Carried**: nothing; no earlier study holds facts on these questions.
- **Read**: **589 story readings about the subject**, published since October 2023, in at most 20 stories a country: 559 in the batch's shared calls (147 calls over 732 stories), read once for every study that lists them, and 30 in 24 calls of its own. A story published before the three-year window can set no stage, and the twenty are each country's best ranked across the batch (`study-calls.py --batch … --cap 20`).
- **Not read**: the rest of the 7,184 documents this study lists, instruments, long reports, passing mentions and the documents the row's current cells cite. A question nothing answers is printed as *Not held*.

## 6. Token ceiling

**14 million** for this study; **85 million** for the batch, checked with `study-tokens.py` after every fan-out.

## 7. Tasks, in order

- [x] **D0. Prepared**: this file, `study.json` and the reading lists, 2026-10-16.
- [x] **D1. Read**, 2026-10-16: the batch's shared calls and this study's own, Sonnet drafters; 49 facts after the parent's corrections (`corrections.csv`).
- [x] **D2. Staged** as at 2026-09-30: 1 at 5, 8 at 3, 15 at 2; unplaced 1, no evidence 29. Every cell is a first pass; no second drafter.
- [x] **D3. Written, rendered and linted**, by `study-first-write.py`; on the soft-launch map. Reported to Bill.

**Decided in the run**: Removed: a flood model's validation results read as a system in service (Mauritania, which stays at 3).

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
