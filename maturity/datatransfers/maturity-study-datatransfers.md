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

**The government's rule on when personal data, or a named kind of data, may be sent out of the country**, whatever it is called and whoever issues it: the part of a data protection law that sets the condition, a regulation, a regulator's or central bank's directive, and what the authority publishes and decides under it.

The study redraws `gov.regional--cross-border-data-transfers`, which as at 2026-08-31 puts 13 countries at stage 3, three at stage 2, two at stage 4 and one at stage 1, none at 5, and leaves 35 unplaced. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| Rule on sending data abroad | Cross-border data transfers: rule on sending data abroad | `gov.regional--cross-border-data-transfers-rule-on-sending-data-abroad` |

Anything else the evidence names is `other`, noted and never staged: an agreement by the government to share data with another government or a donor, such as a health memorandum; a rule that data must be kept in the country, which the data localisation row holds; a treaty or trade protocol with a clause on data flows, which the regional law row holds; a regional guideline being drafted, or a meeting on data flows, which the regional policy row holds; membership of an international privacy forum; a data protection law with no source saying what it rules on sending data abroad.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Is there a rule on sending personal data out of the country, or one being written? | A law, regulation or directive, or a bill or published draft of one, that a source says sets a condition for sending data abroad: the receiving country's protection judged good enough, the authority's permission, the person's consent, or a contract. A stated intention with no drafting begun is not a yes |
| 2 | Is the rule in force? | Enacted or issued, in effect, and not repealed or withdrawn |
| 3 | Has the authority published the means of complying? | A dated source saying the authority has published any of: a list of countries data may go to, model contract terms, a form or procedure for applying for permission, or guidance on transfers |
| 4 | Has the rule been applied in the last three years? | A dated source naming a country approved to receive data, or an organisation given or refused permission, ordered to comply or penalised for sending data abroad; or a published count of permissions given |

## 3. The ladders

**Rule on sending data abroad**

| Stage | Answers |
|---|---|
| 1 Absent | A dated source says the country has no rule on sending personal data abroad and none is being written |
| 2 Preparing | Yes to 1: a rule being written |
| 3 Establishing | Yes to 1 and 2: a rule in force |
| 4 Operating | Yes to 1, 2 and 3: the authority has published the means of complying |
| 5 Leading | Yes to all four: the rule has been applied in the last three years |

- **A yes to a later question answers the earlier ones**: an organisation fined for sending data abroad without permission shows a rule in force.
- **Questions 1 to 3 have no time limit**: a rule in force stands, with its year, until a dated source says it has been repealed or withdrawn. Question 4 counts for three years.
- **A statement that there is no rule counts for three years**, and gives way to a dated source naming one.
- **A data protection law alone is not a yes.** A source must say the law sets a condition on sending data abroad. What a law's text says is not read for the purpose.
- **A rule on one kind of data counts**: banking, health, subscriber or government data. The summary names the data and who must comply.
- **A rule that data must stay in the country is not a yes here.** A rule that data may leave with permission, or with a copy kept at home, is.
- **A law in force whose authority does not yet exist is a yes to question 2**; the summary says so.
- **A rule issued with a later compliance date is a yes to question 2**, and the summary gives the date.
- **Guidance on the whole law that only mentions transfers is not a yes to question 3.**
- **A penalty counts for question 4 only where a source ties it to sending data abroad.**
- **Another country's or the European Union's decision about this country is not this country's rule applied.** It is noted.
- **A law passed, with no source saying it has come into effect, is a yes to question 1 only** *(added in the run, for Zambia and Malawi's Act as first passed)*.
- **A procedure set out in the rule's own text is not the authority publishing the means** *(added in the run, for Côte d'Ivoire)*.
- **A ban on sending a kind of data abroad, with no condition on which it may leave, is not a yes** *(added in the run, for Burkina Faso)*.
- **A source saying the country does not generally restrict sending data abroad is not a rule in force** *(added in the run, for Mozambique)*.
- **A count of requests approved, given by the authority's head to the press, is a published count** *(added in the run, for Ethiopia)*.
- **A stage says how far the rule has been put to work.** Whether it is strict or loose, and whether it matches the African Union's framework, is not judged. This is the change from the row as it stands, whose stage 5 is agreement with that framework.

`study.json` holds this as two aspects: `standing` (`in-force`, `draft`, `none`) for questions 1 and 2, and `use` (`applied`, `means`, `none`) for 3 and 4.

## 4. The norm

The African Union's Convention on Cyber Security and Personal Data Protection (the Malabo Convention), article 14, bars sending personal data to a country outside the Union unless that country protects it adequately. The Union's Data Policy Framework, of 2022, and the digital trade protocol of the African Continental Free Trade Area, of 2024, ask states to let data move across borders under stated safeguards. This study asks whether a rule exists, is in force, has published means of complying and has been applied; it does not judge the rule.

## 5. What the run reads

- **Carried, nothing opened**: the facts the data protection and data localisation studies hold that name sending data abroad.
- **Read**: the 21 news stories about sending data abroad; the 142 stories the current cells cite; then, for a country still short of an answer to question 1 or 2, one call of the news that mentions the subject in passing.
- **Not read**: the texts of the laws and long reports. **No web search and no handover to OSINT.**

## 6. Token ceiling

**40 million.** The run checks after every fan-out and stops at it.

## 7. Tasks, in order

- [x] **D0. Prepare**: this file and `study.json`, 2026-10-13.
- [x] **D1. Bill's word**: run on it, 2026-10-13.
- [x] **D2. Read**: 27 facts carried from 25 the earlier studies hold; then 90 calls in two fan-outs; 74 facts.
- [x] **D3. Staged** as at 2026-09-30: 5: 5, 4: 5, 3: 19, 2: 3, 1: 3, and 19 without evidence; six rows removed or revalued (`corrections.csv`); agreement 19 of 20, and the twentieth cell restaged the second reader's way.
- [x] **D4. Written, rendered and linted**; on the soft-launch map. **D5. Reported to Bill**, 2026-10-13.

**Decided in the run**:

- **Stage 5**: Angola, Ethiopia, Mauritius, Uganda and Zimbabwe. **Stage 4**: Botswana, Kenya, Mauritania, Morocco and Tunisia.
- **Nigeria is stage 3**: its 2025 fine followed an investigation that covered transfers, and the source does not tie the penalty to them.
- **Zambia is stage 2**: the one source held says the Act starts on a date the minister appoints and gives none.
- **Mozambique is stage 2** on its 2026 bill; **Burkina Faso has no evidence**, its bill being reported only as a ban.
- **Eritrea, Namibia and Sudan are stage 1**; Namibia's on an opposition member of parliament's statement.
- **Nineteen countries are without evidence**, Egypt, Rwanda, Benin and Togo among them: their news does not say what the law rules on sending data abroad.
- **Tokens: about 46 million at the map**, ceiling 40 million, step 1 included. The writers took it over; the run was past its last fan-out when the count was read.

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
