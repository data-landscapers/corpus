---
type: task
reader: cc
title: maturity-study-ailaw.md — the twenty-third maturity study: the law or binding rule on artificial intelligence, in four questions
last_reviewed: 2026-10-12
status: run on Bill's word of 2026-10-12; staged, written and on the soft-launch map as at 2026-09-30; awaiting Bill's acceptance
---

# Maturity study: ailaw

*(Commissioned by Bill on 2026-10-12 as `gov.legislate--ai-legislation-regulations`, under `maturity/documentation/maturity-study-method.md`.)*

## 1. What is assessed

**The law, decree or regulation that sets binding rules on how artificial intelligence is built or used**, whatever it is called: an AI act, a regulation on the use of AI issued by a minister or a regulator, or the part of another law that names AI and sets a rule for it.

The study redraws `gov.legislate--ai-legislation-regulations`, which as at 2026-08-31 puts 23 countries at stage 2, 10 at stage 1 and eight at stage 3, none at 4 or 5, leaves 12 unplaced and holds no cell for Cameroon. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| AI law or binding rule | AI legislation / regulations: AI law or binding rule | `gov.legislate--ai-legislation-regulations-ai-law-or-binding-rule` |

Anything else the evidence names is `other`, noted and never staged: an AI strategy or policy, ethics principles or guidelines with no legal force, a data protection law's general rule on automated decisions, a readiness assessment, an AI council, office or institute, a court ruling, a treaty or a continental framework.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Is there a law or binding rule on AI, or a draft of one? | A bill, draft decree or draft regulation published, before parliament or cabinet, or passed, or a law, decree or regulation made. A stated intention to legislate, with no draft begun, is not a yes |
| 2 | Is a binding rule on AI in force? | A law, decree or regulation in force that names AI and sets a rule for it, in one sector or for one use or across all. A bill or draft is not a yes |
| 3 | Is there a law in force on AI itself, and not only for one sector or one use? | An AI act, decree or regulation in force that applies to AI across sectors |
| 4 | Has that law been applied in the last three years? | A dated regulation or order made under it, or a dated registration, licence, decision or penalty by the body it names |

## 3. The ladders

**AI law or binding rule**

| Stage | Answers |
|---|---|
| 1 Absent | A dated source says the country has no law or regulation on AI and no draft of one |
| 2 Preparing | Yes to 1: a bill or draft, and no binding rule in force |
| 3 Establishing | Yes to 1 and 2: a binding rule on AI in force, for one sector or one use |
| 4 Operating | Yes to 1, 2 and 3: a law on AI itself in force |
| 5 Leading | Yes to all four: that law has been applied in the last three years |

- **A yes to a later question answers the earlier ones.**
- **Questions 1 to 3 have no time limit**; a law stands, with its year, until a dated source says it is repealed, replaced or struck down.
- **A statement that there is no law counts for three years**, and gives way to a dated source naming a draft or a rule in force.
- **A source saying there is no AI-specific law, in a country with a sector rule in force, does not undo the sector rule.**
- **A rule for one sector or one use is a yes to question 2 and no more**: AI in higher education, in broadcasting, in elections, in banking. It must name AI.
- **A data protection law's rule on automated decisions places nothing**, and is noted: it is the data protection law row's. This is one change from the row as it stands, which places Cabo Verde at stage 3 on one.
- **A strategy, a policy or ethics guidelines place nothing**, however detailed: they are the AI strategy row's. A strategy that sets out a timetable for a law is not a draft. This is a second change: the row's stage 2 counts guidance without legal effect, and places Libya and Guinea at stage 3 on a strategy and a summit.
- **A consultation or a gap analysis is a yes to question 1 only where a draft text is named.**
- **A private member's bill counts as a bill** while it is before parliament.
- **A law passed but not yet in effect is a yes to question 2**, and the summary gives the date it starts.
- **A decree or regulation counts as well as an act of parliament**, where a source says it binds.
- **How good the law is is not judged.**
- **A third change from the row as it stands**: its stage 4 asks for assessment tools and a regulator together, and its stage 5 is the Continental AI Strategy's end state, with alignment to a regional ethics board. Neither is a fact one story can state.

`study.json` holds this as two aspects: `standing` (`in-force`, `draft`, `none`) for questions 1 and 2, and `reach` (`applied`, `general`, `none`) for 3 and 4.

## 4. The norm

The African Union's Continental AI Strategy, adopted in 2024, asks member states to review and amend existing laws, analyse the gaps and put an enabling framework in place, with independent institutions to oversee it. It sets no date and requires no AI act. This study asks whether a draft exists, a binding rule is in force, a law on AI itself is in force and that law has been applied; it does not measure a law against the strategy.

## 5. What the run reads

- **Read first**: **129 news stories about a law or binding rule on AI**, covering 40 countries. They are 63 stories, a roundup counting once per country it names. Fourteen countries have none.
- **Then, for every country those leave short of an answer**: the news stories its current cell cites, 166 across 49 countries.
- **Then, only for a country with no answer to question 1 or 2**: one call of its newest held news that names such a law, from at most 463 stories across 48 countries.
- **Not read**: the long texts of laws, strategies and reports, 484 of them. **No web search and no handover to OSINT.** A question nothing answers is printed as *Not held*.

## 6. Token ceiling

**50 million.** The run checks after every fan-out and stops at it.

## 7. Tasks, in order

- [x] **D0. Prepare**: this file and `study.json`, 2026-10-12.
- [x] **D1. Bill's word**: run on it, 2026-10-12.
- [x] **D2. Read**: the 129 stories in 49 calls and the 166 cited in 57; then one call each for 14 countries with no answer whose held news names an AI law twice or more, and the Seychelles act's passages. 57 facts held.
- [x] **D3. Staged**: six at stage 3, six at 2, nine at 1, none at 4 or 5, and 33 with no evidence, as at 2026-09-30; six facts removed by the parent (`corrections.csv`); agreement 20 of 20.
- [x] **D4. Written, rendered and linted**; on the soft-launch map. **D5. Reported to Bill**, 2026-10-12.

**Decided in the run**:

- **Stage 3**: Comoros (media code), Gabon (ordinance on AI-generated content), Morocco (electoral law), Mauritius (higher education), Nigeria, Tanzania (online content). **No country has a law on AI itself in force.**
- **Nigeria's data protection directive of 2025 counts**: its articles 43 and 44 name AI and set duties for whoever deploys it. The source is dated after the as-at; the directive is not.
- **A bill announced is not a draft** (Malawi); nor is work said to have begun on a legal framework, with no text named (Algeria, Tunisia). All three hold no fact.
- **A ban for one election campaign is not a rule in force** (Guinea's regulator, 2025).
- **A body saying the country needs an AI law does not say there is none** (Cabo Verde).
- **A draft for one sector is a draft** (Mozambique, education), as is a wider bill that regulates AI among other technologies (Ghana, Nigeria).
- **A statement of no law that names no draft sets stage 1**; only The Gambia's says in terms that none is proposed.
- **A "no law" statement found only in a record's ingest note, not its body, is no fact** (Botswana, Madagascar): six of the row's ten stage 1 cells now hold no evidence.
- **Seychelles holds no fact**: the passages held of its Broadcasting Corporation Act do not carry the AI clause.
- **The summaries were written by the parent.** **Tokens: 41.3 million at the map**, ceiling 50 million.

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
