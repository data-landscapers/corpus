---
type: task
reader: cc
title: maturity-study-agrisatellite.md — satellite data put to use in farming, in four questions
last_reviewed: 2026-10-16
status: first pass run 2026-10-16; staged, written and on the soft-launch map; waits for Bill's acceptance
---

# Maturity study: agrisatellite

*(Commissioned by Bill on 2026-10-16 as `data.satellite--agricultural-use-of-satellite-data`, a first pass under `maturity/documentation/first-pass-batch.md`, in one batch with agrisatellite, metsatellite, digitalsovereignty, healthmis, educationmis, egovservices and ruralelectrification: the chapter the last seven indicators.)*

## 1. What is assessed

**Satellite data used for farming**: a government, agricultural research or early-warning service that uses satellite or remote-sensing data to monitor crops, forecast yields, warn of drought or locusts, or map land for agriculture. What puts satellite data to work for agriculture counts, whatever it is called.

The study redraws `data.satellite--agricultural-use-of-satellite-data`, which as at 2026-08-31 puts two countries at stage 3, nine at 2 and 43 unplaced. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| Satellite data in agriculture | Agricultural use of satellite data: satellite data in agriculture | `data.satellite--agricultural-use-of-satellite-data-satellite-data-in-agriculture` |

Anything else the evidence names is `other`, noted and never staged: weather forecasting with no farming product, mapping for a census or for cities, a satellite launch or a space agency with no farming use on record, an insurance or agritech product sold by a company with no government part, a donor study of the region.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Is satellite data being put to use in farming? | A source from the last three years says a ministry, agency or research institute used satellite or remote-sensing data in a farming study or pilot, or is preparing a service that will |
| 2 | Is a service in use? | A source from the last three years says a government crop-monitoring, drought or locust early-warning, or land-use service using satellite data is in service, for part of the country or for one purpose |
| 3 | Are its outputs published regularly? | A source from the last three years says such a service publishes bulletins, maps or forecasts on a schedule (weekly, monthly or each season) |
| 4 | Do they reach farmers? | A source from the last three years gives a number of farmers, extension workers or districts receiving advice, alerts or insurance based on the service's satellite data |

## 3. The ladders

**Satellite data in agriculture**

| Stage | Answers |
|---|---|
| 1 Absent | A source from the past three years says no farming service or institution uses satellite or remote-sensing data. |
| 2 Under way | Yes to 1 |
| 3 In service | Yes to 2 |
| 4 Published | Yes to 3 |
| 5 Reaching farmers | Yes to 4 |

A later yes answers the earlier ones (method §3.3). `study.json` holds this as three aspects: `service` (`inservice`, `underway`, `none`) for stage 1 and questions 1 and 2, `published` (`scheduled`) for 3 and `reach` (`counted`) for 4.

## 4. The norm

The African Space Strategy asks that space-derived products be used for decision-making; the AU Digital Agriculture Strategy asks for remote sensing in monitoring and forecasting. This study asks the four questions above; it does not measure a country against the norm.

## 5. What the run reads

- **Carried**: nothing; no earlier study holds facts on these questions.
- **Read**: **166 story readings about the subject**, published since October 2023, in at most 20 stories a country: 13 in the batch's shared calls (8 calls over 36 stories), read once for every study that lists them, and 153 in 53 calls of its own. A story published before the three-year window can set no stage, and the twenty are each country's best ranked across the batch (`study-calls.py --batch … --cap 20`).
- **Not read**: the rest of the 1,308 documents this study lists, instruments, long reports, passing mentions and the documents the row's current cells cite. A question nothing answers is printed as *Not held*.

## 6. Token ceiling

**12 million** for this study; **75 million** for the batch, checked with `study-tokens.py` after every fan-out.

## 7. Tasks, in order

- [x] **D0. Prepared**: this file, `study.json` and the reading lists, 2026-10-16.
- [x] **D1. Read**, 2026-10-16: Sonnet drafters, self-contained calls; corrections in `corrections.csv`.
- [x] **D2. Staged** as at 2026-09-30: 1 at 4, 8 at 3, 27 at 2; unplaced 1, no evidence 17. Every cell is a first pass; no second drafter.
- [x] **D3. Written, rendered and linted**; on the soft-launch map. Reported to Bill.

**Decided in the run**: Removed at the top-stage check: COM-002, FAO's GIEWS maps, not a government service; GNB-003, WFP's bulletin, not a government service; MWI-002, GEOCIF forecasts from an international project, not a government service; SOM-003, FSNAU is managed by FAO, not a government service; SSD-002, a World Bank-led monitor, not a government service; SSD-004, a World Bank-led monitor, not a government service.

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
