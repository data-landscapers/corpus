---
type: reference
reader: cc
title: maturity-assessment-norms.md — the anchoring norm for each assessed indicator
last_reviewed: 2026-09-23
status: register ruled on by Bill 2026-09-22 (anchors and kinds agreed; frame change in §2); §6 checked against primary texts 2026-09-23, three lines left open with the reason; cut to lookups/maturity-norms.csv by scripts/maturity-norms-cut.py, which stays the only way the lookup changes
---

# The norms register

*(Written 2026-09-22 in Cowork as the first piece of `maturity-assessment.md`, and revised the same day after Bill's ruling. It is the research the rubric will be built on, one row per assessed indicator, delivered as a document rather than a lookup so that the anchors could be ruled on before CC cuts `lookups/maturity-norms.csv` from it. Every instrument was checked against a live source on 2026-09-22; where a provision, article number, adoption decision or ratification count could not be read it says **not verified** rather than guessing, and §6 lists what is owed. The notes that used to sit in an eighth table column are listed under each table, because the wide table did not read in Obsidian.)*

## 1. The rule the register applies

**Continental first** *(Bill, 2026-09-22)*. The anchor for an indicator is an African Union instrument wherever one exists; where none does, the register looks outward in a fixed order and says which step it stopped at. Every indicator gets a row and a tier, and the tier is what makes the phrase *against continental norms* checkable rather than asserted.

The tiers, in preference order:

- **AU** — an instrument adopted by an AU policy organ: Assembly, Executive Council, a Specialised Technical Committee, or the ACHPR. Treaties (Malabo, the charters, the protocols), strategies (DTS, the Continental AI Strategy, Agenda 2063's implementation plans) and frameworks (the Data Policy Framework, the Interoperability Framework for Digital ID) all count.
- **continental** — an instrument of an AU agency, alliance or ministerial conference that is not an organ decision: Africa CDC, AUDA-NEPAD and PIDA, Smart Africa, ATU, AMCOMET, APAI-CRVS and the Conference of African Ministers responsible for Civil Registration, PAPSS.
- **REC** — a Regional Economic Community instrument (ECOWAS, SADC, EAC and the rest). Used as the anchor only where nothing continental exists; otherwise recorded as a rung.
- **global** — ITU, the UN system, the World Bank, OECD, the standards bodies. Used as the anchor only where nothing African exists; recorded as the *reference* wherever it carries the number the African instrument lacks.
- **corpus** — nothing found at any tier. The rubric for that indicator is Corpus's own and says so, in the spirit of the datasets rule that a classification rubric is ours and says so.

**What a norm fixes** is recorded because most instruments describe an end state and nothing below it. *Top* means the instrument fixes the top of the ladder only and the intermediate stages are Corpus's interpolation; *rungs* means the instrument itself supplies stages, phases or a checklist; *target* means a number with a date, which is what a measure needs.

**Vintage is frozen.** Each row names the instrument as adopted; a later revision of a target (the DTS mid-term review, a SHaSA 3) is a rubric change, recorded and flagged, never fifty-four countries moving in a month.

## 2. Summary

**The frame the register now covers is 117 indicators, not 121** *(Bill, 2026-09-22)*. The five `geopol.*` indicators leave the assessment — they record a relationship, not a position — and a **digital sovereignty** indicator takes their place in the Geopolitics chapter; `finance.mou--strategic-relationships` leaves for the same reason and a **financial sustainability** indicator takes its place. The two additions are planned in `indicator-digital-sovereignty.md` and `indicator-financial-sustainability.md`, following `adding-an-indicator.md`, and their rows are in §3 below with their ids as proposed there. The six that leave stay in `lookups/indicators.csv` flagged as not assessed, so their ids and mapped rows persist (the sovereignty indicator draws on the 260 `geopol.*` rows already mapped across the 54 countries).

| | instrument | system | measure | total |
|---|---|---|---|---|
| **AU** | 42 | 43 | 20 | 105 |
| **continental** | 2 | 4 | 1 | 7 |
| **REC** | — | — | — | 0 |
| **global** | — | 3 | 1 | 4 |
| **corpus** | — | 1 | — | 1 |
| **total** | 44 | 51 | 22 | 117 |

*(Counted from §3 by script on 2026-09-22 after the frame change; the table is derived from the rows, not maintained beside them.)*

One hundred and five of the 117 anchor on an AU organ instrument and a further seven on a continental agency or alliance, so 112 of 117 are continental in Bill's sense. Four fall through to a global body (address register, tax register, tax MIS, payment uptake — nothing African names them) and one, rural police stations, to Corpus's own rubric (§5). No REC instrument is the anchor anywhere, because wherever a REC instrument exists (ECOWAS data protection, the SADC model laws, the EAC cyberlaw framework) an AU instrument sits above it; the REC instruments are recorded as rungs.

Twenty-seven rows carry a numeric target, twenty-six of them from an African instrument — though several are a continental or proxy figure rather than a country one, and the row says so. Seventy-three are *top* only, which is the finding that shapes the rubric: for most indicators the instrument fixes the end state and the intermediate stages will be Corpus's interpolation, marked as such. Nineteen supply *rungs*, alone or beside a target. The DTS 2020–2030 is the anchor or a co-anchor for 48 indicators and Agenda 2063's Second Ten-Year Implementation Plan (2024–2033) supplies most of the dated numbers the DTS lacks. Four anchors are marked *weak* in their notes (quality standards, land register, land MIS, justice MIS): an AU instrument exists but its bearing on the indicator is thin.

The kinds are the rubric families in `maturity-assessment.md` §4; Bill agreed the assignment on 2026-09-22.

## 3. The register, by chapter

Column key — **kind**: I instrument · S system · M measure. **tier**: as §1. **fixes**: top · rungs · target. Instrument short names resolve in §4, which carries the adopting body, date, status and URL once. *Reference* names the global instrument or dataset that carries the number or the stages the anchor lacks.

### Governance

| indicator_id | kind | tier | anchor | provision | fixes | reference |
|---|---|---|---|---|---|---|
| gov.policy--digital-transformation-strategy | I | AU | DTS | Enabling Environment pillar: "Develop and implement national and sectorial digital strategies"; Digital Single Market by 2030 | top | OECD Rec. on Digital Government Strategies (2014) for rungs |
| gov.policy--ict-strategy | I | AU | DTS; Smart Africa Manifesto | Same DTS action; Manifesto principles 2 and 5 | top | — |
| gov.policy--broadband-strategy | I | AU | DTS | 2030 target: universal access at ≥ 6 Mb/s, ≤ 1 US cent/MB, device ≤ USD 100 | target | Broadband Commission Target 1: a funded National Broadband Plan by 2025 — supplies the *plan exists and is funded* rungs |
| gov.policy--data-storage-cloud-strategy | I | AU | DPF; DTS | DPF names cloud as foundational infrastructure; DTS: "Establish a cloud computing infrastructure in Africa", mission-critical data-centre hosting | top | Smart Africa Data Center and Cloud Blueprint (2023, upd. 2026) |
| gov.policy--data-interoperability-framework-roadmap | I | AU | DTS; DPF; AU Interop. Framework | DTS: "Develop a framework with Implementing Acts for interoperability and levels of assurance"; DPF open data standards; Interop. Framework §3.1 open standards, no lock-in | top | OECD 2014 Rec.; ID4D Principle 4 |
| gov.policy--ai-strategy | I | AU | Continental AI Strategy | Member States "must develop national AI strategies"; Phase 1 (2025–2026) national strategies and governance structures, Phase 2 from 2028 | rungs | UNESCO AI Ethics Rec. (2021) and its Readiness Assessment Methodology |
| gov.policy--data-localisation-policies | I | AU | DPF; AfCFTA DTP | DPF: localisation "for certain categories of data" only, sovereignty ≠ localisation; DTP Art. 22: no requirement to locate computing facilities, subject to public-policy exceptions | top | — |
| gov.policy--data-governance-policy | I | AU | DPF | Six sections; "multi-prong strategy"; an implementation figure of formulation → domestication → monitoring and evaluation, with progressive realisation (the research pass reported "five implementation phases"; a read of the document on 2026-09-23 found none — §6) | rungs | — |
| gov.policy--open-data-policy | I | AU | ACHPR Declaration 2019; DPF; DTS | Principle 29: proactive publication "including digital technologies"; Principle 26 access to information; DPF open government data | top | International Open Data Charter (2015) six principles for rungs |
| gov.legislate--data-protection-legislation | I | AU | Malabo Convention | Art. 8(1) legal framework; Art. 13 principles; Arts 16–19 rights; DTS: laws "in line with the Malabo Convention" | top | UNCTAD Cyberlaw Tracker; Convention 108+ |
| gov.legislate--cybersecurity-legislation | I | AU | Malabo Convention ch. III | Art. 24 national policy and strategy; Art. 25 legal measures; Art. 27 governance mechanism; Arts 29–31 offences | top | ITU GCI 2024 five pillars and five tiers |
| gov.legislate--legislation-covering-digital-id | I | AU | DTS; AU Interop. Framework; AfCFTA DTP Art. 14 and Annex on Digital Identities | DTS: 99.9 % digital legal identity by 2030; Framework §4.1 harmonised enabling legal frameworks; DTP Art. 14 "adopt or maintain digital identity systems" | target + top | ID4D Principles (2021) governance principles for rungs |
| gov.legislate--digital-payments-legislation | I | AU | AfCFTA DTP Art. 15 and Annex on Cross-Border Digital Payments; Malabo Art. 7 | Art. 15 interoperability of payment systems; Art. 7 state-approved electronic payment methods | top | G20 HLPs for Digital Financial Inclusion (2016) Principle 3; CPMI–World Bank PAFI (2016) |
| gov.legislate--legislation-enabling-data-interoperability | I | AU | DTS; AfCFTA DTP Art. 19; DPF | DTS framework with Implementing Acts; Art. 19 mutual recognition of e-authentication and digital identities; DPF portability | top | — |
| gov.legislate--ai-legislation-regulations | I | AU | Continental AI Strategy; DTP Annex on Emerging and Advanced Technologies | Five governance activities: amend existing laws, gap analysis, enabling framework, assessment tools, research; independent institutions; regional AI Ethics Board | rungs | UNESCO AI Ethics Rec.; OECD AI Principles (2019, rev. 2024) |
| gov.legislate--e-commerce-legislation | I | AU | Malabo ch. I; AfCFTA DTP Arts 12, 16, 27 | Malabo Arts 2–5 scope of electronic commerce, contracts, advertising; DTP Art. 16 legal framework for electronic transactions; Art. 27 consumer protection | top | UNCTAD Cyberlaw Tracker (four areas); UNCITRAL Model Law (1996) |
| gov.legislate--statistics-legislation | I | AU | African Charter on Statistics; AU Model Statistics Law | Obligation to align national law with the Charter; Art. 3 principles; STYIP Goal 19 tracks statistical legislation | top | UN Fundamental Principles of Official Statistics, Principle 7 |
| gov.legislate--access-to-information-legislation | I | AU | ACHPR Declaration 2019; ACHPR Model Law on Access to Information (2013) | Principle 26 right of access; Principle 29 proactive disclosure; Principle 34 independent oversight mechanism established by law | rungs | UNESCO SDG 16.10.2 |
| gov.protect--data-protection-authority | I | AU | Malabo Arts 11–12; DPF | Art. 11 independent administrative authority; Art. 12 duties and powers; DPF: "independent, funded, and effective" DPAs | rungs | — |
| gov.protect--national-data-protection-readiness | I | AU | DPF; AUC/ISOC Guidelines (2018); Malabo | DPF implementation sequence (formulation → domestication → M&E; "five phases" unverified, §6); Guidelines' 18 recommendations; Malabo Arts 13–23 | rungs | Convention 108+ accession |
| gov.regional--regional-policy-collaboration | I | AU | DTS; PRIDA | DTS regional and continental strategies, coordinated agenda; PRIDA harmonisation track | top | — |
| gov.regional--regional-legal-harmonisation | I | AU | Malabo Art. 28; DTS; AfCFTA DTP Art. 43 | Art. 28 regional harmonisation of cybercrime law and mutual legal assistance; DTS harmonised regional strategies | top | — |
| gov.regional--shared-regional-infrastructure | S | AU | PIDA PAP 2; DTS; Smart Africa One Africa Network | PAP 2 (2021–2030) regional ICT projects; DTS regional licensing and operators' networks | top | — |
| gov.regional--cross-border-data-transfers | I | AU | Malabo Art. 14; DPF; AfCFTA DTP Art. 20 and Annex | Malabo Art. 14(6)(a) adequacy-based transfers; DPF regional flow mechanism; DTP Art. 20 allow transfer subject to the Annex | top | OECD Privacy Guidelines (2013) |
| gov.standards--national-interoperability-standards | I | AU | DTS; AU Interop. Framework | DTS technical standards for G2G/G2B/G2C verification, open standards; Framework §3.3.5.3 W3C VC, ISO/IEC 29151 | top | ID4D Principle 5 |
| gov.standards--national-quality-standards | I | AU | PAQI / CAMI-20 Declaration (2013); Abuja Treaty Art. 67 | PAQI as the continental platform for standardisation, metrology, accreditation; Abuja Art. 67 Member States "adopt a common policy on standardisation and quality assurance" | top | UNIDO Quality Policy Guiding Principles (2018); ISO 8000 / ISO/IEC 25012 for data quality |
| gov.standards--adoption-of-international-standards | I | AU | DTS; AU Interop. Framework; ARSO; AfCFTA Annex 6 (TBT) Art. 6(2) | Technology neutrality; framework "in line with international norms"; Annex 6 Art. 6(2) State Parties "develop and promote the adoption and/or adaption of international standards" and ARSO standards | top | WTO TBT Art. 2.4; ISO membership class as rungs |
| gov.discourse--non-governmental-contribution-to-national-policy | I | AU | ACDEG; Public Service Charter; DPF | ACDEG Arts 12, 27, 28, 30 civil society and participation; Charter Art. 2(4); Malabo Art. 24 policy "in collaboration with stakeholders"; ACHPR Principle 17 multi-stakeholder regulation | top | OECD Rec. on Open Government (2017); OGP membership as a rung |
| gov.discourse--open-discussion-of-government-policy | I | AU | ACHPR Declaration 2019; ACDEG; Public Service Charter | Principles 26, 29, 34, 37, 41; ACDEG Art. 2; Charter Arts 6(3), 9; DTP Art. 38 transparency | top | UNESCO SDG 16.10.2 |

Notes:

- `gov.policy--digital-transformation-strategy` — Smart Africa Manifesto principle 5 is a secondary continental anchor
- `gov.policy--ict-strategy` — DTS treats an ICT strategy as subsumed in a digital transformation strategy; the rubric may make it a lower rung of the same ladder
- `gov.policy--broadband-strategy` — Use the Commission target for the rungs and DTS for the outcome
- `gov.policy--data-storage-cloud-strategy` — No AU instrument requires a *national* cloud strategy as such
- `gov.policy--data-interoperability-framework-roadmap` — The AU framework is ID-specific; a draft AU Data Categorisation and Data Sharing Framework was in validation Dec 2025 and may become the anchor
- `gov.policy--ai-strategy` — The two dated phases are the rungs
- `gov.policy--data-localisation-policies` — The DTS (2020) is more restrictive than DPF (2022) and DTP (2024); anchor on the later instruments. DTP article numbering differs between drafts — confirm against the deposited text
- `gov.policy--data-governance-policy` — EAC data governance framework in drafting (Dec 2024), not adopted
- `gov.policy--open-data-policy` — AUC Continental Open Data Strategy in validation Dec 2025
- `gov.legislate--data-protection-legislation` — Rungs available from ECOWAS Supp. Act A/SA.1/01/10 (binding), SADC Model Law (2013), EAC cyberlaws (2010); ratification of Malabo is itself a rung
- `gov.legislate--cybersecurity-legislation` — Article numbers from the dig.watch reproduction; AU PDF not machine-readable. Continental Cybersecurity Strategy directed Feb 2024, not yet adopted
- `gov.legislate--legislation-enabling-data-interoperability` — No AU instrument mandates a domestic data-sharing act; the draft AU Data Sharing Framework may become one
- `gov.legislate--ai-legislation-regulations` — No dated legislative target
- `gov.legislate--e-commerce-legislation` — SADC and EAC model frameworks as rungs
- `gov.legislate--statistics-legislation` — The Model Law gives a clause-level checklist
- `gov.legislate--access-to-information-legislation` — The Model Law's clauses are the rungs: s.6 records, s.7 proactive disclosure, ss.10–11 information officers, s.12 right of access, s.25 public interest override, Part IV ss.45–64 oversight mechanism (s.53 independence), s.68 reporting
- `gov.protect--data-protection-authority` — The DPF wording is a de-facto checklist: established · independent · funded · enforcing · full coverage. ECOWAS Art. 14 as REC rung; NADPA membership as a rung
- `gov.protect--national-data-protection-readiness` — Composite: ratification · law in force · DPA operating · Guidelines practices
- `gov.regional--regional-policy-collaboration` — Membership of ATU, Smart Africa and the REC regulator associations are measurable rungs
- `gov.regional--regional-legal-harmonisation` — Ratification of Malabo and of the DTP are themselves rungs
- `gov.regional--shared-regional-infrastructure` — PAP 2 ICT project list not verified
- `gov.regional--cross-border-data-transfers` — Malabo Art. 14(6) sits under the sensitive-data heading; (b) lets the DPA authorise a transfer the adequacy rule would bar; draft AU Cross-Border Data Flow Framework validated Dec 2025
- `gov.standards--national-interoperability-standards` — No AU instrument requires a national e-GIF
- `gov.standards--national-quality-standards` — CAMI-20 only asks Member States to join ARSO; the binding text is Abuja Treaty Art. 67. The Africa Quality Policy (STC-TIM, 3 Sep 2021) is guidance
- `gov.standards--adoption-of-international-standards` — ARSO's Constitution binds ARSO ("encourage and facilitate adoption of international standards by member bodies"), not States; the State obligation is AfCFTA Annex 6 Art. 6(2)

### Finance

| indicator_id | kind | tier | anchor | provision | fixes | reference |
|---|---|---|---|---|---|---|
| finance.budget--sustainable-domestic-financing-of-digital-transformation | I | AU | Agenda 2063 Goal 20; DTS | Goal 20: capital markets ≥ 10 % of development financing, aid ≤ 25 % of 2013 level; DTS digital sovereignty fund | target (not digital-specific) | Broadband Commission Target 1 (*funded* plan); Addis Ababa Action Agenda area I |
| finance.sustain--financial-sustainability-of-digital-systems *(proposed; `indicator-financial-sustainability.md`)* | M | AU | Agenda 2063 Goal 20; Addis Ababa Action Agenda area I; DTS | Goal 20: aid ≤ 25 % of 2013 level in the national budget, capital markets ≥ 10 %; AAAA domestic public resources; DTS sovereignty fund | target (proxy) + Africa quintiles | Broadband Commission Target 1 (*funded* plan); GPEDC on-budget and country-systems indicators. Dataset: Corpus's own `budgets/{ISO3}/{FY}.csv` (`finance_origin`, stages, execution) |
| finance.new--mobilisation-of-non-state-finance | M | AU | DTS; Smart Africa; Agenda 2063 Goal 20 | Sovereignty fund; Smart Africa USD 300 bn ambition; Goal 20 capital-markets share | target (continental) | Addis Ababa area II |
| finance.new--development-partner-project-financing | M | AU | Agenda 2063 Goal 20 | Aid ≤ 25 % of 2013 level in the national budget — an inverse indicator | target | Busan / GPEDC monitoring (use of country systems, on-budget aid) |

Notes:

- `finance.budget--sustainable-domestic-financing-of-digital-transformation` — No AU instrument sets a share of budget for digital transformation; the budget extract can supply a figure later
- `finance.sustain--financial-sustainability-of-digital-systems` — replaces `finance.mou--strategic-relationships`, which leaves the assessment (Bill, 2026-09-22: no norm on MoUs as such at any tier, and a relationship is not a position). The value is the domestic-state share of digital expenditure with recurrent costs separated, from the budget extract; a country with only migrated placeholder rows in `budgets/` is unassessed until its country-year is read. Proposed under `finance.budget` because the subject label already covers expenditure and the evidence is the budget file; a new `finance.sustain` subject would need an OSINT taxonomy change and is the alternative
- `finance.new--mobilisation-of-non-state-finance` — The continental targets do not resolve to a country figure; bands need a denominator

### Infrastructure

| indicator_id | kind | tier | anchor | provision | fixes | reference |
|---|---|---|---|---|---|---|
| infra.connect--mobile-penetration | M | AU | DTS | Universal access by 2030 at ≥ 6 Mb/s, device ≤ USD 100 | top | ITU UMC 2030: 100 % mobile ownership (15+), 100 % latest-technology coverage. Dataset: ITU DataHub, GSMA |
| infra.connect--internet-usage | M | AU | Agenda 2063 STYIP; DTS | STYIP Moonshot 2: ≥ 6 Mb/s to 80 % of the population by 2033; DTS 100 % by 2030 | target (80 % / 2033) | ITU UMC 2030: 100 % use (15+). Dataset: ITU DataHub, WDI IT.NET.USER.ZS |
| infra.connect--mobile-affordability | M | AU | DTS | ≤ 1 US cent per MB by 2030; device ≤ USD 100 | target | Broadband Commission Target 2 / UMC 2030: entry-level broadband < 2 % of GNI per capita. Dataset: ITU price baskets |
| infra.connect--national-fibre-backbone | S | AU | DTS; PIDA PAP 2; DPF §5.3.1 | National master plans; regional backbone projects; DPF backbone investment, rights of way, sharing | top | Datasets: ITU broadband maps, Africa Bandwidth Maps |
| infra.connect--international-internet-bandwidth | M | AU | DTS | "a minimum of two international connections" per Member State | target (≥ 2 landings) | ITU international bandwidth per user (DataHub, TeleGeography) |
| infra.connect--internet-exchange-points | S | AU | DTS; AXIS; DPF §5.3.1 | Establish IXPs, remove barriers; AXIS national and regional IXPs | top | Datasets: PCH, Af-IX, ISOC Pulse |
| infra.connect--satellite-broadband-licensing-and-availability | I | continental | ATU-R Rec. 005-0 (2021); African Space Strategy (2016) | Blanket licensing of user terminals, mutual recognition, streamlined NGSO authorisation | rungs (individual → blanket → mutual recognition) | ATU-R Report 004-0 (Aug 2022, Rev1 2023): of 30 administrations surveyed in 2020, about 57 % blanket-license two-way VSATs, 12 accept foreign type approval, 25 have no mutual recognition agreement, 2 report a regional framework |
| infra.store--local-data-centre-capacity-all-providers | M | AU | DTS; Smart Africa DC and Cloud Blueprint | DTS ≥ 30 % of content hosted in Africa by 2030; Blueprint adopts Uptime Tier I–IV | target + rungs | Datasets: ADCA, Xalam, Data Center Map (none official) |
| infra.store--local-data-centre-capacity-national-providers | M | AU | DPF §5.3.1; Smart Africa Blueprint | Sovereign hosting of sensitive data; funding models | top | As above; ownership coded by hand |
| infra.store--off-site-backup-capacity | S | continental | Smart Africa Blueprint | 24/7 availability, dual power, DR via cloud | top | ISO 22301; GTMI Core Government Systems Index |
| infra.energy--sufficient-energy-and-water-for-data-centres | M | continental | Smart Africa Blueprint | PUE as the efficiency metric; dual lines and backup | top | ISO/IEC 30134-2 (PUE), 30134-9 (WUE) |
| infra.energy--grid-reliability | M | AU | AfSEM plans and Continental Power System Master Plan (2023) | "secure, reliable, affordable" electricity; market by 2040 | top | SDG 7.1; datasets: World Bank Enterprise Surveys, RISE |
| infra.energy--rural-electrification | M | AU | Agenda 2063 STYIP; Mission 300 | STYIP: 80 % of households by 2033; Mission 300: 300 m people by 2030 | target | SDG 7.1.1; dataset: Tracking SDG7, WDI rural access |
| infra.capacity--robustness-of-government-hardware-and-software | S | AU | Public Service Charter Art. 8; DTS | Modern technologies to support service delivery; mission-critical hosting | top | GTMI 2025 CGSI and groups A–D |
| infra.capacity--local-capacity-to-maintain-manage-and-develop-government-systems | I | AU | Public Service Charter Art. 21; DPF | Systematic capacity development; skills in state institutions | top | GTMI Enablers Index |
| infra.cybersec--national-cybersecurity-readiness | I | AU | Malabo ch. III; DTS | National policy, strategy, laws, institutions; DTS complete set of legislation | top | ITU GCI 2024 tiers; Oxford CMM five stages |

Notes:

- `infra.connect--mobile-penetration` — DTS carries no penetration %; the number is the ITU's
- `infra.connect--mobile-affordability` — The 2 %-of-GNI rule is the usable band; the DTS cent-per-MB figure is the continental one
- `infra.connect--national-fibre-backbone` — No km or % target at any tier
- `infra.connect--international-internet-bandwidth` — Redundancy is the continental norm; capacity has no target
- `infra.connect--internet-exchange-points` — No count or local-traffic target verified
- `infra.store--local-data-centre-capacity-national-providers` — No numeric target
- `infra.store--off-site-backup-capacity` — No AU treaty or strategy provision found
- `infra.energy--sufficient-energy-and-water-for-data-centres` — No threshold at any tier; Corpus bands
- `infra.energy--grid-reliability` — No SAIDI/SAIFI target
- `infra.cybersec--national-cybersecurity-readiness` — Composite; GCI tiers are the natural rungs

### DPI

| indicator_id | kind | tier | anchor | provision | fixes | reference |
|---|---|---|---|---|---|---|
| dpi.exchange--national-data-exchange-system | S | AU | DTS; DPF §5.3; AU Interop. Framework §3.2.1 | Reuse of core registers in a secure exchange environment; integrated national data systems | top | GTMI I-3 interoperability framework, I-4 service bus; UN DPI Safeguards |
| dpi.exchange--use-of-digital-id-in-other-systems | S | AU | AU Interop. Framework; AfCFTA DTP Arts 14, 19 | Use cases in finance, health, social protection; mutual recognition | top | ID4D Principle 4; GTMI 2025 digital-ID-use sub-indicator |
| dpi.exchange--interoperability-of-health-systems | S | continental | Africa CDC HIE Guidelines and Standards (2023); Smart Africa Digital Health Blueprint (2025) | Policy → standards → use cases; Africa Health Data Space | rungs | WHO Global Strategy on Digital Health |
| dpi.exchange--interoperability-of-education-systems | S | AU | AU Digital Education Strategy (2022) | SO4: EMIS 1.0 → EMIS 2.0 individual-level, ID-linked | rungs | UIS/GPE EMIS guide (2020) |
| dpi.exchange--interoperability-of-social-protection-systems | S | AU | Protocol on Social Protection and Social Security (2022) | Art. 23 social registries and MIS; Art. 4 portability | top | World Bank social registries typology (2017) for rungs |
| dpi.id--robustness-of-system | S | AU | AU Interop. Framework | Technical integrity; §3.3.4.1 Levels of Assurance (definitions deferred to Phase 2) | top | ID4D Principle 3; FATF Digital ID guidance (2020) assurance levels |
| dpi.id--registration-of-entire-population | M | AU | DTS | 99.9 % digital legal identity by 2030 | target | SDG 16.9; ID4D Global Dataset |
| dpi.id--national-maintenance-of-id-and-credentials-systems | I | AU | AU Interop. Framework Principle 7; DPF | Open standards, no vendor or technology lock-in; state sovereignty | top | ID4D Principles 5 and 7 |
| dpi.id--authentication | S | AU | AU Interop. Framework §3.2, §3.4; AfCFTA DTP Arts 8, 9, 19 | Three layers, three phases; e-authentication laws; mutual recognition | rungs | FATF 2020; NIST 800-63 |
| dpi.id--digital-id-from-birth | S | AU | DTS; SDG 17.19.2(b); AU No Name Campaign declaration (2020) | Legal identity "as part of a civil registration process"; 100 % birth and 80 % death registration (SDG 17.19.2(b), restated in CRMC/6 working papers); universal birth registration by 2030 (No Name Campaign) | target | UN Handbook on CRVS and Identity Management (2022) para 29 |
| dpi.id--interoperability-of-birth-registration-and-digital-id | S | AU | AU Interop. Framework §2.2; CAMCR 2019 (Lusaka Declaration paras 3, 7) | Builds on APAI-CRVS; digitisation for interoperability between identity management and CRVS systems (para 3); harmonised law "including interoperability of systems" (para 7) | top | UN Handbook 2022 para 23 |
| dpi.id--use-by-other-systems | S | AU | AU Interop. Framework; DPF | Use cases; ID enabling secure online transactions | top | ID4D Principle 4 |
| dpi.pay--governance-role-of-central-bank | I | continental | AfCFTA DTP Annex on Digital Payments; PAPSS | Interoperability, consumer protection, AML/CFT; central banks as anchor partners | top | CPSS-IOSCO PFMI Responsibilities A–E; PAFI GP1–2 |
| dpi.pay--g2p-functionality | S | AU | DTS | "Digitize government-to-person payments" | top | PAFI GP7; Findex government-payment data |
| dpi.pay--revenue-collection | S | AU | AfCFTA DTP Arts 10, 13; Malabo Art. 7 | E-invoicing legal equivalence; paperless trading; electronic payment methods | top | TADAT P5-15 use of electronic payment methods (A–D; the 2019 Field Guide numbers indicators continuously); GTMI I-20, I-22 |
| dpi.pay--b2b-and-b2g-functionality | S | AU | AfCFTA DTP Arts 13, 15, 16 | E-invoicing; payment-system interoperability; e-transactions framework | top | GTMI I-12 e-procurement |
| dpi.pay--p2p-p2g-and-p2b-functionality | S | AU | DTS | Interoperability of e-money and DFS; low-cost channels and agents | top | PAFI GP4–5 |
| dpi.pay--population-uptake | M | global | World Bank Global Findex | Account ownership and digital-payment use (2024: SSA 58 %, global 79 %) | target (reference values) | DTS enabling-environment objective only |
| dpi.pay--cross-border-functionality | S | AU | DTS; AfCFTA DTP Art. 15; PAPSS | Cross-border mobile money framework; single African payments area | top | G20/FSB cross-border targets (cost ≤ 1 %, ≤ 3 % remittances by 2030) |
| dpi.pay--consumer-protection | I | AU | DTS; AfCFTA DTP Art. 27; Annex on Digital Payments | Four dimensions: disclosure, responsible lending, data privacy, dispute resolution | rungs | G20/OECD HLPs on Financial Consumer Protection (2022) |
| dpi.registry--population-register | S | AU | DTS | "Establish electronic government registers … starting with an electronic population registry" | top | UN P&R Vital Statistics Rev. 3 paras 97–110 |
| dpi.registry--civil-register | S | AU | DTS; APAI-CRVS | Legal identity via civil registration; CRVS Decade 2017–2026; 100 % birth and 80 % death registration (SDG 17.19.2(b), restated in CRMC/6 working papers; not a CAMCR target — §6) | target | UN P&R Rev. 3 para 68 |
| dpi.registry--address-register | S | global | UPU "Addressing the world" (2012) | National addressing policies; S42 standard | top | — |
| dpi.registry--business-register | S | AU | DTS; AfCFTA DTP Art. 14 | "eBusiness register"; digital identity for juridical persons | top | UNCITRAL Legislative Guide on Business Registries (2018) for rungs |
| dpi.registry--social-protection-register | S | AU | Protocol on Social Protection (2022) Art. 23 | Social registries and MIS | top | World Bank 2017 typology |
| dpi.registry--electoral-register | S | AU | ACDEG Art. 17; AU EOM Guidelines (2002) | Independent electoral bodies; registration without discrimination; public access to registers | rungs | — |
| dpi.registry--tax-register | S | global | TADAT Field Guide (2019) POA1 P1-1 | A–D: unique high-integrity TIN, centralised database, whole-of-taxpayer view | rungs | GTMI I-7 |
| dpi.registry--land-register | S | AU | AU Declaration on Land (2009); Framework and Guidelines on Land Policy | F&G §3.6.2 registration and tracking of land rights through "computerized Land Information Systems"; the 2009 Declaration has no registration paragraph; DTS names a "Land Use register" | top | UN-GGIM FELA (2020); ISO 19152 LADM |
| dpi.mis--health | S | continental | Africa CDC Digital Transformation Strategy (2023); HIE Guidelines | Strengthen public health systems; HealthConnekt Africa; integrated surveillance | top | WHO GSDH SO2 |
| dpi.mis--education | S | AU | AU Digital Education Strategy (2022) | EMIS 1.0 → 2.0 | rungs | UIS/GPE 2020 |
| dpi.mis--social-protection | S | AU | Protocol on Social Protection (2022) Arts 23, 25 | MIS; data management | top | GTMI I-11 |
| dpi.mis--justice | S | AU | ACHPR Fair Trial Principles (2003) | Systems for recording proceedings, storing information, public access | top | — |
| dpi.mis--tax | S | global | TADAT (2019) P4-14, P5-15 | Use of electronic filing facilities (P4-14) and of electronic payment methods (P5-15), A–D, the lower deciding; registration integrity (P1-1) is `dpi.registry--tax-register`'s | rungs | GTMI I-7, I-21 |
| dpi.mis--customs | S | AU | AfCFTA Protocol on Trade in Goods Annexes 3 and 4 | Customs automation; single window; risk management; e-payment | top | WCO Revised Kyoto Convention ch. 7; GTMI I-8, I-23 |
| dpi.mis--land | S | AU | AU Declaration on Land (2009); Framework and Guidelines on Land Policy | As land register: F&G §3.6.2 computerised Land Information Systems for land rights delivery | top | UN-GGIM FELA |
| dpi.govtech--e-government-services | S | AU | DTS; Public Service Charter Art. 8 | "single digital gateway"; G2B, G2G, G2C services; modern technologies in service delivery | top | UN EGDI bands; GTMI groups A–D, I-19 |

Notes:

- `dpi.exchange--interoperability-of-education-systems` — DES adopting organ not verified
- `dpi.exchange--interoperability-of-social-protection-systems` — Protocol not in force
- `dpi.id--digital-id-from-birth` — There is no CAMCR 2022 declaration: only CAMCR-6's expert segment met (Oct 2022) and the ministerial segment was postponed; the 100 % / 80 % figures are SDG 17.19.2(b)
- `dpi.id--interoperability-of-birth-registration-and-digital-id` — Lusaka Declaration paras 3 and 7 (verified)
- `dpi.pay--governance-role-of-central-bank` — No AU instrument names the central bank's role; Annex text not public
- `dpi.pay--population-uptake` — No numeric AU target for uptake; anchor is global with the DTS as context
- `dpi.registry--address-register` — Nothing at AU, continental or REC tier
- `dpi.registry--social-protection-register` — Not in force
- `dpi.registry--tax-register` — ATAF publishes no standard; nothing at AU tier
- `dpi.registry--land-register` — F&G §3.6.2 and its definition of a land information system (verified)
- `dpi.mis--justice` — Weak anchor; no e-justice instrument at any tier; section letter not verified
- `dpi.mis--tax` — Nothing at AU tier
- `dpi.mis--customs` — Article numbers not verified
- `dpi.mis--land` — Weak anchor

### Digitalisation

| indicator_id | kind | tier | anchor | provision | fixes | reference |
|---|---|---|---|---|---|---|
| digital.localgov--ict-infrastructure-for-local-government | S | AU | Decentralisation Charter (2014) Art. 16 | ICT "made accessible and effectively used" for local governance; technological resources for local governments | top | UN LOSI (Local Online Services Index) |
| digital.localgov--digitalisation-of-local-government-records | S | AU | DTS; Decentralisation Charter Art. 16 | Digitise government registers; reuse core registers | top | UN EGDI; ISO 15489-1 |
| digital.rural--digitalisation-of-rural-health-clinics | S | continental | Africa CDC DTS (2023); PHC Digitalisation Framework (2025–26) | HealthConnekt: 100,000 facilities connected and 2 m CHWs equipped by 2030; 90 % digitally enabled PHC by 2035 | target | WHO GSDH; GDC para 11 |
| digital.rural--digitalisation-of-rural-primary-schools | S | AU | AU Digital Education Strategy (2022) | Devices for 20 % of students and 50 % of teachers by 2027, a third and all by 2030; 50 % of institutions connected; rural and remote schools emphasised; five maturity categories | target + rungs | ITU UMC 2030: 100 % of schools connected, 20 Mb/s |
| digital.rural--digitalisation-of-rural-registry-offices | S | AU | DTS; APAI-CRVS / CAMCR; Kampala Convention Art. 13 | 99.9 % legal identity by 2030; register all vital events; IDP documentation without unreasonable conditions | target | SDG 16.9; UN LIA |
| digital.rural--digitalisation-of-rural-police-stations | S | corpus | (AFRIPOL Statute 2017 — national level only) | AFSECOM connects national police agencies; nothing sub-national | — | INTERPOL I-24/7 (tool, not norm) |

Notes:

- `digital.localgov--ict-infrastructure-for-local-government` — DTS has no local-government provision
- `digital.rural--digitalisation-of-rural-health-clinics` — PHC framework is a Member States' statement, not an organ decision
- `digital.rural--digitalisation-of-rural-registry-offices` — No norm on rural office digitisation per se
- `digital.rural--digitalisation-of-rural-police-stations` — Searched AFRIPOL, AI Strategy, DTS, ACDEG; nothing at any tier addresses local stations

### Technology

| indicator_id | kind | tier | anchor | provision | fixes | reference |
|---|---|---|---|---|---|---|
| tech.ai--use-of-ai-in-government-administration | S | AU | Continental AI Strategy | "Promoting the adoption of AI in the public sector": use cases, capacity, procurement | top | UNESCO AI Rec.; Oxford Insights readiness index |
| tech.ai--use-of-ai-in-sectoral-management-information-systems | S | AU | Continental AI Strategy; DPF §5.3 | "Accelerate the adoption of AI in the core sectors" (agriculture, education, health, climate) | top | WHO AI-for-health guidance (2021) |
| tech.ai--development-of-national-regional-ai-systems | S | AU | Continental AI Strategy; Smart Africa AI Council (2025) | Compute, datasets, talent; "Local First"; self-managed data and AI | top | GDC para 17; UNESCO RAM |
| tech.ai--control-of-ai-abuse | I | AU | Continental AI Strategy focus area 2; DTP Annex on Emerging Technologies | Risk-based regulation; independent oversight institutions; regional AI Ethics Board; safety standards | top | UNESCO AI Rec. (2021) |
| tech.industry--national-capacity-in-dt-related-production | M | AU | DTS Digital Industry pillar; STISA-2034 | Assembly and manufacturing plants; device ≤ USD 100 made in Africa; ≥ 30 % of content developed and hosted in Africa; R&D 1 % of GDP (continental target cited in the STISA-2034 Implementation Plan) | target | UNIDO CIP index; UNCTAD Digital Economy Report |
| tech.innovate--technology-hubs | S | AU | DTS | A technology park and incubation hub in each region; local innovation centres | top | WIPO GII; Briter Bridges hub counts |
| tech.innovate--tech-startup-ecosystem | I | AU | DTS; AU Startup Model Law Framework (2024) | National start-up strategies and laws; innovation fund; angel networks; seven policy areas | rungs | WIPO GII |

Notes:

- `tech.ai--development-of-national-regional-ai-systems` — No compute target
- `tech.industry--national-capacity-in-dt-related-production` — STISA-2034 itself sets no R&D share (§6.1.1 only "increase"); its GDP-share targets are digital services 6 % and high-tech 20 % of manufactured exports (§6.1.2). The 1 % is the Implementation Plan's
- `tech.innovate--technology-hubs` — The DTS target is regional, not national
- `tech.innovate--tech-startup-ecosystem` — Framework is AUC guidance, not an organ decision

### Capacity

| indicator_id | kind | tier | anchor | provision | fixes | reference |
|---|---|---|---|---|---|---|
| capacity.literacy--digital-literacy-civil-service | M | AU | Public Service Charter Art. 21; DPF | Systematic capacity development; data skills in state institutions | top | GTMI Enablers Index |
| capacity.literacy--digital-literacy-general-population | M | AU | DTS; Agenda 2063 STYIP | 300 m Africans a year in e-skills by 2025; 80 % of primary completers digitally proficient by 2033 | target | ITU UMC 2030: > 70 % basic, > 50 % intermediate skills (15+). Dataset: ITU DataHub SDG 4.4.1 |
| capacity.training--dt-related-training-in-secondary-education | M | AU | AU Digital Education Strategy; CESA 26-35 | Digital literacy and coding framework for all students; 50 % of institutions connected; device targets 2027/2030 | target | ITU UMC 2030 schools; UIS 4.a.1 |
| capacity.training--dt-related-university-facilities-and-qualifications | M | AU | AU Digital Education Strategy; Agenda 2063 STYIP | NRENs in all countries by 2027; ≥ 40 % of graduates in STEM by 2033; tertiary NER 50 % | target | UIS tertiary ICT graduates; AfricaConnect NREN status |
| capacity.training--graduates-entering-dt-ecosystem | M | AU | Agenda 2063 STYIP; Continental TVET Strategy | ≥ 40 % STEM graduates; TVET enrolment + 60 %; youth unemployment 14 % by 2033 | target | UIS; ILOSTAT ICT employment |
| capacity.research--think-tanks-and-academic-departments-contributing-to-dt-policy | I | AU | STISA-2034; Agenda 2063 STYIP | R&D ≥ 1 % of GDP (STISA-2034 Implementation Plan; not in the strategy); 10 % of global research output by 2033 | target (proxy) | UIS R&D; On Think Tanks directory |

Notes:

- `capacity.literacy--digital-literacy-civil-service` — No civil-service literacy target at any tier
- `capacity.training--graduates-entering-dt-ecosystem` — No target for the "entering" step
- `capacity.research--think-tanks-and-academic-departments-contributing-to-dt-policy` — Neither instrument counts think tanks

### Inclusion

| indicator_id | kind | tier | anchor | provision | fixes | reference |
|---|---|---|---|---|---|---|
| include.access--citizen-feedback-portals | S | AU | Decentralisation Charter Art. 13; ACHPR Principle 29; ACDEG | ICT used so that residents provide feedback to elected representatives; proactive publication | top | UN E-Participation Index: e-information → e-consultation → e-decision-making |
| include.access--citizen-participation-in-policy | I | AU | ACDEG Arts 3(7), 30, 31; Decentralisation Charter Art. 12; Maputo Art. 9 | Citizen participation in the development process; special-needs groups; local participation | top | UN EPI |
| include.access--gender-equity | M | AU | Maputo Protocol Arts 12, 18, 19; DTS; African Digital Compact | Women's education in science and technology; access to and control of information technologies; DTS STEAM skills for women and girls | top | ITU UMC 2030 gender parity; GSMA Mobile Gender Gap (SSA gap 26 %, 2026) |
| include.access--inclusion-of-persons-with-disabilities | I | AU | AU Disability Protocol (2018, in force 2024) Arts 23, 24; DTS | Public information in accessible formats and technologies; affordable devices | top | UN CRPD Arts 9, 21; WCAG 2.2 |
| include.access--inclusion-of-refugees-and-idps | I | AU | Kampala Convention Art. 13; OAU Refugee Convention; ACHPR Principle 7 | IDP registries and documents; marginalised groups incl. refugees and IDPs | top | GDC para 13(c); UNHCR Digital Inclusion |
| include.divides--bridging-of-digital-divides | M | AU | DTS; ACHPR Principle 37; African Digital Compact | Universal access ≥ 6 Mb/s at ≤ 1 cent/MB by 2030; "universal, equitable, affordable and meaningful access" | target | ITU UMC 2030 (100 % use, households, < 2 % GNI) |

Notes:

- `include.access--citizen-feedback-portals` — The EPI's three levels are the rungs
- `include.access--gender-equity` — The number is the ITU's
- `include.access--inclusion-of-refugees-and-idps` — DTS and the Compact do not mention refugees

### Data

| indicator_id | kind | tier | anchor | provision | fixes | reference |
|---|---|---|---|---|---|---|
| data.statistics--national-strategy-for-development-of-statistics | I | AU | SHaSA 2 SO 3.1; African Charter on Statistics | NSDS development and implementation aligned to SHaSA | top | PARIS21 NSDS Guidelines; World Bank SPI infrastructure pillar |
| data.statistics--censuses-and-surveys | I | AU | SHaSA 2 SO 1.1; Charter Art. 3 | Coordination around census rounds; no frequency mandate | top | ECOSOC E/RES/2025/13: a census in 2025–2034 (2030 round) |
| data.statistics--statistics-from-administrative-data | S | AU | SHaSA 2 SO 1.1; Charter Art. 3; DTS | Exploitation of administrative sources incl. civil registration | top | UN Fundamental Principles, Principle 5; SPI sources pillar |
| data.open--use-of-open-data | S | AU | DPF; Africa Data Consensus (2015); Charter Art. 3 | Open data standards; openness across the data value chain; statistics not made inaccessible | top | Open Data Charter principles; ODIN; Global Data Barometer |
| data.satellite--agricultural-use-of-satellite-data | S | AU | African Space Strategy (2016); AU Digital Agriculture Strategy (2024) | Space-derived products used for decision-making; remote sensing for monitoring and forecasting | top | Digital Earth Africa; GEOGLAM |
| data.satellite--meteorological-use-of-satellite-data | S | AU | Integrated African Strategy on Meteorology 2021–2030 (AMCOMET) | Sustained access to MTG and polar-orbiting satellites; WIGOS and GBON; 100 % NMHS ISO 9001; ≥ 5 % of NMHS budget to research | target | WMO Early Warnings for All (2027) |

Notes:

- `data.statistics--censuses-and-surveys` — The round rule is global
- `data.satellite--agricultural-use-of-satellite-data` — DAS endorsed EX.CL/Dec.1234(XLIV) para 32(iii), Feb 2024
- `data.satellite--meteorological-use-of-satellite-data` — Original strategy endorsed EX.CL/Dec.744(XXII) 2013; revision mandated 2019

### Geopolitics

The five `geopol.*` indicators (`geopol.usa`, `geopol.china`, `geopol.eu`, `geopol.gulf`, `geopol.india` — MoUs, engagements and commitments with each external power) **are not assessed** *(Bill, 2026-09-22)*: they record a relationship, not a position, and no instrument at any tier measures the maturity of a relationship. The research pass found only principles a partnership can be read against — the DPF's "politically neutral partnerships … national ownership", cloud portability and no lock-in; the AI Strategy's "Local First"; the AfCFTA DTP's computing-facilities and data-transfer articles — and those principles are exactly the norm for the indicator that replaces them. Partner-side frameworks (the US Digital Transformation with Africa initiative, the FOCAC Beijing Action Plan 2025–27, Global Gateway, the Saudi–Africa Summit, IAFS) are context for the status report, never a norm. One circularity to note: the DES 2022 was EU-funded, so it should not be leaned on near any EU-related reading.

| indicator_id | kind | tier | anchor | provision | fixes | reference |
|---|---|---|---|---|---|---|
| geopol.sovereignty--digital-sovereignty *(proposed; `indicator-digital-sovereignty.md`)* | I | AU | DPF (2022); Continental AI Strategy (2024); AU Interop. Framework Principle 7; DTS; Malabo Art. 14; AfCFTA DTP Arts 20, 22 | DPF: sovereignty distinct from localisation, localisation "for certain categories of data" only, "politically neutral partnerships … national ownership", cloud interoperability and portability "so that data subjects are not locked into a single provider"; AI Strategy "Local First", "self-manage their data and AI"; Interop. Framework "prevent vendor and technology lock-in"; DTS ≥ 30 % of content hosted in Africa by 2030; Malabo adequacy; DTP no forced location of computing facilities subject to public-policy exceptions | rungs (DPF's categories → portability → continental mechanism) + target (30 % hosted) | UN DPI Safeguards Framework (2024); GDC para 17 open standards and digital public goods |

Notes:

- `geopol.sovereignty--digital-sovereignty` — the subject slug `geopol.sovereignty` does not exist in `lookups/taxonomy.csv`, which is OSINT's vocabulary; it travels to OSINT as a patch before the frame row can be minted (`adding-an-indicator.md` §2). The 260 rows already mapped to the five retired indicators across the 54 countries are the evidence base. The rubric must not reward localisation as such: the DPF separates sovereignty from localisation, and the DTP forbids forced location of computing facilities, so the top of the ladder is control with portability, not walls

## 4. Instruments, once each

Each instrument named in §3, with what it is, who adopted it, when, its status and the URL checked on 2026-09-22. AU treaty status pages carry ratification lists; counts quoted are as read on the day and are not maintained here.

**AU organ instruments**

- **Digital Transformation Strategy for Africa 2020–2030 (DTS)** — endorsed by STC-CICT-3 Oct 2019 and the Executive Council, EX.CL/Dec.1074(XXXVI) para 12, Feb 2020 (verified); published 18 May 2020. No mid-term review adopted through the 49th Executive Council (Jul 2026): the evaluation was tendered Jul 2025 (ET-AUC-486512-CS-QCBS), so the 2030 targets freeze as published. Non-binding strategy. Verified targets: universal access ≥ 6 Mb/s at ≤ 1 US cent/MB and a device ≤ USD 100 by 2030; ≥ 30 % of content developed and hosted in Africa; 99.9 % digital legal identity as part of civil registration by 2030; e-skills 100 m/yr by 2021 and 300 m/yr by 2025; ≥ 2 international connections per Member State; Malabo in force by 2020 (missed: 2023). https://au.int/sites/default/files/documents/38507-doc-DTS_for_Africa_2020-2030_English.pdf ; decision text https://au.int/sites/default/files/decisions/38181-ex_cl_dec_1073_-_1096_xxxvi_e.pdf
- **Agenda 2063 Second Ten-Year Implementation Plan 2024–2033 (STYIP)** — Executive Council EX.CL/Dec.1260(XLIV) para 4, Feb 2024 (endorses); Assembly/AU/Dec.867(XXXVII), Feb 2024 (adoption and launch). Seven Moonshots; 2033 targets: 80 % of population at ≥ 6 Mb/s; 80 % of households with electricity; 40 % of graduates in STEM; TVET enrolment + 60 %; tertiary NER 50 %; 10 % of global research output; 80 % of primary completers digitally proficient. https://www.nepad.org/publication/agenda-2063-second-ten-year-implementation-plan-2024-2033 (PDF mirrored at https://www.un.org/osaa/sites/www.un.org.osaa/files/43517-wd-agenda_2063_styip_feb_2024_launch_version.pdf). Goal 20 financing ratios are from the First Ten-Year Plan (Assembly/AU/Dec.565(XXIV), 2015): https://au.int/sites/default/files/documents/33126-doc-11_an_overview_of_agenda.pdf
- **AU Convention on Cyber Security and Personal Data Protection (Malabo)** — Assembly, 27 Jun 2014; in force 8 Jun 2023; 21 signatures and 20 ratifications on the AU status list of 2 Feb 2026 (the older `29560-sl-` list still says 16). Art. 1 definitions; Chapter I e-transactions (Arts 2–7), Chapter II personal data (Arts 8–23; Art. 11 independent DPA; Art. 14(6) transfers, under the sensitive-data article), Chapter III cybersecurity (Arts 24–31). Article numbers verified against the AU PDF by OCR, 2026-09-23. Status list https://au.int/sites/default/files/AFRICAN%20UNION%20CONVENTION%20ON%20CYBER%20SECURITY%20AND%20PERSONAL%20DATA%20PROTECTION%20%281%29.pdf https://au.int/en/treaties/african-union-convention-cyber-security-and-personal-data-protection
- **AU Data Policy Framework (DPF)** — Executive Council EX.CL/Dec.1144(XL) para 37, 2–3 Feb 2022 (verified); published 28 Jul 2022. Non-binding; six sections; implementation as formulation → domestication → monitoring and evaluation (the "five phases" reported by the research pass are unverified — §6); §5.3.1 foundational data infrastructure. https://au.int/sites/default/files/documents/42078-doc-DATA-POLICY-FRAMEWORKS-2024-ENG-V2.pdf
- **AU Interoperability Framework for Digital ID** — Executive Council EX.CL/Dec.1144(XL) para 37, 2–3 Feb 2022, with the DPF; published 11 Dec 2023. Ten principles (§3.1), three-layer architecture (§3.2), trust framework and Levels of Assurance (§3.3), Member-State commitments (§4.1), three phases. https://au.int/sites/default/files/documents/43393-doc-AU_Interoperability_framework_for_D_ID_English.pdf
- **Continental Artificial Intelligence Strategy** — 2nd Extraordinary STC-CICT Jun 2024; Executive Council EX.CL/Dec.1268(XLV) para 28(b), Accra, 18–19 Jul 2024 (its Conceptual Framework earlier, EX.CL/Dec.1234(XLIV) para 77(f)). Five focus areas, fifteen action areas; Phase 1 2025–2026, Phase 2 from 2028. https://au.int/sites/default/files/documents/44004-doc-EN-_Continental_AI_Strategy_July_2024.pdf
- **African Digital Compact** — STC-CICT Jun 2024; Executive Council EX.CL/Dec.1268(XLV) para 28(a), Jul 2024 (mandated by EX.CL/Dec.1234(XLIV) para 78(a)); published Jul 2024. No numeric targets. https://au.int/sites/default/files/documents/44005-doc-EN_African_Digital_Compact_-_July_2024.pdf
- **AfCFTA Protocol on Digital Trade (DTP)** — Assembly 37th Ordinary Session, Feb 2024; eight annexes adopted 38th Ordinary Session, 15–16 Feb 2025. Binding once in force (22 ratifications, AfCFTA Agreement Art. 23); au.int carries no status list and no count was found. Article numbers verified against the Feb 2024 text: 8 electronic trust services, 9 e-authentication, 12 e-contracts, 13 e-invoicing, 14 digital ID, 15 digital payments, 16 e-transactions framework, 19 interoperability and mutual recognition, 20 cross-border data, 22 computing facilities, 25 cybersecurity, 27 consumer protection, 38 publication of information, 43 cooperation. All eight annexes (Art. 46) are public in the Compiled Certified Legal Instruments, circulated 27 May 2025; the payments annex is titled *Cross-Border Digital Payments*: https://au.int/sites/default/files/treaties/44963-ax-ENG_Circulation_Digital_Trade_Compiled_Certified_Legal_Instruments_38thAssembly_Feb_2025_27_May2025.pdf Earlier drafts number differently. https://au.int/sites/default/files/treaties/45079-treaty-EN_AfCFTA_Protocol_on_Digital_Trade.pdf ; annex summaries https://www.tralac.org/documents/events/tralac/5918-2025-conference-two-pager-summary-of-the-annexes-to-the-afcfta-protocol-on-digital-trade/file.html
- **AfCFTA Protocol on Trade in Goods, Annexes 3 (Customs Cooperation) and 4 (Trade Facilitation)** — Kigali, Mar 2018; in force 30 May 2019. Article numbers not verified. https://www.tralac.org/documents/resources/factsheets/4388-afcfta-agreement-annexes-customs-and-border-management-july-2021/file.html
- **ACHPR Declaration of Principles on Freedom of Expression and Access to Information in Africa** — ACHPR 65th Ordinary Session, Banjul, 10 Nov 2019. Soft law interpreting Art. 9 of the African Charter. Principles 7, 17, 26, 29, 34, 37, 41, 42. https://achpr.au.int/en/node/902 ; PDF https://achpr.au.int/sites/default/files/files/2022-08/declarationofprinciplesonfreedomofexpressioneng2019.pdf
- **ACHPR Model Law on Access to Information for Africa** — ACHPR, 2013. Clause-level checklist (§3 note). https://achpr.au.int/en/node/873 ; PDF https://achpr.au.int/sites/default/files/files/2021-08/modellawonaccesstoinformationforafrica2013eng.pdf
- **ACHPR Principles and Guidelines on the Right to a Fair Trial and Legal Assistance in Africa** — ACHPR, 2003. Court records and public access. https://hrlibrary.umn.edu/instree/AfricanPrinciples2005.html
- **African Charter on Democracy, Elections and Governance (ACDEG)** — Assembly 30 Jan 2007; in force 15 Feb 2012; 46 signatures and 39 ratifications on the AU status list of 8 Jul 2024. Arts 2, 3, 12, 17, 27, 28, 30, 31. https://au.int/en/treaties/african-charter-democracy-elections-and-governance
- **AU Guidelines for Election Observation and Monitoring Missions** — Durban Declaration AHG/Decl.1(XXXVIII), 2002. §§4.6.10, 5.2.9, 5.4.1 voter registers. https://achpr.au.int/en/node/872
- **African Charter on Values and Principles of Public Service and Administration** — Assembly 31 Jan 2011; in force 23 Jul 2016; 38 signatures and 21 ratifications on the AU status list of 8 Jul 2024. Arts 2(4), 5(4), 6(3), 8, 9, 21. https://au.int/sites/default/files/treaties/36386-treaty-charter_on_the_principles_of_public_service_and_administration.pdf
- **African Charter on the Values and Principles of Decentralisation, Local Governance and Local Development** — Assembly 27 Jun 2014; **not in force**: 18 signatures and 8 ratifications on the AU status list of 25 Mar 2022, against the 15 its Art. 24 requires (the au.int page's "in force 13 Jan 2019" is wrong). The rows citing it anchor on an adopted instrument's text, as rows citing a non-binding strategy do. Arts 12, 13, 16. https://au.int/en/treaties/african-charter-values-and-principles-decentralisation-local-governance-and-local ; text https://africanlii.org/akn/aa-au/act/charter/2014/values-and-principles-of-decentralisation-local-governance-and-local-development/eng@2014-06-27
- **African Charter on Statistics** — Assembly 3–4 Feb 2009; in force 8 Feb 2015; 35 signatures and 26 ratifications on the AU status list of 19 Sep 2023. Art. 3 principles; obligation to align national law. https://au.int/sites/default/files/treaties/36412-treaty-african_charter_on_satistics_eng.pdf ; **AU Model Statistics Law** https://au.int/sites/default/files/documents/32838-doc-charter_modellawen.pdf
- **Strategy for the Harmonization of Statistics in Africa 2017–2026 (SHaSA 2)** — Assembly Jan 2018; EX.CL/Dec.987(XXXII). SO 1.1 administrative sources and CRVS; SO 3.1 NSDS. https://au.int/sites/default/files/documents/34580-doc-34577-doc-shasa_ii_strategy_eng_full_web.pdf
- **Africa Data Consensus** — High-Level Conference on the Data Revolution, 8th AU–ECA Conference of Ministers, Addis Ababa, Mar 2015. Ministerial consensus. https://repository.uneca.org/handle/10855/22669
- **Protocol to the ACHPR on the Rights of Citizens to Social Protection and Social Security** — Assembly 35th Ordinary Session, 6 Feb 2022; not in force; 2 signatures and 2 ratifications (Zimbabwe, Uganda) on the AU status list of 22 May 2026. Arts 4, 11, 23, 25. https://au.int/sites/default/files/treaties/42736-treaty-PROTOCOL_TO_THE_AFCHPR_ON_THE_RIGHTS_ON_CITIZEN_TO_SOCIAL_PROTECTION_AND_SECURITY_E.pdf
- **Maputo Protocol (Rights of Women in Africa)** — Assembly 11 Jul 2003; in force 25 Nov 2005; 44 ratifications (2023). Arts 9, 12(2)(b), 18(2)(b), 19(b). https://au.int/sites/default/files/treaties/37077-treaty-charter_on_rights_of_women_in_africa.pdf
- **Protocol to the ACHPR on the Rights of Persons with Disabilities in Africa** — Assembly Jan 2018; in force 3 May 2024; 14 signatures and 17 ratifications on the AU status list of 22 May 2026. Arts 23, 24. https://au.int/en/treaties/protocol-african-charter-human-and-peoples-rights-rights-persons-disabilities-africa
- **Kampala Convention (IDPs)** — Assembly 22–23 Oct 2009; in force 6 Dec 2012. Arts 9(2)(k), 13. https://au.int/sites/default/files/treaties/36846-treaty-kampala_convention.pdf
- **OAU Convention Governing the Specific Aspects of Refugee Problems in Africa** — 10 Sep 1969; in force 20 Jun 1974. No digital or information provision identified. https://au.int/en/treaties/oau-convention-governing-specific-aspects-refugee-problems-africa
- **AU Declaration on Land Issues and Challenges in Africa** — Assembly/AU/Decl.1(XIII) Rev.1, Sirte, Jul 2009; no registration paragraph (verified). https://faolex.fao.org/docs/pdf/au168483.pdf ; **Framework and Guidelines on Land Policy in Africa** (AUC/AfDB/ECA, 2009–2011) — §3.6.2 reform of land rights delivery systems, including computerised Land Information Systems. PDF https://achpr.au.int/sites/default/files/files/2021-09/frameworkandguidelinesonlandpolicyinafrica2.pdf https://au.int/en/documents/20110131/framework-and-guidelines-land-policy-africa
- **African Space Policy and African Space Strategy** — Assembly 26th Ordinary Session, 31 Jan 2016. No numeric targets; African Space Agency inaugurated Cairo Apr 2025. https://au.int/sites/default/files/documents/37434-doc-au_space_strategy_isbn-electronic.pdf
- **Integrated African Strategy on Meteorology 2021–2030** — AMCOMET; original endorsed EX.CL/Dec.744(XXII), Jan 2013; revision mandated AMCOMET-4, Feb 2019. Pillar 2 satellites, WIGOS, GBON; ISO 9001 and 5 %-of-budget indicators. https://amcomet.wmo.int/sites/default/files/2024-11/wmo_amcomet_strategy_en_0.pdf
- **AU Digital Education Strategy and Implementation Plan (DES, 2023–2028)** — AUC-ESTI, Sep 2022 (adopting organ not verified: no Executive Council decision names it, §6; EU-funded). Device, connectivity and NREN targets 2027/2030; EMIS 2.0; five maturity categories of Member States. https://au.int/sites/default/files/documents/42416-doc-1._DES_EN_-_2022_09_14.pdf
- **Continental Education Strategy for Africa 2026–2035 (CESA 26-35)** — Executive Council EX.CL/Dec.1280(XLVI) para 29, Feb 2025 (adopts); published Jun 2025. No numeric targets. https://au.int/sites/default/files/documents/44940-doc-AU_CESA-2026-2035_Strategy_ENGLISH.pdf
- **Continental Strategy for TVET** — AU, 2018; re-issued Feb 2024; the 2025–2034 strategy adopted by EX.CL/Dec.1280(XLVI) para 29, Feb 2025. Content not extracted. https://au.int/en/documents/20240212/continental-strategy-technical-and-vocational-education-and-training-tvet-foster
- **STISA-2034** — STC-EST-5 ministers Nov 2024; adopted as "STISA 2025-2034" by EX.CL/Dec.1280(XLVI) para 29, Feb 2025; Assembly/AU/Dec.973(XXXIX) para 22, Feb 2026, commends the launch of its Implementation Plan. The strategy sets no R&D share of GDP; the Implementation Plan cites "the continental 1% of GDP target". Strategy https://au.int/sites/default/files/documents/45087-doc-AU_STISA_2025-2034_Strategy_ENGLISH.pdf ; https://www.nepad.org/publication/science-technology-and-innovation-strategy-africa-stisa-2034
- **AU Digital Agriculture Strategy 2024–2030** — AUC-ARBE, 2024; endorsed with its implementation plan (2024–2027) by EX.CL/Dec.1234(XLIV) para 32(iii), Feb 2024. https://au.int/sites/default/files/documents/43481-doc-DAS_EN.pdf
- **AfSEM strategic and action plans; Continental Power System Master Plan synthesis** — STC on infrastructure and energy, Zanzibar, 15 Sep 2023. https://www.nepad.org/continental-master-plan ; https://www.eeas.europa.eu/delegations/african-union-au/powering-africa%E2%80%99s-future-key-documents-officially-adopted-pave-way-sustainable-african-single_en
- **Statute of the AU Mechanism for Police Cooperation (AFRIPOL)** — Assembly 30 Jan 2017; text not machine-readable. https://au.int/en/treaties/statute-african-union-mechanism-police-cooperation-afripol
- **CAMI-20 Declaration on quality infrastructure / PAQI** — Conference of Ministers of Industry, Jun 2013; PAQI launched Aug 2013. The Declaration recognises PAQI and asks Member States to join ARSO; it creates no standards obligation (Abuja Treaty Art. 67 does). https://www.au.int/sites/default/files/documents/29820-doc-ti10434_e_original.pdf ; https://www.paqi.org/
- **AU Startup Model Law / Startup Policy Framework** — AUC with Google and Africa Practice, Jul 2024; not adopted by an organ; AU source page not located. https://www.globalcenter.ai/research/the-african-union-startup-model-law-framework-at-a-glance

**Continental agencies, alliances and conferences**

- **Africa CDC Digital Transformation Strategy** — launched 6 Mar 2023, Kigali; HealthConnekt Africa: 100,000 facilities and 2 m community health workers by 2030. https://africacdc.org/download/digital-transformation-strategy/ ; **AU Health Information Exchange Guidelines and Standards** (Africa CDC, Mar 2023) https://africacdc.org/download/african-union-health-information-exchange-guidelines-and-standards/ ; **Primary Health Care Digitalisation Framework** — Member States' Statement, 12 Mar 2026: 90 % digitally enabled PHC by 2035. https://africacdc.org/download/member-states-statement-on-the-primary-health-care-digitalization-framework/
- **Smart Africa Manifesto and Alliance** — Kigali Oct 2013; endorsed by AU Assembly Jan 2014. https://smartafrica.org/wp-content/uploads/2019/03/Design-English-13.03.pdf ; **Data Center and Cloud for Africa Blueprint** (2023, updated 2026) https://smartafrica.org/wp-content/uploads/2026/02/EN-BLUEPRINT-FOR-DATA-CENTER-AND-CLOUD-FOR-AFRICA-Updated.pdf ; **Digital Identity Blueprint** (2020) https://smartafrica.org/wp-content/uploads/2020/12/BLUEPRINT-SMART-AFRICA-ALLIANCE-%E2%80%93-DIGITAL-IDENTITY-LayoutY.pdf ; **Digital Health Blueprint** (Board, 26 Nov 2025) https://smartafrica.org/wp-content/uploads/2025/11/Digital-Health-Blueprint-English-2.pdf ; **Africa AI Council** (endorsed 2 Apr 2025) https://smartafrica.org/smart-africa-steering-committee-convenes-in-kigali-and-endorses-the-establishment-of-the-africa-artificial-intelligence-council/
- **PIDA Priority Action Plan 2 (2021–2030)** — Executive Council EX.CL/Dec.1108(XXXVIII) para 20, Feb 2021, endorses the project list (four projects referred to a PRC sub-committee); the 34th Assembly's decisions carry no PIDA item; prospectus 2023. https://www.au-pida.org/wp-content/uploads/2023/09/EN-NEPAD-PIDA-PAP2-Project-Prospectus-Web-1-92_81-81.pdf
- **AU AXIS project** — AUC, 2012–2017; national and regional IXPs. https://au.int/en/african-internet-exchange-system-axis-project-overview
- **ATU-R Recommendation 005-0** — African Telecommunications Union, Jul 2021. https://atuuat.africa/wp-content/uploads/2021/08/En_ATU-R-Recommendation-005-0.pdf ; **ATU-R Report 004-0**, *Status of satellite services licensing in Africa and international trends*, Aug 2022 (Rev1 May 2023) https://atuuat.africa/wp-content/uploads/2023/05/ATU-R-Report-004-0-Status-report-on-Satellite-Services-Licensing-in-Africa_Rev1-1-1.pdf
- **APAI-CRVS and the Conference of African Ministers responsible for Civil Registration** — AUC/UNECA/AfDB programme; CRVS Decade 2017–2026; 5th conference Lusaka Oct 2019 (Lusaka Declaration read: paras 3 and 7 on interoperability; no registration-rate target); 6th Addis Ababa Oct 2022, expert segment only, the ministerial segment postponed, so no 2022 declaration. Lusaka text https://au.int/sites/default/files/newsevents/workingdocuments/38223-wd-declaration_crvs_after_adoption_english.pdf https://apai-crvs.uneca.org/ ; https://au.int/en/ea/keyevents/camcr
- **PAPSS** — mandated Niamey Extraordinary Summit 7 Jul 2019; launched 13 Jan 2022; 18 central banks (Nov 2025). https://au-afcfta.org/operational-instruments/papss/
- **Mission 300** — AfDB and World Bank, 2024; Dar es Salaam Energy Declaration endorsed by 48 countries Jan 2025 (Assembly endorsement not verified). https://www.afdb.org/en/topics-and-sectors/initiatives-and-partnerships/mission-300
- **PRIDA** — AU–EU–ITU programme, 2018/19. https://prida.africa/policy-harmonisation/
- **Personal Data Protection Guidelines for Africa** — AUC and Internet Society, May 2018; 18 recommendations. https://www.internetsociety.org/resources/doc/2018/personal-data-protection-guidelines-for-africa/

**REC instruments (recorded as rungs)**

- **ECOWAS Supplementary Act A/SA.1/01/10 on Personal Data Protection** — Abuja, 16 Feb 2010; binding; Art. 14 DPA, Art. 36 adequacy. https://africanlii.org/akn/aa-ecowas/act/2010/1-1/eng@2010-12-31
- **SADC Model Laws (HIPSSA)** — data protection, e-transactions, cybercrime; 2012–13. https://www.itu.int/en/ITU-D/Projects/ITU-EC-ACP/HIPSSA/Documents/FINAL%20DOCUMENTS/FINAL%20DOCS%20ENGLISH/sadc_model_law_data_protection.pdf
- **EAC Legal Framework for Cyberlaws Phase I** — 2010. https://unctad.org/publication/harmonizing-cyberlaws-and-regulations-experience-east-african-community

**Global references**

- **ITU / UN Tech Envoy Universal and Meaningful Connectivity 2030 targets** (2022) — 100 % use and ownership (15+), households, schools (20 Mb/s); > 70 % basic and > 50 % intermediate skills; entry-level broadband < 2 % GNI pc; gender parity. https://www.itu.int/itu-d/meetings/statistics/wp-content/uploads/sites/8/2022/04/UniversalMeaningfulDigitalConnectivityTargets2030.pdf
- **Broadband Commission 2025 Advocacy Targets** — Target 1 funded national broadband plan; Target 2 affordability < 2 % GNI pc. https://www.broadbandcommission.org/advocacy-targets/1-policy/ ; https://www.broadbandcommission.org/advocacy-targets/2-affordability/
- **ITU Global Cybersecurity Index 2024** — five pillars, five tiers. https://www.itu.int/en/ITU-D/Cybersecurity/pages/global-cybersecurity-index.aspx
- **Oxford GCSCC Cybersecurity Capacity Maturity Model** (2021) — five stages. https://gcscc.ox.ac.uk/the-cmm
- **World Bank GovTech Maturity Index 2025** — 197 economies; CGSI, PSDI, DCEI, GTEI; groups A–D. https://www.worldbank.org/en/programs/govtech/gtmi-2025-update
- **UN E-Government Survey 2024** — EGDI bands; E-Participation Index levels; LOSI. https://publicadministration.un.org/egovkb/en-us/Reports/UN-E-Government-Survey-2024
- **World Bank ID4D Principles on Identification** (2017, rev. 2021). https://www.idprinciples.org/
- **UN Legal Identity Agenda; UN Handbook on CRVS and Identity Management** (2022). https://desapublications.un.org/file/1074/download
- **UN Principles and Recommendations for a Vital Statistics System, Rev. 3** (2014). https://unstats.un.org/unsd/demographic-social/Standards-and-Methods/files/Principles_and_Recommendations/CRVS/M19Rev3-E.pdf
- **UN Universal DPI Safeguards Framework** (Sep 2024). https://www.dpi-safeguards.org/framework
- **FATF Guidance on Digital Identity** (Mar 2020). https://www.fatf-gafi.org/content/dam/fatf-gafi/guidance/Guidance-on-Digital-Identity-Executive-Summary.pdf
- **World Bank Global Findex 2025** (2024 data). https://www.worldbank.org/en/publication/globalfindex
- **G20/FSB cross-border payments targets** (2021). https://www.swift.com/payments/g20-goals-enhancing-cross-border-payments (FSB source not read)
- **CPMI–World Bank Payment Aspects of Financial Inclusion** (2016). https://www.bis.org/cpmi/publ/d144.htm ; **CPSS-IOSCO PFMI** (2012), Responsibilities text not read. https://www.bis.org/cpmi/publ/d101a.pdf
- **G20 High-Level Principles for Digital Financial Inclusion** (2016). https://www.gpfi.org/publications/g20-high-level-principles-digital-financial-inclusion
- **G20/OECD High-Level Principles on Financial Consumer Protection** (rev. 2022). https://www.cssf.lu/en/2022/12/updated-g20-oecd-high-level-principles-on-financial-consumer-protection/
- **TADAT Field Guide 2019**. https://www.tadat.org/content/dam/tadat/en/assessments/TADAT%20Field%20Guide%202019%20-%20English.pdf
- **UNCITRAL Legislative Guide on Key Principles of a Business Registry** (2018). https://uncitral.un.org/en/texts/msmes/legislativeguides/business_registry ; **UNCITRAL e-commerce texts** (1996, 2001, 2005). https://uncitral.un.org/en/texts/ecommerce
- **UNCTAD Global Cyberlaw Tracker**. https://unctad.org/topic/ecommerce-and-digital-economy/ecommerce-law-reform/summary-adoption-e-commerce-legislation-worldwide
- **UN-GGIM Framework for Effective Land Administration** (2020). https://ggim.un.org/meetings/GGIM-committee/10th-Session/documents/E-C.20-2020-29-Add_2-Framework-for-Effective-Land-Administration.pdf
- **UPU "Addressing the world – An address for everyone"** (2012). https://www.upu.int/UPU/media/upu/publications/whitePaperAddressingTheWorldEn.pdf
- **World Bank "Social Registries for Social Assistance and Beyond"** (2017). https://documents1.worldbank.org/curated/en/698441502095248081/pdf/117971-REVISED-PUBLIC-Discussion-paper-Social-Registries-for-Social-Assistance-and-Beyond.pdf
- **WHO Global Strategy on Digital Health 2020–2025** (extended to 2027). https://www.who.int/docs/default-source/documents/gs4dhdaa2a9f352b0445bafbc79ca799dce4d.pdf
- **UNESCO Recommendation on the Ethics of AI** (2021) and Readiness Assessment Methodology. https://www.unesco.org/en/artificial-intelligence/recommendation-ethics
- **Global Digital Compact** (UNGA, Sep 2024). https://www.un.org/global-digital-compact/sites/default/files/2024-09/Global%20Digital%20Compact%20-%20English_0.pdf
- **UN Fundamental Principles of Official Statistics** (GA res. 68/261, 2014). https://unstats.un.org/unsd/dnss/gp/fp-new-e.pdf
- **ECOSOC E/RES/2025/13, 2030 World Population and Housing Census Programme**. https://unstats.un.org/unsd/demographic-social/census/
- **International Open Data Charter** (2015). https://opendatacharter.org/principles/ ; **World Bank Open Data Readiness Assessment**. https://opendatatoolkit.worldbank.org/en/data/opendatatoolkit/odra
- **World Bank Statistical Performance Indicators**. https://www.worldbank.org/en/programs/statistical-performance-indicators
- **OECD Recommendation on Digital Government Strategies** (2014, OECD-LEGAL-0406) and **Recommendation on Open Government** (2017) — pages are script-rendered; titles and dates only. https://legalinstruments.oecd.org/en/instruments/OECD-LEGAL-0406
- **Addis Ababa Action Agenda** (2015). https://www.un.org/esa/ffd/ffd3/wp-content/uploads/sites/2/2015/08/AAAA_Outcome.pdf ; **Busan Partnership** (2011). https://effectivecooperation.org/content/busan-partnership-outcome-document
- **UNIDO Quality Policy Technical Guide** (2018). https://www.unido.org/sites/default/files/files/2018-06/QP_TECHNICAL_GUIDE_08062018_online.pdf
- **ISO/IEC 30134-2 (PUE) and 30134-9 (WUE)**. https://www.iso.org/standard/63451.html ; https://www.iso.org/standard/77692.html
- **Tracking SDG7**. https://trackingsdg7.esmap.org/
- **WMO Early Warnings for All**. https://wmo.int/activities/early-warnings-all
- **GSMA Mobile Gender Gap Report 2026**. https://www.gsma.com/gender-gap/
- **UNHCR Digital Transformation Strategy 2022–2026**. https://www.unhcr.org/digitalstrategy/digital-inclusion/
- **Digital Earth Africa**. https://digitalearthafrica.org/en_za/about-digital-earth-africa/

## 5. The one without an anchor, and the eight on a thin one

**The five `geopol.*` indicators and `finance.mou--strategic-relationships`** are out of the assessment *(Bill, 2026-09-22)*; §2 and the Geopolitics section say why and what replaces them.

**`digital.rural--digitalisation-of-rural-police-stations`** has nothing at any tier below the national police agency and gets a Corpus rubric *(Bill, 2026-09-22)*, written on the pattern of the other three `digital.rural` rows: connected · equipped · records digital · linked to the national system. It is the one row in the register whose tier is `corpus`, and the published count says so.

**Eight more have an anchor the rubric will lean on lightly**, and the published count of Corpus-interpolated rungs should include them: the four global-tier rows (`dpi.registry--address-register`, `dpi.registry--tax-register`, `dpi.mis--tax`, `dpi.pay--population-uptake`), where the anchor is a UPU white paper, a TADAT field guide or a Findex figure with no African instrument behind it, and the four marked *weak* in §3 (`gov.standards--national-quality-standards`, `dpi.registry--land-register`, `dpi.mis--land`, `dpi.mis--justice`), where an AU instrument exists but says almost nothing about the indicator. Two continental-tier rows (`infra.store--off-site-backup-capacity`, `infra.energy--sufficient-energy-and-water-for-data-centres`) rest on a Smart Africa blueprint alone and are the next thinnest.

## 6. What is owed before the lookup is cut

**Checked against primary texts on 2026-09-23 (task A2)**: AU decision PDFs, the AU treaty status lists, the Malabo and DTP texts, the CAMCR declarations and reports, the ACHPR Model Law, the land F&G, ATU-R Report 004-0, STISA-2034 and its Implementation Plan, the ARSO, CAMI-20 and AfCFTA Annex 6 texts. Every correction is in §3 and §4. Three lines stay open, and none blocks the lookup — each is a status or a count, not a provision:

- **The DES's adopting organ.** No Executive Council decision names it. Searched: EX.CL/Dec.1190(XLII) paras 32–37, which endorse STC-EST-4's declaration only, and the 41st and 43rd–49th sessions. EX.CL/Dec.1144(XL) para 38 shows it still being drafted in Feb 2022. The row carries *adopting organ not verified*.
- **The AfCFTA DTP's ratification count.** au.int has no status list for the Protocol, and no current count was found. It enters into force at 22.
- **The DPF's "five implementation phases".** The Governance research pass reported five phases (Member-State adoption … evaluation … intra-African collaboration); two reads of the AU PDF on 2026-09-23 found no numbered phases, only an implementation figure of *formulation → domestication → monitoring and evaluation* and a statement of progressive realisation. The rubric's `data-governance-policy` row follows the figure and leaves stage 4 interpolated until this is settled against the full text. Blocks nothing.
- **The DAS period.** The decision endorses the strategy *and its implementation plan (2024–2027)*, and the register calls the strategy 2024–2030. The two were not reconciled against the strategy document. The norm is the strategy's text either way.

**The DTS mid-term review has revised nothing**: it was tendered in Jul 2025 and no decision through the 49th Executive Council (Jul 2026) adopts one, so the rubric freezes the 2030 targets as published.

## 7. Global datasets are references, never the record

*(Bill, 2026-09-22.)* Where a global index or dataset is the norm or the reference for a measure — the ITU's connectivity series, Findex, Tracking SDG7, the UIS — **its figure is not automatically the figure of record.** Corpus's own collected figure, where the base holds one, is likely to be more accurate and is almost always more recent: most global datasets lag what the base is doing by a year or more. So for every measure the rubric names the reference dataset for the *band* and the *target*, and the assessment's `value` column carries whichever dated figure is best evidenced — a cited primary figure from the ledger (a regulator's quarterly statistics, a census, a ministry's audited count) takes precedence over the global dataset's, and the global figure is used when the base holds nothing, or holds only a claim the global figure contradicts. The `value_source` column says which was used, and where the two disagree materially the qualifier says so, because the disagreement is itself a finding the status report may want. Africa-only quintiles *(Bill, 2026-09-22)* are computed from whichever figure the assessment carries for each country, not from the global dataset's column, so that the banding reflects what Corpus knows rather than what the ITU published.

Nothing in this register has been cut to `lookups/`, no script reads it, and no indicator file has been touched. The anchors and kinds are ruled; §6 is what stands between the register and the lookup.
