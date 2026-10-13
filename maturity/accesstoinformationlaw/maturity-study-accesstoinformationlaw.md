---
type: task
reader: cc
title: maturity-study-accesstoinformationlaw.md — the twenty-sixth maturity study: the access to information law, in four questions
last_reviewed: 2026-10-13
status: prepared 2026-10-13; waits for Bill to confirm the questions
---

# Maturity study: accesstoinformationlaw

*(Commissioned by Bill on 2026-10-13 as `gov.legislate--access-to-information-legislation`, under `maturity/documentation/maturity-study-method.md`.)*

## 1. What is assessed

**The law that gives a person the right to ask a public body for the information it holds, and obliges the body to answer**, whatever it is called: an access to information act, a right to information or freedom of information law, a law on access to administrative documents, an ordinance with the force of law, or the part of a wider law or code that does that job.

The study redraws `gov.legislate--access-to-information-legislation`, which as at 2026-08-31 puts one country at stage 4, 25 at stage 3, 13 at stage 2 and five at stage 1, none at 5, and leaves ten unplaced. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| Access to information law | Access to information legislation: access to information law | `gov.legislate--access-to-information-legislation-access-to-information-law` |

Anything else the evidence names is `other`, noted and never staged: a right of access written in the constitution with no law behind it, an open data policy or portal, an open government action plan, a state secrets or classification law, a press, media or broadcasting law, a whistleblower law, an archives law, the data protection law and its authority, a ranking of the law by an outside body, the African Union's model law and the treaties.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Is there an access to information law, or a draft of one? | A bill or draft published, validated, out for consultation, before cabinet or parliament, or passed, or a law made. A law only announced, planned or called for is not a yes |
| 2 | Is that law in force? | A law, ordinance or decree with the force of law in force that gives a right to ask public bodies for information. A bill or draft is not a yes |
| 3 | Has it been put to work: rules made under it, or the body that oversees it set up? | A dated decree, regulation or order made under the law; or the information commission or commissioner the law provides for appointed; or an existing body the law names, such as an ombudsman or a human rights commission, reported as having taken up the job |
| 4 | Has it been applied in the last three years? | A dated decision, order or penalty by the oversight body or a court on a request made under the law; a report by the oversight body giving the number of requests or complaints; or a rule made under the law |

## 3. The ladders

**Access to information law**

| Stage | Answers |
|---|---|
| 1 Absent | A dated source says the country has no access to information law and no draft of one |
| 2 Preparing | Yes to 1: a bill or draft, and no law in force |
| 3 Establishing | Yes to 1 and 2: a law in force |
| 4 Operating | Yes to 1, 2 and 3: rules made under it, or its oversight body set up |
| 5 Leading | Yes to all four: the law applied in the last three years |

- **A yes to a later question answers the earlier ones**: a commission ruling on a request shows the law is in force and the commission set up.
- **Questions 1 to 3 have no time limit**; a law stands, with its year, until a dated source says it is repealed, replaced, suspended or struck down.
- **A statement that there is no law counts for three years**, and gives way to a dated source naming a draft or a law in force.
- **A right of access in the constitution is not a law.** With a source saying no law gives it effect, the country is at stage 1.
- **A wider law or code counts for the part that does the job**, where a source says it gives a right to ask public bodies for information.
- **An ordinary decree, a charter, a policy or a circular on access to information is not a law and not a draft of one.** An ordinance or decree with the force of law is a law.
- **An old law still in force is a yes to question 2 and no more**, until a source names rules made under it or its oversight body. A bill to amend or replace it is named in the summary and does not lower the stage.
- **A law promulgated but not yet in effect is a yes to question 2**, and the summary gives the date it starts. One passed by parliament and not yet promulgated is a yes to question 1 only.
- **A body that also protects personal data counts only for what a source says it did under the access to information law.** A data protection ruling is not a yes to question 4.
- **A budget voted to the commission shows it is set up**, a yes to question 3 and no more.
- **Training, an awareness week, a call for applications, or information officers named is not a yes to question 4.** The question asks for a decision, a penalty or published figures.
- **A request reported as refused or ignored, with no decision by the oversight body or a court, is not a yes to question 4.** It is noted.
- **What the law covers is taken from what a source says of it**, never from reading its text for the purpose.
- **How good the law is is not judged**, nor whether it matches the model law. A reported criticism is noted.
- **Changes from the row as it stands.** Its stage 4 asks for procedures, proactive disclosure, an oversight body and requests on record all together, and its stage 5 for the model law met. Neither is a fact one story can state, which is why one country sits above stage 3. Several of its ten unplaced cells lead with something that is not this law.

`study.json` holds this as two aspects: `standing` (`in-force`, `draft`, `none`) for questions 1 and 2, and `reach` (`applied`, `rules`, `none`) for 3 and 4.

## 4. The norm

The African Commission's Declaration of Principles on Freedom of Expression and Access to Information (2019) sets out a right of access, a duty to publish and an independent oversight body set up by law, and its Model Law on Access to Information (2013) is the template. This study asks whether a law exists, is in force, has been put to work and has been applied; it does not measure the law against either.

## 5. What the run reads

- **Read first**: **74 news stories and short legal notices about an access to information law**, covering 30 countries, 63 of them from the last three years. No study has read them. Twenty-four countries have none.
- **Then, for every country those leave short of an answer**: the news stories its current cell cites, 66 across 36 countries.
- **Then, only for a country still short of an answer**: one call of its newest held news that names such a law, from at most 206 stories.
- **Not read**: the long texts of the laws, codes and reports. **No web search and no handover to OSINT.** A question nothing answers is printed as *Not held*.

## 6. Token ceiling

**45 million.** The run checks after every fan-out and stops at it.

## 7. Tasks, in order

- [x] **D0. Prepare**: this file and `study.json`, 2026-10-13.
- [ ] **D1. Bill's word.**
- [ ] **D2. Read.**
- [ ] **D3. Stage**, as at 2026-09-30.
- [ ] **D4. Write, render and lint**; the soft-launch map. **D5. Report to Bill.**

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
