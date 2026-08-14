# Country status outline

The drafting outline for the country status output. Each `###` sub-section is one taxonomy Level-2 slug (`lookups/taxonomy.md`), and the question under it is what the section answers: **what is the current status of this, in this country, as at this date**. The bullets under the question are the breakdown of that question — the things that have to be established before the question can be answered.

Each bullet carries the variable ids that answer it, from `prep/status-indicators-africa-dpi.csv`. Those ids join directly to `prep/africa-dpi-data.csv` on `Variable Id`, which holds a value, a year, a comment and source URLs for all 54 countries. Every id cited here is present in both files.

**An id may appear under more than one sub-section.** The taxonomy cross-lists by multi-tagging rather than by a single-parent partition, and the indicators behave the same way: `reg-cyber-cloud` answers a question in `infra.store`, another in `infra.cybersec` and another in `gov.legislate`. The mapping is a set of answers to questions, not a filing system.

**`[PROPOSED]` marks an indicator that does not yet exist.** Nine sub-sections are thinly or not at all covered by the DPI dataset — the five `geopol.*` slugs and `data.satellite` hold nothing, and `finance.new`, `finance.mou`, `capacity.research`, `digital.localgov` and `tech.industry` hold very little. Candidate definitions for those are drafted in the appendix, in the same schema as the indicator table, and are flagged inline where they would be used. They are not collected; nothing in `africa-dpi-data.csv` answers them yet.

Where a sub-section is answered mainly from the wiki rather than the dataset, that is stated on the bullet.

**38 sub-sections are mapped; 37 are written.** `finance.budget` is suspended pending budget work and is marked so at the point of use.

**394 of the 453 indicators are used, across 577 citations.** The 59 that are not are almost all Ibrahim Index measures of the general governance environment — corruption, security, environmental policy, clinical health outcomes, electoral pluralism, women's political representation — which bear on digital governance only at one remove and would dilute the sections they were dropped into. The remainder are GovTech Maturity Index *governance* and *transparency* sub-variables duplicating a transparency bullet already carried elsewhere in the same sub-section. They are available if a section proves thin for a given country.

---

## ICT Infrastructure

### `infra.connect` — Connectivity

*How connected is the population, and on what terms?*

- How far the network physically reaches — `ict-connectivity-4gcoverage`
- How many people actually use it, and on what device — `ict-connectivity-internetuse`, `ict-connectivity-mobilepen`, `ict-connectivity-smartphonepen`
- Whether people can afford to — `ict-connectivity-dataafford`
- Backbone capacity and whether traffic stays local — `ict-connectivity-intlbandwidth`, `ict-connectivity-ixp`
- Independent read on infrastructure quality and mobile communications — `iiag-infrastructure-digacc`, `iiag-infrastructure-mobcomm`, `iiag-infrastructure-satinfr`
- The regulatory framework the sector runs under — `reg-connect-telecomlaw`, `reg-connect-spectrum`, `reg-connect-sharing`
- What the state has committed to, and the mechanism to fund it — `reg-connect-broadband`, `reg-connect-ua`
- Whether the sector publishes data on itself — `odin-econ-digital`

### `infra.store` — Data Storage

*Where does the country's data physically sit, and who controls it?*

- Commercial hosting capacity in country — `ict-storage-dcpresence`, `ict-storage-cloudadoption`
- Whether government has its own platform, and whether it is shared — `ict-storage-govcloud`, `govtech-cloud-1`, `govtech-cloud-1.8`
- What that platform is and what it provides — `govtech-cloud-1.4`, `govtech-cloud-1.7`
- The rules on where data may be hosted — `govtech-cloud-1.6`, `ict-storage-datalocalisation`, `reg-cyber-cloud`, `reg-egov-cloudpolicy`
- Whether the hosting arrangements are disclosed — `govtech-cloud-1.9`
- The power the estate depends on — `ict-energy-elecaccess`, `ict-energy-reliability`

### `infra.energy` — Energy

*Can the grid carry a digital economy?*

- Who has electricity at all, and where the gap falls — `ict-energy-elecaccess`, `ict-energy-urbanruraldevide`, `iiag-infrastructure-accenergy`
- Whether supply is reliable enough to run systems on — `ict-energy-reliability`
- Whether power is affordable — `ict-energy-affordability`
- What the generation mix is — `ict-energy-renewableshare`
- Whether off-grid and distributed supply is enabled in policy — `ict-energy-offgridpolicy`
- Whether the sector's own data is open — `odin-environ-energy`

### `infra.capacity` — Technical Capacity

*Does the country have the people to build and run its own systems?*

- The literacy floor — `ict-capacity-digitalliteracy`
- The tertiary pipeline feeding the sector — `ict-capacity-tertiaryict`
- The depth of the working developer community — `ict-capacity-devcommunity`
- Who is excluded from that base — `ict-capacity-gendergap`
- Government's own measured readiness to run digital services — `ict-capacity-egovreadiness`
- Whether there is a public-service skills programme, and what it covers — `govtech-skills-45`, `govtech-skills-45.5`, `govtech-skills-45.4`
- Whether the administration functions well enough to absorb capacity — `iiag-pubadmin-effadmin`

### `infra.cybersec` — Cybersecurity

*Is the state able to defend and govern its digital estate?*

- Measured national readiness — `ict-storage-cybersecurity`
- Whether there is a strategy — `reg-cyber-strategy`
- Whether there is binding law — `reg-cyber-cyberlaw`
- Whether critical information infrastructure is designated and protected — `reg-cyber-ciip`
- Whether the ID system has been independently security-reviewed — `id-uptake-securityreview`
- Whether breaches must be notified in the payments system — `pay-governance-databreachnotif`
- Whether hardware lifecycle and e-waste are regulated — `reg-cyber-ewaste`

---

## DPI

### `dpi.exchange` — Data Exchange

*Is there a working exchange layer, and what actually flows across it?*

- Whether a system exists and is operational — `exchange-system-operational`, `exchange-system-ai`
- The legal and strategic basis it rests on — `exchange-gov-legislation-exists`, `exchange-gov-strategy`, `exchange-gov-roadmap`
- Whether an interoperability framework exists and where it has got to — `govtech-interop-3`, `govtech-interop-3.4`, `reg-id-interop`
- Which foundational systems are connected — `exchange-func-digitalid`, `exchange-func-crvs`, `exchange-func-payments`, `exchange-func-revenue`, `exchange-func-socialprotection`
- Which sectoral systems are connected — `exchange-func-health`, `exchange-func-education`, `exchange-func-justice`, `exchange-func-business`, `exchange-func-agriculture`, `exchange-func-employment`, `exchange-func-passport`, `exchange-func-licensing`, `exchange-func-electoral`, `exchange-func-planning`
- Whether it is run to an operational standard — `govtech-interop-3.6`, `govtech-interop-3.7`, `govtech-interop-3.8`
- How far its reach extends beyond the centre — `exchange-uptake-subnational`, `exchange-uptake-urbanrural`, `exchange-uptake-accessibility`
- Whether its workings and its data-sovereignty terms are public — `exchange-uptake-transparency`, `exchange-uptake-sovereignty`, `govtech-interop-3.9`

### `dpi.id` — Digital Identity and CRVS

*Does a foundational identity exist, who is in it, and what does it unlock?*

- Whether a system exists, and what it is technically — `id-system-didexists`, `id-system-dbelectronic`, `id-system-biocollect`, `id-system-sysinterop`
- How much of the population it holds, and whether enrolment is compulsory — `id-uptake-popcoverage`, `id-uptake-enrollmandatory`, `id-uptake-enrolleligible`
- Who is eligible and what it costs them — `id-uptake-nonnateligible`, `id-uptake-cost`
- The legal basis, and the safeguards attached to it — `id-governance-legframework`, `id-governance-legalproof`, `id-governance-digidreg`, `reg-id-didlaw`, `id-governance-dpaexists`, `id-governance-dpaoversight`, `id-governance-datasharingrules`, `id-governance-courtoversight`
- What holding it lets a person do — `id-uptake-bankuse`, `id-uptake-healthuse`, `id-uptake-socialservicesuse`, `id-uptake-simreguse`
- What the credential technically does — `id-functionality-authdigital`, `id-functionality-authgovtportal`, `id-functionality-kycenable`, `id-functionality-dataview`
- Whether civil registration underpins it, and how complete that is — `id-governance-crvs`, `reg-cr-exists`, `reg-cr-uptake`, `reg-cr-inclusive`, `iiag-pubadmin-civreg`
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
- Whether the registers talk to each other directly — `reg-pop-crvs`, `reg-cr-pop`, `reg-land-address`, `reg-land-business`, `reg-business-address`, `reg-business-land`, `reg-address-land`, `reg-tax-business`

### `dpi.mis` — Sectoral management information systems

*Do the line ministries run real systems, and do those systems talk to anything?*

- Health and education systems, and whether they reach the exchange — `exchange-func-health`, `exchange-func-education`
- Social insurance: whether it exists, its status and platform — `govtech-socialinsure-11`, `govtech-socialinsure-11.7`, `govtech-socialinsure-11.8`
- Social protection delivery and its register — `reg-social-exists`, `reg-social-uptake`, `exchange-func-socialprotection`
- Public-service HR and payroll — `govtech-hr-9`, `govtech-hr-9.4`, `govtech-hr-9.6`, `govtech-payroll-10`, `govtech-payroll-10.4`
- Revenue-side systems — `govtech-customs-8`, `govtech-customs-8.6`, `govtech-taxmanage-7`, `govtech-taxmanage-7.6`
- Justice, employment and immigration — `exchange-func-justice`, `exchange-func-employment`, `exchange-func-passport`, `exchange-func-licensing`
- Whether these use the national ID rather than their own identifiers — `govtech-hr-9.8`, `govtech-socialinsure-11.1`
- Whether they interoperate or stand alone — `govtech-socialinsure-11.9`, `govtech-customs-8.8`, `govtech-customs-8.7`, `govtech-taxmanage-7.7`, `govtech-hr-9.7`

### `dpi.govtech` — Other GovTech and e-Gov

*What can a citizen or a business actually do online with the state?*

- The main service portal and what is on it — `govtech-serviceportal-19`, `govtech-serviceportal-19.3`, `govtech-serviceportal-19.4`, `govtech-serviceportal-19.5`, `govtech-serviceportal-19.6`
- The sectoral portals — `govtech-taxportal-20`, `govtech-taxportal-20.2`, `govtech-taxportal-20.3`, `govtech-socialportal-24`, `govtech-socialportal-24.2`, `govtech-job-25`, `govtech-job-25.2`, `govtech-job-25.3`
- Procurement done electronically — `govtech-procure-12`, `govtech-procure-12.4`, `govtech-procure-12.5`, `reg-egov-procurement`
- The public financial management core — `govtech-financial-5`, `govtech-financial-5.6`, `govtech-treasury-6`, `govtech-debt-13`, `govtech-debt-14`
- Who coordinates and audits all of this — `govtech-govtech-33`, `govtech-govtech-33.8`, `govtech-govtech-33.9`
- Whether it is run as one government or as many ministries — `govtech-digitransform-36`, `govtech-digitransform-36.3`
- The measured readiness and the legal basis — `ict-capacity-egovreadiness`, `reg-egov-egovpol`, `reg-egov-strategy`
- Whether any of it is transparent to the people using it — `govtech-govtech-33.1`, `govtech-serviceportal-19.7`, `govtech-procure-12.8`, `govtech-debt-14.7`, `govtech-digitransform-36.4`

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
- Whether there is a data governance body and a strategy behind it — `govtech-datagov-34`, `govtech-datagov-34.4`, `govtech-datagov-34.6`
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
- Whether the AU and continental instruments have been ratified and domesticated — `[PROPOSED] geopol-regional-instrument`
- Which regional digital bodies and programmes the country is party to — `[PROPOSED] geopol-regional-membership`

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
- Whether feedback reaches government and whether government answers — `govtech-feedback-31`, `govtech-feedback-31.6`, `govtech-feedback-31.2`
- Whether those channels are inclusive and safe to use — `govtech-feedback-31.3`, `govtech-feedback-31.5`, `govtech-particip-30.4`, `govtech-particip-30.5`
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
- The gap between what is available and what is used — `ict-connectivity-4gcoverage`, `ict-connectivity-internetuse`, `ict-connectivity-smartphonepen`
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
- Whether the physical service points outside the capital are digitalised — `rural-clinic-status`, `rural-school-status`, `rural-police-status`, `rural-registry-status`

---

## Technology

### `tech.ai` — AI

*Is there an AI policy, and is anything actually running?*

- Whether there is a national strategy — `reg-ai-strategy`
- Whether there is binding regulation — `reg-ai-ailaw`
- Whether adjacent emerging technology is covered — `reg-ai-emerging`
- Whether the exchange layer has analytics or AI capability — `exchange-system-ai`
- Whether AI appears in citizen-facing services — `govtech-feedback-31.4`
- The data it would have to run on — `stats-score-products`, `stats-score-sources`, `govtech-opendata-29`
- The compute and hosting it would have to run on — `ict-storage-cloudadoption`, `ict-storage-dcpresence`
- The skills base behind it — `ict-capacity-tertiaryict`, `ict-capacity-devcommunity`
- What is actually deployed in production in government — `[PROPOSED] tech-ai-deployment`

### `tech.industry` — ICT Industry

*Is there a domestic technology sector, or only foreign vendors?*

- The startup ecosystem — `ict-innovation-startupecosystem`
- Hubs and physical infrastructure for the sector — `ict-innovation-techhubs`
- The working developer base — `ict-capacity-devcommunity`
- The business and competition environment it operates in — `iiag-business-buscompreg`, `iiag-business-econdiv`
- How easy it is to form and register a company — `govtech-serviceportal-19.5`, `reg-business-exists`, `reg-business-uptake`
- Employment the sector generates — `iiag-business-secemplopp`, `odin-econ-labor`
- The structure of the telecommunications market — `[PROPOSED] tech-industry-mnomarket`
- The size of the domestic software and services industry — `[PROPOSED] tech-industry-softwaresize`
- What share of government technology spend goes to domestic suppliers — `[PROPOSED] tech-industry-localsupply`

### `tech.innovate` — Innovation ecosystem

*Does the system produce and absorb new things?*

- Where it ranks on innovation overall — `ict-innovation-gii`
- Whether there is a startup or innovation law — `reg-ai-startuplaw`, `govtech-startup-48`
- Whether financing and SME support actually exist — `govtech-startup-48.4`, `govtech-startup-48.6`, `govtech-startup-48.5`
- Whether there is a science and technology policy behind it — `reg-ai-innov`
- Whether the public sector innovates — `govtech-publicinnov-46`, `govtech-publicinnov-47`, `govtech-publicinnov-46.4`, `govtech-publicinnov-47.4`
- Whether the public and private sectors work together — `govtech-publicinnov-47.5`
- Whether open source is a route in — `govtech-opensource-17`, `govtech-opensource-15.4`
- Whether regulation makes room to experiment — `reg-fintech-sandbox`

---

## Geopolitics

**No indicator in the DPI dataset addresses any `geopol.*` slug.** Two DPI indicators are weak proxies for hyperscaler presence — `ict-storage-cloudadoption` and `ict-storage-dcpresence` — and neither attributes a provider. This section is currently answered entirely from the wiki, where `geopol.*`-tagged sources carry named actors and dated commitments.

Five indicators are proposed for each of the five actors, on a common frame, so that the answer for one country is comparable across actors and the answer for one actor is comparable across countries. The suffixes are the same in every case: `-infra`, `-platform`, `-finance`, `-agreement`, `-capacity`. Full definitions are in the appendix.

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

`finance.new` and `finance.mou` are the two slugs where the wiki is strong and the dataset holds nothing. The OSINT base carries deals and agreements as first-class entities with dated values in the announcing party's own currency, and the hubs carry a compiled `## Financing` block. The proposed indicators below are the summary figures a status report needs, derived from that material rather than collected separately.

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

**Suspended.** `STATUS-INIT` does not write this sub-section, and a status report carries 37, not 38. The mapping below is kept intact and unsuspends when budget work resumes.

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

---

# Appendix — proposed indicators

Sixty-two candidate indicators, in the schema of `prep/status-indicators-africa-dpi.csv` (*Chapter · Section · Variable Name · Definition · Variable Id*). **None is collected.** They exist because the nine sub-sections listed at the top of this file cannot be answered from the current dataset, and the wireframe is no use as a drafting outline for a topic it can ask nothing about.

Two of the groups — geopolitics and finance — are derivable from the OSINT base rather than needing fresh collection: the wiki already holds deals, agreements and named foreign actors as dated entities. Those are summary rollups of material the wiki has, not new research. The other three groups — satellite, research and local government — would need collection.

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
