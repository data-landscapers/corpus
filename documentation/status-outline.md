---
type: spec
reader: cc
---

# Country status outline

The drafting outline for the country status output. Each `###` sub-section is a taxonomy Level-2 slug (`lookups/taxonomy.md`); its question is **what is the current status of this, in this country, as at this date**, and its bullets are what must be established to answer it. **Under each sub-section its maturity indicators are listed in `Indicator Sort` order** (`lookups/indicators.csv`), the order the report follows (R150), and under each indicator the bullets that answer it. A bullet that answers none is under *Also in this sub-section*. A sub-section with no assessed indicator keeps its bullets and takes no absence line (R151).

Each bullet carries the ids that answer it, from `prep/status-indicators-africa-dpi.csv`; they join to `prep/africa-dpi-data.csv` (value, year, comment, sources, 54 countries) on `Variable Id`, and every id cited is in both. **An id may appear under more than one sub-section**: the mapping is a set of answers to questions, not a filing system.

**`[PROPOSED]` marks an indicator that does not yet exist**, and nothing in the dataset answers it; definitions are in `status-outline-proposed.md`. The five `geopol.*` actor slugs and `data.satellite` hold no dataset indicator; `finance.new`, `finance.mou`, `capacity.research`, `digital.localgov` and `tech.industry` hold very little. `geopol.sovereignty` holds one direct variable and some proxies and is otherwise answered from the wiki; `finance.sustain` is answered from Corpus's budget extract by design. A bullet answered mainly from the wiki says so.

**40 sub-sections are mapped; 39 are written**: `finance.budget` is suspended pending budget work. `geopol.sovereignty` and `finance.sustain` carry the maturity assessment's two indicators (`adding-an-indicator.md` §6), so both ask the same question of the same subject.

**394 of the 453 indicators are used, across 586 citations** *(2026-09-24, all parts, suspended section included)*. The 59 unused are mostly Ibrahim Index general-governance measures (corruption, security, environment, clinical health, electoral pluralism, women's representation), only remotely about digital governance, and GovTech Maturity Index *governance* and *transparency* sub-variables duplicating a bullet in the same sub-section. They are available if a section proves thin.

---

## ICT Infrastructure

### `infra.connect` — Connectivity

*How connected is the population, and on what terms?*

- **Mobile penetration**
  - How many people actually use it, and on what device — `ict-connectivity-internetuse`, `ict-connectivity-mobilepen`, `ict-connectivity-smartphonepen`
- **Internet usage** — as above: how many people actually use it, and on what device
- **Mobile affordability**
  - Whether people can afford to — `ict-connectivity-dataafford`
- **National fibre backbone** — wiki only
- **International internet bandwidth**
  - Backbone capacity and whether traffic stays local — `ict-connectivity-intlbandwidth`, `ict-connectivity-ixp`
- **Internet Exchange Points** — as above: backbone capacity and whether traffic stays local
- **Satellite broadband licensing and availability** — wiki only
- *Also in this sub-section*
  - How far the network physically reaches — `ict-connectivity-4gcoverage`
  - Independent read on infrastructure and mobile communications — `iiag-infrastructure-digacc`, `iiag-infrastructure-mobcomm`, `iiag-infrastructure-satinfr`
  - The regulatory framework the sector runs under — `reg-connect-telecomlaw`, `reg-connect-spectrum`, `reg-connect-sharing`
  - State commitments, and the mechanism to fund them — `reg-connect-broadband`, `reg-connect-ua`
  - Whether the sector publishes its own data — `odin-econ-digital`

### `infra.store` — Data Storage

*Where does the country's data physically sit, and who controls it?*

- **Local data centre capacity (all providers)**
  - Commercial hosting capacity in country — `ict-storage-dcpresence`, `ict-storage-cloudadoption`
- **Local data centre capacity (national providers)**
  - Whether government has its own platform, and whether shared — `ict-storage-govcloud`, `govtech-cloud-1`, `govtech-cloud-1.8`
  - What that platform is and what it provides — `govtech-cloud-1.4`, `govtech-cloud-1.7`
- **Off-site backup capacity** — wiki only
- *Also in this sub-section*
  - The rules on where data may be hosted — `govtech-cloud-1.6`, `ict-storage-datalocalisation`, `reg-cyber-cloud`, `reg-egov-cloudpolicy`
  - Whether the hosting arrangements are disclosed — `govtech-cloud-1.9`
  - The power the estate depends on — `ict-energy-elecaccess`, `ict-energy-reliability`

### `infra.energy` — Energy

*Can the grid carry a digital economy?*

- **Sufficient energy and water for data centres** — wiki only
- **Grid reliability**
  - Whether supply is reliable enough to run systems — `ict-energy-reliability`
- **Rural electrification**
  - Who has electricity at all, and where the gap falls — `ict-energy-elecaccess`, `ict-energy-urbanruraldevide`, `iiag-infrastructure-accenergy`
  - Whether policy enables off-grid and distributed supply — `ict-energy-offgridpolicy`
- *Also in this sub-section*
  - Whether power is affordable — `ict-energy-affordability`
  - What the generation mix is — `ict-energy-renewableshare`
  - Whether the sector's own data is open — `odin-environ-energy`

### `infra.capacity` — Technical Capacity

*Does the country have the people to build and run its own systems?*

- **Robustness of government hardware and software**
  - Government's measured readiness to run digital services — `ict-capacity-egovreadiness`
- **Local capacity to maintain, manage and develop government systems**
  - The tertiary pipeline feeding the sector — `ict-capacity-tertiaryict`
  - The depth of the working developer community — `ict-capacity-devcommunity`
  - Any public-service skills programme, and what it covers — `govtech-skills-45`, `govtech-skills-45.5`, `govtech-skills-45.4`
- *Also in this sub-section*
  - The literacy floor — `ict-capacity-digitalliteracy`
  - Who is excluded from that base — `ict-capacity-gendergap`
  - Whether the administration functions well enough to absorb it — `iiag-pubadmin-effadmin`

### `infra.cybersec` — Cybersecurity

*Is the state able to defend and govern its digital estate?*

- **National cybersecurity readiness**
  - Measured national readiness — `ict-storage-cybersecurity`
  - Whether there is a strategy — `reg-cyber-strategy`
  - Whether there is binding law — `reg-cyber-cyberlaw`
  - Whether critical information infrastructure is designated and protected — `reg-cyber-ciip`
- *Also in this sub-section*
  - Whether the ID system has been independently security-reviewed — `id-uptake-securityreview`
  - Whether payment-system breaches must be notified — `pay-governance-databreachnotif`
  - Whether hardware lifecycle and e-waste are regulated — `reg-cyber-ewaste`

---

## DPI

### `dpi.exchange` — Data Exchange

*Is there a working exchange layer, and what actually flows across it?*

- **National data exchange system**
  - Whether a system exists and is operational — `exchange-system-operational`, `exchange-system-ai`
  - The legal and strategic basis it rests on — `exchange-gov-legislation-exists`, `exchange-gov-strategy`, `exchange-gov-roadmap`
  - Whether an interoperability framework exists, and its stage — `govtech-interop-3`, `govtech-interop-3.4`, `reg-id-interop`
  - Whether it is run to an operational standard — `govtech-interop-3.6`, `govtech-interop-3.7`, `govtech-interop-3.8`
- **Use of digital id in other systems**
  - Which foundational systems are connected — `exchange-func-digitalid`, `exchange-func-crvs`, `exchange-func-payments`, `exchange-func-revenue`, `exchange-func-socialprotection`
- **Interoperability of health systems**
  - Which sectoral systems are connected — `exchange-func-health`, `exchange-func-education`, `exchange-func-justice`, `exchange-func-business`, `exchange-func-agriculture`, `exchange-func-employment`, `exchange-func-passport`, `exchange-func-licensing`, `exchange-func-electoral`, `exchange-func-planning`
- **Interoperability of education systems** — as above: which sectoral systems are connected
- **Interoperability of social protection systems** — as above: which sectoral systems are connected
- *Also in this sub-section*
  - How far it reaches beyond the centre — `exchange-uptake-subnational`, `exchange-uptake-urbanrural`, `exchange-uptake-accessibility`
  - Whether its workings and its data-sovereignty terms are public — `exchange-uptake-transparency`, `exchange-uptake-sovereignty`, `govtech-interop-3.9`

### `dpi.id` — Digital Identity and CRVS

*Does a foundational identity exist, who is in it, and what does it unlock?*

- **Robustness of system**
  - Whether a system exists, and what it is technically — `id-system-didexists`, `id-system-dbelectronic`, `id-system-biocollect`, `id-system-sysinterop`
- **Registration of entire population**
  - Population coverage, and whether enrolment is compulsory — `id-uptake-popcoverage`, `id-uptake-enrollmandatory`, `id-uptake-enrolleligible`
  - Who is eligible and what it costs them — `id-uptake-nonnateligible`, `id-uptake-cost`
- **National maintenance of id and credentials systems**
  - Who owns it and whether it is sustainable — `id-ownership-maintenance`, `id-ownership-sustainability`, `id-ownership-oversight`
- **Authentication**
  - What the credential technically does — `id-functionality-authdigital`, `id-functionality-authgovtportal`, `id-functionality-kycenable`, `id-functionality-dataview`
- **Digital id from birth**
  - Whether civil registration underpins it, and how completely — `id-governance-crvs`, `reg-cr-exists`, `reg-cr-uptake`, `reg-cr-inclusive`, `iiag-pubadmin-civreg`
- **Interoperability of birth registration and digital id** — as above: whether civil registration underpins it, and how completely
- **Use by other systems**
  - What holding it lets a person do — `id-uptake-bankuse`, `id-uptake-healthuse`, `id-uptake-socialservicesuse`, `id-uptake-simreguse`
- *Also in this sub-section*
  - The legal basis, and the safeguards attached to it — `id-governance-legframework`, `id-governance-legalproof`, `id-governance-digidreg`, `reg-id-didlaw`, `id-governance-dpaexists`, `id-governance-dpaoversight`, `id-governance-datasharingrules`, `id-governance-courtoversight`
  - Whether it is recognised outside the country — `id-uptake-crossborder`

### `dpi.pay` — Digital Payments and Fintech

*Can money move digitally, for whom, and under what rules?*

- **Governance role of central bank**
  - Who governs the scheme and whether its rules are public — `pay-governance-cbgovernance`, `pay-governance-schemerulesavail`
- **G2P functionality**
  - Whether government itself pays and collects digitally — `pay-uptake-govtadoption`, `pay-functionality-revenue`, `pay-functionality-taxportal`
- **Revenue collection** — as above: whether government itself pays and collects digitally
- **B2B and B2G functionality**
  - Which flows it supports — `pay-functionality-usecasep2p`, `pay-functionality-usecasep2b`, `pay-functionality-usecaseb2b`, `pay-functionality-usecaseg2p`, `pay-functionality-usecasep2g`, `pay-functionality-usecasecrossborder`
- **P2P, P2G and P2B functionality** — as above: which flows it supports
- **Population uptake**
  - Whether a system exists and how many people use it — `pay-system-dpayexists`, `pay-uptake-activeusers`, `iiag-business-accbankserv`
- **Cross-border functionality** — as above: which flows it supports
- **Consumer protection**
  - What protects the user — `pay-governance-consumerprotectlaw`, `pay-governance-dataprivacylaw`, `pay-governance-databreachnotif`
- *Also in this sub-section*
  - The legal and regulatory framework — `reg-fintech-paylaw`, `reg-fintech-paystrat`, `reg-fintech-openbanking`, `reg-fintech-ecomlaw`, `reg-fintech-sandbox`
  - Who is designed in, and who is not — `pay-governance-propoorgovernance`, `pay-uptake-disabilityaccess`, `pay-uptake-refugeemigrantaccess`
  - Whether performance is audited and reported — `pay-uptake-auditsandreviews`, `pay-governance-performancereporting`

### `dpi.registry` — Registries

*Which registers exist, how complete are they, and are they joined up?*

- **Population register**
  - The population register — `reg-pop-exists`, `reg-pop-uptake`, `reg-pop-inclusive`
- **Civil register**
  - Civil registration — `reg-cr-exists`, `reg-cr-scope`, `reg-cr-uptake`, `reg-cr-inclusive`
- **Address register**
  - Land and address — `reg-land-exists`, `reg-land-uptake`, `reg-land-cadastral`, `reg-address-exists`, `reg-address-house`, `reg-address-business`
- **Business register**
  - The economic registers — `reg-business-exists`, `reg-business-uptake`, `reg-tax-exists`, `reg-tax-scope`, `reg-tax-incomeuptake`, `reg-tax-businessuptake`
- **Social protection register**
  - Electoral and social protection — `reg-elect-exists`, `reg-elect-uptake`, `reg-social-exists`, `reg-social-uptake`
- **Electoral register** — as above: electoral and social protection
- **Tax register** — as above: the economic registers
- **Land register** — as above: land and address
- *Also in this sub-section*
  - Whether each is tied to the national ID — `reg-pop-id`, `reg-cr-id`, `reg-elect-id`, `reg-social-id`, `reg-tax-id`
  - Whether each reaches the exchange layer — `reg-pop-dpi`, `reg-cr-dpi`, `reg-land-dpi`, `reg-address-dpi`, `reg-business-dpi`, `reg-elect-dpi`, `reg-social-dpi`, `reg-tax-dpi`
  - Whether the registers talk directly to each other — `reg-pop-crvs`, `reg-cr-pop`, `reg-land-address`, `reg-land-business`, `reg-business-address`, `reg-business-land`, `reg-address-land`, `reg-tax-business`

### `dpi.mis` — Sectoral management information systems

*Do the line ministries run real systems, and do those systems talk to anything?*

- **Health**
  - Health and education systems, and whether they reach the exchange — `exchange-func-health`, `exchange-func-education`
- **Education** — as above: health and education systems, and whether they reach the exchange
- **Social protection**
  - Social insurance: whether it exists, its status and platform — `govtech-socialinsure-11`, `govtech-socialinsure-11.7`, `govtech-socialinsure-11.8`
  - Social protection delivery and its register — `reg-social-exists`, `reg-social-uptake`, `exchange-func-socialprotection`
- **Justice**
  - Justice, employment and immigration — `exchange-func-justice`, `exchange-func-employment`, `exchange-func-passport`, `exchange-func-licensing`
- **Tax**
  - Revenue-side systems — `govtech-customs-8`, `govtech-customs-8.6`, `govtech-taxmanage-7`, `govtech-taxmanage-7.6`
- **Customs** — as above: revenue-side systems
- **Land** — wiki only
- *Also in this sub-section*
  - Public-service HR and payroll — `govtech-hr-9`, `govtech-hr-9.4`, `govtech-hr-9.6`, `govtech-payroll-10`, `govtech-payroll-10.4`
  - Whether they use the national ID rather than their own identifiers — `govtech-hr-9.8`, `govtech-socialinsure-11.1`
  - Whether they interoperate or stand alone — `govtech-socialinsure-11.9`, `govtech-customs-8.8`, `govtech-customs-8.7`, `govtech-taxmanage-7.7`, `govtech-hr-9.7`

### `dpi.govtech` — Other GovTech and e-Gov

*What can a citizen or a business actually do online with the state?*

- **e-government services**
  - The main service portal and what is on it — `govtech-serviceportal-19`, `govtech-serviceportal-19.3`, `govtech-serviceportal-19.4`, `govtech-serviceportal-19.5`, `govtech-serviceportal-19.6`
  - The sectoral portals — `govtech-taxportal-20`, `govtech-taxportal-20.2`, `govtech-taxportal-20.3`, `govtech-socialportal-24`, `govtech-socialportal-24.2`, `govtech-job-25`, `govtech-job-25.2`, `govtech-job-25.3`
- *Also in this sub-section*
  - Procurement done electronically — `govtech-procure-12`, `govtech-procure-12.4`, `govtech-procure-12.5`, `reg-egov-procurement`
  - The public financial management core — `govtech-financial-5`, `govtech-financial-5.6`, `govtech-treasury-6`, `govtech-debt-13`, `govtech-debt-14`
  - Who coordinates and audits all of this — `govtech-govtech-33`, `govtech-govtech-33.8`, `govtech-govtech-33.9`
  - Whether it is run as one government or many ministries — `govtech-digitransform-36`, `govtech-digitransform-36.3`
  - Measured readiness and the legal basis — `ict-capacity-egovreadiness`, `reg-egov-egovpol`, `reg-egov-strategy`
  - Whether any of it is transparent to its users — `govtech-govtech-33.1`, `govtech-serviceportal-19.7`, `govtech-procure-12.8`, `govtech-debt-14.7`, `govtech-digitransform-36.4`

---

## Inclusion

### `include.divides` — Digital divides

*Who is left out, and along which lines?*

- **Bridging of digital divides**
  - The urban-rural line — `exchange-uptake-urbanrural`, `ict-energy-urbanruraldevide`, `iiag-rural-rurreppart`
  - The gender line — `ict-capacity-gendergap`, `iiag-women-socioeconoppwom`, `iiag-women-accpubservwomvdem`
  - The affordability line — `ict-connectivity-dataafford`, `ict-energy-affordability`, `id-uptake-cost`
  - The gap between availability and use — `ict-connectivity-4gcoverage`, `ict-connectivity-internetuse`, `ict-connectivity-smartphonepen`
  - The literacy and skills floor — `ict-capacity-digitalliteracy`, `iiag-education-compeduc`
  - Who is missing from the registers — `id-uptake-popcoverage`, `reg-cr-inclusive`, `reg-pop-inclusive`
  - Non-nationals, refugees and migrants — `id-uptake-nonnateligible`, `pay-uptake-refugeemigrantaccess`
  - Disability — `pay-uptake-disabilityaccess`, `exchange-uptake-accessibility`, `iiag-inclusion-eqaccpubserv`

### `include.access` — Access to services

*Can people actually obtain the services the state provides?*

- **Citizen feedback portals** — wiki only
- **Citizen participation in policy** — wiki only
- **Gender equity** — wiki only
- **Inclusion of persons with disabilities** — wiki only
- **Inclusion of refugees and IDPs** — wiki only
- *Also in this sub-section*
  - Whether access to public services is equal — `iiag-inclusion-eqaccpubserv`, `iiag-inclusion-pubpercinceq`, `iiag-inclusion-eqsoceconopp`
  - How hard it is to get an identity document — `iiag-pubadmin-pubpercpubadmin`, `id-uptake-popcoverage`
  - Whether the service portal reaches ordinary users — `govtech-serviceportal-19`, `govtech-serviceportal-19.3`, `govtech-serviceportal-19.4`
  - Whether the sectoral portals do — `govtech-taxportal-20.5`, `govtech-socialportal-24.5`, `govtech-job-25.5`
  - What the ID gates — `id-uptake-bankuse`, `id-uptake-healthuse`, `id-uptake-socialservicesuse`
  - Whether social protection actually reaches people — `reg-social-uptake`, `iiag-social-socialsafnet`, `iiag-social-povredpol`
  - Health and education access — `iiag-health-acchealth`, `iiag-education-educenr`
  - Whether service points outside the capital are digitalised — `rural-clinic-status`, `rural-school-status`, `rural-police-status`, `rural-registry-status`

---

## Technology

### `tech.ai` — AI

*Is there an AI policy, and is anything actually running?*

- **Use of AI in government administration**
  - Whether AI appears in citizen-facing services — `govtech-feedback-31.4`
  - What is deployed in production in government — `[PROPOSED] tech-ai-deployment`
- **Use of AI in sectoral management information systems**
  - Whether the exchange layer has analytics or AI — `exchange-system-ai`
- **Development of national / regional AI systems** — wiki only
- **Control of AI abuse**
  - Whether there is binding regulation — `reg-ai-ailaw`
- *Also in this sub-section*
  - Whether there is a national strategy — `reg-ai-strategy`
  - Whether adjacent emerging technology is covered — `reg-ai-emerging`
  - The data it would run on — `stats-score-products`, `stats-score-sources`, `govtech-opendata-29`
  - The compute and hosting it would run on — `ict-storage-cloudadoption`, `ict-storage-dcpresence`
  - The skills base behind it — `ict-capacity-tertiaryict`, `ict-capacity-devcommunity`

### `tech.industry` — ICT Industry

*Is there a domestic technology sector, or only foreign vendors?*

- **National capacity in DT-related production**
  - The startup ecosystem — `ict-innovation-startupecosystem`
  - Hubs and physical infrastructure for the sector — `ict-innovation-techhubs`
  - The working developer base — `ict-capacity-devcommunity`
  - The business and competition environment — `iiag-business-buscompreg`, `iiag-business-econdiv`
  - How easy it is to register a company — `govtech-serviceportal-19.5`, `reg-business-exists`, `reg-business-uptake`
  - Employment the sector generates — `iiag-business-secemplopp`, `odin-econ-labor`
  - The structure of the telecommunications market — `[PROPOSED] tech-industry-mnomarket`
  - The size of the domestic software and services industry — `[PROPOSED] tech-industry-softwaresize`
  - Share of government technology spend going to domestic suppliers — `[PROPOSED] tech-industry-localsupply`

### `tech.innovate` — Innovation ecosystem

*Does the system produce and absorb new things?*

- **Technology hubs** — wiki only
- **Tech startup ecosystem**
  - Whether there is a startup or innovation law — `reg-ai-startuplaw`, `govtech-startup-48`
  - Whether financing and SME support exist — `govtech-startup-48.4`, `govtech-startup-48.6`, `govtech-startup-48.5`
  - Whether regulation makes room to experiment — `reg-fintech-sandbox`
- *Also in this sub-section*
  - Where it ranks on innovation overall — `ict-innovation-gii`
  - Whether a science and technology policy backs it — `reg-ai-innov`
  - Whether the public sector innovates — `govtech-publicinnov-46`, `govtech-publicinnov-47`, `govtech-publicinnov-46.4`, `govtech-publicinnov-47.4`
  - Whether the public and private sectors work together — `govtech-publicinnov-47.5`
  - Whether open source is a route in — `govtech-opensource-17`, `govtech-opensource-15.4`

---

Governance is in [`status-outline-part-3.md`](status-outline-part-3.md), and the last five chapters — Geopolitics, Capacity, Digitalisation, Data and Finance — are in [`status-outline-part-2.md`](status-outline-part-2.md); `status_lib.outline()` reads all three.
