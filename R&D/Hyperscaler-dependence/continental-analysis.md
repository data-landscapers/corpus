---
layout: article
title: Africa is building its own data centres. The state has yet to move in.
subtitle: Where 1,830 strategic institutions in 54 countries run their websites and email
date: 2026-09-30
author: Bill Anderson
category: Sovereignty
summary: African-controlled data centres have multiplied since 2020, but a scan of 1,830 ministries, regulators, security bodies and banks across all 54 countries finds little sign that governments use them. The state's public internet services sit with US cloud companies in Europe, foreign budget hosts, telecoms operators and security shields, and only 2% visibly with African data centre and cloud firms.
has_data_table: false
---

[Corpus dataset: Institution hosting](https://corpus.data-landscapers.io/datasets/institution-hosting/) · [Methodology](https://corpus.data-landscapers.io/datasets/institution-hosting/methodology/)

Africa's own data centre industry is growing fast. [We argued in June](https://data-landscapers.io/2026/06/11/sovereign-infrastructure/) that African-owned operators can now supply the trusted infrastructure that data localisation needs, and the [Corpus data centres dataset](https://corpus.data-landscapers.io/datasets/data-centres/) now records 299 African-controlled facilities in operation across 50 countries. Of those whose opening year is known, more than half opened in 2020 or later.

This article asks the other half of the question: are African governments using them? In the last week of September 2026 we looked up who runs the servers behind the public internet services of 1,830 institutions in all 54 countries, from the presidency, parliament and ministries to the police, the central bank, the ten largest commercial banks, the payment switch, the electoral commission and the ID authority.

The answer, so far, is that they appear to make little use of them. Only 2% of the addresses we found are visibly with African data centre, cloud and IT companies. US cloud companies hold 17%, almost all of it in Europe or on worldwide networks. Foreign budget hosting firms hold 12%, telecoms operators 19%, and a quarter sits behind security shields that hide the host.

> **What this can and cannot see.** The scan covers websites, email and online portals, not the databases, payroll or registers behind them. A quarter of addresses sit behind shields such as Cloudflare, so the US cloud figures are minimums. A server colocated in an African data centre often uses its owner's or its network provider's addresses, so use of African facilities may be higher than it appears. All figures are for 28 and 29 September 2026.

## How it was done

The method follows [a September 2026 Computer Weekly study](https://www.computerweekly.com/news/366650799/Data-dive-Mapping-UK-police-forces-hyperscale-dependence) of UK police forces. It uses only public sources: the domain name system, the public logs in which website certificates are recorded, the internet registries that record who holds each block of addresses, and the address lists the cloud companies publish for their own networks. It needs no cooperation from any institution and no procurement records, and it treats every country the same way.

We drew up one list of 36 kinds of strategic institution and found each one's main internet domain in every country. Where a country has no such body, or its domain could not be found, the gap is recorded rather than filled. The scan found 61,106 web and mail names under those domains and 65,534 working addresses, and assigned each address to the company or body that runs it. The full method, its checks and its limits are in the [methodology](https://corpus.data-landscapers.io/datasets/institution-hosting/methodology/).

## Who hosts the front door

Across the continent, the working addresses divide as follows.

| Host | Share of working addresses |
| --- | ---: |
| Behind a shield (Cloudflare and similar), host not visible | 24% |
| Telecoms operators and internet providers | 19% |
| US cloud: Amazon, Microsoft, Google, Oracle | 17% |
| Other foreign hosting firms | 12% |
| US online services such as Microsoft 365 | 11% |
| The institution's own systems | 9% |
| Government data centres | 6% |
| African data centres, cloud and IT firms | 2% |
| Chinese cloud, private and unidentified addresses | 1% |

## African data centres are barely visible

The African data centre, cloud and IT firms in the table hold 1,513 of the 65,534 addresses. That category is broader than data centre operators: it also includes South African web hosts, IT service companies and banks' own networks. For government bodies alone the share is 2.5%, and 163 of the 1,453 government bodies have any address there at all.

Of the operators profiled in our June article, only Liquid, part of Cassava, appears with more than a handful of addresses, at about 200. The scan found none registered to Open Access Data Centres, Onix or Wingu, and four to ST Digital. Angola Cables, Seacom and Paratus appear, but as network providers rather than as hosts.

Two cautions apply. First, a ministry that rents space in an African data centre for its own servers will usually appear under its own addresses or those of its telecoms provider, not under the data centre's name. Some of the 9% on institutions' own systems and the 19% with telecoms operators may therefore sit in African facilities. Second, shields hide the host of a quarter of the addresses. So the 2% is a floor. The ceiling is limited too: if every address on institutions' own systems and with telecoms operators were in an African facility, the total would be 30%, still less than the 40% visibly with foreign hosts and US services.

What the scan does show clearly is where the state's public services are when they are with a hosting company: in most cases, a foreign one.

## US cloud is widely used, mostly from outside Africa

732 of the 1,830 institutions (40%) have at least one address on Amazon, Microsoft, Google or Oracle cloud, and 968 (53%) use either US cloud or a US online service such as Microsoft 365. For most it is part of the estate rather than all of it: 93 institutions have more than half their addresses on US cloud. Microsoft accounts for half of the US cloud addresses and Amazon for most of the rest.

The US companies have also built in Africa. Amazon has a cloud region in Cape Town and a smaller zone in Lagos, Microsoft has regions in Johannesburg and Cape Town, and Google and Oracle have opened in Johannesburg. These too are little used. Only 7% of the US cloud addresses we found are in those African regions, and institutions in 19 of the 54 countries use them at all. Half are in Europe, and Microsoft's and Amazon's Dublin regions alone hold a third. Another third are on the companies' worldwide delivery networks, which have no single location.

Many services were set up before the African regions opened, and some cloud services are offered only from certain regions. The pattern is nonetheless consistent: whether a data centre in Africa is African-owned or American-owned, the African state's public services have mostly not moved into it.

## Email runs through Microsoft for a third of institutions

Email is the clearest single indicator of office systems, because an institution that receives its mail through Microsoft 365 or Google usually keeps its documents and calendars there too. Of the 1,637 institutions with a mail record, 629 receive their mail through Microsoft 365 and 98 through Google: 44% between them. The rest use their telecoms operator, a government mail service, their own servers or a commercial host.

Banks lean further on Microsoft than governments do: 197 of the 377 commercial banks (52%) against 432 of the 1,453 other institutions (30%). 122 institutions pass their mail through a filtering service first, most often the British company Mimecast, which can hide the provider behind it.

## Telecoms operators and foreign budget hosts

The national telecoms operator is the most common host in several countries: 74% of addresses in Algeria, 64% in Rwanda, 54% in Ethiopia and 51% in Egypt. Many African telecoms operators also run data centres, and some of this hosting may be in them.

Commercial hosting firms outside Africa, other than the four US cloud companies, hold 12% of the addresses. This is ordinary shared and virtual hosting from companies such as OVH, LWS, Hostinger, Contabo, Namecheap and DigitalOcean. In six countries (Congo, Comoros, Chad, South Sudan, Sierra Leone and Liberia) these firms hold more than half of the addresses we found, and French hosting companies are common among institutions in francophone countries. This is where the gap between African supply and state use is plainest: ST Digital, for example, sells an African cloud in Congo, Cameroon and Benin, where many institutions use foreign budget hosts.

## Government data centres and own systems

14% of the addresses are on a government data centre or the institution's own network, and 263 institutions keep most of their estate there. This is the other sovereign route, and a few states take it seriously. In Nigeria, Galaxy Backbone, the government's own provider, hosts most of the estate of State House and the ministries of defence, justice, foreign affairs and health. In Kenya, the national data centre at Konza receives the mail of ten central bodies, including the Executive Office of the President and the Treasury. The share is highest in Gabon (45%), Tanzania (36%) and Burkina Faso (35%), and it is under 5% in 19 countries.

## Shields hide a large part of the estate

A quarter of the addresses are behind a shield. Cloudflare accounts for 86% of these, and Imperva, Akamai, F5 and Radware for most of the rest. Shields protect websites from attack and speed them up, and they are a reasonable choice. They also make the host behind them invisible to this kind of scan. In six countries (Togo, Uganda, Kenya, Somalia, Nigeria and Libya) more than 40% of the addresses are shielded, and in 23 countries the shielded share is larger than the US cloud share. The most sensitive institutions are the most shielded: two thirds of the addresses of the 11 armed forces and six intelligence services we could scan.

## Banks, governments and China

Commercial banks use US cloud more than government bodies do: 22% of bank addresses against 14% of government addresses, and banks are higher in 38 of the 54 countries. Among government bodies, stock exchanges, ID authorities, securities regulators and central banks use US cloud most; presidencies, defence ministries, the armed forces and e-government agencies use it least.

Chinese cloud is almost absent. The scan found 25 addresses on Chinese cloud services, at seven telecoms operators and banks. This says nothing about equipment or internal systems supplied by Chinese firms, which the scan does not cover.

## Differences between regions and countries

| Region | Countries | US cloud | Behind a shield | Government or own | Telecoms | Other foreign hosts |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Southern Africa | 10 | 24% | 20% | 20% | 17% | 4% |
| West Africa | 17 | 18% | 25% | 12% | 12% | 17% |
| Central Africa | 7 | 12% | 15% | 11% | 20% | 31% |
| East Africa | 15 | 11% | 30% | 14% | 23% | 11% |
| North Africa | 5 | 9% | 22% | 8% | 40% | 8% |

Southern Africa, where all the full cloud regions are, uses US cloud most and also keeps the largest share on government or its own systems. North Africa leans most on telecoms operators, Central Africa on foreign budget hosts and East Africa on shields.

The median country has 13% of its addresses on US cloud. The highest shares are in Guinea (34%), Namibia and Equatorial Guinea (both 30%), the Gambia (29%) and South Africa (28%); Eritrea is higher still, but on 47 addresses from five institutions. The lowest are in Algeria (1%), Mauritania (2%) and Burundi (4%). Country figures rest on between five and 52 institutions each, and a country with few institutions or addresses can rank high or low on very little.

## What it means

The supply of African-controlled data centres has grown quickly. On this evidence, demand from the state has not followed, at least not for the public services that can be seen from outside. Several explanations are possible, and the scan cannot choose between them: services set up before local capacity existed, procurement that defaults to familiar global brands, price, or the convenience of services such as Microsoft 365 that have no African equivalent at the same scale.

A few careful conclusions follow.

- **Capacity is not use.** Data localisation and sovereignty policies that count new facilities should also count what moves into them. The same applies to the US companies' African regions.
- **Hosting is decided institution by institution.** Most countries show a mix of telecoms, national, foreign and cloud hosting, often within a single ministry. That suggests the absence of a common hosting policy, or one that is not followed.
- **The easiest gains may be in budget hosting.** Institutions on shared foreign hosting are using commodity services that African operators already sell, often in the same countries.
- **Governments can answer what this scan cannot.** They know where their servers and databases are. Publishing that would settle how far the state has moved into Africa's own data centres.

The scan also found 13 names, in nine countries, that point to cloud addresses which have been deleted and could be claimed by anyone, who could then publish under the institution's name. We have not named them and have passed them on for disclosure.

## The data

Every figure here is as of 28 and 29 September 2026. The [institution-by-institution dataset](https://corpus.data-landscapers.io/datasets/institution-hosting/) can be searched and downloaded, and the [methodology](https://corpus.data-landscapers.io/datasets/institution-hosting/methodology/) sets out how it was made and what it cannot show. A new scan in a year will show whether the state has started to move in.
