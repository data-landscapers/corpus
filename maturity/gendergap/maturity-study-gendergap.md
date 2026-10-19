---
type: task
reader: cc
title: maturity-study-gendergap.md — the gender gap in internet use, from the held ITU series
last_reviewed: 2026-10-16
status: first pass run 2026-10-16; staged, written and on the soft-launch map; waits for Bill's acceptance
---

# Maturity study: gendergap

*(Commissioned by Bill on 2026-10-16 as `include.access--gender-equity`, a first pass under `maturity/documentation/first-pass-batch.md`, in one batch with feedbackportals, eparticipation, gendergap, disabilityaccess, refugees and digitaldivides: the chapter Inclusion. A measure, staged from the held series as `schoolinternet` was, by `study_figure.py`.)*

## 1. What is assessed

**How far women's internet use falls short of men's.** The figure is the gap in internet use, men's rate less women's as a share of men's, from ITU's series by sex (`itu-internet-use-gender-gap` in `reference/measures.csv`), the frame row's own value, or from a national household survey a story reports.

The study redraws `include.access--gender-equity`, which as at 2026-08-31 puts nine countries at stage 4, five at 3, five at 2, five at 1 and 30 unplaced. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| Gender gap in internet use | Gender equity: gender gap in internet use | `include.access--gender-equity` |

Anything else the evidence names is `other`, noted and never staged: a gap in phone ownership, GSMA's mobile internet gender gap (a different definition), a figure for one city or group, a programme for women with no figure.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Is the gap 30 per cent or less? | The latest figure, for 2023 or later, is 30 or less |
| 2 | 20 or less? | That figure is 20 or less |
| 3 | 10 or less? | That figure is 10 or less |
| 4 | Is there parity? | That figure is 2 or less |

## 3. The ladders

**Gender gap in internet use**

| Stage | Answers |
|---|---|
| 1 Wide gap | The latest figure, for 2023 or later, is above 30 |
| 2 | Yes to 1 |
| 3 | Yes to 2 |
| 4 | Yes to 3 |
| 5 Parity | Yes to 4 |

- **The lines are the frame's own provisional cuts** (`lookups/maturity-measures.csv`, direction lower), fixed and not redrawn as quintiles.
- **A rise is a rise**: the latest figure sets the stage. No figure for 2023 or later is *unplaced*; none at all is *No evidence*. A figure below zero, women's use the higher, counts as parity.

`study.json` holds this as one aspect, `gap`, whose value is the figure (`official:…`).

## 4. The norm

The Maputo Protocol asks for women's access to and control of information technologies on equal terms; the Digital Transformation Strategy asks for digital skills for women and girls. The lines are the frame's; this study does not measure a country against the norm.

## 5. What the run reads

- **Carried**: the series for 26 countries, 28 figures since 2021, by `study-figure.py gendergap carry`; no document opened. Six countries hold a figure for 2023 or later: BWA, CIV, KEN, MUS, MWI and UGA.
- **Read**: **20 story readings** about the gap, published since October 2023, for a national survey figure the series lacks: 5 in the batch's shared calls and 15 in 9 calls of its own.
- **Not read**: the rest of the 819 documents this study lists.

## 6. Token ceiling

**5 million** for this study; **90 million** for the batch, checked with `study-tokens.py` after every fan-out.

## 7. Tasks, in order

- [x] **D0. Prepared**: this file, `study.json`, the reading lists and the carried figures, 2026-10-16.
- [x] **D1. Read**, 2026-10-16: Sonnet drafters, self-contained calls; corrections in `corrections.csv`.
- [x] **D2. Staged** as at 2026-09-30: 1 at 5, 2 at 4, 3 at 3, 1 at 2; unplaced 19, no evidence 28. Every cell is a first pass; no second drafter.
- [x] **D3. Written, rendered and linted**; on the soft-launch map. Reported to Bill.

**Decided in the run**: Nothing removed; Lesotho's 8.5 per cent comes from its 2023 household survey (59.9 per cent of men online, 54.8 of women), which the ITU series lacks. A gap below zero, with women's use higher, counts as parity.

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
