---
type: task
reader: cc
title: maturity-study-ecommercelaw.md — the twenty-fourth maturity study: the law on electronic transactions and selling online, in four questions
last_reviewed: 2026-10-13
status: prepared 2026-10-13; nothing read or staged; waits for Bill's word on the questions
---

# Maturity study: ecommercelaw

*(Commissioned by Bill on 2026-10-13 as `gov.legislate--e-commerce-legislation`, under `maturity/documentation/maturity-study-method.md`.)*

## 1. What is assessed

**The law that makes a contract, record or signature made electronically as valid as one on paper, and sets the rules for selling online**, whatever it is called: an electronic transactions act, an e-commerce law, an electronic signature law, or the part of a digital code, a communications act or a consumer protection law that does that job.

The study redraws `gov.legislate--e-commerce-legislation`, which as at 2026-08-31 puts 30 countries at stage 3, five at stage 2 and two at stage 1, none at 4 or 5, leaves 16 unplaced and holds no cell for São Tomé and Príncipe. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| E-commerce law | E-commerce legislation: e-commerce law | `gov.legislate--e-commerce-legislation-e-commerce-law` |

Anything else the evidence names is `other`, noted and never staged: an e-commerce strategy or policy, a tax on digital services or online sales, an electronic invoicing rule, a copyright or intellectual property bill, a law on online media, platforms or social networks, rules for ride-hailing or courier services, a consumer protection law that says nothing of online selling, a signature platform or public key system itself, the data protection, cybercrime and payments laws, a treaty or a regional model law.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Is there a law on electronic transactions or e-commerce, or a draft of one? | A bill or draft published, out for consultation, before cabinet or parliament, or passed, or a law made. A law only announced or planned is not a yes |
| 2 | Is that law in force? | A law, ordinance or decree in force that gives electronic contracts, records or signatures legal effect, or sets rules for selling online. A bill or draft is not a yes |
| 3 | Have rules been made under it to put it to work? | A dated decree, regulation or order made under the law: on electronic signatures, on those who certify them, or on those who sell online |
| 4 | Has it been applied in the last three years? | A dated accreditation or licence of a provider of electronic signatures or certificates under it, a registration or licence of an online seller or digital operator under it, or a penalty or order made under it |

## 3. The ladders

**E-commerce law**

| Stage | Answers |
|---|---|
| 1 Absent | A dated source says the country has no law on electronic transactions or e-commerce and no draft of one |
| 2 Preparing | Yes to 1: a bill or draft, and no law in force |
| 3 Establishing | Yes to 1 and 2: a law in force |
| 4 Operating | Yes to 1, 2 and 3: rules made under it |
| 5 Leading | Yes to all four: the law applied in the last three years |

- **A yes to a later question answers the earlier ones**: a signature provider accredited under the law shows the law is in force.
- **Questions 1 to 3 have no time limit**; a law stands, with its year, until a dated source says it is repealed, replaced or struck down.
- **A statement that there is no law counts for three years**, and gives way to a dated source naming a draft or a law in force.
- **A law on electronic signatures alone is a yes to question 2**: it gives electronic dealings legal effect. The summary says the law covers signatures only.
- **A digital code, a communications act or a consumer protection law counts for the part that does the job**, where a source says it covers electronic transactions or online selling.
- **An old law still in force is a yes to question 2 and no more**, until a source names rules made under it. A bill to replace it is named in the summary and does not lower the stage.
- **A law passed but not yet in effect is a yes to question 2**, and the summary gives the date it starts.
- **A regional act or model law places nothing** until a source says the country has made it its own law.
- **A government office using electronic signatures is not a yes to question 4**; nor is a signature platform launched or a contract to build one. The question asks for an accreditation, licence, registration or penalty under the law.
- **A state body named as the national certification authority is a yes to question 4** where a source says it is named or accredited under the law.
- **What the law covers is taken from what a source says of it**, never from reading its text for the purpose.
- **How good the law is is not judged.** A reported criticism is noted.
- **Three changes from the row as it stands.** Sixteen cells are unplaced, most leading with something that is not this law: a copyright bill (Kenya), a sovereignty bill (Uganda), an e-commerce strategy (Somalia, South Sudan). Its stage 4 asks for consumer provisions, signature rules, accredited providers and enforcement together. Its stage 5 is four laws in force and consistent with each other, three of them other rows'. Neither is a fact one story can state.

`study.json` holds this as two aspects: `standing` (`in-force`, `draft`, `none`) for questions 1 and 2, and `reach` (`applied`, `rules`, `none`) for 3 and 4.

## 4. The norm

Chapter I of the Malabo Convention sets rules for electronic commerce, contracts and advertising, and Article 16 of the AfCFTA Digital Trade Protocol commits each party to a legal framework for electronic transactions, Article 27 to protecting those who buy online. This study asks whether a law exists, is in force, has rules made under it and has been applied; it does not measure the law against either.

## 5. What the run reads

- **Read first**: **108 news stories and short legal notices about an electronic transactions, e-commerce or electronic signature law**, covering 37 countries, 94 of them from the last three years. No study has read them. They are 102 stories, a regional one counting once per country it names. Seventeen countries have none.
- **Then, for every country those leave short of an answer**: the news stories its current cell cites, 155 across 53 countries.
- **Then, only for a country with no answer to question 1 or 2**: one call of its newest held news that names such a law, from at most 428 stories.
- **Not read**: the long texts of the laws, codes and reports. **No web search and no handover to OSINT.** A question nothing answers is printed as *Not held*.

## 6. Token ceiling

**50 million.** The run checks after every fan-out and stops at it.

## 7. Tasks, in order

- [x] **D0. Prepare**: this file and `study.json`, 2026-10-13.
- [ ] **D1. Bill's word** on the four questions.
- [ ] **D2. Read**: `study-select.py ecommercelaw`, then the 108 stories, then what the current cells cite where an answer is short.
- [ ] **D3. Stage** as at 2026-09-30: `scripts/study-ladder-ecommercelaw.py`, the parent's reading of every fact setting stages 4 and 5, and 20 cells restaged blind.
- [ ] **D4. Write, render and lint**; the soft-launch map. **D5. Report to Bill**, with the tokens used.

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
