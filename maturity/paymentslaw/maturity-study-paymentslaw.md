---
type: task
reader: cc
title: maturity-study-paymentslaw.md — the twenty-first maturity study: the law on electronic payments, in four questions
last_reviewed: 2026-10-12
status: prepared 2026-10-12; nothing run; waits for Bill's word on the four questions
---

# Maturity study: paymentslaw

*(Commissioned by Bill on 2026-10-12 as `gov.legislate--digital-payments-legislation`, under `maturity/documentation/maturity-study-method.md`.)*

## 1. What is assessed

**The law or central bank rules that say who may run electronic payments and issue electronic money, and on what terms**, whatever it is called: a national payment system act, a payment services law, e-money or mobile money regulations, or the part of a banking law or a regional central bank's regulation that does that job.

The study redraws `gov.legislate--digital-payments-legislation`, which as at 2026-08-31 puts 35 countries at stage 3 and four at stage 2, none at 1, 4 or 5, leaves 13 unplaced and holds no cell for Cameroon or Senegal. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| Payments law | Digital payments legislation: payments law | `gov.legislate--digital-payments-legislation-payments-law` |

Anything else the evidence names is `other`, noted and never staged: a payment system, switch or instant payment scheme itself, a law or rules on crypto and virtual assets, a central bank digital currency, a general banking or central bank law that says nothing of payment providers, anti-money-laundering rules, a regulatory sandbox, a payments strategy or vision, a tax on mobile money, a treaty.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Is there a payments law or e-money rules, or a draft of either? | A bill or draft regulation published, before parliament or passed, or a law or rules made. Mobile money run on a central bank's letter of no objection alone, with no rules behind it, is a yes here and no further |
| 2 | Is the law, or are the rules, in force? | A payments law promulgated and in force, or central bank regulations, directives or guidelines on e-money or payment services issued and binding. A bill or draft is not a yes |
| 3 | Can a company that is not a bank be licensed under it to offer payments? | A source says the law or rules in force license payment providers or e-money issuers that are not banks, or names one licensed under them |
| 4 | Does a rule require payment providers to connect to each other? | A dated rule in force that mobile money providers and banks must connect to each other or to a national or regional switch |

## 3. The ladders

**Payments law**

| Stage | Answers |
|---|---|
| 1 Absent | A dated source says the country has no payments law or e-money rules and no draft of either |
| 2 Preparing | Yes to 1: a bill or draft rules, or mobile money allowed by letter alone, and nothing in force |
| 3 Establishing | Yes to 1 and 2: a law or rules in force |
| 4 Operating | Yes to 1, 2 and 3: companies that are not banks can be licensed under it |
| 5 Leading | Yes to all four: a rule requires providers to connect to each other |

- **A yes to a later question answers the earlier ones**: a non-bank licensed under the rules shows the rules are in force.
- **No question has a time limit**; a law or rule stands, with its year, until a dated source says it is repealed, replaced or struck down.
- **A statement that there is no law counts for three years.**
- **A regional central bank's regulation counts for each member country it binds**: the BCEAO's for the eight WAEMU states, the CEMAC and BEAC regulations for the six CEMAC states. A licence is a yes to question 3 only for the country it is issued in.
- **Central bank rules count as well as acts of parliament.** In most countries the binding text on e-money is a regulation or guideline, and a source naming it as binding is enough.
- **An old law still in force is a yes to question 2 and no more**, until a source says non-banks are licensed under it. A bill to replace it is named in the summary and does not lower the stage.
- **A law passed but not yet in effect is a yes to question 2**, and the summary gives the date it starts.
- **Whether the law covers non-banks or requires connection is taken from what a source says of it**, never from reading its text for the purpose.
- **Question 4 asks for the rule, not the switch.** A switch that providers may join, or have joined by choice, is not a yes; a deadline set by the regulator to connect is.
- **A rule that only banks must connect is not a yes to question 4.**
- **A crypto or virtual asset law is not the payments law.** The current cells for Kenya and Nigeria lead with one; it is noted.
- **Consumer protection and the central bank's oversight role are other rows** and are not asked here.
- **How good the law is, and whether it is enforced, are not judged.** A reported criticism is noted.
- **Two changes from the row as it stands**: its stage 4 asks for non-bank licensing, interoperability rules and consumer protection together, with enforcement on record; its stage 5 is the AfCFTA Digital Trade Protocol's end state, with cross-border participation and anti-money-laundering embedded. Neither is a fact one story can state.

`study.json` holds this as two aspects: `standing` (`in-force`, `draft`, `none`) for questions 1 and 2, and `reach` (`connect`, `non-bank`, `none`) for 3 and 4.

## 4. The norm

Article 15 of the AfCFTA Digital Trade Protocol and its Annex on Cross-Border Digital Payments commit each party to interoperable payment systems, and Article 7 of the Malabo Convention to state-approved electronic payment methods. This study asks whether a law exists, is in force, licenses non-banks and requires providers to connect; it does not measure the law against either.

## 5. What the run reads

- **Read first**: **97 news stories and short legal notices about a payments law or e-money rules**, covering 40 countries, 82 of them from the last three years. No study has read them. A regional story is read once for each member country it names, 154 readings in all.
- **Then, for every country those leave short of an answer**: the news stories its current cell cites, 169 across 48 countries.
- **Then, only for a country still short of an answer to question 1 or 2**: the newest held news that names such a law, one call a country, from at most 483 stories across 47 countries.
- **Not read**: the long texts of the laws and reports, 191 of them. A law's text is opened only for a country with nothing else.
- **No web search and no handover to OSINT.** A question nothing answers is printed as *Not held*.

## 6. Token ceiling

**50 million.** The run checks after every fan-out and again after the writing step, and stops and reports if it reaches it. The reading is about half as large again as the identity law study's, which used 35.9 million. No earlier study holds facts that answer these questions, so nothing is carried. The parent writes the summaries.

## 7. Tasks, in order

- [x] **D0. Prepare**: this file and `study.json`, 2026-10-12.
- [ ] **D1. Bill's word** on the four questions.
- [ ] **D2. Read**, in the order of §5.
- [ ] **D3. Stage**: as at 2026-09-30; the parent reads every fact that would set stage 4 or 5; two drafters compared on 20 cells.
- [ ] **D4. Write, render and lint**; the soft-launch map. **D5. Report to Bill.**

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
