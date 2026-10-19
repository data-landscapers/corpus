---
type: task
reader: cc
title: maturity-study-nonstatefinance.md — the thirty-seventh maturity study: private money for digital businesses, in four questions
last_reviewed: 2026-10-13
status: run 2026-10-13 on Bill's word; staged as at 2026-09-30, written, rendered and on the soft-launch map; waits for Bill to accept
---

# Maturity study: nonstatefinance

*(Commissioned by Bill on 2026-10-13 as `finance.new--mobilisation-of-non-state-finance`, under `maturity/documentation/maturity-study-method.md`.)*

## 1. What is assessed

**Whether money that is not the state's own is being put into the country's digital businesses: whether it arrives, whether it keeps arriving, whether any of it is raised at home, and whether the government has brought private money into a public digital project.**

**Private money** is a loan, an equity investment, a bond, a guarantee or a grant to a private digital business, a fund that invests in such businesses or a public-private partnership, or the amount a company says it is investing itself. **A digital business** is a telecoms operator, a tower, fibre or data-centre company, a fintech or other technology firm, or a start-up. The financier may be a company, a bank, an investor or a development finance institution.

The study redraws `finance.new--mobilisation-of-non-state-finance`, a measure of such money as a share of GDP, which as at 2026-08-31 puts 34 countries at stage 1, five at stage 2, five at stage 3 and ten at stage 4, none at 5. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| Private money for digital businesses | Mobilisation of non-state finance: private money for digital businesses | `finance.new--mobilisation-of-non-state-finance` |

Anything else the evidence names is `other`, noted and never staged: a loan or grant to the government or a state body, which is `finance.new--development-partner-project-financing`'s; money to a charity, a research body or an international organisation; a memorandum, a pledge or a plan with no amount; a deal announced and not signed; what an operator pays the state for a licence or spectrum; a tax break; the state's own budget and its funds.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Has private money been put into a digital business in the country in the last three years? | A dated source naming an amount lent to, invested in, guaranteed for or granted to a private digital business, fund or partnership in the country, or an amount a company says it is investing there itself, signed or started in 2024 or later |
| 2 | Has it come in more than one of those years? | Two such amounts, signed or started in different years from 2024. **Two in one year is a no** |
| 3 | Has any of it been raised inside the country? | A dated source naming an amount put in by a bank, pension fund, insurer, investor or company of the country itself, or raised by a bond or share issue on the country's own market, from 2024 |
| 4 | Has the government brought private money into a public digital project? | A signed public-private partnership, concession or joint venture in which the private partner puts a named amount into a public digital project, or a state fund that private investors have paid into, from 2024 |

## 3. The ladders

**Private money for digital businesses**

| Stage | Answers |
|---|---|
| 1 Absent | A dated source says no private money has gone into the country's digital businesses, or that investors have withdrawn |
| 2 Preparing | Yes to 1: private money has been put in |
| 3 Establishing | Yes to 1 and 2: and in more than one year |
| 4 Operating | Yes to 1, 2 and 3: and some of it was raised at home |
| 5 Leading | Yes to all four: and the government brought private money into a public project |

- **Corpus's own finance tables answer question 1 for 25 countries and question 2 for 11 before anything is read.** They show a public-private partnership in two, Togo and South Africa, and an African financier in nine; whether that financier is the country's own is read.
- **The row as it stands puts 34 countries at stage 1 because the tables hold nothing for them.** Here nothing held is *No evidence*, and stage 1 needs a source that says so.
- **The amount is not judged, nor its share of GDP.** One dated amount is a yes.
- **A yes to question 3 or 4 answers question 1 and never question 2.** One deal with a local bank in it is stage 2 until a second year is held.
- **A financier is the country's own where the source says so or it is registered there.** A regional group's local subsidiary investing its own money is the company investing itself, and is not a yes to question 3.
- **A deal across several countries counts for a country only where the source names an amount for it.**
- **A deal cancelled, or an investor that has since left, is no longer a yes from that date.**
- **A state-owned operator's own spending is the state's money and is `other`.** Money a private investor or lender puts into it is a yes.

`study.json` holds this as three aspects: `money` (`committed`, `none`) for questions 1 and 2 and stage 1, the years counted from the facts; `home` (`raised`) for question 3; `state` (`brought`) for question 4.

## 4. The norm

Agenda 2063, Goal 20, asks that Africa pay for its own development and that its capital markets carry a growing share. The African Union's Digital Transformation Strategy 2020–2030 calls for private investment and public-private partnerships in digital infrastructure, and Smart Africa set an ambition of USD 300 billion. None sets a figure for a country. This study does not measure a country against any of them.

## 5. What the run reads

- **Carried, nothing opened**: the finance tables in `outputs/non-state-finance/`, for questions 1 and 2, by a carry script written in the run on the pattern of `scripts/study-budget-carry.py`.
- **Read**: 415 news stories about private investment in digital businesses that no study has read for this, in 44 countries, and the 233 short documents the current cells cite: 648 listings in all.
- **Not read**: long texts, reports, passing mentions and the records the tables already hold.

## 6. Token ceiling

**90 million.** The last finance study read 433 listings for 55.9 million; this one lists 648. The run checks after every fan-out and stops at it.

## 7. Tasks, in order

- [x] **D0. Prepare**: this file and `study.json`, 2026-10-13.
- [x] **D1. Bill's word**: run on it, 2026-10-13.
- [x] **D2. Carried and read**: 85 facts from the finance tables in 24 countries; 174 drafters in one fan-out over 648 listings. 260 facts in 39 countries after the parent's reading.
- [x] **D3. Staged** as at 2026-09-30: 4: 4, 3: 11, 2: 20, none at 1 or 5, 4 unplaced, 15 without evidence; agreement 18 of 20.
- [x] **D4. Written, rendered and linted**; on the soft-launch map. **D5. Reported to Bill**, 2026-10-13.

**Decided in the run**:

- **Stage 4**: Egypt, Namibia, Nigeria and South Africa. **No country reaches stage 5**: the four with a signed partnership, Burundi, The Gambia, Liberia and Niger, have nothing raised at home.
- **Namibia's stage 4 rests on a fact the parent added**: RMB Namibia's N$405 million loan to Telecom Namibia, March 2026, which a drafter had filed as money to the state. §3 counts a private lender's money into a state-owned operator. The second stager, reading before it was added, had stage 2.
- **Côte d'Ivoire is stage 2**: every 2025 and 2026 amount held is from CDC-CI Capital, a public fund's investment arm, which is the state's money.
- **Removed by the parent, 15 rows over ten facts** (`corrections.csv`): a memorandum in the Central African Republic, which leaves it without evidence; partnerships approved and not signed in Kenya, and signed with no private amount in DR Congo; a World Bank expectation in Côte d'Ivoire; two grants in the tables that went to a state body and an audit firm.
- **A merge after a removal files the removed row again under a new number.** Five were removed twice; `corrections.csv` says which.
- **Tokens: 89.0 million at the map**, ceiling 90 million, step 1 included.

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
