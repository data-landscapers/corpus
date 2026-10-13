---
type: task
reader: cc
title: maturity-study-opendiscussion.md — the thirty-fifth maturity study: freedom to discuss government policy online and in the press, in four questions
last_reviewed: 2026-10-13
status: prepared 2026-10-13; waits for Bill to confirm the questions
---

# Maturity study: opendiscussion

*(Commissioned by Bill on 2026-10-13 as `gov.discourse--open-discussion-of-government-policy`, under `maturity/documentation/maturity-study-method.md`.)*

## 1. What is assessed

**Whether people can argue in public about what the government does, online and in the press, without the internet being cut or anyone being punished for it.**

**A cut** is the internet, mobile data, a social media or messaging service, or a news site switched off, slowed or blocked by order of the government, a regulator or the security forces, anywhere in the country and for any length of time. A block on gambling, pirated or child-abuse sites is not one.

**Punished** is a person arrested, charged, convicted or jailed, or a newspaper, broadcaster or news site suspended or closed, for what was said or published about the government, an official or public affairs.

The study redraws `gov.discourse--open-discussion-of-government-policy`, which as at 2026-08-31 puts one country at stage 1, 25 at stage 2 and four at stage 3, none at 4 or 5, and leaves the others unplaced. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| Freedom to discuss policy online and in the press | Open discussion of government policy: freedom to discuss policy online and in the press | `gov.discourse--open-discussion-of-government-policy-freedom-to-discuss-policy-online-and-in-the-press` |

Anything else the evidence names is `other`, noted and never staged: a score or rank on a freedom index; a law that punishes speech under which no one is reported charged; a power to block or intercept that has not been used; a request to a platform to take content down; a licence or fee for online publishers; a rule on children's use of social media; a consultation, which is `publicconsultation`'s; an access-to-information law, which is `accesstoinformationlaw`'s.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Has a newspaper, broadcaster, party or group inside the country criticised a government policy in public in the last three years? | A dated story of a named paper, station, opposition party, professional body or civil-society group, inside the country, criticising a named policy, bill or decision of the government |
| 2 | Has the country gone the last twelve months with no one punished for what they said? | A dated source that says so of the country: a monitor's count showing no journalist or critic held, or a report on the country that records none. **A dated arrest, charge, jailing or closure inside the twelve months is a no** |
| 3 | Has a law that punishes speech been repealed or struck down in the last three years? | Parliament repealing, or a court of the country striking down, an offence of criminal defamation, false news, sedition or insulting the head of state |
| 4 | Has the government been barred from cutting the internet in the last three years? | A law, a ruling of the country's own court that a cut was unlawful, or an undertaking the government or regulator gave in court not to cut |

## 3. The ladders

**Freedom to discuss policy online and in the press**

| Stage | Answers |
|---|---|
| 1 Absent | A dated source says the government cut the internet or blocked a service or news site in the last twelve months; or says no independent newspaper, broadcaster or news site is allowed to work |
| 2 Preparing | Yes to 1: policy is criticised in public |
| 3 Establishing | Yes to 1 and 2: and no one was punished for it in twelve months |
| 4 Operating | Yes to 1, 2 and 3: and a law that punished speech has gone |
| 5 Leading | Yes to all four: and the government is barred from cutting the internet |

- **A cut inside the twelve months places a country at stage 1 whatever else is held.** This is the one study where stage 1 outranks a yes: a cut is a dated fact, and Uganda's of January 2026 and Tanzania's of October 2025 sit beside loud public criticism. The row as it stands puts both at stage 2.
- **A cut in one province, a slowed service, and a cut for school examinations are cuts.**
- **A no to question 2 stops the count whatever comes after it.** A later yes answers an earlier question nothing held answers, and never one a dated arrest has answered no.
- **Cuts and punishments count for twelve months; every other answer for three years.** The twelve months are the row's own, kept. A country moves up when a cut passes out of them with no new one.
- **A law that punishes speech places nothing until someone is charged under it**, and is noted. The row as it stands places Angola and Zimbabwe on such a law, and Mauritius on a ministry's warning.
- **A power to block places nothing until it is used.** The row as it stands places Mozambique on a decree since voided.
- **A consultation and an access-to-information law place nothing here.** The row as it stands separates stage 1 from 2 by the law, and puts Cabo Verde, Namibia, São Tomé and Príncipe and Seychelles at stage 3 on consultations.
- **A score or rank on an index places nothing**, and is noted. A monitor's count of people held or of cuts is a fact and does.
- **A ruling by a regional court against the country is a yes to question 3 or 4 only where the source says the government acted on it.**
- **An arrest for fraud, a threat of violence or an image of abuse is not punishment for speech.** Where the source does not say what the person said, it is noted and is not a no.
- **Criticism published only from abroad is not a yes to question 1.**
- **Whether the criticism was fair, and whether a charge was deserved, is not judged.**
- **Two more changes from the row as it stands**: its stage 4 asks for drafts and regulator decisions published as a practice, which `publicconsultation` now asks; its stage 5 is the African Commission's Declaration end state. Neither is a fact one story can state.

`study.json` holds this as three aspects: `debate` (`criticised`, `silenced`) for question 1 and the second half of stage 1; `connection` (`cut`, `barred`) for the first half of stage 1 and question 4; `penalty` (`punished`, `unpunished`, `repealed`) for questions 2 and 3.

## 4. The norm

The African Commission's Declaration of Principles on Freedom of Expression and Access to Information in Africa (2019) asks states not to disrupt access to the internet or to digital services for the whole or part of a population (Principle 38), and to repeal laws that make sedition, insult and false news crimes and to replace criminal defamation with civil remedies (Principle 22). The African Charter on Democracy, Elections and Governance, Article 2, commits its parties to freedom of the press. This study asks whether the internet stays on, whether anyone is punished for speech, and whether a speech offence or the power to cut has been removed; it does not measure a country against either text.

## 5. What the run reads

- **Read**: **185 news stories about cuts, arrests for speech and press freedom that no study has read for this**, in 46 countries, every one but Algeria, Botswana, Burundi, the Central African Republic, Djibouti, Lesotho, Libya and Malawi; and the 169 stories and 17 texts the current cells cite. Ten of the 185 are one yearly count of shutdowns, listed under ten countries.
- **Not read**: long texts, reports and passing mentions. **No web search and no handover to OSINT.**

## 6. Token ceiling

**50 million.** The run checks after every fan-out and stops at it.

## 7. Tasks, in order

- [x] **D0. Prepare**: this file and `study.json`, 2026-10-13.
- [ ] **D1. Bill's word** on the four questions.
- [ ] **D2. Read**: drafters in one fan-out over the documents of §5.
- [ ] **D3. Stage** as at 2026-09-30, with `scripts/study-ladder-opendiscussion.py`; the parent reads every fact that sets stage 4 or 5 and every cut that sets stage 1; second stager on 20 cells.
- [ ] **D4. Write, render and lint**; the soft-launch map. **D5. Report to Bill.**

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
