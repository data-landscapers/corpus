---
type: task
reader: cc
title: maturity-study-refugees.md — registration and digital inclusion of refugees and displaced people, in four questions
last_reviewed: 2026-10-16
status: first pass run 2026-10-16; staged, written and on the soft-launch map; waits for Bill's acceptance
---

# Maturity study: refugees

*(Commissioned by Bill on 2026-10-16 as `include.access--inclusion-of-refugees-and-idps`, a first pass under `maturity/documentation/first-pass-batch.md`, in one batch with feedbackportals, eparticipation, gendergap, disabilityaccess, refugees and digitaldivides: the chapter Inclusion.)*

## 1. What is assessed

**Registration and digital inclusion of refugees and internally displaced people**: the registers and identity documents refugees, asylum seekers and internally displaced people are given, and their access to SIM cards, mobile money, bank accounts and digital ID. What registers or documents the displaced, or opens digital services to them, counts, whatever it is called.

The study redraws `include.access--inclusion-of-refugees-and-idps`, which as at 2026-08-31 puts 17 countries at stage 3, 13 at 2, one at 1 and 18 unplaced. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| Refugees and displaced people | Inclusion of refugees and IDPs: refugees and displaced people | `include.access--inclusion-of-refugees-and-idps-refugees-and-displaced-people` |

Anything else the evidence names is `other`, noted and never staged: aid, food or shelter with no registration or digital service, returnees or citizens abroad, a count of displaced people with no registration, a donor's statement of intent, a camp's health or school services.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Is registration or digital inclusion under way? | A source from the last three years says the government or UNHCR planned, began or resumed registering or documenting refugees or internally displaced people, or piloted a digital service for them, such as cash transfers by phone |
| 2 | Are they registered and documented? | A source from the last three years says refugees or internally displaced people have been registered, biometrically or otherwise, and issued identity documents, with a number stated |
| 3 | Can they use digital services? | A source from the last three years says refugees or internally displaced people may register SIM cards, open mobile money or bank accounts, or enrol in the national digital ID, by law or in practice |
| 4 | Is their digital inclusion counted? | A source from the last three years gives the number or share of refugees or displaced people with a registered SIM, a mobile money or bank account, or a national digital ID |

## 3. The ladders

**Refugees and displaced people**

| Stage | Answers |
|---|---|
| 1 Absent | A source from the past three years says refugees or internally displaced people are not registered, hold no documents, are barred from SIM cards, mobile money or digital ID, or that their registration is suspended. |
| 2 Under way | Yes to 1 |
| 3 Registered | Yes to 2 |
| 4 Digital access | Yes to 3 |
| 5 Counted | Yes to 4 |

A later yes answers the earlier ones (method §3.3). `study.json` holds this as three aspects: `registration` (`documented`, `underway`, `none`) for stage 1 and questions 1 and 2, `access` (`open`) for 3 and `counted` (`counted`) for 4.

## 4. The norm

The Kampala Convention asks for registers and documents for internally displaced people; the Global Digital Compact and UNHCR ask for their digital inclusion. This study asks the four questions above; it does not measure a country against the norm.

## 5. What the run reads

- **Carried**: nothing; no earlier study holds facts on these questions.
- **Read**: **179 story readings about the subject**, published since October 2023, in at most 20 stories a country: 9 in the batch's shared calls (4 calls over 17 stories), read once for every study that lists them, and 170 in 53 calls of its own. A story published before the three-year window can set no stage, and the twenty are each country's best ranked across the batch (`study-calls.py --batch … --cap 20`).
- **Not read**: the rest of the 2,022 documents this study lists, instruments, long reports, passing mentions and the documents the row's current cells cite. No web search and no handover to OSINT. A question nothing answers is printed as *Not held*.

## 6. Token ceiling

**15 million** for this study; **90 million** for the batch, checked with `study-tokens.py` after every fan-out.

## 7. Tasks, in order

- [x] **D0. Prepared**: this file, `study.json` and the reading lists, 2026-10-16.
- [x] **D1. Read**, 2026-10-16: Sonnet drafters, self-contained calls; corrections in `corrections.csv`.
- [x] **D2. Staged** as at 2026-09-30: 3 at 5, 5 at 4, 16 at 3, 8 at 2, 4 at 1; unplaced 2, no evidence 16. Every cell is a first pass; no second drafter.
- [x] **D3. Written, rendered and linted**; on the soft-launch map. Reported to Bill.

**Decided in the run**: Nothing removed.

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
