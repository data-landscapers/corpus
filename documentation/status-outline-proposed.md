---
type: spec
reader: cc
title: Status outline — proposed indicators
---

# Status outline — proposed indicators

Sixty-two candidate indicators for the thin sub-sections of `status-outline.md`, where they are cited as `[PROPOSED]`, in the schema of `prep/status-indicators-africa-dpi.csv` (*Chapter · Section · Variable Name · Definition · Variable Id*). **None is collected**, and `status_lib.outline()` does not read this file.

The geopolitics and finance groups are summary rollups of what the OSINT wiki already holds as dated entities (deals, agreements, named foreign actors), not new research. Satellite, research and local government would need collection.

## Geopolitics — 25 indicators

Five vectors, instantiated identically for each of the five actors, so the answer is comparable both across actors within a country and across countries for one actor. `{actor}` is one of `usa`, `china`, `eu`, `india`, `gulf`.

| Section | Variable Name | Definition | Variable Id |
| --- | --- | --- | --- |
| Presence | Infrastructure Footprint | Physical digital infrastructure in the country built, financed or operated by parties from this actor — submarine cable landings, terrestrial backbone, data centres, network equipment. Recorded as none / single project / multiple projects / dominant supplier, with the named projects. | `geopol-{actor}-infra` |
| Presence | Platform and Systems Presence | Cloud regions, platform services or government systems supplied by this actor's firms, and whether government workloads run on them. | `geopol-{actor}-platform` |
| Commitment | Active Financing | Value of this actor's digital-sector financing commitments to the country that are live at the reporting date, in the announcing party's own currency, with any USD figure written as a dated conversion. | `geopol-{actor}-finance` |
| Commitment | Standing Agreements | Bilateral digital cooperation agreements, MoUs or framework arrangements in force with this actor, and whether they carry binding terms. | `geopol-{actor}-agreement` |
| Commitment | Capacity Programmes | Skills, training, scholarship or institutional-capacity programmes run or funded by this actor in the digital sector. | `geopol-{actor}-capacity` |

The 25 ids: `geopol-usa-infra`, `geopol-usa-platform`, `geopol-usa-finance`, `geopol-usa-agreement`, `geopol-usa-capacity`, `geopol-china-infra`, `geopol-china-platform`, `geopol-china-finance`, `geopol-china-agreement`, `geopol-china-capacity`, `geopol-eu-infra`, `geopol-eu-platform`, `geopol-eu-finance`, `geopol-eu-agreement`, `geopol-eu-capacity`, `geopol-india-infra`, `geopol-india-platform`, `geopol-india-finance`, `geopol-india-agreement`, `geopol-india-capacity`, `geopol-gulf-infra`, `geopol-gulf-platform`, `geopol-gulf-finance`, `geopol-gulf-agreement`, `geopol-gulf-capacity`.

## Regional collaboration — 2 indicators

| Section | Variable Name | Definition | Variable Id |
| --- | --- | --- | --- |
| Regional | Continental Instrument Status | Status of the AU Malabo Convention and comparable continental digital instruments — not signed / signed / ratified / domesticated in national law — with the date of each step. | `geopol-regional-instrument` |
| Regional | Regional Programme Membership | Regional digital bodies and programmes the country is a party to — Smart Africa, the AfCFTA digital trade protocol, REC-level data frameworks — and whether membership carries obligations. | `geopol-regional-membership` |

## Technology — 4 indicators

| Section | Variable Name | Definition | Variable Id |
| --- | --- | --- | --- |
| AI | Government AI Deployment | AI systems in production use in government service delivery or administration, named, as distinct from strategy commitments or pilots. | `tech-ai-deployment` |
| ICT Industry | Telecommunications Market Structure | Number of mobile network operators, the market share of the largest, and whether any is state-owned. | `tech-industry-mnomarket` |
| ICT Industry | Domestic Software and Services Industry | Size of the domestic software, IT services and BPO sector, by employment or revenue, and its export earnings where reported. | `tech-industry-softwaresize` |
| ICT Industry | Domestic Supply of Government ICT | Share of government ICT procurement awarded to domestically registered suppliers. | `tech-industry-localsupply` |

## Research institutions — 4 indicators

| Section | Variable Name | Definition | Variable Id |
| --- | --- | --- | --- |
| Research | Research Output in Computing and Data | Peer-reviewed output in computing, data science and digital governance from institutions in the country, over a stated window. | `capacity-research-output` |
| Research | Research and Development Expenditure | Gross domestic expenditure on R&D as a share of GDP, dated. | `capacity-research-spend` |
| Research | National Research and Education Network | Whether an NREN exists, is operational and is connected to a regional backbone. | `capacity-research-nren` |
| Research | Research Use in Policymaking | Whether national digital policy documents cite domestic research, and whether a standing advisory mechanism links research institutions to policymakers. | `capacity-research-policyuse` |

## Sub-national government — 4 indicators

| Section | Variable Name | Definition | Variable Id |
| --- | --- | --- | --- |
| Local Government | Sub-National Service Portals | Whether sub-national administrations operate their own digital service portals, and how many do. | `localgov-portal` |
| Local Government | Sub-National Financial Systems | Whether local government financial management systems exist and whether they are integrated with the national IFMIS. | `localgov-ifmis` |
| Local Government | Sub-National Expenditure Share | Share of total public expenditure executed at sub-national level, dated. | `localgov-fiscalshare` |
| Local Government | Sub-National Office Connectivity | Whether local government offices have functioning internet connectivity, and what proportion do. | `localgov-connectivity` |

## Satellite and Earth observation — 8 indicators

| Section | Variable Name | Definition | Variable Id |
| --- | --- | --- | --- |
| Earth Observation | Space or Geospatial Agency | Whether a national space agency or designated Earth-observation body exists, and its mandate. | `sat-agency` |
| Earth Observation | Ground Station or Receiving Facility | Whether a satellite ground station or data-receiving facility operates in the country. | `sat-groundstation` |
| Earth Observation | Space or Geospatial Data Policy | Whether a national space policy or geospatial data policy has been adopted. | `sat-policy` |
| Earth Observation | Imagery in Land Administration | Whether satellite or aerial imagery is used in the land register or cadastre, and whether it is current. | `sat-landuse` |
| Earth Observation | Imagery in Agricultural Monitoring | Whether Earth observation feeds agricultural statistics, crop monitoring or food security assessment. | `sat-agriculture` |
| Earth Observation | Imagery in Disaster and Climate Monitoring | Whether Earth observation feeds disaster early warning or climate monitoring. | `sat-disaster` |
| Earth Observation | Regional Programme Participation | Whether the country participates in GMES & Africa, Digital Earth Africa or comparable regional EO programmes. | `sat-regional` |
| Earth Observation | Open Geospatial Data | Whether national geospatial datasets are published under an open licence and in a machine-readable form. | `sat-opengeo` |

## New investments — 7 indicators

Derived from the wiki's deal entities and the hubs' compiled `## Financing` block, over a stated rolling window.

| Section | Variable Name | Definition | Variable Id |
| --- | --- | --- | --- |
| Investment | Committed Value | Total value of digital-sector investment commitments announced in the reporting window, in the announcing party's own currency, with any USD figure written as a dated conversion. | `fin-new-value` |
| Investment | Commitment Count | Number of distinct commitments announced in the window. | `fin-new-count` |
| Investment | Dominant Source | Where the majority of committed value originates — multilateral, bilateral, private, or domestic. | `fin-new-source` |
| Investment | Dominant Instrument | The predominant instrument — grant, concessional loan, commercial loan, equity, or in-kind. | `fin-new-instrument` |
| Investment | Dominant Target | The subsector taking the largest share — connectivity, data centres, identity, payments, government systems, skills. | `fin-new-target` |
| Investment | Disbursement Against Commitment | Share of committed value with evidence of actual disbursement, and the evidence for it. | `fin-new-disbursed` |
| Investment | Largest Active Commitment | The single largest live commitment, named, with its counterparty, value and date. | `fin-new-largest` |

## Agreements — 6 indicators

| Section | Variable Name | Definition | Variable Id |
| --- | --- | --- | --- |
| Agreements | Agreements in Force | Number of digital cooperation MoUs and framework agreements in force at the reporting date. | `fin-mou-count` |
| Agreements | Principal Counterparties | The parties on the other side of those agreements — states, multilaterals, vendors. | `fin-mou-partners` |
| Agreements | Binding Content | Whether the agreements carry binding commitments or stated values, or are statements of intent only. | `fin-mou-binding` |
| Agreements | Text Published | Whether the agreement text is publicly available, and where. | `fin-mou-published` |
| Agreements | Vendor Agreements | Standing agreements with named technology vendors, and what they cover. | `fin-mou-vendor` |
| Agreements | Regional Agreements | Regional and bloc-level digital agreements the country is party to. | `fin-mou-regional` |

## Domestic budget — 2 indicators

| Section | Variable Name | Definition | Variable Id |
| --- | --- | --- | --- |
| Budget | Digital Share of Appropriation | Share of the national budget appropriated to digital and ICT, dated to the fiscal year, with the budget lines counted stated. | `fin-budget-ictshare` |
| Budget | Digital Budget Execution | Share of the digital appropriation actually executed in the fiscal year. | `fin-budget-execution` |
