---
type: task
reader: cc
title: maturity-study-regionalinfrastructure.md — the twenty-ninth maturity study: digital links and facilities shared with other African countries, in four questions
last_reviewed: 2026-11-09
status: run 2026-10-13; redesigned on Bill's word 2026-11-07 and adopted 2026-11-08 (§8)
---

# Maturity study: regionalinfrastructure

*(Commissioned by Bill on 2026-10-13 as `gov.regional--shared-regional-infrastructure`, under `maturity/documentation/maturity-study-method.md`.)*

## 1. What is assessed

*(Redesigned on Bill's word, 2026-11-07, on message 78: "This needs a major overhaul. It is not just about cables but data storage, IXPs, etc. And it needs to involve a degree of active collaboration. Cables transversing a country do not, on their own, constitute sharing." Adopted at the rebuild of 2026-11-08.)*

**Digital infrastructure the country builds, runs or uses together with at least one other African country, under an arrangement both are party to.** Three kinds count:

- **Links**: a cross-border fibre interconnection, a regional backbone, a sea cable held by a consortium of African states or their operators, a shared satellite.
- **Traffic exchange**: an internet exchange point run for more than one country under an agreement between national bodies or a regional programme, or an agreed interconnection between two countries' exchanges.
- **Data storage**: a data centre, cloud or backup site owned jointly, or holding another country's public data under an agreement.

**Active collaboration is the test.** A party is a government, regulator, state operator or national body (an exchange, a research and education network) of each country, or a regional body acting for them.

The study redraws `gov.regional--shared-regional-infrastructure` and touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| Digital links and facilities shared with other African countries | Shared regional infrastructure: digital links and facilities shared with other African countries | `gov.regional--shared-regional-infrastructure` |

Anything else the evidence names is `other`, noted and never staged: a cable that crosses or lands in the country with no arrangement it is party to; one company's network across borders; a commercial facility taking foreign customers with no arrangement between national bodies; a roaming cut, a frequency agreement or a joint body, which the regional policy row holds; a regional payment switch or settlement system, which the cross-border payments row holds; an identity card or a police or customs system shared across borders; a link to a country outside Africa; a national backbone, exchange point or data centre that no other country is reported using under an arrangement.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Has the country agreed in the last three years, with another African country or through a regional body, to build, join or jointly run shared infrastructure? | A dated agreement, memorandum or financing agreement naming the facility and the partner. Talks, a study or a bid to host is not a yes |
| 2 | Has building started in the last three years? | A contract awarded, works begun or cable being laid. A tender or money promised is not a yes |
| 3 | Is shared infrastructure in service under such an arrangement? | A dated source saying it was lit, commissioned or opened, or naming the other country's body as using it under the arrangement |
| 4 | Is shared infrastructure of a second kind in service? | Question 3 answered for two of the three kinds |

## 3. The ladders

**Digital links and facilities shared with other African countries**

| Stage | Answers |
|---|---|
| 1 Absent | A dated source says the country shares no digital infrastructure with another African country |
| 2 Preparing | Yes to 1 |
| 3 Establishing | Yes to 1 and 2 |
| 4 Operating | Yes to 1 to 3: one kind in service |
| 5 Leading | Yes to all four: two kinds in service |

- **A yes to a later question answers the earlier ones**: a link in service was agreed and built.
- **Questions 3 and 4 have no time limit**; a facility in service stands until a dated source says it is cut or closed. Questions 1 and 2 count for three years.
- **A company counts only as a party to an arrangement with the other country's operator or body.** One company's or one group's network across borders, with its own subsidiaries or wholesale customers, is `other`.
- **Foreign networks joining an exchange as members is commercial use, not collaboration** *(settles message 78)*: a yes needs an agreement between the exchange or its national body and a body of the other country, or a regional programme naming both. Neither South Africa (NAPAfrica) nor the Democratic Republic of the Congo (KINIX) takes a yes on peering alone.
- **The arrangement is taken from what a source says**: a source names a party in each country, or the consortium or regional programme that holds the facility. A state operator's link to a neighbour with no party there named is not yet a yes *(adopted at the rebuild, 2026-11-08)*.
- **A statement that the country shares no digital infrastructure counts for three years**, and gives way to a dated source naming some.
- **A link counts for each country a source names at its ends.** A country only named as on the route does not take the stage.
- **A landlocked country's route to a sea cable through a neighbour is a link in service** for both, where a dated source says traffic runs over it under an arrangement both are party to.
- **A submarine cable counts where a source says it joins the country to another African country** and the country's operator is in the consortium or agreement that holds it. A landing alone does not.
- **A regional programme's financing signed by the country is a yes to question 1** where the source names the cross-border link or shared facility it pays for.
- **An agreement a later dated source says is suspended or cancelled is no longer a yes.**
- **A national facility described as serving the region is not a yes to question 3** until a source names another country's body using it under an arrangement.
- **The best-placed facility sets the stage**; the others are named in the summary. How good or how dear a facility is, is not judged.
- **A resolution to pay for a study of a shared satellite is a study**, not a yes to question 1.
- **A network named as crossing the country, with no link to a neighbour named, is not a yes**.
- **A cable owner's announced plan, or a consensus reached at a workshop, is not an agreement**.
- **Withdrawn at the redesign**: a company's link counting as a government's, and a company's cable carrying a landlocked country's traffic to its parent network.

`study.json` holds this as two aspects: `built` (`building`, `agreed`, `none`) for questions 1 and 2, and `service` (`link`, `exchange`, `storage`, `none`) for 3 and 4.

## 4. The norm

The African Union's Programme for Infrastructure Development in Africa and its Digital Transformation Strategy for Africa (2020 to 2030) ask member states to join their networks across borders, to give landlocked countries a route to the sea cables and to share exchange points and data centres. This study asks whether a country has agreed shared digital infrastructure with another African country, started building it, and has one kind or two in service under an arrangement both are party to; it does not measure capacity or price.

## 5. What the run reads

- **Read**: the 183 news stories about cross-border links and shared facilities filed to a country; then the 150 stories the current cells cite, for every country.
- **Not read**: project documents, tenders, long reports and the general run of submarine cable news.

## 6. Token ceiling

**40 million**, checked after every fan-out.

## 7. Tasks, in order

- [x] **D0. Prepare**: this file and `study.json`, 2026-10-13.
- [x] **D1. Bill's word**: run on it, 2026-10-13.
- [x] **D2. Read**: 116 calls in two fan-outs, 185 facts.
- [x] **D3. Staged** as at 2026-09-30; corrections in `corrections.csv`; agreement 19 of 20 after the second reading.
- [x] **D4. Written, rendered and linted**; on the soft-launch map. **D5. Reported to Bill**, 2026-10-13.

**Decided in the run**, superseded by the restaging of §8: no country reached stage 5, seven rows were added for the other end of a link a source names, and the run came to about 41 million tokens against 40 million.

## 8. The redesign

**Redesigned on Bill's word, 2026-11-07, and adopted at the rebuild of 2026-11-08**: §1 to §3 above replace the first run's, and `redesign.md` is deleted. Every `service` row was revalued to its kind or removed with the rows that name no arrangement (`corrections.csv`: 95 removed, 44 revalued, one added). Every country was restaged and logged `ladder`: none at 5, 4: 25, 3: 1, 2: 12, 1: 1, three unplaced, 12 without evidence. No exchange or data facility is yet on record in service under an arrangement, so every stage 4 rests on links.

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
