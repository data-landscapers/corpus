---
type: task
reader: cc
title: maturity-study-authentication.md — services that confirm online who a person is, in four questions
last_reviewed: 2026-10-16
status: first pass run 2026-10-16; staged, written and on the soft-launch map; waits for Bill's acceptance
---

# Maturity study: authentication

*(Commissioned by Bill on 2026-10-16 as `dpi.id--authentication`, a first pass under `maturity/documentation/first-pass-batch.md`, in one batch with idrobustness, idcoverage, idmaintenance, authentication, idfrombirth, birthidlink and idregisters: the topic Digital Identity and CRVS.)*

## 1. What is assessed

**A service that confirms electronically who a person is**: an online check of the national ID by number, biometrics or one-time code, a public key infrastructure and its certification authorities, e-signatures, a mobile ID or digital ID wallet. What lets a person prove their identity remotely counts.

The study redraws `dpi.id--authentication`, which as at 2026-08-31 puts one country at stage 4, 21 at 3, 20 at 2, one at 1 and ten unplaced. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| Authentication | Authentication: authentication | `dpi.id--authentication-authentication` |

Anything else the evidence names is `other`, noted and never staged: a password login to one website, card inspection by eye, a law allowing e-signatures with no service, a payment app's own login.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Is an authentication service under way? | A source from the last three years says an authentication, e-signature or PKI service is authorised, contracted or piloted |
| 2 | Is one in service? | A source from the last three years says one is in use: a certification authority operating, or an online check of the ID for one system |
| 3 | Do several services or channels use it? | A source from the last three years says authentication is used across services or channels: licensed trust service providers, a verification service used by several bodies, mobile ID |
| 4 | Can people prove who they are remotely with a digital ID? | A source from the last three years says a mobile ID app, digital ID wallet or signed digital credential is in service for people to prove their identity online |

## 3. The ladders

**Authentication**

| Stage | Answers |
|---|---|
| 1 Absent | A source from the past three years says no digital authentication service exists; credentials are checked by eye. |
| 2 Under way | Yes to 1 |
| 3 In service | Yes to 2 |
| 4 Across services | Yes to 3 |
| 5 Remote ID | Yes to 4 |

A later yes answers the earlier ones (method §3.3). `study.json` holds this as three aspects: `service` (`inservice`, `underway`, `none`) for stage 1 and questions 1 and 2, `reach` (`several`) for 3 and `remote` (`wallet`) for 4.

## 4. The norm

The African Union's interoperability framework and the AfCFTA Digital Trade Protocol ask for authentication and e-signature services in layers, up to remote authentication recognised across borders. This study asks the four questions above; it does not measure a country against the norm.

## 5. What the run reads

- **Carried**: 308 facts from 227 documents the idverification study read, its services checking people against the ID taken as authentication in service, and in two sectors or more as authentication across services; those documents are not read again.
- **Read**: **437 news stories about the subject**, published since October 2023, in at most 15 a country: 424 in the batch's 149 shared calls, read once for every study that lists them, and 13 in 12 calls of its own. A story published before the three-year window can set no stage, and the fifteen are each country's best ranked across the batch (`study-calls.py --batch … --cap 15`).
- **Not read**: the rest of the 2,421 stories in the window, instruments, long reports, passing mentions and the documents the row's current cells cite. A question nothing answers is printed as *Not held*.

## 6. Token ceiling

**10 million** for this study; **70 million** for the batch, checked with `study-tokens.py` after every fan-out.

## 7. Tasks, in order

- [x] **D0. Prepared**: this file, `study.json` and the reading lists, 2026-10-16.
- [x] **D1. Read**, 2026-10-16: the batch's shared calls and this study's own, Sonnet drafters; 451 facts after the parent's corrections (`corrections.csv`).
- [x] **D2. Staged** as at 2026-09-30: 8 at 5, 13 at 4, 15 at 3, 9 at 2; unplaced 2, no evidence 7. Every cell is a first pass; no second drafter.
- [x] **D3. Written, rendered and linted**, by `study-first-write.py`; on the soft-launch map. Reported to Bill.

**Decided in the run**: Removed: Algeria's regulator that will oversee e-signature providers, Seychelles' virtual card for permit holders only, and Ghana's and Tanzania's cards being required for services with no check against them stated.

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
