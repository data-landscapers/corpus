---
type: spec
reader: cc
title: Status outline — Geopolitics to Finance
---

# Status outline — Geopolitics to Finance

The questions and checklists for the last five chapters of `status-outline.md`, whose preamble governs them. `status_lib.outline()` reads the headings from both files, so each heading lives in one of them only. `[PROPOSED]` definitions are in `status-outline-proposed.md`.

---

## Geopolitics

**No indicator in the DPI dataset addresses any of the five actor slugs.** Two DPI indicators are weak proxies for hyperscaler presence — `ict-storage-cloudadoption` and `ict-storage-dcpresence` — and neither attributes a provider. Those five sub-sections are currently answered entirely from the wiki, where `geopol.*`-tagged sources carry named actors and dated commitments.

**`geopol.sovereignty` asks a different question** — what the state keeps for itself, not what one power holds — and is the chapter's one sub-section the maturity assessment stages (`indicator-digital-sovereignty.md`; the five actor sub-sections are not assessed but stay here unchanged). The dataset answers part of it; the rest is answered from the wiki, reading the agreements the five actor sub-sections list for their terms.

Five indicators are proposed for each of the five actors, on a common frame, so that the answer for one country is comparable across actors and the answer for one actor is comparable across countries. The suffixes are the same in every case: `-infra`, `-platform`, `-finance`, `-agreement`, `-capacity`. Full definitions are in `status-outline-proposed.md`.

### `geopol.usa` — US / hyperscaler activities

*What is the American and US-platform footprint, and what does it hold?*

- Physical infrastructure built, financed or operated by US parties — `[PROPOSED] geopol-usa-infra`
- Platform and cloud presence, and whether government runs on it — `[PROPOSED] geopol-usa-platform`, `ict-storage-cloudadoption`, `ict-storage-dcpresence`
- Active financing commitments from US public and private sources — `[PROPOSED] geopol-usa-finance`
- Standing bilateral agreements and their terms — `[PROPOSED] geopol-usa-agreement`
- Skills, training and scholarship programmes — `[PROPOSED] geopol-usa-capacity`

### `geopol.china` — China activities

*What is the Chinese footprint, and what does it hold?*

- Physical infrastructure built, financed or operated by Chinese parties — `[PROPOSED] geopol-china-infra`
- Platform, network equipment and government systems supplied — `[PROPOSED] geopol-china-platform`
- Active financing commitments — `[PROPOSED] geopol-china-finance`
- Standing bilateral agreements and their terms — `[PROPOSED] geopol-china-agreement`
- Skills, training and scholarship programmes — `[PROPOSED] geopol-china-capacity`

### `geopol.eu` — EU activities

*What is the European footprint, and what does it hold?*

- Physical infrastructure built or financed by EU parties — `[PROPOSED] geopol-eu-infra`
- Platform and systems presence — `[PROPOSED] geopol-eu-platform`
- Active financing commitments, Global Gateway included — `[PROPOSED] geopol-eu-finance`
- Standing agreements, and adequacy or GDPR-alignment arrangements — `[PROPOSED] geopol-eu-agreement`
- Skills and institutional capacity programmes — `[PROPOSED] geopol-eu-capacity`

### `geopol.india` — India activities

*What is the Indian footprint, and what does it hold?*

- Physical infrastructure built or financed by Indian parties — `[PROPOSED] geopol-india-infra`
- Platform presence, and any India Stack-derived deployment — `[PROPOSED] geopol-india-platform`
- Active financing commitments — `[PROPOSED] geopol-india-finance`
- Standing agreements and their terms — `[PROPOSED] geopol-india-agreement`
- Skills and training programmes — `[PROPOSED] geopol-india-capacity`

### `geopol.gulf` — Gulf/UAE activities

*What is the Gulf footprint, and what does it hold?*

- Physical infrastructure, data centres especially — `[PROPOSED] geopol-gulf-infra`
- Platform and operator holdings — `[PROPOSED] geopol-gulf-platform`
- Active financing commitments and equity positions — `[PROPOSED] geopol-gulf-finance`
- Standing agreements and their terms — `[PROPOSED] geopol-gulf-agreement`
- Skills and training programmes — `[PROPOSED] geopol-gulf-capacity`

### `geopol.sovereignty` — Digital sovereignty

*How far does the state control its own digital estate — where its data sits and under whose law, who can run and change its core systems, and on what terms it has bound itself to outside providers and powers?*

- Whether there is a rule on where state data sits, and whether it localises by category or wholesale — `ict-storage-datalocalisation`, `govtech-cloud-1.6`, `reg-cyber-cloud`, `reg-egov-cloudpolicy`
- Whether national control of government data and protection against foreign access are written into the exchange's rules — `exchange-uptake-sovereignty`
- Where government data is actually hosted, and under whose law — `ict-storage-govcloud`, with `ict-storage-dcpresence` and `ict-storage-cloudadoption` as weak proxies that attribute no provider
- Whether the core systems — identity, payments, the exchange layer, government hosting — can be maintained and changed nationally: source code, skills, contracts with exit terms — answered from the wiki; no variable
- The terms of agreements with outside providers and powers — data jurisdiction, portability, exit — answered from the wiki, from the agreements the five actor sub-sections list; no variable
- Whether the country takes part in a regional or continental cross-border data mechanism — answered from the wiki; `gov.regional` asks the same of cross-border transfers
- Where the state's AI models and compute sit, and whether its AI strategy addresses hosting, model ownership and access terms — answered from the wiki; no variable

The drafting brief — what the section says, what it reads, what *Not established* looks like — is `status-brief-geopol-sovereignty.md`.

---

## Capacity

### `capacity.literacy` — Literacy

*Can people read the systems they are being asked to use?*

- Basic digital literacy — `ict-capacity-digitalliteracy`
- Whether children complete school at all — `iiag-education-compeduc`, `iiag-education-educenr`
- Whether the education they get is any good — `iiag-education-eduqqual`, `iiag-education-educres`
- Whether it is equally distributed — `iiag-education-equeduc`
- What the public thinks of it — `iiag-education-sateduc`
- Whether education data is published — `odin-social-educoutcome`, `odin-social-educfacility`
- Whether digital skills programmes reach citizens and schools — `govtech-skills-45.6`

### `capacity.training` — Training and skills

*Is anyone being trained, and for what?*

- Whether there is a digital skills strategy — `govtech-skills-45`
- What the programme is and what it covers — `govtech-skills-45.5`, `govtech-skills-45.4`
- How far it reaches — `govtech-skills-45.6`
- Whether it is transparent — `govtech-skills-45.7`
- The tertiary ICT and STEM pipeline — `ict-capacity-tertiaryict`
- The developer community it feeds — `ict-capacity-devcommunity`
- Whether the labour market absorbs them — `iiag-business-secemplopp`, `odin-econ-labor`
- Whether the state runs a jobs platform that matches them — `govtech-job-25`, `govtech-job-25.2`, `govtech-job-25.3`

### `capacity.research` — Research institutions

*Is knowledge produced here, or only consumed here?*

- Innovation and technology hubs — `ict-innovation-techhubs`
- The tertiary ICT and STEM base — `ict-capacity-tertiaryict`
- Whether there is a national science and technology policy — `reg-ai-innov`
- Whether the statistical system can support research — `iiag-pubadmin-capstatsys`, `stats-score-use`
- University research output in computing and data — `[PROPOSED] capacity-research-output`
- Public research and development expenditure — `[PROPOSED] capacity-research-spend`
- Whether there is a national research and education network — `[PROPOSED] capacity-research-nren`
- Whether domestic research is used in policymaking — `[PROPOSED] capacity-research-policyuse`

---

## Digitalisation

### `digital.rural` — Rural digital data capture

*Does anything get captured digitally outside the capital?*

- Clinics — `rural-clinic-status`
- Schools — `rural-school-status`
- Police stations — `rural-police-status`
- Registry offices — `rural-registry-status`
- Whether the connectivity and power to do it exist — `ict-connectivity-4gcoverage`, `ict-energy-urbanruraldevide`
- Whether the exchange layer reaches rural users at all — `exchange-uptake-urbanrural`
- Whether the rural economy is supported and connected to markets — `iiag-rural-rurecosupp`, `iiag-rural-rurmarkaccifad`
- Agricultural and land data as the material being captured — `exchange-func-agriculture`, `odin-environ-agric`, `iiag-rural-rurlandwatacc`

### `digital.localgov` — Digitalisation of sub-national government

*Does the digital state exist below the national level?*

- Whether sub-national bodies participate in the exchange layer — `exchange-uptake-subnational`
- Whether local facilities are digitalised at all — `rural-registry-status`, `rural-clinic-status`, `rural-school-status`
- Whether the IFMIS and the TSA reach sub-national government — `govtech-financial-5.7`, `govtech-treasury-6.5`
- Whether the registers local government depends on exist — `reg-address-exists`, `reg-land-exists`
- Whether sub-national e-service portals exist — `[PROPOSED] localgov-portal`
- Whether local financial systems connect to the national one — `[PROPOSED] localgov-ifmis`
- What share of public expenditure is executed sub-nationally — `[PROPOSED] localgov-fiscalshare`
- Whether local government offices are connected — `[PROPOSED] localgov-connectivity`

---

## Data

### `data.statistics` — National statistics

*Can the state count what it governs?*

- The Statistical Performance Indicators pillar scores — `stats-score-use`, `stats-score-service`, `stats-score-products`, `stats-score-sources`, `stats-score-infrastructure`
- Whether the censuses have been run — `stats-census-population`, `stats-census-agriculture`, `stats-census-business`
- Whether the survey programme is maintained — `stats-survey-household`, `stats-survey-labour`, `stats-survey-health`, `stats-survey-agriculture`, `stats-survey-business`
- The capacity of the statistical office itself — `iiag-pubadmin-capstatsys`
- Whether administrative data can substitute for survey data — `reg-cr-uptake`, `reg-pop-uptake`, `iiag-pubadmin-civreg`
- Whether statistics are wired into the exchange layer — `exchange-func-planning`
- Whether vital statistics are published — `odin-social-pop`
- Whether the state monitors its own SDG and programme performance — `govtech-financial-5.11`, `govtech-financial-5.12`

### `data.open` — Open data

*Is public data actually public?*

- Whether there is an open data policy — `reg-egov-opendata`
- Whether the portal exists and is maintained — `govtech-opendata-29`, `govtech-opendata-29.3`, `govtech-opendata-29.2`, `govtech-opendata-29.4`
- Social data coverage and openness — `odin-social-pop`, `odin-social-healthoutcome`, `odin-social-healthfacility`, `odin-social-educoutcome`, `odin-social-educfacility`, `odin-social-poverty`, `odin-social-gender`, `odin-social-crime`, `odin-social-food`, `odin-social-reprod`
- Economic and financial data coverage — `odin-econ-nataccs`, `odin-econ-govfin`, `odin-econ-prices`, `odin-econ-labor`, `odin-econ-trade`, `odin-econ-balpay`, `odin-econ-bank`, `odin-econ-digital`
- Environmental data coverage — `odin-environ-agric`, `odin-environ-energy`, `odin-environ-pollution`, `odin-environ-resource`, `odin-environ-builtenv`
- Whether there is a right to ask for what is not published — `govtech-rti-37`, `govtech-rti-37.4`, `reg-id-rti`, `iiag-account-accpubrec`, `iiag-account-discpubrec`
- Whether the systems themselves are transparent — `govtech-datagov-34.7`, `exchange-uptake-transparency`
- Who governs data as an asset — `govtech-datagov-34`, `govtech-datagov-34.5`

### `data.satellite` — Use of satellite data

**No indicator in the DPI dataset addresses this slug.** The nearest existing evidence is the openness of the underlying domains — `odin-environ-agric`, `odin-environ-builtenv`, `odin-environ-resource` — and whether the cadastre is separate from the land register, `reg-land-cadastral`. All eight bullets below are proposed.

*Is Earth observation used, and by whom?*

- Whether there is a national space or geospatial agency — `[PROPOSED] sat-agency`
- Whether there is a ground station or receiving facility — `[PROPOSED] sat-groundstation`
- Whether there is a space or geospatial data policy — `[PROPOSED] sat-policy`
- Whether imagery is used in the land register and cadastre — `[PROPOSED] sat-landuse`, `reg-land-cadastral`
- Whether it is used in agricultural monitoring and statistics — `[PROPOSED] sat-agriculture`, `odin-environ-agric`
- Whether it is used in disaster and climate monitoring — `[PROPOSED] sat-disaster`
- Whether the country participates in regional EO programmes — `[PROPOSED] sat-regional`
- Whether national geospatial data is openly available — `[PROPOSED] sat-opengeo`, `odin-environ-builtenv`

---

## Finance

`finance.new` and `finance.mou` are the two slugs where the wiki is strong and the dataset holds nothing. The OSINT base carries deals and agreements as first-class entities with dated values in the announcing party's own currency, and the hubs carry a compiled `## Financing` block. The proposed indicators below are the summary figures a status report needs, derived from that material rather than collected separately. **`finance.sustain` is the one Finance sub-section answered from Corpus's own data** — the budget extract — rather than from the dataset or the wiki, and cites no DPI variable by design.

### `finance.new` — New investments

*Who is putting money into this country's digital estate, and how much?*

- Total value committed in the reporting window — `[PROPOSED] fin-new-value`
- How many distinct commitments that is — `[PROPOSED] fin-new-count`
- Where the money comes from — `[PROPOSED] fin-new-source`
- On what terms — `[PROPOSED] fin-new-instrument`
- What it is for — `[PROPOSED] fin-new-target`
- Whether committed money has actually been disbursed — `[PROPOSED] fin-new-disbursed`
- The single largest active commitment — `[PROPOSED] fin-new-largest`

### `finance.mou` — MoUs and other agreements

*What has been signed, with whom, and does any of it bind?*

- How many digital cooperation agreements are in force — `[PROPOSED] fin-mou-count`
- Who the principal counterparties are — `[PROPOSED] fin-mou-partners`
- Whether they carry binding commitments or stated values — `[PROPOSED] fin-mou-binding`
- Whether the text is published — `[PROPOSED] fin-mou-published`
- Standing agreements with named technology vendors — `[PROPOSED] fin-mou-vendor`
- Regional and bloc-level agreements the country is party to — `[PROPOSED] fin-mou-regional`, `[PROPOSED] geopol-regional-membership`
- Whether public-private collaboration is a stated mechanism — `govtech-publicinnov-47.5`

### `finance.budget` — Domestic budget appropriations and expenditure

**Suspended.** `STATUS-INIT` does not write this sub-section. The mapping below is kept intact and unsuspends when budget work resumes.

*Does the country pay for any of this itself?*

- Whether there is an IFMIS and what it does — `govtech-financial-5`, `govtech-financial-5.6`, `govtech-financial-5.7`, `govtech-financial-5.8`
- Whether spending can be classified and tracked to programme — `govtech-financial-5.10`, `govtech-financial-5.12`
- Whether there is a functioning treasury single account — `govtech-treasury-6`, `govtech-treasury-6.5`, `govtech-treasury-6.6`, `govtech-treasury-6.7`
- Whether debt and investment are managed on a system — `govtech-debt-13`, `govtech-debt-14`, `govtech-debt-14.6`
- The quality of budget and revenue management overall — `iiag-pubadmin-budgmgmt`, `iiag-pubadmin-taxrevmob`
- Whether government finance data is published — `odin-econ-govfin`
- Whether the wage bill runs on a system — `govtech-payroll-10`, `govtech-payroll-10.6`
- What share of the national budget is appropriated to digital — `[PROPOSED] fin-budget-ictshare`
- What share of that appropriation is actually executed — `[PROPOSED] fin-budget-execution`

### `finance.sustain` — Financial sustainability

*Is the digital state paying for itself — are the systems in service funded from the state's own resources, and is the money voted actually spent?*

- What share of the digital lines in the state's own budget document the state finances itself — answered from `budgets/{ISO3}/{FY}.csv` and `external.csv` (`python scripts/budget_source.py --share`); no variable
- Whether the lines that keep systems running — maintenance, licences, subscriptions, connectivity — are domestically financed — answered from the budget extract's economic classification, where the document prints one; no variable
- Whether what is voted is spent — execution against the voted figure, where an outturn is held — answered from the budget extract's stage history; no variable
- Whether own-source revenue or a levy finances digital programmes in law — answered from the finance law's articles as the budget extract reads them; `finance.budget` asks the same of the mechanism
- What the state is doing to get there — costed strategies with or without a line, plans to bring externally built systems onto the recurrent budget, reprioritisation visible across the years held — answered from the budget extract and the wiki; no variable
- Whether private-sector partnerships carry any of it on terms that last — the state's obligation and the revenue model stated — answered from the wiki; `finance.new` carries the announcements

Where a country's `budgets/` folder holds only migrated rows, the section says the budget has not yet been read, dated — which is true, and is the extraction queue.

The drafting brief — what the section says, what it reads, what *Not established* looks like — is `status-brief-finance-sustain.md`.
