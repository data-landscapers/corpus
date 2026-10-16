---
type: task
reader: cc
title: maturity-study-healthexchange.md — health information systems exchanging data, in four questions
last_reviewed: 2026-10-16
status: first pass run 2026-10-16; staged, written and on the soft-launch map; waits for Bill's acceptance
---

# Maturity study: healthexchange

*(Commissioned by Bill on 2026-10-16 as `dpi.exchange--interoperability-of-health-systems`, a first pass under `maturity/documentation/first-pass-batch.md`, in one batch with dataexchange, idverification, healthexchange, educationexchange and socialexchange.)*

## 1. What is assessed

**Data passing between two or more health information systems**: the HMIS with patient records, laboratory, supply chain, surveillance or insurance systems; a health information exchange; a client or facility registry that several systems use. What moves health data between systems counts, whatever the product.

The study redraws `dpi.exchange--interoperability-of-health-systems`, which as at 2026-08-31 puts five countries at stage 3, 36 at 2 and 13 unplaced. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| Interoperability of health systems | Interoperability of health systems: interoperability of health systems | `dpi.exchange--interoperability-of-health-systems-interoperability-of-health-systems` |

Anything else the evidence names is `other`, noted and never staged: a single system on its own (the health study holds those), a policy, architecture or standard with no exchange in service, a dashboard drawing on one system, telemedicine, a donor's reporting link to its own platform.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Is an exchange between health systems under way? | A source from the last three years says one is contracted, being built or piloted, or a health information exchange is being set up |
| 2 | Do two health systems exchange data in service? | A source from the last three years says two or more health systems exchange data in routine use |
| 3 | Does the exchange reach across the health system? | A source from the last three years says three or more health systems exchange data, or a national health information exchange is in service |
| 4 | Are patients matched by a national identifier? | A source from the last three years says patient records are linked through the national ID or a national unique health identifier used across systems |

## 3. The ladders

**Interoperability of health systems**

| Stage | Answers |
|---|---|
| 1 Absent | A source from the last three years says it is absent |
| 2 Under way | Yes to 1 |
| 3 In service | Yes to 2 |
| 4 Across the system | Yes to 3 |
| 5 Patients matched | Yes to 4 |

A later yes answers the earlier ones (method §3.3). `study.json` holds this as three aspects: `exchange` (`inservice`, `underway`, `none`) for questions 1 and 2, `breadth` (`wide`) for 3 and `identifier` (`linked`) for 4. **For the drafter**: the system's name goes in `system`, the bodies or systems it links in the fact.

## 4. The norm

Africa CDC's health information exchange guidelines and Smart Africa's digital health blueprint ask for a national exchange policy, common standards and identifiers, then exchanges in service across the health system. This study asks the four questions above; it does not measure a country against the norm.

## 5. What the run reads

- **Carried**: nothing; no earlier study holds facts on these questions.
- **Read**: **33 news stories about the subject that no study has read**, in 18 countries; then the 184 documents the row's current cells cite, in 52 countries. 79 calls of its own, besides the batch's 19 shared calls over 84 stories read once for two studies or more.
- **Not read**: instruments, long reports and passing mentions. No web search and no handover to OSINT. A question nothing answers is printed as *Not held*.

## 6. Token ceiling

**40 million** for this study; **200 million** for the batch, checked with `study-tokens.py` after every fan-out.

## 7. Tasks, in order

- [x] **D0. Prepared**: this file, `study.json` and the reading lists, 2026-10-16.
- [x] **D1. Read**, 2026-10-16: the batch's 19 shared calls and this study's own, Sonnet drafters; 110 facts after the parent's corrections (`corrections.csv`).
- [x] **D2. Staged** as at 2026-09-30: 1 at 5, 4 at 4, 16 at 3, 15 at 2, 2 at 1; unplaced 0, no evidence 16. Every cell is a first pass; no second drafter.
- [x] **D3. Written, rendered and linted**, by `study-first-write.py`; on the soft-launch map. Reported to Bill. Batch tokens 203M of 200M, the reading of all five studies.

**Decided in the run**: Côte d'Ivoire's 2024 decree naming the health insurance number as the health identifier is removed as patients matched: a decree is not records linked in service.

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
