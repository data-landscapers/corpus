---
type: task
reader: cc
title: maturity-study-domesticfinancing.md — the thirty-sixth maturity study: the state's own money for digital programmes, in four questions
last_reviewed: 2026-10-13
status: prepared 2026-10-13; waits for Bill to confirm the questions
---

# Maturity study: domesticfinancing

*(Commissioned by Bill on 2026-10-13 as `finance.budget--sustainable-domestic-financing-of-digital-transformation`, under `maturity/documentation/maturity-study-method.md`.)*

## 1. What is assessed

**Whether the state pays for its digital programmes with its own money, year after year, and says what it spent.**

**Its own money** is a line in the state budget for a digital ministry, a digital agency or a named digital programme or project, or a fund or levy set up by law to pay for digital programmes: a universal service or universal access fund, a digital development fund, a levy on operators or a tax assigned to digital programmes.

The study redraws `finance.budget--sustainable-domestic-financing-of-digital-transformation`, which as at 2026-08-31 puts eight countries at stage 2, 26 at stage 3 and nine at stage 4, none at 1 or 5, and leaves eleven unplaced. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| The state's own money for digital programmes | Sustainable domestic financing of digital transformation: the state's own money for digital programmes | `finance.budget--sustainable-domestic-financing-of-digital-transformation-the-states-own-money-for-digital-programmes` |

Anything else the evidence names is `other`, noted and never staged: a loan or grant from a donor or lender; a tax break or customs exemption; private investment and an operator's own spending; a fund that invests in start-ups or private firms; a regulator's income from licence fees that no law assigns to digital programmes; a tax on digital services whose yield goes to the general budget; the share of digital spending the state carries, which is `finance.sustain`'s.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Has the state budget given money to a digital ministry, agency or programme in the last three years? | A finance law, budget estimate or dated story naming an amount for a digital ministry, a digital agency or a named digital programme or project, in a budget year from 2024 |
| 2 | Has the government published what was actually spent on it? | A budget execution report, a settlement law, audited accounts or a later budget's own column giving the amount spent on that ministry, agency or programme, for a budget year from 2024 |
| 3 | Is there a fund or levy, set up by law, that pays for digital programmes? | A law or decree creating the fund or levy in the last three years; or a dated story from the last three years of an older one collecting money or paying for a project |
| 4 | Has that fund published what it collected and what it spent in the last three years? | The fund's or regulator's annual report, its audited accounts, or a budget annex, giving both figures for the fund |

## 3. The ladders

**The state's own money for digital programmes**

| Stage | Answers |
|---|---|
| 1 Absent | A dated source says the state budget gives no money to digital programmes, or that they are paid for wholly by donors and lenders |
| 2 Preparing | Yes to 1: the budget gives money to digital programmes |
| 3 Establishing | Yes to 1 and 2: and what was spent is published |
| 4 Operating | Yes to 1, 2 and 3: and a fund or levy in law pays for digital programmes |
| 5 Leading | Yes to all four: and the fund publishes what it collects and spends |

- **Corpus's own budget tables answer questions 1 and 2 before anything is read.** `outputs/budgets/` holds a digital line from 2024 or later for 52 countries, every one but Eritrea and Sudan, and an amount spent for 29. The row as it stands leaves eleven of those 52 unplaced and puts eight at stage 2 as one-off projects; it was drawn before the tables were complete.
- **A fund abolished, or whose law is repealed, is a no to question 3 from that date.** Cameroon's telecommunications fund was abolished in 2024 and Mauritania's decree repealed in July 2026.
- **A fund that exists only in an old law, with no story of it collecting or paying in three years, is not a yes.** The row as it stands puts South Sudan at stage 4 on its 2012 Act alone.
- **A fund created in the last three years is a yes to question 3 before it has collected anything**, as Guinea's of May 2026.
- **One figure is not an account**: a story giving what a fund paid for one project answers question 3 and not question 4.
- **A line the source says is paid wholly by a loan or grant is not a yes to question 1.** A line part-paid by one is.
- **How much was given, whether it rose or fell, and how much of it was spent, are not judged.** Benin's programme that spent 0.62 per cent of its credits by April is a yes to question 2.
- **A budget proposed and not yet passed is a yes to question 1 only where no passed budget is held**, and the short summary says so.
- **Two changes from the row as it stands**: its stage 2 and 3 turn on whether money is given project by project or as a standing programme, which the tables now show is standing nearly everywhere, so stage 3 asks instead whether spending is published; its stage 5 adds "external finance confined to capital", which is not a fact one source can state.

`study.json` holds this as two aspects: `budget` (`allocated`, `spent`, `none`) for questions 1 and 2 and stage 1; `fund` (`established`, `accounted`, `abolished`) for questions 3 and 4.

## 4. The norm

Agenda 2063, Goal 20, asks that Africa take full responsibility for financing its own development. The African Union's Digital Transformation Strategy 2020–2030 proposes a digital sovereignty fund and calls for universal service funds to be put to use. Neither sets a share of the budget for digital programmes. This study asks whether the budget gives money, whether spending is published, and whether a fund in law pays and accounts for itself; it does not measure a country against either text.

## 5. What the run reads

- **Carried, nothing opened**: the budget tables, for questions 1 and 2. A small script, `scripts/study-budget-carry.py`, written at D2, files one fact per country per budget year under the table's own source.
- **Read**: **148 news stories and notices about universal service funds, digital levies and digital budgets that no study has read for this**, in 39 countries, every one but Cameroon, Chad, Comoros, Egypt, Equatorial Guinea, Eritrea, Ethiopia, Gambia, Libya, Mauritius, São Tomé and Príncipe, Somalia, Sudan, Togo and Zambia; and the 261 short documents the current cells cite that are neither among those nor budget lines the tables already hold. Eight of the 148 are one story listed under eight countries.
- **Not read**: long texts, reports, passing mentions and the 49 budget records the tables hold. **No web search and no handover to OSINT.**

## 6. Token ceiling

**50 million.** The run checks after every fan-out and stops at it.

## 7. Tasks, in order

- [x] **D0. Prepare**: this file and `study.json`, 2026-10-13.
- [ ] **D1. Bill's word** on the four questions.
- [ ] **D2. Carry and read**: `study-budget-carry.py` over the budget tables; drafters in one fan-out over the documents of §5.
- [ ] **D3. Stage** as at 2026-09-30, with `scripts/study-ladder-domesticfinancing.py`; the parent reads every fact that sets stage 4 or 5; second stager on 20 cells.
- [ ] **D4. Write, render and lint**; the soft-launch map. **D5. Report to Bill.**

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
