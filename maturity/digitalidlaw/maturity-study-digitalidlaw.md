---
type: task
reader: cc
title: maturity-study-digitalidlaw.md — the twentieth maturity study: the national identity law, in four questions
last_reviewed: 2026-10-12
status: prepared 2026-10-12; nothing run; waits for Bill's word on the four questions
---

# Maturity study: digitalidlaw

*(Commissioned by Bill on 2026-10-12 as `gov.legislate--legislation-covering-digital-id`, under `maturity/documentation/maturity-study-method.md`.)*

## 1. What is assessed

**The law that sets up the country's identity system: the identity number, the register of persons or the identity card, and the body that runs it**, whatever it is called: an act of its own, an ordinance or decree-law with the force of law, or the part of a civil registration law, a trust services law or a digital code that does that job.

The study redraws `gov.legislate--legislation-covering-digital-id`, which as at 2026-08-31 puts 37 countries at stage 3 and six at stage 2, none at 1, 4 or 5, leaves ten unplaced and holds no cell for Burkina Faso. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| National identity law | Legislation covering digital id: national identity law | `gov.legislate--legislation-covering-digital-id-national-identity-law` |

Anything else the evidence names is `other`, noted and never staged: the identity system or project itself, a digital identity strategy or policy, a data protection law, a law on electronic signatures alone, a civil registration law that sets up no identity number or card, SIM card registration rules, a voters' roll law, a nationality or passport law, a treaty.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Is there a national identity law, or a bill for one? | A bill drafted, before parliament or passed, or a law. An identity system run on a decree or order alone, with no law behind it, is a yes here and no further |
| 2 | Is the law in force? | A law, ordinance or decree-law promulgated and in force, standing alone or as part of a larger law or code. A bill is not a yes |
| 3 | Does the law provide for a digital identity? | A source says the law in force sets up a biometric register, an identity number unique to each person, or an identity that can be checked electronically. A law for a paper card only is not a yes |
| 4 | Have rules been made under it in the last three years? | A dated regulation or decree applying the law, or a dated rule made under it that banks, phone companies or public bodies must check identity against the system |

## 3. The ladders

**National identity law**

| Stage | Answers |
|---|---|
| 1 Absent | A dated source says the country has no national identity law and no bill for one |
| 2 Preparing | Yes to 1: a bill, or a system run on a decree alone, and no law in force |
| 3 Establishing | Yes to 1 and 2: a law in force |
| 4 Operating | Yes to 1, 2 and 3: the law in force provides for a digital identity |
| 5 Leading | Yes to all four: rules have been made under that law in the last three years |

- **A yes to a later question answers the earlier ones**: a regulation made under a law shows the law is in force.
- **Questions 1 to 3 have no time limit**; a law stands, with its year, until a dated source says it is repealed, replaced or struck down.
- **A statement that there is no law counts for three years.**
- **An old law still in force is a yes to question 2 and no more**, until a source says it, or an amendment to it, provides for the digital identity. A bill to replace it is named in the summary and does not lower the stage.
- **Whether a law covers digital identity is taken from what a source says of it**, never from reading its text for the purpose.
- **A law passed but not yet in effect is a yes to question 2**, and the summary gives the date it starts.
- **A court ruling that suspends or strikes down the law reverses the yes** from its date.
- **Cards issued and people enrolled are not rules made under the law**: the digital identity rows read those. Nor is a change to fees.
- **A data protection law is not the identity law.** That it applies to the identity system is noted.
- **A civil registration law counts only where it also sets up the identity number, register or card.**
- **A trust services or electronic transactions law counts only where a source says it sets up the national electronic identity**, not for signatures alone.
- **How good the law is, and whom it leaves out, are not judged.** A reported criticism is noted.
- **Two changes from the row as it stands**: its stage 4 asks for regulations, an authority, rights to enrol, data protection, grievance and oversight together, applied in practice; its stage 5 is the African Union interoperability framework's end state, with the Malabo Convention ratified. Neither is a fact one story can state.

`study.json` holds this as two aspects: `standing` (`in-force`, `bill`, `none`) for questions 1 and 2, and `cover` (`applied`, `digital`, `none`) for 3 and 4.

## 4. The norm

The African Union's Digital Transformation Strategy sets a target of digital legal identity for 99.9% of people by 2030, and its Interoperability Framework for Digital ID (§4.1) asks for a harmonised enabling legal framework. Article 14 of the AfCFTA Digital Trade Protocol commits each party to adopt or maintain digital identity systems. This study asks whether a law exists, is in force, provides for a digital identity and has had rules made under it; it does not measure the law against any of the three.

## 5. What the run reads

- **Read first**: **82 news stories and short legal notices about a national identity law**, across 28 countries, 58 of them from the last three years. No study has read them.
- **Then, for every country those leave short of an answer**: the news stories its current cell cites, 128 across 46 countries.
- **Then, only for a country still short of an answer to question 1 or 2**: the newest held news that names such a law, one call a country, from at most 455 stories across 45 countries.
- **Not read**: the long texts of the laws and reports, 376 of them. A law's text is opened only for a country with nothing else.
- **No web search and no handover to OSINT.** A question nothing answers is printed as *Not held*.

## 6. Token ceiling

**40 million.** The run checks after every fan-out and again after the writing step, and stops and reports if it reaches it. The reading is the size of the cybercrime law study's. The registry study holds identity facts but none that answers these questions, so nothing is carried. The parent writes the summaries.

## 7. Tasks, in order

- [x] **D0. Prepare**: this file and `study.json`, 2026-10-12.
- [ ] **D1. Bill's word** on the four questions.
- [ ] **D2. Read**, in the order of §5.
- [ ] **D3. Stage**: as at 2026-09-30; the parent reads every fact that would set stage 4 or 5; two drafters compared on 20 cells.
- [ ] **D4. Write, render and lint**; the soft-launch map. **D5. Report to Bill.**

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
