---
type: task
reader: cc
title: maturity-study-nationaldatacentres.md — the forty-sixth maturity study: nationally owned data centres for hire, in four questions
last_reviewed: 2026-10-14
status: run 2026-10-14; on the soft-launch map, waits for Bill to accept
---

# Maturity study: nationaldatacentres

*(Commissioned by Bill on 2026-10-14 as `infra.store--local-data-centre-capacity-national-providers`, under `maturity/documentation/maturity-study-method.md`.)*

## 1. What is assessed

**A data centre for hire in the country that is owned in the country**: by the state, a state enterprise, or a company owned mostly by the country's own people or firms, whatever it is called. "For hire" is the datacentres study's test: it rents space, power or computing to other organisations.

The study redraws `infra.store--local-data-centre-capacity-national-providers`, which as at 2026-08-31 puts 18 countries at stage 4, 7 at stage 3, 8 at stage 2 and 8 at stage 1, none at stage 5, and 13 without a stage. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| Nationally owned data centres for hire | Local data centre capacity (national providers): nationally owned data centres for hire | `infra.store--local-data-centre-capacity-national-providers` |

Anything else the evidence names is `other`, noted and never staged: a foreign-owned data centre, which `datacentres` assesses; one announced, financed or under construction; one used only by its owner; a rule that data must stay in the country, which `datalocalisation` assesses.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Is a nationally owned data centre for hire in service? | A source states that a data centre for hire in service is owned by the state, a state enterprise or a company owned mostly in the country |
| 2 | Is one of them Tier III or above? | A source states that such a data centre is Tier III or IV, by certification, a TIA-942 rating or the operator's own statement |
| 3 | Are two of them Tier III or above? | Sources state that two such data centres are Tier III or IV |
| 4 | Does the government host its own data with a national provider? | A source states that ministries' or the state's own systems or data are hosted in a nationally owned data centre in the country |

## 3. The ladders

**Nationally owned data centres for hire**

| Stage | Answers |
|---|---|
| 1 Absent | A source from the past three years says no data centre for hire in the country is nationally owned |
| 2 Preparing | Yes to 1: a nationally owned data centre for hire in service |
| 3 Establishing | Yes to 2: one at Tier III or above |
| 4 Operating | Yes to 3: two at Tier III or above |
| 5 Leading | Yes to 3 and 4: two at Tier III, and the state's own data hosted with a national provider |

- **No question has a window.** A data centre in service, and a state's hosting, stand until a later source says they have ended.
- **Ownership is the owner's, at the as-at date.** A company bought by a foreign group is foreign from the sale. A joint venture is national where the country's side holds the majority.
- **Stages 2 to 4 change.** The row banded the share of facilities nationally owned, at 25 % and 50 %. A share needs every facility counted, and no story states one; a share of 100 % also put a country with one small state facility above one with five. The study counts nationally owned facilities and their Tier instead, as `datacentres` does for all owners.
- **Stage 5 is the row's own end state**, asked as a fact: the row's wording also required a data classification in force, which needs a law read and belongs to `datalocalisation`.
- **Stage 1 needs a statement of absence**, as in every study. A country whose only data centres for hire are foreign-owned, with no such statement, is unplaced and says so.

`study.json` holds this as three aspects: `centre` (`two`, `tier3`, `service`, `none`) for a facility, `owner` (`national`, `foreign`) for who owns it, and `state` (`hosted`, `none`) for question 4.

## 4. The norm

The African Union's Data Policy Framework (2022), §5.3.1, asks that national providers hold data centre capacity and that the state's sensitive data be hosted under national jurisdiction. This study asks whether a country has nationally owned data centres for hire, whether one or two are built to Tier III, and whether the state hosts its own data with them; it does not measure capacity, price or how much of the market national providers hold.

## 5. What the run reads

- **Carried first**: the datacentres study's facilities, 595 in all, each with its source, its Tier and its owner (named for 589). No document is opened for them. **Whether an owner is national is the parent's reading**, held in `owners.csv` and checked against the data centres dataset's `ownership_type`.
- **Read**: **118 news readings**, in 44 countries: 71 on the subject that no study has read, in 31 countries, and 47 the datacentres study read whose carried facts speak of government data or a government data centre, reopened because question 4 turns on them.
- **Not read**: long texts, reports and passing mentions.

## 6. Token ceiling

**45 million**, raised by Bill from 15 million after the read came to 30.4 million: the drafters cost about 118,000 tokens a reading, not the 76,000 the satellite broadband study did, and the reading grew to 194. The run came to 40.2 million.

## 7. Tasks, in order

- [x] **D0. Prepare**: this file, `study.json` and the reading lists, 2026-10-14.
- [x] **D1. Bill's word**: run on it, 2026-10-14.
- [x] **D2. Carried and read**: 873 facts carried; 100 drafters over 194 readings (75 the frame's cells cite, 71 on the subject, 48 reopened); 940 facts in all; `owners.csv` rules 356 of 371 owners. Stopped at 30.4M of the 15M ceiling; Bill raised it to 45M.
- [x] **D3. Staged** as at 2026-09-30: 5: 5, 4: 4, 3: 18, 2: 15, 1: 0, 7 unplaced, 5 without evidence; 1 row revalued, 1 removed and 2 added (`corrections.csv`); agreement 19 of 20.
- [x] **D4. Written, rendered and linted**; on the soft-launch map. **D5. Reported to Bill**, 2026-10-14.

**Decided in the run**:

- **Who owns a facility is read three ways, in order**: an `owner` fact on it; the owner `systems.csv` names, through `owners.csv`; and, where neither holds, an owner's name inside the facility's own, or the owner a carried dataset fact names, read through `owners.csv` and then the dataset's `ownership_type`. A facility no route reaches counts for neither side.
- **A company is national unless one foreign group holds more than half of it.** So Safaricom (Vodacom and Vodafone 44.9 %), Sonatel and Mauritius Telecom count, and Maroc Telecom (e& 53 %) does not. Africa Data Centres and Liquid, Cassava companies headquartered in London, are foreign everywhere; Paratus is national in Namibia and Axian's Stellarix in Madagascar.
- **One facility is counted once.** `study-ladder-nationaldatacentres.py` → `SAME` joins the names drafters gave Zamengoe, Rose-Belle, Kalaa Kebira, Digital Parks Africa, 21st Century and TelOne. TelOne's pages call a Tier 3 facility "its data centre" without naming it, so Zimbabwe is at stage 3 on one.
- **A state-run data centre answers question 4 though it is not for hire**, since the question is where the state's data sits; `STATE_RUN` names those the evidence gives no owner for. Two facts the drafters filed under `centre` only were restated as `state`: Rose-Belle hosting Mauritian government projects, and Galaxy Backbone's Abuja centre serving government.
- **Five are at stage 5**: Cameroon (CAMTEL Zamengoe), Kenya (Konza), Mauritius (Rose-Belle), Nigeria (Galaxy Backbone) and South Africa (SITA). Malawi is at stage 3: no held source says its National Data Centre rents space yet, only that colocation racks will be offered.
- **The agreement split once**, on Libya: the second drafter had no ruling on TransSahara's owner, a Libyan joint venture with a domestic majority in the dataset, and placed it at stage 2.

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
