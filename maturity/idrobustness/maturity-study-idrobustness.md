---
type: task
reader: cc
title: maturity-study-idrobustness.md — the national ID system and how sound it is, in four questions
last_reviewed: 2026-10-16
status: first pass run 2026-10-16; staged, written and on the soft-launch map; waits for Bill's acceptance
---

# Maturity study: idrobustness

*(Commissioned by Bill on 2026-10-16 as `dpi.id--robustness-of-system`, a first pass under `maturity/documentation/first-pass-batch.md`, in one batch with idrobustness, idcoverage, idmaintenance, authentication, idfrombirth, birthidlink and idregisters: the topic Digital Identity and CRVS.)*

## 1. What is assessed

**The national identity system: the register and credential that give each resident a unique identity**, under whatever name: a national ID card, a national identification number, a digital ID. What issues one unique identity per person counts.

The study redraws `dpi.id--robustness-of-system`, which as at 2026-08-31 puts 32 countries at stage 3, 18 at 2 and four unplaced. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| Robustness of system | Robustness of system: robustness of system | `dpi.id--robustness-of-system` |

Anything else the evidence names is `other`, noted and never staged: a voter card, a passport, a sectoral ID (health, social, student), a civil register of births and deaths on its own, a law with no system.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Is a national ID system under way? | A source from the last three years says one is procured, being built or piloted, or is ready and waiting on its law |
| 2 | Is it in service? | A source from the last three years says the system is issuing credentials or numbers that are unique to each person |
| 3 | Does it check people by biometrics? | A source from the last three years says it checks fingerprints, face or iris to stop one person enrolling twice |
| 4 | Is its security certified or audited? | A source from the last three years reports a security certification (such as ISO 27001), a published audit, or a level of assurance set for the system |

## 3. The ladders

**Robustness of system**

| Stage | Answers |
|---|---|
| 1 Absent | A source from the past three years says there is no national ID system, or only a paper one with no unique number. |
| 2 Under way | Yes to 1 |
| 3 In service | Yes to 2 |
| 4 Biometric checks | Yes to 3 |
| 5 Certified | Yes to 4 |

A later yes answers the earlier ones (method §3.3). `study.json` holds this as three aspects: `system` (`inservice`, `underway`, `none`) for stage 1 and questions 1 and 2, `biometric` (`checked`) for 3 and `assurance` (`certified`) for 4.

## 4. The norm

The African Union's interoperability framework asks that a national ID system have technical integrity: unique identities, defined levels of assurance and security baselines that others can trust. This study asks the four questions above; it does not measure a country against the norm.

## 5. What the run reads

- **Carried**: nothing; no earlier study holds facts on these questions.
- **Read**: **634 news stories about the subject**, published since October 2023, in at most 15 a country: 592 in the batch's 149 shared calls, read once for every study that lists them, and 42 in 32 calls of its own. A story published before the three-year window can set no stage, and the fifteen are each country's best ranked across the batch (`study-calls.py --batch … --cap 15`).
- **Not read**: the rest of the 2,421 stories in the window, instruments, long reports, passing mentions and the documents the row's current cells cite. A question nothing answers is printed as *Not held*.

## 6. Token ceiling

**10 million** for this study; **70 million** for the batch, checked with `study-tokens.py` after every fan-out.

## 7. Tasks, in order

- [x] **D0. Prepared**: this file, `study.json` and the reading lists, 2026-10-16.
- [x] **D1. Read**, 2026-10-16: the batch's shared calls and this study's own, Sonnet drafters; 468 facts after the parent's corrections (`corrections.csv`).
- [x] **D2. Staged** as at 2026-09-30: 2 at 5, 10 at 4, 39 at 3, 2 at 2; unplaced 0, no evidence 1. Every cell is a first pass; no second drafter.
- [x] **D3. Written, rendered and linted**, by `study-first-write.py`; on the soft-launch map. Reported to Bill.

**Decided in the run**: Removed: Mauritius's rule requiring an audit every three years, which is not an audit on record.

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
