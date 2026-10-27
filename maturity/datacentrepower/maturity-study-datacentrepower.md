---
type: task
reader: cc
title: maturity-study-datacentrepower.md — the forty-eighth maturity study: power and water for data centres, in four questions
last_reviewed: 2026-10-14
status: run 2026-10-14; on the soft-launch map, waits for Bill to accept
---

# Maturity study: datacentrepower

*(Commissioned by Bill on 2026-10-14 as `infra.energy--sufficient-energy-and-water-for-data-centres`, under `maturity/documentation/maturity-study-method.md`.)*

## 1. What is assessed

**The power and water a country's data centres can count on**: a supply that keeps a data centre running when the grid fails, power set aside for data-centre load, and power and water used sparingly. A data centre is one for hire or the government's own, in service, as in the datacentres and nationaldatacentres studies.

The study redraws `infra.energy--sufficient-energy-and-water-for-data-centres`. As at 2026-08-31 the row stages no country: it bands an operator-published PUE, which no cell holds. It touches no other row, and the national grid's reliability stays with `infra.energy--grid-reliability`.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| Power and water for data centres | Sufficient energy and water for data centres: power and water for data centres | `infra.energy--sufficient-energy-and-water-for-data-centres` |

Anything else the evidence names is `other`, noted and never staged: standby generators and batteries alone, which every data centre has; a plant, line or contract planned, tendered or under construction; the national grid's capacity, outages or water supply where no source ties them to a data centre; a PUE or water figure for a data centre not yet in service.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Does a data centre in service have a secured power supply? | A source states that a data centre in service draws on two grid feeds, a dedicated substation or line, or its own power plant, beyond standby generators |
| 2 | Is power set aside for data centres? | A source states a supply contract signed for data-centre load, a plant or substation in service built for data centres, or a tariff or zone in force that gives them supply |
| 3 | Does a data centre in service state a PUE of 1.6 or less? | The operator states the facility's power usage effectiveness at 1.6 or less, measured or by design |
| 4 | Does a data centre in service publish its water use, or cool without using water? | The operator states the facility's water usage effectiveness or annual water use, or that its cooling consumes no water |

## 3. The ladders

**Power and water for data centres**

| Stage | Answers |
|---|---|
| 1 Absent | A source from the past three years says a data centre was stopped, delayed or rationed for want of power or water, or runs on diesel as its main supply |
| 2 Preparing | Yes to 1: a data centre in service on a secured supply |
| 3 Establishing | Yes to 2: power set aside for data centres |
| 4 Operating | Yes to 3: a data centre states a PUE of 1.6 or less |
| 5 Leading | Yes to 4: a data centre publishes its water use, or cools without water |

- **Questions 1 and 2 have no window**: a supply in service or an agreement in force stands until a later source says it has ended. **Questions 3 and 4 have the usual three years.**
- **The PUE bands go.** The row cut stages at PUE 2.0, 1.8 and 1.6. Few operators publish one, so no country was staged; 1.6 stays, as one question.
- **Stage 5 is the Blueprint's end state asked as facts**: a secured supply, an efficiency figure and water use published.
- **A data centre's own power plant is question 1, not question 2** *(Bill, 2026-10-27)*: a plant counts as power set aside only when it is built to supply data centres generally. **No stage is skipped**: a PUE of 1.6 or less does not lift a country past a no to question 2, so Nigeria stays at 2.
- **Stage 1 needs a statement that a data centre went short**, as every study needs a statement of absence. A country-wide power shortage does not set it.

`study.json` holds this as three aspects: `supply` (`reserved`, `secured`, `none`) for questions 1 and 2, `pue` (`low`) for question 3, and `water` (`published`) for question 4. **For the drafter**: `supply` `none` is the stage 1 statement, a data centre stopped, delayed or rationed for want of power or water, or running on diesel as its main supply; `secured` is question 1 and `reserved` question 2, each for a data centre or arrangement in service or in force. A PUE above 1.6 is no fact: record it under `systems` and say so in the note. **Name the data centre in `system`**, or for `reserved` the plant, contract, tariff or zone; class `datacentre` for all three aspects.

## 4. The norm

The Smart Africa Data Center and Cloud Blueprint names PUE as the efficiency measure and asks for dual grid feeds with backup generation; ISO/IEC 30134-2 and 30134-9 define PUE and WUE. This study asks whether a data centre's supply is secured, whether power is set aside for data centres, and whether operators publish their efficiency and water use; it does not measure how much power a country can spare.

## 5. What the run reads

- **Carried first**: the datacentres and nationaldatacentres studies' facts, matched to the questions from their own text; 29 of them speak of power, cooling or water.
- **Read**: **145 documents**, in 48 countries: 79 the frame's cells cite, in 41 countries; and 66 the two data-centre studies read that name PUE, cooling or data-centre power three times or more, reopened because their carried facts were filed for other questions (`reopen.csv`). No unread story is about the subject: the 32 that carry a term name it once.
- **Not read**: long texts, reports and passing mentions, including 49 environmental studies and datasheets that name PUE or cooling.

## 6. Token ceiling

**30 million**, the offsitebackup study's: 145 documents against its 165. Within the usual share of the week.

## 7. Tasks, in order

- [x] **D0. Prepare**: this file, `study.json`, the reading lists and `reopen.csv`, 2026-10-14.
- [x] **D1. Bill's word**: run on it, 2026-10-14.
- [x] **D2. Read**: 91 drafters over 159 readings, two regional stories read once; 26 facts. The parent added one, Gabon's solar plant, from a frame-cited story the drafters were not given. No carry: the two data-centre studies' facts answer none of the questions in their own terms.
- [x] **D3. Staged** as at 2026-09-30: 5: 1, 2: 4, 3 unplaced, 46 without evidence; 2 rows removed; agreement 5 of 5, the only staged cells.
- [x] **D4. Written, rendered and linted**; on the soft-launch map. **D5. Reported to Bill**, 2026-10-14. Tokens 33.2M of 30M: the session that ran step 1 also ran step 3, and its own thread is counted.

**Decided in the run**:

- **Power set aside answers question 1**: a contract or plant serving a data centre in service is a supply of its own. Otherwise each question needs the one before, so a PUE or water figure alone places no country: Nigeria, Togo and Ethiopia (whose 2021 figure is also out of window) are unplaced.
- **No country is at stage 1.** Every shortage the frame cites is country-wide; none names a data centre that went short.
- **Kenya stops at stage 2** though the Konza and iXAfrica sites state PUEs of 1.45 and 1.25: no source held says power is set aside for data centres. Africa Data Centres' "37.5 MW secured from the utility" is read as capacity, not a contract.
- **South Africa reaches stage 5** on Africa Data Centres' wheeled solar contract for CPT1, Teraco's 2025 PUE of 1.43 and published water use.
- **A substation caption is not a dedicated supply** (ZAF-014), and a third party's unverified report of an operator's claim is not the operator's statement (ZAF-015); both removed in `corrections.csv`.

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
