---
title: Kenya — who hosts the state's front door
date: 2026-09-29
author: Bill Anderson
source: R&D/Hyperscaler-dependence/scan/KEN/ (nodes.csv, organisations.csv, run.json)
scan_date: 2026-09-29
---

# Kenya: who hosts the state's front door

29 September 2026 · Bill Anderson · scan of 29 September 2026

The scan covered 51 state bodies, banks and state-owned companies in Kenya. 11% of their working server addresses are on US cloud: Amazon, Microsoft, Google or Oracle. 49% are behind shields such as Cloudflare, which hide the host. 13% are on government data centres or the institutions' own systems.

The scan found 3,654 web and mail names and 4,780 working addresses. 30 of the 51 institutions use US cloud for at least part of their estate. 27 use Microsoft for email and 5 use Google.

Of the 54 countries scanned so far, Kenya has the 31st highest US cloud share (median 13%) and the 3rd highest share behind shields (median 12%).

## Where it lives

![US cloud: 11% of working addresses; behind shields: 49%](report-chart.png)

522 addresses are on US cloud. Where they are: 51% in Europe, 25% on worldwide delivery networks (no fixed location), 18% in Africa, 2% in a region the providers do not publish, 2% in North America and 2% in Asia or the Middle East.

2,333 addresses are behind shields: Cloudflare (81%), Imperva (15%) and Radware (2%). The host behind a shield cannot be seen, so the US cloud share is a minimum.

## Banks against government

| Share of working addresses | Government (41) | Banks (10) |
| --- | --- | --- |
| On US cloud | 8% | 20% |
| …of which in Africa | 2% | 1% |
| US online services (Microsoft 365 and others) | 6% | 12% |
| Behind a shield | 46% | 55% |
| Government data centres | 9% | 0% |
| Run by the institution itself | 8% | 5% |
| Telecoms companies | 20% | 4% |
| African data centres and IT firms | 2% | 2% |
| Other foreign hosting firms | 2% | 2% |

8 of 10 banks and 22 of 41 government bodies use US cloud somewhere. "Government" includes the central bank, the payment switch, the stock exchange and the state-owned companies.

## Email

27 of the 51 institutions use Microsoft 365 for email and 5 use Google.

- **Microsoft 365:** 27. Parliament of Kenya, Judiciary of Kenya, Central Bank of Kenya, KCB Group, Equity Bank, Co-operative Bank of Kenya, NCBA Group, I&M Bank, Diamond Trust Bank, Family Bank, Prime Bank, State Department for Immigration and Citizen Services (Civil Registration Services; National Registration Bureau), Office of the Data Protection Commissioner, Independent Electoral and Boundaries Commission (IEBC), Social Health Authority, Nairobi Securities Exchange, Capital Markets Authority, Retirement Benefits Authority, Public Procurement Regulatory Authority, Kenya Power, KenGen, Kenya Ports Authority, Telkom Kenya, Konza Technopolis, National KE-CIRT/CC, Communications Authority of Kenya and Office of the Auditor-General.
- **Google:** 5. Kenya National Bureau of Statistics, Integrated Payment Services (PesaLink), Government tenders portal, eCitizen and Ministry of Information, Communications and the Digital Economy.
- **Government data centre (Konza Technopolis):** 9. Executive Office of the President, Ministry of Foreign and Diaspora Affairs, The National Treasury, Ministry of Interior and National Administration, Department of Immigration Services, Ministry of Health, State Department for Social Protection, Ministry of Lands (Ardhisasa) and ICT Authority.
- **Own mail servers:** 1. Kenya Revenue Authority.
- **Telecoms companies:** 2. Ministry of Defence and Kenya Defence Forces (Telkom Kenya) and Ethics and Anti-Corruption Commission (Safaricom).
- **African hosts (Host Africa):** 1. National Social Security Fund.
- **US cloud:** 1. National Police Service.
- **Behind a mail filter, provider not visible:** 1. Safaricom.
- **No mail on the domain scanned:** 4. Office of the Attorney General, National Intelligence Service, Absa Bank Kenya and Stanbic Bank Kenya.

## Institution by institution

Each figure is a share of that institution's working addresses. The rest are with telecoms companies, African data centres, US online services or foreign hosts. Rows follow the order of institution types.

| Institution | Type | On US cloud | …in Africa | Behind a shield | Own or government | Email |
| --- | --- | --- | --- | --- | --- | --- |
| Executive Office of the President | Presidency | 0% | 0% | 21% | 32% | Government |
| Parliament of Kenya | Parliament | 3% | 0% | 77% | 0% | Microsoft |
| Ministry of Foreign and Diaspora Affairs | Foreign Affairs | 0% | 0% | 0% | 62% | Government |
| Ministry of Defence and Kenya Defence Forces | Defence | 0% | 0% | 0% | 0% | Telecoms |
| National Police Service | Police | 8% | 0% | 0% | 31% | US cloud |
| Judiciary of Kenya | Justice | 0% | 0% | 0% | 6% | Microsoft |
| Office of the Attorney General | Justice | 0% | 0% | 0% | 50% | — |
| The National Treasury | Treasury / Finance | 0% | 0% | 0% | 53% | Government |
| Kenya Revenue Authority | Revenue Service | 3% | 0% | 3% | 66% | Own servers |
| National Intelligence Service | Intelligence | 0% | 0% | 0% | 0% | — |
| Ministry of Interior and National Administration | Interior / Home Affairs | 8% | 0% | 0% | 58% | Government |
| Central Bank of Kenya | Central Bank | 0% | 0% | 7% | 36% | Microsoft |
| KCB Group | Commercial Banks | 13% | 0% | 63% | 0% | Microsoft |
| Equity Bank | Commercial Banks | 44% | 0% | 10% | 19% | Microsoft |
| Co-operative Bank of Kenya | Commercial Banks | 22% | 0% | 4% | 15% | Microsoft |
| NCBA Group | Commercial Banks | 50% | 3% | 17% | 14% | Microsoft |
| Absa Bank Kenya | Commercial Banks | 37% | 18% | 33% | 13% | — |
| Stanbic Bank Kenya | Commercial Banks | 11% | 0% | 85% | 0% | — |
| I&M Bank | Commercial Banks | 0% | 0% | 74% | 0% | Microsoft |
| Diamond Trust Bank | Commercial Banks | 14% | 0% | 74% | 6% | Microsoft |
| Family Bank | Commercial Banks | 0% | 0% | 70% | 8% | Microsoft |
| Prime Bank | Commercial Banks | 53% | 0% | 8% | 7% | Microsoft |
| State Department for Immigration and Citizen Services (Civil Registration Services; National Registration Bureau) | Civil registry / National ID authority | 0% | 0% | 0% | 16% | Microsoft |
| Department of Immigration Services | Immigration / Passports | 0% | 0% | 36% | 36% | Government |
| Office of the Data Protection Commissioner | Data protection authority | 0% | 0% | 3% | 48% | Microsoft |
| Independent Electoral and Boundaries Commission (IEBC) | Electoral commission | 18% | 0% | 0% | 0% | Microsoft |
| Kenya National Bureau of Statistics | Statistics office | 0% | 0% | 3% | 63% | Google |
| Ministry of Health | Health ministry / National health insurance | 9% | 7% | 0% | 43% | Government |
| Social Health Authority | Health ministry / National health insurance | 32% | 27% | 29% | <1% | Microsoft |
| National Social Security Fund | Social protection / Social registry | 0% | 0% | 0% | 0% | African host |
| State Department for Social Protection | Social protection / Social registry | 0% | 0% | 0% | 72% | Government |
| Ministry of Lands (Ardhisasa) | Land registry | 0% | 0% | 0% | 54% | Government |
| Integrated Payment Services (PesaLink) | National payment switch | 1% | 0% | 89% | 0% | Google |
| Nairobi Securities Exchange | Stock exchange | 25% | 4% | 0% | 0% | Microsoft |
| Capital Markets Authority | Securities regulator | 15% | 0% | 0% | 0% | Microsoft |
| Retirement Benefits Authority | Sovereign wealth fund / National pension fund | 10% | 0% | 13% | 0% | Microsoft |
| Public Procurement Regulatory Authority | Public procurement authority | 28% | 0% | 0% | 0% | Microsoft |
| Government tenders portal | Public procurement authority | 0% | 0% | 0% | 0% | Google |
| Kenya Power | Energy utility | 10% | 0% | 10% | 14% | Microsoft |
| KenGen | Energy utility | 15% | 0% | 26% | 1% | Microsoft |
| Kenya Ports Authority | Ports authority | 22% | 0% | 4% | 31% | Microsoft |
| Safaricom | State-owned telco / National backbone operator | 8% | <1% | 69% | 18% | Filtered |
| Telkom Kenya | State-owned telco / National backbone operator | 3% | 0% | 0% | 74% | Microsoft |
| eCitizen | E-government agency | 1% | 0% | 52% | 0% | Google |
| ICT Authority | E-government agency | 4% | 1% | 1% | 71% | Government |
| Konza Technopolis | National data centre / Government cloud operator | 0% | 0% | 97% | 3% | Microsoft |
| National KE-CIRT/CC | Cybersecurity agency / National CERT | 26% | 0% | 0% | 0% | Microsoft |
| Communications Authority of Kenya | Communications regulator | 27% | 0% | 6% | 0% | Microsoft |
| Office of the Auditor-General | Audit office | 52% | 0% | 0% | 0% | Microsoft |
| Ethics and Anti-Corruption Commission | Anti-corruption commission | 0% | 0% | 0% | 0% | Telecoms |
| Ministry of Information, Communications and the Digital Economy | E-government agency | 0% | 0% | 0% | 59% | Google |

2 of the 36 types are covered by another institution in the table: Armed Forces (in Defence) and Customs (in Revenue Service).

## What stood out

- **Most on US cloud.** Prime Bank (53%) and Office of the Auditor-General (52%) have more than half their working addresses on US cloud.
- **US cloud in Africa.** Social Health Authority has 27% of its working addresses in US cloud data centres in Africa, the highest share in Kenya.
- **Core state bodies on foreign hosting firms.** Executive Office of the President (Network Solutions and Contabo), Ministry of Defence and Kenya Defence Forces (Contabo), Judiciary of Kenya (TierPoint and Contabo) and Kenya Revenue Authority (DigitalOcean).
- **Chinese cloud.** 12 addresses, all at Safaricom, are on Chinese cloud.
- **Names anyone could claim.** One web address at Safaricom points at a deleted cloud name that anyone could register and then publish under. We have flagged it and do not name it here.

## What this can and cannot tell you

The scan sees only the front door: websites, email, login portals, remote-access gateways and online banking. It cannot see where a bank's core ledger, the ID register or the payroll run.

- **Every US figure is a minimum.** Anything behind a shield or a mail filter could also be on US cloud. In Kenya that is 49% of working addresses.
- **It counts addresses, not importance.** An institution with many test and marketing sites weighs more than one with few.
- **The list of institutions was drawn up for this scan.** Each domain was checked to exist, not confirmed as the institution's main one.
- **It is a snapshot.** Every figure is as of 29 September 2026.
- **Nothing was touched.** The scan used public address lookups, public certificate records and the cloud companies' published address lists. It never connected to any institution's systems.

The data and method are in `R&D/Hyperscaler-dependence/scan/KEN/` and `R&D/Hyperscaler-dependence/HYPERSCALER-SCAN.md` in the Corpus repository.
