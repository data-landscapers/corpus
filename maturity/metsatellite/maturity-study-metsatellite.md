---
type: task
reader: cc
title: maturity-study-metsatellite.md — satellite data in the national weather service, in four questions
last_reviewed: 2026-10-16
status: first pass run 2026-10-16; staged, written and on the soft-launch map; waits for Bill's acceptance
---

# Maturity study: metsatellite

*(Commissioned by Bill on 2026-10-16 as `data.satellite--meteorological-use-of-satellite-data`, a first pass under `maturity/documentation/first-pass-batch.md`, in one batch with agrisatellite, metsatellite, digitalsovereignty, healthmis, educationmis, egovservices and ruralelectrification: the chapter the last seven indicators.)*

## 1. What is assessed

**Satellite data in the national weather service**: the national meteorological service's reception of satellite data and its use in forecasts and warnings. What brings satellite data into national weather forecasting counts, whatever it is called.

The study redraws `data.satellite--meteorological-use-of-satellite-data`, which as at 2026-08-31 puts four countries at stage 3, three at 2 and 47 unplaced. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| Satellite data in weather services | Meteorological use of satellite data: satellite data in weather services | `data.satellite--meteorological-use-of-satellite-data` |

Anything else the evidence names is `other`, noted and never staged: a ground weather station or radar with no satellite data, a farming service using satellite maps, a satellite launch or a space agency, a mobile operator's weather app, a regional centre's product with no national use on record.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Does the weather service receive satellite data? | A source from the last three years says the national meteorological service has a satellite receiving station or data stream installed, contracted or being upgraded |
| 2 | Does it use it in forecasts? | A source from the last three years says the national meteorological service uses satellite data in its forecasts or nowcasting |
| 3 | Does it issue warnings from it? | A source from the last three years says the national meteorological service issues early warnings or impact-based forecasts that draw on satellite data |
| 4 | Is the service ISO 9001-certified? | A source from the last three years says the national meteorological service holds ISO 9001 certification for its services |

## 3. The ladders

**Satellite data in weather services**

| Stage | Answers |
|---|---|
| 1 Absent | A source from the past three years says the national weather service receives no satellite data. |
| 2 Receiving | Yes to 1 |
| 3 Used in forecasts | Yes to 2 |
| 4 Warnings issued | Yes to 3 |
| 5 Certified | Yes to 4 |

A later yes answers the earlier ones (method §3.3). `study.json` holds this as three aspects: `stream` (`inservice`, `underway`, `none`) for stage 1 and questions 1 and 2, `warnings` (`issued`) for 3 and `certified` (`certified`) for 4.

## 4. The norm

The Integrated African Strategy on Meteorology asks for sustained access to geostationary and polar-orbiting satellites, WMO's observing standards and ISO 9001 certification for every national weather service. This study asks the four questions above; it does not measure a country against the norm.

## 5. What the run reads

- **Carried**: nothing; no earlier study holds facts on these questions.
- **Read**: **73 story readings about the subject**, published since October 2023, in at most 20 stories a country: 13 in the batch's shared calls (8 calls over 36 stories), read once for every study that lists them, and 60 in 25 calls of its own. A story published before the three-year window can set no stage, and the twenty are each country's best ranked across the batch (`study-calls.py --batch … --cap 20`).
- **Not read**: the rest of the 279 documents this study lists, instruments, long reports, passing mentions and the documents the row's current cells cite. A question nothing answers is printed as *Not held*.

## 6. Token ceiling

**12 million** for this study; **75 million** for the batch, checked with `study-tokens.py` after every fan-out.

## 7. Tasks, in order

- [x] **D0. Prepared**: this file, `study.json` and the reading lists, 2026-10-16.
- [x] **D1. Read**, 2026-10-16: Sonnet drafters, self-contained calls; corrections in `corrections.csv`.
- [x] **D2. Staged** as at 2026-09-30: 5 at 4, 2 at 3, 10 at 2; unplaced 0, no evidence 37. Every cell is a first pass; no second drafter.
- [x] **D3. Written, rendered and linted**; on the soft-launch map. Reported to Bill.

**Decided in the run**: Nothing removed.

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
