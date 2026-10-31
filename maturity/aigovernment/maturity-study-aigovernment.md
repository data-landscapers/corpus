---
type: task
reader: cc
title: maturity-study-aigovernment.md — AI in use in public administration, in four questions
last_reviewed: 2026-10-16
status: first pass run 2026-10-16; staged, written and on the soft-launch map; waits for Bill's acceptance
---

# Maturity study: aigovernment

*(Commissioned by Bill on 2026-10-16 as `tech.ai--use-of-ai-in-government-administration`, a first pass under `maturity/documentation/first-pass-batch.md`, in one batch with aigovernment, aisectoral, aisystems, aiabuse, techhubs and startups: the chapter Technology.)*

## 1. What is assessed

**AI in use in public administration**: a government body using an AI system for its own work or to serve the public, such as a chatbot answering citizens, document or case processing, translation or fraud detection. What a government body uses AI for counts, whatever it is called.

The study redraws `tech.ai--use-of-ai-in-government-administration`, which as at 2026-08-31 puts 12 countries at stage 3, 12 at 2, three at 1 and 26 unplaced. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| AI in administration | Use of AI in government administration: AI in administration | `tech.ai--use-of-ai-in-government-administration` |

Anything else the evidence names is `other`, noted and never staged: an AI strategy, law or policy on its own, AI inside a sector's management system (health, education, agriculture, tax, customs), a training course or workshop, a company's AI product with no government user.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Is AI in administration under way? | A source from the last three years says a government body has tendered, piloted or is testing an AI system for its own work or its services |
| 2 | Is an AI system in service in administration? | A source from the last three years says a government body uses an AI system in service, such as a chatbot for a public service or AI processing documents |
| 3 | Is AI in service in several bodies? | A source from the last three years says AI systems are in service in two or more government bodies, or one government-wide AI platform serves several |
| 4 | Are rules or a register for government AI published? | A source from the last three years says the government's authority for cross-government digital governance has issued rules for government bodies' use or purchase of AI, or published a register of the government's AI systems |

## 3. The ladders

**AI in administration**

| Stage | Answers |
|---|---|
| 1 Absent | A source from the past three years says no AI system is in use in public administration. |
| 2 Under way | Yes to 1 |
| 3 In service | Yes to 2 |
| 4 Several bodies | Yes to 3 |
| 5 Rules or register | Yes to 4 |

**Question 4 is the central authority's** *(Bill, 2026-10-31, messages-for-bill 57)*: rules issued by one public body for its own AI use, such as the Bank of Tanzania's, place nothing; TZA stays at 4.

A later yes answers the earlier ones (method §3.3). `study.json` holds this as three aspects: `use` (`inservice`, `underway`, `none`) for stage 1 and questions 1 and 2, `bodies` (`several`) for 3 and `rules` (`rules`) for 4.

## 4. The norm

The Continental AI Strategy asks for AI adopted in the public sector under a governance framework, with innovation-friendly procurement and use cases shared and reported. This study asks the four questions above; it does not measure a country against the norm.

## 5. What the run reads

- **Carried**: nothing; no earlier study holds facts on these questions.
- **Read**: **588 story readings about the subject**, published since October 2023, in at most 20 stories a country: 553 in the batch's shared calls (147 calls over 732 stories), read once for every study that lists them, and 35 in 31 calls of its own. A story published before the three-year window can set no stage, and the twenty are each country's best ranked across the batch (`study-calls.py --batch … --cap 20`).
- **Not read**: the rest of the 7,056 documents this study lists, instruments, long reports, passing mentions and the documents the row's current cells cite. A question nothing answers is printed as *Not held*.

## 6. Token ceiling

**14 million** for this study; **85 million** for the batch, checked with `study-tokens.py` after every fan-out.

## 7. Tasks, in order

- [x] **D0. Prepared**: this file, `study.json` and the reading lists, 2026-10-16.
- [x] **D1. Read**, 2026-10-16: the batch's shared calls and this study's own, Sonnet drafters; 44 facts after the parent's corrections (`corrections.csv`).
- [x] **D2. Staged** as at 2026-09-30: 1 at 5, 2 at 4, 8 at 3, 10 at 2; unplaced 2, no evidence 31. Every cell is a first pass; no second drafter.
- [x] **D3. Written, rendered and linted**, by `study-first-write.py`; on the soft-launch map. Reported to Bill.

**Decided in the run**: Nothing removed at the top-stage check.

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
