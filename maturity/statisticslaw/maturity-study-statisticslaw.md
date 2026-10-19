---
type: task
reader: cc
title: maturity-study-statisticslaw.md — the twenty-fifth maturity study: the law on official statistics, in four questions
last_reviewed: 2026-10-13
status: run 2026-10-13 on Bill's word; staged as at 2026-09-30, written, rendered and on the soft-launch map; waits for Bill to accept
---

# Maturity study: statisticslaw

*(Commissioned by Bill on 2026-10-13 as `gov.legislate--statistics-legislation`, under `maturity/documentation/maturity-study-method.md`.)*

## 1. What is assessed

**The law that governs official statistics: it sets up the national statistics office or the national statistical system and says who may collect statistics and how**, whatever it is called: a statistics act, a law on statistical activity, a law of the national statistical system, a proclamation, an ordinance or a decree with the force of law.

The study redraws `gov.legislate--statistics-legislation`, which as at 2026-08-31 puts 50 countries at stage 3 and one at stage 2, none at 1, 4 or 5, and leaves three unplaced. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| Statistics law | Statistics legislation: statistics law | `gov.legislate--statistics-legislation-statistics-law` |

Anything else the evidence names is `other`, noted and never staged: a national strategy for the development of statistics, a statistics office's strategic plan or budget, a law or decree for one census or one survey, a civil registration law, the data protection and access to information laws, an open data policy, a peer review of the statistical system, the African Charter on Statistics and whether the country has ratified it.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Is there a statistics law, or a draft of one? | A bill or draft published, validated, out for consultation, before cabinet or parliament, or passed, or a law made. A law only announced or planned is not a yes |
| 2 | Is that law in force? | A law, ordinance or decree with the force of law in force that governs official statistics or sets up the national statistics office. A bill or draft is not a yes |
| 3 | Have rules been made under it to put it to work? | A dated decree, regulation or order made under the law: setting up or organising the statistics office, the statistics council or the board, or on how surveys are approved and data kept confidential |
| 4 | Has it been applied in the last three years? | A dated act a source says was done under the law: the council or board it sets up appointed or meeting, the head of the office appointed under it, a standard, release calendar or survey approval issued under it, a rule made under it, or a penalty |

## 3. The ladders

**Statistics law**

| Stage | Answers |
|---|---|
| 1 Absent | A dated source says the country has no statistics law and no draft of one |
| 2 Preparing | Yes to 1: a bill or draft, and no law in force |
| 3 Establishing | Yes to 1 and 2: a law in force |
| 4 Operating | Yes to 1, 2 and 3: rules made under it |
| 5 Leading | Yes to all four: the law applied in the last three years |

- **A yes to a later question answers the earlier ones**: a council appointed under the law shows the law is in force.
- **Questions 1 to 3 have no time limit**; a law stands, with its year, until a dated source says it is repealed or replaced.
- **A statement that there is no law counts for three years**, and gives way to a dated source naming a draft or a law in force.
- **An old law still in force is a yes to question 2 and no more**, until a source names rules made under it. The summary gives its year. A bill to replace it is named in the summary and does not lower the stage.
- **A statistics office set up by an ordinary decree, with no statistics law behind it, is a yes to question 1 and no further.** A legislative decree, decree-law or ordinance with the force of law is a law.
- **A law promulgated but not yet in effect is a yes to question 2**, and the summary gives the date it starts. One passed by parliament and not yet promulgated is a yes to question 1 only.
- **A census or survey carried out is not a yes to question 4**, nor is a strategy, a plan or a budget. The question asks for an act a source ties to the law.
- **A rule made under the law in the last three years is a yes to questions 3 and 4.**
- **What the law covers is taken from what a source says of it**, never from reading its text for the purpose.
- **How good the law is is not judged**, nor whether it matches the African Charter on Statistics. A reported criticism, and a peer review's call for a new law, are noted.
- **Changes from the row as it stands.** Its stages 4 and 5 ask whether the act writes in independence, coordination, confidentiality and funding, and conforms to the Charter and the model law. That needs the text read and judged, which is why 50 countries sit together at stage 3.

`study.json` holds this as two aspects: `standing` (`in-force`, `draft`, `none`) for questions 1 and 2, and `reach` (`applied`, `rules`, `none`) for 3 and 4.

## 4. The norm

The African Charter on Statistics (2009) obliges its parties to bring national law into line with its principles: professional independence, confidentiality, coordination. This study asks whether a law exists, is in force, has rules made under it and has been applied; it does not measure the law against the Charter.

## 5. What the run reads

- **Read first**: **52 news stories and short legal notices about a statistics law**, covering 29 countries, 28 of them from the last three years. No study has read them. Twenty-five countries have none.
- **Then, for every country those leave short of an answer**: the news stories its current cell cites, 69 across 31 countries.
- **Then, only for a country still short of an answer**: one call of its newest held news that names such a law, from at most 126 stories.
- **Not read**: the long texts of the laws, strategies and reports. A question nothing answers is printed as *Not held*.

## 6. Token ceiling

**40 million.** The run checks after every fan-out and stops at it.

## 7. Tasks, in order

- [x] **D0. Prepare**: this file and `study.json`, 2026-10-13.
- [x] **D1. Bill's word**: run on it, 2026-10-13.
- [x] **D2. Read**: the 52 stories and what the current cells cite, 80 calls; newest news for 31 countries short of an answer; two countries read by the parent. 168 facts held.
- [x] **D3. Staged**: seven at stage 5, eight at 4, 38 at 3, one at 2, none unplaced, as at 2026-09-30; two facts removed and three added by the parent (`corrections.csv`); agreement 20 of 20.
- [x] **D4. Written, rendered and linted**; on the soft-launch map. **D5. Reported to Bill**, 2026-10-13.

**Decided in the run**:

- **Stage 5**: Angola, Burkina Faso, Côte d'Ivoire and Gabon (a decree under the law since 2023), Botswana (board constituted under the Act, 2023/24), Togo (council sat June 2026), Zambia (release calendar the Act requires).
- **What the current cells cite was read for every country, laws included**, in the same fan-out as the 52 stories: for 25 countries the law's own text is the one source held.
- **A decree adopted by cabinet counts as made** (Côte d'Ivoire), as in the e-commerce study.
- **Orders for a population census are not rules under the law** (Kenya, stage 3). **Data-sharing agreements signed "in line with the Act" are not the law applied** (Ghana, stage 3).
- **A decree that only cites the law among its bases is not a rule under it** (Benin, Djibouti).
- **An amendment to the law is not a rule under it** (Mauritius, South Africa).
- **Djibouti and Mauritania, unplaced before, hold a law**: Djibouti's of 2011 through decrees citing it, Mauritania's of 2005 with a 2006 council decree. **Equatorial Guinea**: Law 3/2020, from its statistics strategy.
- **Passed and not shown as promulgated**: Ethiopia and Morocco stay on their old laws; Niger's draft ordonnance likewise.
- **The summaries were written by the parent.** A country with one fact says so in its second paragraph to reach the word floor.
- **Tokens: 37 million at the map**, step 1 included, ceiling 40 million.

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
