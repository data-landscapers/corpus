---
type: task
reader: cc
title: maturity-study-admindata.md — official statistics drawn from administrative records, in four questions
last_reviewed: 2026-10-19
status: run 2026-10-15; ladder changed 2026-10-19, restaged by that night's rebuild
---

# Maturity study: admindata

*(Commissioned by Bill on 2026-10-15 as `data.statistics--statistics-from-administrative-data`, under `maturity/documentation/maturity-study-method.md`.)*

## 1. What is assessed

**Official statistics compiled from the records a public body keeps to run a service, and published**: births and deaths from civil registration, pupils from school returns, patients from health facility reports, trade from customs declarations, revenue from tax returns, crimes from police records. Whoever compiles them counts, the statistics office or a ministry's statistics unit, and whatever the product is called: a yearbook, a bulletin, an abstract, a vital statistics report.

The study redraws `data.statistics--statistics-from-administrative-data`, which as at 2026-08-31 puts 24 countries at stage 3 and 12 at stage 2, none at 1, 4 or 5, and leaves 18 unplaced. It touches no other row: civil registration's own digitisation stays with the registry study, censuses and surveys with theirs.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| Statistics from administrative data | Statistics from administrative data: statistics from administrative data | `data.statistics--statistics-from-administrative-data-statistics-from-administrative-data` |

Anything else the evidence names is `other`, noted and never staged: a census or survey, a ministry's report on its own activity, a dashboard or information system with no published statistics from it, central bank statistics, a register digitised or linked to identity, an international compilation of national figures.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Is work under way to draw statistics from administrative records? | A source from the last three years states a register assessed for statistical use, staff trained, a data-sharing agreement between the statistics office and a record-holder, a pilot, or a project funded to that end. A plan only announced is not a yes |
| 2 | Have statistics compiled from administrative records been published in the last three years? | A yearbook, bulletin, abstract or report of statistics drawn from those records, published since 1 October 2023 |
| 3 | Has one source's statistics been published twice? | Two editions of statistics drawn from the same administrative source, both published since 1 October 2023 |
| 4 | Have three sources' statistics each been published twice? | Three distinct administrative sources, each with two editions published since 1 October 2023 |

**A source is one body's records kept for one service**: civil registration, customs declarations, school returns, health facility reports, tax returns, police records. Two products from the same records are one source; a yearbook drawing on five registers is five.

## 3. The ladders

**Statistics from administrative data**

| Stage | Answers |
|---|---|
| 1 Absent | A source from the last three years says no official statistics are drawn from administrative records and no work is under way |
| 2 Preparing | Yes to 1 only: work under way, nothing published |
| 3 Published | Yes to 2: statistics from at least one administrative source published |
| 4 Operating | Yes to 3: statistics from at least one administrative source published at least twice in the last three years |
| 5 Leading | Yes to 4: statistics from at least three administrative sources published at least twice in the last three years |

- **A later yes answers the earlier ones.**
- **One yearbook published twice can carry stage 5** where each edition draws on three sources or more.
- **Two editions are two publications**: one report covering two years is one edition.
- **Civil registration is one source among the rest** *(Bill, 2026-10-19)*. The ladder of 2026-10-15 put vital statistics at 4 and their yearly publication at 5; it is replaced by the count of sources and editions above.

`study.json` holds this as aspects: `use` (`published`, `preparing`, `none`) for questions 1 and 2, and `vital` and `series` from the 2026-10-15 ladder until the rebuild of 2026-10-19 replaces them (§7, D6). **For the drafter**: the product and its edition go in `country_label` (e.g. *Annuaire statistique 2023*), the year its figures cover in the fact beside the date it was published, and every administrative source it draws on in the fact.

## 4. The norm

The African Charter on Statistics (2009, Art. 3) and SHaSA 2 (strategic objective 1.1) ask each country to exploit its administrative sources, civil registration among them, for official statistics. The UN Fundamental Principles of Official Statistics (Principle 5) let data be drawn from any source, administrative records included.

## 5. What the run reads

- **Read**: **128 news stories about statistics from administrative records that no study has read**, in 39 countries (none for Algeria, Benin, Comoros, Congo, Gabon, Guinea-Bissau, Libya, Malawi, Mali, Mauritius, Niger, São Tomé and Príncipe, South Sudan, Togo or Tunisia), one call of them regional and read once; then the 138 news stories and 37 documents that the row's current cells cite, in 53 countries. 107 drafters.
- **No earlier study is carried**: the registry study read civil registration for its digitisation and holds no answer to whether vital statistics were published; the census and statistics studies noted administrative data as `other`.
- **Not read**: yearbooks and reports themselves beyond those listed, and passing mentions. A question nothing answers is printed as *Not held*.

## 6. Token ceiling

**40 million**: censuses read 127 calls for 41.8 million and the statistics strategy 97 for 36.4 million; this plans 107.

## 7. Tasks, in order

- [x] **D0. Prepare**: this file, `study.json` and the reading lists, 2026-10-15.
- [x] **D1. Bill's word**, 2026-10-15, the questions as prepared.
- [x] **D2. Read**: 107 drafters, four regional stories read once; 82 facts after the parent's corrections (`corrections.csv`).
- [x] **D3. Staged** as at 2026-09-30: stage 5 Egypt, Eswatini; 4 Botswana, Cabo Verde, Côte d'Ivoire, Equatorial Guinea, Lesotho, Namibia, Rwanda, Seychelles, Uganda, Zimbabwe; 3 fourteen; 2 Ghana, Guinea-Bissau, Mozambique, Senegal, Sierra Leone; none at 1; unplaced Eritrea, Libya, São Tomé and Príncipe; no evidence twenty. The second drafter agreed on 19 of 20.
- [ ] **D6. Ladder changed** *(Bill, 2026-10-19)*: §2 and §3 above. The rebuild of 2026-10-19 replaces `vital` and `series` with an aspect naming each published row's source, counts sources and editions in `study-ladder-admindata.py` and the gaps in `study-admindata-write.py`, re-reads each cell for the sources and editions it names, and logs every restaging `--kind ladder`. `study.json` → `criteria` already holds the new rungs.
- [x] **D4. Written, rendered and linted**, by `study-admindata-write.py`; on the soft-launch map. **D5. Reported to Bill.** Tokens 35.5M of 40M, step 1's thread counted.

**Decided in the run**:

- **Morocco's fact is removed**: cooperation conventions "being finalised" in October 2025 are not signed. It held nothing else and is *No evidence*.
- **Uganda's three budget-report facts are redated to December 2025**, the end of the half-year the report covers; dated to the document's year they fell after the as-at. Its 2024 vital statistics report puts it at 4.
- **Namibia's stage 4 rests on one passing reference** to the 2023 vital statistics report in a 2025 synthesis report; the summary says so.
- **Egypt's stage 5 rests on a 2026 presentation stating CAPMAS issues annual and monthly birth and death reports**, with no report years named. It stands: the source states the series. Eswatini's 2022 report calls itself the seventh annual one.
- **Twenty countries are *No evidence***: what the cells cite and the news read named information systems, laws and registration drives, not a published product. Finding their yearbooks and vital statistics is the rotation's search (method §5), not this study's.
- **Zimbabwe's one report covering 2023 and 2024 is one edition**, not two years running.

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
