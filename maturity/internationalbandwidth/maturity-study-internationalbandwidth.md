---
type: task
reader: cc
title: maturity-study-internationalbandwidth.md — the forty-second maturity study: fibre routes to the rest of the world, in four questions
last_reviewed: 2026-10-14
status: run 2026-10-14 on Bill's word; staged as at 2026-09-30, written, rendered and on the soft-launch map; waits for Bill to accept
---

# Maturity study: internationalbandwidth

*(Commissioned by Bill on 2026-10-14 as `infra.connect--international-internet-bandwidth`, under `maturity/documentation/maturity-study-method.md`.)*

## 1. What is assessed

**Fibre that carries the country's internet traffic abroad**, whoever owns it and whatever it is called: a submarine cable landing in the country, or for any country a fibre link to a neighbour's network that its international traffic runs over.

The study redraws `infra.connect--international-internet-bandwidth`, which as at 2026-08-31 puts seven countries at stage 4, eight at stage 3, three at stage 2 and Eritrea at stage 1, none at stage 5, leaves Angola, the Gambia, Seychelles and Uganda unplaced and 31 countries without evidence. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| Fibre routes to the rest of the world | International internet bandwidth: fibre routes to the rest of the world | `infra.connect--international-internet-bandwidth` |

Anything else the evidence names is `other`, noted and never staged: satellite and microwave links; a cable that passes the country without landing; a cable announced, financed or being laid but not in service; the national backbone inland, which `fibrebackbone` assesses; data centres and exchange points; bandwidth in gigabits, which is reported in the long summary and sets nothing.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Is the country joined to the rest of the world by fibre? | A source states that a submarine cable lands in the country and is in service, or that the country's international traffic runs over fibre to a neighbour |
| 2 | Does it have two or more such routes? | Two routes, each stated in service, on one source or two |
| 3 | Are two of them independent of each other? | Two routes that share no landing station: two cables landing at different stations, a cable and a land link through a neighbour, or for a country without a coast, links through two different neighbours |
| 3a | Does a high-capacity cable carry its traffic? | A source states that a cable of more than 100 Tbps design capacity is in service and lands in the country, or carries its traffic through a neighbour |
| 4 | Is capacity on them sold to other operators? | A source states that operators other than the owner buy capacity at the landing station or on the cable, or that it runs on open-access or regulated wholesale terms |

## 3. The ladders

**Fibre routes to the rest of the world**

| Stage | Answers |
|---|---|
| 1 Absent | A source from the past three years says the country has no international fibre route: satellite or microwave only |
| 2 Preparing | Yes to 1: one route |
| 3 Establishing | Yes to 2: two or more routes, sharing one landing station or one neighbour, or with no high-capacity cable |
| 4 Operating | Yes to 3 and 3a: two independent routes, and a high-capacity cable carries the country's traffic |
| 5 Leading | Yes to 4: two independent routes, a high-capacity cable, and capacity sold to other operators |

- **High-capacity cables** *(Bill, 2026-10-30)*: more than 100 Tbps design capacity, the cable's whole system and not the branch. 2Africa, Equiano and Medusa count; Umoja, Waterworth and Seacom 2.0 count once a source says they carry traffic. Another cable counts where a source states its design capacity above 100 Tbps. `high-capacity.csv` names, per country, the row that shows such a cable carrying its traffic; a stager adds a line when a cell reaches question 3a.
- **A sale at a point of presence is not question 4** *(Bill, 2026-10-30)*: the capacity must be sold at the landing station, on the cable, or on open-access or regulated terms.
- **No question has a window.** A route in service stays in service until a later source says it is cut or closed; a cut that is repaired is still in service.
- **A route counts for the country it lands in, or whose traffic a source says it carries.** A cable that passes offshore does not count.
- **Question 3 was reworded in the run** to say that a cable and a land link through a neighbour share no landing station; drafters had read it as asking for two landing stations only. Every country was restaged.
- **Question 4 needs question 3.** Open access on routes that are not independent is noted and leaves the country at stage 3.
- **Stages 1 to 4 are the row as it stands.** Stage 5 asked for bandwidth per internet user in Africa's top fifth; Corpus holds that figure for no country, so no country could reach it. Capacity sold to other operators replaces it: the African Union asks for infrastructure to be shared, and a story states it.

`study.json` holds this as two aspects: `routes` (`independent`, `two`, `one`, `none`) for questions 1 to 3, and `access` (`open`, `none`) for question 4.

## 4. The norm

The African Union's Digital Transformation Strategy 2020–2030 asks every member state for at least two international connections, and asks operators to share infrastructure. This study asks whether a country has a fibre route abroad, has two, has two that do not share a point of failure, and sells their capacity to other operators; it does not measure bandwidth or price.

## 5. What the run reads

- **Read**: **847 news readings**, in all 54 countries: 778 about the routes, which are 361 stories, a regional cable story being read once for each country it names, and 69 more that the current cells cite for this row. 127 of the 778 were read by `fibrebackbone` or `regionalinfrastructure` for their own questions, and are read again for these.
- **Not read**: long texts, reports and passing mentions.

## 6. Token ceiling

**70 million.** The fibre backbone study read 388 stories and came to 40 million with its summaries written by a script; this one reads 847. The run checks after every fan-out and stops at it.

## 7. Tasks, in order

- [x] **D0. Prepare**: this file, `study.json` and the reading lists, 2026-10-14.
- [x] **D1. Bill's word**: run on it, 2026-10-14.
- [x] **D2. Read**: 192 drafters over the 847 readings, then two over the regulator reports that the Burundi and Zimbabwe cells cite (method §4). 314 facts after the parent's reading.
- [x] **D3. Staged** as at 2026-09-30: 5: 7, 4: 8, 3: 23, 2: 12, 1: 1, one unplaced, two without evidence; 41 rows removed or revalued (`corrections.csv`); agreement 20 of 20.
- [x] **D4. Written, rendered and linted**; on the soft-launch map. **D5. Reported to Bill**, 2026-10-14.

**Decided in the run**:

- **Seven are at stage 5**: DR Congo, Egypt, Mozambique, Nigeria, Somalia, Tunisia and South Africa. Each has two routes that share no landing station, and a source saying other operators buy capacity or have regulated access. Tunisia's is a 2013 regulator's order for access at the Bizerte station; DR Congo's is the Goma to Mombasa land route sold wholesale.
- **Eight are at stage 4**: Benin, Burkina Faso, Botswana, the Central African Republic, Djibouti, Algeria, the Gambia and Zambia. Djibouti's open access is reversed by a September 2026 source that says one state operator still controls its landing stations.
- **Facts drawn from Data Landscapers' own AI-compiled cable factsheet were all removed**, 26 rows: the sister site is not an independent source. So were statements that 2Africa is open access as a whole, where no country was named.
- **The same route named twice is one route.** An unnamed "single cable" beside ACE is ACE: Guinea, Liberia and Sierra Leone are at stage 2. So are Ethiopia (the fibre through Djibouti) and Rwanda (the Goma to Mombasa route). A May 2026 source saying ACE is Mauritania's only route in service removed two older facts naming a second route.
- **Zambia's minister says it has fibre links to eight neighbours** (February 2026); the parent added the fact from the document the drafter read. Niger's minister says only that it is "interconnected" with five neighbours, which was removed: the statement does not say the links carry its traffic. Niger is at stage 2.
- **Eritrea is at stage 1**, on an August 2026 source that it has no submarine cable landing. Mali is unplaced: its fibre link to Senegal opened on 5 October 2026, after the as-at. Malawi and Zimbabwe are without evidence.
- **A script wrote the summaries**, `scripts/study-internationalbandwidth-write.py`, from the drafters' fact sentences, to hold the ceiling.
- **Tokens: 62.4 million at the map**, ceiling 70 million, step 1 included.

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
