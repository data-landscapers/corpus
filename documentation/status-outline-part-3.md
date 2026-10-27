---
type: spec
reader: cc
title: Status outline — Governance
---

# Status outline — Governance

The questions and checklists for the Governance chapter of `status-outline.md`, whose preamble governs them. It is a part of its own to keep each file under the spec cap; `status_lib.outline()` reads all three parts.

---
## Governance

### `gov.legislate` — Legislation and regulation

*What binding law is on the books, and where are the holes?*

- **Data protection legislation**
  - Data protection and access to information — `reg-id-dplaw`, `reg-id-rti`, `govtech-dataprotect-38`, `govtech-rti-37`
- **Cybersecurity legislation**
  - Cyber, critical infrastructure and e-waste — `reg-cyber-cyberlaw`, `reg-cyber-ciip`, `reg-cyber-ewaste`
- **Legislation covering digital id**
  - Identity and electronic trust — `reg-id-didlaw`, `reg-id-esig`
- **Digital payments legislation**
  - Payments, e-commerce and open banking — `reg-fintech-paylaw`, `reg-fintech-ecomlaw`, `reg-fintech-openbanking`
- **Legislation enabling data interoperability** — wiki only
- **AI legislation / regulations**
  - AI, emerging technology and startups — `reg-ai-ailaw`, `reg-ai-emerging`, `reg-ai-startuplaw`
- **E-commerce legislation** — as above: payments, e-commerce and open banking
- **Statistics legislation** — wiki only
- **Access to information legislation** — as above: data protection and access to information
- *Also in this sub-section*
  - Communications and spectrum — `reg-connect-telecomlaw`, `reg-connect-spectrum`, `reg-connect-sharing`
  - E-government and procurement — `reg-egov-egovpol`, `reg-egov-procurement`
  - Whether law on the books is law in practice — `iiag-law-execcomprol`, `iiag-law-lawenf`, `iiag-law-pubpercrol`, `iiag-law-eqtreatlaw`

### `gov.policy` — Strategies, plans and policies

*What has the state committed to on paper, and who owns delivery?*

- **Digital transformation strategy**
  - The overarching digital strategy — `reg-egov-strategy`, `govtech-digitransform-35`
  - Who leads it and through what machinery — `govtech-digitransform-36.2`, `govtech-digitransform-36.3`, `govtech-digitransform-36`
- **ICT strategy** — wiki only
- **Broadband strategy**
  - The sector strategies — `reg-connect-broadband`, `reg-connect-ua`, `reg-fintech-paystrat`, `reg-cyber-strategy`, `reg-ai-strategy`
- **Data storage / cloud strategy**
  - Hosting and cloud policy — `reg-cyber-cloud`, `reg-egov-cloudpolicy`, `ict-storage-govcloud`
- **Data interoperability framework / roadmap** — wiki only
- **AI strategy** — as above: the sector strategies
- **Data localisation policies** — wiki only
- **Data governance policy**
  - Whether there is a data governance body and strategy — `govtech-datagov-34`, `govtech-datagov-34.4`, `govtech-datagov-34.6`
- **Open data policy**
  - Open data and open source commitments — `reg-egov-opendata`, `govtech-opensource-15`
- *Also in this sub-section*
  - Skills and innovation commitments — `govtech-skills-45`, `govtech-publicinnov-46`, `reg-ai-innov`
  - Whether the documents themselves are published — `govtech-digitransform-36.4`, `govtech-datagov-34.7`, `govtech-skills-45.7`

### `gov.regional` — Regional collaboration

*How far does the country's digital estate reach across its borders?*

- **Regional policy collaboration**
  - Which regional digital bodies and programmes it is party to — `[PROPOSED] geopol-regional-membership`
- **Regional legal harmonisation**
  - Whether national standards align with regional frameworks — `reg-id-interop`, `govtech-interop-3`
  - Whether AU and continental instruments are ratified and domesticated — `[PROPOSED] geopol-regional-instrument`
- **Shared regional infrastructure** — wiki only
- **Cross-border data transfers**
  - What constrains cross-border data flow — `exchange-uptake-sovereignty`, `ict-storage-datalocalisation`
- *Also in this sub-section*
  - Whether the national ID is recognised regionally — `id-uptake-crossborder`
  - Whether payments cross the border — `pay-functionality-usecasecrossborder`
  - How integrated the economy is regionally — `iiag-business-reginteg`, `odin-econ-trade`

### `gov.standards` — Standards

*Are systems built to shared, published standards, or one at a time?*

- **National interoperability standards**
  - Whether an interoperability framework exists and is in force — `govtech-interop-3`, `govtech-interop-3.4`, `reg-id-interop`
- **National quality standards**
  - Whether data quality and uptime are held to a standard — `govtech-interop-3.6`, `govtech-interop-3.7`
- **Adoption of international standards**
  - Electronic signature and trust standards — `reg-id-esig`
- *Also in this sub-section*
  - Whether procurement enforces standards — `govtech-procure-12.5`, `govtech-procure-12.6`
  - Open source: policy, adoption and who governs it — `govtech-opensource-15`, `govtech-opensource-15.4`, `govtech-opensource-15.3`
  - Standardised financial classification — `govtech-financial-5.10`, `govtech-financial-5.13`
  - Whether legacy systems are being retired to standard — `govtech-interop-3.8`

### `gov.protect` — Data protection

*Is personal data protected in law, and is anyone enforcing it?*

- **Data protection authority**
  - Whether an authority exists and has real oversight — `govtech-dataprotect-39`, `id-governance-dpaoversight`
  - Whether compliance is monitored — `govtech-dataprotect-38.4`
  - Whether the regime and the regulator publish anything — `govtech-dataprotect-39.4`, `govtech-dataprotect-38.5`
- **National data protection readiness**
  - Whether legislation exists — `reg-id-dplaw`, `govtech-dataprotect-38`, `id-governance-dpaexists`, `ict-storage-dataprotection`
  - The rules governing sharing, and whether courts can review them — `id-governance-datasharingrules`, `id-governance-courtoversight`
- *Also in this sub-section*
  - How payment data specifically is covered — `pay-governance-dataprivacylaw`, `pay-governance-databreachnotif`
  - Localisation and sovereignty terms — `ict-storage-datalocalisation`, `exchange-uptake-sovereignty`
  - The rights environment the regime sits in — `iiag-rights-digrights`, `iiag-rights-perslibert`, `iiag-rights-protagdiscrim`

### `gov.discourse` — Public debate and participation in policymaking

*Who gets a say in digital policy, and can they say it freely?*

- **Non-governmental contribution to national policy**
  - Whether participation platforms exist and what they do — `govtech-particip-30`, `govtech-particip-30.3`, `govtech-particip-30.2`
  - Whether feedback reaches government, and whether it answers — `govtech-feedback-31`, `govtech-feedback-31.6`, `govtech-feedback-31.2`
  - The wider space for deliberation and civil society — `iiag-participate-delibpartgov`, `iiag-participate-civsocspace`, `iiag-participate-freeassocass`
- **Open discussion of government policy**
  - Whether media and expression are free — `iiag-rights-mediafree`, `iiag-rights-freeexpbelief`, `iiag-rights-pubfreespafr`
  - Digital freedom specifically — `iiag-rights-digrights`
- *Also in this sub-section*
  - Whether those channels are inclusive and safe — `govtech-feedback-31.3`, `govtech-feedback-31.5`, `govtech-particip-30.4`, `govtech-particip-30.5`
  - Whether the public can obtain the records to argue with — `govtech-rti-37`, `govtech-rti-37.3`, `iiag-account-accpubrec`, `iiag-account-discpubrec`
  - Whether citizens are involved in designing the services — `govtech-serviceportal-19.2`, `govtech-taxportal-20.4`, `govtech-socialportal-24.3`, `govtech-job-25.4`
