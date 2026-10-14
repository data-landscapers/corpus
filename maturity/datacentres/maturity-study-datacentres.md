---
type: task
reader: cc
title: maturity-study-datacentres.md — the forty-fifth maturity study: data centres for hire, in four questions
last_reviewed: 2026-10-14
status: prepared 2026-10-14; waits for Bill's word on the questions
---

# Maturity study: datacentres

*(Commissioned by Bill on 2026-10-14 as `infra.store--local-data-centre-capacity-all-providers`, under `maturity/documentation/maturity-study-method.md`.)*

## 1. What is assessed

**A data centre in the country that rents space, power or computing to other organisations**, whoever owns it and whatever it is called: a colocation or carrier-neutral facility, a cloud provider's, or a state or operator data centre that also sells to outside customers.

The study redraws `infra.store--local-data-centre-capacity-all-providers`, which as at 2026-08-31 puts 22 countries at stage 4, 8 at stage 3, 11 at stage 2 and 13 at stage 1, none at stage 5. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| Data centres for hire in service | Local data centre capacity (all providers): data centres for hire in service | `infra.store--local-data-centre-capacity-all-providers-data-centres-for-hire-in-service` |

Anything else the evidence names is `other`, noted and never staged: a data centre announced, financed or under construction; one used only by its owner, such as a bank's, a mobile operator's own network or a government data centre serving only the state; who owns the data centres, which `local-data-centre-capacity-national-providers` assesses; cloud and hosting policy, which `cloudstrategy` and `datalocalisation` assess; megawatts, racks and floor space, reported in the long summary and setting nothing.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Is a data centre for hire in service? | A source states that a data centre in the country rents space, power or computing to other organisations |
| 2 | Is one built to Tier III or above? | A source states that such a data centre in service is Tier III or IV, by Uptime Institute certification, a TIA-942 rating or the operator's own statement |
| 3 | Are two of them Tier III or above? | A source, or two, states that two such data centres in service are Tier III or IV |
| 4 | Does a global cloud provider run a cloud region there? | A source states that Amazon, Microsoft, Google, Oracle, Huawei or another public cloud provider sells its services from a cloud region in the country |

## 3. The ladders

**Data centres for hire in service**

| Stage | Answers |
|---|---|
| 1 Absent | A source from the past three years says no data centre in the country rents space or computing to others |
| 2 Preparing | Yes to 1: a data centre for hire in service |
| 3 Establishing | Yes to 2: one at Tier III or above |
| 4 Operating | Yes to 3: two at Tier III or above |
| 5 Leading | Yes to 4: a global cloud region |

- **No question has a window.** A data centre or a cloud region in service stays in service until a later source says it has closed.
- **The Tier is taken as stated**, certified or claimed; the long summary says which. A Tier III design certificate for a facility in service counts.
- **Stages 1 to 4 are the row as it stands.** The row read them from Corpus's data centres dataset; the run carries that dataset's facilities, each with its own source, before reading anything.
- **Stage 5 changes.** The row asked for capacity per head in the African top fifth and a published figure that 30 % of content is hosted in Africa; no story states either, and the dataset leaves megawatts blank for most facilities. A cloud region is where a country's content and computing are hosted at scale, and a story states it. A content cache, or a cloud "zone" run from a region elsewhere, is not a region.

`study.json` holds this as two aspects: `centre` (`two`, `tier3`, `service`, `none`) for questions 1 to 3, and `cloud` (`region`, `none`) for question 4.

## 4. The norm

The African Union's Digital Transformation Strategy 2020–2030 asks that 30 % of Africa's content be hosted in Africa by 2030, and the Smart Africa Data Center and Cloud Blueprint asks for data centres built to the Uptime Institute's tiers. This study asks whether a country has a data centre for hire, whether one or two are built to Tier III, and whether a global cloud provider runs a region there; it does not measure capacity, price, power or who owns them.

## 5. What the run reads

- **Carried first**: the 209 facilities the data centres dataset holds in service and for hire, in 41 countries, 88 of them at Tier III or above, each with its source. No document is opened for them.
- **Read**: **2,213 news readings**, in all 54 countries: 2,160 about data centres, which are 1,299 stories about one country and 861 readings of 208 regional stories, a regional story being read once for each country it names, and 53 more that the current cells cite for this row. Twenty-six longer documents the cells cite are opened only where a question turns on one.
- **Not read**: long texts, reports and passing mentions. **No web search and no handover to OSINT.**

## 6. Token ceiling

**175 million.** The satellite broadband study read 820 readings and came to 62.6 million, about 76,000 a reading; this one reads 2,213. The run checks after every fan-out and stops at it.

## 7. Tasks, in order

- [x] **D0. Prepare**: this file, `study.json` and the reading lists, 2026-10-14.
- [ ] **D1. Bill's word** on the questions.
- [ ] **D2. Carry** the dataset's facilities, then **read**: one fan-out of drafters over the 2,213 readings.
- [ ] **D3. Stage** as at 2026-09-30, the parent reading every fact that sets stage 4 or 5; agreement on 20 cells.
- [ ] **D4. Write, render and lint**; the soft-launch map. **D5. Report to Bill.**

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
