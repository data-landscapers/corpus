---
type: task
reader: cc
title: maturity-study-opendatause.md — government data published for anyone to reuse, and reused, in four questions
last_reviewed: 2026-10-25
status: run 2026-10-15; staged, written and on the soft-launch map; waits for Bill's acceptance
---

# Maturity study: opendatause

*(Commissioned by Bill on 2026-10-15 as `data.open--use-of-open-data`, under `maturity/documentation/maturity-study-method.md`.)*

## 1. What is assessed

**Data a public body publishes online for anyone to download and reuse, and the reuse of it**: datasets on a national open data portal, a statistics office's data portal, a ministry's, a regulator's or parliament's, a geoportal. Whoever publishes counts, under whatever name, with or without a policy behind it.

The study redraws `data.open--use-of-open-data`, which as at 2026-08-31 puts five countries at stage 3, 36 at stage 2 and two at stage 1, none at 4 or 5, and leaves eleven unplaced. It touches no other row: whether an open data policy exists, is adopted and has a portal under it stays with the open data policy study.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| Use of open data | Use of open data: use of open data | `data.open--use-of-open-data` |

Anything else the evidence names is `other`, noted and never staged: a dashboard or report with no data to download, a portal announced or being built, a portal run by a donor, a development bank or an international body, an international compilation of national figures, a rating such as the Open Data Inventory, an access to information request, a policy or law with no data published under it, a hackathon whose data is not said to be the government's.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Does a public body publish data online for anyone to download? | A source from the last three years shows datasets a public body publishes for download, on a portal or its own site, or reports an open data portal at work |
| 2 | Is that data published under an open licence? | A source from the last three years states a licence or terms that let anyone reuse the data, such as Creative Commons or the Licence Ouverte, for at least one body's data |
| 3 | Do several public bodies publish data that way? | A source from the last three years names two or more public bodies publishing data on a portal, or counts the bodies publishing |
| 4 | Do four or more public bodies publish data that way? | A source from the last two years names four or more public bodies publishing data on a portal, or counts them at four or more |

## 3. The ladders

**Use of open data**

| Stage | Answers |
|---|---|
| 1 Absent | A source from the last three years says no public body publishes data for anyone to download |
| 2 Published | Yes to 1: data published for download, no open licence on record |
| 3 Licensed | Yes to 2: data published under an open licence |
| 4 Several bodies | Yes to 3: two or more public bodies publish |
| 5 Four or more bodies | Yes to 4: four or more public bodies publish, on a source from the last two years |

- **A later yes answers the earlier ones**, as the method has it: four or more bodies publishing places a country at stage 5 whether or not its licence is held.
- **A statistics office's data portal counts**, and will carry most stage 2 and 3 cells. A portal a development bank or donor runs counts only where a source says the government body publishes on it.
- **A statement that there is no national portal is not a stage 1**: a statistics office may still publish. Stage 1 needs a source that no body publishes data for download.
- **Dataset counts and how open the data is are not judged.** A count is given where a source gives one.
- **Changes from the row as it stands.** Stage 2 counted a portal planned or piloted, and a dashboard: both go to `other`, since nothing is downloadable. Stage 4 asked for several bodies, a licence, bulk download or an interface and reuse together; the interface goes, as it needs the portal itself examined, and reuse moves to stage 5. Stage 5 asked for open data by default, timely, disaggregated and interoperable across the value chain: that is alignment and quality, and goes.

`study.json` holds this as two aspects: `access` (`licensed`, `published`, `none`) for questions 1 and 2, and `breadth` (`many`, `several`) for 3 and 4, `many` being four or more bodies.

**Rung 5 rewritten** *(Bill, 2026-10-25)*: four or more public bodies publishing, named or counted within two years, replaces reuse, and a download or view count is not evidence of use. The five reuse facts were removed (`corrections.csv`). Burkina Faso holds 5; Libya and Togo rise from 4 to 5; Liberia and Senegal fall from 5 to 4; the Central African Republic falls from 5 to 3, its statistics portal the one publisher on record. **For the drafter**: the portal or site goes in `country_label` with its address, and the body that publishes in the fact.

## 4. The norm

The African Union's Data Policy Framework (2022) asks states to open government data for reuse, and the Africa Data Consensus (2015) calls for data open by default across the data value chain. This study asks whether data is published, licensed, published by several bodies and reused; it does not measure a country against either.

## 5. What the run reads

- **Carried, not read**: 30 facts on open data portals and published data from the open data policy study, 24 documents in its reading. Its five facts that a country has no national portal are not carried: they do not say no body publishes.
- **Read**: **56 news stories about open data that no study has read**, in 31 countries (none for Algeria, Cabo Verde, Chad, the Comoros, Congo, the Democratic Republic of the Congo, Egypt, Equatorial Guinea, Eritrea, Eswatini, Lesotho, Libya, Madagascar, Mozambique, Namibia, Niger, Rwanda, São Tomé and Príncipe, Somalia, South Sudan, Sudan, Togo or Zimbabwe), one call of them regional and read once; then the 58 news stories and 10 documents the row's current cells cite, in 33 countries. 65 drafters.
- **Not read**: the portals themselves, policy texts, long reports and passing mentions. A question nothing answers is printed as *Not held*.

## 6. Token ceiling

**25 million**: the administrative data study read 107 calls for 35.5 million; this plans 65.

## 7. Tasks, in order

- [x] **D0. Prepare**: this file, `study.json`, the carry and the reading lists, 2026-10-15.
- [x] **D1. Bill's word**, 2026-10-15, the questions as prepared.
- [x] **D2. Read**: the 65 planned drafters, the regional story read once, then, on Bill's word, the 232 documents the open data policy study had read: the carry passes over every one of them though it carried facts from only 24, and the licence pages Burundi, Mali and Somalia's cells cite were among them. 113 facts after the parent's corrections (`corrections.csv`).
- [x] **D3. Staged** as at 2026-09-30: stage 5 Liberia, Senegal; 4 Guinea-Bissau, Libya, Togo, Zambia; 3 Burundi, Central African Republic, Madagascar, Mali, Mozambique, Somalia, South Sudan; 2 twenty-three; none at 1; unplaced Burkina Faso, Algeria, Kenya, Nigeria, Sierra Leone; no evidence thirteen. The second drafter agreed on 18 of 20.
- [x] **D4. Written, rendered and linted**, by `study-opendatause-write.py`; on the soft-launch map. **D5. Reported to Bill.** Tokens 43.0M of 25M: the second read, about 17M, was Bill's call at the ceiling.

**Decided in the run**:

- **Stage 5 rests on usage figures**: Liberia's microdata catalogue shows 273 downloads of a 2024 survey, Senegal's national data archive per-dataset view counts. Neither has an open licence on record; the later answer places them (method §3.3), and the summary says so.
- **Mauritania's EITI news articles are removed as reuse**: articles citing a report's figures are a report quoted, not data reused.
- **A count of bodies tagged as access is moved to question 3**: Libya's platform counts nine government entities, Togo's geoportal 23 ministries. Congo's statement that ministries' data is being loaded names and counts none, and is removed.
- **Data you must ask for, or reports, are not data published**: Tunisia's registry for viewing and requesting inventoried data, Niger's nutrition portal of reports and Nigeria's education platform with no download stated are removed.
- **Guinea-Bissau's summary data page** lists the statistics institute, the finance ministry and the regional central bank as providers; it stands at 4.

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
