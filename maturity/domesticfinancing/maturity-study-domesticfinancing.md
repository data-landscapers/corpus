---
type: task
reader: cc
title: maturity-study-domesticfinancing.md — the thirty-sixth maturity study: the state's own money for digital programmes, in four questions
last_reviewed: 2026-10-13
status: prepared 2026-10-13, questions redrawn the same day on Bill's word; waits for Bill to confirm them
---

# Maturity study: domesticfinancing

*(Commissioned by Bill on 2026-10-13 as `finance.budget--sustainable-domestic-financing-of-digital-transformation`, under `maturity/documentation/maturity-study-method.md`. **Redrawn the same day** *(Bill)*: a fund in law was too narrow a test; look for a budget rising year on year, and a commitment to pay at home that is acted on.)*

## 1. What is assessed

**Whether the state pays for digital transformation with its own money: whether that money is growing, whether the government has said it must be found at home and acted on it, and whether it says what it spent.**

**Its own money** is a line in the state budget for a digital ministry, a digital agency or a named digital programme or project, or a fund, levy or tax that a law assigns to digital programmes: a universal service or universal access fund, a digital development fund, a levy on operators.

The study redraws `finance.budget--sustainable-domestic-financing-of-digital-transformation`, which as at 2026-08-31 puts eight countries at stage 2, 26 at stage 3 and nine at stage 4, none at 1 or 5, and leaves eleven unplaced. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| The state's own money for digital programmes | Sustainable domestic financing of digital transformation: the state's own money for digital programmes | `finance.budget--sustainable-domestic-financing-of-digital-transformation-the-states-own-money-for-digital-programmes` |

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

- **Corpus's own budget tables answer three of the four before anything is read.** `outputs/budgets/` holds a digital line from 2024 or later for 52 countries, every one but Eritrea and Sudan; lines in both of the last two budget years for 42, of which 26 rose and 16 fell; and an amount spent for 29. The row as it stands leaves eleven of the 52 unplaced; it was drawn before the tables were complete.
- **A fall in the latest budget is a no to question 2 and stops the count, whatever comes after.** Namibia, with a levy, a working fund and published accounts, stays at stage 2 while its digital lines are down. A country moves up when the next budget rises.
- **Published spending does not answer the questions before it.** Each of questions 2 and 3 is answered on its own evidence. A yes to question 3 answers question 1 and never question 2.
- **A statement with no act is noted and is not a yes; nor is an act with no statement**, except a law that creates a fund or levy, which is both.
- **A fund in an old law counts as the act only where a dated source from the last three years has it collecting money or paying for a project.** The row as it stands puts South Sudan at stage 4 on its 2012 Act alone.
- **A fund abolished, or whose law is repealed, is no longer an act from that date.** Cameroon's telecommunications fund was abolished in 2024 and Mauritania's decree repealed in July 2026.
- **A statement about raising taxes or domestic revenue in general is not a yes.** It has to name digital transformation, the digital sector or a named digital programme.
- **A line the source says is paid wholly by a loan or grant is not a yes to question 1.** A line part-paid by one is.
- **The rise is not adjusted for inflation, and how much of the money was spent is not judged.**
- **Where a source gives the digital ministry's budget for both years, that sets question 2**; otherwise the lines the tables hold in both years, added up. A country with no line in both years is not answered.
- **A budget proposed and not yet passed counts only where no passed budget is held**, and the short summary says so.
- **Dropped from the row as it stands**: project-by-project against standing money, which the tables show is standing nearly everywhere; and "external finance confined to capital", which no one source states.

`study.json` holds this as two aspects: `budget` (`allocated`, `rose`, `fell`, `spent`, `none`) for questions 1, 2 and 4 and stage 1; `commitment` (`stated`, `acted`, `abolished`) for question 3.

## 4. The norm

Agenda 2063, Goal 20, asks that Africa take full responsibility for financing its own development. The African Union's Digital Transformation Strategy 2020–2030 proposes a digital sovereignty fund and calls for universal service funds to be put to use. Neither sets a share of the budget for digital programmes. This study asks whether the budget gives money and is rising, whether the government has committed to paying at home and acted, and whether spending is published; it does not measure a country against either text.

## 5. What the run reads

- **Carried, nothing opened**: the budget tables, for questions 1, 2 and 4. A small script, `scripts/study-budget-carry.py`, written at D2, files the facts under the tables' own sources.
- **Read**: **148 news stories and notices about digital budgets, universal service funds and digital levies that no study has read for this**, in 39 countries, every one but Cameroon, Chad, Comoros, Egypt, Equatorial Guinea, Eritrea, Ethiopia, Gambia, Libya, Mauritius, São Tomé and Príncipe, Somalia, Sudan, Togo and Zambia; and the 261 short documents the current cells cite that are neither among those nor budget lines the tables already hold. Eight of the 148 are one story listed under eight countries. Statements are taken from these; terms naming the financing of digital transformation added no story to the 148.
- **Not read**: long texts, reports, passing mentions and the 49 budget records the tables hold. **No web search and no handover to OSINT.**

## 6. Token ceiling

**50 million.** The run checks after every fan-out and stops at it.

## 7. Tasks, in order

- [x] **D0. Prepare**: this file and `study.json`, 2026-10-13; redrawn the same day.
- [ ] **D1. Bill's word** on the four questions.
- [ ] **D2. Carry and read**: `study-budget-carry.py` over the budget tables; drafters in one fan-out over the documents of §5.
- [ ] **D3. Stage** as at 2026-09-30, with `scripts/study-ladder-domesticfinancing.py`; the parent reads every fact that sets stage 4 or 5; second stager on 20 cells.
- [ ] **D4. Write, render and lint**; the soft-launch map. **D5. Report to Bill.**

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
