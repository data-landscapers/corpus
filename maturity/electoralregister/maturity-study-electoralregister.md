---
type: task
reader: cc
title: maturity-study-electoralregister.md — a digital voters' roll, in four questions
last_reviewed: 2026-10-16
status: first pass run 2026-10-16; staged, written and on the soft-launch map; waits for Bill's acceptance
---

# Maturity study: electoralregister

*(Commissioned by Bill on 2026-10-16 as `dpi.registry--electoral-register`, a first pass under `maturity/documentation/first-pass-batch.md`, in one batch with populationregister, civilregister, addressregister, businessregister, socialregistry, electoralregister, taxregister and landregister: the topic Registries.)*

## 1. What is assessed

**The voters' roll held in a digital or biometric register** by the electoral body. What holds the roll digitally counts, whatever it is called.

The study redraws `dpi.registry--electoral-register`, which as at 2026-08-31 puts 11 countries at stage 3, 20 at 2, one at 1 and 22 unplaced. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| Electoral register | Electoral register: electoral register | `dpi.registry--electoral-register-electoral-register` |

Anything else the evidence names is `other`, noted and never staged: a party membership list, a turnout figure, voting machines or result transmission with no register, a census.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Is a digital voters' roll under way? | A source from the last three years says a digital or biometric voter register is procured or piloted |
| 2 | Is the roll held digitally? | A source from the last three years says a digital or biometric voter register is in service |
| 3 | Can voters check the roll? | A source from the last three years says the roll was published or open to voters to check, online, by text message or at centres |
| 4 | Is it drawn from or checked against the ID or civil register? | A source from the last three years says the voters' roll is drawn from or checked against the national ID, population or civil register |

## 3. The ladders

**Electoral register**

| Stage | Answers |
|---|---|
| 1 By hand | A source from the past three years says the voters' roll is compiled by hand for each poll. |
| 2 Under way | Yes to 1 |
| 3 Digital roll | Yes to 2 |
| 4 Open for checking | Yes to 3 |
| 5 Linked to ID | Yes to 4 |

A later yes answers the earlier ones (method §3.3). `study.json` holds this as three aspects: `roll` (`inservice`, `underway`, `none`) for stage 1 and questions 1 and 2, `checked` (`open`) for 3 and `linked` (`linked`) for 4.

## 4. The norm

The African Charter on Democracy, Elections and Governance and the AU's election observation guidelines ask for an accurate voters' roll, open to public inspection and kept up to date. This study asks the four questions above; it does not measure a country against the norm.

## 5. What the run reads

- **Carried**: nothing; no earlier study holds facts on these questions.
- **Read**: **142 story readings about the subject**, published since October 2023, in at most 20 stories a country: 38 in the batch's 15 shared calls (75 stories), read once for every study that lists them, and 104 in 48 calls of its own. A story published before the three-year window can set no stage, and the twenty are each country's best ranked across the batch (`study-calls.py --batch … --cap 20`).
- **Not read**: the rest of the 1,494 documents this study lists, instruments, long reports, passing mentions and the documents the row's current cells cite. No web search and no handover to OSINT. A question nothing answers is printed as *Not held*.

## 6. Token ceiling

**13 million** for this study; **105 million** for the batch, checked with `study-tokens.py` after every fan-out.

## 7. Tasks, in order

- [x] **D0. Prepared**: this file, `study.json` and the reading lists, 2026-10-16.
- [x] **D1. Read**, 2026-10-16: the batch's shared calls and this study's own, Sonnet drafters; 86 facts after the parent's corrections (`corrections.csv`).
- [x] **D2. Staged** as at 2026-09-30: 9 at 5, 10 at 4, 8 at 3, 5 at 2; unplaced 1, no evidence 21. Every cell is a first pass; no second drafter.
- [x] **D3. Written, rendered and linted**, by `study-first-write.py`; on the soft-launch map. Reported to Bill.

**Decided in the run**: Removed: an ID card required to register read as a link to the ID register (Congo, Madagascar, Senegal); a statement of principle (Burundi); integration under way (Zimbabwe, which stays at 5 on another fact).

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
