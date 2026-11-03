---
type: task
reader: cc
title: maturity-study-datatransfers.md — the thirtieth maturity study: the rule on sending data out of the country, in four questions
last_reviewed: 2026-10-13
status: run 2026-10-13 on Bill's word; staged as at 2026-09-30, written, rendered and on the soft-launch map; waits for Bill to accept
---

# Maturity study: datatransfers

*(Commissioned by Bill on 2026-10-13 as `gov.regional--cross-border-data-transfers`, under `maturity/documentation/maturity-study-method.md`.)*

## 1. What is assessed

**Whether the country lets data cross its borders while protecting personal data** *(Bill, 2026-10-31, messages-for-bill 58)*: the aim is that a country **encourages** transfers **and** protects the data sent, and the balance between the two is evident. A rule that keeps data at home, or makes every transfer wait on the authority's permission, is over-protective: it hinders the African Continental Free Trade Area as much as having no protection does.

The study redrew `gov.regional--cross-border-data-transfers` on 2026-10-13; Bill's ruling of 2026-10-31 replaced that ladder with this one. It touches no other row, and reads the data localisation and regional law studies' facts as its own (§5).

| Sub-indicator | Indicator text | Id |
|---|---|---|
| Rule on sending data abroad | Cross-border data transfers: rule on sending data abroad | `gov.regional--cross-border-data-transfers` |

Anything else is `other`, noted and never staged: a government data-sharing agreement, a regional guideline or meeting, a privacy forum, or a data protection law no source says rules on sending data abroad.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Is personal data sent abroad protected? | A law, regulation or directive in force, or a bill or published draft, that a source says sets a condition for sending personal data abroad: the receiving country's protection judged good enough, the authority's permission, the person's consent, or a contract |
| 2 | Can data leave without the authority's permission each time? | The rule in force lets some transfers go without a case-by-case permission (to a country judged adequate, on consent, or under a contract), and no rule in force requires personal data in general to be kept in the country |
| 3 | Is there a published way to send data without asking? | A dated source saying the authority has published a list of countries data may go to, model contract terms, or a general authorisation covering a class of transfers. A form or procedure for applying for permission is not a yes |
| 4 | Is the country open to its African partners? | The country has ratified the AfCFTA Digital Trade Protocol or the Malabo Convention, or a source says it treats a regional partner's protection as good enough and that is applied |

## 3. The ladders

**Rule on sending data abroad**

| Stage | Answers |
|---|---|
| 1 Absent | Closed or unprotected: a rule in force keeps personal data in general in the country, with no transfer rule on record; or a dated source says nothing protects personal data sent abroad |
| 2 Preparing | Protected but closed: a transfer rule is being written; or one is in force but every transfer needs the authority's permission, or a rule keeping personal data in general at home stands beside it |
| 3 Establishing | Protected and open: yes to 1 and 2 |
| 4 Operating | Workable: yes to 1, 2 and 3 |
| 5 Leading | Open to Africa: yes to all four |

- **Every lower stage is shown by its own evidence** *(Bill, 2026-10-31, ruling 51)*: a ratification without a transfer rule in force places nothing above stage 1, and a published adequacy list does not answer question 2 where a general localisation rule stands.
- **Questions 1, 2 and 4 have no time limit**: a rule in force or a ratification stands, with its year, until a dated source says it has gone. A statement that nothing protects data sent abroad counts for three years.
- **A rule that keeps one kind of data at home is not general localisation**: banking, payment, health, subscriber or government data. It is noted, and does not answer question 2 no. Personal data in general, or all data of a class of controllers as wide as every company, is general.
- **Every transfer needs permission** where the source says the authority must authorise transfers and names no route without it. Where transfers to adequate countries, on consent or under contract go without it, question 2 is a yes even if the rest need permission.
- **A rule in force whose openness is not shown either way is stage 2**: protected, and not shown open. The gap names question 2.
- **A transfer rule on one kind of data only is noted, not staged**: subscriber, banking or payment data. Question 1 asks about personal data in general.
- **A data protection law alone is not a yes to question 1.** A source must say it sets a condition on sending data abroad. What a law's text says is not read for the purpose.
- **A law passed, with no source saying it has come into effect, is a draft.**
- **Another country's or the European Union's decision about this country is not this country's rule.** It is noted.
- **Signature without ratification is not a yes to question 4.** The ECOWAS Supplementary Act and other community acts bind members without ratification and are not a yes either; a source saying a community partner's protection is treated as adequate is.
- **Permissions granted, fines and counts are noted, not staged**: how often the authority says yes is not the test.

`study.json` holds this as four aspects, one a question and one paragraph each on the country page: `standing` (`in-force`, `draft`, `none`) for 1; `open` (`open`, `closed`) for 2; `route` (`published`) for 3; `africa` (`ratified`, `signed`, `none`) for 4. Carried localisation facts sit under `open` (`localised`, `localising`, `unlocalised`) and the 2026-10-13 ladder's under `route` (`means`, `applied`, `none`), read through question 3's test.

## 4. The norm

The African Union's Convention on Cyber Security and Personal Data Protection (the Malabo Convention), article 14, bars sending personal data to a country outside the Union unless that country protects it adequately. The Union's Data Policy Framework, of 2022, and the digital trade protocol of the African Continental Free Trade Area, of 2024, ask states to let data move across borders under stated safeguards.

## 5. What the run reads

- **Carried, nothing opened**: the facts the data protection and data localisation studies hold that name sending data abroad.
- **Carried for the rescore of 2026-10-31**: every `standing` fact of the data localisation study, as `localise`, and every regional law fact on the Malabo Convention or the AfCFTA Digital Trade Protocol, as `africa`: 179 rows, added to each country's `evidence.csv` with new ids.
- **Read**: the 21 news stories about sending data abroad; the 142 stories the current cells cite; then, for a country still short of an answer to question 1 or 2, one call of the news that mentions the subject in passing.
- **Not read**: the texts of the laws and long reports.

## 6. Token ceiling

**40 million.** The run checks after every fan-out and stops at it.

## 7. Tasks, in order

- [x] **D0. Prepare**: this file and `study.json`, 2026-10-13.
- [x] **D1. Bill's word**: run on it, 2026-10-13.
- [x] **D2. Read**: 27 facts carried from 25 the earlier studies hold; then 90 calls in two fan-outs; 74 facts.
- [x] **D3. Staged** as at 2026-09-30: 5: 5, 4: 5, 3: 19, 2: 3, 1: 3, and 19 without evidence; six rows removed or revalued (`corrections.csv`); agreement 19 of 20, and the twentieth cell restaged the second reader's way.
- [x] **D4. Written, rendered and linted**; on the soft-launch map. **D5. Reported to Bill**, 2026-10-13.

**Decided in the run**: superseded by the rescore of 2026-10-31 below. The run took about 46 million tokens against a ceiling of 40 million.

## Rescore, 2026-10-31

**Bill's ruling of 2026-10-31 (messages-for-bill 58)** replaced the ladder (§1 to §3): the indicator now rewards a country that encourages transfers while protecting personal data. 179 facts were carried in from the data localisation and regional law studies; three Sonnet drafters restaged all 54 cells from the facts alone and rewrote every page, and the parent checked each against the ladder. Every cell is staged by hand; `study-ladder-datatransfers.py` counts the 2026-10-13 ladder and is retired for this study.

- **Now**: `outputs/maturity/datatransfers/assessment.csv` holds the stages.
- **What fell**: regimes that make every transfer wait on permission, and those with a general localisation rule beside their transfer rule. Angola, Nigeria and Uganda fell from 5 to 3: open, but no route without asking is published.
- **Why nearly no one is at 5**: of the nineteen that ratified Malabo, only Cabo Verde, São Tomé and Mauritania are also open, and only Mauritania publishes a route without asking.
- **Next**: the rebuild searches each country on the four new questions; whether permission is needed for every transfer is the question the news least often answers, so a stage-2 cell often means *not shown open*.

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
