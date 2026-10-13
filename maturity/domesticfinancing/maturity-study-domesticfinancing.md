---
type: task
reader: cc
title: maturity-study-domesticfinancing.md — the thirty-sixth maturity study: the state's own money for digital programmes, in four questions
last_reviewed: 2026-10-13
status: run 2026-10-13 on Bill's word; staged as at 2026-09-30, written, rendered and on the soft-launch map; waits for Bill to accept
---

# Maturity study: domesticfinancing

*(Commissioned by Bill on 2026-10-13 as `finance.budget--sustainable-domestic-financing-of-digital-transformation`, under `maturity/documentation/maturity-study-method.md`. **Redrawn the same day** *(Bill)*: look for a budget rising year on year, and a commitment to pay at home that is acted on.)*

## 1. What is assessed

**Whether the state pays for digital transformation with its own money: whether that money is growing, whether the government has said it must be found at home and acted on it, and whether it says what it spent.**

**Its own money** is a line in the state budget for a digital ministry, a digital agency or a named digital programme or project, or a fund, levy or tax that a law assigns to digital programmes: a universal service or universal access fund, a digital development fund, a levy on operators.

The study redraws `finance.budget--sustainable-domestic-financing-of-digital-transformation`, which as at 2026-08-31 puts eight countries at stage 2, 26 at stage 3 and nine at stage 4, none at 1 or 5, and leaves eleven unplaced. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| The state's own money for digital programmes | Sustainable domestic financing of digital transformation: state money for digital programmes | `finance.budget--sustainable-domestic-financing-of-digital-transformation-state-money-for-digital-programmes` |

Anything else the evidence names is `other`, noted and never staged: a loan or grant from a donor or lender; a tax break or customs exemption; private investment and an operator's own spending; a fund that invests in start-ups or private firms; a regulator's income from licence fees that no law assigns to digital programmes; a tax on digital services whose yield goes to the general budget; the share of digital spending the state carries, which is `finance.sustain`'s.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Has the state budget given money to digital transformation in the last three years? | A finance law, budget estimate or dated story naming an amount for a digital ministry, a digital agency or a named digital programme or project, in a budget year from 2024 |
| 2 | Is that money higher in the latest budget than in the one before? | The digital ministry's budget, or the digital lines held for both years taken together, higher in the latest budget year than the year before, in the country's own currency. **Lower or the same is a no** |
| 3 | Has the government said digital transformation must be paid for from the country's own resources, and acted on it, in the last three years? | A dated statement by the head of state, a minister, a budget speech or a national strategy, **and** an act that follows it: a fund, levy or tax assigned to digital programmes by law, or state money put to the programme the statement named. A law creating such a fund or levy is both at once |
| 4 | Has the government published what was actually spent? | A budget execution report, settlement law or audited accounts giving the amount spent on the digital ministry, agency or programme, or a fund's published account of what it collected and spent, for a year from 2024 |

## 3. The ladders

**The state's own money for digital programmes**

| Stage | Answers |
|---|---|
| 1 Absent | A dated source says the state budget gives no money to digital programmes, or that they are paid for wholly by donors and lenders |
| 2 Preparing | Yes to 1: the budget gives money to digital transformation |
| 3 Establishing | Yes to 1 and 2: and the money rose in the latest budget |
| 4 Operating | Yes to 1, 2 and 3: and the government said it must be paid for at home, and acted |
| 5 Leading | Yes to all four: and what was spent is published |

- **Corpus's own budget tables answer three of the four before anything is read**: a digital line from 2024 or later for 52 countries, lines in both of the last two budget years for 44, and an amount spent for 28.
- **A fall in the latest budget is a no to question 2 and stops the count, whatever comes after.**
- **Published spending does not answer the questions before it.** Each of questions 2 and 3 is answered on its own evidence. A yes to question 3 answers question 1 and never question 2.
- **A statement with no act is noted and is not a yes; nor is an act with no statement**, except a law that creates a fund or levy, which is both.
- **A fund in an old law counts as the act only where a dated source from the last three years has it collecting money or paying for a project.** The row as it stands puts South Sudan at stage 4 on its 2012 Act alone.
- **A fund abolished, or whose law is repealed, is no longer an act from that date.** Cameroon's telecommunications fund was abolished in 2024 and Mauritania's decree repealed in July 2026.
- **A statement about raising taxes or domestic revenue in general is not a yes.** It has to name digital transformation, the digital sector or a named digital programme.
- **A line the source says is paid wholly by a loan or grant is not a yes to question 1.**
- **The rise is not adjusted for inflation; how much was spent is not judged.**
- **Where a source gives the digital ministry's budget for both years, that sets question 2**; otherwise the lines the tables hold in both years, added up. A country with no line in both years is not answered.
- **A fall the source puts down to a mandate moving between budget heads is not a fall where both heads are held and together rose.** *(Added in the run.)*

`study.json` holds this as two aspects: `budget` (`allocated`, `rose`, `fell`, `spent`, `none`) for questions 1, 2 and 4 and stage 1; `commitment` (`stated`, `acted`, `abolished`) for question 3.

## 4. The norm

Agenda 2063, Goal 20, asks that Africa take full responsibility for financing its own development. The African Union's Digital Transformation Strategy 2020–2030 proposes a digital sovereignty fund and calls for universal service funds to be put to use. Neither sets a share of the budget for digital programmes. This study does not measure a country against either text.

## 5. What the run reads

- **Carried, nothing opened**: the budget tables, for questions 1, 2 and 4, by `scripts/study-budget-carry.py`.
- **Read**: 148 news stories and notices about digital budgets, universal service funds and digital levies that no study had read for this, in 39 countries, and the short documents the current cells cite: 433 listings in all.
- **Not read**: long texts, reports, passing mentions and the budget records the tables hold. **No web search and no handover to OSINT.**

## 6. Token ceiling

**50 million.** The run checks after every fan-out and stops at it.

## 7. Tasks, in order

- [x] **D0. Prepare**: this file and `study.json`, 2026-10-13; redrawn the same day.
- [x] **D1. Bill's word**: run on it, 2026-10-13.
- [x] **D2. Carried and read**: 124 facts from the budget tables; 109 drafters in one fan-out over 433 listings. 406 facts in 52 countries.
- [x] **D3. Staged** as at 2026-09-30: 5: 7, 4: 2, 3: 20, 2: 23, none at 1, 2 without evidence; agreement 19 of 20.
- [x] **D4. Written, rendered and linted**; on the soft-launch map. **D5. Reported to Bill**, 2026-10-13.

**Decided in the run**:

- **Stage 5**: Côte d'Ivoire, the Republic of the Congo, Mali, Mozambique, Eswatini, Uganda and South Africa. **Stage 4**: Burundi and Guinea, with no spending published.
- **No statement was found anywhere**: no source read has a government saying digital transformation must be paid for at home. Every yes to question 3 is a fund, levy or assigned tax created, collecting or paying.
- **A fall holds 17 countries at stage 2**; six more have no two years to compare. Botswana, Cabo Verde, Kenya, Madagascar, Namibia, Nigeria and Tanzania have a working fund and a falling budget.
- **Where a source and the tables disagree, the source giving the ministry's budget stands**: Côte d'Ivoire, Uganda and Zimbabwe rose on it; Tanzania, Kenya and Djibouti fell on it. Côte d'Ivoire's gives a 37 per cent rise and no earlier figure; the second stager read stage 2.
- **Eswatini's stage 5 rests on a fund page dated 3 October 2023**, two days inside the three years.
- **Removed by the parent, six rows** (`corrections.csv`); Burkina Faso's work-plan figure would have been stage 3.
- **Tokens: 55.9 million at the map**, ceiling 50 million, step 1 included: passed in the write-up.

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
