---
type: task
reader: cc
title: maturity-study-ruralelectrification.md — rural access to electricity, from the held World Bank series
last_reviewed: 2026-10-16
status: first pass run 2026-10-16; staged, written and on the soft-launch map; waits for Bill's acceptance
---

# Maturity study: ruralelectrification

*(Commissioned by Bill on 2026-10-16 as `infra.energy--rural-electrification`, a first pass under `maturity/documentation/first-pass-batch.md`, in one batch with agrisatellite, metsatellite, digitalsovereignty, healthmis, educationmis and egovservices: the last seven indicators. A measure, staged from the held series as `gendergap` was, by `study_figure.py`. It replaces the four-question version prepared on 2026-10-10, which was never run.)*

## 1. What is assessed

**The share of rural people with electricity.** The figure is the World Bank's rural access series (`wdi-elc-accs-rural` in `reference/measures.csv`, EG.ELC.ACCS.RU.ZS), the frame row's own value.

The study redraws `infra.energy--rural-electrification`, which as at 2026-08-31 has no cells. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| Rural access to electricity | Rural electrification: rural access to electricity | `infra.energy--rural-electrification-rural-access-to-electricity` |

## 2. The questions

| # | Question | A yes is |
|---|---|---|
| 1 | Do 27 per cent or more of rural people have electricity? | The latest figure, for 2023 or later, is 27 or more |
| 2 | 53 or more? | That figure is 53 or more |
| 3 | 80 or more? | That figure is 80 or more |
| 4 | 95 or more? | That figure is 95 or more: universal access |

## 3. The ladders

**Rural access to electricity**

| Stage | Answers |
|---|---|
| 1 Low | The latest figure, for 2023 or later, is below 27 |
| 2 | Yes to 1 |
| 3 | Yes to 2 |
| 4 | Yes to 3 |
| 5 Universal | Yes to 4 |

- **The lines are the frame's own cuts** (`lookups/maturity-measures.csv`, direction higher), fixed and not redrawn as quintiles.
- **A fall is a fall**: the latest figure sets the stage. No figure for 2023 or later is *unplaced*.

`study.json` holds this as one aspect, `access`, whose value is the figure (`official:…`).

## 4. The norm

The African Union's Agenda 2063 first ten-year plan asks for 80% of households to have electricity; Mission 300 aims to connect 300 million Africans by 2030. The lines are the frame's; this study does not measure a country against the norm.

## 5. What the run reads

- **Carried**: the series for 54 countries, 206 figures since 2021, by `study-figure.py ruralelectrification carry`; no document opened. 52 countries hold a figure for 2024; Libya and Mauritania hold only 2012.
- **Read**: nothing. With a 2024 figure for 52 countries, no story is read.
- **Not read**: the 2,110 documents this study lists.

## 6. Token ceiling

**1 million** for this study; **75 million** for the batch.

## 7. Tasks, in order

- [x] **D0. Prepared**: this file, `study.json`, the reading lists and the carried figures, 2026-10-16.
- [x] **D1. Read**: nothing to read.
- [x] **D2. Staged** as at 2026-09-30: 8 at 5, 4 at 4, 6 at 3, 17 at 2, 17 at 1; unplaced 2. Every cell is a first pass.
- [x] **D3. Written, rendered and linted**; on the soft-launch map. Reported to Bill.

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
