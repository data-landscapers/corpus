---
type: task
reader: cc
title: The redesign of the shared regional infrastructure study, adopted at its next rebuild
last_reviewed: 2026-11-07
---

# Redesign: regionalinfrastructure

*(Bill, 2026-11-07, on message 78: "This needs a major overhaul. It is not just about cables but data storage, IXPs, etc. And it needs to involve a degree of active collaboration. Cables transversing a country do not, on their own, constitute sharing.")*

**The next rebuild replaces the study file's §1 to §3 with this file and deletes it.** `study.json` → `ladder_rewritten` puts it first in the queue. At the rebuild: `service` takes the values `link`, `exchange`, `storage` and `none`, and both aspects are renamed (*Shared infrastructure agreed and under construction*; *Shared infrastructure in service, by kind*); every `service` row is revalued to its kind, or removed in `corrections.csv` where no arrangement the country is party to is named; every country is restaged `--kind ladder`; the five `criteria` and `criteria_of` are rewritten; every country is searched on the new questions. `study-ladder-regionalinfrastructure.py` already counts the new ladder.

## What is assessed

**Digital infrastructure the country builds, runs or uses together with at least one other African country, under an arrangement both are party to.** Three kinds count:

- **Links**: a cross-border fibre interconnection, a regional backbone, a sea cable held by a consortium of African states or their operators, a shared satellite.
- **Traffic exchange**: an internet exchange point run for more than one country under an agreement between national bodies or a regional programme, or an agreed interconnection between two countries' exchanges.
- **Data storage**: a data centre, cloud or backup site owned jointly, or holding another country's public data under an agreement.

**Active collaboration is the test.** A party is a government, regulator, state operator or national body (an exchange, a research and education network) of each country, or a regional body acting for them. `other`, never staged: a cable that crosses or lands in the country with no arrangement it is party to; one company's network across borders; a commercial facility taking foreign customers with no arrangement between national bodies; and everything §1 already lists.

## The questions

| # | Question | A yes is |
|---|---|---|
| 1 | Has the country agreed in the last three years, with another African country or through a regional body, to build, join or jointly run shared infrastructure? | A dated agreement, memorandum or financing agreement naming the facility and the partner. Talks, a study or a bid to host is not a yes |
| 2 | Has building started in the last three years? | A contract awarded, works begun or cable being laid. A tender or money promised is not a yes |
| 3 | Is shared infrastructure in service under such an arrangement? | A dated source saying it was lit, commissioned or opened, or naming the other country's body as using it under the arrangement |
| 4 | Is shared infrastructure of a second kind in service? | Question 3 answered for two of the three kinds |

## The ladder

| Stage | Answers |
|---|---|
| 1 Absent | A dated source says the country shares no digital infrastructure with another African country |
| 2 Preparing | Yes to 1 |
| 3 Establishing | Yes to 1 and 2 |
| 4 Operating | Yes to 1 to 3: one kind in service |
| 5 Leading | Yes to all four: two kinds in service |

- **Questions 3 and 4 have no time limit**; a facility in service stands until a dated source says it is cut or closed. Questions 1 and 2 count for three years.
- **The §3 rules stand except two.** *A company's link counts as a government's* is withdrawn: a company counts only as a party to an arrangement with the other country's operator or body. *A link live and carrying traffic for customers not named* no longer bears on a question.
- **Foreign networks joining an exchange as members is commercial use, not collaboration** *(settles message 78)*: a yes needs an agreement between the exchange or its national body and a body of the other country, or a regional programme naming both. Neither South Africa (NAPAfrica) nor the Democratic Republic of the Congo (KINIX) takes a yes on peering alone.

