---
type: task
reader: cc
title: maturity-study-digitalsovereignty.md — the state's control of its own data and systems, in four questions
last_reviewed: 2026-10-16
status: first pass run 2026-10-16; staged, written and on the soft-launch map; waits for Bill's acceptance
---

# Maturity study: digitalsovereignty

*(Commissioned by Bill on 2026-10-16 as `geopol.sovereignty--digital-sovereignty`, a first pass under `maturity/documentation/first-pass-batch.md`, in one batch with agrisatellite, metsatellite, digitalsovereignty, healthmis, educationmis, egovservices and ruralelectrification: the chapter the last seven indicators.)*

## 1. What is assessed

**The state's control of its own data and systems**: policy, law and practice that keep government data and core systems (ID, payments, data exchange, government hosting) under national jurisdiction and able to move between providers. What keeps state data and systems under the state's control counts, whatever it is called. Keeping data in the country is not the end in itself.

The study redraws `geopol.sovereignty--digital-sovereignty`, which as at 2026-08-31 puts every country unplaced: the row has no cells yet. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| Control of state data | Digital sovereignty: control of state data | `geopol.sovereignty--digital-sovereignty` |

Anything else the evidence names is `other`, noted and never staged: a private company's data centre with no government data in it, a data protection law on personal data alone, a cybersecurity strategy, a foreign loan or donor project with no data terms on record, a statement about sovereignty in general.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Is control of state data a stated goal? | A source from the last three years says the government adopted, published or announced a strategy, plan or draft rule to keep government data or systems under national control: a national or government cloud, a data classification, or a rule on where state data is held |
| 2 | Is a rule on state data in force? | A source from the last three years says a law, decree or policy in force classifies government data or requires government or state data to be held in the country |
| 3 | Are state data and systems hosted nationally? | A source from the last three years says government data or a core system (ID, payments, data exchange, government services) is hosted in a government or nationally owned data centre or cloud in the country |
| 4 | Do contracts carry data terms? | A source from the last three years says a government contract or agreement with a foreign provider or partner includes terms on data jurisdiction, portability, exit or handing over source code |

## 3. The ladders

**Control of state data**

| Stage | Answers |
|---|---|
| 1 Absent | A source from the past three years says no policy or law governs where state data is held or who may process it. |
| 2 Stated goal | Yes to 1 |
| 3 Rule in force | Yes to 2 |
| 4 Hosted nationally | Yes to 3 |
| 5 Contract terms | Yes to 4 |

**Every lower stage is shown by its own evidence** *(Bill, 2026-10-31, messages-for-bill 51)*: a later yes does not answer the earlier ones (`study.json` → `"later_yes": false`). Hosting or contract terms without a goal or rule on state data place nothing. `study.json` holds this as three aspects: `rule` (`inservice`, `underway`, `none`) for stage 1 and questions 1 and 2, `hosted` (`national`) for 3 and `terms` (`carried`) for 4.

**A rule on state data must include government or state data** *(Bill, 2026-10-31, messages-for-bill 60)*: a rule binding personal data in general, banks or payment firms answers no question here. BWA, ETH, LBY, MAR, MOZ, TZA 3→2; CMR, ZWE 4→2; NGA keeps 4 on its 2025 cloud policy for government data.

## 4. The norm

The AU Data Policy Framework asks for localisation of certain categories of data only, with portability so that no one is locked into a single provider; the Digital Transformation Strategy asks for 30 per cent of content hosted in Africa by 2030. This study asks the four questions above; it does not measure a country against the norm.

## 5. What the run reads

- **Carried**: the datalocalisation study's rules in force or in draft (questions 2 and 1) and the nationaldatacentres study's facts on government systems hosted in a nationally owned data centre (question 3). No document opened.
- **Read**: **172 story readings about the subject**, published since October 2023, in at most 20 stories a country: 3 in the batch's shared calls (8 calls over 36 stories), read once for every study that lists them, and 169 in 55 calls of its own. A story published before the three-year window can set no stage, and the twenty are each country's best ranked across the batch (`study-calls.py --batch … --cap 20`).
- **Not read**: the rest of the 3,960 documents this study lists, instruments, long reports, passing mentions and the documents the row's current cells cite. A question nothing answers is printed as *Not held*.

## 6. Token ceiling

**12 million** for this study; **75 million** for the batch, checked with `study-tokens.py` after every fan-out.

## 7. Tasks, in order

- [x] **D0. Prepared**: this file, `study.json` and the reading lists, 2026-10-16.
- [x] **D1. Read**, 2026-10-16: Sonnet drafters, self-contained calls; corrections in `corrections.csv`.
- [x] **D2. Staged** as at 2026-09-30: 16 at 4, 10 at 3, 10 at 2; unplaced 9, no evidence 9. Every cell is a first pass; no second drafter.
- [x] **D3. Written, rendered and linted**; on the soft-launch map. Reported to Bill.
- [x] **D4. Second drafter**, 2026-10-31, after the rebuild (housekeeping 46): 20 of 44 staged cells drawn, restaged blind from `evidence.csv` and `study.json` alone by a drafter who had read no page (the first restage, by the drafter who had just rewritten the pages, was not blind and is replaced). 17 of 20 agree; `agreement.csv`. The three splits stand at the first stage: SEN 2 against 3, SEN-001's 2021 instruction is outside the window and cites no instrument; SLE 2 against 4, SLE-002 shows the data centre but no state system hosted in it; TUN 2 against 3, TUN-001 binds credit bureaux' data, not state data.
- [x] **D5. Every lower stage shown**, 2026-10-31 (messages-for-bill 51): eleven cells resting on a later yes restaged and logged `--kind ladder`. AGO, COM, GHA, GIN, MRT, MUS, MWI 4→2; CPV, SWZ, UGA 4→unplaced; ERI 5→unplaced. Now 8 at 4, 8 at 3, 23 at 2, 1 at 1; unplaced 8, no evidence 6.

**Decided in the run**: Removed at the top-stage check: BWA-003, the data centre's owner is not stated; EGY-002, a plan for an AI model to run in Egypt, not state data hosted; MAR-003, an AI marketplace, not state data or a core system hosted; MLI-001, what the data centre will host, not what it hosts; MOZ-002, a university's data centre, not a core government system.

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
