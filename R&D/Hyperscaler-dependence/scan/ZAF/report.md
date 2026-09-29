---
title: South Africa — who hosts the state's front door
date: 2026-09-29
author: Bill Anderson
source: R&D/Hyperscaler-dependence/scan/ZAF/ (nodes.csv, organisations.csv, run.json)
scan_date: 2026-09-28
---

# South Africa: who hosts the state's front door

29 September 2026 · Bill Anderson · scan of 28 September 2026

The scan covered 51 state bodies, banks and state-owned companies in South Africa. 28% of their working server addresses are on US cloud: Amazon, Microsoft, Google or Oracle. 27% are behind shields such as Cloudflare, which hide the host. 25% are on government data centres or the institutions' own systems.

The scan found 12,666 web and mail names and 7,436 working addresses. 44 of the 51 institutions use US cloud for at least part of their estate. 31 use Microsoft for email and none use Google.

Of the 54 countries scanned so far, South Africa has the 6th highest US cloud share (median 13%) and the 9th highest share behind shields (median 12%).

## Where it lives

![US cloud: 28% of working addresses; behind shields: 27%](report-chart.png)

2,119 addresses are on US cloud. Where they are: 54% on worldwide delivery networks (no fixed location), 26% in Europe, 16% in Africa, 3% in North America, 1% in a region the providers do not publish and <1% in Asia or the Middle East.

1,984 addresses are behind shields: Cloudflare (88%), Imperva (8%) and Radware (4%). The host behind a shield cannot be seen, so the US cloud share is a minimum.

## Banks against government

| Share of working addresses | Government (39) | Banks (12) |
| --- | --- | --- |
| On US cloud | 27% | 30% |
| …of which in Africa | 3% | 5% |
| US online services (Microsoft 365 and others) | 6% | 4% |
| Behind a shield | 26% | 27% |
| Government data centres | 7% | 0% |
| Run by the institution itself | 11% | 30% |
| Telecoms companies | 13% | 7% |
| African data centres and IT firms | 7% | <1% |
| Other foreign hosting firms | 2% | <1% |

11 of 12 banks and 33 of 39 government bodies use US cloud somewhere. "Government" includes the central bank, the payment switch, the stock exchange and the state-owned companies.

## Email

31 of the 51 institutions use Microsoft 365 for email and none use Google.

- **Microsoft 365:** 31. Parliament of the Republic of South Africa, Department of International Relations and Cooperation (DIRCO), South African Police Service, Department of Justice and Constitutional Development, National Treasury, South African Revenue Service, Standard Bank, Absa, Absa (group), Nedbank, Capitec Bank, Discovery Bank, African Bank, TymeBank, Bidvest Bank, Information Regulator, South African Social Security Agency (SASSA), Department of Social Development, BankservAfrica, Johannesburg Stock Exchange, Financial Sector Conduct Authority, Public Investment Corporation, National Treasury eTender portal, Eskom, Transnet, Broadband Infraco, Department of Communications and Digital Technologies, ICASA, Auditor-General of South Africa, Special Investigating Unit and Public Protector.
- **Government data centre (State Information Technology Agency):** 1. Government portal (GCIS).
- **Own mail servers (FNB):** 1. FirstRand.
- **Telecoms companies:** 5. Department of Defence and SANDF (Telkom SA), State Security Agency (Telkom SA), Department of Home Affairs (Dimension Data), State Information Technology Agency (SITA) (Dimension Data) and Cybersecurity Hub (national CSIRT) (TENET).
- **Behind a mail filter, provider not visible:** 11. Office of the Chief Justice / Judiciary, South African Reserve Bank, FirstRand, Investec, Electoral Commission of South Africa (IEC), Statistics South Africa, National Department of Health, Payments Association of South Africa (PASA), Government Employees Pension Fund, Telkom and Sentech.
- **No mail on the domain scanned:** 2. The Presidency and Department of Land Reform and Rural Development (Deeds Office).

## Institution by institution

Each figure is a share of that institution's working addresses. The rest are with telecoms companies, African data centres, US online services or foreign hosts. Rows follow the order of institution types.

| Institution | Type | On US cloud | …in Africa | Behind a shield | Own or government | Email |
| --- | --- | --- | --- | --- | --- | --- |
| The Presidency | Presidency | 0% | 0% | 0% | 40% | — |
| Parliament of the Republic of South Africa | Parliament | 0% | 0% | 0% | 0% | Microsoft |
| Department of International Relations and Cooperation (DIRCO) | Foreign Affairs | 33% | 5% | 0% | 5% | Microsoft |
| Department of Defence and SANDF | Defence | 0% | 0% | 0% | 7% | Telecoms |
| South African Police Service | Police | 26% | 0% | 0% | 71% | Microsoft |
| Department of Justice and Constitutional Development | Justice | 20% | 0% | 0% | 0% | Microsoft |
| Office of the Chief Justice / Judiciary | Justice | 26% | 5% | 0% | 55% | Filtered |
| National Treasury | Treasury / Finance | 74% | <1% | <1% | 19% | Microsoft |
| South African Revenue Service | Revenue Service | 3% | 2% | 60% | 0% | Microsoft |
| State Security Agency | Intelligence | 43% | 0% | 0% | 0% | Telecoms |
| Department of Home Affairs | Interior / Home Affairs | 24% | 2% | 0% | 71% | Telecoms |
| South African Reserve Bank | Central Bank | 28% | 24% | 0% | 65% | Filtered |
| Standard Bank | Commercial Banks | 21% | 1% | 55% | 22% | Microsoft |
| FirstRand | Commercial Banks | 0% | 0% | 0% | 77% | Filtered |
| FirstRand (FNB) | Commercial Banks | 10% | 4% | 2% | 74% | Own servers |
| Absa | Commercial Banks | 53% | 29% | 6% | 34% | Microsoft |
| Absa (group) | Commercial Banks | 35% | 26% | 13% | 10% | Microsoft |
| Nedbank | Commercial Banks | 48% | 7% | 0% | 3% | Microsoft |
| Investec | Commercial Banks | 4% | 0% | 82% | 9% | Filtered |
| Capitec Bank | Commercial Banks | 10% | 0% | 3% | 82% | Microsoft |
| Discovery Bank | Commercial Banks | 28% | 2% | 16% | 30% | Microsoft |
| African Bank | Commercial Banks | 46% | 2% | 38% | 9% | Microsoft |
| TymeBank | Commercial Banks | 91% | 1% | <1% | 0% | Microsoft |
| Bidvest Bank | Commercial Banks | 56% | 5% | 5% | 0% | Microsoft |
| Information Regulator | Data protection authority | 20% | 0% | 0% | 7% | Microsoft |
| Electoral Commission of South Africa (IEC) | Electoral commission | 5% | 0% | 87% | 0% | Filtered |
| Statistics South Africa | Statistics office | 2% | 0% | 95% | 1% | Filtered |
| National Department of Health | Health ministry / National health insurance | 12% | 12% | 0% | 2% | Filtered |
| South African Social Security Agency (SASSA) | Social protection / Social registry | 0% | 0% | 0% | 0% | Microsoft |
| Department of Social Development | Social protection / Social registry | 4% | 2% | 0% | 64% | Microsoft |
| Department of Land Reform and Rural Development (Deeds Office) | Land registry | no working address | | | | — |
| BankservAfrica | National payment switch | 38% | 1% | 0% | 12% | Microsoft |
| Payments Association of South Africa (PASA) | National payment switch | 39% | 0% | 0% | 0% | Filtered |
| Johannesburg Stock Exchange | Stock exchange | 8% | 0% | 79% | 10% | Microsoft |
| Financial Sector Conduct Authority | Securities regulator | 43% | 5% | 0% | 0% | Microsoft |
| Public Investment Corporation | Sovereign wealth fund / National pension fund | 64% | 15% | 0% | 0% | Microsoft |
| Government Employees Pension Fund | Sovereign wealth fund / National pension fund | 33% | 0% | 7% | 0% | Filtered |
| National Treasury eTender portal | Public procurement authority | 38% | 0% | 0% | 22% | Microsoft |
| Eskom | Energy utility | 9% | 0% | 75% | 14% | Microsoft |
| Transnet | Ports authority | 9% | 5% | 26% | 3% | Microsoft |
| Telkom | State-owned telco / National backbone operator | 49% | 2% | 0% | 39% | Filtered |
| Broadband Infraco | State-owned telco / National backbone operator | 25% | 0% | 6% | 19% | Microsoft |
| Sentech | State-owned telco / National backbone operator | 54% | 0% | 9% | 24% | Filtered |
| Government portal (GCIS) | E-government agency | 0% | 0% | 0% | 56% | Government |
| Department of Communications and Digital Technologies | E-government agency | 8% | 0% | 0% | 75% | Microsoft |
| State Information Technology Agency (SITA) | National data centre / Government cloud operator | 28% | 0% | 0% | 68% | Telecoms |
| Cybersecurity Hub (national CSIRT) | Cybersecurity agency / National CERT | 31% | 0% | 0% | 10% | Telecoms |
| ICASA | Communications regulator | 57% | 26% | 3% | 0% | Microsoft |
| Auditor-General of South Africa | Audit office | 5% | 4% | 0% | 0% | Microsoft |
| Special Investigating Unit | Anti-corruption commission | 21% | 2% | 0% | 0% | Microsoft |
| Public Protector | Anti-corruption commission | 6% | 0% | 0% | 42% | Microsoft |

4 of the 36 types are covered by another institution in the table: Armed Forces (in Defence), Customs (in Revenue Service), Civil registry / National ID authority (in Interior) and Immigration / Passports (in Interior).

## What stood out

- **Most on US cloud.** TymeBank (91%), National Treasury (74%), Public Investment Corporation (64%), ICASA (57%) and Bidvest Bank (56%) have more than half their working addresses on US cloud. 2 more are over half.
- **US cloud in Africa.** Absa has 29% of its working addresses in US cloud data centres in Africa, the highest share in South Africa.
- **Core state bodies on foreign hosting firms.** The Presidency (DigitalOcean), Parliament of the Republic of South Africa (Casablanca INT and SuperNetwork), Office of the Chief Justice / Judiciary (Akamai Connected Cloud (Linode)) and South African Reserve Bank (DigitalOcean).
- **No Chinese cloud.** The scan found no address on Huawei, Alibaba or Tencent cloud.
- **Names anyone could claim.** 3 web addresses at Absa, South African Revenue Service and Standard Bank point at a deleted cloud name that anyone could register and then publish under. We have flagged them and do not name them here.

## What this can and cannot tell you

The scan sees only the front door: websites, email, login portals, remote-access gateways and online banking. It cannot see where a bank's core ledger, the ID register or the payroll run.

- **Every US figure is a minimum.** Anything behind a shield or a mail filter could also be on US cloud. In South Africa that is 27% of working addresses.
- **It counts addresses, not importance.** An institution with many test and marketing sites weighs more than one with few.
- **The list of institutions was drawn up for this scan.** Each domain was checked to exist, not confirmed as the institution's main one.
- **It is a snapshot.** Every figure is as of 28 September 2026.
- **Nothing was touched.** The scan used public address lookups, public certificate records and the cloud companies' published address lists. It never connected to any institution's systems.

The data and method are in `R&D/Hyperscaler-dependence/scan/ZAF/` and `R&D/Hyperscaler-dependence/HYPERSCALER-SCAN.md` in the Corpus repository.
