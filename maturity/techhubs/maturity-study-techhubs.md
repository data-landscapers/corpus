---
type: task
reader: cc
title: maturity-study-techhubs.md — technology hubs, incubators and parks, in four questions
last_reviewed: 2026-10-16
status: first pass run 2026-10-16; staged, written and on the soft-launch map; waits for Bill's acceptance
---

# Maturity study: techhubs

*(Commissioned by Bill on 2026-10-16 as `tech.innovate--technology-hubs`, a first pass under `maturity/documentation/first-pass-batch.md`, in one batch with aigovernment, aisectoral, aisystems, aiabuse, techhubs and startups: the chapter Technology.)*

## 1. What is assessed

**Technology hubs**: incubators, accelerators, innovation hubs and technology parks where tech startups are hosted and supported. What hosts and supports tech startups counts, whatever it is called.

The study redraws `tech.innovate--technology-hubs`, which as at 2026-08-31 puts 20 countries at stage 3, 27 at 2 and seven unplaced. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| Technology hubs | Technology hubs: technology hubs | `tech.innovate--technology-hubs-technology-hubs` |

Anything else the evidence names is `other`, noted and never staged: a coworking space with no programme, a university department, a data centre, an economic zone with no technology tenants, a one-off hackathon or prize, a startup law or fund on its own.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Is a hub or technology park under way? | A source from the last three years says a technology hub, incubator or park is being built, or one is open with no programme on record |
| 2 | Does a hub run programmes for startups? | A source from the last three years says a hub or incubator in service runs an incubation or acceleration programme with a cohort of startups |
| 3 | Are hubs in more than one city? | A source from the last three years says hubs with programmes are in service in two or more cities |
| 4 | Is a technology park open with tenants? | A source from the last three years says a science or technology park is in service with companies or startups as tenants |

## 3. The ladders

**Technology hubs**

| Stage | Answers |
|---|---|
| 1 Absent | A source from the past three years says no technology hub, incubator or park operates in the country. |
| 2 Under way | Yes to 1 |
| 3 Programmes | Yes to 2 |
| 4 Several cities | Yes to 3 |
| 5 Technology park | Yes to 4 |

A later yes answers the earlier ones (method §3.3). `study.json` holds this as three aspects: `hubs` (`inservice`, `underway`, `none`) for stage 1 and questions 1 and 2, `cities` (`several`) for 3 and `park` (`tenants`) for 4.

## 4. The norm

The Digital Transformation Strategy asks for a technology park and incubation hub in each region, and local innovation centres. This study asks the four questions above; it does not measure a country against the norm.

## 5. What the run reads

- **Carried**: nothing; no earlier study holds facts on these questions.
- **Read**: **352 story readings about the subject**, published since October 2023, in at most 20 stories a country: 311 in the batch's shared calls (147 calls over 732 stories), read once for every study that lists them, and 41 in 30 calls of its own. A story published before the three-year window can set no stage, and the twenty are each country's best ranked across the batch (`study-calls.py --batch … --cap 20`).
- **Not read**: the rest of the 5,166 documents this study lists, instruments, long reports, passing mentions and the documents the row's current cells cite. A question nothing answers is printed as *Not held*.

## 6. Token ceiling

**14 million** for this study; **85 million** for the batch, checked with `study-tokens.py` after every fan-out.

## 7. Tasks, in order

- [x] **D0. Prepared**: this file, `study.json` and the reading lists, 2026-10-16.
- [x] **D1. Read**, 2026-10-16: the batch's shared calls and this study's own, Sonnet drafters; 144 facts after the parent's corrections (`corrections.csv`).
- [x] **D2. Staged** as at 2026-09-30: 1 at 5, 3 at 4, 28 at 3, 19 at 2; unplaced 2, no evidence 1. Every cell is a first pass; no second drafter.
- [x] **D3. Written, rendered and linted**, by `study-first-write.py`; on the soft-launch map. Reported to Bill.

**Decided in the run**: Removed: a fact from the Botswana Startup Ecosystem Report, whose record has no URL (Botswana stays at 3).

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
