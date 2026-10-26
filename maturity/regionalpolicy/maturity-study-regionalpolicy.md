---
type: task
reader: cc
title: maturity-study-regionalpolicy.md — the twenty-seventh maturity study: the country's part in regional digital policy, in four questions
last_reviewed: 2026-10-13
status: run 2026-10-13 on Bill's word; staged as at 2026-09-30, written, rendered and on the soft-launch map; waits for Bill to accept
---

# Maturity study: regionalpolicy

*(Commissioned by Bill on 2026-10-13 as `gov.regional--regional-policy-collaboration`, under `maturity/documentation/maturity-study-method.md`.)*

## 1. What is assessed

**The country's part in making digital policy with other African governments, and in carrying out what they agree**, whatever form it takes: membership of an African body that sets digital policy, an agreement or declaration signed with another African government or with such a body, a meeting hosted or chaired, a seat won, and the thing agreed put into effect at home.

*Digital* means telecommunications, the internet, data, digital identity, digital government, digital payments, digital trade, cybersecurity and artificial intelligence. *An African body* is the African Union, one of its regional communities, or a body whose members are mostly African states: the African Telecommunications Union, Smart Africa, a regional association of regulators or of data protection authorities.

The study redraws `gov.regional--regional-policy-collaboration`, which as at 2026-08-31 puts 29 countries at stage 3, 14 at stage 2 and one at stage 1, none at 4 or 5, and leaves ten unplaced. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| Regional cooperation on digital policy | Regional policy collaboration: regional cooperation on digital policy | `gov.regional--regional-policy-collaboration` |

Anything else the evidence names is `other`, noted and never staged: an agreement with a government or body outside Africa, or with a company; a global body or campaign; an Arab League or Francophonie body; a donor's programme no African body runs; a national law brought into line with a regional model, a shared cable or exchange point, and a rule on sending data abroad, each of which has its own row; a trade or political agreement that is not about digital policy.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Does the country belong to an African body that makes digital policy? | A source naming the country as a member of such a body, as joining it, or as taking part in its meeting. Membership of the African Union or a regional community alone is not a yes |
| 2 | Has it taken an active part in the last three years? | A dated agreement, memorandum, protocol or declaration on digital policy signed with another African government or an African body; or a meeting of such a body hosted or chaired; or a seat or office in one won. Talks opened, a visit, or a meeting attended is not a yes |
| 3 | Has anything it agreed been put into effect? | A dated source saying a thing agreed has started in the country: roaming charges cut or removed with a neighbour, a joint committee or council set up, a regional guideline or strategy adopted as a national rule or plan, a shared service opened |
| 4 | Is that reported in use in the last three years? | Published figures of its use; a dated decision of the joint body; or a published review of what the agreement has delivered. A launch, a renewal or a statement of intent is not a yes |

## 3. The ladders

**Regional cooperation on digital policy**

| Stage | Answers |
|---|---|
| 1 Absent | A dated source says the country is suspended from, has left or stands outside the African bodies that make digital policy, with no agreement on record |
| 2 Preparing | Yes to 1: a member, and nothing more on record |
| 3 Establishing | Yes to 1 and 2: an agreement signed, a meeting hosted or chaired, or a seat won, in the last three years |
| 4 Operating | Yes to 1, 2 and 3: something agreed put into effect |
| 5 Leading | Yes to all four: reported in use in the last three years |

- **A yes to a later question answers the earlier ones**: an agreement signed shows the country takes part; a joint body's decision shows it was set up.
- **Membership has no time limit**; it stands, with its year, until a dated source says the country has left or is suspended.
- **Question 3 has no time limit**; what was put into effect stands until a dated source says it has ended. Questions 2 and 4 count for three years.
- **A statement that the country stands outside counts for three years**, and gives way to a dated source naming a membership or an agreement.
- **A suspension from one body is not stage 1** where the country is a member of another or has signed an agreement since. It is named in the summary.
- **Chairing, hosting or holding office is a yes to question 2 and no more.** It shows an active part, not a thing delivered.
- **An agreement approved by one side only, or awaiting signature, is not a yes to question 2.**
- **A regional strategy, declaration or guideline that names the country as bound, with no act of the country's own, is a yes to question 1 only.**
- **A national plan that says it follows a regional one is not a yes to question 3.** The question asks for a dated act that a source ties to what was agreed.
- **A donor's regional programme counts where an African body runs it**, and then as that body's: joining it is a yes to question 1, a financing agreement signed under it a yes to question 2.
- **A declaration that lists the country among many signatories, with no act of its own reported, is a yes to question 1 only** *(added in the run, for the Africa Declaration on Artificial Intelligence and its 49 signatories)*.
- **A body created by signature, its statutes and work programme still to be adopted, is not yet a joint body set up** *(added in the run, for the Council of Sahel Regulators)*. A joint commission that has met is.
- **Projects agreed by a joint body are a statement of intent, not a decision in use** *(added in the run, for Algeria and Tunisia)*.
- **A body of countries that share a language is `other`** *(added in the run)*, as the Francophonie is.
- **A statistics body is not digital policy** *(Bill, 2026-10-26)*.
- **What an agreement covers is taken from what a source says of it**, never from reading its text for the purpose.

`study.json` holds this as two aspects: `part` (`active`, `member`, `none`) for questions 1 and 2, and `effect` (`in-use`, `in-effect`, `none`) for 3 and 4.

## 4. The norm

The African Union's Digital Transformation Strategy for Africa (2020 to 2030) asks member states to coordinate their digital policies through the Union and its regional communities, and its policy and regulation initiative, PRIDA, is the working track. This study asks whether a country belongs, takes an active part, has put what was agreed into effect and has it in use; it does not measure a country's policies against the Strategy.

## 5. What the run reads

- **Read**: the 353 news stories about regional digital cooperation filed to a country; then, for the 22 countries left at stage 2 or without evidence, the stories their current cells cite and, for the eight with nothing, one call of regional stories.
- **Not read**: long texts and reports.

## 6. Token ceiling

**50 million.** The run checks after every fan-out and stops at it.

## 7. Tasks, in order

- [x] **D0. Prepare**: this file and `study.json`, 2026-10-13.
- [x] **D1. Bill's word**: run on it, 2026-10-13.
- [x] **D2. Read**: 127 calls in two fan-outs, 285 facts.
- [x] **D3. Staged** as at 2026-09-30: 5: 5, 4: 10, 3: 23, 2: 15, none at 1, none unplaced, one without evidence; ten rows revalued or removed and two added (`corrections.csv`); agreement 17 of 20.
- [x] **D4. Written, rendered and linted**; on the soft-launch map. **D5. Reported to Bill**, 2026-10-13.

**Decided in the run**:

- **Stage 5**: Burundi, Kenya, Rwanda, Tanzania and Uganda, on the East African regulators' published 2025 figures of calls under the shared roaming area.
- **Stage 4**: a roaming cut in effect for Benin, Botswana, Ghana, The Gambia, Liberia, Namibia, Senegal and Togo; the joint commission for Algeria and Tunisia.
- **Burkina Faso, Mali and Niger are stage 3** on the Sahel regulators' convention.
- **Nigeria is stage 3**: a national forum to plan for the continental digital trade protocol is preparation.
- **South Africa is stage 2**: hosting the regional community's general summit is not a digital policy meeting.
- **Egypt and Libya are stage 2**: their Arab roles, and Libya's audit roadmap with Tunisia, are noted.
- **Eritrea is without evidence.**
- **The second reading differed** on Algeria, Equatorial Guinea and Sudan.
- **Tokens: about 43 million at the map**, ceiling 50 million.

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
