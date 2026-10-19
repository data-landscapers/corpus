---
type: task
reader: cc
title: maturity-study-policyresearch.md — think tanks and universities researching digital policy, in four questions
last_reviewed: 2026-10-16
status: first pass run 2026-10-16; staged, written and on the soft-launch map; waits for Bill's acceptance
---

# Maturity study: policyresearch

*(Commissioned by Bill on 2026-10-16 as `capacity.research--think-tanks-and-academic-departments-contributing-to-dt-policy`, a first pass under `maturity/documentation/first-pass-batch.md`, in one batch with civilserviceskills, digitalskills, policyresearch, schoolinternet, stemgraduates and ictjobs: the chapter Capacity.)*

## 1. What is assessed

**Research on digital policy in the country**: a think tank, university centre or department, or research network based in the country that researches and publishes on digital transformation, technology or internet policy. What researches digital policy in the country counts, whatever it is called.

The study redraws `capacity.research--think-tanks-and-academic-departments-contributing-to-dt-policy`, which as at 2026-08-31 puts five countries at stage 3, 37 at 2 and 12 unplaced. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| Digital policy research | Think tanks and academic departments contributing to DT policy: digital policy research | `capacity.research--think-tanks-and-academic-departments-contributing-to-dt-policy` |

Anything else the evidence names is `other`, noted and never staged: a degree or training course with no research, a company's market report, a foreign body's study with no local institution named, a hackathon or conference with no research, a policy written by government alone.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Has research on digital policy begun? | A source from the last three years says a local institution has held a research workshop, opened a chair, centre or project on digital policy, or joined a research network on it |
| 2 | Does a local institution publish on it? | A source from the last three years says a local think tank, university centre or department has published research on digital policy, such as a report, study or index |
| 3 | Has local research fed a policy process? | A source from the last three years says a local institution submitted evidence to a consultation, was commissioned by government for a study, or sits on an advisory body, on a digital policy, law or strategy |
| 4 | Is the role standing? | A source from the last three years says a local research institution holds a standing advisory role in digital policy, or a national research agenda on digital transformation is adopted |

## 3. The ladders

**Digital policy research**

| Stage | Answers |
|---|---|
| 1 Absent | A source from the past three years says no local institution researches digital policy. |
| 2 Begun | Yes to 1 |
| 3 Publishing | Yes to 2 |
| 4 Feeding policy | Yes to 3 |
| 5 Standing role | Yes to 4 |

A later yes answers the earlier ones (method §3.3). `study.json` holds this as three aspects: `research` (`publishing`, `begun`, `none`) for stage 1 and questions 1 and 2, `policy` (`contributed`) for 3 and `standing` (`standing`) for 4.

## 4. The norm

STISA-2034 and Agenda 2063's second ten-year plan ask for research systems funded toward 1 per cent of GDP and contributing to policy; neither counts think tanks. This study asks the four questions above; it does not measure a country against the norm.

## 5. What the run reads

- **Carried**: nothing; no earlier study holds facts on these questions.
- **Read**: **270 story readings about the subject**, published since October 2023, in at most 20 stories a country: 6 in the batch's shared calls (49 calls over 243 stories), read once for every study that lists them, and 264 in 71 calls of its own. A story published before the three-year window can set no stage, and the twenty are each country's best ranked across the batch (`study-calls.py --batch … --cap 20`).
- **Not read**: the rest of the 2,873 documents this study lists, instruments, long reports, passing mentions and the documents the row's current cells cite. A question nothing answers is printed as *Not held*.

## 6. Token ceiling

**20 million** for this study; **70 million** for the batch, checked with `study-tokens.py` after every fan-out.

## 7. Tasks, in order

- [x] **D0. Prepared**: this file, `study.json` and the reading lists, 2026-10-16.
- [x] **D1. Read**, 2026-10-16: Sonnet drafters, self-contained calls; corrections in `corrections.csv`.
- [x] **D2. Staged** as at 2026-09-30: 2 at 4, 7 at 3, 2 at 2; unplaced 0, no evidence 43. Every cell is a first pass; no second drafter.
- [x] **D3. Written, rendered and linted**; on the soft-launch map. Reported to Bill.

**Decided in the run**: Nothing removed.

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
