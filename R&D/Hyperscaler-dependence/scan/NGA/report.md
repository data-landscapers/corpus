---
title: Nigeria — who hosts the state's front door
date: 2026-09-29
author: Bill Anderson
source: R&D/Hyperscaler-dependence/scan/NGA/ (nodes.csv, organisations.csv, run.json)
scan_date: 2026-09-29
---

# Nigeria: who hosts the state's front door

29 September 2026 · Bill Anderson · scan of 29 September 2026

The scan covered 52 state bodies, banks and state-owned companies in Nigeria. 24% of their working server addresses are on US cloud: Amazon, Microsoft, Google or Oracle. 44% are behind shields such as Cloudflare, which hide the host. 14% are on government data centres or the institutions' own systems.

The scan found 6,667 web and mail names and 5,765 working addresses. 36 of the 52 institutions use US cloud for at least part of their estate. 24 use Microsoft for email and 2 use Google.

Of the 54 countries scanned so far, Nigeria has the 10th highest US cloud share (median 13%) and the 5th highest share behind shields (median 12%).

## Where it lives

![US cloud: 24% of working addresses; behind shields: 44%](report-chart.png)

1,393 addresses are on US cloud. Where they are: 55% on worldwide delivery networks (no fixed location), 31% in Europe, 5% in Africa, 4% in North America, 3% in a region the providers do not publish and 3% in Asia or the Middle East.

2,555 addresses are behind shields: Cloudflare (81%), F5 (11%) and Imperva (7%). The host behind a shield cannot be seen, so the US cloud share is a minimum.

## Banks against government

| Share of working addresses | Government (42) | Banks (10) |
| --- | --- | --- |
| On US cloud | 30% | 16% |
| …of which in Africa | 2% | <1% |
| US online services (Microsoft 365 and others) | 5% | 3% |
| Behind a shield | 28% | 65% |
| Government data centres | 12% | 0% |
| Run by the institution itself | 5% | 11% |
| Telecoms companies | 3% | 1% |
| African data centres and IT firms | 7% | <1% |
| Other foreign hosting firms | 10% | 2% |

10 of 10 banks and 26 of 42 government bodies use US cloud somewhere. "Government" includes the central bank, the payment switch, the stock exchange and the state-owned companies.

## Email

24 of the 52 institutions use Microsoft 365 for email and 2 use Google.

- **Microsoft 365:** 24. Federal Ministry of Finance, Federal Inland Revenue Service, Nigeria Revenue Service, Central Bank of Nigeria, Zenith Bank, Access Bank, United Bank for Africa, Guaranty Trust Bank, Fidelity Bank, First City Monument Bank, Union Bank, Nigeria Data Protection Commission, National Bureau of Statistics, National Social Safety-Nets Coordinating Office, Abuja Geographic Information Systems (FCT lands registry), Nigeria Inter-Bank Settlement System (NIBSS), Interswitch, Nigerian Exchange Group, Nigeria Sovereign Investment Authority, National Pension Commission, Bureau of Public Procurement, Nigerian Ports Authority, National Information Technology Development Agency (NITDA) and Nigerian Communications Commission.
- **Google:** 2. National Judicial Council and Nigeria Immigration Service.
- **Government data centre:** 12. State House (Galaxy Backbone), National Assembly (National Assembly Abuja), Ministry of Foreign Affairs (Galaxy Backbone), Ministry of Defence (Galaxy Backbone), Nigeria Police Force (Galaxy Backbone), Federal Ministry of Justice (Galaxy Backbone), Office of the Accountant-General of the Federation (Galaxy Backbone), Federal Ministry of Interior (Galaxy Backbone), Federal Ministry of Health (Galaxy Backbone), NIGCOMSAT (Galaxy Backbone), ngCERT (Galaxy Backbone) and Office of the Auditor-General for the Federation (Galaxy Backbone).
- **Own mail servers:** 2. National Identity Management Commission and Galaxy Backbone.
- **Telecoms companies:** 2. Nigerian Army (Globacom) and Department of State Services (Backbone Connectivity Network).
- **African hosts:** 3. Nigeria Customs Service (Trade Modernisation Project), Securities and Exchange Commission (MainOne) and Economic and Financial Crimes Commission (Layer3).
- **US cloud:** 1. Transmission Company of Nigeria.
- **Foreign hosting firms:** 3. Sterling Bank (Zoho), National Health Insurance Authority (Contabo) and Independent Corrupt Practices Commission (Cyberspace).
- **Behind a mail filter, provider not visible:** 1. First Bank of Nigeria.
- **Not identified (INEC):** 1. Independent National Electoral Commission.
- **No mail on the domain scanned:** 1. Stanbic IBTC.

## Institution by institution

Each figure is a share of that institution's working addresses. The rest are with telecoms companies, African data centres, US online services or foreign hosts. Rows follow the order of institution types.

| Institution | Type | On US cloud | …in Africa | Behind a shield | Own or government | Email |
| --- | --- | --- | --- | --- | --- | --- |
| State House | Presidency | 0% | 0% | 0% | 94% | Government |
| National Assembly | Parliament | 47% | 0% | 0% | 47% | Government |
| Ministry of Foreign Affairs | Foreign Affairs | 0% | 0% | 9% | 78% | Government |
| Ministry of Defence | Defence | 0% | 0% | 0% | 93% | Government |
| Nigerian Army | Armed Forces | 0% | 0% | 4% | 4% | Telecoms |
| Nigeria Police Force | Police | 42% | 0% | 0% | 32% | Government |
| Federal Ministry of Justice | Justice | 0% | 0% | 0% | 93% | Government |
| National Judicial Council | Justice | 15% | 13% | 0% | 0% | Google |
| Federal Ministry of Finance | Treasury / Finance | 0% | 0% | 0% | 44% | Microsoft |
| Office of the Accountant-General of the Federation | Treasury / Finance | 0% | 0% | 0% | 89% | Government |
| Federal Inland Revenue Service | Revenue Service | 13% | 0% | 7% | 6% | Microsoft |
| Nigeria Revenue Service | Revenue Service | 23% | 1% | 10% | 0% | Microsoft |
| Nigeria Customs Service | Customs | 1% | 0% | 88% | 0% | African host |
| Department of State Services | Intelligence | 0% | 0% | 23% | 23% | Telecoms |
| Federal Ministry of Interior | Interior / Home Affairs | 19% | 0% | 0% | 54% | Government |
| Central Bank of Nigeria | Central Bank | 28% | <1% | 56% | 15% | Microsoft |
| Zenith Bank | Commercial Banks | 39% | 0% | 15% | 41% | Microsoft |
| Access Bank | Commercial Banks | 17% | 0% | 72% | 2% | Microsoft |
| First Bank of Nigeria | Commercial Banks | 26% | 0% | 35% | 36% | Filtered |
| United Bank for Africa | Commercial Banks | 35% | 0% | 32% | 26% | Microsoft |
| Guaranty Trust Bank | Commercial Banks | 31% | 0% | 17% | 31% | Microsoft |
| Fidelity Bank | Commercial Banks | <1% | 0% | 97% | <1% | Microsoft |
| First City Monument Bank | Commercial Banks | 41% | <1% | 28% | 12% | Microsoft |
| Stanbic IBTC | Commercial Banks | 28% | 0% | 66% | 7% | — |
| Union Bank | Commercial Banks | 26% | 0% | 18% | 42% | Microsoft |
| Sterling Bank | Commercial Banks | 15% | 0% | 76% | 0% | Foreign host |
| National Identity Management Commission | Civil registry / National ID authority | 84% | 0% | 1% | 11% | Own servers |
| Nigeria Immigration Service | Immigration / Passports | 37% | 0% | 0% | 27% | Google |
| Nigeria Data Protection Commission | Data protection authority | 95% | 76% | 0% | 0% | Microsoft |
| Independent National Electoral Commission (INEC) | Electoral commission | 80% | 0% | 7% | 0% | Not identified |
| National Bureau of Statistics | Statistics office | 28% | 0% | 0% | 13% | Microsoft |
| Federal Ministry of Health | Health ministry / National health insurance | 7% | 2% | 0% | 88% | Government |
| National Health Insurance Authority | Health ministry / National health insurance | 44% | 19% | 0% | 0% | Foreign host |
| National Social Safety-Nets Coordinating Office | Social protection / Social registry | 0% | 0% | 0% | 0% | Microsoft |
| Abuja Geographic Information Systems (FCT lands registry) | Land registry | 0% | 0% | 0% | 79% | Microsoft |
| Nigeria Inter-Bank Settlement System (NIBSS) | National payment switch | 26% | 0% | 41% | 15% | Microsoft |
| Interswitch | National payment switch | 13% | <1% | 75% | 0% | Microsoft |
| Nigerian Exchange Group | Stock exchange | 94% | 0% | 2% | <1% | Microsoft |
| Securities and Exchange Commission | Securities regulator | 14% | 0% | 9% | 0% | African host |
| Nigeria Sovereign Investment Authority | Sovereign wealth fund / National pension fund | 25% | 0% | 50% | 0% | Microsoft |
| National Pension Commission | Sovereign wealth fund / National pension fund | 46% | 0% | 0% | 4% | Microsoft |
| Bureau of Public Procurement | Public procurement authority | 27% | 0% | 0% | 27% | Microsoft |
| Transmission Company of Nigeria | Energy utility | 25% | 0% | 4% | 8% | US cloud |
| Nigerian Ports Authority | Ports authority | 15% | 0% | 44% | 39% | Microsoft |
| NIGCOMSAT | State-owned telco / National backbone operator | 0% | 0% | 52% | 48% | Government |
| National Information Technology Development Agency (NITDA) | E-government agency | 10% | 0% | 0% | 36% | Microsoft |
| Galaxy Backbone | National data centre / Government cloud operator | 0% | 0% | 0% | 100% | Own servers |
| ngCERT | Cybersecurity agency / National CERT | 0% | 0% | 88% | 9% | Government |
| Nigerian Communications Commission | Communications regulator | 2% | 0% | 72% | <1% | Microsoft |
| Office of the Auditor-General for the Federation | Audit office | 0% | 0% | 0% | 100% | Government |
| Economic and Financial Crimes Commission | Anti-corruption commission | 0% | 0% | 95% | 0% | African host |
| Independent Corrupt Practices Commission | Anti-corruption commission | 0% | 0% | 24% | 30% | Foreign host |

## What stood out

- **Most on US cloud.** Nigeria Data Protection Commission (95%), Nigerian Exchange Group (94%), National Identity Management Commission (84%) and Independent National Electoral Commission (INEC) (80%) have more than half their working addresses on US cloud.
- **US cloud in Africa.** Nigeria Data Protection Commission has 76% of its working addresses in US cloud data centres in Africa, the highest share in Nigeria.
- **Core state bodies at home.** State House (94%), Ministry of Defence (93%), Federal Ministry of Justice (93%) and Office of the Accountant-General of the Federation (89%) keep at least 80% of their working addresses on government data centres or their own systems.
- **Core state bodies on foreign hosting firms.** National Assembly (DreamHost), Ministry of Defence (IONOS), Nigeria Police Force (DigitalOcean and A2 Hosting), Federal Ministry of Justice (Akamai Connected Cloud (Linode) and 24 Shells), National Judicial Council (Hosting and Hawk Host) and Federal Ministry of Finance (Namecheap), and 6 more.
- **Chinese cloud.** 1 address, all at Zenith Bank, is on Chinese cloud.
- **Names anyone could claim.** 2 web addresses at Central Bank of Nigeria and Federal Ministry of Health point at a deleted cloud name that anyone could register and then publish under. We have flagged them and do not name them here.

## What this can and cannot tell you

The scan sees only the front door: websites, email, login portals, remote-access gateways and online banking. It cannot see where a bank's core ledger, the ID register or the payroll run.

- **Every US figure is a minimum.** Anything behind a shield or a mail filter could also be on US cloud. In Nigeria that is 44% of working addresses.
- **It counts addresses, not importance.** An institution with many test and marketing sites weighs more than one with few.
- **The list of institutions was drawn up for this scan.** Each domain was checked to exist, not confirmed as the institution's main one.
- **It is a snapshot.** Every figure is as of 29 September 2026.
- **Nothing was touched.** The scan used public address lookups, public certificate records and the cloud companies' published address lists. It never connected to any institution's systems.

The data and method are in `R&D/Hyperscaler-dependence/scan/NGA/` and `R&D/Hyperscaler-dependence/HYPERSCALER-SCAN.md` in the Corpus repository.
