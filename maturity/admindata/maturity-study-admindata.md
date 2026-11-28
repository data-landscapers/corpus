---
type: task
reader: cc
title: maturity-study-admindata.md — official statistics drawn from administrative records, in four questions
last_reviewed: 2026-11-27
status: run 2026-10-15; ladder changed and rebuilt 2026-10-19; stage 4's editions rewritten 2026-11-27; rulings 159-161 applied 2026-11-27
---

# Maturity study: admindata

*(Commissioned by Bill on 2026-10-15 as `data.statistics--statistics-from-administrative-data`, under `maturity/documentation/maturity-study-method.md`.)*

## 1. What is assessed

**Official statistics compiled from the records a public body keeps to run a service, and published**: births and deaths from civil registration, pupils from school returns, patients from health facility reports, trade from customs declarations, revenue from tax returns, crimes from police records. Whoever compiles them counts, the statistics office or a ministry's statistics unit, and whatever the product is called: a yearbook, a bulletin, an abstract, a vital statistics report.

The study redraws `data.statistics--statistics-from-administrative-data`, which as at 2026-08-31 puts 24 countries at stage 3 and 12 at stage 2, none at 1, 4 or 5, and leaves 18 unplaced. It touches no other row: civil registration's own digitisation stays with the registry study, censuses and surveys with theirs.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| Statistics from administrative data | Statistics from administrative data: statistics from administrative data | `data.statistics--statistics-from-administrative-data` |

Anything else the evidence names is `other`, noted and never staged: a census or survey, a ministry's report on its own activity, a dashboard or information system with no published statistics from it, central bank statistics, a register digitised or linked to identity, an international compilation of national figures.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Is work under way to draw statistics from administrative records? | A source from the last three years states a register assessed for statistical use, staff trained, a data-sharing agreement between the statistics office and a record-holder, a pilot, or a project funded to that end. A plan only announced is not a yes |
| 2 | Have statistics compiled from administrative records been published in the last three years? | A yearbook, bulletin, abstract or report of statistics drawn from those records, published in the three years to the as-at |
| 3 | Has one source's statistics been published twice? | Two editions of statistics drawn from the same administrative source, each shown published in the three years to the as-at |
| 4 | Have three sources' statistics each been published twice? | Three distinct administrative sources, each with two editions published in the three years to the as-at |

**A source is one body's records kept for one service**: civil registration, customs declarations, school returns, health facility reports, tax returns, police records. Two products from the same records are one source, and two editions of it *(Bill, message 160)*; a yearbook drawing on five registers is five. **A product counts only where its source says the figures are drawn from the records** *(Bill, 2026-10-19)*: a body named as a table's source, or as supplying data, does not show that, since the figures could be estimates, surveys or censuses. A statistical compendium that shows no more is unplaced.

## 3. The ladders

**Statistics from administrative data**

| Stage | Answers |
|---|---|
| 1 Absent | A source from the last three years says no official statistics are drawn from administrative records and no work is under way |
| 2 Preparing | Yes to 1 only: work under way, nothing published |
| 3 Published | Yes to 2: statistics from at least one administrative source published |
| 4 Operating | Yes to 3: statistics from at least one administrative source published at least twice in the last three years |
| 5 Mature | Yes to 4: statistics from at least three administrative sources published at least twice in the last three years |

- **Each step of the ladder must be met to progress** *(Bill, 2026-11-09, message 114)*. The four questions measure one yearbook at rising levels, so a higher answer is the same fact.
- **One yearbook published twice can carry stage 5** where each edition draws on three sources or more.
- **Two editions are two publications**: one report covering two years is one edition.
- **The window is a rolling three years** *(Bill, message 161)*: editions are counted back from the as-at, not from a fixed 1 October 2023. At the as-at of 27 November 2026 it opens on 27 November 2023.
- **An edition counts only where it is shown** *(R185, 2026-11-27)*: by its own publication date inside the window, or by figures for a period ending inside it, which cannot have been published earlier; a date given only as the month or year in which the window opens shows nothing on its own. A source saying a product is annual, or giving its place in a series, shows the edition it speaks of, or one current edition where it names none.
- **A stated regular series counts as two editions** *(Bill, message 159)*: a source saying a product is annual, quarterly or the Nth in a series answers question 3 for its source where one edition of it is dated in the window. A volume or issue number of a general compendium, or a title such as *Annual Report*, is not such a statement.
- **Two different products from the same records are two editions** *(Bill, message 160)*: the enterprise register statistics and a social protection bulletin drawn from one social security file count twice. Two volumes of one report, or one report revised, are one edition.
- **Civil registration is one source among the rest** *(Bill, 2026-10-19)*. The ladder of 2026-10-15 put vital statistics at 4 and their yearly publication at 5; it is replaced by the count of sources and editions above.

`study.json` holds this as aspects: `use` (`published`, `preparing`, `none`) for questions 1 and 2, and `vital` and `series` from the 2026-10-15 ladder until the rebuild of 2026-10-19 replaces them (§7, D6). **For the drafter**: the product and its edition go in `country_label` (e.g. *Annuaire statistique 2023*), the year its figures cover in the fact beside the date it was published, and every administrative source it draws on in the fact.

## 4. The norm

The African Charter on Statistics (2009, Art. 3) and SHaSA 2 (strategic objective 1.1) ask each country to exploit its administrative sources, civil registration among them, for official statistics. The UN Fundamental Principles of Official Statistics (Principle 5) let data be drawn from any source, administrative records included.

## 5. What the run reads

- **Read**: **128 news stories about statistics from administrative records that no study has read**, in 39 countries, one call of them regional and read once; then the 138 news stories and 37 documents that the row's current cells cite, in 53 countries. 107 drafters.
- **No earlier study is carried**: the registry study read civil registration for its digitisation and holds no answer to whether vital statistics were published; the census and statistics studies noted administrative data as `other`.
- **Not read**: yearbooks and reports themselves beyond those listed, and passing mentions. A question nothing answers is printed as *Not held*.

## 6. Token ceiling

**40 million**: censuses read 127 calls for 41.8 million and the statistics strategy 97 for 36.4 million; this plans 107.

## 7. Tasks, in order

*(Each step's counts are in git and `history.csv`.)*

- [x] **D0-D5.** Prepared and approved by Bill, 2026-10-15; read (107 drafters); staged as at 2026-09-30, the second drafter agreeing on 19 of 20; written, rendered and reported. 35.5M of 40M tokens.
- [x] **D6. Ladder rebuilt**, 2026-10-19 *(Bill)*: `source` and `series` name the records a product draws on; all 54 countries searched; every cell with evidence logged `--kind ladder`.
- [x] **D7. A named source is not administrative data**, 2026-10-19 *(Bill, on Libya)*: 33 facts naming a body as a table's source, without saying its figures come from records, removed; 18 cells logged `--kind review`.
- [x] **D8. Editions rewritten**, 2026-11-27 *(R185, agreement 35%)*: a product called annual or numbered in a series is not two editions. Every cell restaged `--kind ladder`, eleven moved; a fresh draw agreed on 16 of 20.
- [x] **D9. Rulings 159-161**, 2026-11-27: a stated series with one edition dated counts as two, two products from one source's records count as two, and the window rolls back three years from the as-at. Fourteen cells logged `--kind ruling`.

**Decided in the run**:

- **Conventions count once signed**: Morocco's, "being finalised" in October 2025, are not, and it is *No evidence*.
- **A half-year report is dated to the end of its half-year** (Uganda, December 2025).
- **A passing reference to a report counts as the report** (Namibia's 2023 vital statistics), and the summary says so.
- **A source stating a series stands without report years** (Egypt, CAPMAS); a report calling itself the seventh annual one is a series (Eswatini).
- **One report covering two years is one edition** (Zimbabwe).
- ***No evidence* means no published product was found**: finding yearbooks is the search's work (method §5), not this study's.

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
