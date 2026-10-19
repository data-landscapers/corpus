---
type: task
reader: cc
title: maturity-study-datalocalisation.md — the seventeenth maturity study: the rule on keeping data in the country, in four questions
last_reviewed: 2026-10-12
status: run on Bill's word of 2026-10-12; staged, written and on the soft-launch map as at 2026-09-30; awaiting Bill's acceptance
---

# Maturity study: datalocalisation

*(Commissioned by Bill on 2026-10-12 as `gov.policy--data-localisation-policies`, under `maturity/documentation/maturity-study-method.md`.)*

## 1. What is assessed

**The government's rule that data, or a named kind of data, must be stored or processed inside the country**, whatever it is called and whoever issues it: a law, a decree, a regulation, a regulator's or central bank's directive, a head of government's instruction, or the part of a larger law or policy where a source states that rule.

The study redraws `gov.policy--data-localisation-policies`, which as at 2026-08-31 puts 18 countries at stage 2, eight at stage 3 and four at stage 1, none at 4 or 5, and leaves 24 unplaced. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| Data localisation rule | Data localisation policies: localisation rule | `gov.policy--data-localisation-policies` |

Anything else the evidence names is `other`, noted and never staged: a condition on sending data abroad, a data centre or sovereign cloud built or planned, a company choosing to host in the country, a statement that data ought to be kept at home, a data protection law.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Is there a rule that data must be kept in the country, or one being written? | A rule requiring data, or a named kind of data, to be stored or processed in the country: being drafted, out for consultation, or in force. A stated intention with no drafting begun is not a yes |
| 2 | Is the rule in force? | Enacted or issued by the government, the minister or the regulator responsible, and not repealed, replaced or withdrawn |
| 3 | Has a body been named to enforce it? | A regulator, agency or ministry unit that the rule or a source says checks compliance or grants exemptions. A regulator that issued the rule for the bodies it licenses counts |
| 4 | Has the rule been applied? | In the last three years: a dated source naming an organisation ordered to bring data into the country, penalised, or granted or refused an exemption under the rule, or naming or counting organisations that have moved data into the country to comply |

## 3. The ladders

**Data localisation rule**

| Stage | Answers |
|---|---|
| 1 Absent | A dated source says the country has no rule that data must be kept in the country and none is being written |
| 2 Preparing | Yes to 1: a rule being written, or one repealed with no successor |
| 3 Establishing | Yes to 1 and 2: a rule in force |
| 4 Operating | Yes to 1, 2 and 3: a body is named to enforce it |
| 5 Leading | Yes to all four: the rule has been applied |

- **Questions 1 to 3 have no time limit**: a rule in force stands, with its year, until a dated source says it has been repealed, replaced or withdrawn.
- **A statement that there is no rule counts for three years.**
- **A rule on one kind of data counts**: state data, secret or sensitive data, payment or banking data, health data, subscriber data. The summary names the data it covers and who must comply.
- **Whether the rule covers all data or named kinds is stated and not judged.** This is the change from the row as it stands, whose stage 2 holds a rule on all data below a rule on named kinds, and whose stage 5 is agreement with the African Union's framework.
- **A stage says how far a rule has been put to work, not that more localisation is better.** A country that has chosen to let data move freely is stage 1 where a source says so.
- **A condition on sending data abroad is not a rule that it must stay**: an adequacy test, an authorisation or a consent requirement is noted. A rule that a copy must be kept in the country counts.
- **A duty on public bodies to host in a named data centre inside the country counts**; a cloud policy that names no place does not. The hosting and cloud row is not changed by it.
- **A data centre alone places nothing**, nor does a minister saying data should come home.
- **A rule issued with a later compliance date is a yes to question 2**, and the summary gives the date.
- **A law that names no enforcer is not a yes to question 3.** The data protection authority counts only where a source ties it to this rule.
- **A company moving its data by choice is not the rule applied.** The source must tie the move, the order or the penalty to the rule.
- **A rule that is part of a larger law or policy** is named in the summary by that instrument's name; the data protection, cybersecurity and cloud rows are not changed by it.

`study.json` holds this as two aspects: `standing` (`in-force`, `ended`, `draft`, `none`) for questions 1 and 2, and `use` (`applied`, `enforcer`, `none`) for 3 and 4.

## 4. The norm

The African Union's Data Policy Framework, of 2022, asks states to keep only certain kinds of data in the country and to let the rest move. The digital trade protocol of the African Continental Free Trade Area, of 2024, says a state shall not require computing facilities to be in its territory, with exceptions for public policy. This study asks whether a rule exists, is in force, has an enforcer and has been applied; it does not judge whether the country should have one or how wide it is.

## 5. What the run reads

- **Read first**: **60 news stories about a rule on keeping data in the country**, across 19 countries. No study has read them. 23 of them are Nigeria's.
- **Then, for every country those leave short of an answer**: the news stories its current cell cites, 159 across 44 countries.
- **Then, only for a country still short of an answer to question 1 or 2**: the newest held news that names such a rule, one call a country, from at most 604 stories across 51 countries.
- **Not read**: the texts of the laws and long reports, 653 of them. A rule's text is opened only for a country with nothing else.
- A question nothing answers is printed as *Not held*.

## 6. Token ceiling

**50 million.** The run checks after every fan-out and again after the writing step, and stops and reports if it reaches it. The interoperability study, the same size, spent 45.3 million against 50, so the third read is one call a country and the parent writes the summaries. No earlier study holds facts on a localisation rule, so nothing is carried.

## 7. Tasks, in order

- [x] **D0. Prepare**: this file and `study.json`, 2026-10-12.
- [x] **D1. Bill's word**: run on it, 2026-10-12.
- [x] **D2. Read**: the 60 `about` stories; then the cited news of the 35 countries with none; then, for the 42 countries still without a fact, the rest of their cited news and one call of the newest held news each; then the cited texts of nine countries whose current cell names a rule, Tunisia's by the parent. 117 calls, 65 facts.
- [x] **D3. Staged**: eight at stage 4, eleven at 3, three at 2, one at 1, none at 5, one unplaced and 30 with no evidence, as at 2026-09-30; five corrections by the parent; agreement 20 of 20.
- [x] **D4. Written, rendered and linted**; on the soft-launch map. **D5. Reported to Bill**, 2026-10-12. 42.3 million tokens, step 1 included.

**Decided in the run**:

- **A strategy stating that data will be stored in the country is a rule being written** (Côte d'Ivoire), as is a policy a minister cites with no instrument or date (Ghana).
- **A profile with no date of its own does not say there is no rule** (Togo): stage 1 needs the statement dated. One dated outside three years leaves the country unplaced (Eritrea).
- **A central bank or regulator that issued the rule for the firms it licenses is its enforcer** (Nigeria, Libya, Mozambique, Tanzania, Tunisia, Zimbabwe), and so is an agency the rule names to supervise and fine (Angola) or to certify (Rwanda).
- **An authority the law leaves unnamed is not an enforcer** (Gabon), and nor is a committee that authorises something else (Kenya).
- **"Should be hosted locally", with hosting abroad allowed on conditions, is not a rule** (Liberia), nor is a circular favouring national hosting (Burkina Faso).

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
