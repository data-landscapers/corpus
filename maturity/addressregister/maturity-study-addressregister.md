---
type: task
reader: cc
title: maturity-study-addressregister.md — a national addressing system, in four questions
last_reviewed: 2026-10-16
status: first pass run 2026-10-16; staged, written and on the soft-launch map; waits for Bill's acceptance
---

# Maturity study: addressregister

*(Commissioned by Bill on 2026-10-16 as `dpi.registry--address-register`, a first pass under `maturity/documentation/first-pass-batch.md`, in one batch with populationregister, civilregister, addressregister, businessregister, socialregistry, electoralregister, taxregister and landregister: the topic Registries.)*

## 1. What is assessed

**A system giving places an address and holding them in a register**: street naming and numbering, digital or postcode addresses, recorded centrally. What gives and records addresses counts, whoever runs it.

The study redraws `dpi.registry--address-register`, which as at 2026-08-31 puts three countries at stage 3, 30 at 2, eight at 1 and ten unplaced. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| Address register | Address register: address register | `dpi.registry--address-register` |

Anything else the evidence names is `other`, noted and never staged: a private map or delivery app with no government role, a land cadastre, a postcode list with no addresses.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Is an addressing system under way? | A source from the last three years says a national addressing policy is adopted, or street naming, numbering or digital addressing is under way in some cities |
| 2 | Is an address register or digital addressing system in service? | A source from the last three years says an address register or digital addressing system is in service |
| 3 | Does it cover the whole country? | A source from the last three years says the addressing system covers the whole country, rural areas included |
| 4 | Do other services use it? | A source from the last three years says the post, emergency services, utilities or other registers use the address system |

## 3. The ladders

**Address register**

| Stage | Answers |
|---|---|
| 1 None | A source from the past three years says there is no national addressing system. |
| 2 Under way | Yes to 1 |
| 3 In service | Yes to 2 |
| 4 Nationwide | Yes to 3 |
| 5 Used by services | Yes to 4 |

A later yes answers the earlier ones (method §3.3). `study.json` holds this as three aspects: `addressing` (`inservice`, `underway`, `none`) for stage 1 and questions 1 and 2, `national` (`nationwide`) for 3 and `used` (`used`) for 4.

## 4. The norm

The Universal Postal Union's Addressing the World asks every country for a national addressing policy, an address for everyone and an address register other systems can use. This study asks the four questions above; it does not measure a country against the norm.

## 5. What the run reads

- **Carried**: nothing; no earlier study holds facts on these questions.
- **Read**: **101 story readings about the subject**, published since October 2023, in at most 20 stories a country: 31 in the batch's 15 shared calls (75 stories), read once for every study that lists them, and 70 in 39 calls of its own. A story published before the three-year window can set no stage, and the twenty are each country's best ranked across the batch (`study-calls.py --batch … --cap 20`).
- **Not read**: the rest of the 1,249 documents this study lists, instruments, long reports, passing mentions and the documents the row's current cells cite. A question nothing answers is printed as *Not held*.

## 6. Token ceiling

**13 million** for this study; **105 million** for the batch, checked with `study-tokens.py` after every fan-out.

## 7. Tasks, in order

- [x] **D0. Prepared**: this file, `study.json` and the reading lists, 2026-10-16.
- [x] **D1. Read**, 2026-10-16: the batch's shared calls and this study's own, Sonnet drafters; 69 facts after the parent's corrections (`corrections.csv`).
- [x] **D2. Staged** as at 2026-09-30: 4 at 5, 1 at 4, 3 at 3, 20 at 2, 1 at 1; unplaced 0, no evidence 25. Every cell is a first pass; no second drafter.
- [x] **D3. Written, rendered and linted**, by `study-first-write.py`; on the soft-launch map. Reported to Bill.

**Decided in the run**: Removed: private address apps and a private firm's coverage claim (Cameroon, Lesotho), and an app's own delivery feature (Ghana).

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
