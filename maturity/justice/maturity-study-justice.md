---
type: task
reader: cc
title: maturity-study-justice.md — courts run on a case management system, in four questions
last_reviewed: 2026-10-16
status: first pass run 2026-10-16; staged, written and on the soft-launch map; waits for Bill's acceptance
---

# Maturity study: justice

*(Commissioned by Bill on 2026-10-16 as `dpi.mis--justice`, a first pass under `maturity/documentation/first-pass-batch.md`, in one batch with socialprotection, justice, taxadmin, customs and landadmin: the topic Sectoral management information systems.)*

## 1. What is assessed

**The system courts manage their cases on**: registering cases, scheduling them and keeping their records electronically. What manages court cases counts, whatever it is called.

The study redraws `dpi.mis--justice`, which as at 2026-08-31 puts 17 countries at stage 3, 20 at 2, two at 1 and 14 unplaced. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| Justice | Justice: justice | `dpi.mis--justice-justice` |

Anything else the evidence names is `other`, noted and never staged: a police or prison system with no court system named, a justice reform or law with no system, hearings by video alone, a legal-information site run privately.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Is a court case management system under way? | A source from the last three years says a case management or e-justice system is procured, piloted in some courts or being built |
| 2 | Do courts manage cases electronically? | A source from the last three years says a case management system is in service in some courts or one tier |
| 3 | Can cases be filed online? | A source from the last three years says lawyers or litigants can file cases or documents with the courts online |
| 4 | Are judgments or case status open online? | A source from the last three years says court decisions are published online or the public can look up a case's status online |

## 3. The ladders

**Justice**

| Stage | Answers |
|---|---|
| 1 Paper | A source from the past three years says court proceedings and records are on paper with no case management system. |
| 2 Under way | Yes to 1 |
| 3 In service | Yes to 2 |
| 4 Online filing | Yes to 3 |
| 5 Open online | Yes to 4 |

A later yes answers the earlier ones (method §3.3). `study.json` holds this as three aspects: `cases` (`inservice`, `underway`, `none`) for stage 1 and questions 1 and 2, `filing` (`online`) for 3 and `public` (`open`) for 4.

## 4. The norm

The African Commission's Fair Trial Principles ask for systems recording proceedings and storing court information, with public access to decisions. This study asks the four questions above; it does not measure a country against the norm.

## 5. What the run reads

- **Carried**: nothing; no earlier study holds facts on these questions.
- **Read**: **42 story readings about the subject**, published since October 2023, in at most 20 stories a country: 2 in the batch's three shared calls (13 stories), read once for every study that lists them, and 40 in 24 calls of its own. A story published before the three-year window can set no stage, and the twenty are each country's best ranked across the batch (`study-calls.py --batch … --cap 20`).
- **Not read**: the rest of the 620 documents this study lists, instruments, long reports, passing mentions and the documents the row's current cells cite. A question nothing answers is printed as *Not held*.

## 6. Token ceiling

**8 million** for this study; **40 million** for the batch, checked with `study-tokens.py` after every fan-out.

## 7. Tasks, in order

- [x] **D0. Prepared**: this file, `study.json` and the reading lists, 2026-10-16.
- [x] **D1. Read**, 2026-10-16: the batch's shared calls and this study's own, Sonnet drafters; 38 facts after the parent's corrections (`corrections.csv`).
- [x] **D2. Staged** as at 2026-09-30: 2 at 5, 7 at 3, 8 at 2; unplaced 1, no evidence 36. Every cell is a first pass; no second drafter.
- [x] **D3. Written, rendered and linted**, by `study-first-write.py`; on the soft-launch map. Reported to Bill.

**Decided in the run**: Nothing removed at the top-stage check.

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
