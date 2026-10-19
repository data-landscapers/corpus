---
type: task
reader: cc
title: maturity-study-idverification.md — other systems that check people against the national ID, in four questions
last_reviewed: 2026-10-16
status: first pass run 2026-10-16; staged, written and on the soft-launch map; waits for Bill's acceptance
---

# Maturity study: idverification

*(Commissioned by Bill on 2026-10-16 as `dpi.exchange--use-of-digital-id-in-other-systems`, a first pass under `maturity/documentation/first-pass-batch.md`, in one batch with dataexchange, idverification, healthexchange, educationexchange and socialexchange.)*

## 1. What is assessed

**A system other than the ID system itself that checks people against the national ID**: SIM registration verified against the ID database, a bank's or mobile money provider's KYC, enrolment in a social programme, health insurance, tax or voter registration that verifies the ID number. What relies on the ID to confirm who someone is counts, public or private.

The study redraws `dpi.exchange--use-of-digital-id-in-other-systems`, which as at 2026-08-31 puts two countries at stage 4, 24 at 3, 19 at 2 and nine unplaced. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| Use of digital ID in other systems | Use of digital id in other systems: use of digital id in other systems | `dpi.exchange--use-of-digital-id-in-other-systems-use-of-digital-id-in-other-systems` |

Anything else the evidence names is `other`, noted and never staged: the ID system's own enrolment or card issue, a register merely keyed on the number with no check (the ID row's `use-by-other-systems` holds that), a foreign passport or a sectoral ID with no link to the national one, a law that allows use with none on record.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Is another system's use of the ID under way? | A source from the last three years says a link to the ID is contracted, being built or piloted for another system |
| 2 | Does another system check people against the ID? | A source from the last three years says a service in use verifies people against the national ID |
| 3 | Do services in two or more sectors check against it? | Sources from the last three years show services in two or more sectors (telecoms, banking, social protection, health, tax, elections) verifying against the ID |
| 4 | Is the use reported? | A source from the last three years gives a figure for verifications made, or counts the services or institutions relying on the ID |

## 3. The ladders

**Use of digital ID in other systems**

| Stage | Answers |
|---|---|
| 1 Absent | A source from the last three years says it is absent |
| 2 Under way | Yes to 1 |
| 3 In use | Yes to 2 |
| 4 Across sectors | Yes to 3 |
| 5 Use reported | Yes to 4 |

A later yes answers the earlier ones (method §3.3). `study.json` holds this as three aspects: `use` (`inservice`, `underway`, `none`) for questions 1 and 2, `sectors` (`several`) for 3 and `usage` (`reported`) for 4. **For the drafter**: the system's name goes in `system`, the bodies or systems it links in the fact.

## 4. The norm

The African Union's interoperability framework and the AfCFTA Digital Trade Protocol ask that a national digital ID be the credential other public and private services rely on, recognised across borders. This study asks the four questions above; it does not measure a country against the norm.

## 5. What the run reads

- **Carried**: nothing; no earlier study holds facts on these questions.
- **Read**: **253 news stories about the subject that no study has read**, in 40 countries; then the 298 documents the row's current cells cite, in 54 countries. 149 calls of its own, besides the batch's 19 shared calls over 84 stories read once for two studies or more.
- **Not read**: instruments, long reports and passing mentions. A question nothing answers is printed as *Not held*.

## 6. Token ceiling

**40 million** for this study; **200 million** for the batch, checked with `study-tokens.py` after every fan-out.

## 7. Tasks, in order

- [x] **D0. Prepared**: this file, `study.json` and the reading lists, 2026-10-16.
- [x] **D1. Read**, 2026-10-16: the batch's 19 shared calls and this study's own, Sonnet drafters; 338 facts after the parent's corrections (`corrections.csv`).
- [x] **D2. Staged** as at 2026-09-30: 10 at 5, 5 at 4, 17 at 3, 11 at 2; unplaced 2, no evidence 9. Every cell is a first pass; no second drafter.
- [x] **D3. Written, rendered and linted**, by `study-first-write.py`; on the soft-launch map. Reported to Bill. Batch tokens 203M of 200M, the reading of all five studies.

**Decided in the run**: Removed as use reported: Egypt's app sign-ups, Ghana's share cross-referenced with no count and its SIM linkage never checked against the register, South Africa's bank branches offering Home Affairs services. A Ghana fact whose source has no URL is removed. Two drafters filed an aspect key as the sub-indicator (`use` is both); the rows were set right before merging.

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
