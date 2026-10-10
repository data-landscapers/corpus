---
type: task
reader: cc
title: maturity-study-localgov.md — the fifth maturity study: ICT infrastructure for local government, as the office's connection
last_reviewed: 2026-10-10
status: CC's proposal, run unamended on Bill's word of 2026-10-10; step 3 under way
---

# Maturity study: localgov — office connection

*(Commissioned by Bill on 2026-10-10, under `maturity/documentation/maturity-study-method.md`. CC's proposal, modelled on the police study. Trigger: "**run maturity study localgov**".)*

## 1. The question, and the row it redraws

**Is the local government's own office connected, and does it work over the connection?** `digital.localgov--ict-infrastructure-for-local-government` has no settled subject. Its 37 staged cells hold fibre contracts, computers handed over, permit and revenue platforms, service centres and one city's portal as one thing; 25 sit at stage 2.

**One sub-indicator replaces the row**:

| Sub-indicator | Indicator text | Id |
|---|---|---|
| Office connection | ICT infrastructure for local government: office connection | `digital.localgov--ict-infrastructure-for-local-government-office-connection` |

The id enters `lookups/indicators.csv` at acceptance. **`digital.localgov--digitalisation-of-local-government-records` is not redrawn**: its evidence is logged in `applications.csv`.

## 2. Typology

| Class | What it is | Treatment |
|---|---|---|
| `connection` | A data connection **at the local government's own office, provided to the office, that its staff work over**: the government network, fibre, a leased line, a satellite link or a subscription the state or the authority pays for | Assessed |
| `equipment` | Computers, servers, an office network, power or kits handed to a local government, with no connection stated | Noted, not assessed |
| `application` | A system a local government works in: revenue, permits, accounts, civil registration, records | Logged for the records row; see the test |
| `web` | A local government's website, portal, app or social media page, and online services to residents | Noted, not assessed |
| `public-access` | Telecentres, community digital centres, public Wi-Fi and smart villages, for residents | Noted, not assessed |
| `city-systems` | Cameras, sensors, traffic and lighting control, smart-city platforms | Noted, not assessed |
| `backbone` | A national backbone, government network or data centre, with no local government office said to be on it | Noted, not assessed |
| `capacity` | ICT staff, training, and a local government's own ICT policy or strategy | Noted, not assessed |
| `upper-tier` | The networks and platforms of a state, province or region | Noted, not assessed; stated in the long summary |
| `central` | Field offices of a ministry or national agency, and the service centres they run: prefectures beside elected communes, district treasuries, one-stop shops | Out of scope |

**The test: is the office itself connected, by a connection provided to it?** Staff working on their own phones or modems are not a connection. A network that *reaches the district* connects nothing until a source puts the office on it.

**Working online is evidence of a connection.** A source saying local governments enter transactions, at their own offices, in a national system held elsewhere states a `connection`, used for `systems`. The system itself is not staged here.

**Classified by what the source says, never by name**: an *e-commune* is a connection in one country and a portal in another.

**Local governments.** The unit is the **basic tier**: the lowest body that administers a locality generally and holds its own budget, whether **elected or appointed**: communes, municipalities, district and town councils, local government areas, counties, woredas. The denominator is the country's own count of them. Their sub-offices, such as wards and *arrondissements*, are noted.

**One flag that never changes the stage.** *On the government network*: the offices are on the government's own network.

## 3. Aspects

| # | Aspect | Role | Values |
|---|---|---|---|
| 1 | Governance, planning, finance | qualifier | Owner: the state, central or local; partner or vendor. Plan: a current strategy or costed plan naming the connection of local governments, or none. Finance: domestic budget line, donor only, or not stated |
| 2 | What the office does over it | coverage | `systems`: staff work in a national or shared system held elsewhere. `internet`: email and the web, or use not stated. `none` |
| 3 | How the office is connected | coverage | `institutional`: provided to the office and paid for by the state or the authority. `personal`: staff's own phones or modems. `none` |
| 4 | Last twelve months | qualifier | Advancing, no change on record, or regressing, with the dated event |
| 5 | Local governments connected | coverage | Share of basic-tier local governments, with numerator, denominator, year and who says so; else `equipped`, a share given equipment, covered by a programme or passed by the network; else a count; else *not published* |

**Aspects 2, 3 and 5 set the stage; 1 and 4 cap or flag it and never raise it. The cap rule and aspect 4 are the health study's, unchanged** (its §3): without the state as owner and a domestic budget line or current plan, stage 4 or 5 is capped at 3 and flagged *externally run*.

**Rural.** The stage reads local governments nationally. Where a dated source says rural ones are unconnected, the cell is flagged *rural gap* and the short summary gives the figure.

**Two tiers.** The cell is staged on the basic tier and the long summary states the other. The short summary names the tier its figure counts.

## 4. The ladder

**Office connection**

| Stage | What the office does | How connected | Local governments |
|---|---|---|---|
| 1 Absent | A dated statement that local government offices have no connection of their own | `personal` or `none` | |
| 2 Preparing | A programme to connect them is being prepared or piloted; or only the capital city or the upper tier is connected | Any, or not stated | Pilot local governments, or none |
| 3 Establishing | `systems` or `internet`: past its pilot and live in some local governments outside the capital | `institutional` | A minority, a count with no total, or not published |
| 4 Operating | `systems` or `internet` | `institutional` | More than half, on a share or a count with a denominator |
| 5 Leading | `systems` | `institutional` | 90 per cent or more, on a figure published within two years that gives the rural share |

**Pilot or live, and preparation, are read as the schools study reads them** (its §4). Equipment delivered under a named connection programme is preparation.

**A noted class never places a country above stage 1**, as in the police study (its §4).

**A share of local governments *equipped*, *covered*, *supported* or *computerised* is not a share connected**: it is `equipped` and places at stage 3 only where a connection is live. *All councils*, said by the ministry beside a count of them, is 100 per cent.

**The registry study's R3 fixes hold** (its §4): `institutional` is read from the fact's words, and a law places nothing. A connection with no use named is read as `internet`.

## 5. The norm

The frame's anchor (`lookups/maturity-norms.csv`) is the African Union's decentralisation charter of 2014, Article 16(2): local governments "shall be provided with the required human, financial and technological resources", and ICT "shall be made accessible and effectively used". Its reference measure is the United Nations' Local Online Services Index.

**Neither measures what the sub-indicator measures.** Article 16 sets a duty and no measure. The Index scores the portal of each country's most populous city: the `web` class, in one local government. The ladder takes the Charter's two words: *accessible* is the connection and *effectively used* is `systems`. The 90 per cent line is the health study's. *(Article 16 read 2026-10-10, in the Laws.Africa text.)*

## 6. What the review reads and the search asks for

- **Subjects and term list**: in `study.json`.
- **Source types for the briefs**, ranked: annual reports of the ministry of local government and the national ICT agency, for government-network coverage; budget performance reports and parliamentary answers; audit reports on local governments; World Bank, African Development Bank, European Union and UNDP project documents and evaluations; local government association surveys; dated news, for aspect 4.

## 7. Tasks, in order

- [x] **L1. Bill's rulings**: the six proposals stand, 2026-10-10.
- [ ] **L2. Review all 54 countries**, method §4: 4,154 listings on the dry run.
- [ ] **L3. Test and fix the ladder.**
- [ ] **L4. Search and hand over**, method §5.
- [ ] **L5. Re-read and stage.**
- [ ] **L6. Write, render and lint.**
- [ ] **L7. Report to Bill.**

**The rulings of L1**, CC's proposals, run unamended:

1. **The office's connection only.** Equipment, websites and public access are noted.
2. **Only this row is redrawn.** The records row stands and takes the application evidence.
3. **The basic tier, elected or appointed.** States, provinces and regions are noted; ministries' field offices are out.
4. **Working online in a national system counts as a connection.**
5. **Stage 5 needs `systems` use.** Staff's own phones place nothing.
6. **A connection in the capital city only is stage 2.**

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
