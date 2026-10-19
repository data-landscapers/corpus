---
type: task
reader: cc
title: maturity-study-startups.md — a startup law or strategy, applied and funded, in four questions
last_reviewed: 2026-10-16
status: first pass run 2026-10-16; staged, written and on the soft-launch map; waits for Bill's acceptance
---

# Maturity study: startups

*(Commissioned by Bill on 2026-10-16 as `tech.innovate--tech-startup-ecosystem`, a first pass under `maturity/documentation/first-pass-batch.md`, in one batch with aigovernment, aisectoral, aisystems, aiabuse, techhubs and startups: the chapter Technology.)*

## 1. What is assessed

**What the state does in law and money for tech startups**: a startup act or strategy, the labelling of startups under it, and a public or public-backed fund financing them. What the state does for startups in law or money counts, whatever it is called.

The study redraws `tech.innovate--tech-startup-ecosystem`, which as at 2026-08-31 puts nine countries at stage 3, 28 at 2 and 17 unplaced. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| Startup law and funding | Tech startup ecosystem: startup law and funding | `tech.innovate--tech-startup-ecosystem` |

Anything else the evidence names is `other`, noted and never staged: a private investor's deal with no public scheme, a hub's own programme, a general small-business scheme with no startup measures, a hackathon or prize on its own.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Is a startup law or strategy being prepared? | A source from the last three years says a startup bill is drafted or tabled, or a startup strategy is being written or in consultation |
| 2 | Is a startup law or strategy adopted? | A source from the last three years says a startup act is passed or a startup strategy adopted |
| 3 | Are startups labelled under it? | A source from the last three years says startups are labelled or registered under the act or strategy, or its tax or other measures are applied to them |
| 4 | Does a public fund finance startups under it? | A source from the last three years says a public or public-backed fund set up under the act or strategy has financed startups, with investments named or counted |

## 3. The ladders

**Startup law and funding**

| Stage | Answers |
|---|---|
| 1 Absent | A source from the past three years says no startup law, strategy or public support for startups exists. |
| 2 Draft | Yes to 1 |
| 3 Adopted | Yes to 2 |
| 4 Labelling | Yes to 3 |
| 5 Funded | Yes to 4 |

A later yes answers the earlier ones (method §3.3). `study.json` holds this as three aspects: `law` (`adopted`, `draft`, `none`) for stage 1 and questions 1 and 2, `labelled` (`labelled`) for 3 and `funded` (`funded`) for 4.

## 4. The norm

The Digital Transformation Strategy and the AU Startup Model Law Framework ask for a national startup law and strategy across seven areas, an innovation fund and angel networks. This study asks the four questions above; it does not measure a country against the norm.

## 5. What the run reads

- **Carried**: nothing; no earlier study holds facts on these questions.
- **Read**: **328 story readings about the subject**, published since October 2023, in at most 20 stories a country: 309 in the batch's shared calls (147 calls over 732 stories), read once for every study that lists them, and 19 in 17 calls of its own. A story published before the three-year window can set no stage, and the twenty are each country's best ranked across the batch (`study-calls.py --batch … --cap 20`).
- **Not read**: the rest of the 5,004 documents this study lists, instruments, long reports, passing mentions and the documents the row's current cells cite. A question nothing answers is printed as *Not held*.

## 6. Token ceiling

**14 million** for this study; **85 million** for the batch, checked with `study-tokens.py` after every fan-out.

## 7. Tasks, in order

- [x] **D0. Prepared**: this file, `study.json` and the reading lists, 2026-10-16.
- [x] **D1. Read**, 2026-10-16: the batch's shared calls and this study's own, Sonnet drafters; 40 facts after the parent's corrections (`corrections.csv`).
- [x] **D2. Staged** as at 2026-09-30: 2 at 5, 3 at 4, 9 at 3, 6 at 2; unplaced 1, no evidence 33. Every cell is a first pass; no second drafter.
- [x] **D3. Written, rendered and linted**, by `study-first-write.py`; on the soft-launch map. Reported to Bill.

**Decided in the run**: Removed: a blanket tax exemption and a law's provision with measures still drafted read as labelling (DR Congo, now 3); a donor-backed grant programme (Madagascar) and a competition prize (Mauritius) read as a fund under a startup law, both now no evidence.

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
