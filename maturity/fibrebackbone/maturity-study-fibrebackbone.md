---
type: task
reader: cc
title: maturity-study-fibrebackbone.md — the forty-first maturity study: long-distance fibre across the country, in four questions
last_reviewed: 2026-10-14
status: run 2026-10-14 on Bill's word; staged as at 2026-09-30, written, rendered and on the soft-launch map; waits for Bill to accept
---

# Maturity study: fibrebackbone

*(Commissioned by Bill on 2026-10-14 as `infra.connect--national-fibre-backbone`, under `maturity/documentation/maturity-study-method.md`.)*

## 1. What is assessed

**Fibre that carries traffic between the capital and the country's other regions**, whoever owns it and whatever it is called: a state backbone, a power or rail utility's fibre, an operator's own national network.

The study redraws `infra.connect--national-fibre-backbone`, which as at 2026-08-31 puts 36 countries at stage 3 and 13 at stage 2, none at 1, 4 or 5, leaves Comoros, Egypt, Eritrea and Rwanda unplaced and São Tomé and Príncipe without a row. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| Long-distance fibre across the country | National fibre backbone: long-distance fibre across the country | `infra.connect--national-fibre-backbone` |

Anything else the evidence names is `other`, noted and never staged: fibre within one city; fibre to homes and offices; sea cables and landing stations; a link across a border on its own, which `regionalinfrastructure` assesses; microwave and satellite links; data centres and exchange points; a study, a plan or money promised with no contract.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Is a national fibre backbone being built? | A contract awarded or works begun, in the past three years |
| 2 | Is some of it in service, linking the capital to other regions? | Fibre stated in service between the capital and at least one other region |
| 3 | Does it reach every province or region? | A source states that every province, region or regional capital is connected |
| 4 | Is capacity on that nationwide backbone sold to other operators? | A source states that other operators buy or lease capacity on it, or that it runs on open-access or wholesale terms |

## 3. The ladders

**Long-distance fibre across the country**

| Stage | Answers |
|---|---|
| 1 Absent | A source from the past three years says the country has no national fibre backbone |
| 2 Preparing | Yes to 1: being built |
| 3 Establishing | Yes to 2: in service between the capital and other regions |
| 4 Operating | Yes to 3: reaching every province or region |
| 5 Leading | Yes to 4: every region reached, and capacity sold to other operators |

- **Only question 1 has a window, three years.** A backbone in service stays in service, and reach stays reached, until a later source says otherwise.
- **Question 4 needs question 3.** Open access on a backbone that reaches some regions only is noted and leaves the country at stage 3.
- **Length in kilometres is reported in the long summary and sets nothing.** No norm sets a length, as the row as it stands already says.
- **The row as it stands asks more of stage 4**: every region, published open-access terms, a cross-border link and a current length, all at once. That is why nobody is above stage 3. Here stage 4 asks for every region alone, open access moves to stage 5, and the cross-border link is left to `regionalinfrastructure`.
- **Stage 5 no longer asks for a master plan implemented, redundancy, and rules on sharing and rights of way.** Each is a judgement, or a law's text, and none is a fact a story states.

`study.json` holds this as two aspects: `reach` (`every-region`, `in-service`, `building`, `none`) for questions 1 to 3, and `access` (`open`, `none`) for question 4.

## 4. The norm

The African Union's Digital Transformation Strategy 2020–2030 and the Programme for Infrastructure Development in Africa ask member states to build national backbones that reach every region and join their neighbours' networks, and to share infrastructure among operators. This study asks whether a backbone is being built, is in service, reaches every region, and carries other operators' traffic; it does not measure length, capacity or price.

## 5. What the run reads

- **Read**: **388 news stories that no study has read**, in 53 countries: 171 about the backbone, in 41 countries, and 217 more that the current cells cite for this row.
- **Not read**: long texts, reports and passing mentions.
- **São Tomé and Príncipe has nothing to read**: no unread story about the backbone and no cell. It stays *No evidence*.

## 6. Token ceiling

**45 million.** The shared-infrastructure study read 333 stories and came to 41 million; this one reads 388, with writers for the summaries. The run checks after every fan-out and stops at it.

## 7. Tasks, in order

- [x] **D0. Prepare**: this file, `study.json` and the reading lists, 2026-10-14.
- [x] **D1. Bill's word**: run on it, 2026-10-14.
- [x] **D2. Read**: 98 drafters over the 388 stories, then 17 over the 18 longer documents the current cells cite, opened because a question turned on them (method §4). 184 facts after the parent's reading.
- [x] **D3. Staged** as at 2026-09-30: 5: 1, 4: 6, 3: 28, 2: 5, 1: 1, one unplaced, 12 without evidence; two rows removed (`corrections.csv`); agreement 20 of 20.
- [x] **D4. Written, rendered and linted**; on the soft-launch map. **D5. Reported to Bill**, 2026-10-14.

**Decided in the run**:

- **Tanzania alone is at stage 5**: the minister says the backbone reaches every mainland regional headquarters (December 2025), and the state operator sells capacity on it to Burundi's backbone company (September 2026). The statement covers the mainland only.
- **Six are at stage 4**: Angola (all provincial capitals, 2023), Burundi (all provinces, the regulator's report for 2024), Guinea (all administrative regions, 2025), Kenya (all 47 counties, 2017), Malawi (all districts, the power utility, 2025) and Nigeria.
- **Nigeria is at 4 on fibre across all 36 states and the capital territory**, counted from the regulator's figures across every operator (August 2026). That is later than the World Bank's statement of September 2025 that the country has no national backbone, so it stands. Its open access is a planned build and was removed; so was Niger's, which is a stated aim.
- **Guinea-Bissau is at stage 1**, on an August 2025 report that the country still needs a backbone to link its main cities.
- **Open access waits on every region**: Botswana, Cameroon, Gabon, the Gambia, Mauritania, Eswatini, South Africa and Zimbabwe all hold a fact on capacity sold to other operators, and none on reach to every region.
- **Twelve countries are without evidence**, Ghana, Morocco and Mauritius among them: what their cells cite gave no fact on the four questions. Benin is unplaced: its one build dates from 2016, outside the window.
- **A script wrote the summaries**, `scripts/study-fibrebackbone-write.py`, from the drafters' fact sentences, to hold the ceiling; no writer was called.
- **Tokens: 40.0 million at the map**, ceiling 45 million, step 1 included.

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
