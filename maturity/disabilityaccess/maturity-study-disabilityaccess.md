---
type: task
reader: cc
title: maturity-study-disabilityaccess.md — information and digital services made accessible to persons with disabilities, in four questions
last_reviewed: 2026-10-16
status: first pass run 2026-10-16; staged, written and on the soft-launch map; waits for Bill's acceptance
---

# Maturity study: disabilityaccess

*(Commissioned by Bill on 2026-10-16 as `include.access--inclusion-of-persons-with-disabilities`, a first pass under `maturity/documentation/first-pass-batch.md`, in one batch with feedbackportals, eparticipation, gendergap, disabilityaccess, refugees and digitaldivides: the chapter Inclusion.)*

## 1. What is assessed

**Access to information and digital services for persons with disabilities**: a law, policy, standard or programme that makes public information, websites, digital services or devices accessible to people with disabilities, through accessible formats, screen readers, sign language or assistive technology. What makes information and digital services accessible to persons with disabilities counts, whatever it is called.

The study redraws `include.access--inclusion-of-persons-with-disabilities`, which as at 2026-08-31 puts 13 countries at stage 3, 23 at 2, two at 1 and 15 unplaced. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| Digital accessibility | Inclusion of persons with disabilities: digital accessibility | `include.access--inclusion-of-persons-with-disabilities-digital-accessibility` |

Anything else the evidence names is `other`, noted and never staged: a disability law or programme with nothing on information, communication or technology, physical access to buildings, a disability grant or job quota, a charity's device donation with no government part, an awareness day or event.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Is digital accessibility under way? | A source from the last three years says a government body has drafted, launched or is preparing a law, policy, standard or programme to make information or digital services accessible to persons with disabilities |
| 2 | Is a rule in force? | A source from the last three years says a law, regulation, policy or standard in force requires public information, websites or digital services to be accessible to persons with disabilities |
| 3 | Is it delivered? | A source from the last three years says a government body delivered accessible digital services, assistive technology or devices to persons with disabilities, or made public websites or broadcasts accessible, naming the service or a number reached |
| 4 | Is accessibility audited? | A source from the last three years gives the results of an audit or survey of how accessible public websites or digital services are to persons with disabilities |

## 3. The ladders

**Digital accessibility**

| Stage | Answers |
|---|---|
| 1 Absent | A source from the past three years says no law or policy addresses access to information or digital services for persons with disabilities. |
| 2 Under way | Yes to 1 |
| 3 Rule in force | Yes to 2 |
| 4 Delivered | Yes to 3 |
| 5 Audited | Yes to 4 |

A later yes answers the earlier ones (method §3.3). `study.json` holds this as three aspects: `rule` (`inforce`, `underway`, `none`) for stage 1 and questions 1 and 2, `delivered` (`delivered`) for 3 and `audit` (`published`) for 4.

## 4. The norm

The AU Disability Protocol asks for public information in accessible formats and technologies and for affordable devices; the UN CRPD asks the same of states. This study asks the four questions above; it does not measure a country against the norm.

## 5. What the run reads

- **Carried**: nothing; no earlier study holds facts on these questions.
- **Read**: **178 story readings about the subject**, published since October 2023, in at most 20 stories a country: 13 in the batch's shared calls (4 calls over 17 stories), read once for every study that lists them, and 165 in 58 calls of its own. A story published before the three-year window can set no stage, and the twenty are each country's best ranked across the batch (`study-calls.py --batch … --cap 20`).
- **Not read**: the rest of the 2,389 documents this study lists, instruments, long reports, passing mentions and the documents the row's current cells cite. No web search and no handover to OSINT. A question nothing answers is printed as *Not held*.

## 6. Token ceiling

**15 million** for this study; **90 million** for the batch, checked with `study-tokens.py` after every fan-out.

## 7. Tasks, in order

- [x] **D0. Prepared**: this file, `study.json` and the reading lists, 2026-10-16.
- [x] **D1. Read**, 2026-10-16: Sonnet drafters, self-contained calls; corrections in `corrections.csv`.
- [x] **D2. Staged** as at 2026-09-30: 1 at 5, 10 at 4, 1 at 3, 10 at 2, 2 at 1; unplaced 3, no evidence 27. Every cell is a first pass; no second drafter.
- [x] **D3. Written, rendered and linted**; on the soft-launch map. Reported to Bill.

**Decided in the run**: Four facts removed as not delivery of accessibility: an NGO's project in Burkina Faso, Braille ballot jackets in Zambia, a teachers' workshop and laptops for bursary holders in Zimbabwe.

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
