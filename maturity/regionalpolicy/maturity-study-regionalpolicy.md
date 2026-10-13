---
type: task
reader: cc
title: maturity-study-regionalpolicy.md — the twenty-seventh maturity study: the country's part in regional digital policy, in four questions
last_reviewed: 2026-10-13
status: prepared 2026-10-13; waits for Bill to confirm the questions
---

# Maturity study: regionalpolicy

*(Commissioned by Bill on 2026-10-13 as `gov.regional--regional-policy-collaboration`, under `maturity/documentation/maturity-study-method.md`.)*

## 1. What is assessed

**The country's part in making digital policy with other African governments, and in carrying out what they agree**, whatever form it takes: membership of an African body that sets digital policy, an agreement or declaration signed with another African government or with such a body, a meeting hosted or chaired, a seat won, and the thing agreed put into effect at home.

*Digital* means telecommunications, the internet, data, digital identity, digital government, digital payments, digital trade, cybersecurity and artificial intelligence. *An African body* is the African Union, one of its regional communities, or a body whose members are mostly African states: the African Telecommunications Union, Smart Africa, a regional association of regulators or of data protection authorities.

The study redraws `gov.regional--regional-policy-collaboration`, which as at 2026-08-31 puts 29 countries at stage 3, 14 at stage 2 and one at stage 1, none at 4 or 5, and leaves ten unplaced. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| Regional cooperation on digital policy | Regional policy collaboration: regional cooperation on digital policy | `gov.regional--regional-policy-collaboration-regional-cooperation-on-digital-policy` |

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
- **An agreement between two African governments counts as one made in a regional body does.**
- **An agreement approved by one side only, or awaiting signature, is not a yes to question 2.**
- **A regional strategy, declaration or guideline that names the country as bound, with no act of the country's own, is a yes to question 1 only.**
- **A national plan that says it follows a regional one is not a yes to question 3.** The question asks for a dated act that a source ties to what was agreed.
- **A donor's regional programme counts where an African body runs it**, and then as that body's: joining it is a yes to question 1, a financing agreement signed under it a yes to question 2.
- **What an agreement covers is taken from what a source says of it**, never from reading its text for the purpose.
- **How much the cooperation has achieved is not judged.** A reported criticism is noted.
- **Changes from the row as it stands.** Its stage 4 asks for regional rules carried out in more than one area with reporting to the regional body, and its stage 5 for a national strategy stating its alignment, which no one story can state.

`study.json` holds this as two aspects: `part` (`active`, `member`, `none`) for questions 1 and 2, and `effect` (`in-use`, `in-effect`, `none`) for 3 and 4.

## 4. The norm

The African Union's Digital Transformation Strategy for Africa (2020 to 2030) asks member states to coordinate their digital policies through the Union and its regional communities, and its policy and regulation initiative, PRIDA, is the working track. This study asks whether a country belongs, takes an active part, has put what was agreed into effect and has it in use; it does not measure a country's policies against the Strategy.

## 5. What the run reads

- **Read first**: **353 news stories about regional digital cooperation filed to a country**, covering 52 countries, 247 of the 257 distinct stories from the last three years. No study has read them. Equatorial Guinea and Sudan have none.
- **Then, for every country those leave short of an answer**: the news stories its current cell cites, 209 across 54 countries.
- **Then, only for a country still short of an answer**: one call of the regional stories that name it, from 55 stories shared across countries.
- **Not read**: treaties, strategies, communiqués at length and reports. **No web search and no handover to OSINT.** A question nothing answers is printed as *Not held*.

## 6. Token ceiling

**50 million.** The run checks after every fan-out and stops at it.

## 7. Tasks, in order

- [x] **D0. Prepare**: this file and `study.json`, 2026-10-13.
- [ ] **D1. Bill's word.**
- [ ] **D2. Read.**
- [ ] **D3. Stage**, as at 2026-09-30.
- [ ] **D4. Write, render and lint**; the soft-launch map. **D5. Report to Bill.**

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
