---
type: task
reader: cc
title: maturity-study-populationregister.md — a national register of the population, in four questions
last_reviewed: 2026-10-16
status: first pass run 2026-10-16; staged, written and on the soft-launch map; waits for Bill's acceptance
---

# Maturity study: populationregister

*(Commissioned by Bill on 2026-10-16 as `dpi.registry--population-register`, a first pass under `maturity/documentation/first-pass-batch.md`, in one batch with populationregister, civilregister, addressregister, businessregister, socialregistry, electoralregister, taxregister and landregister: the topic Registries.)*

## 1. What is assessed

**One government register holding a record for each person in the country**, whatever it is called: a population register, a civil-status database or a national ID register that the source says serves as the register of the population. What holds the population's records counts.

The study redraws `dpi.registry--population-register`, which as at 2026-08-31 puts 27 countries at stage 3, nine at 2, one at 1 and 16 unplaced. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| Population register | Population register: population register | `dpi.registry--population-register` |

Anything else the evidence names is `other`, noted and never staged: an ID card or passport issued with no register named, a census count, a voter roll, a programme's own beneficiary list.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Is a population register under way? | A source from the last three years says a population register is being built, procured or provided for in a new law |
| 2 | Is a population register in service? | A source from the last three years says a population register, or a national ID register serving as one, is in service |
| 3 | Is it updated from births and deaths? | A source from the last three years says births or deaths registered are entered in the population register |
| 4 | Do other systems draw on it? | A source from the last three years says other registers or services take people's records from the population register |

## 3. The ladders

**Population register**

| Stage | Answers |
|---|---|
| 1 None | A source from the past three years says no population register exists. |
| 2 Under way | Yes to 1 |
| 3 In service | Yes to 2 |
| 4 Updated from vital events | Yes to 3 |
| 5 Source for others | Yes to 4 |

A later yes answers the earlier ones (method §3.3). `study.json` holds this as three aspects: `register` (`inservice`, `underway`, `none`) for stage 1 and questions 1 and 2, `vital` (`updated`) for 3 and `used` (`source`) for 4.

## 4. The norm

The African Union's Digital Transformation Strategy puts an electronic population register first among the base registers, continuously updated from civil registration. This study asks the four questions above; it does not measure a country against the norm.

## 5. What the run reads

- **Carried**: nothing; no earlier study holds facts on these questions.
- **Read**: **78 story readings about the subject**, published since October 2023, in at most 20 stories a country: 52 in the batch's 15 shared calls (75 stories), read once for every study that lists them, and 26 in 17 calls of its own. A story published before the three-year window can set no stage, and the twenty are each country's best ranked across the batch (`study-calls.py --batch … --cap 20`).
- **Not read**: the rest of the 1,401 documents this study lists, instruments, long reports, passing mentions and the documents the row's current cells cite. A question nothing answers is printed as *Not held*.

## 6. Token ceiling

**13 million** for this study; **105 million** for the batch, checked with `study-tokens.py` after every fan-out.

## 7. Tasks, in order

- [x] **D0. Prepared**: this file, `study.json` and the reading lists, 2026-10-16.
- [x] **D1. Read**, 2026-10-16: the batch's shared calls and this study's own, Sonnet drafters; 70 facts after the parent's corrections (`corrections.csv`).
- [x] **D2. Staged** as at 2026-09-30: 8 at 5, 5 at 3, 5 at 2; unplaced 2, no evidence 34. Every cell is a first pass; no second drafter.
- [x] **D3. Written, rendered and linted**, by `study-first-write.py`; on the soft-launch map. Reported to Bill.

**Decided in the run**: Removed: an intended link (Niger), a convention for future use (Guinea) and a law's provision (Burkina Faso) read as other systems drawing on the register.

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
