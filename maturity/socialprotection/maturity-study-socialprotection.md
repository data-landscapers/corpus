---
type: task
reader: cc
title: maturity-study-socialprotection.md — social programmes run on a management information system, in four questions
last_reviewed: 2026-10-16
status: first pass run 2026-10-16; staged, written and on the soft-launch map; waits for Bill's acceptance
---

# Maturity study: socialprotection

*(Commissioned by Bill on 2026-10-16 as `dpi.mis--social-protection`, a first pass under `maturity/documentation/first-pass-batch.md`, in one batch with socialprotection, justice, taxadmin, customs and landadmin: the topic Sectoral management information systems.)*

## 1. What is assessed

**The management information system a social programme runs on**: enrolling beneficiaries, keeping their records and drawing up who is paid. What runs a programme's administration counts, whatever it is called.

The study redraws `dpi.mis--social-protection`, which as at 2026-08-31 puts 38 countries at stage 3, eight at 2 and eight unplaced. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| Social protection | Social protection: social protection | `dpi.mis--social-protection` |

Anything else the evidence names is `other`, noted and never staged: a social registry of households on its own, a payment provider with no programme system named, a programme's budget or size alone, a humanitarian agency's own list.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Is a programme management information system under way? | A source from the last three years says a management information system for a social programme is procured, piloted or being built |
| 2 | Is a programme run on one? | A source from the last three years says a social programme's beneficiaries are enrolled and managed in an information system in service |
| 3 | Does it pay beneficiaries electronically? | A source from the last three years says the programme's system sends payments to beneficiaries through banks or mobile money |
| 4 | Does one system serve several programmes? | A source from the last three years says one information system serves two or more social programmes, or contributory and non-contributory schemes together |

## 3. The ladders

**Social protection**

| Stage | Answers |
|---|---|
| 1 Paper | A source from the past three years says social programmes are administered on paper. |
| 2 Under way | Yes to 1 |
| 3 In service | Yes to 2 |
| 4 Paid electronically | Yes to 3 |
| 5 Several programmes | Yes to 4 |

A later yes answers the earlier ones (method §3.3). `study.json` holds this as three aspects: `system` (`inservice`, `underway`, `none`) for stage 1 and questions 1 and 2, `payments` (`electronic`) for 3 and `integrated` (`several`) for 4.

## 4. The norm

The African Union's Protocol on Social Protection asks for an integrated social protection information system across schemes, with disaggregated data published. This study asks the four questions above; it does not measure a country against the norm.

## 5. What the run reads

- **Carried**: nothing; no earlier study holds facts on these questions.
- **Read**: **89 story readings about the subject**, published since October 2023, in at most 20 stories a country: 0 in the batch's three shared calls (13 stories), read once for every study that lists them, and 89 in 37 calls of its own. A story published before the three-year window can set no stage, and the twenty are each country's best ranked across the batch (`study-calls.py --batch … --cap 20`).
- **Not read**: the rest of the 1,263 documents this study lists, instruments, long reports, passing mentions and the documents the row's current cells cite. A question nothing answers is printed as *Not held*.

## 6. Token ceiling

**8 million** for this study; **40 million** for the batch, checked with `study-tokens.py` after every fan-out.

## 7. Tasks, in order

- [x] **D0. Prepared**: this file, `study.json` and the reading lists, 2026-10-16.
- [x] **D1. Read**, 2026-10-16: the batch's shared calls and this study's own, Sonnet drafters; 50 facts after the parent's corrections (`corrections.csv`).
- [x] **D2. Staged** as at 2026-09-30: 1 at 5, 11 at 4, 4 at 3, 2 at 2; unplaced 1, no evidence 35. Every cell is a first pass; no second drafter.
- [x] **D3. Written, rendered and linted**, by `study-first-write.py`; on the soft-launch map. Reported to Bill.

**Decided in the run**: Removed: the social registry's use across sectors read as one system serving several programmes (Burundi, which stays at 4); a payment card serving several programmes with no system named (Egypt, which stays at 4).

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
