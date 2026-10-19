---
type: task
reader: cc
title: maturity-study-taxadmin.md — taxes filed and paid online, in four questions
last_reviewed: 2026-10-16
status: first pass run 2026-10-16; staged, written and on the soft-launch map; waits for Bill's acceptance
---

# Maturity study: taxadmin

*(Commissioned by Bill on 2026-10-16 as `dpi.mis--tax`, a first pass under `maturity/documentation/first-pass-batch.md`, in one batch with socialprotection, justice, taxadmin, customs and landadmin: the topic Sectoral management information systems.)*

## 1. What is assessed

**The system the tax authority runs filing and payment on**: tax returns filed and taxes paid electronically. What takes returns and payments electronically counts, whatever it is called.

The study redraws `dpi.mis--tax`, which as at 2026-08-31 puts 12 countries at stage 3, 27 at 2 and 15 unplaced. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| Tax | Tax: tax | `dpi.mis--tax` |

Anything else the evidence names is `other`, noted and never staged: a taxpayer register or number alone, a tax law or rate change, electronic invoicing or fiscal tills with no filing, customs duties.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Is an electronic tax system under way? | A source from the last three years says an integrated tax administration or e-filing system is procured, piloted or being built |
| 2 | Can tax returns be filed online? | A source from the last three years says taxpayers can file returns online for at least one core tax |
| 3 | Can taxes be paid electronically? | A source from the last three years says taxes can be paid online, by bank transfer or by mobile money, through the tax authority's system |
| 4 | Is online filing mandatory or used by most? | A source from the last three years says online filing is mandatory for some taxpayers, or puts the share of returns filed online at half or more |

## 3. The ladders

**Tax**

| Stage | Answers |
|---|---|
| 1 Paper | A source from the past three years says tax returns are filed and taxes paid on paper. |
| 2 Under way | Yes to 1 |
| 3 Online filing | Yes to 2 |
| 4 Electronic payment | Yes to 3 |
| 5 Mostly online | Yes to 4 |

A later yes answers the earlier ones (method §3.3). `study.json` holds this as three aspects: `filing` (`inservice`, `underway`, `none`) for stage 1 and questions 1 and 2, `payment` (`electronic`) for 3 and `uptake` (`most`) for 4.

## 4. The norm

TADAT asks for electronic filing and payment of all core taxes, filing mandatory for designated taxpayers, with immediate confirmation. This study asks the four questions above; it does not measure a country against the norm.

## 5. What the run reads

- **Carried**: nothing; no earlier study holds facts on these questions.
- **Read**: **83 story readings about the subject**, published since October 2023, in at most 20 stories a country: 14 in the batch's three shared calls (13 stories), read once for every study that lists them, and 69 in 32 calls of its own. A story published before the three-year window can set no stage, and the twenty are each country's best ranked across the batch (`study-calls.py --batch … --cap 20`).
- **Not read**: the rest of the 1,003 documents this study lists, instruments, long reports, passing mentions and the documents the row's current cells cite. A question nothing answers is printed as *Not held*.

## 6. Token ceiling

**8 million** for this study; **40 million** for the batch, checked with `study-tokens.py` after every fan-out.

## 7. Tasks, in order

- [x] **D0. Prepared**: this file, `study.json` and the reading lists, 2026-10-16.
- [x] **D1. Read**, 2026-10-16: the batch's shared calls and this study's own, Sonnet drafters; 85 facts after the parent's corrections (`corrections.csv`).
- [x] **D2. Staged** as at 2026-09-30: 3 at 5, 11 at 4, 5 at 3, 8 at 2; unplaced 2, no evidence 25. Every cell is a first pass; no second drafter.
- [x] **D3. Written, rendered and linted**, by `study-first-write.py`; on the soft-launch map. Reported to Bill.

**Decided in the run**: Removed: an IMF target read as use (Central African Republic, which stays at 4 on other facts); non-tax fees read as taxes (Uganda); a finance law's provision read as practice (Chad).

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
