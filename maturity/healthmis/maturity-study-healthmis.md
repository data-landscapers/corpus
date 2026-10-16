---
type: task
reader: cc
title: maturity-study-healthmis.md — the national health information system, in four questions
last_reviewed: 2026-10-16
status: first pass run 2026-10-16; staged, written and on the soft-launch map; waits for Bill's acceptance
---

# Maturity study: healthmis

*(Commissioned by Bill on 2026-10-16 as `dpi.mis--health`, a first pass under `maturity/documentation/first-pass-batch.md`, in one batch with agrisatellite, metsatellite, digitalsovereignty, healthmis, educationmis, egovservices and ruralelectrification: the chapter the last seven indicators.)*

## 1. What is assessed

**The national health management information system**: the system through which health facilities and districts report patients seen, services given and stock, to the health ministry, often DHIS2. What carries routine health reporting from across the country to the ministry digitally counts, whatever it is called; a system serving one facility or district alone does not.

The study redraws `dpi.mis--health`, which as at 2026-08-31 puts 13 countries at stage 3, five at 2 and 36 unplaced. The `health` study claimed the row until 2026-10-16 but staged only rural clinics; this study asks about the national system *(Bill)*. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| Health information system | Health: health information system | `dpi.mis--health-health-information-system` |

Anything else the evidence names is `other`, noted and never staged: a system run by one hospital, clinic or district on its own, a patient record at one hospital, a telemedicine app, a health insurance system, a donor's project database, a laboratory or vaccine-stock system with no link to routine reporting on record.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Is a health information system under way? | A source from the last three years says the health ministry procured, piloted or is rolling out a health management information system, or one is in use in some districts |
| 2 | Is a national one in service? | A source from the last three years says a national health management information system is in service, with facilities or districts across the country reporting through it |
| 3 | Is it linked to other health systems? | A source from the last three years says the system is linked to, or exchanges data with, disease surveillance, the medicines supply chain, or a patient or immunisation register |
| 4 | Is its reporting rate published? | A source from the last three years gives the reporting completeness or timeliness of the national system, as a share of reports due |

## 3. The ladders

**Health information system**

| Stage | Answers |
|---|---|
| 1 Absent | A source from the past three years says health reporting is on paper and there is no national health information system. |
| 2 Under way | Yes to 1 |
| 3 National | Yes to 2 |
| 4 Linked | Yes to 3 |
| 5 Reporting rate published | Yes to 4 |

A later yes answers the earlier ones (method §3.3). `study.json` holds this as three aspects: `system` (`inservice`, `underway`, `none`) for stage 1 and questions 1 and 2, `linked` (`linked`) for 3 and `completeness` (`published`) for 4.

## 4. The norm

The Africa CDC Digital Transformation Strategy asks for national digital health systems strengthened to its Health Information Exchange Guidelines, with integrated surveillance. This study asks the four questions above; it does not measure a country against the norm.

## 5. What the run reads

- **Carried**: nothing; no earlier study holds facts on these questions.
- **Read**: **220 story readings about the subject**, published since October 2023, in at most 20 stories a country: 21 in the batch's shared calls (8 calls over 36 stories), read once for every study that lists them, and 199 in 69 calls of its own. A story published before the three-year window can set no stage, and the twenty are each country's best ranked across the batch (`study-calls.py --batch … --cap 20`).
- **Not read**: the rest of the 1,617 documents this study lists, instruments, long reports, passing mentions and the documents the row's current cells cite. No web search and no handover to OSINT. A question nothing answers is printed as *Not held*.

## 6. Token ceiling

**12 million** for this study; **75 million** for the batch, checked with `study-tokens.py` after every fan-out.

## 7. Tasks, in order

- [x] **D0. Prepared**: this file, `study.json` and the reading lists, 2026-10-16.
- [x] **D1. Read**, 2026-10-16: Sonnet drafters, self-contained calls; corrections in `corrections.csv`.
- [x] **D2. Staged** as at 2026-09-30: 11 at 5, 9 at 4, 14 at 3, 9 at 2; unplaced 1, no evidence 10. Every cell is a first pass; no second drafter.
- [x] **D3. Written, rendered and linted**; on the soft-launch map. Reported to Bill.

**Decided in the run**: Removed at the top-stage check: SOM-003, completeness in 111 facilities, not the national system; GHA-003, an application integrating surveillance protocols; no link to the national system stated; GMB-002, an MoU signed, not a link in service.

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
