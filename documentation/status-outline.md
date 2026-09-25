---
type: spec
reader: cc
---

# Country status outline

The drafting outline for the country status output. Each `###` sub-section is a taxonomy Level-2 slug (`lookups/taxonomy.md`); its question is **what is the current status of this, in this country, as at this date**, and its bullets are what must be established to answer it.

Each bullet carries the ids that answer it, from `prep/status-indicators-africa-dpi.csv`; they join to `prep/africa-dpi-data.csv` (value, year, comment, sources, 54 countries) on `Variable Id`, and every id cited is in both. **An id may appear under more than one sub-section**: the mapping is a set of answers to questions, not a filing system.

**`[PROPOSED]` marks an indicator that does not yet exist**, and nothing in the dataset answers it; definitions are in `status-outline-proposed.md`. The five `geopol.*` actor slugs and `data.satellite` hold no dataset indicator; `finance.new`, `finance.mou`, `capacity.research`, `digital.localgov` and `tech.industry` hold very little. `geopol.sovereignty` holds one direct variable and some proxies and is otherwise answered from the wiki; `finance.sustain` is answered from Corpus's budget extract by design. A bullet answered mainly from the wiki says so.

**40 sub-sections are mapped; 39 are written**: `finance.budget` is suspended pending budget work. `geopol.sovereignty` and `finance.sustain` carry the maturity assessment's two indicators (`adding-an-indicator.md` §6), so both ask the same question of the same subject.

**394 of the 453 indicators are used, across 586 citations** *(2026-09-24, both files, suspended section included)*. The 59 unused are mostly Ibrahim Index general-governance measures (corruption, security, environment, clinical health, electoral pluralism, women's representation), only remotely about digital governance, and GovTech Maturity Index *governance* and *transparency* sub-variables duplicating a bullet in the same sub-section. They are available if a section proves thin.

---

## ICT Infrastructure

### `infra.connect` — Connectivity

*How connected is the population, and on what terms?*

- How far the network physically reaches — `ict-connectivity-4gcoverage`
- How many people actually use it, and on what device — `ict-connectivity-internetuse`, `ict-connectivity-mobilepen`, `ict-connectivity-smartphonepen`
- Whether people can afford to — `ict-connectivity-dataafford`
- Backbone capacity and whether traffic stays local — `ict-connectivity-intlbandwidth`, `ict-connectivity-ixp`
- Independent read on infrastructure and mobile communications — `iiag-infrastructure-digacc`, `iiag-infrastructure-mobcomm`, `iiag-infrastructure-satinfr`
- The regulatory framework the sector runs under — `reg-connect-telecomlaw`, `reg-connect-spectrum`, `reg-connect-sharing`
- State commitments, and the mechanism to fund them — `reg-connect-broadband`, `reg-connect-ua`
- Whether the sector publishes its own data — `odin-econ-digital`

### `infra.store` — Data Storage

*Where does the country's data physically sit, and who controls it?*

- Commercial hosting capacity in country — `ict-storage-dcpresence`, `ict-storage-cloudadoption`
- Whether government has its own platform, and whether shared — `ict-storage-govcloud`, `govtech-cloud-1`, `govtech-cloud-1.8`
- What that platform is and what it provides — `govtech-cloud-1.4`, `govtech-cloud-1.7`
- The rules on where data may be hosted — `govtech-cloud-1.6`, `ict-storage-datalocalisation`, `reg-cyber-cloud`, `reg-egov-cloudpolicy`
- Whether the hosting arrangements are disclosed — `govtech-cloud-1.9`
- The power the estate depends on — `ict-energy-elecaccess`, `ict-energy-reliability`

### `infra.energy` — Energy

*Can the grid carry a digital economy?*

- Who has electricity at all, and where the gap falls — `ict-energy-elecaccess`, `ict-energy-urbanruraldevide`, `iiag-infrastructure-accenergy`
- Whether supply is reliable enough to run systems — `ict-energy-reliability`
- Whether power is affordable — `ict-energy-affordability`
- What the generation mix is — `ict-energy-renewableshare`
- Whether policy enables off-grid and distributed supply — `ict-energy-offgridpolicy`
- Whether the sector's own data is open — `odin-environ-energy`

### `infra.capacity` — Technical Capacity

*Does the country have the people to build and run its own systems?*

- The literacy floor — `ict-capacity-digitalliteracy`
- The tertiary pipeline feeding the sector — `ict-capacity-tertiaryict`
- The depth of the working developer community — `ict-capacity-devcommunity`
- Who is excluded from that base — `ict-capacity-gendergap`
- Government's measured readiness to run digital services — `ict-capacity-egovreadiness`
- Any public-service skills programme, and what it covers — `govtech-skills-45`, `govtech-skills-45.5`, `govtech-skills-45.4`
- Whether the administration functions well enough to absorb it — `iiag-pubadmin-effadmin`

### `infra.cybersec` — Cybersecurity

*Is the state able to defend and govern its digital estate?*

- Measured national readiness — `ict-storage-cybersecurity`
- Whether there is a strategy — `reg-cyber-strategy`
- Whether there is binding law — `reg-cyber-cyberlaw`
- Whether critical information infrastructure is designated and protected — `reg-cyber-ciip`
- Whether the ID system has been independently security-reviewed — `id-uptake-securityreview`
- Whether payment-system breaches must be notified — `pay-governance-databreachnotif`
- Whether hardware lifecycle and e-waste are regulated — `reg-cyber-ewaste`

---

## DPI

### `dpi.exchange` — Data Exchange

*Is there a working exchange layer, and what actually flows across it?*

- Whether a system exists and is operational — `exchange-system-operational`, `exchange-system-ai`
- The legal and strategic basis it rests on — `exchange-gov-legislation-exists`, `exchange-gov-strategy`, `exchange-gov-roadmap`
- Whether an interoperability framework exists, and its stage — `govtech-interop-3`, `govtech-interop-3.4`, `reg-id-interop`
- Which foundational systems are connected — `exchange-func-digitalid`, `exchange-func-crvs`, `exchange-func-payments`, `exchange-func-revenue`, `exchange-func-socialprotection`
- Which sectoral systems are connected — `exchange-func-health`, `exchange-func-education`, `exchange-func-justice`, `exchange-func-business`, `exchange-func-agriculture`, `exchange-func-employment`, `exchange-func-passport`, `exchange-func-licensing`, `exchange-func-electoral`, `exchange-func-planning`
- Whether it is run to an operational standard — `govtech-interop-3.6`, `govtech-interop-3.7`, `govtech-interop-3.8`
- How far it reaches beyond the centre — `exchange-uptake-subnational`, `exchange-uptake-urbanrural`, `exchange-uptake-accessibility`
- Whether its workings and its data-sovereignty terms are public — `exchange-uptake-transparency`, `exchange-uptake-sovereignty`, `govtech-interop-3.9`

### `dpi.id` — Digital Identity and CRVS

*Does a foundational identity exist, who is in it, and what does it unlock?*

- Whether a system exists, and what it is technically — `id-system-didexists`, `id-system-dbelectronic`, `id-system-biocollect`, `id-system-sysinterop`
- Population coverage, and whether enrolment is compulsory — `id-uptake-popcoverage`, `id-uptake-enrollmandatory`, `id-uptake-enrolleligible`
- Who is eligible and what it costs them — `id-uptake-nonnateligible`, `id-uptake-cost`
- The legal basis, and the safeguards attached to it — `id-governance-legframework`, `id-governance-legalproof`, `id-governance-digidreg`, `reg-id-didlaw`, `id-governance-dpaexists`, `id-governance-dpaoversight`, `id-governance-datasharingrules`, `id-governance-courtoversight`
- What holding it lets a person do — `id-uptake-bankuse`, `id-uptake-healthuse`, `id-uptake-socialservicesuse`, `id-uptake-simreguse`
- What the credential technically does — `id-functionality-authdigital`, `id-functionality-authgovtportal`, `id-functionality-kycenable`, `id-functionality-dataview`
- Whether civil registration underpins it, and how completely — `id-governance-crvs`, `reg-cr-exists`, `reg-cr-uptake`, `reg-cr-inclusive`, `iiag-pubadmin-civreg`
- Who owns it and whether it is sustainable — `id-ownership-maintenance`, `id-ownership-sustainability`, `id-ownership-oversight`
- Whether it is recognised outside the country — `id-uptake-crossborder`

### `dpi.pay` — Digital Payments and Fintech

*Can money move digitally, for whom, and under what rules?*

- Whether a system exists and how many people use it — `pay-system-dpayexists`, `pay-uptake-activeusers`, `iiag-business-accbankserv`
- Which flows it supports — `pay-functionality-usecasep2p`, `pay-functionality-usecasep2b`, `pay-functionality-usecaseb2b`, `pay-functionality-usecaseg2p`, `pay-functionality-usecasep2g`, `pay-functionality-usecasecrossborder`
- Whether government itself pays and collects digitally — `pay-uptake-govtadoption`, `pay-functionality-revenue`, `pay-functionality-taxportal`
- The legal and regulatory framework — `reg-fintech-paylaw`, `reg-fintech-paystrat`, `reg-fintech-openbanking`, `reg-fintech-ecomlaw`, `reg-fintech-sandbox`
- Who governs the scheme and whether its rules are public — `pay-governance-cbgovernance`, `pay-governance-schemerulesavail`
- What protects the user — `pay-governance-consumerprotectlaw`, `pay-governance-dataprivacylaw`, `pay-governance-databreachnotif`
- Who is designed in, and who is not — `pay-governance-propoorgovernance`, `pay-uptake-disabilityaccess`, `pay-uptake-refugeemigrantaccess`
- Whether performance is audited and reported — `pay-uptake-auditsandreviews`, `pay-governance-performancereporting`

### `dpi.registry` — Registries

*Which registers exist, how complete are they, and are they joined up?*

- The population register — `reg-pop-exists`, `reg-pop-uptake`, `reg-pop-inclusive`
- Civil registration — `reg-cr-exists`, `reg-cr-scope`, `reg-cr-uptake`, `reg-cr-inclusive`
- Land and address — `reg-land-exists`, `reg-land-uptake`, `reg-land-cadastral`, `reg-address-exists`, `reg-address-house`, `reg-address-business`
- The economic registers — `reg-business-exists`, `reg-business-uptake`, `reg-tax-exists`, `reg-tax-scope`, `reg-tax-incomeuptake`, `reg-tax-businessuptake`
- Electoral and social protection — `reg-elect-exists`, `reg-elect-uptake`, `reg-social-exists`, `reg-social-uptake`
- Whether each is tied to the national ID — `reg-pop-id`, `reg-cr-id`, `reg-elect-id`, `reg-social-id`, `reg-tax-id`
- Whether each reaches the exchange layer — `reg-pop-dpi`, `reg-cr-dpi`, `reg-land-dpi`, `reg-address-dpi`, `reg-business-dpi`, `reg-elect-dpi`, `reg-social-dpi`, `reg-tax-dpi`
- Whether the registers talk directly to each other — `reg-pop-crvs`, `reg-cr-pop`, `reg-land-address`, `reg-land-business`, `reg-business-address`, `reg-business-land`, `reg-address-land`, `reg-tax-business`

### `dpi.mis` — Sectoral management information systems

*Do the line ministries run real systems, and do those systems talk to anything?*

- Health and education systems, and whether they reach the exchange — `exchange-func-health`, `exchange-func-education`
- Social insurance: whether it exists, its status and platform — `govtech-socialinsure-11`, `govtech-socialinsure-11.7`, `govtech-socialinsure-11.8`
- Social protection delivery and its register — `reg-social-exists`, `reg-social-uptake`, `exchange-func-socialprotection`
- Public-service HR and payroll — `govtech-hr-9`, `govtech-hr-9.4`, `govtech-hr-9.6`, `govtech-payroll-10`, `govtech-payroll-10.4`
- Revenue-side systems — `govtech-customs-8`, `govtech-customs-8.6`, `govtech-taxmanage-7`, `govtech-taxmanage-7.6`
- Justice, employment and immigration — `exchange-func-justice`, `exchange-func-employment`, `exchange-func-passport`, `exchange-func-licensing`
- Whether they use the national ID rather than their own identifiers — `govtech-hr-9.8`, `govtech-socialinsure-11.1`
- Whether they interoperate or stand alone — `govtech-socialinsure-11.9`, `govtech-customs-8.8`, `govtech-customs-8.7`, `govtech-taxmanage-7.7`, `govtech-hr-9.7`

### `dpi.govtech` — Other GovTech and e-Gov

*What can a citizen or a business actually do online with the state?*

- The main service portal and what is on it — `govtech-serviceportal-19`, `govtech-serviceportal-19.3`, `govtech-serviceportal-19.4`, `govtech-serviceportal-19.5`, `govtech-serviceportal-19.6`
- The sectoral portals — `govtech-taxportal-20`, `govtech-taxportal-20.2`, `govtech-taxportal-20.3`, `govtech-socialportal-24`, `govtech-socialportal-24.2`, `govtech-job-25`, `govtech-job-25.2`, `govtech-job-25.3`
- Procurement done electronically — `govtech-procure-12`, `govtech-procure-12.4`, `govtech-procure-12.5`, `reg-egov-procurement`
- The public financial management core — `govtech-financial-5`, `govtech-financial-5.6`, `govtech-treasury-6`, `govtech-debt-13`, `govtech-debt-14`
- Who coordinates and audits all of this — `govtech-govtech-33`, `govtech-govtech-33.8`, `govtech-govtech-33.9`
- Whether it is run as one government or many ministries — `govtech-digitransform-36`, `govtech-digitransform-36.3`
- Measured readiness and the legal basis — `ict-capacity-egovreadiness`, `reg-egov-egovpol`, `reg-egov-strategy`
- Whether any of it is transparent to its users — `govtech-govtech-33.1`, `govtech-serviceportal-19.7`, `govtech-procure-12.8`, `govtech-debt-14.7`, `govtech-digitransform-36.4`

---

## Governance

### `gov.legislate` — Legislation and regulation

*What binding law is on the books, and where are the holes?*

- Communications and spectrum — `reg-connect-telecomlaw`, `reg-connect-spectrum`, `reg-connect-sharing`
- Cyber, critical infrastructure and e-waste — `reg-cyber-cyberlaw`, `reg-cyber-ciip`, `reg-cyber-ewaste`
- Identity and electronic trust — `reg-id-didlaw`, `reg-id-esig`
- Data protection and access to information — `reg-id-dplaw`, `reg-id-rti`, `govtech-dataprotect-38`, `govtech-rti-37`
- Payments, e-commerce and open banking — `reg-fintech-paylaw`, `reg-fintech-ecomlaw`, `reg-fintech-openbanking`
- AI, emerging technology and startups — `reg-ai-ailaw`, `reg-ai-emerging`, `reg-ai-startuplaw`
- E-government and procurement — `reg-egov-egovpol`, `reg-egov-procurement`
- Whether law on the books is law in practice — `iiag-law-execcomprol`, `iiag-law-lawenf`, `iiag-law-pubpercrol`, `iiag-law-eqtreatlaw`

### `gov.policy` — Strategies, plans and policies

*What has the state committed to on paper, and who owns delivery?*

- The overarching digital strategy — `reg-egov-strategy`, `govtech-digitransform-35`
- Who leads it and through what machinery — `govtech-digitransform-36.2`, `govtech-digitransform-36.3`, `govtech-digitransform-36`
- The sector strategies — `reg-connect-broadband`, `reg-connect-ua`, `reg-fintech-paystrat`, `reg-cyber-strategy`, `reg-ai-strategy`
- Hosting and cloud policy — `reg-cyber-cloud`, `reg-egov-cloudpolicy`, `ict-storage-govcloud`
- Whether there is a data governance body and strategy — `govtech-datagov-34`, `govtech-datagov-34.4`, `govtech-datagov-34.6`
- Open data and open source commitments — `reg-egov-opendata`, `govtech-opensource-15`
- Skills and innovation commitments — `govtech-skills-45`, `govtech-publicinnov-46`, `reg-ai-innov`
- Whether the documents themselves are published — `govtech-digitransform-36.4`, `govtech-datagov-34.7`, `govtech-skills-45.7`

### `gov.regional` — Regional collaboration

*How far does the country's digital estate reach across its borders?*

- Whether the national ID is recognised regionally — `id-uptake-crossborder`
- Whether payments cross the border — `pay-functionality-usecasecrossborder`
- How integrated the economy is regionally — `iiag-business-reginteg`, `odin-econ-trade`
- What constrains cross-border data flow — `exchange-uptake-sovereignty`, `ict-storage-datalocalisation`
- Whether national standards align with regional frameworks — `reg-id-interop`, `govtech-interop-3`
- Whether AU and continental instruments are ratified and domesticated — `[PROPOSED] geopol-regional-instrument`
- Which regional digital bodies and programmes it is party to — `[PROPOSED] geopol-regional-membership`

### `gov.standards` — Standards

*Are systems built to shared, published standards, or one at a time?*

- Whether an interoperability framework exists and is in force — `govtech-interop-3`, `govtech-interop-3.4`, `reg-id-interop`
- Whether data quality and uptime are held to a standard — `govtech-interop-3.6`, `govtech-interop-3.7`
- Whether procurement enforces standards — `govtech-procure-12.5`, `govtech-procure-12.6`
- Open source: policy, adoption and who governs it — `govtech-opensource-15`, `govtech-opensource-15.4`, `govtech-opensource-15.3`
- Standardised financial classification — `govtech-financial-5.10`, `govtech-financial-5.13`
- Electronic signature and trust standards — `reg-id-esig`
- Whether legacy systems are being retired to standard — `govtech-interop-3.8`

### `gov.protect` — Data protection

*Is personal data protected in law, and is anyone enforcing it?*

- Whether legislation exists — `reg-id-dplaw`, `govtech-dataprotect-38`, `id-governance-dpaexists`, `ict-storage-dataprotection`
- Whether an authority exists and has real oversight — `govtech-dataprotect-39`, `id-governance-dpaoversight`
- Whether compliance is monitored — `govtech-dataprotect-38.4`
- Whether the regime and the regulator publish anything — `govtech-dataprotect-39.4`, `govtech-dataprotect-38.5`
- The rules governing sharing, and whether courts can review them — `id-governance-datasharingrules`, `id-governance-courtoversight`
- How payment data specifically is covered — `pay-governance-dataprivacylaw`, `pay-governance-databreachnotif`
- Localisation and sovereignty terms — `ict-storage-datalocalisation`, `exchange-uptake-sovereignty`
- The rights environment the regime sits in — `iiag-rights-digrights`, `iiag-rights-perslibert`, `iiag-rights-protagdiscrim`

### `gov.discourse` — Public debate and participation in policymaking

*Who gets a say in digital policy, and can they say it freely?*

- Whether participation platforms exist and what they do — `govtech-particip-30`, `govtech-particip-30.3`, `govtech-particip-30.2`
- Whether feedback reaches government, and whether it answers — `govtech-feedback-31`, `govtech-feedback-31.6`, `govtech-feedback-31.2`
- Whether those channels are inclusive and safe — `govtech-feedback-31.3`, `govtech-feedback-31.5`, `govtech-particip-30.4`, `govtech-particip-30.5`
- The wider space for deliberation and civil society — `iiag-participate-delibpartgov`, `iiag-participate-civsocspace`, `iiag-participate-freeassocass`
- Whether media and expression are free — `iiag-rights-mediafree`, `iiag-rights-freeexpbelief`, `iiag-rights-pubfreespafr`
- Digital freedom specifically — `iiag-rights-digrights`
- Whether the public can obtain the records to argue with — `govtech-rti-37`, `govtech-rti-37.3`, `iiag-account-accpubrec`, `iiag-account-discpubrec`
- Whether citizens are involved in designing the services — `govtech-serviceportal-19.2`, `govtech-taxportal-20.4`, `govtech-socialportal-24.3`, `govtech-job-25.4`

---

## Inclusion

### `include.divides` — Digital divides

*Who is left out, and along which lines?*

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

- Whether there is a national strategy — `reg-ai-strategy`
- Whether there is binding regulation — `reg-ai-ailaw`
- Whether adjacent emerging technology is covered — `reg-ai-emerging`
- Whether the exchange layer has analytics or AI — `exchange-system-ai`
- Whether AI appears in citizen-facing services — `govtech-feedback-31.4`
- The data it would run on — `stats-score-products`, `stats-score-sources`, `govtech-opendata-29`
- The compute and hosting it would run on — `ict-storage-cloudadoption`, `ict-storage-dcpresence`
- The skills base behind it — `ict-capacity-tertiaryict`, `ict-capacity-devcommunity`
- What is deployed in production in government — `[PROPOSED] tech-ai-deployment`

### `tech.industry` — ICT Industry

*Is there a domestic technology sector, or only foreign vendors?*

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

- Where it ranks on innovation overall — `ict-innovation-gii`
- Whether there is a startup or innovation law — `reg-ai-startuplaw`, `govtech-startup-48`
- Whether financing and SME support exist — `govtech-startup-48.4`, `govtech-startup-48.6`, `govtech-startup-48.5`
- Whether a science and technology policy backs it — `reg-ai-innov`
- Whether the public sector innovates — `govtech-publicinnov-46`, `govtech-publicinnov-47`, `govtech-publicinnov-46.4`, `govtech-publicinnov-47.4`
- Whether the public and private sectors work together — `govtech-publicinnov-47.5`
- Whether open source is a route in — `govtech-opensource-17`, `govtech-opensource-15.4`
- Whether regulation makes room to experiment — `reg-fintech-sandbox`

---

The last five chapters — Geopolitics, Capacity, Digitalisation, Data and Finance — are in [`status-outline-part-2.md`](status-outline-part-2.md); `status_lib.outline()` reads both files.
